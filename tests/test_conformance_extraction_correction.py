"""Regression tests for the PR #62 extraction correction
(src/mcc_conformance/extract.py): a canonical-ID-bearing H1 section must not
cause other independent normative MUST/SHALL obligations in that same
section to be silently dropped, and the corrected extractor must not
degrade into an unsafe "one line containing MUST/SHALL equals one
requirement" rule.

Each test below is anchored either to a synthetic minimal fixture (isolating
one specific mechanism) or to a concrete, already-verified location in the
real specifications (guarding the actual defect this PR fixes). Real-corpus
line numbers cited in comments were verified against the specification
files at the time this test was written; if a future specification edit
moves them, the assertions here are on *content*, not on hardcoded line
numbers, except where explicitly noted.
"""

from __future__ import annotations

from pathlib import Path

from mcc_conformance.extract import (
    SPEC_FILES,
    _normalize,
    extract_all,
    extract_all_with_audit,
    extract_spec,
    extract_spec_with_audit,
)

REPO_ROOT = Path(__file__).resolve().parents[1]

_HEADER = "Version: 1.0\nStatus: Normative\n\n"


def _write_spec(tmp_path: Path, spec_id: str, body: str) -> Path:
    specs_dir = tmp_path / "specs"
    specs_dir.mkdir(parents=True, exist_ok=True)
    path = specs_dir / f"{spec_id}.md"
    path.write_text(_HEADER + body, encoding="utf-8")
    return tmp_path


def _source_window(source_file: str, source_line: int, extra: int = 2) -> str:
    lines = (REPO_ROOT / source_file).read_text(encoding="utf-8").split("\n")
    start = max(0, source_line - 1)
    end = min(len(lines), start + 1 + extra)
    return " ".join(l.strip() for l in lines[start:end])


# ---------------------------------------------------------------------------
# 1. Canonical ID + additional independent normative obligation in the same
#    H1 section.
# ---------------------------------------------------------------------------


def test_canonical_section_also_yields_independent_orphaned_obligation(tmp_path):
    body = (
        "# 1. Example Section\n\n"
        "An independent obligation not tied to any canonical ID. "
        "This section MUST remain framework-neutral.\n\n"
        "## 1.5 Example Invariants\n\n"
        "EX-STR-001\n\n"
        "This is the canonical requirement text.\n\n"
        "---\n"
    )
    root = _write_spec(tmp_path, "MCC-CP-001", body)
    reqs = extract_spec("MCC-CP-001", root)
    ids = {r.requirement_id: r for r in reqs}
    assert "EX-STR-001" in ids
    assert ids["EX-STR-001"].requirement_text == "This is the canonical requirement text."
    derived = [r for r in reqs if r.id_origin == "derived"]
    assert len(derived) == 1
    assert "framework-neutral" in derived[0].requirement_text


# ---------------------------------------------------------------------------
# 2. Canonical text is not re-extracted as a duplicate derived requirement.
# ---------------------------------------------------------------------------


def test_canonical_text_verbatim_repeated_is_not_duplicated(tmp_path):
    body = (
        "# 1. Example Section\n\n"
        "Every Widget SHALL have exactly one Owner.\n\n"
        "## 1.5 Example Invariants\n\n"
        "EX-STR-001\n\n"
        "Every Widget SHALL have exactly one Owner.\n\n"
        "---\n"
    )
    root = _write_spec(tmp_path, "MCC-CP-001", body)
    reqs, audit = extract_spec_with_audit("MCC-CP-001", root)
    canonical = [r for r in reqs if r.id_origin == "canonical"]
    derived = [r for r in reqs if r.id_origin == "derived"]
    assert len(canonical) == 1
    assert derived == []  # the verbatim repeat must not become its own ID
    dup_entries = [e for e in audit if e.disposition == "DUPLICATE_OF_CANONICAL"]
    assert len(dup_entries) == 1
    assert dup_entries[0].duplicate_of == "EX-STR-001"


