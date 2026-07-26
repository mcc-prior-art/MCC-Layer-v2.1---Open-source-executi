"""MCC-TC-001 Technical Certificate (Wave C) — direct requirement-linked
tests plus 24 numbered negative scenarios for the fail-closed producer and
verifier in ``src/mcc_evidence/tc001_certificate.py``.

Every test builds a real Evidence Bundle (Wave A) and a real Certification
Manifest (Wave B) on disk, then a real Technical Certificate over them —
the full transitive chain Evidence Bundle -> Certification Manifest ->
Technical Certificate is exercised end to end, never mocked.
"""

from __future__ import annotations

import ast
import json
from dataclasses import replace as _dc_replace
from pathlib import Path

import pytest

from mcc_core.signing import SigningKey
from mcc_evidence.cm001_manifest import build_cm001_manifest, write_cm001_manifest
from mcc_evidence.eb001_export import EB001BundleInput, EvidenceItemInput, build_eb001_bundle
from mcc_evidence.hash_reference import HashReference
from mcc_evidence.tc001_certificate import (
    TC001_CERT_SCHEMA_VERSION,
    CertEvidenceBundleReference,
    CertificationResult,
    IncompleteTC001CertificateError,
    CertificateIdRegistry,
    ManifestReference,
    RevocationRegistry,
    TC001Error,
    TC001Status,
    TC001StructuralError,
    TechnicalCertificate,
    TrustAnchor,
    TrustAnchorRegistry,
    build_direct_evidence_bundle_reference,
    build_technical_certificate,
    read_tc001_certificate,
    revoke_certificate,
    sign_technical_certificate,
    verify_technical_certificate,
    write_tc001_certificate,
)

REPO_ROOT = Path(__file__).resolve().parents[1]

SUBJECT_ID = "examples/reference_governed_agent"
ISSUER_ID = "axlogiq-ca-1"
ISSUANCE_TS = 1_000_000
NOW_OK = 1_000_500


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------


def _build_bundle(tmp_path: Path, *, bundle_id: str = "wave-c-bundle") -> Path:
    bundle_input = EB001BundleInput(
        cp001_specification_version="1.0",
        certification_run_id=f"run-{bundle_id}",
        certification_subject_id=SUBJECT_ID,
        evidence_items=[EvidenceItemInput(name="req-TC-001.json", content=b'{"requirement":"TC-001","outcome":"PASS"}')],
        bundle_id=bundle_id,
    )
    return build_eb001_bundle(bundle_input, tmp_path / bundle_id)


def _build_manifest(tmp_path: Path, bundle_path: Path, *, name: str = "manifest.json") -> Path:
    manifest = build_cm001_manifest(bundle_path)
    return write_cm001_manifest(manifest, tmp_path / name)


def _build_bad_schema_bundle(dest: Path, *, bundle_id: str) -> Path:
    """A self-consistent (structurally valid, correctly-enumerated) MCC-EB-001
    Bundle whose Bundle Descriptor / Integrity Record / Provenance Record all
    declare a genuinely unsupported schema_version from the start -- distinct
    from tampering a real Bundle after the fact."""
    from mcc_core.signing import canonical_bytes
    from mcc_evidence.eb001_schema import (
        BUNDLE_DESCRIPTOR_NAME,
        EVIDENCE_DIR_NAME,
        INTEGRITY_RECORD_NAME,
        PROVENANCE_RECORD_NAME,
    )
    from mcc_evidence.hash_reference import compute_hash_reference

    bad_version = "mcc-eb-001/99"
    files = {
        BUNDLE_DESCRIPTOR_NAME: canonical_bytes(
            {"schema_version": bad_version, "bundle_id": bundle_id, "cp001_specification_version": "1.0"}
        ),
        PROVENANCE_RECORD_NAME: canonical_bytes(
            {"schema_version": bad_version, "bundle_id": bundle_id,
             "certification_run_id": f"run-{bundle_id}", "cp001_specification_version": "1.0"}
        ),
        f"{EVIDENCE_DIR_NAME}/.keep": b"",
    }
    entries = [
        {"path": path, "hash_reference": compute_hash_reference(files[path], content_ref=path).to_dict()}
        for path in sorted(files)
    ]
    files[INTEGRITY_RECORD_NAME] = canonical_bytes(
        {"schema_version": bad_version, "bundle_id": bundle_id, "algorithm": "sha256", "entries": entries}
    )
    for name, data in files.items():
        p = dest / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)
    return dest


@pytest.fixture()
def env(tmp_path: Path):
    bundle_path = _build_bundle(tmp_path)
    manifest_path = _build_manifest(tmp_path, bundle_path)
    key = SigningKey.generate("issuer-key-1")
    trust = TrustAnchorRegistry([TrustAnchor(issuer_id=ISSUER_ID, kid="issuer-key-1", public_key=key.public_key())])
    revocation = RevocationRegistry()
    id_registry = CertificateIdRegistry()
    return {
        "tmp_path": tmp_path,
        "bundle_path": bundle_path,
        "manifest_path": manifest_path,
        "key": key,
        "trust": trust,
        "revocation": revocation,
        "id_registry": id_registry,
    }


def _build_unsigned(env, *, certificate_id: str = "cert-1", **overrides):
    kwargs = dict(
        certificate_id=certificate_id,
        subject_id=SUBJECT_ID,
        cp001_specification_version="1.0",
        certified_capability_profiles=("baseline",),
        manifest_path=env["manifest_path"],
        manifest_id="wave-c-manifest",
        primary_evidence_bundle_path=env["bundle_path"],
        issuer_id=ISSUER_ID,
        issuance_timestamp=ISSUANCE_TS,
        id_registry=env["id_registry"],
    )
    kwargs.update(overrides)
    return build_technical_certificate(**kwargs)


def _build_and_sign(env, *, certificate_id: str = "cert-1", **overrides):
    cert = _build_unsigned(env, certificate_id=certificate_id, **overrides)
    return sign_technical_certificate(cert, env["key"])


def _imported_modules(source: str) -> set:
    tree = ast.parse(source)
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module)
    return imported


def _verify(env, cert_or_dict, *, now: int = NOW_OK, manifest_path=None, bundle_path=None, trust=None, revocation=None):
    return verify_technical_certificate(
        cert_or_dict,
        trust_anchors=trust if trust is not None else env["trust"],
        revocation_registry=revocation if revocation is not None else env["revocation"],
        manifest_path=manifest_path if manifest_path is not None else env["manifest_path"],
        primary_evidence_bundle_path=bundle_path if bundle_path is not None else env["bundle_path"],
        now=now,
    )


