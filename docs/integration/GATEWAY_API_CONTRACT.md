# Gateway API Contract

**Status:** integration-readiness contract, v1.0 (aligned to `mcc_client.contract.CONTRACT_VERSION`).
**Scope:** the external HTTP surface of the MCC-Core Gateway (`gateway/app.py` +
`gateway/governance_api.py`). Machine-readable form:
[`openapi/mcc-gateway.yaml`](../../openapi/mcc-gateway.yaml).

**This is not adapter certification.** This document makes no claim of
certified adapters, AXLOGIQ-certified status, a production signing ceremony,
an official certification program, issued technical certificates, or any
legal/commercial certification. Adapter certification (`mcc_compliance`,
`certifications/manifest.json`) is a separate, pre-existing program; this
contract is deferred and orthogonal to it — it is about integration
readiness: how an external caller talks to the Gateway over HTTP, not about
which frameworks or adapters are certified.

This document is deliberately narrower than, and does not replace:

- [`docs/INTEGRATION_CONTRACT.md`](../INTEGRATION_CONTRACT.md) — the
  normative, framework-neutral contract at the **SDK level**
  (`mcc_client`/`mcc_protocol`/`mcc_adapter_sdk`), including the stable
  `ContractErrorCode` taxonomy this document reuses.
- [`docs/GOVERNANCE_HTTP_API.md`](../GOVERNANCE_HTTP_API.md) — prose reference
  for the mandate/approval/trust-administration endpoints in full detail
  (request/response fields, curl examples, threat model).
- [`docs/TRANSACTION_GOVERNANCE.md`](../TRANSACTION_GOVERNANCE.md) — the five
  distinct transaction protections (nonce, idempotency, transaction binding,
  velocity, aggregate/anti-splitting) this document's §10–§12 depend on.

Where this document and one of the above overlap, the more detailed document
is authoritative for implementation-level detail; this document is
authoritative for the **raw external HTTP contract shape**.

---

## 1. Purpose

An external AI agent, backend service, or integration system needs one
question answered before it does anything real: *is this specific action, by
this specific actor, with this specific payload, authorized right now?*

The Gateway is the only place that question gets answered. It is reachable
over plain HTTP so that a caller in any language, any framework, can
integrate against it without adopting the Python SDK — the SDK
(`mcc_client`) is a convenience over this same wire contract, not a
different one.

This document defines that wire contract precisely enough that a caller who
has never seen the MCC-Core source code can implement a conforming
integration from this document and the OpenAPI file alone.

## 2. Architecture

```
AI Agent / Backend Service / Integration System
              │  POST /evaluate  (propose)
              ▼
        MCC-Core Gateway
        ┌──────────────────────────────────┐
        │  Authority Model (policy eval)    │
        │  Ed25519 Decision Token signing   │
        └──────────────────────────────────┘
              │  ALLOW / DENY / ESCALATE / CONSTRAIN
              ▼
   Caller holds a Decision Token (ALLOW/CONSTRAIN only)
              │  POST /mandates/execute
              │  POST /approvals/{request_id}/execute
              │  POST /consensus/execute
              ▼
   EnforcementCoordinator.enforce()   (the ONE execution path, §5)
        gate verify → nonce consume → [consensus re-verify] →
        [challenge consume] → revocation re-check → [approval consume] →
        idempotency reserve → velocity reserve →
        audit BEFORE actuation → execute → audit result →
        idempotency finalize
              │
              ▼
        Governed upstream executor  →  Receipt
              │
              ▼
        Append-only hash-chain audit log (fsync every write)
```

The canonical formula, unchanged:

```
The model proposes.
MCC decides.
The gate enforces.
The audit chain records.
```

**The executor must act only after a verified MCC decision.**

## 3. Trust boundary

- The Gateway is the sole authority boundary. No caller-supplied field is
  ever trusted for authorization — every field that matters to a decision
  (action, actor, payload, resource, policy) is independently re-derived and
  hash-bound by the Gateway itself, never taken as given from the request.
- A Decision Token is proof the Gateway *issued* it, not proof a caller is
  entitled to submit it — the token is re-verified in full at every
  execution call (`ExecutionGate._verify()`, §9), including its own
  signature, audience, time window, policy hash, and payload/action hash.
- Two API-key boundaries exist today, both header-based, both placeholders
  for this integration-readiness contract (see §19 for what production
  key issuance is *not* yet):
  - `X-API-Key` — the **agent** boundary. Required on `/evaluate`, every
    governed `/…/execute` endpoint, `/verify`, `/export`.
  - `X-Operator-Key` — the **operator** boundary. Required on
    approve/deny/invalidate/revoke and trust-administration routes (see
    `docs/GOVERNANCE_HTTP_API.md`). An unset operator key disables ALL
    operator actions — fail-closed, never a silent bypass.
- `/health` and `/ready` require no key — they are liveness/readiness probes
  for an orchestrator, not a decision surface.
- The Gateway never calls out to the caller. All state relevant to a
  decision is either supplied in the request or held by the Gateway's own
  runtime (policy, trust config, nonce/idempotency/velocity registries,
  audit log).

## 4. Agent-to-MCC flow

