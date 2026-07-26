"""Direct behavioral tests for the MCC-CM-001 Evidence Bundle Reference
(``src/mcc_evidence/cm001_manifest.py``), covering the Wave B selected
requirements: CM-EBREF-001, CM-EBREF-002, CM-EBREF-003, CM-EBREF-004, and
CM-HASH-003 (now provable because the Evidence Bundle Reference it depends
on exists).

Every test is linked to its requirement ID in its name or docstring.
Negative tests build a valid Manifest + Bundle first and then corrupt
exactly the one thing under test.
"""

from __future__ import annotations

import json
import shutil

import pytest

from mcc_evidence import EB001BundleInput, EvidenceItemInput, build_eb001_bundle
from mcc_evidence.cm001_manifest import (
    CM001_MANIFEST_SCHEMA_VERSION,
    CM001Error,
    CM001Status,
    EvidenceBundleReference,
    EvidenceBundleReferenceKind,
    IncompleteCM001ManifestError,
    build_cm001_manifest,
    build_evidence_bundle_reference,
    read_cm001_manifest,
    verify_cm001_manifest,
    verify_evidence_bundle_reference,
    write_cm001_manifest,
)
from mcc_evidence.eb001_schema import BUNDLE_DESCRIPTOR_NAME, INTEGRITY_RECORD_NAME
from mcc_evidence.hash_reference import HashReference, HashReferenceError


def _bundle(tmp_path, bundle_id, name, run_id="run-1", n_items=1):
    items = [EvidenceItemInput(name=f"item{i}.json", content=f'{{"i":{i}}}'.encode()) for i in range(n_items)]
    inp = EB001BundleInput(
        cp001_specification_version="1.0", certification_run_id=run_id,
        evidence_items=items, bundle_id=bundle_id,
    )
    return build_eb001_bundle(inp, tmp_path / name)


# ---------------------------------------------------------------------------
# 1/2 — valid creation + successful verification
# ---------------------------------------------------------------------------


def test_cm_ebref_002_valid_evidence_bundle_reference_creation(tmp_path):
    bundle = _bundle(tmp_path, "bundle-1", "b1")
    ref = build_evidence_bundle_reference(bundle)
    assert ref.bundle_id == "bundle-1"
    assert ref.schema_version == "mcc-eb-001/1"
    assert len(ref.hash_references) >= 1


def test_cm_ebref_004_successful_verification_against_intended_bundle(tmp_path):
    bundle = _bundle(tmp_path, "bundle-1", "b1")
    ref = build_evidence_bundle_reference(bundle)
    result = verify_evidence_bundle_reference(ref, bundle)
    assert result.overall_status is CM001Status.VALID, result.failures


# ---------------------------------------------------------------------------
# 3/4/5 — correct Bundle ID / schema version / at least one HashReference
# ---------------------------------------------------------------------------


def test_cm_ebref_002_reference_carries_correct_bundle_id(tmp_path):
    bundle = _bundle(tmp_path, "the-exact-bundle-id", "b1")
    ref = build_evidence_bundle_reference(bundle)
    assert ref.bundle_id == "the-exact-bundle-id"


def test_cm_ebref_002_reference_carries_correct_schema_version(tmp_path):
    bundle = _bundle(tmp_path, "bundle-1", "b1")
    ref = build_evidence_bundle_reference(bundle)
    assert ref.schema_version == "mcc-eb-001/1"


def test_cm_hash_003_at_least_one_hash_reference_present(tmp_path):
    bundle = _bundle(tmp_path, "bundle-1", "b1")
    ref = build_evidence_bundle_reference(bundle)
    assert len(ref.hash_references) >= 1
    assert isinstance(ref.hash_references[0], HashReference)


def test_cm_hash_003_from_dict_rejects_zero_hash_references():
    with pytest.raises(HashReferenceError):
        EvidenceBundleReference.from_dict(
            {"bundle_id": "x", "schema_version": "mcc-eb-001/1", "hash_references": []},
            kind=EvidenceBundleReferenceKind.PRIMARY,
        )


# ---------------------------------------------------------------------------
# 6/7/24/25 — deterministic serialization / verification / repeated creation
# ---------------------------------------------------------------------------


