"""Direct-service behavioral matrix for MCCProposalService (Section 23,
items A-P, Q-Y, Z-AB, AJ, AK-AN, AS-AT). Cross-adapter items (AO-AR) live in
``tests/proposal_conformance/``; HTTP/MCP-transport-specific items live in
``tests/test_proposal_http_api.py`` / ``tests/test_mcp_proposal_adapter.py``.
"""

from __future__ import annotations

import asyncio

import pytest

from mcc_core.idempotency import IdempotencyBackendUnavailable, InMemoryIdempotencyRegistry
from mcc_core.profiles import ProfileRegistry
from mcc_proposal import (
    InMemoryProposalRegistry,
    MCCProposalService,
    OperationStatusValue,
    ProposalBackendUnavailable,
)

run = asyncio.run

BASE = {
    "actor": "agent/notify-bot", "action": "send_notification", "resource": "crm",
    "payload": {"recipient": "c-1", "message": "hi"},
}


def service(**kwargs) -> MCCProposalService:
    kwargs.setdefault("proposals", InMemoryProposalRegistry())
    return MCCProposalService(**kwargs)


# -- A-E: mandatory logical_operation_id ------------------------------------ #

def test_a_valid_proposal_is_accepted():
    svc = service()
    r = run(svc.submit_proposal(tenant_id="t", request={"logical_operation_id": "op-a", **BASE}))
    assert r.accepted is True
    assert r.status == "PROPOSED"
    assert r.proposal_binding is not None


@pytest.mark.parametrize("bad_id,label", [
    (None, "missing"), ("", "empty"), ("   ", "whitespace"), (12345, "non-string"), ([], "non-string-list"),
])
def test_b_c_d_e_invalid_logical_operation_id_rejected(bad_id, label):
    svc = service()
    request = {**BASE}
    if bad_id is not None or label == "missing":
        request["logical_operation_id"] = bad_id
    if label == "missing":
        request.pop("logical_operation_id", None)
    r = run(svc.submit_proposal(tenant_id="t", request=request))
    assert r.accepted is False, label
    assert r.status == "REJECTED", label


# -- F-I: idempotent duplicate / binding conflict --------------------------- #

def test_f_same_id_same_binding_is_idempotent():
    svc = service()
    r1 = run(svc.submit_proposal(tenant_id="t", request={"logical_operation_id": "op-f", **BASE}))
    r2 = run(svc.submit_proposal(tenant_id="t", request={"logical_operation_id": "op-f", **BASE}))
    assert r1.status == r2.status == "PROPOSED"
    assert r1.proposal_binding == r2.proposal_binding


def test_g_same_id_different_payload_is_binding_conflict():
    svc = service()
    run(svc.submit_proposal(tenant_id="t", request={"logical_operation_id": "op-g", **BASE}))
    altered = {**BASE, "payload": {**BASE["payload"], "message": "ALTERED"}}
    r2 = run(svc.submit_proposal(tenant_id="t", request={"logical_operation_id": "op-g", **altered}))
    assert r2.status == "BINDING_CONFLICT"
    assert r2.accepted is False


def test_h_same_id_different_action_is_binding_conflict():
    svc = service()
    run(svc.submit_proposal(tenant_id="t", request={"logical_operation_id": "op-h", **BASE}))
    altered = {**BASE, "action": "restart_service", "resource": "restart_service",
              "payload": {"target": "svc-1", "environment": "staging"}}
    # keep same action-neutral profile fields but a DIFFERENT action string
    altered = {**BASE, "action": "some_other_action"}
    r2 = run(svc.submit_proposal(tenant_id="t", request={"logical_operation_id": "op-h", **altered}))
    assert r2.status == "BINDING_CONFLICT"


def test_i_same_id_different_resource_is_binding_conflict():
    svc = service()
    run(svc.submit_proposal(tenant_id="t", request={"logical_operation_id": "op-i", **BASE}))
    altered = {**BASE, "resource": "a-different-resource"}
    r2 = run(svc.submit_proposal(tenant_id="t", request={"logical_operation_id": "op-i", **altered}))
    assert r2.status == "BINDING_CONFLICT"