# ---------------------------------------------------------------------------
# End-to-end positive path
# ---------------------------------------------------------------------------


def test_end_to_end_valid_certificate_verifies(env):
    signed = _build_and_sign(env)
    result = _verify(env, signed.to_dict())
    assert result.overall_status is TC001Status.VALID, result.failures
    assert result.failures == []


def test_end_to_end_via_write_and_read_round_trip(env):
    signed = _build_and_sign(env)
    path = write_tc001_certificate(signed, env["tmp_path"] / "cert.json")
    read_back = read_tc001_certificate(path)
    assert read_back.to_dict() == signed.to_dict()
    result = _verify(env, read_back.to_dict())
    assert result.valid


# ---------------------------------------------------------------------------
# TC-MODEL-001..004 — Certificate Model
# ---------------------------------------------------------------------------


def test_tc_model_001_certificate_represents_exactly_one_pass_outcome(env):
    signed = _build_and_sign(env)
    assert signed.certification_result == CertificationResult.PASS.value


def test_tc_model_002_certificate_references_exactly_one_manifest(env):
    signed = _build_and_sign(env)
    assert isinstance(signed.manifest_reference, ManifestReference)
    # the dataclass has exactly one manifest_reference field, not a collection
    assert not isinstance(signed.manifest_reference, (list, tuple))


def test_tc_model_003_certificate_is_not_a_runtime_execution_authorization():
    # Static/architecture guard: the Certificate schema has no verdict/
    # decision-shaped field (only certification_result, PASS-only, never a
    # runtime verdict), and the module imports no gate/authority internals.
    field_names = set(TechnicalCertificate.__dataclass_fields__.keys())
    assert "verdict" not in field_names and "decision" not in field_names
    source = (REPO_ROOT / "src" / "mcc_evidence" / "tc001_certificate.py").read_text(encoding="utf-8")
    imported = _imported_modules(source)
    assert not any(m.startswith(("mcc_core.gate", "mcc_core.authority", "gateway")) for m in imported)


def test_tc_model_004_certificate_traceable_to_subject_spec_manifest_bundle(env):
    signed = _build_and_sign(env)
    assert signed.subject_id == SUBJECT_ID
    assert signed.cp001_specification_version == "1.0"
    assert signed.manifest_reference.manifest_id == "wave-c-manifest"
    assert signed.evidence_bundle_reference.bundle_id == "wave-c-bundle"


# ---------------------------------------------------------------------------
# TC-SCHEMA-001..005 — Certificate Schema
# ---------------------------------------------------------------------------


def test_tc_schema_001_certificate_is_a_single_structured_document(env):
    signed = _build_and_sign(env)
    path = write_tc001_certificate(signed, env["tmp_path"] / "cert.json")
    assert path.is_file()
    json.loads(path.read_bytes())  # a single parseable JSON document


def test_tc_schema_002_every_field_has_an_unambiguous_type(env):
    signed = _build_and_sign(env)
    d = signed.to_dict()
    assert isinstance(d["certificate_id"], str)
    assert isinstance(d["issuance_timestamp"], int)
    assert isinstance(d["certified_capability_profiles"], list)
    assert isinstance(d["manifest_reference"], dict)


def test_tc_schema_003_top_level_groups_all_present_except_optional(env):
    signed = _build_and_sign(env)
    d = signed.to_dict()
    for required_group in (
        "certificate_id", "subject_id", "certification_result", "issuer_id",
        "issuance_timestamp", "manifest_reference", "evidence_bundle_reference", "kid", "sig",
    ):
        assert required_group in d
    assert "expiration_timestamp" not in d  # optional, correctly absent


def test_tc_schema_004_signing_canonical_form_excludes_signature_field(env):
    cert = build_technical_certificate(
        certificate_id="cert-x", subject_id=SUBJECT_ID, cp001_specification_version="1.0",
        certified_capability_profiles=("baseline",), manifest_path=env["manifest_path"],
        manifest_id="wave-c-manifest", primary_evidence_bundle_path=env["bundle_path"],
        issuer_id=ISSUER_ID, issuance_timestamp=ISSUANCE_TS, id_registry=env["id_registry"],
    )
    unsigned = cert.unsigned_dict()
    assert "kid" not in unsigned and "sig" not in unsigned


def test_tc_schema_005_schema_independent_of_serialization_technology(env):
    signed = _build_and_sign(env)
    # The in-memory dataclass -> dict form round-trips independent of the
    # JSON file writer; to_dict()/from_dict() never touch a file.
    reconstructed = TechnicalCertificate.from_dict(signed.to_dict())
    assert reconstructed.to_dict() == signed.to_dict()


# ---------------------------------------------------------------------------
# TC-ID-001..003 — Certificate Identity
# ---------------------------------------------------------------------------


def test_tc_id_001_certificate_has_a_unique_identifier(env):
    signed = _build_and_sign(env)
    assert signed.certificate_id == "cert-1"


def test_tc_id_002_identifier_reuse_is_rejected_including_after_revocation(env):
    _build_and_sign(env, certificate_id="cert-reuse")
    with pytest.raises(IncompleteTC001CertificateError):
        build_technical_certificate(
            certificate_id="cert-reuse", subject_id=SUBJECT_ID, cp001_specification_version="1.0",
            certified_capability_profiles=("baseline",), manifest_path=env["manifest_path"],
            manifest_id="wave-c-manifest", primary_evidence_bundle_path=env["bundle_path"],
            issuer_id=ISSUER_ID, issuance_timestamp=ISSUANCE_TS + 1, id_registry=env["id_registry"],
        )


def test_tc_id_003_revalidation_produces_a_new_certificate_with_a_new_id(env):
    first = _build_and_sign(env, certificate_id="cert-v1")
    second = _build_and_sign(env, certificate_id="cert-v2", superseded_certificate_ids=("cert-v1",))
    assert first.certificate_id != second.certificate_id
    assert second.superseded_certificate_ids == ("cert-v1",)


# ---------------------------------------------------------------------------
# TC-RFLD-001..006 — Required Fields
# ---------------------------------------------------------------------------


def test_tc_rfld_001_baseline_required_fields_present(env):
    signed = _build_and_sign(env)
    d = signed.to_dict()
    for f in (
        "certificate_id", "subject_id", "cp001_specification_version", "certification_result",
        "certified_capability_profiles", "manifest_reference", "evidence_bundle_reference", "issuance_timestamp",
    ):
        assert f in d


def test_tc_rfld_002_issuer_validity_and_signature_present(env):
    signed = _build_and_sign(env)
    d = signed.to_dict()
    assert "issuer_id" in d
    assert "issuance_timestamp" in d
    assert "kid" in d and "sig" in d


