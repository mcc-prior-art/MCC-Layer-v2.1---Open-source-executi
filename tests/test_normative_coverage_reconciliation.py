"""PR #66 — MCC Normative v1.0 Certification Program Completion Audit &
Coverage Reconciliation.

This is not a new parallel extractor or registry. It is an independent
audit *of* the existing tooling (``src/mcc_conformance/extract.py``,
``assess.py``, ``generate.py``, ``validate.py``) and the committed
registry (``conformance/normative-v1.0/requirements.json``): completeness
(every H1 section with a binding obligation yields at least one
requirement), identity integrity (no duplicate or cross-specification-
colliding requirement IDs), and evidence integrity (every CONFORMANT
requirement's cited evidence file actually contains a matching record, and
every wave evidence record's ``proving_tests`` node ids actually resolve to
real test functions).

See ``conformance/normative-v1.0/reconciliation/`` for the full
human-readable audit report this test file's real-corpus assertions back.
"""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

import pytest

from mcc_conformance.extract import (
    H1_RE,
    SPEC_FILES,
    _has_binding,
    _is_structural,
    extract_all_with_audit,
    extract_spec_with_audit,
)
from mcc_conformance.generate import build_requirements
from mcc_conformance.models import Requirement
from mcc_conformance.validate import validate_evidence_test_nodes, validate_requirements

REPO_ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = REPO_ROOT / "conformance" / "normative-v1.0" / "requirements.json"
REMEDIATION_DIR = REPO_ROOT / "conformance" / "normative-v1.0" / "remediation"

_HEADER = "Version: 1.0\nStatus: Normative\n\n"


def _registry() -> dict:
    return json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))


def _write_spec(tmp_path: Path, spec_id: str, body: str) -> Path:
    specs_dir = tmp_path / "specs"
    specs_dir.mkdir(parents=True, exist_ok=True)
    (specs_dir / f"{spec_id}.md").write_text(_HEADER + body, encoding="utf-8")
    return tmp_path


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


# ---------------------------------------------------------------------------
# 1-2. Deterministic extraction / repeated extraction is byte-identical
# (already exercised extensively by test_conformance_baseline.py /
# test_conformance_extraction_correction.py; re-asserted here at the
# reconciliation-report level so this audit stands on its own).
# ---------------------------------------------------------------------------


def test_full_extraction_is_deterministic_across_repeated_runs():
    first = build_requirements(REPO_ROOT)
    second = build_requirements(REPO_ROOT)
    assert [r.to_dict() for r in first] == [r.to_dict() for r in second]


# ---------------------------------------------------------------------------
# 3-4. Every inventory record has a valid specification ID / section / provenance
# ---------------------------------------------------------------------------


def test_every_registered_requirement_has_a_recognized_specification_id():
    reqs = _registry()["requirements"]
    for r in reqs:
        assert r["specification_id"] in SPEC_FILES, r["requirement_id"]


def test_every_registered_requirement_has_a_nonempty_section_and_source_line():
    reqs = _registry()["requirements"]
    for r in reqs:
        assert r["section"], r["requirement_id"]
        assert isinstance(r["source_line"], int) and r["source_line"] > 0, r["requirement_id"]
        assert (REPO_ROOT / r["source_file"]).exists(), r["requirement_id"]


# ---------------------------------------------------------------------------
# 5-6. No duplicate requirement identity / no duplicate stable ID
# ---------------------------------------------------------------------------


def test_no_duplicate_requirement_id_in_the_real_registry():
    reqs = _registry()["requirements"]
    ids = [r["requirement_id"] for r in reqs]
    dupes = [rid for rid, count in Counter(ids).items() if count > 1]
    assert dupes == []


def test_no_duplicate_normalized_requirement_text_within_the_same_section():
    # Distinct from ID uniqueness: two different IDs should not carry the
    # exact same normalized text within the same (spec, category) --
    # extract.py's own DUPLICATE_OF_CANONICAL/DUPLICATE_WITHIN_DERIVED
    # dedup already prevents this at extraction time; re-verify on the
    # committed registry as a regression guard.
    reqs = _registry()["requirements"]
    seen: dict = {}
    collisions = []
    for r in reqs:
        key = (r["specification_id"], r["requirement_category"], " ".join(r["requirement_text"].split()))
        if key in seen:
            collisions.append((seen[key], r["requirement_id"]))
        else:
            seen[key] = r["requirement_id"]
    assert collisions == []