def test_binding_conflict_never_overwrites_the_first_accepted_binding():
    svc = service()
    r1 = run(svc.submit_proposal(tenant_id="t", request={"logical_operation_id": "op-noover", **BASE}))
    altered = {**BASE, "payload": {**BASE["payload"], "message": "ALTERED"}}
    run(svc.submit_proposal(tenant_id="t", request={"logical_operation_id": "op-noover", **altered}))
    status = run(svc.get_operation_status(tenant_id="t", logical_operation_id="op-noover"))
    assert status.proposal_binding == r1.proposal_binding


# -- J-P: no other identifier may substitute for logical_operation_id ------- #

@pytest.mark.parametrize("smuggled_field", [
    "request_id", "trace_id", "challenge_id", "approval_id", "session_id",
    "tool_call_id", "message_id", "nonce", "correlation_id",
])
def test_j_to_p_alternate_identifiers_cannot_substitute(smuggled_field):
    """Omit logical_operation_id, supply a plausible-looking alternate
    identifier field instead -- must be rejected outright, never silently
    adopted as the operation identity."""
    svc = service()
    request = {**BASE, smuggled_field: "some-other-id-value"}
    r = run(svc.submit_proposal(tenant_id="t", request=request))
    assert r.accepted is False
    assert r.status == "REJECTED"


def test_payload_cannot_replace_logical_operation_id():
    """A logical_operation_id-shaped value living only inside payload must
    never be treated as the operation identity."""
    svc = service()
    request = {**BASE, "payload": {**BASE["payload"], "logical_operation_id": "op-inside-payload"}}
    request.pop("logical_operation_id", None)
    r = run(svc.submit_proposal(tenant_id="t", request=request))
    assert r.accepted is False
    assert r.status == "REJECTED"


# -- Q-Y: status precedence -------------------------------------------------- #

def test_q_proposal_only_state_is_proposed():
    svc = service()
    run(svc.submit_proposal(tenant_id="t", request={"logical_operation_id": "op-q", **BASE}))
    s = run(svc.get_operation_status(tenant_id="t", logical_operation_id="op-q"))
    assert s.status == OperationStatusValue.PROPOSED.value


@pytest.mark.parametrize("transition,expected", [
    ("reserved", "RESERVED"),
    ("dispatch_owned", "DISPATCH_OWNED"),
    ("unknown", "UNKNOWN"),
    ("executed", "EXECUTED"),
])
def test_r_to_u_durable_states_map_verbatim(transition, expected):
    idem = InMemoryIdempotencyRegistry()
    svc = service(durable_execution_state=idem)
    run(svc.submit_proposal(tenant_id="t", request={"logical_operation_id": "op-ru", **BASE}))

    reserve = run(idem.reserve("op-ru", binding="whatever"))
    if transition == "reserved":
        s = run(svc.get_operation_status(tenant_id="t", logical_operation_id="op-ru"))
        assert s.status == expected
        return
    run(idem.commit_dispatch("op-ru", fence=reserve.fence))
    if transition == "dispatch_owned":
        s = run(svc.get_operation_status(tenant_id="t", logical_operation_id="op-ru"))
        assert s.status == expected
        return
    if transition == "unknown":
        run(idem.mark_unknown("op-ru", fence=reserve.fence))
        s = run(svc.get_operation_status(tenant_id="t", logical_operation_id="op-ru"))
        assert s.status == expected
        return
    run(idem.mark_executed("op-ru", fence=reserve.fence))
    s = run(svc.get_operation_status(tenant_id="t", logical_operation_id="op-ru"))
    assert s.status == expected


def test_v_no_proposal_and_no_durable_record_is_not_found():
    svc = service(durable_execution_state=InMemoryIdempotencyRegistry())
    s = run(svc.get_operation_status(tenant_id="t", logical_operation_id="op-never-existed"))
    assert s.status == OperationStatusValue.NOT_FOUND.value


class _DownIdempotency:
    async def get_state(self, key):
        raise IdempotencyBackendUnavailable("down")


class _DownProposals:
    async def register(self, **kwargs):
        raise ProposalBackendUnavailable("down")

    async def get(self, **kwargs):
        raise ProposalBackendUnavailable("down")


def test_w_durable_backend_uncertainty_is_unavailable_never_not_found():
    svc = service(durable_execution_state=_DownIdempotency())
    s = run(svc.get_operation_status(tenant_id="t", logical_operation_id="op-any"))
    assert s.status == OperationStatusValue.UNAVAILABLE.value
    assert s.status != OperationStatusValue.NOT_FOUND.value


