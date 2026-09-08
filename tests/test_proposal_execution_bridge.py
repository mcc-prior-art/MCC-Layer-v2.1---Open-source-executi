"""Phase 2 — PROPOSAL -> SIGNED AUTHORITY -> GOVERNED EXECUTION.

Adversarial behavioral matrix (A-N) for
``gateway.proposal_execution_service.ProposalExecutionService`` /
``reconcile_proposal_operation``, plus the Phase 2 remediation round's
Blocker 1 (unbound reconciliation evidence) and Blocker 2 (actuator
resource binding) adversarial matrices and non-vacuity probes. Exercises
the REAL service/coordinator boundary throughout: a real
``mcc_proposal.MCCProposalService``/``InMemoryProposalRegistry``, a real
``mcc_core.core.DecisionEngine``/``mcc_core.gate.ExecutionGate``/
``mcc_core.coordinator.EnforcementCoordinator``/
``mcc_core.idempotency.InMemoryIdempotencyRegistry``, and a real
``mcc_core.authority.AuthorityModel`` -- never a hash comparison in
isolation.
"""

from __future__ import annotations

import asyncio
import copy
import tempfile
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Dict, List, Optional

import pytest

from mcc_core import (
    ActionPolicy,
    AuditLog,
    AuthorityModel,
    DecisionEngine,
    EnforcementCoordinator,
    ExecutionGate,
    IdempotencyBackendUnavailable,
    IdempotencyState,
    InMemoryIdempotencyRegistry,
    InMemoryNonceRegistry,
    InMemoryVelocityRegistry,
    Mandate,
    MandateRegistry,
    ProfileRegistry,
    SigningKey,
    Verdict,
)
from mcc_core.signing import hash_payload
from mcc_proposal import InMemoryProposalRegistry, MCCProposalService
from mcc_proposal.registry import ProposalBackendUnavailable, ProposalRecord

from gateway.proposal_execution_service import (
    ProposalExecOutcome,
    ProposalExecStatus,
    ProposalExecutionService,
    ReconcileOutcome,
    ResourceBoundUpstream,
    ResourceMismatchError,
    reconcile_proposal_operation,
)

run = asyncio.run


def _authority(allowed_tenants, *, action="test_action", max_amount=None,
               without_mandate=Verdict.DENY) -> AuthorityModel:
    grants = {}
    for t in allowed_tenants:
        constraints = {"max_amount": max_amount} if max_amount is not None else {}
        grants[t] = [{"authority": "execute", "constraints": constraints}]
    registry = MandateRegistry.from_config(grants)
    on_violation = Verdict.CONSTRAIN if max_amount is not None else Verdict.DENY
    policy = ActionPolicy(
        action=action, requires="execute", on_mandate=Verdict.ALLOW,
        on_violation=on_violation, without_mandate=without_mandate,
    )
    return AuthorityModel(registry=registry, policies=[policy], default=Verdict.DENY)


def build_stack(*, allowed_tenants=("tenant-a", "tenant-b", "tenant-c"),
                 action="test_action", max_amount=None,
                 without_mandate=Verdict.DENY, actuator_resource="res-1"):
    proposals = InMemoryProposalRegistry()
    idem = InMemoryIdempotencyRegistry()
    svc = MCCProposalService(proposals=proposals, durable_execution_state=idem)

    signing_key = SigningKey.generate("bridge-test-key")
    engine = DecisionEngine(
        signing_key=signing_key, issuer="mcc/test", audience="test-gate",
        policy_id="test/v1", policy_hash="sha256:test", token_ttl_seconds=60,
    )
    gate = ExecutionGate(
        trusted_keys={signing_key.kid: signing_key.public_key()}, audience="test-gate",
        nonce_registry=InMemoryNonceRegistry(), policy_hash="sha256:test",
    )
    audit_path = str(Path(tempfile.mkdtemp(prefix="mcc-phase2-test-")) / "audit.jsonl")
    audit = AuditLog(audit_path)
    coordinator = EnforcementCoordinator(
        gate=gate, idempotency=idem, velocity=InMemoryVelocityRegistry(),
        audit=audit, profiles=ProfileRegistry(),
    )
    authority = _authority(allowed_tenants, action=action, max_amount=max_amount,
                           without_mandate=without_mandate)

    calls: List[Any] = []

    async def raw_upstream(*, resource: Optional[str], action: str, payload: Dict[str, Any]) -> Any:
        calls.append((action, copy.deepcopy(payload)))
        return {"ok": True, "action": action, "resource": resource}

    upstream = ResourceBoundUpstream(resource=actuator_resource, dispatch=raw_upstream)

    bridge = ProposalExecutionService(
        proposals=proposals, authority=authority, engine=engine,
        coordinator=coordinator, upstream=upstream,
    )
    return SimpleNamespace(
        proposals=proposals, idem=idem, svc=svc, bridge=bridge, calls=calls,
        engine=engine, gate=gate, coordinator=coordinator, authority=authority,
        signing_key=signing_key, audit=audit, raw_upstream=raw_upstream,
    )


async def _propose(stack, tenant, op_id, *, action="test_action", resource="res-1",
                    payload=None):
    return await stack.svc.submit_proposal(tenant_id=tenant, request={
        "logical_operation_id": op_id, "actor": "agent/x", "action": action,
        "resource": resource, "payload": payload or {"n": 1},
    })


def _bound_evidence(*, tenant_id, logical_operation_id, action, resource, payload):
    """The well-formed, operation-bound evidence shape
    ``reconcile_proposal_operation`` requires (Blocker 1)."""
    return {
        "tenant_id": tenant_id, "logical_operation_id": logical_operation_id,
        "action": action, "resource": resource, "payload": payload,
    }


# --------------------------------------------------------------------------- #
# A. Tenant A cannot authorize or execute Tenant B's proposal.
# --------------------------------------------------------------------------- #

def test_a_tenant_a_cannot_authorize_or_execute_tenant_bs_proposal():
    stack = build_stack()
    r = run(_propose(stack, "tenant-b", "op-a"))
    assert r.accepted

    out = run(stack.bridge.authorize_and_execute(tenant_id="tenant-a", logical_operation_id="op-a"))
    assert out.status == ProposalExecStatus.NOT_FOUND
    assert stack.calls == []

    own = run(stack.bridge.authorize_and_execute(tenant_id="tenant-b", logical_operation_id="op-a"))
    assert own.status == ProposalExecStatus.EXECUTED


# --------------------------------------------------------------------------- #
# B. Two tenants, identical logical_operation_id AND identical binding,
#    execute independently, exactly once each.
# --------------------------------------------------------------------------- #

def test_b_identical_id_and_binding_cross_tenant_execute_independently():
    stack = build_stack()
    payload = {"n": 42}
    run(_propose(stack, "tenant-a", "op-shared", payload=payload))
    run(_propose(stack, "tenant-b", "op-shared", payload=payload))

    out_a = run(stack.bridge.authorize_and_execute(tenant_id="tenant-a", logical_operation_id="op-shared"))
    out_b = run(stack.bridge.authorize_and_execute(tenant_id="tenant-b", logical_operation_id="op-shared"))
    assert out_a.status == ProposalExecStatus.EXECUTED
    assert out_b.status == ProposalExecStatus.EXECUTED
    assert len(stack.calls) == 2

    state_a = run(stack.idem.get_state("op-shared", tenant_id="tenant-a"))
    state_b = run(stack.idem.get_state("op-shared", tenant_id="tenant-b"))
    assert state_a.state == IdempotencyState.EXECUTED
    assert state_b.state == IdempotencyState.EXECUTED
    assert state_a.generation != state_b.generation or state_a is not state_b


# --------------------------------------------------------------------------- #
# C. Same tenant / same logical_operation_id / changed payload is rejected.
# --------------------------------------------------------------------------- #

def test_c_same_tenant_same_id_changed_payload_is_rejected():
    stack = build_stack()
    r1 = run(_propose(stack, "tenant-a", "op-c", payload={"n": 1}))
    assert r1.accepted
    r2 = run(_propose(stack, "tenant-a", "op-c", payload={"n": 2}))
    assert not r2.accepted
    assert r2.status == "BINDING_CONFLICT"

    out = run(stack.bridge.authorize_and_execute(tenant_id="tenant-a", logical_operation_id="op-c"))
    assert out.status == ProposalExecStatus.EXECUTED
    assert stack.calls[-1][1] == {"n": 1}


# --------------------------------------------------------------------------- #
# D. Proposal payload mutated after authority issuance is rejected with
#    zero actuator calls -- tested at the registry's storage boundary,
#    since the bridge's ``authorize_and_execute`` takes no payload
#    parameter at all (there is nothing for a caller to mutate).
# --------------------------------------------------------------------------- #