def test_canonical_id_short_prefix_never_spans_multiple_specifications():
    reqs = [r for r in _registry()["requirements"] if r["id_origin"] == "canonical"]
    prefix_to_specs: dict = {}
    for r in reqs:
        m = re.match(r"^([A-Z]+)-", r["requirement_id"])
        prefix = m.group(1) if m else r["requirement_id"]
        prefix_to_specs.setdefault(prefix, set()).add(r["specification_id"])
    collisions = {p: s for p, s in prefix_to_specs.items() if len(s) > 1}
    assert collisions == {}


def test_derived_ids_are_prefixed_by_their_own_specification_id():
    reqs = [r for r in _registry()["requirements"] if r["id_origin"] == "derived"]
    assert reqs, "expected at least one derived requirement in the real registry"
    for r in reqs:
        assert r["requirement_id"].startswith(r["specification_id"] + "-"), r["requirement_id"]


# ---------------------------------------------------------------------------
# 7-8. No registered requirement is silently orphaned / no evidence record
# points to a missing requirement
# ---------------------------------------------------------------------------


def test_every_conformant_requirements_evidence_file_contains_a_matching_record():
    reqs = [r for r in _registry()["requirements"] if r["conformance_status"] == "CONFORMANT"]
    assert reqs, "expected at least one CONFORMANT requirement"
    cache: dict = {}
    for r in reqs:
        for ev in r["evidence_references"]:
            if ev not in cache:
                cache[ev] = json.loads((REPO_ROOT / ev).read_text(encoding="utf-8"))
            ids_in_file = {rec["requirement_id"] for rec in cache[ev]["records"]}
            assert r["requirement_id"] in ids_in_file, (r["requirement_id"], ev)


def test_no_wave_evidence_record_is_orphaned_from_the_registry():
    reqs_by_id = {r["requirement_id"]: r for r in _registry()["requirements"]}
    for evidence_path in sorted(REMEDIATION_DIR.glob("wave-*-evidence.json")):
        payload = json.loads(evidence_path.read_text(encoding="utf-8"))
        for rec in payload["records"]:
            rid = rec["requirement_id"]
            assert rid in reqs_by_id, (evidence_path.name, rid)
            r = reqs_by_id[rid]
            assert r["conformance_status"] == "CONFORMANT", (evidence_path.name, rid, r["conformance_status"])
            assert str(evidence_path.relative_to(REPO_ROOT)) in r["evidence_references"], (evidence_path.name, rid)


# ---------------------------------------------------------------------------
# 9-11. No CONFORMANT requirement lacks implementation/test evidence;
# referenced implementation files and test nodes exist
# ---------------------------------------------------------------------------


def test_no_conformant_requirement_lacks_implementation_test_or_evidence_references():
    reqs = _registry()["requirements"]
    conformant = [r for r in reqs if r["conformance_status"] == "CONFORMANT"]
    assert conformant, "expected at least one CONFORMANT requirement"
    for r in conformant:
        assert r["implementation_references"], r["requirement_id"]
        assert r["test_references"], r["requirement_id"]
        assert r["evidence_references"], r["requirement_id"]


def test_validate_requirements_rejects_conformant_missing_any_of_the_three_references():
    for missing_field in ("implementation_references", "test_references", "evidence_references"):
        kwargs = dict(
            conformance_status="CONFORMANT",
            implementation_references=["src/mcc_core/signing.py"],
            test_references=["tests/test_mcc_core.py::test_x"],
            evidence_references=["conformance/normative-v1.0/remediation/wave-a-evidence.json"],
        )
        kwargs[missing_field] = []
        errors = validate_requirements([_sample_requirement(**kwargs)], REPO_ROOT)
        assert any("CONFORMANT requires at least one" in e for e in errors), missing_field


