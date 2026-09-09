# Pilot Execution API

PR #111. A production-like, multi-tenant, authenticated HTTP transport
layer over the already-existing, unmodified Phase 2 governed execution
bridge (`gateway.proposal_execution_service.ProposalExecutionService.authorize_and_execute`,
PR #106). It introduces **no new authority mechanism, Gate,
EnforcementCoordinator, execution registry, or actuator path** — every
authority/execution decision is made by exactly the same code Phase 2
already proved and shipped.

> **API authentication establishes identity. It does not establish
> authority.**
>
> **The execution endpoint cannot mint permission. It can only request
> execution through the existing MCC authority boundary.**

## 1. HTTP contract

```
POST /v1/operations/{logical_operation_id}/execute
POST /v1/operations/{logical_operation_id}/reconcile     (optional, see §9)
```

`execute` takes **no request body**. There is no field for a caller to
supply `action`, `resource`, `payload`, `tenant_id`, `actor`, a signed
authority, a decision/verdict, an idempotency key, or any other
authorization field — the handler's only inputs are the path's
`logical_operation_id` and the authenticated, server-resolved
`tenant_id`, exactly mirroring `ProposalExecutionService.authorize_and_execute`'s
own signature. Every byte of what gets executed comes exclusively from
the tenant-owned stored proposal (`POST /v1/proposals`, Phase 1); nothing
in the execute request can reconstruct, enrich, mutate, or replace it.

Response body (`execute`):

```json
{
  "status": "EXECUTED",
  "reason": "executed",
  "decision": "ALLOW",
  "audit_ref": "8cec32d2...",
  "applied_changes": []
}
```

`status` is one of `ProposalExecutionService`'s existing, unmodified
vocabulary: `EXECUTED`, `BLOCKED`, `EXECUTION_FAILED`, `DENIED`,
`ESCALATED`, `NOT_FOUND`, `UNAVAILABLE`, `REJECTED`, `RESOURCE_MISMATCH`.
The response deliberately excludes `ProposalExecOutcome.execution` (the
raw actuator return value) — an arbitrary actuator's return shape is not
a stable wire contract and is not needed for a caller to know what
happened. No token material, signing key, or backend connection detail is
ever present in `ProposalExecOutcome`, so none can leak through this
mapping.

## 2. Authentication model

Reuses, unchanged, the SAME `X-Api-Key -> tenant_id` credential-mapping
pattern Phase 1's `gateway/proposal_api.py` already established
(`get_tenant_dependency`, exported and imported by this router, not
duplicated): an authenticated API key resolves, server-side only, to
exactly one tenant identity. Configuration is the SAME
`MCC_PROPOSAL_TENANTS` JSON object (`{"api-key": "tenant-id", ...}`), or a
deployment-specific equivalent passed directly to
`mount_proposal_execution_routes(..., tenants=...)`.

- Unknown/missing credential -> HTTP 401.
- Malformed authentication configuration -> fail closed at startup
  (`tenants_from_env` already raises `ProposalTenantConfigError`).
- No default tenant fallback, no "pilot" fallback for this surface.
- Tenant identity is **never** accepted from the request body, a query
  parameter, a URL segment, or any header other than the one the
  authentication dependency itself consumes (`X-Api-Key`) — proven
  adversarially in `tests/test_proposal_execution_api.py` (tests D, P,
  non-vacuity 1): every plausible smuggling vector (`?tenant_id=`,
  `X-Tenant-Id` header, a `tenant_id` body field) is silently ignored,
  because nothing in the handler even reads it.

## 3. Trusted tenant resolution vs. authority

Authentication (§2) answers *"who is this caller"*. It is a completely
separate layer from **authority** — *"what may that identity do"* —
which is answered exclusively by the existing `mcc_core.authority.AuthorityModel`,
constructed by `gateway.proposal_execution_stack.build_proposal_execution_stack`
from a declarative `tenant_id -> grant` config, the SAME shape every
other Phase 2 reference call site in this repository already uses
(`examples/phase2_live_sandbox/stack.py`,
`tests/test_proposal_execution_bridge.py`). An authenticated tenant with
no authority grant for the configured action is `DENIED` (or `ESCALATED`,
depending on policy) — authentication succeeding never implies execution
is permitted.

## 4. Exact call path

```
authenticated API credential
  -> get_tenant_dependency(tenants)              (X-Api-Key -> tenant_id;
                                                    gateway.proposal_api,
                                                    reused unchanged)
  -> ProposalExecutionService.authorize_and_execute(tenant_id=, logical_operation_id=)
  -> ProposalRegistry.get(tenant_id=, logical_operation_id=)   (ownership +
     the proposal's OWN stored action/resource/payload)
  -> AuthorityModel.evaluate(identity=tenant_id, ...)          (trusted verdict)
  -> DecisionEngine.issue_token                                (signed authority)
  -> EnforcementCoordinator.enforce                             (ExecutionGate +
     tenant-scoped IdempotencyRegistry + audit-before-actuation)
  -> ResourceBoundUpstream.execute(resource=, action=, payload=) (Phase 2's
     existing resource-binding contract)
  -> the injected, caller-configured actuator
```

`gateway/proposal_execution_api.py` (the router) contains **none** of the
middle layers — it holds a reference to nothing but an already-built
`ProposalExecutionService`. `gateway/proposal_execution_stack.py` (the
builder) is the ONLY new code that constructs the authority/execution
machinery, and it does so by composing the exact same public primitives
Phase 2 already ships (`AuthorityModel`, `DecisionEngine`, `ExecutionGate`,
`EnforcementCoordinator`) — no new decision logic. This separation is
enforced by a static AST guard
(`tests/test_proposal_execution_api_architecture_guards.py`) that forbids
the router module from importing the Gate, the coordinator, the authority
model, the decision engine, a signing key, or the stack builder itself.

## 5. Tenant isolation

`(tenant_id, logical_operation_id)` remains the durable execution
identity — unchanged from Phase 2. Two tenants may use the identical raw
`logical_operation_id` and execute completely independently, with no
collision, no shared fencing state, and no cross-tenant disclosure: a
non-owner attempting to execute another tenant's operation receives a
tenant-safe `NOT_FOUND` (HTTP 404) and learns nothing about whether that
identity exists for a different tenant, its execution state, or any
other detail — the identical response an unqualified, never-submitted
identity produces. Proven in tests D, E, and non-vacuity 1.

## 6. Replay and concurrency

Both go through the SAME real, unmodified durable execution machinery
`ProposalExecutionService` already uses — never a transport-layer mutex
or HTTP-specific deduplication. A second `execute` call for an identity
already `EXECUTED` never re-dispatches (test F); concurrent `execute`
calls for the same identity resolve to exactly one `EXECUTED` and at most
one actuator invocation (test G, and the real-Redis-backed equivalents),
via the coordinator's own admission semantics.

## 7. UNKNOWN / ambiguous-failure behavior

When the actuator's dispatch raises after being invoked (the outcome is
genuinely unknown — the request may or may not have reached the external
system), `authorize_and_execute` reports `EXECUTION_FAILED` and the
durable idempotency record is left in its existing UNKNOWN-eligible
state. This router adds **no transport-level auto-retry**: a second HTTP
call is just a second `authorize_and_execute` invocation, which the
existing coordinator/idempotency semantics handle exactly as they would
any other caller — it does not silently convert an ambiguous failure into
a fresh executable reservation (test M).

