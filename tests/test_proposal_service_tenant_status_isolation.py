"""PR #104 remediation — tenant status isolation.

Defect closed here: ``MCCProposalService.get_operation_status`` used to
consult the durable execution registry (``mcc_core.idempotency`` — globally
keyed by ``logical_operation_id``, with no tenant dimension of its own)
BEFORE ever establishing that the authenticated tenant owned that
identity. A second tenant that queried the same ``logical_operation_id`` a
first tenant had used for a REAL execution could observe that first
tenant's RESERVED/DISPATCH_OWNED/UNKNOWN/EXECUTED state and its
``proposal_binding`` — a cross-tenant disclosure.

Fix: ``get_operation_status`` now performs a tenant-scoped proposal
OWNERSHIP lookup first (``ProposalRegistry.get(tenant_id, ...)``, which was
already tenant-scoped). Only once that lookup proves this tenant registered
a proposal for this exact identity is the (still-global) durable execution
registry ever consulted. A tenant with no proposal record for an id gets
NOT_FOUND unconditionally — never RESERVED/DISPATCH_OWNED/UNKNOWN/EXECUTED,
and never a binding, regardless of what any other tenant did with that same
id, and regardless of whether the durable backend is up or down.

A second layer closed a subtler variant of the same defect: two tenants may
LEGITIMATELY register the identical raw ``logical_operation_id`` with
DIFFERENT bindings (Section 4 explicitly permits this). "Has a proposal for
this id" alone could not tell which tenant's binding a shared, globally-keyed
durable record belonged to. At the time this file was first written, that was
closed by comparing the durable record's own ``binding`` against THIS
tenant's registered binding and only disclosing on a match.

PR #105 superseded that binding-comparison mechanism: durable identity
itself is now the pair ``(tenant_id, key)`` at the registry level (see
``src/mcc_core/idempotency.py`` and ``tests/test_idempotency.py``), so
``get_operation_status`` performs a TENANT-SCOPED ``get_state(key,
tenant_id=tenant_id)`` lookup directly (Section 6) -- the registry itself,
not a binding comparison, is what proves a returned record belongs to this
tenant. Binding comparison is retained in ``service.py`` only as
defense-in-depth / internal-consistency checking within an
already-tenant-proven record. Every cross-tenant assertion below (tenant B
never observes tenant A's durable state, even for the identical raw id)
now holds structurally because of THAT tenant-scoped registry keying, not
because of a binding mismatch fallback -- proven directly by
``tests/test_idempotency.py``'s own PR #105 cross-tenant test matrix and
re-asserted here at the ``MCCProposalService`` boundary specifically.

This file proves the eight behaviors required by the original remediation
task, numbered to match; the mechanism producing each result has moved (see
above) but the observable guarantee at this boundary is unchanged and, per
requirement 8, must never regress.
"""

from __future__ import annotations

import asyncio

from mcc_core.idempotency import IdempotencyBackendUnavailable, InMemoryIdempotencyRegistry
from mcc_core.profiles import ProfileRegistry
from mcc_proposal import InMemoryProposalRegistry, MCCProposalService, OperationStatusValue
from mcc_proposal.binding import compute_proposal_binding

run = asyncio.run

BASE = {
    "actor": "agent/notify-bot", "action": "send_notification", "resource": "crm",
    "payload": {"recipient": "c-1", "message": "hi"},
}
BASE_B = {
    "actor": "agent/notify-bot", "action": "send_notification", "resource": "crm",
    "payload": {"recipient": "c-2", "message": "a completely different tenant-B operation"},
}


def _service(durable=None, proposals=None) -> MCCProposalService:
    return MCCProposalService(proposals=proposals or InMemoryProposalRegistry(), durable_execution_state=durable)


def real_binding(request: dict) -> str:
    """The exact binding a real coordinator dispatch of this
    action/resource/payload would compute -- see the identical helper and
    rationale in test_mcc_proposal_service.py."""
    return compute_proposal_binding(
        action=request["action"], resource=request["resource"], payload=request["payload"],
        profiles=ProfileRegistry.default_pilot(),
    )


# -- 1/2: an owning tenant sees the real durable state, verbatim ------------ #