def test_tc_rfld_003_certificate_omitting_a_required_field_is_rejected(env):
    signed = _build_and_sign(env)
    d = signed.to_dict()
    del d["subject_id"]
    with pytest.raises(TC001StructuralError):
        TechnicalCertificate.from_dict(d)


def test_tc_rfld_004_manifest_reference_structure(env):
    signed = _build_and_sign(env)
    mr = signed.manifest_reference
    assert mr.manifest_id and mr.manifest_schema_version
    assert isinstance(mr.hash_reference, HashReference)


def test_tc_rfld_005_evidence_bundle_reference_structure(env):
    signed = _build_and_sign(env)
    ebr = signed.evidence_bundle_reference
    assert ebr.bundle_id and ebr.schema_version
    assert isinstance(ebr.hash_reference, HashReference)


def test_tc_rfld_006_evidence_bundle_reference_is_direct_not_transitive_only(env):
    signed = _build_and_sign(env)
    d = signed.to_dict()
    # present directly on the Certificate, not only reachable via the Manifest
    assert "evidence_bundle_reference" in d
    assert d["evidence_bundle_reference"]["bundle_id"] == "wave-c-bundle"


# ---------------------------------------------------------------------------
# TC-OPTF-001..003 — Optional Fields
# ---------------------------------------------------------------------------


def test_tc_optf_001_optional_fields_may_be_omitted(env):
    signed = _build_and_sign(env)
    assert signed.label is None
    assert signed.expiration_timestamp is None
    result = _verify(env, signed.to_dict())
    assert result.valid


def test_tc_optf_002_optional_fields_conform_to_type_rules_when_present(env):
    signed = _build_and_sign(env, certificate_id="cert-label", label="pilot-run-1")
    assert signed.label == "pilot-run-1"
    d = signed.to_dict()
    d["label"] = 12345  # wrong type
    with pytest.raises(TC001StructuralError):
        TechnicalCertificate.from_dict(d)


def test_tc_optf_003_optional_fields_do_not_satisfy_required_field_obligations(env):
    # Even with every optional field populated, all Required Fields must
    # still independently be present -- optional fields are additive only.
    signed = _build_and_sign(env, certificate_id="cert-full-optional", label="l", superseded_certificate_ids=("x",))
    d = signed.to_dict()
    del d["subject_id"]
    with pytest.raises(TC001StructuralError):
        TechnicalCertificate.from_dict(d)


# ---------------------------------------------------------------------------
# TC-SUBJ-001 — Subject Identification (self-consistency only; see module
# docstring for the documented Manifest-side exclusion of TC-SUBJ-002/003)
# ---------------------------------------------------------------------------


def test_tc_subj_001_certificate_identifies_exactly_one_subject(env):
    signed = _build_and_sign(env)
    assert isinstance(signed.subject_id, str) and signed.subject_id


# ---------------------------------------------------------------------------
# TC-RES-001, TC-RES-003 — Certification Result Representation (TC-RES-002
# manifest-side cross-check excluded; see module docstring)
# ---------------------------------------------------------------------------


def test_tc_res_001_result_field_present_and_pass(env):
    signed = _build_and_sign(env)
    assert signed.certification_result == "PASS"


def test_tc_res_001_negative_result_field_rejects_non_pass():
    d = {
        "certificate_schema_version": TC001_CERT_SCHEMA_VERSION,
        "certificate_id": "x", "cp001_specification_version": "1.0", "subject_id": "s",
        "certification_result": "FAIL", "certified_capability_profiles": ["baseline"],
        "manifest_reference": {"manifest_id": "m", "manifest_schema_version": "mcc-cm-001/1",
                                "hash_reference": {"digest": "sha256:" + "0" * 64, "algorithm": "sha256", "content_ref": "m"}},
        "evidence_bundle_reference": {"bundle_id": "b", "schema_version": "mcc-eb-001/1",
                                       "hash_reference": {"digest": "sha256:" + "0" * 64, "algorithm": "sha256", "content_ref": "b"}},
        "issuer_id": "i", "signature_algorithm": "Ed25519", "issuance_timestamp": 1, "kid": "k", "sig": "s",
    }
    with pytest.raises(TC001StructuralError):
        TechnicalCertificate.from_dict(d)


def test_tc_res_003_certified_profiles_limited_to_those_verified(env):
    signed = _build_and_sign(env, certified_capability_profiles=("baseline", "infra"))
    assert set(signed.certified_capability_profiles) == {"baseline", "infra"}


# ---------------------------------------------------------------------------
# TC-ISS-001..003 — Issuer Information
# ---------------------------------------------------------------------------


def test_tc_iss_001_certificate_identifies_its_issuer(env):
    signed = _build_and_sign(env)
    assert signed.issuer_id == ISSUER_ID


def test_tc_iss_002_issuer_identifier_associated_with_resolvable_trust_anchor(env):
    signed = _build_and_sign(env)
    anchor = env["trust"].resolve(signed.kid)
    assert anchor is not None
    assert anchor.issuer_id == signed.issuer_id


def test_tc_iss_003_unrecognized_issuer_causes_verification_failure(env):
    signed = _build_and_sign(env)
    empty_trust = TrustAnchorRegistry()
    result = _verify(env, signed.to_dict(), trust=empty_trust)
    assert not result.valid
    assert result.overall_status is TC001Status.INVALID


# ---------------------------------------------------------------------------
# TC-VALID-001..004 — Validity Period
# ---------------------------------------------------------------------------


def test_tc_valid_001_issuance_timestamp_recorded(env):
    signed = _build_and_sign(env)
    assert signed.issuance_timestamp == ISSUANCE_TS


def test_tc_valid_002_not_valid_before_issuance(env):
    signed = _build_and_sign(env)
    result = _verify(env, signed.to_dict(), now=ISSUANCE_TS - 10)
    assert not result.valid
    assert result.check("validity_period").status.value == "FAIL"


def test_tc_valid_003_expired_certificate_not_treated_as_valid(env):
    signed = _build_and_sign(env, certificate_id="cert-exp", expiration_timestamp=ISSUANCE_TS + 100)
    result = _verify(env, signed.to_dict(), now=ISSUANCE_TS + 200)
    assert not result.valid


def test_tc_valid_004_absence_of_expiration_is_not_a_failure(env):
    signed = _build_and_sign(env)
    assert signed.expiration_timestamp is None
    result = _verify(env, signed.to_dict(), now=ISSUANCE_TS + 10_000_000)
    assert result.valid


# ---------------------------------------------------------------------------
# TC-REV-001..006 — Revocation Model
# ---------------------------------------------------------------------------