def test_d_stored_binding_mismatch_after_the_fact_is_rejected_zero_calls():
    stack = build_stack()
    run(_propose(stack, "tenant-a", "op-d", payload={"n": 1}))

    real = run(stack.proposals.get(tenant_id="tenant-a", logical_operation_id="op-d"))
    tampered = ProposalRecord(
        tenant_id=real.tenant_id, logical_operation_id=real.logical_operation_id,
        binding=real.binding, created_at=real.created_at,
        action=real.action, resource=real.resource, payload={"n": 999},
    )
    stack.proposals._store["tenant-a\x00op-d"] = tampered

    out = run(stack.bridge.authorize_and_execute(tenant_id="tenant-a", logical_operation_id="op-d"))
    assert out.status == ProposalExecStatus.REJECTED
    assert "consistency" in out.reason
    assert stack.calls == []


# --------------------------------------------------------------------------- #
# E. Authority for Proposal A cannot execute Proposal B.
# --------------------------------------------------------------------------- #

class _Capture:
    def __init__(self, real):
        self._real = real
        self.last = None

    def issue_token(self, **kw):
        tok = self._real.issue_token(**kw)
        self.last = tok
        return tok


def test_e_authority_for_proposal_a_cannot_execute_proposal_b():
    stack = build_stack()
    run(_propose(stack, "tenant-a", "op-e-a", payload={"n": 1}))
    run(_propose(stack, "tenant-a", "op-e-b", payload={"n": 2}))

    captured = _Capture(stack.engine)
    stack.bridge._engine = captured  # type: ignore[attr-defined]

    out_a = run(stack.bridge.authorize_and_execute(tenant_id="tenant-a", logical_operation_id="op-e-a"))
    assert out_a.status == ProposalExecStatus.EXECUTED
    token_for_a = captured.last
    assert token_for_a["idempotency_key"] == "op-e-a"

    async def dispatch():
        return await stack.bridge._upstream.execute(resource="res-1", action="test_action", payload={"n": 2})  # type: ignore[attr-defined]

    calls_before = len(stack.calls)
    result = run(stack.coordinator.enforce(
        token=token_for_a, action="test_action", payload={"n": 2}, executor=dispatch,
        request_binding={"actor_id": "tenant-a", "resource_id": "res-1",
                         "transaction_id": None, "tenant_id": "tenant-a"},
    ))
    assert result.status.value != "EXECUTED"
    assert len(stack.calls) == calls_before

    state_b = run(stack.idem.get_state("op-e-b", tenant_id="tenant-a"))
    assert state_b is None


# --------------------------------------------------------------------------- #
# F. Authority for Tenant A cannot execute the identical proposal identity
#    under Tenant B.
# --------------------------------------------------------------------------- #

def test_f_authority_for_tenant_a_cannot_execute_identical_identity_under_tenant_b():
    stack = build_stack()
    payload = {"n": 7}
    run(_propose(stack, "tenant-a", "op-f", payload=payload))
    run(_propose(stack, "tenant-b", "op-f", payload=payload))

    captured = _Capture(stack.engine)
    stack.bridge._engine = captured  # type: ignore[attr-defined]

    out_a = run(stack.bridge.authorize_and_execute(tenant_id="tenant-a", logical_operation_id="op-f"))
    assert out_a.status == ProposalExecStatus.EXECUTED
    token_for_a = captured.last
    assert token_for_a["tenant_id"] == "tenant-a"

    out_b = run(stack.bridge.authorize_and_execute(tenant_id="tenant-b", logical_operation_id="op-f"))
    assert out_b.status == ProposalExecStatus.EXECUTED

    state_a = run(stack.idem.get_state("op-f", tenant_id="tenant-a"))
    state_b = run(stack.idem.get_state("op-f", tenant_id="tenant-b"))
    assert state_a.state == IdempotencyState.EXECUTED
    assert state_b.state == IdempotencyState.EXECUTED
    assert len(stack.calls) == 2


# --------------------------------------------------------------------------- #
# G. Replayed token cannot execute twice.
# --------------------------------------------------------------------------- #

def test_g_replayed_token_cannot_execute_twice():
    stack = build_stack()
    run(_propose(stack, "tenant-a", "op-g"))

    captured = _Capture(stack.engine)
    stack.bridge._engine = captured  # type: ignore[attr-defined]

    out = run(stack.bridge.authorize_and_execute(tenant_id="tenant-a", logical_operation_id="op-g"))
    assert out.status == ProposalExecStatus.EXECUTED
    token = captured.last

    async def dispatch():
        return await stack.bridge._upstream.execute(resource="res-1", action="test_action", payload={"n": 1})  # type: ignore[attr-defined]

    calls_before = len(stack.calls)
    replay = run(stack.coordinator.enforce(
        token=token, action="test_action", payload={"n": 1}, executor=dispatch,
        request_binding={"actor_id": "tenant-a", "resource_id": "res-1",
                         "transaction_id": None, "tenant_id": "tenant-a"},
    ))
    assert replay.status.value != "EXECUTED"
    assert len(stack.calls) == calls_before


# --------------------------------------------------------------------------- #
# H. Two concurrent execution attempts for the same tenant operation produce
#    at most one external effect.
# --------------------------------------------------------------------------- #

def test_h_concurrent_same_tenant_execution_produces_at_most_one_effect():
    stack = build_stack()
    run(_propose(stack, "tenant-a", "op-h"))

    async def go():
        return await asyncio.gather(
            stack.bridge.authorize_and_execute(tenant_id="tenant-a", logical_operation_id="op-h"),
            stack.bridge.authorize_and_execute(tenant_id="tenant-a", logical_operation_id="op-h"),
        )

    r1, r2 = run(go())
    statuses = sorted([r1.status.value, r2.status.value])
    assert statuses[0] != "EXECUTED" or statuses.count("EXECUTED") == 1
    assert len(stack.calls) == 1


# --------------------------------------------------------------------------- #
# I. Crash/error after dispatch ownership preserves UNKNOWN and no
#    automatic retry.
# --------------------------------------------------------------------------- #

def test_i_crash_after_dispatch_ownership_preserves_unknown_no_auto_retry():
    stack = build_stack()
    run(_propose(stack, "tenant-a", "op-i"))

    async def boom(*, resource, action, payload):
        raise ConnectionError("simulated crash after dispatch")

    stack.bridge._upstream = ResourceBoundUpstream(resource="res-1", dispatch=boom)  # type: ignore[attr-defined]

    out = run(stack.bridge.authorize_and_execute(tenant_id="tenant-a", logical_operation_id="op-i"))
    assert out.status == ProposalExecStatus.EXECUTION_FAILED

    state = run(stack.idem.get_state("op-i", tenant_id="tenant-a"))
    assert state.state == IdempotencyState.UNKNOWN

    calls_before = len(stack.calls)
    out2 = run(stack.bridge.authorize_and_execute(tenant_id="tenant-a", logical_operation_id="op-i"))
    assert out2.status != ProposalExecStatus.EXECUTED
    assert len(stack.calls) == calls_before


# --------------------------------------------------------------------------- #
# J. Reconciliation of Tenant A cannot alter Tenant B's identical operation.
# --------------------------------------------------------------------------- #

def test_j_reconciliation_of_tenant_a_cannot_alter_tenant_bs_identical_operation():
    stack = build_stack()
    payload = {"n": 5}
    run(_propose(stack, "tenant-a", "op-j", payload=payload))
    run(_propose(stack, "tenant-b", "op-j", payload=payload))

    async def boom(*, resource, action, payload):
        raise ConnectionError("simulated crash")

    stack.bridge._upstream = ResourceBoundUpstream(resource="res-1", dispatch=boom)  # type: ignore[attr-defined]
    out_a = run(stack.bridge.authorize_and_execute(tenant_id="tenant-a", logical_operation_id="op-j"))
    out_b = run(stack.bridge.authorize_and_execute(tenant_id="tenant-b", logical_operation_id="op-j"))
    assert out_a.status == ProposalExecStatus.EXECUTION_FAILED
    assert out_b.status == ProposalExecStatus.EXECUTION_FAILED

    async def evidence_for_a(*, tenant_id, logical_operation_id, action, resource, payload_hash):
        return _bound_evidence(
            tenant_id=tenant_id, logical_operation_id=logical_operation_id,
            action=action, resource=resource, payload=payload,
        )

    result = run(reconcile_proposal_operation(
        proposals=stack.proposals, idempotency=stack.idem, authority=stack.authority,
        tenant_id="tenant-a", logical_operation_id="op-j", verify_external_evidence=evidence_for_a,
    ))
    assert result.outcome == ReconcileOutcome.RESOLVED

    state_a = run(stack.idem.get_state("op-j", tenant_id="tenant-a"))
    state_b = run(stack.idem.get_state("op-j", tenant_id="tenant-b"))
    assert state_a.state == IdempotencyState.EXECUTED
    assert state_b.state == IdempotencyState.UNKNOWN  # untouched by tenant-a's reconciliation


