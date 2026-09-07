"""MCCProposalService — the ONE transport-neutral proposal/status boundary.

    ANY INTELLIGENCE / ANY FRAMEWORK / ANY TRANSPORT
                    |
                    v
            MCCProposalService            <-- Phase 1 stops here
                    |
                    v
       MCC INDEPENDENT AUTHORITY BOUNDARY   (future phase)
                    |
                    v
             EnforcementCoordinator
                    |
                    v
              SERVER-OWNED ACTUATOR

This module is deliberately, verifiably non-actuating. It imports NOTHING
from ``mcc_core.gate``, ``mcc_core.coordinator``, ``mcc_core.authority``,
``mcc_core.signing.SigningKey``/``sign_token``, ``mcc_core.mandate``,
``mcc_core.approvals``, or ``gateway.governance_service`` -- see
``tests/test_proposal_service_architecture_guards.py``. It knows nothing
about HTTP, MCP, LangGraph, CrewAI, AutoGen, VoltAgent, gRPC, or any other
transport: every adapter converges on ``submit_proposal``/
``get_operation_status`` and nothing else.

    PROPOSAL != PERMISSION.
    STATUS != AUTHORITY.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from mcc_core.profiles import ProfileRegistry

from .binding import BindingComputationError, compute_proposal_binding
from .models import (
    OperationStatusV1,
    OperationStatusValue,
    ProposalReceiptV1,
    ProposalRequestV1,
    ProposalValidationError,
)
from .registry import ProposalBackendUnavailable, ProposalRegisterStatus

# The read-only durable-execution status view this service is permitted to
# consult. Only ``get_state`` is ever called on it -- see the architecture
# guard test, which asserts this module contains no reference to ``reserve``,
# ``commit_dispatch``, ``mark_executed``, ``mark_unknown``, or
# ``resolve_unknown``.
try:  # pragma: no cover - import-shape only
    from mcc_core.idempotency import IdempotencyBackendUnavailable, IdempotencyState
except ImportError:  # pragma: no cover
    IdempotencyBackendUnavailable = None  # type: ignore[assignment,misc]
    IdempotencyState = None  # type: ignore[assignment,misc]


_DURABLE_STATE_MAP = {}
if IdempotencyState is not None:
    _DURABLE_STATE_MAP = {
        IdempotencyState.RESERVED: OperationStatusValue.RESERVED,
        IdempotencyState.DISPATCH_OWNED: OperationStatusValue.DISPATCH_OWNED,
        IdempotencyState.UNKNOWN: OperationStatusValue.UNKNOWN,
        IdempotencyState.EXECUTED: OperationStatusValue.EXECUTED,
    }


class MCCProposalService:
    """Transport-neutral. Construct one instance per deployment and hand it
    to every adapter (HTTP router, MCP handler, framework facade, SDK
    server-side counterpart) -- never let an adapter construct its own
    registry or recompute its own binding."""

    def __init__(
        self,
        *,
        proposals: Any,
        profiles: Optional[ProfileRegistry] = None,
        durable_execution_state: Optional[Any] = None,
    ) -> None:
        self._proposals = proposals
        self._profiles = profiles or ProfileRegistry.default_pilot()
        # Optional read-only durable-execution registry (an
        # ``InMemoryIdempotencyRegistry``/``RedisIdempotencyRegistry`` or
        # anything exposing an async ``get_state(key) -> StateRecord|None``).
        # ``None`` means this deployment of the proposal service is not wired
        # to a real execution backend yet -- status composition then never
        # reports RESERVED/DISPATCH_OWNED/UNKNOWN/EXECUTED, only
        # PROPOSED/NOT_FOUND, which is the honest answer for that
        # configuration (documented in
        # docs/MCC_UNIVERSAL_PROPOSAL_SERVICE_PHASE1.md).
        self._durable = durable_execution_state

    # -- submission ---------------------------------------------------- #

    async def submit_proposal(self, *, tenant_id: str, request: Dict[str, Any]) -> ProposalReceiptV1:
        """Register a proposal. Never calls the Gate, the coordinator, the
        signing key, or any actuator/upstream -- this either writes one
        PROPOSED record or reports why it did not."""
        if not isinstance(tenant_id, str) or not tenant_id.strip():
            raise ValueError("tenant_id must be a non-empty authenticated identity")

        try:
            proposal = ProposalRequestV1.from_dict(request)
        except ProposalValidationError as exc:
            return ProposalReceiptV1.rejected(
                logical_operation_id=(request.get("logical_operation_id")
                                      if isinstance(request, dict) and isinstance(
                                          request.get("logical_operation_id"), str) else "") or "",
                reason=f"{exc.code}: {exc.reason}",
            )

        try:
            binding = compute_proposal_binding(
                action=proposal.action, resource=proposal.resource,
                payload=proposal.payload, profiles=self._profiles,
            )
        except BindingComputationError as exc:
            return ProposalReceiptV1.rejected(
                logical_operation_id=proposal.logical_operation_id, reason=str(exc),
            )

        try:
            result = await self._proposals.register(
                tenant_id=tenant_id, logical_operation_id=proposal.logical_operation_id,
                binding=binding,
            )
        except ProposalBackendUnavailable as exc:
            return ProposalReceiptV1.unavailable(
                logical_operation_id=proposal.logical_operation_id,
                reason=f"proposal backend unavailable: {exc}",
            )

        if result.status == ProposalRegisterStatus.ERROR:
            return ProposalReceiptV1.unavailable(
                logical_operation_id=proposal.logical_operation_id, reason=result.reason,
            )
        if result.status == ProposalRegisterStatus.BINDING_CONFLICT:
            return ProposalReceiptV1.conflict(logical_operation_id=proposal.logical_operation_id)
        # REGISTERED or IDEMPOTENT_DUPLICATE both surface as an accepted,
        # idempotent PROPOSED receipt carrying the one true binding.
        return ProposalReceiptV1.proposed(
            logical_operation_id=proposal.logical_operation_id, proposal_binding=result.binding or binding,
        )

    # -- status ---------------------------------------------------------- #

    async def get_operation_status(self, *, tenant_id: str, logical_operation_id: str) -> OperationStatusV1:
        """Read-only. Performs zero state writes and calls no actuator.

        Ownership-gated precedence (tenant isolation -- Section 5/7):

          1. tenant-scoped proposal ownership lookup uncertain -> UNAVAILABLE
             (cannot prove ownership; never disclose)
          2. no tenant-scoped proposal record for this identity -> NOT_FOUND,
             WITHOUT ever consulting the durable execution registry. The
             durable registry is globally keyed (it has no tenant dimension,
             matching the unmodified EnforcementCoordinator), so it is never
             read at all unless this tenant has already proven ownership of
             ``logical_operation_id`` via its own proposal record -- a tenant
             that never proposed this identity can neither observe another
             tenant's durable state nor infer that it exists.
          3. ownership established; durable execution backend uncertain ->
             UNAVAILABLE
          4. ownership established; durable execution record exists AND its
             binding matches this tenant's own registered binding -> the
             durable record's exact state, verbatim (two tenants may
             legitimately reuse the same raw id with different bindings --
             see step 4a)
          4a. ownership established; durable execution record exists but its
             binding does NOT match this tenant's own registered binding ->
             that durable record belongs to a different registrant that
             reused the same id; never disclosed -> falls through to 5
          5. ownership established; no (disclosable) durable record ->
             PROPOSED
        """
        if not isinstance(tenant_id, str) or not tenant_id.strip():
            raise ValueError("tenant_id must be a non-empty authenticated identity")
        if not isinstance(logical_operation_id, str) or not logical_operation_id.strip():
            return OperationStatusV1.of(
                logical_operation_id=str(logical_operation_id),
                status=OperationStatusValue.NOT_FOUND,
                detail="invalid logical_operation_id",
            )

        # 1-2. Ownership gate: only a tenant that has itself registered a
        # proposal for this exact logical_operation_id may have durable
        # execution state composed into its response.
        try:
            record = await self._proposals.get(tenant_id=tenant_id, logical_operation_id=logical_operation_id)
        except ProposalBackendUnavailable as exc:
            return OperationStatusV1.of(
                logical_operation_id=logical_operation_id, status=OperationStatusValue.UNAVAILABLE,
                detail=f"proposal backend unavailable: {exc}",
            )
        if record is None:
            return OperationStatusV1.of(logical_operation_id=logical_operation_id, status=OperationStatusValue.NOT_FOUND)

        # 3-5. Ownership established -- the durable execution registry (if
        # configured) is now safe to consult and compose.
        if self._durable is not None:
            try:
                state = await self._durable.get_state(logical_operation_id)
            except IdempotencyBackendUnavailable as exc:  # type: ignore[misc]
                return OperationStatusV1.of(
                    logical_operation_id=logical_operation_id, status=OperationStatusValue.UNAVAILABLE,
                    detail=f"durable execution backend unavailable: {exc}",
                )
            if state is not None and state.binding == record.binding:
                # Section 4/16: two tenants may independently register the
                # SAME logical_operation_id with DIFFERENT bindings (this is
                # explicitly permitted, not a conflict). The durable
                # execution registry is still a single global-keyed record
                # per raw logical_operation_id, so "this tenant owns a
                # proposal for this id" alone cannot tell which tenant's
                # binding a given durable record belongs to. The durable
                # registry's own ``binding`` (computed identically --
                # ``hash_document({action, resource, payload_hash})`` -- by
                # both ``mcc_proposal.binding.compute_proposal_binding`` and
                # ``EnforcementCoordinator``'s ``binding_ref``) is the proof:
                # only when it matches THIS tenant's own registered binding
                # is the durable record for the operation this tenant
                # actually proposed. A mismatch means the durable record
                # belongs to a different registrant that reused the same raw
                # id with a different action/resource/payload -- it is never
                # disclosed, and this tenant's status falls through to its
                # own proposal-only view below.
                mapped = _DURABLE_STATE_MAP.get(state.state)
                if mapped is None:  # pragma: no cover - defensive; never mask as NOT_FOUND/PROPOSED
                    return OperationStatusV1.of(
                        logical_operation_id=logical_operation_id, status=OperationStatusValue.UNAVAILABLE,
                        detail="durable execution backend returned an unrecognized state",
                    )
                return OperationStatusV1.of(
                    logical_operation_id=logical_operation_id, status=mapped, proposal_binding=state.binding,
                )

        return OperationStatusV1.of(
            logical_operation_id=logical_operation_id, status=OperationStatusValue.PROPOSED,
            proposal_binding=record.binding,
        )


__all__ = ["MCCProposalService"]
