"""Audit-evidence generation for the reference governed agent (PR #43).

The final step of the integration contract — **Audit → portable evidence** — is
implemented by reusing the PR #42 Governance Evidence Bundle Core. This module is
a thin, observational adapter: it converts the public SDK objects the agent
already holds (a :class:`mcc_client.models.Decision` and its
:class:`mcc_client.models.ExecutionResult`) into an :class:`mcc_evidence.EvidenceInput`
and, optionally, exports a portable bundle.

It creates no authority, re-evaluates nothing, and calls no executor. The signed
decision token, the authorized payload and the verified receipt are packaged
exactly as governance produced them; a DENY / non-executed result never carries a
fabricated receipt (the evidence layer enforces this, fail-closed).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

from mcc_client.models import Decision, ExecutionResult

from mcc_evidence import EvidenceInput, export_bundle


def _receipt_of(result: Optional[ExecutionResult]) -> Optional[Dict[str, Any]]:
    if result is None or not result.executed:
        return None
    receipt = result.execution
    return dict(receipt) if isinstance(receipt, dict) else None


def agent_evidence(decision: Decision, result: Optional[ExecutionResult] = None) -> EvidenceInput:
    """Build an :class:`EvidenceInput` from a completed governed decision.

    Uses only client-visible artifacts: the signed ``decision.decision_token``,
    the authoritative payload (``decision.authorized_payload`` — the clamped body
    for CONSTRAIN), and the verified receipt from an EXECUTED result. The audit
    slice is a server-side concern and is intentionally omitted here (the bundle's
    audit section is optional); a server-side exporter can attach it. A non-ALLOW/
    CONSTRAIN or non-executed decision carries no token/receipt, so the bundle is
    denial/at-most-integrity evidence — never a fabricated execution.
    """
    verdict = decision.verdict.value if hasattr(decision.verdict, "value") else str(decision.verdict)
    executable = verdict in ("ALLOW", "CONSTRAIN")
    receipt = _receipt_of(result) if executable else None
    return EvidenceInput(
        verdict=verdict,
        actor_id=decision.actor_id,
        resource_id=decision.resource_id or "",
        action=decision.action,
        correlation_id=decision.correlation_id or None,
        decision_token=decision.decision_token if executable else None,
        proposal=dict(decision.authorized_payload) if executable else None,
        receipt=receipt,
        gate_result={"verdict": verdict, "executed": bool(receipt)},
        denial=None if executable else {"verdict": verdict, "reason": decision.reason},
    )


def export_agent_evidence(
    decision: Decision,
    result: Optional[ExecutionResult],
    dest: Path | str,
    *,
    archive: bool = False,
) -> Path:
    """Export a portable Governance Evidence Bundle for a completed decision.

    Thin wrapper over :func:`mcc_evidence.export_bundle`; fails closed on
    inconsistent evidence exactly as the evidence layer does.
    """
    return export_bundle(agent_evidence(decision, result), dest, archive=archive)


__all__ = ["agent_evidence", "export_agent_evidence"]
