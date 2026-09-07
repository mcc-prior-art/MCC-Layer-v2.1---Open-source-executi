# Durable Logical-Operation Safety (Rounds 17-24)

## The defect this closes

Astra's Round 16/17 inspection identified a concrete execution-safety gap in
`EnforcementCoordinator.enforce` (`src/mcc_core/coordinator.py`) and
`InMemoryIdempotencyRegistry`/`RedisIdempotencyRegistry`
(`src/mcc_core/idempotency.py`):

```
external side effect may occur
  -> response/acknowledgement may be lost or an exception may occur
  -> current failure handling may release/delete logical-operation ownership
  -> a fresh independently valid authorization may actuate the same
     logical operation again
  -> duplicate external side effect becomes possible
```

Concretely, the old coordinator did this on *any* exception from the
executor, regardless of whether the exception happened before or after the
external call was actually attempted:

```python
except Exception as exc:
    if idem_key:
        await self.idempotency.mark_failed(idem_key)   # <-- deleted the key unconditionally
    ...
    return ActuationResult(ActuationStatus.EXECUTION_FAILED, ...)
```

`mark_failed` deleted the idempotency record unconditionally, regardless of
current state or ownership. Round 17 fixed the coordinator's own call site
(the exception handler now calls the fenced `mark_unknown`), but Round 18's
independent re-inspection found `mark_failed` itself still existed as an
unfenced, state-blind "legacy" API on both registries — reachable by any
future caller, and (worse) the Round 17 mutation-assurance defect meant to
prove this class of regression stays caught was itself only catchable on a
harmless state-label technicality. Round 18 closes both: the unsafe API is
now **removed entirely**, and the mutation defect was replaced with one that
provably reopens actuation.

## Round 17 -> Round 18 blocker -> fix map

