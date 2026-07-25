"""Deterministic reconciliation of every previously-orphaned normative source
line against the corrected extractor (src/mcc_conformance/extract.py).

"Previously orphaned" means: a MUST/MUST NOT/SHALL/SHALL NOT/REQUIRED-bearing
source line inside an H1 section that already contained at least one
canonical requirement ID elsewhere. The original extractor silently dropped
every such line (documented as Finding 1 in
conformance/normative-v1.0/remediation/wave-1-execution-boundary-scope-manifest.md,
391 lines across the four specifications). This module does not re-derive
that population from scratch; it reports, for the corrected extractor's own
internal accounting, the disposition of every candidate line it considered
within a canonical-requirement-bearing H1 section — which is exactly that
previously-orphaned population, plus the reconciled outcome for each one:

- ``EXTRACTED``: became a new derived requirement (requirement_id set).
- ``DUPLICATE_OF_CANONICAL``: verbatim-identical, after whitespace
  normalization, to a canonical requirement already in the same section
  (duplicate_of set to that canonical ID) — not extracted again.
- ``DUPLICATE_WITHIN_DERIVED``: verbatim-identical to another derived
  requirement already extracted earlier in the same section in this same
  pass (duplicate_of set to that derived ID).

Lines that are part of an enumerated field/value list (e.g. "- REQUIRED" as
one of three classification-enum values, or a bullet enumerating a
required field) are consolidated into the ONE requirement their
list-introducing line produced; they are not independently "orphaned"
normative statements (they carry no obligation of their own) and so do not
appear as their own audit entries, consistent with how the specifications'
own canonical Required-Fields-style sections state one requirement with an
enumerated field list.
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import List

from mcc_conformance.extract import SPEC_FILES, CoverageAuditEntry, extract_all_with_audit

OUT_DIR = Path("conformance/normative-v1.0")

_DISPOSITIONS = ("EXTRACTED", "DUPLICATE_OF_CANONICAL", "DUPLICATE_WITHIN_DERIVED")


def build_audit_entries(repo_root: Path) -> List[CoverageAuditEntry]:
    """Every audit entry from a canonical-requirement-bearing H1 section
    (the previously-orphaned population), across all four specifications, in
    deterministic (spec, then source line) order."""
    _, audits = extract_all_with_audit(repo_root)

    # Which H1 categories, per spec, contain at least one canonical
    # requirement -- the scope this audit reconciles.
    all_reqs, _ = extract_all_with_audit(repo_root)
    canonical_categories = {
        spec_id: {
            r.requirement_category
            for r in all_reqs
            if r.specification_id == spec_id and r.id_origin == "canonical"
        }
        for spec_id in SPEC_FILES
    }

    entries: List[CoverageAuditEntry] = []
    for spec_id in SPEC_FILES:  # deterministic spec order
        spec_entries = [
            e for e in audits[spec_id] if e.category in canonical_categories[spec_id]
        ]
        spec_entries.sort(key=lambda e: (e.source_line, e.normalized_text))
        entries.extend(spec_entries)
    return entries


def _audit_json(entries: List[CoverageAuditEntry]) -> str:
    payload = {
        "schema": "schemas/coverage_audit.schema.json",
        "entry_count": len(entries),
        "disposition_totals": dict(
            sorted(Counter(e.disposition for e in entries).items())
        ),
        "entries": [e.to_dict() for e in entries],
    }
    return json.dumps(payload, indent=2) + "\n"


def _audit_md(entries: List[CoverageAuditEntry]) -> str:
    counts = Counter(e.disposition for e in entries)
    by_spec = Counter(e.specification_id for e in entries)
    lines = [
        "# MCC Normative v1.0 — Extraction Coverage Audit",
        "",
        "Auto-generated. Do not hand-edit — regenerate with:",
        "",
        "```",
        "python -m mcc_conformance generate",
        "```",
        "",
        "Reconciles every normative-looking (MUST/MUST NOT/SHALL/SHALL "
        "NOT/REQUIRED) source line previously silently dropped by the "
        "extractor because its H1 section already contained a canonical "
        "requirement ID elsewhere, against its disposition under the "
        "corrected extractor "
        "(`src/mcc_conformance/extract.py`). See "
        "`conformance/normative-v1.0/remediation/`"
        "`wave-1-execution-boundary-scope-manifest.md` (Finding 1) for how "
        "this defect was discovered, and "
        "`conformance/normative-v1.0/README.md` for the resulting coverage "
        "semantics.",
        "",
        "## Disposition totals",
        "",
        "| Disposition | Count |",
        "|---|---|",
    ]
    for disp in _DISPOSITIONS:
        lines.append(f"| {disp} | {counts.get(disp, 0)} |")
    lines.append(f"| **Total** | **{len(entries)}** |")
    lines.append("")
    lines.append("## Totals by specification")
    lines.append("")
    lines.append("| Specification | Entries |")
    lines.append("|---|---|")
    for spec_id in SPEC_FILES:
        lines.append(f"| {spec_id} | {by_spec.get(spec_id, 0)} |")
    lines.append("")
    lines.append("## Full audit trail")
    lines.append("")
    lines.append(
        "| Spec | Line | Disposition | Requirement ID | Duplicate of | Normalized text |"
    )
    lines.append("|---|---|---|---|---|---|")
    for e in entries:
        text = e.normalized_text.replace("|", "\\|")
        if len(text) > 90:
            text = text[:87] + "..."
        lines.append(
            f"| {e.specification_id} | {e.source_line} | {e.disposition} | "
            f"{e.requirement_id or '—'} | {e.duplicate_of or '—'} | {text} |"
        )
    lines.append("")
    return "\n".join(lines) + "\n"


def generate_audit(repo_root: Path) -> None:
    entries = build_audit_entries(repo_root)
    out = repo_root / OUT_DIR
    out.mkdir(parents=True, exist_ok=True)
    (out / "extraction_coverage_audit.json").write_text(
        _audit_json(entries), encoding="utf-8"
    )
    (out / "extraction_coverage_audit.md").write_text(
        _audit_md(entries), encoding="utf-8"
    )
