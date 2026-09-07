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
        Precedence (Section 8):

          1. durable execution backend uncertain -> UNAVAILABLE
          2. durable execution record exists -> its exact state, verbatim
          3. else a proposal record exists -> PROPOSED
          4. else -> NOT_FOUND
        """
        if not isinstance(tenant_id, str) or not tenant_id.strip():
            raise ValueError("tenant_id must be a non-empty authenticated identity")
        if not isinstance(logical_operation_id, str) or not logical_operation_id.strip():
            return OperationStatusV1.of(
                logical_operation_id=str(logical_operation_id),
                status=OperationStatusValue.NOT_FOUND,
                detail="invalid logical_operation_id",
            )

        if self._durable is not None:
            try:
                state = await self._durable.get_state(logical_operation_id)
            except IdempotencyBackendUnavailable as exc:  # type: ignore[misc]
                return OperationStatusV1.of(
                    logical_operation_id=logical_operation_id, status=OperationStatusValue.UNAVAILABLE,
                    detail=f"durable execution backend unavailable: {exc}",
                )
            if state is not None:
                mapped = _DURABLE_STATE_MAP.get(state.state)
                if mapped is None:  # pragma: no cover - defensive; never mask as NOT_FOUND/PROPOSED
                    return OperationStatusV1.of(
                        logical_operation_id=logical_operation_id, status=OperationStatusValue.UNAVAILABLE,
                        detail="durable execution backend returned an unrecognized state",
                    )
                return OperationStatusV1.of(
                    logical_operation_id=logical_operation_id, status=mapped, proposal_binding=state.binding,
                )

        try:
            record = await self._proposals.get(tenant_id=tenant_id, logical_operation_id=logical_operation_id)
        except ProposalBackendUnavailable as exc:
            return OperationStatusV1.of(
                logical_operation_id=logical_operation_id, status=OperationStatusValue.UNAVAILABLE,
                detail=f"proposal backend unavailable: {exc}",
            )
        if record is not None:
            return OperationStatusV1.of(
                logical_operation_id=logical_operation_id, status=OperationStatusValue.PROPOSED,
                proposal_binding=record.binding,
            )
        return OperationStatusV1.of(logical_operation_id=logical_operation_id, status=OperationStatusValue.NOT_FOUND)


__all__ = ["MCCProposalService"]