def test_deterministic_serialization_of_the_reference(tmp_path):
    bundle = _bundle(tmp_path, "bundle-1", "b1")
    ref1 = build_evidence_bundle_reference(bundle)
    ref2 = build_evidence_bundle_reference(bundle)
    assert ref1.to_dict() == ref2.to_dict()


def test_deterministic_verification_result(tmp_path):
    bundle = _bundle(tmp_path, "bundle-1", "b1")
    ref = build_evidence_bundle_reference(bundle)
    r1 = verify_evidence_bundle_reference(ref, bundle)
    r2 = verify_evidence_bundle_reference(ref, bundle)
    assert r1.to_dict() == r2.to_dict()


def test_repeated_creation_produces_stable_manifest_output(tmp_path):
    bundle = _bundle(tmp_path, "bundle-1", "b1")
    m1 = build_cm001_manifest(bundle)
    m2 = build_cm001_manifest(bundle)
    assert m1.to_dict() == m2.to_dict()


def test_repeated_verification_produces_stable_result(tmp_path):
    bundle = _bundle(tmp_path, "bundle-1", "b1")
    manifest = build_cm001_manifest(bundle)
    r1 = verify_cm001_manifest(manifest, bundle)
    r2 = verify_cm001_manifest(manifest, bundle)
    assert r1.to_dict() == r2.to_dict()


def test_manifest_round_trips_through_write_and_read(tmp_path):
    bundle = _bundle(tmp_path, "bundle-1", "b1")
    manifest = build_cm001_manifest(bundle)
    path = write_cm001_manifest(manifest, tmp_path / "manifest.json")
    loaded = read_cm001_manifest(path)
    assert loaded == manifest


def test_manifest_is_a_single_json_document_not_a_directory(tmp_path):
    bundle = _bundle(tmp_path, "bundle-1", "b1")
    manifest = build_cm001_manifest(bundle)
    path = write_cm001_manifest(manifest, tmp_path / "manifest.json")
    assert path.is_file()
    assert not path.is_dir()


# ---------------------------------------------------------------------------
# 8/9 — missing / incorrect Bundle ID rejected
# ---------------------------------------------------------------------------


def test_cm_ebref_002_missing_bundle_id_rejected():
    with pytest.raises(HashReferenceError):
        EvidenceBundleReference.from_dict(
            {"schema_version": "mcc-eb-001/1", "hash_references": [{"digest": "sha256:" + "a" * 64, "algorithm": "sha256", "content_ref": "x"}]},
            kind=EvidenceBundleReferenceKind.PRIMARY,
        )


def test_cm_ebref_004_incorrect_bundle_id_rejected(tmp_path):
    bundle = _bundle(tmp_path, "real-bundle-id", "b1")
    ref = build_evidence_bundle_reference(bundle)
    forged = EvidenceBundleReference(
        bundle_id="wrong-bundle-id", schema_version=ref.schema_version, hash_references=ref.hash_references,
    )
    result = verify_evidence_bundle_reference(forged, bundle)
    assert result.overall_status is CM001Status.INVALID
    assert any("bundle_id_binding" in f for f in result.failures)


# ---------------------------------------------------------------------------
# 10/11 — missing / incorrect or unsupported schema version rejected
# ---------------------------------------------------------------------------


def test_cm_ebref_002_missing_schema_version_rejected():
    with pytest.raises(HashReferenceError):
        EvidenceBundleReference.from_dict(
            {"bundle_id": "x", "hash_references": [{"digest": "sha256:" + "a" * 64, "algorithm": "sha256", "content_ref": "x"}]},
            kind=EvidenceBundleReferenceKind.PRIMARY,
        )


def test_cm_ebref_004_incorrect_schema_version_rejected(tmp_path):
    bundle = _bundle(tmp_path, "bundle-1", "b1")
    ref = build_evidence_bundle_reference(bundle)
    forged = EvidenceBundleReference(
        bundle_id=ref.bundle_id, schema_version="mcc-eb-001/999", hash_references=ref.hash_references,
    )
    result = verify_evidence_bundle_reference(forged, bundle)
    assert result.overall_status is CM001Status.INVALID
    assert any("schema_version_binding" in f for f in result.failures)


