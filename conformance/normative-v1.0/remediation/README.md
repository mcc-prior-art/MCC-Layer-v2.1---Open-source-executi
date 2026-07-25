# Normative v1.0 Conformance Remediation Waves

Each remediation wave selects a bounded subset of `GAP`/`PARTIAL`
requirements from `conformance/normative-v1.0/requirements.json`, implements
the minimal corrections needed to move them to `CONFORMANT`, and records the
result here as `wave-<n>-<name>-scope-manifest.{json,md}`.

A wave manifest is required even when the wave's proposed scope turns out to
have no eligible requirements — see `wave-1-execution-boundary-scope-manifest.md`
for why Wave 1 could not select anything, and why fabricating a selection
would have misrepresented conformance rather than establishing it.

## Waves

| Wave | Name | Selected requirements | Outcome |
|---|---|---|---|
| 1 | Execution Boundary | 0 | Blocked — target vocabulary is explicitly out of scope for all four Normative v1.0 specifications. Also documents two independent findings (extraction coverage gap; disconnected but real Integration Contract coverage) and three dependency-ordered candidate waves for future work. See manifest. |

## Wave 1 — what it actually is

Wave 1 did not become an implementation wave. It is a **methodology and
specification-coverage gap report**:

- **Verified**: none of the 429 requirements in the current baseline govern
  the runtime execution boundary (Decision Token, Execution Gate, nonce,
  audience, policy-hash, validity window, fail-closed, audit-before-actuation,
  bypass prevention) — this is the correct scope of MCC-CP-001/EB-001/CM-001/
  TC-001, not a defect.
- **Also found**: `src/mcc_conformance/extract.py` never extracted 391
  MUST/SHALL-class lines (vs. 429 currently in the baseline) because of how
  it treats H1 sections that already contain a canonical Invariants block.
  Documented, not corrected, in this PR.
- **Also found**: `docs/INTEGRATION_CONTRACT.md` (already `Status: Normative`,
  v1.0) already normatively covers the entire execution-boundary vocabulary,
  with real conformance evidence (`src/mcc_compliance/vectors/v1/manifest.json`,
  `certifications/manifest.json`, `tests/test_compliance_suite.py`) — it is
  simply disconnected from this four-spec program (no cross-references,
  incompatible identifier scheme, not in `extract.py`'s `SPEC_FILES`).
- **Not decided by this PR**: whether to register/reconcile the Integration
  Contract under a new identifier (e.g. `MCC-RG-001`) or extend the
  extractor to ingest it directly.
- **Not implemented by this PR**: three dependency-ordered candidate waves
  (A: Evidence Bundle Structure + Hash Reference alignment; B: Evidence
  Bundle Reference in the Certification Manifest; C: Technical Certificate
  required fields/model) for genuinely in-scope MCC-EB-001/CM-001/TC-001
  findings, recorded as a starting point for future implementation PRs.

See `wave-1-execution-boundary-scope-manifest.md` for the full analysis.
