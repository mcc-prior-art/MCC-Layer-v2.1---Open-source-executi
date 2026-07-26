# Wave C Scope Manifest — Technical Certificate

Machine-readable form: [`wave-c-technical-certificate-scope-manifest.json`](./wave-c-technical-certificate-scope-manifest.json).
Deterministic evidence: [`wave-c-evidence.json`](./wave-c-evidence.json)
(regenerate with `PYTHONPATH=src python3 conformance/normative-v1.0/remediation/generate_wave_c_evidence.py`).

## Objective

Implement the MCC-TC-001 Technical Certificate model — a minimal, real,
cryptographically and structurally bound Technical Certificate producer and
fail-closed verifier — reusing Wave A's Hash Reference / Evidence Bundle
verifier and Wave B's Certification Manifest / Evidence Bundle Reference
verifier unchanged, so the full transitive verification chain **Evidence
Bundle → Certification Manifest → Technical Certificate** is genuinely
provable end to end, without inventing a parallel PKI/CA system, a runtime
revocation service, or a second Hash Reference / signing implementation.

## Selected requirement IDs (73, all promoted `CONFORMANT`)

Full per-requirement detail (exact obligation, source span, implementation
location, proving tests, deterministic evidence pointer) is in the JSON
manifest. Summarized by category:

| Category (source section) | IDs | Count | Before |
|---|---|---|---|
| 3. Certificate Model | `TC-MODEL-001..004` | 4 | PARTIAL |
| 4. Certificate Schema | `TC-SCHEMA-001..005` | 5 | PARTIAL |
| 5. Certificate Identity | `TC-ID-001..003` | 3 | PARTIAL |
| 6. Required Fields | `TC-RFLD-001..006` | 6 | PARTIAL |
| 7. Optional Fields | `TC-OPTF-001..003` | 3 | GAP |
| 8. Subject Identification | `TC-SUBJ-001` (only) | 1 | PARTIAL |
| 9. Certification Result Representation | `TC-RES-001, TC-RES-003` | 2 | PARTIAL |
| 10. Issuer Information | `TC-ISS-001..003` | 3 | PARTIAL |
| 11. Validity Period | `TC-VALID-001..004` | 4 | PARTIAL |
| 12. Revocation Model | `TC-REV-001..006` | 6 | PARTIAL |
| 13. Cryptographic Integrity | `TC-HASH-001..003` | 3 | PARTIAL |
| 14. Signature Requirements | `TC-SIG-001..005` | 5 | PARTIAL |
| 15. Verification Procedure | `TC-VERIFY-001..006` | 6 | PARTIAL |
| 16. Trust Model | `TC-TRUST-001..004` | 4 | PARTIAL |
| 17. Compatibility | `TC-COMPAT-001..004` | 4 | PARTIAL |
| 18. Versioning | `TC-VSN-001..004` | 4 | PARTIAL |
| 19. Security Considerations | `TC-SEC-001..005` | 5 | PARTIAL |
| 21. Conformance Requirements | `TC-CONF-001..005` | 5 | GAP |
| **Total** | | **73** | |

## Excluded candidates (7) — genuine dependency/scope gaps, not oversights