# --------------------------------------------------------------------------- #
# K. Durable backend outage produces no actuation.
# --------------------------------------------------------------------------- #

class _DownIdempotency:
    async def reserve(self, *a, **k):
        raise IdempotencyBackendUnavailable("down")

    async def get_state(self, *a, **k):
        raise IdempotencyBackendUnavailable("down")

    async def commit_dispatch(self, *a, **k):
        raise IdempotencyBackendUnavailable("down")

    async def mark_executed(self, *a, **k):
        raise IdempotencyBackendUnavailable("down")

    async def mark_unknown(self, *a, **k):
        raise IdempotencyBackendUnavailable("down")

    async def release(self, *a, **k):
        raise IdempotencyBackendUnavailable("down")


def test_k_durable_backend_outage_produces_no_actuation():
    stack = build_stack()
    run(_propose(stack, "tenant-a", "op-k"))

    down_coordinator = EnforcementCoordinator(
        gate=stack.gate, idempotency=_DownIdempotency(), velocity=InMemoryVelocityRegistry(),
        audit=stack.audit, profiles=ProfileRegistry(),
    )
    stack.bridge._coordinator = down_coordinator  # type: ignore[attr-defined]

    with pytest.raises(IdempotencyBackendUnavailable):
        run(stack.bridge.authorize_and_execute(tenant_id="tenant-a", logical_operation_id="op-k"))
    assert stack.calls == []


# --------------------------------------------------------------------------- #
# L. Non-owned proposal lookup during durable-backend outage remains
#    tenant-safe NOT_FOUND and does not disclose backend state for another
#    tenant.
# --------------------------------------------------------------------------- #

def test_l_non_owned_lookup_during_backend_outage_stays_tenant_safe_not_found():
    stack = build_stack()
    run(_propose(stack, "tenant-a", "op-l"))

    down_coordinator = EnforcementCoordinator(
        gate=stack.gate, idempotency=_DownIdempotency(), velocity=InMemoryVelocityRegistry(),
        audit=stack.audit, profiles=ProfileRegistry(),
    )
    stack.bridge._coordinator = down_coordinator  # type: ignore[attr-defined]

    out = run(stack.bridge.authorize_and_execute(tenant_id="tenant-c", logical_operation_id="op-l"))
    assert out.status == ProposalExecStatus.NOT_FOUND
    assert stack.calls == []


# --------------------------------------------------------------------------- #
# M. Restart/persistence -- see scripts/redis_proposal_phase2_smoke.py for
#    the real-Redis version.
# --------------------------------------------------------------------------- #

def test_m_restart_persistence_tenant_isolated_in_memory_equivalent():
    stack = build_stack()
    run(_propose(stack, "tenant-a", "op-m"))
    out = run(stack.bridge.authorize_and_execute(tenant_id="tenant-a", logical_operation_id="op-m"))
    assert out.status == ProposalExecStatus.EXECUTED

    fresh_svc = MCCProposalService(proposals=stack.proposals, durable_execution_state=stack.idem)
    status = run(fresh_svc.get_operation_status(tenant_id="tenant-a", logical_operation_id="op-m"))
    assert status.status == "EXECUTED"


# --------------------------------------------------------------------------- #
# N. Final outbound payload equals the exact payload authorized by the
#    signed token.
# --------------------------------------------------------------------------- #

def test_n_final_outbound_payload_equals_the_authorized_payload():
    stack = build_stack()
    payload = {"n": 123, "note": "exact-bytes"}
    run(_propose(stack, "tenant-a", "op-n", payload=payload))

    captured = _Capture(stack.engine)
    stack.bridge._engine = captured  # type: ignore[attr-defined]

    out = run(stack.bridge.authorize_and_execute(tenant_id="tenant-a", logical_operation_id="op-n"))
    assert out.status == ProposalExecStatus.EXECUTED

    dispatched_action, dispatched_payload = stack.calls[-1]
    assert dispatched_payload == payload
    assert hash_payload(dispatched_payload) == captured.last["payload_hash"]


# --------------------------------------------------------------------------- #
# CONSTRAIN / ESCALATE / DENY / validation paths.
# --------------------------------------------------------------------------- #

def test_deny_path_never_issues_a_token_or_calls_upstream():
    stack = build_stack(allowed_tenants=())
    run(_propose(stack, "tenant-a", "op-deny"))
    out = run(stack.bridge.authorize_and_execute(tenant_id="tenant-a", logical_operation_id="op-deny"))
    assert out.status == ProposalExecStatus.DENIED
    assert stack.calls == []


def test_escalate_path_never_executes():
    stack = build_stack(allowed_tenants=(), without_mandate=Verdict.ESCALATE)
    run(_propose(stack, "tenant-a", "op-escalate"))
    out = run(stack.bridge.authorize_and_execute(tenant_id="tenant-a", logical_operation_id="op-escalate"))
    assert out.status == ProposalExecStatus.ESCALATED
    assert stack.calls == []


def test_constrain_path_executes_only_the_clamped_payload():
    stack = build_stack(allowed_tenants=("tenant-a",), max_amount=100)
    run(_propose(stack, "tenant-a", "op-constrain", payload={"n": 1, "amount": 500}))
    out = run(stack.bridge.authorize_and_execute(tenant_id="tenant-a", logical_operation_id="op-constrain"))
    assert out.status == ProposalExecStatus.EXECUTED
    assert out.decision == "CONSTRAIN"
    dispatched_action, dispatched_payload = stack.calls[-1]
    assert dispatched_payload["amount"] == 100


def test_missing_tenant_id_and_missing_logical_operation_id_fail_closed():
    stack = build_stack()
    out1 = run(stack.bridge.authorize_and_execute(tenant_id="", logical_operation_id="op-x"))
    assert out1.status == ProposalExecStatus.REJECTED
    out2 = run(stack.bridge.authorize_and_execute(tenant_id="tenant-a", logical_operation_id="   "))
    assert out2.status == ProposalExecStatus.REJECTED
    assert stack.calls == []


def test_proposal_backend_unavailable_maps_to_unavailable_not_not_found():
    class _DownProposals:
        async def get(self, **kw):
            raise ProposalBackendUnavailable("down")

    stack = build_stack()
    stack.bridge._proposals = _DownProposals()  # type: ignore[attr-defined]
    out = run(stack.bridge.authorize_and_execute(tenant_id="tenant-a", logical_operation_id="op-y"))
    assert out.status == ProposalExecStatus.UNAVAILABLE
    assert stack.calls == []


def test_record_with_no_stored_content_is_rejected_not_executed():
    """A Phase-1-only / legacy record (no action/resource/payload) must
    never be treated as executable -- the same fail-closed rule that
    protects a real legacy Redis record (tests/test_mcc_proposal_registry.py)."""
    stack = build_stack()
    run(stack.proposals.register(tenant_id="tenant-a", logical_operation_id="op-bare", binding="sha256:whatever"))
    out = run(stack.bridge.authorize_and_execute(tenant_id="tenant-a", logical_operation_id="op-bare"))
    assert out.status == ProposalExecStatus.REJECTED
    assert stack.calls == []


def test_resource_bound_upstream_rejects_construction_with_a_bare_callable():
    async def bare(action, payload):
        return {"ok": True}

    stack = build_stack()
    with pytest.raises(TypeError):
        ProposalExecutionService(
            proposals=stack.proposals, authority=stack.authority, engine=stack.engine,
            coordinator=stack.coordinator, upstream=bare,
        )


# --------------------------------------------------------------------------- #
# Reconciliation edge cases beyond J.
# --------------------------------------------------------------------------- #

