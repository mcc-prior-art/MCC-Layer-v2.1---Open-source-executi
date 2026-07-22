# Canonical Governance Protocol & Canonical Ingress Pipeline (PR #49)

This document specifies the official, framework-neutral **Canonical Governance
Protocol** and the mandatory **Canonical Ingress Pipeline** that every MCC-Core
adapter follows. It turns the five-adapter interoperability proof (PR #48) into a
reusable execution-governance platform with **one** normative wire contract and
**one** ingress path.

> The framework proposes. MCC-Core decides. The gate enforces. The audit chain
> records.

## Objective & architecture

Every adapter — current or future — follows exactly the same architecture:

```
Framework  (planning, orchestration, memory, prompts, agent comms, workflow)
    │
    ▼
Thin Adapter            normalizes the framework's intent
    │
    ▼
CanonicalProposal       the one normative governance request
    │
    ▼
Canonical Ingress Pipeline   validate → normalize → enrich → route (in-process, fail-closed)
    │
    ▼
MCC Gateway             the ONE authoritative governance engine (unchanged)
    │
    ▼
Governance Decision  →  Decision Token  →  Execution Gate  →  Audit Chain
```

MCC-Core remains responsible **only** for execution governance. Frameworks remain
responsible for planning, orchestration, memory, prompts, agent communication, and
workflow execution. The ingress pipeline adds no governance — it is a thin,
in-process front door to the existing Gateway.

## Reconciliation with the Integration Contract (PR #43) — no semantic drift

PR #43 established that there is **one** normative wire contract and that the SDK's
shipped models (`mcc_client.Verdict`, `mcc_client.Decision`,
`mcc_client.ExecutionResult`, and the authorization artifacts) are the canonical
implementation artifacts — *no parallel wire models*. PR #49 preserves this exactly:

| PR #49 concept | How it reconciles with PR #43 |
|----------------|-------------------------------|
| `PROTOCOL_VERSION` | **Is** `mcc_client.contract.CONTRACT_VERSION` — one version axis, not a second number. |
| Version negotiation | Reuses `mcc_client.contract.check_version_compatibility` verbatim (unknown major fails closed). |
| Error/reason codes | Reuse `mcc_client.contract.ContractErrorCode` / `ErrorCategory` — no new taxonomy. |
| `GovernanceDecision` | A response **envelope** that *wraps* `mcc_client.Decision` (held by reference) and re-exposes it in the canonical response shape. It never replaces the `Decision` or the Decision Token, and its verdicts are `mcc_client.Verdict`. |
| `CanonicalProposal` | An **additive** request object — the SDK previously had no first-class request type. It is the promotion of the proven interop proposal into a normative object. |
| Capabilities | Validated against the single PR #47 vocabulary (`mcc_compliance.capability_profile.KNOWN_CAPABILITIES`). |
| Canonicalization / hashing | Reuses `mcc_core.signing` (one implementation) so proposal hashes match the rest of the platform's evidence tooling. |
| Adapter Registry | Descriptive/informational only; distinct from the compliance-suite factory registry (`mcc_compliance.registry`). Grants no authority. |

The authoritative decision remains `mcc_client.Decision`; the authoritative
execution-authorization artifact remains its **Decision Token**. `GovernanceDecision`
only *describes* a decision the Gateway already made.

## CanonicalProposal — the normative request

`mcc_protocol.CanonicalProposal` is the one request object every adapter produces.
Fields (all present; optional ones default):

- protocol/identity: `contract_version`, `proposal_id`, `trace_id`, `correlation_id`,
  `adapter_id`, `adapter_version`, `framework`, `framework_version`
- principal/actor: `actor`, `principal`
- action: `action`, `resource`, `requested_scope`, `payload`
- context: `authority_context`, `policy_context`, `risk_context`, `metadata`
- integrity/lifetime: `action_hash`, `nonce`, `issued_at`, `expires_at`

**Lifecycle.** `CanonicalProposal.create(...)` fills protocol defaults (ids, nonce,
timestamps, and the `action_hash` over `{action, resource, actor, payload}` using the
platform canonicalization) and validates. `validate()` is fail-closed: any missing or
empty required field, non-object payload/context, or an `action_hash` that does not
match its binding is rejected with `ProposalValidationError`. Building or validating a
proposal **never authorizes anything** — schema validity is not authorization, and
`action_hash` is a proposal-integrity/trace hash, *not* the Gate's authoritative
binding (the Gate recomputes and verifies its own).

## GovernanceDecision — the response envelope

`mcc_protocol.GovernanceDecision` composes an `mcc_client.Decision` and re-exposes:
`decision_id`, `proposal_id`, `verdict` (an `mcc_client.Verdict`), `reason_codes`
(from `ContractErrorCode`), `reason`, `constraints`, `applied_constraints`,
`decision_token` (the existing token, by reference), `policy_hash`, `action_hash`,
`nonce`, `validity_window`, `audit_reference`, `contract_version`, `timestamp`.

**Lifecycle.** `GovernanceDecision.from_decision(proposal, decision)` binds a gateway
`Decision` to its originating proposal. It copies nothing semantic — verdict, token,
constraints, and audit id all come straight from the authoritative `Decision`, which
is retained by reference (`.decision`). `has_decision_token`, `executable`, `denied`,
and `needs_approval` delegate to the wrapped decision's semantics.

## Canonical Ingress Pipeline

`mcc_protocol.CanonicalIngressPipeline` runs, in fixed order, before governance:

1. **schema validation** — structural validity of the proposal (fail-closed).
2. **protocol validation** — a protocol version is declared; the proposal is not
   already expired.
3. **version negotiation** — `check_version_compatibility`; an unsupported major
   fails closed with no downgrade.
4. **adapter registry lookup** — the adapter is registered and supports the version
   (configurable; `require_registered_adapter`).
5. **capability validation** — any `policy_context.required_capabilities` are declared
   by the adapter (single PR #47 vocabulary).
6. **metadata enrichment** — standardized ingress metadata (trace/correlation ids,
   timestamps, adapter/framework, protocol version) is attached. Only metadata
   changes; the action binding is never touched.
7. **policy context resolution** — normalizes the policy context the Gateway will use
   (an optional, non-authorizing resolver hook). It does **not** evaluate policy.
8. **routing** — the enriched proposal is submitted to the authoritative MCC Gateway
   through an injected `Router` callable (in production, `mcc_client.MCCClient`), and
   the returned `Decision` is wrapped into a `GovernanceDecision`.

**The pipeline is not a second governance engine.** It imports no gateway/gate/
authority/consensus/executor/signing internals; it reaches the Gateway *only* through
the injected router. Every failure fails closed: after a rejection **no router call
happens**, and a rejection is never an authorization. Each rejection carries the
`IngressStage` (observability) and a blocking `ContractErrorCode` (the one taxonomy).

## Adapter Registry

`mcc_protocol.AdapterRegistry` holds `AdapterDescriptor`s: `adapter_id`, `framework`,
`adapter_version`, `supported_protocol_versions`, `capabilities`, and informational
`conformance`/`compatibility` metadata. It is **informational only** — a hard
boundary enforced by an architecture guard: it does not grant authority, certify
trust by itself, authorize execution, verify signatures, or become a governance
decision boundary. Registration is not permission; conformance metadata is a claim/
reference (e.g. to a PR #46 certification), never a trust decision made by the
registry.

## Version negotiation

There is one version axis: `PROTOCOL_VERSION == CONTRACT_VERSION` (`1.0`). Negotiation
delegates to the PR #43 rule: a malformed version → `CONTRACT_VERSION_MALFORMED`; an
unknown major → `CONTRACT_VERSION_UNSUPPORTED` (fail-closed, no downgrade); a known
major with a higher minor is compatible but flagged (`newer_minor`). Adapters declare
`supported_protocol_versions`; the pipeline rejects a proposal whose version the
adapter does not support.

## Unified observability

`mcc_protocol.PipelineMetrics` provides bounded-cardinality Prometheus metrics on an
**isolated** registry (never the global default): requests per adapter/framework/
version, protocol-version usage, validation/pipeline failures (by stage + stable
code), routing outcomes, verdict statistics, and pipeline latency. Labels are
low-cardinality and caller-controlled; no payloads, secrets, or PII ever enter a
label or value. Instrumentation never influences a decision.

## Architecture guards (CI-enforced)

`tests/protocol/test_architecture_guards.py` fails CI if the protocol layer:

- imports governance internals (gate, coordinator, authority, consensus, mandate,
  policy engine, audit, nonce, the gateway app, the executor);
- imports any signing/token-issuing surface (only the pure hash helpers
  `canonical_bytes` / `sha256_hex` / `hash_payload` / `hash_action` from
  `mcc_core.signing` are allowed);
- exposes a local `authorize`/`execute`/`sign`/`issue_token`/`mint`/`decide` surface;
- reaches the Gateway other than through the injected router;
- introduces a second version axis (`PROTOCOL_VERSION` must equal `CONTRACT_VERSION`).

`tests/protocol/test_reconciliation.py` additionally pins the single-contract
guarantees (same `Verdict`/`Decision` objects, reason codes ⊆ `ContractErrorCode`,
capability vocabulary is the PR #47 one, one canonicalization).

## Evidence

`tests/interoperability/test_canonical_ingress.py` produces reproducible evidence
(`artifacts/protocol/canonical_ingress_evidence.json`) that every registered PR #48
adapter — Generic HTTP, LangGraph, CrewAI, AutoGen, VoltAgent — builds a
`CanonicalProposal` and traverses the **identical** ingress pipeline into the **one**
real, out-of-process MCC Gateway (over real HTTP) and yields a `GovernanceDecision`
that wraps the authoritative `Decision` + Decision Token. As in PR #48, the frameworks
pin mutually incompatible dependencies, so the full five-adapter set is proven as the
union of the isolated per-framework CI jobs over the identical pipeline code.

## Extension rules (adding a future adapter)

A new framework requires **only a thin adapter** — never a change to the protocol,
pipeline, or governance:

1. Write a thin adapter that turns the framework's native intent into a
   `CanonicalProposal` via `CanonicalProposal.create(...)`. Do nothing else — no
   authorization, no signing, no execution, no local policy.
2. Register an `AdapterDescriptor` (identity, version, supported protocol versions,
   capabilities from the PR #47 vocabulary).
3. Route through `CanonicalIngressPipeline` with a router backed by `mcc_client`.
4. Add the adapter to the interoperability matrix and its isolated CI job.

Prohibited (and guarded): importing governance internals, minting decisions or
tokens, evaluating policy, bypassing the pipeline/gateway/audit, or introducing
framework-specific governance semantics. Capability support is not execution
permission; registration is not authority.

## Adapter developer guide (quick start)

```python
import mcc_protocol as mp
from mcc_client import MCCClient

# 1. Build the one canonical request from your framework's intent.
proposal = mp.CanonicalProposal.create(
    adapter_id="my-adapter", adapter_version="1.0.0", framework="my-framework",
    actor="agent/notify-bot", action="send_notification", resource="notifications",
    payload={"recipient": "customer-123", "message": "hi", "priority": 2,
             "channel": "email"},
)

# 2. Register the adapter descriptor (informational).
registry = mp.AdapterRegistry()
registry.register(mp.AdapterDescriptor(
    adapter_id="my-adapter", framework="my-framework", adapter_version="1.0.0",
    supported_protocol_versions=(mp.PROTOCOL_VERSION,)))

# 3. Route through the one ingress pipeline into the authoritative Gateway.
def router(p):
    client = MCCClient("https://gateway.example", api_key="…")
    return client.evaluate(actor_id=p.actor, action=p.action,
                           resource=p.resource, payload=p.payload)

pipeline = mp.CanonicalIngressPipeline(registry, router)
result = pipeline.process(proposal)

if result.ok:
    gov = result.decision           # GovernanceDecision, wrapping mcc_client.Decision
    if gov.executable:
        ...                          # execute ONLY via the governed path + authorization
else:
    err = result.error               # fail-closed: stage + stable ContractErrorCode
```

The adapter never authorizes or executes. Execution still requires the governed
execution path with valid authorization material (consensus/mandate/approval) and a
Decision Token that the Execution Gate verifies — unchanged by PR #49.

## Non-goals

PR #49 does **not**: introduce another adapter; change governance, Decision Token,
Policy Bundle, or Execution Gate semantics; move orchestration/planning/workflow
execution into MCC-Core; add a second gateway, governance engine, or authorization
path; or introduce framework-specific routing logic. It standardizes the mandatory
ingress path — nothing more.
