# Wave C Implementation Report — Technical Certificate

PR #65. Scope manifest: [`wave-c-technical-certificate-scope-manifest.{json,md}`](./wave-c-technical-certificate-scope-manifest.json).
Deterministic evidence: [`wave-c-evidence.json`](./wave-c-evidence.json).

This is a bounded remediation wave, not a certification and not the
executable Certification Suite. It does not claim MCC-Core is conformant to
MCC-TC-001 as a whole, nor implement a full PKI/CA or key-management
system — only the 73 specific requirement IDs listed below.

## Selected requirement IDs

73 of 80 genuine MCC-TC-001 candidates (`TC-RID-001..004` were already
`NOT_APPLICABLE` before this wave and are not candidates), spanning every
non-excluded category: `TC-MODEL-001..004`, `TC-SCHEMA-001..005`,
`TC-ID-001..003`, `TC-RFLD-001..006`, `TC-OPTF-001..003`, `TC-SUBJ-001`,
`TC-RES-001`, `TC-RES-003`, `TC-ISS-001..003`, `TC-VALID-001..004`,
`TC-REV-001..006`, `TC-HASH-001..003`, `TC-SIG-001..005`,
`TC-VERIFY-001..006`, `TC-TRUST-001..004`, `TC-COMPAT-001..004`,
`TC-VSN-001..004`, `TC-SEC-001..005`, `TC-CONF-001..005` — all promoted
`PARTIAL`/`GAP` → `CONFORMANT`.

## Excluded candidates (7)

- `TC-SUBJ-002`, `TC-SUBJ-003` — require cross-checking the Certificate's
  Subject against the referenced Certification Manifest's Subject. Wave
  B's minimal `CM001Manifest` (PR #64) carries no Certification Metadata
  at all — no `subject_id` field exists on a Manifest to check against.
- `TC-RES-002` — same dependency gap, for the certification result field.
- `TC-EXT-001..004` — no extension-declaration mechanism exists anywhere in
  this repository, for any of the four Normative v1.0 specifications (the
  pre-existing cross-cutting `RULES` entry in `assess.py` already covers
  this, unchanged).

All 7 remain at their pre-existing status (`PARTIAL` for the `TC-SUBJ`/
`TC-RES` pair, `GAP` for `TC-EXT-*`). Full rationale in the scope manifest.

## Existing implementation reused

- `mcc_core.signing.SigningKey` / `verify_token` / `canonical_bytes` —
  Ed25519 signing and verification, unchanged. No second signature
  implementation.
- `src/mcc_evidence/hash_reference.py` (`HashReference`,
  `compute_hash_reference`, `verify_hash_reference`) — Waves A/B, unchanged.
- `src/mcc_evidence/cm001_manifest.py` (`read_cm001_manifest`,
  `verify_cm001_manifest`, `verify_evidence_bundle_reference`,
  `EvidenceBundleReference`) — Wave B, unchanged, used directly to resolve
  and verify the referenced Certification Manifest and, transitively, its
  Evidence Bundle Reference.
- `src/mcc_evidence/eb001_schema.py` / `eb001_verify.py` — Wave A, unchanged.

## Production changes

One new module, `src/mcc_evidence/tc001_certificate.py`, inside the
existing `src/mcc_evidence/` package — **no second Hash Reference type, no
second Evidence Bundle or Certification Manifest model, no duplicate
verifier, no parallel PKI/CA or signing implementation**:

- `ManifestReference` / `CertEvidenceBundleReference` — minimal reference
  containers (identifier, schema version, one `HashReference`), the same
  design pattern Wave B used for `EvidenceBundleReference`.
- `TechnicalCertificate` — a closed-field-set Certificate document (Section
  4.2); `from_dict` performs Structural Verification (Section 15.2),
  rejecting any missing Required Field, undeclared field, or
  type-ambiguous value.
- `build_technical_certificate` — the producer. Refuses to issue
  (`IncompleteTC001CertificateError`) unless: the referenced Certification
  Manifest is itself independently verifiable (`verify_cm001_manifest`
  reused unmodified); the Certificate's direct Evidence Bundle Reference
  and the Manifest's primary reference identify the same Evidence Bundle,
  checked *before* signing (TC-CONF-005 / Section 3.3); and
  `certified_capability_profiles` is non-empty. There is no
  `certification_result` parameter — a FAIL Certificate cannot be
  constructed (TC-CONF-002).
