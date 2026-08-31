"""MCC Attestation — EvidenceAttestation contract, signing, trust, and
deterministic fail-closed verification (PR-1: pre-execution attestation
foundation).

This package is independent of and does not integrate with MCC-Control,
AuthorityModel, decision-token issuance, ExecutionGate, or the Gateway API
(see ``tests/test_mcc_attestation_architecture_guards.py`` for the static
guards proving that boundary). These tests exercise only
``mcc_attestation`` itself: construction, canonical signing, trust
resolution, and the 13-step deterministic verification order documented in
``verifier.py`` / ``docs/ATTESTATION_ARCHITECTURE.md``.
"""

from __future__ import annotations

import copy

import pytest

from mcc_attestation import (
    AttestationStatus,
    AttesterTrustAnchor,
    AttesterTrustStore,
    EvidenceAttestation,
    LocalAttester,
    sign_attestation,
    verify_attestation,
)
from mcc_attestation.schema import ATTESTATION_SCHEMA_VERSION, MalformedAttestationError
from mcc_core.signing import SigningKey, canonical_bytes, hash_action

ACTION = "payment.refund"
SCOPE = "payment:vendor_invoice"
ISSUED_AT = 1_000_000
NOT_BEFORE = 1_000_000
EXPIRES_AT = 1_000_300


def _action_hash() -> str:
    return hash_action(ACTION)


@pytest.fixture()
def attester_key() -> SigningKey:
    return SigningKey.generate("attester.payment-risk.v1-key-01")


@pytest.fixture()
def attester(attester_key: SigningKey) -> LocalAttester:
    return LocalAttester("attester.payment-risk.v1", attester_key)


@pytest.fixture()
def other_attester_key() -> SigningKey:
    # Deliberately given the SAME kid string as attester_key, to construct
    # the "key belonging to another attester" scenario (test 9): a kid that
    # is only ever registered under a *different* attester_id.
    return SigningKey.generate("attester.payment-risk.v1-key-01")


@pytest.fixture()
def trust_store(attester_key: SigningKey) -> AttesterTrustStore:
    return AttesterTrustStore([
        AttesterTrustAnchor(
            attester_id="attester.payment-risk.v1",
            kid=attester_key.kid,
            public_key=attester_key.public_key(),
            allowed_evidence_types=frozenset({"risk_assessment"}),
        ),
    ])


def _attest(attester: LocalAttester, **overrides) -> EvidenceAttestation:
    kwargs = dict(
        evidence_type="risk_assessment",
        claims={"risk_class": "low"},
        action_hash=_action_hash(),
        scope=SCOPE,
        provenance={"model": "payment-risk-v3", "input_ref": "trace-1"},
        issued_at=ISSUED_AT,
        not_before=NOT_BEFORE,
        expires_at=EXPIRES_AT,
        nonce="nonce-1",
    )
    kwargs.update(overrides)
    return attester.attest(**kwargs)


def _verify(raw, trust_store, **overrides):
    kwargs = dict(
        trust_store=trust_store,
        expected_action_hash=_action_hash(),
        expected_scope=SCOPE,
        now=ISSUED_AT + 100,
    )
    kwargs.update(overrides)
    return verify_attestation(raw, **kwargs)


# ---------------------------------------------------------------------------
# 1. valid trusted attestation -> VERIFIED
# ---------------------------------------------------------------------------


def test_01_valid_trusted_attestation_is_verified(attester, trust_store):
    att = _attest(attester)
    result = _verify(att.to_dict(), trust_store)
    assert result.overall_status is AttestationStatus.VERIFIED
    assert result.verified is True
    assert not result.failures
    assert result.attestation_id == att.attestation_id
    assert result.attester_id == att.attester_id
    # every structured dimension is True on the happy path
    for field in (
        "schema_supported", "structure_valid", "signer_verified", "signer_trusted",
        "evidence_type_allowed", "time_valid", "action_binding_valid",
        "payload_binding_valid", "scope_valid", "policy_binding_valid",
    ):
        assert getattr(result, field) is True, field


# ---------------------------------------------------------------------------
# 2. missing signature -> INVALID
# ---------------------------------------------------------------------------


def test_02_missing_signature_is_invalid(attester, trust_store):
    att = _attest(attester)
    raw = att.to_dict()
    del raw["sig"]
    result = _verify(raw, trust_store)
    assert result.overall_status is AttestationStatus.INVALID
    assert result.verified is False