| Blocker | Fix |
|---|---|
| (R17) `mark_failed` releases ownership after any executor exception | `coordinator.enforce` only releases the logical operation for a *pre-dispatch* failure; once `commit_dispatch` succeeds, an executor exception calls `mark_unknown`. |
| (R17) Logical-operation identity was `payload_hash` alone | `binding_ref = hash_document({"action":.., "resource":.., "payload_hash":..})`; a mismatch is `BINDING_CONFLICT`. |
| (R17) No durable "dispatch ownership" boundary | `IdempotencyState.DISPATCH_OWNED`, committed strictly after audit-before-actuation and strictly before `executor()`. |
| (R17) No `UNKNOWN`/indeterminate state | `IdempotencyState.UNKNOWN`; blocks `reserve()` exactly like `EXECUTED`. |
| (R17) State mutation was read-then-write | Every mutation is a fenced (generation-token) CAS. |
| (R18) `mark_failed` still existed as an unfenced deletion API, usable against `DISPATCH_OWNED`/`UNKNOWN`/`EXECUTED` | **Removed entirely** from both `InMemoryIdempotencyRegistry` and `RedisIdempotencyRegistry` — there is no deletion-capable call except the already-fenced `release()`, which only ever succeeds from `RESERVED` with the current generation. |
| (R18) `mark_executed` accepted an optional `ttl_seconds`, which — if a caller ever passed one — would let a **terminal** `EXECUTED` record expire and silently become re-admittable | `ttl_seconds` removed from `mark_executed`'s signature on both backends. An `EXECUTED` record is unconditionally permanent; there is no parameter that can reopen it. |
| (R18) The Astra reference stack (`_localstack.py`) constructed `InMemoryIdempotencyRegistry()` directly, bypassing the enforcement-mode gate entirely | Replaced with `idempotency_registry_from_env()` — the SAME factory production code uses — selected before any server/thread starts. `MCC_DEPLOYMENT_MODE=enforcement` now fails the stack's own construction closed unless a real Redis backend is configured. |
| (R18) `logical_operation_id` was only enforced in `cli.py`; `pipeline.run_positive_path`/`issue_authority` themselves still accepted `None`, and `live_matrix.py`/`live_redteam.py`/`adversarial.py` called them without one at all | `logical_operation_id` is now a **required** keyword argument on `run_positive_path`/`issue_authority`, validated (`models.require_logical_operation_id`) as the FIRST thing either function does — before any attestation/authority/gate/actuator call. `enforce_authority` independently re-validates the token's own `idempotency_key` too (defense in depth). Every caller across the package (CLI, adversarial scenarios, the live matrix, the live red-team loop) now mints and threads one explicitly. |
| (R18) `adversarial.build_multi_actuator` wired a RAW `GitHubIssueActuator` for `CANONICAL_ACTION`, bypassing `ResourceBoundActuator`/`LogicalOperationMarkerActuator` entirely (only `cli.py`'s path had them) | Wrapped identically to `cli.py`; `LogicalOperationMarkerActuator.logical_operation_id` is now a mutable property so ONE long-lived actuator (shared across a multi-turn adversarial scenario) can still be updated, immediately before each governed call, to the exact id that call presents — never a second, independently-drifting id. A static architecture guard enumerates every raw `GitHubIssueActuator(...)` construction site in the package and asserts each one also imports `ResourceBoundActuator`. |
| (R18) Reconciliation trusted a marker substring alone | `reconcile_github_issue_operation` now takes the real, gate-verified signed **token** the operation ran under as its single source of truth, and validates the candidate evidence against the STORED registry record on `logical_operation_id` (registry key == `token["idempotency_key"]`), `action` (must be exactly `create_github_issue`), `resource` (must equal the actuator's configured lookup destination, checked before any network call), the authorized payload (via the SAME `hash_document` binding the coordinator computed at admission, compared against the stored record's `binding`), and `generation` (fenced, exactly like every other mutation). Any mismatch refuses before resolving anything. |
| (R18) A crash after `commit_dispatch` but before `mark_unknown`/`mark_executed` could run left the operation permanently stuck at `DISPATCH_OWNED` with no path forward | `resolve_unknown` now accepts `DISPATCH_OWNED` as a source state (identically to `UNKNOWN`) — reconciliation can resolve either directly to `EXECUTED` from verified positive evidence; absence of evidence leaves either state exactly as it was. |
| (R18) The mutation-assurance defect modeling this class of regression (`idempotency-unsafe-release-after-dispatch`) mutated the coordinator to call the ALREADY-fenced `release()`, which fails harmlessly against `DISPATCH_OWNED` — so its own detector tests could only fail on a state-*label* technicality, never by proving a real duplicate actuation | Replaced with `idempotency-reserve-reopens-pending-states`, which mutates `reserve()` itself to treat `DISPATCH_OWNED`/`UNKNOWN`/in-flight `RESERVED` as available (only `EXECUTED` remains protected). Its detector (`test_no_second_actuator_invocation_after_ambiguous_first_attempt`) asserts purely on actuator invocation COUNT, deliberately independent of which state label the first attempt left behind. |

## State machine

```
                    reserve()
       (absent) ─────────────────────────► RESERVED
                                             │  │
                              commit_dispatch│  │release() (fenced; only from RESERVED)
                                             │  └──────────────► (absent)   [retry-eligible]
                                             ▼
                                      DISPATCH_OWNED ── the point of no return
                                       │           │      │
                          mark_unknown()│           │mark_ │
                                       ▼           ▼ executed()
                                   UNKNOWN      EXECUTED  ── terminal, permanent, no TTL ever
                                       │           ▲
                     resolve_unknown() │           │ resolve_unknown() (fenced; positive
                     (fenced; positive │           │  external evidence only; never
                     evidence only)    └───────────┘  creates; also accepts DISPATCH_OWNED
                                                       as a source state directly)
```

* `RESERVED` is the only state with a TTL that feeds admission logic — a
  reservation abandoned before any dispatch commitment is safe to recover
  (no external call could have been attempted).
* `DISPATCH_OWNED`, `UNKNOWN`, and `EXECUTED` are written with **no**
  expiry, ever. None of the three ever becomes admittable again through the
  passage of time; `reserve()` on any of them returns `DUPLICATE_INFLIGHT`,
  `DUPLICATE_UNKNOWN`, or `DUPLICATE_EXECUTED` respectively, forever, until
  an explicit, independent reconciliation resolves `DISPATCH_OWNED`/
  `UNKNOWN -> EXECUTED`. `mark_executed` takes no `ttl_seconds` parameter at
  all (Round 18 removed it) — there is no way to make an `EXECUTED` record
  expire.
* A record with a `binding` (the `action`/`resource`/`payload_hash` triple)
  that does not match the presented binding is `BINDING_CONFLICT` — a
  distinct outcome from a plain duplicate, at every state.
* There is no deletion-capable call except `release()`, and `release()`
  itself only ever succeeds from `RESERVED` with the CURRENT generation —
  every other `(state, fence)` combination is rejected and the record is
  left unchanged. `mark_failed` (the old unfenced, state-blind delete) does
  not exist on either backend.

## Durability model

* **Backend**: `RedisIdempotencyRegistry` is the durable, multi-instance
  backend. Every mutating operation is one atomic Lua script (`EVAL`), so
  the compare-and-swap on `(state, generation)` is indivisible even under
  concurrent callers or multiple coordinator instances sharing one Redis.
* **Across a process restart**: a `DISPATCH_OWNED`, `UNKNOWN`, or `EXECUTED`
  record survives — it has no TTL, and any new process reading the same
  Redis key sees the identical state and generation. `reserve()` from a
  fresh process is fenced exactly the same way. Proven directly in
  `tests/test_idempotency.py::test_dispatch_owned_persists_and_blocks_after_restart`
  and its `UNKNOWN`/`EXECUTED` counterparts, using two independent registry
  instances sharing one fake-Redis store (the same pattern
  `tests/test_nonce.py`/`tests/test_velocity.py` already use for
  cross-instance proofs).
* **`InMemoryIdempotencyRegistry` is explicitly NOT durable.** It is a
  single-process dict, documented as such. `idempotency_registry_from_env`
  refuses to select it — explicitly or by default — under
  `MCC_DEPLOYMENT_MODE=enforcement`, mirroring `nonce_registry_from_env`'s
  identical guard; the Astra reference stack (`_localstack.py`) now goes
  through this SAME factory rather than constructing
  `InMemoryIdempotencyRegistry()` itself, so that gate actually applies to
  it (Round 18 requirement 4). `test_idempotency.py` carries an explicit
  negative control (`test_inmemory_registry_is_not_durable_across_instances`)
  proving two in-memory instances do **not** share state — precisely so the
  Redis durability tests are not mistaken for an artifact of both sides
  reading the same in-process dict.
* **Backend outage**: every mutating call fails closed (`ReserveStatus.ERROR`
  / `False` / `ReconcileStatus.ERROR`), and `get_state` raises
  `IdempotencyBackendUnavailable` rather than returning `None`. No caller of
  this registry can distinguish "backend down" from "safe to retry" by
  accident — they are different return shapes entirely.

## Exactly-once safety: what is actually guaranteed

**Not claimed:** mathematically perfect exactly-once delivery to GitHub (or
any external API without native idempotency-key support on the create
endpoint). The real GitHub REST "create issue" call has no idempotency
parameter; a genuinely doubled *client* request (two independent processes,
each unaware of the other, each holding a *distinct* logical operation id)
would still create two issues, correctly, because it authorized two
distinct operations.

**What is guaranteed**, for one logical operation (one `logical_operation_id`
bound to one exact `action`/`resource`/`payload_hash`):

1. **At most one actuator invocation is ever permitted to proceed past the
   durable dispatch boundary.** `commit_dispatch` is a fenced CAS from
   `RESERVED` (held by exactly one `reserve()` winner) to `DISPATCH_OWNED`;
   every other concurrent or subsequent caller sees a non-`RESERVED` status
   and never reaches `executor()` at all.
2. **A second, fresh, independently valid authorization for the same
   logical operation can never trigger a second dispatch while the first is
   unresolved or resolved.** `DISPATCH_OWNED`, `UNKNOWN`, and `EXECUTED` all
   block `reserve()` unconditionally and indefinitely — this is the literal
   meaning of "AUTHORIZED != SAFE_TO_ACTUATE": passing the nonce/signature/
   mandate checks again is necessary but never sufficient to reach the
   actuator a second time. Proven independent of any specific intermediate
   state label by
   `tests/test_coordinator.py::test_no_second_actuator_invocation_after_ambiguous_first_attempt`.
3. **A raise, timeout, disconnect, or lost response after dispatch
   commitment never frees the operation for a retry.** It becomes `UNKNOWN`
   (or, if the process dies before even that write completes, stays at
   `DISPATCH_OWNED`) and stays there — the only way out is
   `resolve_unknown`, which fires only on independently verified positive
   evidence and never on the absence of evidence.
4. **A stale owner cannot mutate a newer generation's record, and cannot
   delete a current one.** Every mutation is fenced by the exact generation
   token `reserve()` issued; a superseded generation's
   `mark_executed`/`mark_unknown`/`release` calls are rejected outright, and
   `release()` itself refuses to act against anything but `RESERVED` even
   with the CURRENT generation — so a crashed-then-recovered process
   replaying an old attempt cannot regress, hijack, or delete the current
   owner's state.

Combined, this means: **for any one `logical_operation_id`, the number of
times the actuator's HTTP POST is actually invoked is bounded by the number
of times `commit_dispatch` succeeds, which is bounded by 1** (the CAS from
`RESERVED` is won by exactly one caller, and `RESERVED` itself is only
reachable from `(absent)`, which — after a `commit_dispatch` — is never
reached again for that key, since none of `DISPATCH_OWNED`/`UNKNOWN`/
`EXECUTED` ever transitions back to `(absent)`). Reconciliation cannot
increase that count: it has no path to the actuator at all — it only reads
external state and, at most, applies a state transition inside this
registry.

## Resource binding and mandatory guards on the GitHub path

`github_actuator.ResourceBoundActuator` performs a synchronous,
pre-external-call equality check between the resource a request was
authorized for and the actuator's own `GitHubActuatorConfig.repo` (fixed at
construction time, from `MCC_ASTRA_GITHUB_REPO`, never read from the
proposal or the governed payload). A mismatch raises `ResourceBindingError`
before any network I/O.

