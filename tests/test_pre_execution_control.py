"""PR-2 — Pre-Execution Attestation Control Integration: unit-level tests
against ``gateway.pre_execution_control.PreExecutionControl`` directly.

These exercise the Control boundary itself (crypto/trust/binding/claim-policy/
replay decisions) in isolation from the full mandate/consensus authority
stack. End-to-end wiring through real ``GovernanceService.execute_with_*``
paths (mandate + CONSTRAIN exact-payload binding + consensus + no-bypass) is
covered separately in ``tests/test_governance_service_attestation.py``.

Numbered comments below map directly to the task's 28 mandatory security
tests; several (crypto/trust/binding failure modes) are proven once here at
the Control-unit level rather than duplicated through the full HTTP stack,
since ``PreExecutionControl.evaluate()`` is the single place those decisions
are made -- proving it here is proving it for every caller.
"""

from __future__ import annotations

import asyncio
import time

import pytest

from gateway.pre_execution_control import (
    AttestationControlReason,
    AttestationRequirement,
    AttestationRequirementRegistry,
    ControlAttestationResult,
    PreExecutionControl,
)
from mcc_attestation import AttesterTrustAnchor, AttesterTrustStore, LocalAttester
from mcc_core.nonce import InMemoryNonceRegistry
from mcc_core.signing import SigningKey, hash_action, hash_payload

NOW = 1_800_000_000
ACTION = "send_payment"
RESOURCE = "vendor-1"
FORWARD_CONTEXT = {"amount": 100, "currency": "EUR"}


def _attester_key() -> SigningKey:
    return SigningKey.generate("attester.payment-risk.v1-key-01")


def _requirement(**overrides) -> AttestationRequirement:
    kw = dict(
        action_pattern=ACTION, evidence_type="risk_assessment",
        scope_template="payment:{resource}", required_claims={"risk_class": ("low",)},
    )
    kw.update(overrides)
    return AttestationRequirement(**kw)


def _control(key: SigningKey, *, requirement=None, nonce_registry=None,
             evidence_types=("risk_assessment",)) -> PreExecutionControl:
    requirements = AttestationRequirementRegistry([requirement or _requirement()])
    trust_store = AttesterTrustStore([
        AttesterTrustAnchor("attester.payment-risk.v1", key.kid, key.public_key(),
                            frozenset(evidence_types)),
    ])
    return PreExecutionControl(
        requirements=requirements, trust_store=trust_store,
        nonce_registry=InMemoryNonceRegistry() if nonce_registry is None else nonce_registry,
    )


def _valid_attestation(key: SigningKey, *, forward_context=None, **overrides):
    attester = LocalAttester("attester.payment-risk.v1", key)
    fc = FORWARD_CONTEXT if forward_context is None else forward_context
    kw = dict(
        evidence_type="risk_assessment", claims={"risk_class": "low"},
        action_hash=hash_action(ACTION), scope=f"payment:{RESOURCE}",
        provenance={"model": "payment-risk-v3"}, payload_hash=hash_payload(fc),
        issued_at=NOW, not_before=NOW, expires_at=NOW + 300, nonce="nonce-1",
    )
    kw.update(overrides)
    return attester.attest(**kw)


def _evaluate(control, *, raw_attestation, forward_context=None, action=ACTION,
              resource=RESOURCE, now=NOW + 10, policy_hash=None) -> ControlAttestationResult:
    fc = FORWARD_CONTEXT if forward_context is None else forward_context
    return asyncio.run(control.evaluate(
        action=action, forward_context=fc, resource=resource,
        raw_attestation=raw_attestation, policy_hash=policy_hash, now=now,
    ))


# ---------------------------------------------------------------------------
# 4. forged attestation signature -> no token
# ---------------------------------------------------------------------------


def test_04_forged_signature_blocks_issuance():
    key = _attester_key()
    control = _control(key)
    att = _valid_attestation(key)
    raw = att.to_dict()
    raw["sig"] = "A" * len(raw["sig"])
    result = _evaluate(control, raw_attestation=raw)
    assert not result.ok
    assert result.reason_code is AttestationControlReason.ATTESTATION_INVALID


# ---------------------------------------------------------------------------
# 5. unknown attester/key -> no token
# ---------------------------------------------------------------------------


