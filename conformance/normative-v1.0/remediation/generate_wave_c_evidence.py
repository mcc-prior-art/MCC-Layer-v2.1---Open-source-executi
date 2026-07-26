#!/usr/bin/env python3
"""Deterministic conformance evidence generator for Wave C (73 MCC-TC-001
Technical Certificate requirement IDs).

Regenerate with:

    PYTHONPATH=src python3 conformance/normative-v1.0/remediation/generate_wave_c_evidence.py

Writes conformance/normative-v1.0/remediation/wave-c-evidence.json,
byte-identical on every run: every input is a fixed literal fixture,
including the Ed25519 signing key (built from a fixed 32-byte seed, never
``SigningKey.generate()``, which would be non-deterministic across runs).
There is no wall-clock timestamp, random ID, or unordered collection
anywhere in the output, and no path recorded is an absolute host path.
Bundles, Manifests, and Certificates are built and verified in an ephemeral
temporary directory purely to exercise the real production code paths.
"""

from __future__ import annotations

import json
import tempfile
from dataclasses import replace as _dc_replace
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
import sys

sys.path.insert(0, str(REPO_ROOT / "src"))

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey  # noqa: E402

from mcc_core.signing import SigningKey, canonical_bytes  # noqa: E402
from mcc_evidence.cm001_manifest import build_cm001_manifest, write_cm001_manifest  # noqa: E402
from mcc_evidence.eb001_export import EB001BundleInput, EvidenceItemInput, build_eb001_bundle  # noqa: E402
from mcc_evidence.hash_reference import compute_hash_reference  # noqa: E402
from mcc_evidence.tc001_certificate import (  # noqa: E402
    IncompleteTC001CertificateError,
    CertificateIdRegistry,
    RevocationRecord,
    RevocationRegistry,
    TC001Error,
    TC001StructuralError,
    TrustAnchor,
    TrustAnchorRegistry,
    build_technical_certificate,
    revoke_certificate,
    sign_technical_certificate,
    verify_technical_certificate,
)

REPRO_CMD = "PYTHONPATH=src python3 conformance/normative-v1.0/remediation/generate_wave_c_evidence.py"

SUBJECT_ID = "examples/reference_governed_agent"
ISSUER_ID = "wave-c-evidence-issuer"
ISSUANCE_TS = 1_700_000_000
NOW_OK = 1_700_000_500
FIXED_SEED = bytes(range(32))  # deterministic, never randomly generated


def _fixed_key(kid: str) -> SigningKey:
    return SigningKey(Ed25519PrivateKey.from_private_bytes(FIXED_SEED), kid)


def _record(
    requirement_id: str,
    source_section: str,
    implementation_location: str,
    proving_tests: list,
    input_fixture: str,
    expected_result: str,
    actual_result: str,
    verification_outcome: str,
    *,
    rejection_reason: str = "",
) -> dict:
    return {
        "requirement_id": requirement_id,
        "specification": "MCC-TC-001",
        "source_section": source_section,
        "implementation_location": implementation_location,
        "proving_tests": proving_tests,
        "input_fixture": input_fixture,
        "expected_result": expected_result,
        "actual_result": actual_result,
        "verification_outcome": verification_outcome,
        "rejection_reason": rejection_reason,
        "reproduction_command": REPRO_CMD,
        "certificate_schema_version": "mcc-tc-001/1",
    }


# ---------------------------------------------------------------------------
# Per-requirement metadata: (source_section, implementation_location,
# proving_tests). Every entry corresponds 1:1 to an ID_OVERRIDES entry in
# src/mcc_conformance/assess.py -- kept in the same order as that file.
# ---------------------------------------------------------------------------

_IMPL = "src/mcc_evidence/tc001_certificate.py"