Round 18/19: this guard, together with `VerifiedFinalPayloadActuator` (Round
19; replaces the Round 17/18 `LogicalOperationMarkerActuator`), is now
mandatory on **every** path in this package that wires a real
`GitHubIssueActuator` — not just `cli.py`'s. `adversarial.build_multi_actuator`
(also used by `live_matrix.py`/`live_redteam.py`) wraps the SAME way. A
static architecture guard
(`test_every_raw_github_issue_actuator_construction_is_resource_bound`)
enumerates every raw `GitHubIssueActuator(...)` construction site in the
package and fails if any of them does not also import
`ResourceBoundActuator` — there is no alternative raw path. See "Round 19"
below for `VerifiedFinalPayloadActuator` itself and why
`LogicalOperationMarkerActuator` was removed rather than patched.

## Reconciliation: trust model

`examples/gpt6_astra_reference/reconciliation.py` is the narrowest reusable
piece needed for the one real actuator this repository ships
(`GitHubIssueActuator`). It is read-only — it never issues a `POST` — and
(Round 18) it trusts nothing about a candidate match except what it can
verify against the STORED logical-operation record:

1. **Single source of truth.** The caller passes the real, gate-verified
   signed decision **token** the operation ran under — never a
   loose bundle of independently-suppliable strings. Every value this
   function checks (`logical_operation_id`, `action`, `resource`,
   `payload_hash`) comes from that ONE token.
2. **Action.** Must be exactly `create_github_issue` — the only action this
   path understands.
3. **Resource.** The token's `resource_id` must equal the actuator's own
   configured lookup destination (`actuator_repo`) — checked BEFORE any
   network call.
4. **Payload binding.** `hash_document({"action":.., "resource":..,
   "payload_hash":..})`, computed the identical way
   `EnforcementCoordinator` did at admission time, must equal the STORED
   record's own `binding` (fetched via `idempotency.get_state`) — a token
   claiming a different action/resource/payload than what was actually
   admitted under this id is refused.
5. **Generation.** The caller's `expected_generation` must equal the stored
   record's current generation — the same fencing every other mutation
   uses, so a late-arriving legitimate completion of the SAME dispatch and
   a reconciliation call race safely (exactly one write applies).
6. **The marker.** Only once 1-5 all hold does this function even look for
   external evidence: an issue, in the query already scoped to
   `actuator_repo`, whose body contains the EXACT
   `github_actuator.logical_operation_marker(logical_operation_id)` string.
   The candidate's own reported repository is checked again defensively.

A marker substring match alone is *never* sufficient — steps 1-5 must all
pass first. Any single mismatch, or the complete absence of positive
evidence, leaves the record exactly as it was: this function never creates
anything, and never applies `resolve_unknown` on anything less than a full
match. "Not found", a transport error, a timeout, and a non-2xx response are
all treated identically — as inconclusive.

`resolve_unknown` (the registry method reconciliation calls) accepts BOTH
`UNKNOWN` and `DISPATCH_OWNED` as source states (Round 18 requirement 7) —
closing the gap where a crash after `commit_dispatch` but before
`mark_unknown`/`mark_executed` could even run would otherwise strand the
operation with no path forward at all.

## What is intentionally out of scope here

* True exactly-once delivery against an external API with no
  idempotency-key support is not achievable by any client-side change; see
  "Exactly-once safety" above.
* Automatic, unattended reconciliation scheduling (a background worker that
  periodically calls `reconcile_github_issue_operation` for every pending
  operation) is not wired up as a running service in this reference
  integration — the function is provided, tested, and safe to call
  repeatedly (idempotent: a second reconciliation attempt on an already-
  `EXECUTED` operation is a no-op), but operating it on a schedule is a
  deployment concern for a real integration, not a demo-repo default.
* No live GitHub sandbox actuation has been performed as part of this
  remediation (Round 18 explicitly out of scope) — the next step is an
  independent, read-only Astra verification of the resulting commit.

## Round 19 — final outbound payload binding, and closing marker/context drift

