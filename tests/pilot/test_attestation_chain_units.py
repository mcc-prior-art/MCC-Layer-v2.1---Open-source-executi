"""Offline unit tests (PR-6) for the attestation-aware full-chain pilot's
own config/evidence primitives -- no real Gateway or Attester process
needed. Real-process-boundary behavior is covered separately in
``test_attestation_chain_pilot.py``.
"""

from __future__ import annotations

import pytest

from pilot.reference_python.attestation_config import (
    AttestationChainConfig,
    AttestationChainConfigError,
)
from pilot.reference_python.attestation_evidence import (
    AttestationChainEvidence,
    build_attestation_summary,
    validate_attestation_evidence,
)

VALID_KWARGS = dict(
    gateway_url="http://127.0.0.1:8001", attester_url="http://127.0.0.1:8100",
    attester_auth_secret="s3cr3t", gateway_api_key="demo-key",
)


def test_config_rejects_non_http_gateway_url():
    with pytest.raises(AttestationChainConfigError):
        AttestationChainConfig(**{**VALID_KWARGS, "gateway_url": "ftp://x"})


def test_config_rejects_non_http_attester_url():
    with pytest.raises(AttestationChainConfigError):
        AttestationChainConfig(**{**VALID_KWARGS, "attester_url": "not-a-url"})


def test_config_rejects_empty_attester_auth_secret():
    with pytest.raises(AttestationChainConfigError):
        AttestationChainConfig(**{**VALID_KWARGS, "attester_auth_secret": ""})


def test_config_rejects_empty_gateway_api_key():
    with pytest.raises(AttestationChainConfigError):
        AttestationChainConfig(**{**VALID_KWARGS, "gateway_api_key": ""})


def test_config_rejects_invalid_mode():
    with pytest.raises(AttestationChainConfigError):
        AttestationChainConfig(**{**VALID_KWARGS, "mode": "yolo"})


def test_config_rejects_non_positive_timeout():
    with pytest.raises(AttestationChainConfigError):
        AttestationChainConfig(**{**VALID_KWARGS, "timeout_seconds": 0})


def test_config_defaults_to_observe_mode():
    config = AttestationChainConfig(**VALID_KWARGS)
    assert config.mode == "observe"


def test_config_from_env_fails_closed_when_required_vars_missing():
    with pytest.raises(AttestationChainConfigError):
        AttestationChainConfig.from_env({})


def test_config_from_env_builds_from_full_environment():
    env = {
        "MCC_PILOT_GATEWAY_URL": "http://127.0.0.1:8001",
        "MCC_PILOT_ATTESTATION_ATTESTER_URL": "http://127.0.0.1:8100",
        "MCC_PILOT_ATTESTATION_ATTESTER_AUTH_SECRET": "s3cr3t",
        "MCC_PILOT_API_KEY": "demo-key",
        "MCC_PILOT_MODE": "enforced",
    }
    config = AttestationChainConfig.from_env(env)
    assert config.mode == "enforced"
    assert config.gateway_url == "http://127.0.0.1:8001"


def test_build_attestation_summary_never_includes_sig_claims_or_provenance():
    raw = {
        "attester_id": "a.risk.v1", "kid": "k1", "attestation_id": "att-1",
        "evidence_type": "risk_assessment", "claims": {"risk_class": "low"},
        "provenance": {"model": "secret-internal-model-name"}, "issued_at": 1, "expires_at": 2,
        "sig": "deadbeef-signature-material",
    }
    summary = build_attestation_summary(raw)
    assert "sig" not in summary
    assert "claims" not in summary
    assert "provenance" not in summary
    assert summary["attestation_id"] == "att-1"
    assert summary["evidence_digest_client_computed"].startswith("sha256:")


def test_evidence_finalize_excludes_secrets_from_config_fingerprint():
    config = AttestationChainConfig(**VALID_KWARGS)
    summary = build_attestation_summary({
        "attester_id": "a", "kid": "k", "attestation_id": "att-1",
        "evidence_type": "risk_assessment", "issued_at": 1, "expires_at": 2,
    })
    evidence = AttestationChainEvidence(
        config=config, mode="observe", action="send_notification", resource="notifications",
        attestation_summary=summary,
    )
    finalized = evidence.finalize()
    assert config.attester_auth_secret not in str(finalized)
    assert config.gateway_api_key not in str(finalized)
    assert finalized["mode"] == "observe"
    assert finalized["known_limitations"]  # never silently empty about what's not included


def test_evidence_validates_against_schema():
    config = AttestationChainConfig(**VALID_KWARGS)
    summary = build_attestation_summary({
        "attester_id": "a", "kid": "k", "attestation_id": "att-1",
        "evidence_type": "risk_assessment", "issued_at": 1, "expires_at": 2,
    })
    evidence = AttestationChainEvidence(
        config=config, mode="enforced", action="send_notification", resource="notifications",
        attestation_summary=summary, gateway_decision="ALLOW", gateway_status="EXECUTED",
        gateway_reason="ok", audit_ref="deadbeef", execution_receipt_present=True,
        actuated=True, attester_service_calls=1, gateway_calls=1,
    )
    validate_attestation_evidence(evidence.finalize())  # raises on schema violation


def test_evidence_export_writes_file_and_refuses_overwrite(tmp_path):
    config = AttestationChainConfig(**VALID_KWARGS)
    summary = build_attestation_summary({
        "attester_id": "a", "kid": "k", "attestation_id": "att-1",
        "evidence_type": "risk_assessment", "issued_at": 1, "expires_at": 2,
    })
    evidence = AttestationChainEvidence(
        config=config, mode="observe", action="send_notification", resource="notifications",
        attestation_summary=summary, run_correlation_id="fixed-id-for-test",
    )
    path = evidence.finalize_and_export(str(tmp_path))
    assert path.exists()
    with pytest.raises(FileExistsError):
        evidence.finalize_and_export(str(tmp_path))