def test_tc_rev_001_certificate_content_never_mutated_to_represent_revocation(env):
    signed = _build_and_sign(env, certificate_id="cert-rev-1")
    before = signed.to_dict()
    anchor = env["trust"].resolve(signed.kid)
    revoke_certificate(env["revocation"], "cert-rev-1", ISSUANCE_TS + 10, issuing_trust_anchor=anchor)
    assert signed.to_dict() == before  # the Certificate object itself is untouched


def test_tc_rev_002_revocation_represented_by_an_external_record(env):
    signed = _build_and_sign(env, certificate_id="cert-rev-2")
    anchor = env["trust"].resolve(signed.kid)
    record = revoke_certificate(env["revocation"], "cert-rev-2", ISSUANCE_TS + 10, issuing_trust_anchor=anchor)
    assert env["revocation"].get("cert-rev-2") is record


def test_tc_rev_003_revocation_record_identifies_required_fields(env):
    signed = _build_and_sign(env, certificate_id="cert-rev-3")
    anchor = env["trust"].resolve(signed.kid)
    record = revoke_certificate(env["revocation"], "cert-rev-3", ISSUANCE_TS + 10, issuing_trust_anchor=anchor, reason="key compromise")
    assert record.certificate_id == "cert-rev-3"
    assert record.revoked_at == ISSUANCE_TS + 10
    assert record.issuer_id == ISSUER_ID
    assert record.reason == "key compromise"


def test_tc_rev_004_only_the_issuer_may_produce_a_valid_revocation(env):
    from mcc_evidence.tc001_certificate import RevocationRecord

    signed = _build_and_sign(env, certificate_id="cert-rev-4")
    other_key = SigningKey.generate("other-issuer-key")
    other_anchor = TrustAnchor(issuer_id="not-the-real-issuer", kid="other-issuer-key", public_key=other_key.public_key())
    # a Revocation Record claiming the REAL issuer_id, presented alongside a
    # Trust Anchor for a DIFFERENT issuer -- the registry must independently
    # cross-check, not trust the record's self-declared issuer_id.
    mismatched_record = RevocationRecord(certificate_id="cert-rev-4", revoked_at=ISSUANCE_TS + 10, issuer_id=ISSUER_ID)
    with pytest.raises(TC001Error):
        env["revocation"].revoke(mismatched_record, issuing_trust_anchor=other_anchor)


def test_tc_rev_005_verifier_checks_revocation_before_treating_as_valid(env):
    signed = _build_and_sign(env, certificate_id="cert-rev-5")
    anchor = env["trust"].resolve(signed.kid)
    revoke_certificate(env["revocation"], "cert-rev-5", ISSUANCE_TS + 10, issuing_trust_anchor=anchor)
    result = _verify(env, signed.to_dict(), now=ISSUANCE_TS + 20)
    assert not result.valid
    assert result.check("revocation_check").status.value == "FAIL"


def test_tc_rev_006_revoked_certificates_remain_available_for_audit(env):
    signed = _build_and_sign(env, certificate_id="cert-rev-6")
    anchor = env["trust"].resolve(signed.kid)
    revoke_certificate(env["revocation"], "cert-rev-6", ISSUANCE_TS + 10, issuing_trust_anchor=anchor)
    assert env["revocation"].is_revoked("cert-rev-6")
    assert env["revocation"].get("cert-rev-6") is not None
    # the Certificate itself remains fully readable/parseable
    assert TechnicalCertificate.from_dict(signed.to_dict()).certificate_id == "cert-rev-6"


# ---------------------------------------------------------------------------
# TC-HASH-001..003 — Cryptographic Integrity
# ---------------------------------------------------------------------------


def test_tc_hash_001_manifest_and_bundle_hash_references_use_sha256(env):
    signed = _build_and_sign(env)
    assert signed.manifest_reference.hash_reference.algorithm == "sha256"
    assert signed.evidence_bundle_reference.hash_reference.algorithm == "sha256"


def test_tc_hash_002_bindings_are_independently_recomputable(env):
    signed = _build_and_sign(env)
    result = _verify(env, signed.to_dict())
    assert result.check("manifest_reference_verification").status.value == "PASS"
    assert result.check("evidence_bundle_reference_consistency").status.value == "PASS"


def test_tc_hash_003_whole_certificate_integrity_via_signature_not_a_self_digest(env):
    signed = _build_and_sign(env)
    d = signed.to_dict()
    assert "digest" not in d  # no separate self-digest field; the Signature covers everything
    assert "sig" in d


# ---------------------------------------------------------------------------
# TC-SIG-001..005 — Signature Requirements
# ---------------------------------------------------------------------------


def test_tc_sig_001_certificate_signed_with_asymmetric_scheme(env):
    signed = _build_and_sign(env)
    assert signed.signature_algorithm == "Ed25519"


def test_tc_sig_002_symmetric_key_mechanisms_never_used():
    # Guard the actual import graph, not documentation prose (this module's
    # own docstrings discuss why HMAC is excluded, which would otherwise
    # trip a naive substring search).
    source = (REPO_ROOT / "src" / "mcc_evidence" / "tc001_certificate.py").read_text(encoding="utf-8")
    imported = _imported_modules(source)
    assert "hmac" not in imported


def test_tc_sig_003_signature_covers_complete_canonical_form_excluding_itself(env):
    signed = _build_and_sign(env)
    tampered = dict(signed.to_dict())
    tampered["issuer_id"] = "someone-else"
    result = _verify(env, tampered)
    assert not result.valid
    assert result.check("signature_verification").status.value == "FAIL"


def test_tc_sig_004_certificate_declares_algorithm_and_issuer_identity(env):
    signed = _build_and_sign(env)
    d = signed.to_dict()
    assert d["signature_algorithm"] == "Ed25519"
    assert d["issuer_id"] == ISSUER_ID
    assert d["kid"] == "issuer-key-1"


def test_tc_sig_005_modification_of_any_signed_field_invalidates_signature(env):
    signed = _build_and_sign(env)
    for field_name, new_value in (
        ("certificate_id", "different-id"),
        ("issuance_timestamp", ISSUANCE_TS + 1),
        ("certified_capability_profiles", ["other"]),
    ):
        tampered = dict(signed.to_dict())
        tampered[field_name] = new_value
        result = _verify(env, tampered)
        assert not result.valid, field_name


# ---------------------------------------------------------------------------
# TC-VERIFY-001..006 — Verification Procedure
# ---------------------------------------------------------------------------


def test_tc_verify_001_verification_is_fail_closed(env):
    result = _verify(env, {"not": "a certificate"})
    assert result.overall_status is TC001Status.UNSUPPORTED_SCHEMA