An independent verification of the Round 18 commit (live code execution, not
documentation) found exactly two remaining implementation defects. Both are
closed here; nothing about the state machine, authorization verification,
nonce protection, audit-before-actuation, reconciliation, dispatch ownership,
or `UNKNOWN`/`DISPATCH_OWNED` semantics documented above changed.

### Defect 1 — the payload sent to GitHub was not the payload that was verified

`ExecutionGate` verifies `token["payload_hash"]` against the canonical
payload BEFORE the coordinator ever calls the executor. But
`LogicalOperationMarkerActuator` ran *inside* that executor's call chain and
appended the reconciliation marker to `payload["body"]` **after** that
verification had already happened — so the bytes actually POSTed to GitHub
were never the exact bytes the Gate checked and the token's signature
covers. Confirmed live: for a payload `{'title': 't', 'body':
'ORIGINAL-BODY'}` whose token carried `payload_hash` for that exact
document, the actual sent body was `'ORIGINAL-BODY\n\n<!--
mcc-logical-operation-id: op-verify-1 -->'` — hash mismatch between what was
authorized and what was sent.

**Fix — construct the final payload before hashing, not after.**
`github_actuator.build_marked_payload(payload, *,
logical_operation_id)` is now the ONLY place the marker is applied, and it
is called by `governed_call.prepare_marked_call` — the ONE place every
governed call in this package prepares its call — **before** the resulting
proposal is ever canonicalized, attested, or presented to
`issue_authority`/`run_positive_path`. The marker is therefore part of the
SAME payload the Gate verifies and signs into `payload_hash`; nothing
downstream of authorization ever touches the payload again.
`LogicalOperationMarkerActuator` (which mutated post-verification) is
**removed entirely**, not patched.

As a final-boundary backstop — not the primary mechanism, which is simply
"never mutate after hashing" — `github_actuator.VerifiedFinalPayloadActuator`
wraps the innermost actuator (after `ResourceBoundActuator`, immediately
before the real HTTP POST) and refuses to invoke it unless the caller has,
immediately beforehand, armed this exact call (`.expect(action=...,
payload_hash=...)`) with the action/payload_hash it was actually authorized
under:

* for the two-step `issue_authority` → `enforce_authority` path (tamper,
  replay, expired, stale-authority-rebinding), the values armed are the
  REAL, signed `issued.token["action"]`/`issued.token["payload_hash"]`;
* for the one-step `run_positive_path` convenience path (no token exists yet
  at call time), the values armed are `hash_payload` of the exact marked
  canonical payload about to be submitted — computed with the SAME
  canonicalization (`ActionProfile.canonical_payload`, identity for
  `create_github_issue`) the real token issuance path independently applies.

Either way, the expected value is captured BEFORE the call it guards, never
derived from the payload the check is evaluating. `expect()` is single-use:
`__call__` consumes it as the first thing it does, so a mismatch — or no
arming at all — raises `PayloadBindingError` before `ResourceBoundActuator`
or `GitHubIssueActuator` ever runs, and before any network I/O.
`tests/test_gpt6_astra_final_payload_binding.py` proves, at the real
actuator/mock-network boundary (never a token-vs-registry comparison or a
before-the-Gate denial): the exact outbound bytes hash to the real token's
`payload_hash`; a title, body, or marker change made strictly after arming
is refused with zero network calls; a destination mismatch and an unarmed
call are refused identically.

### Defect 2 — a shared actuator could drift context between two operations

`cli.py`'s `run_autonomous_expansion` built ONE `_governed_actuator` for its
primary operation's `logical_operation_id`, then invoked a second, distinct
logical operation (`extra_logical_operation_id`) through the SAME actuator
instance without ever updating it. The extra action happened to be denied by
mandate action scope before reaching the actuator (so no duplicate
side-effect ever occurred), but the actuator wrapper itself carried no
structural guarantee against this — a future change reaching the actuator
under those conditions would have sent the WRONG marker.

**Fix — arm per call, not per actuator lifetime.**
`VerifiedFinalPayloadActuator` has no persistent, settable "current
operation identity" at all (unlike `LogicalOperationMarkerActuator`'s old
mutable `.logical_operation_id` property) — every `__call__` consumes
whatever was armed and nothing else, so a caller that forgets to re-arm
fails closed rather than silently reusing a prior call's expectation.
`governed_call.prepare_marked_call` is the ONE place that builds a marked
proposal AND arms the actuator, together, immediately before each governed
call; `cli.py`, `adversarial.py` (`_prepare_actuation`), `live_matrix.py`,
and `live_redteam.py` all now call it per invocation rather than mutating
shared actuator state. `run_autonomous_expansion` now mints its own marked
proposal and its own (`actuator=None`, since it is denied before reaching
the actuator anyway) call for the extra action, structurally independent of
the primary call's expectation.
`tests/test_gpt6_astra_final_payload_binding.py::test_two_operations_through_shared_actuator_no_context_leak`
proves it directly: two distinct, IN-SCOPE operations reaching one shared
actuator instance each produce an issue carrying only their own marker,
never the other's, and each outbound payload's hash is bound only to its
own verified authorization.

### Round 18 → Round 19 fix map

| Defect | Fix |
|---|---|
| Payload actually sent to GitHub could differ from the payload the Gate verified (marker appended post-verification by `LogicalOperationMarkerActuator`) | Marker embedded into the payload BEFORE canonicalization/attestation/hashing (`governed_call.prepare_marked_call` + `github_actuator.build_marked_payload`); `LogicalOperationMarkerActuator` removed; `VerifiedFinalPayloadActuator` proves action/payload_hash match the verified authorization immediately before the real HTTP POST, fail-closed on any mismatch or missing arming. |
| A shared actuator instance could be reused across two logical operations without updating its marker/identity, risking drift | No mutable settable identity remains on the actuator; every governed call arms its own single-use expectation immediately before its own use (`governed_call.prepare_marked_call`); `run_autonomous_expansion`'s two calls now each carry their own coherent context. |

## Round 21 — closing payload projection and operation-context enforcement