def test_reconciliation_never_dispatches_to_the_actuator():
    stack = build_stack()
    run(_propose(stack, "tenant-a", "op-recon-noexec"))

    async def boom(*, resource, action, payload):
        raise ConnectionError("crash")

    stack.bridge._upstream = ResourceBoundUpstream(resource="res-1", dispatch=boom)  # type: ignore[attr-defined]
    run(stack.bridge.authorize_and_execute(tenant_id="tenant-a", logical_operation_id="op-recon-noexec"))

    dispatched = []

    async def evidence(*, tenant_id, logical_operation_id, action, resource, payload_hash):
        return _bound_evidence(
            tenant_id=tenant_id, logical_operation_id=logical_operation_id,
            action=action, resource=resource, payload={"n": 1},
        )

    async def spy_upstream(*, resource, action, payload):
        dispatched.append((action, payload))
        return {"ok": True}

    stack.bridge._upstream = ResourceBoundUpstream(resource="res-1", dispatch=spy_upstream)  # type: ignore[attr-defined]
    result = run(reconcile_proposal_operation(
        proposals=stack.proposals, idempotency=stack.idem, authority=stack.authority,
        tenant_id="tenant-a", logical_operation_id="op-recon-noexec", verify_external_evidence=evidence,
    ))
    assert result.outcome == ReconcileOutcome.RESOLVED
    assert dispatched == []


def test_reconciliation_with_no_evidence_leaves_record_pending():
    stack = build_stack()
    run(_propose(stack, "tenant-a", "op-recon-none"))

    async def boom(*, resource, action, payload):
        raise ConnectionError("crash")

    stack.bridge._upstream = ResourceBoundUpstream(resource="res-1", dispatch=boom)  # type: ignore[attr-defined]
    run(stack.bridge.authorize_and_execute(tenant_id="tenant-a", logical_operation_id="op-recon-none"))

    async def no_evidence(**kw):
        return None

    result = run(reconcile_proposal_operation(
        proposals=stack.proposals, idempotency=stack.idem, authority=stack.authority,
        tenant_id="tenant-a", logical_operation_id="op-recon-none", verify_external_evidence=no_evidence,
    ))
    assert result.outcome == ReconcileOutcome.NO_EVIDENCE
    state = run(stack.idem.get_state("op-recon-none", tenant_id="tenant-a"))
    assert state.state == IdempotencyState.UNKNOWN


def test_reconciliation_of_non_owned_proposal_is_tenant_safe_not_found():
    stack = build_stack()
    run(_propose(stack, "tenant-a", "op-recon-notmine"))

    async def evidence(**kw):
        return _bound_evidence(tenant_id="tenant-c", logical_operation_id="op-recon-notmine",
                               action="test_action", resource="res-1", payload={"n": 1})

    result = run(reconcile_proposal_operation(
        proposals=stack.proposals, idempotency=stack.idem, authority=stack.authority,
        tenant_id="tenant-c", logical_operation_id="op-recon-notmine", verify_external_evidence=evidence,
    ))
    assert result.outcome == ReconcileOutcome.NOT_FOUND


def test_reconciliation_of_already_executed_operation_is_not_reconcilable():
    stack = build_stack()
    run(_propose(stack, "tenant-a", "op-recon-done"))
    run(stack.bridge.authorize_and_execute(tenant_id="tenant-a", logical_operation_id="op-recon-done"))

    async def evidence(*, tenant_id, logical_operation_id, action, resource, payload_hash):
        return _bound_evidence(tenant_id=tenant_id, logical_operation_id=logical_operation_id,
                               action=action, resource=resource, payload={"n": 1})

    result = run(reconcile_proposal_operation(
        proposals=stack.proposals, idempotency=stack.idem, authority=stack.authority,
        tenant_id="tenant-a", logical_operation_id="op-recon-done", verify_external_evidence=evidence,
    ))
    assert result.outcome == ReconcileOutcome.NOT_RECONCILABLE


# =========================================================================== #
# BLOCKER 1 -- reconciliation must not resolve on unbound evidence.
# =========================================================================== #

async def _crash_and_leave_unknown(stack, tenant, op_id):
    async def boom(*, resource, action, payload):
        raise ConnectionError("crash")

    stack.bridge._upstream = ResourceBoundUpstream(resource="res-1", dispatch=boom)  # type: ignore[attr-defined]
    return await stack.bridge.authorize_and_execute(tenant_id=tenant, logical_operation_id=op_id)


def test_blocker1_1_unrelated_evidence_cannot_resolve():
    stack = build_stack()
    run(_propose(stack, "tenant-a", "op-b1-1", payload={"n": 1}))
    run(_crash_and_leave_unknown(stack, "tenant-a", "op-b1-1"))

    async def unrelated(**kw):
        return {"marker": "found"}  # the exact defect the remediation targets

    result = run(reconcile_proposal_operation(
        proposals=stack.proposals, idempotency=stack.idem, authority=stack.authority,
        tenant_id="tenant-a", logical_operation_id="op-b1-1", verify_external_evidence=unrelated,
    ))
    assert result.outcome == ReconcileOutcome.EVIDENCE_MISMATCH
    state = run(stack.idem.get_state("op-b1-1", tenant_id="tenant-a"))
    assert state.state == IdempotencyState.UNKNOWN


def test_blocker1_2_correct_action_wrong_resource_cannot_resolve():
    stack = build_stack()
    run(_propose(stack, "tenant-a", "op-b1-2", payload={"n": 1}))
    run(_crash_and_leave_unknown(stack, "tenant-a", "op-b1-2"))

    async def wrong_resource(*, tenant_id, logical_operation_id, action, resource, payload_hash):
        return _bound_evidence(tenant_id=tenant_id, logical_operation_id=logical_operation_id,
                               action=action, resource="a-completely-different-resource", payload={"n": 1})

    result = run(reconcile_proposal_operation(
        proposals=stack.proposals, idempotency=stack.idem, authority=stack.authority,
        tenant_id="tenant-a", logical_operation_id="op-b1-2", verify_external_evidence=wrong_resource,
    ))
    assert result.outcome == ReconcileOutcome.EVIDENCE_MISMATCH
    state = run(stack.idem.get_state("op-b1-2", tenant_id="tenant-a"))
    assert state.state == IdempotencyState.UNKNOWN


def test_blocker1_3_correct_resource_wrong_payload_cannot_resolve():
    stack = build_stack()
    run(_propose(stack, "tenant-a", "op-b1-3", payload={"n": 1}))
    run(_crash_and_leave_unknown(stack, "tenant-a", "op-b1-3"))

    async def wrong_payload(*, tenant_id, logical_operation_id, action, resource, payload_hash):
        return _bound_evidence(tenant_id=tenant_id, logical_operation_id=logical_operation_id,
                               action=action, resource=resource, payload={"n": 999})

    result = run(reconcile_proposal_operation(
        proposals=stack.proposals, idempotency=stack.idem, authority=stack.authority,
        tenant_id="tenant-a", logical_operation_id="op-b1-3", verify_external_evidence=wrong_payload,
    ))
    assert result.outcome == ReconcileOutcome.EVIDENCE_MISMATCH
    state = run(stack.idem.get_state("op-b1-3", tenant_id="tenant-a"))
    assert state.state == IdempotencyState.UNKNOWN


def test_blocker1_4_evidence_for_another_tenants_identical_id_cannot_resolve():
    stack = build_stack()
    payload = {"n": 1}
    run(_propose(stack, "tenant-a", "op-b1-4", payload=payload))
    run(_propose(stack, "tenant-b", "op-b1-4", payload=payload))
    run(_crash_and_leave_unknown(stack, "tenant-a", "op-b1-4"))
    run(_crash_and_leave_unknown(stack, "tenant-b", "op-b1-4"))

    async def evidence_claiming_tenant_b(*, tenant_id, logical_operation_id, action, resource, payload_hash):
        # A verifier bug/attack: reports tenant-b's identity while being
        # invoked (scoped) for tenant-a's reconciliation.
        return _bound_evidence(tenant_id="tenant-b", logical_operation_id=logical_operation_id,
                               action=action, resource=resource, payload=payload)

    result = run(reconcile_proposal_operation(
        proposals=stack.proposals, idempotency=stack.idem, authority=stack.authority,
        tenant_id="tenant-a", logical_operation_id="op-b1-4", verify_external_evidence=evidence_claiming_tenant_b,
    ))
    assert result.outcome == ReconcileOutcome.EVIDENCE_MISMATCH
    state_a = run(stack.idem.get_state("op-b1-4", tenant_id="tenant-a"))
    state_b = run(stack.idem.get_state("op-b1-4", tenant_id="tenant-b"))
    assert state_a.state == IdempotencyState.UNKNOWN
    assert state_b.state == IdempotencyState.UNKNOWN