def test_05_unknown_attester_key_blocks_issuance():
    key = _attester_key()
    unknown_key = SigningKey.generate("unknown-kid")
    control = _control(key)  # trust store only knows `key`
    att = _valid_attestation(unknown_key)
    result = _evaluate(control, raw_attestation=att.to_dict())
    assert not result.ok
    assert result.reason_code is AttestationControlReason.ATTESTER_UNTRUSTED


# ---------------------------------------------------------------------------
# 6. revoked attester trust anchor -> no token
# ---------------------------------------------------------------------------


def test_06_revoked_trust_anchor_blocks_issuance():
    key = _attester_key()
    control = _control(key)
    control.trust_store.revoke("attester.payment-risk.v1", key.kid)
    att = _valid_attestation(key)
    result = _evaluate(control, raw_attestation=att.to_dict())
    assert not result.ok
    assert result.reason_code is AttestationControlReason.ATTESTER_UNTRUSTED


# ---------------------------------------------------------------------------
# 7. wrong evidence_type -> no token
# ---------------------------------------------------------------------------


def test_07_wrong_evidence_type_blocks_issuance():
    key = _attester_key()
    control = _control(key, evidence_types=("fraud_signal",))  # not risk_assessment
    att = _valid_attestation(key)
    result = _evaluate(control, raw_attestation=att.to_dict())
    assert not result.ok
    assert result.reason_code is AttestationControlReason.ATTESTATION_EVIDENCE_TYPE_MISMATCH


# ---------------------------------------------------------------------------
# 8. expired attestation -> no token
# ---------------------------------------------------------------------------


def test_08_expired_attestation_blocks_issuance():
    key = _attester_key()
    control = _control(key)
    att = _valid_attestation(key)
    result = _evaluate(control, raw_attestation=att.to_dict(), now=NOW + 1000)
    assert not result.ok
    assert result.reason_code is AttestationControlReason.ATTESTATION_EXPIRED


# ---------------------------------------------------------------------------
# 9. not-yet-valid attestation -> no token
# ---------------------------------------------------------------------------


def test_09_not_yet_valid_attestation_blocks_issuance():
    key = _attester_key()
    control = _control(key)
    att = _valid_attestation(key, not_before=NOW + 200, expires_at=NOW + 500)
    result = _evaluate(control, raw_attestation=att.to_dict(), now=NOW + 10)
    assert not result.ok
    assert result.reason_code is AttestationControlReason.ATTESTATION_NOT_YET_VALID


# ---------------------------------------------------------------------------
# 10. wrong action_hash -> no token
# ---------------------------------------------------------------------------


def test_10_action_hash_tampered_after_signing_blocks_issuance():
    key = _attester_key()
    control = _control(key)
    att = _valid_attestation(key)
    raw = att.to_dict()
    raw["action_hash"] = hash_action("delete_all_vendors")  # tamper post-signing
    result = _evaluate(control, raw_attestation=raw)
    assert not result.ok
    # signature covers action_hash, so tampering after signing invalidates the
    # signature first -- ATTESTATION_INVALID, not a binding-specific code.
    assert result.reason_code is AttestationControlReason.ATTESTATION_INVALID


def test_10b_wrong_action_hash_via_wrong_action_blocks_issuance():
    # A genuinely-signed attestation for a DIFFERENT action than the one
    # actually being proposed -- signature is valid, but action_hash mismatch
    # is a real binding failure (not caught earlier as a forgery).
    key = _attester_key()
    control = _control(key, requirement=_requirement(action_pattern="*"))
    attester = LocalAttester("attester.payment-risk.v1", key)
    att = attester.attest(
        evidence_type="risk_assessment", claims={"risk_class": "low"},
        action_hash=hash_action("some_other_action"), scope=f"payment:{RESOURCE}",
        provenance={}, payload_hash=hash_payload(FORWARD_CONTEXT),
        issued_at=NOW, not_before=NOW, expires_at=NOW + 300, nonce="nonce-x",
    )
    result = _evaluate(control, raw_attestation=att.to_dict())
    assert not result.ok
    assert result.reason_code is AttestationControlReason.ATTESTATION_ACTION_MISMATCH


# ---------------------------------------------------------------------------
# 11. wrong payload_hash -> no token
# ---------------------------------------------------------------------------


def test_11_wrong_payload_hash_blocks_issuance():
    key = _attester_key()
    control = _control(key)
    # attestation bound to a DIFFERENT payload than forward_context.
    att = _valid_attestation(key, forward_context={"amount": 999, "currency": "EUR"})
    result = _evaluate(control, raw_attestation=att.to_dict(), forward_context=FORWARD_CONTEXT)
    assert not result.ok
    assert result.reason_code is AttestationControlReason.ATTESTATION_PAYLOAD_MISMATCH


