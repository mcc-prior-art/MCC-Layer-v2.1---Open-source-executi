"""PR-3 — Evidence-Bound Execution Ticket: unit-level tests.

Covers the evidence_digest primitive (determinism, mutation sensitivity),
Control's evidence_digest derivation (success / NOT_REQUIRED / every failure
mode), the DecisionEngine's evidence_digest claim (signature coverage), and
ExecutionGate's strict evidence-binding enforcement (exact match, missing,
substitution, mutation, ordering relative to nonce consumption, legacy
tokens).

End-to-end coverage through the real GovernanceService.execute_with_mandate /
execute_with_consensus / execute_with_approval paths (mandate CONSTRAIN +
evidence binding together, consensus, approval delegation, no-authority-from-
evidence-alone) lives in tests/test_governance_service_attestation.py,
alongside the PR-2 tests it already contains -- there is exactly one Control
verification path and exactly one token-issuance path for either PR.
"""

from __future__ import annotations

import asyncio
import copy

import pytest

from gateway.pre_execution_control import (
    AttestationControlReason,
    AttestationRequirement,
    AttestationRequirementRegistry,
    PreExecutionControl,
)
from mcc_attestation import AttesterTrustAnchor, AttesterTrustStore, LocalAttester
from mcc_core import (
    DecisionEngine,
    ExecutionGate,
    InMemoryNonceRegistry,
    SigningKey,
    hash_action,
    hash_document,
    hash_payload,
)

run = asyncio.run

NOW = 1_800_000_000
ACTION = "send_payment"
RESOURCE = "vendor-1"
FORWARD_CONTEXT = {"amount": 100, "currency": "EUR"}
POLICY_HASH = "sha256:" + "0" * 64


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
              resource=RESOURCE, now=NOW + 10, policy_hash=None):
    fc = FORWARD_CONTEXT if forward_context is None else forward_context
    return run(control.evaluate(
        action=action, forward_context=fc, resource=resource,
        raw_attestation=raw_attestation, policy_hash=policy_hash, now=now,
    ))


def _gate(trusted_kid: str, public_key, *, policy_hash=POLICY_HASH,
          nonce_registry=None) -> ExecutionGate:
    return ExecutionGate(
        trusted_keys={trusted_kid: public_key}, audience="pilot",
        nonce_registry=nonce_registry or InMemoryNonceRegistry(), policy_hash=policy_hash,
    )


def _engine(signing_key: SigningKey) -> DecisionEngine:
    return DecisionEngine(
        signing_key=signing_key, issuer="mcc/core", audience="pilot",
        policy_id="pilot/v1", policy_hash=POLICY_HASH,
    )


# ---------------------------------------------------------------------------
# 1. Deterministic evidence digest -- same complete attestation, different
#    dict key order -> same digest.
# ---------------------------------------------------------------------------


def test_01_evidence_digest_is_deterministic_regardless_of_key_order():
    key = _attester_key()
    att = _valid_attestation(key)
    doc = att.to_dict()
    reordered = dict(reversed(list(doc.items())))
    assert doc != list(doc.items())  # sanity: really is a dict, not accidentally equal-order
    assert hash_document(doc) == hash_document(reordered)
    assert hash_document(doc).startswith("sha256:")
    assert len(hash_document(doc)) == len("sha256:") + 64