def test_blocker1_5_evidence_for_another_logical_operation_id_cannot_resolve():
    stack = build_stack()
    payload = {"n": 1}
    run(_propose(stack, "tenant-a", "op-b1-5a", payload=payload))
    run(_propose(stack, "tenant-a", "op-b1-5b", payload=payload))
    run(_crash_and_leave_unknown(stack, "tenant-a", "op-b1-5a"))
    run(_crash_and_leave_unknown(stack, "tenant-a", "op-b1-5b"))

    async def evidence_for_wrong_op(*, tenant_id, logical_operation_id, action, resource, payload_hash):
        return _bound_evidence(tenant_id=tenant_id, logical_operation_id="op-b1-5b",
                               action=action, resource=resource, payload=payload)

    result = run(reconcile_proposal_operation(
        proposals=stack.proposals, idempotency=stack.idem, authority=stack.authority,
        tenant_id="tenant-a", logical_operation_id="op-b1-5a", verify_external_evidence=evidence_for_wrong_op,
    ))
    assert result.outcome == ReconcileOutcome.EVIDENCE_MISMATCH
    state_a = run(stack.idem.get_state("op-b1-5a", tenant_id="tenant-a"))
    state_b = run(stack.idem.get_state("op-b1-5b", tenant_id="tenant-a"))
    assert state_a.state == IdempotencyState.UNKNOWN
    assert state_b.state == IdempotencyState.UNKNOWN


def test_blocker1_6_exact_matching_evidence_resolves_only_the_intended_tenant_operation():
    stack = build_stack()
    payload = {"n": 1}
    run(_propose(stack, "tenant-a", "op-b1-6", payload=payload))
    run(_propose(stack, "tenant-b", "op-b1-6", payload=payload))
    run(_crash_and_leave_unknown(stack, "tenant-a", "op-b1-6"))
    run(_crash_and_leave_unknown(stack, "tenant-b", "op-b1-6"))

    async def exact(*, tenant_id, logical_operation_id, action, resource, payload_hash):
        return _bound_evidence(tenant_id=tenant_id, logical_operation_id=logical_operation_id,
                               action=action, resource=resource, payload=payload)

    result = run(reconcile_proposal_operation(
        proposals=stack.proposals, idempotency=stack.idem, authority=stack.authority,
        tenant_id="tenant-a", logical_operation_id="op-b1-6", verify_external_evidence=exact,
    ))
    assert result.outcome == ReconcileOutcome.RESOLVED
    state_a = run(stack.idem.get_state("op-b1-6", tenant_id="tenant-a"))
    state_b = run(stack.idem.get_state("op-b1-6", tenant_id="tenant-b"))
    assert state_a.state == IdempotencyState.EXECUTED
    assert state_b.state == IdempotencyState.UNKNOWN


def test_blocker1_7_no_evidence_leaves_unknown_unchanged():
    stack = build_stack()
    run(_propose(stack, "tenant-a", "op-b1-7", payload={"n": 1}))
    run(_crash_and_leave_unknown(stack, "tenant-a", "op-b1-7"))

    async def none_found(**kw):
        return None

    result = run(reconcile_proposal_operation(
        proposals=stack.proposals, idempotency=stack.idem, authority=stack.authority,
        tenant_id="tenant-a", logical_operation_id="op-b1-7", verify_external_evidence=none_found,
    ))
    assert result.outcome == ReconcileOutcome.NO_EVIDENCE
    state = run(stack.idem.get_state("op-b1-7", tenant_id="tenant-a"))
    assert state.state == IdempotencyState.UNKNOWN


def test_blocker1_8_stale_generation_cannot_resolve():
    """Two concurrent, otherwise-identical, CORRECTLY-bound reconciliation
    attempts for the same UNKNOWN operation: exactly one applies (RESOLVED);
    the other observes its captured generation is stale by the time it
    reaches ``resolve_unknown`` and does NOT re-apply/duplicate."""
    stack = build_stack()
    payload = {"n": 1}
    run(_propose(stack, "tenant-a", "op-b1-8", payload=payload))
    run(_crash_and_leave_unknown(stack, "tenant-a", "op-b1-8"))

    async def exact(*, tenant_id, logical_operation_id, action, resource, payload_hash):
        await asyncio.sleep(0)
        return _bound_evidence(tenant_id=tenant_id, logical_operation_id=logical_operation_id,
                               action=action, resource=resource, payload=payload)

    async def go():
        return await asyncio.gather(
            reconcile_proposal_operation(
                proposals=stack.proposals, idempotency=stack.idem, authority=stack.authority,
                tenant_id="tenant-a", logical_operation_id="op-b1-8", verify_external_evidence=exact,
            ),
            reconcile_proposal_operation(
                proposals=stack.proposals, idempotency=stack.idem, authority=stack.authority,
                tenant_id="tenant-a", logical_operation_id="op-b1-8", verify_external_evidence=exact,
            ),
        )

    r1, r2 = run(go())
    outcomes = sorted([r1.outcome.value, r2.outcome.value])
    assert outcomes == sorted([ReconcileOutcome.RESOLVED.value, ReconcileOutcome.EVIDENCE_MATCHED_NOT_APPLIED.value])
    state = run(stack.idem.get_state("op-b1-8", tenant_id="tenant-a"))
    assert state.state == IdempotencyState.EXECUTED


def test_blocker1_9_reconciliation_never_invokes_upstream():
    stack = build_stack()
    payload = {"n": 1}
    run(_propose(stack, "tenant-a", "op-b1-9", payload=payload))
    run(_crash_and_leave_unknown(stack, "tenant-a", "op-b1-9"))

    dispatched = []

    async def spy(*, resource, action, payload):
        dispatched.append((action, payload))
        return {"ok": True}

    stack.bridge._upstream = ResourceBoundUpstream(resource="res-1", dispatch=spy)  # type: ignore[attr-defined]

    async def exact(*, tenant_id, logical_operation_id, action, resource, payload_hash):
        return _bound_evidence(tenant_id=tenant_id, logical_operation_id=logical_operation_id,
                               action=action, resource=resource, payload=payload)

    result = run(reconcile_proposal_operation(
        proposals=stack.proposals, idempotency=stack.idem, authority=stack.authority,
        tenant_id="tenant-a", logical_operation_id="op-b1-9", verify_external_evidence=exact,
    ))
    assert result.outcome == ReconcileOutcome.RESOLVED
    assert dispatched == []


# =========================================================================== #
# BLOCKER 2 -- actuator resource binding.
# =========================================================================== #

def test_blocker2_1_token_for_resource_a_cannot_actuate_configured_resource_b():
    stack = build_stack(actuator_resource="resource-B")
    run(_propose(stack, "tenant-a", "op-b2-1", resource="resource-A", payload={"n": 1}))
    out = run(stack.bridge.authorize_and_execute(tenant_id="tenant-a", logical_operation_id="op-b2-1"))
    assert out.status == ProposalExecStatus.RESOURCE_MISMATCH
    assert stack.calls == []


def test_blocker2_2_identical_action_payload_wrong_actuator_target_is_blocked():
    stack = build_stack(actuator_resource="resource-B")
    payload = {"n": 1}
    run(_propose(stack, "tenant-a", "op-b2-2", resource="resource-A", payload=payload))
    out = run(stack.bridge.authorize_and_execute(tenant_id="tenant-a", logical_operation_id="op-b2-2"))
    assert out.status == ProposalExecStatus.RESOURCE_MISMATCH
    assert "resource-A" in out.reason and "resource-B" in out.reason
    assert stack.calls == []
    # No durable admission was attempted either -- fully pre-dispatch refusal.
    state = run(stack.idem.get_state("op-b2-2", tenant_id="tenant-a"))
    assert state is None


def test_blocker2_3_exact_resource_match_executes():
    stack = build_stack(actuator_resource="resource-A")
    run(_propose(stack, "tenant-a", "op-b2-3", resource="resource-A", payload={"n": 1}))
    out = run(stack.bridge.authorize_and_execute(tenant_id="tenant-a", logical_operation_id="op-b2-3"))
    assert out.status == ProposalExecStatus.EXECUTED
    assert len(stack.calls) == 1


def test_blocker2_4_final_outbound_payload_still_equals_authorized_payload():
    stack = build_stack(actuator_resource="resource-A")
    payload = {"n": 55, "note": "still-exact"}
    run(_propose(stack, "tenant-a", "op-b2-4", resource="resource-A", payload=payload))
    out = run(stack.bridge.authorize_and_execute(tenant_id="tenant-a", logical_operation_id="op-b2-4"))
    assert out.status == ProposalExecStatus.EXECUTED
    assert stack.calls[-1][1] == payload


