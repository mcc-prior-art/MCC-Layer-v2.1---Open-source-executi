# mcc-sdk

The official Python SDK for MCC-Core — a thin, typed, framework-neutral
client over the public Gateway API's `POST /evaluate` boundary
([`docs/integration/GATEWAY_API_CONTRACT.md`](../../docs/integration/GATEWAY_API_CONTRACT.md),
[`openapi/mcc-gateway.yaml`](../../openapi/mcc-gateway.yaml)).

```
The model proposes. MCC decides. The gate enforces. The audit chain records.
```

This package packages the existing protocol boundary — it does not
redesign or duplicate MCC-Core's governance logic, and it does not execute
anything. See [Security boundary](#security-boundary).

## Installation

From the monorepo root (editable, for development on this repo):

```bash
pip install -e ./sdk/mcc-sdk
```

As a standalone package (e.g. in another project's environment), point pip
at this directory or build and install the wheel — see
[Package build](#package-build).

### Supported Python versions

Python 3.9 and later (`requires-python = ">=3.9"` in `pyproject.toml`),
mirrored by `[tool.mypy] python_version = "3.11"` for local type-checking
and `target-version = "py39"` in `[tool.ruff]`.

## Quickstart — connect to MCC-Core in about 10 minutes

**1. Start a local Gateway** (repository root, separate terminal):

```bash
pip install -r requirements.txt
uvicorn gateway.app:app --host 127.0.0.1 --port 8001
```

This boots the real Gateway with its pilot policy
(`gateway/pilot_policy.py`), an ephemeral Ed25519 signing key, and the
default agent API key `demo-key` (override with the `MCC_GATEWAY_API_KEY`
environment variable — see `gateway/app.py::GatewaySettings`).

**2. Install the SDK** (a second terminal, or the same environment):

```bash
pip install -e ./sdk/mcc-sdk
```

**3. Submit a proposed action:**

```python
from mcc_sdk import MCCClient, EvaluateRequest, Verdict

with MCCClient(base_url="http://127.0.0.1:8001", timeout=5.0, api_key="demo-key") as client:
    result = client.evaluate(
        EvaluateRequest(
            identity="agent/payments-bot",
            action="send_payment",
            context={"amount": 1000, "currency": "USD"},
            mode="inline",
        )
    )

if result.decision == Verdict.ALLOW:
    print("authorized:", result.audit_id)
elif result.decision == Verdict.CONSTRAIN:
    print("authorized only for:", result.forward_context)
elif result.decision == Verdict.DENY:
    print("refused:", result.reason)
elif result.decision == Verdict.ESCALATE:
    print("needs human approval:", result.reason)
```

That's it — the model/application has proposed an action and received a
typed governance verdict. **The SDK has no execution path**: acting on an
ALLOW/CONSTRAIN verdict means calling the Gateway's separate, governed
execution endpoints (`POST /mandates/execute`,
`POST /approvals/{id}/execute`, `POST /consensus/execute` — see the Gateway
API Contract §5), never something this SDK does for you.

## Minimal synchronous example

```python
from mcc_sdk import MCCClient, EvaluateRequest

with MCCClient(base_url="http://127.0.0.1:8001", api_key="demo-key") as client:
    result = client.evaluate(
        EvaluateRequest(identity="agent/ops-bot", action="read_account")
    )
    print(result.decision, result.reason)
```

## Minimal asynchronous example

```python
import asyncio
from mcc_sdk import AsyncMCCClient, EvaluateRequest

async def main():
    async with AsyncMCCClient(base_url="http://127.0.0.1:8001", api_key="demo-key") as client:
        result = await client.evaluate(
            EvaluateRequest(identity="agent/ops-bot", action="read_account")
        )
        print(result.decision, result.reason)

asyncio.run(main())
```

## Handling every verdict

```python
from mcc_sdk import EvaluateRequest, MCCClient, Verdict

with MCCClient(base_url="http://127.0.0.1:8001", api_key="demo-key") as client:
    result = client.evaluate(
        EvaluateRequest(
            identity="agent/payments-bot", action="send_payment",
            context={"amount": 1000}, mode="inline",
        )
    )

if result.decision == Verdict.ALLOW:
    # result.decision_token is the signed authorization artifact.
    # result.forward_context == the original context (nothing was clamped).
    ...
elif result.decision == Verdict.CONSTRAIN:
    # result.decision_token is signed over the CLAMPED payload only.
    # A subsequent governed execute call must submit result.forward_context,
    # never the original request's context -- see result.applied_constraints
    # for what was changed and why.
    ...
elif result.decision == Verdict.DENY:
    # result.decision_token is None. Nothing to execute. result.reason
    # explains why.
    ...
elif result.decision == Verdict.ESCALATE:
    # result.decision_token is None. A human must approve via the
    # Gateway's separate ESCALATE/approval loop before anything can be
    # governed-executed -- see docs/ESCALATE_APPROVAL.md. This SDK does
    # not simulate or perform that approval.
    ...
```

## Handling validation failure, timeout, and Gateway unavailability

```python
from mcc_sdk import (
    EvaluateRequest, MCCClient,
    MCCAuthenticationError, MCCConfigurationError, MCCContractError,
    MCCGatewayError, MCCTimeoutError, MCCTransportError,
)

try:
    with MCCClient(base_url="http://127.0.0.1:8001", api_key="demo-key", timeout=5.0) as client:
        result = client.evaluate(EvaluateRequest(identity="agent/x", action="send_payment"))
except MCCConfigurationError:
    ...  # bad base_url / timeout -- caught before any network call
except MCCTimeoutError:
    ...  # the Gateway didn't respond in time; outcome unknown, do not assume success
except MCCTransportError:
    ...  # couldn't reach the Gateway at all (connection refused, DNS, TLS, ...)
except MCCAuthenticationError as exc:
    ...  # HTTP 401/403 -- exc.status_code, exc.detail (never the API key itself)
except MCCGatewayError as exc:
    ...  # any other HTTP 4xx/5xx, e.g. HTTP 422 -- exc.status_code, exc.detail
except MCCContractError:
    ...  # malformed/non-JSON body, unrecognized verdict, or a response that
         # doesn't match the documented EvaluateResponse schema -- never
         # silently treated as a decision
```

A locally-invalid request (e.g. an unknown top-level field, or a missing
`identity`/`action`) raises `pydantic.ValidationError` when you construct
the `EvaluateRequest` itself, before any network call:

```python
from pydantic import ValidationError
from mcc_sdk import EvaluateRequest

try:
    EvaluateRequest(identity="agent/x", action="send_payment", not_a_real_field="x")
except ValidationError:
    ...  # rejected locally, the same way the live Gateway rejects it with HTTP 422
```

## Configuration reference

| Parameter | Type | Default | Meaning |
|---|---|---|---|
| `base_url` | `str` | *(required)* | The Gateway's base URL, e.g. `http://127.0.0.1:8001`. Must start with `http://` or `https://`. |
| `timeout` | `float` | `10.0` | Request timeout in seconds (connect/read/write/pool). |
| `api_key` | `str \| None` | `None` | Sent as `X-API-Key` if provided — the live Gateway's agent authentication boundary (`gateway/app.py::get_caller`). Omit only against a deployment that doesn't require it. |
| `transport` | `httpx.BaseTransport \| None` (sync) / `httpx.AsyncBaseTransport \| None` (async) | `None` | An injected transport (e.g. `httpx.MockTransport`) for hermetic testing. **Not for production use.** |

No other configuration exists in this release. There is no retry
configuration — see [Retries](#retries-none-by-default) — and no
correlation-header configuration, because the live `/evaluate` contract does
not define a client-supplied correlation header (see
[Known contract observations](#known-contract-observations-not-fixed-by-this-sdk)).

## Retries: none, by default

`MCCClient.evaluate()` / `AsyncMCCClient.evaluate()` make **exactly one**
HTTP attempt. There is no retry logic in this release at all — not even for
connection failures or timeouts. This is deliberate: retrying `POST
/evaluate` could interact incorrectly with the Gateway's audit and (on the
governed execute endpoints, which this SDK does not call) nonce/idempotency
semantics, and a narrow SDK without retries is the safer default posture. A
`MCCTimeoutError` or `MCCTransportError` always means "the outcome is
unknown" — never "safe to retry automatically." If you need retry behavior,
implement it explicitly at the call site, re-authorizing (a fresh
`EvaluateRequest`) rather than blindly resending.

## Error and exception reference

All exceptions inherit from `mcc_sdk.MCCSDKError`.

| Exception | Raised when |
|---|---|
| `MCCConfigurationError` | Invalid `base_url` or `timeout` — raised before any network call. |
| `MCCTransportError` | A network/transport failure (connection refused, DNS, TLS, ...). |
| `MCCTimeoutError` (subclass of `MCCTransportError`) | The request timed out. |
| `MCCGatewayError` | The Gateway returned HTTP 4xx/5xx. Carries `.status_code`, `.detail` (the response body's `detail` field, or a text snippet), and `.body` (the full parsed JSON body, if any). |
| `MCCAuthenticationError` (subclass of `MCCGatewayError`) | HTTP 401/403 — the Gateway rejected the configured API key. |
| `MCCContractError` | The 200-status response body was non-JSON, not a JSON object, missing a required field, or carried an unrecognized verdict — i.e. it could not be trusted as a valid `EvaluateResponse`. |

`pydantic.ValidationError` (not an `mcc_sdk` exception) is raised directly
by constructing an invalid `EvaluateRequest` — this happens locally, before
any network call, and is not wrapped, so standard Pydantic error-handling
applies.

No `MCCRateLimitError` is defined in this release: the current Gateway API
Contract does not document any rate-limiting (HTTP 429) behavior for
`/evaluate`, and this SDK does not invent one. If a deployment ever returns
HTTP 429, it surfaces as a plain `MCCGatewayError(status_code=429, ...)`.

No exception message or `repr()` ever includes the configured `api_key` or
any other authorization header value.

## Security boundary

**This SDK is not an execution engine.** It provides:

- a typed `POST /evaluate` request/response boundary, and
- nothing else.

It does **not** provide, and never will as part of this package:

- direct actuator / governed-execution access (`POST /mandates/execute`,
  `POST /approvals/{id}/execute`, `POST /consensus/execute` are all
  out of scope — a separate, governance-aware client would be needed to
  call them, and this SDK deliberately does not);
- local ALLOW/DENY decision logic — every verdict comes from the live
  Gateway; the SDK never computes one;
- local policy evaluation;
- signature verification or generation of any kind (Decision Token
  signatures are the Execution Gate's concern, never the SDK's);
- approval simulation for ESCALATE;
- a fallback / degraded-mode "continue on error" execution path when the
  Gateway is unavailable — every failure mode raises a typed exception
  (see [Error and exception reference](#error-and-exception-reference)),
  never a best-effort guess.

The model or application proposes. MCC-Core decides. The Execution Gate
enforces. The audit chain records. This SDK's role is transporting the
first step — nothing more.

## Known contract observations (not fixed by this SDK)

Discovered while building this SDK against the live contract, out of scope
for a client-library PR (no Gateway changes were made — see the PR #81
report for the explicit confirmation):

- `openapi/mcc-gateway.yaml`'s `EvaluateRequest.mode` documents an
  `enum: [inline, observe]`, but the live `gateway/app.py::EvaluateRequest`
  does not enforce it server-side (`mode: Optional[str]`, unconstrained;
  any other string is silently treated like `observe` because
  `enforce = (mode == "inline")`). This SDK's own `EvaluateRequest.mode`
  intentionally constrains the value to `"inline" | "observe"` client-side,
  matching what the OpenAPI document already claims — this can only ever
  *reject* a request the live Gateway would otherwise silently
  misinterpret, never accept one the Gateway would reject.
- The live `/evaluate` contract does not define a client-supplied
  correlation/request-identifier header. This SDK therefore does not send
  one; the only correlation identifiers available are the response's
  `audit_id` (the audit-correlation key) and `trace_id` (a per-request
  trace identifier, explicitly documented as "not a security boundary").

## Local development and test commands

From the monorepo root:

```bash
pip install -e ./sdk/mcc-sdk[dev]

# Unit + integration + contract-drift tests for this SDK:
PYTHONPATH=src:.:sdk/mcc-sdk/src pytest tests/mcc_sdk/ -v

# Lint, format check, and strict type-check:
cd sdk/mcc-sdk
ruff check src/
ruff format --check src/
mypy
```

`tests/mcc_sdk/` follows the same convention as `tests/test_mcc_client_sdk.py`
for the sibling `mcc_client` package: it inserts `sdk/mcc-sdk/src` onto
`sys.path` directly (see `tests/mcc_sdk/conftest.py`), so no editable
install is required to run it as part of the main repository's `pytest
tests/` suite. `tests/mcc_sdk/test_integration.py` and
`test_contract_drift.py` boot a real, local instance of `gateway.app`
(via `examples/_demo_server.py`'s `DemoServer`) rather than mocking it.

## Package build

```bash
cd sdk/mcc-sdk
python -m build --outdir dist
```

Produces exactly one wheel and one sdist. Verify a clean install (outside
this checkout):

```bash
python -m venv /tmp/mcc-sdk-smoke
/tmp/mcc-sdk-smoke/bin/pip install dist/*.whl
/tmp/mcc-sdk-smoke/bin/python -c "from mcc_sdk import MCCClient, EvaluateRequest; print('OK')"
```

This package is **not published to PyPI** as part of this PR (see the PR
#81 report for the explicit confirmation).

## What this package deliberately does not include

- No MCP support, no UI, no TypeScript SDK, no framework-specific adapters.
- No adapter certification of any kind.
- No Pilot Integration Pack or production pilot deployment tooling.
- No local policy engine or execution helpers.
- No changes to the Gateway, to governance semantics, or to execution
  semantics — this package only transports the existing, unmodified
  `POST /evaluate` boundary.

These are explicitly out of scope for this PR; see the file map in
`CLAUDE.md` for where related (separate) work already lives
(`mcc_adapter_sdk` for the framework-neutral adapter SDK,
`mcc_compliance` for adapter certification, `sdk/python/`'s `mcc_client`
for the existing full-surface client covering mandates/approvals/consensus).
