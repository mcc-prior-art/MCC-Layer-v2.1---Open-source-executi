"""PR-4 — Independent Attester Service: unit/behavioral tests.

Covers required items B-H (private-key-vs-runtime E excepted for the
config-loader half, see below; process isolation is a separate file):

* B. CALLER CANNOT SELF-ATTEST -- strict schema rejects every bypass-shaped
  field.
* C. PROVIDER OWNS ASSESSMENT -- signed claims/evidence_type/provenance
  come from the configured AssessmentProvider only.
* D. SERVICE OWNS BINDING -- action_hash/payload_hash/scope are derived by
  the service from the actual request, never caller-substitutable.
* E. PRIVATE KEY FAILURE -- missing/malformed key config fails closed
  (config-loader half); a signing failure at request time also fails
  closed (service half).
* F. PROVIDER FAILURE -- unavailable/raising/malformed-output provider
  fails closed, no signed artifact.
* G. AUTH FAILURE -- missing/wrong service auth fails closed BEFORE
  assessment or signing are ever attempted.
* H. SIGNATURE VERIFICATION -- a real artifact from this service verifies
  through the existing, unmodified MCC-AT-001 verifier.
"""

from __future__ import annotations

import asyncio
import tempfile
from pathlib import Path
from typing import Any, Dict, Optional

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from fastapi.testclient import TestClient

from mcc_attestation import AttesterTrustAnchor, AttesterTrustStore, verify_attestation
from mcc_attester_service import (
    AssessmentProvider,
    AssessmentProviderError,
    AssessmentResult,
    AttesterService,
    AttesterServiceConfig,
    AttesterServiceConfigError,
    DeterministicTestProvider,
    SigningFailedError,
    attester_service_config_from_env,
    build_attester_app,
)
from mcc_core.signing import SigningKey, hash_action, hash_payload

run = asyncio.run

NOW = 1_800_000_000
ACTION = "send_payment"
RESOURCE = "vendor-1"
PAYLOAD = {"amount": 100, "currency": "EUR"}
AUTH_SECRET = "attester-service-auth-secret-01"
SCOPE_TEMPLATE = "payment:{resource}"


def _key(kid: str = "attester.payment-risk.v1-key-01") -> SigningKey:
    return SigningKey.generate(kid)


def _config(key: SigningKey, **overrides) -> AttesterServiceConfig:
    kw = dict(
        attester_id="attester.payment-risk.v1", signing_key=key, auth_secret=AUTH_SECRET,
        scope_template=SCOPE_TEMPLATE, validity_seconds=300,
    )
    kw.update(overrides)
    return AttesterServiceConfig(**kw)


def _provider(**table) -> DeterministicTestProvider:
    return DeterministicTestProvider(table)


def _low_risk_result(**overrides) -> AssessmentResult:
    kw = dict(evidence_type="risk_assessment", claims={"risk_class": "low"},
              provenance={"model": "payment-risk-v3"})
    kw.update(overrides)
    return AssessmentResult(**kw)


def _service(key: SigningKey, provider: AssessmentProvider, **config_overrides) -> AttesterService:
    return AttesterService(config=_config(key, **config_overrides), provider=provider,
                           clock=lambda: NOW)


def _attest(service: AttesterService, *, action=ACTION, resource=RESOURCE, payload=None):
    return run(service.attest(action=action, resource=resource, payload=payload or dict(PAYLOAD)))


def _client(key: SigningKey, provider: AssessmentProvider, **config_overrides) -> TestClient:
    config = _config(key, **config_overrides)
    app = build_attester_app(config=config, provider=provider)
    return TestClient(app)


def _pem_path(tmp_path: Path, private_key: Ed25519PrivateKey) -> str:
    pem = private_key.private_bytes(
        serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    )
    path = tmp_path / "attester_key.pem"
    path.write_bytes(pem)
    return str(path)


# ---------------------------------------------------------------------------
# B. CALLER CANNOT SELF-ATTEST -- schema rejects every bypass-shaped field.
# ---------------------------------------------------------------------------


_BYPASS_FIELDS = {
    "claims": {"risk_class": "low"},
    "risk_class": "low",
    "attester_id": "attester.forged",
    "kid": "forged-kid",
    "sig": "Zm9yZ2Vk",
    "nonce": "forged-nonce",
    "issued_at": NOW,
    "not_before": NOW,
    "expires_at": NOW + 300,
    "action_hash": "sha256:" + "0" * 64,
    "payload_hash": "sha256:" + "1" * 64,
    "evidence_digest": "sha256:" + "2" * 64,
    "verified": True,
    "verification": {"overall_status": "VERIFIED"},
    "provenance": {"model": "forged"},
    "evidence_type": "forged_type",
    "attestation_id": "att-forged",
}


