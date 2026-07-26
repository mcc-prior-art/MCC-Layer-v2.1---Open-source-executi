# MCC End-to-End Certification Pipeline

PR #67 (trust and publication foundation added in PR #68 — see
[`CERTIFICATION_TRUST_AND_PUBLICATION.md`](CERTIFICATION_TRUST_AND_PUBLICATION.md)
for the Issuer Identity model, Trust Store, Signing-Key Provider contract,
Publication mechanism, and trusted offline verification against an
explicit trust-anchor set; PR #69 registers the five production reference
ecosystems as real Certification Targets on top of this same pipeline —
see [`CERTIFICATION_FIVE_ECOSYSTEMS.md`](CERTIFICATION_FIVE_ECOSYSTEMS.md)).
This is a **different** system from
[`docs/CERTIFICATION.md`](CERTIFICATION.md) / [`COMPLIANCE.md`](COMPLIANCE.md)
(the pre-existing Integration-Contract-scoped adapter certification suite,
`src/mcc_compliance/`). That system certifies an *adapter version* against
the wire-protocol Integration Contract. **This** system implements the
MCC-CP-001 Certification Program's own normative pipeline: it produces and
independently verifies the full **Evidence Bundle → Certification Manifest →
Technical Certificate** chain (MCC-EB-001, MCC-CM-001, MCC-TC-001) for a
*Certification Target*. The two never reinterpret or reuse each other's
artifacts.

## Conformance vs. certification

- **Conformance** (`conformance/normative-v1.0/`, `src/mcc_conformance/`) is
  a self-audit: is MCC-Core's *own source code* conformant to the four
  Normative v1.0 specifications? It answers that question for the
  specifications' authors/maintainers and is not about any external target.
- **Certification** (this package, `mcc_certify`) is a *pipeline*: given a
  Certification Target (an implementation to be evaluated), it runs a
  Conformance Run against that target, packages the result as a
  reproducible Evidence Bundle, binds a Certification Manifest to it, issues
  a Technical Certificate, and independently verifies the whole chain
  offline before ever reporting success.

The two are related (certification's Conformance Run stage evaluates
normative requirements, the same vocabulary the conformance self-audit
uses) but are not the same system, and this PR does not merge them.

## Certification lifecycle

```
Certification Target
    -> Preflight                  (CP-001 §9.1 Registration + §9.2 Environment Validation)
    -> Conformance Run            (CP-001 §9.3 Conformance Evaluation)
    -> Evidence Bundle            (CP-001 §9.4 Evidence Generation)
    -> Certification Manifest     (CP-001 §9.7 Artifact Generation, manifest half)
    -> Technical Certificate      (CP-001 §9.7 Artifact Generation, certificate half;
                                    gated by §9.5/§9.6 Conformance Assessment / Decision,
                                    folded into the Conformance Run's own PASS/FAIL result)
    -> Offline Verification       (Goal G3 / Invariant CI-008 "Independently Verifiable";
                                    not a numbered CP-001 pipeline stage, but mandatory
                                    and never skippable in this pipeline)
```

CP-001 §9.8 Publication is explicitly `MAY` (optional) in the specification
and is not implemented — writing the run's artifact tree to `--output`
already satisfies Artifact Generation; nothing is further "published" (no
registry, no distribution mechanism).