def test_tc_verify_002_structural_verification_precedes_everything_else(env):
    # A structurally-broken certificate never reaches signature verification.
    result = _verify(env, {"certificate_schema_version": TC001_CERT_SCHEMA_VERSION})
    assert result.check("structural_verification").status.value == "FAIL"
    assert result.check("signature_verification") is None


def test_tc_verify_003_signature_verified_against_a_trust_anchor(env):
    signed = _build_and_sign(env)
    result = _verify(env, signed.to_dict())
    assert result.check("signature_verification").status.value == "PASS"


def test_tc_verify_004_validity_and_revocation_both_checked(env):
    signed = _build_and_sign(env, certificate_id="cert-verify-004")
    result = _verify(env, signed.to_dict())
    assert result.check("validity_period").status.value == "PASS"
    assert result.check("revocation_check").status.value == "PASS"


def test_tc_verify_005_any_failing_step_rejects_the_whole_certificate(env):
    signed = _build_and_sign(env)
    tampered = dict(signed.to_dict())
    tampered["sig"] = "invalid-signature-value"
    result = _verify(env, tampered)
    assert result.overall_status is TC001Status.INVALID


def test_tc_verify_006_mismatched_direct_and_manifest_evidence_bundle_references_rejected(env, tmp_path):
    other_bundle_path = _build_bundle(tmp_path, bundle_id="wave-c-bundle-other")
    signed = _build_and_sign(env, certificate_id="cert-verify-006")
    # Craft a certificate whose direct reference points at a DIFFERENT bundle
    # than the Manifest's own primary reference -- bypassing the producer's
    # own pre-issuance check by hand-building the object directly.
    from dataclasses import replace as _replace
    bad_ref = build_direct_evidence_bundle_reference(other_bundle_path)
    tampered = _replace(signed, evidence_bundle_reference=bad_ref)
    from mcc_core.signing import SigningKey as _SK
    resigned = sign_technical_certificate(
        TechnicalCertificate(**{**tampered.__dict__, "kid": None, "sig": None}), env["key"],
    )
    result = _verify(env, resigned.to_dict())
    assert not result.valid
    assert result.check("evidence_bundle_reference_consistency").status.value == "FAIL"


# ---------------------------------------------------------------------------
# TC-TRUST-001..004 — Trust Model
# ---------------------------------------------------------------------------


def test_tc_trust_001_verifier_relies_only_on_recognized_trust_anchors(env):
    signed = _build_and_sign(env)
    result = _verify(env, signed.to_dict(), trust=TrustAnchorRegistry())
    assert not result.valid


def test_tc_trust_002_trust_not_inferred_from_self_declared_issuer_alone(env):
    signed = _build_and_sign(env)
    tampered = dict(signed.to_dict())
    tampered["issuer_id"] = "a-completely-different-issuer"
    # the signature itself becomes invalid because issuer_id is signed content
    result = _verify(env, tampered)
    assert not result.valid


def test_tc_trust_003_rotation_does_not_retroactively_invalidate_historical_issuance(env):
    signed = _build_and_sign(env, certificate_id="cert-trust-003")
    before_content = signed.to_dict()
    env["trust"].revoke_key("issuer-key-1")
    result = _verify(env, signed.to_dict())
    assert not result.valid  # no longer currently trusted
    assert signed.to_dict() == before_content  # but the historical record is untouched


def test_tc_trust_004_verifier_may_recognize_multiple_trust_anchors(env):
    other_key = SigningKey.generate("issuer-key-2")
    env["trust"].add(TrustAnchor(issuer_id="axlogiq-ca-2", kid="issuer-key-2", public_key=other_key.public_key()))
    signed = _build_and_sign(env, certificate_id="cert-multi-anchor")
    result = _verify(env, signed.to_dict())
    assert result.valid


# ---------------------------------------------------------------------------
# TC-COMPAT-001..004 — Compatibility
# ---------------------------------------------------------------------------


def test_tc_compat_001_schema_version_compatibility_is_explicit(env):
    signed = _build_and_sign(env)
    assert signed.certificate_schema_version == TC001_CERT_SCHEMA_VERSION


def test_tc_compat_002_unrecognized_schema_version_not_silently_accepted(env):
    signed = _build_and_sign(env)
    d = dict(signed.to_dict())
    d["certificate_schema_version"] = "mcc-tc-001/99"
    result = _verify(env, d)
    assert result.overall_status is TC001Status.UNSUPPORTED_SCHEMA


def test_tc_compat_003_validity_accounts_for_manifest_schema_version_compatibility(env, tmp_path):
    # A Certification Manifest whose own manifest_schema_version is
    # genuinely unsupported (not a tampered Certificate field). The
    # producer's internal verify_cm001_manifest pre-issuance check (reused
    # unmodified from Wave B) refuses to issue a Certificate against it at
    # all -- a stronger guarantee than rejecting it only at verification
    # time.
    from mcc_core.signing import canonical_bytes
    from mcc_evidence.cm001_manifest import build_evidence_bundle_reference

    bad_manifest_path = tmp_path / "manifest-unsupported-schema.json"
    bad_manifest_path.write_bytes(canonical_bytes({
        "manifest_schema_version": "mcc-cm-001/99",
        "primary_evidence_bundle_reference": build_evidence_bundle_reference(env["bundle_path"]).to_dict(),
        "supplementary_evidence_bundle_references": [],
    }))
    with pytest.raises(IncompleteTC001CertificateError):
        build_technical_certificate(
            certificate_id="cert-compat-003", subject_id=SUBJECT_ID, cp001_specification_version="1.0",
            certified_capability_profiles=("baseline",), manifest_path=bad_manifest_path,
            manifest_id="manifest-bad-schema", primary_evidence_bundle_path=env["bundle_path"],
            issuer_id=ISSUER_ID, issuance_timestamp=ISSUANCE_TS,
        )


def test_tc_compat_004_validity_accounts_for_evidence_bundle_schema_version_compatibility(env, tmp_path):
    # An Evidence Bundle whose own Bundle Descriptor/Integrity Record
    # declare a genuinely unsupported schema_version (self-consistent
    # otherwise). The producer's internal verify_cm001_manifest pre-
    # issuance check transitively verifies the referenced Bundle
    # (verify_eb001_bundle) and refuses to issue against it.
    bad_bundle_path = _build_bad_schema_bundle(tmp_path / "bad-schema-bundle", bundle_id="wave-c-bundle-bad-schema")
    bad_manifest = build_cm001_manifest(bad_bundle_path)
    bad_manifest_path = write_cm001_manifest(bad_manifest, tmp_path / "bad-schema-manifest.json")
    with pytest.raises(IncompleteTC001CertificateError):
        build_technical_certificate(
            certificate_id="cert-compat-004", subject_id=SUBJECT_ID, cp001_specification_version="1.0",
            certified_capability_profiles=("baseline",), manifest_path=bad_manifest_path,
            manifest_id="manifest-for-bad-bundle", primary_evidence_bundle_path=bad_bundle_path,
            issuer_id=ISSUER_ID, issuance_timestamp=ISSUANCE_TS,
        )