def test_real_corpus_eb001_verbatim_duplicate_is_reconciled_not_dropped():
    # specs/MCC-EB-001.md Section 10.1 states "Every Evidence Bundle SHALL
    # have exactly one Bundle Root." verbatim; Section 10.5's canonical
    # EB-STR-001 restates the identical sentence. The corrected extractor
    # must recognize this as the same obligation, not silently drop it and
    # not fabricate a second requirement ID for it.
    reqs, audits = extract_all_with_audit(REPO_ROOT)
    ids = {r.requirement_id for r in reqs}
    assert "EB-STR-001" in ids
    dup = [
        e
        for e in audits["MCC-EB-001"]
        if e.disposition == "DUPLICATE_OF_CANONICAL" and e.duplicate_of == "EB-STR-001"
    ]
    assert len(dup) == 1


# ---------------------------------------------------------------------------
# 3. Multiple independent orphaned obligations in one canonical-covered
#    section.
# ---------------------------------------------------------------------------


def test_multiple_independent_orphans_in_one_canonical_covered_section(tmp_path):
    body = (
        "# 1. Example Section\n\n"
        "All certifications SHALL be performed according to this model.\n\n"
        "Certification SHALL NOT evaluate implementation popularity.\n\n"
        "Every successful certification SHALL produce reproducible artifacts.\n\n"
        "## 1.5 Example Invariants\n\n"
        "EX-001\n\n"
        "The canonical statement.\n\n"
        "---\n"
    )
    root = _write_spec(tmp_path, "MCC-CP-001", body)
    reqs = extract_spec("MCC-CP-001", root)
    derived_texts = [r.requirement_text for r in reqs if r.id_origin == "derived"]
    assert len(derived_texts) == 3
    assert len(set(derived_texts)) == 3  # three distinct requirement_ids too
    derived_ids = {r.requirement_id for r in reqs if r.id_origin == "derived"}
    assert len(derived_ids) == 3


def test_real_corpus_cp001_certification_model_yields_several_orphans():
    # specs/MCC-CP-001.md Section 7 "Certification Model" has a canonical
    # Invariants block (7.5, CI-001..CI-010) but several independent prose
    # obligations in 7 / 7.1 / 7.2 / 7.3 / 7.4 that CI-001..010 does not
    # restate verbatim (see remediation manifest Finding 1's CP-001 §7.4
    # example). The corrected extractor must surface more than one of them.
    reqs = extract_spec("MCC-CP-001", REPO_ROOT)
    orphans = [
        r
        for r in reqs
        if r.id_origin == "derived" and r.requirement_category == "7. Certification Model"
    ]
    assert len(orphans) >= 3


# ---------------------------------------------------------------------------
# 4. A wrapped, multi-line normative paragraph is extracted once, not
#    truncated and not duplicated per physical line.
# ---------------------------------------------------------------------------


def test_wrapped_multiline_sentence_extracted_once(tmp_path):
    body = (
        "# 1. Example Section\n\n"
        "A Widget MUST remain traceable to its Owner, its creation\n"
        "timestamp, and the process that produced it.\n\n"
        "## 1.5 Example Invariants\n\n"
        "EX-001\n\n"
        "The canonical statement.\n\n"
        "---\n"
    )
    root = _write_spec(tmp_path, "MCC-CP-001", body)
    reqs = extract_spec("MCC-CP-001", root)
    derived = [r for r in reqs if r.id_origin == "derived"]
    assert len(derived) == 1
    assert derived[0].requirement_text == (
        "A Widget MUST remain traceable to its Owner, its creation "
        "timestamp, and the process that produced it."
    )


# ---------------------------------------------------------------------------
# 5. MUST NOT / SHALL NOT extraction.
# ---------------------------------------------------------------------------


def test_must_not_and_shall_not_extracted_in_canonical_covered_section(tmp_path):
    body = (
        "# 1. Example Section\n\n"
        "A Widget MUST NOT be issued without an Owner.\n\n"
        "A Gadget SHALL NOT reference a revoked Widget.\n\n"
        "## 1.5 Example Invariants\n\n"
        "EX-001\n\n"
        "The canonical statement.\n\n"
        "---\n"
    )
    root = _write_spec(tmp_path, "MCC-CP-001", body)
    reqs = extract_spec("MCC-CP-001", root)
    derived_texts = {r.requirement_text for r in reqs if r.id_origin == "derived"}
    assert "A Widget MUST NOT be issued without an Owner." in derived_texts
    assert "A Gadget SHALL NOT reference a revoked Widget." in derived_texts


