"""PR-2 — Pre-Execution Attestation Control Integration: end-to-end tests
through the REAL ``GovernanceService.execute_with_mandate`` /
``execute_with_consensus`` paths (the same code the ``/mandates/execute``,
``/approvals/{id}/execute``, and ``/consensus/execute`` HTTP routes call).

Complements ``tests/test_pre_execution_control.py`` (unit-level Control
decisions in isolation). These tests prove the wiring itself: that a real
signed mandate / real consensus quorum plus a real PR-1 EvidenceAttestation
together determine whether ``DecisionEngine.issue_token`` is ever reached, in
both directions (authority alone is not enough; attestation alone is not
enough), and that a mandate's CONSTRAIN rewrite is exactly what the
attestation must bind to.
"""

from __future__ import annotations

import asyncio
import tempfile
import time
from pathlib import Path

import pytest

from gateway.governance_service import GovernanceService
from gateway.pre_execution_control import (
    AttestationRequirement,
    AttestationRequirementRegistry,
    PreExecutionControl,
)
from mcc_attestation import AttesterTrustAnchor, AttesterTrustStore, LocalAttester
from mcc_core import (
    ApprovalService,
    AuditLog,
    ConsensusPolicy,
    ConsensusVerifier,
    DecisionEngine,
    EnforcementCoordinator,
    ExecutionGate,
    InMemoryApprovalRegistry,
    InMemoryIdempotencyRegistry,
    InMemoryNonceRegistry,
    InMemoryRevocationRegistry,
    InMemoryVelocityRegistry,
    MandateAuthority,
    MandateVerifier,
    ProfileRegistry,
    SigningKey,
    hash_action,
    hash_payload,
    issue_mandate,
    issue_vote,
)
from gateway.trust import TrustSet

run = asyncio.run

def _now() -> int:
    """Real wall-clock now, evaluated at the CALL site (never cached at
    module-import time). ``GovernanceService._now()`` and
    ``PreExecutionControl.evaluate()`` both default to ``time.time()`` (no
    injectable clock), so mandate/attestation validity windows must be
    anchored to the actual moment each test runs -- a module-level constant
    captured once at collection time would drift stale (and expire a short
    attestation window) if the full suite takes minutes to reach this file."""
    return int(time.time())


ACTION = "send_payment"
RESOURCE = "vendor-1"
POLICY_HASH = "sha256:" + "0" * 64


def _tmp_audit() -> AuditLog:
    d = tempfile.mkdtemp(prefix="mcc-pr2-test-")
    return AuditLog(str(Path(d) / "audit.jsonl"))


def _raw_context(**overrides) -> dict:
    ctx = {"source": "acct-1", "beneficiary_id": RESOURCE, "amount": 100, "currency": "eur"}
    ctx.update(overrides)
    return ctx


def _canonical(context: dict) -> dict:
    """The exact canonicalization ``send_payment`` (PaymentProfile) applies --
    what actually becomes ``forward_context`` inside GovernanceService, and
    therefore what an attestation must bind its payload_hash to."""
    return ProfileRegistry.default_pilot().for_action(ACTION).canonical_payload(context)


def _attester_key() -> SigningKey:
    return SigningKey.generate("attester.payment-risk.v1-key-01")


def _requirement(**overrides) -> AttestationRequirement:
    kw = dict(
        action_pattern=ACTION, evidence_type="risk_assessment",
        scope_template="payment:{resource}", required_claims={"risk_class": ("low",)},
    )
    kw.update(overrides)
    return AttestationRequirement(**kw)


def _pre_execution_control(attester_key: SigningKey, requirement=None) -> PreExecutionControl:
    return PreExecutionControl(
        requirements=AttestationRequirementRegistry([requirement or _requirement()]),
        trust_store=AttesterTrustStore([
            AttesterTrustAnchor("attester.payment-risk.v1", attester_key.kid,
                                attester_key.public_key(), frozenset({"risk_assessment"})),
        ]),
        nonce_registry=InMemoryNonceRegistry(),
    )


