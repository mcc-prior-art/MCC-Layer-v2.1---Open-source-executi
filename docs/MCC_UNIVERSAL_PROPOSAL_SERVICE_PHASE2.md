# MCC Universal Proposal Service — Phase 2

> **PROPOSAL != PERMISSION.**
> **TENANT_ID != AUTHORITY.**
> **PROPOSAL SERVICE != EXECUTION ENGINE.**
>
> INTELLIGENCE CAN PROPOSE.
> AUTHORITY MUST VERIFY.
> EXECUTION MUST ENFORCE.

## 0. What Phase 2 adds, and what it does not

Phase 1 (`docs/MCC_UNIVERSAL_PROPOSAL_SERVICE_PHASE1.md`) shipped a
transport-neutral, strictly non-actuating proposal/status boundary — any
agent framework could register a governed operation's identity and later
ask what happened to it, but nothing could ever execute through it.

Phase 2 closes the gap the Phase 1 doctrine boxed as **"MCC INDEPENDENT
AUTHORITY BOUNDARY (future phase)"**: it lets a tenant-owned, durably
registered proposal actually enter the real, unmodified governed execution
path this repository already ships.

```
authenticated tenant
    |
    v
ProposalRegistry.get(tenant_id=, logical_operation_id=)   <- ownership + the
    |                                                         proposal's OWN
    |                                                         stored content
    v
mcc_core.authority.AuthorityModel.evaluate(identity=tenant_id, ...)
    |                                                       <- trusted verdict
    v
mcc_core.core.DecisionEngine.issue_token                  <- signed authority
    |
    v
mcc_core.coordinator.EnforcementCoordinator.enforce         <- the ONE
    |                                                         execution path
    v
mcc_core.idempotency.{InMemory,Redis}IdempotencyRegistry     <- durable
    |                                                          identity =
    |                                                          (tenant_id,
    |                                                          logical_op_id)
    v
the injected upstream actuator
```

**What did NOT change:** there is still exactly one `ExecutionGate`, one
`EnforcementCoordinator`, one durable execution registry, and one durable
execution identity — `(tenant_id, logical_operation_id)`, established by
PR #105. Phase 2 introduces **zero** new decision logic, **zero** new token
format, and **zero** second execution path. It introduces exactly one new
service boundary — `gateway.proposal_execution_service.
ProposalExecutionService` — that composes the SAME public primitives
`examples/governed_agent/mcc_client.py` and `gateway/governance_service.py`
already use for the identical purpose.

`mcc_proposal.service.MCCProposalService` itself is unchanged in spirit: it
still never imports the Gate, the coordinator, the authority model, or a
signing key (`tests/test_proposal_service_architecture_guards.py` still
enforces this statically over every file under `src/mcc_proposal/`). The
bridge lives in `gateway/` instead — the same package that already legitimately
wires the coordinator/authority/gate together for the HTTP governance layer.

## 1. Proposal identity

Unchanged from Phase 1: `logical_operation_id` is caller-supplied, never
generated/inferred/substituted, and stable across retries. It becomes the
signed token's `idempotency_key` at authorization time — the exact same
value, never regenerated.

**New in Phase 2:** the `ProposalRegistry` (`InMemoryProposalRegistry` /
`RedisProposalRegistry`) now durably stores the proposal's canonical
`action`, `resource`, and canonical `payload` alongside its `binding` hash
— not merely the hash. This is what lets authorization read ONE source of
truth for what it is about to authorize, rather than accepting an
independently re-supplied payload that could diverge from what was
actually proposed (see §3). A record written before this field existed, or
written directly via the low-level registry API with no content, has
`action is None` — `ProposalExecutionService` treats that as "no governable
content available" and fails closed rather than guessing.

The Redis wire format changed accordingly: Phase 1's `binding|created_at`
pipe-delimited string became a single JSON document (`{"binding",
"created_at", "action", "resource", "payload"}`). This is a legitimate,
intentional Phase 2 evolution of the storage contract — the
`REGISTERED`/`IDEMPOTENT_DUPLICATE`/`BINDING_CONFLICT`/fail-closed-on-
backend-failure invariants `tests/test_mcc_proposal_registry.py` proves are
unchanged; only the bytes on the wire changed shape (see that file's
updated tests for the exact before/after).