- `sign_technical_certificate` / `write_tc001_certificate` /
  `read_tc001_certificate` — signs via `SigningKey.sign_token` (Ed25519)
  over `unsigned_dict()` (the Canonical Form excluding `kid`/`sig`); writes
  one JSON document, never a directory or archive.
- `verify_technical_certificate` — the complete, ordered Section 15
  procedure: **structural → signature → manifest reference → evidence
  bundle reference consistency → subject/result self-consistency →
  validity/revocation**, fail-closed at every step (`TC001Status.VALID` /
  `INVALID` / `UNSUPPORTED_SCHEMA`; never a partial pass).
- `TrustAnchor` / `TrustAnchorRegistry` (Section 16) — a
  Technical-Certificate-scoped trust set holding `{kid: (issuer_id,
  public_key, revoked)}`. Deliberately **not** `gateway.trust.TrustSet`:
  MCC-TC-001 Section 3.4 draws Technical Certificates as a distinct trust
  domain from MCC-Core runtime governance, and this module imports nothing
  from `gateway`, `mcc_core.gate`, or `mcc_core.authority` (asserted
  directly by an AST-based import-graph test). `revoke_key` supports
  rotation/revocation without erasing history (TC-TRUST-003).
- `RevocationRecord` / `RevocationRegistry` (Section 12) — an in-memory
  implementation of exactly the normative revocation content and effect;
  `revoke` refuses a record whose `issuer_id` does not match the
  authorizing Trust Anchor (TC-REV-004). Section 12.6 explicitly declines
  to mandate a specific registry technology, so no Redis-backed or
  otherwise durable backend is introduced — a legitimate, separate future
  extension, exactly as MCC-CM-001's full Certification Metadata remains
  deferred past Wave B.
- `CertificateIdRegistry` (Section 5.3) — enforces certificate
  identifier non-reuse within a single producer process (TC-ID-002/003);
  true cross-process global uniqueness is a documented, out-of-scope
  deployment concern.

`src/mcc_evidence/__init__.py` exports the new public API alongside the
existing two schemas and the Certification Manifest container.

## Transitive verification chain

```
Evidence Bundle (Wave A)
   ↑ Hash Reference (Wave A)
Certification Manifest (Wave B)
   ↑ Hash Reference + direct Evidence Bundle Reference (Wave C)
Technical Certificate (Wave C)
```

`verify_technical_certificate` independently recomputes both bindings
(never trusting a stored "already verified" flag): the Manifest Reference's
Hash Reference against the Manifest's actual bytes, and — via the
Certificate's own direct Evidence Bundle Reference, cross-checked against
the Manifest's primary reference for identity (TC-VERIFY-006) — the
Evidence Bundle Reference's Hash Reference against the Bundle's actual
Integrity Record, reusing Wave B's `verify_evidence_bundle_reference`
directly.

## Verification and fail-closed behavior

Any single failing check — unsupported schema version, structural defect,
unresolvable/revoked signing key, forged or tampered signature, unverifiable
Manifest, mismatched or unverifiable direct Evidence Bundle Reference,
not-yet-valid, expired, or revoked — yields `INVALID` (or
`UNSUPPORTED_SCHEMA`), never a partial pass. 103 direct tests in
`tests/test_tc001_technical_certificate.py`, including 24 numbered negative
scenarios (missing/undeclared fields, non-PASS result, unsupported schema
versions, empty capability profiles, Manifest/Bundle tampering and
substitution after issuance, mismatched Evidence Bundle References, unknown/
revoked signing keys, forged signatures, issuer/Trust-Anchor mismatch,
expired/not-yet-valid validity windows, revoked certificates, reused
certificate identifiers, duplicate Trust Anchor key ids, mismatched
revocation authority, missing Manifest files, re-signing an already-signed
Certificate, and malformed Hash References).

## Backward compatibility

`gateway/trust.py` (`TrustSet`, runtime mandate/approval trust) and any
runtime governance module (`mcc_core.gate`, `mcc_core.authority`,
`mcc_core.coordinator`, `egress_proxy`, `interceptors`) are **completely
untouched** — `tc001_certificate.py` imports none of them, asserted
directly by an AST-based import-graph test
(`test_tc_sec_005_valid_certificate_not_treated_as_runtime_execution_authorization`,
`test_tc001_certificate_module_does_not_import_gateway_trust`). The
pre-existing `src/mcc_compliance/` certification manifest
(`certifications/manifest.json`) remains a different, Integration-Contract
-scoped artifact and is never accepted as a Technical Certificate
(`test_legacy_compliance_manifest_never_accepted_as_a_technical_certificate`).

## Deterministic evidence

