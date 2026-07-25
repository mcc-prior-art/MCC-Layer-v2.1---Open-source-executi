# Wave B Implementation Report — Certification Manifest Evidence Bundle Reference

PR #64. Scope manifest: [`wave-b-evidence-bundle-reference-scope-manifest.{json,md}`](./wave-b-evidence-bundle-reference-scope-manifest.json).
Deterministic evidence: [`wave-b-evidence.json`](./wave-b-evidence.json).

This is a bounded remediation wave, not a certification and not the
executable Certification Suite. It does not claim MCC-Core is conformant to
MCC-CM-001 as a whole, nor implement the complete Certification Manifest —
only the 5 specific requirement IDs listed below.

## Selected requirement IDs

`CM-EBREF-001..004` (`GAP` → `CONFORMANT`), `CM-HASH-003` (`PARTIAL` →
`CONFORMANT`) — 5 total. No candidate was excluded.

## Existing implementation reused

- `src/mcc_evidence/hash_reference.py` (`HashReference`,
  `compute_hash_reference`, `verify_hash_reference`) — Wave A, unchanged,
  used directly.
- `src/mcc_evidence/eb001_schema.py` (`BUNDLE_DESCRIPTOR_NAME`,
  `INTEGRITY_RECORD_NAME`) and `eb001_verify.py:verify_eb001_bundle` — Wave
  A, unchanged, used directly to validate the referenced Bundle's own
  structure before trusting anything it contains.

## Production changes

One new module, `src/mcc_evidence/cm001_manifest.py`, inside the existing
`src/mcc_evidence/` package — **no second Evidence Bundle model, no second
Hash Reference type, no parallel Certification Manifest subsystem, no
duplicate verifier**:

