# MCC-Core Adapter Certification — Semantics

Certification is a **fail-closed**, version-specific statement about a single
adapter version. See [COMPLIANCE.md](COMPLIANCE.md) for architecture and how to
run it.

## What certification means

A certification result says: *this exact adapter version, driven through the
framework-neutral Integration Contract boundary, satisfied every mandatory
compliance vector for this exact contract version.* Nothing more.

Certification:

- **is version-specific** — bound to a contract version (e.g. `1.0`);
- **is adapter-version-specific** — a new adapter version is a new result;
- **does not certify downstream application code** built on the adapter;
- **does not certify a framework as a whole**;
- **does not replace a production security review**;
- **is fail-closed** — every mandatory vector must pass;
- **treats the pass percentage as informational only** — it never controls the
  decision. A "99% compliant" adapter with one failed mandatory security invariant
  is `NOT_CERTIFIED`.

## Statuses

| Status | Meaning |
|--------|---------|
| `CERTIFIED` | version matches, metadata complete, **all** mandatory vectors passed, no error/skip |
| `NOT_CERTIFIED` | a mandatory vector failed or was skipped, metadata incomplete, or the adapter claimed a contract version other than the target |
| `ERROR` | the result is indeterminate (adapter exception, normalization failure, invalid/unsupported manifest or version) — never treated as success |

An adapter is `CERTIFIED` **only** when all of the following hold:

1. the requested contract version is supported and has published vectors;
2. the adapter's `claimed_contract_version` matches the target;
3. required adapter metadata is present;
4. all mandatory vectors were executed;
5. all mandatory vectors passed;
6. no runner/adapter error occurred;
7. no mandatory vector was skipped.

## Exit codes (CLI)

| Code | Status |
|-----:|--------|
| `0` | `CERTIFIED` |
| `1` | `NOT_CERTIFIED` |
| `2` | `ERROR` (suite/adapter/manifest error, unknown adapter or unsupported version) |

## Reports

Three artifacts per run, under
`artifacts/compliance/<adapter>/<contract-version>/`:

- `report.json` — full machine-readable report (schema version `1`, deterministic
  ordering, stable failure codes, per-case results, certification decision).
- `report.md` — human-readable summary (identity, totals, failed/errored/skipped
  cases, decision reasons, disclaimer).
- `certification.json` — the focused certification record: adapter identity,
  claimed vs certified contract version, suite version, vector manifest digest,
  status, totals, and the certification fingerprint.

## Certification fingerprint

A stable digest (SHA-256 over canonical serialization) binding:

- adapter name, version, implementation id, framework, claimed contract version;
- contract version;
- compliance suite version;
- vector manifest digest;
- the stable per-case outcomes (id + status + failure code).

It **excludes** the timestamp, durations, and any environment-specific value, so:

- repeated identical runs produce the **same** fingerprint;
- changing the adapter version, the vectors (manifest digest), or the contract
  version **changes** the fingerprint.

The fingerprint identifies a certification result; it is **not** a cryptographic
signature and makes no third-party trust claim. (No certification signing is
introduced in this suite.)

## Stable failure codes

Every non-pass outcome carries a stable `ComplianceErrorCode`. Representative
codes: `FABRICATED_EXECUTION`, `EXPECTED_NOT_EXECUTED_BUT_WAS`,
`EXPECTED_EXECUTED_BUT_NOT`, `WRONG_VERDICT`, `UNKNOWN_VERDICT`,
`CONSTRAINT_NOT_APPLIED`, `AUDIT_NOT_VERIFIED`, `REPLAY_NOT_BLOCKED`,
`MANDATORY_SKIP`, `ADAPTER_EXCEPTION`, `NORMALIZATION_FAILED`,
`ADAPTER_VERSION_MISMATCH`, `UNSUPPORTED_CONTRACT_VERSION`, `DUPLICATE_VECTOR_ID`,
`UNKNOWN_VECTOR_TYPE`, `MANIFEST_INVALID`.

## Change control

The suite certifies adapters against the **official** Integration Contract. Adapter
behavior never redefines the contract. Contract evolution follows the
change-control policy in [INTEGRATION_CONTRACT.md](INTEGRATION_CONTRACT.md);
released golden vectors for a contract version are immutable except for documented
defect corrections, and a semantic change requires a new contract (and vector)
version.