`conformance/normative-v1.0/remediation/generate_wave_c_evidence.py`
produces `wave-c-evidence.json` (73 records) from fixed literal fixtures,
including an Ed25519 signing key built from a fixed 32-byte seed (never
`SigningKey.generate()`, which is non-deterministic) — byte-identical
across runs, no host-specific paths. Each record identifies: requirement
ID, source section, implementation location, proving tests, input fixture
(positive or a specific documented negative case), expected/actual result,
verification outcome, and the reproduction command.

## Conformance status delta

| Metric | Before | After |
|---|---|---|
| `CONFORMANT` | 18 | **91** |
| `PARTIAL` | 592 | 527 |
| `GAP` | 110 | 102 |
| `NOT_APPLICABLE` | 90 | 90 |
| Total | 810 | 810 |

`src/mcc_conformance/assess.py` gained 73 more requirement-ID-scoped
`ID_OVERRIDES` entries, not a category-wide rule change — verified
directly that every other MCC-TC-001 requirement outside the 73 selected
and 7 excluded IDs (including the cross-cutting `TC-EXT-*` rule and
`TC-RID-*`, already `NOT_APPLICABLE`) remains at its pre-existing status,
and that Waves A/B's 18 previously-promoted requirements and their
evidence linkage are untouched
(`tests/test_wave_c_scope_manifest.py`, `tests/test_wave_a_scope_manifest.py`,
`tests/test_wave_b_scope_manifest.py`).

## Cross-wave test-design fix (discovered, not introduced, by this PR)

Wave B's `tests/test_wave_b_scope_manifest.py::test_global_conformant_count_includes_wave_a_plus_wave_b`
implicitly assumed Wave B was the final wave — it asserted the *global*
`CONFORMANT` count equaled exactly 18 forever. That assumption broke the
instant this wave legitimately added 73 more `CONFORMANT` requirements,
exactly the same class of pre-existing test-design defect Wave B itself
found and fixed in Wave A's test suite. Fixed narrowly here: the test now
asserts Wave B's 18-requirement floor (`global_status_delta.after`, a fixed
historical fact) and that the real count is `>= 18`, rather than asserting
equality with the current global count — mirroring the identical fix
already applied to Wave A's own test in Wave B. No global conformance
control was weakened: `test_no_unexpected_status_transition_outside_selected_scope`
in both Wave A's and Wave B's suites, and the equivalent new check in Wave
C's own suite, continue to catch any genuinely unexpected promotion.

## Unresolved / remaining limitations

- `TC-SUBJ-002/003`, `TC-RES-002` remain `PARTIAL` (excluded; depend on a
  future Certification Manifest Certification Metadata extension).
- `TC-EXT-001..004` remain `GAP` (excluded; depend on a future,
  cross-cutting Extension Model).
- No persistent/distributed Revocation Registry or Trust Anchor
  distribution/rotation-notification mechanism — MCC-TC-001 explicitly
  declines to mandate one; a Redis-backed or otherwise durable backend
  remains a legitimate, separate future extension.
- `CertificateIdRegistry` enforces non-reuse only within a single
  producer process; true cross-process/cross-issuer global uniqueness is a
  documented, out-of-scope deployment concern.
- No CLI subcommand was added for Technical Certificate issuance/
  verification (no selected requirement required one); reachable only as a
  Python API (`from mcc_evidence import build_technical_certificate,
  verify_technical_certificate, ...`).

## Reproduction

```bash
PYTHONPATH=src python3 -m pytest tests/test_tc001_technical_certificate.py tests/test_wave_c_scope_manifest.py tests/test_wave_a_scope_manifest.py tests/test_wave_b_scope_manifest.py -v
PYTHONPATH=src python3 conformance/normative-v1.0/remediation/generate_wave_c_evidence.py
PYTHONPATH=src python3 -m mcc_conformance generate
PYTHONPATH=src python3 -m mcc_conformance validate
PYTHONPATH=src python3 -m pytest tests/ -q
```

## Explicitly not implemented, not started, not claimed by this PR

A PKI/CA issuance ceremony or key-management infrastructure; a persistent
or distributed Revocation Registry / Trust Anchor distribution mechanism;
the Extension Model (any of the four specifications); Manifest-side
Certification Metadata (Subject/Result); the executable MCC Normative v1.0
Certification Suite; adapter certification; `MCC-RG-001`; Integration
Contract integration; and any runtime governance behavior (Decision Token,
Execution Gate, Policy Bundle, Canonical Ingress Pipeline, nonce/replay,
audit chain, adapter authorization) — all unchanged.