# ---------------------------------------------------------------------------
# 3. forged signature -> INVALID
# ---------------------------------------------------------------------------


def test_03_forged_signature_is_invalid(attester, trust_store):
    att = _attest(attester)
    raw = att.to_dict()
    raw["sig"] = "A" * len(raw["sig"])
    result = _verify(raw, trust_store)
    assert result.overall_status is AttestationStatus.INVALID
    assert result.check("signature_verification").status.value == "FAIL"


# ---------------------------------------------------------------------------
# 4. modified claims after signing -> INVALID
# ---------------------------------------------------------------------------


def test_04_modified_claims_after_signing_is_invalid(attester, trust_store):
    att = _attest(attester)
    raw = att.to_dict()
    raw["claims"] = {"risk_class": "high"}
    result = _verify(raw, trust_store)
    assert result.overall_status is AttestationStatus.INVALID
    assert result.signer_verified is False


# ---------------------------------------------------------------------------
# 5. modified action_hash after signing -> INVALID
# ---------------------------------------------------------------------------


def test_05_modified_action_hash_after_signing_is_invalid(attester, trust_store):
    att = _attest(attester)
    raw = att.to_dict()
    raw["action_hash"] = hash_action("payment.delete_all_vendors")
    result = _verify(raw, trust_store)
    assert result.overall_status is AttestationStatus.INVALID
    # caught by signature verification before the binding check is ever reached
    assert result.signer_verified is False


# ---------------------------------------------------------------------------
# 6. modified scope after signing -> INVALID
# ---------------------------------------------------------------------------


def test_06_modified_scope_after_signing_is_invalid(attester, trust_store):
    att = _attest(attester)
    raw = att.to_dict()
    raw["scope"] = "payment:unlimited"
    result = _verify(raw, trust_store)
    assert result.overall_status is AttestationStatus.INVALID
    assert result.signer_verified is False


# ---------------------------------------------------------------------------
# 7. unknown attester -> INVALID
# ---------------------------------------------------------------------------


def test_07_unknown_attester_is_invalid(trust_store):
    # unsigned/signed with an attester_id the trust store has never heard of
    # (LocalAttester.attest() always uses its own attester_id, so build the
    # attestation manually to declare an arbitrary one).
    key = SigningKey.generate("some-kid")
    unsigned = EvidenceAttestation(
        schema_version=ATTESTATION_SCHEMA_VERSION,
        attestation_id="att-unknown-1",
        attester_id="attester.totally-unknown.v1",
        evidence_type="risk_assessment",
        claims={"risk_class": "low"},
        action_hash=_action_hash(),
        scope=SCOPE,
        provenance={},
        issued_at=ISSUED_AT, not_before=NOT_BEFORE, expires_at=EXPIRES_AT,
        nonce="nonce-x",
    )
    signed = sign_attestation(unsigned, key)
    result = _verify(signed.to_dict(), trust_store)
    assert result.overall_status is AttestationStatus.INVALID
    assert result.check("attester_trust").status.value == "FAIL"


# ---------------------------------------------------------------------------
# 8. unknown kid -> INVALID
# ---------------------------------------------------------------------------


def test_08_unknown_kid_is_invalid(trust_store):
    key = SigningKey.generate("kid-not-in-trust-store")
    attester = LocalAttester("attester.payment-risk.v1", key)
    att = _attest(attester)
    result = _verify(att.to_dict(), trust_store)
    assert result.overall_status is AttestationStatus.INVALID
    assert result.check("attester_trust").status.value == "FAIL"


# ---------------------------------------------------------------------------
# 9. key belonging to another attester -> INVALID
# ---------------------------------------------------------------------------


def test_09_key_belonging_to_another_attester_is_invalid(other_attester_key, trust_store):
    # other_attester_key shares the SAME kid string as the trust store's
    # registered anchor, but is a DIFFERENT private key, and is used here to
    # sign on behalf of a DIFFERENT attester_id than the one that kid is
    # registered to.
    impostor = LocalAttester("attester.impostor.v1", other_attester_key)
    att = _attest(impostor)
    result = _verify(att.to_dict(), trust_store)
    assert result.overall_status is AttestationStatus.INVALID
    # fails closed at trust resolution: (attester.impostor.v1, shared-kid)
    # was never registered, regardless of the kid string colliding.
    assert result.check("attester_trust").status.value == "FAIL"