- `EvidenceBundleReference(bundle_id, schema_version, hash_references, kind)`.
- `build_evidence_bundle_reference(bundle_path)` — reads the target
  Bundle's own Bundle Descriptor for `bundle_id`/`schema_version` and
  computes one `HashReference` over the Bundle's actual
  `integrity_record.json` bytes, with `content_ref` set to the Bundle
  identifier (the literal example MCC-CM-001's own CM-HASH-001 gives for
  what a Hash Reference's referenced content may be).
- `CM001Manifest(primary_evidence_bundle_reference,
  supplementary_evidence_bundle_references)` — the minimum container;
  written as one JSON document via `write_cm001_manifest`
  (`manifest_schema_version = "mcc-cm-001/1"`), never a directory or
  archive (MCC-CM-001 §9.2).
- `build_cm001_manifest(primary_bundle_path, supplementary_bundle_paths=())`
  — fails closed (raises `IncompleteCM001ManifestError`) if a supplementary
  reference is indistinguishable from (shares the `bundle_id` of) the
  primary, or duplicates another supplementary reference.
- `verify_evidence_bundle_reference` / `verify_cm001_manifest` — fail-closed:
  the referenced Bundle must exist, be structurally valid
  (`verify_eb001_bundle`), match the declared `bundle_id` and
  `schema_version`, and its actual `integrity_record.json` bytes must
  recompute to the declared Hash Reference's digest. Any single failure
  invalidates the whole Manifest (`CM-EBREF-004`), regardless of
  supplementary references.

`src/mcc_evidence/__init__.py` exports the new public API alongside the
existing two schemas.

## Evidence Bundle Reference model

```json
{
  "bundle_id": "wave-b-evidence-bundle-primary",
  "schema_version": "mcc-eb-001/1",
  "hash_references": [{"digest": "sha256:...", "algorithm": "sha256", "content_ref": "wave-b-evidence-bundle-primary"}],
  "kind": "primary"
}
```

No field beyond what MCC-CM-001 §14.2 requires was invented. `kind` is an
explicit, non-normative bookkeeping tag distinguishing primary from
supplementary storage — the normative distinguishability requirement
(`CM-EBREF-003`) is additionally enforced semantically:
`_validate_distinguishable` rejects a supplementary reference sharing the
primary's `bundle_id`.

## Manifest boundary — explicitly deferred

Only `manifest_schema_version`, `primary_evidence_bundle_reference`, and
`supplementary_evidence_bundle_references` exist on `CM001Manifest`.
**Not implemented**: Certification Metadata (§15), Requirement Results,
Manifest Schema fields beyond §14, the overall certification
decision/result field, Technical Certificate generation, signing, trust,
and the executable Certification Suite.

## Verification and fail-closed behavior

`verify_cm001_manifest` returns `VALID` only when the primary reference's
`verify_evidence_bundle_reference` passes every check (bundle resolves,
bundle structurally valid, `bundle_id` matches, `schema_version` matches,
Hash Reference well-formed/collision-resistant/correctly bound, digest
recomputes against the actual Integrity Record) and every supplied
supplementary reference (if any) also passes. A tampered, substituted,
regenerated-with-different-content, or unresolved bundle is rejected —
verified directly, including the subtle case where the referenced bundle
is *independently* re-verified as a valid MCC-EB-001 Bundle on its own but
its Integrity Record content differs from what the reference was created
against (`test_post_reference_bundle_regeneration_with_different_content_rejected`).

## Backward compatibility

`src/mcc_compliance/` and `certifications/manifest.json` (the
Integration-Contract-scoped certification manifest) are **completely
untouched** — different fields entirely (`adapter_name`, `contract_version`,
`scenarios`, no `bundle_id`/`schema_version`/Hash Reference concept). Two
tests assert the legacy manifest is never accepted as an MCC-CM-001
`CM001Manifest` and vice versa.

## Direct requirement-linked tests

42 new tests in `tests/test_cm001_evidence_bundle_reference.py`, covering
valid creation/verification, correct/incorrect Bundle ID and Schema
Version, Hash Reference presence/malformation/algorithm/digest-mismatch,
content-pointer binding, missing/structurally-invalid/substituted/tampered
referenced bundles, primary-invalidates-whole-Manifest, supplementary
distinguishability and duplicate rejection, determinism (creation,
serialization, verification), and legacy-manifest non-interference.

## Deterministic evidence

`conformance/normative-v1.0/remediation/generate_wave_b_evidence.py`
produces `wave-b-evidence.json` from fixed literal fixtures — byte-identical
across runs, no host-specific paths. Each of the 5 records identifies:
requirement ID, specification, source section, implementation location,
proving tests, input fixture, referenced Evidence Bundle/Bundle ID/schema
version/Hash Reference, expected/actual result, verification outcome,
rejection reason (negative cases), and the reproduction command.

## Conformance status delta

| Metric | Before | After |
|---|---|---|
| `CONFORMANT` | 13 | **18** |
| `PARTIAL` | 593 | 592 |
| `GAP` | 114 | 110 |
| `NOT_APPLICABLE` | 90 | 90 |
| Total | 810 | 810 |

`src/mcc_conformance/assess.py` gained 5 more requirement-ID-scoped
`ID_OVERRIDES` entries, not a category-wide rule change — verified directly
that the near-duplicate derived prose in the same two categories
(`MCC-CM-001-14-EVIDENCE-BUNDLE-REFERENCES-D01..05`, still `GAP`, and
`MCC-CM-001-13-HASH-REFERENCES-D01..04`, still `PARTIAL`) and Wave A's own
13 requirements remain exactly at their expected status
(`tests/test_wave_b_scope_manifest.py`,
`tests/test_wave_a_scope_manifest.py`).

## Requirement transition table

| ID | Before | After |
|---|---|---|
| `CM-EBREF-001` | GAP | CONFORMANT |
| `CM-EBREF-002` | GAP | CONFORMANT |
| `CM-EBREF-003` | GAP | CONFORMANT |
| `CM-EBREF-004` | GAP | CONFORMANT |
| `CM-HASH-003` | PARTIAL | CONFORMANT |

## Unresolved / remaining limitations

None among the 5 selected. The complete Certification Manifest (metadata,
requirement results, certification decision) remains out of scope, deferred
explicitly, not left unresolved within this wave's scope.

## Reproduction

```bash
PYTHONPATH=src python3 -m pytest tests/test_cm001_evidence_bundle_reference.py tests/test_wave_b_scope_manifest.py tests/test_wave_a_scope_manifest.py -v
PYTHONPATH=src python3 conformance/normative-v1.0/remediation/generate_wave_b_evidence.py
PYTHONPATH=src python3 -m mcc_conformance generate
PYTHONPATH=src python3 -m mcc_conformance validate
PYTHONPATH=src python3 -m pytest tests/ -q
```

## Wave C exclusion (explicit)

Not implemented, not started, not claimed by this PR: the MCC-TC-001
Technical Certificate model (schema, signature, trust, validity,
revocation), the executable MCC Normative v1.0 Certification Suite,
adapter certification, `MCC-RG-001`, Integration Contract integration, and
any runtime governance behavior (Decision Token, Execution Gate, Policy
Bundle, Canonical Ingress Pipeline, nonce/replay, audit chain, adapter
authorization) — all unchanged.