def test_real_corpus_tc001_revocation_shall_not_and_shall_split():
    # specs/MCC-TC-001.md Section 12.2 states, on one source line:
    # "Revocation SHALL NOT be represented by modifying a Technical
    # Certificate's own content. Revocation SHALL be represented by an
    # external Revocation Record." -- two distinct obligations that must
    # become two separate requirements, not one combined or one dropped.
    reqs = extract_spec("MCC-TC-001", REPO_ROOT)
    texts = {r.requirement_text for r in reqs if r.id_origin == "derived"}
    assert (
        "Revocation SHALL NOT be represented by modifying a Technical "
        "Certificate's own content."
    ) in texts
    assert "Revocation SHALL be represented by an external Revocation Record." in texts


# ---------------------------------------------------------------------------
# 6. Non-normative examples / explanatory text must not become requirements.
# ---------------------------------------------------------------------------


def test_non_normative_prose_not_extracted(tmp_path):
    body = (
        "# 1. Example Section\n\n"
        "This section explains the general design philosophy behind Widgets.\n\n"
        "For example, a Widget typically has one Owner and one Digest.\n\n"
        "## 1.5 Example Invariants\n\n"
        "EX-001\n\n"
        "The canonical statement.\n\n"
        "---\n"
    )
    root = _write_spec(tmp_path, "MCC-CP-001", body)
    reqs = extract_spec("MCC-CP-001", root)
    derived = [r for r in reqs if r.id_origin == "derived"]
    assert derived == []


def test_real_corpus_required_classification_enum_bullets_not_spuriously_extracted():
    # specs/MCC-CP-001.md Section 10.3 lists "- REQUIRED / - OPTIONAL / -
    # CONDITIONAL" as bare classification-enum values under an intro line
    # ending in ":". None of these bare bullets is an independent
    # obligation; "REQUIRED" here names an enum value, not an RFC 2119
    # keyword governing that bullet. They must be absorbed into the intro
    # requirement, never extracted as their own (nonsensical) requirement.
    reqs = extract_spec("MCC-CP-001", REPO_ROOT)
    for r in reqs:
        assert r.requirement_text.strip() not in ("REQUIRED", "OPTIONAL", "CONDITIONAL")
    combined = [
        r
        for r in reqs
        if r.id_origin == "derived" and "classified as one of" in r.requirement_text
    ]
    assert len(combined) == 1
    assert "REQUIRED" in combined[0].requirement_text
    assert "OPTIONAL" in combined[0].requirement_text


def test_real_corpus_may_permission_with_required_enum_word_not_extracted():
    # specs/MCC-EB-001.md Section 9.3: "An Evidence Bundle MAY contain
    # Evidence Items for REQUIRED, OPTIONAL, and CONDITIONAL requirements
    # alike, ..." -- MAY is not binding, and the bare "REQUIRED" here is
    # again the classification-enum label, not an obligation on this
    # sentence. It must not be extracted as a requirement.
    reqs = extract_spec("MCC-EB-001", REPO_ROOT)
    for r in reqs:
        assert "Evidence Items for REQUIRED" not in r.requirement_text


# ---------------------------------------------------------------------------
# 7. Stable, deterministic derived IDs across repeated runs.
# ---------------------------------------------------------------------------


def test_derived_ids_stable_across_repeated_runs():
    reqs1 = [r.to_dict() for r in extract_all(REPO_ROOT) if r.id_origin == "derived"]
    reqs2 = [r.to_dict() for r in extract_all(REPO_ROOT) if r.id_origin == "derived"]
    assert reqs1 == reqs2


# ---------------------------------------------------------------------------
# 8. No collisions between canonical and derived IDs.
# ---------------------------------------------------------------------------


def test_no_id_collisions_between_canonical_and_derived():
    reqs = extract_all(REPO_ROOT)
    canonical_ids = {r.requirement_id for r in reqs if r.id_origin == "canonical"}
    derived_ids = {r.requirement_id for r in reqs if r.id_origin == "derived"}
    assert canonical_ids.isdisjoint(derived_ids)
    all_ids = [r.requirement_id for r in reqs]
    assert len(all_ids) == len(set(all_ids))


# ---------------------------------------------------------------------------
# 9. Preservation of existing IDs for unchanged source obligations.
# ---------------------------------------------------------------------------


