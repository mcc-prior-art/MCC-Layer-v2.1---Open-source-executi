"""Tests for the Normative v1.0 implementation-conformance baseline tooling
(src/mcc_conformance). These tests fail closed: an incomplete or structurally
invalid conformance inventory is a test failure, not a warning.
"""

from __future__ import annotations

import copy
from pathlib import Path

from mcc_conformance.extract import SPEC_FILES, extract_all, extract_spec
from mcc_conformance.generate import BASELINE, build_requirements
from mcc_conformance.models import ALLOWED_STATUSES, Requirement
from mcc_conformance.validate import (
    validate_all,
    validate_committed_matches_generated,
    validate_in_memory,
    validate_requirements,
    validate_schemas,
)

REPO_ROOT = Path(__file__).resolve().parents[1]


# ---------------------------------------------------------------------------
# Discovery
# ---------------------------------------------------------------------------


def test_discovers_requirements_from_all_four_specs():
    reqs = extract_all(REPO_ROOT)
    found_specs = {r.specification_id for r in reqs}
    assert found_specs == set(SPEC_FILES)
    # Exact total from the corrected deterministic extraction (see
    # conformance/normative-v1.0/remediation/wave-1-execution-boundary-scope-manifest.md,
    # Finding 1, and extraction_coverage_audit.json for the full
    # reconciliation). Not an advance estimate: this is the actual output of
    # extract_all() as of this corrected extractor, re-asserted here so a
    # future regression in extraction coverage is a test failure rather than
    # a silently-passing floor check.
    assert len(reqs) == 810


def test_discovers_canonical_and_derived_requirements():
    reqs = extract_all(REPO_ROOT)
    origins = {r.id_origin for r in reqs}
    assert origins == {"canonical", "derived"}
    # Canonical extraction (Pass 1) is untouched by the extraction
    # correction: exactly the same 361 canonical requirements as before.
    canonical = [r for r in reqs if r.id_origin == "canonical"]
    assert len(canonical) == 361
    derived = [r for r in reqs if r.id_origin == "derived"]
    assert len(derived) == 449


def test_canonical_ids_use_the_specifications_own_identifiers():
    reqs = extract_spec("MCC-TC-001", REPO_ROOT)
    ids = {r.requirement_id for r in reqs if r.id_origin == "canonical"}
    # TC-SIG-001 is a real canonical identifier defined in MCC-TC-001 Section 14.
    assert "TC-SIG-001" in ids


# ---------------------------------------------------------------------------
# Stable ID generation / determinism
# ---------------------------------------------------------------------------


def test_extraction_is_deterministic_across_runs():
    reqs1 = [r.to_dict() for r in extract_all(REPO_ROOT)]
    reqs2 = [r.to_dict() for r in extract_all(REPO_ROOT)]
    assert reqs1 == reqs2


def test_full_pipeline_is_deterministic():
    reqs1 = [r.to_dict() for r in build_requirements(REPO_ROOT)]
    reqs2 = [r.to_dict() for r in build_requirements(REPO_ROOT)]
    assert reqs1 == reqs2


def test_derived_id_format_is_stable():
    reqs = extract_all(REPO_ROOT)
    derived = [r for r in reqs if r.id_origin == "derived"]
    assert derived, "expected at least one derived requirement in the corpus"
    for r in derived[:5]:
        assert r.requirement_id.startswith(f"{r.specification_id}-")
        assert "-D" in r.requirement_id


# ---------------------------------------------------------------------------
# Duplicate / missing detection
# ---------------------------------------------------------------------------


def test_no_duplicate_requirement_ids_in_real_corpus():
    reqs = build_requirements(REPO_ROOT)
    ids = [r.requirement_id for r in reqs]
    assert len(ids) == len(set(ids))


def test_duplicate_requirement_id_is_detected():
    reqs = build_requirements(REPO_ROOT)
    reqs.append(copy.deepcopy(reqs[0]))
    errors = validate_requirements(reqs, REPO_ROOT)
    assert any("Duplicate requirement_id" in e for e in errors)


def test_empty_requirement_set_is_rejected():
    errors = validate_requirements([], REPO_ROOT)
    assert any("empty set" in e for e in errors)


# ---------------------------------------------------------------------------
# Status / reference validation
# ---------------------------------------------------------------------------


def _sample_requirement(**overrides) -> Requirement:
    base = dict(
        requirement_id="TEST-001",
        specification_id="MCC-TC-001",
        specification_version="1.0",
        source_file="specs/MCC-TC-001.md",
        section="14. Signature Requirements",
        normative_keyword="MUST",
        requirement_text="Test requirement.",
        requirement_category="Signature Requirements",
        id_origin="canonical",
        source_line=1,
        conformance_status="GAP",
        rationale="test rationale",
    )
    base.update(overrides)
    return Requirement(**base)


def test_invalid_status_is_rejected():
    reqs = [_sample_requirement(conformance_status="MOSTLY_FINE")]
    errors = validate_requirements(reqs, REPO_ROOT)
    assert any("invalid conformance_status" in e for e in errors)


def test_conformant_without_implementation_reference_is_rejected():
    reqs = [
        _sample_requirement(
            conformance_status="CONFORMANT",
            test_references=["tests/test_mcc_core.py::test_x"],
            implementation_references=[],
        )
    ]
    errors = validate_requirements(reqs, REPO_ROOT)
    assert any("CONFORMANT requires at least one implementation_reference" in e for e in errors)


def test_conformant_without_test_reference_is_rejected():
    reqs = [
        _sample_requirement(
            conformance_status="CONFORMANT",
            implementation_references=["src/mcc_core/signing.py"],
            test_references=[],
        )
    ]
    errors = validate_requirements(reqs, REPO_ROOT)
    assert any("CONFORMANT requires at least one test_reference" in e for e in errors)


