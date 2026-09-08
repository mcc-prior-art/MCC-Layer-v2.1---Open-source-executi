"""ProposalExecutionService — Phase 2 bridge: tenant-owned proposal -> signed
authority -> the EXISTING, unmodified governed execution path.

    authenticated tenant
    -> ProposalRegistry.get(tenant_id=, logical_operation_id=)   (ownership +
       the proposal's OWN stored action/resource/canonical payload -- the
       ONE source of truth for what is about to be authorized; never an
       independently re-supplied payload)
    -> mcc_core.authority.AuthorityModel.evaluate(identity=tenant_id, ...)
       (trusted, tenant-identity-keyed verdict: ALLOW/DENY/ESCALATE/CONSTRAIN)
    -> mcc_core.core.DecisionEngine.issue_token   (signed authority; carries
       tenant_id + idempotency_key=logical_operation_id, exactly the PR #105
       durable identity pair)
    -> mcc_core.coordinator.EnforcementCoordinator.enforce   (the ONE
       execution path this repository has: ExecutionGate verification, the
       tenant-scoped IdempotencyRegistry, velocity, audit-before-actuation)
    -> the injected upstream actuator

    PROPOSAL != PERMISSION.
    TENANT_ID != AUTHORITY.
    PROPOSAL SERVICE != EXECUTION ENGINE.

This module is deliberately the ONLY new service boundary Phase 2
introduces. It composes exclusively public primitives this repository
already ships and already uses elsewhere for the identical purpose
(``examples/governed_agent/mcc_client.py``, ``gateway/governance_service.py``,
``examples/gpt6_astra_reference/pipeline.py``) -- no new decision logic, no
new token format, no second Gate, no second ``EnforcementCoordinator``, no
second durable execution registry, and no proposal-specific actuator bypass.

Lives in ``gateway/`` (not ``src/mcc_proposal/``) deliberately:
``tests/test_proposal_service_architecture_guards.py`` statically forbids
every file under ``src/mcc_proposal/`` from importing the Gate, the
coordinator, the authority model, or the signing authority at all -- a
future refactor cannot silently smuggle execution authority into what must
stay a transport-neutral, non-actuating ingress/lifecycle boundary. This
bridge is exactly what fills the "MCC INDEPENDENT AUTHORITY BOUNDARY" layer
``mcc_proposal/service.py``'s own module docstring already draws a box for.
"""

from __future__ import annotations

import copy
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Awaitable, Callable, Dict, List, Optional

from mcc_core import (
    ActuationStatus,
    AuthorityModel,
    DecisionEngine,
    EnforcementCoordinator,
    ProfileError,
    ProfileRegistry,
    Verdict,
    hash_document,
)

from mcc_proposal.binding import BindingComputationError, compute_proposal_binding
from mcc_proposal.registry import ProposalBackendUnavailable

# An upstream actuator performs the real side effect. It is the *only* thing
# the coordinator's executor calls -- identical contract to
# ``gateway.governance_service.Upstream``.
Upstream = Callable[[str, Dict[str, Any]], Awaitable[Any]]


class ProposalExecStatus(str, Enum):
    """The stable outcome vocabulary for :meth:`ProposalExecutionService.
    authorize_and_execute`. Distinct from ``OperationStatusValue``
    (``mcc_proposal.models``) -- that vocabulary describes the durable
    execution *state* a status read observes; this one describes what THIS
    ONE authorize-and-execute ATTEMPT did."""

    EXECUTED = "EXECUTED"
    BLOCKED = "BLOCKED"                # refused before/without dispatch; safe, no side effect
    EXECUTION_FAILED = "EXECUTION_FAILED"  # dispatched; outcome durably UNKNOWN
    DENIED = "DENIED"                  # trusted authority verdict was DENY
    ESCALATED = "ESCALATED"            # trusted authority verdict was ESCALATE
    NOT_FOUND = "NOT_FOUND"            # no tenant-owned proposal for this identity (tenant-safe)
    UNAVAILABLE = "UNAVAILABLE"        # backend uncertainty; never "safe to execute"
    REJECTED = "REJECTED"              # malformed/incomplete input or record; zero calls made


@dataclass(frozen=True)
class ProposalExecOutcome:
    status: ProposalExecStatus
    reason: str
    decision: Optional[str] = None          # ALLOW / DENY / ESCALATE / CONSTRAIN, when known
    audit_ref: Optional[str] = None
    execution: Any = None
    applied_changes: List[str] = field(default_factory=list)

    @property
    def executed(self) -> bool:
        return self.status == ProposalExecStatus.EXECUTED


