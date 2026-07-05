"""The framework-neutral reference governed agent.

This is the canonical reference: a real agent that proposes an action, submits it
to MCC-Core through the supported SDK, obtains approval when required, and — only
when governance authorizes it — executes through the **governed** path and
verifies the external receipt and the audit chain.

It is deliberately framework-neutral: no VoltAgent, LangGraph, CrewAI, or agent
SDK anywhere in the loop. Any of those can integrate later as an adapter that
produces a proposal and hands it to this same SDK boundary.

Invariants this agent embodies:

* **Reasoning is not authority.** The provider only proposes; MCC decides.
* **Proposal is not permission.** Nothing runs without a governance decision.
* **No direct execution path.** The agent holds no HTTP/notification/socket
  client. Every side effect goes agent -> MCC SDK -> gateway -> governed
  executor -> external system. A provider or operator failure cannot bypass this.
* **Fail-closed.** Any error, denial, or missing authorization yields a
  non-executed result; the external service is never called.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from mcc_client import (
    Decision,
    MCCClient,
    MCCError,
    Verdict,
)

from .authorizers import ExecutionAuthorizer
from .models import AgentRunResult, ProviderError
from .operator import ApprovalRequest, Operator, ProgrammaticOperator
from .providers import DeterministicProvider, ReasoningProvider


class ReferenceGovernedAgent:
    """Propose -> evaluate -> (approve) -> governed execute -> verify.

    Wiring is injected: a reasoning ``provider`` (what to propose), an
    ``operator`` (the human authority for ESCALATE), and an optional
    ``authorizer`` (the authorization-material source for ALLOW/CONSTRAIN
    execution). The agent's only outward channel is the injected ``client`` — the
    MCC SDK. It never constructs a network client of its own.
    """

    def __init__(
        self,
        client: MCCClient,
        *,
        provider: Optional[ReasoningProvider] = None,
        operator: Optional[Operator] = None,
        authorizer: Optional[ExecutionAuthorizer] = None,
        verify_audit: bool = True,
    ) -> None:
        self._client = client
        self._provider: ReasoningProvider = provider or DeterministicProvider()
        self._operator: Operator = operator or ProgrammaticOperator(approve=True)
        self._authorizer = authorizer
        self._verify_audit = verify_audit

    # ------------------------------------------------------------------ #
    # Public entry point.                                                 #
    # ------------------------------------------------------------------ #

    def handle(self, request: str) -> AgentRunResult:
        """Run one full governed cycle for a natural-language request."""
        # 1. Reasoning: propose an action. A provider failure is NOT permission —
        #    the agent simply has no action to submit, and nothing executes.
        try:
            proposal = self._provider.propose(request)
        except ProviderError as exc:
            return AgentRunResult(
                request=request, proposal={}, verdict="NONE",
                reason=f"no proposal produced: {exc}", execution_status="BLOCKED",
                error=str(exc))

        proposal_dict = proposal.to_dict()

        # 2. Governance decision (side-effect-free evaluate). Fail closed on any
        #    SDK/transport error — never assume authorization.
        try:
            decision = self._client.evaluate(
                actor_id=proposal.actor_id, action=proposal.action,
                resource=proposal.resource, payload=proposal.payload)
        except MCCError as exc:
            return AgentRunResult(
                request=request, proposal=proposal_dict, verdict="ERROR",
                reason="governance evaluation failed", execution_status="BLOCKED",
                error=f"{type(exc).__name__}: {exc}")

        # 3. Dispatch on the verdict.
        if decision.verdict == Verdict.DENY:
            return self._denied(request, proposal_dict, decision)
        if decision.verdict == Verdict.ESCALATE:
            return self._escalate(request, proposal_dict, decision)
        if decision.verdict in (Verdict.ALLOW, Verdict.CONSTRAIN):
            return self._execute_authorized(request, proposal_dict, decision)
        # Unknown verdict cannot reach here (the SDK fails closed on parse), but
        # be explicit: an unrecognised verdict never executes.
        return AgentRunResult(  # pragma: no cover - SDK rejects unknown verdicts
            request=request, proposal=proposal_dict, verdict=decision.verdict.value,
            reason=decision.reason, execution_status="BLOCKED",
            error="unrecognised verdict; refusing to execute")

    __call__ = handle

    # ------------------------------------------------------------------ #
    # Verdict handlers.                                                   #
    # ------------------------------------------------------------------ #

    def _denied(self, request: str, proposal: Dict[str, Any],
                decision: Decision) -> AgentRunResult:
        # DENY: no execution, no external call. Surface the denial reason.
        return AgentRunResult(
            request=request, proposal=proposal, verdict="DENY",
            reason=decision.reason or "governance denied the action",
            execution_status="BLOCKED")

    def _escalate(self, request: str, proposal: Dict[str, Any],
                  decision: Decision) -> AgentRunResult:
        # ESCALATE: pause and ask the operator. Before a valid approval, nothing
        # executes and the external service is never called.
        try:
            approval = self._client.request_approval(decision)
        except MCCError as exc:
            return AgentRunResult(
                request=request, proposal=proposal, verdict="ESCALATE",
                reason="could not open approval request", approval_status="ERROR",
                execution_status="BLOCKED", error=f"{type(exc).__name__}: {exc}")

        granted = self._operator.decide(ApprovalRequest(
            request_id=approval.request_id, actor_id=decision.actor_id,
            action=decision.action, resource=decision.resource_id,
            reason=decision.reason))

        if not granted:
            # Operator rejected -> terminal, nothing runs.
            try:
                self._client.deny_approval(approval)
            except MCCError:
                pass
            return AgentRunResult(
                request=request, proposal=proposal, verdict="ESCALATE",
                reason="operator rejected the request", approval_status="REJECTED",
                execution_status="BLOCKED")

        # Operator approved -> mint a single-use mandate, then execute the ORIGINAL
        # requested payload (the gateway re-evaluates it under the mandate).
        try:
            approved = self._client.approve(approval)
            result = self._client.execute_after_approval(decision, approved)
        except MCCError as exc:
            return AgentRunResult(
                request=request, proposal=proposal, verdict="ESCALATE",
                reason="governed execution after approval did not complete",
                approval_status="APPROVED", execution_status="BLOCKED",
                error=f"{type(exc).__name__}: {exc}")

        return self._executed(
            request, proposal, decision, result, approval_status="APPROVED",
            final_payload=dict(decision.requested_payload))

    def _execute_authorized(self, request: str, proposal: Dict[str, Any],
                            decision: Decision) -> AgentRunResult:
        # ALLOW / CONSTRAIN: an authorized body exists. Execution still requires
        # authorization material (consensus votes / a mandate) — the agent does
        # not self-authorize. Without an authorizer it cannot proceed, and that is
        # a BLOCKED (non-executed) result, NOT a bypass.
        verdict = decision.verdict.value
        if self._authorizer is None:
            return AgentRunResult(
                request=request, proposal=proposal, verdict=verdict,
                reason=decision.reason,
                applied_constraints=list(decision.applied_constraints),
                final_payload=dict(decision.authorized_payload),
                execution_status="BLOCKED",
                error="no authorization material available; execution not attempted")

        try:
            authorization = self._authorizer.material(self._client, decision)
            # Sends ONLY the decision's authoritative payload (clamped for
            # CONSTRAIN) — never the original for a constrained decision.
            result = self._client.execute(decision, authorization)
        except MCCError as exc:
            return AgentRunResult(
                request=request, proposal=proposal, verdict=verdict,
                reason=decision.reason,
                applied_constraints=list(decision.applied_constraints),
                final_payload=dict(decision.authorized_payload),
                execution_status="BLOCKED", error=f"{type(exc).__name__}: {exc}")

        return self._executed(
            request, proposal, decision, result,
            final_payload=dict(decision.authorized_payload))

    # ------------------------------------------------------------------ #
    # Shared post-execution: receipt summary + audit verification.        #
    # ------------------------------------------------------------------ #

    def _executed(self, request: str, proposal: Dict[str, Any], decision: Decision,
                  result: Any, *, final_payload: Dict[str, Any],
                  approval_status: Optional[str] = None) -> AgentRunResult:
        audit_valid: Optional[bool] = None
        if self._verify_audit:
            try:
                audit_valid = self._client.verify_audit_chain().get("valid")
            except MCCError:
                audit_valid = None
        return AgentRunResult(
            request=request, proposal=proposal, verdict=decision.verdict.value,
            reason=decision.reason or "authorized",
            execution_status=result.status,
            approval_status=approval_status,
            final_payload=final_payload,
            applied_constraints=list(decision.applied_constraints),
            receipt=_receipt_summary(result.execution),
            audit_valid=audit_valid)


def _receipt_summary(execution: Any) -> Optional[Dict[str, Any]]:
    """A safe, non-sensitive summary of the governed executor's receipt.

    Never exposes secrets/tokens — only confirmation, correlation id, and the
    payload fingerprint the external service echoed back."""
    if not isinstance(execution, dict):
        return None
    body = execution.get("body")
    receipt = body if isinstance(body, dict) else execution
    return {
        "receipt_verified": execution.get("receipt_verified"),
        "upstream_status": execution.get("upstream_status"),
        "received": receipt.get("received"),
        "correlation_id": receipt.get("correlation_id"),
        "payload_sha256": receipt.get("payload_sha256"),
    }


__all__ = ["ReferenceGovernedAgent"]