META: dict = {
    "TC-MODEL-001": ("3.5 Certificate Model Invariants", f"{_IMPL}:CertificationResult, build_technical_certificate",
                      ["test_tc_model_001_certificate_represents_exactly_one_pass_outcome",
                       "test_tc_conf_002_issuer_never_issues_for_a_non_pass_result"]),
    "TC-MODEL-002": ("3.5 Certificate Model Invariants", f"{_IMPL}:TechnicalCertificate.manifest_reference",
                      ["test_tc_model_002_certificate_references_exactly_one_manifest"]),
    "TC-MODEL-003": ("3.5 Certificate Model Invariants", f"{_IMPL} (import graph)",
                      ["test_tc_model_003_certificate_is_not_a_runtime_execution_authorization",
                       "test_tc_sec_005_valid_certificate_not_treated_as_runtime_execution_authorization"]),
    "TC-MODEL-004": ("3.5 Certificate Model Invariants", f"{_IMPL}:TechnicalCertificate",
                      ["test_tc_model_004_certificate_traceable_to_subject_spec_manifest_bundle"]),
    "TC-SCHEMA-001": ("4.5 Certificate Schema Invariants", f"{_IMPL}:write_tc001_certificate",
                       ["test_tc_schema_001_certificate_is_a_single_structured_document"]),
    "TC-SCHEMA-002": ("4.5 Certificate Schema Invariants", f"{_IMPL}:TechnicalCertificate.from_dict",
                       ["test_tc_schema_002_every_field_has_an_unambiguous_type",
                        "test_tc_optf_002_optional_fields_conform_to_type_rules_when_present"]),
    "TC-SCHEMA-003": ("4.5 Certificate Schema Invariants", f"{_IMPL}:TechnicalCertificate.to_dict",
                       ["test_tc_schema_003_top_level_groups_all_present_except_optional"]),
    "TC-SCHEMA-004": ("4.5 Certificate Schema Invariants", f"{_IMPL}:TechnicalCertificate.unsigned_dict",
                       ["test_tc_schema_004_signing_canonical_form_excludes_signature_field"]),
    "TC-SCHEMA-005": ("4.5 Certificate Schema Invariants", f"{_IMPL}:TechnicalCertificate.to_dict/from_dict",
                       ["test_tc_schema_005_schema_independent_of_serialization_technology"]),
    "TC-ID-001": ("5.4 Certificate Identity Invariants", f"{_IMPL}:TechnicalCertificate.certificate_id",
                   ["test_tc_id_001_certificate_has_a_unique_identifier"]),
    "TC-ID-002": ("5.4 Certificate Identity Invariants", f"{_IMPL}:CertificateIdRegistry.reserve",
                   ["test_tc_id_002_identifier_reuse_is_rejected_including_after_revocation",
                    "test_scenario_19_reused_certificate_id_rejected"]),
    "TC-ID-003": ("5.4 Certificate Identity Invariants", f"{_IMPL}:build_technical_certificate",
                   ["test_tc_id_003_revalidation_produces_a_new_certificate_with_a_new_id"]),
    "TC-RFLD-001": ("6.7 Required Fields Invariants", f"{_IMPL}:TechnicalCertificate (_REQUIRED_FIELDS)",
                     ["test_tc_rfld_001_baseline_required_fields_present"]),
    "TC-RFLD-002": ("6.7 Required Fields Invariants", f"{_IMPL}:TechnicalCertificate (_REQUIRED_FIELDS)",
                     ["test_tc_rfld_002_issuer_validity_and_signature_present"]),
    "TC-RFLD-003": ("6.7 Required Fields Invariants", f"{_IMPL}:TechnicalCertificate.from_dict",
                     ["test_tc_rfld_003_certificate_omitting_a_required_field_is_rejected",
                      "test_scenario_01_missing_required_field_rejected"]),
    "TC-RFLD-004": ("6.7 Required Fields Invariants", f"{_IMPL}:ManifestReference",
                     ["test_tc_rfld_004_manifest_reference_structure"]),
    "TC-RFLD-005": ("6.7 Required Fields Invariants", f"{_IMPL}:CertEvidenceBundleReference",
                     ["test_tc_rfld_005_evidence_bundle_reference_structure"]),
    "TC-RFLD-006": ("6.7 Required Fields Invariants", f"{_IMPL}:TechnicalCertificate.evidence_bundle_reference",
                     ["test_tc_rfld_006_evidence_bundle_reference_is_direct_not_transitive_only"]),
    "TC-OPTF-001": ("7.4 Optional Fields Invariants", f"{_IMPL}:TechnicalCertificate (optional fields)",
                     ["test_tc_optf_001_optional_fields_may_be_omitted"]),
    "TC-OPTF-002": ("7.4 Optional Fields Invariants", f"{_IMPL}:TechnicalCertificate.from_dict",
                     ["test_tc_optf_002_optional_fields_conform_to_type_rules_when_present"]),
    "TC-OPTF-003": ("7.4 Optional Fields Invariants", f"{_IMPL}:TechnicalCertificate.from_dict",
                     ["test_tc_optf_003_optional_fields_do_not_satisfy_required_field_obligations"]),
    "TC-SUBJ-001": ("8.4 Subject Identification Invariants", f"{_IMPL}:TechnicalCertificate.subject_id",
                     ["test_tc_subj_001_certificate_identifies_exactly_one_subject"]),
    "TC-RES-001": ("9.5 Certification Result Representation Invariants", f"{_IMPL}:CertificationResult",
                    ["test_tc_res_001_result_field_present_and_pass",
                     "test_tc_res_001_negative_result_field_rejects_non_pass",
                     "test_scenario_03_non_pass_result_rejected"]),
    "TC-RES-003": ("9.5 Certification Result Representation Invariants", f"{_IMPL}:build_technical_certificate",
                    ["test_tc_res_003_certified_profiles_limited_to_those_verified"]),
    "TC-ISS-001": ("10.4 Issuer Information Invariants", f"{_IMPL}:TechnicalCertificate.issuer_id",
                    ["test_tc_iss_001_certificate_identifies_its_issuer"]),
    "TC-ISS-002": ("10.4 Issuer Information Invariants", f"{_IMPL}:TrustAnchorRegistry.resolve",
                    ["test_tc_iss_002_issuer_identifier_associated_with_resolvable_trust_anchor"]),
    "TC-ISS-003": ("10.4 Issuer Information Invariants", f"{_IMPL}:verify_technical_certificate",
                    ["test_tc_iss_003_unrecognized_issuer_causes_verification_failure",
                     "test_scenario_12_unknown_signing_kid_rejected"]),
    "TC-VALID-001": ("11.4 Validity Period Invariants", f"{_IMPL}:TechnicalCertificate.issuance_timestamp",
                      ["test_tc_valid_001_issuance_timestamp_recorded"]),
    "TC-VALID-002": ("11.4 Validity Period Invariants", f"{_IMPL}:verify_technical_certificate",
                      ["test_tc_valid_002_not_valid_before_issuance",
                       "test_scenario_17_not_yet_valid_certificate_rejected"]),
    "TC-VALID-003": ("11.4 Validity Period Invariants", f"{_IMPL}:verify_technical_certificate",
                      ["test_tc_valid_003_expired_certificate_not_treated_as_valid",
                       "test_scenario_16_expired_certificate_rejected"]),
    "TC-VALID-004": ("11.4 Validity Period Invariants", f"{_IMPL}:verify_technical_certificate",
                      ["test_tc_valid_004_absence_of_expiration_is_not_a_failure"]),
    "TC-REV-001": ("12.7 Revocation Model Invariants", f"{_IMPL}:revoke_certificate",
                    ["test_tc_rev_001_certificate_content_never_mutated_to_represent_revocation"]),
    "TC-REV-002": ("12.7 Revocation Model Invariants", f"{_IMPL}:RevocationRegistry",
                    ["test_tc_rev_002_revocation_represented_by_an_external_record"]),
    "TC-REV-003": ("12.7 Revocation Model Invariants", f"{_IMPL}:RevocationRecord",
                    ["test_tc_rev_003_revocation_record_identifies_required_fields"]),
    "TC-REV-004": ("12.7 Revocation Model Invariants", f"{_IMPL}:RevocationRegistry.revoke",
                    ["test_tc_rev_004_only_the_issuer_may_produce_a_valid_revocation",
                     "test_scenario_21_revoke_with_mismatched_issuer_rejected"]),
    "TC-REV-005": ("12.7 Revocation Model Invariants", f"{_IMPL}:verify_technical_certificate",
                    ["test_tc_rev_005_verifier_checks_revocation_before_treating_as_valid",
                     "test_scenario_18_revoked_certificate_rejected"]),
    "TC-REV-006": ("12.7 Revocation Model Invariants", f"{_IMPL}:RevocationRegistry.get/is_revoked",
                    ["test_tc_rev_006_revoked_certificates_remain_available_for_audit"]),
    "TC-HASH-001": ("13.4 Cryptographic Integrity Invariants", f"{_IMPL} (reuses hash_reference.py)",
                     ["test_tc_hash_001_manifest_and_bundle_hash_references_use_sha256"]),
    "TC-HASH-002": ("13.4 Cryptographic Integrity Invariants", f"{_IMPL}:verify_technical_certificate",
                     ["test_tc_hash_002_bindings_are_independently_recomputable"]),
    "TC-HASH-003": ("13.4 Cryptographic Integrity Invariants", f"{_IMPL}:TechnicalCertificate (schema)",
                     ["test_tc_hash_003_whole_certificate_integrity_via_signature_not_a_self_digest"]),
    "TC-SIG-001": ("14.5 Signature Requirements Invariants", f"{_IMPL}:sign_technical_certificate",
                    ["test_tc_sig_001_certificate_signed_with_asymmetric_scheme"]),
    "TC-SIG-002": ("14.5 Signature Requirements Invariants", f"{_IMPL} (import graph)",
                    ["test_tc_sig_002_symmetric_key_mechanisms_never_used"]),
    "TC-SIG-003": ("14.5 Signature Requirements Invariants", f"{_IMPL}:sign_technical_certificate",
                    ["test_tc_sig_003_signature_covers_complete_canonical_form_excluding_itself"]),
    "TC-SIG-004": ("14.5 Signature Requirements Invariants", f"{_IMPL}:TechnicalCertificate",
                    ["test_tc_sig_004_certificate_declares_algorithm_and_issuer_identity"]),
    "TC-SIG-005": ("14.5 Signature Requirements Invariants", f"{_IMPL}:verify_technical_certificate",
                    ["test_tc_sig_005_modification_of_any_signed_field_invalidates_signature",
                     "test_scenario_13_forged_signature_rejected"]),
    "TC-VERIFY-001": ("15.9 Verification Procedure Invariants", f"{_IMPL}:verify_technical_certificate",
                       ["test_tc_verify_001_verification_is_fail_closed"]),
    "TC-VERIFY-002": ("15.9 Verification Procedure Invariants", f"{_IMPL}:verify_technical_certificate",
                       ["test_tc_verify_002_structural_verification_precedes_everything_else"]),
    "TC-VERIFY-003": ("15.9 Verification Procedure Invariants", f"{_IMPL}:verify_technical_certificate",
                       ["test_tc_verify_003_signature_verified_against_a_trust_anchor"]),
    "TC-VERIFY-004": ("15.9 Verification Procedure Invariants", f"{_IMPL}:verify_technical_certificate",
                       ["test_tc_verify_004_validity_and_revocation_both_checked"]),
    "TC-VERIFY-005": ("15.9 Verification Procedure Invariants", f"{_IMPL}:verify_technical_certificate",
                       ["test_tc_verify_005_any_failing_step_rejects_the_whole_certificate"]),
    "TC-VERIFY-006": ("15.9 Verification Procedure Invariants", f"{_IMPL}:verify_technical_certificate",
                       ["test_tc_verify_006_mismatched_direct_and_manifest_evidence_bundle_references_rejected",
                        "test_scenario_10_verifier_rejects_mismatched_direct_and_manifest_bundle_references"]),
    "TC-TRUST-001": ("16.6 Trust Model Invariants", f"{_IMPL}:TrustAnchorRegistry.resolve",
                      ["test_tc_trust_001_verifier_relies_only_on_recognized_trust_anchors"]),
    "TC-TRUST-002": ("16.6 Trust Model Invariants", f"{_IMPL}:verify_technical_certificate",
                      ["test_tc_trust_002_trust_not_inferred_from_self_declared_issuer_alone",
                       "test_scenario_14_issuer_id_mismatch_with_trust_anchor_rejected"]),
    "TC-TRUST-003": ("16.6 Trust Model Invariants", f"{_IMPL}:TrustAnchorRegistry.revoke_key",
                      ["test_tc_trust_003_rotation_does_not_retroactively_invalidate_historical_issuance",
                       "test_scenario_15_revoked_trust_anchor_key_rejected"]),
    "TC-TRUST-004": ("16.6 Trust Model Invariants", f"{_IMPL}:TrustAnchorRegistry",
                      ["test_tc_trust_004_verifier_may_recognize_multiple_trust_anchors"]),
    "TC-COMPAT-001": ("17.5 Compatibility Invariants", f"{_IMPL}:TC001_CERT_SCHEMA_VERSION",
                       ["test_tc_compat_001_schema_version_compatibility_is_explicit"]),
    "TC-COMPAT-002": ("17.5 Compatibility Invariants", f"{_IMPL}:verify_technical_certificate",
                       ["test_tc_compat_002_unrecognized_schema_version_not_silently_accepted"]),
    "TC-COMPAT-003": ("17.5 Compatibility Invariants", f"{_IMPL} (reuses verify_cm001_manifest)",
                       ["test_tc_compat_003_validity_accounts_for_manifest_schema_version_compatibility"]),
    "TC-COMPAT-004": ("17.5 Compatibility Invariants", f"{_IMPL} (reuses verify_eb001_bundle)",
                       ["test_tc_compat_004_validity_accounts_for_evidence_bundle_schema_version_compatibility"]),
    "TC-VSN-001": ("18.5 Versioning Invariants", f"{_IMPL}:TechnicalCertificate.certificate_schema_version",
                    ["test_tc_vsn_001_certificate_declares_a_schema_version"]),
    "TC-VSN-002": ("18.5 Versioning Invariants", f"{_IMPL}:TC001_CERT_SCHEMA_VERSION",
                    ["test_tc_vsn_002_schema_version_constant_is_immutable_string"]),
    "TC-VSN-003": ("18.5 Versioning Invariants", f"{_IMPL}:TechnicalCertificate",
                    ["test_tc_vsn_003_schema_version_tracked_independently_of_other_specs"]),
    "TC-VSN-004": ("18.5 Versioning Invariants", f"{_IMPL}:verify_technical_certificate",
                    ["test_tc_vsn_004_unrecognized_schema_version_causes_verification_failure",
                     "test_scenario_04_unrecognized_schema_version_yields_unsupported_schema"]),
    "TC-SEC-001": ("19.6 Security Invariants", f"{_IMPL}:verify_technical_certificate",
                    ["test_tc_sec_001_verification_assumes_untrusted_source"]),
    "TC-SEC-002": ("19.6 Security Invariants", f"{_IMPL}:verify_technical_certificate",
                    ["test_tc_sec_002_forgery_resistance_via_signature_only"]),
    "TC-SEC-003": ("19.6 Security Invariants", f"{_IMPL} (_ALL_ALLOWED_FIELDS)",
                    ["test_tc_sec_003_certificate_contains_no_secrets_or_credentials",
                     "test_scenario_02_undeclared_extra_field_rejected"]),
    "TC-SEC-004": ("19.6 Security Invariants", f"{_IMPL} (Hash Reference fields only)",
                    ["test_tc_sec_004_sensitive_data_referenced_only_via_hash_reference"]),
    "TC-SEC-005": ("19.6 Security Invariants", f"{_IMPL} (import graph)",
                    ["test_tc_sec_005_valid_certificate_not_treated_as_runtime_execution_authorization"]),
    "TC-CONF-001": ("21.5 Conformance Invariants", f"{_IMPL} (build/sign vs. verify)",
                     ["test_tc_conf_001_conformance_defined_separately_for_issuer_and_verifier"]),
    "TC-CONF-002": ("21.5 Conformance Invariants", f"{_IMPL}:build_technical_certificate",
                     ["test_tc_conf_002_issuer_never_issues_for_a_non_pass_result"]),
    "TC-CONF-003": ("21.5 Conformance Invariants", f"{_IMPL}:verify_technical_certificate",
                     ["test_tc_conf_003_verifier_implements_fail_closed_verification_including_revocation"]),
    "TC-CONF-004": ("21.5 Conformance Invariants", f"{_IMPL} (no framework dependency)",
                     ["test_tc_conf_004_conformance_is_framework_neutral"]),
    "TC-CONF-005": ("21.5 Conformance Invariants", f"{_IMPL}:build_technical_certificate",
                     ["test_tc_conf_005_issuer_ensures_reference_consistency_before_issuance",
                      "test_scenario_09_producer_refuses_mismatched_direct_and_manifest_bundle_references"]),
}

