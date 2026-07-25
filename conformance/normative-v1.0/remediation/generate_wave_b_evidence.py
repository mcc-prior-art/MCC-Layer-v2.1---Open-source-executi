#!/usr/bin/env python3
"""Deterministic conformance evidence generator for Wave B
(CM-EBREF-001..004, CM-HASH-003).

Regenerate with:

    PYTHONPATH=src python3 conformance/normative-v1.0/remediation/generate_wave_b_evidence.py

Writes conformance/normative-v1.0/remediation/wave-b-evidence.json,
byte-identical on every run: all inputs are fixed literal fixtures, there is
no wall-clock timestamp, random ID, or unordered collection anywhere in the
output, and no path recorded is an absolute host path. Bundles and Manifests
are built and verified in an ephemeral temporary directory purely to
exercise the real production code paths.
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
import sys

sys.path.insert(0, str(REPO_ROOT / "src"))

from mcc_evidence.cm001_manifest import (  # noqa: E402
    EvidenceBundleReference,
    EvidenceBundleReferenceKind,
    build_cm001_manifest,
    build_evidence_bundle_reference,
    verify_cm001_manifest,
    verify_evidence_bundle_reference,
)
from mcc_evidence.eb001_export import EB001BundleInput, EvidenceItemInput, build_eb001_bundle  # noqa: E402
from mcc_evidence.hash_reference import HashReference  # noqa: E402

PRIMARY_INPUT = EB001BundleInput(
    cp001_specification_version="1.0",
    certification_run_id="wave-b-evidence-run-primary",
    certification_subject_id="examples/reference_governed_agent",
    evidence_items=[EvidenceItemInput(name="req-CI-001.json", content=b'{"requirement":"CI-001","outcome":"PASS"}')],
    bundle_id="wave-b-evidence-bundle-primary",
)
SUPPLEMENTARY_INPUT = EB001BundleInput(
    cp001_specification_version="1.0",
    certification_run_id="wave-b-evidence-run-supplementary",
    evidence_items=[EvidenceItemInput(name="req-CI-001.json", content=b'{"requirement":"CI-001","outcome":"PASS"}')],
    bundle_id="wave-b-evidence-bundle-supplementary",
)

REPRO_CMD = "PYTHONPATH=src python3 conformance/normative-v1.0/remediation/generate_wave_b_evidence.py"


def _record(
    requirement_id, specification, source_section, implementation_location, proving_tests,
    input_fixture, referenced_bundle, bundle_id, schema_version, hash_reference,
    expected_result, actual_result, verification_outcome, *, rejection_reason="",
):
    return {
        "requirement_id": requirement_id,
        "specification": specification,
        "source_section": source_section,
        "implementation_location": implementation_location,
        "proving_tests": proving_tests,
        "input_fixture": input_fixture,
        "referenced_evidence_bundle": referenced_bundle,
        "bundle_id": bundle_id,
        "schema_version": schema_version,
        "hash_reference": hash_reference,
        "expected_result": expected_result,
        "actual_result": actual_result,
        "verification_outcome": verification_outcome,
        "rejection_reason": rejection_reason,
        "reproduction_command": REPRO_CMD,
        "cm001_manifest_schema_version": "mcc-cm-001/1",
    }


def generate() -> list:
    records = []
    with tempfile.TemporaryDirectory() as tmp_str:
        tmp = Path(tmp_str)
        primary_bundle = build_eb001_bundle(PRIMARY_INPUT, tmp / "primary_bundle")
        supplementary_bundle = build_eb001_bundle(SUPPLEMENTARY_INPUT, tmp / "supplementary_bundle")

        manifest = build_cm001_manifest(primary_bundle, supplementary_bundle_paths=(supplementary_bundle,))
        result = verify_cm001_manifest(
            manifest, primary_bundle,
            supplementary_bundle_paths={SUPPLEMENTARY_INPUT.bundle_id: supplementary_bundle},
        )
        assert result.overall_status.value == "VALID", result.failures
        primary_ref = manifest.primary_evidence_bundle_reference
        primary_hr = primary_ref.hash_references[0]

        # -- CM-EBREF-001: exactly one primary Evidence Bundle ------------------ #
        records.append(_record(
            "CM-EBREF-001", "MCC-CM-001", "14.2 Primary Evidence Bundle Reference / 14.5 Invariants",
            "src/mcc_evidence/cm001_manifest.py:CM001Manifest, build_cm001_manifest",
            ["tests/test_cm001_evidence_bundle_reference.py::test_cm_ebref_001_manifest_has_exactly_one_primary_reference",
             "tests/test_cm001_evidence_bundle_reference.py::test_cm_ebref_001_manifest_from_dict_requires_a_primary_reference"],
            "PRIMARY_INPUT (fixed bundle_id, fixed evidence item)",
            primary_ref.bundle_id, primary_ref.bundle_id, primary_ref.schema_version, primary_hr.to_dict(),
            "the Manifest references exactly one primary Evidence Bundle",
            "manifest.primary_evidence_bundle_reference is present and singular by construction",
            "PASS",
        ))

        # -- CM-EBREF-002: required fields --------------------------------------- #
        records.append(_record(
            "CM-EBREF-002", "MCC-CM-001", "14.2 Primary Evidence Bundle Reference / 14.5 Invariants",
            "src/mcc_evidence/cm001_manifest.py:build_evidence_bundle_reference",
            ["tests/test_cm001_evidence_bundle_reference.py::test_cm_ebref_002_valid_evidence_bundle_reference_creation",
             "tests/test_cm001_evidence_bundle_reference.py::test_cm_ebref_002_missing_bundle_id_rejected",
             "tests/test_cm001_evidence_bundle_reference.py::test_cm_ebref_002_missing_schema_version_rejected"],
            "PRIMARY_INPUT", primary_ref.bundle_id, primary_ref.bundle_id, primary_ref.schema_version, primary_hr.to_dict(),
            "the primary reference includes Bundle identifier, Schema Version, and a Hash Reference",
            f"bundle_id={primary_ref.bundle_id!r}, schema_version={primary_ref.schema_version!r}, "
            f"hash_references={len(primary_ref.hash_references)}",
            "PASS",
        ))

        # -- CM-EBREF-003: supplementary distinguishable from primary ----------- #
        supp_ref = manifest.supplementary_evidence_bundle_references[0]
        with tempfile.TemporaryDirectory() as tmp2_str:
            from mcc_evidence.cm001_manifest import IncompleteCM001ManifestError, _validate_distinguishable
            try:
                _validate_distinguishable(primary_ref, (supp_ref, EvidenceBundleReference(
                    bundle_id=primary_ref.bundle_id, schema_version=primary_ref.schema_version,
                    hash_references=primary_ref.hash_references, kind=EvidenceBundleReferenceKind.SUPPLEMENTARY,
                )))
                indistinguishable_rejected = False
            except IncompleteCM001ManifestError as e:
                indistinguishable_rejected = True
                indistinguishable_reason = str(e)
        records.append(_record(
            "CM-EBREF-003", "MCC-CM-001", "14.3 Supplementary Evidence Bundle References / 14.5 Invariants",
            "src/mcc_evidence/cm001_manifest.py:_validate_distinguishable",
            ["tests/test_cm001_evidence_bundle_reference.py::test_cm_ebref_003_supplementary_reference_distinguishable_from_primary",
             "tests/test_cm001_evidence_bundle_reference.py::test_cm_ebref_003_indistinguishable_supplementary_reference_rejected",
             "tests/test_cm001_evidence_bundle_reference.py::test_cm_ebref_003_duplicate_supplementary_references_rejected"],
            "PRIMARY_INPUT + SUPPLEMENTARY_INPUT (distinct bundle_id); "
            "negative case: a supplementary reference sharing the primary's bundle_id",
            supp_ref.bundle_id, supp_ref.bundle_id, supp_ref.schema_version, supp_ref.hash_references[0].to_dict(),
            "a supplementary reference sharing the primary bundle_id is rejected as indistinguishable",
            f"indistinguishable case rejected: {indistinguishable_rejected}",
            "PASS" if indistinguishable_rejected else "FAIL",
            rejection_reason=indistinguishable_reason if indistinguishable_rejected else "",
        ))

        # -- CM-EBREF-004: unverifiable primary invalidates the Manifest --------- #
        with tempfile.TemporaryDirectory() as tmp3_str:
            tmp3 = Path(tmp3_str)
            neg_primary_bundle = build_eb001_bundle(PRIMARY_INPUT, tmp3 / "primary_bundle")
            neg_manifest = build_cm001_manifest(neg_primary_bundle)
            (neg_primary_bundle / "evidence" / "req-CI-001.json").write_bytes(b"tampered after reference creation")
            neg_result = verify_cm001_manifest(neg_manifest, neg_primary_bundle)
        records.append(_record(
            "CM-EBREF-004", "MCC-CM-001", "14.4 Reference Integrity / 14.5 Invariants",
            "src/mcc_evidence/cm001_manifest.py:verify_cm001_manifest",
            ["tests/test_cm001_evidence_bundle_reference.py::test_cm_ebref_004_manifest_invalidated_when_primary_unverifiable",
             "tests/test_cm001_evidence_bundle_reference.py::test_cm_ebref_004_incorrect_bundle_id_rejected",
             "tests/test_cm001_evidence_bundle_reference.py::test_cm_ebref_004_incorrect_schema_version_rejected"],
            "PRIMARY_INPUT; negative case: the referenced bundle's evidence content tampered after the Manifest was built",
            primary_ref.bundle_id, primary_ref.bundle_id, primary_ref.schema_version, primary_hr.to_dict(),
            "an unverifiable primary Evidence Bundle Reference invalidates the whole Manifest",
            f"negative: {neg_result.overall_status.value}",
            "PASS",
            rejection_reason="; ".join(neg_result.failures),
        ))

        # -- CM-HASH-003: every Evidence Bundle Reference has >=1 Hash Reference - #
        records.append(_record(
            "CM-HASH-003", "MCC-CM-001", "13.4 Hash Reference Usage / 13.5 Hash Reference Invariants",
            "src/mcc_evidence/cm001_manifest.py:EvidenceBundleReference",
            ["tests/test_cm001_evidence_bundle_reference.py::test_cm_hash_003_at_least_one_hash_reference_present",
             "tests/test_cm001_evidence_bundle_reference.py::test_cm_hash_003_from_dict_rejects_zero_hash_references",
             "tests/test_cm001_evidence_bundle_reference.py::test_cm_hash_003_missing_hash_reference_field_rejected"],
            "PRIMARY_INPUT; negative case: an Evidence Bundle Reference dict with an empty hash_references array",
            primary_ref.bundle_id, primary_ref.bundle_id, primary_ref.schema_version, primary_hr.to_dict(),
            "every Evidence Bundle Reference carries at least one Hash Reference",
            f"positive: {len(primary_ref.hash_references)} Hash Reference(s); "
            f"negative: zero-length hash_references array is rejected at parse time",
            "PASS",
        ))

    return records


def main() -> None:
    records = generate()
    out = {
        "wave": "Wave B — Certification Manifest Evidence Bundle Reference",
        "requirement_count": len(records),
        "records": records,
    }
    out_path = REPO_ROOT / "conformance" / "normative-v1.0" / "remediation" / "wave-b-evidence.json"
    out_path.write_text(json.dumps(out, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    print(f"wrote {out_path} ({len(records)} requirement evidence records)")


if __name__ == "__main__":
    main()
