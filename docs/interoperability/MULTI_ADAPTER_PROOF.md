# Multi-Adapter Interoperability Proof

**Status: 48e — COMPLETE. All five adapters land: framework-neutral HTTP + four real
framework ecosystems (LangGraph, AutoGen, CrewAI, VoltAgent), each proven through the
one shared MCC Gateway over the same Integration Contract, policy bundle,
decision-token semantics, execution gate, nonce/replay protection, and audit chain.**
Because the frameworks pin **mutually incompatible** dependencies (see
[Why the adapters run in isolated jobs](#why-the-adapters-run-in-isolated-jobs)),
each is proven in its own isolated CI job over the identical shared governance code —
the 5/5 matrix is the union of those jobs, not one combined process. That isolation
is itself evidence of genuine framework-neutrality: the adapters cannot even share a
Python process, yet every one reaches governance through the same path.

## Objective

Prove that genuinely distinct adapter ingress implementations operate through **one**
shared MCC Gateway under the same Integration Contract, policy bundle, decision-token
semantics, execution gate, nonce/replay protection, and audit chain — establishing
that MCC-Core is framework-neutral governance infrastructure and that VoltAgent is a
reference *integration*, not the reference *specification*.

> The model or framework proposes. MCC decides. The gate enforces. The audit chain
> records.

## The adapter matrix

| # | Adapter | Classification | Native object exercised | Status |
|---|---------|----------------|-------------------------|--------|
| 1 | **VoltAgent** | **REAL FRAMEWORK INTEGRATION** | `@voltagent/core` `Agent.generateText` (Node) | **✔ 48e** (@voltagent/core 2.8.1) |
| 2 | **LangGraph** | **REAL FRAMEWORK INTEGRATION** | `langgraph.graph.StateGraph` → `CompiledStateGraph` | **✔ 48b** (langgraph 1.2.9) |
| 3 | **CrewAI** | **REAL FRAMEWORK INTEGRATION** | `crewai.flow.flow.Flow` via `kickoff` | **✔ 48d** (crewai 1.15.5) |
| 4 | **AutoGen** | **REAL FRAMEWORK INTEGRATION** | `autogen_core.RoutedAgent` on `SingleThreadedAgentRuntime` | **✔ 48c** (autogen-agentchat/core 0.7.5) |
| 5 | **Generic HTTP** | **FRAMEWORK-NEUTRAL HTTP INTEGRATION** | canonical proposal over real `httpx` | **✔ 48a** |

48a delivered adapter 5/5 (Generic HTTP) end-to-end plus the reusable harness the
framework adapters plug into. **48b adds the first real framework adapter,
LangGraph:** it builds and invokes a native `langgraph.graph.StateGraph`
(`CompiledStateGraph`) offline, extracts the node's emitted proposal, normalizes it
to the canonical contract, and runs the same seven scenarios through the same shared
Gateway — total now **2 adapters × 7 = 14 end-to-end scenario results**, one of them
a real framework ecosystem. **48c adds a second real framework adapter, AutoGen**
(Microsoft AutoGen v0.4+ line, `autogen-agentchat`/`autogen-core` 0.7.5): it runs a
native `RoutedAgent` on a native `SingleThreadedAgentRuntime` offline, whose
message-handler emits the proposal. **48d adds a third real framework adapter,
CrewAI** (`crewai` 1.15.5): it builds and runs a native `crewai.flow.flow.Flow`
(`@start` / `@listen` steps) through the framework's own `kickoff` entrypoint
offline, whose final step emits the proposal — total now **4 adapters × 7 = 28
scenario results**, **3 real framework ecosystems**. Each framework is an isolated
optional test dependency (`requirements-langgraph.txt` / `requirements-autogen.txt` /
`requirements-crewai.txt`), installed only by its dedicated CI job
(`interop-langgraph` / `interop-autogen` / `interop-crewai`), which fails if the
official package is absent or not genuinely exercised. CrewAI ships opt-out
telemetry that would otherwise phone home on `kickoff`; the adapter opts out
(`CREWAI_DISABLE_TELEMETRY` / `CREWAI_TRACING_ENABLED=false` / `OTEL_SDK_DISABLED`)
**before** importing crewai, keeping the native run fully offline.

**48e completes the matrix with the fourth real framework, VoltAgent** — a
Node/TypeScript framework, so unlike the in-process Python adapters it is exercised
across a language boundary. The `VoltAgentAdapter` runs the real `@voltagent/core`
`Agent` in a Node subprocess (`integrations/voltagent/src/interop-originate.ts`, part
of the existing VoltAgent governed integration) using the same deterministic offline
model that integration already ships. The native agent genuinely selects its governed
tool and fills the notification arguments; the subprocess emits that proposal as JSON,
and the Python adapter normalizes it and runs the same seven scenarios through the
same shared Gateway. Total now **5 adapters × 7 = 35 end-to-end scenario results**,
**4 real framework ecosystems** + the framework-neutral HTTP integration. The Node
side captures the proposal only — it does **not** run the TypeScript governed path;
governance stays on the one shared Python→Gateway path, identical for every adapter.

### Why the adapters run in isolated jobs

The frameworks pin **mutually incompatible** dependencies — most sharply, CrewAI
requires `pydantic<2.13` while the current AutoGen line resolves `pydantic>=2.13`, and
their OpenTelemetry pins also conflict. A normal `pip install` resolver therefore
**cannot produce a conflict-free environment** containing them together; co-installing
them only succeeds by forcing pip past the conflicts into a state it reports as broken.
Rather than a limitation, this is strong evidence that MCC-Core governance is genuinely
framework-neutral: the adapters do not share a reconcilable runtime dependency surface
with each other, yet every one of them reaches the identical shared Gateway,
Integration Contract, decision-token semantics, execution gate, and audit chain. Each
framework is therefore proven in its **own isolated, reproducible CI job**
(`interop-langgraph` / `interop-autogen` / `interop-crewai` / `interop-voltagent`),
each producing its own evidence bundle over the same harness code; the 5/5 matrix is
the union of those jobs. VoltAgent, being Node, is isolated by language and installs
no Python framework at all. (A single "install everything" job was considered and
rejected: it cannot be built by a clean dependency resolution given the pydantic/OTel
conflicts, so it would not be a reproducible proof.)

## What 48a proves (executable, offline)

One framework-neutral integration was validated against one shared MCC Gateway and
one governance enforcement path, and it **crossed a real HTTP transport boundary**.

- **Shared Gateway topology:** the harness boots one **out-of-process** Gateway
  server (`python -m tests.interoperability._gateway_process`) bound to a real
  loopback TCP endpoint, health-gated on `/ready`. Adapters connect with a real
  `httpx` client (`mcc_client.MCCClient`) — never an in-process ASGI/handler/service
  call. Evidence records the shared `gateway.app.Gateway` /
  `mcc_core.coordinator.EnforcementCoordinator` gate / `mcc_core.audit.AuditLog`
  chain, the deployment id, endpoint, and one shared policy hash.
- **One authorization path:** N-of-M consensus votes bound to a gateway-issued
  single-use challenge, verified server-side. The adapter holds no signing key and
  mints no decisions; the harness plays the independent evaluators.
- **Seven common governance scenarios** (per adapter): `ALLOW`, `DENY`, `REPLAY`,
  `MISMATCH` (actor/resource/payload binding), `AUDIT`, `GATEWAY_UNAVAILABLE`,
  `INVALID_OR_EXPIRED`. 48a total: **1 adapter × 7 = 7 end-to-end scenario results**
  (plus assertions). Each traverses proposal → shared Gateway → decision → gate →
  governed execution or rejection → shared audit.
- **Governance invariants proven:** execution happens only after a verified decision
  passes the gate (ALLOW); policy DENY blocks with no local fallback; a replayed
  challenge/nonce executes at most once; a tampered binding is rejected; expired
  material is rejected; gateway-unavailable fails closed; the shared audit chain
  verifies.

## Why the ingress implementations are genuinely different (and what is shared)

- **Framework-specific** (stops at proposal normalization): each adapter originates
  its proposal its own way. Generic HTTP builds the canonical proposal with no
  framework at all and submits over real HTTP. The framework adapters run a native
  object first, then normalize: LangGraph a compiled `StateGraph`, AutoGen a
  `RoutedAgent` on a `SingleThreadedAgentRuntime`, CrewAI a `Flow` via `kickoff`, and
  VoltAgent a real `@voltagent/core` `Agent` in a Node subprocess.
- **Shared** (identical for all): the Integration Contract + canonical proposal
  shape, the Gateway, the authorization path, the decision-token semantics, the
  execution gate, the nonce/replay registry, and the audit chain. Static AST guards
  (`test_shared_governance_path.py`) prove adapter modules cannot import the decision
  engine, gate/coordinator, signing/token issuer, authority/mandate/consensus
  verifier, the governed executor, or the gateway app, and expose no local
  authorize/execute/sign surface — only the public `mcc_client` boundary.

## Capability-profile linkage

Each adapter publishes a PR #47 Governance Capability Profile; the matrix maps every
declared capability → the scenario that proves it → result, and **fails** if a
declared capability lacks passing evidence.

## Evidence bundle

Generated (not committed) under `artifacts/interoperability/`:
`multi_adapter_matrix.json` (+ `multi_adapter_matrix.schema.json`),
`framework_provenance.json`, `capability_evidence_map.json`,
`audit_verification.json`. The matrix carries proof-format version, a deterministic
`run_id` (excludes wall-clock), the shared-gateway identity, per-adapter provenance +
scenario results + capability map, the audit-chain verification, limitations, and an
overall PASS/FAIL. Generation **fails closed** rather than emitting PASS when
provenance, scenario results, audit correlation, or a declared capability's proof is
missing.

## CI

The base `interoperability` job installs the runtime and runs the whole suite (boot
shared Gateway → 7 scenarios → static guards → build + structurally validate evidence
→ verify audit chain) with the framework-neutral HTTP adapter only, and uploads the
evidence bundle. Each real framework then has its **own isolated job** that installs
just that framework and re-runs the suite, failing if the framework is absent or not
genuinely exercised: `interop-langgraph`, `interop-autogen`, `interop-crewai` (Python;
each `pip install`s its `requirements-<fw>.txt`), and `interop-voltagent` (Node;
`actions/setup-node` + `npm ci` in `integrations/voltagent`, exercising the real
`@voltagent/core` `Agent`). The jobs are isolated because the frameworks pin
incompatible dependencies (see [Why the adapters run in isolated jobs](#why-the-adapters-run-in-isolated-jobs)).
All jobs are offline; no external/paid LLM calls.

## Reproduce locally

```bash
pip install -r requirements.txt -r requirements-dev.txt
pytest tests/interoperability/ -v                        # full 48a suite
pytest tests/interoperability/test_matrix.py -v          # scenarios + evidence
pytest tests/interoperability/test_shared_governance_path.py -v   # static guards
cat artifacts/interoperability/multi_adapter_matrix.json # generated evidence
```

## Limitations & non-claims

- The proof covers **five adapters across four real frameworks** (LangGraph, AutoGen,
  CrewAI, VoltAgent) plus the framework-neutral HTTP integration — each proven in its
  own isolated CI job over the identical shared governance path. The 5/5 matrix is the
  **union** of those jobs (the frameworks cannot share one process); no single run
  registers all five simultaneously, and the evidence bundle is per-job by design.
- This establishes **tested interoperability**, not universal compatibility with
  every AI framework or version, not production certification of third-party
  frameworks, and not production adoption. Each framework is exercised through a
  deterministic, offline path (no LLM, no network) — it proves the governance boundary
  is framework-neutral, not that any given framework's full feature surface is covered.
- VoltAgent remains the reference integration, **not** the reference specification.
  All adapters are subordinate to MCC-Core governance: they only normalize and submit
  proposals, they introduce no second authorization path, execution is impossible
  without a valid MCC decision, and all enforcement remains fail-closed.