@pytest.mark.parametrize("field_name", sorted(_BYPASS_FIELDS))
def test_b_caller_cannot_supply_a_bypass_shaped_field(field_name):
    key = _key()
    client = _client(key, _provider(**{ACTION: _low_risk_result()}))
    body = {"action": ACTION, "resource": RESOURCE, "payload": dict(PAYLOAD),
            field_name: _BYPASS_FIELDS[field_name]}
    resp = client.post("/attest", json=body, headers={"X-Attester-Auth": AUTH_SECRET})
    assert resp.status_code == 422
    detail = resp.json()["detail"]
    assert any(d.get("loc", [None, None])[-1] == field_name for d in detail), detail


def test_b_a_well_formed_request_with_no_bypass_fields_succeeds():
    key = _key()
    client = _client(key, _provider(**{ACTION: _low_risk_result()}))
    resp = client.post(
        "/attest", json={"action": ACTION, "resource": RESOURCE, "payload": dict(PAYLOAD)},
        headers={"X-Attester-Auth": AUTH_SECRET},
    )
    assert resp.status_code == 200, resp.text


# ---------------------------------------------------------------------------
# C. PROVIDER OWNS ASSESSMENT -- signed claims/evidence_type/provenance come
#    from the provider, never from the caller (who has no way to supply
#    them at all -- proven above) and are exactly what the provider
#    returned.
# ---------------------------------------------------------------------------


def test_c_signed_claims_evidence_type_provenance_match_the_provider_exactly():
    key = _key()
    result = AssessmentResult(
        evidence_type="risk_assessment", claims={"risk_class": "low", "score": 7},
        provenance={"model": "payment-risk-v3", "version": "3.2.1"},
    )
    service = _service(key, _provider(**{ACTION: result}))
    raw = _attest(service)
    assert raw["evidence_type"] == "risk_assessment"
    assert raw["claims"] == {"risk_class": "low", "score": 7}
    assert raw["provenance"] == {"model": "payment-risk-v3", "version": "3.2.1"}


def test_c_different_payload_content_does_not_change_provider_controlled_fields():
    """The caller can vary payload/resource freely, but cannot influence
    evidence_type/claims/provenance through them -- those come only from
    whichever provider entry the ACTION resolves to."""
    key = _key()
    result = _low_risk_result()
    service = _service(key, _provider(**{ACTION: result}))
    raw_a = _attest(service, payload={"amount": 1})
    raw_b = _attest(service, payload={"amount": 999999, "note": "unrelated"})
    assert raw_a["claims"] == raw_b["claims"] == dict(result.claims)
    assert raw_a["evidence_type"] == raw_b["evidence_type"] == result.evidence_type


# ---------------------------------------------------------------------------
# D. SERVICE OWNS BINDING -- action_hash/payload_hash/scope are derived by
#    the service from the actual request; the caller has no way to submit a
#    substitute (proven structurally above) and the derived values are
#    exactly what the shared mcc_core.signing primitives compute.
# ---------------------------------------------------------------------------


def test_d_action_hash_and_payload_hash_are_derived_from_the_actual_request():
    key = _key()
    service = _service(key, _provider(**{ACTION: _low_risk_result()}))
    raw = _attest(service, payload={"amount": 42})
    assert raw["action_hash"] == hash_action(ACTION)
    assert raw["payload_hash"] == hash_payload({"amount": 42})


def test_d_different_payloads_yield_different_payload_hashes():
    key = _key()
    service = _service(key, _provider(**{ACTION: _low_risk_result()}))
    raw_a = _attest(service, payload={"amount": 1})
    raw_b = _attest(service, payload={"amount": 2})
    assert raw_a["payload_hash"] != raw_b["payload_hash"]


def test_d_scope_is_derived_from_the_trusted_server_side_template():
    key = _key()
    service = _service(key, _provider(**{ACTION: _low_risk_result()}),
                       scope_template="payment:{resource}")
    raw = _attest(service, resource="vendor-42")
    assert raw["scope"] == "payment:vendor-42"


# ---------------------------------------------------------------------------
# E. PRIVATE KEY FAILURE -- missing/malformed key config fails closed.
# ---------------------------------------------------------------------------


def test_e_missing_signing_key_path_env_fails_closed_at_config_load():
    env = {
        "MCC_ATTESTER_ID": "attester.payment-risk.v1",
        "MCC_ATTESTER_KEY_ID": "k1",
        "MCC_ATTESTER_SERVICE_AUTH_SECRET": AUTH_SECRET,
        "MCC_ATTESTER_SCOPE_TEMPLATE": SCOPE_TEMPLATE,
    }
    with pytest.raises(AttesterServiceConfigError):
        attester_service_config_from_env(env)


