# MCC-Core Integration Contract — Compliance & Certification

The Compliance & Certification Suite (`mcc_compliance`) independently determines
whether an adapter conforms to a specific version of the framework-neutral
[Integration Contract](INTEGRATION_CONTRACT.md).

```
The Integration Contract defines required behavior.
Adapters implement the Integration Contract.
The Compliance Suite verifies adapter conformance.
No adapter — including VoltAgent — defines the specification.
```

## Compliance architecture

- **The Integration Contract is normative.** It is the single specification an
  adapter conforms to (`docs/INTEGRATION_CONTRACT.md` + the machine-readable
  `mcc_client.contract`).
- **Adapters implement it.** An adapter turns a framework's intent into a proposal
  and drives it through the governed path (`mcc_client` → gateway → gate →
  governed executor). It holds no authority.
- **The suite verifies conformance.** It runs an adapter through a single
  framework-neutral boundary against a **real, in-process governed stack** (real
  gateway + gate + N-of-M consensus + append-only audit + receipt-verifying
  executor, all on loopback), and independently cross-checks every claim against
  ground truth (recorded executions + audit chain). An adapter cannot pass by
  *claiming* success — a fabricated "executed" with no recorded execution is
  detected and fails.
- **Reference integration vs. reference specification.** VoltAgent is a *proven
  reference integration*; it certifies through the same generic boundary as every
  other adapter. It is **not** the reference specification. No adapter defines the
  contract.

The suite is observational and downstream of governance: it introduces no
authorization semantics, no execution path, and no bypass. Like `mcc_evidence` it
lives in the runtime source tree (`src/mcc_compliance/`) and is **not** shipped in
the `mcc-core` wheel.

### Components

| Module | Role |
|--------|------|
| `mcc_compliance.protocol` | the framework-neutral `ComplianceAdapter` boundary (experimental/internal) |
| `mcc_compliance.registry` | strict, fail-closed vector-manifest loading + adapter registry |
| `mcc_compliance.runner` | deterministic runner + ground-truth cross-checks |
| `mcc_compliance.certification` | fail-closed decision + stable fingerprint |
| `mcc_compliance.reporting` | JSON + Markdown + certification manifest |
| `mcc_compliance.cli` | `python -m mcc_compliance certify …` |
| `mcc_compliance/vectors/v1/` | versioned golden vectors for contract v1.0 |

## Running certification

Local command (deterministic, offline):

```bash
python -m mcc_compliance certify \
  --adapter voltagent \
  --contract-version 1.0 \
  --output-dir artifacts/compliance
```

Python API:

```python
from mcc_compliance import run_compliance
from mcc_compliance.adapters import VoltAgentComplianceAdapter

report = run_compliance(VoltAgentComplianceAdapter(), "1.0")
print(report.status, report.certification.fingerprint)
```

- **Select an adapter:** `--adapter reference` or `--adapter voltagent`
  (`python -m mcc_compliance list-adapters`).
- **Select a contract version:** `--contract-version 1.0` (explicit; there is no
  implicit fallback to another version).
- **Reports:** written to
  `artifacts/compliance/<adapter>/<contract-version>/{report.json,report.md,certification.json}`.

Exit codes: `0` CERTIFIED · `1` NOT_CERTIFIED · `2` ERROR. See
[CERTIFICATION.md](CERTIFICATION.md).

## Adding a new adapter

1. **Implement the boundary** (`mcc_compliance.protocol.ComplianceAdapter`): a
   `describe()` returning stable `AdapterMetadata` (including the contract version
   you claim), and a `run_scenario(ctx)` that drives the governed cycle and returns
   a normalized `AdapterOutcome`.
2. **Required metadata:** `name`, `version`, `implementation_id`, and
   `claimed_contract_version` — all non-empty. Incomplete metadata fails closed.
3. **Register it:** `register_adapter("myadapter", MyAdapter)`.
4. **Run certification** as above.
5. **Avoid framework-specific leakage:** the normative vectors and the boundary
   never mention a framework. Your adapter emits proposals only; it MUST NOT
   authorize locally, sign, add an executor, or bypass MCC-Core (the runner and
   the reference-agent static guard enforce this).

## Golden vector governance

Golden vectors are normative executable examples bound to a specific contract
version. The rules:

1. Released vectors for an existing contract version are **immutable** except for
   a clearly documented defect correction.
2. A semantic contract change requires a **new contract version** (new `vX/`).
3. A vector schema change requires a **vector schema version** bump.
4. New mandatory behavior is never silently injected into an old contract version.
5. Every vector references a normative requirement / invariant.
6. Vector IDs (`IC-V1-…`) are stable; ordering is deterministic (by id).
7. Vector content never depends on VoltAgent, never contains secrets, and never
   requires network access.
8. Digests use canonical serialization (`mcc_core.signing.canonical_bytes`); a
   drift test guards the manifest.

## Determinism & security

- The certification **fingerprint** binds adapter identity + adapter version +
  contract version + suite version + vector manifest digest + stable case
  outcomes. It excludes timestamps and durations, so identical inputs produce an
  identical fingerprint.
- The suite fails closed on every error path (adapter load, incomplete metadata,
  wrong claimed version, invalid manifest, unparseable vector, mandatory skip,
  normalization failure, adapter exception, unsupported version). No error path
  yields CERTIFIED.
- Reports never contain secrets, tokens, authorization material, keys, or absolute
  paths — only vector ids, stable codes, verdicts, and counts.

## Known limitations

- The suite certifies **contract-conformant behavior at the governed boundary**.
  For a framework adapter implemented in another language (e.g. VoltAgent in
  TypeScript), the suite drives the same framework-neutral governed contract path
  in-process; it does **not** re-run that framework's native runtime. VoltAgent's
  TS wiring is covered by its own vitest/Docker E2E (`integrations/voltagent/`).
- Deterministic timeout/non-response testing is not part of v1.0 vectors (the
  in-process stack has no deterministic timeout surface); it may be added in a
  future vector schema version.
- `mcc_compliance` is a repository-internal certification tool; it is not an
  independently installable distribution (consistent with `mcc_evidence`).