# ---------------------------------------------------------------------------
# 2. Mutation sensitivity -- claims / provenance / kid / sig each change the
#    digest. The digest binds the COMPLETE signed artifact.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("mutate", [
    lambda d: {**d, "claims": {**d["claims"], "risk_class": "high"}},
    lambda d: {**d, "provenance": {**d["provenance"], "model": "different-model"}},
    lambda d: {**d, "kid": d["kid"] + "-x"},
    lambda d: {**d, "sig": d["sig"][:-4] + "AAAA"},
    lambda d: {**d, "attestation_id": d["attestation_id"] + "-x"},
    lambda d: {**d, "attester_id": d["attester_id"] + "-x"},
    lambda d: {**d, "evidence_type": "different_type"},
    lambda d: {**d, "action_hash": "sha256:" + "1" * 64},
    lambda d: {**d, "scope": d["scope"] + "-x"},
    lambda d: {**d, "issued_at": d["issued_at"] - 1},
    lambda d: {**d, "not_before": d["not_before"] - 1},
    lambda d: {**d, "expires_at": d["expires_at"] + 1},
    lambda d: {**d, "nonce": d["nonce"] + "-x"},
], ids=["claims", "provenance", "kid", "sig", "attestation_id", "attester_id",
        "evidence_type", "action_hash", "scope", "issued_at", "not_before",
        "expires_at", "nonce"])
def test_02_digest_is_sensitive_to_every_field_mutation(mutate):
    key = _attester_key()
    att = _valid_attestation(key)
    original = att.to_dict()
    mutated = mutate(copy.deepcopy(original))
    assert hash_document(mutated) != hash_document(original)


# ---------------------------------------------------------------------------
# 3. Control success -- VERIFIED required attestation produces evidence_digest.
# ---------------------------------------------------------------------------


def test_03_control_verified_result_carries_evidence_digest_matching_raw_document():
    key = _attester_key()
    control = _control(key)
    att = _valid_attestation(key)
    raw = att.to_dict()
    result = _evaluate(control, raw_attestation=raw)
    assert result.ok and result.reason_code == AttestationControlReason.VERIFIED
    assert result.evidence_digest == hash_document(raw)
    assert result.evidence_digest.startswith("sha256:")


# ---------------------------------------------------------------------------
# 4. Control NOT_REQUIRED -- no evidence_digest.
# ---------------------------------------------------------------------------


def test_04_control_not_required_carries_no_evidence_digest():
    key = _attester_key()
    control = _control(key)
    result = _evaluate(control, raw_attestation=None, action="unrelated_action")
    assert result.ok and result.reason_code == AttestationControlReason.NOT_REQUIRED
    assert result.evidence_digest is None


# ---------------------------------------------------------------------------
# 5. Control failure -- invalid/untrusted/expired/mis-bound/replayed
#    attestation never yields a trusted evidence_digest usable for issuance.
# ---------------------------------------------------------------------------


def test_05a_missing_attestation_carries_no_evidence_digest():
    key = _attester_key()
    control = _control(key)
    result = _evaluate(control, raw_attestation=None)
    assert not result.ok
    assert result.evidence_digest is None


def test_05b_forged_signature_carries_no_evidence_digest():
    key = _attester_key()
    control = _control(key)
    raw = _valid_attestation(key).to_dict()
    raw["sig"] = "A" * len(raw["sig"])
    result = _evaluate(control, raw_attestation=raw)
    assert not result.ok
    assert result.reason_code == AttestationControlReason.ATTESTATION_INVALID
    assert result.evidence_digest is None


def test_05c_untrusted_attester_carries_no_evidence_digest():
    key = _attester_key()
    rogue_key = SigningKey.generate("rogue")
    control = _control(key)  # trusts only `key`, not `rogue_key`
    raw = _valid_attestation(rogue_key).to_dict()
    result = _evaluate(control, raw_attestation=raw)
    assert not result.ok
    assert result.reason_code == AttestationControlReason.ATTESTER_UNTRUSTED
    assert result.evidence_digest is None


def test_05d_expired_attestation_carries_no_evidence_digest():
    key = _attester_key()
    control = _control(key)
    raw = _valid_attestation(key, issued_at=NOW, not_before=NOW, expires_at=NOW + 5).to_dict()
    result = _evaluate(control, raw_attestation=raw, now=NOW + 1000)
    assert not result.ok
    assert result.reason_code == AttestationControlReason.ATTESTATION_EXPIRED
    assert result.evidence_digest is None


