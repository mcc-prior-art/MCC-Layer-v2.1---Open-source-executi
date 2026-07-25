"""Direct behavioral tests for the MCC-EB-001 Evidence Bundle
(``src/mcc_evidence/eb001_export.py`` / ``eb001_verify.py``), covering the
Wave A selected requirements: EB-STR-001..005, EB-FILE-001..005.

Every test is linked to its requirement ID in its name or docstring.
Negative tests construct a valid bundle first and then corrupt exactly the
one thing under test, so a failure is attributable to a single cause.
"""

from __future__ import annotations

import json
import tarfile
import io

import pytest

from mcc_evidence.eb001_export import (
    EB001BundleInput,
    EvidenceItemInput,
    build_eb001_bundle,
)
from mcc_evidence.eb001_schema import (
    BUNDLE_DESCRIPTOR_NAME,
    EB001_SCHEMA_VERSION,
    EVIDENCE_DIR_NAME,
    INTEGRITY_RECORD_NAME,
    PROVENANCE_RECORD_NAME,
    EB001Status,
    IncompleteEB001BundleError,
)
from mcc_evidence.eb001_verify import verify_eb001_bundle
from mcc_evidence.hash_reference import compute_hash_reference


def _sample_input(**overrides) -> EB001BundleInput:
    base = dict(
        cp001_specification_version="1.0",
        certification_run_id="run-2026-07-25-001",
        certification_subject_id="examples/reference_governed_agent",
        evidence_items=[
            EvidenceItemInput(name="req-CI-001.json", content=b'{"requirement":"CI-001","outcome":"PASS"}'),
            EvidenceItemInput(name="req-CI-002.json", content=b'{"requirement":"CI-002","outcome":"PASS"}'),
        ],
        bundle_id="fixed-bundle-id-eb001-tests",
    )
    base.update(overrides)
    return EB001BundleInput(**base)


def _rewrite_tar_member(archive_path, member_name: str, new_content: bytes) -> None:
    """Rewrite exactly one member's content in a .tar.gz, preserving the rest,
    for precise single-field tamper tests."""
    members = {}
    with tarfile.open(archive_path, "r:gz") as tar:
        for m in tar.getmembers():
            f = tar.extractfile(m)
            members[m.name] = f.read() if f else b""
    members[member_name] = new_content
    with tarfile.open(archive_path, "w:gz") as tar:
        for name in sorted(members):
            data = members[name]
            info = tarfile.TarInfo(name=name)
            info.size = len(data)
            info.mtime = 0
            tar.addfile(info, io.BytesIO(data))


def _add_tar_member(archive_path, member_name: str, content: bytes) -> None:
    members = {}
    with tarfile.open(archive_path, "r:gz") as tar:
        for m in tar.getmembers():
            f = tar.extractfile(m)
            members[m.name] = f.read() if f else b""
    members[member_name] = content
    with tarfile.open(archive_path, "w:gz") as tar:
        for name in sorted(members):
            data = members[name]
            info = tarfile.TarInfo(name=name)
            info.size = len(data)
            info.mtime = 0
            tar.addfile(info, io.BytesIO(data))


def _duplicate_tar_member(archive_path, member_name: str) -> None:
    """Append a second member with the SAME name -- the only way to exercise
    a duplicate-singleton bundle, since a real filesystem cannot represent
    one."""
    with tarfile.open(archive_path, "r:gz") as tar:
        entries = [(m.name, (tar.extractfile(m) or io.BytesIO(b"")).read()) for m in tar.getmembers()]
    with tarfile.open(archive_path, "w:gz") as tar:
        for name, data in entries:
            info = tarfile.TarInfo(name=name)
            info.size = len(data)
            info.mtime = 0
            tar.addfile(info, io.BytesIO(data))
        # append a second copy of the targeted member
        dup_data = dict(entries)[member_name]
        info = tarfile.TarInfo(name=member_name)
        info.size = len(dup_data)
        info.mtime = 0
        tar.addfile(info, io.BytesIO(dup_data))