def _now() -> int:
    return int(time.time())


class ProposalExecutionService:
    """Bridges :class:`mcc_proposal.registry` (a ``ProposalRegistry`` --
    ``InMemoryProposalRegistry``/``RedisProposalRegistry``) into the real
    authority + execution machinery. Construct ONE instance per deployment,
    wired to the SAME ``ProposalRegistry`` instance
    :class:`mcc_proposal.service.MCCProposalService` uses for status reads,
    and the SAME ``IdempotencyRegistry`` instance passed to it as
    ``durable_execution_state`` -- there is exactly one durable execution
    registry in this deployment, read by the status service and written by
    the coordinator this class drives.
    """

    def __init__(
        self,
        *,
        proposals: Any,
        authority: AuthorityModel,
        engine: DecisionEngine,
        coordinator: EnforcementCoordinator,
        upstream: Upstream,
        profiles: Optional[ProfileRegistry] = None,
    ) -> None:
        self._proposals = proposals
        self._authority = authority
        self._engine = engine
        self._coordinator = coordinator
        self._upstream = upstream
        self._profiles = profiles or ProfileRegistry.default_pilot()

    async def authorize_and_execute(
        self, *, tenant_id: str, logical_operation_id: str,
    ) -> ProposalExecOutcome:
        """Authorize and (if authority allows) execute exactly one
        tenant-owned proposal. Takes NO payload/action/resource parameter --
        by construction, this method cannot accept an independently supplied
        execution body that could diverge from the proposal's own stored
        content (Section 2); the only inputs are the two identity
        components, exactly like ``MCCProposalService.get_operation_status``.
        """
        # ---- Section 1: tenant ownership first, before anything else ----
        if not isinstance(tenant_id, str) or not tenant_id.strip():
            return ProposalExecOutcome(
                ProposalExecStatus.REJECTED, "tenant_id must be a non-empty authenticated identity",
            )
        if not isinstance(logical_operation_id, str) or not logical_operation_id.strip():
            return ProposalExecOutcome(
                ProposalExecStatus.REJECTED, "logical_operation_id must be a non-empty string",
            )

        try:
            record = await self._proposals.get(tenant_id=tenant_id, logical_operation_id=logical_operation_id)
        except ProposalBackendUnavailable as exc:
            return ProposalExecOutcome(
                ProposalExecStatus.UNAVAILABLE, f"proposal backend unavailable: {exc}",
            )
        if record is None:
            # Tenant-safe: whether this identity was never proposed at all,
            # or was proposed by a DIFFERENT tenant, is indistinguishable
            # here -- exactly mirroring the read-only status boundary.
            return ProposalExecOutcome(ProposalExecStatus.NOT_FOUND, "no proposal for this tenant/identity")

        # ---- Section 2: the proposal record's OWN content is the ONLY
        # source of the governed operation. A record written before this
        # bridge existed (or via the low-level registry API with no content)
        # carries no governable action -- refuse rather than guess. ----
        if not isinstance(record.action, str) or not record.action.strip():
            return ProposalExecOutcome(
                ProposalExecStatus.REJECTED,
                "proposal record carries no stored action/resource/payload content; "
                "cannot authorize an operation with no known shape",
            )
        action = record.action
        resource = record.resource
        payload = dict(record.payload or {})

        # Defense-in-depth internal-consistency check: the binding stored at
        # registration time must still match a fresh recomputation over the
        # SAME stored content, via the SAME reused primitive
        # ``compute_proposal_binding`` -- this should be unreachable by
        # construction (registration always computes both together), but a
        # divergence here can only mean storage corruption, never "this
        # actually belongs to someone else" (the registry is already
        # tenant-scoped). Fail closed rather than execute an unverified body.
        try:
            recomputed_binding = compute_proposal_binding(
                action=action, resource=resource, payload=payload, profiles=self._profiles,
            )
        except BindingComputationError as exc:
            return ProposalExecOutcome(
                ProposalExecStatus.REJECTED, f"stored proposal content no longer profile-valid: {exc}",
            )
        if recomputed_binding != record.binding:
            return ProposalExecOutcome(
                ProposalExecStatus.REJECTED,
                "stored proposal binding does not match its own stored content; "
                "internal consistency error, fail-closed",
            )

        # ---- Section 3: trusted authority issuance. Identity is the
        # AUTHENTICATED tenant_id -- never the proposal's caller-supplied
        # ``actor`` field, which is untrusted transport content. ----
        try:
            profile = self._profiles.for_action(action)
        except ProfileError as exc:
            return ProposalExecOutcome(ProposalExecStatus.REJECTED, f"PROFILE_ERROR: {exc}")

        decision = self._authority.evaluate(identity=tenant_id, action=action, context=payload, now=_now())

        if decision.verdict == Verdict.DENY:
            return ProposalExecOutcome(ProposalExecStatus.DENIED, decision.reason, decision=Verdict.DENY.value)
        if decision.verdict == Verdict.ESCALATE:
            return ProposalExecOutcome(
                ProposalExecStatus.ESCALATED, decision.reason, decision=Verdict.ESCALATE.value,
            )
        if decision.verdict not in (Verdict.ALLOW, Verdict.CONSTRAIN):
            # Unknown/malformed verdict -- never execute.
            return ProposalExecOutcome(
                ProposalExecStatus.REJECTED, f"unknown authority verdict {decision.verdict!r}; fail-closed",
            )

        forward_context = dict(decision.forward_context or payload)

        auth_claims = dict(profile.auth_claims(forward_context))
        token = self._engine.issue_token(
            verdict=decision.verdict.value,
            subject=tenant_id,
            action=action,
            payload=forward_context,
            constraints=decision.constraints,
            # The proposal's OWN stable identity becomes the idempotency_key
            # -- never regenerated for a retry (Section 3): a second
            # authorize_and_execute call for the SAME (tenant_id,
            # logical_operation_id) presents the SAME idempotency_key, so
            # the coordinator's own duplicate/UNKNOWN semantics (Section 9)
            # apply exactly as they would for any other governed caller.
            idempotency_key=logical_operation_id,
            tenant_id=tenant_id,
            actor_id=tenant_id,
            resource_id=resource,
            auth_claims=auth_claims,
        )

        # Round-24-style hardening (examples/gpt6_astra_reference/pipeline.py
        # ``enforce_authority``): a private, deep-copied snapshot taken here,
        # synchronously, before the first await -- the Gate's verification
        # and the executor's actual dispatch (separated by several awaited
        # admission steps inside ``coordinator.enforce``) observe the
        # IDENTICAL bytes; nothing outside this frame holds a mutable
        # reference to what actually gets dispatched (Section 6).
        effective_payload = copy.deepcopy(forward_context)

        async def executor() -> Any:
            return await self._upstream(action, effective_payload)

        result = await self._coordinator.enforce(
            token=token, action=action, payload=effective_payload, executor=executor,
            request_binding={
                "actor_id": tenant_id, "resource_id": resource,
                "transaction_id": None, "tenant_id": tenant_id,
            },
        )

        status_map = {
            ActuationStatus.EXECUTED: ProposalExecStatus.EXECUTED,
            ActuationStatus.BLOCKED: ProposalExecStatus.BLOCKED,
            ActuationStatus.EXECUTION_FAILED: ProposalExecStatus.EXECUTION_FAILED,
        }
        return ProposalExecOutcome(
            status=status_map.get(result.status, ProposalExecStatus.BLOCKED),
            reason=result.reason,
            decision=result.decision.value if result.decision else decision.verdict.value,
            audit_ref=result.audit_ref,
            execution=result.execution,
            applied_changes=list(decision.applied_changes or []),
        )