# ---------------------------------------------------------------------------
# 10. attester not permitted for evidence_type -> INVALID
# ---------------------------------------------------------------------------


def test_10_attester_not_permitted_for_evidence_type_is_invalid(attester, trust_store):
    att = _attest(attester, evidence_type="fraud_signal")
    result = _verify(att.to_dict(), trust_store)
    assert result.overall_status is AttestationStatus.INVALID
    assert result.check("evidence_type_authorization").status.value == "FAIL"
    assert result.signer_verified is True  # reached past signature check
    assert result.evidence_type_allowed is False


# ---------------------------------------------------------------------------
# 11. expired attestation -> INVALID
# ---------------------------------------------------------------------------


def test_11_expired_attestation_is_invalid(attester, trust_store):
    att = _attest(attester)
    result = _verify(att.to_dict(), trust_store, now=EXPIRES_AT + 1)
    assert result.overall_status is AttestationStatus.INVALID
    assert result.check("validity_window").status.value == "FAIL"
    assert result.time_valid is False


def test_11b_now_equal_to_expires_at_is_invalid(attester, trust_store):
    # expires_at is exclusive: now == expires_at is already expired.
    att = _attest(attester)
    result = _verify(att.to_dict(), trust_store, now=EXPIRES_AT)
    assert result.overall_status is AttestationStatus.INVALID


# ---------------------------------------------------------------------------
# 12. not-yet-valid attestation -> INVALID
# ---------------------------------------------------------------------------


def test_12_not_yet_valid_attestation_is_invalid(attester, trust_store):
    # not_before must stay strictly before expires_at (structural rule,
    # test 19) -- push both forward so "now" can still precede not_before.
    att = _attest(attester, not_before=ISSUED_AT + 200, expires_at=ISSUED_AT + 500)
    result = _verify(att.to_dict(), trust_store, now=ISSUED_AT + 10)
    assert result.overall_status is AttestationStatus.INVALID
    assert result.check("validity_window").status.value == "FAIL"


# ---------------------------------------------------------------------------
# 13. wrong expected action_hash -> INVALID
# ---------------------------------------------------------------------------


def test_13_wrong_expected_action_hash_is_invalid(attester, trust_store):
    att = _attest(attester)
    result = _verify(att.to_dict(), trust_store, expected_action_hash=hash_action("payment.other"))
    assert result.overall_status is AttestationStatus.INVALID
    assert result.check("action_binding").status.value == "FAIL"
    assert result.action_binding_valid is False


# ---------------------------------------------------------------------------
# 14. wrong expected payload_hash -> INVALID
# ---------------------------------------------------------------------------


def test_14_wrong_expected_payload_hash_is_invalid(attester, trust_store):
    att = _attest(attester, payload_hash="sha256:" + "a" * 64)
    result = _verify(att.to_dict(), trust_store, expected_payload_hash="sha256:" + "b" * 64)
    assert result.overall_status is AttestationStatus.INVALID
    assert result.check("payload_binding").status.value == "FAIL"


def test_14b_correct_expected_payload_hash_is_verified(attester, trust_store):
    ph = "sha256:" + "a" * 64
    att = _attest(attester, payload_hash=ph)
    result = _verify(att.to_dict(), trust_store, expected_payload_hash=ph)
    assert result.overall_status is AttestationStatus.VERIFIED


# ---------------------------------------------------------------------------
# 15. wrong expected scope -> INVALID
# ---------------------------------------------------------------------------


def test_15_wrong_expected_scope_is_invalid(attester, trust_store):
    att = _attest(attester)
    result = _verify(att.to_dict(), trust_store, expected_scope="payment:unlimited")
    assert result.overall_status is AttestationStatus.INVALID
    assert result.check("scope_binding").status.value == "FAIL"


# ---------------------------------------------------------------------------
# 16. wrong expected policy version/hash -> INVALID
# ---------------------------------------------------------------------------


def test_16a_wrong_expected_policy_version_is_invalid(attester, trust_store):
    att = _attest(attester, policy_version="2026-09-01")
    result = _verify(att.to_dict(), trust_store, expected_policy_version="2026-01-01")
    assert result.overall_status is AttestationStatus.INVALID
    assert result.check("policy_binding").status.value == "FAIL"