def test_x_proposal_backend_uncertainty_is_unavailable_fail_closed():
    svc = service(proposals=_DownProposals())
    r = run(svc.submit_proposal(tenant_id="t", request={"logical_operation_id": "op-x", **BASE}))
    assert r.status == "UNAVAILABLE"
    s = run(svc.get_operation_status(tenant_id="t", logical_operation_id="op-x"))
    assert s.status == OperationStatusValue.UNAVAILABLE.value


def test_y_unknown_never_causes_retry_or_reservation():
    calls = {"reserve": 0}

    class _CountingIdempotency(InMemoryIdempotencyRegistry):
        async def reserve(self, *a, **k):
            calls["reserve"] += 1
            return await super().reserve(*a, **k)

    idem = _CountingIdempotency()
    svc = service(durable_execution_state=idem)
    run(svc.submit_proposal(tenant_id="t", request={"logical_operation_id": "op-y", **BASE}))
    reserve = run(idem.reserve("op-y", binding="b"))
    calls["reserve"] = 0  # reset after the direct test-setup call above
    run(idem.commit_dispatch("op-y", fence=reserve.fence))
    run(idem.mark_unknown("op-y", fence=reserve.fence))

    # Re-submitting the SAME proposal (a caller retrying) and reading status
    # repeatedly must never itself call reserve.
    for _ in range(3):
        run(svc.submit_proposal(tenant_id="t", request={"logical_operation_id": "op-y", **BASE}))
        s = run(svc.get_operation_status(tenant_id="t", logical_operation_id="op-y"))
        assert s.status == "UNKNOWN"
    assert calls["reserve"] == 0


# -- Z/AA/AB: zero state writes / zero actuator calls ------------------------ #

class _ExplodingDurable:
    """Every method raises AssertionError except get_state -- proves
    get_operation_status calls ONLY get_state, and submit_proposal never
    touches the durable registry at all."""

    async def get_state(self, key):
        return None

    def __getattr__(self, name):
        def _boom(*a, **k):
            raise AssertionError(f"get_operation_status/submit_proposal must never call {name}()")
        return _boom


def test_z_status_performs_zero_state_writes():
    svc = service(durable_execution_state=_ExplodingDurable())
    run(svc.submit_proposal(tenant_id="t", request={"logical_operation_id": "op-z", **BASE}))
    s = run(svc.get_operation_status(tenant_id="t", logical_operation_id="op-z"))
    assert s.status == "PROPOSED"  # would have raised AssertionError if any mutator were called


def test_aa_submit_proposal_never_touches_durable_execution_state():
    svc = service(durable_execution_state=_ExplodingDurable())
    r = run(svc.submit_proposal(tenant_id="t", request={"logical_operation_id": "op-aa", **BASE}))
    assert r.status == "PROPOSED"  # get_state itself was never called either


def test_ab_status_calls_proposals_get_not_register():
    calls = {"get": 0, "register": 0}

    class _Spy(InMemoryProposalRegistry):
        async def register(self, **k):
            calls["register"] += 1
            return await super().register(**k)

        async def get(self, **k):
            calls["get"] += 1
            return await super().get(**k)

    proposals = _Spy()
    svc = service(proposals=proposals)
    run(svc.submit_proposal(tenant_id="t", request={"logical_operation_id": "op-ab", **BASE}))
    calls["register"] = 0
    calls["get"] = 0
    run(svc.get_operation_status(tenant_id="t", logical_operation_id="op-ab"))
    assert calls == {"get": 1, "register": 0}


# -- AJ: authority-bearing fields cannot be honored -------------------------- #

@pytest.mark.parametrize("field", [
    "decision_token", "signed_authority", "mandate", "approval_mandate",
    "private_key", "signing_key", "trusted_issuer", "policy_override",
    "policy_hash_override", "nonce_override", "generation", "fence",
    "dispatch_owner", "resolve_unknown", "mark_executed", "actuator",
    "executor", "execute", "force", "retry_anyway",
])
def test_aj_authority_bearing_fields_rejected(field):
    svc = service()
    request = {"logical_operation_id": "op-aj", **BASE, field: "smuggled-value"}
    r = run(svc.submit_proposal(tenant_id="t", request=request))
    assert r.accepted is False
    assert r.status == "REJECTED"
    assert "AUTHORITY" in (r.reason or "")


# -- AK/AL: tenant isolation --------------------------------------------------#

