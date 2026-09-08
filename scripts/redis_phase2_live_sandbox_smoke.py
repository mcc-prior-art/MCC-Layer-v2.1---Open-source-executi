#!/usr/bin/env python3
"""Real-Redis smoke for the Phase 2 live sandbox proof (Section 14).

Run against a real Redis AND a local mock GitHub HTTP server (no live
GitHub network access needed for this smoke -- see
``examples/phase2_live_sandbox/run_live_proof.py`` for the actual live
run):

    python scripts/redis_phase2_live_sandbox_smoke.py

Proves, against REAL Redis (``RedisProposalRegistry`` +
``RedisIdempotencyRegistry`` + ``RedisNonceRegistry`` -- never fakes) and a
real local HTTP server (never a stub client), the full chain:

    proposal -> authority -> ExecutionGate -> tenant-scoped durable
    admission -> ResourceBoundUpstream -> real HTTP dispatch -> durable
    EXECUTED

plus replay-safety and reconciliation, exactly like this repository's
other ``scripts/redis_*_smoke.py`` scripts. Does NOT replace
``scripts/redis_proposal_phase2_smoke.py`` (Section 14).

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

from examples._demo_server import DemoServer, free_port  # noqa: E402
from examples.gpt6_astra_reference.mock_github_service import (  # noqa: E402
    build_mock_github_service,
    recorded_issues,
    reset_issues,
)
from examples.phase2_live_sandbox.config import SandboxConfig  # noqa: E402
from examples.phase2_live_sandbox.marker import prepare_sandbox_issue_payload  # noqa: E402
from examples.phase2_live_sandbox.stack import build_live_sandbox_stack  # noqa: E402
from gateway.proposal_execution_service import (  # noqa: E402
    ProposalExecStatus,
    ReconcileOutcome,
    ResourceBoundUpstream,
    reconcile_proposal_operation,
)

REDIS_URL = os.environ.get("MCC_REDIS_URL", "redis://127.0.0.1:6379/0")


async def main() -> int:
    run_id = uuid.uuid4().hex[:8]
    reset_issues()
    port = free_port()
    server = DemoServer(build_mock_github_service(), port).start()
    base_url = f"http://127.0.0.1:{port}"
    failures = []

    config = SandboxConfig(
        live=True, repo=f"sandbox-owner/sandbox-repo-{run_id}", base_url=base_url, token=None, redis_url=REDIS_URL,
    )
    tenant_a, tenant_b = f"tenant-a-{run_id}", f"tenant-b-{run_id}"
    op_id = f"op-{run_id}"

    stack = await build_live_sandbox_stack(config=config, tenants={tenant_a: {}, tenant_b: {}}, namespace_suffix=run_id)

    payload = prepare_sandbox_issue_payload(
        {"title": "Phase 2 live sandbox Redis smoke", "body": f"run {run_id}"},
        tenant_id=tenant_a, logical_operation_id=op_id,
    )
    receipt = await stack.svc.submit_proposal(tenant_id=tenant_a, request={
        "logical_operation_id": op_id, "actor": "agent/smoke", "action": "create_github_issue",
        "resource": config.repo, "payload": payload,
    })
    print(f"submit -> {receipt.status}")
    if receipt.status != "PROPOSED":
        failures.append(f"submission did not report PROPOSED ({receipt.status})")

    out = await stack.bridge.authorize_and_execute(tenant_id=tenant_a, logical_operation_id=op_id)
    print(f"authorize_and_execute -> {out.status.value}")
    if out.status != ProposalExecStatus.EXECUTED:
        failures.append(f"authorize_and_execute did not report EXECUTED ({out.status})")
    if len(recorded_issues()) != 1:
        failures.append(f"expected exactly one real issue, got {len(recorded_issues())}")

    replay = await stack.bridge.authorize_and_execute(tenant_id=tenant_a, logical_operation_id=op_id)
    print(f"replay -> {replay.status.value}")
    if replay.status == ProposalExecStatus.EXECUTED:
        failures.append("replay wrongly reported EXECUTED again")
    if len(recorded_issues()) != 1:
        failures.append("replay wrongly created a second real issue")

    # Cross-tenant identical logical_operation_id does not collide.
    payload_b = prepare_sandbox_issue_payload(
        {"title": "Phase 2 live sandbox Redis smoke (tenant-b)", "body": f"run {run_id}"},
        tenant_id=tenant_b, logical_operation_id=op_id,
    )
    await stack.svc.submit_proposal(tenant_id=tenant_b, request={
        "logical_operation_id": op_id, "actor": "agent/smoke", "action": "create_github_issue",
        "resource": config.repo, "payload": payload_b,
    })
    out_b = await stack.bridge.authorize_and_execute(tenant_id=tenant_b, logical_operation_id=op_id)
    print(f"tenant-b authorize_and_execute (identical op id) -> {out_b.status.value}")
    if out_b.status != ProposalExecStatus.EXECUTED:
        failures.append(f"tenant-b did not independently EXECUTE ({out_b.status})")
    if len(recorded_issues()) != 2:
        failures.append(f"expected exactly two real issues total, got {len(recorded_issues())}")

    # Ambiguous post-dispatch failure -> durable UNKNOWN -> reconciliation.
    op_crash = f"op-crash-{run_id}"
    payload_crash = prepare_sandbox_issue_payload(
        {"title": "Crash scenario", "body": f"run {run_id}"}, tenant_id=tenant_a, logical_operation_id=op_crash,
    )
    await stack.svc.submit_proposal(tenant_id=tenant_a, request={
        "logical_operation_id": op_crash, "actor": "agent/smoke", "action": "create_github_issue",
        "resource": config.repo, "payload": payload_crash,
    })

    async def crashing(*, resource, action, payload):
        import httpx

        async with httpx.AsyncClient() as client:
            await client.post(f"{base_url}/repos/{resource}/issues", json=payload)
        raise ConnectionError("simulated ambiguous post-dispatch failure")

    stack.bridge._upstream = ResourceBoundUpstream(resource=config.repo, dispatch=crashing)
    crashed = await stack.bridge.authorize_and_execute(tenant_id=tenant_a, logical_operation_id=op_crash)
    print(f"crash -> {crashed.status.value}")
    if crashed.status != ProposalExecStatus.EXECUTION_FAILED:
        failures.append(f"crash did not report EXECUTION_FAILED ({crashed.status})")

    recon = await reconcile_proposal_operation(
        proposals=stack.proposals, idempotency=stack.idempotency, authority=stack.authority,
        tenant_id=tenant_a, logical_operation_id=op_crash, verify_external_evidence=stack.evidence_verifier,
    )
    print(f"reconciliation -> {recon.outcome.value}")
    if recon.outcome != ReconcileOutcome.RESOLVED:
        failures.append(f"reconciliation of the crashed operation did not RESOLVE ({recon.outcome})")

    server.stop()

    if failures:
        print("\nREDIS PHASE 2 LIVE SANDBOX SMOKE FAILED:")
        for f in failures:
            print("  -", f)
        return 1
    print("\nREDIS PHASE 2 LIVE SANDBOX SMOKE PASSED: proposal->authority->tenant-scoped durable "
          "admission->real HTTP dispatch chain holds against real Redis.")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