def test_16b_wrong_expected_policy_hash_is_invalid(attester, trust_store):
    att = _attest(attester, policy_hash="sha256:" + "c" * 64)
    result = _verify(att.to_dict(), trust_store, expected_policy_hash="sha256:" + "d" * 64)
    assert result.overall_status is AttestationStatus.INVALID
    assert result.check("policy_binding").status.value == "FAIL"


def test_16c_correct_expected_policy_binding_is_verified(attester, trust_store):
    att = _attest(attester, policy_version="2026-09-01", policy_hash="sha256:" + "c" * 64)
    result = _verify(
        att.to_dict(), trust_store,
        expected_policy_version="2026-09-01", expected_policy_hash="sha256:" + "c" * 64,
    )
    assert result.overall_status is AttestationStatus.VERIFIED


# ---------------------------------------------------------------------------
# 17. unsupported schema version -> UNSUPPORTED_SCHEMA
# ---------------------------------------------------------------------------


def test_17_unsupported_schema_version_is_unsupported_schema(attester, trust_store):
    att = _attest(attester)
    raw = att.to_dict()
    raw["schema_version"] = "mcc-attestation/99"
    # tamper is fine here: schema-version check happens BEFORE signature
    # verification, so we don't even need a validly re-signed payload.
    result = _verify(raw, trust_store)
    assert result.overall_status is AttestationStatus.UNSUPPORTED_SCHEMA
    assert result.schema_supported is False


def test_17b_missing_schema_version_is_unsupported_schema(attester, trust_store):
    att = _attest(attester)
    raw = att.to_dict()
    del raw["schema_version"]
    result = _verify(raw, trust_store)
    assert result.overall_status is AttestationStatus.UNSUPPORTED_SCHEMA


# ---------------------------------------------------------------------------
# 18. malformed required fields -> INVALID
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("field", [
    "attestation_id", "attester_id", "evidence_type", "action_hash",
    "scope", "nonce", "kid", "sig",
])
def test_18a_missing_required_string_field_is_invalid(attester, trust_store, field):
    att = _attest(attester)
    raw = att.to_dict()
    del raw[field]
    result = _verify(raw, trust_store)
    assert result.overall_status is AttestationStatus.INVALID
    assert result.check("structural_validation").status.value == "FAIL"


@pytest.mark.parametrize("field", ["claims", "provenance"])
def test_18b_missing_required_object_field_is_invalid(attester, trust_store, field):
    att = _attest(attester)
    raw = att.to_dict()
    del raw[field]
    result = _verify(raw, trust_store)
    assert result.overall_status is AttestationStatus.INVALID


def test_18c_wrong_type_field_is_invalid(attester, trust_store):
    att = _attest(attester)
    raw = att.to_dict()
    raw["claims"] = "not-a-dict"
    result = _verify(raw, trust_store)
    assert result.overall_status is AttestationStatus.INVALID


def test_18d_undeclared_field_is_invalid(attester, trust_store):
    att = _attest(attester)
    raw = att.to_dict()
    raw["execution_allowed"] = True  # attempted authority injection
    result = _verify(raw, trust_store)
    assert result.overall_status is AttestationStatus.INVALID
    assert result.check("structural_validation").status.value == "FAIL"


def test_18e_empty_string_field_is_invalid(attester, trust_store):
    att = _attest(attester)
    raw = att.to_dict()
    raw["scope"] = ""
    result = _verify(raw, trust_store)
    assert result.overall_status is AttestationStatus.INVALID


# ---------------------------------------------------------------------------
# 19. malformed timestamp ordering -> INVALID
# ---------------------------------------------------------------------------


def test_19_expires_at_before_not_before_is_invalid(attester, trust_store):
    with pytest.raises(MalformedAttestationError):
        EvidenceAttestation.from_dict({
            "schema_version": ATTESTATION_SCHEMA_VERSION,
            "attestation_id": "att-bad-order",
            "attester_id": "attester.payment-risk.v1",
            "evidence_type": "risk_assessment",
            "claims": {},
            "action_hash": _action_hash(),
            "scope": SCOPE,
            "provenance": {},
            "issued_at": ISSUED_AT,
            "not_before": 2_000,
            "expires_at": 1_000,  # before not_before
            "nonce": "n",
            "kid": "k",
            "sig": "s",
        })