# ---------------------------------------------------------------------------
# TC-VSN-001..004 — Versioning
# ---------------------------------------------------------------------------


def test_tc_vsn_001_certificate_declares_a_schema_version(env):
    signed = _build_and_sign(env)
    assert signed.certificate_schema_version


def test_tc_vsn_002_schema_version_constant_is_immutable_string():
    assert TC001_CERT_SCHEMA_VERSION == "mcc-tc-001/1"


def test_tc_vsn_003_schema_version_tracked_independently_of_other_specs(env):
    signed = _build_and_sign(env)
    assert signed.certificate_schema_version != signed.cp001_specification_version
    assert signed.certificate_schema_version != signed.manifest_reference.manifest_schema_version
    assert signed.certificate_schema_version != signed.evidence_bundle_reference.schema_version


def test_tc_vsn_004_unrecognized_schema_version_causes_verification_failure(env):
    signed = _build_and_sign(env)
    d = dict(signed.to_dict())
    d["certificate_schema_version"] = "not-a-real-version"
    result = _verify(env, d)
    assert result.overall_status is TC001Status.UNSUPPORTED_SCHEMA


# ---------------------------------------------------------------------------
# TC-SEC-001..005 — Security Considerations
# ---------------------------------------------------------------------------


def test_tc_sec_001_verification_assumes_untrusted_source(env):
    forged = {
        "certificate_schema_version": TC001_CERT_SCHEMA_VERSION, "certificate_id": "forged",
        "cp001_specification_version": "1.0", "subject_id": "attacker", "certification_result": "PASS",
        "certified_capability_profiles": ["baseline"],
        "manifest_reference": {"manifest_id": "m", "manifest_schema_version": "mcc-cm-001/1",
                                "hash_reference": {"digest": "sha256:" + "1" * 64, "algorithm": "sha256", "content_ref": "m"}},
        "evidence_bundle_reference": {"bundle_id": "b", "schema_version": "mcc-eb-001/1",
                                       "hash_reference": {"digest": "sha256:" + "1" * 64, "algorithm": "sha256", "content_ref": "b"}},
        "issuer_id": ISSUER_ID, "signature_algorithm": "Ed25519", "issuance_timestamp": 1,
        "kid": "issuer-key-1", "sig": "forged-signature-bytes-not-real",
    }
    result = _verify(env, forged)
    assert not result.valid


def test_tc_sec_002_forgery_resistance_via_signature_only(env):
    signed = _build_and_sign(env)
    d = dict(signed.to_dict())
    d["sig"] = "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
    result = _verify(env, d)
    assert not result.valid


def test_tc_sec_003_certificate_contains_no_secrets_or_credentials(env):
    signed = _build_and_sign(env)
    d = signed.to_dict()
    for forbidden in ("password", "secret", "private_key", "credential", "api_key"):
        assert forbidden not in d


def test_tc_sec_004_sensitive_data_referenced_only_via_hash_reference(env):
    signed = _build_and_sign(env)
    d = signed.to_dict()
    # Manifest and Evidence Bundle content is referenced only by Hash
    # Reference, never embedded raw.
    assert set(d["manifest_reference"]["hash_reference"].keys()) == {"digest", "algorithm", "content_ref"}
    assert set(d["evidence_bundle_reference"]["hash_reference"].keys()) == {"digest", "algorithm", "content_ref"}


def test_tc_sec_005_valid_certificate_not_treated_as_runtime_execution_authorization():
    source = (REPO_ROOT / "src" / "mcc_evidence" / "tc001_certificate.py").read_text(encoding="utf-8")
    imported = _imported_modules(source)
    forbidden_modules = {"gateway", "gateway.trust", "gateway.app", "mcc_core.gate", "mcc_core.authority",
                          "mcc_core.coordinator", "egress_proxy", "interceptors"}
    assert not (imported & forbidden_modules), imported & forbidden_modules


# ---------------------------------------------------------------------------
# TC-CONF-001..005 — Conformance Requirements
# ---------------------------------------------------------------------------


def test_tc_conf_001_conformance_defined_separately_for_issuer_and_verifier(env):
    signed = _build_and_sign(env)
    assert signed.is_signed  # issuer-side artifact
    result = _verify(env, signed.to_dict())  # verifier-side procedure
    assert result.valid


def test_tc_conf_002_issuer_never_issues_for_a_non_pass_result():
    import inspect
    params = inspect.signature(build_technical_certificate).parameters
    assert "certification_result" not in params


def test_tc_conf_003_verifier_implements_fail_closed_verification_including_revocation(env):
    signed = _build_and_sign(env, certificate_id="cert-conf-003")
    anchor = env["trust"].resolve(signed.kid)
    revoke_certificate(env["revocation"], "cert-conf-003", ISSUANCE_TS + 5, issuing_trust_anchor=anchor)
    result = _verify(env, signed.to_dict(), now=ISSUANCE_TS + 10)
    assert not result.valid


def test_tc_conf_004_conformance_is_framework_neutral():
    source = (REPO_ROOT / "src" / "mcc_evidence" / "tc001_certificate.py").read_text(encoding="utf-8")
    for framework_marker in ("langgraph", "autogen", "crewai", "voltagent", "fastapi", "flask", "django"):
        assert framework_marker not in source.lower()


def test_tc_conf_005_issuer_ensures_reference_consistency_before_issuance(env, tmp_path):
    other_bundle_path = _build_bundle(tmp_path, bundle_id="wave-c-bundle-mismatch")
    with pytest.raises(IncompleteTC001CertificateError):
        build_technical_certificate(
            certificate_id="cert-conf-005", subject_id=SUBJECT_ID, cp001_specification_version="1.0",
            certified_capability_profiles=("baseline",), manifest_path=env["manifest_path"],
            manifest_id="wave-c-manifest",
            primary_evidence_bundle_path=other_bundle_path,  # mismatched vs. the Manifest's own bundle
            issuer_id=ISSUER_ID, issuance_timestamp=ISSUANCE_TS, id_registry=env["id_registry"],
        )


# ---------------------------------------------------------------------------
# 24 numbered negative scenarios
# ---------------------------------------------------------------------------


