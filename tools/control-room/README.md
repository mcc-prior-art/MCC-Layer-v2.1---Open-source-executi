# MCC-Core Control Room

> **Local Self-Administered Demonstration — Not a Production Administrative Console.**
> This is a local, self-administered demonstration of the MCC-Core protocol
> implementation. It is not a third-party audit, production administrative
> console, or production deployment.

A local, browser-based interface that lets the repository owner, technical
reviewers, pilot partners, and investors see and interact with the **real**
MCC-Core execution-governance path:

```
Proposed Action → MCC Decision → Signed Decision Token
                → Execution Gate Verification → Actuation Result → Audit Record
```

Every field shown in the browser is copied verbatim from the real, running
`gateway.app` process. Nothing here computes, predicts, hard-codes, or
overrides a decision, a token, a gate verdict, or an audit entry.

-----

## Purpose and limitations

**What this is:** a genuine external client of the MCC-Core reference
runtime, wired up so a non-engineer can watch and drive the real protocol
path from a browser instead of a terminal.

**What this is not:**

- not a mock, a frontend simulation, a duplicated policy engine, or an
  alternative execution path;
- not a production administrative console;
- not an independently audited system, a third-party validation, or a
  production banking deployment;
- not proof of production-scale readiness.

Nothing this demonstration actuates reaches a real banking, payment, cloud,
email, or database system. The one thing governed execution can reach is a
local, loopback-only mock echo service this tool starts itself (see
[Architecture](#architecture) below) — the same non-production pattern
`deploy/pilot/docker-compose.yml`'s `upstream-echo` service and
`examples/governance_http_demo.py` already use elsewhere in this repository.

-----

## Architecture

```
 Browser (index.html / app.js)
        │  fetch("/api/...")
        ▼
 Control Room BFF  (tools/control-room/backend/server.py)
        │  HTTP only, via pilot.client.MCCGatewayClient
        │  (the repository's existing, supported, transport-only client)
        ▼
 Real MCC-Core Gateway  (gateway/app.py — completely unmodified)
        │
        ▼
 AuthorityModel → DecisionEngine (Ed25519) → ExecutionGate
        → EnforcementCoordinator → AuditLog (append-only, fsync'd)
        │
        ▼
 Local mock upstream (loopback only; started by this tool; never a
 real external system)
```

`tools/control-room/backend/runtime.py` boots the real `gateway.app` ASGI
app and a local mock upstream as genuine separate HTTP processes — exactly
the way `deploy/pilot/Dockerfile` (`uvicorn gateway.app:app`) and
`examples/governance_http_demo.py` already run the real gateway for a live
HTTP demo. It generates ephemeral, **never committed** consensus-evaluator
keys and API keys the same way `deploy/pilot/generate_pilot_config.py`
already does for the Docker pilot.

### Trust boundary

- **MCC-Core never imports, depends on, starts, or requires the Control
  Room.** `src/mcc_core/`, `gateway/`, and `egress_proxy/` contain zero
  references to `tools/control-room` — enforced by
  `tools/control-room/tests/test_no_core_dependency.py`, a static guard that
  scans every file in those packages.
- The Control Room reaches MCC-Core **only** as an external HTTP client,
  through `pilot.client.MCCGatewayClient` — the repository's existing,
  supported, transport-only SDK. It never imports `AuthorityModel`,
  `DecisionEngine`, `ExecutionGate`, `EnforcementCoordinator`, or
  `AuditLog` directly in its own request-handling logic (`server.py`,
  `scenarios.py`). The one exception is `runtime.py`, whose entire job is
  *starting* the real gateway process — the same thing every deployment
  script in this repository already does.
- A Control Room failure, compromise, outdated dependency, or incorrect
  display has **zero effect** on MCC-Core availability, policy decisions,
  Decision Token generation/verification, Execution Gate enforcement,
  nonce/replay protection, actuation, or audit-chain integrity — proven by
  `test_control_room_backend_going_down_does_not_affect_the_gateway` and
  `test_gateway_operates_via_plain_http_without_any_control_room_code`.
- **No decision or verification logic lives in the frontend.** The browser
  never computes a verdict and never re-verifies a signature; every result
  displayed is the gateway's own HTTP response, copied through unchanged.
  Consensus votes are signed, and operator approvals are issued, from the
  backend process only — the private evaluator keys and the operator API
  key never leave it (never sent to the browser, never logged, never
  written outside this run's temporary state directory).

-----

## Prerequisites

- Python 3.11+
- The repository's existing runtime dependencies:
  ```bash
  pip install -r requirements.txt
  ```
  (The Control Room adds **no** new third-party dependencies — see
  `tools/control-room/requirements.txt`.)
- Free local ports: `8765` (the Control Room UI) plus two OS-assigned
  ephemeral ports for the real gateway and the mock upstream. No Docker, no
  Redis, and no Node/npm are required.

## Clean-clone instructions

```bash
git clone <this repository>
cd mcc-layer
pip install -r requirements.txt
```

## Exact startup command

```bash
python tools/control-room/start.py
```

Runs detached in the background (like `docker compose up -d`); prints the
browser URL once the real gateway and the Control Room UI are both ready,
then returns control of your terminal. Bound to `127.0.0.1` only.

To run in the foreground instead (stop with Ctrl+C):

```bash
python tools/control-room/start.py --foreground
```

## Exact browser URL

```
http://127.0.0.1:8765/
```

(Override the port with `MCC_CONTROL_ROOM_PORT=<port>` before starting; if
`8765` is already taken, `start.py` automatically falls back to an
OS-assigned free port and prints the actual URL.)

## Exact shutdown command

```bash
python tools/control-room/stop.py
```

Sends a graceful shutdown signal to the background process; it tears down
its own BFF server, the real gateway, and the mock upstream, in that order,
before exiting. (In foreground mode, Ctrl+C does the same thing.)

-----

## Sample demonstration flow

1. `python tools/control-room/start.py` → open the printed URL.
2. Click **Run this scenario** on the **ALLOW** card. Watch all six stages
   populate: the proposed payment, the real `ALLOW` decision from
   `gateway/pilot_policy.py`, the real signed Ed25519 decision token, the
   real N-of-M consensus + gate verification, the real actuation against
   the local mock upstream, and the matching real audit-chain entry.
3. Click **DENY**, **ESCALATE**, and **CONSTRAIN** to see the other three
   verdicts, all from the same unmodified policy.
4. Click **ESCALATE → Approve → EXECUTED** to see the full human-in-the-loop
   path: an agent escalates, an operator (held only on the backend) approves
   it, and the same coordinator path actuates it for real.
5. Click **Consensus-evidence replay rejected**, **Action-binding tamper
   rejected**, **Expired consensus-challenge rejected**, and **Invalid
   evaluator signature rejected** to see the real gate fail-closed on each
   attack, using the exact mechanisms
   `tests/test_consensus_enforcement_http.py` and
   `tests/test_challenge_http.py` already prove over HTTP. See
   [What the four rejection scenarios actually demonstrate](#what-the-four-rejection-scenarios-actually-demonstrate)
   below for exactly which real invariant each one proves.
6. Use **Submit a custom proposed action** to try your own identity, action,
   and JSON context — `Propose` shows Stages 1–3; `Propose + Execute through
   Gate` runs the full pipeline for ALLOW/CONSTRAIN decisions.
7. Click **Verify hash chain now** to recompute the append-only audit log's
   integrity on demand.
8. `python tools/control-room/stop.py` when done.

-----

## What the four rejection scenarios actually demonstrate

MCC-Core deliberately provides **no** HTTP endpoint that accepts a
previously-issued, client-supplied Decision Token for direct re-verification
— by design, there is no second execution path (see
`gateway/governance_service.py`'s own module docstring: "There is no second
execution path"). This Control Room does **not** add one for demonstration
purposes.

So instead of a literal "resubmit this Decision Token" button, these four
scenarios exercise the same real, already-tested invariants at the layer
where MCC-Core actually exposes them for a client-driven governed
execution — the consensus-challenge and evaluator-vote evidence a
`POST /consensus/execute` call is bound to, verified by the exact same
`EnforcementCoordinator.enforce()` / `ExecutionGate` code a Decision Token
itself passes through at actuation:

| Scenario (precise label) | What is submitted twice / altered | Real invariant demonstrated | Not to be confused with |
|---|---|---|---|
| **Consensus-evidence replay rejected** | The identical signed evaluator votes and the identical one-time gateway-issued nonce, submitted a second time | The gate's one-time nonce consumption (`src/mcc_core/nonce.py`) — the same mechanism a Decision Token's `nonce` claim is checked against | "Decision Token replay" — no endpoint re-verifies a previously-issued token |
| **Action-binding tamper rejected** | A payload different from the one the consensus evidence was issued for | Action/payload-hash binding — the same invariant a Decision Token's `action_hash` / `payload_hash` claims enforce | Modifying a Decision Token's own claims post-issuance — there is no endpoint that would accept one |
| **Expired consensus-challenge rejected** | A gateway-issued challenge used after its own TTL has passed | Time-bounded validity — the same invariant a Decision Token's `exp` claim enforces | An expired Decision Token being resubmitted — again, no such endpoint exists |
| **Invalid evaluator signature rejected** | An evaluator vote altered after being signed | Real Ed25519 signature verification failing closed — the same primitive (`src/mcc_core/signing.py`) that verifies a Decision Token's own `sig` | A tampered Decision Token being resubmitted for re-verification |

Every one of these calls the **real** gateway's `/consensus/challenge` and
`/consensus/execute` endpoints, over real HTTP, using votes signed by the
demo's own ephemeral evaluator keys — nothing is simulated in the frontend,
and no new bypass or second engine was added to make any of the four
possible.

-----

## Explanation of every displayed stage

| Stage | What it shows | Where it comes from |
|---|---|---|
| **Proposed Action** | The identity/actor, action, resource, and context you submitted | Your input, echoed back |
| **MCC Decision** | `ALLOW` / `DENY` / `ESCALATE` / `CONSTRAIN`, the reason, and any applied constraints | `POST /evaluate` on the real gateway — `AuthorityModel.evaluate()` against `gateway/pilot_policy.py`, unmodified |
| **Decision Token** | Action hash, payload hash, policy hash, nonce, audience, issuer, validity window (`iat`/`nbf`/`exp`), constraints, and the Ed25519 signature + signing key id | The `decision_token` field of the same `/evaluate` response — signed by `DecisionEngine.issue_token()` inside the real gateway. Its signature is deliberately **not** re-verified in the browser (see [Trust boundary](#trust-boundary)); the gate's own re-verification at actuation is what proves it (Stage 4), and `tools/control-room/tests` independently verify it cryptographically offline. |
| **Gate Verification & Actuation** | The real N-of-M consensus check, the real one-time-nonce gate check, and the resulting status | `POST /consensus/execute` (or, for the ESCALATE path, `POST /approvals/{id}/execute`) — `EnforcementCoordinator.enforce()` inside the real gateway |
| **Actuation Result** | Whether the local mock upstream was actually called, and with what body | The mock upstream's own record of what it received (`runtime.py`'s `upstream_seen` list) |
| **Audit Record** | The matching append-only, hash-chained entries and a live chain-integrity check | `GET /export` + `GET /verify` on the real gateway, reading the same file `src/mcc_core/audit.py`'s `AuditLog` `fsync`s to |

A separate propose-only ("Stages 1–3") request against `/evaluate` never
actuates anything, so it never counts against `send_payment`'s real
velocity limit (see Troubleshooting).

-----

## Troubleshooting

- **"velocity limit 'payment_count' exceeded: count N > max 3"** — this is
  real, correct enforcement (`gateway/pilot_policy.py`'s
  `PILOT_VELOCITY`: no more than 3 `send_payment` actuations per actor per
  60-second window), not a bug. Re-running **ALLOW** / **CONSTRAIN** /
  **ESCALATE → Approve → EXECUTED** more than three times within a minute
  will trip it; wait roughly a minute and try again.
- **A scenario's Gate stage shows `BLOCKED: operation already executed`** —
  the idempotency guard has correctly recognized a duplicate submission.
  Every scenario mints a fresh idempotency key per click, so this should
  not happen in normal use; if you see it, you likely re-submitted the
  exact same custom proposal with the same identity/action/context/resource
  twice in a row via the custom form.
- **"real gateway unreachable"** in the browser, or the health badge stays
  red — the real gateway process failed to start or exited. Check
  `tools/control-room/.run/control-room.log` for the underlying error.
- **`start.py` says "already running"** but nothing responds — a stale
  `tools/control-room/.run/instance.json` was left behind (e.g. after a
  hard kill). Run `python tools/control-room/stop.py` first (it cleans up a
  stale file safely), then start again.
- **Port `8765` already in use** — set `MCC_CONTROL_ROOM_PORT` to a free
  port before starting, or just start anyway: `start.py` automatically
  falls back to an OS-assigned free port and prints the URL it actually
  bound.

-----

## Security disclaimer

**This is a local, self-administered demonstration of the MCC-Core protocol
implementation. It is not a third-party audit, production administrative
console, or production deployment.**

- Every credential this tool generates (gateway signing key, evaluator
  keys, agent/operator API keys) is ephemeral, generated fresh per run, and
  never committed to the repository.
- No private key or secret is ever sent to the browser, written to a log
  file, or included in a screenshot the UI itself takes — proven by
  `tools/control-room/tests/test_control_room_live.py::test_no_secrets_reach_the_http_responses`.
  Consensus votes are signed, and operator approvals are issued, from the
  backend process only.
- All actuation targets a local, loopback-only mock service. Nothing here
  ever contacts a real banking, payment, cloud, email, or database system.
- All services bind to `127.0.0.1` only.

## Confirmation: MCC-Core does not depend on the Control Room

- `src/mcc_core/`, `gateway/`, `egress_proxy/`, and `interceptors/` contain
  zero references to `tools/control-room` — statically enforced by
  `tools/control-room/tests/test_no_core_dependency.py`.
- The real gateway used by this demonstration is started, and answers real
  HTTP requests, using nothing from `tools/control-room` at all in the call
  path — proven by
  `test_gateway_operates_via_plain_http_without_any_control_room_code`.
- Building (and never starting) the Control Room's own BFF app has no
  effect on the already-running gateway — proven by
  `test_control_room_backend_going_down_does_not_affect_the_gateway`.
- Every other test, demo, and pilot deployment in this repository
  (`tests/`, `examples/`, `deploy/pilot/`) already runs the real gateway
  without ever touching `tools/control-room`.

-----

## Running the tests

```bash
pytest tools/control-room/tests -v
```

This is a separate, isolated test suite — it is **not** part of
`pytest tests/` (the repository's main suite) and does not need to be, since
`tools/control-room` sits outside the trusted computing base by design. Run
the main suite too, unmodified, to confirm nothing here touched it:

```bash
pytest tests/ -v
```
