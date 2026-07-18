# MCC-Core — Packaging & Public SDK (`mcc`)

Install MCC-Core, point it at a governance gateway, and get cryptographically
governed execution from a stable, typed Python import namespace.

> The model proposes. MCC decides. The gate enforces. The audit chain records.
> **Proposal is not permission.**

This document covers **installation** and the **public `mcc` API**. It does not
change the governance architecture; it is a thin, stable packaging surface over
the already-supported [`mcc-client`](../sdk/python/README.md) SDK.

---

## What `mcc` is (and is not)

`mcc` is a **thin facade**. Every symbol it exposes is re-exported **unchanged**
from `mcc_client` (the same class objects, not copies). It adds no transport, no
signing, no policy evaluation, no verification, and **no local decision logic**.

Authorization is performed **remotely by the MCC Gateway**, never locally by the
client. That is why there is deliberately **no** `MCC.authorize()` method that
would imply a local decision — the public API accurately represents the real
architecture:

```
Agent → MCCClient → MCC Gateway → Governance Decision → Execution Gate
      → Governed Executor → External System → Verified Receipt → Audit Chain
```

The client is a client: it makes no decisions, signs nothing, bypasses neither
the gateway nor the execution gate, and never treats a network success as
governance approval (fail-closed).

---

## Installation

### End users (once published)

```bash
pip install mcc-core
```

This installs the `mcc` facade and its dependency `mcc-client`.

### From this monorepo (editable / development)

`mcc-core` depends on `mcc-client`, which lives under `sdk/python/`. Install both
editable in a single command:

```bash
pip install -e ./sdk/python -e .
```

If `mcc-client` is already installed, `pip install -e .` on its own is enough.

Optional dependency groups:

```bash
pip install -e ".[gateway]"   # also install FastAPI + uvicorn to run the gateway locally
pip install -e ".[dev]"       # pytest, mypy, ruff, build
```

### Build artifacts (sdist + wheel)

```bash
python -m build          # produces dist/mcc_core-<v>.tar.gz and .whl
```

The wheel contains **only** the `mcc` package (plus `py.typed`); it does not
vendor `mcc_client`, so `mcc-core` and `mcc-client` never both provide the same
import namespace.

---

## Quick start

```python
from mcc import MCCClient

# Point the client at your MCC Gateway (the governance authority).
client = MCCClient("https://gateway.example.com", api_key="…")

# 1. Propose an action. The GATEWAY decides — this is not a local decision.
decision = client.evaluate(
    actor="agent/payments-bot",
    action="send_payment",
    resource="acct-1",
    context={"amount": 1000, "currency": "USD", "beneficiary_id": "ben-1"},
)
print(decision.verdict)          # Verdict.ALLOW / DENY / CONSTRAIN / ESCALATE

# 2. Execute only through the governed path, with the required authorization
#    material (consensus votes, an approval mandate, etc.). No bypass exists.
if decision.verdict is Verdict.ALLOW:
    result = client.execute(decision, authorization)   # authorization obtained per your policy
    print(result.status)         # EXECUTED only on a verified receipt

# 3. The audit chain is independently verifiable.
print(client.verify_audit_chain()["valid"])
```

`ESCALATE` and `CONSTRAIN` follow the same client surface (`request_approval` /
`approve` / `execute_after_approval`, and re-evaluation of the constrained
payload). See the [`mcc-client` README](../sdk/python/README.md) for the full
method reference — `mcc` exposes those exact objects.

---

## Public API

`from mcc import …`

| Symbol | Kind | Meaning |
|--------|------|---------|
| `MCCClient` | class | The governed client (evaluate / approvals / challenge / execute / verify_audit_chain). |
| `Authorization` | type | Union of the authorization materials accepted by `execute`. |
| `Transport` | class | HTTP transport (safe-only retries; no silent fallback). |
| `Verdict` | enum | `ALLOW` / `DENY` / `CONSTRAIN` / `ESCALATE`. |
| `Decision` | model | A gateway decision (verdict + bound fields). |
| `Approval` | model | An ESCALATE approval handle. |
| `ExecutionResult` | model | Governed execution outcome (status, receipt). |
| `ApprovalAuthorization` / `MandateAuthorization` / `ConsensusAuthorization` | models | Authorization materials for `execute`. |
| `Payload` | type | Canonical action payload. |
| `MCCError` + subclasses | exceptions | `MCCTransportError`, `MCCTimeoutError`, `MCCProtocolError`, `MCCAuthenticationError`, `MCCDeniedError`, `MCCApprovalRequiredError`, `MCCInvalidDecisionError`, `MCCReplayError`, `MCCExecutionError`, `MCCAmbiguousExecutionError`. |
| `__version__` | str | The `mcc-core` facade version. |
| `client_version` | str | The underlying `mcc-client` version. |

Every one of these is the identical object from `mcc_client` — verified by
`tests/test_mcc_facade.py`.

---

## Backward compatibility

`mcc_client` is unchanged: existing code that does `from mcc_client import MCCClient`
keeps working exactly as before. `mcc` is additive — a shorter, stable alias — so
you can migrate imports at your own pace or not at all.

---

## Security invariants (unchanged)

The facade preserves every MCC-Core guarantee because it contains no security
logic of its own:

- Proposal is not permission; authorization is remote and verified.
- Verified Ed25519 decision tokens; replay protection; authority / scope /
  identity / policy binding; audit-before-actuation; append-only audit chain.
- Fail-closed: no local fallback authorization, no silent transport fallback,
  `EXECUTED` only on a verified receipt.

Security always has higher priority than convenience.
