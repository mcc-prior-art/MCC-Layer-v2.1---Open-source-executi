#!/usr/bin/env python3
"""End-to-end Redis smoke for the Phase 2 proposal -> authority -> execution
bridge (Section 13).

Run against a real Redis (CI provides one as a service container):

    MCC_REDIS_URL=redis://127.0.0.1:6379/0 python scripts/redis_proposal_phase2_smoke.py

Proves, against REAL Redis (``RedisProposalRegistry`` +
``RedisIdempotencyRegistry`` + ``RedisNonceRegistry`` -- not fakes), the
whole chain:

    proposal -> signed authority -> tenant-scoped durable admission
    -> execution state

and independently proves that two tenants sharing the IDENTICAL
``logical_operation_id`` (and identical action/resource/payload) do not
collide -- each gets its own durable record and its own dispatch.

No real destructive external actuator is used (Section 13): the upstream is
a safe, local, in-process async function.

Exits non-zero on any miss.
"""

from __future__ import annotations

import asyncio
import os
import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from mcc_core import (  # noqa: E402
    ActionPolicy,
    AuditLog,
    AuthorityModel,
    DecisionEngine,
    EnforcementCoordinator,
    ExecutionGate,
    InMemoryVelocityRegistry,
    MandateRegistry,
    ProfileRegistry,
    RedisIdempotencyRegistry,
    RedisNonceRegistry,
    SigningKey,
    Verdict,
)
from mcc_proposal import MCCProposalService, RedisProposalRegistry  # noqa: E402

from gateway.proposal_execution_service import ProposalExecStatus, ProposalExecutionService  # noqa: E402

URL = os.environ.get("MCC_REDIS_URL", "redis://127.0.0.1:6379/0")