def test_05e_scope_mismatch_carries_no_evidence_digest():
    key = _attester_key()
    control = _control(key)
    raw = _valid_attestation(key, scope="payment:someone-else").to_dict()
    result = _evaluate(control, raw_attestation=raw)
    assert not result.ok
    assert result.reason_code == AttestationControlReason.ATTESTATION_SCOPE_MISMATCH
    assert result.evidence_digest is None


def test_05f_payload_mismatch_carries_no_evidence_digest():
    key = _attester_key()
    control = _control(key)
    raw = _valid_attestation(key, forward_context={"amount": 999}).to_dict()
    result = _evaluate(control, raw_attestation=raw, forward_context={"amount": 1})
    assert not result.ok
    assert result.reason_code == AttestationControlReason.ATTESTATION_PAYLOAD_MISMATCH
    assert result.evidence_digest is None


def test_05g_replayed_attestation_carries_no_evidence_digest_on_second_use():
    key = _attester_key()
    registry = InMemoryNonceRegistry()
    control = _control(key, nonce_registry=registry)
    raw = _valid_attestation(key).to_dict()
    first = _evaluate(control, raw_attestation=raw)
    assert first.ok and first.evidence_digest is not None
    second = _evaluate(control, raw_attestation=raw)
    assert not second.ok
    assert second.reason_code == AttestationControlReason.ATTESTATION_REPLAYED
    assert second.evidence_digest is None


def test_05h_claim_policy_mismatch_carries_no_evidence_digest():
    key = _attester_key()
    control = _control(key)
    raw = _valid_attestation(key, claims={"risk_class": "high"}).to_dict()
    result = _evaluate(control, raw_attestation=raw)
    assert not result.ok
    assert result.reason_code == AttestationControlReason.ATTESTATION_CLAIM_POLICY_MISMATCH
    assert result.evidence_digest is None


def test_05i_result_construction_rejects_a_digest_on_a_non_verified_reason_code():
    """Structural proof (not just behavioral): ControlAttestationResult itself
    refuses to be constructed with a digest attached to any reason_code other
    than VERIFIED -- a caller cannot accidentally (or maliciously) turn a
    failed attestation decision into one carrying trusted evidence."""
    from gateway.pre_execution_control import ControlAttestationResult

    with pytest.raises(ValueError):
        ControlAttestationResult(
            False, AttestationControlReason.ATTESTATION_INVALID, "x",
            evidence_digest="sha256:" + "0" * 64,
        )
    with pytest.raises(ValueError):
        ControlAttestationResult(
            True, AttestationControlReason.NOT_REQUIRED, "x",
            evidence_digest="sha256:" + "0" * 64,
        )


# ---------------------------------------------------------------------------
# 6. Decision token -- evidence_digest is inside the signed token; tampering
#    evidence_digest causes signature verification failure.
# ---------------------------------------------------------------------------


def test_06a_issued_token_carries_the_exact_evidence_digest():
    signing_key = SigningKey.generate("gw-1")
    engine = _engine(signing_key)
    digest = "sha256:" + "ab" * 32
    token = engine.issue_token(
        verdict="ALLOW", subject="agent/x", action=ACTION, payload=FORWARD_CONTEXT,
        evidence_digest=digest,
    )
    assert token["evidence_digest"] == digest


def test_06b_legacy_issuance_omits_evidence_digest_entirely():
    signing_key = SigningKey.generate("gw-1")
    engine = _engine(signing_key)
    token = engine.issue_token(
        verdict="ALLOW", subject="agent/x", action=ACTION, payload=FORWARD_CONTEXT,
    )
    assert "evidence_digest" not in token


def test_06c_tampering_evidence_digest_breaks_signature_verification():
    from mcc_core.signing import verify_token

    signing_key = SigningKey.generate("gw-1")
    engine = _engine(signing_key)
    digest = "sha256:" + "ab" * 32
    token = engine.issue_token(
        verdict="ALLOW", subject="agent/x", action=ACTION, payload=FORWARD_CONTEXT,
        evidence_digest=digest,
    )
    assert verify_token(token, signing_key.public_key())
    tampered = dict(token)
    tampered["evidence_digest"] = "sha256:" + "cd" * 32
    assert not verify_token(tampered, signing_key.public_key())