# ---------------------------------------------------------------------------
# 1/2 — production of a valid bundle + successful verification (both forms)
# ---------------------------------------------------------------------------


def test_produces_and_verifies_a_valid_eb001_bundle_directory_form(tmp_path):
    bundle = build_eb001_bundle(_sample_input(), tmp_path / "bundle")
    result = verify_eb001_bundle(bundle)
    assert result.overall_status is EB001Status.VALID, result.failures
    assert result.failures == []


def test_produces_and_verifies_a_valid_eb001_bundle_archive_form(tmp_path):
    archive = build_eb001_bundle(_sample_input(), tmp_path / "bundle", archive=True)
    result = verify_eb001_bundle(archive)
    assert result.overall_status is EB001Status.VALID, result.failures


# ---------------------------------------------------------------------------
# EB-STR-002 / EB-FILE-001..003 — exact required Bundle Root structure and
# filenames.
# ---------------------------------------------------------------------------


def test_eb_str_002_bundle_root_contains_exactly_the_required_entries(tmp_path):
    bundle = build_eb001_bundle(_sample_input(), tmp_path / "bundle")
    top_level = {p.name for p in bundle.iterdir()}
    assert top_level == {BUNDLE_DESCRIPTOR_NAME, INTEGRITY_RECORD_NAME, PROVENANCE_RECORD_NAME, EVIDENCE_DIR_NAME}


def test_eb_file_001_bundle_descriptor_present_and_declares_required_fields(tmp_path):
    bundle = build_eb001_bundle(_sample_input(), tmp_path / "bundle")
    descriptor = json.loads((bundle / BUNDLE_DESCRIPTOR_NAME).read_bytes())
    assert descriptor["schema_version"] == EB001_SCHEMA_VERSION
    assert descriptor["bundle_id"]
    assert descriptor["cp001_specification_version"] == "1.0"


def test_eb_file_002_integrity_record_present(tmp_path):
    bundle = build_eb001_bundle(_sample_input(), tmp_path / "bundle")
    assert (bundle / INTEGRITY_RECORD_NAME).exists()


def test_eb_file_003_provenance_record_present_and_declares_origin(tmp_path):
    bundle = build_eb001_bundle(_sample_input(), tmp_path / "bundle")
    provenance = json.loads((bundle / PROVENANCE_RECORD_NAME).read_bytes())
    assert provenance["certification_run_id"] == "run-2026-07-25-001"
    assert provenance["cp001_specification_version"] == "1.0"


def test_evidence_directory_present_with_items(tmp_path):
    bundle = build_eb001_bundle(_sample_input(), tmp_path / "bundle")
    items = sorted(p.name for p in (bundle / EVIDENCE_DIR_NAME).iterdir())
    assert items == ["req-CI-001.json", "req-CI-002.json"]


def test_evidence_directory_may_be_empty_but_must_still_exist(tmp_path):
    bundle = build_eb001_bundle(_sample_input(evidence_items=[]), tmp_path / "bundle")
    assert (bundle / EVIDENCE_DIR_NAME).is_dir()
    result = verify_eb001_bundle(bundle)
    assert result.overall_status is EB001Status.VALID, result.failures


# ---------------------------------------------------------------------------
# EB-STR-003/004/005 + determinism (items 12/13/35/36)
# ---------------------------------------------------------------------------


def test_eb_str_003_004_deterministic_regeneration_produces_identical_files(tmp_path):
    b1 = build_eb001_bundle(_sample_input(), tmp_path / "run1")
    b2 = build_eb001_bundle(_sample_input(), tmp_path / "run2")
    files1 = {p.relative_to(b1): p.read_bytes() for p in b1.rglob("*") if p.is_file()}
    files2 = {p.relative_to(b2): p.read_bytes() for p in b2.rglob("*") if p.is_file()}
    assert files1 == files2


