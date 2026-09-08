# Tenant-Scoped Durable Execution Identity (PR #105)

## The defect this closes

PR #104 (`docs/MCC_UNIVERSAL_PROPOSAL_SERVICE_PHASE1.md`) added a
tenant-scoped `ProposalRegistry` and, in its own remediation, an
ownership-gate + binding-comparison check in front of
`MCCProposalService.get_operation_status` so that a tenant could not
observe another tenant's durable execution state merely by presenting the
same raw `logical_operation_id`.

That remediation was insufficient for one concrete case: two tenants can
**legitimately** submit the identical `logical_operation_id` **and** the
identical binding (same action, same resource, same canonical payload —
e.g. both tenants send an identical `send_notification` to `crm` with the
identical recipient). Binding comparison cannot disambiguate this case,
because there is nothing to compare — both tenants' bindings are, correctly,
the same value. The underlying reason is structural: `mcc_core.idempotency`
(`InMemoryIdempotencyRegistry` / `RedisIdempotencyRegistry`) — the ONE
durable execution state machine `EnforcementCoordinator` drives — was keyed
by the raw `key` (`idempotency_key`/`logical_operation_id`) alone, with no
tenant dimension. Under that scheme, both tenants' operations collapse onto
the identical durable record: whichever tenant reserves first durably owns
it, and the second tenant's operation is refused as a duplicate of an
operation it never submitted, or — worse — a status reader for the second
tenant could be shown the first tenant's real execution state.

## The fix: durable identity is `(tenant_id, key)`, not `key`

Every operation `mcc_core.idempotency` admits, tracks, resolves, or reports
on is now identified by the **pair** `(tenant_id, key)`, at the registry
level itself — not by a downstream binding comparison bolted on afterward.
Two tenants presenting the identical raw key **and** the identical binding
are structurally independent: separate reservations, separate generations,
separate fences, separate terminal states. Neither can observe, block, or be
unblocked by the other's record.

`tenant_id` is:

- **mandatory** on every `InMemoryIdempotencyRegistry` /
  `RedisIdempotencyRegistry` method (`reserve`, `commit_dispatch`,
  `mark_executed`, `mark_unknown`, `release`, `get_state`,
  `resolve_unknown`) — a keyword-only parameter with **no default**. An
  omitted value is a caller bug, caught immediately as a `TypeError` (or, on
  `reserve`, `ReserveStatus.ERROR` / on `get_state`, `ValueError` — see
  `_require_tenant_id`), never silently defaulted or inferred.
- **never** generated, inferred from `actor`, inferred from `payload`,
  inferred from `logical_operation_id`, or inferred from the proposal
  binding. `tenant_id` and operation binding (`hash_document({action,
  resource, payload_hash})`) are separate invariants; tenant scoping answers
  *whose* operation this is, binding answers *what* operation it is.
- **orthogonal** to binding. `(tenant-a, op-123)` and `(tenant-b, op-123)`
  can carry the identical binding and remain fully independent (this is the
  test matrix item A / requirement 7 case above); `(tenant-a, op-123)` with
  two different bindings across two presentations is still, exactly as
  before, a `BINDING_CONFLICT`.

## Trusted origin: `tenant_id` is identity, not a new authority mechanism

**PR #105 is durable identity scoping, not a new authority mechanism.**
`tenant_id != execution authority` — a valid `tenant_id` grants no
permission by itself; it only determines which tenant's durable-operation
namespace a decision's admission/tracking/resolution is scoped to. The
verdict (ALLOW/DENY/ESCALATE/CONSTRAIN) is still decided entirely by
existing authority/mandate/consensus machinery, unchanged by this PR.

`tenant_id` becomes a signed claim on the Ed25519-signed decision token
(`DecisionEngine.issue_token(..., tenant_id=...)`, `src/mcc_core/core.py`),
established by trusted server-side/authenticated context **before**
issuance — the same trust boundary and the same treatment Round 25 gave
`idempotency_key`. It is never accepted from a request-body/payload field a
caller controls, and once signed it cannot be altered, omitted, or forged
without invalidating the token's signature.