## 2. Tenant identity

`tenant_id` is the authenticated, trusted, server-side identity — exactly
the same trust boundary Phase 1's `MCCProposalService.submit_proposal`/
`get_operation_status` already required (never taken from proposal payload
content, never taken from the proposal's own `actor` field, which remains
untrusted transport content). `ProposalExecutionService.
authorize_and_execute(tenant_id=, logical_operation_id=)` takes exactly
these two parameters and nothing else — there is no payload parameter for a
caller to supply, so there is no way for a caller to present a governed
body that differs from the tenant's own stored proposal.

`AuthorityModel.evaluate(identity=tenant_id, ...)` uses `tenant_id` — never
the proposal's `actor` field — as the authority-lookup identity. This is a
deliberate design choice: allowing a caller-supplied `actor` string to
select which authority policy applies would let any tenant claim another
identity's authority simply by naming it in a proposal payload. Authority
mandates are therefore configured per-`tenant_id`, mirroring
`gateway/pilot_policy.py`'s existing per-identity mandate convention.

## 3. Operation binding

Reused, not reinvented: `mcc_proposal.binding.compute_proposal_binding`
(`hash_document({action, resource, payload_hash})` where `payload_hash =
hash_payload(profile.canonical_payload(payload))`) is the SAME formula
Phase 1 already used to detect a conflicting resubmission. Phase 2 calls it
a second time, at authorization time, over the record's OWN stored content,
and compares the result to the record's OWN stored `binding` before issuing
any token. A mismatch can only mean storage corruption (the registry is
already tenant-scoped, so this is never "someone else's record") and fails
closed with `REJECTED` — zero token issuance, zero actuator calls.

Because `authorize_and_execute` never accepts a payload parameter, there is
no seam at which a caller could present a body that diverges from what was
authorized: the ONLY payload that is ever hashed, signed, gate-verified,
and dispatched is `dict(record.payload)` (or, for a `CONSTRAIN` verdict,
the authority-clamped rewrite of it) — deep-copied synchronously before the
coordinator's first `await`, mirroring the Round-24 hardening in
`examples/gpt6_astra_reference/pipeline.py`'s `enforce_authority`, so no
live reference held elsewhere can mutate it between Gate verification and
actual dispatch.

## 4. Authority issuance

`ProposalExecutionService` evaluates `mcc_core.authority.AuthorityModel.
evaluate(identity=tenant_id, action=record.action, context=record.payload)`
— the SAME declarative, tenant/identity-keyed mandate-and-policy engine
`examples/governed_agent/mcc_client.py`'s `GovernedMCCClient` and
`egress_proxy`'s `AuthorityModel`-based runtime already use, reusing its
four-verdict result (`ALLOW`/`DENY`/`ESCALATE`/`CONSTRAIN`) unmodified.

* `DENY` → `ProposalExecStatus.DENIED`. No token issued.
* `ESCALATE` → `ProposalExecStatus.ESCALATED`. No token issued. (The
  human-approval consumption loop — `ApprovalService` — is not wired into
  this bridge in this round; see §11 Remaining limitations.)
* `ALLOW` / `CONSTRAIN` → a signed token is issued via
  `mcc_core.core.DecisionEngine.issue_token`, carrying (at minimum):

  | claim | value |
  |---|---|
  | `tenant_id` | the trusted, authenticated `tenant_id` parameter |
  | `idempotency_key` | the proposal's own stable `logical_operation_id` |
  | `action` | `record.action` |
  | `resource_id` | `record.resource` |
  | `payload_hash` | `hash_payload(forward_context)` (the authority-authorized, possibly-clamped body) |
  | `subject` / `actor_id` | `tenant_id` |
  | `auth_claims` | `profile.auth_claims(forward_context)` (action-profile-specific, e.g. payment fields) |
  | `nonce`, `iat`/`nbf`/`exp`, `policy_id`/`policy_hash`, `jti` | the standard `DecisionEngine` claims, unchanged |

  `mandate_id` is intentionally omitted — Phase 2's authority decision comes
  from the tenant-keyed `AuthorityModel`, not a pre-issued, individually
  signed `Mandate` object; there is nothing to bind a `mandate_id` to.

## 5. Execution boundary