def test_1_tenant_a_proposal_plus_durable_executed_is_visible_to_tenant_a():
    idem = InMemoryIdempotencyRegistry()
    svc = _service(durable=idem)
    run(svc.submit_proposal(tenant_id="tenant-a", request={"logical_operation_id": "op-1", **BASE}))
    reserve = run(idem.reserve("op-1", binding=real_binding(BASE), tenant_id="tenant-a"))
    run(idem.commit_dispatch("op-1", fence=reserve.fence, tenant_id="tenant-a"))
    run(idem.mark_executed("op-1", fence=reserve.fence, tenant_id="tenant-a"))

    s = run(svc.get_operation_status(tenant_id="tenant-a", logical_operation_id="op-1"))
    assert s.status == OperationStatusValue.EXECUTED.value


def test_2_tenant_a_proposal_plus_durable_unknown_is_visible_to_tenant_a():
    idem = InMemoryIdempotencyRegistry()
    svc = _service(durable=idem)
    run(svc.submit_proposal(tenant_id="tenant-a", request={"logical_operation_id": "op-2", **BASE}))
    reserve = run(idem.reserve("op-2", binding=real_binding(BASE), tenant_id="tenant-a"))
    run(idem.commit_dispatch("op-2", fence=reserve.fence, tenant_id="tenant-a"))
    run(idem.mark_unknown("op-2", fence=reserve.fence, tenant_id="tenant-a"))

    s = run(svc.get_operation_status(tenant_id="tenant-a", logical_operation_id="op-2"))
    assert s.status == OperationStatusValue.UNKNOWN.value  # UNKNOWN semantics not weakened


# -- 3: a non-owning tenant gets NOT_FOUND, no disclosure -------------------- #

def test_3_tenant_b_same_id_no_tenant_b_proposal_is_not_found_no_disclosure():
    idem = InMemoryIdempotencyRegistry()
    svc = _service(durable=idem)
    run(svc.submit_proposal(tenant_id="tenant-a", request={"logical_operation_id": "op-3", **BASE}))
    reserve = run(idem.reserve("op-3", binding="tenant-a-secret-binding", tenant_id="tenant-a"))
    run(idem.commit_dispatch("op-3", fence=reserve.fence, tenant_id="tenant-a"))
    run(idem.mark_executed("op-3", fence=reserve.fence, tenant_id="tenant-a"))

    s = run(svc.get_operation_status(tenant_id="tenant-b", logical_operation_id="op-3"))
    assert s.status == OperationStatusValue.NOT_FOUND.value
    # No disclosure whatsoever of tenant A's binding or durable state.
    assert s.proposal_binding is None
    assert "tenant-a-secret-binding" not in (s.detail or "")
    body = s.to_dict()
    assert "tenant-a-secret-binding" not in str(body)
    assert body.get("status") == "NOT_FOUND"
    assert "proposal_binding" not in body


def test_3b_tenant_b_same_id_not_found_even_while_durable_state_is_reserved_or_unknown():
    """Every durable state (not just EXECUTED) must stay invisible to a
    non-owning tenant."""
    for transition in ("reserved", "dispatch_owned", "unknown", "executed"):
        idem = InMemoryIdempotencyRegistry()
        svc = _service(durable=idem)
        op_id = f"op-3b-{transition}"
        run(svc.submit_proposal(tenant_id="tenant-a", request={"logical_operation_id": op_id, **BASE}))
        reserve = run(idem.reserve(op_id, binding="b", tenant_id="tenant-a"))
        if transition != "reserved":
            run(idem.commit_dispatch(op_id, fence=reserve.fence, tenant_id="tenant-a"))
        if transition == "unknown":
            run(idem.mark_unknown(op_id, fence=reserve.fence, tenant_id="tenant-a"))
        elif transition == "executed":
            run(idem.mark_executed(op_id, fence=reserve.fence, tenant_id="tenant-a"))

        s = run(svc.get_operation_status(tenant_id="tenant-b", logical_operation_id=op_id))
        assert s.status == OperationStatusValue.NOT_FOUND.value, transition
        assert s.proposal_binding is None, transition


# -- 4: independent tenants may reuse the same id with different bindings --- #

def test_4_two_tenants_independently_register_the_same_id_different_bindings():
    svc = _service()
    r_a = run(svc.submit_proposal(tenant_id="tenant-a", request={"logical_operation_id": "op-4", **BASE}))
    r_b = run(svc.submit_proposal(tenant_id="tenant-b", request={"logical_operation_id": "op-4", **BASE_B}))
    assert r_a.status == "PROPOSED"
    assert r_b.status == "PROPOSED"  # not BINDING_CONFLICT -- independent tenants
    assert r_a.proposal_binding != r_b.proposal_binding

    s_a = run(svc.get_operation_status(tenant_id="tenant-a", logical_operation_id="op-4"))
    s_b = run(svc.get_operation_status(tenant_id="tenant-b", logical_operation_id="op-4"))
    assert s_a.proposal_binding == r_a.proposal_binding
    assert s_b.proposal_binding == r_b.proposal_binding
    assert s_a.proposal_binding != s_b.proposal_binding