Where trusted tenant resolution happens, per production entrypoint:

- **`gateway/app.py` + `gateway/governance_service.py` +
  `gateway/governance_api.py`** — the gateway's existing single-credential
  trust boundary (one API key / one agent identity per instance) is
  extended with a single configurable `tenant_id` per gateway instance
  (`MCC_GATEWAY_TENANT_ID`, default `"pilot"`). This is a deliberate,
  documented pilot-scope decision (see Limitations below), not a gap.
- **`main.py`'s `GovernancePipeline`** — `evaluate(self, tenant: str, ...)`
  already carried a real, authenticated `tenant` parameter that was never
  forwarded into `issue_token`/`coordinator.enforce`; PR #105 closes that
  latent gap by threading it through.
- **`examples/governed_agent/mcc_client.py`** — `GovernedMCCClient` IS the
  trusted server-side boundary for that reference deployment (no separate
  HTTP layer in front of it); it carries its own fixed `self.tenant_id`.
- **`examples/gpt6_astra_reference/`** — `LocalAstraDemoStack.tenant_id`
  (a fixed per-stack constant) is threaded through
  `pipeline.issue_authority`/`run_positive_path` explicitly; `pipeline.
  enforce_authority` reads `tenant_id` back off the already-issued,
  already-signed token rather than accepting a second, independently
  suppliable value for a function that only ever presents an existing
  token.

## Mandatory coordinator check

`EnforcementCoordinator.enforce()` extracts and validates `tenant_id`
immediately after the existing mandatory `idempotency_key` check (Round 25)
— unconditionally, before consensus/challenge/approval consumption, durable
admission, velocity reservation, audit-before-actuation, or executor
invocation:

```python
tenant_id = token.get("tenant_id")
if not isinstance(tenant_id, str) or not tenant_id.strip():
    # BLOCKED: MISSING_TENANT_IDENTITY — zero side effects
```

A missing, empty, whitespace-only, or non-string `tenant_id` yields
`ActuationStatus.BLOCKED` with reason `MISSING_TENANT_IDENTITY` — no
durable record is created, no audit `pre_actuation`/`actuation_result` entry
is written (only `actuation_rejected`), and the executor is never invoked.
See `tests/test_coordinator_mandatory_tenant_id.py` (mirrors
`tests/test_coordinator_mandatory_logical_operation_id.py` exactly).

`gateway/governance_service.py` additionally carries a `_missing_tenant_id`
transport-layer check (mirroring `_missing_logical_operation_id`) — this is
explicitly **defense-in-depth only**; the coordinator's check above is the
sole authoritative enforcement point. `src/mcc_core/gate.py` required no
changes: `request_binding` already supports arbitrary keys, so
`"tenant_id"` rides through the Gate's existing generic binding-dict
mechanism for free wherever a caller includes it.

## Keying: InMemory and Redis

**`InMemoryIdempotencyRegistry`** re-keys its store to an exact-value Python
tuple `(tenant_id, key)` — never a concatenated/encoded string, so there is
no possible collision between e.g. tenant `"a"` / key `"b:c"` and tenant
`"a:b"` / key `"c"`.

**`RedisIdempotencyRegistry`** keys as:

```
scoped_root + hash_component(tenant_id) + ":" + key
```

