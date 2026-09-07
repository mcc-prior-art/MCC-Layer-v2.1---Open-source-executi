"""Adapter-SDK ingress for the Compliance & Certification Suite (PR #51).

The Adapter SDK (PR #50) is the **canonical certification ingress**: an adapter is
consumed for certification exclusively through its public ``mcc_adapter_sdk.Adapter``
surface. :class:`SdkComplianceAdapter` bridges any such SDK adapter into the existing
:class:`~mcc_compliance.protocol.ComplianceAdapter` boundary, so it flows through the
one existing certification engine (``run_compliance`` → golden vectors → certification
→ reporting/manifest) — **no second pipeline, no duplicated infrastructure**.

For each scenario the bridge:
1. exercises the adapter's SDK surface — ``describe`` / ``to_proposal`` / ``to_response``
   — via :class:`mcc_adapter_sdk.AdapterRunner` and the mandatory Canonical Ingress
   Pipeline, routing evaluation through the governed ``mcc_client`` (the SDK ingress);
2. drives the governed execution (the SDK is translational and never executes) through
   the SAME ``mcc_client`` governed path the reference agent uses — the harness, not
   the adapter, executes; the gate + audit remain MCC-Core's.

The bridge holds no signing key and no executor; its only outward channel is the
injected governed client. It never authorizes, and it fails closed.
"""

from __future__ import annotations

from typing import Any, List, Optional, Tuple

from mcc_adapter_sdk import Adapter, AdapterContext as SdkAdapterContext, AdapterRunner
from mcc_client import Decision, Verdict
from mcc_client.exceptions import MCCError

from examples.reference_governed_agent.operator import ApprovalRequest

from .models import AdapterMetadata, AdapterOutcome
from .protocol import AdapterContext


def _compliance_metadata(adapter: Adapter) -> AdapterMetadata:
    md = adapter.describe().validate()
    return AdapterMetadata(
        name=md.adapter_id, version=md.adapter_version,
        implementation_id=md.adapter_id,
        claimed_contract_version=md.contract_version,
        framework=(md.framework_name if md.framework_name and md.framework_name != "none"
                   else None))


def _govern_execute(decision: Decision, *, client: Any, authorizer: Any,
                    operator: Any) -> Tuple[bool, List[str], Optional[bool], Optional[str]]:
    """Drive the governed execution for a decision through the SAME governed path the
    reference agent uses. Fail-closed: any error/denial/missing authorization is a
    non-executed result; the external service is never called on a non-ALLOW path."""
    applied = list(decision.applied_constraints)

    if decision.verdict == Verdict.DENY:
        return False, [], None, None

    if decision.verdict == Verdict.ESCALATE:
        try:
            approval = client.request_approval(decision)
        except MCCError as exc:
            return False, [], None, f"{type(exc).__name__}: {exc}"
        granted = operator.decide(ApprovalRequest(
            request_id=approval.request_id, actor_id=decision.actor_id,
            action=decision.action, resource=decision.resource_id, reason=decision.reason))
        if not granted:
            try:
                client.deny_approval(approval)
            except MCCError:
                pass
            return False, [], None, None
        try:
            approved = client.approve(approval)
            result = client.execute_after_approval(decision, approved)
        except MCCError as exc:
            return False, [], None, f"{type(exc).__name__}: {exc}"
        return bool(result.executed), applied, _audit_valid(client), None

    if decision.verdict in (Verdict.ALLOW, Verdict.CONSTRAIN):
        if authorizer is None:
            return False, applied, None, "no authorization material available"
        try:
            authorization = authorizer.material(client, decision)
            result = client.execute(decision, authorization)
        except MCCError as exc:
            return False, applied, None, f"{type(exc).__name__}: {exc}"
        return bool(result.executed), applied, _audit_valid(client), None

    return False, applied, None, "unrecognised verdict; refusing to execute"


def _audit_valid(client: Any) -> Optional[bool]:
    try:
        return client.verify_audit_chain().get("valid")
    except MCCError:
        return None


class SdkComplianceAdapter:
    """Bridge an ``mcc_adapter_sdk.Adapter`` into the certification engine."""

    def __init__(self, sdk_adapter: Adapter) -> None:
        self._sdk = sdk_adapter
        self._meta = _compliance_metadata(sdk_adapter)

    def describe(self) -> AdapterMetadata:
        return self._meta

    def run_scenario(self, ctx: AdapterContext) -> AdapterOutcome:
        params = dict(ctx.provider_config)
        # 1. SDK ingress: translate (adapter) → proposal → pipeline → evaluate (via the
        #    governed client). The adapter is consumed ONLY through its SDK surface.
        sdk_ctx = SdkAdapterContext.create(
            actor_reference=params.get("actor_id", "agent/notify-bot"),
            tenant="compliance", namespace="certification")

        def router(proposal):
            # Round 25: EnforcementCoordinator now fails closed without a
            # stable logical-operation identity. The proposal's own
            # ``proposal_id`` (already a fresh, unique-per-request UUID
            # minted by CanonicalProposal.create()) is the natural one --
            # never invented at the gateway/coordinator layer.
            return ctx.client.evaluate(actor_id=proposal.actor, action=proposal.action,
                                       resource=proposal.resource, payload=proposal.payload,
                                       idempotency_key=proposal.proposal_id)

        runner = AdapterRunner(self._sdk, router)
        result = runner.run(sdk_ctx, {"request": ctx.request, "params": params})

        if not result.ok:
            stage = (result.error or {}).get("stage", "")
            if stage == "to_proposal":
                # Malformed request → no action proposed (matches the reference agent).
                return AdapterOutcome(verdict="NONE", executed=False)
            return AdapterOutcome(verdict="ERROR", executed=False,
                                  error=(result.error or {}).get("error"))

        # 2. Governed execution (harness/MCC-Core, not the adapter). Cross-checked by
        #    the runner against ground-truth receipts + audit.
        decision = result.governance_decision.decision
        executed, applied, audit_valid, error = _govern_execute(
            decision, client=ctx.client, authorizer=ctx.authorizer, operator=ctx.operator)
        return AdapterOutcome(
            verdict=decision.verdict.value, executed=executed,
            applied_constraints=applied, audit_valid=audit_valid, error=error)


__all__ = ["SdkComplianceAdapter"]