# --------------------------------------------------------------------------- #
# Reconciliation (Section 8) -- domain-neutral, tenant-scoped, resolves
# durable uncertainty from independently verified positive external
# evidence only. Never executes a new side effect.
# --------------------------------------------------------------------------- #


class ReconcileOutcome(str, Enum):
    RESOLVED = "RESOLVED"              # evidence matched; UNKNOWN/DISPATCH_OWNED -> EXECUTED, by THIS call
    EVIDENCE_MATCHED_NOT_APPLIED = "EVIDENCE_MATCHED_NOT_APPLIED"  # matched, but a racing writer/stale fence beat this call
    NO_EVIDENCE = "NO_EVIDENCE"        # no positive external evidence found; left pending
    NOT_FOUND = "NOT_FOUND"            # no tenant-owned proposal, or no durable record; tenant-safe
    NOT_RECONCILABLE = "NOT_RECONCILABLE"  # durable state is not UNKNOWN/DISPATCH_OWNED
    REJECTED = "REJECTED"              # malformed input / internal-consistency mismatch
    UNAVAILABLE = "UNAVAILABLE"


@dataclass(frozen=True)
class ProposalReconciliationOutcome:
    outcome: ReconcileOutcome
    reason: str


# A verifier looks for independently-observed positive evidence that a
# specific external side effect actually happened, and returns the exact
# CONTENT that evidence reports (never a bare boolean) so the caller can
# bind it to the authorized payload_hash -- OR ``None`` for "not found /
# inconclusive", which is always treated identically to a genuine absence,
# never distinguished for the purpose of authorizing anything further. This
# mirrors ``examples/gpt6_astra_reference/reconciliation.py``'s
# ``_find_issue_by_marker`` boundary, made explicitly pluggable so the
# Universal Proposal Service's reconciliation stays domain-neutral (it must
# work for ANY actuator, not just one hardcoded external service).
EvidenceVerifier = Callable[[], Awaitable[Optional[Dict[str, Any]]]]