def test_e_malformed_signing_key_file_fails_closed_at_config_load(tmp_path):
    bad_path = tmp_path / "not_a_key.pem"
    bad_path.write_text("this is not a PEM key")
    env = {
        "MCC_ATTESTER_ID": "attester.payment-risk.v1",
        "MCC_ATTESTER_SIGNING_KEY_PATH": str(bad_path),
        "MCC_ATTESTER_KEY_ID": "k1",
        "MCC_ATTESTER_SERVICE_AUTH_SECRET": AUTH_SECRET,
        "MCC_ATTESTER_SCOPE_TEMPLATE": SCOPE_TEMPLATE,
    }
    with pytest.raises(AttesterServiceConfigError):
        attester_service_config_from_env(env)


def test_e_config_loader_never_silently_generates_a_key(tmp_path):
    """There is no code path in attester_service_config_from_env that
    fabricates a signing key when none is configured -- every failure
    above raises, never falls back to SigningKey.generate()."""
    env: Dict[str, str] = {}
    with pytest.raises(AttesterServiceConfigError):
        attester_service_config_from_env(env)


def test_e_auth_secret_equal_to_the_public_key_value_fails_closed():
    """AIS-KEY-003: the one 'key-shaped' string genuinely comparable to
    auth_secret in this design is the Attester's PUBLIC key value -- a
    plausible copy-paste misconfiguration. A literal comparison against the
    PRIVATE key is not implementable (SigningKey never exposes it as a
    plaintext value) and is not what this guards against."""
    key = _key()
    with pytest.raises(AttesterServiceConfigError):
        AttesterServiceConfig(
            attester_id="attester.payment-risk.v1", signing_key=key,
            auth_secret=key.public_key_b64(), scope_template=SCOPE_TEMPLATE,
            validity_seconds=300,
        )


def test_e_auth_secret_distinct_from_public_key_value_succeeds():
    key = _key()
    config = AttesterServiceConfig(
        attester_id="attester.payment-risk.v1", signing_key=key,
        auth_secret=AUTH_SECRET, scope_template=SCOPE_TEMPLATE, validity_seconds=300,
    )
    assert config.auth_secret == AUTH_SECRET
    assert config.auth_secret != key.public_key_b64()


def test_e_a_valid_pem_key_file_loads_successfully(tmp_path):
    private_key = Ed25519PrivateKey.generate()
    path = _pem_path(tmp_path, private_key)
    env = {
        "MCC_ATTESTER_ID": "attester.payment-risk.v1",
        "MCC_ATTESTER_SIGNING_KEY_PATH": path,
        "MCC_ATTESTER_KEY_ID": "k1",
        "MCC_ATTESTER_SERVICE_AUTH_SECRET": AUTH_SECRET,
        "MCC_ATTESTER_SCOPE_TEMPLATE": SCOPE_TEMPLATE,
    }
    config = attester_service_config_from_env(env)
    assert config.signing_key.kid == "k1"


def test_e_signing_failure_at_request_time_fails_closed_no_artifact():
    """Defense in depth beyond config-load-time validation: if signing
    itself fails for any reason (simulated here via a broken key double),
    the service raises and returns no artifact -- never a partial one."""

    class _BrokenSigningKey:
        kid = "broken"

        def sign_token(self, claims):
            raise RuntimeError("simulated HSM/key failure")

    key = _key()
    config = AttesterServiceConfig(
        attester_id="attester.payment-risk.v1", signing_key=key, auth_secret=AUTH_SECRET,
        scope_template=SCOPE_TEMPLATE, validity_seconds=300,
    )
    # Swap in a broken signing key AFTER construction (bypassing __post_init__'s
    # isinstance check, which only runs once at construction) to simulate a
    # key that fails at the moment of use.
    object.__setattr__(config, "signing_key", _BrokenSigningKey())
    service = AttesterService(config=config, provider=_provider(**{ACTION: _low_risk_result()}),
                              clock=lambda: NOW)
    with pytest.raises(SigningFailedError):
        _attest(service)


# ---------------------------------------------------------------------------
# F. PROVIDER FAILURE -- unavailable/raising/malformed-output provider
#    fails closed; no signed artifact is ever produced.
# ---------------------------------------------------------------------------


class _RaisingProvider(AssessmentProvider):
    async def assess(self, *, action, resource, payload):
        raise RuntimeError("simulated provider outage")