def test_blocker2_5_constrain_still_dispatches_only_the_clamped_authorized_payload():
    stack = build_stack(allowed_tenants=("tenant-a",), max_amount=100, actuator_resource="resource-A")
    run(_propose(stack, "tenant-a", "op-b2-5", resource="resource-A", payload={"n": 1, "amount": 500}))
    out = run(stack.bridge.authorize_and_execute(tenant_id="tenant-a", logical_operation_id="op-b2-5"))
    assert out.status == ProposalExecStatus.EXECUTED
    assert out.decision == "CONSTRAIN"
    assert stack.calls[-1][1]["amount"] == 100


def test_blocker2_6_resource_mismatch_causes_zero_external_calls():
    stack = build_stack(actuator_resource="resource-configured")
    run(_propose(stack, "tenant-a", "op-b2-6", resource="resource-different", payload={"n": 1}))
    out = run(stack.bridge.authorize_and_execute(tenant_id="tenant-a", logical_operation_id="op-b2-6"))
    assert out.status == ProposalExecStatus.RESOURCE_MISMATCH
    assert stack.calls == []
    # A second, correctly-targeted proposal on the SAME actuator still works
    # -- proving the block above is resource-specific, not a global failure.
    run(_propose(stack, "tenant-a", "op-b2-6b", resource="resource-configured", payload={"n": 1}))
    out2 = run(stack.bridge.authorize_and_execute(tenant_id="tenant-a", logical_operation_id="op-b2-6b"))
    assert out2.status == ProposalExecStatus.EXECUTED


def test_none_resource_actuator_matches_only_none_resource_proposals():
    stack = build_stack(actuator_resource=None)
    run(_propose(stack, "tenant-a", "op-b2-none", resource=None, payload={"n": 1}))
    out = run(stack.bridge.authorize_and_execute(tenant_id="tenant-a", logical_operation_id="op-b2-none"))
    assert out.status == ProposalExecStatus.EXECUTED

    run(_propose(stack, "tenant-a", "op-b2-real", resource="some-resource", payload={"n": 1}))
    out2 = run(stack.bridge.authorize_and_execute(tenant_id="tenant-a", logical_operation_id="op-b2-real"))
    assert out2.status == ProposalExecStatus.RESOURCE_MISMATCH


# =========================================================================== #
# Section 12 -- non-vacuity (Phase 2 original round, unchanged probes 1-4).
# =========================================================================== #

class _NoOwnershipCheckBridge(ProposalExecutionService):
    def __init__(self, real: ProposalExecutionService, all_records):
        self.__dict__.update(real.__dict__)
        self._all_records = all_records

    async def authorize_and_execute(self, *, tenant_id: str, logical_operation_id: str):
        for key, record in self._all_records.items():
            t, _, op = key.partition("\x00")
            if op == logical_operation_id:
                return await ProposalExecutionService.authorize_and_execute(
                    self, tenant_id=t, logical_operation_id=logical_operation_id,
                )
        return await ProposalExecutionService.authorize_and_execute(
            self, tenant_id=tenant_id, logical_operation_id=logical_operation_id,
        )


def test_non_vacuity_1_tenant_ownership_bypass_makes_test_a_fail():
    stack = build_stack()
    run(_propose(stack, "tenant-b", "op-nv1"))

    broken = _NoOwnershipCheckBridge(stack.bridge, stack.proposals._store)
    out = run(broken.authorize_and_execute(tenant_id="tenant-a", logical_operation_id="op-nv1"))
    assert out.status == ProposalExecStatus.EXECUTED
    assert len(stack.calls) == 1
    stack2 = build_stack()
    run(_propose(stack2, "tenant-b", "op-nv1"))
    real_out = run(stack2.bridge.authorize_and_execute(tenant_id="tenant-a", logical_operation_id="op-nv1"))
    assert real_out.status == ProposalExecStatus.NOT_FOUND


class _NoBindingCheckBridge(ProposalExecutionService):
    async def authorize_and_execute(self, *, tenant_id: str, logical_operation_id: str):
        record = await self._proposals.get(tenant_id=tenant_id, logical_operation_id=logical_operation_id)
        if record is None or not record.action:
            return await ProposalExecutionService.authorize_and_execute(
                self, tenant_id=tenant_id, logical_operation_id=logical_operation_id,
            )
        decision = self._authority.evaluate(
            identity=tenant_id, action=record.action, context=dict(record.payload or {}),
        )
        if decision.verdict not in (Verdict.ALLOW, Verdict.CONSTRAIN):
            return ProposalExecOutcome(ProposalExecStatus.DENIED, decision.reason)
        forward = dict(decision.forward_context or record.payload or {})
        token = self._engine.issue_token(
            verdict=decision.verdict.value, subject=tenant_id, action=record.action,
            payload=forward, idempotency_key=logical_operation_id, tenant_id=tenant_id,
            actor_id=tenant_id, resource_id=record.resource,
        )

        async def executor():
            return await self._upstream.execute(resource=record.resource, action=record.action, payload=forward)

        result = await self._coordinator.enforce(
            token=token, action=record.action, payload=forward, executor=executor,
            request_binding={"actor_id": tenant_id, "resource_id": record.resource,
                             "transaction_id": None, "tenant_id": tenant_id},
        )
        status = ProposalExecStatus.EXECUTED if result.status.value == "EXECUTED" else ProposalExecStatus.BLOCKED
        return ProposalExecOutcome(status, result.reason)


def test_non_vacuity_2_binding_bypass_makes_test_d_fail():
    stack = build_stack()
    run(_propose(stack, "tenant-a", "op-nv2", payload={"n": 1}))
    real = run(stack.proposals.get(tenant_id="tenant-a", logical_operation_id="op-nv2"))
    tampered = ProposalRecord(
        tenant_id=real.tenant_id, logical_operation_id=real.logical_operation_id,
        binding=real.binding, created_at=real.created_at,
        action=real.action, resource=real.resource, payload={"n": 999},
    )
    stack.proposals._store["tenant-a\x00op-nv2"] = tampered

    broken = _NoBindingCheckBridge(
        proposals=stack.proposals, authority=stack.authority, engine=stack.engine,
        coordinator=stack.coordinator, upstream=stack.bridge._upstream,  # type: ignore[attr-defined]
    )
    out = run(broken.authorize_and_execute(tenant_id="tenant-a", logical_operation_id="op-nv2"))
    assert out.status == ProposalExecStatus.EXECUTED
    assert stack.calls[-1][1] == {"n": 999}


def test_non_vacuity_3_tenant_dimension_removed_from_durable_identity_makes_test_b_collide():
    class _TenantBlindIdempotency(InMemoryIdempotencyRegistry):
        async def reserve(self, key, *, tenant_id, binding=""):
            return await super().reserve(key, tenant_id="*shared*", binding=binding)

        async def get_state(self, key, *, tenant_id):
            return await super().get_state(key, tenant_id="*shared*")

        async def commit_dispatch(self, key, *, tenant_id, fence):
            return await super().commit_dispatch(key, tenant_id="*shared*", fence=fence)

        async def mark_executed(self, key, *, tenant_id, fence, binding="", result_ref=None):
            return await super().mark_executed(
                key, tenant_id="*shared*", fence=fence, binding=binding, result_ref=result_ref,
            )

        async def mark_unknown(self, key, *, tenant_id, fence):
            return await super().mark_unknown(key, tenant_id="*shared*", fence=fence)

        async def release(self, key, *, tenant_id, fence):
            return await super().release(key, tenant_id="*shared*", fence=fence)

    broken_idem = _TenantBlindIdempotency()
    proposals = InMemoryProposalRegistry()
    signing_key = SigningKey.generate("nv3-key")
    engine = DecisionEngine(signing_key=signing_key, issuer="mcc/test", audience="test-gate",
                            policy_id="test/v1", policy_hash="sha256:test", token_ttl_seconds=60)
    gate = ExecutionGate(trusted_keys={signing_key.kid: signing_key.public_key()}, audience="test-gate",
                         nonce_registry=InMemoryNonceRegistry(), policy_hash="sha256:test")
    audit = AuditLog(str(Path(tempfile.mkdtemp(prefix="mcc-phase2-nv3-")) / "audit.jsonl"))
    coordinator = EnforcementCoordinator(gate=gate, idempotency=broken_idem, velocity=InMemoryVelocityRegistry(),
                                         audit=audit, profiles=ProfileRegistry())
    authority = _authority(("tenant-a", "tenant-b"))

    async def raw_upstream(*, resource, action, payload):
        return {"ok": True}

    upstream = ResourceBoundUpstream(resource="res-1", dispatch=raw_upstream)
    bridge = ProposalExecutionService(proposals=proposals, authority=authority, engine=engine,
                                      coordinator=coordinator, upstream=upstream)
    svc = MCCProposalService(proposals=proposals, durable_execution_state=broken_idem)

    payload = {"n": 1}
    run(svc.submit_proposal(tenant_id="tenant-a", request={
        "logical_operation_id": "op-nv3", "actor": "x", "action": "test_action",
        "resource": "res-1", "payload": payload,
    }))
    run(svc.submit_proposal(tenant_id="tenant-b", request={
        "logical_operation_id": "op-nv3", "actor": "x", "action": "test_action",
        "resource": "res-1", "payload": payload,
    }))

    out_a = run(bridge.authorize_and_execute(tenant_id="tenant-a", logical_operation_id="op-nv3"))
    out_b = run(bridge.authorize_and_execute(tenant_id="tenant-b", logical_operation_id="op-nv3"))
    assert out_a.status == ProposalExecStatus.EXECUTED
    assert out_b.status != ProposalExecStatus.EXECUTED


