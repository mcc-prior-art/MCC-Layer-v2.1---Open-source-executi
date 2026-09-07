# MCC Universal Proposal Service — Phase 1

> **PROPOSAL != PERMISSION.**
> **TRANSPORT != AUTHORITY.**
>
> INTELLIGENCE CAN PROPOSE.
> AUTHORITY MUST VERIFY.
> EXECUTION MUST ENFORCE.
>
> INTELLIGENCE != AUTHORITY != EXECUTION.
>
> NO VERIFIED AUTHORITY. NO EXECUTION.

## 0. What this is, and what it is not

This is a **transport-neutral proposal/status boundary**: one service that
lets any agent framework, SDK, protocol, or enterprise system register a
governed operation's identity and later ask what happened to it, **without
executing anything**.

```
ANY INTELLIGENCE / ANY AGENT / ANY FRAMEWORK / ANY TRANSPORT

    LangGraph, CrewAI, AutoGen, VoltAgent, Generic HTTP,
    MCP, the native SDK, future gRPC/event-bus/A2A clients

                    |
                    v
        TRANSPORT / FRAMEWORK ADAPTERS
                    |
                    v
          MCCProposalService                <-- Phase 1 stops here
        (transport-neutral contract)
                    |
                    v
     MCC INDEPENDENT AUTHORITY BOUNDARY       <-- future phase
                    |
                    v
                SIGNED AUTHORITY
                    |
                    v
           EnforcementCoordinator
                    |
                    v
             SERVER-OWNED ACTUATOR
```

**Phase 1 is strictly non-actuating.** No code path reachable from a
proposal submission or a status lookup calls `EnforcementCoordinator.enforce()`,
`GovernanceService.execute_with_mandate()`/`execute_with_approval()`,
`service.upstream(...)`, any actuator, or any reconciliation mutator
(`resolve_unknown`/`mark_executed`/`commit_dispatch`). This is enforced
structurally (the service module imports none of those symbols) and proven
by static architecture guards
(`tests/test_proposal_service_architecture_guards.py`) plus behavioral
zero-actuator tests.

## 1. The canonical contract (`mcc_proposal.models`)

### `ProposalRequestV1`

```json
{
  "logical_operation_id": "string, required, non-empty, non-whitespace",
  "actor": "string, required",
  "action": "string, required",
  "resource": "string | null",
  "payload": { "...": "arbitrary JSON object" }
}
```

This is a **strict allow-list** (`ALLOWED_REQUEST_FIELDS`). Any other
top-level field is rejected outright — never silently dropped, never
silently honored. A closed list of known authority-bearing field names
(`decision_token`, `mandate`, `signing_key`, `force`, `execute`, …) is
called out explicitly so a rejection can say *why* it was refused, but the
enforcement mechanism is the allow-list itself: **an unrecognized field of
any name is rejected**, not only the ones on that list.

### `ProposalReceiptV1`

```json
{
  "contract_version": "v1",
  "accepted": true,
  "logical_operation_id": "...",
  "status": "PROPOSED",
  "proposal_binding": "sha256:..."
}
```

`status` is one of `PROPOSED` (accepted, possibly idempotent),
`BINDING_CONFLICT`, `REJECTED` (structurally invalid, an authority-bearing
field, or a profile-canonicalization failure), or `UNAVAILABLE` (backend
uncertainty — fail-closed, never silently treated as rejected-forever or
retry-safe).

### `OperationStatusV1`

```json
{
  "contract_version": "v1",
  "logical_operation_id": "...",
  "status": "PROPOSED | RESERVED | DISPATCH_OWNED | UNKNOWN | EXECUTED | NOT_FOUND | UNAVAILABLE"
}
```

Every adapter exposes exactly these seven names. No adapter renames or
reinterprets them.

## 2. `logical_operation_id` — unavoidable

Mandatory, caller-supplied, checked immediately: must be a non-empty,
non-whitespace **string**. It is never generated, never inferred from
payload, never substituted from `request_id`/`trace_id`/`correlation_id`/
`challenge_id`/`approval_id`/`nonce`/`session_id`/`tool_call_id`/
`message_id`/an MCP request id/a framework run or task id — any of those
supplied *instead of* `logical_operation_id` is simply an unrecognized
field and the whole proposal is rejected. This is the exact same identity
discipline Round 25-27 established for `EnforcementCoordinator.enforce()`'s
mandatory `idempotency_key`: **if this operation is later proposed for real
execution, this is the identity the coordinator will require.**

## 3. Exact proposal binding (`mcc_proposal.binding`)