def test_06d_evidence_digest_is_not_placed_inside_auth_claims():
    signing_key = SigningKey.generate("gw-1")
    engine = _engine(signing_key)
    digest = "sha256:" + "ab" * 32
    token = engine.issue_token(
        verdict="ALLOW", subject="agent/x", action=ACTION, payload=FORWARD_CONTEXT,
        evidence_digest=digest, auth_claims={"some": "claim"},
    )
    assert "evidence_digest" not in token["auth_claims"]
    assert token["evidence_digest"] == digest


# ---------------------------------------------------------------------------
# 7-12: ExecutionGate strict evidence binding.
# ---------------------------------------------------------------------------


def _issue_evidence_bound_token(signing_key: SigningKey, *, evidence_digest, now=NOW):
    engine = _engine(signing_key)
    return engine.issue_token(
        verdict="ALLOW", subject="agent/x", action=ACTION, payload=FORWARD_CONTEXT,
        evidence_digest=evidence_digest, now=now,
    )


def test_07_gate_allows_when_evidence_exactly_matches_bound_digest():
    signing_key = SigningKey.generate("gw-1")
    key = _attester_key()
    att = _valid_attestation(key).to_dict()
    token = _issue_evidence_bound_token(
        signing_key, evidence_digest=hash_document(att),
    )
    gate = _gate(signing_key.kid, signing_key.public_key())
    result = run(gate.verify(token, action=ACTION, payload=FORWARD_CONTEXT, evidence=att, now=NOW))
    assert result.allowed, result.reason


def test_08_gate_denies_and_does_not_consume_nonce_when_evidence_missing():
    signing_key = SigningKey.generate("gw-1")
    key = _attester_key()
    att = _valid_attestation(key).to_dict()
    token = _issue_evidence_bound_token(signing_key, evidence_digest=hash_document(att))
    registry = InMemoryNonceRegistry()
    gate = _gate(signing_key.kid, signing_key.public_key(), nonce_registry=registry)

    result = run(gate.verify(token, action=ACTION, payload=FORWARD_CONTEXT, evidence=None, now=NOW))
    assert not result.allowed
    assert "EVIDENCE_REQUIRED" in result.reason

    # The nonce must not have been burned: a fresh attempt with the SAME
    # token must still be able to consume it.
    still_available = run(registry.consume(token["nonce"], ttl_seconds=60))
    assert still_available is True


def test_09_gate_denies_evidence_substitution_even_when_independently_valid():
    """Token issued against attestation A + attestation B presented at
    actuation -> DENY, even when B is independently well-formed/valid for
    the SAME action and payload. Nonce is not consumed."""
    signing_key = SigningKey.generate("gw-1")
    key = _attester_key()
    att_a = _valid_attestation(key, nonce="nonce-a").to_dict()
    att_b = _valid_attestation(key, nonce="nonce-b").to_dict()  # different nonce only
    assert hash_document(att_a) != hash_document(att_b)

    token = _issue_evidence_bound_token(signing_key, evidence_digest=hash_document(att_a))
    registry = InMemoryNonceRegistry()
    gate = _gate(signing_key.kid, signing_key.public_key(), nonce_registry=registry)

    result = run(gate.verify(token, action=ACTION, payload=FORWARD_CONTEXT, evidence=att_b, now=NOW))
    assert not result.allowed
    assert "EVIDENCE_DIGEST_MISMATCH" in result.reason

    still_available = run(registry.consume(token["nonce"], ttl_seconds=60))
    assert still_available is True