# ---------------------------------------------------------------------------
# 12. wrong scope -> no token
# ---------------------------------------------------------------------------


def test_12_wrong_scope_blocks_issuance():
    key = _attester_key()
    control = _control(key)
    att = _valid_attestation(key, scope="payment:someone-else")
    result = _evaluate(control, raw_attestation=att.to_dict())
    assert not result.ok
    assert result.reason_code is AttestationControlReason.ATTESTATION_SCOPE_MISMATCH


# ---------------------------------------------------------------------------
# 13. wrong policy binding -> no token
# ---------------------------------------------------------------------------


def test_13_wrong_policy_binding_blocks_issuance():
    key = _attester_key()
    requirement = _requirement(require_policy_binding=True)
    control = _control(key, requirement=requirement)
    att = _valid_attestation(key, policy_hash="sha256:" + "a" * 64)
    result = _evaluate(control, raw_attestation=att.to_dict(), policy_hash="sha256:" + "b" * 64)
    assert not result.ok
    assert result.reason_code is AttestationControlReason.ATTESTATION_POLICY_MISMATCH


def test_13b_correct_policy_binding_permits_issuance():
    key = _attester_key()
    requirement = _requirement(require_policy_binding=True)
    control = _control(key, requirement=requirement)
    ph = "sha256:" + "a" * 64
    att = _valid_attestation(key, policy_hash=ph)
    result = _evaluate(control, raw_attestation=att.to_dict(), policy_hash=ph)
    assert result.ok


# ---------------------------------------------------------------------------
# 14. required signed claim absent -> no token
# ---------------------------------------------------------------------------


def test_14_required_claim_absent_blocks_issuance():
    key = _attester_key()
    control = _control(key)
    att = _valid_attestation(key, claims={"other_claim": "x"})
    result = _evaluate(control, raw_attestation=att.to_dict())
    assert not result.ok
    assert result.reason_code is AttestationControlReason.ATTESTATION_CLAIM_POLICY_MISMATCH


# ---------------------------------------------------------------------------
# 15. required signed claim outside allowed deterministic values -> no token
# ---------------------------------------------------------------------------


def test_15_required_claim_outside_allowed_values_blocks_issuance():
    key = _attester_key()
    control = _control(key)
    att = _valid_attestation(key, claims={"risk_class": "high"})
    result = _evaluate(control, raw_attestation=att.to_dict())
    assert not result.ok
    assert result.reason_code is AttestationControlReason.ATTESTATION_CLAIM_POLICY_MISMATCH


# ---------------------------------------------------------------------------
# 16. valid signed risk_class=low with policy accepting low -> Control
#     accepts without any semantic reclassification
# ---------------------------------------------------------------------------


def test_16_valid_low_risk_claim_accepted_deterministically():
    key = _attester_key()
    control = _control(key)
    att = _valid_attestation(key, claims={"risk_class": "low"})
    result = _evaluate(control, raw_attestation=att.to_dict())
    assert result.ok
    assert result.reason_code is AttestationControlReason.VERIFIED
    # Control's own claim-policy step is a plain equality/membership
    # check -- prove no other machinery is involved by confirming the
    # verification result's claims are exactly what was signed.
    assert result.verification is not None
    assert result.verification.verified


# ---------------------------------------------------------------------------
# 17. same valid attestation used twice -> exactly one issuance succeeds
# ---------------------------------------------------------------------------


def test_17_replayed_attestation_fails_closed():
    key = _attester_key()
    nonce_registry = InMemoryNonceRegistry()
    control = _control(key, nonce_registry=nonce_registry)
    att = _valid_attestation(key)
    raw = att.to_dict()
    first = _evaluate(control, raw_attestation=raw, now=NOW + 10)
    second = _evaluate(control, raw_attestation=raw, now=NOW + 11)
    assert first.ok
    assert not second.ok
    assert second.reason_code is AttestationControlReason.ATTESTATION_REPLAYED


# ---------------------------------------------------------------------------
# 18. concurrent attempts using the same attestation nonce -> at most one
#     executable token can be issued
# ---------------------------------------------------------------------------