```python
canonical_payload = ProfileRegistry.for_action(action).canonical_payload(payload)
payload_hash      = hash_payload(canonical_payload)          # mcc_core.signing
proposal_binding  = hash_document({"action": action,
                                    "resource": resource,
                                    "payload_hash": payload_hash})
```

This reuses the **exact same** canonicalization and hashing primitives
protected execution uses — no MCP-specific, HTTP-specific,
framework-specific, or TypeScript-only alternate serialization exists
anywhere. The same semantic operation, submitted through any adapter,
produces the identical `proposal_binding` (proven by
`tests/proposal_conformance/test_cross_adapter_parity.py` across six
adapters, including difficult JSON: reordered keys, Unicode, nested
objects/arrays, booleans, null, numeric forms, empty structures).

* Same `logical_operation_id` + identical binding → idempotent duplicate
  (`PROPOSED`, same binding echoed back).
* Same `logical_operation_id` + different action/resource/payload → `BINDING_CONFLICT`.
  The **first** accepted binding is never overwritten.

## 4. Proposal registry vs. execution idempotency registry

`mcc_proposal.registry` (`InMemoryProposalRegistry` / `RedisProposalRegistry`)
is **deliberately distinct** from `mcc_core.idempotency`. `RESERVED` there
has a precise security meaning: a durably admitted, pre-dispatch logical
operation on the real execution path. A proposal has not been admitted for
anything. `mcc_proposal.registry` never imports or calls
`reserve`/`commit_dispatch`/`mark_executed`/`mark_unknown`/`resolve_unknown`
— see the architecture guards. Registering a proposal produces exactly one
state: `PROPOSED`.

The Redis backend's atomicity is one Lua script (first-writer-wins,
matching `mcc_core.idempotency`'s own convention), keyed under the
project's canonical `redis_keys` namespace
(`mcc:v1:{env}:proposal:{hash(tenant)}:{safe(logical_operation_id)}`).
`MCC_PROPOSAL_BACKEND=memory|redis` mirrors
`MCC_IDEMPOTENCY_BACKEND`: `redis` requires `MCC_REDIS_URL` (no silent
fallback to memory), and `MCC_DEPLOYMENT_MODE=enforcement` refuses `memory`
outright.

## 5. Tenant / security-domain isolation

Every proposal and status lookup is scoped by `(tenant_id,
logical_operation_id)`. `tenant_id` **must** come from the transport's
authenticated caller identity (an API key resolved server-side via
`MCC_PROPOSAL_TENANTS`, an HTTP header, a per-session credential) — never
from `actor` or any other payload/request field. Two tenants can use the
identical `logical_operation_id` with different bindings with zero
collision, and neither can read, infer the existence of, or conflict with
the other's operation (`tests/test_mcc_proposal_service.py::test_ak_*`,
`test_al_*`, `tests/test_proposal_service_tenant_status_isolation.py`;
cross-adapter parity tests reuse one shared tenant precisely to prove the
*opposite* — identity across adapters *within* one tenant).

**Cross-tenant status disclosure (closed).** The *durable execution*
registry (`mcc_core.idempotency`) is architecture-wide global-keyed — it has
no tenant dimension, because `EnforcementCoordinator` itself has none (left
unmodified, out of scope). `get_operation_status` therefore never consults
it on `tenant_id` alone: see Section 6 for the ownership-gated algorithm
that makes this safe without touching the coordinator, adding a second
execution registry, or weakening `UNKNOWN` semantics.

## 6. Status composition (`MCCProposalService.get_operation_status`)

Ownership-gated precedence, in order:

1. Tenant-scoped proposal **ownership** lookup (`ProposalRegistry.get(tenant_id, ...)`,
   already tenant-scoped) cannot definitively answer → `UNAVAILABLE` (cannot
   prove ownership; never disclose).
2. No tenant-scoped proposal record for this identity → `NOT_FOUND`,
   **without ever consulting the durable execution registry** — a tenant
   that never proposed this identity can neither observe another tenant's
   durable state nor infer that it exists, regardless of whether the
   durable backend is up or down.
3. Ownership established; durable execution backend cannot definitively
   answer → `UNAVAILABLE`.
4. Ownership established; a durable execution record exists **and its
   `binding` matches this tenant's own registered binding** → the record's
   exact state, verbatim (`RESERVED`/`DISPATCH_OWNED`/`UNKNOWN`/`EXECUTED`).
5. Ownership established; a durable execution record exists but its
   `binding` does **not** match this tenant's own registered binding → that
   record belongs to a different registrant that reused the same raw id
   with a different action/resource/payload (Section 3/5 explicitly permit
   this); never disclosed, falls through to 6.