Round 20's independent re-verification (executing real `DecisionEngine`/
`ExecutionGate`/`EnforcementCoordinator`/actuator code) reproduced two
remaining blocker classes on top of Round 19's fix. Both are closed here;
every invariant listed under "What Round 19 preserved" above still holds,
unchanged.

### Blocker 1 — payload projection after final hash verification

`GitHubIssueActuator.__call__` reconstructed a NEW `{"title": .., "body":
..}` object before POSTing, regardless of what else the verified payload
carried. A proposal payload could carry an additional authorized field
(e.g. `labels`) that generic canonicalization retained (so it was signed
into the token and checked by `VerifiedFinalPayloadActuator`), but that
field silently disappeared at the actuator's own reconstruction step —
confirmed live: calling the actuator directly with `{"title": "t", "body":
"b", "labels": ["bug"]}` before this fix would have produced a 200 against
the mock service using only `{"title": "t", "body": "b"}`; after the fix
the SAME direct call sends `labels` through unprojected, and the mock
service's own strict schema (`extra="forbid"`) now rejects it with 422 —
proof the actuator no longer decides which fields survive the trip.

**Fix:**

1. **One explicit request schema.** `issue_contract.
   validate_github_issue_request_payload` accepts EXACTLY `title`
   (required, non-empty string) and `body` (optional, materialized to `""`
   if absent) for `create_github_issue` — any other field is a hard
   rejection, never silently discarded, and no value is ever coerced.
2. **Validated before attestation/token issuance.** `governed_call.
   prepare_marked_call` calls `issue_contract.
   prepare_complete_github_issue_payload` (schema validation, THEN marker
   embedding) before the proposal is ever canonicalized/attested/
   authorized. The three protected boundaries (`pipeline.run_positive_path`
   / `issue_authority` / `enforce_authority`) independently re-validate the
   SAME schema — a direct caller that skips `prepare_marked_call` cannot
   bypass it.
3. **No post-verification field projection.** `GitHubIssueActuator.
   __call__` now sends `json=dict(payload)` — the exact dict it was called
   with, never a reconstruction from named fields. Combined with the strict
   schema, an authorized field can never again silently disappear between
   what was signed and what is serialized.
4. **The expected action/hash stay independent of the candidate outbound
   object.** Unchanged from Round 19: `VerifiedFinalPayloadActuator`'s
   bound expectation always comes from the real signed token (two-step
   path) or the pre-submission canonical hash (one-step path) — never
   recomputed from the payload the check is evaluating.

### Blocker 2 — operation id and marker not enforced as one context

Two counterexamples: (A) a raw input body already containing a marker,
followed by this package appending a second marker for a different
operation, executing with BOTH; (B) a payload prepared with marker A, but a
GENUINE token issued with a DIFFERENT `idempotency_key` B — the Gate's own
hash check cannot catch this (the hash matches the token perfectly fine;
it says nothing about which operation the payload's own marker names).

**Fix — one immutable per-invocation operation context (`issue_contract.py`,
a module deliberately separate from `github_actuator.py` so `pipeline.py`
can depend on it without violating the "pipeline never imports the
actuator" architecture guard):**

1. **Marker syntax is closed and validated, not merely appended.**
   `build_marked_payload` now refuses (before appending anything): a raw
   body that already contains ANY marker-shaped substring — a complete
   marker, or merely a bare prefix/suffix (`reject_preexisting_marker`) —
   and a `logical_operation_id` that contains a substring able to break out
   of or inject the marker's fixed delimiters (`-->`, `<!--`, or a newline
   — `validate_operation_id_for_marker`). An existing marker is never
   silently deleted or replaced.
2. **Context coherence validated independently at all three protected
   boundaries**, not only inside `prepare_marked_call`:
   `run_positive_path`/`issue_authority` check the proposal's payload
   against the `logical_operation_id` argument BEFORE any
   attestation/authority/token call; `enforce_authority` checks the
   EFFECTIVE payload (the caller's override, or `issued.canonical_payload`)
   against the REAL signed `issued.token["idempotency_key"]` — the check
   that specifically closes counterexample B, since it is independent of
   whatever `issue_authority` did or didn't validate for the token actually
   presented. `issue_contract.require_coherent_marker_context` requires
   EXACTLY ONE well-formed marker whose id exactly equals the id being
   presented — never derived from the payload itself (circular), always
   from the caller's own explicit argument or the token's own claim. Marker
   text remains DATA, never authority: none of this substitutes for the
   real Gate's signature/binding verification, which is unaffected and
   still mandatory.
3. **No persistent mutable operation identity on the actuator.**
   `VerifiedFinalPayloadActuator` is now IMMUTABLE and single-shot — bound
   to one action/payload_hash AT CONSTRUCTION, no `.expect(...)` mutator,
   `__call__` at most once. `VerifiedDispatchSlot` (the new outer wrapper
   every construction site uses) holds at most one currently-armed,
   single-shot verifier at a time; `.expect(...)` REPLACES it, and
   dispatch clears the slot as the first thing it does. A governed call
   that forgets to (re-)arm fails closed — either because nothing is
   installed, or because whatever remains from an earlier, unconsumed
   (e.g. blocked-before-actuator) attempt does not match this call's actual
   action/payload. Two `.expect(...)` calls with no dispatch in between
   (overlap) simply mean the LATEST installed verifier is the only one that
   can ever be dispatched to — the earlier one is discarded, never
   substitutable.
4. **All callers updated consistently** (`cli.py`, `adversarial.py`
   `_prepare_actuation`, `live_matrix.py`, `live_redteam.py`, and the
   affected test helpers) to the `VerifiedDispatchSlot`/`.expect(...)` API;
   `adversarial.CountingMultiActuator.github_slot` (renamed from
   `github_verified`) is the shared slot reference these use.

`tests/test_gpt6_astra_final_payload_binding.py` (31 tests) proves all of
this through the real local authorization/Gate/coordinator path and the
actual mock GitHub HTTP receiver where the requirement calls for it
(end-to-end golden path with audit-entry verification; two genuinely
in-scope operations through one shared actuator with admission/audit/result
identity checks), plus focused final-boundary tests for every mutation
introduced strictly AFTER a call was armed (title/body/marker
add/remove/replace/action/destination — all zero POST invocations), the
four pre-existing-marker variants (matching/foreign/duplicate/malformed),
the context-A-presented-as-B rejection at both `run_positive_path` and
`issue_authority`, the hand-crafted-genuine-token-for-B-with-marker-A proof
that `enforce_authority`'s check is independent of the Gate's own hash
check, and the forget-to-arm / overlapping-arm slot-safety proofs.

### Round 20 → Round 21 fix map

| Defect | Fix |
|---|---|
| `GitHubIssueActuator` reconstructed `{"title","body"}` from named fields, silently dropping any other authorized field the token's payload_hash covered | Strict, closed request schema (`issue_contract.validate_github_issue_request_payload`) validated before token issuance, checked independently at all three protected boundaries; `GitHubIssueActuator` now sends the exact `dict(payload)` it was called with — no reconstruction. |
| A raw body already containing a marker, followed by a second marker being appended, could execute with both | `build_marked_payload` refuses any pre-existing marker-shaped substring in the raw body before appending its own. |
| A genuinely signed token for operation B could be presented alongside a payload whose marker names a different operation A — the Gate's hash check alone cannot catch this | `require_coherent_marker_context` independently checked at `run_positive_path`/`issue_authority` (payload vs. the id being presented) AND `enforce_authority` (effective payload vs. the REAL token's `idempotency_key`). |
| `VerifiedFinalPayloadActuator` was a shared, re-armable object — a stale, unconsumed expectation from an attempt blocked before ever reaching the actuator could persist | `VerifiedFinalPayloadActuator` is now immutable/single-shot, constructed fresh per call; `VerifiedDispatchSlot` holds at most one current verifier, replaced (never mutated) on each `.expect(...)`, cleared on every dispatch attempt. |

## Round 23 — marker-safety validation unavoidable at the protected boundary

Round 21's `issue_contract.validate_operation_id_for_marker` (rejects a
`logical_operation_id` containing `-->`, `<!--`, a newline, or a carriage
return) was only ever invoked from the WRITE side —
`build_marked_payload`, reached exclusively through
`governed_call.prepare_marked_call`. `require_coherent_marker_context` (the
READ/acceptance side, and the ONLY marker check `pipeline.
run_positive_path`/`issue_authority`/`enforce_authority` actually call)
never independently validated the EXTERNAL expected identity it was
comparing against — only whether it matched whatever the payload's body
happened to say. A direct caller who skipped `prepare_marked_call` and
hand-constructed a body whose marker text superficially named an unsafe id
could get that id accepted as coherent, since nothing on the acceptance
side re-checked the id itself.