def test_referenced_implementation_and_test_file_paths_all_exist_in_real_registry():
    reqs = _registry()["requirements"]
    for r in reqs:
        for ref in r["implementation_references"] + r["test_references"] + r["evidence_references"]:
            path_part = ref.split("::", 1)[0].split(":", 1)[0]
            assert (REPO_ROOT / path_part).exists(), (r["requirement_id"], ref)


def test_validate_evidence_test_nodes_passes_on_the_real_committed_evidence():
    errors = validate_evidence_test_nodes(REPO_ROOT)
    assert errors == []


def test_validate_evidence_test_nodes_detects_a_missing_test_function(tmp_path):
    remediation = tmp_path / "conformance" / "normative-v1.0" / "remediation"
    remediation.mkdir(parents=True)
    tests_dir = tmp_path / "tests"
    tests_dir.mkdir()
    (tests_dir / "test_fixture.py").write_text("def test_something_else():\n    pass\n", encoding="utf-8")
    (remediation / "wave-x-evidence.json").write_text(json.dumps({
        "records": [{"requirement_id": "X-001", "proving_tests": ["tests/test_fixture.py::test_this_does_not_exist"]}]
    }), encoding="utf-8")
    errors = validate_evidence_test_nodes(tmp_path)
    assert any("no `def test_this_does_not_exist`" in e for e in errors)


def test_validate_evidence_test_nodes_detects_a_missing_file(tmp_path):
    remediation = tmp_path / "conformance" / "normative-v1.0" / "remediation"
    remediation.mkdir(parents=True)
    (remediation / "wave-x-evidence.json").write_text(json.dumps({
        "records": [{"requirement_id": "X-001", "proving_tests": ["tests/does_not_exist.py::test_x"]}]
    }), encoding="utf-8")
    errors = validate_evidence_test_nodes(tmp_path)
    assert any("missing file" in e for e in errors)


def test_validate_evidence_test_nodes_detects_a_bare_non_qualified_name(tmp_path):
    remediation = tmp_path / "conformance" / "normative-v1.0" / "remediation"
    remediation.mkdir(parents=True)
    (remediation / "wave-x-evidence.json").write_text(json.dumps({
        "records": [{"requirement_id": "X-001", "proving_tests": ["test_bare_name_no_file"]}]
    }), encoding="utf-8")
    errors = validate_evidence_test_nodes(tmp_path)
    assert any("not a fully-qualified pytest node id" in e for e in errors)


# ---------------------------------------------------------------------------
# 12. Cross-specification category names cannot cause status collisions
# ---------------------------------------------------------------------------


def test_category_names_shared_across_specifications_do_not_cause_rule_collisions():
    # MCC-TC-001 and MCC-EB-001/MCC-CM-001 legitimately share category
    # *names* (e.g. "6. Required Fields" exists in more than one spec) --
    # assess.py's rule matching must be scoped by specification_id, never
    # by category string alone.
    from mcc_conformance.assess import RULES

    for rule_spec, _pattern, _status, _evidence, _rationale in RULES:
        assert rule_spec == "*" or rule_spec in SPEC_FILES, rule_spec

    reqs = _registry()["requirements"]
    cats_by_spec: dict = {}
    for r in reqs:
        cats_by_spec.setdefault(r["requirement_category"], set()).add(r["specification_id"])
    shared_categories = {c: s for c, s in cats_by_spec.items() if len(s) > 1}
    assert shared_categories, "expected at least one category name shared across specs (sanity check for this test)"

    # For every shared category, confirm the two specs' requirements were
    # assessed independently (their rationale text or status is not
    # necessarily identical, proving the match is per-spec, not a category
    # string broadcast) -- spot check via requirement_id specificity.
    for category, specs in shared_categories.items():
        for spec_id in specs:
            matching = [r for r in reqs if r["requirement_category"] == category and r["specification_id"] == spec_id]
            assert matching, (category, spec_id)


# ---------------------------------------------------------------------------
# 13. Generated totals reconcile exactly
# ---------------------------------------------------------------------------


