"""Operator abstraction for the ESCALATE (human authorization) flow.

When MCC-Core returns ``ESCALATE``, the agent pauses and asks an operator. The
operator's only power is to *decide* — approve or reject the pending request. It
never executes; the governed execution still runs through the SDK afterwards, and
only a valid, single-use operator mandate lets it proceed.

Two operators ship:

* :class:`ProgrammaticOperator` — a fixed approve/reject decision, for tests and
  headless demos.
* :class:`CLIOperator` — prompts a human at the terminal.

Neither operator signs anything or calls an external system.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Optional, Protocol, runtime_checkable


@dataclass(frozen=True)
class ApprovalRequest:
    """The context an operator needs to decide on a paused ESCALATE action."""

    request_id: str
    actor_id: str
    action: str
    resource: Optional[str]
    reason: str

    def summary(self) -> str:
        where = f" on {self.resource}" if self.resource else ""
        return (f"approval {self.request_id}: {self.actor_id} wants to "
                f"{self.action}{where} — {self.reason or 'human authorization required'}")


@runtime_checkable
class Operator(Protocol):
    """Decide whether a paused, escalated action may proceed."""

    def decide(self, request: ApprovalRequest) -> bool: ...


class ProgrammaticOperator:
    """A deterministic operator: always approve, or always reject.

    For tests and headless demos. The decision is fixed at construction so a run
    is fully reproducible."""

    def __init__(self, *, approve: bool = True) -> None:
        self._approve = approve
        self.decisions: list[ApprovalRequest] = []

    def decide(self, request: ApprovalRequest) -> bool:
        self.decisions.append(request)
        return self._approve


class CLIOperator:
    """Prompt a human operator at the terminal (demo use).

    Falls back to *reject* on EOF / non-interactive input — fail-closed: absence
    of an explicit approval is not approval."""

    def __init__(self, *, prompt: Callable[[str], str] = input,
                 out: Callable[[str], Any] = print) -> None:
        self._prompt = prompt
        self._out = out

    def decide(self, request: ApprovalRequest) -> bool:
        self._out(f"\n[OPERATOR] {request.summary()}")
        try:
            answer = self._prompt("[OPERATOR] approve this action? [y/N] ")
        except (EOFError, KeyboardInterrupt):
            self._out("[OPERATOR] no input — rejecting (fail-closed).")
            return False
        return str(answer).strip().lower() in ("y", "yes")


__all__ = ["ApprovalRequest", "Operator", "ProgrammaticOperator", "CLIOperator"]
