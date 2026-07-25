# Wave A Implementation Report — Evidence Bundle Structure & Hash Reference

PR #63. Scope manifest: [`wave-a-evidence-bundle-scope-manifest.{json,md}`](./wave-a-evidence-bundle-scope-manifest.json).
Deterministic evidence: [`wave-a-evidence.json`](./wave-a-evidence.json).

This is a bounded remediation wave, not a certification and not the
executable Certification Suite. It does not claim MCC-Core is conformant to
MCC-EB-001 or MCC-CM-001 as a whole — only the 13 specific requirement IDs
listed below.

## Selected requirement IDs

`EB-STR-001..005`, `EB-FILE-001..005`, `CM-HASH-001`, `CM-HASH-002`,
`CM-HASH-004` — 13 total, all promoted `PARTIAL` → `CONFORMANT`.

## Excluded candidate

`CM-HASH-003` ("Every Evidence Bundle Reference MUST include at least one
Hash Reference") depends on the Evidence Bundle Reference object MCC-CM-001
§14 defines (`CM-EBREF-001..004`), which does not exist yet — that is Wave
B's scope (PR #64). Remains `PARTIAL`, unchanged. Full rationale in the
scope manifest.

## Existing implementation reused

- `mcc_core.signing.canonical_bytes` / `sha256_hex` — the same canonical
  serialization and digest primitives used everywhere else in this
  repository; no cryptographic code was duplicated.
- `src/mcc_evidence/verify.py`'s `_Reader` (directory/`.tar.gz` reader) —
  imported and reused directly by the new verifier, not reimplemented.
- The existing deterministic archive-writing pattern (`mtime=0`, sorted
  member order) from `src/mcc_evidence/export.py`.
- The existing `CheckResult`/`CheckStatus` structured-reporting pair from
  `src/mcc_evidence/schema.py`.

## Production changes

Four new modules, all inside the existing `src/mcc_evidence/` package —
**no second Evidence Bundle package was created**:

- `hash_reference.py` — `HashReference` (digest, algorithm, content_ref),
  `SUPPORTED_HASH_ALGORITHMS = frozenset({"sha256"})`,
  `compute_hash_reference` / `verify_hash_reference`. Reusable, unchanged, by
  a future Wave B.
- `eb001_schema.py` — `EB001_SCHEMA_VERSION = "mcc-eb-001/1"` (distinct from
  the pre-existing `mcc-evidence/1`), fixed filename constants,
  `EB001Status` / `EB001VerificationResult`.
- `eb001_export.py` — `build_eb001_bundle`: writes one Bundle Root (directory
  or `.tar.gz`) containing exactly one Bundle Descriptor, Integrity Record,
  Provenance Record, and Evidence Directory, from the identical in-memory
  file set for both forms.
- `eb001_verify.py` — `verify_eb001_bundle`: fail-closed structural,
  enumeration-completeness, digest, and identity-consistency verification.

`src/mcc_evidence/__init__.py` exports the new public API alongside the
existing one; both schemas coexist and never interpret each other's files
(verified by `test_governance_bundle_is_never_labeled_eb001_valid` and
`test_eb001_bundle_is_never_labeled_governance_bundle_valid`).

## Normative Evidence Bundle structure implemented

```
<Bundle Root>/
  bundle_descriptor.json   (schema_version, bundle_id, cp001_specification_version)
  integrity_record.json    (algorithm, entries: [{path, hash_reference}, ...])
  provenance_record.json   (bundle_id, certification_run_id, cp001_specification_version)
  evidence/
    <Evidence Item files>  (or a single placeholder if the Evidence Directory is empty)
```

Every file except `integrity_record.json` itself is enumerated in it by a
`HashReference`. The Bundle Descriptor/Provenance Record intentionally carry
only the fields their MCC-EB-001 sections (§11.1, §11.3) require for
presence — full §12 Required Metadata (`EB-META-*`) and full §14 Provenance
Requirements (`EB-PROV-*`, if such an ID range exists) are **not** selected
or claimed by this wave.

## Structured Hash Reference model

`{digest: "sha256:<hex>", algorithm: "sha256", content_ref: "<bundle-relative path>"}`.
`SUPPORTED_HASH_ALGORITHMS` is a closed set — currently only `sha256`;
constructing or verifying a reference with any other algorithm fails closed.

## Verifier behavior and fail-closed rejection

`verify_eb001_bundle` returns `EB001Status.VALID` only when every check
passes: schema supported, exactly the four required root entries present
with no duplicates and no unaccounted entries, bundle identity consistent
across all three records, every file enumerated exactly once, every
Hash Reference well-formed/collision-resistant/correctly bound, and every
digest recomputes. Any single failure yields `INVALID` (or
`UNSUPPORTED_SCHEMA` for a schema-version mismatch) — never a partial pass.
40 direct tests in `tests/test_eb001_evidence_bundle.py` and 16 in
`tests/test_hash_reference.py` exercise both the positive and negative
paths (missing/duplicate/unenumerated/tampered/malformed/inconsistent/
unresolved cases).

## Backward compatibility

The pre-existing Governance Evidence Bundle (`schema.py` / `export.py` /
`verify.py`, `BUNDLE_SCHEMA_VERSION = "mcc-evidence/1"`) is **completely
unmodified** — same files, same public behavior, same 56 pre-existing tests
still passing unchanged. The two schemas are mutually exclusive by
construction (different required root filenames), so neither verifier can
ever mistake the other's bundle for its own; this is asserted directly by
test, not merely assumed.

## Conformance status delta

| Metric | Before | After |
|---|---|---|
| `CONFORMANT` | 0 | **13** |
| `PARTIAL` | 606 | 593 |
| `GAP` | 114 | 114 |
| `NOT_APPLICABLE` | 90 | 90 |
| Total | 810 | 810 |

`src/mcc_conformance/assess.py` gained one small, requirement-ID-scoped
addition (`ID_OVERRIDES`), not a category-wide rule change — verified
directly that every other requirement sharing the same three categories
("10. Bundle Directory Structure", "11. Required Files", "13. Hash
References") remains at its pre-existing status
(`tests/test_wave_a_scope_manifest.py::test_no_unexpected_status_transition_outside_selected_scope`).

## Unresolved / remaining limitations

- `CM-HASH-003` remains `PARTIAL` (excluded; depends on Wave B).
- `EB-META-*` (Required Metadata), `EB-PROV-*`/§14 Provenance Requirements,
  and `EB-HASH-*` (Hash and Integrity Model canonical invariants) are not
  claimed by this wave, even though the implementation incidentally
  satisfies much of their spirit — they were not in the approved candidate
  cluster and are left for a future, explicitly-scoped wave to select and
  test directly.
- No CLI subcommand was added for the MCC-EB-001 bundle (no selected
  requirement required one); it is reachable only as a Python API
  (`from mcc_evidence import build_eb001_bundle, verify_eb001_bundle`).

## Reproduction

```bash
PYTHONPATH=src python3 -m pytest tests/test_hash_reference.py tests/test_eb001_evidence_bundle.py tests/test_wave_a_scope_manifest.py -v
PYTHONPATH=src python3 conformance/normative-v1.0/remediation/generate_wave_a_evidence.py
PYTHONPATH=src python3 -m mcc_conformance generate
PYTHONPATH=src python3 -m mcc_conformance validate
PYTHONPATH=src python3 -m pytest tests/ -q
```

## Wave B / Wave C exclusions (explicit)

Not implemented, not started, not claimed by this PR: MCC-CM-001 Evidence
Bundle Reference (`CM-EBREF-*`), the MCC-TC-001 Technical Certificate model
(schema, signature, trust, validity, revocation), the executable MCC
Normative v1.0 Certification Suite, adapter certification, `MCC-RG-001`,
Integration Contract integration, and any runtime governance behavior
(Decision Token, Execution Gate, Policy Bundle, Canonical Ingress Pipeline,
nonce/replay, audit chain, adapter authorization) — all unchanged.