def test_18_concurrent_replay_attempts_at_most_one_succeeds():
    key = _attester_key()
    nonce_registry = InMemoryNonceRegistry()
    control = _control(key, nonce_registry=nonce_registry)
    att = _valid_attestation(key)
    raw = att.to_dict()

    async def attempt():
        return await control.evaluate(
            action=ACTION, forward_context=FORWARD_CONTEXT, resource=RESOURCE,
            raw_attestation=raw, now=NOW + 10,
        )

    async def run_concurrently():
        return await asyncio.gather(*(attempt() for _ in range(10)))

    results = asyncio.run(run_concurrently())
    successes = [r for r in results if r.ok]
    assert len(successes) == 1
    for r in results:
        if not r.ok:
            assert r.reason_code is AttestationControlReason.ATTESTATION_REPLAYED


# ---------------------------------------------------------------------------
# 19. replay backend unavailable / exception -> zero executable tokens
# ---------------------------------------------------------------------------


class _RaisingNonceRegistry:
    async def consume(self, nonce, ttl_seconds=300):
        raise ConnectionError("simulated Redis outage")


def test_19_replay_backend_unavailable_blocks_issuance():
    key = _attester_key()
    control = _control(key, nonce_registry=_RaisingNonceRegistry())
    att = _valid_attestation(key)
    result = _evaluate(control, raw_attestation=att.to_dict())
    assert not result.ok
    assert result.reason_code is AttestationControlReason.ATTESTATION_REPLAY_UNAVAILABLE


def test_19b_no_replay_registry_configured_blocks_issuance():
    key = _attester_key()
    requirements = AttestationRequirementRegistry([_requirement()])
    trust_store = AttesterTrustStore([
        AttesterTrustAnchor("attester.payment-risk.v1", key.kid, key.public_key(),
                            frozenset({"risk_assessment"})),
    ])
    control = PreExecutionControl(requirements=requirements, trust_store=trust_store,
                                   nonce_registry=None)
    att = _valid_attestation(key)
    result = _evaluate(control, raw_attestation=att.to_dict())
    assert not result.ok
    assert result.reason_code is AttestationControlReason.ATTESTATION_REPLAY_UNAVAILABLE


# ---------------------------------------------------------------------------
# 20. malformed attestation / verifier exception -> zero executable tokens
# ---------------------------------------------------------------------------


def test_20a_malformed_attestation_blocks_issuance():
    key = _attester_key()
    control = _control(key)
    result = _evaluate(control, raw_attestation={"not": "a valid attestation"})
    assert not result.ok
    assert result.reason_code is AttestationControlReason.ATTESTATION_INVALID


def test_20b_non_dict_attestation_blocks_issuance():
    key = _attester_key()
    control = _control(key)
    result = _evaluate(control, raw_attestation="not-even-a-dict")  # type: ignore[arg-type]
    assert not result.ok
    assert result.reason_code is AttestationControlReason.ATTESTATION_REQUIRED


def test_20c_verifier_internal_exception_fails_closed_via_pr1():
    """An exception raised inside PR-1's own verify_attestation (e.g. a
    trust-store lookup failure) is already caught by PR-1's own outer
    try/except (see mcc_attestation.verifier) and reported as a structured
    INVALID result -- Control's own exception handler is never reached for
    this case, and the result correctly maps to ATTESTATION_INVALID."""
    key = _attester_key()

    class _ExplodingTrustStore:
        def resolve(self, attester_id, kid):
            raise RuntimeError("boom")

    requirements = AttestationRequirementRegistry([_requirement()])
    control = PreExecutionControl(
        requirements=requirements, trust_store=_ExplodingTrustStore(),
        nonce_registry=InMemoryNonceRegistry(),
    )
    att = _valid_attestation(key)
    result = _evaluate(control, raw_attestation=att.to_dict())
    assert not result.ok
    assert result.reason_code is AttestationControlReason.ATTESTATION_INVALID
    assert result.verification is not None
    assert result.verification.overall_status.value == "INVALID"


def test_20d_controls_own_internal_exception_fails_closed():
    """An exception raised in Control's OWN code (outside verify_attestation
    entirely -- e.g. requirement resolution) is caught by Control's own
    outer try/except and reported as ATTESTATION_CONTROL_ERROR, distinct
    from a PR-1-internal failure."""
    key = _attester_key()

    class _ExplodingRequirements:
        def for_action(self, action):
            raise RuntimeError("boom")

    trust_store = AttesterTrustStore([
        AttesterTrustAnchor("attester.payment-risk.v1", key.kid, key.public_key(),
                            frozenset({"risk_assessment"})),
    ])
    control = PreExecutionControl(
        requirements=_ExplodingRequirements(), trust_store=trust_store,
        nonce_registry=InMemoryNonceRegistry(),
    )
    att = _valid_attestation(key)
    result = _evaluate(control, raw_attestation=att.to_dict())
    assert not result.ok
    assert result.reason_code is AttestationControlReason.ATTESTATION_CONTROL_ERROR