## 8. HTTP result mapping

| `ProposalExecStatus` | HTTP code | Rationale |
|---|---|---|
| `EXECUTED` | 200 | Governed success |
| `BLOCKED` | 200 | Safely refused before/without dispatch; not a transport failure |
| `EXECUTION_FAILED` | 200 | Dispatched; durably uncertain — the caller must read `status`, not infer from the transport layer |
| `DENIED` | 200 | A policy denial is not an HTTP infrastructure failure |
| `ESCALATED` | 200 | Ditto |
| `RESOURCE_MISMATCH` | 200 | Safely refused before any external call |
| `NOT_FOUND` | 404 | Tenant-safe: unqualified or genuinely absent, indistinguishable |
| `UNAVAILABLE` | 503 | Genuine backend outage |
| `REJECTED` | 422 | Malformed input (e.g. a whitespace-only `logical_operation_id`) |

Authentication failure (invalid/missing API key) is always 401, decided
before any of the above is ever reached. The reconcile endpoint (§9) maps
its own `ReconcileOutcome` vocabulary the same way (`NOT_FOUND` -> 404,
`UNAVAILABLE` -> 503, `REJECTED` -> 422, everything else -> 200).

## 9. Reconciliation (optional, deferred by default)

`POST /v1/operations/{logical_operation_id}/reconcile` is mounted **only**
when the deployment supplies a trusted `verify_external_evidence`
(`EvidenceVerifier` — the exact contract `reconcile_proposal_operation`
already defines) to `mount_proposal_execution_routes`. There is no
deployment-agnostic default evidence verifier in this repository:
evidence lookup is inherently actuator-specific (see
`examples/phase2_live_sandbox/evidence.py`'s GitHub-specific
implementation, which looks for a marker in a GitHub issue). A deployment
with no configured actuator/verifier therefore gets **no reconcile route
at all**, rather than a route that would have nothing meaningful to check
evidence against.