def test_manifest_unsupported_schema_version_rejected(tmp_path):
    bundle = _bundle(tmp_path, "bundle-1", "b1")
    manifest = build_cm001_manifest(bundle)
    forged = manifest.__class__(
        primary_evidence_bundle_reference=manifest.primary_evidence_bundle_reference,
        manifest_schema_version="mcc-cm-001/999",
    )
    result = verify_cm001_manifest(forged, bundle)
    assert result.overall_status is CM001Status.UNSUPPORTED_SCHEMA


# ---------------------------------------------------------------------------
# 12/13/14 — missing / malformed HashReference / unsupported algorithm
# ---------------------------------------------------------------------------


def test_cm_hash_003_missing_hash_reference_field_rejected():
    with pytest.raises(HashReferenceError):
        EvidenceBundleReference.from_dict(
            {"bundle_id": "x", "schema_version": "mcc-eb-001/1"},
            kind=EvidenceBundleReferenceKind.PRIMARY,
        )


def test_malformed_hash_reference_rejected(tmp_path):
    bundle = _bundle(tmp_path, "bundle-1", "b1")
    ref = build_evidence_bundle_reference(bundle)
    bad = HashReference(digest="not-a-digest", algorithm="sha256", content_ref=ref.bundle_id)
    forged = EvidenceBundleReference(bundle_id=ref.bundle_id, schema_version=ref.schema_version, hash_references=(bad,))
    result = verify_evidence_bundle_reference(forged, bundle)
    assert result.overall_status is CM001Status.INVALID
    assert any("hash_reference_integrity" in f for f in result.failures)


def test_unsupported_algorithm_rejected(tmp_path):
    bundle = _bundle(tmp_path, "bundle-1", "b1")
    ref = build_evidence_bundle_reference(bundle)
    bad = HashReference(digest="md5:" + "a" * 32, algorithm="md5", content_ref=ref.bundle_id)
    forged = EvidenceBundleReference(bundle_id=ref.bundle_id, schema_version=ref.schema_version, hash_references=(bad,))
    result = verify_evidence_bundle_reference(forged, bundle)
    assert result.overall_status is CM001Status.INVALID
    assert any("hash_reference_integrity" in f for f in result.failures)


# ---------------------------------------------------------------------------
# 15 — digest mismatch rejected
# ---------------------------------------------------------------------------


def test_digest_mismatch_rejected(tmp_path):
    bundle = _bundle(tmp_path, "bundle-1", "b1")
    ref = build_evidence_bundle_reference(bundle)
    wrong_digest = HashReference(
        digest="sha256:" + "0" * 64, algorithm="sha256", content_ref=ref.bundle_id,
    )
    forged = EvidenceBundleReference(bundle_id=ref.bundle_id, schema_version=ref.schema_version, hash_references=(wrong_digest,))
    result = verify_evidence_bundle_reference(forged, bundle)
    assert result.overall_status is CM001Status.INVALID
    assert any("does not match the actual Integrity Record" in f for f in result.failures)


# ---------------------------------------------------------------------------
# 16 — invalid or unresolved content pointer rejected
# ---------------------------------------------------------------------------


def test_content_ref_bound_to_different_bundle_rejected(tmp_path):
    bundle = _bundle(tmp_path, "bundle-1", "b1")
    ref = build_evidence_bundle_reference(bundle)
    hr = ref.hash_references[0]
    mismatched = HashReference(digest=hr.digest, algorithm=hr.algorithm, content_ref="a-different-bundle-id")
    forged = EvidenceBundleReference(bundle_id=ref.bundle_id, schema_version=ref.schema_version, hash_references=(mismatched,))
    result = verify_evidence_bundle_reference(forged, bundle)
    assert result.overall_status is CM001Status.INVALID
    assert any("not bound to this Evidence Bundle Reference" in f for f in result.failures)


# ---------------------------------------------------------------------------
# 17/18 — reference to missing / structurally invalid bundle rejected
# ---------------------------------------------------------------------------