def _valid_attestation(attester_key: SigningKey, *, forward_context: dict, nonce="nonce-1",
                       claims=None, **overrides):
    attester = LocalAttester("attester.payment-risk.v1", attester_key)
    now = _now()
    kw = dict(
        evidence_type="risk_assessment", claims=claims or {"risk_class": "low"},
        action_hash=hash_action(ACTION), scope=f"payment:{RESOURCE}",
        provenance={"model": "payment-risk-v3"}, payload_hash=hash_payload(forward_context),
        issued_at=now, not_before=now, expires_at=now + 900, nonce=nonce,
    )
    kw.update(overrides)
    return attester.attest(**kw)


def _governance_service(*, pre_execution_control=None, mandate_key: SigningKey,
                        mandate_constraints=None) -> GovernanceService:
    signing_key = SigningKey.generate("gw-signing-1")
    engine = DecisionEngine(
        signing_key=signing_key, issuer="mcc/core", audience="pilot", policy_id="pilot/v1",
        policy_hash=POLICY_HASH,
    )
    gate = ExecutionGate(
        trusted_keys={signing_key.kid: signing_key.public_key()}, audience="pilot",
        nonce_registry=InMemoryNonceRegistry(), policy_hash=POLICY_HASH,
    )
    coordinator = EnforcementCoordinator(
        gate=gate, idempotency=InMemoryIdempotencyRegistry(),
        velocity=InMemoryVelocityRegistry(), audit=_tmp_audit(),
        profiles=ProfileRegistry.default_pilot(), revocation_registry=InMemoryRevocationRegistry(),
    )
    trust_set = TrustSet()
    trust_set.add_runtime_issuer("axlogiq/pilot", mandate_key.kid, mandate_key.public_key())
    approver_key = SigningKey.generate("approver-1")
    approvals = ApprovalService(InMemoryApprovalRegistry(), approver_key)

    async def upstream(action, payload):
        return {"ok": True, "action": action, "payload": payload}

    return GovernanceService(
        engine=engine, coordinator=coordinator, trust_set=trust_set,
        revocation_registry=InMemoryRevocationRegistry(), approvals=approvals,
        profiles=ProfileRegistry.default_pilot(), upstream=upstream, policy_hash=POLICY_HASH,
        pre_execution_control=pre_execution_control,
    )


def _mandate(mandate_key: SigningKey, *, constraints=None):
    now = _now()
    return issue_mandate(
        mandate_key, issuer="axlogiq/pilot", subject="agent/payments-bot",
        action_scope=[ACTION], resource_scope=[RESOURCE],
        constraints=constraints or {}, not_before=now - 10, not_after=now + 3600,
        issued_at=now,
    )


# ---------------------------------------------------------------------------
# 1. valid mandate + required valid attestation -> executable token may be
#    issued
# ---------------------------------------------------------------------------


def test_01_valid_mandate_and_valid_attestation_issues_token():
    mandate_key = SigningKey.generate("issuer-1")
    attester_key = _attester_key()
    service = _governance_service(
        pre_execution_control=_pre_execution_control(attester_key), mandate_key=mandate_key,
    )
    mandate = _mandate(mandate_key)
    context = _raw_context()
    att = _valid_attestation(attester_key, forward_context=_canonical(context))

    out = run(service.execute_with_mandate(
        mandate=mandate, actor="agent/payments-bot", action=ACTION, resource=RESOURCE,
        context=context, attestation=att.to_dict(),
    ))
    assert out.status == "EXECUTED"
    assert out.decision == "ALLOW"


# ---------------------------------------------------------------------------
# 2. valid mandate + missing required attestation -> no token
# ---------------------------------------------------------------------------