def test_scenario_01_missing_required_field_rejected(env):
    signed = _build_and_sign(env)
    d = dict(signed.to_dict())
    del d["certificate_id"]
    with pytest.raises(TC001StructuralError):
        TechnicalCertificate.from_dict(d)


def test_scenario_02_undeclared_extra_field_rejected(env):
    signed = _build_and_sign(env)
    d = dict(signed.to_dict())
    d["secret_backdoor_field"] = "smuggled"
    with pytest.raises(TC001StructuralError):
        TechnicalCertificate.from_dict(d)


def test_scenario_03_non_pass_result_rejected(env):
    signed = _build_and_sign(env)
    d = dict(signed.to_dict())
    d["certification_result"] = "FAIL"
    with pytest.raises(TC001StructuralError):
        TechnicalCertificate.from_dict(d)


def test_scenario_04_unrecognized_schema_version_yields_unsupported_schema(env):
    signed = _build_and_sign(env)
    d = dict(signed.to_dict())
    d["certificate_schema_version"] = "mcc-tc-001/2"
    result = _verify(env, d)
    assert result.overall_status is TC001Status.UNSUPPORTED_SCHEMA


def test_scenario_05_producer_refuses_empty_capability_profiles(env):
    with pytest.raises(IncompleteTC001CertificateError):
        build_technical_certificate(
            certificate_id="cert-empty-profiles", subject_id=SUBJECT_ID, cp001_specification_version="1.0",
            certified_capability_profiles=(), manifest_path=env["manifest_path"], manifest_id="wave-c-manifest",
            primary_evidence_bundle_path=env["bundle_path"], issuer_id=ISSUER_ID,
            issuance_timestamp=ISSUANCE_TS, id_registry=env["id_registry"],
        )


def test_scenario_06_from_dict_rejects_empty_capability_profiles_list(env):
    signed = _build_and_sign(env)
    d = dict(signed.to_dict())
    d["certified_capability_profiles"] = []
    with pytest.raises(TC001StructuralError):
        TechnicalCertificate.from_dict(d)


def test_scenario_07_manifest_reference_content_ref_mismatch_rejected(env):
    # The bad content_ref is embedded BEFORE signing, so the certificate is
    # internally self-consistent (signature verifies) and the defect is
    # caught specifically by the manifest_reference_verification step's own
    # content_ref binding check, not masked by an upstream signature failure.
    cert = _build_unsigned(env, certificate_id="cert-scenario-07")
    bad_hash_ref = _dc_replace(cert.manifest_reference.hash_reference, content_ref="not-the-real-manifest-id")
    cert = _dc_replace(cert, manifest_reference=_dc_replace(cert.manifest_reference, hash_reference=bad_hash_ref))
    signed = sign_technical_certificate(cert, env["key"])
    result = _verify(env, signed.to_dict())
    assert not result.valid
    assert result.check("manifest_reference_verification").status.value == "FAIL"


def test_scenario_08_manifest_tampered_after_issuance_rejected(env):
    signed = _build_and_sign(env, certificate_id="cert-scenario-08")
    env["manifest_path"].write_bytes(
        b'{"manifest_schema_version": "mcc-cm-001/1", "tampered": true, '
        b'"primary_evidence_bundle_reference": {"bundle_id": "x", "schema_version": "mcc-eb-001/1", '
        b'"hash_references": [{"digest": "sha256:' + b"0" * 64 + b'", "algorithm": "sha256", "content_ref": "x"}]}, '
        b'"supplementary_evidence_bundle_references": []}'
    )
    result = _verify(env, signed.to_dict())
    assert not result.valid
    assert result.check("manifest_reference_verification").status.value == "FAIL"


def test_scenario_09_producer_refuses_mismatched_direct_and_manifest_bundle_references(env, tmp_path):
    other_bundle_path = _build_bundle(tmp_path, bundle_id="wave-c-bundle-scenario-09")
    with pytest.raises(IncompleteTC001CertificateError):
        build_technical_certificate(
            certificate_id="cert-scenario-09", subject_id=SUBJECT_ID, cp001_specification_version="1.0",
            certified_capability_profiles=("baseline",), manifest_path=env["manifest_path"],
            manifest_id="wave-c-manifest", primary_evidence_bundle_path=other_bundle_path,
            issuer_id=ISSUER_ID, issuance_timestamp=ISSUANCE_TS, id_registry=env["id_registry"],
        )


def test_scenario_10_verifier_rejects_mismatched_direct_and_manifest_bundle_references(env, tmp_path):
    test_tc_verify_006_mismatched_direct_and_manifest_evidence_bundle_references_rejected(env, tmp_path)


def test_scenario_11_referenced_bundle_tampered_after_issuance_rejected(env):
    # Tampering the externally-referenced Evidence Bundle (not the
    # Certificate itself) is caught at Section 15.4 already, because
    # Manifest Reference verification re-verifies the whole Manifest
    # (transitively, the Bundle it references) via verify_cm001_manifest --
    # Section 15.5's Certificate-side re-check is only reached once 15.4
    # itself succeeds.
    signed = _build_and_sign(env, certificate_id="cert-scenario-11")
    (env["bundle_path"] / "evidence" / "req-TC-001.json").write_bytes(b"tampered content")
    result = _verify(env, signed.to_dict())
    assert not result.valid
    assert result.check("manifest_reference_verification").status.value == "FAIL"


def test_scenario_12_unknown_signing_kid_rejected(env):
    signed = _build_and_sign(env)
    result = _verify(env, signed.to_dict(), trust=TrustAnchorRegistry())
    assert not result.valid
    assert result.check("signature_verification").status.value == "FAIL"


def test_scenario_13_forged_signature_rejected(env):
    signed = _build_and_sign(env)
    d = dict(signed.to_dict())
    d["sig"] = d["sig"][:-4] + "AAAA"
    result = _verify(env, d)
    assert not result.valid


def test_scenario_14_issuer_id_mismatch_with_trust_anchor_rejected(env):
    other_key = SigningKey.generate("issuer-key-mismatch")
    env["trust"].add(TrustAnchor(issuer_id="a-different-issuer", kid="issuer-key-mismatch", public_key=other_key.public_key()))
    cert = build_technical_certificate(
        certificate_id="cert-scenario-14", subject_id=SUBJECT_ID, cp001_specification_version="1.0",
        certified_capability_profiles=("baseline",), manifest_path=env["manifest_path"],
        manifest_id="wave-c-manifest", primary_evidence_bundle_path=env["bundle_path"],
        issuer_id=ISSUER_ID,  # declares the ORIGINAL issuer...
        issuance_timestamp=ISSUANCE_TS, id_registry=env["id_registry"],
    )
    signed = sign_technical_certificate(cert, other_key)  # ...but signs with a DIFFERENT issuer's key
    result = _verify(env, signed.to_dict())
    assert not result.valid
    assert result.check("signature_verification").status.value == "FAIL"


