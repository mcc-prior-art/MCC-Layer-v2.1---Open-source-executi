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
| A | Evidence Bundle Structure & Hash Reference | 13 (of 14 candidates; `CM-HASH-003` excluded — depended on Wave B at the time) | **Implemented.** `EB-STR-001..005`, `EB-FILE-001..005`, `CM-HASH-001/002/004` promoted `PARTIAL` → `CONFORMANT` via a real, tested extension of `src/mcc_evidence/` (PR #63). Global `CONFORMANT`: 0 → 13. See scope manifest and implementation report. |
| B | Certification Manifest Evidence Bundle Reference | 5 (of 5 candidates; none excluded) | **Implemented.** `CM-EBREF-001..004` (`GAP`→`CONFORMANT`) and `CM-HASH-003` (`PARTIAL`→`CONFORMANT`, previously excluded from Wave A — its Wave A dependency now exists) via `src/mcc_evidence/cm001_manifest.py` (PR #64), reusing Wave A's Evidence Bundle producer/verifier and Hash Reference directly. Global `CONFORMANT`: 13 → 18. See scope manifest and implementation report. |

## Wave A — status

Implemented in PR #63. `src/mcc_evidence/` gained `hash_reference.py`,
`eb001_schema.py`, `eb001_export.py`, `eb001_verify.py` (a second,
explicitly-versioned bundle schema alongside the pre-existing Governance
Evidence Bundle, coexisting without interpreting each other's files) and 56
new direct tests. `CM-HASH-003` was evaluated and explicitly excluded at
the time (depended on the not-yet-built Evidence Bundle Reference). No
other requirement sharing these categories was affected. See
`wave-a-evidence-bundle-scope-manifest.{json,md}` and
`wave-a-evidence-bundle-implementation-report.md` for the full record.

## Wave B — status

Implemented in PR #64. `src/mcc_evidence/` gained `cm001_manifest.py`: the
minimum Certification Manifest container needed to hold and verify an
Evidence Bundle Reference (`EvidenceBundleReference`, `CM001Manifest`,
`build_cm001_manifest`, `verify_cm001_manifest`), reusing Wave A's
`HashReference` and `verify_eb001_bundle` directly — no second Evidence
Bundle model, no second Hash Reference type, no duplicate verifier. 42 new
direct tests. `CM-HASH-003`, excluded from Wave A because its dependency
(the Evidence Bundle Reference) did not exist yet, is now promoted — this
is the anticipated, planned progression, not scope creep. See
`wave-b-evidence-bundle-reference-scope-manifest.{json,md}` and
`wave-b-evidence-bundle-reference-implementation-report.md` for the full
record.

Wave C (Technical Certificate) remains not started.

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
