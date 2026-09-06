# Durable Logical-Operation Safety (Round 17)

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
        await self.idempotency.mark_failed(idem_key)   # <-- deletes the key
    ...
    return ActuationResult(ActuationStatus.EXECUTION_FAILED, ...)
```

`mark_failed` deleted the idempotency record unconditionally. A caller who
retried with a fresh, independently valid, differently-nonced authorization
for the same logical operation would be admitted again — even though the
first attempt's external side effect might already have happened (a timeout,
a dropped connection, or a lost response all look identical to "the executor
raised" from the coordinator's point of view). The old idempotency binding
also keyed only on `payload_hash` (`str(token.get("payload_hash", ""))`),
so the same `idempotency_key` could, in principle, be silently reused across
a different `action` or a different `resource` without being rejected as a
distinct operation.

## Blocker -> fix map

| Round 16/17 blocker | Fix |
|---|---|
| `mark_failed` releases ownership after any executor exception, regardless of whether the external call was ever attempted | `coordinator.enforce` now only ever releases the logical operation for a *pre-dispatch* failure (audit-before-actuation, velocity, or the dispatch-commit call itself). Once `commit_dispatch` succeeds, an executor exception calls `mark_unknown`, never `release`/`mark_failed`. |
| Logical-operation identity was `payload_hash` alone | `binding_ref = hash_document({"action": action, "resource": resource_id, "payload_hash": payload_hash})`. A mismatch on any of the three is `ReserveStatus.BINDING_CONFLICT`, rejected before any reservation. |
| No durable "dispatch ownership" boundary before the external call | `IdempotencyState.DISPATCH_OWNED`, committed via `commit_dispatch` strictly after audit-before-actuation and strictly before `executor()` is invoked. |
| `UNKNOWN`/indeterminate state didn't exist | `IdempotencyState.UNKNOWN` — set on any executor exception, and on a failure to durably persist `EXECUTED` after a genuine external success. Blocks `reserve()` (`ReserveStatus.DUPLICATE_UNKNOWN`) exactly like `EXECUTED` does. |
| State mutation was read-then-write, not fenced | Every mutating call (`commit_dispatch`/`mark_executed`/`mark_unknown`/`release`/`resolve_unknown`) takes the `fence` (generation) token `reserve()` issued and performs a single atomic compare-and-swap (a Lua script in Redis; a synchronous critical section in the in-memory backend) against both the current state and that fence. |
| `get_state` returned `None` on both "not found" and "backend down" | `get_state` raises `IdempotencyBackendUnavailable` on any backend failure; `None` means, unambiguously, "no record". |
| No reconciliation path | `examples/gpt6_astra_reference/reconciliation.py` — read-only; the ONLY thing that may move `UNKNOWN -> EXECUTED`, and only from positive, exact external evidence (an issue whose body carries the operation's own marker). |
| No resource-binding check between the authorized resource and the actuator's own configured destination | `github_actuator.ResourceBoundActuator` — checked synchronously, before any HTTP call. |
| The Astra-facing request path had no `logical_operation_id` concept at all | `models.require_logical_operation_id` — a protected action's request is rejected before governance is ever invoked if it doesn't carry one; it becomes the signed token's `idempotency_key`. |

## State machine

```
                    reserve()
       (absent) ─────────────────────────► RESERVED
                                             │  │
                              commit_dispatch│  │release() (fenced; only from RESERVED)
                                             │  └──────────────► (absent)   [retry-eligible]
                                             ▼
                                      DISPATCH_OWNED ── the point of no return
                                       │           │
                          mark_unknown()│           │mark_executed() (fenced)
                                       ▼           ▼
                                   UNKNOWN      EXECUTED  ── terminal
                                       │
                     resolve_unknown() │ (fenced; positive external
                                       │  evidence only; never creates)
                                       ▼
                                   EXECUTED