def test_10_gate_denies_mutated_evidence():
    signing_key = SigningKey.generate("gw-1")
    key = _attester_key()
    att = _valid_attestation(key).to_dict()
    token = _issue_evidence_bound_token(signing_key, evidence_digest=hash_document(att))
    mutated = {**att, "claims": {**att["claims"], "risk_class": "high"}}

    gate = _gate(signing_key.kid, signing_key.public_key())
    result = run(gate.verify(token, action=ACTION, payload=FORWARD_CONTEXT, evidence=mutated, now=NOW))
    assert not result.allowed
    assert "EVIDENCE_DIGEST_MISMATCH" in result.reason


def test_11_retry_with_correct_evidence_after_mismatch_succeeds_same_token():
    """Proves evidence checks precede nonce consumption end-to-end: the
    SAME token is presented twice. The first attempt (wrong evidence) is
    denied; the second attempt (correct evidence) with the identical token
    succeeds. If the first failure had burned the nonce, the second call
    would fail with NONCE_REJECTED instead."""
    signing_key = SigningKey.generate("gw-1")
    key = _attester_key()
    att = _valid_attestation(key).to_dict()
    wrong = _valid_attestation(key, nonce="different-nonce").to_dict()
    token = _issue_evidence_bound_token(signing_key, evidence_digest=hash_document(att))
    gate = _gate(signing_key.kid, signing_key.public_key())

    first = run(gate.verify(token, action=ACTION, payload=FORWARD_CONTEXT, evidence=wrong, now=NOW))
    assert not first.allowed
    assert "EVIDENCE_DIGEST_MISMATCH" in first.reason

    second = run(gate.verify(token, action=ACTION, payload=FORWARD_CONTEXT, evidence=att, now=NOW))
    assert second.allowed, second.reason


def test_12_legacy_token_with_no_evidence_digest_is_completely_unaffected():
    signing_key = SigningKey.generate("gw-1")
    engine = _engine(signing_key)
    token = engine.issue_token(
        verdict="ALLOW", subject="agent/x", action=ACTION, payload=FORWARD_CONTEXT, now=NOW,
    )
    gate = _gate(signing_key.kid, signing_key.public_key())

    # No evidence supplied at all -> still ALLOW (no new requirement introduced).
    result = run(gate.verify(token, action=ACTION, payload=FORWARD_CONTEXT, evidence=None, now=NOW))
    assert result.allowed, result.reason


def test_12b_legacy_token_ignores_an_unexpected_evidence_artifact_too():
    """A legacy (non-evidence-bound) token has nothing to check an evidence
    artifact against, so supplying one anyway must not change the outcome
    either -- Rule A is unconditional, not merely "when none is supplied"."""
    signing_key = SigningKey.generate("gw-1")
    engine = _engine(signing_key)
    token = engine.issue_token(
        verdict="ALLOW", subject="agent/x", action=ACTION, payload=FORWARD_CONTEXT, now=NOW,
    )
    gate = _gate(signing_key.kid, signing_key.public_key())
    key = _attester_key()
    att = _valid_attestation(key).to_dict()

    result = run(gate.verify(token, action=ACTION, payload=FORWARD_CONTEXT, evidence=att, now=NOW))
    assert result.allowed, result.reason


# ---------------------------------------------------------------------------
# 16. valid signed risk_class=low with policy accepting low -> Control
#     accepts without semantic reclassification, and still produces a
#     digest that means only "this exact artifact", never "this is true".
# ---------------------------------------------------------------------------


def test_16_verified_low_risk_claim_yields_digest_without_semantic_claim():
    key = _attester_key()
    control = _control(key, requirement=_requirement(required_claims={"risk_class": ("low",)}))
    raw = _valid_attestation(key, claims={"risk_class": "low"}).to_dict()
    result = _evaluate(control, raw_attestation=raw)
    assert result.ok and result.reason_code == AttestationControlReason.VERIFIED
    # The digest identifies the artifact; it is not, and does not carry, any
    # separate "this was semantically correct" assertion -- there is no such
    # field anywhere on ControlAttestationResult.
    assert result.evidence_digest == hash_document(raw)
    assert not hasattr(result, "risk_is_true")
    assert not hasattr(result, "semantically_correct")