```
1. Agent decides it wants to perform an action.
2. Agent POSTs the proposed action to /evaluate.
3. Gateway returns a verdict:
     ALLOW      → Decision Token issued, signed.
     DENY       → no token; stop, do not execute.
     ESCALATE   → no token; a human must approve first.
     CONSTRAIN  → Decision Token issued for a CLAMPED payload, not the original.
4. For ALLOW/CONSTRAIN, agent calls the matching governed /…/execute endpoint
   with the exact forward_context /evaluate returned (never the original
   context for CONSTRAIN).
5. Gateway re-verifies everything at the gate, actuates through the governed
   executor, records the outcome, returns status: EXECUTED / BLOCKED /
   EXECUTION_FAILED.
6. Every step — decision and actuation — is in the append-only audit chain,
   correlated by audit_ref (§16).
```

For ESCALATE, step 4 is replaced by the human-approval loop in
`docs/ESCALATE_APPROVAL.md`: an operator approves via
`POST /approvals/{request_id}/approve`, which mints a single-use approval
mandate; the agent then calls `POST /approvals/{request_id}/execute`.

## 5. Difference between `/evaluate` and `/execute`

**`POST /evaluate` is real, implemented, and side-effect-free.** It never
touches the upstream executor. It only returns a verdict and, for
ALLOW/CONSTRAIN, a signed Decision Token.

**A single unified `POST /execute` does not exist in the running Gateway
today.** This is documented honestly as a **gap**, not hidden or faked. The
target shape is defined in `openapi/mcc-gateway.yaml` under `/execute`,
marked `x-implementation-status: not-implemented`, returning `501`.

What exists instead is three action-specific governed execution endpoints,
each running the **identical** `EnforcementCoordinator.enforce()` path
(§2 diagram, §9), differing only in what authorization artifact they accept:

| Endpoint | Authorization artifact | Use when |
|---|---|---|
| `POST /mandates/execute` | A signed, standing mandate (`docs/SIGNED_MANDATES.md`) | The actor holds a durable, pre-issued mandate for this authority. |
| `POST /approvals/{request_id}/execute` | A single-use approval mandate minted after an operator approves an ESCALATE request | The original `/evaluate` call returned ESCALATE and a human has since approved it. |
| `POST /consensus/execute` | N-of-M independent Ed25519-signed evaluator votes, bound to a gateway-issued challenge | The deployment requires Multi-Context Consensus (`docs/MULTI_CONTEXT_CONSENSUS.md`) for this action. |

A caller integrating today **must** call the endpoint matching the
authorization material it actually holds. There is no fallback and no
generic path — calling the wrong one is a request-shape error, not a
governance decision.

Honest assessment of what unifying them would require: a single `/execute`
would need to accept a discriminated union of authorization artifacts
(mandate vs. approval vs. consensus votes) and route internally to the same
three code paths that exist today — the *governance* semantics would not
change, only the wire shape. This is future work, not started, and no
implementation exists to describe further than that.

## 6. Request envelope

`POST /evaluate` (`EvaluateRequest`, `gateway/app.py`):

| Field | Required | Meaning |
|---|---|---|
| `identity` | yes | The proposing actor (matched against mandates/policy). |
| `action` | yes | What the actor wants to do (matched against policy patterns). |
| `context` | no (default `{}`) | The action's parameters — the **payload**. Canonicalized and hashed into the token when one is issued. |
| `transaction_id` | no | Caller-supplied transaction identifier, bound into the token. |
| `idempotency_key` | no | Business-operation idempotency key (§10). Distinct from the token's one-time nonce (§11). |
| `actor_id` | no | Generic operation-binding actor identity; defaults to `identity`. |
| `resource_id` | no | Generic operation-binding resource identity. |
| `mode` | no | Per-request override of `inline`/`observe` enforcement mode. |