`hash_component` (`src/mcc_core/redis_keys.py`, reused unchanged from PR
#104's `RedisProposalRegistry`) is a SHA-256 digest truncated to 32 hex
characters — fixed-length and collision-resistant regardless of what
characters `tenant_id` or `key` themselves contain, so a crafted `tenant_id`
can never manufacture a key that aliases a different tenant's namespace.
Every durable-state Lua script (`_COMMIT_DISPATCH_LUA`, `_MARK_EXECUTED_LUA`,
`_MARK_UNKNOWN_LUA`, `_RELEASE_LUA`, `_RESOLVE_UNKNOWN_LUA`) receives this
one scoped key as `KEYS[1]`, unchanged in shape from before PR #105 — only
what string is passed as that key changed.

**`scoped_root` is deliberately NOT simply `namespace`** — see "Keyspace
disjointness" immediately below; this was a remediated defect (Blocker 1),
not the original PR #105 design.

### Keyspace disjointness (remediation round, Blocker 1)

The original PR #105 design built the scoped key as `namespace +
hash_component(tenant_id) + ":" + key`. This is **not** structurally
disjoint from the legacy keyspace: a legacy key is `namespace + raw_key` for
an **unconstrained** `raw_key` (any string at all), so `namespace` is always
a literal prefix of the original scheme's scoped key too. An adversarial (or
merely coincidental) legacy `raw_key` equal to `hash_component(tenant_id) +
":" + key` makes the two keys byte-for-byte identical — **no hash collision
required**. The same flaw survives naively appending a version marker
(`namespace + "v2:" + ...`): appending after `namespace` never changes the
fact that `namespace` is a literal prefix of the result, so a legacy
`raw_key` can always be chosen to fill in whatever comes after it.

The fix (`_derive_disjoint_root` in `src/mcc_core/idempotency.py`): both the
tenant-scoped root and the migration-claim root (below) are built by
**replacing** `namespace`'s own guaranteed trailing `':'` with a
distinguishing marker (`"~scope-v2"` / `"~migrate-claim"`), rather than
appending after it:

```
namespace     = "mcc:idem:"
scoped_root   = "mcc:idem" + "~scope-v2"       + ":"   =  "mcc:idem~scope-v2:"
claim_root    = "mcc:idem" + "~migrate-claim"  + ":"   =  "mcc:idem~migrate-claim:"
```

This makes the two roots diverge from `namespace` at the exact character
position of `namespace`'s own trailing colon (index `len(namespace) - 1`) —
a position that is entirely FIXED by `namespace` itself: a legacy key's
`raw_key` only ever supplies characters **after** the end of `namespace`, so
it can never reach back and change a character that already differs.
Consequently, for **every possible** `raw_key`, `tenant_id`, and `key`:

```
legacy_key(raw_key) != scoped_key(tenant_id, key)
legacy_key(raw_key) != claim_key(key)
```

— provably, not just empirically. `RedisIdempotencyRegistry.__init__`
normalizes `namespace` to always end in `':'` first, so this holds
regardless of whatever `namespace` an operator configures.
`tests/test_idempotency.py::test_a_legacy_scoped_key_alias_no_longer_exists`
reconstructs the exact former alias and proves it no longer exists, against
the Redis-backed path; `test_a_scoped_and_claim_roots_are_pairwise_disjoint_
from_legacy` proves the general pairwise-disjointness property directly.
`scripts/redis_migration_smoke.py` re-proves this against a **real** Redis
server.

## Legacy (pre-PR-105) durable state — security-critical

Before PR #105, `RedisIdempotencyRegistry` stored one record per raw `key`
(`namespace + key`, no tenant dimension). Re-keying to the scheme above
means a durable record written under the OLD format is invisible to a
lookup under the NEW format. **Silently treating "no record at the new key"
as "safe to admit" would let an operation that already reached
`DISPATCH_OWNED`/`UNKNOWN`/`EXECUTED` under the old scheme be dispatched a
SECOND time** — exactly the duplicate-actuation class of defect
`docs/DURABLE_OPERATION_SAFETY.md` exists to prevent, reopened by a key
format change instead of a coordinator bug.

This is closed structurally:

- `RedisIdempotencyRegistry.reserve` checks the legacy key
  (`_legacy_key(key)` = `namespace + key`) **first**, inside the SAME atomic
  Lua script, before the scoped key is touched at all. If a legacy record
  exists, `reserve` returns `ReserveStatus.LEGACY_UNMIGRATED` — a distinct,
  explicit fail-closed signal, never a fresh `RESERVED`.
- `RedisIdempotencyRegistry.get_state`, when the scoped key is absent, also
  checks the legacy key; if found, it raises `IdempotencyBackendUnavailable`
  rather than returning `None` ("not found" must never be conflated with
  "an operation may already exist under the old scheme").
- There is **no automatic ownership claim** of a legacy record by any
  tenant — a raw key alone proves nothing about which tenant legitimately
  owns it (no binding-based "auto-detection" either; binding is not
  evidence of tenant identity).
- Migration is an explicit, operator-invoked function, **never** called
  from the hot path:

  ```python
  result = await migrate_legacy_record(registry, tenant_id="<verified-owning-tenant>",
                                        key="<logical_operation_id>", delete_legacy=True)
  # result.status: MIGRATED | ALREADY_MIGRATED | ABSENT | CONFLICT | INVALID_INPUT | ERROR
  ```

  The operator must independently verify, out-of-band (original request
  logs, the audit chain, a pre-migration inventory), which tenant actually
  owns the operation before calling this.

- **No duplicate-actuation window**: immediately after migration, a
  `reserve` for the same `(tenant_id, key)` correctly reports the migrated
  terminal state (e.g. `DUPLICATE_EXECUTED`) rather than a fresh
  `RESERVED` — proven directly by
  `tests/test_idempotency.py::test_legacy_record_never_silently_reopens_an_already_executed_operation`.

`InMemoryIdempotencyRegistry` has no legacy-record concept: nothing survives
a process restart there, so there is no pre-existing unscoped state a
re-keying could ever fail to see (this is exclusively a durable-backend
migration concern).

### Input validation (remediation round, Blocker 2)

`migrate_legacy_record` validates `tenant_id` (must be a non-empty,
non-whitespace string) and `key` (must be a non-empty string) **before any
Redis read, write, or delete**. An invalid value returns
`MigrationStatus.INVALID_INPUT` immediately — zero Redis calls are made, and
the legacy record (if any) is left byte-for-byte untouched. See
`tests/test_idempotency.py::test_b_blank_or_invalid_tenant_migration_fails_closed`
/ `test_b_invalid_key_migration_fails_closed` (parametrized over
`None`/`""`/whitespace/non-string values) and
`scripts/redis_migration_smoke.py` (real Redis).

### Atomic migration (remediation round, Blocker 3)

The original PR #105 design performed migration as four separate Redis
calls (`GET legacy`, `GET scoped`, `SET scoped`, `DELETE legacy`) — not an
atomic ownership transfer. Two concurrent migration attempts for **different
tenants** could both observe the legacy record before either deleted it,
and both copy it into two different tenant scopes: **one legacy durable
record** could produce **two tenant-scoped owners**.

The fix: migration is now **one atomic Redis Lua script**
(`_MIGRATE_LEGACY_LUA`), gated by a per-legacy-key **claim marker**
(`registry._claim_key(key)`, itself structurally disjoint from both the
legacy and tenant-scoped keyspaces — see "Keyspace disjointness" above).
The claim check, the legacy/target reads, the copy, the claim write, and
the optional legacy delete all happen inside the single script execution,
which Redis always runs to completion, single-threaded, before serving any
other command — there is no read-then-write window a second concurrent
caller can observe.

Algorithm (`KEYS[1]`=legacy, `KEYS[2]`=tenant-scoped target,
`KEYS[3]`=claim; `ARGV[1]`=tenant_id, `ARGV[2]`=delete_legacy flag):

1. **Claim already held** — if `KEYS[3]` holds a DIFFERENT tenant_id ->
   `CONFLICT` (refused before touching legacy/target at all). If it holds
   the SAME tenant_id -> idempotent `ALREADY_MIGRATED` (re-invoking an
   already-completed migration is always safe).
2. **Legacy absent** — if the target scoped key already exists ->
   `ALREADY_MIGRATED`; otherwise `ABSENT`. Never creates anything.
3. **Legacy exists, target absent** — copy the encoded record into the
   target, write the claim, and (if `delete_legacy`) delete the legacy key
   — all in this same atomic step -> `MIGRATED`.
4. **Legacy exists, target exists with the IDENTICAL encoded record** —
   treated as safe idempotent equivalence: claim it and optionally drop the
   now-redundant legacy copy -> `ALREADY_MIGRATED`. Never merges.
5. **Legacy exists, target exists with a DIFFERENT record** — refused,
   nothing is overwritten, merged, or deleted -> `CONFLICT`.
6. **Backend failure** at any point -> `MigrationStatus.ERROR`, fail-closed.
   Because the whole operation is one atomic script, there is no
   client-observable state where the legacy record disappeared but the
   scoped target was not durably written (or vice versa).

**Concurrent two-tenant race**: whichever invocation Redis serializes first
wins the claim (step 3, `MIGRATED`); the second invocation's script then
sees the claim already held by a different tenant and is refused at step 1
(`CONFLICT`) — never a duplicate copy, and never both `MIGRATED`. This holds
even for concurrent attempts by the SAME tenant (idempotent: one gets
`MIGRATED`, the other `ALREADY_MIGRATED`, never an error or a divergent
outcome). Proven directly in `tests/test_idempotency.py` (tests `test_c_*`,
`test_d_*`, `test_e_*`) and, for genuine concurrency against a real Redis
server, in `scripts/redis_migration_smoke.py`.

## `MCCProposalService` status: tenant-scoped lookup, binding demoted

`get_operation_status` now queries the durable registry directly with the
tenant-scoped call, `self._durable.get_state(key, tenant_id=tenant_id)` —
never a globally-keyed lookup. Ownership is established structurally by the
registry itself returning (or not returning) a record for this exact
`(tenant_id, key)` pair, not by comparing the returned record's binding
against the tenant's own proposal binding.

The proposal-binding-vs-durable-binding comparison is retained, but only as
**defense-in-depth / internal-consistency checking**: since the registry is
now tenant-scoped, a binding mismatch within an already-tenant-proven record
can only mean internal corruption (this tenant's own proposal and its own
durable dispatch record disagree about what operation this id names) — it
is fail-closed (`OperationStatusValue.UNAVAILABLE`), and it is **never**
reinterpreted as "this must belong to another tenant." See
`src/mcc_proposal/service.py` and
`tests/test_proposal_service_tenant_status_isolation.py` (updated for PR
#105; the observable cross-tenant guarantees are unchanged from PR #104's
remediation, but now hold because of tenant-scoped registry keying rather
than binding comparison).

## What did NOT change

- **One execution state machine.** No second `EnforcementCoordinator`, Gate,
  authority system, or proposal-specific execution registry was introduced.
  `RESERVED -> DISPATCH_OWNED -> EXECUTED|UNKNOWN -> (resolve_unknown) ->
  EXECUTED` is the same state machine, same fencing, same TTL rules — only
  its addressing scheme changed.
- **Binding invariant.** `hash_document({action, resource, payload_hash})`
  is unchanged and remains the mechanism that makes a same-tenant,
  different-payload resubmission a `BINDING_CONFLICT`.
- **Same-tenant semantics.** Every pre-PR-105 duplicate/conflict/
  UNKNOWN/EXECUTED/DISPATCH_OWNED/RESERVED guarantee for a single tenant is
  unchanged — re-asserted directly alongside the new cross-tenant tests in
  `tests/test_idempotency.py`.
- **Reconciliation.** `examples/gpt6_astra_reference/reconciliation.py`
  derives `tenant_id` from the same real, gate-verified signed token every
  other field (`idempotency_key`/`action`/`resource_id`/`payload_hash`)
  already came from — never a second, independently-suppliable value — and
  scopes both its `get_state` lookup and its terminal `resolve_unknown` call
  to it.

## Limitations / scope

- The gateway's trusted-tenant-resolution boundary
  (`MCC_GATEWAY_TENANT_ID`, one tenant per gateway instance) mirrors the
  gateway's existing single-credential-per-instance pilot design; it is not
  full multi-tenant HTTP authentication (per-API-key tenant resolution).
  Building that out is future work, tracked separately from this PR's scope
  (durable identity scoping).
- Phase 2 (a Proposal → Signed Authority → Execution bridge, tracked as a
  future PR) is explicitly out of scope here; `MCCProposalService` remains
  non-actuating.
