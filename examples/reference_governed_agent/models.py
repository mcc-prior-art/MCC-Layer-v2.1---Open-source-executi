"""Typed models for the framework-neutral reference governed agent."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


class ProviderError(Exception):
    """A reasoning provider could not produce a proposal. This is NOT permission
    and never bypasses governance — the agent simply has no action to submit."""


@dataclass(frozen=True)
class ProposedAction:
    """A structured action proposal — the agent's intent, never authority."""

    action: str
    actor_id: str
    resource: str
    payload: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {"action": self.action, "actor_id": self.actor_id,
                "resource": self.resource, "payload": dict(self.payload)}


@dataclass(frozen=True)
class AgentRunResult:
    """The outcome of one governed agent run."""

    request: str
    proposal: Dict[str, Any]
    verdict: str                         # ALLOW / DENY / ESCALATE / CONSTRAIN / …
    reason: str
    execution_status: str                # EXECUTED / BLOCKED / PENDING_APPROVAL
    approval_status: Optional[str] = None
    final_payload: Optional[Dict[str, Any]] = None
    applied_constraints: List[str] = field(default_factory=list)
    receipt: Any = None                  # verified external receipt (safe summary)
    audit_valid: Optional[bool] = None
    error: Optional[str] = None

    @property
    def executed(self) -> bool:
        return self.execution_status == "EXECUTED"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "request": self.request, "proposal": self.proposal, "verdict": self.verdict,
            "reason": self.reason, "execution_status": self.execution_status,
            "approval_status": self.approval_status, "final_payload": self.final_payload,
            "applied_constraints": list(self.applied_constraints),
            "receipt": self.receipt, "audit_valid": self.audit_valid, "error": self.error,
        }