```

* `RESERVED` is the only state with a TTL that feeds admission logic — a
  reservation abandoned before any dispatch commitment is safe to recover
  (no external call could have been attempted).
* `DISPATCH_OWNED`, `UNKNOWN`, and `EXECUTED` are written with **no**
  expiry. None of the three ever becomes admittable again through the
  passage of time; `reserve()` on any of them returns `DUPLICATE_INFLIGHT`,
  `DUPLICATE_UNKNOWN`, or `DUPLICATE_EXECUTED` respectively, forever, until
  an explicit, independent reconciliation resolves `UNKNOWN -> EXECUTED`.
* A record with a `binding` (the `action`/`resource`/`payload_hash` triple)
  that does not match the presented binding is `BINDING_CONFLICT` — a
  distinct outcome from a plain duplicate, at every state.
* `mark_executed`/`resolve_unknown` accept an optional `ttl_seconds` purely
  as an operator-controlled storage-retention knob; it defaults to `None`
  (no expiry) and is never consulted by `reserve()`'s admission logic. Set
  it deliberately, as a distinct, explicit garbage-collection decision, if
  and when a deployment needs to bound storage growth for terminal records —
  never as a substitute for real archival.

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
  single-process dict, documented as such, and is refused outright by
  `deployment_mode.is_enforcement_mode()` for a real deployment (see
  `nonce_registry_from_env`'s sibling guard in `idempotency_registry_from_env`
  once wired the same way at the deployment-mode layer). `test_idempotency.py`
  carries an explicit negative control
  (`test_inmemory_registry_is_not_durable_across_instances`) proving two
  in-memory instances do **not** share state — precisely so the Redis
  durability tests are not mistaken for an artifact of both sides reading
  the same in-process dict.
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
   and never reaches `executor()` at all — proven for two concurrent
   submissions (`test_concurrent_duplicate_exactly_one_winner`) and for two
   *separately signed, separately nonced* authorizations presented
   sequentially or concurrently (`test_two_valid_tokens_same_key_at_most_one_side_effect`,
   scenario 23).
2. **A second, fresh, independently valid authorization for the same
   logical operation can never trigger a second dispatch while the first is
   unresolved or resolved.** `DISPATCH_OWNED`, `UNKNOWN`, and `EXECUTED` all
   block `reserve()` unconditionally and indefinitely (scenario 5/18/23) —
   this is the literal meaning of "AUTHORIZED != SAFE_TO_ACTUATE": passing
   the nonce/signature/mandate checks again is necessary but never
   sufficient to reach the actuator a second time.
3. **A raise, timeout, disconnect, or lost response after dispatch
   commitment never frees the operation for a retry.** It becomes `UNKNOWN`
   and stays there — the only way out is `resolve_unknown`, which itself
   only ever fires on independently verified positive evidence and never on
   the absence of evidence (negative/inconclusive results leave `UNKNOWN`
   untouched — scenario 8/17/18).
4. **A stale owner cannot mutate a newer generation's record.** Every
   mutation is fenced by the exact generation token `reserve()` issued;
   a superseded generation's `mark_executed`/`mark_unknown`/`release` calls
   are rejected outright (scenario 15/16), so a crashed-then-recovered
   process replaying an old attempt cannot regress or hijack the current
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

## Resource binding

`github_actuator.ResourceBoundActuator` performs a synchronous,
pre-external-call equality check between the resource a request was
authorized for and the actuator's own `GitHubActuatorConfig.repo` (fixed at
construction time, from `MCC_ASTRA_GITHUB_REPO`, never read from the
proposal or the governed payload). A mismatch raises `ResourceBindingError`
before any network I/O — proven by pointing the actuator at a deliberately
unreachable `base_url` and confirming the exception is the binding error,
not a connection failure (`tests/test_gpt6_astra_durable_operation_safety.py`).
This does not change the shared `gateway.governance_service.Upstream`
contract (`(action, payload) -> Any`) that every other governed executor in
this repository (`pilot_notify`, `clinic_service`) also uses — the check is
entirely local to this reference actuator's own wiring.

## Reconciliation

`examples/gpt6_astra_reference/reconciliation.py` is the narrowest reusable
piece needed for the one real actuator this repository ships
(`GitHubIssueActuator`). It is read-only:

* it never issues a `POST`;
* it looks for an issue whose body contains
  `github_actuator.logical_operation_marker(logical_operation_id)` — a
  marker `LogicalOperationMarkerActuator` appends to every issue this
  actuator creates, purely so a later, independent lookup has something
  exact to match on (the real "create issue" endpoint has no idempotency
  parameter to echo back);
* "not found", a transport error, a timeout, and a non-2xx response are all
  treated identically — as inconclusive, leaving `UNKNOWN` exactly as it
  was;
* a positive match calls `idempotency.resolve_unknown(key,
  expected_generation=...)`, which is itself a fenced CAS from `UNKNOWN` to
  `EXECUTED` — safe to race against a late-arriving legitimate completion of
  the very same dispatch, a blocked fresh retry, or a second reconciliation
  worker (exactly one write applies; see
  `tests/test_idempotency.py::test_reconciliation_races_with_late_completion_exactly_one_wins`).

## What is intentionally out of scope here

* True exactly-once delivery against an external API with no
  idempotency-key support is not achievable by any client-side change; see
  "Exactly-once safety" above.
* Automatic, unattended reconciliation scheduling (a background worker that
  periodically calls `reconcile_github_issue_operation` for every `UNKNOWN`
  operation) is not wired up as a running service in this reference
  integration — the function is provided, tested, and safe to call
  repeatedly (idempotent: a second reconciliation attempt on an already-
  `EXECUTED` operation is a no-op), but operating it on a schedule is a
  deployment concern for a real integration, not a demo-repo default.