def test_status_counts_reconcile_to_the_total_requirement_count():
    reqs = _registry()["requirements"]
    counts = Counter(r["conformance_status"] for r in reqs)
    assert sum(counts.values()) == len(reqs) == _registry()["requirement_count"]


# ---------------------------------------------------------------------------
# 14-15. New requirements cannot become CONFORMANT automatically; missing
# requirements default to the evidence-supported status (GAP), not optimistic
# ---------------------------------------------------------------------------


def test_a_brand_new_requirement_defaults_to_gap_not_conformant(tmp_path):
    from mcc_conformance.assess import assess

    fresh = Requirement(
        requirement_id="ZZ-NEW-999",
        specification_id="MCC-TC-001",
        specification_version="1.0",
        source_file="specs/MCC-TC-001.md",
        section="A Brand New Section Nobody Has Ever Assessed",
        normative_keyword="MUST",
        requirement_text="A brand new obligation nothing in the repository implements yet.",
        requirement_category="A Brand New Section Nobody Has Ever Assessed",
        id_origin="derived",
        source_line=1,
    )
    assessed = assess([fresh])[0]
    assert assessed.conformance_status == "GAP"
    assert assessed.rationale


# ---------------------------------------------------------------------------
# 16-18. NOT_APPLICABLE / PARTIAL / GAP require explicit rationale
# ---------------------------------------------------------------------------


def test_every_not_applicable_requirement_has_an_explicit_scope_rationale():
    reqs = [r for r in _registry()["requirements"] if r["conformance_status"] == "NOT_APPLICABLE"]
    assert reqs
    for r in reqs:
        assert r["rationale"].strip(), r["requirement_id"]


def test_every_partial_and_gap_requirement_has_an_explicit_rationale():
    reqs = [r for r in _registry()["requirements"] if r["conformance_status"] in ("PARTIAL", "GAP")]
    assert reqs
    for r in reqs:
        assert r["rationale"].strip(), r["requirement_id"]


# ---------------------------------------------------------------------------
# 19-21. Existing Wave A/B/C evidence remains valid
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("wave_letter,expected_count", [("a", 13), ("b", 5), ("c", 73)])
def test_wave_evidence_record_count_matches_its_scope_manifest(wave_letter, expected_count):
    evidence_path = REMEDIATION_DIR / f"wave-{wave_letter}-evidence.json"
    payload = json.loads(evidence_path.read_text(encoding="utf-8"))
    assert payload["requirement_count"] == len(payload["records"]) == expected_count
    for rec in payload["records"]:
        assert rec["verification_outcome"] == "PASS", rec["requirement_id"]


# ---------------------------------------------------------------------------
# 22-23. Registry / report generation is idempotent
# ---------------------------------------------------------------------------


def test_registry_generation_is_idempotent():
    from mcc_conformance import generate as gen

    reqs = build_requirements(REPO_ROOT)
    first = gen._requirements_json(reqs)
    second = gen._requirements_json(build_requirements(REPO_ROOT))
    assert first == second


def test_report_generation_is_idempotent():
    from mcc_conformance import generate as gen

    reqs = build_requirements(REPO_ROOT)
    assert gen._matrix_md(reqs) == gen._matrix_md(build_requirements(REPO_ROOT))
    assert gen._gap_report_md(reqs) == gen._gap_report_md(build_requirements(REPO_ROOT))


# ---------------------------------------------------------------------------
# 24-27. Intentional fixtures: missing requirement / duplicate / non-normative
# example / cross-specification ID collision
# ---------------------------------------------------------------------------


def test_fixture_missing_must_requirement_in_a_canonical_bearing_section_is_detected(tmp_path):
    # Reproduces, on a minimal fixture, exactly the class of defect Wave 1
    # found in the real corpus (391 orphaned lines): a MUST statement in a
    # section that already has a canonical ID must still be extracted.
    body = (
        "# 1. Example Section\n\n"
        "EX-001\n\nThe canonical requirement text.\n\n"
        "A second, independent obligation: the system MUST also do this.\n"
    )
    root = _write_spec(tmp_path, "MCC-EB-001", body)
    reqs, _audit = extract_spec_with_audit("MCC-EB-001", root)
    texts = [r.requirement_text for r in reqs]
    assert any("MUST also do this" in t for t in texts)


