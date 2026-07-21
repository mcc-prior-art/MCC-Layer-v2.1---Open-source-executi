"""Deterministic JSON + human-readable Markdown reports, and the certification
manifest.

Reports never contain secrets, tokens, authorization material, private keys, or
absolute filesystem paths — the runner only ever records vector ids, stable codes,
verdicts, and counts. The JSON body is stable (sorted keys); only the informational
``generated_at`` timestamp varies between runs and it is excluded from the
fingerprint.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from .models import CaseResult, CaseStatus, CertificationStatus
from .runner import ComplianceReport

_CERT_DISCLAIMER = (
    "Certification applies ONLY to the exact adapter version and contract version "
    "tested. It does not certify downstream application code, does not certify a "
    "framework as a whole, and does not replace a production security review. It is "
    "fail-closed: every mandatory vector must pass. The percentage is informational."
)


def report_to_json(report: ComplianceReport) -> Dict[str, Any]:
    """The full machine-readable report body (deterministic + generated_at)."""
    body = report.stable_dict()
    body["generated_at"] = report.generated_at
    body["disclaimer"] = _CERT_DISCLAIMER
    return body


def certification_manifest(report: ComplianceReport) -> Dict[str, Any]:
    """A focused certification record."""
    m = report.adapter_metadata
    cert = report.certification
    return {
        "report_schema_version": report.report_schema_version,
        "adapter_name": m.name,
        "adapter_version": m.version,
        "adapter_implementation_id": m.implementation_id,
        "target_framework": m.framework,
        "claimed_contract_version": m.claimed_contract_version,
        "certified_contract_version": (
            report.contract_version if cert.status is CertificationStatus.CERTIFIED else None),
        "compliance_suite_version": report.suite_version,
        "vector_manifest_digest": report.vector_manifest_digest,
        "certification_status": cert.status.value,
        "certification_fingerprint": cert.fingerprint,
        "totals": report.totals.to_dict(),
        "informational_pass_percentage": cert.informational_pass_percentage,
        "generated_at": report.generated_at,
        "disclaimer": _CERT_DISCLAIMER,
    }


def report_to_markdown(report: ComplianceReport) -> str:
    m = report.adapter_metadata
    cert = report.certification
    t = report.totals
    lines = [
        f"# MCC-Core Integration Contract Compliance — {m.name}",
        "",
        f"- **Adapter:** `{m.name}` v`{m.version}` (`{m.implementation_id}`)",
        f"- **Target framework:** {m.framework or '—'}",
        f"- **Contract version:** `{report.contract_version}` "
        f"(adapter claims `{m.claimed_contract_version}`)",
        f"- **Compliance suite version:** `{report.suite_version}`",
        f"- **Certification status:** **{cert.status.value}**",
        f"- **Vector manifest digest:** `{report.vector_manifest_digest or '—'}`",
        f"- **Certification fingerprint:** `{cert.fingerprint}`",
        "",
        "## Totals",
        "",
        "| total | passed | failed | errored | skipped | mandatory passed |",
        "|------:|-------:|-------:|--------:|--------:|-----------------:|",
        f"| {t.total} | {t.passed} | {t.failed} | {t.errored} | {t.skipped} | "
        f"{t.mandatory_passed}/{t.mandatory_total} |",
        "",
        f"Informational pass rate: {cert.informational_pass_percentage}% "
        f"(does not control certification).",
        "",
    ]

    failed = [r for r in report.results if r.status is CaseStatus.FAIL]
    errored = [r for r in report.results if r.status is CaseStatus.ERROR]
    skipped = [r for r in report.results if r.status is CaseStatus.SKIP]

    def _section(title: str, rows: List[CaseResult]) -> None:
        lines.append(f"## {title} ({len(rows)})")
        lines.append("")
        if not rows:
            lines.append("_none_")
            lines.append("")
            return
        lines.append("| vector | invariant | code | explanation |")
        lines.append("|--------|-----------|------|-------------|")
        for r in rows:
            lines.append(f"| `{r.vector_id}` | `{r.invariant}` | "
                         f"`{r.failure_code or '—'}` | {r.failure_explanation or ''} |")
        lines.append("")

    _section("Failed cases", failed)
    _section("Errored cases", errored)
    _section("Skipped cases", skipped)

    if cert.reasons:
        lines.append("## Decision reasons")
        lines.append("")
        for reason in cert.reasons:
            lines.append(f"- {reason}")
        lines.append("")

    lines.append("---")
    lines.append("")
    lines.append(f"> {_CERT_DISCLAIMER}")
    lines.append("")
    return "\n".join(lines)


def write_reports(report: ComplianceReport, output_dir: str) -> Dict[str, str]:
    """Write report.json, report.md, and certification.json under
    ``<output_dir>/<adapter>/<contract-version>/``. Returns the written paths."""
    m = report.adapter_metadata
    dest = Path(output_dir) / m.name / report.contract_version
    dest.mkdir(parents=True, exist_ok=True)

    json_path = dest / "report.json"
    md_path = dest / "report.md"
    cert_path = dest / "certification.json"

    json_path.write_text(json.dumps(report_to_json(report), indent=2, sort_keys=True) + "\n",
                         encoding="utf-8")
    cert_path.write_text(json.dumps(certification_manifest(report), indent=2, sort_keys=True) + "\n",
                         encoding="utf-8")
    md_path.write_text(report_to_markdown(report), encoding="utf-8")
    return {"json": str(json_path), "markdown": str(md_path), "certification": str(cert_path)}


__all__ = ["report_to_json", "certification_manifest", "report_to_markdown", "write_reports"]