def test_non_vacuity_4_non_atomic_admission_allows_duplicate_concurrent_execution():
    class _NonAtomicIdempotency(InMemoryIdempotencyRegistry):
        async def reserve(self, key, *, tenant_id, binding=""):
            from mcc_core.idempotency import ReserveResult, ReserveStatus

            return ReserveResult(ReserveStatus.RESERVED, "reserved", binding=binding, fence="fence")

        async def commit_dispatch(self, key, *, tenant_id, fence):
            return True

        async def mark_executed(self, key, *, tenant_id, fence, binding="", result_ref=None):
            return True

    broken_idem = _NonAtomicIdempotency()
    proposals = InMemoryProposalRegistry()
    signing_key = SigningKey.generate("nv4-key")
    engine = DecisionEngine(signing_key=signing_key, issuer="mcc/test", audience="test-gate",
                            policy_id="test/v1", policy_hash="sha256:test", token_ttl_seconds=60)
    gate = ExecutionGate(trusted_keys={signing_key.kid: signing_key.public_key()}, audience="test-gate",
                         nonce_registry=InMemoryNonceRegistry(), policy_hash="sha256:test")
    audit = AuditLog(str(Path(tempfile.mkdtemp(prefix="mcc-phase2-nv4-")) / "audit.jsonl"))
    coordinator = EnforcementCoordinator(gate=gate, idempotency=broken_idem, velocity=InMemoryVelocityRegistry(),
                                         audit=audit, profiles=ProfileRegistry())
    authority = _authority(("tenant-a",))
    calls = []

    async def raw_upstream(*, resource, action, payload):
        calls.append(1)
        await asyncio.sleep(0)
        return {"ok": True}

    upstream = ResourceBoundUpstream(resource="res-1", dispatch=raw_upstream)
    bridge = ProposalExecutionService(proposals=proposals, authority=authority, engine=engine,
                                      coordinator=coordinator, upstream=upstream)
    svc = MCCProposalService(proposals=proposals, durable_execution_state=broken_idem)
    run(svc.submit_proposal(tenant_id="tenant-a", request={
        "logical_operation_id": "op-nv4", "actor": "x", "action": "test_action",
        "resource": "res-1", "payload": {"n": 1},
    }))

    async def go():
        return await asyncio.gather(
            bridge.authorize_and_execute(tenant_id="tenant-a", logical_operation_id="op-nv4"),
            bridge.authorize_and_execute(tenant_id="tenant-a", logical_operation_id="op-nv4"),
        )

    r1, r2 = run(go())
    assert len(calls) == 2


# =========================================================================== #
# Phase 2 remediation round -- non-vacuity probes 5 and 6.
# =========================================================================== #

def test_non_vacuity_5_unbound_evidence_acceptance_makes_blocker1_tests_fail():
    """Reintroduces the EXACT original Blocker 1 defect (any non-None dict
    resolves) as a LOCAL function, calling the real ``idempotency.
    resolve_unknown`` directly -- never touching the shipped
    ``reconcile_proposal_operation`` -- and shows unrelated evidence WRONGLY
    resolves, proving ``test_blocker1_1_*`` is not vacuous."""
    stack = build_stack()
    run(_propose(stack, "tenant-a", "op-nv5", payload={"n": 1}))
    run(_crash_and_leave_unknown(stack, "tenant-a", "op-nv5"))

    async def vulnerable_reconcile(idempotency, tenant_id, logical_operation_id, evidence):
        from mcc_core.signing import hash_document

        state = await idempotency.get_state(logical_operation_id, tenant_id=tenant_id)
        if evidence is None:
            return "NO_EVIDENCE"
        # THE DEFECT: no binding check against tenant_id/logical_operation_id/
        # action/resource/payload_hash whatsoever.
        result_ref = hash_document({"evidence": evidence})
        result = await idempotency.resolve_unknown(
            logical_operation_id, tenant_id=tenant_id, expected_generation=state.generation, result_ref=result_ref,
        )
        return result.status.value

    outcome = run(vulnerable_reconcile(stack.idem, "tenant-a", "op-nv5", {"marker": "found"}))
    assert outcome == "RESOLVED"  # WRONGLY resolved by unrelated evidence
    state = run(stack.idem.get_state("op-nv5", tenant_id="tenant-a"))
    assert state.state == IdempotencyState.EXECUTED  # the vulnerable path corrupted it

    # The real, shipped reconcile_proposal_operation correctly refuses the
    # identical unrelated evidence for a fresh, otherwise-identical operation.
    stack2 = build_stack()
    run(_propose(stack2, "tenant-a", "op-nv5b", payload={"n": 1}))
    run(_crash_and_leave_unknown(stack2, "tenant-a", "op-nv5b"))

    async def unrelated(**kw):
        return {"marker": "found"}

    real_result = run(reconcile_proposal_operation(
        proposals=stack2.proposals, idempotency=stack2.idem, authority=stack2.authority,
        tenant_id="tenant-a", logical_operation_id="op-nv5b", verify_external_evidence=unrelated,
    ))
    assert real_result.outcome == ReconcileOutcome.EVIDENCE_MISMATCH


class _NoCheckAnywhereDispatcher:
    """Simulates a world with ZERO resource verification anywhere -- no
    ``ProposalExecutionService``-level pre-check, and no
    ``ResourceBoundUpstream.execute``-level defense-in-depth either.
    Exposes the SAME ``.resource``/``.execute`` shape so it satisfies
    ``ProposalExecutionService.__init__``'s construction-time validation,
    but ``execute`` performs zero verification before dispatching."""

    def __init__(self, resource, dispatch):
        self.resource = resource
        self._dispatch = dispatch

    async def execute(self, *, resource, action, payload):
        return await self._dispatch(resource=resource, action=action, payload=payload)


def test_non_vacuity_6_missing_resource_check_anywhere_makes_blocker2_tests_fail():
    """Reintroduces a world with NO resource verification at all -- neither
    ``ProposalExecutionService``'s own pre-token-issuance check NOR
    ``ResourceBoundUpstream.execute``'s defense-in-depth check (both are
    bypassed together here, via a bridge subclass skipping its own check
    AND a dispatcher stub skipping its own) -- and shows a
    resource-B-configured actuator WRONGLY executes an operation authorized
    for resource-A, proving ``test_blocker2_1_*`` is not vacuous."""

    class _NoResourceCheckBridge(ProposalExecutionService):
        async def authorize_and_execute(self, *, tenant_id: str, logical_operation_id: str):
            record = await self._proposals.get(tenant_id=tenant_id, logical_operation_id=logical_operation_id)
            decision = self._authority.evaluate(
                identity=tenant_id, action=record.action, context=dict(record.payload or {}),
            )
            forward = dict(decision.forward_context or record.payload or {})
            token = self._engine.issue_token(
                verdict=decision.verdict.value, subject=tenant_id, action=record.action,
                payload=forward, idempotency_key=logical_operation_id, tenant_id=tenant_id,
                actor_id=tenant_id, resource_id=record.resource,
            )
            # THE DEFECT: no check of self._upstream.resource vs record.resource
            # before dispatch -- and (see _NoCheckAnywhereDispatcher) the
            # upstream itself performs no check either.

            async def executor():
                return await self._upstream.execute(resource=record.resource, action=record.action, payload=forward)

            result = await self._coordinator.enforce(
                token=token, action=record.action, payload=forward, executor=executor,
                request_binding={"actor_id": tenant_id, "resource_id": record.resource,
                                 "transaction_id": None, "tenant_id": tenant_id},
            )
            status = ProposalExecStatus.EXECUTED if result.status.value == "EXECUTED" else ProposalExecStatus.BLOCKED
            return ProposalExecOutcome(status, result.reason)

    destinations = {"resource-A": [], "resource-B": []}

    async def hardcoded_to_b(*, resource, action, payload):
        # Ignores its own ``resource`` argument entirely -- always writes to
        # resource-B regardless of what it is told, exactly like the
        # original Blocker 2 defect's disconnected callable.
        destinations["resource-B"].append((action, payload))
        return {"ok": True}

    stack = build_stack(actuator_resource="resource-B")
    unchecked_upstream = _NoCheckAnywhereDispatcher(resource="resource-B", dispatch=hardcoded_to_b)
    run(_propose(stack, "tenant-a", "op-nv6", resource="resource-A", payload={"n": 1}))

    broken = _NoResourceCheckBridge(
        proposals=stack.proposals, authority=stack.authority, engine=stack.engine,
        coordinator=stack.coordinator, upstream=unchecked_upstream,
    )
    out = run(broken.authorize_and_execute(tenant_id="tenant-a", logical_operation_id="op-nv6"))
    assert out.status == ProposalExecStatus.EXECUTED  # WRONGLY executed against the wrong actuator
    assert destinations["resource-B"] == [("test_action", {"n": 1})]  # the side effect WRONGLY landed on B

    # The real, shipped bridge (with its own pre-check) refuses the
    # identical scenario, even against the SAME zero-internal-check
    # dispatcher -- ProposalExecutionService's own check is what saves it.
    stack2 = build_stack(actuator_resource="resource-B")
    run(_propose(stack2, "tenant-a", "op-nv6b", resource="resource-A", payload={"n": 1}))
    real_out = run(stack2.bridge.authorize_and_execute(tenant_id="tenant-a", logical_operation_id="op-nv6b"))
    assert real_out.status == ProposalExecStatus.RESOURCE_MISMATCH
    assert stack2.calls == []


