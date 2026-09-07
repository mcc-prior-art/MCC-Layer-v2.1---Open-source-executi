#!/usr/bin/env python3
"""Real Governed Executor Pilot — agent runner (Docker Compose).

Uses the supported MCC Python SDK (``mcc_client``) to drive the canonical path
against the running gateway. It never calls the mock notification service
directly — only the governed executor (inside the gateway) does, and only after a
verified decision + authorization + audit-before-execution + a confirmed receipt.

Demonstrates the four verdicts (evaluate) and a genuine EXECUTED result via the
ESCALATE -> approve -> execute path (which reaches the mock service and requires a
confirmed matching receipt before EXECUTED).
"""

from __future__ import annotations

import os
import sys
import time

sys.path.insert(0, "/app/sdk/python/src")
sys.path.insert(0, "/app/src")
sys.path.insert(0, "/app")

from mcc_client import (  # noqa: E402
    MCCClient, Verdict, MCCDeniedError, MCCError,
)

GATEWAY = os.environ.get("MCC_GATEWAY_URL", "http://mcc-gateway:8001")
API_KEY = os.environ.get("MCC_GATEWAY_API_KEY", "demo-key")
OP_KEY = os.environ.get("MCC_GATEWAY_OPERATOR_API_KEY", "op-key")


def _wait_ready(client: MCCClient) -> None:
    deadline = time.time() + 60
    while time.time() < deadline:
        try:
            if client._t.get("/ready").get("ready") in (True, False):  # reachable
                return
        except Exception:
            time.sleep(1.0)
    raise SystemExit("gateway did not become reachable")


def _corr(name: str) -> str:
    return f"corr-{name}-{int(time.time())}"


def main() -> int:
    client = MCCClient(GATEWAY, api_key=API_KEY, operator_key=OP_KEY, timeout=15.0)
    _wait_ready(client)
    failures = []

    scenarios = [
        ("ALLOW", "agent/notify-bot", {"recipient": "cust-1", "message": "Hi", "priority": 1, "channel": "email"}),
        ("DENY", "agent/notify-bot", {"recipient": "cust-1", "message": "Hi", "priority": 1, "channel": "pager"}),
        ("CONSTRAIN", "agent/notify-bot", {"recipient": "cust-1", "message": "Hi", "priority": 9, "channel": "email"}),
        ("ESCALATE", "agent/unknown", {"recipient": "cust-1", "message": "Hi", "priority": 1, "channel": "email"}),
    ]

    print("\n" + "=" * 60)
    print("MCC-Core Real Governed Executor Pilot")
    print("=" * 60)

    for expected, actor, payload in scenarios:
        payload = dict(payload, correlation_id=_corr(expected.lower()))
        d = client.evaluate(actor_id=actor, action="send_notification",
                            resource="crm", payload=payload,
                            idempotency_key=payload["correlation_id"])
        print(f"\n--- Scenario: {expected} ---")
        print(f"  proposed action    : send_notification  by {actor}")
        print(f"  proposed payload   : {payload}")
        print(f"  MCC verdict        : {d.verdict.value}")
        print(f"  authorization state: {'authorized-body-present' if d.executable else d.verdict.value}")
        if d.verdict.value != expected:
            failures.append(f"{expected}: got {d.verdict.value}")

        if d.verdict == Verdict.DENY:
            try:
                from mcc_client import MandateAuthorization
                client.execute(d, MandateAuthorization(mandate={"unused": True}))
                failures.append("DENY executed")
            except MCCDeniedError:
                print("  execution result   : BLOCKED (governed executor never called)")

        if d.verdict == Verdict.ESCALATE:
            approval = client.request_approval(d)
            print(f"  approval state     : requested ({approval.request_id}) — not executed")
            granted = client.approve(approval)          # operator path
            print(f"  approval state     : {granted.state} (operator granted)")
            try:
                result = client.execute_after_approval(d, granted)
                print(f"  final payload      : {payload}")
                print(f"  execution result   : {result.status}")
                print(f"  external receipt   : {result.execution}")
                if not result.executed:
                    failures.append("ESCALATE approved but not executed")
            except MCCError as exc:
                failures.append(f"ESCALATE execute: {type(exc).__name__}: {exc}")

    print("\n--- Audit chain ---")
    try:
        chain = client.verify_audit_chain()
        print(f"  audit verification : valid={chain.get('valid')}")
        if chain.get("valid") is not True:
            failures.append("audit chain did not verify")
    except MCCError as exc:
        failures.append(f"audit verify: {exc}")

    print("\n" + "=" * 60)
    if failures:
        print("PILOT FAILED:", "; ".join(failures))
        return 1
    print("PILOT PASSED: four verdicts + genuine EXECUTED (confirmed receipt) + audit verified.")
    print("The model proposes. MCC decides. The gate enforces. The audit chain records.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
