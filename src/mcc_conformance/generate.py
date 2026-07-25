"""Deterministic generation of the Normative v1.0 conformance artifacts.

Given only the four specification files at a fixed baseline commit, this
module always produces byte-identical output: no wall-clock timestamps,
random IDs, or unordered collections are used anywhere in the generated
artifacts.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import List

from mcc_conformance.assess import assess
from mcc_conformance.extract import SPEC_FILES, extract_all
from mcc_conformance.models import Requirement

BASELINE = {
    "release_title": "MCC Specification Program — Normative v1.0",
    "tag": "mcc-spec-v1.0.0",
    "baseline_commit": "a65b2f375408dfbe8df86fbfc09724c5c45d3ba4",
    "declaration_status": "Normative",
    "final_disposition": "APPROVE FOR NORMATIVE v1.0",
    "declaration_document": "docs/MCC_SPECIFICATION_PROGRAM_NORMATIVE_V1_0.md",
    "review_document": "docs/reviews/MCC_SPECIFICATION_PROGRAM_NORMATIVE_V1_REVIEW.md",
    "specifications": [
        {
            "specification_id": spec_id,
            "source_file": source_file,
            "version": "1.0",
            "status": "Normative",
        }
        for spec_id, source_file in SPEC_FILES.items()
    ],
    "generated_at_note": (
        "This record carries no wall-clock timestamp so that generation "
        "remains byte-for-byte deterministic. Provenance is anchored to "
        "baseline_commit and tag above, not to generation time."
    ),
}

OUT_DIR = Path("conformance/normative-v1.0")


def build_requirements(repo_root: Path) -> List[Requirement]:
    reqs = assess(extract_all(repo_root))
    reqs.sort(key=lambda r: (r.specification_id, r.requirement_id))
    return reqs


def _requirements_json(reqs: List[Requirement]) -> str:
    payload = {
        "schema": "schemas/requirement.schema.json",
        "requirement_count": len(reqs),
        "requirements": [r.to_dict() for r in reqs],
    }
    return json.dumps(payload, indent=2, sort_keys=False) + "\n"

def _baseline_json() -> str:
    return json.dumps(BASELINE, indent=2, sort_keys=False) + "\n"


def _matrix_json(reqs: List[Requirement]) -> str:
    rows = []
    for r in reqs:
        rows.append(
            {
                "requirement_id": r.requirement_id,
                "specification_id": r.specification_id,
                "section": r.section,
                "conformance_status": r.conformance_status,
                "implementation_references": r.implementation_references,
                "test_references": r.test_references,
                "evidence_references": r.evidence_references,
            }
        )
    return json.dumps({"schema": "schemas/requirement.schema.json", "matrix": rows}, indent=2) + "\n"


def _status_counts(reqs: List[Requirement]):
    from collections import Counter

    return Counter(r.conformance_status for r in reqs)


def _matrix_md(reqs: List[Requirement]) -> str:
    lines = [
        "# MCC Normative v1.0 — Implementation Traceability Matrix",
        "",
        "Auto-generated. Do not hand-edit — regenerate with:",
        "",
        "```",
        "python -m mcc_conformance generate",
        "```",
        "",
        "## Baseline Provenance",
        "",
        f"- Release: {BASELINE['release_title']}",
        f"- Tag: `{BASELINE['tag']}`",
        f"- Baseline commit: `{BASELINE['baseline_commit']}`",
        f"- Declaration: {BASELINE['declaration_document']}",
        f"- Review: {BASELINE['review_document']}",
        f"- Final disposition: {BASELINE['final_disposition']}",
        "",
        "## Totals by Specification",
        "",
        "| Specification | Requirements |",
        "|---|---|",
    ]
    from collections import Counter

    by_spec = Counter(r.specification_id for r in reqs)
    for spec_id in SPEC_FILES:
        lines.append(f"| {spec_id} | {by_spec.get(spec_id, 0)} |")
    lines.append(f"| **Total** | **{len(reqs)}** |")
    lines.append("")

    lines.append("## Totals by Conformance Status")
    lines.append("")
    lines.append("| Status | Count | % of total |")
    lines.append("|---|---|---|")
    counts = _status_counts(reqs)
    for status in ("CONFORMANT", "PARTIAL", "GAP", "NOT_APPLICABLE", "NOT_ASSESSED"):
        n = counts.get(status, 0)
        pct = (100.0 * n / len(reqs)) if reqs else 0.0
        lines.append(f"| {status} | {n} | {pct:.1f}% |")
    lines.append("")

    conformant = counts.get("CONFORMANT", 0)
    applicable = len(reqs) - counts.get("NOT_APPLICABLE", 0)
    coverage = (100.0 * conformant / applicable) if applicable else 0.0
    lines.append(
        f"**Conformance coverage (CONFORMANT / applicable requirements): "
        f"{coverage:.1f}% ({conformant}/{applicable})**"
    )
    lines.append("")

    lines.append("## Full Traceability Matrix")
    lines.append("")
    lines.append("| Requirement ID | Spec | Section | Status | Implementation | Tests |")
    lines.append("|---|---|---|---|---|---|")
    for r in reqs:
        impl = "; ".join(r.implementation_references) or "—"
        test = "; ".join(r.test_references) or "—"
        section = r.section.replace("|", "\\|")
        lines.append(
            f"| {r.requirement_id} | {r.specification_id} | {section} | "
            f"{r.conformance_status} | {impl} | {test} |"
        )
    lines.append("")

    lines.append("## Limitations of This Assessment")
    lines.append("")
    lines.append(
        "- Assessment was performed at requirement-category granularity, "
        "not as an independently bespoke code review of all "
        f"{len(reqs)} individual requirements. Requirements sharing a "
        "specification section and normative theme share a status and "
        "rationale unless repository evidence specifically distinguished "
        "them. This is disclosed, not hidden."
    )
    lines.append(
        "- No requirement is marked CONFORMANT in this baseline. That "
        "status requires both an implementation and a meaningful "
        "automated test tied to the specific requirement; as of the "
        "reviewed commit, no code in this repository implements the "
        "Evidence Bundle, Certification Manifest, Technical Certificate, "
        "or Certification Program process these specifications define."
    )
    lines.append(
        "- PARTIAL status is granted only for two narrow, independently "
        "verifiable primitives (deterministic canonical serialization / "
        "digest, and Ed25519-only / asymmetric-only signing) that exist and "
        "are tested for a different artifact (the runtime Decision Token) "
        "and are not wired to any Evidence Bundle, Manifest, or "
        "Certificate object."
    )
    lines.append(
        "- This assessment does not execute or validate any generated "
        "Evidence Bundle, Manifest, or Certificate, because none exist "
        "to generate. It is a static, source-level trace only."
    )
    lines.append("")
    lines.append("## Reproduction")
    lines.append("")
    lines.append("```")
    lines.append("python -m mcc_conformance generate")
    lines.append("python -m mcc_conformance validate")
    lines.append("pytest tests/test_conformance_baseline.py -v")
    lines.append("```")
    lines.append("")

    return "\n".join(lines) + "\n"


def _gap_report_md(reqs: List[Requirement]) -> str:
    non_conformant = [r for r in reqs if r.conformance_status != "CONFORMANT"]
    lines = [
        "# MCC Normative v1.0 — Gap Report",
        "",
        "Auto-generated. Do not hand-edit — regenerate with:",
        "",
        "```",
        "python -m mcc_conformance generate",
        "```",
        "",
        f"Total non-CONFORMANT requirements: {len(non_conformant)} of {len(reqs)}.",
        "",
    ]

    def scope_for(r: Requirement) -> str:
        if r.conformance_status == "PARTIAL":
            return "SMALL"
        if r.specification_id in ("MCC-EB-001", "MCC-CM-001", "MCC-TC-001"):
            return "LARGE"
        return "LARGE"

    def affects_public_interfaces(r: Requirement) -> str:
        if r.conformance_status == "NOT_APPLICABLE":
            return "N/A"
        return "Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected."

    for r in non_conformant:
        lines.append(f"## {r.requirement_id}")
        lines.append("")
        lines.append(f"- Specification / section: {r.specification_id} / {r.section}")
        lines.append(f"- Status: {r.conformance_status}")
        lines.append(f"- Requirement: {r.requirement_text}")
        lines.append(
            f"- Existing implementation: "
            f"{'; '.join(r.implementation_references) if r.implementation_references else 'None'}"
        )
        lines.append(
            f"- Missing implementation behavior: "
            f"{'Full requirement not implemented.' if r.conformance_status == 'GAP' else 'Not wired to the artifact this specification defines; see rationale.' if r.conformance_status == 'PARTIAL' else 'N/A (not an implementable requirement).'}"
        )
        lines.append(
            f"- Missing test coverage: "
            f"{'No test exists for this requirement.' if not r.test_references else 'Existing tests cover the reused primitive only, not this requirement directly.'}"
        )
        lines.append(
            f"- Missing evidence: "
            f"{'No generated evidence artifact exists for this requirement.' if r.conformance_status != 'NOT_APPLICABLE' else 'N/A'}"
        )
        lines.append(f"- Rationale: {r.rationale}")
        lines.append(f"- Recommended remediation scope: {scope_for(r)}")
        lines.append(f"- May affect public interfaces / governance semantics: {affects_public_interfaces(r)}")
        lines.append("")

    return "\n".join(lines) + "\n"


def generate(repo_root: Path) -> None:
    from mcc_conformance import coverage_audit

    reqs = build_requirements(repo_root)
    out = repo_root / OUT_DIR
    out.mkdir(parents=True, exist_ok=True)
    (out / "baseline.json").write_text(_baseline_json(), encoding="utf-8")
    (out / "requirements.json").write_text(_requirements_json(reqs), encoding="utf-8")
    (out / "traceability_matrix.json").write_text(_matrix_json(reqs), encoding="utf-8")
    (out / "traceability_matrix.md").write_text(_matrix_md(reqs), encoding="utf-8")
    (out / "gap_report.md").write_text(_gap_report_md(reqs), encoding="utf-8")
    coverage_audit.generate_audit(repo_root)