class _MalformedOutputProvider(AssessmentProvider):
    async def assess(self, *, action, resource, payload):
        return {"not": "an AssessmentResult"}  # wrong type entirely


def test_f_provider_unconfigured_action_fails_closed():
    key = _key()
    service = _service(key, _provider())  # empty table
    with pytest.raises(AssessmentProviderError):
        _attest(service)


def test_f_provider_raising_arbitrary_exception_fails_closed():
    key = _key()
    service = AttesterService(config=_config(key), provider=_RaisingProvider(), clock=lambda: NOW)
    with pytest.raises(AssessmentProviderError):
        _attest(service)


def test_f_provider_malformed_output_fails_closed():
    key = _key()
    service = AttesterService(config=_config(key), provider=_MalformedOutputProvider(),
                              clock=lambda: NOW)
    with pytest.raises(AssessmentProviderError):
        _attest(service)


def test_f_provider_failure_via_http_returns_no_artifact():
    key = _key()
    client = TestClient(build_attester_app(config=_config(key), provider=_RaisingProvider()))
    resp = client.post(
        "/attest", json={"action": ACTION, "resource": RESOURCE, "payload": dict(PAYLOAD)},
        headers={"X-Attester-Auth": AUTH_SECRET},
    )
    assert resp.status_code == 503
    body = resp.json()
    assert "sig" not in body and "kid" not in body and "claims" not in body


# ---------------------------------------------------------------------------
# G. AUTH FAILURE -- missing/wrong service auth fails closed BEFORE
#    assessment/signing is even attempted.
# ---------------------------------------------------------------------------


class _SpyProvider(AssessmentProvider):
    def __init__(self, result: AssessmentResult) -> None:
        self.calls = 0
        self._result = result

    async def assess(self, *, action, resource, payload):
        self.calls += 1
        return self._result


def test_g_missing_auth_header_rejected_before_provider_is_called():
    key = _key()
    spy = _SpyProvider(_low_risk_result())
    client = TestClient(build_attester_app(config=_config(key), provider=spy))
    resp = client.post("/attest", json={"action": ACTION, "resource": RESOURCE, "payload": {}})
    assert resp.status_code == 401
    assert spy.calls == 0


def test_g_wrong_auth_header_rejected_before_provider_is_called():
    key = _key()
    spy = _SpyProvider(_low_risk_result())
    client = TestClient(build_attester_app(config=_config(key), provider=spy))
    resp = client.post(
        "/attest", json={"action": ACTION, "resource": RESOURCE, "payload": {}},
        headers={"X-Attester-Auth": "totally-wrong-secret-value"},
    )
    assert resp.status_code == 401
    assert spy.calls == 0


def test_g_correct_auth_header_allows_the_provider_to_be_called():
    key = _key()
    spy = _SpyProvider(_low_risk_result())
    client = TestClient(build_attester_app(config=_config(key), provider=spy))
    resp = client.post(
        "/attest", json={"action": ACTION, "resource": RESOURCE, "payload": {}},
        headers={"X-Attester-Auth": AUTH_SECRET},
    )
    assert resp.status_code == 200
    assert spy.calls == 1


# ---------------------------------------------------------------------------
# H. SIGNATURE VERIFICATION -- a real artifact from this service verifies
#    through the existing, UNMODIFIED MCC-AT-001 verifier.
# ---------------------------------------------------------------------------


def test_h_service_artifact_verifies_through_the_existing_pr1_verifier():
    key = _key()
    service = _service(key, _provider(**{ACTION: _low_risk_result()}))
    raw = _attest(service)

    trust_store = AttesterTrustStore([
        AttesterTrustAnchor("attester.payment-risk.v1", key.kid, key.public_key(),
                            frozenset({"risk_assessment"})),
    ])
    result = verify_attestation(
        raw, trust_store=trust_store, expected_action_hash=hash_action(ACTION),
        expected_scope=f"payment:{RESOURCE}", now=NOW + 10,
        expected_payload_hash=hash_payload(PAYLOAD),
    )
    assert result.verified, result.failures


def test_h_service_artifact_fails_verification_under_the_wrong_trust_key():
    key = _key()
    other_key = _key("some-other-key")
    service = _service(key, _provider(**{ACTION: _low_risk_result()}))
    raw = _attest(service)

    trust_store = AttesterTrustStore([
        AttesterTrustAnchor("attester.payment-risk.v1", other_key.kid, other_key.public_key(),
                            frozenset({"risk_assessment"})),
    ])
    result = verify_attestation(
        raw, trust_store=trust_store, expected_action_hash=hash_action(ACTION),
        expected_scope=f"payment:{RESOURCE}", now=NOW + 10,
    )
    assert not result.verified
