# mcc-client — MCC-Core Python SDK

The supported, typed Python client for **MCC-Core** governance. It is the
canonical integration path for an external AI agent or application.

```
External AI Agent
  → MCCClient (this SDK)
  → MCC Gateway            (POST /evaluate)
  → Governance Decision    (ALLOW / DENY / ESCALATE / CONSTRAIN)
  → Execution Gate         (governed /…/execute)
  → Governed Executor
  → External System
```

> The model proposes. MCC decides. The gate enforces. The audit chain records.
>
> **Proposal is not permission.**

The SDK is a **client, not a policy engine**. It creates no decisions locally,
signs nothing, bypasses neither the gateway nor the execution gate, calls no
external target directly, exposes no raw executor, and never treats a network
success as governance approval.

## Installation

```bash
pip install mcc-client            # from a package index
# local development, from the repository:
pip install -e sdk/python
```

The public package imports as `mcc_client` and ships `py.typed` (fully typed).

- **Supported Python:** 3.9+ (the MCC-Core repository targets 3.11).
- **Dependencies:** `httpx` only.

## Configuration

```python
from mcc_client import MCCClient

client = MCCClient(
    base_url="http://localhost:8001",  # your MCC gateway
    api_key="…",                       # agent X-API-Key
    operator_key="…",                  # optional; only for approve/deny (operator)
    timeout=10.0,
    max_safe_retries=2,                # applies ONLY to safe, pre-execution requests
)
```

## Canonical architecture

`evaluate()` is a side-effect-free decision. `execute()` is a separate, explicit,
governed call — evaluation never executes automatically.

## Evaluate

```python
decision = client.evaluate(
    actor_id="agent-01",
    action="send_payment",
    resource="payments",
    payload={"amount": 1000},
    idempotency_key="req-001",
)
print(decision.verdict)              # Verdict.ALLOW / DENY / ESCALATE / CONSTRAIN
print(decision.reason)               # human-readable reason
print(decision.audit_id)             # audit linkage
print(decision.correlation_id)       # server trace id
print(decision.authorized_payload)   # the body the verdict authorizes
```

## Verdict handling

### ALLOW / CONSTRAIN — explicit governed execution

Execution is always explicit and always governed. You provide the authorization
material the gateway requires (an approved mandate, a standing mandate, or
consensus votes); the SDK sends **only** the decision's authoritative payload.

```python
from mcc_client import MandateAuthorization, MCCExecutionError, MCCAmbiguousExecutionError

if decision.executable:
    try:
        result = client.execute(decision, MandateAuthorization(mandate=my_mandate))
        assert result.executed
    except MCCExecutionError as e:
        ...   # governed execution ran but did not complete (BLOCKED / FAILED)
    except MCCAmbiguousExecutionError as e:
        ...   # outcome unknown — DO NOT assume success; reconcile via the audit chain
```

For **CONSTRAIN**, `decision.authorized_payload` is the server-clamped body.
`execute()` sends exactly that — the original unconstrained payload is never sent,
and a caller cannot substitute or mutate actor/action/resource/payload-bound
fields (there is no parameter to do so).

### DENY

```python
from mcc_client import MCCDeniedError
try:
    client.execute(decision, authorization)
except MCCDeniedError as e:
    print("denied:", e.reason)   # never downgraded to success
```

### ESCALATE — approval flow

```python
from mcc_client import MCCApprovalRequiredError

if decision.needs_approval:
    approval = client.request_approval(decision)   # open a request bound to the op
    granted  = client.approve(approval)            # operator action (mints a mandate)
    result   = client.execute_after_approval(decision, granted)
```

The SDK never approves automatically, never executes automatically, and never
polls indefinitely.

## Timeouts, retries, idempotency, correlation IDs

- **Timeouts** raise `MCCTimeoutError`. A timeout is never interpreted as success.
- **Retries** apply only to safe, side-effect-free, pre-execution requests
  (`GET`, and `evaluate`). Governed **execution is never retried**: an uncertain
  outcome raises `MCCAmbiguousExecutionError` — reconcile via the audit chain.
- **Idempotency** — pass `idempotency_key` to `evaluate`; it is propagated to the
  gateway and echoed into the governed execution.
- **Correlation IDs** — a correlation id is generated per call (or pass
  `correlation_id=`) and sent as `X-MCC-Correlation-Id`; the decision exposes the
  server `correlation_id`.

## Failure modes (all fail closed)

`MCCProtocolError` (malformed / schema-invalid / unknown verdict / missing decision
material / actor-or-action mismatch), `MCCTimeoutError`, `MCCTransportError`,
`MCCAuthenticationError`, `MCCDeniedError`, `MCCApprovalRequiredError`,
`MCCInvalidDecisionError`, `MCCReplayError`, `MCCExecutionError`,
`MCCAmbiguousExecutionError` — all subclasses of `MCCError`. No error, timeout,
malformed response, or network success is ever interpreted as permission.

## Security boundary

The SDK does **not**: create authoritative decisions locally; sign decisions or
tokens; bypass the gateway or the execution gate; call the external target
directly; expose a raw executor; allow replacement of the constrained payload;
downgrade DENY/ESCALATE; treat network success as approval; fall back to an
ungoverned path; disable signature/nonce/replay/authority/policy/token/audit
validation; or reproduce server-side governance logic.

## Version compatibility

SDK `0.1.0`, tracking the MCC-Core gateway contract (`/evaluate` +
`/mandates|/approvals|/consensus/execute`). Semantic versioning.

## Quickstart

```bash
python examples/python_sdk_quickstart.py
```

Runs self-contained against the real gateway on loopback and demonstrates client
init, evaluation, all four verdicts, explicit governed execution, and the absence
of any direct executor / external-target access.