def test_eb_str_005_directory_and_archive_forms_are_structurally_equivalent(tmp_path):
    d = build_eb001_bundle(_sample_input(), tmp_path / "bundle_dir")
    a = build_eb001_bundle(_sample_input(), tmp_path / "bundle_archive", archive=True)
    dir_files = {str(p.relative_to(d)): p.read_bytes() for p in d.rglob("*") if p.is_file()}
    with tarfile.open(a, "r:gz") as tar:
        tar_files = {m.name: tar.extractfile(m).read() for m in tar.getmembers() if m.isfile()}
    assert dir_files == tar_files


def test_repeated_generation_is_deterministic(tmp_path):
    inputs = _sample_input()
    b1 = build_eb001_bundle(inputs, tmp_path / "gen1")
    b2 = build_eb001_bundle(inputs, tmp_path / "gen2")
    assert (b1 / INTEGRITY_RECORD_NAME).read_bytes() == (b2 / INTEGRITY_RECORD_NAME).read_bytes()


def test_repeated_verification_is_deterministic(tmp_path):
    bundle = build_eb001_bundle(_sample_input(), tmp_path / "bundle")
    r1 = verify_eb001_bundle(bundle)
    r2 = verify_eb001_bundle(bundle)
    assert r1.to_dict() == r2.to_dict()


def test_integrity_record_entries_are_in_deterministic_sorted_order(tmp_path):
    bundle = build_eb001_bundle(_sample_input(), tmp_path / "bundle")
    integrity = json.loads((bundle / INTEGRITY_RECORD_NAME).read_bytes())
    paths = [e["path"] for e in integrity["entries"]]
    assert paths == sorted(paths)


# ---------------------------------------------------------------------------
# EB-FILE-004 — complete enumeration (items 14/17/18)
# ---------------------------------------------------------------------------


def test_eb_file_004_every_non_integrity_record_file_is_enumerated(tmp_path):
    bundle = build_eb001_bundle(_sample_input(), tmp_path / "bundle")
    integrity = json.loads((bundle / INTEGRITY_RECORD_NAME).read_bytes())
    enumerated = {e["path"] for e in integrity["entries"]}
    actual = {
        str(p.relative_to(bundle)) for p in bundle.rglob("*") if p.is_file()
    } - {INTEGRITY_RECORD_NAME}
    assert enumerated == actual


def test_eb_file_004_unenumerated_file_is_rejected(tmp_path):
    bundle = build_eb001_bundle(_sample_input(), tmp_path / "bundle")
    (bundle / EVIDENCE_DIR_NAME / "sneaked-in.json").write_bytes(b"{}")
    result = verify_eb001_bundle(bundle)
    assert result.overall_status is EB001Status.INVALID
    assert any("not enumerated" in f for f in result.failures)


def test_eb_file_004_missing_enumerated_file_is_rejected(tmp_path):
    bundle = build_eb001_bundle(_sample_input(), tmp_path / "bundle")
    (bundle / EVIDENCE_DIR_NAME / "req-CI-001.json").unlink()
    result = verify_eb001_bundle(bundle)
    assert result.overall_status is EB001Status.INVALID
    assert any("not actually present" in f for f in result.failures)


# ---------------------------------------------------------------------------
# EB-FILE-001/002/003/005 — missing required root artifact rejected
# (items 15/29)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("missing_name", [BUNDLE_DESCRIPTOR_NAME, INTEGRITY_RECORD_NAME, PROVENANCE_RECORD_NAME])
def test_eb_file_005_missing_required_root_artifact_is_rejected(tmp_path, missing_name):
    bundle = build_eb001_bundle(_sample_input(), tmp_path / "bundle")
    (bundle / missing_name).unlink()
    result = verify_eb001_bundle(bundle)
    assert result.overall_status is EB001Status.INVALID
    if missing_name == BUNDLE_DESCRIPTOR_NAME:
        assert any("bundle_descriptor" in f for f in result.failures)
    else:
        assert any(missing_name in f or "missing required root" in f for f in result.failures)


