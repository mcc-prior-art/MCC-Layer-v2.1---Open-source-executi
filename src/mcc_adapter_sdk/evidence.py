"""Deterministic Adapter SDK evidence (PR #50).

Produces a small, sanitized, reproducible evidence record for an adapter: its
metadata + digest, the SDK/protocol/contract versions, and (optionally) a summary
of one governed run and a structural-validation report. The record is deterministic
(stable ordering, no wall-clock, no random identifiers, no secrets) so generating it
twice yields byte-identical output.

SDK evidence is intentionally **distinct** from the future Compliance/Certification
evidence: it attests only that an adapter is structurally SDK-compatible and that a
request traversed the mandatory ingress path — never that it is certified, trusted,
or production-approved.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional

from mcc_client.contract import CONTRACT_VERSION
from mcc_protocol import PROTOCOL_VERSION

from ._version import SDK_VERSION
from .adapter import Adapter
from .runner import AdapterRunResult
from .validation import AdapterValidationReport

EVIDENCE_FORMAT = "mcc-adapter-sdk-evidence/1"
DEFAULT_DIR = "artifacts/adapter-sdk"

# Keys that must never appear anywhere in the evidence (sanitization guard).
_FORBIDDEN_SUBSTRINGS = ("api_key", "operator_key", "secret", "password",
                         "private", "-----begin", "authorization")


def _decision_summary(run_result: Optional[AdapterRunResult]) -> Optional[Dict[str, Any]]:
    if run_result is None or run_result.governance_decision is None:
        return None
    gd = run_result.governance_decision
    # Deterministic, token-free summary: no audit id, no timestamp, no token material.
    return {
        "verdict": gd.verdict.value,
        "reason_codes": list(gd.reason_codes),
        "applied_constraints": list(gd.applied_constraints),
        "has_decision_token": gd.has_decision_token,
        "executable": gd.executable,
        "policy_hash": gd.policy_hash,
    }


def _sanitize(evidence: Dict[str, Any]) -> None:
    text = json.dumps(evidence, sort_keys=True).lower()
    for bad in _FORBIDDEN_SUBSTRINGS:
        if bad in text:
            raise ValueError(f"refusing to emit evidence containing {bad!r}")


def generate_adapter_evidence(adapter: Adapter, *,
                              run_result: Optional[AdapterRunResult] = None,
                              validation_report: Optional[AdapterValidationReport] = None,
                              out_dir: Optional[str] = DEFAULT_DIR,
                              write: bool = True) -> Dict[str, Any]:
    """Build (and optionally write) deterministic, sanitized SDK evidence."""
    metadata = adapter.describe().validate()
    evidence: Dict[str, Any] = {
        "evidence_format": EVIDENCE_FORMAT,
        "sdk_version": SDK_VERSION,
        "protocol_version": PROTOCOL_VERSION,
        "contract_version": CONTRACT_VERSION,
        "adapter_metadata": metadata.to_dict(),
        "adapter_metadata_digest": metadata.digest(),
        "proposal_hash": run_result.proposal_hash if run_result else None,
        "pipeline_summary": dict(run_result.pipeline_summary) if run_result else None,
        "governance_decision_summary": _decision_summary(run_result),
        "validation": validation_report.to_dict() if validation_report else None,
        "note": ("Adapter SDK evidence — structural + ingress-traversal only. "
                 "NOT certification, official compliance, or production approval; "
                 "distinct from the Compliance & Certification evidence."),
    }
    _sanitize(evidence)
    if write and out_dir is not None:
        path = Path(out_dir)
        path.mkdir(parents=True, exist_ok=True)
        (path / f"adapter_sdk_evidence_{metadata.adapter_id}.json").write_text(
            json.dumps(evidence, indent=2, sort_keys=True), encoding="utf-8")
    return evidence


__all__ = ["generate_adapter_evidence", "EVIDENCE_FORMAT", "DEFAULT_DIR"]