**Fix — one line, at the one place both blockers already funnel through.**
`require_coherent_marker_context` now calls
`validate_operation_id_for_marker(logical_operation_id)` FIRST — before the
payload's body is inspected at all, let alone a marker "accepted". Because
`pipeline.py`'s single helper (`_require_github_issue_context_coherence`)
is the only caller of `require_coherent_marker_context`, and it is already
invoked at all three protected boundaries with exactly the required
identity source (`run_positive_path`/`issue_authority`: the explicit
`logical_operation_id` argument; `enforce_authority`: the real signed
`token["idempotency_key"]`), this one change closes the gap everywhere it
mattered, with no other call site to update.

Verified non-vacuous: `tests/test_gpt6_astra_marker_id_boundary_safety.py`
(27 tests, none routed through `prepare_marked_call`/`build_marked_payload`)
pins every rejection to `validate_operation_id_for_marker`'s own message —
disambiguating it from an incidental "no marker found" `MarkerSyntaxError`
a `\n`/`\r`-containing id could otherwise produce via unrelated regex
mechanics. Reverting the fix (`git stash` the one-line change) was
confirmed to make exactly the 18 boundary/message-pinned tests fail while
the 9 tests of pre-existing Round 21 behavior keep passing — proving the
new tests exercise the actual fix, not coincidental behavior. A
companion pair of tests proves the forward and contrapositive of
requirement 6: an id accepted through real protected execution
(attestation → authority → Gate → coordinator → actuator → mock HTTP
receiver) is guaranteed safe for `reconciliation.py`'s later
`logical_operation_marker(token["idempotency_key"])` reconstruction, and
every id rejected at the protected boundary is rejected identically by
that same reconstruction call — one validation gate, not two that could
drift apart.

### Round 21 → Round 23 fix map

| Defect | Fix |
|---|---|
| `require_coherent_marker_context` compared a payload's marker against the caller's `logical_operation_id` argument, but never validated that argument itself was safe -- a direct caller bypassing `prepare_marked_call` could get an unsafe id (`-->`/`<!--`/newline/carriage-return) accepted if a hand-crafted body's marker text matched it | `require_coherent_marker_context` now calls `validate_operation_id_for_marker(logical_operation_id)` before inspecting the payload's body at all -- validated at all three protected boundaries (`run_positive_path`/`issue_authority`/`enforce_authority`) via the one shared pipeline helper, with no way for a direct caller to skip it. |

## Round 24 — TOCTOU, per-call resource binding, and reconciliation content/shape hardening

An independent review of the Round 23 commit
(`a4c4a32c7e13fd5a3d463d27450be26588cf3c75`) reported six findings. Two
described calling `mcc_core.coordinator.enforce`/
`gateway.governance_service.GovernanceService.execute_with_mandate`
**directly**, bypassing `pipeline.py` entirely — accurate as code
observations, but not a regression: those are the shared, domain-neutral
primitives every other governed domain in this repository (payments,
infra, robotics, VoltAgent, egress) also uses, and Round 21 explicitly
required keeping GitHub-specific rules *out* of that layer. The Astra
reference boundary itself (`pipeline.py`) was independently re-verified to
still reject both cases correctly. Left as-is.

The other four were genuine, live-reproducible gaps in this package's own
code, confirmed by direct reproduction against the real chain BEFORE each
fix, then re-run to confirm each is closed:

### 1. TOCTOU via a mutable payload dict

