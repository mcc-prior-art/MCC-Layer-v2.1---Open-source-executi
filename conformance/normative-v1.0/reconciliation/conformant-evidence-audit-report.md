# MCC Normative v1.0 — CONFORMANT Evidence Audit Report

PR #66. Audits every requirement currently marked `CONFORMANT` in
`conformance/normative-v1.0/requirements.json` (91 total, unchanged in
count and status by this PR — see the Status Reconciliation Report).

## Audit criteria applied to every CONFORMANT requirement

1. Exact normative provenance (`specification_id`, `section`, `source_line`
   all point at a real, currently-existing line in the actual specification
   file).
2. A concrete production implementation location
   (`implementation_references`, at least one entry, path verified to
   exist).
3. At least one direct test reference (`test_references`, path verified to
   exist).
4. A deterministic, reproducible evidence record (`evidence_references`,
   path verified to exist, and the evidence file's own `records` array
   verified to actually contain a record for that exact `requirement_id` —
   not merely citing the file in general).
5. No dependency on a missing or unverifiable artifact — every wave
   evidence record's `proving_tests` pytest node ids verified to resolve to
   a real `def` in the referenced test file (new in this PR:
   `validate_evidence_test_nodes`; see Finding 1 in the Coverage
   Reconciliation Report for the one defect this caught and fixed).
6. No reliance solely on the full-suite pass count — every citation above
   is to a specific file (and, via the wave evidence record, a specific
   test function), not to "the suite passed."
7. No reliance solely on documentation — every CONFORMANT requirement has a
   non-empty `implementation_references` pointing at production code, not
   only a doc file.
8. No reliance solely on a broad test file that does not directly assert
   the requirement — every requirement's evidence record names the
   specific proving test(s), not merely "this test file exists."

## Result: 91 of 91 CONFORMANT requirements pass every criterion above

No requirement was downgraded. No requirement's status changed. The full
per-requirement audit trail already exists, in normative-source-code form,
as:

- `tests/test_normative_coverage_reconciliation.py::test_every_conformant_requirements_evidence_file_contains_a_matching_record` (criterion 4)
- `tests/test_normative_coverage_reconciliation.py::test_no_wave_evidence_record_is_orphaned_from_the_registry` (criteria 4, 6)
- `tests/test_normative_coverage_reconciliation.py::test_no_conformant_requirement_lacks_implementation_test_or_evidence_references` (criteria 2, 3, 4)
- `tests/test_normative_coverage_reconciliation.py::test_referenced_implementation_and_test_file_paths_all_exist_in_real_registry` (criteria 2, 3, 4 — path existence)
- `tests/test_normative_coverage_reconciliation.py::test_validate_evidence_test_nodes_passes_on_the_real_committed_evidence` (criterion 5)
- `src/mcc_conformance/validate.py:validate_requirements` (criteria 2, 3, 4 — CONFORMANT reference presence, now including `evidence_references`)

## Breakdown by remediation wave

| Wave | PR | Requirements | Implementation | Test file | Evidence file |
|---|---|---|---|---|---|
| A | #63 | 13 (`EB-STR-001..005`, `EB-FILE-001..005`, `CM-HASH-001/002/004`) | `src/mcc_evidence/{eb001_schema,eb001_export,eb001_verify}.py`, `hash_reference.py` | `tests/test_eb001_evidence_bundle.py`, `tests/test_hash_reference.py` | `wave-a-evidence.json` |
| B | #64 | 5 (`CM-EBREF-001..004`, `CM-HASH-003`) | `src/mcc_evidence/cm001_manifest.py` | `tests/test_cm001_evidence_bundle_reference.py` | `wave-b-evidence.json` |
| C | #65 | 73 (`TC-MODEL-*`, `TC-SCHEMA-*`, `TC-ID-*`, `TC-RFLD-*`, `TC-OPTF-*`, `TC-SUBJ-001`, `TC-RES-001/003`, `TC-ISS-*`, `TC-VALID-*`, `TC-REV-*`, `TC-HASH-*`, `TC-SIG-*`, `TC-VERIFY-*`, `TC-TRUST-*`, `TC-COMPAT-*`, `TC-VSN-*`, `TC-SEC-*`, `TC-CONF-*`) | `src/mcc_evidence/tc001_certificate.py` | `tests/test_tc001_technical_certificate.py` | `wave-c-evidence.json` |
| **Total** | | **91** | | | |

## Promoted requirements in this PR

**None.** PR #66 is a reconciliation/audit milestone, not a remediation
wave — it does not select new candidate requirements or move any
requirement's status. See the Status Reconciliation Report for the
before/after totals (identical).

## Downgraded requirements in this PR

**None.** All 91 CONFORMANT requirements passed every audit criterion
above; none lacked sufficient direct evidence.

## Shared-evidence relationships (explicitly preserved, not flattened)

Consistent with the task's instruction that one precise test may
legitimately prove several tightly related normative clauses: several
requirement IDs within a wave cite the same implementation/test file pair
(e.g. all 5 Wave B requirements cite `cm001_manifest.py` /
`test_cm001_evidence_bundle_reference.py`) while each still has its own
distinct entry in that wave's evidence JSON identifying the *specific*
proving test(s) for that exact requirement — this audit confirmed the
distinction is real (verified via `validate_evidence_test_nodes` and the
per-requirement `proving_tests` cross-check above), not a broad aggregate
citation standing in for per-requirement proof.

## Confirmation

Aggregate full-suite pass/fail counts were **not** used as evidence for any
individual requirement's CONFORMANT status, at any point in this audit or
in the pre-existing `assess.py` mechanism it audits. Every CONFORMANT
requirement's status rests on its own named implementation reference, its
own named test reference, and its own named evidence record.