The token is presented to `mcc_core.coordinator.EnforcementCoordinator.
enforce()` — the identical public method every other production/reference
call site (`GovernanceService`, `GovernedMCCClient`,
`examples/gpt6_astra_reference/pipeline.py`) already calls. Nothing about
the coordinator's a-h ordering, the Gate's signature/audience/expiry/
binding/nonce verification, velocity reservation, or audit-before-actuation
changes for a proposal-originated token — it is, from the coordinator's
point of view, an ordinary signed token like any other.

No second `EnforcementCoordinator`, no second `ExecutionGate`, no
proposal-specific actuator bypass, and no direct actuator invocation from
`mcc_proposal`/`MCCProposalService` — `ProposalExecutionService` is the
ONLY new file that ever calls `coordinator.enforce`, and it lives outside
`src/mcc_proposal/` specifically so the static architecture guard keeps
proving that package can never become an execution authority.

## 6. Durable identity

Unchanged from PR #105: `(tenant_id, logical_operation_id)`. Every
admission/state transition inside `coordinator.enforce` — `reserve`,
`commit_dispatch`, `mark_executed`, `mark_unknown` — is scoped by this
exact pair, via the SAME `IdempotencyRegistry` instance
`MCCProposalService`'s `durable_execution_state` reads from. Two tenants
presenting the identical `logical_operation_id` (and even the identical
action/resource/payload) admit, dispatch, and resolve as two completely
independent durable records — proven directly (`tests/
test_proposal_execution_bridge.py::test_b_*`, `::test_f_*`) and against
real Redis (`scripts/redis_proposal_phase2_smoke.py`).

## 7. Status composition

Unchanged — `MCCProposalService.get_operation_status` already composed
`PROPOSED`/`RESERVED`/`DISPATCH_OWNED`/`UNKNOWN`/`EXECUTED`/`NOT_FOUND`/
`UNAVAILABLE` directly from the tenant-scoped durable registry in Phase 1,
in anticipation of exactly this phase. Phase 2 introduces no second
execution-state database and no changes to that composition logic: a
proposal `ProposalExecutionService` executes is observed through the SAME
read path a Phase-1-only deployment already exposed.

## 8. Reconciliation

`gateway.proposal_execution_service.reconcile_proposal_operation` is a new,
domain-neutral reconciliation entry point, modeled directly on
`examples/gpt6_astra_reference/reconciliation.py`'s security pattern but
made explicitly pluggable (an injected `EvidenceVerifier` async callable)
rather than hardcoded to one actuator — the Universal Proposal Service must
stay useful for any actuator, not only GitHub issues.