def test_ak_tenant_cannot_read_another_tenants_operation():
    svc = service()
    run(svc.submit_proposal(tenant_id="tenant-a", request={"logical_operation_id": "op-shared-id", **BASE}))
    s = run(svc.get_operation_status(tenant_id="tenant-b", logical_operation_id="op-shared-id"))
    assert s.status == OperationStatusValue.NOT_FOUND.value


def test_al_tenant_cannot_conflict_with_another_tenant_via_same_id():
    """Two different tenants using the identical logical_operation_id with
    DIFFERENT bindings must both succeed independently -- no cross-tenant
    BINDING_CONFLICT, and no cross-tenant overwrite."""
    svc = service()
    r_a = run(svc.submit_proposal(tenant_id="tenant-a", request={"logical_operation_id": "op-cross", **BASE}))
    altered = {**BASE, "payload": {**BASE["payload"], "message": "tenant-b-payload"}}
    r_b = run(svc.submit_proposal(tenant_id="tenant-b", request={"logical_operation_id": "op-cross", **altered}))
    assert r_a.status == "PROPOSED"
    assert r_b.status == "PROPOSED"  # not BINDING_CONFLICT -- independent tenants
    assert r_a.proposal_binding != r_b.proposal_binding


# -- AM/AN: concurrency ------------------------------------------------------- #

def test_am_concurrent_same_binding_submission_is_atomic_one_identity():
    svc = service()

    async def go():
        return await asyncio.gather(*[
            svc.submit_proposal(tenant_id="t", request={"logical_operation_id": "op-conc-same", **BASE})
            for _ in range(20)
        ])

    results = run(go())
    assert all(r.status == "PROPOSED" for r in results)
    bindings = {r.proposal_binding for r in results}
    assert len(bindings) == 1


def test_an_concurrent_conflicting_binding_has_exactly_one_winner():
    svc = service()

    async def go():
        tasks = []
        for i in range(10):
            payload = {**BASE["payload"], "variant": i}
            tasks.append(svc.submit_proposal(
                tenant_id="t", request={"logical_operation_id": "op-conc-race", **BASE, "payload": payload},
            ))
        return await asyncio.gather(*tasks)

    results = run(go())
    proposed = [r for r in results if r.status == "PROPOSED"]
    conflicts = [r for r in results if r.status == "BINDING_CONFLICT"]
    assert len(proposed) == 1
    assert len(conflicts) == 9
    # The final durable status must match the ONE winner's binding.
    status = run(svc.get_operation_status(tenant_id="t", logical_operation_id="op-conc-race"))
    assert status.proposal_binding == proposed[0].proposal_binding


# -- AS/AT: restart / backend outage semantics ------------------------------- #

def test_as_restart_does_not_mint_a_new_logical_identity():
    """A second service instance wired to the SAME durable proposal store
    (simulating a process restart against shared/durable storage) must see
    the exact same record, never mint a fresh identity for the same
    logical_operation_id."""
    shared_registry = InMemoryProposalRegistry()
    svc1 = service(proposals=shared_registry)
    r1 = run(svc1.submit_proposal(tenant_id="t", request={"logical_operation_id": "op-restart", **BASE}))

    svc2 = MCCProposalService(proposals=shared_registry)  # "after restart"
    s2 = run(svc2.get_operation_status(tenant_id="t", logical_operation_id="op-restart"))
    assert s2.status == "PROPOSED"
    assert s2.proposal_binding == r1.proposal_binding


def test_at_backend_outage_never_becomes_not_found_or_safe_to_retry():
    svc = service(durable_execution_state=_DownIdempotency())
    s = run(svc.get_operation_status(tenant_id="t", logical_operation_id="op-outage"))
    assert s.status not in (OperationStatusValue.NOT_FOUND.value,)
    assert s.status == OperationStatusValue.UNAVAILABLE.value


# -- profile-error payloads reject cleanly (payment profile requires fields) - #

def test_binding_computation_error_surfaces_as_rejected_not_a_crash():
    profiles = ProfileRegistry.default_pilot()
    svc = service(profiles=profiles)
    # send_payment requires source/beneficiary_id/amount/currency; omit them.
    r = run(svc.submit_proposal(tenant_id="t", request={
        "logical_operation_id": "op-profile-err", "actor": "agent/payments-bot",
        "action": "send_payment", "resource": None, "payload": {},
    }))
    assert r.status == "REJECTED"
    assert r.accepted is False