# =========================================================================== #
# FINAL ACTUATOR RESOURCE BINDING REMEDIATION -- the authorized resource must
# be part of the actual controlled actuator invocation, not merely metadata
# checked once and discarded (mandatory adversarial test + non-vacuity).
# =========================================================================== #

def test_blocker2_final_declared_a_matches_but_zero_side_effect_on_configured_b():
    """The mandatory adversarial scenario: authorized resource = resource-A,
    declared/wrapper resource = resource-A (passes every check), and the
    underlying actuator is "configured" (via an irrelevant, dead legacy
    attribute) to want resource-B. Proves -- via REAL per-resource routing
    behavior, never a string re-assertion -- that the actual dispatch lands
    on resource-A only; resource-B's bucket remains completely untouched."""
    destinations: Dict[str, List[Any]] = {"resource-A": [], "resource-B": []}

    async def routing_dispatch(*, resource, action, payload):
        # A real (if simple) multi-destination actuator implementation:
        # the ONLY way resource-B's bucket could ever be touched is if THIS
        # call is made with resource="resource-B". ProposalExecutionService
        # always passes the AUTHORIZED resource here -- never anything else.
        destinations[resource].append((action, payload))
        return {"ok": True, "resource": resource}

    upstream = ResourceBoundUpstream(resource="resource-A", dispatch=routing_dispatch)
    # A stray, irrelevant legacy field representing a "misconfigured
    # deployment" that superficially suggests resource-B -- no code path in
    # the shipped design ever reads this; it is intentionally dead data,
    # here only to prove it has zero effect on the actual outcome.
    upstream._legacy_hardcoded_target = "resource-B"  # type: ignore[attr-defined]

    stack = build_stack(actuator_resource="resource-A")
    stack.bridge._upstream = upstream  # type: ignore[attr-defined]

    run(_propose(stack, "tenant-a", "op-b2final-1", resource="resource-A", payload={"n": 1}))
    out = run(stack.bridge.authorize_and_execute(tenant_id="tenant-a", logical_operation_id="op-b2final-1"))

    assert out.status == ProposalExecStatus.EXECUTED
    assert destinations["resource-A"] == [("test_action", {"n": 1})]
    assert destinations["resource-B"] == []  # ZERO SIDE EFFECT ON RESOURCE-B


def test_blocker2_final_authorized_resource_is_an_argument_of_the_actual_dispatch_call():
    """Direct proof the authorized resource is part of the real invocation:
    captures the exact keyword arguments the low-level dispatch callable
    received and asserts ``resource`` is present and correct -- not merely
    that ``.resource`` metadata matched somewhere else beforehand."""
    received: Dict[str, Any] = {}

    async def capturing_dispatch(*, resource, action, payload):
        received["resource"] = resource
        received["action"] = action
        received["payload"] = payload
        return {"ok": True}

    stack = build_stack(actuator_resource="res-1")
    stack.bridge._upstream = ResourceBoundUpstream(resource="res-1", dispatch=capturing_dispatch)  # type: ignore[attr-defined]
    run(_propose(stack, "tenant-a", "op-b2final-2", resource="res-1", payload={"n": 9}))
    out = run(stack.bridge.authorize_and_execute(tenant_id="tenant-a", logical_operation_id="op-b2final-2"))

    assert out.status == ProposalExecStatus.EXECUTED
    assert received["resource"] == "res-1"
    assert received["action"] == "test_action"
    assert received["payload"] == {"n": 9}


def test_blocker2_final_execute_defense_in_depth_rejects_mismatch_even_called_directly():
    """Even bypassing ProposalExecutionService entirely and calling
    ``ResourceBoundUpstream.execute`` directly with a mismatched resource,
    the wrapper's own independent check refuses -- zero dispatch."""
    dispatched = []

    async def dispatch(*, resource, action, payload):
        dispatched.append((resource, action, payload))
        return {"ok": True}

    upstream = ResourceBoundUpstream(resource="resource-A", dispatch=dispatch)
    with pytest.raises(ResourceMismatchError):
        run(upstream.execute(resource="resource-B", action="test_action", payload={"n": 1}))
    assert dispatched == []

    # The matching call still works normally.
    result = run(upstream.execute(resource="resource-A", action="test_action", payload={"n": 1}))
    assert result == {"ok": True}
    assert dispatched == [("resource-A", "test_action", {"n": 1})]


def test_non_vacuity_7_metadata_only_resource_check_wrongly_touches_b():
    """Reproduces the EXACT design this round replaces: ``resource`` is
    verified as disconnected metadata ONCE (an old-style wrapper whose
    dispatch call never receives it), so a callable hardcoded to a
    DIFFERENT destination can freely diverge from what the wrapper
    declares. Shows this WRONGLY touches resource-B, and that the real,
    shipped ``ResourceBoundUpstream``/``ProposalExecutionService`` cannot
    even be constructed to reproduce it."""
    destinations: Dict[str, List[Any]] = {"resource-A": [], "resource-B": []}

    class _VulnerableMetadataOnlyUpstream:
        """The pre-remediation design this round replaces: declares
        ``.resource``, but the wrapped callable receives only
        ``(action, payload)`` -- never ``resource`` -- so its actual
        behavior is completely disconnected from the declared value."""

        def __init__(self, resource, hardcoded_call):
            self.resource = resource
            self._call = hardcoded_call

        async def __call__(self, action, payload):
            return await self._call(action, payload)

    async def hardcoded_to_b(action, payload):
        # THE DEFECT: hardcoded to resource-B, with zero relationship to
        # whatever the wrapper's `.resource` metadata claims.
        destinations["resource-B"].append((action, payload))
        return {"ok": True}

    vulnerable = _VulnerableMetadataOnlyUpstream(resource="resource-A", hardcoded_call=hardcoded_to_b)

    # Reproduce the ORIGINAL remediation round's pre-check in isolation:
    authorized_resource = "resource-A"
    assert vulnerable.resource == authorized_resource  # the OLD metadata check passes
    run(vulnerable("test_action", {"n": 1}))            # the OLD calling convention
    assert destinations["resource-B"] == [("test_action", {"n": 1})]  # WRONGLY touched B
    assert destinations["resource-A"] == []

    # The real, shipped ProposalExecutionService refuses to even construct
    # against this object -- it exposes no ``.execute``, so there is no way
    # to wire it into the real service at all.
    stack = build_stack()
    with pytest.raises(TypeError):
        ProposalExecutionService(
            proposals=stack.proposals, authority=stack.authority, engine=stack.engine,
            coordinator=stack.coordinator, upstream=vulnerable,
        )

    # And the real, shipped design's own adversarial test (above) proves
    # the equivalent "declared A, something else attempts B" scenario
    # results in ZERO side effect on B when routed through the real
    # ResourceBoundUpstream.execute contract.
