# Wave B Scope Manifest — Certification Manifest Evidence Bundle Reference

Machine-readable form: [`wave-b-evidence-bundle-reference-scope-manifest.json`](./wave-b-evidence-bundle-reference-scope-manifest.json).
Deterministic evidence: [`wave-b-evidence.json`](./wave-b-evidence.json)
(regenerate with `PYTHONPATH=src python3 conformance/normative-v1.0/remediation/generate_wave_b_evidence.py`).

## Objective

Connect a Certification Manifest to an actual MCC-EB-001 Evidence Bundle
through the exact normative Evidence Bundle Reference model MCC-CM-001
Section 14 defines, reusing Wave A's Evidence Bundle producer/verifier and
structured Hash Reference.

## Selected requirement IDs (5, all promoted `CONFORMANT`)

| ID | Obligation (summary) | Source | Before |
|---|---|---|---|
| `CM-EBREF-001` | Exactly one primary Evidence Bundle Reference | §14.2 / §14.5 | GAP |
| `CM-EBREF-002` | Primary reference includes identifier, Schema Version, Hash Reference | §14.2 / §14.5 | GAP |
| `CM-EBREF-003` | Supplementary references distinguishable from primary | §14.3 / §14.5 | GAP |
| `CM-EBREF-004` | Unverifiable primary reference invalidates the Manifest | §14.4 / §14.5 | GAP |
| `CM-HASH-003` | Every Evidence Bundle Reference has ≥1 Hash Reference | §13.4 / §13.5 | PARTIAL |

No candidate was excluded — all 5 originally-listed IDs exist with
materially matching normative meaning and were fully implementable within
this bounded wave. No requirement outside this list was added as a
dependency. Full per-requirement detail (exact obligation, source span,
reused implementation, production change, tests, evidence pointer,
dependencies, files affected) is in the JSON manifest.

## Architecture

New module `src/mcc_evidence/cm001_manifest.py` (still inside the existing
`mcc_evidence` package — no second Evidence Bundle model, no second
`HashReference` type, no duplicate verifier, no parallel Certification
Manifest subsystem):

- `EvidenceBundleReference(bundle_id, schema_version, hash_references, kind)`
  — reuses Wave A's `HashReference` directly.
- `build_evidence_bundle_reference(bundle_path)` — reads the referenced
  Bundle's own Bundle Descriptor for `bundle_id`/`schema_version` and
  computes one `HashReference` over the Bundle's actual
  `integrity_record.json` bytes (`content_ref` = the Bundle identifier,
  the exact example CM-HASH-001 itself gives).
- `CM001Manifest(primary_evidence_bundle_reference, supplementary_evidence_bundle_references)`
  — the **minimum** Certification Manifest container needed to hold and
  verify Evidence Bundle References. `manifest_schema_version =
  "mcc-cm-001/1"`. A single JSON document, never a directory or archive
  (MCC-CM-001 §9.2).
- `verify_evidence_bundle_reference` / `verify_cm001_manifest` — fail-closed
  verification reusing Wave A's `verify_eb001_bundle` for the referenced
  Bundle's own structural validity, then independently recomputing the
  Hash Reference against the actual `integrity_record.json` content.

The pre-existing `src/mcc_compliance/` certification manifest
(`certifications/manifest.json`) is untouched — it is a different,
Integration-Contract-scoped artifact with no `bundle_id` / `schema_version`
/ Hash Reference concept at all; it is never reinterpreted as an
MCC-CM-001 Manifest (asserted directly by test).

## Manifest boundary — explicitly deferred

This wave implements **only** the Evidence Bundle Reference and the
minimal container to hold it. Explicitly **not** implemented (see
`cm001_manifest.py`'s module docstring): Certification Metadata,
Requirement Results, the overall certification decision/result field, and
every other Manifest Schema field MCC-CM-001 §10-§20 defines beyond §14.
Technical Certificate generation, signing, trust, and the executable
Certification Suite are Wave C / later milestones, not touched here.

## Global status delta

| Metric | Before | After |
|---|---|---|
| `CONFORMANT` | 13 | **18** |
| `PARTIAL` | 593 | 592 |
| `GAP` | 114 | 110 |
| `NOT_APPLICABLE` | 90 | 90 |
| Total | 810 | 810 |

No transition occurred outside the 5 selected IDs — verified directly
against every other requirement sharing the same two categories ("13. Hash
References", "14. Evidence Bundle References"): the near-duplicate derived
prose (`MCC-CM-001-14-EVIDENCE-BUNDLE-REFERENCES-D01..05`, still `GAP`, and
`MCC-CM-001-13-HASH-REFERENCES-D01..04`, still `PARTIAL`) remain at their
pre-existing status.

## Explicitly not implemented in this PR

The complete MCC-CM-001 Certification Manifest, MCC-TC-001 Technical
Certificate (Wave C), the executable MCC Normative v1.0 Certification
Suite, adapter certification, `MCC-RG-001` / Integration Contract
integration, and any runtime governance behavior.
