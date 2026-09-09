"""HTTP transport for the MCC Phase 2 governed execution bridge (Pilot
Execution API, PR #111).

Additive endpoints only. This module performs authentication, path
parsing, and response serialization ONLY — every authority/execution
decision is made by the EXISTING, unmodified
``gateway.proposal_execution_service.ProposalExecutionService`` /
``reconcile_proposal_operation``, never here.

    POST /v1/operations/{logical_operation_id}/execute    -> ProposalExecResultV1
    POST /v1/operations/{logical_operation_id}/reconcile   -> ProposalReconcileResultV1  (optional, see below)

Canonical chain this router is a thin wrapper over:

    authenticated API credential
    -> trusted server-side tenant_id resolution (X-Api-Key -> tenant_id,
       via the SAME ``get_tenant_dependency`` gateway.proposal_api uses)
    -> tenant-owned proposal
    -> ProposalExecutionService.authorize_and_execute(tenant_id=, logical_operation_id=)
    -> AuthorityModel -> signed authority token -> EnforcementCoordinator
    -> tenant-scoped durable execution identity -> ResourceBoundUpstream
    -> controlled actuator

PROPOSAL != PERMISSION. TENANT IDENTITY != EXECUTION AUTHORITY.
No verified authority -> no execution.

The execute endpoint takes NO request body at all — there is no field for
a caller to supply action/resource/payload/tenant_id/actor/signed
authority/decision/verdict/idempotency_key, or any other authorization
field, because the handler signature structurally has nowhere to put one:
its only inputs are the path's ``logical_operation_id`` and the
authenticated, server-resolved ``tenant_id``, exactly mirroring
``ProposalExecutionService.authorize_and_execute``'s own signature. Every
byte of what gets executed comes exclusively from the tenant-owned stored
proposal (Phase 1's ``POST /v1/proposals``) — this router cannot
reconstruct, enrich, mutate, or replace it.

The reconcile endpoint is mounted ONLY when the caller supplies a trusted
``verify_external_evidence`` (an ``EvidenceVerifier`` — the SAME contract
``reconcile_proposal_operation`` already defines). There is no
deployment-agnostic default evidence verifier in this repository —
evidence lookup is inherently actuator-specific (see
``examples/phase2_live_sandbox/evidence.py``'s GitHub-specific
implementation) — so a deployment with no configured verifier gets no
reconcile route at all, rather than a route that would have to accept
caller-supplied "it happened" evidence to do anything (which
``reconcile_proposal_operation`` already refuses to do: evidence always
comes from the trusted verifier, never from the request).
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import Depends, FastAPI, HTTPException

from gateway.proposal_api import get_tenant_dependency
from gateway.proposal_execution_service import (
    EvidenceVerifier,
    ProposalExecOutcome,
    ProposalExecStatus,
    ProposalExecutionService,
    ReconcileOutcome,
    reconcile_proposal_operation,
)

# Recommended HTTP status mapping (documented in docs/PILOT_EXECUTION_API.md):
# authentication failure -> 401 (handled by get_tenant_dependency itself);
# tenant-safe NOT_FOUND -> 404; backend unavailable -> 503; malformed
# input -> 422; every governed non-execution result (DENIED, ESCALATED,
# BLOCKED, EXECUTION_FAILED, RESOURCE_MISMATCH) stays a structured 200 --
# a policy denial or a safely-blocked replay is not an HTTP infrastructure
# failure.
_EXEC_STATUS_HTTP_CODE = {
    ProposalExecStatus.EXECUTED: 200,
    ProposalExecStatus.BLOCKED: 200,
    ProposalExecStatus.EXECUTION_FAILED: 200,
    ProposalExecStatus.DENIED: 200,
    ProposalExecStatus.ESCALATED: 200,
    ProposalExecStatus.RESOURCE_MISMATCH: 200,
    ProposalExecStatus.NOT_FOUND: 404,
    ProposalExecStatus.UNAVAILABLE: 503,
    ProposalExecStatus.REJECTED: 422,
}

_RECONCILE_STATUS_HTTP_CODE = {
    ReconcileOutcome.RESOLVED: 200,
    ReconcileOutcome.EVIDENCE_MATCHED_NOT_APPLIED: 200,
    ReconcileOutcome.NO_EVIDENCE: 200,
    ReconcileOutcome.EVIDENCE_MISMATCH: 200,
    ReconcileOutcome.NOT_RECONCILABLE: 200,
    ReconcileOutcome.NOT_FOUND: 404,
    ReconcileOutcome.REJECTED: 422,
    ReconcileOutcome.UNAVAILABLE: 503,
}


def _exec_outcome_to_response(outcome: ProposalExecOutcome) -> Dict[str, Any]:
    # Deliberately excludes ``outcome.execution`` (the raw actuator return
    # value) -- it is not a stable, wire-safe shape (an arbitrary actuator
    # may return connection/backend detail unsuitable for a caller) and is
    # not needed for a caller to know what happened; only the governed
    # status/reason/decision/audit_ref/applied_changes are exposed. No
    # token material, signing keys, or backend connection details ever
    # reach this dict -- ``ProposalExecOutcome`` never carries them.
    return {
        "status": outcome.status.value,
        "reason": outcome.reason,
        "decision": outcome.decision,
        "audit_ref": outcome.audit_ref,
        "applied_changes": list(outcome.applied_changes or []),
    }


def mount_proposal_execution_routes(
    app: FastAPI,
    service: ProposalExecutionService,
    *,
    tenants: Dict[str, str],
    proposals: Any = None,
    idempotency: Any = None,
    authority: Any = None,
    verify_external_evidence: Optional[EvidenceVerifier] = None,
) -> None:
    """Mount the Pilot Execution API onto an existing FastAPI app.

    ``tenants`` maps an authenticated API key to the tenant identity that
    scopes every execution — reused, unchanged, from
    ``gateway.proposal_api``'s Phase 1 credential-mapping pattern; this
    identity is never taken from the request body, a query parameter, or
    any URL segment other than the credential-authenticated dependency
    itself.

    The reconcile route is mounted only when ``verify_external_evidence``
    is provided, together with the SAME ``proposals``/``idempotency``/
    ``authority`` instances ``service`` was built from (see
    ``gateway.proposal_execution_stack.build_proposal_execution_stack``).
    """
    get_tenant = get_tenant_dependency(tenants)

    @app.post("/v1/operations/{logical_operation_id}/execute")
    async def execute_operation(
        logical_operation_id: str, tenant: str = Depends(get_tenant),
    ) -> Dict[str, Any]:
        outcome = await service.authorize_and_execute(
            tenant_id=tenant, logical_operation_id=logical_operation_id,
        )
        body = _exec_outcome_to_response(outcome)
        code = _EXEC_STATUS_HTTP_CODE.get(outcome.status, 500)
        if code >= 400:
            raise HTTPException(status_code=code, detail=body)
        return body

    if verify_external_evidence is None:
        return

    if proposals is None or idempotency is None or authority is None:
        raise ValueError(
            "mount_proposal_execution_routes: verify_external_evidence was provided "
            "but proposals/idempotency/authority were not -- the reconcile route "
            "requires all three (the SAME instances 'service' was built from) to "
            "call the existing reconcile_proposal_operation"
        )

    @app.post("/v1/operations/{logical_operation_id}/reconcile")
    async def reconcile_operation(
        logical_operation_id: str, tenant: str = Depends(get_tenant),
    ) -> Dict[str, Any]:
        outcome = await reconcile_proposal_operation(
            proposals=proposals, idempotency=idempotency, authority=authority,
            tenant_id=tenant, logical_operation_id=logical_operation_id,
            verify_external_evidence=verify_external_evidence,
        )
        body = {"outcome": outcome.outcome.value, "reason": outcome.reason}
        code = _RECONCILE_STATUS_HTTP_CODE.get(outcome.outcome, 500)
        if code >= 400:
            raise HTTPException(status_code=code, detail=body)
        return body


__all__ = ["mount_proposal_execution_routes"]
