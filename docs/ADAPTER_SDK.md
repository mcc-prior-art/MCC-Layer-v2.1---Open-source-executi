# MCC-Core Adapter SDK (PR #50)

A small, stable, framework-neutral **public SDK** for building MCC-Core adapters.
It lets third-party developers integrate any framework with MCC-Core governance
**without** importing or depending on the gateway, execution gate, authority, policy
engine, audit chain, runtime executor, or private signing internals.

> Framework proposes. Adapter translates. CanonicalProposal is produced.
> CanonicalIngressPipeline executes. GovernanceDecision is returned. The Execution
> Gate enforces. The audit chain records.

This is **ecosystem enablement**, not new architecture. It adds no governance
semantics, no second decision/proposal/verdict model, and no alternate authorization
or gateway path. It is a thin façade over the Canonical Governance Protocol (PR #49).

## Purpose

Make the platform usable by external adapter authors with the minimum stable surface
needed to: declare an adapter, describe its metadata, translate a framework-native
request into the authoritative `CanonicalProposal`, submit it **only** through the
mandatory `CanonicalIngressPipeline`, receive a `GovernanceDecision`, translate it
back to a native response, validate the adapter's structure, and generate
deterministic evidence.

## Trust boundary

An adapter is **purely translational**. It never authorizes, allows, approves,
executes, enforces, evaluates policy, issues tokens, or signs. Those verbs belong to
the governance runtime, reached only through the ingress pipeline into the
authoritative MCC Gateway. CI **architecture guards** (`tests/adapter_sdk/test_architecture_guards.py`)
fail the build if the SDK imports any governance internal (gate/authority/policy/
audit/executor/gateway/private-signing) or exposes any of those verbs, and if it
introduces a parallel `Decision`/`Verdict`/`CanonicalProposal`/`GovernanceDecision`
model. The SDK reuses the authoritative models verbatim.

```
native request
   │  Adapter.to_proposal(context, native_request)     ← translate only
   ▼
CanonicalProposal            (mcc_protocol — authoritative request)
   │  AdapterRunner.run(...)  → CanonicalIngressPipeline (the ONE mandatory path)
   ▼
MCC Gateway                  (authoritative decision — unchanged)
   ▼
GovernanceDecision           (envelope wrapping Decision + Decision Token + Verdict)
   │  Adapter.to_response(decision)                    ← translate only
   ▼
native response
```

## Public surface

Curated, no wildcards, no implementation helpers:

| Export | Purpose |
|--------|---------|
| `Adapter` | Base class: implement `describe` / `to_proposal` / `to_response` (+ optional `sample_request`). |
| `AdapterMetadata` | Immutable, deterministic, version-compatible, fail-closed metadata. |
| `AdapterContext` | Immutable, secret-free, ingress-safe context for building a proposal. |
| `AdapterRunner` / `AdapterRunResult` | Drives native → proposal → pipeline → decision → native, fail-closed. |
| `register_adapter` / `AdapterRegistration` | Informational registration (reuses `AdapterRegistry`); grants no authority. |
| `validate_adapter` / `AdapterValidationReport` | Structural validation only — **not** certification. |
| `generate_adapter_evidence` | Deterministic, sanitized SDK evidence. |
| `AdapterSDKError` | Fail-closed error carrying an existing `ContractErrorCode`. |
| `SDK_VERSION` | The single-source `mcc-core` distribution version. |

## Adapter lifecycle

1. **Declare** — subclass `Adapter`; implement `describe()`, `to_proposal()`,
   `to_response()`, and (optionally) `sample_request()`.
2. **Describe** — `describe()` returns an `AdapterMetadata` (immutable). Validate it
   with `.validate()`; hash it deterministically with `.digest()`.
3. **Translate in** — `to_proposal(context, native_request)` builds a
   `CanonicalProposal` via `self.make_proposal(...)`, bound to the adapter identity
   and the request context. It never authorizes.
4. **Submit** — `AdapterRunner.run(context, native_request)` runs the proposal
   through the **one** `CanonicalIngressPipeline` (schema → protocol → version
   negotiation → adapter registry → capability → enrichment → policy-context →
   routing) into the Gateway. There is no bypass.
5. **Receive** — the runner returns an `AdapterRunResult` carrying the
   `GovernanceDecision` (which wraps the authoritative `Decision` + Decision Token +
   `Verdict`).
6. **Translate out** — `to_response(decision)` maps the decision to a native
   response. A native response is produced **only after** a decision is returned; a
   pipeline rejection fails closed with no response.

## AdapterMetadata

Immutable; reuses the single capability vocabulary (PR #47), the single version
rule (PR #43), and the single canonicalization (`mcc_core.signing`). Unsupported
metadata raises `AdapterSDKError` with an existing `ContractErrorCode`
(fail-closed). Fields: `adapter_id`, `adapter_version`, `framework_name`,
`framework_version`, `protocol_version`, `contract_version`, `capabilities`,
`supported_input_modes`, `supported_output_modes`, `vendor`, `maintainer`,
`documentation_url`, `source_url`. `to_dict()` is deterministic; `digest()` is a
reproducible content hash.

## AdapterContext

Immutable, deterministic, and **secret-free**: its `repr()` never dumps
`framework_metadata` / `extension` values (only key names), and evidence never
carries them. Extension data is bounded and must be JSON-serializable (unserializable
values are rejected, fail-closed). Fields: `actor_reference`, `tenant`, `namespace`,
`trace_id`, `correlation_id`, `request_timestamp`, `framework_metadata`,
`declared_capabilities`, `extension`.

## Registration

`register_adapter(adapter, registry)` records an informational `AdapterDescriptor`
in a protocol `AdapterRegistry`. It **grants no authority** and certifies nothing.
Duplicate adapter ids are rejected (unless `replace=True`); incompatible protocol
versions are rejected. Registration is deterministic and serializable.

## Validation — NOT certification

`validate_adapter(adapter)` returns a deterministic `AdapterValidationReport` with
structural checks only (metadata validity, required translational methods, no
authoritative verbs, protocol/contract compatibility, deterministic serialization,
capability vocabulary, registry compatibility, `CanonicalProposal` production). Its
status is `VALIDATION_PASSED` / `VALIDATION_FAILED` and it carries an explicit
disclaimer.

**SDK validation is NOT certification.** It never claims *certified*, *officially
compliant*, *production-approved*, or *trusted*. Certification is a separate, later
roadmap milestone (the Compliance & Certification Suite already exists as
`mcc_compliance`; binding it to the SDK surface is future work).

## Evidence

`generate_adapter_evidence(adapter, run_result=..., validation_report=...)` produces
a deterministic, reproducible, sanitized record (adapter metadata + digest, SDK /
protocol / contract versions, proposal hash, pipeline summary, a token-free
governance-decision summary, and the validation report) under
`artifacts/adapter-sdk/`. It excludes wall-clock time, random identifiers, and any
secret/token material, so generating it twice yields byte-identical output. SDK
evidence is intentionally **distinct** from future Compliance/Certification evidence.

## Version compatibility

There is one version axis. `protocol_version` and `contract_version` are checked with
the reused rule (`mcc_client.contract.check_version_compatibility`): a malformed or
unsupported-major version fails closed with no downgrade. `SDK_VERSION` is the single
`mcc-core` distribution version.

## Migration guide

To migrate an existing adapter to the SDK:

1. Move the framework-native → proposal logic into `Adapter.to_proposal`, building
   the proposal with `self.make_proposal(...)` (keep the same action / resource /
   payload so behaviour is preserved).
2. Move the decision → native logic into `Adapter.to_response`.
3. Declare `describe()` with the adapter's metadata and capabilities.
4. Drive requests with `AdapterRunner` and a router backed by
   `mcc_client.MCCClient.evaluate` — do not call the gateway any other way.

The reference migration is the framework-neutral HTTP adapter
(`examples/adapter_sdk/reference_http_adapter.py`), chosen because it is the smallest,
framework-neutral integration. It preserves the PR #48 `GenericHttpAdapter`'s
behaviour (identical stable proposal content and identical verdicts through the real
Gateway) and the existing interoperability evidence is untouched — see
`tests/adapter_sdk/test_reference_migration.py`. Only one adapter is migrated.

## Quick start

See `examples/adapter_sdk/minimal_adapter.py` for a complete, runnable example
(declare → translate → pipeline → decision → native → validation → evidence) with no
execution, authorization, credentials, or external side effects.

## Packaging

The Adapter SDK ships **inside the existing `mcc-core` distribution** — no new,
separately-versioned or separately-published package, no new PyPI project. It uses
the single-source version (`mcc._version`). The wheel/sdist carry the facade (`mcc`),
the Adapter SDK (`mcc_adapter_sdk`), and the Canonical Governance Protocol
(`mcc_protocol`), plus the **governance-free** curated subsets of `mcc_core` (pure
canonical hashing) and `mcc_compliance` (the capability vocabulary) that the SDK
import path needs. The governance engine (gate, authority, consensus, coordinator,
audit, …) and the compliance suite are **excluded from the built distribution** by a
narrow `build_py` correction (`setup.py`), and importing the SDK/protocol never loads
them (lazy package exports). A clean install can import the curated public API and
run the minimal example. `mcc_client` remains its own dependency distribution and is
never vendored.

## Non-goals

No new governance semantics, no second `CanonicalProposal`/`GovernanceDecision`/
`Verdict`, no local authorization/policy/execution/enforcement, no token issuance or
signing, no new gateway/ingress pipeline/transport, no dynamic marketplace or plugin
loading, no new framework adapters, no migration of every adapter, and no
Compliance & Certification Suite — those are out of scope for this PR.