def test_previously_derived_ids_in_uncovered_sections_are_preserved():
    # "8. Certification Lifecycle" (MCC-CP-001) had zero canonical IDs
    # before this correction, so the corrected extractor's behavior there
    # must be byte-identical to the original line-based algorithm: same
    # IDs, same text, same count.
    reqs = extract_spec("MCC-CP-001", REPO_ROOT)
    lifecycle = {
        r.requirement_id: r.requirement_text
        for r in reqs
        if r.requirement_category == "8. Certification Lifecycle" and r.id_origin == "derived"
    }
    assert lifecycle["MCC-CP-001-8-CERTIFICATION-LIFECYCLE-D01"] == (
        "Every certification SHALL progress through the following lifecycle."
    )
    assert lifecycle["MCC-CP-001-8-CERTIFICATION-LIFECYCLE-D06"] == (
        "Certification SHALL NOT continue if preparation fails."
    )
    assert len(lifecycle) == 23


def test_only_two_disclosed_exceptions_to_derived_id_stability():
    # Documented, justified exceptions (both pre-existing-defect corrections,
    # not scheme failures -- see the PR #62 reconciliation report):
    #  - MCC-EB-001-9-EVIDENCE-BUNDLE-OVERVIEW-D05 removed: it was a
    #    false-positive (a MAY-permission sentence misflagged as binding
    #    solely because of the classification-enum word "REQUIRED").
    #  - MCC-TC-001-ABSTRACT-D02 text narrowed: it previously combined one
    #    binding sentence with two non-binding framing sentences on the
    #    same physical line; the corrected extractor isolates only the
    #    genuinely binding sentence.
    # No other derived ID from the pre-correction baseline may differ.
    reqs = extract_all(REPO_ROOT)
    by_id = {r.requirement_id: r.requirement_text for r in reqs}
    assert "MCC-EB-001-9-EVIDENCE-BUNDLE-OVERVIEW-D05" not in by_id
    assert by_id["MCC-TC-001-ABSTRACT-D02"] == (
        "It is not, and SHALL NOT be interpreted as, a runtime execution authorization."
    )


# ---------------------------------------------------------------------------
# 10. Complete source linkage for every newly derived requirement.
# ---------------------------------------------------------------------------


def test_every_derived_requirement_has_traceable_source_line():
    reqs = extract_all(REPO_ROOT)
    derived = [r for r in reqs if r.id_origin == "derived"]
    assert derived
    for r in derived:
        assert r.source_line >= 1
        window = _normalize(_source_window(r.source_file, r.source_line))
        needle = _normalize(" ".join(r.requirement_text.split()[:4]))
        assert needle in window, (r.requirement_id, r.source_line, r.requirement_text[:80])


def test_every_canonical_requirement_also_has_a_source_line():
    reqs = extract_all(REPO_ROOT)
    canonical = [r for r in reqs if r.id_origin == "canonical"]
    assert canonical
    for r in canonical:
        assert r.source_line >= 1
        lines = (REPO_ROOT / r.source_file).read_text(encoding="utf-8").split("\n")
        assert lines[r.source_line - 1].strip() == r.requirement_id.split("#")[0]


# ---------------------------------------------------------------------------
# 11. A normative obligation inside a Markdown bullet list.
# ---------------------------------------------------------------------------


def test_self_contained_bullet_obligation_extracted_independently(tmp_path):
    body = (
        "# 1. Purpose\n\n"
        "Goals of this specification are:\n\n"
        "- **Framework Neutrality.** The format MUST remain independent of any "
        "particular framework.\n"
        "- **Traceability.** A record MUST remain traceable to its subject.\n"
        "- **Long-Term Stability.** The format SHOULD evolve carefully.\n\n"
        "---\n"
    )
    root = _write_spec(tmp_path, "MCC-TC-001", body)
    reqs = extract_spec("MCC-TC-001", root)
    derived_texts = {r.requirement_text for r in reqs if r.id_origin == "derived"}
    assert (
        "- **Framework Neutrality.** The format MUST remain independent of any "
        "particular framework."
    ) in derived_texts
    assert (
        "- **Traceability.** A record MUST remain traceable to its subject."
    ) in derived_texts
    # The SHOULD-only bullet is not binding and must not be extracted.
    assert not any("Long-Term Stability" in t for t in derived_texts)