async def main() -> int:
    import redis.asyncio as redis

    run_id = uuid.uuid4().hex[:8]
    client = redis.from_url(URL, decode_responses=True)
    failures = []

    proposals = RedisProposalRegistry(client, namespace=f"mcc:v1:phase2smoke-{run_id}:proposal:")
    idem = RedisIdempotencyRegistry(client, namespace=f"mcc:idem:phase2smoke-{run_id}:")
    nonces = RedisNonceRegistry(client, namespace=f"mcc:nonce:phase2smoke-{run_id}:")

    signing_key = SigningKey.generate(f"phase2-smoke-{run_id}")
    engine = DecisionEngine(
        signing_key=signing_key, issuer="mcc/phase2-smoke", audience="phase2-smoke-gate",
        policy_id="phase2-smoke/v1", policy_hash="sha256:phase2-smoke", token_ttl_seconds=60,
    )
    gate = ExecutionGate(
        trusted_keys={signing_key.kid: signing_key.public_key()}, audience="phase2-smoke-gate",
        nonce_registry=nonces, policy_hash="sha256:phase2-smoke",
    )
    audit = AuditLog(f"/tmp/mcc-phase2-smoke-{run_id}-audit.jsonl")
    coordinator = EnforcementCoordinator(
        gate=gate, idempotency=idem, velocity=InMemoryVelocityRegistry(),
        audit=audit, profiles=ProfileRegistry(),
    )

    tenant_a, tenant_b, tenant_c = f"tenant-a-{run_id}", f"tenant-b-{run_id}", f"tenant-c-{run_id}"
    authority = AuthorityModel(
        registry=MandateRegistry.from_config({
            tenant_a: [{"authority": "execute"}],
            tenant_b: [{"authority": "execute"}],
        }),
        policies=[ActionPolicy(action="smoke_action", requires="execute", on_mandate=Verdict.ALLOW,
                               without_mandate=Verdict.DENY)],
        default=Verdict.DENY,
    )

    dispatched = []

    async def upstream(action: str, payload) -> dict:
        dispatched.append((action, dict(payload)))
        return {"ok": True, "action": action}

    bridge = ProposalExecutionService(
        proposals=proposals, authority=authority, engine=engine,
        coordinator=coordinator, upstream=upstream,
    )
    svc = MCCProposalService(proposals=proposals, durable_execution_state=idem)

    # --- Chain proof: proposal -> authority -> durable admission -> execution ---
    op_id = f"op-{run_id}"
    payload = {"n": 1, "run": run_id}
    receipt = await svc.submit_proposal(tenant_id=tenant_a, request={
        "logical_operation_id": op_id, "actor": "agent/smoke", "action": "smoke_action",
        "resource": "res-1", "payload": payload,
    })
    print(f"chain: submit -> {receipt.status}")
    if receipt.status != "PROPOSED":
        failures.append(f"chain: proposal submission did not report PROPOSED ({receipt.status})")

    pre_status = await svc.get_operation_status(tenant_id=tenant_a, logical_operation_id=op_id)
    print(f"chain: status before authorization -> {pre_status.status}")
    if pre_status.status != "PROPOSED":
        failures.append(f"chain: status before authorization was not PROPOSED ({pre_status.status})")

    out = await bridge.authorize_and_execute(tenant_id=tenant_a, logical_operation_id=op_id)
    print(f"chain: authorize_and_execute -> {out.status.value} ({out.reason})")
    if out.status != ProposalExecStatus.EXECUTED:
        failures.append(f"chain: authorize_and_execute did not report EXECUTED ({out.status})")
    if dispatched != [("smoke_action", payload)]:
        failures.append(f"chain: unexpected actuator dispatch record {dispatched}")

    post_status = await svc.get_operation_status(tenant_id=tenant_a, logical_operation_id=op_id)
    print(f"chain: status after execution -> {post_status.status}")
    if post_status.status != "EXECUTED":
        failures.append(f"chain: status after execution was not EXECUTED ({post_status.status})")

    # --- Non-owned lookup stays tenant-safe (real Redis-backed registries) ---
    foreign = await bridge.authorize_and_execute(tenant_id=tenant_c, logical_operation_id=op_id)
    print(f"isolation: tenant-c authorize on tenant-a's op -> {foreign.status.value}")
    if foreign.status != ProposalExecStatus.NOT_FOUND:
        failures.append(f"isolation: non-owned tenant did not get NOT_FOUND ({foreign.status})")

    # --- Two tenants, identical logical_operation_id, do not collide ---
    shared_op = f"op-shared-{run_id}"
    shared_payload = {"n": 2, "run": run_id}
    for tenant in (tenant_a, tenant_b):
        r = await svc.submit_proposal(tenant_id=tenant, request={
            "logical_operation_id": shared_op, "actor": "agent/smoke", "action": "smoke_action",
            "resource": "res-1", "payload": shared_payload,
        })
        if r.status != "PROPOSED":
            failures.append(f"collision: {tenant} submission did not report PROPOSED ({r.status})")

    out_a = await bridge.authorize_and_execute(tenant_id=tenant_a, logical_operation_id=shared_op)
    out_b = await bridge.authorize_and_execute(tenant_id=tenant_b, logical_operation_id=shared_op)
    print(f"collision: tenant-a -> {out_a.status.value}, tenant-b -> {out_b.status.value}")
    if out_a.status != ProposalExecStatus.EXECUTED or out_b.status != ProposalExecStatus.EXECUTED:
        failures.append(
            f"collision: identical logical_operation_id across tenants did not both EXECUTE "
            f"(a={out_a.status}, b={out_b.status})"
        )
    if len(dispatched) != 3:  # 1 from the chain proof + 2 here
        failures.append(f"collision: expected 3 total actuator dispatches, got {len(dispatched)}")

    status_a = await svc.get_operation_status(tenant_id=tenant_a, logical_operation_id=shared_op)
    status_b = await svc.get_operation_status(tenant_id=tenant_b, logical_operation_id=shared_op)
    print(f"collision: post-status tenant-a={status_a.status}, tenant-b={status_b.status}")
    if status_a.status != "EXECUTED" or status_b.status != "EXECUTED":
        failures.append("collision: post-execution status did not independently report EXECUTED for both tenants")

    # --- Replay: presenting the same durable identity again is a duplicate,
    # never a second dispatch (tenant-a's op_id, re-run through the bridge) ---
    dispatched_before_replay = len(dispatched)
    replay = await bridge.authorize_and_execute(tenant_id=tenant_a, logical_operation_id=op_id)
    print(f"replay: second authorize_and_execute on the same op -> {replay.status.value}")
    if replay.status == ProposalExecStatus.EXECUTED:
        failures.append("replay: a second authorize_and_execute on an already-EXECUTED op reported EXECUTED again")
    if len(dispatched) != dispatched_before_replay:
        failures.append("replay: a second authorize_and_execute on an already-EXECUTED op caused a NEW dispatch")

    await client.aclose()

    if failures:
        print("\nREDIS PROPOSAL PHASE 2 SMOKE FAILED:")
        for f in failures:
            print("  -", f)
        return 1
    print("\nREDIS PROPOSAL PHASE 2 SMOKE PASSED: proposal->authority->tenant-scoped durable "
          "admission->execution chain holds; identical-id cross-tenant collision does not occur.")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