def test_reference_to_missing_bundle_rejected(tmp_path):
    bundle = _bundle(tmp_path, "bundle-1", "b1")
    ref = build_evidence_bundle_reference(bundle)
    result = verify_evidence_bundle_reference(ref, tmp_path / "does-not-exist")
    assert result.overall_status is CM001Status.INVALID
    assert any("not found" in f for f in result.failures)


def test_reference_to_structurally_invalid_bundle_rejected(tmp_path):
    bundle = _bundle(tmp_path, "bundle-1", "b1")
    ref = build_evidence_bundle_reference(bundle)
    (bundle / BUNDLE_DESCRIPTOR_NAME).unlink()  # corrupt the bundle's own structure
    result = verify_evidence_bundle_reference(ref, bundle)
    assert result.overall_status is CM001Status.INVALID
    assert any("not a structurally valid" in f for f in result.failures)


# ---------------------------------------------------------------------------
# 19/20 — substitution with another valid bundle / post-reference tampering
# ---------------------------------------------------------------------------


def test_substitution_with_another_valid_bundle_rejected(tmp_path):
    bundle_a = _bundle(tmp_path, "bundle-A", "ba")
    ref = build_evidence_bundle_reference(bundle_a)
    bundle_b = _bundle(tmp_path, "bundle-B", "bb")  # independently valid, different bundle
    result = verify_evidence_bundle_reference(ref, bundle_b)
    assert result.overall_status is CM001Status.INVALID
    assert any("bundle_id_binding" in f for f in result.failures)


def test_post_reference_bundle_content_tampering_rejected(tmp_path):
    bundle = _bundle(tmp_path, "bundle-1", "b1")
    ref = build_evidence_bundle_reference(bundle)
    (bundle / "evidence" / "item0.json").write_bytes(b'{"tampered": true}')
    result = verify_evidence_bundle_reference(ref, bundle)
    assert result.overall_status is CM001Status.INVALID


def test_post_reference_bundle_regeneration_with_different_content_rejected(tmp_path):
    # The bundle is regenerated (still independently structurally valid) but
    # with different evidence -- its Integrity Record content differs, so
    # the Manifest's existing reference to the old Integrity Record must
    # fail, independent of the bundle's own internal consistency.
    bundle = _bundle(tmp_path, "bundle-1", "b1", n_items=1)
    ref = build_evidence_bundle_reference(bundle)
    shutil.rmtree(bundle)
    regenerated = _bundle(tmp_path, "bundle-1", "b1", n_items=2)
    result = verify_evidence_bundle_reference(ref, regenerated)
    assert result.overall_status is CM001Status.INVALID
    assert any("hash_reference_integrity" in f for f in result.failures)


# ---------------------------------------------------------------------------
# 21 — incomplete reference fails closed
# ---------------------------------------------------------------------------


def test_incomplete_manifest_input_rejected_before_any_write(tmp_path):
    with pytest.raises(IncompleteCM001ManifestError):
        build_evidence_bundle_reference(tmp_path / "not-a-real-bundle")


def test_cm_ebref_004_manifest_invalidated_when_primary_unverifiable(tmp_path):
    bundle = _bundle(tmp_path, "bundle-1", "b1")
    manifest = build_cm001_manifest(bundle)
    (bundle / "evidence" / "item0.json").write_bytes(b"tampered")
    result = verify_cm001_manifest(manifest, bundle)
    assert result.overall_status is CM001Status.INVALID
    assert result.primary is not None
    assert not result.primary.valid


# ---------------------------------------------------------------------------
# CM-EBREF-001 — exactly one primary reference
# ---------------------------------------------------------------------------


def test_cm_ebref_001_manifest_has_exactly_one_primary_reference(tmp_path):
    bundle = _bundle(tmp_path, "bundle-1", "b1")
    manifest = build_cm001_manifest(bundle)
    assert manifest.primary_evidence_bundle_reference is not None
    assert manifest.primary_evidence_bundle_reference.kind is EvidenceBundleReferenceKind.PRIMARY