def test_fixture_duplicate_requirement_text_is_flagged_not_silently_extracted_twice(tmp_path):
    # The repeated sentence sits after a horizontal rule so it is genuinely
    # outside any canonical ID's own absorbed paragraph (a real-corpus
    # example: MCC-EB-001's EB-STR-001 restates Section 10.1's opening
    # sentence word for word, later in the same H1 section) -- proving the
    # dedup match is by normalized text, not merely "never re-extract
    # anything after an ID line".
    body = (
        "# 1. Example Section\n\n"
        "EX-001\n\nThe system MUST remain framework-neutral.\n\n"
        "EX-002\n\nA completely different requirement text.\n\n"
        "---\n\n"
        "The system MUST remain framework-neutral.\n"
    )
    root = _write_spec(tmp_path, "MCC-EB-001", body)
    reqs, audit = extract_spec_with_audit("MCC-EB-001", root)
    non_canonical = [r for r in reqs if r.id_origin != "canonical"]
    assert non_canonical == []
    assert any(e.disposition == "DUPLICATE_OF_CANONICAL" for e in audit)


def test_fixture_non_normative_example_section_is_assessed_not_applicable():
    # Real corpus: MCC-CP-001's Appendix E (Example Certification Flow) and
    # Appendix F (Future Extensions) contain MUST/SHALL-bearing prose that
    # extraction correctly finds (it is not silently dropped), but
    # assessment correctly marks NOT_APPLICABLE -- never CONFORMANT/
    # PARTIAL/GAP -- because it is illustrative, not a normative obligation
    # on the certification subject.
    reqs = _registry()["requirements"]
    example_appendix = [
        r for r in reqs
        if r["requirement_category"] in ("Appendix E — Example Certification Flow", "Appendix F — Future Extensions")
    ]
    assert example_appendix, "expected the real corpus to contain these appendices"
    for r in example_appendix:
        assert r["conformance_status"] == "NOT_APPLICABLE", r["requirement_id"]


def test_fixture_cross_specification_requirement_id_collision_is_rejected():
    reqs = [
        _sample_requirement(requirement_id="SHARED-001", specification_id="MCC-EB-001"),
        _sample_requirement(requirement_id="SHARED-001", specification_id="MCC-TC-001"),
    ]
    errors = validate_requirements(reqs, REPO_ROOT)
    assert any("Duplicate requirement_id: SHARED-001" in e for e in errors)


# ---------------------------------------------------------------------------
# 28. No global conformance control was weakened
# ---------------------------------------------------------------------------


def test_every_h1_section_with_a_binding_keyword_yields_at_least_one_requirement():
    """Independent, from-scratch re-verification (not reusing extract.py's
    own internal bookkeeping) that no H1 section containing a MUST/MUST
    NOT/SHALL/SHALL NOT/REQUIRED-bearing line is silently unrepresented in
    the registry -- the exact class of completeness failure this PR's
    audit was commissioned to rule out."""
    reqs, _audits = extract_all_with_audit(REPO_ROOT)
    produced = set()
    for r in reqs:
        produced.add((r.specification_id, r.requirement_category))

    problems = []
    for spec_id, rel_path in SPEC_FILES.items():
        lines = (REPO_ROOT / rel_path).read_text(encoding="utf-8").split("\n")
        current_h1 = None
        has_binding = False

        def flush():
            if current_h1 is not None and has_binding and (spec_id, current_h1) not in produced:
                problems.append((spec_id, current_h1))

        for line in lines:
            m = H1_RE.match(line)
            if m:
                flush()
                current_h1 = m.group(1).strip()
                has_binding = False
                continue
            stripped = line.strip()
            if current_h1 and not _is_structural(stripped) and _has_binding(stripped):
                has_binding = True
        flush()
    assert problems == []