A failed mandatory stage terminates certification (CP-001 §9 "A failed
mandatory stage SHALL terminate certification"). Evidence is always
generated once Conformance Evaluation completes — even for a target whose
requirements FAIL — consistent with CI-002 "Evidence precedes
certification"; but Certification Manifest and Technical Certificate
generation are skipped whenever any requirement FAILs, consistent with
CI-003 "Certification precedes Technical Certificate issuance" (8.7: "A
Technical Certificate SHALL only be issued after successful certification").

## Certification Target model

A Certification Target (`mcc_certify.CertificationTarget`) is CP-001 §7.2's
"Certification Subject": *any implementation evaluated against one or more
MCC specifications*. It carries only:

- a stable `target_id` and `target_type`;
- `implementation_version`;
- `certification_profile` (its own declared default; `--profile` overrides it);
- `provenance` metadata;
- `declared_capabilities`;
- a deterministic `conformance_entry_point` — the target's own test/
  conformance entry point, evaluated by the pipeline (never by the target
  itself: "the certification pipeline certifies targets, targets do not
  certify themselves").

It carries **no** authorization, policy evaluation, token issuance,
execution, or governance authority.

### Registered targets

Six: `reference-fixture` — an internal, deterministic test fixture with
four trivial self-referential checks — plus, as of PR #69, the five
production reference ecosystems (`generic-http`, `langgraph`, `crewai`,
`autogen`, `voltagent`), each wired to its real, unmodified PR #48 adapter.
Registration is independent of official certification: see
[`CERTIFICATION_FIVE_ECOSYSTEMS.md`](CERTIFICATION_FIVE_ECOSYSTEMS.md) for
which of the five are currently CANDIDATE versus OFFICIALLY CERTIFIED —
**no ecosystem has an OFFICIAL certificate yet** (no production Issuer key
exists in this repository).

## CLI

No top-level `mcc` console-script binary exists anywhere in this repository
today — every existing CLI here is invoked as `python -m <package> ...`
(see `mcc_conformance`, `mcc_compliance`), and the distributed `mcc-core`
wheel deliberately ships only a curated, governance-free module subset
(`pyproject.toml` / `setup.py`), excluding `mcc_conformance` and
`mcc_evidence` entirely. This PR does not add a first-ever top-level
console-script entry point or expand the curated wheel's contents without
explicit approval. The requested `mcc certify <target>` contract is
therefore realized, functionally equivalently, as:

```bash
python -m mcc_certify certify <target> [options]
python -m mcc_certify verify <run-dir>
python -m mcc_certify list-targets
```

### `certify` options

| Option | Meaning |
|---|---|
| `--output <dir>` | output directory (default `artifacts/certification`) |
| `--run-id <id>` | explicit run identifier — **required** for reproducible regeneration |
| `--timestamp <RFC3339>` | explicit issuance timestamp — **required** for reproducible regeneration |
| `--profile <id>` | certification profile override (defaults to the target's own) |
| `--format json` | print the machine-readable `certification-result.json` to stdout |
| `--verify` | accepted for CLI-contract compatibility; offline verification is **always** performed and cannot be disabled |
| `--force` | overwrite an existing run directory for this `target_id`/`run_id` |

Exit codes: `0` CERTIFIED, `1` NOT_CERTIFIED (see the result's `failed_stage`
/ `failure_reason`), `2` usage/unexpected error.

### Minimal example

```bash
python -m mcc_certify certify reference-fixture \
  --output artifacts/certification \
  --run-id example-run-001 \
  --timestamp 2026-07-26T00:00:00Z
```

### Independent offline verification of the result

```bash
python -m mcc_certify verify artifacts/certification/reference-fixture/example-run-001
```

## Output artifacts

```
<output>/
  <target-id>/
    <run-id>/
      conformance/
        conformance-run.json        # requirement_id + outcome + detail, per requirement
      evidence-bundle/
        bundle_descriptor.json      # MCC-EB-001 Bundle Descriptor
        integrity_record.json       # MCC-EB-001 Integrity Record (Hash References)
        provenance_record.json      # MCC-EB-001 Provenance Record
        evidence/
          req-<requirement_id>.json # one Evidence Item per requirement
      certification-manifest.json   # MCC-CM-001 Certification Manifest (Evidence Bundle Reference)
      technical-certificate.json    # MCC-TC-001 Technical Certificate (signed)
      verification-report.json      # Stage 6 Offline Verification result
      certification-result.json     # final machine-readable result (see below)
      run-metadata.json             # target/profile/run identity + tool/spec versions
      README.txt
```

A failed run is retained (for diagnostics) under `<run-id>.failed/` instead
of `<run-id>/` — the real `<run-id>` directory is **never** created unless
every mandatory stage, including Offline Verification, succeeded.

`certification-result.json` states: `target_id`, `certification_profile`,
`run_id`, `outcome` (`CERTIFIED`/`NOT_CERTIFIED`), every stage's
status/detail/artifacts, `run_dir_relative` (a deterministic
`target_id/run_id` string — the real, host-specific absolute path is never
part of this canonical artifact), `certificate_id` (only when
`CERTIFIED`), `failed_stage`/`failure_reason` (only when
`NOT_CERTIFIED`), and `artifact_hashes` (a `sha256:<hex>` digest per
top-level artifact file).

Filenames were chosen to reuse the specifications' own canonical Bundle
Descriptor / Integrity Record / Provenance Record names (MCC-EB-001)
directly, rather than inventing parallel ones.

## Determinism and reproducibility

With an identical `target_id`, `--run-id`, `--timestamp`, and (unchanged)
target implementation, the entire generated artifact tree is
byte-for-byte reproducible, including the Technical Certificate's
signature: the reference pipeline derives its Ed25519 signing key
deterministically from `sha256("mcc-certify:" + target_id + ":" + run_id)`
(see `mcc_certify.pipeline._derive_signing_key`) rather than generating a
random key per run. `certification-result.json` deliberately never records
the run's absolute filesystem path — only `run_dir_relative` — so no
volatile, host-specific value ever appears in a canonical artifact.
`tests/test_mcc_certify_pipeline.py::test_deterministic_repeated_generation_produces_byte_identical_artifacts`
runs the complete pipeline twice and compares every generated artifact's
bytes directly.

## Failure semantics

- The pipeline stages artifacts in a temporary `.tmp-<run-id>-<random>/`
  directory and only atomically renames it to the final `<run-id>/`
  directory after every mandatory stage, including Offline Verification,
  succeeds.
- Any stage failure moves the staging directory to `<run-id>.failed/`
  instead — clearly non-certified, retained for diagnostics, never mistaken
  for a completed run (`verify_certification_run` requires all of
  `run-metadata.json`, `technical-certificate.json`,
  `certification-manifest.json`, and `evidence-bundle/` to exist, and an
  interrupted/bare `.tmp-*` staging directory never satisfies that).
- An existing `<run-id>/` directory is never overwritten unless `--force`
  is passed.
- Any Hash Reference mismatch, cross-artifact identity mismatch
  (target/profile/run, checked independently against the run's own
  `run-metadata.json`, not only internally between the Certificate/
  Manifest/Bundle), or tampering anywhere in the chain fails Offline
  Verification, and a Technical Certificate never survives that as a
  reported success.

## Security and trust boundaries

- This package imports **no** runtime-governance internals
  (`mcc_core.gate`, `mcc_core.authority`, `mcc_core.coordinator`,
  `gateway`, `egress_proxy`, `interceptors`) — verified by
  `tests/test_mcc_certify_architecture_guards.py`. Certification is an
  assessment and artifact-issuance system built **above** the existing
  governance runtime; it never mints a Decision Token, evaluates
  operational policy, executes a governed action, bypasses the Execution
  Gate, or mutates the runtime audit chain.
- **Trust Anchor limitation (partially addressed by PR #68):** MCC-TC-001
  Section 16.2 explicitly leaves Trust Anchor distribution out of its own
  normative scope. This pipeline's *default* (fixture) path still derives
  its signing key deterministically and proves only internal
  self-consistency, not independent issuer attestation. PR #68 adds an
  explicit, optional **official mode** (`--issuer-config` /
  `--signing-key` / `--trust-store` / `--publication-dir`) with a real
  Issuer Identity, an offline Trust Store, a pluggable
  `SigningKeyProvider` (a local-file provider is included; no cloud
  KMS/HSM/Vault yet), a static Publication mechanism, and trusted offline
  verification against an explicit trust-anchor set — see
  [`CERTIFICATION_TRUST_AND_PUBLICATION.md`](CERTIFICATION_TRUST_AND_PUBLICATION.md).
  Trust Store *distribution* to verifiers remains manual/out-of-band, and
  no official reference-ecosystem certificate has been issued yet.
- No revocation registry is wired into this pipeline; `mcc_evidence`'s
  Wave C `RevocationRegistry` exists and is reused as an empty registry for
  every verification in this PR (no certificate issued by this pipeline is
  ever revoked here).

## Current limitations

- **No official reference-ecosystem certificate has been issued yet.** As
  of PR #69, `generic-http`/`langgraph`/`crewai`/`autogen`/`voltagent` are
  real, registered Certification Targets wired to their actual PR #48
  adapters (see
  [`CERTIFICATION_FIVE_ECOSYSTEMS.md`](CERTIFICATION_FIVE_ECOSYSTEMS.md)),
  but every certificate produced so far is signed by a disclosed,
  non-production CI candidate issuer — OFFICIAL SIGNING IS PENDING a real,
  separately-held production Issuer key.
- Trust Anchor / production key management: PR #68 adds an explicit,
  optional official mode (Issuer Identity, Trust Store, Signing-Key
  Provider) — see
  [`CERTIFICATION_TRUST_AND_PUBLICATION.md`](CERTIFICATION_TRUST_AND_PUBLICATION.md).
  Trust Store distribution to verifiers remains manual/out-of-band, and no
  cloud KMS/HSM/Vault-backed signing-key provider exists yet.
- CP-001 §9.8 Publication: PR #68 adds a static, offline Publication
  Record/Index mechanism (see the same document) — writing to
  `--output`/`--publication-dir` remains the full extent of "publication";
  there is still no hosted registry or network-based distribution service.
- The Conformance Run stage's requirement set, for `reference-fixture`, is
  still a small, fixed, self-referential set (4 checks) intrinsic to the
  fixture itself. PR #69 wires a real, target-specific requirement set
  (the seven common governance scenarios + capability-profile validation +
  provenance, ~11 checks) against the five real ecosystems' actual
  behavior through their real adapters — see
  [`CERTIFICATION_FIVE_ECOSYSTEMS.md`](CERTIFICATION_FIVE_ECOSYSTEMS.md).