async def reconcile_proposal_operation(
    *,
    proposals: Any,
    idempotency: Any,
    tenant_id: str,
    logical_operation_id: str,
    verify_external_evidence: EvidenceVerifier,
    profiles: Optional[ProfileRegistry] = None,
) -> ProposalReconciliationOutcome:
    """Reconcile ONE proposal-originated operation. Tenant-scoped throughout
    (Section 8): every lookup is keyed by ``(tenant_id, logical_operation_id)``,
    so no tenant may ever resolve another tenant's identical-id record, even
    one sharing every other field byte-for-byte. Never dispatches to an
    actuator -- ``verify_external_evidence`` is a pure, already-scoped LOOK,
    never a side-effecting call, and this function calls it at most once.
    """
    profiles = profiles or ProfileRegistry.default_pilot()

    if not isinstance(tenant_id, str) or not tenant_id.strip():
        return ProposalReconciliationOutcome(ReconcileOutcome.REJECTED, "tenant_id must be non-empty")
    if not isinstance(logical_operation_id, str) or not logical_operation_id.strip():
        return ProposalReconciliationOutcome(ReconcileOutcome.REJECTED, "logical_operation_id must be non-empty")

    try:
        record = await proposals.get(tenant_id=tenant_id, logical_operation_id=logical_operation_id)
    except ProposalBackendUnavailable as exc:
        return ProposalReconciliationOutcome(ReconcileOutcome.UNAVAILABLE, f"proposal backend unavailable: {exc}")
    if record is None or not isinstance(record.action, str) or not record.action.strip():
        return ProposalReconciliationOutcome(ReconcileOutcome.NOT_FOUND, "no proposal for this tenant/identity")

    from mcc_core.idempotency import IdempotencyBackendUnavailable, IdempotencyState, ReconcileStatus

    try:
        state = await idempotency.get_state(logical_operation_id, tenant_id=tenant_id)
    except IdempotencyBackendUnavailable as exc:
        return ProposalReconciliationOutcome(ReconcileOutcome.UNAVAILABLE, f"durable backend unavailable: {exc}")
    if state is None:
        return ProposalReconciliationOutcome(ReconcileOutcome.NOT_FOUND, "no durable record for this operation")
    if state.state not in (IdempotencyState.UNKNOWN, IdempotencyState.DISPATCH_OWNED):
        return ProposalReconciliationOutcome(
            ReconcileOutcome.NOT_RECONCILABLE, f"durable state is {state.state.value}; nothing to reconcile",
        )

    try:
        expected_binding = compute_proposal_binding(
            action=record.action, resource=record.resource, payload=dict(record.payload or {}), profiles=profiles,
        )
    except BindingComputationError as exc:
        return ProposalReconciliationOutcome(ReconcileOutcome.REJECTED, f"stored proposal content invalid: {exc}")
    if expected_binding != state.binding:
        return ProposalReconciliationOutcome(
            ReconcileOutcome.REJECTED,
            "durable record binding does not match this tenant's own proposal binding; "
            "internal consistency error, fail-closed",
        )

    evidence = await verify_external_evidence()
    if evidence is None:
        return ProposalReconciliationOutcome(ReconcileOutcome.NO_EVIDENCE, "no positive external evidence found")

    result_ref = hash_document({"evidence": evidence})
    result = await idempotency.resolve_unknown(
        logical_operation_id, tenant_id=tenant_id, expected_generation=state.generation, result_ref=result_ref,
    )
    if result.status == ReconcileStatus.RESOLVED:
        return ProposalReconciliationOutcome(ReconcileOutcome.RESOLVED, result.reason)
    return ProposalReconciliationOutcome(ReconcileOutcome.EVIDENCE_MATCHED_NOT_APPLIED, result.reason)


__all__ = [
    "ProposalExecStatus",
    "ProposalExecOutcome",
    "ProposalExecutionService",
    "ReconcileOutcome",
    "ProposalReconciliationOutcome",
    "EvidenceVerifier",
    "reconcile_proposal_operation",
]