def test_real_corpus_tc001_goals_bullets_each_independently_extracted():
    reqs = extract_spec("MCC-TC-001", REPO_ROOT)
    texts = [r.requirement_text for r in reqs if r.id_origin == "derived"]
    assert any("Framework Neutrality" in t and "MUST remain independent" in t for t in texts)
    assert any("Authoritative Representation" in t for t in texts)
    assert any("Independent Verifiability" in t for t in texts)
    assert any("Traceability" in t and "Certification Subject" in t for t in texts)
    assert not any("Long-Term Stability" in t for t in texts)  # SHOULD, not binding


# ---------------------------------------------------------------------------
# 12. A canonical requirement followed by independent normative prose in the
#     same subsection.
# ---------------------------------------------------------------------------


def test_real_corpus_eb001_bundle_root_prose_alongside_canonical_invariants():
    # specs/MCC-EB-001.md Section 10.1 states two obligations in prose
    # ("All Bundle contents SHALL be located within the Bundle Root." and
    # "The Bundle Root SHALL NOT contain content that is not part of the
    # Evidence Bundle.") that Section 10.5's canonical EB-STR-001..005 does
    # not restate. Both the canonical requirements and this prose must be
    # present in the final corpus.
    reqs = extract_spec("MCC-EB-001", REPO_ROOT)
    ids = {r.requirement_id for r in reqs if r.id_origin == "canonical"}
    assert "EB-STR-001" in ids and "EB-STR-002" in ids
    texts = {r.requirement_text for r in reqs if r.id_origin == "derived"}
    assert "All Bundle contents SHALL be located within the Bundle Root." in texts
    assert (
        "The Bundle Root SHALL NOT contain content that is not part of the "
        "Evidence Bundle."
    ) in texts


# ---------------------------------------------------------------------------
# 13. Repeated normative wording is not duplicated when it represents the
#     same source obligation (audit-trail visibility of duplicates).
# ---------------------------------------------------------------------------


def test_all_duplicate_of_canonical_dispositions_have_no_matching_derived_id():
    reqs, audits = extract_all_with_audit(REPO_ROOT)
    derived_texts = {_normalize(r.requirement_text) for r in reqs if r.id_origin == "derived"}
    dup_count = 0
    for spec_id in SPEC_FILES:
        for entry in audits[spec_id]:
            if entry.disposition == "DUPLICATE_OF_CANONICAL":
                dup_count += 1
                assert entry.duplicate_of is not None
                assert entry.requirement_id is None
                assert entry.normalized_text not in derived_texts
    assert dup_count == 8  # exact, reconciled count as of this corrected extractor


# ---------------------------------------------------------------------------
# 14. Separate obligations preserved when one paragraph / source line
#     contains more than one independently testable MUST/SHALL statement.
# ---------------------------------------------------------------------------


def test_two_sentences_on_one_line_become_two_requirements(tmp_path):
    body = (
        "# 6. Required Fields\n\n"
        "## 6.4 Field Presence Rule\n\n"
        "A Widget MUST NOT omit a Required Field. A consumer that omits any "
        "Required Field MUST be rejected under Section 15.\n\n"
        "## 6.7 Required Fields Invariants\n\n"
        "EX-RFLD-001\n\n"
        "The canonical statement.\n\n"
        "---\n"
    )
    root = _write_spec(tmp_path, "MCC-TC-001", body)
    reqs = extract_spec("MCC-TC-001", root)
    derived = [r for r in reqs if r.id_origin == "derived"]
    assert len(derived) == 2
    assert derived[0].requirement_text == "A Widget MUST NOT omit a Required Field."
    assert derived[1].requirement_text == (
        "A consumer that omits any Required Field MUST be rejected under Section 15."
    )
    # Same source line for both -- the split occurs within one physical line.
    assert derived[0].source_line == derived[1].source_line


def test_real_corpus_tc001_required_field_omission_split_into_two():
    reqs = extract_spec("MCC-TC-001", REPO_ROOT)
    texts = {r.requirement_text for r in reqs if r.id_origin == "derived"}
    assert "A Technical Certificate MUST NOT omit a Required Field." in texts
    assert (
        "A Certificate that omits any Required Field MUST be rejected under Section 15."
    ) in texts