def test_missing_evidence_directory_is_rejected(tmp_path):
    bundle = build_eb001_bundle(_sample_input(evidence_items=[]), tmp_path / "bundle")
    import shutil

    shutil.rmtree(bundle / EVIDENCE_DIR_NAME)
    result = verify_eb001_bundle(bundle)
    assert result.overall_status is EB001Status.INVALID
    assert any("Evidence Directory is absent" in f for f in result.failures)


# ---------------------------------------------------------------------------
# EB-STR-002 singleton cardinality — duplicate root member rejected
# (item 6/16)
# ---------------------------------------------------------------------------


def test_duplicate_singleton_root_artifact_is_rejected(tmp_path):
    archive = build_eb001_bundle(_sample_input(), tmp_path / "bundle", archive=True)
    _duplicate_tar_member(archive, BUNDLE_DESCRIPTOR_NAME)
    result = verify_eb001_bundle(archive)
    assert result.overall_status is EB001Status.INVALID
    assert any("duplicate" in f for f in result.failures)


def test_unaccounted_top_level_entry_is_rejected(tmp_path):
    bundle = build_eb001_bundle(_sample_input(), tmp_path / "bundle")
    (bundle / "sneaky_top_level_file.json").write_bytes(b"{}")
    result = verify_eb001_bundle(bundle)
    assert result.overall_status is EB001Status.INVALID
    assert any("unaccounted top-level content" in f for f in result.failures)


# ---------------------------------------------------------------------------
# CM-HASH-driven integrity checks in context (items 19-24, 27)
# ---------------------------------------------------------------------------


def test_digest_mismatch_is_rejected(tmp_path):
    bundle = build_eb001_bundle(_sample_input(), tmp_path / "bundle")
    (bundle / EVIDENCE_DIR_NAME / "req-CI-001.json").write_bytes(b'{"requirement":"CI-001","outcome":"FAIL"}')
    result = verify_eb001_bundle(bundle)
    assert result.overall_status is EB001Status.INVALID
    assert any("digest mismatch" in f for f in result.failures)


def test_tampered_evidence_content_is_rejected(tmp_path):
    bundle = build_eb001_bundle(_sample_input(), tmp_path / "bundle")
    (bundle / EVIDENCE_DIR_NAME / "req-CI-002.json").write_bytes(b"malicious content")
    result = verify_eb001_bundle(bundle)
    assert result.overall_status is EB001Status.INVALID


def test_tampered_bundle_descriptor_is_rejected(tmp_path):
    bundle = build_eb001_bundle(_sample_input(), tmp_path / "bundle")
    descriptor = json.loads((bundle / BUNDLE_DESCRIPTOR_NAME).read_bytes())
    descriptor["cp001_specification_version"] = "9.9"  # tamper after generation
    (bundle / BUNDLE_DESCRIPTOR_NAME).write_bytes(json.dumps(descriptor).encode())
    result = verify_eb001_bundle(bundle)
    assert result.overall_status is EB001Status.INVALID
    assert any("digest mismatch" in f for f in result.failures)


def test_tampered_provenance_record_is_rejected(tmp_path):
    bundle = build_eb001_bundle(_sample_input(), tmp_path / "bundle")
    provenance = json.loads((bundle / PROVENANCE_RECORD_NAME).read_bytes())
    provenance["certification_run_id"] = "forged-run-id"
    (bundle / PROVENANCE_RECORD_NAME).write_bytes(json.dumps(provenance).encode())
    result = verify_eb001_bundle(bundle)
    assert result.overall_status is EB001Status.INVALID
    assert any("digest mismatch" in f for f in result.failures)