def test_conformant_with_both_references_passes():
    reqs = [
        _sample_requirement(
            conformance_status="CONFORMANT",
            implementation_references=["src/mcc_core/signing.py"],
            test_references=["tests/test_mcc_core.py::test_x"],
        )
    ]
    errors = validate_requirements(reqs, REPO_ROOT)
    assert errors == []


def test_non_conformant_without_rationale_is_rejected():
    reqs = [_sample_requirement(conformance_status="GAP", rationale="")]
    errors = validate_requirements(reqs, REPO_ROOT)
    assert any("requires a non-empty rationale" in e for e in errors)


def test_invalid_repository_reference_is_rejected_in_real_corpus():
    errors = validate_in_memory(REPO_ROOT)
    # The real corpus must reference only real paths.
    assert not any("does not exist" in e for e in errors), errors


def test_invalid_repository_reference_is_detected():
    bad = _sample_requirement(
        implementation_references=["src/mcc_core/this_file_does_not_exist.py"],
        test_references=["tests/test_mcc_core.py"],
    )
    errors = validate_requirements([bad], REPO_ROOT)
    assert any("does not exist" in e for e in errors), errors


def test_invalid_source_file_is_detected():
    bad = _sample_requirement(source_file="specs/MCC-DOES-NOT-EXIST-001.md")
    errors = validate_requirements([bad], REPO_ROOT)
    assert any("source_file does not exist" in e for e in errors), errors


# ---------------------------------------------------------------------------
# Schema validation
# ---------------------------------------------------------------------------


def test_committed_artifacts_pass_schema_validation():
    errors = validate_schemas(REPO_ROOT)
    assert errors == [], errors


def test_requirement_schema_rejects_unknown_field():
    from mcc_conformance.validate import _check_object, _load_schema

    schema = _load_schema(REPO_ROOT, "requirement.schema.json")
    obj = {
        "requirement_id": "X",
        "specification_id": "MCC-TC-001",
        "specification_version": "1.0",
        "source_file": "specs/MCC-TC-001.md",
        "section": "x",
        "normative_keyword": "MUST",
        "requirement_text": "x",
        "requirement_category": "x",
        "id_origin": "canonical",
        "source_line": 1,
        "implementation_references": [],
        "test_references": [],
        "evidence_references": [],
        "conformance_status": "GAP",
        "rationale": "x",
        "notes": None,
        "unexpected_field": "boom",
    }
    errors = _check_object(obj, schema, "test")
    assert any("unexpected field" in e for e in errors)


def test_requirement_schema_rejects_invalid_enum():
    from mcc_conformance.validate import _check_object, _load_schema

    schema = _load_schema(REPO_ROOT, "requirement.schema.json")
    obj = {
        "requirement_id": "X",
        "specification_id": "NOT-A-REAL-SPEC",
        "specification_version": "1.0",
        "source_file": "specs/MCC-TC-001.md",
        "section": "x",
        "normative_keyword": "MUST",
        "requirement_text": "x",
        "requirement_category": "x",
        "id_origin": "canonical",
        "source_line": 1,
        "implementation_references": [],
        "test_references": [],
        "evidence_references": [],
        "conformance_status": "GAP",
        "rationale": "x",
        "notes": None,
    }
    errors = _check_object(obj, schema, "test")
    assert any("not in" in e for e in errors)


# ---------------------------------------------------------------------------
# Baseline / provenance
# ---------------------------------------------------------------------------


def test_baseline_provenance_matches_the_declared_normative_commit():
    assert BASELINE["baseline_commit"] == "a65b2f375408dfbe8df86fbfc09724c5c45d3ba4"
    assert BASELINE["tag"] == "mcc-spec-v1.0.0"
    assert BASELINE["final_disposition"] == "APPROVE FOR NORMATIVE v1.0"
    assert len(BASELINE["specifications"]) == 4
    for spec in BASELINE["specifications"]:
        assert spec["version"] == "1.0"
        assert spec["status"] == "Normative"


def test_specification_files_declare_normative_v1_status():
    for spec_id, source_file in SPEC_FILES.items():
        text = (REPO_ROOT / source_file).read_text(encoding="utf-8")
        assert "Version: 1.0" in text, f"{spec_id} does not declare Version: 1.0"
        assert "Status: Normative" in text, f"{spec_id} does not declare Status: Normative"


# ---------------------------------------------------------------------------
# Full validator (fail-closed) against the real committed artifacts
# ---------------------------------------------------------------------------


def test_committed_artifacts_are_not_stale():
    errors = validate_committed_matches_generated(REPO_ROOT)
    assert errors == [], errors


def test_full_validate_all_passes_on_committed_baseline():
    errors = validate_all(REPO_ROOT)
    assert errors == [], errors


def test_every_requirement_has_exactly_one_status():
    reqs = build_requirements(REPO_ROOT)
    for r in reqs:
        assert r.conformance_status in ALLOWED_STATUSES
        assert isinstance(r.conformance_status, str)


def test_no_requirement_claims_conformant_without_evidence():
    """As of this baseline, no requirement is CONFORMANT (see README /
    gap_report.md for why) — this test guards against silently upgrading a
    requirement to CONFORMANT without also adding real implementation and
    test references, which validate_in_memory would otherwise catch, but
    this test documents the intent explicitly."""
    reqs = build_requirements(REPO_ROOT)
    for r in reqs:
        if r.conformance_status == "CONFORMANT":
            assert r.implementation_references, r.requirement_id
            assert r.test_references, r.requirement_id
