"""Typed models for the MCC-Core gateway protocol.

These mirror the authoritative server contract (``gateway/app.py`` ``/evaluate``
and the governed ``/…/execute`` endpoints). Critical enum values (the verdict)
are validated: an unknown verdict fails closed. The public API avoids loose
untyped dictionaries except for the action ``payload`` / ``context``, which is
legitimately arbitrary JSON.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Mapping, Optional

from .exceptions import MCCProtocolError

# JSON-compatible action payload.
Payload = Mapping[str, Any]


class Verdict(str, Enum):
    """The four canonical MCC-Core verdicts."""

    ALLOW = "ALLOW"
    DENY = "DENY"
    ESCALATE = "ESCALATE"
    CONSTRAIN = "CONSTRAIN"

    @classmethod
    def parse(cls, value: Any) -> "Verdict":
        """Parse a verdict, failing closed on anything unknown."""
        if not isinstance(value, str):
            raise MCCProtocolError(f"verdict is not a string: {value!r}")
        try:
            return cls(value)
        except ValueError as exc:
            raise MCCProtocolError(f"unknown verdict {value!r}; refusing to proceed") from exc


@dataclass(frozen=True)
class Decision:
    """The gateway's verdict for a proposed action (``POST /evaluate``).

    ``authorized_payload`` is the body the verdict authorizes: the original
    payload for ALLOW, the server-clamped payload for CONSTRAIN. It is the ONLY
    payload the SDK will execute — a caller cannot substitute it.
    """

    verdict: Verdict
    reason: str
    audit_id: str
    actor_id: str
    action: str
    resource_id: Optional[str]
    authorized_payload: Dict[str, Any]        # server ``forward_context``
    requested_payload: Dict[str, Any]         # the payload the caller proposed
    applied_constraints: List[str]
    constraints: Dict[str, Any]
    decision_token: Optional[Dict[str, Any]]
    authority_required: Optional[str]
    policy_ref: str
    correlation_id: str                        # server ``trace_id``
    transaction_id: Optional[str]
    idempotency_key: Optional[str]
    raw: Dict[str, Any] = field(default_factory=dict)

    # -- classification --

    @property
    def executable(self) -> bool:
        """ALLOW or CONSTRAIN — an authorized body exists (execution still must be
        performed explicitly, through the governed path, with authorization material)."""
        return self.verdict in (Verdict.ALLOW, Verdict.CONSTRAIN)

    @property
    def denied(self) -> bool:
        return self.verdict == Verdict.DENY

    @property
    def needs_approval(self) -> bool:
        return self.verdict == Verdict.ESCALATE

    @property
    def constrained(self) -> bool:
        return self.verdict == Verdict.CONSTRAIN

    # -- construction --

    @classmethod
    def from_response(cls, data: Any, *, requested_actor: str, requested_action: str,
                      requested_resource: Optional[str],
                      requested_payload: Optional[Dict[str, Any]] = None) -> "Decision":
        """Build (and validate) a Decision from a gateway response.

        Fails closed on a malformed body, a missing verdict, an unknown verdict,
        or a decision that cannot be bound to the requested actor/action."""
        if not isinstance(data, dict):
            raise MCCProtocolError("gateway response is not a JSON object")
        if "decision" not in data:
            raise MCCProtocolError("gateway response missing 'decision'")
        verdict = Verdict.parse(data.get("decision"))

        # Bind the decision to the requested action. The gateway echoes the
        # operation binding; if it names a different actor/action, refuse (a
        # decision must not be reinterpreted against a different action).
        echoed_actor = data.get("actor_id")
        echoed_action = data.get("action")  # may be absent in some responses
        if echoed_actor is not None and echoed_actor != requested_actor:
            raise MCCProtocolError(
                f"decision actor {echoed_actor!r} != requested {requested_actor!r}")
        if echoed_action is not None and echoed_action != requested_action:
            raise MCCProtocolError(
                f"decision action {echoed_action!r} != requested {requested_action!r}")

        fwd = data.get("forward_context")
        if fwd is None:
            fwd = {}
        if not isinstance(fwd, dict):
            raise MCCProtocolError("forward_context is not a JSON object")

        return cls(
            verdict=verdict,
            reason=str(data.get("reason", "")),
            audit_id=str(data.get("audit_id", "")),
            actor_id=requested_actor,
            action=requested_action,
            resource_id=requested_resource,
            authorized_payload=dict(fwd),
            requested_payload=dict(requested_payload or {}),
            applied_constraints=list(data.get("applied_constraints") or []),
            constraints=dict(data.get("constraints") or {}),
            decision_token=data.get("decision_token"),
            authority_required=data.get("authority_required"),
            policy_ref=str(data.get("policy_ref", "")),
            correlation_id=str(data.get("trace_id", "")),
            transaction_id=data.get("transaction_id"),
            idempotency_key=data.get("idempotency_key"),
            raw=data,
        )


@dataclass(frozen=True)
class Approval:
    """An approval request / grant (the ESCALATE flow)."""

    request_id: str
    state: str
    mandate: Optional[Dict[str, Any]] = None

    @property
    def granted(self) -> bool:
        return self.state.upper() in ("APPROVED", "GRANTED") and self.mandate is not None


@dataclass(frozen=True)
class ExecutionResult:
    """The result of a governed execution (a ``/…/execute`` endpoint)."""

    status: str                                # EXECUTED / BLOCKED / EXECUTION_FAILED
    reason: str
    decision: Optional[str] = None
    audit_ref: Optional[str] = None
    execution: Any = None
    raw: Dict[str, Any] = field(default_factory=dict)

    @property
    def executed(self) -> bool:
        return self.status == "EXECUTED"


# -- authorization material for explicit execution --

@dataclass(frozen=True)
class ApprovalAuthorization:
    """Authorize execution with an approved single-use mandate (ESCALATE path)."""

    request_id: str
    mandate: Dict[str, Any]


@dataclass(frozen=True)
class MandateAuthorization:
    """Authorize execution with a standing signed mandate."""

    mandate: Dict[str, Any]


@dataclass(frozen=True)
class ConsensusAuthorization:
    """Authorize execution with N-of-M evaluator votes bound to a challenge."""

    votes: List[Dict[str, Any]]
    challenge_id: Optional[str] = None
    nonce: Optional[str] = None


__all__ = [
    "Payload", "Verdict", "Decision", "Approval", "ExecutionResult",
    "ApprovalAuthorization", "MandateAuthorization", "ConsensusAuthorization",
]
