"""Deterministic verification of an EvidenceAttestation.

Performs cryptographic and structural checks only. The verifier MUST NOT,
and does not, determine whether an attestation's semantic assessment
(``claims``) is correct — it determines whether the assertion is authentic,
trusted, current, integrity-protected, and correctly bound. See
``docs/ATTESTATION_ARCHITECTURE.md`` for the full doctrine.

Verification order (fixed, deterministic):

    1. input/type validation
    2. schema version
    3. required fields / structural validation
    4. attester identity (structural — part of step 3)
    5. key lookup/trust
    6. signature verification
    7. evidence_type authorization
    8. issued_at / not_before / expires_at
    9. action_hash binding
    10. optional payload_hash binding
    11. expected scope
    12. expected policy binding
    13. success

Any failing step returns a fail-closed structured result immediately; later
steps are not evaluated once one has failed (they would be moot — the
overall result is already INVALID). Any unexpected exception anywhere in
this function is caught and resolves to INVALID; no exception path can
produce a VERIFIED result.

Replay (nonce consumption) is intentionally NOT performed here — the
attestation's ``nonce`` field is carried and structurally validated (as part
of step 3), but consuming it against a registry is a Control/runtime
responsibility deferred to PR-2, per the task's explicit scope boundary.
This module does not create, or depend on, a second nonce registry.
"""

from __future__ import annotations

from typing import Any, List, Optional

from mcc_core.signing import verify_token

from .schema import (
    AttestationStatus,
    AttestationVerificationResult,
    CheckResult,
    CheckStatus,
    EvidenceAttestation,
    MalformedAttestationError,
    SUPPORTED_SCHEMA_VERSIONS,
)
from .trust import AttesterTrustStore


