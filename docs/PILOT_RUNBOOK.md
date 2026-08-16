# Pilot Runbook

```
The model proposes. MCC decides. The gate enforces. The audit chain records.
```

This runbook is the operational procedure for connecting an external
engineering team to MCC-Core for a production pilot, using the official
Python SDK (`sdk/mcc-sdk`, package `mcc_sdk`, PR #81) and the reference
integration in [`pilot/reference_python/`](../pilot/reference_python/).

**This document prepares a pilot. Completing it does not itself constitute
a completed pilot, a successful pilot, third-party validation, or an audit
result.** See [`docs/PILOT_ACCEPTANCE_CHECKLIST.md`](PILOT_ACCEPTANCE_CHECKLIST.md)
for what additionally has to be true, and confirmed by the external
partner, before any of those claims can be made.

---

## 1. Pilot purpose and scope

The purpose of this pilot is to let a real external engineering team
connect a candidate integration to a real, running MCC-Core Gateway and
observe genuine governance decisions (`ALLOW` / `DENY` / `ESCALATE` /
`CONSTRAIN`) for their own candidate actions, first in a **non-actuating
observe mode**, and only later — deliberately, and only if the team
chooses to — in an **enforced mode** that permits a local, simulated
actuator to react to a decision.

In scope:

- Connecting to `POST /evaluate` on a real MCC-Core Gateway via the
  official `mcc_sdk` package.
- Submitting real candidate actions and receiving real governance
  decisions.
- Running the reference integration (`pilot/reference_python/`) against
  that Gateway in observe mode, then enforced mode.
- Producing a reproducible, machine-readable evidence bundle of what
  happened during a pilot run.

Out of scope (this document does not cover, and this PR does not add):

- A production actuator that performs a real external action. The
  reference integration's actuator is local and simulated only — see
  §3 below.
- Publishing any package to PyPI. The pilot installs `mcc_sdk` from an
  exact commit of this repository — see §3.
- Any claim of a completed, certified, audited, or externally validated
  pilot. Only the external partner can make that determination — see
  `docs/PILOT_ACCEPTANCE_CHECKLIST.md`.
- Partner-specific code, credentials, endpoints, or business logic.

---

## 2. Prerequisites

- Python 3.9 or later (matches `sdk/mcc-sdk`'s `requires-python`).
- `git`, and network access to clone this repository (or an existing
  clean clone).
- A way to run the MCC-Core Gateway — either:
  - locally, via `uvicorn` (see §6), for evaluation and integration
    development; or
  - a Gateway instance your organization already operates or has been
    given network access to (its operator provides the base URL and,
    if required, an API key).
- No production credentials, partner secrets, or PHI/PII are required or
  should ever be placed in any file tracked by this repository. See
  `.env.pilot-readiness.example` for the safe placeholder configuration
  template.

---

## 3. Supported architecture

```
   candidate action
         |
         v
  official mcc_sdk (MCCClient / AsyncMCCClient)
         |
         v
  POST /evaluate  --------------------------->  MCC-Core Gateway
         |                                        (Policy Evaluation +
         v                                         Ed25519 signing +
  decision validation (mcc_sdk; fails                nonce/audit)
    closed on malformed/unknown verdict)
         |
         v
  pilot-side mode gate (observe: never
    actuates; enforced: only ALLOW/CONSTRAIN
    may actuate)
         |
         v
  SimulatedActuator (local only; no network
    call, no real external system)
         |
         v
  Pilot evidence bundle (pilot/schema/pilot_evidence.schema.json)
```

Two independent fail-closed layers sit between a decision and any
simulated actuation:

1. **The Gateway itself** — the Execution Gate is fail-closed by design
   (see the root `CLAUDE.md` doctrine); it never returns `enforce: true`
   without a genuine, verified decision.
2. **The pilot integration's own mode gate**
   (`pilot/reference_python/integration.py::PilotIntegration.submit`) —
   independently of the Gateway's own `mode`/`enforce` fields, the pilot
   integration itself only ever invokes the simulated actuator when its
   *own* configuration is `mode=enforced` **and** the decision is `ALLOW`
   or `CONSTRAIN`. `DENY` and `ESCALATE` are never actuated, in either
   mode.

There is no code path in `pilot/reference_python/` that performs the
simulated action without both of these gates having passed — see
`pilot/reference_python/actuator.py::SimulatedActuator.execute`, which
also only ever acts on the Gateway's own `forward_context`, never a
caller-substituted payload. This is what makes a `CONSTRAIN` decision
structurally unable to actuate outside its own returned constraints.

---

## 4. Exact clean-clone and commit-pinning procedure

The pilot is reproducible from an exact commit of this repository. No
package needs to be published to PyPI.

```bash
git clone https://github.com/mcc-prior-art/mcc-layer.git
cd mcc-layer

# Pin to the exact commit this pilot was validated against.
# Replace <PILOT_COMMIT_SHA> with the commit SHA agreed with AXLOGIQ for
# this pilot engagement (e.g. the commit reported in the PR #82 evidence).
git checkout <PILOT_COMMIT_SHA>

# Record the exact commit in your own pilot notes -- it is also recorded
# automatically in every evidence bundle's mcc_commit_sha field (see §15).
git rev-parse HEAD
```

Do this in a fresh clone (or a clean working tree with no local
modifications) so that `git rev-parse HEAD` unambiguously identifies the
code the pilot ran.

---

## 5. Installing the official `mcc-sdk` package from the repository

```bash
python3 -m venv .venv
source .venv/bin/activate   # or the Windows equivalent

# From the pinned clone's repository root:
pip install -e ./sdk/mcc-sdk

# The pilot's own runtime dependencies (jsonschema for evidence
# validation, and the runtime deps mcc_sdk itself needs):
pip install -r requirements.txt
pip install jsonschema>=4.0
```

This installs the exact `mcc_sdk` package that was reviewed and merged in
PR #81, from the pinned commit — not a PyPI release. Verify:

```bash
python3 -c "import mcc_sdk; print(mcc_sdk.__version__)"
```

---

## 6. Gateway startup and health verification

**Option A — run a Gateway locally** (repository root, separate
terminal):

```bash
uvicorn gateway.app:app --host 127.0.0.1 --port 8001
```

This boots the real Gateway with its pilot policy
(`gateway/pilot_policy.py`), an ephemeral Ed25519 signing key, and the
default agent API key `demo-key` (override via `MCC_GATEWAY_API_KEY` —
see §7 and `gateway/app.py::GatewaySettings`).

**Option B — connect to an existing Gateway** your organization already
operates. Obtain its base URL and (if required) API key from its
operator; do not record either in any file tracked by this repository.

**Health verification**, against whichever Gateway you are using:

```bash
curl -s http://127.0.0.1:8001/health | python3 -m json.tool
```

A healthy Gateway returns HTTP 200 with `"status": "ok"`, its current
`mode`, and its Ed25519 signing key metadata. If the deployment also
exposes readiness checks (Redis, trust store, signing key — see
`gateway/app.py`'s `/ready` route), verify those as well before
proceeding:

```bash
curl -s http://127.0.0.1:8001/ready | python3 -m json.tool
```

Do not proceed to §8/§9 against a Gateway that does not report healthy.

---

## 7. Environment variables and configuration

**Gateway-side** (only relevant if you are operating the Gateway
yourself — see `gateway/app.py::GatewaySettings`, env prefix
`MCC_GATEWAY_`): `MCC_GATEWAY_API_KEY`, `MCC_GATEWAY_MODE`
(`inline`/`observe`), `MCC_GATEWAY_AUDIT_LOG_PATH`, and related settings.
Do not change Gateway decision semantics for the purpose of this pilot —
see the Scope constraints in the PR description.

**Pilot-side** (`pilot/reference_python/config.py::PilotConfig`, env
prefix `MCC_PILOT_`) — copy
[`pilot/reference_python/.env.pilot-readiness.example`](../pilot/reference_python/.env.pilot-readiness.example)
to a git-ignored `.env.pilot-readiness` and fill in real values:

| Variable | Purpose | Safe default |
|---|---|---|
| `MCC_PILOT_GATEWAY_URL` | Base URL of the Gateway to connect to | *(required, no default)* |
| `MCC_PILOT_TIMEOUT_SECONDS` | Per-request timeout, seconds | `10.0` |
| `MCC_PILOT_MODE` | `observe` or `enforced` | `observe` |
| `MCC_PILOT_ID` | Pilot engagement identifier | `example-pilot` |
| `MCC_PILOT_INTEGRATION_ID` | This integration build identifier | `reference-python-v1` |
| `MCC_PILOT_EVIDENCE_DIR` | Evidence output directory | `./artifacts/pilot-evidence` |
| `MCC_PILOT_RUN_CORRELATION_ID` | Correlation id for one run (optional; random if unset) | *(generated)* |
| `MCC_PILOT_API_KEY` | Gateway `X-API-Key`, if required (optional) | *(unset)* |

Never commit `.env.pilot-readiness`, real credentials, private keys,
partner names, real endpoints, or production data. `PilotConfig` never
includes `api_key` in its exported evidence or its configuration
fingerprint (`pilot/reference_python/config.py`) — this is structural,
not a formatting convention.

---

## 8. Observe-mode procedure

Observe mode is the safe, default starting point. The pilot integration
records what the Gateway decided and what would have happened, without
ever invoking the simulated actuator, regardless of the verdict returned.

```bash
export MCC_PILOT_GATEWAY_URL=http://127.0.0.1:8001
export MCC_PILOT_API_KEY=demo-key       # or your Gateway's real key
export MCC_PILOT_MODE=observe
export MCC_PILOT_EVIDENCE_DIR=./artifacts/pilot-evidence

python3 -m pilot.reference_python.runner
```

Or programmatically:

```python
from pilot.reference_python import PilotConfig, PilotIntegration

config = PilotConfig(
    gateway_url="http://127.0.0.1:8001",
    api_key="demo-key",
    mode="observe",
)
with PilotIntegration(config) as pilot:
    outcome = pilot.submit(
        identity="agent/your-integration", action="your_candidate_action",
        context={"...": "..."},
    )
    print(outcome.decision.decision, outcome.actuated)  # actuated is always False here
```

Stay in observe mode until the exit criteria in
`docs/PILOT_ACCEPTANCE_CHECKLIST.md` §"Observe-mode exit criteria" are
met.

---

## 9. Enforced-mode procedure

Enforced mode is a deliberate transition, never a default. Set
`MCC_PILOT_MODE=enforced` (or `PilotConfig(mode="enforced", ...)`) only
after observe-mode exit criteria are satisfied.

```bash
export MCC_PILOT_MODE=enforced
python3 -m pilot.reference_python.runner
```

In enforced mode:

- An `ALLOW` or `CONSTRAIN` decision may reach the local
  `SimulatedActuator` — and only the local simulated actuator; there is
  no other actuation path in this package.
- `DENY` and `ESCALATE` decisions never actuate, in either mode.
- A `CONSTRAIN` decision can only ever actuate the Gateway's own
  `forward_context` — never the originally requested payload.

Enforced mode in this reference integration still performs no real
external action — see §3. A real production actuator is a separate,
future milestone, not part of this PR.

---

## 10. Rollback and emergency-disable procedure

To stop or roll back the pilot integration at any point:

1. **Stop submitting new actions.** Terminate the running
   `pilot/reference_python/runner.py` process (or your own integration
   process) — there is no background process, queue, or persistent
   connection left running once the process exits.
2. **Revert to observe mode immediately** if you need to keep evaluating
   but stop any (simulated) actuation: set `MCC_PILOT_MODE=observe` (or
   `PilotConfig(mode="observe", ...)`) and restart. This alone is
   sufficient — it is enforced by the pilot integration's own code, not
   just by configuration convention (see §3).
3. **Disable the Gateway connection entirely** by removing network
   reachability to the Gateway, or by asking the Gateway's operator to
   revoke/rotate the API key used by this pilot (`gateway/pilot_policy.py`
   / the Gateway's trust configuration) — the pilot integration fails
   closed (raises, actuates nothing) the instant the Gateway becomes
   unreachable or the credential is rejected (§12).
4. **No state to undo.** The reference integration holds no persistent
   state of its own beyond the evidence files it writes (§15) — there is
   no database, queue, or partial transaction to roll back on the pilot
   side. Any real system state is a matter for whatever real system a
   future production actuator would call — out of scope for this PR.

---

## 11. Expected ALLOW, DENY, ESCALATE, and CONSTRAIN behavior

| Verdict | Gateway meaning | Pilot integration behavior (observe) | Pilot integration behavior (enforced) |
|---|---|---|---|
| `ALLOW` | Execution authorized, token signed | Recorded; actuator **not** invoked | Actuator invoked with the Gateway's `forward_context` |
| `DENY` | Execution blocked, gate closed | Recorded; actuator **not** invoked | Actuator **not** invoked |
| `ESCALATE` | Requires human authorization before execution | Recorded; actuator **not** invoked | Actuator **not** invoked (this reference integration does not implement an approval loop — see `docs/ESCALATE_APPROVAL.md` for the Gateway-side mechanism) |
| `CONSTRAIN` | Execution permitted within modified parameters only | Recorded; actuator **not** invoked | Actuator invoked, but only with the Gateway's own (constrained) `forward_context` — never the original request payload |

Every decision, regardless of verdict, is recorded as a `correlation_ref`
in the pilot evidence bundle (§15), with the Gateway's own `audit_id` and
`trace_id`.

---

## 12. Failure and timeout behavior

The pilot integration fails closed on every failure mode below — it never
fabricates a decision, and it never actuates as a result of a failure:

| Condition | `mcc_sdk` exception | Pilot integration behavior |
|---|---|---|
| Gateway unreachable (connection refused, DNS failure, etc.) | `MCCTransportError` | Raises; evidence records `unavailable_count`; no actuation |
| Request exceeds `MCC_PILOT_TIMEOUT_SECONDS` | `MCCTimeoutError` | Raises; evidence records `timeout_count`; no actuation |
| Gateway returns a non-2xx status, or a malformed/schema-mismatched 200 body | `MCCContractError` / `MCCGatewayError` | Raises; evidence records `malformed_count`; no actuation |
| Gateway returns an unrecognized verdict (not one of the four canonical values) | `MCCContractError` (Pydantic rejects it constructing `EvaluateResponse`) | Raises; evidence records `malformed_count`; no actuation |
| Wrong/missing API key | `MCCAuthenticationError` | Raises; no actuation |

No automatic retry is performed at any layer — `mcc_sdk.MCCClient` makes
exactly one attempt per `evaluate()` call, and the reference integration
adds none of its own. A transport failure, timeout, or malformed response
is always surfaced to the caller as a typed exception; a caller that
wants to retry must decide to do so explicitly and construct a new
request (a fresh `idempotency_key`/`transaction_id` is generated per
`submit()` call already, so a deliberate re-submission behaves as a new,
independently governed action, not a hidden retry).

---

## 13. Fail-closed requirements

The following are structural properties of this reference integration,
not configuration choices a pilot operator can accidentally disable:

- A candidate action can only reach the simulated actuator by going
  through `PilotIntegration.submit()` — i.e., through a real
  `POST /evaluate` call and a real, validated `EvaluateResponse`. There is
  no lower-level "just execute" method exposed.
- The simulated actuator's `execute()` method independently re-checks the
  decision is `ALLOW`/`CONSTRAIN` and carries a non-null
  `decision_token` before recording anything as executed — see
  `pilot/reference_python/actuator.py::SimulatedActuator.execute`. A
  forged or incomplete decision raises `DirectActuationRejected`.
- The exported API key is never present in evidence output (`api_key` is
  excluded from both `PilotConfig.to_evidence_dict()` and
  `PilotConfig.fingerprint()`) — no configuration or environment change
  can cause it to leak into a pilot evidence bundle.
- `observe` mode never actuates, unconditionally — the check is on the
  pilot's own configured mode, not on anything the Gateway response
  claims.
- Every one of the failure modes in §12 raises rather than silently
  returning a default/fabricated outcome.

---

## 14. Audit-log collection

The Gateway's own append-only, hash-chained audit log
(`audit.jsonl`, or whatever `MCC_GATEWAY_AUDIT_LOG_PATH` is configured to
on the Gateway you are using) is the authoritative record of every
decision made — it exists independently of anything the pilot integration
does, and is written by the Gateway itself with `fsync` on every entry.

To collect it during or after a pilot run:

```bash
# Recompute and verify the hash chain (requires the same api_key used for
# /evaluate, unless the deployment scopes /verify differently):
curl -s http://127.0.0.1:8001/verify -H "X-API-Key: $MCC_PILOT_API_KEY" | python3 -m json.tool

# Export the full signed audit log for an external auditor:
curl -s "http://127.0.0.1:8001/export?fmt=jsonl" \
    -H "X-API-Key: $MCC_PILOT_API_KEY" -o mcc-audit-export.jsonl
```

The pilot evidence bundle (§15) does not duplicate audit-log content — it
only records `audit_id`/`trace_id` **references** into it
(`correlation_refs`), so the two can be correlated without the pilot
integration needing to read or re-serialize the Gateway's own log.

---

## 15. Evidence export procedure

Every pilot run through `PilotIntegration` accumulates counts and
correlation references in a `PilotEvidenceCollector`
(`pilot/reference_python/evidence.py`). At the end of a run:

```python
path = pilot.evidence.finalize_and_export()
print(f"evidence written to {path}")
```

or, using the CLI runner, evidence is exported automatically at the end
of the run and its path printed.

The exported JSON is validated against
[`pilot/schema/pilot_evidence.schema.json`](../pilot/schema/pilot_evidence.schema.json)
and contains (see the schema for the authoritative field list): the exact
`mcc_commit_sha` this run's `mcc_sdk` was installed from, the `sdk_version`,
pilot/integration identifiers, UTC start/end timestamps, a
secret-free configuration fingerprint, verdict counts, failure-mode
counts, an `executed_count`, `correlation_refs` into the audit log, the
`final_mode`, and a `status`/`status_reason`.

`finalize_and_export()` never silently overwrites an earlier run's
evidence — the default filename embeds the run's (unique, unless you
pinned it) `run_correlation_id`, and it raises `FileExistsError` rather
than overwrite an existing file at that path.

Validate a previously exported bundle independently at any time:

```python
import json
from pilot.reference_python import validate_evidence

data = json.loads(open("artifacts/pilot-evidence/pilot-evidence-<id>.json").read())
validate_evidence(data)  # raises on schema violation
```

---

## 16. Troubleshooting

| Symptom | Likely cause | What to check |
|---|---|---|
| `MCCConfigurationError` at startup | Invalid `gateway_url` / `timeout` | `PilotConfig`/`MCCClient` construction arguments; §7 |
| `MCCTransportError` on every call | Gateway not running, wrong URL/port, firewalled | §6 health check; network path to the Gateway |
| `MCCAuthenticationError` | Wrong or missing `MCC_PILOT_API_KEY` | The Gateway operator's configured API key; §7 |
| `MCCTimeoutError` | Gateway overloaded, or timeout too aggressive for the network path | `MCC_PILOT_TIMEOUT_SECONDS`; Gateway `/health` latency |
| `MCCContractError` (schema mismatch) | Gateway version mismatch, or a non-conforming intermediary (proxy/load balancer) rewriting the response | Confirm the Gateway is the exact version this pilot was validated against; inspect the raw HTTP response |
| `DirectActuationRejected` | Something called `SimulatedActuator.execute()` directly, or with a `DENY`/`ESCALATE` decision, or one without a `decision_token` | This is the pilot's own bypass guard working as intended — go through `PilotIntegration.submit()` instead |
| `FileExistsError` on evidence export | Re-running with a pinned `MCC_PILOT_RUN_CORRELATION_ID` that was already used | Use a new correlation id, or the default (randomly generated) one |
| Evidence fails `validate_evidence()` | A hand-modified evidence file, or a schema/writer version mismatch | Re-export a fresh bundle; do not hand-edit evidence JSON |

---

## 17. This runbook is not third-party validation

Completing every procedure in this runbook — cloning the pinned commit,
installing the official SDK, connecting to a Gateway, running in observe
mode and then enforced mode, and exporting an evidence bundle — proves
only that the reference integration in this repository works correctly
against a real MCC-Core Gateway. **It is not, on its own, third-party
validation, a certified pilot outcome, or evidence of a successful
production deployment.** Those determinations belong to the external
partner and are addressed explicitly in
[`docs/PILOT_ACCEPTANCE_CHECKLIST.md`](PILOT_ACCEPTANCE_CHECKLIST.md).