def test_02_valid_mandate_missing_attestation_blocks():
    mandate_key = SigningKey.generate("issuer-1")
    attester_key = _attester_key()
    service = _governance_service(
        pre_execution_control=_pre_execution_control(attester_key), mandate_key=mandate_key,
    )
    mandate = _mandate(mandate_key)
    context = _raw_context()

    out = run(service.execute_with_mandate(
        mandate=mandate, actor="agent/payments-bot", action=ACTION, resource=RESOURCE,
        context=context, attestation=None,
    ))
    assert out.status == "BLOCKED"
    assert out.decision == "DENY"
    assert "ATTESTATION_REQUIRED" in out.reason


# ---------------------------------------------------------------------------
# 3. valid attestation + no valid mandate -> no token
# ---------------------------------------------------------------------------


def test_03_valid_attestation_invalid_mandate_blocks():
    mandate_key = SigningKey.generate("issuer-1")
    rogue_key = SigningKey.generate("rogue-issuer")  # NOT trusted by the service
    attester_key = _attester_key()
    service = _governance_service(
        pre_execution_control=_pre_execution_control(attester_key), mandate_key=mandate_key,
    )
    bad_mandate = _mandate(rogue_key)  # signed by an untrusted issuer
    context = _raw_context()
    att = _valid_attestation(attester_key, forward_context=_canonical(context))

    out = run(service.execute_with_mandate(
        mandate=bad_mandate, actor="agent/payments-bot", action=ACTION, resource=RESOURCE,
        context=context, attestation=att.to_dict(),
    ))
    assert out.status == "BLOCKED"
    assert out.decision == "DENY"
    # Never even reaches attestation evaluation -- authority failure short-circuits first.


# ---------------------------------------------------------------------------
# 22. mandate CONSTRAIN rewrites the payload, but supplied attestation is
#     bound to original payload -> no token
# ---------------------------------------------------------------------------


def test_22_constrain_rewrite_invalidates_attestation_bound_to_original_payload():
    mandate_key = SigningKey.generate("issuer-1")
    attester_key = _attester_key()
    service = _governance_service(
        pre_execution_control=_pre_execution_control(attester_key), mandate_key=mandate_key,
    )
    mandate = _mandate(mandate_key, constraints={"max_amount": 50})
    original_context = _raw_context(amount=999)  # will be clamped to 50

    # Attestation is bound to the ORIGINAL (pre-constraint) canonical payload.
    att = _valid_attestation(attester_key, forward_context=_canonical(original_context))

    out = run(service.execute_with_mandate(
        mandate=mandate, actor="agent/payments-bot", action=ACTION, resource=RESOURCE,
        context=original_context, attestation=att.to_dict(),
    ))
    assert out.status == "BLOCKED"
    assert out.decision == "DENY"
    assert "ATTESTATION_PAYLOAD_MISMATCH" in out.reason


# ---------------------------------------------------------------------------
# 23. fresh attestation bound to the constrained final payload -> token may
#     be issued
# ---------------------------------------------------------------------------


def test_23_attestation_bound_to_constrained_payload_issues_token():
    mandate_key = SigningKey.generate("issuer-1")
    attester_key = _attester_key()
    service = _governance_service(
        pre_execution_control=_pre_execution_control(attester_key), mandate_key=mandate_key,
    )
    mandate = _mandate(mandate_key, constraints={"max_amount": 50})
    original_context = _raw_context(amount=999)
    # What MandateAuthority.authorize() actually rewrites forward_context to:
    # the canonical payload with "amount" clamped to the exact constraint bound
    # value (apply_constraints() assigns the bound literal itself, not a
    # re-normalized float) -- this is what the fresh attestation must bind to.
    constrained_context = dict(_canonical(original_context))
    constrained_context["amount"] = 50

    # Attestation is bound to the EXACT constrained/final payload.
    att = _valid_attestation(attester_key, forward_context=constrained_context)

    out = run(service.execute_with_mandate(
        mandate=mandate, actor="agent/payments-bot", action=ACTION, resource=RESOURCE,
        context=original_context, attestation=att.to_dict(),
    ))
    assert out.status == "EXECUTED"
    assert out.decision == "CONSTRAIN"


# ---------------------------------------------------------------------------
# 24. action with no AttestationRequirement -> existing behavior remains
#     backward compatible
# ---------------------------------------------------------------------------


