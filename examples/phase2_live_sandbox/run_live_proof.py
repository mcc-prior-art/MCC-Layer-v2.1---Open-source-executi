#!/usr/bin/env python3
"""The ONE live sandbox proof run: proposal -> authority -> real GitHub
sandbox dispatch -> replay proof -> reconciliation proof, entirely through
the existing, unmodified ``ProposalExecutionService.authorize_and_execute``
path.

Requires explicit configuration (Section 11) -- refuses to run at all
unless ``MCC_PHASE2_LIVE_SANDBOX=1`` plus a non-core sandbox repo, a GitHub
token, and a Redis URL are all set. Never targets
``mcc-prior-art/mcc-layer`` (see ``config.py``).

Intended to be invoked ONLY by the manual, explicitly-triggered GitHub
Actions workflow (``.github/workflows/phase2-live-sandbox-manual.yml``) --
never by normal pull-request CI.

Exits non-zero on any miss.
"""

from __future__ import annotations

import asyncio
import sys
import time
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from gateway.proposal_execution_service import (  # noqa: E402
    ProposalExecStatus,
    ReconcileOutcome,
    reconcile_proposal_operation,
)

from examples.phase2_live_sandbox.config import SandboxConfig, SandboxConfigError  # noqa: E402
from examples.phase2_live_sandbox.marker import prepare_sandbox_issue_payload  # noqa: E402
from examples.phase2_live_sandbox.stack import build_live_sandbox_stack  # noqa: E402


async def main() -> int:
    try:
        config = SandboxConfig.from_env()
    except SandboxConfigError as exc:
        print(f"LIVE EXTERNAL SANDBOX: NOT EXECUTED — CREDENTIALS NOT AVAILABLE ({exc})")
        return 1
    if not config.live:
        print("LIVE EXTERNAL SANDBOX: NOT EXECUTED — MCC_PHASE2_LIVE_SANDBOX is not set to 1")
        return 1

    run_id = uuid.uuid4().hex[:8]
    tenant_id = f"live-sandbox-tenant-{run_id}"
    logical_operation_id = f"live-sandbox-op-{run_id}"
    failures = []

    print(f"sandbox repo:  {config.repo}")
    print(f"tenant_id:     {tenant_id}")
    print(f"operation id:  {logical_operation_id}")

    stack = await build_live_sandbox_stack(config=config, tenants={tenant_id: {}}, namespace_suffix=run_id)

    raw_payload = {
        "title": "MCC Phase 2 Live Sandbox Proof",
        "body": f"Automated MCC-Core Phase 2 live sandbox proof run {run_id}.",
    }
    payload = prepare_sandbox_issue_payload(
        raw_payload, tenant_id=tenant_id, logical_operation_id=logical_operation_id,
    )

    receipt = await stack.svc.submit_proposal(tenant_id=tenant_id, request={
        "logical_operation_id": logical_operation_id, "actor": "agent/live-sandbox-proof",
        "action": "create_github_issue", "resource": config.repo, "payload": payload,
    })
    print(f"submit -> {receipt.status}")
    if receipt.status != "PROPOSED":
        failures.append(f"submission did not report PROPOSED ({receipt.status})")

    out = await stack.bridge.authorize_and_execute(tenant_id=tenant_id, logical_operation_id=logical_operation_id)
    print(f"authorize_and_execute -> {out.status.value} ({out.reason})")
    if out.status != ProposalExecStatus.EXECUTED:
        failures.append(f"authorize_and_execute did not report EXECUTED ({out.status}: {out.reason})")
    else:
        print(f"external result: {out.execution}")

    # Replay proof: the identical (tenant_id, logical_operation_id) again.
    replay = await stack.bridge.authorize_and_execute(tenant_id=tenant_id, logical_operation_id=logical_operation_id)
    print(f"replay -> {replay.status.value}")
    if replay.status == ProposalExecStatus.EXECUTED:
        failures.append("replay wrongly reported EXECUTED a second time")

    # Reconciliation proof (informational on the ALLOW path -- there is
    # nothing to reconcile since the operation already reached EXECUTED,
    # so this proves the read-only path is safe to call, not that it
    # changes anything).
    if stack.evidence_verifier is not None:
        recon = await reconcile_proposal_operation(
            proposals=stack.proposals, idempotency=stack.idempotency, authority=stack.authority,
            tenant_id=tenant_id, logical_operation_id=logical_operation_id,
            verify_external_evidence=stack.evidence_verifier,
        )
        print(f"reconciliation (already EXECUTED) -> {recon.outcome.value}")
        if recon.outcome != ReconcileOutcome.NOT_RECONCILABLE:
            failures.append(f"reconciliation on an already-EXECUTED operation was not NOT_RECONCILABLE ({recon.outcome})")

    if failures:
        print("\nLIVE EXTERNAL SANDBOX FAILED:")
        for f in failures:
            print("  -", f)
        return 1
    print("\nLIVE EXTERNAL SANDBOX PASSED: proposal -> authority -> real sandbox dispatch -> "
          "replay-safe, entirely through ProposalExecutionService.authorize_and_execute.")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