def test_19b_expires_at_equal_not_before_is_invalid():
    with pytest.raises(MalformedAttestationError):
        EvidenceAttestation.from_dict({
            "schema_version": ATTESTATION_SCHEMA_VERSION,
            "attestation_id": "att-bad-order-2",
            "attester_id": "attester.payment-risk.v1",
            "evidence_type": "risk_assessment",
            "claims": {},
            "action_hash": _action_hash(),
            "scope": SCOPE,
            "provenance": {},
            "issued_at": ISSUED_AT,
            "not_before": 1_000,
            "expires_at": 1_000,
            "nonce": "n",
            "kid": "k",
            "sig": "s",
        })


def test_19c_verify_end_to_end_reports_invalid_via_structural_validation(attester, trust_store):
    # Even reaching the verifier (not just direct from_dict), a bad ordering
    # is caught at structural validation, before signature is ever checked.
    att = _attest(attester)
    raw = att.to_dict()
    raw["not_before"] = raw["expires_at"]
    result = _verify(raw, trust_store)
    assert result.overall_status is AttestationStatus.INVALID
    assert result.check("structural_validation").status.value == "FAIL"


# ---------------------------------------------------------------------------
# 20. malformed signature encoding -> INVALID
# ---------------------------------------------------------------------------


def test_20_malformed_signature_encoding_is_invalid(attester, trust_store):
    att = _attest(attester)
    raw = att.to_dict()
    raw["sig"] = "not-valid-base64!!!"
    result = _verify(raw, trust_store)
    assert result.overall_status is AttestationStatus.INVALID
    assert result.check("signature_verification").status.value == "FAIL"


# ---------------------------------------------------------------------------
# 21. verifier internal exception -> INVALID fail-closed
# ---------------------------------------------------------------------------


def test_21_verifier_internal_exception_is_invalid_fail_closed(attester):
    att = _attest(attester)

    class _ExplodingTrustStore:
        def resolve(self, attester_id, kid):
            raise RuntimeError("simulated trust-store failure")

    result = verify_attestation(
        att.to_dict(), trust_store=_ExplodingTrustStore(),
        expected_action_hash=_action_hash(), expected_scope=SCOPE, now=ISSUED_AT + 10,
    )
    assert result.overall_status is AttestationStatus.INVALID
    assert result.verified is False
    assert any("verifier_internal_error" in f for f in result.failures)


def test_21b_no_exception_path_produces_verified(attester):
    att = _attest(attester)

    class _ExplodingTrustStore:
        def resolve(self, attester_id, kid):
            raise ValueError("boom")

        def evidence_type_allowed(self, anchor, evidence_type):
            raise AssertionError("should never be reached")

    result = verify_attestation(
        att.to_dict(), trust_store=_ExplodingTrustStore(),
        expected_action_hash=_action_hash(), expected_scope=SCOPE, now=ISSUED_AT + 10,
    )
    assert result.overall_status is not AttestationStatus.VERIFIED


# ---------------------------------------------------------------------------
# 22. canonical signing of equivalent data is deterministic
# ---------------------------------------------------------------------------


def test_22_canonical_signing_is_deterministic_regardless_of_key_order(attester_key):
    attester = LocalAttester("attester.payment-risk.v1", attester_key)
    claims_a = {"risk_class": "low", "score": 12}
    claims_b = {"score": 12, "risk_class": "low"}  # same content, different insertion order
    fixed_id = "att-deterministic-1"

    att_a = attester.attest(
        evidence_type="risk_assessment", claims=claims_a, action_hash=_action_hash(),
        scope=SCOPE, provenance={"model": "m", "input_ref": "r"},
        issued_at=ISSUED_AT, not_before=NOT_BEFORE, expires_at=EXPIRES_AT,
        nonce="nonce-fixed", attestation_id=fixed_id,
    )
    att_b = attester.attest(
        evidence_type="risk_assessment", claims=claims_b, action_hash=_action_hash(),
        scope=SCOPE, provenance={"model": "m", "input_ref": "r"},
        issued_at=ISSUED_AT, not_before=NOT_BEFORE, expires_at=EXPIRES_AT,
        nonce="nonce-fixed", attestation_id=fixed_id,
    )
    assert canonical_bytes(att_a.unsigned_dict()) == canonical_bytes(att_b.unsigned_dict())
    assert att_a.sig == att_b.sig  # identical canonical content -> identical Ed25519 signature


def test_22b_canonical_bytes_differ_for_different_content(attester_key):
    attester = LocalAttester("attester.payment-risk.v1", attester_key)
    att_a = _attest(attester, claims={"risk_class": "low"})
    att_b = _attest(attester, claims={"risk_class": "high"})
    assert att_a.sig != att_b.sig