def test_24_unrelated_action_unaffected_by_attestation_requirement():
    mandate_key = SigningKey.generate("issuer-1")
    attester_key = _attester_key()
    # Requirement only governs "send_payment" -- this mandate/action pair
    # ("check_balance") has no matching requirement.
    service = _governance_service(
        pre_execution_control=_pre_execution_control(attester_key), mandate_key=mandate_key,
    )
    now = _now()
    mandate = issue_mandate(
        mandate_key, issuer="axlogiq/pilot", subject="agent/payments-bot",
        action_scope=["check_balance"], resource_scope=[RESOURCE], constraints={},
        not_before=now - 10, not_after=now + 3600, issued_at=now,
    )
    out = run(service.execute_with_mandate(
        mandate=mandate, actor="agent/payments-bot", action="check_balance", resource=RESOURCE,
        context={}, attestation=None,  # no attestation supplied, and none required
    ))
    assert out.status == "EXECUTED"
    assert out.decision == "ALLOW"


def test_24b_no_pre_execution_control_configured_is_fully_backward_compatible():
    mandate_key = SigningKey.generate("issuer-1")
    # No PreExecutionControl at all -- must behave exactly as pre-PR-2.
    service = _governance_service(pre_execution_control=None, mandate_key=mandate_key)
    mandate = _mandate(mandate_key)
    context = _raw_context()
    out = run(service.execute_with_mandate(
        mandate=mandate, actor="agent/payments-bot", action=ACTION, resource=RESOURCE,
        context=context, attestation=None,
    ))
    assert out.status == "EXECUTED"
    assert out.decision == "ALLOW"


# ---------------------------------------------------------------------------
# 27. all governed runtime issuance paths requiring attestation go through
#     the new Control boundary (mandate execute AND consensus execute)
# ---------------------------------------------------------------------------


def test_27_consensus_execute_path_is_also_gated_by_attestation():
    mandate_key = SigningKey.generate("issuer-1")  # unused by consensus path
    attester_key = _attester_key()
    evaluator_keys = [SigningKey.generate(f"evaluator-{i}") for i in range(3)]
    consensus_verifier = ConsensusVerifier(
        trusted_keys={k.kid: k.public_key() for k in evaluator_keys},
        policy=ConsensusPolicy(threshold=3),
    )
    service = _governance_service(
        pre_execution_control=_pre_execution_control(attester_key), mandate_key=mandate_key,
    )
    service.consensus_verifier = consensus_verifier

    context = _raw_context()
    canonical = service.profiles.for_action(ACTION).canonical_payload(context)

    def _votes(nonce: str):
        now = _now()
        return [
            issue_vote(
                k, evaluator_id=k.kid, verdict="ALLOW", action=ACTION, payload=canonical,
                actor="agent/payments-bot", resource=RESOURCE, policy_hash=POLICY_HASH,
                nonce=nonce, not_before=now - 10, not_after=now + 3600, issued_at=now,
            )
            for k in evaluator_keys
        ]

    votes = _votes("consensus-nonce-1")

    # (a) without attestation -> blocked, even though consensus itself is valid.
    out_missing = run(service.execute_with_consensus(
        votes=votes, actor="agent/payments-bot", action=ACTION, resource=RESOURCE,
        context=context, nonce="consensus-nonce-1",
    ))
    assert out_missing.status == "BLOCKED"
    assert "ATTESTATION_REQUIRED" in out_missing.reason

    # (b) with a valid attestation bound to the exact canonical payload -> issues.
    att = _valid_attestation(attester_key, forward_context=canonical, nonce="att-nonce-consensus")
    votes2 = _votes("consensus-nonce-2")
    out_ok = run(service.execute_with_consensus(
        votes=votes2, actor="agent/payments-bot", action=ACTION, resource=RESOURCE,
        context=context, nonce="consensus-nonce-2", attestation=att.to_dict(),
    ))
    assert out_ok.status == "EXECUTED"