# -- 5: a durable record for tenant A never overrides/leaks into tenant B --- #
#
# PR #105: this now holds because the durable registry itself is
# tenant-scoped -- tenant-b's get_state("op-5", tenant_id="tenant-b") finds
# NO record at all (tenant-a's reservation lives under a structurally
# different (tenant_id, key) entry), never because of a binding mismatch.

def test_5_tenant_a_durable_record_never_overrides_or_leaks_into_tenant_b_status():
    idem = InMemoryIdempotencyRegistry()
    svc = _service(durable=idem)
    run(svc.submit_proposal(tenant_id="tenant-a", request={"logical_operation_id": "op-5", **BASE}))
    r_b = run(svc.submit_proposal(tenant_id="tenant-b", request={"logical_operation_id": "op-5", **BASE_B}))

    # Tenant A's operation reaches real EXECUTED durable state.
    reserve = run(idem.reserve("op-5", binding=real_binding(BASE), tenant_id="tenant-a"))
    run(idem.commit_dispatch("op-5", fence=reserve.fence, tenant_id="tenant-a"))
    run(idem.mark_executed("op-5", fence=reserve.fence, tenant_id="tenant-a"))

    s_a = run(svc.get_operation_status(tenant_id="tenant-a", logical_operation_id="op-5"))
    s_b = run(svc.get_operation_status(tenant_id="tenant-b", logical_operation_id="op-5"))
    assert s_a.status == OperationStatusValue.EXECUTED.value
    # Tenant B's status is computed from ITS OWN proposal only -- it must
    # never be upgraded/overridden to EXECUTED by tenant A's durable record,
    # and it must never see tenant A's proposal_binding.
    assert s_b.status == OperationStatusValue.PROPOSED.value
    assert s_b.proposal_binding == r_b.proposal_binding
    assert s_b.proposal_binding != s_a.proposal_binding


# -- 6: durable backend unavailable for an OWNED operation -> UNAVAILABLE --- #

class _DownIdempotency:
    async def get_state(self, key, *, tenant_id):
        raise IdempotencyBackendUnavailable("down")


def test_6_durable_backend_unavailable_for_owned_operation_is_unavailable():
    svc = _service(durable=_DownIdempotency())
    run(svc.submit_proposal(tenant_id="tenant-a", request={"logical_operation_id": "op-6", **BASE}))
    s = run(svc.get_operation_status(tenant_id="tenant-a", logical_operation_id="op-6"))
    assert s.status == OperationStatusValue.UNAVAILABLE.value


def test_6b_durable_backend_unavailable_for_a_non_owned_operation_is_not_found_not_unavailable():
    """The complementary, stronger case: for an id this tenant never
    proposed, backend downtime must not even distinguish "exists for someone
    else" from "does not exist" -- both are NOT_FOUND, since the durable
    registry is never consulted without proven ownership."""
    svc = _service(durable=_DownIdempotency())
    s = run(svc.get_operation_status(tenant_id="tenant-a", logical_operation_id="op-never-proposed"))
    assert s.status == OperationStatusValue.NOT_FOUND.value


# -- 7: no actuator/upstream/state-mutator invocation introduced ------------ #

class _ExplodingDurable:
    """Every method raises except get_state -- proves get_operation_status
    (now ownership-gated) still calls ONLY get_state on the durable
    registry, never a mutator, and still no actuator exists to call."""

    async def get_state(self, key, *, tenant_id):
        return None

    def __getattr__(self, name):
        def _boom(*a, **k):
            raise AssertionError(f"get_operation_status must never call {name}()")
        return _boom


def test_7_no_durable_mutator_or_actuator_call_introduced_by_the_ownership_gate():
    svc = _service(durable=_ExplodingDurable())
    run(svc.submit_proposal(tenant_id="tenant-a", request={"logical_operation_id": "op-7", **BASE}))
    s = run(svc.get_operation_status(tenant_id="tenant-a", logical_operation_id="op-7"))
    assert s.status == OperationStatusValue.PROPOSED.value  # would have raised if any mutator were called

    # Non-owning tenant: the ownership gate itself means the durable
    # registry (exploding or not) is never even reached.
    s2 = run(svc.get_operation_status(tenant_id="tenant-b", logical_operation_id="op-7"))
    assert s2.status == OperationStatusValue.NOT_FOUND.value
