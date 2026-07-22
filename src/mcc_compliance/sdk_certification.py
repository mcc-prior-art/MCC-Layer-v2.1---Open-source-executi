"""Adapter-SDK certification API + deterministic outputs (PR #51).

The stable, public entry point for certifying an ``mcc_adapter_sdk.Adapter`` through
the one Compliance & Certification Suite, with the Adapter SDK as the canonical
ingress. It reuses the existing certification engine end-to-end (``run_compliance`` →
golden vectors → ``certify_report`` → reporting) — it introduces **no** second
pipeline and mints **no** new certification model. Every output is deterministic and
reproducible: no wall-clock time, no random identifiers, no filesystem paths.

Outputs (written to a directory, or returned as documents):

* ``certification.json`` — the machine-readable certification (status, evidence
  digest, covered invariants, ordered scenario outcomes), schema-versioned.
* ``evidence.json`` — the deterministic compliance evidence bundle (``stable_dict``:
  per-scenario results + totals + vector-manifest digest).
* ``certification-report.md`` — the human-readable technical certification report.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Tuple

from mcc_adapter_sdk import Adapter

from .program import CertificationResult, certify_report
from .reporting import report_to_markdown
from .runner import ComplianceReport, run_compliance
from .sdk_bridge import SdkComplianceAdapter

#: Versioned schema for the certification document. Bump only on a breaking change.
SDK_CERTIFICATION_SCHEMA_VERSION = "1"

#: The canonical certification ingress for this suite.
CERTIFICATION_INGRESS = "adapter-sdk"

DEFAULT_DIR = "artifacts/certification"


def run_sdk_certification(sdk_adapter: Adapter, *,
                          contract_version: str) -> Tuple[CertificationResult, ComplianceReport]:
    """Run the official compliance evaluation for an SDK adapter (real governed
    stack, ground-truth cross-check, no wall-clock) and derive its certification.
    Deterministic for the same adapter, contract version, vectors, and evidence."""
    bridge = SdkComplianceAdapter(sdk_adapter)
    report = run_compliance(bridge, contract_version, include_timestamp=False)
    result = certify_report(report)
    return result, report


def certify_sdk_adapter(sdk_adapter: Adapter, *, contract_version: str) -> CertificationResult:
    """Stable certification API: certify an ``mcc_adapter_sdk.Adapter``."""
    result, _ = run_sdk_certification(sdk_adapter, contract_version=contract_version)
    return result


def certification_document(result: CertificationResult) -> Dict[str, Any]:
    """The deterministic ``certification.json`` body."""
    body = {
        "schema_version": SDK_CERTIFICATION_SCHEMA_VERSION,
        "certification_ingress": CERTIFICATION_INGRESS,
        "certification": result.manifest_entry(),
    }
    return body


def evidence_document(report: ComplianceReport) -> Dict[str, Any]:
    """The deterministic ``evidence.json`` body (no wall-clock, no random ids)."""
    return {
        "schema_version": SDK_CERTIFICATION_SCHEMA_VERSION,
        "certification_ingress": CERTIFICATION_INGRESS,
        "evidence": report.stable_dict(),
    }


def report_document(report: ComplianceReport) -> str:
    """The deterministic ``certification-report.md`` text."""
    return report_to_markdown(report)


def write_certification(sdk_adapter: Adapter, *, contract_version: str,
                        out_dir: str = DEFAULT_DIR) -> Dict[str, str]:
    """Certify an SDK adapter and write the three deterministic outputs. Returns the
    written paths. Running twice produces byte-identical files."""
    result, report = run_sdk_certification(sdk_adapter, contract_version=contract_version)
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    cert_path = out / "certification.json"
    ev_path = out / "evidence.json"
    rep_path = out / "certification-report.md"
    cert_path.write_text(
        json.dumps(certification_document(result), indent=2, sort_keys=True) + "\n",
        encoding="utf-8")
    ev_path.write_text(
        json.dumps(evidence_document(report), indent=2, sort_keys=True) + "\n",
        encoding="utf-8")
    rep_path.write_text(report_document(report), encoding="utf-8")
    return {"certification": str(cert_path), "evidence": str(ev_path),
            "report": str(rep_path)}


__all__ = [
    "SDK_CERTIFICATION_SCHEMA_VERSION", "CERTIFICATION_INGRESS",
    "run_sdk_certification", "certify_sdk_adapter", "certification_document",
    "evidence_document", "report_document", "write_certification",
]