When mounted, the route is a thin authenticated wrapper: the caller
identifies only the operation (path `logical_operation_id`); tenant
identity comes from the same authenticated credential as `execute`; there
is no request body, so a caller cannot supply raw `"executed": true` (or
any other) evidence — evidence always comes from the trusted verifier the
deployment configured, exactly as `reconcile_proposal_operation` already
requires. Reconciliation never invokes the actuator.

## 10. Configuration

| Variable / parameter | Meaning |
|---|---|
| `tenants` (constructor arg to `mount_proposal_execution_routes`) | `{api_key: tenant_id}` — reuse `gateway.proposal_api.tenants_from_env()` (`MCC_PROPOSAL_TENANTS`) for the SAME map Phase 1 uses, or a dedicated map |
| `tenants` (constructor arg to `build_proposal_execution_stack`) | `{tenant_id: constraints}` — the AUTHORITY grant map, deliberately independent of the credential map above |
| `action` | The single action name this deployment's execute route authorizes |
| `upstream` | A `ResourceBoundUpstream` — the controlled actuator; **required**, no default |
| `proposals` / `idempotency` / `nonces` | Already-constructed, durable registries — **required**, no default, and MUST be the exact same instances Phase 1's `MCCProposalService` uses (see §11) |

Secrets (API keys) are never logged — the router only ever compares a
supplied key against the configured map and returns the resolved
`tenant_id`, never the key itself, in any response or audit entry. An
empty/unset `tenants` mapping means no authenticated execution clients
exist for this deployment (fail closed — every request 401s). There is no
insecure default actuator on this route: `build_proposal_execution_stack`
requires an explicit `upstream`; nothing about this module will silently
construct one.

## 11. Security boundaries and the shared-instance requirement

`ProposalExecutionService` and `MCCProposalService` (Phase 1's
proposal/status boundary) **must** share the exact same `proposals` and
`idempotency` registry instances — there is exactly one durable execution
registry and one proposal registry per deployment. `build_proposal_execution_stack`
deliberately takes them as required, already-constructed arguments rather
than selecting a backend from the environment itself: doing so a second
time (e.g. calling `proposal_registry_from_env()` again) would, under an
in-memory backend, silently construct a SECOND, divergent registry
invisible to the Phase 1 routes — a proposal submitted through
`POST /v1/proposals` would never be found by `POST /v1/operations/{id}/execute`.
Making the shared instance an explicit constructor argument makes that
correctness requirement impossible to get wrong by omission, and is
exactly why this repository is not, in this PR, auto-wiring the Pilot
Execution API into `gateway/app.py`'s default startup (see §12).

## 12. Deferred / not wired into the default gateway process

This PR does **not** mount the Pilot Execution API onto the live,
default-running `gateway/app.py` process. Two reasons, both deliberate:

1. **No production actuator decision has been made for this repository.**
   `README.md`'s own "Production Pilot" section already documents "a real
   external actuator... [none] of this exists yet" as an open item; the
   only actuator this repository has actually exercised end-to-end
   against a real external system is the Phase 2 live GitHub sandbox
   proof (PR #108/#110), which is deliberately sandbox-scoped. Wiring
   ANY concrete actuator into the default gateway process's startup path
   would be inventing new production behavior beyond this PR's scope, and
   risks exactly the "insecure developer default" this task explicitly
   forbids.
2. The shared-instance requirement (§11) means wiring this into
   `gateway/app.py` correctly requires reusing `proposal_service`'s exact
   registry instances and a real, operator-chosen actuator — a decision
   for a future, explicitly-scoped PR, not an implicit side effect of this
   one.

Instead, `examples/pilot_execution_api/app.py` demonstrates the full,
correctly-wired composition (Phase 1 + this PR's routes, sharing ONE
`proposals`/`idempotency` pair, with a caller-supplied actuator) as a
runnable reference — the same pattern this repository already uses for
`examples/phase2_live_sandbox/`.

## 13. Limitations

- No HTTP-level rate limiting/velocity beyond whatever the injected
  `AuthorityModel`'s constraints already express — this router adds none
  of its own.
- The response body's `reason` string may echo internal detail (e.g. a
  backend exception's `repr()`) for `UNAVAILABLE`/`EXECUTION_FAILED` —
  useful for pilot debugging, but a hardened production deployment should
  consider redacting it before it is a public contract.
- Reconciliation (§9) is off by default and requires an
  actuator-specific `EvidenceVerifier` a deployment must supply itself.
- Not wired into the default `gateway/app.py` process (§12) — a
  deployment must explicitly compose it (see the example).