# ---------------------------------------------------------------------------
# 23. attestation carries no executable verdict / authority grant semantics
# ---------------------------------------------------------------------------


_AUTHORITY_LIKE_NAMES = {
    "verdict", "decision", "allow", "deny", "escalate", "constrain",
    "authority", "authorized", "authorization", "token_issued",
    "execution_allowed", "permit", "grant",
}


def test_23a_attestation_field_set_carries_no_authority_grant_field():
    from mcc_attestation.schema import _ALL_ALLOWED_FIELDS

    lowered = {f.lower() for f in _ALL_ALLOWED_FIELDS}
    overlap = lowered & _AUTHORITY_LIKE_NAMES
    assert not overlap, f"EvidenceAttestation schema must carry no authority-grant field, found: {overlap}"


def test_23b_attestation_status_enum_carries_no_allow_like_member():
    allowed_values = {s.value.lower() for s in AttestationStatus}
    overlap = allowed_values & {"allow", "authorized", "executed", "grant"}
    assert not overlap
    assert allowed_values == {"verified", "invalid", "unsupported_schema"}


def test_23c_verified_result_to_dict_carries_no_authority_field(attester, trust_store):
    att = _attest(attester)
    result = _verify(att.to_dict(), trust_store)
    assert result.overall_status is AttestationStatus.VERIFIED
    d = result.to_dict()
    overlap = {k.lower() for k in d} & _AUTHORITY_LIKE_NAMES
    assert not overlap, f"verification result must carry no authority-grant field, found: {overlap}"


def test_23d_module_exposes_no_authorize_or_execute_function():
    import mcc_attestation

    public = {name for name in dir(mcc_attestation) if not name.startswith("_")}
    for forbidden in ("authorize", "execute", "allow", "grant_authority", "issue_token", "decide"):
        assert forbidden not in {n.lower() for n in public}, forbidden


# ---------------------------------------------------------------------------
# Additional structural / trust-model coverage beyond the mandatory 23
# ---------------------------------------------------------------------------


def test_double_signing_is_refused(attester_key):
    attester = LocalAttester("attester.payment-risk.v1", attester_key)
    att = _attest(attester)
    with pytest.raises(Exception):
        sign_attestation(att, attester_key)


def test_trust_store_revocation_fails_closed(attester, trust_store, attester_key):
    att = _attest(attester)
    trust_store.revoke("attester.payment-risk.v1", attester_key.kid)
    result = _verify(att.to_dict(), trust_store)
    assert result.overall_status is AttestationStatus.INVALID
    assert result.check("attester_trust").status.value == "FAIL"


def test_trust_anchor_requires_at_least_one_evidence_type(attester_key):
    with pytest.raises(Exception):
        AttesterTrustAnchor(
            attester_id="attester.x", kid=attester_key.kid,
            public_key=attester_key.public_key(), allowed_evidence_types=frozenset(),
        )


def test_duplicate_trust_anchor_registration_refused(attester_key):
    store = AttesterTrustStore()
    anchor = AttesterTrustAnchor(
        attester_id="attester.x", kid=attester_key.kid,
        public_key=attester_key.public_key(), allowed_evidence_types=frozenset({"t"}),
    )
    store.add(anchor)
    with pytest.raises(Exception):
        store.add(anchor)


def test_verification_result_is_not_a_bare_boolean(attester, trust_store):
    att = _attest(attester)
    result = _verify(att.to_dict(), trust_store)
    assert not isinstance(result, bool)
    assert hasattr(result, "overall_status")
    assert hasattr(result, "checks")


def test_input_not_a_dict_is_invalid(trust_store):
    result = _verify("not-a-dict", trust_store)
    assert result.overall_status is AttestationStatus.INVALID


def test_input_none_is_invalid(trust_store):
    result = _verify(None, trust_store)
    assert result.overall_status is AttestationStatus.INVALID


def test_deep_copy_of_valid_attestation_still_verifies(attester, trust_store):
    # A defensive sanity check that verification does not depend on object
    # identity / aliasing of claims or provenance dicts.
    att = _attest(attester)
    raw = copy.deepcopy(att.to_dict())
    result = _verify(raw, trust_store)
    assert result.overall_status is AttestationStatus.VERIFIED
