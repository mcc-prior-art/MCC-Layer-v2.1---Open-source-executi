"""Phase 2 — PROPOSAL -> SIGNED AUTHORITY -> GOVERNED EXECUTION.

Adversarial behavioral matrix (A-N) for
``gateway.proposal_execution_service.ProposalExecutionService`` /
``reconcile_proposal_operation``, plus mandatory non-vacuity probes
(Section 12). Exercises the REAL service/coordinator boundary throughout:
a real ``mcc_proposal.MCCProposalService``/``InMemoryProposalRegistry``, a
real ``mcc_core.core.DecisionEngine``/``mcc_core.gate.ExecutionGate``/
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
from mcc_proposal import InMemoryProposalRegistry, MCCProposalService
from mcc_proposal.registry import ProposalBackendUnavailable, ProposalRecord

from gateway.proposal_execution_service import (
    ProposalExecStatus,
    ProposalExecutionService,
    ReconcileOutcome,
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
                 without_mandate=Verdict.DENY):
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

    async def upstream(act: str, payload: Dict[str, Any]) -> Any:
        calls.append((act, copy.deepcopy(payload)))
        return {"ok": True, "action": act}

    bridge = ProposalExecutionService(
        proposals=proposals, authority=authority, engine=engine,
        coordinator=coordinator, upstream=upstream,
    )
    return SimpleNamespace(
        proposals=proposals, idem=idem, svc=svc, bridge=bridge, calls=calls,
        engine=engine, gate=gate, coordinator=coordinator, authority=authority,
        signing_key=signing_key, audit=audit,
    )


async def _propose(stack, tenant, op_id, *, action="test_action", resource="res-1",
                    payload=None):
    return await stack.svc.submit_proposal(tenant_id=tenant, request={
        "logical_operation_id": op_id, "actor": "agent/x", "action": action,
        "resource": resource, "payload": payload or {"n": 1},
    })


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

    # tenant-b's own call succeeds -- proving the block above is ownership,
    # not e.g. a global misconfiguration.
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

    # The ORIGINAL binding is still what gets executed -- a rejected
    # resubmission never silently overwrites the stored proposal.
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
    # Simulate a corrupted/tampered record: content changed, binding NOT
    # recomputed -- exactly what "mutated after authorization" looks like
    # at the storage layer this bridge reads from.
    tampered = ProposalRecord(
        tenant_id=real.tenant_id, logical_operation_id=real.logical_operation_id,
        binding=real.binding, created_at=real.created_at,
        action=real.action, resource=real.resource, payload={"n": 999},
    )
    stack.proposals._store[f"tenant-a\x00op-d"] = tampered

    out = run(stack.bridge.authorize_and_execute(tenant_id="tenant-a", logical_operation_id="op-d"))
    assert out.status == ProposalExecStatus.REJECTED
    assert "consistency" in out.reason
    assert stack.calls == []


# --------------------------------------------------------------------------- #
# E. Authority for Proposal A cannot execute Proposal B.
# --------------------------------------------------------------------------- #

def test_e_authority_for_proposal_a_cannot_execute_proposal_b():
    stack = build_stack()
    run(_propose(stack, "tenant-a", "op-e-a", payload={"n": 1}))
    run(_propose(stack, "tenant-a", "op-e-b", payload={"n": 2}))

    class _Capture:
        def __init__(self, real):
            self._real = real
            self.last = None

        def issue_token(self, **kw):
            tok = self._real.issue_token(**kw)
            self.last = tok
            return tok

    captured = _Capture(stack.engine)
    stack.bridge._engine = captured  # type: ignore[attr-defined]

    out_a = run(stack.bridge.authorize_and_execute(tenant_id="tenant-a", logical_operation_id="op-e-a"))
    assert out_a.status == ProposalExecStatus.EXECUTED
    token_for_a = captured.last
    assert token_for_a["idempotency_key"] == "op-e-a"

    # Reuse op-A's real, signed, verified token directly against the real
    # coordinator, but presented for op-B's action/payload/resource. The
    # Gate's own action_hash/payload_hash binding must refuse it before any
    # actuator call -- op-B's own durable record is never touched.
    async def dispatch():
        return await stack.bridge._upstream("test_action", {"n": 2})  # type: ignore[attr-defined]

    calls_before = len(stack.calls)
    result = run(stack.coordinator.enforce(
        token=token_for_a, action="test_action", payload={"n": 2}, executor=dispatch,
        request_binding={"actor_id": "tenant-a", "resource_id": "res-1",
                         "transaction_id": None, "tenant_id": "tenant-a"},
    ))
    assert result.status.value != "EXECUTED"
    assert len(stack.calls) == calls_before  # no new actuator call

    # op-B remains untouched (never admitted/executed by op-A's authority).
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

    class _Capture:
        def __init__(self, real):
            self._real = real
            self.last = None

        def issue_token(self, **kw):
            tok = self._real.issue_token(**kw)
            self.last = tok
            return tok

    captured = _Capture(stack.engine)
    stack.bridge._engine = captured  # type: ignore[attr-defined]

    out_a = run(stack.bridge.authorize_and_execute(tenant_id="tenant-a", logical_operation_id="op-f"))
    assert out_a.status == ProposalExecStatus.EXECUTED
    token_for_a = captured.last
    assert token_for_a["tenant_id"] == "tenant-a"

    # tenant-b's own record for the IDENTICAL id/binding must still be
    # independently authorized -- tenant-a's token can never substitute.
    out_b = run(stack.bridge.authorize_and_execute(tenant_id="tenant-b", logical_operation_id="op-f"))
    assert out_b.status == ProposalExecStatus.EXECUTED

    state_a = run(stack.idem.get_state("op-f", tenant_id="tenant-a"))
    state_b = run(stack.idem.get_state("op-f", tenant_id="tenant-b"))
    assert state_a.state == IdempotencyState.EXECUTED
    assert state_b.state == IdempotencyState.EXECUTED
    assert len(stack.calls) == 2  # each tenant caused exactly one dispatch


# --------------------------------------------------------------------------- #
# G. Replayed token cannot execute twice.
# --------------------------------------------------------------------------- #

def test_g_replayed_token_cannot_execute_twice():
    stack = build_stack()
    run(_propose(stack, "tenant-a", "op-g"))

    class _Capture:
        def __init__(self, real):
            self._real = real
            self.last = None

        def issue_token(self, **kw):
            tok = self._real.issue_token(**kw)
            self.last = tok
            return tok

    captured = _Capture(stack.engine)
    stack.bridge._engine = captured  # type: ignore[attr-defined]

    out = run(stack.bridge.authorize_and_execute(tenant_id="tenant-a", logical_operation_id="op-g"))
    assert out.status == ProposalExecStatus.EXECUTED
    token = captured.last

    async def dispatch():
        return await stack.bridge._upstream("test_action", {"n": 1})  # type: ignore[attr-defined]

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

    async def boom(action, payload):
        raise ConnectionError("simulated crash after dispatch")

    stack.bridge._upstream = boom  # type: ignore[attr-defined]

    out = run(stack.bridge.authorize_and_execute(tenant_id="tenant-a", logical_operation_id="op-i"))
    assert out.status == ProposalExecStatus.EXECUTION_FAILED

    state = run(stack.idem.get_state("op-i", tenant_id="tenant-a"))
    assert state.state == IdempotencyState.UNKNOWN

    # A second attempt must NOT silently retry/reopen -- it is blocked, and
    # the upstream is never called a second time.
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

    async def boom(action, p):
        raise ConnectionError("simulated crash")

    stack.bridge._upstream = boom  # type: ignore[attr-defined]
    out_a = run(stack.bridge.authorize_and_execute(tenant_id="tenant-a", logical_operation_id="op-j"))
    out_b = run(stack.bridge.authorize_and_execute(tenant_id="tenant-b", logical_operation_id="op-j"))
    assert out_a.status == ProposalExecStatus.EXECUTION_FAILED
    assert out_b.status == ProposalExecStatus.EXECUTION_FAILED

    async def evidence_for_a():
        return {"marker": "tenant-a-evidence"}

    result = run(reconcile_proposal_operation(
        proposals=stack.proposals, idempotency=stack.idem, tenant_id="tenant-a",
        logical_operation_id="op-j", verify_external_evidence=evidence_for_a,
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

    # Coordinator built directly against a down idempotency backend --
    # ``reserve`` inside ``enforce`` is expected to fail closed (matching
    # ``tests/test_idempotency.py``/``tests/test_coordinator.py`` conventions).
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

    # tenant-c never proposed anything under op-l -- the proposal-ownership
    # gate (Section 1) is checked BEFORE the durable backend is ever
    # touched, so a durable outage never surfaces for a non-owner.
    out = run(stack.bridge.authorize_and_execute(tenant_id="tenant-c", logical_operation_id="op-l"))
    assert out.status == ProposalExecStatus.NOT_FOUND
    assert stack.calls == []


# --------------------------------------------------------------------------- #
# M. Restart/persistence test using Redis semantics -- see
#    ``scripts/redis_proposal_phase2_smoke.py`` (Section 13) for the real
#    Redis version; this is the InMemory-backed restart-persistence
#    equivalent, exercising the same "fresh registry instance, same backing
#    store" pattern PR #105's own test suite uses.
# --------------------------------------------------------------------------- #

def test_m_restart_persistence_tenant_isolated_in_memory_equivalent():
    stack = build_stack()
    run(_propose(stack, "tenant-a", "op-m"))
    out = run(stack.bridge.authorize_and_execute(tenant_id="tenant-a", logical_operation_id="op-m"))
    assert out.status == ProposalExecStatus.EXECUTED

    # A fresh MCCProposalService instance over the SAME backing registries
    # ("restart" of the read path) still reports EXECUTED.
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

    class _Capture:
        def __init__(self, real):
            self._real = real
            self.last = None

        def issue_token(self, **kw):
            tok = self._real.issue_token(**kw)
            self.last = tok
            return tok

    captured = _Capture(stack.engine)
    stack.bridge._engine = captured  # type: ignore[attr-defined]

    out = run(stack.bridge.authorize_and_execute(tenant_id="tenant-a", logical_operation_id="op-n"))
    assert out.status == ProposalExecStatus.EXECUTED

    from mcc_core.signing import hash_payload

    dispatched_action, dispatched_payload = stack.calls[-1]
    assert dispatched_payload == payload
    assert hash_payload(dispatched_payload) == captured.last["payload_hash"]


# --------------------------------------------------------------------------- #
# CONSTRAIN and ESCALATE and DENY paths (round out the four-verdict matrix;
# not separately lettered above, but required by the "trusted authorization
# decision" contract and exercised the same way A-N are).
# --------------------------------------------------------------------------- #

def test_deny_path_never_issues_a_token_or_calls_upstream():
    stack = build_stack(allowed_tenants=())  # tenant-a holds no mandate
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
    assert dispatched_payload["amount"] == 100  # clamped, never the proposed 500


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
    """A Phase-1-only record (registered via the low-level registry API with
    no action/resource/payload) must never be treated as executable."""
    stack = build_stack()
    run(stack.proposals.register(tenant_id="tenant-a", logical_operation_id="op-bare", binding="sha256:whatever"))
    out = run(stack.bridge.authorize_and_execute(tenant_id="tenant-a", logical_operation_id="op-bare"))
    assert out.status == ProposalExecStatus.REJECTED
    assert stack.calls == []


# --------------------------------------------------------------------------- #
# Reconciliation edge cases beyond J.
# --------------------------------------------------------------------------- #

def test_reconciliation_never_dispatches_to_the_actuator():
    stack = build_stack()
    run(_propose(stack, "tenant-a", "op-recon-noexec"))

    async def boom(action, p):
        raise ConnectionError("crash")

    stack.bridge._upstream = boom  # type: ignore[attr-defined]
    run(stack.bridge.authorize_and_execute(tenant_id="tenant-a", logical_operation_id="op-recon-noexec"))

    dispatched = []

    async def evidence():
        return {"marker": "found"}

    async def spy_upstream(action, payload):
        dispatched.append((action, payload))
        return {"ok": True}

    stack.bridge._upstream = spy_upstream  # type: ignore[attr-defined]
    result = run(reconcile_proposal_operation(
        proposals=stack.proposals, idempotency=stack.idem, tenant_id="tenant-a",
        logical_operation_id="op-recon-noexec", verify_external_evidence=evidence,
    ))
    assert result.outcome == ReconcileOutcome.RESOLVED
    assert dispatched == []  # reconciliation itself never calls the actuator


def test_reconciliation_with_no_evidence_leaves_record_pending():
    stack = build_stack()
    run(_propose(stack, "tenant-a", "op-recon-none"))

    async def boom(action, p):
        raise ConnectionError("crash")

    stack.bridge._upstream = boom  # type: ignore[attr-defined]
    run(stack.bridge.authorize_and_execute(tenant_id="tenant-a", logical_operation_id="op-recon-none"))

    async def no_evidence():
        return None

    result = run(reconcile_proposal_operation(
        proposals=stack.proposals, idempotency=stack.idem, tenant_id="tenant-a",
        logical_operation_id="op-recon-none", verify_external_evidence=no_evidence,
    ))
    assert result.outcome == ReconcileOutcome.NO_EVIDENCE
    state = run(stack.idem.get_state("op-recon-none", tenant_id="tenant-a"))
    assert state.state == IdempotencyState.UNKNOWN


def test_reconciliation_of_non_owned_proposal_is_tenant_safe_not_found():
    stack = build_stack()
    run(_propose(stack, "tenant-a", "op-recon-notmine"))

    async def evidence():
        return {"marker": "found"}

    result = run(reconcile_proposal_operation(
        proposals=stack.proposals, idempotency=stack.idem, tenant_id="tenant-c",
        logical_operation_id="op-recon-notmine", verify_external_evidence=evidence,
    ))
    assert result.outcome == ReconcileOutcome.NOT_FOUND


def test_reconciliation_of_already_executed_operation_is_not_reconcilable():
    stack = build_stack()
    run(_propose(stack, "tenant-a", "op-recon-done"))
    run(stack.bridge.authorize_and_execute(tenant_id="tenant-a", logical_operation_id="op-recon-done"))

    async def evidence():
        return {"marker": "found"}

    result = run(reconcile_proposal_operation(
        proposals=stack.proposals, idempotency=stack.idem, tenant_id="tenant-a",
        logical_operation_id="op-recon-done", verify_external_evidence=evidence,
    ))
    assert result.outcome == ReconcileOutcome.NOT_RECONCILABLE


# =========================================================================== #
# Section 12 -- non-vacuity: prove the security-critical tests actually
# detect the defect they claim to. Each probe temporarily reintroduces the
# vulnerable behavior IN A LOCAL SUBCLASS/PATCH (never in the shipped
# implementation), confirms the SAME test method fails for the expected
# reason, then the shipped code (never modified) is what every other test
# in this file continues to run against.
# =========================================================================== #

class _NoOwnershipCheckBridge(ProposalExecutionService):
    """Non-vacuity probe #1: tenant ownership bypass. Reintroduces the exact
    defect Section 1 forbids -- looks the proposal up by
    ``logical_operation_id`` alone, ignoring which tenant is asking."""

    def __init__(self, real: ProposalExecutionService, all_records):
        self.__dict__.update(real.__dict__)
        self._all_records = all_records

    async def authorize_and_execute(self, *, tenant_id: str, logical_operation_id: str):
        # Deliberately broken: search ALL tenants' records for a matching
        # logical_operation_id, regardless of the caller's own tenant_id.
        # InMemoryProposalRegistry keys its store by "tenant\x00op".
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
    # With the ownership check bypassed, tenant-a WRONGLY reaches execution
    # against tenant-b's proposal -- proving test A would have caught this
    # exact defect had it been present in the shipped code.
    assert out.status == ProposalExecStatus.EXECUTED
    assert len(stack.calls) == 1
    # The real, shipped bridge (unmodified) still correctly refuses.
    stack2 = build_stack()
    run(_propose(stack2, "tenant-b", "op-nv1"))
    real_out = run(stack2.bridge.authorize_and_execute(tenant_id="tenant-a", logical_operation_id="op-nv1"))
    assert real_out.status == ProposalExecStatus.NOT_FOUND


class _NoBindingCheckBridge(ProposalExecutionService):
    """Non-vacuity probe #2: proposal/token payload binding bypass. Skips
    the internal-consistency recomputation Section 2 requires, so a
    corrupted/tampered stored record is executed as-is."""

    async def authorize_and_execute(self, *, tenant_id: str, logical_operation_id: str):
        record = await self._proposals.get(tenant_id=tenant_id, logical_operation_id=logical_operation_id)
        if record is None or not record.action:
            return await ProposalExecutionService.authorize_and_execute(
                self, tenant_id=tenant_id, logical_operation_id=logical_operation_id,
            )
        # Deliberately broken: NO recomputation/comparison against
        # record.binding -- straight to authority + token + enforce.
        decision = self._authority.evaluate(
            identity=tenant_id, action=record.action, context=dict(record.payload or {}),
        )
        if decision.verdict not in (Verdict.ALLOW, Verdict.CONSTRAIN):
            from gateway.proposal_execution_service import ProposalExecOutcome
            return ProposalExecOutcome(ProposalExecStatus.DENIED, decision.reason)
        forward = dict(decision.forward_context or record.payload or {})
        token = self._engine.issue_token(
            verdict=decision.verdict.value, subject=tenant_id, action=record.action,
            payload=forward, idempotency_key=logical_operation_id, tenant_id=tenant_id,
            actor_id=tenant_id, resource_id=record.resource,
        )

        async def executor():
            return await self._upstream(record.action, forward)

        result = await self._coordinator.enforce(
            token=token, action=record.action, payload=forward, executor=executor,
            request_binding={"actor_id": tenant_id, "resource_id": record.resource,
                             "transaction_id": None, "tenant_id": tenant_id},
        )
        from gateway.proposal_execution_service import ProposalExecOutcome
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
    # With the consistency check removed, the tampered payload (999) WRONGLY
    # executes -- proving test D would have caught this exact defect.
    assert out.status == ProposalExecStatus.EXECUTED
    assert stack.calls[-1][1] == {"n": 999}


def test_non_vacuity_3_tenant_dimension_removed_from_durable_identity_makes_test_b_collide():
    """Reintroduces PR #105's exact original defect (durable identity keyed
    by ``logical_operation_id`` alone) directly at the registry the bridge
    drives, and shows the SAME scenario test B proves independent now
    instead collides -- confirming test B is not vacuous."""

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

    async def upstream(action, payload):
        return {"ok": True}

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
    # With the tenant dimension collapsed, tenant-b's admission WRONGLY
    # collides with tenant-a's already-EXECUTED record instead of executing
    # independently -- proving test B is not vacuous.
    assert out_a.status == ProposalExecStatus.EXECUTED
    assert out_b.status != ProposalExecStatus.EXECUTED


def test_non_vacuity_4_non_atomic_admission_allows_duplicate_concurrent_execution():
    """Reintroduces a non-atomic (check-then-act, not compare-and-swap)
    reserve at the registry the bridge drives, and shows the SAME
    concurrent scenario test H proves single-winner now instead allows both
    concurrent callers to dispatch -- confirming test H is not vacuous."""

    class _NonAtomicIdempotency(InMemoryIdempotencyRegistry):
        """Deliberately broken: ``reserve`` always reports success without
        ever persisting admission state (no compare-and-swap, no
        durable record at all) -- the exact class of bug atomic admission
        exists to prevent. ``commit_dispatch``/``mark_executed`` similarly
        no-op successfully so the coordinator's own path completes."""

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

    async def upstream(action, payload):
        calls.append(1)
        await asyncio.sleep(0)
        return {"ok": True}

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
    # With atomicity removed, BOTH concurrent callers WRONGLY dispatch --
    # proving test H is not vacuous.
    assert len(calls) == 2