def test_unsupported_hash_algorithm_is_rejected(tmp_path):
    bundle = build_eb001_bundle(_sample_input(), tmp_path / "bundle")
    integrity = json.loads((bundle / INTEGRITY_RECORD_NAME).read_bytes())
    integrity["algorithm"] = "md5"
    for entry in integrity["entries"]:
        entry["hash_reference"]["algorithm"] = "md5"
        entry["hash_reference"]["digest"] = "md5:" + "a" * 32
    (bundle / INTEGRITY_RECORD_NAME).write_bytes(json.dumps(integrity).encode())
    result = verify_eb001_bundle(bundle)
    assert result.overall_status is EB001Status.INVALID
    assert any("non-collision-resistant" in f or "not collision-resistant" in f for f in result.failures)


def test_malformed_digest_is_rejected(tmp_path):
    bundle = build_eb001_bundle(_sample_input(), tmp_path / "bundle")
    integrity = json.loads((bundle / INTEGRITY_RECORD_NAME).read_bytes())
    integrity["entries"][0]["hash_reference"]["digest"] = "not-a-valid-digest"
    (bundle / INTEGRITY_RECORD_NAME).write_bytes(json.dumps(integrity).encode())
    result = verify_eb001_bundle(bundle)
    assert result.overall_status is EB001Status.INVALID
    assert any("not valid" in f for f in result.failures)


def test_invalid_content_pointer_bound_to_wrong_content_is_rejected(tmp_path):
    bundle = build_eb001_bundle(_sample_input(), tmp_path / "bundle")
    integrity = json.loads((bundle / INTEGRITY_RECORD_NAME).read_bytes())
    for entry in integrity["entries"]:
        if entry["path"] == "evidence/req-CI-001.json":
            entry["hash_reference"]["content_ref"] = "evidence/req-CI-002.json"
    (bundle / INTEGRITY_RECORD_NAME).write_bytes(json.dumps(integrity).encode())
    result = verify_eb001_bundle(bundle)
    assert result.overall_status is EB001Status.INVALID
    assert any("bound to different content" in f for f in result.failures)


def test_unresolved_content_reference_is_rejected(tmp_path):
    bundle = build_eb001_bundle(_sample_input(), tmp_path / "bundle")
    integrity = json.loads((bundle / INTEGRITY_RECORD_NAME).read_bytes())
    ghost_ref = compute_hash_reference(b"ghost", content_ref="evidence/does-not-exist.json")
    integrity["entries"].append({"path": "evidence/does-not-exist.json", "hash_reference": ghost_ref.to_dict()})
    (bundle / INTEGRITY_RECORD_NAME).write_bytes(json.dumps(integrity).encode())
    result = verify_eb001_bundle(bundle)
    assert result.overall_status is EB001Status.INVALID
    assert any("does not resolve to any actual file" in f for f in result.failures)


def test_malformed_integrity_record_entry_is_rejected(tmp_path):
    bundle = build_eb001_bundle(_sample_input(), tmp_path / "bundle")
    integrity = json.loads((bundle / INTEGRITY_RECORD_NAME).read_bytes())
    integrity["entries"][0] = {"path": "evidence/req-CI-001.json"}  # missing hash_reference
    (bundle / INTEGRITY_RECORD_NAME).write_bytes(json.dumps(integrity).encode())
    result = verify_eb001_bundle(bundle)
    assert result.overall_status is EB001Status.INVALID
    assert any("malformed" in f for f in result.failures)


def test_malformed_json_record_is_rejected(tmp_path):
    bundle = build_eb001_bundle(_sample_input(), tmp_path / "bundle")
    (bundle / BUNDLE_DESCRIPTOR_NAME).write_bytes(b"{not valid json")
    result = verify_eb001_bundle(bundle)
    assert result.overall_status is EB001Status.INVALID
    assert any("malformed" in f for f in result.failures)


# ---------------------------------------------------------------------------
# Bundle identity consistency (item 30)
# ---------------------------------------------------------------------------