Tenant-scoped throughout: the proposal lookup, the durable `get_state`
read, and the terminal `resolve_unknown` call are all keyed by
`(tenant_id, logical_operation_id)`, so no tenant may ever resolve another
tenant's identical-id record (`tests/test_proposal_execution_bridge.py::
test_j_*`). Every check `examples/gpt6_astra_reference/reconciliation.py`
performs has a direct analogue here:

* proposal ownership (§1) — a non-owned or unregistered identity is
  refused, tenant-safe, before any durable lookup;
* the durable state must be `UNKNOWN` or `DISPATCH_OWNED` — anything else
  (`RESERVED`, `EXECUTED`, or no record at all) is refused, never "helped
  along";
* the stored proposal's OWN recomputed binding must match the durable
  record's `binding` — an internal-consistency check, fail-closed on
  mismatch;
* the durable record's `generation` is the CAS fence
  `idempotency.resolve_unknown` itself enforces, so a racing writer or a
  stale caller cannot double-resolve.

It never dispatches to an actuator — `verify_external_evidence` is a pure,
already-scoped LOOK (called at most once), never a side-effecting call
(`tests/test_proposal_execution_bridge.py::
test_reconciliation_never_dispatches_to_the_actuator`).

## 9. Trust boundaries

* **`tenant_id != authority`.** Holding a valid `tenant_id` proves only
  identity, never permission — `AuthorityModel.evaluate` is what converts
  identity into a verdict, and a `tenant_id` with no configured mandate
  denies by default (`AuthorityModel.default = Verdict.DENY`).
* **`proposal != authority`.** A registered `PROPOSED` record proves only
  "this tenant asked for this exact operation," never that it is
  authorized — `ProposalRegistry` and `AuthorityModel` are two entirely
  separate components; nothing about registering a proposal touches
  authority, and nothing about authority touches the proposal registry
  except to read (never write) it.
* **`proposal service != execution engine`.** `MCCProposalService` remains
  non-actuating; `ProposalExecutionService` is the ONLY component that
  bridges the two, and it is itself a thin composition of existing,
  unmodified authority/execution primitives — not a reimplementation of
  any of their decision logic.
* **The proposal's own `actor` field is never trusted for authority
  lookup, execution binding, or reconciliation** — only for observability
  (it travels in `ProposalRequestV1` purely as caller-supplied metadata,
  covered by the binding hash like every other payload field, but never
  read by `ProposalExecutionService`/`reconcile_proposal_operation`).

## 10. Failure modes (fail-closed)

| condition | outcome |
|---|---|
| proposal not owned by the authenticated tenant | `NOT_FOUND` (tenant-safe; indistinguishable from "never proposed") |
| missing/invalid `tenant_id` or `logical_operation_id` | `REJECTED`, zero registry/authority/coordinator calls |
| stored record carries no action/resource/payload (Phase-1-only record) | `REJECTED` |
| proposal/authority binding mismatch (storage corruption) | `REJECTED`, zero token issuance |
| authority verdict `DENY` | `DENIED`, zero token issuance |
| authority verdict `ESCALATE` | `ESCALATED`, zero token issuance |
| expired authority / invalid signature / replayed nonce | `BLOCKED` — caught by `ExecutionGate` inside `coordinator.enforce`, unchanged |
| durable backend unavailable | the coordinator's own `IdempotencyBackendUnavailable`/fail-closed `ERROR` reserve outcome propagates unchanged; zero actuation |
| malformed durable record / migration-required legacy record | handled unchanged by `mcc_core.idempotency` (PR #105); `ReserveStatus.LEGACY_UNMIGRATED` blocks exactly as it does for any other caller |
| conflicting proposal/durable state | `BINDING_CONFLICT` inside `reserve()`; `BLOCKED`, zero actuation |
| unresolved predecessor operation (`UNKNOWN`) | `DUPLICATE_UNKNOWN`; `BLOCKED`, zero actuation, zero automatic retry |
| proposal backend unavailable | `UNAVAILABLE`, never reinterpreted as `NOT_FOUND` |

No failure path in this bridge ever downgrades uncertainty to "safe to
execute" — every branch above either explicitly refuses or delegates to a
coordinator/gate/idempotency mechanism whose own fail-closed behavior is
unchanged by this phase.

## 11. Remaining limitations / intentionally deferred work

* **ESCALATE approval consumption is not wired into this bridge.** An
  `ESCALATE` verdict is surfaced as `ProposalExecStatus.ESCALATED` and
  stops there; a human-approval loop (`mcc_core.approvals.ApprovalService`)
  exists and is proven elsewhere in this repository, but connecting it to
  proposal-originated operations is deferred to a future round.
* **No HTTP transport for `authorize_and_execute`/reconciliation.**
  `gateway/proposal_api.py` still exposes only the Phase 1 submit/status
  endpoints; Phase 2's bridge is currently a Python service boundary,
  exercised directly (by an operator tool, a CLI, or a future HTTP router)
  rather than mounted onto the gateway's FastAPI app. Adding that endpoint
  is a thin, mechanical extension of the existing pattern
  (`gateway/governance_api.py`'s auth/serialization boundary) and does not
  change anything described in this document.
* **Consensus/challenge (Multi-Context Consensus) is not wired into this
  bridge.** `ProposalExecutionService` issues tokens via the single-signer
  `DecisionEngine` path, the same one `execute_with_mandate` uses when
  `consensus_verifier`/`require_consensus` are not configured. Requiring
  N-of-M evaluator consensus for proposal-originated operations is
  possible (the coordinator already supports it) but out of this round's
  minimum-bridge scope.
* **A per-tenant authority policy source is deployment-specific.** This
  document and the accompanying tests use `AuthorityModel.from_config`
  directly, mirroring `gateway/pilot_policy.py`'s hardcoded-for-the-pilot
  convention; a production deployment supplies its own tenant→mandate
  configuration exactly as `gateway/pilot_policy.py` already does for the
  existing single-tenant pilot.
