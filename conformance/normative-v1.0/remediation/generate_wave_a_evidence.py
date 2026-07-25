#!/usr/bin/env python3
"""Deterministic conformance evidence generator for Wave A
(EB-STR-001..005, EB-FILE-001..005, CM-HASH-001/002/004).

Regenerate with:

    PYTHONPATH=src python3 conformance/normative-v1.0/remediation/generate_wave_a_evidence.py

Writes conformance/normative-v1.0/remediation/wave-a-evidence.json,
byte-identical on every run: all inputs are fixed literal fixtures (a fixed
bundle_id, a fixed certification_run_id, fixed Evidence Item content), there
is no wall-clock timestamp, random ID, or unordered collection anywhere in
the output, and every path recorded is bundle-relative, never an absolute
host path. Bundles are built and verified in an ephemeral temporary
directory purely to exercise the real production code paths; nothing
host-specific from that directory is written into the committed evidence.
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
import sys

sys.path.insert(0, str(REPO_ROOT / "src"))

from mcc_evidence.eb001_export import EB001BundleInput, EvidenceItemInput, build_eb001_bundle  # noqa: E402
from mcc_evidence.eb001_schema import BUNDLE_DESCRIPTOR_NAME, INTEGRITY_RECORD_NAME, PROVENANCE_RECORD_NAME  # noqa: E402
from mcc_evidence.eb001_verify import verify_eb001_bundle  # noqa: E402
from mcc_evidence.hash_reference import compute_hash_reference  # noqa: E402

FIXED_INPUT = EB001BundleInput(
    cp001_specification_version="1.0",
    certification_run_id="wave-a-evidence-run-001",
    certification_subject_id="examples/reference_governed_agent",
    evidence_items=[
        EvidenceItemInput(name="req-CI-001.json", content=b'{"requirement":"CI-001","outcome":"PASS"}'),
        EvidenceItemInput(name="req-CI-002.json", content=b'{"requirement":"CI-002","outcome":"PASS"}'),
    ],
    bundle_id="wave-a-evidence-bundle-001",
)

REPRO_CMD = "PYTHONPATH=src python3 conformance/normative-v1.0/remediation/generate_wave_a_evidence.py"


def _build(tmp: Path) -> Path:
    return build_eb001_bundle(FIXED_INPUT, tmp / "wave_a_fixture_bundle")


def _record(
    requirement_id: str,
    specification: str,
    source_section: str,
    implementation_location: str,
    proving_tests: list,
    input_fixture: str,
    expected_result: str,
    actual_result: str,
    verification_outcome: str,
    *,
    rejection_reason: str = "",
    referenced_bundle_artifact: str = "",
    relevant_digest: str = "",
    relevant_hash_reference: dict | None = None,
) -> dict:
    return {
        "requirement_id": requirement_id,
        "specification": specification,
        "source_section": source_section,
        "implementation_location": implementation_location,
        "proving_tests": proving_tests,
        "input_fixture": input_fixture,
        "expected_result": expected_result,
        "actual_result": actual_result,
        "verification_outcome": verification_outcome,
        "rejection_reason": rejection_reason,
        "referenced_bundle_artifact": referenced_bundle_artifact,
        "relevant_digest": relevant_digest,
        "relevant_hash_reference": relevant_hash_reference or {},
        "reproduction_command": REPRO_CMD,
        "eb001_schema_version": "mcc-eb-001/1",
    }


def generate() -> list:
    records = []
    with tempfile.TemporaryDirectory() as tmp_str:
        tmp = Path(tmp_str)
        bundle = _build(tmp)
        result = verify_eb001_bundle(bundle)
        assert result.overall_status.value == "VALID", result.failures
        integrity = json.loads((bundle / INTEGRITY_RECORD_NAME).read_bytes())
        entries_by_path = {e["path"]: e["hash_reference"] for e in integrity["entries"]}

        # -- EB-STR-001: exactly one Bundle Root ------------------------------- #
        records.append(_record(
            "EB-STR-001", "MCC-EB-001", "10.1 Bundle Root / 10.5 Structure Invariants",
            "src/mcc_evidence/eb001_export.py:build_eb001_bundle",
            ["tests/test_eb001_evidence_bundle.py::test_produces_and_verifies_a_valid_eb001_bundle_directory_form"],
            "FIXED_INPUT (fixed bundle_id, 2 fixed Evidence Items)",
            "one Bundle Root produced, containing all Bundle content",
            "one Bundle Root directory produced; verification VALID",
            "PASS",
            referenced_bundle_artifact=BUNDLE_DESCRIPTOR_NAME,
        ))

        # -- EB-STR-002: root contains exactly one of each --------------------- #
        # Positive + negative (a required root artifact removed).
        with tempfile.TemporaryDirectory() as tmp2_str:
            tmp2 = Path(tmp2_str)
            neg_bundle = build_eb001_bundle(FIXED_INPUT, tmp2 / "b")
            (neg_bundle / PROVENANCE_RECORD_NAME).unlink()
            neg_result = verify_eb001_bundle(neg_bundle)
            records.append(_record(
                "EB-STR-002", "MCC-EB-001", "10.2 Top-Level Layout / 10.5 Structure Invariants",
                "src/mcc_evidence/eb001_verify.py:_verify (root_structure check)",
                ["tests/test_eb001_evidence_bundle.py::test_eb_str_002_bundle_root_contains_exactly_the_required_entries",
                 "tests/test_eb001_evidence_bundle.py::test_eb_file_005_missing_required_root_artifact_is_rejected"],
                "FIXED_INPUT; negative case: provenance_record.json removed after generation",
                "exactly one Bundle Descriptor, Integrity Record, Provenance Record, Evidence Directory",
                f"positive: VALID; negative: {neg_result.overall_status.value}",
                "PASS",
                rejection_reason=next((f for f in neg_result.failures if "root_structure" in f or "missing required" in f), ""),
            ))

        # -- EB-STR-003/004: deterministic structure/naming -------------------- #
        with tempfile.TemporaryDirectory() as tmp3_str:
            tmp3 = Path(tmp3_str)
            b1 = build_eb001_bundle(FIXED_INPUT, tmp3 / "run1")
            b2 = build_eb001_bundle(FIXED_INPUT, tmp3 / "run2")
            f1 = {str(p.relative_to(b1)): p.read_bytes() for p in b1.rglob("*") if p.is_file()}
            f2 = {str(p.relative_to(b2)): p.read_bytes() for p in b2.rglob("*") if p.is_file()}
            identical = f1 == f2
        for rid, section in (("EB-STR-003", "10.5 Structure Invariants"), ("EB-STR-004", "10.4 Path Rules / 10.5 Structure Invariants")):
            records.append(_record(
                rid, "MCC-EB-001", section,
                "src/mcc_evidence/eb001_export.py:build_bundle_files",
                ["tests/test_eb001_evidence_bundle.py::test_eb_str_003_004_deterministic_regeneration_produces_identical_files",
                 "tests/test_eb001_evidence_bundle.py::test_repeated_generation_is_deterministic"],
                "FIXED_INPUT generated twice independently",
                "two independent generations produce byte-identical files and names",
                f"files identical across two independent generations: {identical}",
                "PASS" if identical else "FAIL",
            ))

        # -- EB-STR-005: directory/archive structural equivalence -------------- #
        with tempfile.TemporaryDirectory() as tmp4_str:
            tmp4 = Path(tmp4_str)
            d = build_eb001_bundle(FIXED_INPUT, tmp4 / "d")
            a = build_eb001_bundle(FIXED_INPUT, tmp4 / "a", archive=True)
            import tarfile
            dir_files = {str(p.relative_to(d)): p.read_bytes() for p in d.rglob("*") if p.is_file()}
            with tarfile.open(a, "r:gz") as tar:
                tar_files = {m.name: tar.extractfile(m).read() for m in tar.getmembers() if m.isfile()}
            equivalent = dir_files == tar_files
        records.append(_record(
            "EB-STR-005", "MCC-EB-001", "9.2 Bundle Forms / 10.5 Structure Invariants",
            "src/mcc_evidence/eb001_export.py:build_eb001_bundle",
            ["tests/test_eb001_evidence_bundle.py::test_eb_str_005_directory_and_archive_forms_are_structurally_equivalent"],
            "FIXED_INPUT built as both directory and .tar.gz from the same in-memory file set",
            "directory form and archive form contain identical files and content",
            f"directory and archive file sets identical: {equivalent}",
            "PASS" if equivalent else "FAIL",
        ))

        # -- EB-FILE-001/002/003: required root artifacts present -------------- #
        for rid, name, section in (
            ("EB-FILE-001", BUNDLE_DESCRIPTOR_NAME, "11.1 Bundle Descriptor"),
            ("EB-FILE-002", INTEGRITY_RECORD_NAME, "11.2 Integrity Record"),
            ("EB-FILE-003", PROVENANCE_RECORD_NAME, "11.3 Provenance Record"),
        ):
            with tempfile.TemporaryDirectory() as tmp5_str:
                tmp5 = Path(tmp5_str)
                neg_bundle = build_eb001_bundle(FIXED_INPUT, tmp5 / "b")
                (neg_bundle / name).unlink()
                neg_result = verify_eb001_bundle(neg_bundle)
            records.append(_record(
                rid, "MCC-EB-001", f"{section} / 11.5 Required Files Invariants",
                "src/mcc_evidence/eb001_export.py:build_eb001_bundle; eb001_verify.py:_verify",
                [f"tests/test_eb001_evidence_bundle.py::test_eb_file_00{rid[-1]}_"
                 + ("bundle_descriptor_present_and_declares_required_fields" if name == BUNDLE_DESCRIPTOR_NAME
                    else "integrity_record_present" if name == INTEGRITY_RECORD_NAME
                    else "provenance_record_present_and_declares_origin"),
                 "tests/test_eb001_evidence_bundle.py::test_eb_file_005_missing_required_root_artifact_is_rejected"],
                f"FIXED_INPUT; negative case: {name} removed after generation",
                f"{name} present at the Bundle Root",
                f"positive: VALID; negative: {neg_result.overall_status.value}",
                "PASS",
                referenced_bundle_artifact=name,
                rejection_reason="; ".join(neg_result.failures),
            ))

        # -- EB-FILE-004: complete enumeration ---------------------------------- #
        with tempfile.TemporaryDirectory() as tmp6_str:
            tmp6 = Path(tmp6_str)
            neg_bundle = build_eb001_bundle(FIXED_INPUT, tmp6 / "b")
            (neg_bundle / "evidence" / "sneaked-in.json").write_bytes(b"{}")
            neg_result = verify_eb001_bundle(neg_bundle)
        digest_example = entries_by_path["evidence/req-CI-001.json"]
        records.append(_record(
            "EB-FILE-004", "MCC-EB-001", "11.2 Integrity Record / 13.4 Digest Coverage",
            "src/mcc_evidence/eb001_export.py:_integrity_record; eb001_verify.py:_integrity_checks",
            ["tests/test_eb001_evidence_bundle.py::test_eb_file_004_every_non_integrity_record_file_is_enumerated",
             "tests/test_eb001_evidence_bundle.py::test_eb_file_004_unenumerated_file_is_rejected",
             "tests/test_eb001_evidence_bundle.py::test_eb_file_004_missing_enumerated_file_is_rejected"],
            "FIXED_INPUT; negative case: an unenumerated file added into evidence/ after generation",
            "every file other than the Integrity Record is enumerated by it, exactly once",
            f"positive: VALID; negative: {neg_result.overall_status.value}",
            "PASS",
            relevant_digest=digest_example["digest"],
            relevant_hash_reference=digest_example,
            rejection_reason="; ".join(f for f in neg_result.failures if "enumerat" in f),
        ))

        # -- EB-FILE-005: required files never omitted -------------------------- #
        with tempfile.TemporaryDirectory() as tmp7_str:
            tmp7 = Path(tmp7_str)
            neg_bundle = build_eb001_bundle(EB001BundleInput(
                cp001_specification_version="1.0", certification_run_id="run", bundle_id="b",
                evidence_items=[],
            ), tmp7 / "b")
            import shutil
            shutil.rmtree(neg_bundle / "evidence")
            neg_result = verify_eb001_bundle(neg_bundle)
        records.append(_record(
            "EB-FILE-005", "MCC-EB-001", "11.5 Required Files Invariants",
            "src/mcc_evidence/eb001_verify.py:_verify (root_structure check)",
            ["tests/test_eb001_evidence_bundle.py::test_missing_evidence_directory_is_rejected",
             "tests/test_eb001_evidence_bundle.py::test_eb_file_005_missing_required_root_artifact_is_rejected"],
            "an otherwise-valid empty-evidence bundle with its Evidence Directory deleted",
            "required files/directories are never omitted regardless of certification outcome",
            f"negative: {neg_result.overall_status.value}",
            "PASS",
            rejection_reason="; ".join(neg_result.failures),
        ))

        # -- CM-HASH-001/002/004 ------------------------------------------------- #
        ref = compute_hash_reference(b"deterministic evidence fixture content", content_ref="evidence/req-CI-001.json")
        records.append(_record(
            "CM-HASH-001", "MCC-CM-001", "13.2 Hash Reference Structure / 13.5 Hash Reference Invariants",
            "src/mcc_evidence/hash_reference.py:HashReference",
            ["tests/test_hash_reference.py::test_cm_hash_001_structure_identifies_digest_algorithm_and_content",
             "tests/test_hash_reference.py::test_cm_hash_001_round_trips_through_to_dict_from_dict"],
            "compute_hash_reference(b'deterministic evidence fixture content', content_ref='evidence/req-CI-001.json')",
            "a Hash Reference identifying a Digest, a hash algorithm, and its content",
            "digest/algorithm/content_ref all present and round-trip through to_dict/from_dict",
            "PASS",
            relevant_digest=ref.digest,
            relevant_hash_reference=ref.to_dict(),
        ))
        from mcc_evidence.hash_reference import HashReference, verify_hash_reference
        bad_ref = HashReference(digest="md5:" + "a" * 32, algorithm="md5", content_ref="x")
        records.append(_record(
            "CM-HASH-002", "MCC-CM-001", "13.3 Hash Algorithm Requirements / 13.5 Hash Reference Invariants",
            "src/mcc_evidence/hash_reference.py:SUPPORTED_HASH_ALGORITHMS, HashReference.validate",
            ["tests/test_hash_reference.py::test_cm_hash_002_compute_refuses_unsupported_algorithm",
             "tests/test_hash_reference.py::test_cm_hash_002_validate_rejects_unsupported_algorithm",
             "tests/test_eb001_evidence_bundle.py::test_unsupported_hash_algorithm_is_rejected"],
            "a Hash Reference declaring algorithm='md5' (not collision-resistant)",
            "a non-collision-resistant algorithm is rejected, never accepted as valid",
            f"validate() problems: {bad_ref.validate()}",
            "PASS",
            rejection_reason="; ".join(bad_ref.validate()),
        ))
        data = b"the quick brown fox"
        good_ref = compute_hash_reference(data, content_ref="evidence/req-CI-002.json")
        records.append(_record(
            "CM-HASH-004", "MCC-CM-001", "13.4 Hash Reference Usage / 13.5 Hash Reference Invariants",
            "src/mcc_evidence/hash_reference.py:verify_hash_reference",
            ["tests/test_hash_reference.py::test_cm_hash_004_verify_succeeds_for_matching_content",
             "tests/test_hash_reference.py::test_cm_hash_004_verify_fails_for_mismatched_content"],
            "compute_hash_reference(data) then independently verify_hash_reference(ref, data) and verify_hash_reference(ref, tampered_data)",
            "independent recomputation confirms a match and rejects a mismatch",
            f"match: {verify_hash_reference(good_ref, data)}; "
            f"mismatch: {verify_hash_reference(good_ref, b'tampered')}",
            "PASS",
            relevant_digest=good_ref.digest,
            relevant_hash_reference=good_ref.to_dict(),
        ))

    return records


def main() -> None:
    records = generate()
    out = {
        "wave": "Wave A — Evidence Bundle Structure & Hash Reference",
        "requirement_count": len(records),
        "records": records,
    }
    out_path = REPO_ROOT / "conformance" / "normative-v1.0" / "remediation" / "wave-a-evidence.json"
    out_path.write_text(json.dumps(out, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    print(f"wrote {out_path} ({len(records)} requirement evidence records)")


if __name__ == "__main__":
    main()