def verify_attestation(
    raw_attestation: Any,
    *,
    trust_store: AttesterTrustStore,
    expected_action_hash: str,
    expected_scope: str,
    now: int,
    expected_payload_hash: Optional[str] = None,
    expected_policy_hash: Optional[str] = None,
    expected_policy_version: Optional[str] = None,
) -> AttestationVerificationResult:
    """Verify ``raw_attestation`` (a ``dict``, as received over any
    transport) against ``trust_store`` and the caller's expected bindings.

    ``VERIFIED`` means only that the attestation is cryptographically and
    structurally valid under the supplied trust and expected bindings. It
    does not mean the semantic assessment in ``claims`` is correct, and it
    grants no execution authority by itself — interpreting a VERIFIED
    attestation into an authorization decision is a Control-layer concern
    outside this function (PR-2/PR-3).
    """
    checks: List[CheckResult] = []
    failures: List[str] = []
    warnings: List[str] = []

    def add(name: str, status: CheckStatus, detail: str = "") -> None:
        checks.append(CheckResult(name, status, detail))
        if status is CheckStatus.FAIL:
            failures.append(f"{name}: {detail}")

    def invalid(attestation_id: Optional[str] = None, attester_id: Optional[str] = None,
                **flags: bool) -> AttestationVerificationResult:
        return AttestationVerificationResult(
            overall_status=AttestationStatus.INVALID,
            checks=checks, failures=list(failures), warnings=list(warnings),
            attestation_id=attestation_id, attester_id=attester_id, **flags,
        )

    try:
        # --- 1. input/type validation --------------------------------------
        if not isinstance(raw_attestation, dict):
            add("input_validation", CheckStatus.FAIL, "attestation must be a JSON object")
            return invalid()
        add("input_validation", CheckStatus.PASS, "attestation is a JSON object")

        # --- 2. schema version -----------------------------------------------
        schema_version = raw_attestation.get("schema_version")
        if schema_version not in SUPPORTED_SCHEMA_VERSIONS:
            add("schema_version_supported", CheckStatus.FAIL,
                f"unsupported or missing schema_version {schema_version!r}")
            return AttestationVerificationResult(
                overall_status=AttestationStatus.UNSUPPORTED_SCHEMA, schema_supported=False,
                checks=checks, failures=list(failures), warnings=list(warnings),
            )
        add("schema_version_supported", CheckStatus.PASS, schema_version)

        # --- 3./4. required fields / structural validation (incl. attester ---
        # --- identity, which is just one of the required string fields) ------
        try:
            attestation = EvidenceAttestation.from_dict(raw_attestation)
        except MalformedAttestationError as e:
            add("structural_validation", CheckStatus.FAIL, str(e))
            return invalid(schema_supported=True)
        add("structural_validation", CheckStatus.PASS, "all required fields present and well-typed")

        # --- 5. key lookup/trust ----------------------------------------------
        anchor = trust_store.resolve(attestation.attester_id, attestation.kid)
        if anchor is None:
            add("attester_trust", CheckStatus.FAIL,
                f"attester_id={attestation.attester_id!r} kid={attestation.kid!r} does not resolve to a "
                "trusted, currently-active key")
            return invalid(attestation.attestation_id, attestation.attester_id,
                            schema_supported=True, structure_valid=True)
        add("attester_trust", CheckStatus.PASS,
            f"resolved trusted key for attester_id={attestation.attester_id!r} kid={attestation.kid!r}")

        # --- 6. signature verification -----------------------------------------
        if not verify_token(attestation.to_dict(), anchor.public_key):
            add("signature_verification", CheckStatus.FAIL, "Ed25519 signature does not verify")
            return invalid(attestation.attestation_id, attestation.attester_id,
                            schema_supported=True, structure_valid=True)
        add("signature_verification", CheckStatus.PASS, "Ed25519 signature valid")

        # --- 7. evidence_type authorization -------------------------------------
        if not trust_store.evidence_type_allowed(anchor, attestation.evidence_type):
            add("evidence_type_authorization", CheckStatus.FAIL,
                f"attester_id={attestation.attester_id!r} is not permitted to assert "
                f"evidence_type={attestation.evidence_type!r}")
            return invalid(attestation.attestation_id, attestation.attester_id,
                            schema_supported=True, structure_valid=True,
                            signer_verified=True, signer_trusted=True)
        add("evidence_type_authorization", CheckStatus.PASS,
            f"attester_id={attestation.attester_id!r} is permitted for evidence_type="
            f"{attestation.evidence_type!r}")

        common_flags = dict(
            schema_supported=True, structure_valid=True,
            signer_verified=True, signer_trusted=True, evidence_type_allowed=True,
        )

        # --- 8. issued_at / not_before / expires_at ------------------------------
        if now < attestation.not_before:
            add("validity_window", CheckStatus.FAIL,
                f"now ({now}) precedes not_before ({attestation.not_before}); not yet valid")
            return invalid(attestation.attestation_id, attestation.attester_id, **common_flags)
        if now >= attestation.expires_at:
            add("validity_window", CheckStatus.FAIL,
                f"now ({now}) is at or after expires_at ({attestation.expires_at}); expired")
            return invalid(attestation.attestation_id, attestation.attester_id, **common_flags)
        add("validity_window", CheckStatus.PASS, "current time is within the declared validity window")
        common_flags["time_valid"] = True

        # --- 9. action_hash binding ---------------------------------------------
        if attestation.action_hash != expected_action_hash:
            add("action_binding", CheckStatus.FAIL,
                f"action_hash {attestation.action_hash!r} != expected {expected_action_hash!r}")
            return invalid(attestation.attestation_id, attestation.attester_id, **common_flags)
        add("action_binding", CheckStatus.PASS, "action_hash matches the expected bound action")
        common_flags["action_binding_valid"] = True

        # --- 10. optional payload_hash binding -----------------------------------
        if expected_payload_hash is not None:
            if attestation.payload_hash != expected_payload_hash:
                add("payload_binding", CheckStatus.FAIL,
                    f"payload_hash {attestation.payload_hash!r} != expected {expected_payload_hash!r}")
                return invalid(attestation.attestation_id, attestation.attester_id, **common_flags)
            add("payload_binding", CheckStatus.PASS, "payload_hash matches the expected bound payload")
        else:
            add("payload_binding", CheckStatus.PASS, "no expected payload_hash supplied; binding not checked")
        common_flags["payload_binding_valid"] = True

        # --- 11. expected scope --------------------------------------------------
        if attestation.scope != expected_scope:
            add("scope_binding", CheckStatus.FAIL,
                f"scope {attestation.scope!r} != expected {expected_scope!r}")
            return invalid(attestation.attestation_id, attestation.attester_id, **common_flags)
        add("scope_binding", CheckStatus.PASS, "scope matches the expected scope")
        common_flags["scope_valid"] = True

        # --- 12. expected policy binding ------------------------------------------
        policy_problems = []
        if expected_policy_hash is not None and attestation.policy_hash != expected_policy_hash:
            policy_problems.append(f"policy_hash {attestation.policy_hash!r} != expected {expected_policy_hash!r}")
        if expected_policy_version is not None and attestation.policy_version != expected_policy_version:
            policy_problems.append(
                f"policy_version {attestation.policy_version!r} != expected {expected_policy_version!r}"
            )
        if policy_problems:
            add("policy_binding", CheckStatus.FAIL, "; ".join(policy_problems))
            return invalid(attestation.attestation_id, attestation.attester_id, **common_flags)
        add("policy_binding", CheckStatus.PASS,
            "policy binding matches expectations" if (expected_policy_hash or expected_policy_version)
            else "no expected policy binding supplied; binding not checked")
        common_flags["policy_binding_valid"] = True

        # --- 13. success -----------------------------------------------------------
        return AttestationVerificationResult(
            overall_status=AttestationStatus.VERIFIED,
            checks=checks, failures=list(failures), warnings=list(warnings),
            attestation_id=attestation.attestation_id, attester_id=attestation.attester_id,
            **common_flags,
        )

    except Exception as e:  # noqa: BLE001 — any unexpected error fails closed, never VERIFIED.
        add("verifier_internal_error", CheckStatus.FAIL, f"unexpected verifier error: {e!r}")
        return AttestationVerificationResult(
            overall_status=AttestationStatus.INVALID,
            checks=checks, failures=list(failures), warnings=list(warnings),
        )


__all__ = ["verify_attestation"]
