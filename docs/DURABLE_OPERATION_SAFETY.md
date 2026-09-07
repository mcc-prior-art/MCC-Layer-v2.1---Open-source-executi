# Durable Logical-Operation Safety (Rounds 17-18)

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

Round 18: this guard, together with `LogicalOperationMarkerActuator`, is now
mandatory on **every** path in this package that wires a real
`GitHubIssueActuator` — not just `cli.py`'s. `adversarial.build_multi_actuator`
(also used by `live_matrix.py`/`live_redteam.py`) wraps the SAME way.
`LogicalOperationMarkerActuator.logical_operation_id` is a mutable property
precisely so one actuator instance, reused across several governed calls in
a scenario, can still be kept correctly in sync — the caller sets it to the
exact id it is about to pass to `run_positive_path`/`issue_authority`,
immediately before that call (`adversarial._prepare_actuation` is the
reference pattern). A static architecture guard
(`test_every_raw_github_issue_actuator_construction_is_resource_bound`)
enumerates every raw `GitHubIssueActuator(...)` construction site in the
package and fails if any of them does not also import
`ResourceBoundActuator` — there is no alternative raw path.

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