6. Otherwise → `PROPOSED` (this tenant's own registered binding).

The binding comparison in step 4/5 is what makes ownership alone
insufficient to prove *which* tenant's operation a shared, globally-keyed
durable record belongs to when two tenants legitimately reused the same
`logical_operation_id`: `mcc_proposal.binding.compute_proposal_binding` and
`EnforcementCoordinator`'s own `binding_ref` are the **identical**
`hash_document({action, resource, payload_hash})` formula, so a match is
proof the durable record is for the exact operation this tenant proposed,
and a mismatch is proof it is not.

`UNKNOWN` is never mapped to `NOT_FOUND` or `PROPOSED`; backend
`UNAVAILABLE` is never mapped to `NOT_FOUND` **for an operation this tenant
owns** (for an operation it does not own, backend uncertainty is `NOT_FOUND`
like everything else about that identity — never `UNAVAILABLE`, which would
itself disclose that *something* is tracked under that id). Status lookup
performs **zero state writes** and calls **zero actuators** — proven by
spy-based tests (`_ExplodingDurable`, a stub that raises `AssertionError` on
any method other than `get_state`).

The Gateway wires `MCCProposalService`'s `durable_execution_state` to
`governance.coordinator.idempotency` — the literal registry instance the
real `EnforcementCoordinator` uses — so status is never a second,
independently-constructed view that could drift from the truth.

## 7. HTTP transport (`gateway/proposal_api.py`)

```
POST /v1/proposals                          -> ProposalReceiptV1
GET  /v1/operations/{logical_operation_id}  -> OperationStatusV1
```

Additive only — `/evaluate` and its semantics are completely untouched.
The router performs authentication, deserialization, transport-level shape
validation (a strict Pydantic model mirroring `EvaluateRequest`'s
`extra="forbid"` convention), and serialization — **no decision logic**.
Authentication is `x-api-key` resolved against `MCC_PROPOSAL_TENANTS` (a
JSON `{api_key: tenant_id}` object); unset/empty means **no tenants
configured**, so every request is rejected (fail-closed default — no
anonymous/default writer). A `Content-Length` bound (`MAX_REQUEST_BODY_BYTES`)
returns `413` for a pathological body (checked after FastAPI/Pydantic has
already parsed the JSON — a true pre-parse bound would need a custom ASGI
middleware, more than this transport needs at these size bounds).

## 8. MCP adapter (`integrations/mcp/`)

Exposes exactly two tools, both pure translation:

* `mcc_submit_proposal`
* `mcc_get_operation_status`

**No `mcp` PyPI package is used.** It is not installed in this environment,
and `CLAUDE.md`'s project rules forbid adding a dependency without explicit
approval. `integrations/mcp/protocol.py` implements the small, stable
subset of the MCP wire shape Phase 1 needs (`initialize`, `tools/list`,
`tools/call`) directly on JSON-RPC 2.0 — a documented, explicit decision,
not an oversight. Adopting the official SDK later only touches
`protocol.py`/`server.py`; it changes no binding/authority/status
semantics, all of which live in `mcc_proposal`.

Two interchangeable backends (`integrations/mcp/backend.py`, re-exporting
`mcc_proposal.transport`):

* `HttpProposalBackend` — the realistic deployment shape: forwards the
  caller's credential to a real Gateway's `/v1/proposals` /
  `/v1/operations/{id}` over a genuine HTTP socket (stdlib `urllib`, no new
  dependency). Proven with a real bound TCP server, not just an in-process
  ASGI call (`tests/test_mcp_proposal_adapter.py::test_http_proposal_backend_real_socket_round_trip`).
* `InProcessProposalBackend` — local development / the conformance suite.

`build_mcp_http_app` (`integrations/mcp/http_app.py`) is the "Remote
HTTP-capable MCP transport" Section 12 requires — a standalone FastAPI app,
**not mounted into `gateway/app.py`** and **not started by anything in this
phase**. `main.py`'s `run_stdio` entrypoint is the optional local-stdio
development path. MCC remains fully usable with `integrations/mcp` never
imported.

This satisfies the Forward Architecture Rule already written into
`CLAUDE.md` for a future MCP adapter: MCP is an ingress adapter only, never
an execution authority, never its own executor, never a direct upstream
caller — every path reaches the platform through the governed contract
(here, `MCCProposalService`; in a future phase, the same discipline extends
to the Gateway's execution endpoints).

## 9. Five-ecosystem facades (`src/mcc_proposal/adapters/`)

`generic_http.py`, `langgraph.py`, `crewai.py`, `autogen.py` each expose the
identical `submit_proposal`/`get_operation_status` signature
(`(backend, credential, *, logical_operation_id, actor, action, resource, payload)`)
and reduce entirely to `mcc_proposal.adapters._common` — translation only,
zero binding/authority/policy/status logic of their own. Each also offers
an **optional** native tool-builder (`build_langgraph_tools`,
`build_crewai_tools`, `build_autogen_tools`) that lazily imports the
optional framework package and raises a clean `ImportError` if it is not
installed — none of LangGraph, CrewAI, or AutoGen is installed in this
environment, so the native builders are verified only for clean-failure
behavior here; the framework-neutral action functions are fully exercised
by the conformance suite regardless.

VoltAgent (TypeScript) gets the equivalent `submitProposal`/
`getOperationStatus` methods directly on the existing
`integrations/voltagent/src/mcc-client.ts` `MccClient`, verified by its own
vitest suite (`integrations/voltagent/tests/mcc-client-unit.test.ts`). A
Python-side drift guard
(`tests/proposal_conformance/test_voltagent_wire_contract_matches_python.py`)
pins the TS suite's asserted wire-field list against
`mcc_proposal.models.ALLOWED_REQUEST_FIELDS`, so a change to one without
the other is caught without needing to run Node from the Python suite.

## 10. Native SDK

`sdk/python/src/mcc_client.MCCClient` (the supported, independently
installable Python client) gained `submit_proposal(...)` /
`get_operation_status(...)`, pure translation onto the same two HTTP
endpoints, reusing the existing `Transport`. No second binding
implementation, no local proposal registry, no client-side authoritative
decision — the server remains authoritative for binding, exactly as for
every other MCC-Core client operation.

(The unrelated, pre-existing `sdk/mcc-sdk` package — a separate `mcc_sdk`
distribution over `/evaluate` only — was left untouched; it is out of scope
for this phase and not referenced by the existing five-ecosystem
interoperability proof or by `CLAUDE.md`'s repository file map.)

## 11. Adapter Conformance Suite (`tests/proposal_conformance/`)

One shared `MCCProposalService` + one shared tenant, wrapped behind six
adapters (Generic HTTP, MCP, LangGraph, CrewAI, AutoGen, the native Python
SDK) via one protocol (`submit(request) -> dict`, `status(id) -> dict`).
Cross-adapter tests submit through one adapter and read through another,
asserting byte-identical `proposal_binding`/`status` — and that a
conflicting resubmission through a *different* adapter is rejected
identically regardless of which pair of adapters is used (all 30 ordered
pairs of the six adapters are exercised).

## 12. Authority boundary

The public schema cannot carry a decision token, a mandate, a signing key,
a policy override, a nonce override, a dispatch/generation fence, or an
`execute`/`force`/`retry_anyway` flag — the allow-list simply does not
include them, and an adapter that tried to forward one (see the MCP
`tools/call` argument filter) never gets it past the boundary. No adapter
resolves trust, chooses an authority issuer, changes policy, or resets
replay/operation state. `AUTHENTICATION != EXECUTION AUTHORITY`: an
authenticated tenant may always *propose*; nothing here ever grants it
permission to *execute*.

## 13. Future adapter extension contract

Adding gRPC, Kafka/NATS/other event buses, webhook/event-driven clients, an
A2A-compatible client, OpenAI Agents SDK, Semantic Kernel, or any other
future ingress requires only:

1. a transport wrapper reaching `MCCProposalService` (in-process or via
   `mcc_proposal.transport.HttpProposalBackend`-style HTTP forwarding),
2. serialization into `ProposalRequestV1`,
3. authentication integration resolving a `tenant_id`,
4. conformance tests added to `tests/proposal_conformance/`.

It must **never** require new authority logic, new binding logic, new
replay logic, new status semantics, or a new execution path — all of that
stays exactly where it is today.

## 14. Deferred to future phases

* Real execution: Phase 1 stops at the proposal boundary. A future phase
  wires a *verified* authority decision on top of an accepted proposal —
  through the existing Gate/coordinator, never a second one.
* Cross-tenant status disclosure is closed (Section 6's ownership + binding
  gate) without touching `mcc_core.idempotency`'s keying. A true per-tenant
  *durable execution* namespace (rather than ownership-gated read access to
  one global registry) would still require touching the coordinator's own
  keying — explicitly out of this phase's scope, and unnecessary for the
  disclosure guarantee Phase 1 makes.
* The official `mcp` PyPI SDK, pending explicit dependency approval.
* Deploying the MCP HTTP transport anywhere (`build_mcp_http_app` exists
  and is tested, but is not started by any process in this phase).
* Native framework tool-builders for LangGraph/CrewAI/AutoGen are
  implemented but only verified for clean `ImportError` behavior in this
  environment (the packages are not installed); a dedicated optional-
  dependency CI job, mirroring `tests/interoperability`'s existing
  per-ecosystem jobs, is future work if these are promoted beyond a thin
  facade.
