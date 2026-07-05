#!/usr/bin/env python3
"""Reference Governed Agent — Docker Compose runner.

Drives the framework-neutral reference agent (``examples.reference_governed_agent``)
against the running MCC gateway through the supported SDK. It never calls the mock
notification service directly — only the governed executor inside the gateway does,
and only after a verified decision + operator approval + audit-before-execution +
a confirmed receipt.

It proves, end-to-end in real containers:

* DENY     -> no execution, the external service is never called;
* ESCALATE -> operator approval enforced -> governed execution -> verified external
              receipt -> EXECUTED -> the audit chain verifies.

(ALLOW/CONSTRAIN genuine execution needs consensus authorization material, which a
remote agent does not hold; those flows are proven in the deterministic tests. The
agent here reports them BLOCKED for lack of authorization — never a bypass.)

Prints the markers the E2E workflow asserts; a clean exit alone is NOT success.
"""

from __future__ import annotations

import os
import sys
import time

sys.path.insert(0, "/app/sdk/python/src")
sys.path.insert(0, "/app/src")
sys.path.insert(0, "/app")

from mcc_client import MCCClient  # noqa: E402

from examples.reference_governed_agent import (  # noqa: E402
    DeterministicProvider,
    ProgrammaticOperator,
    ReferenceGovernedAgent,
)

GATEWAY = os.environ.get("MCC_GATEWAY_URL", "http://mcc-gateway:8001")
API_KEY = os.environ.get("MCC_GATEWAY_API_KEY", "demo-key")
OP_KEY = os.environ.get("MCC_GATEWAY_OPERATOR_API_KEY", "op-key")

REQUEST = "Notify customer-123 that the appointment is confirmed"


def _wait_ready(client: MCCClient) -> None:
    deadline = time.time() + 60
    while time.time() < deadline:
        try:
            if client._t.get("/ready").get("ready") in (True, False):
                return
        except Exception:  # noqa: BLE001
            time.sleep(1.0)
    raise SystemExit("gateway did not become reachable")


def _print(result) -> None:
    print(f"  user request       : {result.request}")
    print(f"  proposal created   : {result.proposal.get('action')} "
          f"by {result.proposal.get('actor_id')}")
    print(f"  MCC verdict        : {result.verdict}")
    print(f"  verdict reason     : {result.reason}")
    if result.approval_status is not None:
        print(f"  operator approval  : {result.approval_status}")
    if result.final_payload is not None:
        print(f"  executed payload   : {result.final_payload}")
    print(f"  execution result   : {result.execution_status}")
    if result.receipt is not None:
        print(f"  external receipt   : {result.receipt}")
    if result.audit_valid is not None:
        print(f"  audit verification : valid={result.audit_valid}")
    if result.error:
        print(f"  detail             : {result.error}")


def main() -> int:
    client = MCCClient(GATEWAY, api_key=API_KEY, operator_key=OP_KEY, timeout=15.0)
    _wait_ready(client)
    failures: list[str] = []

    print("\n" + "=" * 66)
    print("MCC-Core Framework-Neutral Reference Governed Agent (Docker E2E)")
    print("=" * 66)

    # --- DENY: a disallowed channel is blocked; the service is never called. ---
    print("\n--- Scenario: DENY (disallowed channel) ---")
    deny_agent = ReferenceGovernedAgent(
        client, provider=DeterministicProvider(actor_id="agent/notify-bot",
                                               priority="normal", channel="pager"),
        authorizer=None)
    deny = deny_agent.handle(REQUEST)
    _print(deny)
    if deny.verdict != "DENY" or deny.executed:
        failures.append(f"DENY: verdict={deny.verdict} executed={deny.executed}")

    # --- ESCALATE: operator approval -> governed execution -> confirmed receipt. ---
    print("\n--- Scenario: ESCALATE (operator authorization) ---")
    esc_agent = ReferenceGovernedAgent(
        client, provider=DeterministicProvider(actor_id="agent/unknown",
                                               priority="normal", channel="email"),
        operator=ProgrammaticOperator(approve=True), authorizer=None)
    esc = esc_agent.handle(REQUEST)
    _print(esc)
    if esc.verdict != "ESCALATE":
        failures.append(f"ESCALATE: got verdict {esc.verdict}")
    if esc.approval_status != "APPROVED":
        failures.append("ESCALATE: operator approval was not enforced/granted")
    if esc.execution_status != "EXECUTED":
        failures.append("ESCALATE: genuine EXECUTED result absent (no confirmed receipt)")
    if not (esc.receipt and esc.receipt.get("receipt_verified")):
        failures.append("ESCALATE: external receipt was not verified")
    if esc.audit_valid is not True:
        failures.append("ESCALATE: audit chain did not verify")

    print("\n" + "=" * 66)
    if failures:
        print("REFERENCE AGENT PILOT FAILED:", "; ".join(failures))
        return 1
    print("REFERENCE AGENT PILOT PASSED: DENY blocked + ESCALATE approved -> "
          "governed execution -> verified receipt -> EXECUTED + audit verified.")
    print("The model proposes. MCC-Core decides. The gate enforces. "
          "The audit chain records.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
