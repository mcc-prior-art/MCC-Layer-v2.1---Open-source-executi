# Multi-Adapter Interoperability Proof

**Status: 48a — reusable foundation + framework-neutral HTTP integration (adapter
5/5).** The four real-framework adapters (VoltAgent, LangGraph, CrewAI, AutoGen)
are added in follow-ups 48b–e, each with its own isolated dependency install. This
document describes the foundation and what it proves today; it does **not** yet
claim the full five-adapter / four-framework matrix.

## Objective

Prove that genuinely distinct adapter ingress implementations operate through **one**
shared MCC Gateway under the same Integration Contract, policy bundle, decision-token
semantics, execution gate, nonce/replay protection, and audit chain — establishing
that MCC-Core is framework-neutral governance infrastructure and that VoltAgent is a
reference *integration*, not the reference *specification*.

> The model or framework proposes. MCC decides. The gate enforces. The audit chain
> records.

## The adapter matrix

| # | Adapter | Classification | Status |
|---|---------|----------------|--------|
| 1 | VoltAgent | REAL FRAMEWORK INTEGRATION | pending 48b–e |
| 2 | LangGraph | REAL FRAMEWORK INTEGRATION | pending 48b–e |
| 3 | CrewAI | REAL FRAMEWORK INTEGRATION | pending 48b–e |
| 4 | AutoGen | REAL FRAMEWORK INTEGRATION | pending 48b–e |
| 5 | **Generic HTTP** | **FRAMEWORK-NEUTRAL HTTP INTEGRATION** | **✔ 48a** |

48a delivers adapter 5/5 (Generic HTTP) end-to-end plus the reusable harness the
framework adapters plug into. A feasibility probe confirmed all four frameworks
install and run in this environment (LangGraph/AutoGen light; CrewAI heavy but
resolvable; VoltAgent via Node 22) — so 48b–e are unblocked.

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
  framework at all and submits over real HTTP. The framework adapters (48b–e) run a
  native `langgraph`/`crewai`/`autogen`/VoltAgent object first, then normalize.
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

The `interoperability` job installs the runtime, runs the whole suite (boot shared
Gateway → 7 scenarios → static guards → build + structurally validate evidence →
verify audit chain), and uploads the evidence bundle. Offline; no external/paid LLM
calls. 48b–e add isolated per-framework install steps.

## Reproduce locally

```bash
pip install -r requirements.txt -r requirements-dev.txt
pytest tests/interoperability/ -v                        # full 48a suite
pytest tests/interoperability/test_matrix.py -v          # scenarios + evidence
pytest tests/interoperability/test_shared_governance_path.py -v   # static guards
cat artifacts/interoperability/multi_adapter_matrix.json # generated evidence
```

## Limitations & non-claims

- 48a proves **one** framework-neutral integration end-to-end and the shared
  foundation; it is **not** yet the five-adapter / four-framework proof.
- This establishes **tested interoperability**, not universal compatibility with
  every AI framework or version, not production certification of third-party
  frameworks, and not production adoption.
- VoltAgent remains the reference integration, **not** the reference specification.
  All adapters are subordinate to MCC-Core governance: they only normalize and submit
  proposals, they introduce no second authorization path, execution is impossible
  without a valid MCC decision, and all enforcement remains fail-closed.