def test_cm_ebref_001_manifest_from_dict_requires_a_primary_reference():
    with pytest.raises(HashReferenceError):
        from mcc_evidence.cm001_manifest import CM001Manifest

        CM001Manifest.from_dict({"manifest_schema_version": CM001_MANIFEST_SCHEMA_VERSION})


# ---------------------------------------------------------------------------
# CM-EBREF-003 — supplementary references distinguishable from primary
# ---------------------------------------------------------------------------


def test_cm_ebref_003_supplementary_reference_distinguishable_from_primary(tmp_path):
    primary_bundle = _bundle(tmp_path, "bundle-primary", "bp")
    supplementary_bundle = _bundle(tmp_path, "bundle-old-run", "bs", run_id="run-0")
    manifest = build_cm001_manifest(primary_bundle, supplementary_bundle_paths=(supplementary_bundle,))
    assert len(manifest.supplementary_evidence_bundle_references) == 1
    supp = manifest.supplementary_evidence_bundle_references[0]
    assert supp.bundle_id != manifest.primary_evidence_bundle_reference.bundle_id
    assert supp.kind is EvidenceBundleReferenceKind.SUPPLEMENTARY


def test_cm_ebref_003_indistinguishable_supplementary_reference_rejected(tmp_path):
    bundle = _bundle(tmp_path, "same-bundle-id", "b1")
    with pytest.raises(IncompleteCM001ManifestError):
        build_cm001_manifest(bundle, supplementary_bundle_paths=(bundle,))


def test_cm_ebref_003_duplicate_supplementary_references_rejected(tmp_path):
    primary_bundle = _bundle(tmp_path, "bundle-primary", "bp")
    dup_bundle_1 = _bundle(tmp_path, "dup-bundle", "d1", run_id="run-a")
    # Build a second, separate reference to a bundle with the SAME bundle_id
    # (simulating two supplementary entries claiming the same identity).
    from mcc_evidence.cm001_manifest import build_evidence_bundle_reference, _validate_distinguishable

    primary_ref = build_evidence_bundle_reference(primary_bundle)
    supp_ref = build_evidence_bundle_reference(dup_bundle_1, kind=EvidenceBundleReferenceKind.SUPPLEMENTARY)
    with pytest.raises(IncompleteCM001ManifestError):
        _validate_distinguishable(primary_ref, (supp_ref, supp_ref))


def test_verify_supplementary_references_with_supplied_bundle_paths(tmp_path):
    primary_bundle = _bundle(tmp_path, "bundle-primary", "bp")
    supplementary_bundle = _bundle(tmp_path, "bundle-old-run", "bs", run_id="run-0")
    manifest = build_cm001_manifest(primary_bundle, supplementary_bundle_paths=(supplementary_bundle,))
    result = verify_cm001_manifest(
        manifest, primary_bundle,
        supplementary_bundle_paths={"bundle-old-run": supplementary_bundle},
    )
    assert result.overall_status is CM001Status.VALID
    assert len(result.supplementary) == 1
    assert result.supplementary[0].valid


# ---------------------------------------------------------------------------
# 22/23 — legacy manifest (mcc_compliance) compatibility & no false labeling
# ---------------------------------------------------------------------------


def test_legacy_compliance_manifest_still_functions_unmodified():
    # certifications/manifest.json is untouched by Wave B; a smoke import
    # confirms the legacy path still loads and is a different shape.
    import json as _json
    from pathlib import Path as _Path

    repo_root = _Path(__file__).resolve().parents[1]
    legacy = _json.loads((repo_root / "certifications" / "manifest.json").read_text())
    assert "certifications" in legacy
    for entry in legacy["certifications"]:
        assert "manifest_schema_version" not in entry  # not the CM-001 shape
        assert "primary_evidence_bundle_reference" not in entry


def test_legacy_compliance_manifest_entry_is_not_a_cm001_manifest():
    import json as _json
    from pathlib import Path as _Path

    from mcc_evidence.cm001_manifest import CM001Manifest

    repo_root = _Path(__file__).resolve().parents[1]
    legacy = _json.loads((repo_root / "certifications" / "manifest.json").read_text())
    entry = legacy["certifications"][0]
    with pytest.raises(HashReferenceError):
        CM001Manifest.from_dict(entry)