def test_scenario_15_revoked_trust_anchor_key_rejected(env):
    signed = _build_and_sign(env, certificate_id="cert-scenario-15")
    env["trust"].revoke_key("issuer-key-1")
    result = _verify(env, signed.to_dict())
    assert not result.valid


def test_scenario_16_expired_certificate_rejected(env):
    signed = _build_and_sign(env, certificate_id="cert-scenario-16", expiration_timestamp=ISSUANCE_TS + 50)
    result = _verify(env, signed.to_dict(), now=ISSUANCE_TS + 1000)
    assert not result.valid


def test_scenario_17_not_yet_valid_certificate_rejected(env):
    signed = _build_and_sign(env, certificate_id="cert-scenario-17")
    result = _verify(env, signed.to_dict(), now=ISSUANCE_TS - 100)
    assert not result.valid


def test_scenario_18_revoked_certificate_rejected(env):
    signed = _build_and_sign(env, certificate_id="cert-scenario-18")
    anchor = env["trust"].resolve(signed.kid)
    revoke_certificate(env["revocation"], "cert-scenario-18", ISSUANCE_TS + 5, issuing_trust_anchor=anchor)
    result = _verify(env, signed.to_dict(), now=ISSUANCE_TS + 10)
    assert not result.valid


def test_scenario_19_reused_certificate_id_rejected(env):
    _build_and_sign(env, certificate_id="cert-scenario-19")
    with pytest.raises(IncompleteTC001CertificateError):
        build_technical_certificate(
            certificate_id="cert-scenario-19", subject_id=SUBJECT_ID, cp001_specification_version="1.0",
            certified_capability_profiles=("baseline",), manifest_path=env["manifest_path"],
            manifest_id="wave-c-manifest", primary_evidence_bundle_path=env["bundle_path"],
            issuer_id=ISSUER_ID, issuance_timestamp=ISSUANCE_TS + 1, id_registry=env["id_registry"],
        )


def test_scenario_20_duplicate_trust_anchor_kid_rejected(env):
    dup_key = SigningKey.generate("issuer-key-1")  # same kid as the fixture's anchor
    with pytest.raises(TC001Error):
        env["trust"].add(TrustAnchor(issuer_id="another-issuer", kid="issuer-key-1", public_key=dup_key.public_key()))


def test_scenario_21_revoke_with_mismatched_issuer_rejected(env):
    from mcc_evidence.tc001_certificate import RevocationRecord

    signed = _build_and_sign(env, certificate_id="cert-scenario-21")
    wrong_key = SigningKey.generate("wrong-key")
    wrong_anchor = TrustAnchor(issuer_id="wrong-issuer", kid="wrong-key", public_key=wrong_key.public_key())
    mismatched_record = RevocationRecord(certificate_id="cert-scenario-21", revoked_at=ISSUANCE_TS + 5, issuer_id=ISSUER_ID)
    with pytest.raises(TC001Error):
        env["revocation"].revoke(mismatched_record, issuing_trust_anchor=wrong_anchor)


def test_scenario_22_missing_manifest_file_rejected(env, tmp_path):
    with pytest.raises(IncompleteTC001CertificateError):
        build_technical_certificate(
            certificate_id="cert-scenario-22", subject_id=SUBJECT_ID, cp001_specification_version="1.0",
            certified_capability_profiles=("baseline",), manifest_path=tmp_path / "does-not-exist.json",
            manifest_id="wave-c-manifest", primary_evidence_bundle_path=env["bundle_path"],
            issuer_id=ISSUER_ID, issuance_timestamp=ISSUANCE_TS, id_registry=env["id_registry"],
        )
    signed = _build_and_sign(env, certificate_id="cert-scenario-22b")
    result = _verify(env, signed.to_dict(), manifest_path=tmp_path / "does-not-exist.json")
    assert not result.valid


def test_scenario_23_re_signing_an_already_signed_certificate_rejected(env):
    signed = _build_and_sign(env, certificate_id="cert-scenario-23")
    with pytest.raises(TC001Error):
        sign_technical_certificate(signed, env["key"])


def test_scenario_24_malformed_hash_reference_rejected(env):
    cert = _build_unsigned(env, certificate_id="cert-scenario-24")
    malformed = HashReference(digest="not-a-real-digest", algorithm="sha256", content_ref="wave-c-manifest")
    cert = _dc_replace(cert, manifest_reference=_dc_replace(cert.manifest_reference, hash_reference=malformed))
    signed = sign_technical_certificate(cert, env["key"])
    result = _verify(env, signed.to_dict())
    assert not result.valid
    assert result.check("manifest_reference_verification").status.value == "FAIL"


# ---------------------------------------------------------------------------
# Determinism
# ---------------------------------------------------------------------------


def test_unsigned_serialization_is_deterministic(env):
    cert = build_technical_certificate(
        certificate_id="cert-determinism", subject_id=SUBJECT_ID, cp001_specification_version="1.0",
        certified_capability_profiles=("baseline",), manifest_path=env["manifest_path"],
        manifest_id="wave-c-manifest", primary_evidence_bundle_path=env["bundle_path"],
        issuer_id=ISSUER_ID, issuance_timestamp=ISSUANCE_TS,
    )
    from mcc_core.signing import canonical_bytes
    first = canonical_bytes(cert.unsigned_dict())
    second = canonical_bytes(cert.unsigned_dict())
    assert first == second


# ---------------------------------------------------------------------------
# Backward compatibility — the pre-existing certifications/manifest.json and
# gateway.trust.TrustSet are never reinterpreted by this module.
# ---------------------------------------------------------------------------


def test_legacy_compliance_manifest_never_accepted_as_a_technical_certificate():
    legacy_path = REPO_ROOT / "certifications" / "manifest.json"
    if not legacy_path.exists():
        pytest.skip("legacy certifications/manifest.json not present")
    legacy = json.loads(legacy_path.read_text(encoding="utf-8"))
    with pytest.raises(TC001StructuralError):
        TechnicalCertificate.from_dict(legacy)


def test_tc001_certificate_module_does_not_import_gateway_trust():
    source = (REPO_ROOT / "src" / "mcc_evidence" / "tc001_certificate.py").read_text(encoding="utf-8")
    imported = _imported_modules(source)
    assert not any(m == "gateway" or m.startswith("gateway.") for m in imported)