def test_inconsistent_bundle_identity_is_rejected(tmp_path):
    bundle = build_eb001_bundle(_sample_input(), tmp_path / "bundle")
    provenance = json.loads((bundle / PROVENANCE_RECORD_NAME).read_bytes())
    provenance["bundle_id"] = "a-different-bundle-id"
    (bundle / PROVENANCE_RECORD_NAME).write_bytes(json.dumps(provenance).encode())
    result = verify_eb001_bundle(bundle)
    assert result.overall_status is EB001Status.INVALID
    # Either the identity check or the digest check (provenance was
    # rewritten) will catch this -- both are legitimate blocking failures.
    assert any("inconsistent bundle_id" in f or "digest mismatch" in f for f in result.failures)


# ---------------------------------------------------------------------------
# Schema version (item 31)
# ---------------------------------------------------------------------------


def test_unsupported_schema_version_is_rejected(tmp_path):
    bundle = build_eb001_bundle(_sample_input(), tmp_path / "bundle")
    descriptor = json.loads((bundle / BUNDLE_DESCRIPTOR_NAME).read_bytes())
    descriptor["schema_version"] = "mcc-eb-001/999"
    (bundle / BUNDLE_DESCRIPTOR_NAME).write_bytes(json.dumps(descriptor).encode())
    result = verify_eb001_bundle(bundle)
    assert result.overall_status is EB001Status.UNSUPPORTED_SCHEMA


# ---------------------------------------------------------------------------
# Fail-closed verification (item 32)
# ---------------------------------------------------------------------------


def test_verification_fails_closed_on_nonexistent_path(tmp_path):
    result = verify_eb001_bundle(tmp_path / "does-not-exist")
    assert result.overall_status is EB001Status.INVALID


def test_verification_fails_closed_on_corrupt_archive(tmp_path):
    bad = tmp_path / "corrupt.tar.gz"
    bad.write_bytes(b"this is not a valid gzip tar archive")
    result = verify_eb001_bundle(bad)
    assert result.overall_status is EB001Status.INVALID


def test_incomplete_bundle_input_is_rejected_before_any_write(tmp_path):
    with pytest.raises(IncompleteEB001BundleError):
        build_eb001_bundle(
            EB001BundleInput(cp001_specification_version="", certification_run_id="run-1"),
            tmp_path / "bundle",
        )
    assert not (tmp_path / "bundle").exists()


def test_duplicate_evidence_item_name_is_rejected_before_any_write(tmp_path):
    with pytest.raises(IncompleteEB001BundleError):
        build_eb001_bundle(
            _sample_input(evidence_items=[
                EvidenceItemInput(name="dup.json", content=b"{}"),
                EvidenceItemInput(name="dup.json", content=b"{}"),
            ]),
            tmp_path / "bundle",
        )
    assert not (tmp_path / "bundle").exists()


# ---------------------------------------------------------------------------
# Backward compatibility: the two bundle schemas never interpret each
# other's files (items 33/34).
# ---------------------------------------------------------------------------


def test_governance_bundle_is_never_labeled_eb001_valid(tmp_path):
    from mcc_evidence import EvidenceInput, export_bundle

    # A minimal DENY governance bundle (no signed token / receipt required).
    ev = EvidenceInput(
        verdict="DENY", actor_id="agent/ops", resource_id="db/users",
        action="delete_resource", denial={"verdict": "DENY", "reason": "no mandate"},
    )
    governance_bundle = export_bundle(ev, tmp_path / "governance_bundle")
    result = verify_eb001_bundle(governance_bundle)
    assert result.overall_status is not EB001Status.VALID


def test_eb001_bundle_is_never_labeled_governance_bundle_valid(tmp_path):
    from mcc_evidence import verify_bundle
    from mcc_evidence.schema import EvidenceStatus

    eb001_bundle = build_eb001_bundle(_sample_input(), tmp_path / "eb001_bundle")
    result = verify_bundle(eb001_bundle)
    assert result.overall_status in (EvidenceStatus.INVALID, EvidenceStatus.UNSUPPORTED_SCHEMA)
    assert result.trusted is False