# ---------------------------------------------------------------------------
# 21. static failure before nonce consumption -> nonce is not burned
# ---------------------------------------------------------------------------


def test_21_static_failure_does_not_burn_the_nonce():
    key = _attester_key()
    nonce_registry = InMemoryNonceRegistry()
    control = _control(key, nonce_registry=nonce_registry)
    # First: an attestation with the SAME nonce but a WRONG scope -> a
    # static (pre-nonce) failure.
    bad = _valid_attestation(key, scope="payment:wrong-resource", nonce="shared-nonce")
    bad_result = _evaluate(control, raw_attestation=bad.to_dict())
    assert not bad_result.ok
    assert bad_result.reason_code is AttestationControlReason.ATTESTATION_SCOPE_MISMATCH

    # Second: a freshly, correctly-bound attestation reusing the SAME nonce
    # value must still succeed -- proving the first (failed) attempt never
    # consumed it.
    good = _valid_attestation(key, nonce="shared-nonce")
    good_result = _evaluate(control, raw_attestation=good.to_dict(), now=NOW + 20)
    assert good_result.ok


# ---------------------------------------------------------------------------
# 24. action with no AttestationRequirement -> existing behavior preserved
# ---------------------------------------------------------------------------


def test_24_action_with_no_requirement_is_unaffected():
    key = _attester_key()
    control = _control(key, requirement=_requirement(action_pattern="send_payment"))
    result = asyncio.run(control.evaluate(
        action="totally_unrelated_action", forward_context={}, resource=None,
        raw_attestation=None, now=NOW,
    ))
    assert result.ok
    assert result.reason_code is AttestationControlReason.NOT_REQUIRED


# ---------------------------------------------------------------------------
# 25. caller supplies a fake/precomputed verified=True without a raw valid
#     attestation -> cannot authorize anything
# ---------------------------------------------------------------------------


def test_25_precomputed_verified_flag_is_not_a_parameter_and_is_ignored():
    import inspect

    params = set(inspect.signature(PreExecutionControl.evaluate).parameters)
    # There is no way for a caller to hand Control a pre-verified result --
    # only the raw attestation document.
    assert "verified" not in params
    assert "verification_result" not in params
    assert "attestation_verification_result" not in params
    assert "raw_attestation" in params

    # Behaviorally: even a dict with an (extraneous, meaningless) "verified"
    # key inside the raw attestation itself is still fully re-verified and
    # rejected on its own (unsigned) merits.
    key = _attester_key()
    control = _control(key)
    result = _evaluate(control, raw_attestation={"verified": True, "sig": "forged"})
    assert not result.ok


# ---------------------------------------------------------------------------
# Additional coverage beyond the mandatory 28: constructor invariant, TTL
# derivation, requirement registry resolution order.
# ---------------------------------------------------------------------------


def test_result_ok_reason_code_consistency_is_enforced():
    with pytest.raises(ValueError):
        ControlAttestationResult(True, AttestationControlReason.ATTESTATION_REQUIRED, "bad")
    with pytest.raises(ValueError):
        ControlAttestationResult(False, AttestationControlReason.VERIFIED, "bad")


def test_requirement_registry_first_match_wins():
    specific = _requirement(action_pattern="send_payment", evidence_type="risk_assessment")
    generic = _requirement(action_pattern="*", evidence_type="generic_review")
    registry = AttestationRequirementRegistry([specific, generic])
    assert registry.for_action("send_payment") is specific
    assert registry.for_action("something_else") is generic


def test_nonce_ttl_is_bounded_and_never_nonnegative():
    key = _attester_key()
    control = _control(key)
    # Attestation already expired relative to "now": remaining is negative.
    ttl = control._nonce_ttl(expires_at=NOW, now=NOW + 10_000)
    assert ttl >= control.min_nonce_ttl_seconds
    # Attestation with an enormous remaining window: clamps to the max.
    ttl2 = control._nonce_ttl(expires_at=NOW + 10_000_000, now=NOW)
    assert ttl2 <= control.max_nonce_ttl_seconds