`EvaluateRequest` is now a **strict** top-level schema
(`model_config = ConfigDict(extra="forbid")`, `gateway/app.py`, fixed by
PR #80) — an unrecognized top-level field is rejected with HTTP 422, not
silently ignored. See §18's strictness matrix.

`context` itself stays a generic, unvalidated `Dict[str, Any]` **by
design** — action payload shapes are domain-specific (payments, infra,
robotics profiles each define their own), so this endpoint does not
enforce a single fixed nested schema for it. This is a documented,
intentional remaining scope limit, not an oversight — see §18 and §21.

The three governed execute endpoints and `POST /consensus/challenge` use
**strict** schemas (`extra="forbid"`, `gateway/governance_api.py`'s
`_Strict` base) — see `openapi/mcc-gateway.yaml` component schemas
`MandateExecuteRequest`, `ApprovalExecuteRequest`, `ChallengeCreateRequest`,
`ConsensusExecuteRequest` for the exact field lists.

Real example: [`examples/allow.request.json`](examples/allow.request.json).

## 7. Decision envelope

`POST /evaluate` returns `EvaluateResponse`. Every field is defined in
`openapi/mcc-gateway.yaml`'s `EvaluateResponse` schema; the fields that
matter for integration:

| Field | Present when | Meaning |
|---|---|---|
| `decision` | always | One of the four canonical verdicts (§8). |
| `reason` | always | Human-readable justification. Not a stable machine code — see §18. |
| `audit_id` | always | Hash of the audit entry written for this decision — the audit-correlation key (§16). |
| `decision_token` | ALLOW, CONSTRAIN | The full signed authorization artifact (§ below). `null` for DENY/ESCALATE. |
| `signature` | ALLOW, CONSTRAIN | The token's detached signature, duplicated for convenience. `null` otherwise. |
| `forward_context` | always | The body the verdict actually authorizes — identical to the submitted `context` for ALLOW, the **server-clamped** body for CONSTRAIN. This, never the original `context`, is what a subsequent execute call must submit. |
| `applied_constraints` | CONSTRAIN | Human-readable list of clamps applied. Empty otherwise. |
| `authority_required` | usually | The authority name the policy required (e.g. `payments.send`). |
| `policy_ref` | always | `{policy_id}@{policy_hash}` — the exact policy version this decision was made under (§12). |

The **Decision Token** (`decision_token`, present only for ALLOW/CONSTRAIN)
carries every field a subsequent execute call is re-verified against:
`iss`/`sub`/`aud`/`jti`/`iat`/`nbf`/`exp`, `decision`, `action`,
`action_hash`, `payload_hash`, `constraints`, `policy_id`, `policy_hash`,
`nonce`, `audit_ref`, `transaction_id`, `idempotency_key`, `actor_id`,
`resource_id`, `auth_claims`, `mandate_id`, `kid`, `sig`. All of these are
covered by `sig` — an Ed25519 detached signature over the full token — and
none can be altered independently. See `openapi/mcc-gateway.yaml`'s
`DecisionToken` schema for the authoritative field-by-field list.

Real, unedited example (genuinely issued by the running Gateway):
[`examples/allow.response.json`](examples/allow.response.json).

## 8. Verdict behavior

Four verdicts. No others.

### ALLOW

- **Meaning:** the action is authorized exactly as proposed.
- **Execution:** the executor **may** be called, and only with a verified
  Decision Token (§9). The token authorizes the original `context`
  unchanged.
- **Required fields:** `decision_token` and `signature` are present;
  `forward_context == context`; `applied_constraints == []`.
- **Audit:** the decision is recorded (`audit_id`); actuation, if it
  happens, is recorded again before execution (§16).
- **Example:** [`examples/allow.request.json`](examples/allow.request.json) /
  [`examples/allow.response.json`](examples/allow.response.json).

### DENY

- **Meaning:** the action is refused.
- **Execution:** **must never execute.** No token is issued
  (`decision_token: null`, `signature: null`); there is nothing an executor
  could even present.
- **Required fields:** `decision`, `reason`, `audit_id` only —
  `constraints`, `forward_context`, `applied_constraints` are all empty.
- **Audit:** the decision is recorded; there is no actuation stage to
  record.
- **Example:** [`examples/deny.request.json`](examples/deny.request.json) /
  [`examples/deny.response.json`](examples/deny.response.json).

### ESCALATE

- **Meaning:** the action exceeds standing authority; a human must decide.
- **Execution:** **must not execute** until an operator approves
  (`docs/ESCALATE_APPROVAL.md`) and the resulting single-use approval
  mandate is consumed via `POST /approvals/{request_id}/execute`. No token
  is issued at `/evaluate` time.
- **Required fields:** same shape as DENY — no token, no constraints.
- **Audit:** the ESCALATE decision is recorded; the eventual approve/deny
  and any execution are recorded as their own, separately correlated audit
  entries.
- **Example:**
  [`examples/escalate.request.json`](examples/escalate.request.json) /
  [`examples/escalate.response.json`](examples/escalate.response.json).

### CONSTRAIN

- **Meaning:** the action is authorized only in a clamped/modified form —
  never as originally proposed.
- **Execution:** the executor **may** be called, but **only** with the
  constrained payload (`forward_context`), **never** the original
  `context`. The Decision Token's `payload_hash` is bound to the clamped
  payload, not the original — submitting the original payload to an execute
  endpoint fails hash-binding at the gate (`PAYLOAD_HASH_MISMATCH`, §9).
- **Required fields:** `decision_token`, `signature`, non-empty
  `constraints` and `applied_constraints`; `forward_context != context`.
- **Audit:** identical shape to ALLOW.
- **Example:**
  [`examples/constrain.request.json`](examples/constrain.request.json) /
  [`examples/constrain.response.json`](examples/constrain.response.json) —
  a real run that clamped `amount: 99000 → 5000` against a `max_amount: 5000`
  mandate bound.

## 9. Fail-closed rules

Default behavior: **fail-closed.** If the Gateway does not issue a signed
ALLOW/CONSTRAIN token, or a subsequent verification step fails, execution
does not happen. This is architecture, not configuration.

`ExecutionGate._verify()` (`src/mcc_core/gate.py`) runs an **ordered**
sequence of checks at actuation time; the first failing check is the reason
returned, and no check downstream of a failure ever runs:

| Order | Check | Reason string |
|---|---|---|
| 1 | Token present | `NO_TOKEN` |
| 2 | Signing key trusted | `UNTRUSTED_KEY` |
| 3 | Signature valid | `INVALID_SIGNATURE` |
| 4 | Audience matches this gate | `AUDIENCE_MISMATCH` |
| 5 | Time window well-formed | `INVALID_TIME_WINDOW` |
| 6 | Not before `nbf` | `TOKEN_NOT_YET_VALID` |
| 7 | Not past `exp` | `TOKEN_EXPIRED` |
| 8 | Verdict is executable (ALLOW/CONSTRAIN) | `NON_EXECUTABLE_VERDICT` |
| 9 | Policy hash matches live policy | `POLICY_HASH_MISMATCH` |
| 10 | Action hash matches submitted action | `ACTION_HASH_MISMATCH` |
| 11 | Payload hash matches submitted payload | `PAYLOAD_HASH_MISMATCH` |
| 12 | Actor/resource/transaction binding matches | `BINDING_MISMATCH` |
| 13 | Nonce unused | `NONCE_REJECTED` |
| — | Any unexpected exception during verification | `GATE_ERROR` |
| — | All checks passed | `VERIFIED` |

Beyond the gate, `EnforcementCoordinator.enforce()` (`src/mcc_core/
coordinator.py`) fails closed at every one of its ordered stages — a
consensus re-verify failure, a challenge not consumed exactly once, a
revoked mandate, an idempotency conflict, or a velocity/aggregate ceiling
breach all produce `status: BLOCKED` **before** the upstream executor is
ever called, and are all recorded to the audit log.

Explicitly fail-closed conditions this contract makes no exception for:

- MCC runtime unavailable, timeout, or malformed response — the caller must
  treat any non-2xx or unparseable response as "not authorized," never as
  an implicit ALLOW.
- Unknown verdict — `mcc_client.Decision` rejects any value outside
  ALLOW/DENY/ESCALATE/CONSTRAIN; there is no default-permissive fallback.
- Missing decision token or missing audit correlation on an execute
  call — `NO_TOKEN`, refused.
- Invalid or reused nonce — `NONCE_REJECTED`, refused.
- Idempotency conflict — `DUPLICATE_INFLIGHT` / `DUPLICATE_UNKNOWN` /
  `DUPLICATE_EXECUTED` / `BINDING_CONFLICT`, refused (§10).
- Policy hash or payload hash mismatch — `POLICY_HASH_MISMATCH` /
  `PAYLOAD_HASH_MISMATCH`, refused.
- Stale or revoked mandate — checked at authority-resolution time and again
  at actuation (revocation re-check is its own coordinator stage); refused.
- Invalid approval — an approval mandate that is forged, expired, wrong
  subject, or already consumed is refused, single-use is enforced exactly
  once.
- Redis required but unavailable — when a deployment declares Redis-backed
  nonce/idempotency/velocity/challenge/revocation registries required, a
  backend outage fails the operation closed; it never silently falls back
  to an in-memory (and therefore non-cross-instance-safe) registry.
- Any unrecognized error — the coordinator's own exception handling
  classifies unexpected failures as `BLOCKED` or, if the executor itself
  raised after durable dispatch commitment, `EXECUTION_FAILED` (§ next
  paragraph) — never as success.

`ActuationStatus` has exactly three values, and their meaning is precise:

- `EXECUTED` — ran and durably confirmed; the idempotency key is marked
  `EXECUTED`, terminal.
- `BLOCKED` — refused before durable dispatch commitment; the upstream is
  never reached; any pre-dispatch idempotency reservation is released, not
  consumed.
- `EXECUTION_FAILED` — the outcome is **indeterminate (`UNKNOWN`)**, never
  assumed successful. Reached two ways: the executor raised after durable
  dispatch commitment (the external call may already be in flight or
  complete despite the raise), or the executor succeeded but the registry
  could not durably persist `EXECUTED`. Either way, the idempotency key is
  **NOT** freed — it is marked `UNKNOWN` and stays there, blocking every
  further admission attempt on that key, however freshly authorized, until
  independently verified positive evidence resolves it (never a blind
  retry). See `docs/DURABLE_OPERATION_SAFETY.md`.

## 10. Idempotency

Idempotency (`src/mcc_core/idempotency.py`) protects the **business
operation** — "did I already do this?" — and is distinct from the nonce
(§11), which protects the **authorization artifact** — "has this exact
signed token already been consumed?" A caller can retry the same business
operation with the same `idempotency_key` across multiple, freshly-signed
authorization attempts (new tokens/votes/nonces each time); idempotency is
what recognizes those as the same operation regardless of how many times
authorization was separately re-verified.

- **Uniqueness:** the `idempotency_key` is caller-supplied and must be
  unique per intended business operation. The Gateway does not generate one
  on the caller's behalf.
- **Transaction binding:** `idempotency_key` travels alongside
  `transaction_id`/`actor_id`/`resource_id` and is signed into the Decision
  Token when one is issued; the coordinator's idempotency stage keys its
  registry on it directly.
- **Lifecycle:** `RESERVED` (pre-dispatch, TTL-bound) → `DISPATCH_OWNED`
  (durable dispatch commitment; the point of no return) → `EXECUTED`
  (terminal) or `UNKNOWN` (indeterminate; durable; blocks every further
  admission attempt until independently verified positive evidence resolves
  it — never a blind retry). A `BLOCKED` outcome refused strictly
  *before* dispatch commitment releases the key, retryable; once
  `DISPATCH_OWNED`, the key can never again be released for a fresh
  admission — see `docs/DURABLE_OPERATION_SAFETY.md` for the full state
  machine, fencing, and durability model.
- **Duplicate/conflicting-duplicate behavior:** a second attempt with an
  idempotency key already `RESERVED`/`DISPATCH_OWNED` returns
  `DUPLICATE_INFLIGHT` (`"operation already reserved"`); already `UNKNOWN`
  returns `DUPLICATE_UNKNOWN` (`"operation outcome UNKNOWN; requires
  reconciliation, not retry"`); already `EXECUTED` returns
  `DUPLICATE_EXECUTED` (`"operation already executed"`); the same key bound
  to a *different* action/resource/payload returns `BINDING_CONFLICT`. All
  four map to `status: BLOCKED` at the HTTP layer — the upstream executor is
  never called a second time for the same key.
- **Cross-instance (Redis-backed) behavior:** when the deployment uses
  `RedisIdempotencyRegistry`, the reservation is atomic across every Gateway
  instance sharing that Redis — two instances racing the same key cannot
  both reserve it. `idempotency_registry_from_env` is fail-closed: if Redis
  is declared required and is unreachable, the registry does not silently
  degrade to in-memory.
- **Audit linkage for repeated attempts:** every attempt — reserved,
  duplicate-rejected, dispatch-committed, executed, or resolved-unknown —
  writes its own audit entry (§16); the audit chain shows the full history
  of an idempotency key, not just its terminal state.

Real, genuine example — a `/consensus/execute` call resubmitted with the
same `idempotency_key` after the first attempt already executed:
[`examples/idempotency-conflict.response.json`](examples/idempotency-conflict.response.json)
(`{"status": "BLOCKED", "reason": "operation already executed", ...}`).

This contract makes no claim beyond what the current runtime proves:
idempotency is enforced per Gateway deployment's configured registry
(in-memory for a single-process pilot, Redis for multi-instance); it does
not claim cross-deployment or cross-region idempotency beyond that shared
backend's own guarantees.

## 11. Nonce / replay protection

The **nonce** (`src/mcc_core/nonce.py`) is a one-time value bound into the
Decision Token (or, for consensus, into the gateway-issued challenge) and
consumed exactly once at the gate. It protects the **authorization
artifact** itself: even a byte-for-byte identical request, replayed with
the same token or the same consensus votes, fails at the gate with
`NONCE_REJECTED` — regardless of the idempotency key's state.

- **Consumption point:** nonce consumption happens at the gate, as stage
  (b) of `EnforcementCoordinator.enforce()`, **before** idempotency
  reservation. A nonce reuse is rejected before the idempotency registry is
  ever consulted.
- **Cross-instance (Redis-backed) behavior:** `RedisNonceRegistry` claims a
  nonce atomically across every Gateway instance sharing that Redis — two
  instances racing the same nonce cannot both succeed. Nonce checks are
  fail-closed on backend unavailability, identically to idempotency.
- **Consensus-specific replay protection:** the challenge nonce
  (`docs/CONSENSUS_CHALLENGE.md`) adds a second, gateway-owned layer: the
  nonce evaluators vote over is minted by `POST /consensus/challenge`, not
  supplied by the caller, and the challenge itself is single-use — a second
  `/consensus/execute` against an already-consumed challenge fails with
  `CHALLENGE_NOT_OPEN: state CONSUMED` before votes are even re-verified.

Real, genuine example — the exact request body that succeeds once against a
gateway-issued challenge; resubmitting it (even with a different
`idempotency_key`) is rejected because the challenge nonce was already
consumed:
[`examples/replay-deny.request.json`](examples/replay-deny.request.json).
The real rejection observed:
`{"status": "BLOCKED", "reason": "CHALLENGE_NOT_OPEN: state CONSUMED", "decision": "DENY"}`.

## 12. Policy and payload binding

- **Policy binding:** every Decision Token carries `policy_id` and
  `policy_hash` — the hash of the exact policy configuration that produced
  the decision. At actuation, the gate recomputes the deployment's *live*
  policy hash and rejects on any mismatch (`POLICY_HASH_MISMATCH`) — a
  token signed under a policy that has since changed cannot be replayed
  against the new policy.
- **Payload binding:** the token's `payload_hash` is the sha256 of the
  canonical payload (`forward_context` for CONSTRAIN, `context` for ALLOW)
  at decision time. At actuation, the gate recomputes the hash of the
  submitted payload and rejects on any mismatch
  (`PAYLOAD_HASH_MISMATCH`) — a caller cannot present an ALLOW token
  alongside a different payload than the one actually authorized, and
  cannot present a CONSTRAIN token alongside the original, unconstrained
  payload.
- **Action binding:** `action_hash` binds the action string itself
  (`ACTION_HASH_MISMATCH` on mismatch).
- **Actor/resource/transaction binding:** `actor_id`/`resource_id`/
  `transaction_id` are all bound into the token and re-checked
  (`BINDING_MISMATCH` on mismatch) — see `docs/TRANSACTION_GOVERNANCE.md`
  and `tests/test_transaction_binding.py` for the substitution attacks this
  closes (beneficiary swap, amount/currency substitution, etc.).

`policy_ref` in the `/evaluate` response (`{policy_id}@{policy_hash}`) is
the caller-facing, human-readable form of this binding — an integrator can
log it to see, at a glance, which exact policy version authorized a given
decision.

## 13. Mandate / authority context

Every decision is made against an `AuthorityModel` — the config-driven
`action → authority → verdict` mapping (`src/mcc_core/authority.py`). Two
distinct authorization artifacts can satisfy it at execute time:

- **Standing mandate** (`docs/SIGNED_MANDATES.md`) — a signed, revocable,
  scoped grant issued ahead of time by a `MandateAuthority`, presented via
  `POST /mandates/execute`. Verified for forgery, expiry, subject match,
  scope, and revocation on every use — revocation is re-checked at
  actuation, not just at issuance.
- **Consensus votes** (`docs/MULTI_CONTEXT_CONSENSUS.md`) — N independent
  Ed25519-signed evaluator votes, bound to the exact
  action/actor/payload/resource/policy_hash/nonce, presented via
  `POST /consensus/execute`. A deployment can make consensus **mandatory**
  for executable verdicts (`MCC_REQUIRE_CONSENSUS`), in which case
  `/evaluate`'s own ALLOW/CONSTRAIN is not sufficient on its own — the
  coordinator's consensus-re-verify stage still runs.

`decision_token.mandate_id` (nullable) names the standing mandate that
justified a token, when one was used, purely for audit/traceability — it is
not itself an authorization artifact a caller presents.

## 14. Approval and escalation references

An ESCALATE verdict carries no reference an agent can act on directly — by
design, the next step is a human, not the agent. The full loop
(`docs/ESCALATE_APPROVAL.md`):

1. `/evaluate` returns ESCALATE. The Gateway internally tracks a pending
   approval request (`request_id`) an operator can act on via
   `docs/GOVERNANCE_HTTP_API.md`'s approval routes
   (`GET/POST /approvals`, `/approvals/{id}/approve|deny|invalidate`).
2. An operator (holding `X-Operator-Key`) approves. The Gateway mints a
   **single-use** approval mandate bound to the original action, actor, and
   payload.
3. The agent calls `POST /approvals/{request_id}/execute` with that
   mandate. The coordinator consumes it exactly once, atomically, as part
   of actuation — a second attempt with the same approval is rejected, not
   silently re-executed.
4. If the operator instead denies or invalidates the request, no approval
   mandate is ever minted, and any subsequent execute attempt is refused
   for lack of one.

This document does not restate the full approval HTTP surface;
`docs/GOVERNANCE_HTTP_API.md` and `docs/ESCALATE_APPROVAL.md` are
authoritative for it. This section exists so an integrator reading only
this contract understands that ESCALATE is not a dead end — it is a
defined, single-use-terminated loop back into `/…/execute`.

## 15. Constraints

`constraints` (in the `/evaluate` response and the Decision Token) states
the bounds a CONSTRAIN verdict clamped the payload to — e.g.
`{"max_amount": 5000}`. `applied_constraints` is the human-readable list of
what was actually rewritten to satisfy those bounds — e.g.
`["amount: 99000.0 -> 5000 (max)"]` (a real, genuine value from the
generated example).

The **authoritative** constrained payload is `forward_context`, not
`constraints` — `constraints` describes the rule; `forward_context` is the
already-clamped result. A caller must submit `forward_context` verbatim to
the matching execute endpoint; the Decision Token's `payload_hash` is bound
to `forward_context`, not to the original `context`, so submitting the
original payload fails `PAYLOAD_HASH_MISMATCH` at the gate (§9, §12) —
this is what makes "CONSTRAIN may execute only the constrained payload,
never the original unsafe payload" an enforced invariant, not a convention
callers must remember to honor.

## 16. Audit correlation

Every path — decision and actuation — writes to the append-only hash-chain
audit log (`src/mcc_core/audit.py`, `fsync` on every write, no buffered
writes). The fields that let a caller correlate a proposed action all the
way through to its audit record:

| Stage | Field | Where |
|---|---|---|
| Proposed action | `transaction_id`, `idempotency_key`, `actor_id`, `resource_id` | Request body |
| MCC decision | `audit_id` | `/evaluate` response — the audit entry hash for the decision itself |
| Decision token | `jti` (token id), `audit_ref` (decision's audit hash, embedded in the token) | `decision_token` |
| Execution gate result | `audit_ref` | `/…/execute` response — the audit entry hash written **before** actuation for this attempt |
| Audit record | recomputable hash chain | `GET /verify` (integrity), `GET /export` (full log) |

The invariant this enables: **audit-before-actuation.** The coordinator
writes the audit entry for an execution attempt *before* calling the
executor, not after — so a crash between authorization and execution still
leaves a durable record that the attempt was authorized and about to run,
never a record that silently omits an attempt that actually reached the
upstream. `tests/test_coordinator.py` and
`tests/examples/test_egress_governance_audit.py` cover this ordering
directly.

`GET /verify` recomputes every entry's hash and confirms the chain links
correctly, returning the signing key needed to verify any token this
Gateway issued. `GET /export` hands the full log to an external auditor,
self-verifying (it carries its own chain-validity flag and public key).

## 17. Redis/multi-instance notes

A single-process pilot deployment can run entirely in-memory (nonce,
idempotency, velocity, challenge, revocation registries). A multi-instance
deployment **must** back all of these with Redis for the fail-closed
guarantees in §9–§11 to hold across instances — an in-memory registry
protects only within one process.

- `nonce_registry_from_env`, `idempotency_registry_from_env`, and the
  equivalent constructors for velocity/challenge/revocation are all
  **env-selectable with no silent fallback**: if a deployment declares
  Redis required and it is unreachable, construction fails closed rather
  than silently returning an in-memory registry.
- `GET /ready` (§ below) reflects this directly — a deployment that
  declared Redis required reports `ready: false` (HTTP 503) if Redis is not
  reachable, rather than reporting healthy while quietly running
  degraded.
- Every cross-instance guarantee in this document (atomic nonce claim,
  atomic idempotency reservation, atomic single-use challenge/approval
  consumption) is proven by dedicated `scripts/redis_*_smoke.py` E2E
  scripts and `tests/test_*_redis.py`/`tests/test_challenge_redis.py`
  suites against a real Redis instance — not assumed from the in-memory
  behavior.

This contract makes no claim beyond that: it does not claim geo-distributed
consensus, multi-region failover, or any guarantee beyond what a single
shared Redis (or Redis Sentinel, per `tests/` coverage) actually provides.

## 18. Error model

**Strictness matrix** — which request schemas reject unknown fields
(`extra="forbid"`) versus which stay open, verified empirically (not
assumed) against the running gateway, updated by PR #80:

| Endpoint | Schema source | Unknown top-level field | Unknown nested field (inside `context`) | Missing required field |
|---|---|---|---|---|
| `POST /evaluate` | `gateway/app.py::EvaluateRequest` (`extra="forbid"`, fixed by PR #80) | HTTP 422 | **Allowed** — `context` stays a generic, unvalidated dict by design (§6, §21) | HTTP 422 |
| `POST /mandates/execute` | `governance_api.py`'s `_Strict` (`extra="forbid"`) | HTTP 422 | n/a (payload also a generic dict) | HTTP 422 |
| `POST /approvals/{id}/execute` | `_Strict` | HTTP 422 | n/a | HTTP 422 |
| `POST /consensus/challenge` | `_Strict` | HTTP 422 | n/a | HTTP 422 |
| `POST /consensus/execute` | `_Strict` | HTTP 422 | n/a | HTTP 422 |

Real, genuine example of a `/evaluate` 422 for a **missing required field**
(`action`):
[`examples/malformed-request.response.json`](examples/malformed-request.response.json)
— `{"detail": [{"type": "missing", "loc": ["body", "action"], "msg": "Field required", ...}]}`,
FastAPI/Pydantic's own validation error shape, unedited.

An **unknown top-level field** (e.g. `not_a_real_field`) now produces the
same status with Pydantic's standard `extra_forbidden` shape —
`{"detail": [{"type": "extra_forbidden", "loc": ["body", "not_a_real_field"], "msg": "Extra inputs are not permitted", ...}]}`
— exercised directly against the running gateway by
`tests/test_gateway.py::test_http_evaluate_rejects_unknown_top_level_field`
rather than duplicated here as a second static file.

**HTTP status codes used across the surface:**

| Status | Meaning |
|---|---|
| `200` | A response was produced — this includes DENY/ESCALATE decisions and BLOCKED execution outcomes. A 200 is not itself a success signal; check `decision`/`status`. |
| `401` | Missing or incorrect `X-API-Key` / `X-Operator-Key`. |
| `403` | Operator boundary present but the action is refused for the operator (see `docs/GOVERNANCE_HTTP_API.md`). |
| `409` | A required backend (e.g. challenge service) is not configured for this deployment — fail-closed, not a client error. |
| `422` | Request schema validation failed (see strictness matrix above). |
| `503` | `GET /ready` only — a required dependency is not reachable. |

**Reason-code prefixes** actually used by the runtime (not paraphrased —
pulled directly from `src/mcc_core/gate.py` and
`src/mcc_core/idempotency.py`): `NO_TOKEN`, `UNTRUSTED_KEY`,
`INVALID_SIGNATURE`, `AUDIENCE_MISMATCH`, `INVALID_TIME_WINDOW`,
`TOKEN_NOT_YET_VALID`, `TOKEN_EXPIRED`, `NON_EXECUTABLE_VERDICT`,
`POLICY_HASH_MISMATCH`, `ACTION_HASH_MISMATCH`, `PAYLOAD_HASH_MISMATCH`,
`BINDING_MISMATCH`, `NONCE_REJECTED`, `GATE_ERROR`, `VERIFIED`,
`DUPLICATE_INFLIGHT` (`"operation already reserved"`),
`DUPLICATE_UNKNOWN` (`"operation outcome UNKNOWN; requires reconciliation, not retry"`),
`DUPLICATE_EXECUTED` (`"operation already executed"`),
`BINDING_CONFLICT` (`"logical operation bound to a different action/resource/payload"`),
`CHALLENGE_NOT_OPEN: state <STATE>`.

The `reason` field in `/evaluate` responses (decision refusals from the
`AuthorityModel`, e.g. `"identity 'x' holds no verified mandate for
authority 'y'"`) is human-readable prose, **not** a stable machine code —
an integrator should not pattern-match on it. The gate/coordinator
reason-code prefixes above, returned in `/…/execute` responses, **are**
stable strings suitable for programmatic branching.

For the SDK-level, framework-neutral stable error taxonomy (`ContractErrorCode`,
`ErrorCategory`, retryability) that sits above this raw HTTP contract, see
`docs/INTEGRATION_CONTRACT.md` and `sdk/python/src/mcc_client/contract.py` —
this document does not duplicate that taxonomy, it is the HTTP shape that
taxonomy is derived from.

## 19. Security expectations for integrators

- Treat `X-API-Key` and `X-Operator-Key` as secrets; this contract does not
  itself define key issuance, rotation, or a production key-management
  process — that is explicitly out of scope here (see
  `docs/GOVERNANCE_HTTP_API.md`'s auth boundary section and
  `gateway/trust.py` for the multi-issuer trust set that exists at the
  Ed25519 signing-key layer, which is separate from these HTTP API keys).
- Never treat a `200` response as authorization by itself — always inspect
  `decision`/`status`. A DENY, ESCALATE, or BLOCKED response is a normal,
  successful HTTP call that means **do not execute**.
- Never execute against `context` after a CONSTRAIN verdict — always
  `forward_context`. The gate enforces this via payload-hash binding (§12,
  §15), but an integrator that ignores `forward_context` and tries the
  original payload anyway will simply see every execute call fail
  `PAYLOAD_HASH_MISMATCH` — it is not a silent bypass, but it is wasted
  work worth avoiding.
- Never fabricate or reuse a nonce/idempotency key across genuinely
  different business operations — idempotency is a safety mechanism, not
  an obstacle to route around with fresh keys per retry of the *same*
  operation.
- Verify Decision Tokens independently when feasible: `GET /verify` and
  `GET /export` expose the public signing key precisely so a caller (or a
  third-party auditor) is not required to trust the Gateway's own runtime
  state — the token's signature is checkable offline.

## 20. Current implementation status

| Surface | Status |
|---|---|
| `POST /evaluate` | **Implemented.** |
| `POST /execute` (unified) | **Not implemented.** Documented as target only; see §5. |
| `POST /mandates/execute` | **Implemented.** |
| `POST /approvals/{request_id}/execute` | **Implemented.** |
| `POST /consensus/challenge` | **Implemented.** |
| `POST /consensus/execute` | **Implemented.** |
| `GET /health` | **Implemented.** |
| `GET /ready` | **Implemented.** |
| `GET /verify` | **Implemented.** |
| `GET /export` | **Implemented.** |
| Approval/trust administration routes | **Implemented**; documented fully in `docs/GOVERNANCE_HTTP_API.md`, not restated here. |

## 21. Known gaps

- **No unified `/execute` endpoint** (§5) — three action-specific endpoints
  cover its intended scope today; a caller must pick the right one.
- ~~`/evaluate` request schema is not strict at the top level~~ — **fixed by
  PR #80.** `EvaluateRequest` now rejects unknown top-level fields with
  HTTP 422 (`extra="forbid"`), matching every governed execute endpoint.
  See §6, §18.
- **`context` remains a generic, unvalidated `Dict[str, Any]`** (§6, §18) —
  this is an intentional, documented scope limit, not an oversight: action
  payload shapes are domain-specific (payment/infra/robotics profiles each
  define their own canonical payload), and enforcing one fixed nested
  schema for `context` at the Gateway HTTP boundary would require
  redesigning the profile layer, which is out of scope for a request-schema
  hardening change. An unknown key inside `context` is accepted, not
  rejected. The same applies to `mandate`/`context` on the governed execute
  endpoints and to consensus `votes` entries, which are also generic dicts.
- **No production API-key issuance/rotation process documented for the
  `X-API-Key`/`X-Operator-Key` HTTP boundary** (§19) — the mechanism exists
  (header-based, checked against configured keys), but a full lifecycle
  (issuance, rotation, per-caller scoping) is not yet specified at this
  layer. `gateway/trust.py`'s Ed25519 multi-issuer trust set (for
  Decision Token signing/verification) is more mature and is out of scope
  confusion to conflate with these HTTP API keys.
- **`reason` strings on `/evaluate` are not a stable taxonomy** (§18) — they
  are the live `AuthorityModel`'s human-readable prose. Only the
  gate/coordinator-level reason-code prefixes are stable.

## 22. Residual risks

- A caller that does not re-verify a Decision Token's signature/claims
  independently is fully trusting the Gateway's own re-verification at
  actuation time; this contract does not change that trust model, only
  documents it.
- Multi-instance deployments that do **not** configure Redis for
  nonce/idempotency/velocity/challenge lose the cross-instance guarantees
  in §17 while still appearing to function correctly on a single instance
  — `GET /ready` is the intended safeguard, but only if an operator
  actually wires deployment-required-dependency checks correctly for their
  topology.
- A caller with a typo'd key **inside** `context` still gets a silent
  field-drop rather than an error, since `context` is intentionally
  unvalidated (§21) — PR #80 closed this for top-level fields only. This is
  a real, accepted ergonomic/safety trade-off for integrators, not
  something this contract claims to have eliminated.
- This document describes the Gateway's HTTP shape as of this PR; it is not
  itself enforced by a runtime schema-conformance check beyond the
  lightweight structural test in this repository's test suite (§ below) —
  drift between this document and the running code is possible in future
  changes unless that guard is maintained.

## 23. Example integration flow

All requests/responses below are byte-identical to files generated by the
real, running Gateway during this PR's authoring — no field was hand-typed
into a response file.

```
1. Propose a payment.

   POST /evaluate
   → examples/allow.request.json

   Response: ALLOW, with a signed Decision Token.
   → examples/allow.response.json

2. Execute it via the standing mandate that justified the ALLOW
   (POST /mandates/execute), or via consensus if this deployment
   requires it (POST /consensus/execute) — submitting forward_context
   from step 1, not a re-derived payload.

3. An over-limit payment instead comes back CONSTRAIN.

   POST /evaluate
   → examples/constrain.request.json

   Response: CONSTRAIN, amount clamped 99000 -> 5000, token bound to
   the CLAMPED payload only.
   → examples/constrain.response.json

   Executing this must submit forward_context (amount: 5000), never
   the original context (amount: 99000) — the gate's payload-hash
   binding rejects the original.

4. An action with no mandate path at all comes back DENY, no token,
   nothing to execute.
   → examples/deny.request.json / examples/deny.response.json

5. An action above standing authority comes back ESCALATE. No token;
   the agent's job here is to stop and wait for
   docs/ESCALATE_APPROVAL.md's human-approval loop, not retry.
   → examples/escalate.request.json / examples/escalate.response.json

6. A consensus-gated action executes once successfully, then a replay
   of the identical signed evidence against the same (now-consumed)
   challenge is rejected before any re-execution:
   → examples/replay-deny.request.json
   Real rejection: {"status": "BLOCKED",
                     "reason": "CHALLENGE_NOT_OPEN: state CONSUMED",
                     "decision": "DENY"}

7. Resubmitting the same idempotency_key for an operation that already
   executed is rejected without re-invoking the executor:
   → examples/idempotency-conflict.response.json
   {"status": "BLOCKED", "reason": "operation already executed"}

8. A malformed /evaluate request (missing the required "action" field)
   is rejected by schema validation before any policy evaluation runs:
   → examples/malformed-request.response.json
```

---

The model proposes.
MCC decides.
The gate enforces.
The audit chain records.