| ID | Reason |
|---|---|
| `TC-SUBJ-002` | Requires cross-checking the Certificate's Subject against the referenced Certification Manifest's Subject. Wave B's minimal `CM001Manifest` (PR #64) carries **no Certification Metadata at all** — no `subject_id` field exists on a Manifest to check against. |
| `TC-SUBJ-003` | Same dependency gap as `TC-SUBJ-002` (the mismatch-detection half of the same requirement pair). |
| `TC-RES-002` | Requires cross-checking the Certificate's certification result against the referenced Manifest's own result field. `CM001Manifest` carries no result/decision field at all (deliberately deferred by Wave B — see its scope manifest's "Manifest boundary — explicitly deferred" section). |
| `TC-EXT-001` | No extension-declaration mechanism exists anywhere in this repository, for any of the four Normative v1.0 specifications (cross-cutting `RULES` entry in `assess.py` already covers this — unchanged by this wave). |
| `TC-EXT-002` | Same — extension content coverage by the Signature has no extension content to cover. |
| `TC-EXT-003` | Same — no extension points exist to constrain. |
| `TC-EXT-004` | Same — no unrecognized-extension-ignoring behavior exists because no extension mechanism exists. |

`TC-SUBJ-001` (identify exactly one Subject) and `TC-RES-001`/`TC-RES-003`
(result present/PASS; certified profiles limited to those verified) remain
**included** — they are fully self-contained on the Certificate side and do
not depend on the excluded Manifest-side fields.

`TC-RID-001..004` (Requirement Identifier Registry) are **not** candidates
at all — they were already `NOT_APPLICABLE` before this wave, consistent
with `EB-RID`/`CM-RID` in Waves A/B, and remain untouched.

## Architecture

New module `src/mcc_evidence/tc001_certificate.py` (still inside the
existing `mcc_evidence` package — no second Hash Reference type, no second
Evidence Bundle or Certification Manifest model, no duplicate verifier, no
parallel signing/trust/revocation system):

- `ManifestReference` / `CertEvidenceBundleReference` — minimal reference
  containers (id, schema version, one `HashReference`), the same design
  pattern Wave B used for `EvidenceBundleReference`, reusing Wave A's
  `HashReference` directly.
- `TechnicalCertificate` — the closed-field-set Certificate document
  (Section 4.2); `from_dict` performs Structural Verification (Section
  15.2), rejecting any missing Required Field, undeclared field, or
  type-ambiguous value.
- `build_technical_certificate` — the producer. Fails closed unless the
  referenced Certification Manifest is itself independently verifiable
  (reuses `verify_cm001_manifest` unmodified) **and** the Certificate's own
  direct Evidence Bundle Reference agrees with the Manifest's primary
  reference — checked *before* signing (TC-CONF-005).
- `sign_technical_certificate` / `verify_technical_certificate` — signs and
  verifies via `mcc_core.signing.SigningKey` / `verify_token` (Ed25519)
  unchanged; `verify_technical_certificate` implements the complete,
  ordered Section 15 procedure (structural → signature → manifest
  reference → evidence bundle reference consistency → subject/result
  self-consistency → validity/revocation), fail-closed at every step.
- `TrustAnchor` / `TrustAnchorRegistry` — a Technical-Certificate-scoped
  trust set (Section 16), deliberately **not** `gateway.trust.TrustSet`:
  MCC-TC-001 Section 3.4 draws Technical Certificates as a distinct trust
  domain from MCC-Core runtime governance, and this module imports nothing
  from `gateway`, `mcc_core.gate`, or `mcc_core.authority`.
  `revoke_key` supports rotation/revocation without erasing history.
- `RevocationRecord` / `RevocationRegistry` — an in-memory implementation of
  exactly the normative revocation content and effect Section 12 requires;
  Section 12.6 explicitly declines to mandate a specific registry
  technology, so no Redis-backed or otherwise durable backend is
  introduced (a legitimate, separate future extension).
- `CertificateIdRegistry` — enforces certificate-identifier
  non-reuse (Section 5.3) within a single producer process; true
  cross-process global uniqueness is a documented, out-of-scope deployment
  concern.

## Certificate boundary — explicitly deferred

This wave implements the Technical Certificate model, schema, signature,
trust, revocation, and verification procedure to the extent genuinely
supportable given what Waves A and B built. It does **not** implement: a
PKI/CA issuance ceremony, key-management infrastructure, a persistent or
distributed Revocation Registry / Trust Anchor distribution mechanism, the
Extension Model, or Manifest-side Certification Metadata (Subject/Result)
that a future Wave D-style extension to `CM001Manifest` could unlock —
see "Excluded candidates" above and the JSON manifest's
`not_implemented_in_this_pr`.

## Global status delta

| Metric | Before | After |
|---|---|---|
| `CONFORMANT` | 18 | **91** |
| `PARTIAL` | 592 | 527 |
| `GAP` | 110 | 102 |
| `NOT_APPLICABLE` | 90 | 90 |
| Total | 810 | 810 |

No transition occurred outside the 73 selected IDs — verified directly
against every other requirement sharing these MCC-TC-001 categories: the
near-duplicate derived prose in the same sections, the 7 explicitly
excluded IDs, and `TC-RID-001..004`/`TC-EXT-001..004` all remain at their
pre-existing status. Waves A and B's own 18 promoted requirements and their
evidence linkage remain untouched.

## Explicitly not implemented in this PR

`TC-SUBJ-002/003`, `TC-RES-002` (Manifest-side cross-checks pending future
Certification Metadata), `TC-EXT-001..004` (Extension Model, cross-cutting
future work), a persistent/distributed Revocation Registry or Trust Anchor
distribution mechanism, cross-process global certificate-identifier
uniqueness, the executable MCC Normative v1.0 Certification Suite, adapter
certification, `MCC-RG-001` / Integration Contract integration, and any
runtime governance behavior (Decision Token, Execution Gate, Policy Bundle,
Canonical Ingress Pipeline, nonce/replay, audit chain, adapter
authorization) — all unchanged.