`pipeline.enforce_authority` used the caller's own payload object, by
reference, across every `await` inside `coordinator.enforce` (idempotency
reservation, velocity, audit) between the point the Gate verifies its hash
and the point `executor()` actually dispatches it. Reproduced: arm
`VerifiedDispatchSlot` for operation A but never consume it (a blocked
attempt); start `enforce_authority` for a genuinely signed token for
operation B built on a caller-held mutable dict; mutate that SAME dict back
to A's content from inside a patched `idempotency.reserve` (an await point
strictly between Gate verification and dispatch). Before the fix: `EXECUTED`,
A's content actually sent under B's token/audit trail,
`hash(sent) != token["payload_hash"]`. Fix: `effective_payload` is now
`copy.deepcopy`'d into a private snapshot synchronously, before the first
`await` — every subsequent read (context coherence, the Gate, and
`executor()`'s dispatch) uses that same frozen copy, unreachable by any
external reference. After the fix the same reproduction correctly returns
`EXECUTION_FAILED`/`UNKNOWN` (the stale slot A correctly refuses B's real,
unmutated content) with zero issues recorded.

### 2. Resource binding not tied to the current token

`ResourceBoundActuator` only ever compared two values fixed at
*construction* time against each other — the slot's own
`authorized_resource` and the raw actuator's configured `repo` — never the
CURRENT call's actual authorized resource. Reproduced: build a slot for
`REPO_A` (matching the raw actuator's own config, unremarkably); present a
genuinely signed token naming `REPO_B`; `EXECUTED`, dispatched to `REPO_A`
regardless of what the token said. Fix: `VerifiedFinalPayloadActuator` is
now also bound, at construction, to `resource` (the current call's real
authorized resource, from the same trusted source as `action`/`payload_hash`
— the signed token's `resource_id` for the two-step path, the proposal's
resource for the one-step path) and `configured_resource` (the raw
actuator's own destination, captured by `VerifiedDispatchSlot` once);
`__call__` raises `ResourceBindingError` on mismatch, every dispatch.
`VerifiedDispatchSlot.expect(...)`/`_CountingActuator.expect(...)` (and
every call site: `governed_call.prepare_marked_call`, `cli.py`'s
tamper/replay/expired, `adversarial.py`'s `run_stale_authority_rebinding`)
now pass `resource=` alongside `action=`/`payload_hash=`.

### 3. Reconciliation resolved on marker+repo alone

`reconcile_github_issue_operation` validated the STORED REGISTRY record's
binding against the token, and the candidate's reported repository —  but
never hashed the candidate's own reported `title`/`body` and compared
against `payload_hash`. Reproduced: park an operation UNKNOWN; inject a
candidate issue with the correct marker and correct repo but completely
different content; resolved UNKNOWN → EXECUTED anyway. Fix: after the
marker+repository match, the candidate's own `{"title", "body"}` is hashed
with the same `hash_payload` the Gate uses and compared against
`payload_hash`; any mismatch refuses, leaving the record exactly as it was.

### 4. Reconciliation could never match real GitHub data

The real GitHub REST API reports an issue's repository via
`repository_url` (e.g. `"https://api.github.com/repos/{owner}/{repo}"`),
never a bare `repo` field — that field is this package's own mock
service's convenience shape. Without support for the real shape,
reconciliation could never resolve anything against genuine GitHub data at
all (fails closed — a functional gap, not a security one). Fix:
`_issue_repository_identity` recognizes both shapes; the mock service's own
`GET /repos/{owner}/{repo}/issues` filter (`_matches_repo`) was hardened
identically so an end-to-end test using a candidate reported *only* via
`repository_url` (no mock-specific `repo` field at all) is provably found
and correctly resolved.

`tests/test_gpt6_astra_round24_hardening.py` (11 tests) proves all four,
each with the exploit reproduction plus a positive control proving the
honest case still works unmodified.

### Round 23 → Round 24 fix map

| Defect | Fix |
|---|---|
| A caller-held mutable payload dict could be mutated during `coordinator.enforce`'s await window, after the Gate verified it but before `executor()` dispatched it, letting a stale slot expectation accept mismatched content | `enforce_authority` deep-copies the effective payload into a private snapshot before its first `await`; the Gate and the actuator dispatch always see the identical, frozen content. |
| `ResourceBoundActuator`/`VerifiedFinalPayloadActuator` never compared the CURRENT call's authorized resource against the actuator's real destination — only two construction-time-fixed values against each other | `VerifiedFinalPayloadActuator` is now also bound to `resource` (from the real token/proposal) and `configured_resource` (the raw actuator's own destination); every dispatch re-verifies them match. |
| Reconciliation resolved UNKNOWN/DISPATCH_OWNED → EXECUTED on a marker+repository match alone, never checking the candidate's own content against `payload_hash` | The candidate's `{"title","body"}` is hashed and compared against `payload_hash` before any resolution. |
| Reconciliation's repository check (`issue.get("repo")`) could never match the real GitHub REST API's response shape (`repository_url`, no `repo` field) | `_issue_repository_identity` recognizes both shapes; the mock service's own query filter was hardened to match. |

## Round 25 — mandatory logical_operation_id at the domain-neutral core execution boundary

Every remediation through Round 24 hardened the GPT-6 Astra reference
integration's own payload/marker/context machinery. Independent review then
established that the underlying defect this whole document exists to close —
durable execution reaching the actuator with no stable logical-operation
identity — was never actually closed at its real, authoritative boundary:
`EnforcementCoordinator.enforce()` in `src/mcc_core/coordinator.py`. That
function is the ONE domain-neutral enforcement point shared by every
governed action in this repository (payments, infrastructure, robotics,
VoltAgent, the egress proxy, the AXFlow clinic pilot, the GPT-6 Astra
reference integration, and any future integration) — Astra's own
`prepare_marked_call`/pipeline machinery is one caller among many, not the
boundary itself.

### The defect

`enforce()` treated `idempotency_key` as **optional** throughout: every
durable-safety step —
`idempotency.reserve` (admission), `commit_dispatch` (dispatch ownership),
`mark_executed`, `mark_unknown` — was wrapped in `if idem_key:`. A genuinely
valid, signed, executable (`ALLOW`/`CONSTRAIN`) decision token whose
`idempotency_key` was `None`, `""`, or whitespace-only skipped every one of
those steps entirely and still reached the real executor — with **zero**
replay protection, duplicate-suppression, or durable dispatch-ownership
record. Two independently-issued keyless tokens for the identical
action/actor/resource/payload both actuate, back to back, with nothing to
stop either.

Reproduced directly against the real coordinator (no Astra-specific code
involved at all): issue two genuinely signed, executable tokens with
`idempotency_key=None` for the same action/resource/payload; call
`coordinator.enforce()` for each. Before the fix: both return `EXECUTED`,
the test executor is invoked twice, and `AuditLog` never records a
`pre_actuation` idempotency binding for either — the coordinator never even
attempted admission.

This was independently confirmed as a real, live production gap: `main.py`'s
`GovernancePipeline.decide()` (the wired `/evaluate` consensus+challenge
runtime) minted its executable token with no `idempotency_key` argument at
all, and `gateway/governance_service.py`'s `execute_with_mandate`/
`execute_with_consensus` (backing `/mandates/execute`,
`/approvals/{id}/execute`, `/consensus/execute`) accepted and forwarded
`idempotency_key=None` with no rejection anywhere in the chain.

### The fix

**Target invariant: NO VALID LOGICAL_OPERATION_ID → BLOCKED → ZERO ACTUATOR
INVOCATIONS.** This is now enforced at the coordinator itself, unconditionally,
for every domain and every caller — not merely inside the GPT-6 Astra
reference integration.

1. **`src/mcc_core/coordinator.py`** — immediately after Gate verification
   (step a/b) and before anything else stateful (consensus verification,
   consensus-challenge consumption, actuation-time revocation re-check,
   approval consumption, durable admission, velocity reservation,
   audit-before-actuation, or the executor call), `enforce()` now validates
   `token["idempotency_key"]` is present, a `str`, and non-empty after
   stripping whitespace. Any other value returns `ActuationStatus.BLOCKED`
   with reason `MISSING_LOGICAL_OPERATION_ID: ...; fail-closed` — the
   executor is never reached. Every downstream `if idem_key:` guard around
   `reserve`/`commit_dispatch`/`mark_executed`/`mark_unknown` was removed:
   those steps are now structurally unconditional, since a valid key is
   guaranteed present by the time they run. No identity is ever
   silently generated anywhere in this path.
2. **`gateway/governance_service.py`** — `execute_with_mandate` (backing both
   `/mandates/execute` and, by delegation, `/approvals/{id}/execute`) and
   `execute_with_consensus` (backing `/consensus/execute`) now reject a
   missing/blank `idempotency_key` immediately after authorization (mandate
   authority / consensus quorum) and the PR-2/PR-3 attestation gate succeed,
   before any signed token is ever minted. This is **defense-in-depth
   only** — `_missing_logical_operation_id`'s docstring says so explicitly —
   the coordinator's own check is what actually makes this fail-closed; this
   layer only avoids spending a real signature on a request that could never
   actuate anyway.
3. **`gateway/governance_api.py`** — the `idempotency_key` field on
   `MandateExecuteRequest`/`ApprovalExecuteRequest`/`ConsensusExecuteRequest`
   was deliberately **left** `Optional[str] = None` at the transport/schema
   level rather than made a required Pydantic field. Rejecting a missing key
   at the schema layer would turn it into an HTTP 422 with no `status`/
   `reason` business payload — breaking legitimate BLOCKED responses for
   requests that are rejected for an *earlier*, unrelated reason (actor/
   resource substitution, policy drift) before idempotency is ever
   evaluated. Enforcement for this invariant lives in `governance_service.py`
   (defense-in-depth) and `coordinator.py` (authoritative) instead, both of
   which return a normal `BLOCKED` `ExecOutcome`, not a schema error.
4. **`src/mcc_core/core.py` (`DecisionEngine.issue_token`)** — deliberately
   **unchanged**: `idempotency_key` remains `Optional[str] = None`. Not
   every legitimate call to `issue_token` represents a protected-execution
   request that will ever reach `EnforcementCoordinator.enforce()` (e.g. a
   `DENY`/`ESCALATE` token, or a token minted purely for inspection/testing
   that is never enforced) — tightening the generic issuance contract would
   either break that legitimate non-execution compatibility or require
   `issue_token` to know, itself, whether its caller intends to actuate,
   which it structurally cannot. The coordinator's own check is therefore
   the sole authoritative enforcement point for this invariant, exactly as
   the module docstring already states — this decision does not weaken or
   remove it under any circumstance.

`tests/test_coordinator_mandatory_logical_operation_id.py` proves the
invariant directly against `EnforcementCoordinator.enforce()` (not routed
through Astra's pipeline helpers) for `None`, `""`, and whitespace-only
`idempotency_key` values, plus a non-string value, each with a genuinely
valid signature/action/resource/payload/policy/time-window/nonce: every case
is `BLOCKED`, the executor is invoked zero times, and no durable dispatch
record or `pre_actuation` audit entry is ever created for the attempt.

### Round 24 → Round 25 fix map

| Defect | Fix |
|---|---|
| `EnforcementCoordinator.enforce()` treated `idempotency_key` as optional (`if idem_key:` around every durable-safety step); a valid, signed, executable token with no key skipped admission/dispatch-ownership entirely and still reached the executor | Mandatory, unconditional validation immediately after Gate verification, before any other stateful step; `BLOCKED`/`MISSING_LOGICAL_OPERATION_ID` on failure; all downstream `if idem_key:` guards removed (structurally unconditional once validated). |
| `main.py`'s wired consensus+challenge runtime minted its executable token with no `idempotency_key` at all | `GovernancePipeline.decide()` accepts and forwards a caller-supplied `idempotency_key` (the existing `EvaluateRequest.idempotency_key` field) into `issue_token`; never auto-generated. |
| `gateway/governance_service.py`'s mandate/consensus execution accepted and forwarded a missing `idempotency_key` with no rejection anywhere in the chain | Defense-in-depth `BLOCKED` check added right before token issuance, after authorization and the attestation gate succeed; the coordinator remains the authoritative enforcement point. |
