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

---

# Certified Adapter Program

A narrow, repository-native layer (`mcc_compliance.program`) that turns an official
compliance result into a deterministic, machine-readable **certification** and
records the repository's certified adapters in a version-controlled manifest that
CI regenerates and verifies.

## What repository certification means — and does not

- **Means:** for the stated contract and vector-set versions, this exact adapter
  version passed the repository's official compliance suite, and the evidence
  hashes to the recorded digest.
- **Does not mean:** any public, third-party, or legal accreditation; any assurance
  about downstream application code; any grant of execution authority. Certification
  changes no MCC-Core governance decision, Gate semantics, or the verified
  execution path.

## Normative vs informative

- **Normative:** the Integration Contract and the golden vectors (mapped to
  invariants).
- **Informative:** adapters, compliance reports, **and certifications/manifest**.
  A certification is a *representation* of compliance evidence — it never defines
  required behavior.

## The chain (and how each link binds)

```
Integration Contract  → golden vectors → compliance result → certification → manifest
   (normative)           (normative)      (run_compliance)     (derived)     (recorded)
```

`certify(adapter, contract_version=…)` runs `run_compliance` (real governed stack,
ground-truth cross-check, **no wall-clock time**) and derives a `CertificationResult`.
Certification is `CERTIFIED` only when the compliance result is `CERTIFIED`, the
adapter's claimed contract version matches the target, and metadata is complete —
otherwise `NOT_CERTIFIED` (fail-closed).

## Version binding

A certification is bound to the exact **contract version** and the exact
**compliance-suite / vector-set version** (and the vector-manifest digest). A
mismatch or unsupported version fails closed and never certifies.

## Deterministic evidence digest

`evidence_digest` is a SHA-256 over the canonical serialization of the semantic
evidence: adapter identity + version, contract version, compliance/vector-set
version, vector-manifest digest, ordered scenario outcomes, invariant coverage, and
the overall status. It excludes the timestamp (certification carries **no**
wall-clock time), filesystem paths, and object repr, so the same inputs always
produce the same digest. It is an **integrity fingerprint, not a signature** — no
PKI, no trust roots, no remote verification.

## Certify an adapter locally

```bash
# One adapter → JSON/Markdown/certification.json under the output dir
python -m mcc_compliance certify --adapter voltagent --contract-version 1.0 \
  --output-dir artifacts/compliance

# Regenerate the repository manifest of certified adapters
python -m mcc_compliance build-manifest --contract-version 1.0

# Verify the committed manifest against freshly regenerated evidence
python -m mcc_compliance verify-manifest      # exit 0 == OK, 1 == mismatch
```

Python API: `from mcc_compliance import certify, build_manifest, verify_manifest`.

## The repository manifest

`certifications/manifest.json` records only adapters the official suite genuinely
certifies (currently the **reference** adapter and **VoltAgent**). Each entry binds
adapter identity + version, contract version, compliance-suite/vector-set version,
vector-manifest digest, status, scenario counts, covered invariants, and the
evidence digest (also the stable `report_id`). It is deterministically ordered and
schema-versioned.

## How CI verifies it

CI runs `verify-manifest`, which **regenerates** certification from real evidence
and compares it canonically to the committed file. It fails if:

- an official adapter no longer conforms (regression);
- a digest, status, or count was hand-edited (tamper);
- an entry is stale, or a non-certified adapter was slipped in as `CERTIFIED`.

A developer therefore cannot flip an entry to `CERTIFIED` without CI detecting that
the actual compliance evidence does not match.

## Adding a future adapter

1. Implement the framework-neutral `ComplianceAdapter` boundary and register it.
2. Confirm it certifies: `python -m mcc_compliance certify --adapter <name> …`.
3. Add its registry key to `OFFICIAL_ADAPTERS`, run `build-manifest`, and commit the
   updated `certifications/manifest.json`. CI's `verify-manifest` will hold it to
   real evidence from then on.

## Invalidation

Any change to the adapter (version/behavior), the contract version, or the vector
set changes the evidence digest and therefore the certification. A regression drops
the adapter from the regenerated manifest, and CI fails until the committed manifest
is corrected. VoltAgent remains a **conforming reference integration, not the
reference specification**.