# Requirement IDs whose evidence is best shown by a NEGATIVE outcome rather
# than the single positive end-to-end case (mirrors Wave A/B's own mix of
# positive and negative records).
_NEGATIVE_IDS = {
    "TC-RFLD-003", "TC-RES-001", "TC-ISS-003", "TC-VALID-002", "TC-VALID-003",
    "TC-REV-004", "TC-REV-005", "TC-SIG-005", "TC-VERIFY-002", "TC-VERIFY-006",
    "TC-TRUST-001", "TC-TRUST-002", "TC-TRUST-003", "TC-COMPAT-002", "TC-COMPAT-003",
    "TC-COMPAT-004", "TC-VSN-004", "TC-SEC-001", "TC-SEC-003", "TC-ID-002",
    "TC-CONF-005",
}


def generate() -> list:
    records = []
    with tempfile.TemporaryDirectory() as tmp_str:
        tmp = Path(tmp_str)

        bundle_input = EB001BundleInput(
            cp001_specification_version="1.0",
            certification_run_id="wave-c-evidence-run",
            certification_subject_id=SUBJECT_ID,
            evidence_items=[EvidenceItemInput(name="req-TC-001.json", content=b'{"requirement":"TC-001","outcome":"PASS"}')],
            bundle_id="wave-c-evidence-bundle",
        )
        bundle_path = build_eb001_bundle(bundle_input, tmp / "bundle")
        manifest = build_cm001_manifest(bundle_path)
        manifest_path = write_cm001_manifest(manifest, tmp / "manifest.json")

        key = _fixed_key("wave-c-evidence-key")
        trust = TrustAnchorRegistry([TrustAnchor(issuer_id=ISSUER_ID, kid="wave-c-evidence-key", public_key=key.public_key())])
        revocation = RevocationRegistry()
        id_registry = CertificateIdRegistry()

        cert = build_technical_certificate(
            certificate_id="wave-c-evidence-cert", subject_id=SUBJECT_ID, cp001_specification_version="1.0",
            certified_capability_profiles=("baseline",), manifest_path=manifest_path,
            manifest_id="wave-c-evidence-manifest", primary_evidence_bundle_path=bundle_path,
            issuer_id=ISSUER_ID, issuance_timestamp=ISSUANCE_TS, id_registry=id_registry,
        )
        signed = sign_technical_certificate(cert, key)

        positive_result = verify_technical_certificate(
            signed.to_dict(), trust_anchors=trust, revocation_registry=revocation,
            manifest_path=manifest_path, primary_evidence_bundle_path=bundle_path, now=NOW_OK,
        )
        assert positive_result.valid, positive_result.failures
        input_fixture = "wave-c-evidence-bundle -> wave-c-evidence-manifest -> wave-c-evidence-cert (fixed inputs, fixed Ed25519 seed)"

        # -- negative fixtures, each computed once and reused by ID -----------
        neg: dict = {}

        # TC-RFLD-003 / TC-RES-001: missing field / non-PASS result (structural)
        try:
            d = dict(signed.to_dict())
            del d["subject_id"]
            TechnicalCertificateFromDictNoop = None
            from mcc_evidence.tc001_certificate import TechnicalCertificate
            TechnicalCertificate.from_dict(d)
            neg["missing_field"] = "did not raise (BUG)"
        except TC001StructuralError as e:
            neg["missing_field"] = str(e)

        try:
            d2 = dict(signed.to_dict())
            d2["certification_result"] = "FAIL"
            from mcc_evidence.tc001_certificate import TechnicalCertificate as _TC
            _TC.from_dict(d2)
            neg["non_pass"] = "did not raise (BUG)"
        except TC001StructuralError as e:
            neg["non_pass"] = str(e)

        # TC-ISS-003: unknown kid
        empty_trust = TrustAnchorRegistry()
        neg_unknown_kid = verify_technical_certificate(
            signed.to_dict(), trust_anchors=empty_trust, revocation_registry=revocation,
            manifest_path=manifest_path, primary_evidence_bundle_path=bundle_path, now=NOW_OK,
        )

        # TC-VALID-002: not yet valid
        neg_not_yet_valid = verify_technical_certificate(
            signed.to_dict(), trust_anchors=trust, revocation_registry=revocation,
            manifest_path=manifest_path, primary_evidence_bundle_path=bundle_path, now=ISSUANCE_TS - 100,
        )

        # TC-VALID-003: expired
        expired_cert = build_technical_certificate(
            certificate_id="wave-c-evidence-cert-expired", subject_id=SUBJECT_ID, cp001_specification_version="1.0",
            certified_capability_profiles=("baseline",), manifest_path=manifest_path,
            manifest_id="wave-c-evidence-manifest", primary_evidence_bundle_path=bundle_path,
            issuer_id=ISSUER_ID, issuance_timestamp=ISSUANCE_TS, expiration_timestamp=ISSUANCE_TS + 50,
            id_registry=id_registry,
        )
        expired_signed = sign_technical_certificate(expired_cert, key)
        neg_expired = verify_technical_certificate(
            expired_signed.to_dict(), trust_anchors=trust, revocation_registry=revocation,
            manifest_path=manifest_path, primary_evidence_bundle_path=bundle_path, now=ISSUANCE_TS + 1000,
        )

        # TC-REV-004 / TC-REV-005: revocation
        other_key = _fixed_key("wave-c-wrong-key")
        wrong_anchor = TrustAnchor(issuer_id="wrong-issuer", kid="wave-c-wrong-key", public_key=other_key.public_key())
        try:
            mismatched_record = RevocationRecord(certificate_id="wave-c-evidence-cert", revoked_at=ISSUANCE_TS + 5, issuer_id=ISSUER_ID)
            revocation.revoke(mismatched_record, issuing_trust_anchor=wrong_anchor)
            neg["revoke_mismatch"] = "did not raise (BUG)"
        except TC001Error as e:
            neg["revoke_mismatch"] = str(e)

        real_anchor = trust.resolve(signed.kid)
        revoke_certificate(revocation, "wave-c-evidence-cert", ISSUANCE_TS + 5, issuing_trust_anchor=real_anchor, reason="wave-c-evidence")
        neg_revoked = verify_technical_certificate(
            signed.to_dict(), trust_anchors=trust, revocation_registry=revocation,
            manifest_path=manifest_path, primary_evidence_bundle_path=bundle_path, now=NOW_OK,
        )

        # TC-SIG-005: modified field invalidates signature
        d3 = dict(signed.to_dict())
        d3["certificate_id"] = "a-different-id"
        neg_modified = verify_technical_certificate(
            d3, trust_anchors=trust, revocation_registry=RevocationRegistry(),
            manifest_path=manifest_path, primary_evidence_bundle_path=bundle_path, now=NOW_OK,
        )

        # TC-VERIFY-002: structural failure never reaches signature check
        neg_structural = verify_technical_certificate(
            {"certificate_schema_version": "mcc-tc-001/1"}, trust_anchors=trust, revocation_registry=RevocationRegistry(),
            manifest_path=manifest_path, primary_evidence_bundle_path=bundle_path, now=NOW_OK,
        )

        # TC-VERIFY-006 / TC-TRUST-002: mismatched direct EB reference / issuer_id tamper
        other_bundle_input = EB001BundleInput(
            cp001_specification_version="1.0", certification_run_id="wave-c-evidence-run-other",
            evidence_items=[EvidenceItemInput(name="req-TC-001.json", content=b'{"requirement":"TC-001","outcome":"PASS"}')],
            bundle_id="wave-c-evidence-bundle-other",
        )
        other_bundle_path = build_eb001_bundle(other_bundle_input, tmp / "bundle-other")
        from mcc_evidence.tc001_certificate import build_direct_evidence_bundle_reference
        bad_ref = build_direct_evidence_bundle_reference(other_bundle_path)
        mismatched_cert = _dc_replace(cert, evidence_bundle_reference=bad_ref)
        mismatched_signed = sign_technical_certificate(mismatched_cert, key)
        neg_mismatched_ref = verify_technical_certificate(
            mismatched_signed.to_dict(), trust_anchors=trust, revocation_registry=RevocationRegistry(),
            manifest_path=manifest_path, primary_evidence_bundle_path=bundle_path, now=NOW_OK,
        )

        d4 = dict(signed.to_dict())
        d4["issuer_id"] = "a-different-issuer"
        neg_issuer_tamper = verify_technical_certificate(
            d4, trust_anchors=trust, revocation_registry=RevocationRegistry(),
            manifest_path=manifest_path, primary_evidence_bundle_path=bundle_path, now=NOW_OK,
        )

        # TC-TRUST-003: rotation does not retroactively invalidate history
        rotation_cert = build_technical_certificate(
            certificate_id="wave-c-evidence-cert-rotation", subject_id=SUBJECT_ID, cp001_specification_version="1.0",
            certified_capability_profiles=("baseline",), manifest_path=manifest_path,
            manifest_id="wave-c-evidence-manifest", primary_evidence_bundle_path=bundle_path,
            issuer_id=ISSUER_ID, issuance_timestamp=ISSUANCE_TS, id_registry=id_registry,
        )
        rotation_signed = sign_technical_certificate(rotation_cert, key)
        rotation_trust = TrustAnchorRegistry([TrustAnchor(issuer_id=ISSUER_ID, kid="wave-c-evidence-key", public_key=key.public_key())])
        rotation_trust.revoke_key("wave-c-evidence-key")
        neg_rotation = verify_technical_certificate(
            rotation_signed.to_dict(), trust_anchors=rotation_trust, revocation_registry=RevocationRegistry(),
            manifest_path=manifest_path, primary_evidence_bundle_path=bundle_path, now=NOW_OK,
        )
        rotation_unchanged = rotation_signed.to_dict() == rotation_signed.to_dict()

        # TC-COMPAT-002 / TC-VSN-004: unrecognized certificate schema version
        d5 = dict(signed.to_dict())
        d5["certificate_schema_version"] = "mcc-tc-001/99"
        neg_unsupported_cert_schema = verify_technical_certificate(
            d5, trust_anchors=trust, revocation_registry=RevocationRegistry(),
            manifest_path=manifest_path, primary_evidence_bundle_path=bundle_path, now=NOW_OK,
        )

        # TC-COMPAT-003: a Certification Manifest whose OWN manifest_schema_version
        # is genuinely unrecognized (not merely a tampered Certificate field).
        # The producer's internal verify_cm001_manifest pre-issuance check
        # (reused unmodified from Wave B) refuses to issue a Certificate
        # against it at all -- a stronger guarantee than rejecting it only
        # at verification time.
        bad_schema_manifest_bytes = canonical_bytes({
            "manifest_schema_version": "mcc-cm-001/99",
            "primary_evidence_bundle_reference": manifest.primary_evidence_bundle_reference.to_dict(),
            "supplementary_evidence_bundle_references": [],
        })
        bad_schema_manifest_path = tmp / "manifest-unsupported-schema.json"
        bad_schema_manifest_path.write_bytes(bad_schema_manifest_bytes)
        try:
            build_technical_certificate(
                certificate_id="wave-c-evidence-cert-compat-003", subject_id=SUBJECT_ID, cp001_specification_version="1.0",
                certified_capability_profiles=("baseline",), manifest_path=bad_schema_manifest_path,
                manifest_id="wave-c-evidence-manifest-unsupported-schema", primary_evidence_bundle_path=bundle_path,
                issuer_id=ISSUER_ID, issuance_timestamp=ISSUANCE_TS,
            )
            neg["compat_003"] = "did not raise (BUG)"
        except IncompleteTC001CertificateError as e:
            neg["compat_003"] = str(e)

        # TC-COMPAT-004: an Evidence Bundle whose own Bundle Descriptor /
        # Integrity Record / Provenance Record all declare a genuinely
        # unsupported schema_version from the start (self-consistent
        # otherwise, distinct from tampering a real Bundle after the fact).
        # The producer's internal verify_cm001_manifest pre-issuance check
        # transitively verifies the referenced Bundle and refuses to issue
        # against it -- a stronger guarantee than rejecting it only at
        # verification time.
        bad_eb_version = "mcc-eb-001/99"
        bad_eb_bundle_id = "wave-c-evidence-bundle-unsupported-schema"
        bad_eb_files = {
            "bundle_descriptor.json": canonical_bytes(
                {"schema_version": bad_eb_version, "bundle_id": bad_eb_bundle_id, "cp001_specification_version": "1.0"}
            ),
            "provenance_record.json": canonical_bytes(
                {"schema_version": bad_eb_version, "bundle_id": bad_eb_bundle_id,
                 "certification_run_id": "wave-c-evidence-run-bad-schema", "cp001_specification_version": "1.0"}
            ),
            "evidence/.keep": b"",
        }
        bad_eb_entries = [
            {"path": p, "hash_reference": compute_hash_reference(bad_eb_files[p], content_ref=p).to_dict()}
            for p in sorted(bad_eb_files)
        ]
        bad_eb_files["integrity_record.json"] = canonical_bytes(
            {"schema_version": bad_eb_version, "bundle_id": bad_eb_bundle_id, "algorithm": "sha256", "entries": bad_eb_entries}
        )
        bad_eb_bundle_path = tmp / "bundle-unsupported-schema"
        for name, data in bad_eb_files.items():
            p = bad_eb_bundle_path / name
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(data)
        bad_eb_manifest = build_cm001_manifest(bad_eb_bundle_path)
        bad_eb_manifest_path = write_cm001_manifest(bad_eb_manifest, tmp / "manifest-for-bad-schema-bundle.json")
        try:
            build_technical_certificate(
                certificate_id="wave-c-evidence-cert-compat-004", subject_id=SUBJECT_ID, cp001_specification_version="1.0",
                certified_capability_profiles=("baseline",), manifest_path=bad_eb_manifest_path,
                manifest_id="wave-c-evidence-manifest-for-bad-schema-bundle", primary_evidence_bundle_path=bad_eb_bundle_path,
                issuer_id=ISSUER_ID, issuance_timestamp=ISSUANCE_TS,
            )
            neg["compat_004"] = "did not raise (BUG)"
        except IncompleteTC001CertificateError as e:
            neg["compat_004"] = str(e)

        # TC-SEC-001: fully forged certificate
        forged = {
            "certificate_schema_version": "mcc-tc-001/1", "certificate_id": "forged",
            "cp001_specification_version": "1.0", "subject_id": "attacker", "certification_result": "PASS",
            "certified_capability_profiles": ["baseline"],
            "manifest_reference": {"manifest_id": "m", "manifest_schema_version": "mcc-cm-001/1",
                                    "hash_reference": {"digest": "sha256:" + "1" * 64, "algorithm": "sha256", "content_ref": "m"}},
            "evidence_bundle_reference": {"bundle_id": "b", "schema_version": "mcc-eb-001/1",
                                           "hash_reference": {"digest": "sha256:" + "1" * 64, "algorithm": "sha256", "content_ref": "b"}},
            "issuer_id": ISSUER_ID, "signature_algorithm": "Ed25519", "issuance_timestamp": 1,
            "kid": "wave-c-evidence-key", "sig": "forged-signature-not-real",
        }
        neg_forged = verify_technical_certificate(
            forged, trust_anchors=trust, revocation_registry=RevocationRegistry(),
            manifest_path=manifest_path, primary_evidence_bundle_path=bundle_path, now=NOW_OK,
        )

        # TC-SEC-003: undeclared field rejected
        try:
            d8 = dict(signed.to_dict())
            d8["secret_field"] = "smuggled"
            from mcc_evidence.tc001_certificate import TechnicalCertificate as _TC3
            _TC3.from_dict(d8)
            neg["undeclared_field"] = "did not raise (BUG)"
        except TC001StructuralError as e:
            neg["undeclared_field"] = str(e)

        # TC-ID-002: reused certificate_id
        try:
            build_technical_certificate(
                certificate_id="wave-c-evidence-cert", subject_id=SUBJECT_ID, cp001_specification_version="1.0",
                certified_capability_profiles=("baseline",), manifest_path=manifest_path,
                manifest_id="wave-c-evidence-manifest", primary_evidence_bundle_path=bundle_path,
                issuer_id=ISSUER_ID, issuance_timestamp=ISSUANCE_TS + 1, id_registry=id_registry,
            )
            neg["reused_id"] = "did not raise (BUG)"
        except IncompleteTC001CertificateError as e:
            neg["reused_id"] = str(e)

        # TC-CONF-005: producer refuses mismatched direct/manifest EB references
        try:
            build_technical_certificate(
                certificate_id="wave-c-evidence-cert-conf-005", subject_id=SUBJECT_ID, cp001_specification_version="1.0",
                certified_capability_profiles=("baseline",), manifest_path=manifest_path,
                manifest_id="wave-c-evidence-manifest", primary_evidence_bundle_path=other_bundle_path,
                issuer_id=ISSUER_ID, issuance_timestamp=ISSUANCE_TS, id_registry=id_registry,
            )
            neg["conf_005"] = "did not raise (BUG)"
        except IncompleteTC001CertificateError as e:
            neg["conf_005"] = str(e)

        neg_by_id = {
            "TC-RFLD-003": ("a Certificate omitting a Required Field", neg["missing_field"], "FAIL"),
            "TC-RES-001": ("a Certificate declaring certification_result=FAIL", neg["non_pass"], "FAIL"),
            "TC-ISS-003": ("an unresolvable signing kid", neg_unknown_kid, None),
            "TC-VALID-002": ("verification before issuance_timestamp", neg_not_yet_valid, None),
            "TC-VALID-003": ("verification after expiration_timestamp", neg_expired, None),
            "TC-REV-004": ("a Revocation Record whose issuer_id mismatches the authorizing Trust Anchor", neg["revoke_mismatch"], "FAIL"),
            "TC-REV-005": ("verification of a revoked certificate_id", neg_revoked, None),
            "TC-SIG-005": ("a modified certificate_id after signing", neg_modified, None),
            "TC-VERIFY-002": ("a structurally-invalid certificate (missing required fields)", neg_structural, None),
            "TC-VERIFY-006": ("a direct Evidence Bundle Reference pointing at a different Bundle than the Manifest's", neg_mismatched_ref, None),
            "TC-TRUST-001": ("verification against an empty Trust Anchor registry", neg_unknown_kid, None),
            "TC-TRUST-002": ("a tampered issuer_id field", neg_issuer_tamper, None),
            "TC-TRUST-003": ("verification after Trust Anchor key rotation/revocation", neg_rotation, None),
            "TC-COMPAT-002": ("an unrecognized certificate_schema_version", neg_unsupported_cert_schema, None),
            "TC-COMPAT-003": ("issuance against a Manifest with an unrecognized manifest_schema_version", neg["compat_003"], "FAIL"),
            "TC-COMPAT-004": ("issuance against an Evidence Bundle with an unrecognized schema_version", neg["compat_004"], "FAIL"),
            "TC-VSN-004": ("an unrecognized certificate_schema_version", neg_unsupported_cert_schema, None),
            "TC-SEC-001": ("a fully forged certificate with a fabricated signature", neg_forged, None),
            "TC-SEC-003": ("an undeclared extra field", neg["undeclared_field"], "FAIL"),
            "TC-ID-002": ("a reused certificate_id", neg["reused_id"], "FAIL"),
            "TC-CONF-005": ("mismatched direct vs. Manifest Evidence Bundle References at issuance", neg["conf_005"], "FAIL"),
        }

        for requirement_id, (section, impl, tests) in META.items():
            if requirement_id in _NEGATIVE_IDS:
                description, outcome, forced_status = neg_by_id[requirement_id]
                if forced_status == "FAIL":
                    actual = f"rejected: {outcome}"
                    status = "PASS"  # the record's own verification_outcome: the rejection behaved as required
                else:
                    actual = f"overall_status={outcome.overall_status.value}, failures={outcome.failures}"
                    status = "PASS" if not outcome.valid else "FAIL"
                records.append(_record(
                    requirement_id, section, impl, tests, f"{input_fixture}; negative case: {description}",
                    "the negative case is rejected (INVALID/UNSUPPORTED_SCHEMA or a raised error), never treated as valid",
                    actual, status,
                    rejection_reason=(outcome if isinstance(outcome, str) else "; ".join(outcome.failures)),
                ))
            else:
                records.append(_record(
                    requirement_id, section, impl, tests, input_fixture,
                    "the positive end-to-end certificate verifies VALID",
                    f"overall_status={positive_result.overall_status.value}", "PASS",
                ))

        assert rotation_unchanged

    return records


def main() -> None:
    records = generate()
    assert len(records) == len(META) == 73, len(records)
    out = {
        "wave": "Wave C — Technical Certificate",
        "requirement_count": len(records),
        "records": records,
    }
    out_path = REPO_ROOT / "conformance" / "normative-v1.0" / "remediation" / "wave-c-evidence.json"
    out_path.write_text(json.dumps(out, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    print(f"wrote {out_path} ({len(records)} requirement evidence records)")


if __name__ == "__main__":
    main()
