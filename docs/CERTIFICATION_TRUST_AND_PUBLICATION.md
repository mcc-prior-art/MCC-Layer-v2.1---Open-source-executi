# MCC Certification Trust Anchor, Issuer Key Management & Publication

PR #68. Builds directly on [`CERTIFICATION_PIPELINE.md`](CERTIFICATION_PIPELINE.md)
(PR #67, `mcc_certify`): that pipeline's reference/fixture path derives its
own Ed25519 signing key deterministically from `target_id`/`run_id` and
documented this explicitly as **not** a production trust mechanism (see
that document's "Security and Trust Boundaries"). This PR implements the
missing trust and publication foundation so a *future* milestone can issue
**official** certificates for the five production reference ecosystems
(Generic HTTP, LangGraph, CrewAI, AutoGen, VoltAgent) — **this PR does not
issue any of those certificates itself**. `reference-fixture` remains the
only registered Certification Target.

## Why this is a separate layer, not a Technical Certificate change

MCC-TC-001 defines the normative *concepts* — Issuer Information (Section
10), Signature Requirements (Section 14), and the Trust Model (Section 16:
Trust Anchors, rotation, revocation) — but explicitly leaves their
*persisted, distributable representation* out of its own scope (Section
16.1: "the mechanism by which a Trust Anchor is distributed to verifiers is
outside the scope of this specification"). Grepping all four Normative
v1.0 specifications confirms the literal term "Trust Anchor" occurs **only**
in MCC-TC-001 — zero occurrences in MCC-CP-001, MCC-CM-001, or MCC-EB-001.
CP-001's own Publication text (Sections 8.8/9.8) is similarly minimal:
"Certification outputs MAY be published. Publication SHALL NOT modify
certification results. Published artifacts SHALL remain reproducible." No
format is mandated. This PR implements exactly the smallest, secure,
interoperable, offline contract that fills those two deliberately-open
gaps — no new Technical Certificate field, no new signature algorithm, no
new certification pipeline.

## 1. Issuer Identity (`mcc_certify.issuer`)

A versioned, schema-validated (`mcc-certify-issuer/1`), canonically
serialized record of exactly what MCC-TC-001 Sections 10/14/16 require an
Issuer/Trust Anchor to carry:

```json
{
  "issuer_identity_schema_version": "mcc-certify-issuer/1",
  "issuer_id": "axlogiq-ca-1",
  "display_name": "AXLOGIQ Certification Authority",
  "key_id": "issuer-key-1",
  "signing_algorithm": "Ed25519",
  "public_key_b64": "...",
  "public_key_fingerprint": "sha256:...",
  "valid_from": 1785024000,
  "specification_version": "1.0",
  "created_at": 1785024000,
  "status": "ACTIVE"
}
```

Every field is either supplied explicitly or **independently derived from
the actual public key bytes** — `public_key_fingerprint` is always
recomputed from `public_key_b64` and compared against the declared value;
a mismatch is rejected (`IssuerIdentityError`), never trusted at face
value. Nothing is inferred from a filename, local path, process state, or
private-key contents. `signing_algorithm` is restricted to the same closed
set the Technical Certificate model already enforces
(`SUPPORTED_SIGNATURE_ALGORITHMS = {"Ed25519"}` — never a symmetric-key or
shared-secret signing mechanism).

`IssuerStatus` is a closed set — `ACTIVE` / `REVOKED` — matching exactly
what MCC-TC-001's own Trust Model distinguishes; no additional status is
invented.

## 2. Trust Anchor Model (reused, not duplicated)

This PR does **not** introduce a second Trust Anchor type. The existing
Wave C runtime types (`mcc_evidence.tc001_certificate.TrustAnchor` /
`TrustAnchorRegistry`, from PR #65) are reused unchanged. `IssuerIdentity`
is a richer, persisted, schema-validated *superset* that **converts down**
into that existing runtime type at verification time (see §3). The
verifier (`verify_technical_certificate`) is never modified, forked, or
reimplemented.

## 3. Trust Store (`mcc_certify.trust_store`)

A versioned, canonical, **offline-only** document (`mcc-certify-trust-store/1`)
collecting one or more `IssuerIdentity` records:

```json
{
  "trust_store_schema_version": "mcc-certify-trust-store/1",
  "issuers": [ { "issuer_id": "axlogiq-ca-1", "key_id": "issuer-key-1", ... } ]
}
```

`TrustStore` validation (fail-closed, at construction time) rejects:

- fewer than one Issuer;
- a duplicate `(issuer_id, key_id)` pair;
- a `key_id` bound to two different public keys within the same store
  (an ambiguous, conflicting Trust Anchor);
- an unsupported `trust_store_schema_version`;
- a malformed `IssuerIdentity` entry (propagated from §1's own validation).

`TrustStore.resolve(issuer_id, key_id)` looks up **exactly** that pair —
never by `key_id` alone, so an unknown issuer can never silently match a
`key_id` that happens to exist for a different issuer.

`TrustStore.to_trust_anchor_registry(now)` is the **one** place a Wave C
`TrustAnchor` is ever constructed from a Trust Store, computing effective
revocation independently per entry:

```
effectively_revoked =
    status == REVOKED
    or now < valid_from        # not yet valid
    or (valid_until is not None and now > valid_until)   # expired
```

A Trust Store is always loaded from a local file (`read_trust_store`) —
there is no network client anywhere in this module (verified by both an
AST import guard and a `_NETWORK_MODULES` grep guard in
`tests/test_mcc_certify_trust_publication_guards.py`). MCC-TC-001 Section
16.3's "trust MUST NOT be established dynamically" holds by construction.
A Technical Certificate can never add itself, or any of its own declared
fields, to a Trust Store.

## 4. Issuer Signing-Key Contract (`mcc_certify.signing_provider`)

`SigningKeyProvider` is an abstract boundary between the pipeline and
wherever a real private key actually lives:

```python
class SigningKeyProvider(abc.ABC):
    def get_signing_key(self) -> SigningKey: ...
    def expected_issuer_id(self) -> str: ...
    def expected_key_id(self) -> str: ...
    @property
    def is_fixture(self) -> bool: ...   # False unless explicitly a fixture provider
```

`LocalFileSigningKeyProvider(private_key_path, issuer_identity)` loads a
real Ed25519 private key from a local PEM file and, **at construction
time** (before any certificate is ever built), verifies:

- the key loads as a valid Ed25519 private key (`SigningKey.from_pem_file`);
- its public key bytes exactly match `issuer_identity.resolved_public_key()`;
- its recomputed fingerprint exactly matches `issuer_identity.public_key_fingerprint`.

Any mismatch, missing file, or parse error raises
`SigningKeyProviderError` immediately — a mismatched provider never yields
a usable key. This PR introduces **no** cloud KMS/HSM/Vault integration,
but the abstract interface is designed so a future KMS-backed provider can
be added without changing any caller.

## 5. Fixture vs. Official Mode

`FixtureSigningKeyProvider` wraps PR #67's deterministic
`pipeline._derive_signing_key` unchanged and sets `is_fixture = True`.
`CertificationPipeline.run()` refuses (`signing_provider` stage FAIL) any
official-mode request whose `signing_key_provider.is_fixture` is `True` —
**there is no silent fallback** from a real issuer configuration to
fixture keys.

`CertificationRequest.official_mode` defaults to `False`. Left unset (or
`False`), certification reproduces PR #67's fixture behavior **byte for
byte** — every existing test in `tests/test_mcc_certify_pipeline.py`
continues to pass unmodified, and no new pipeline stage, output field, or
key-derivation path is exercised. Setting `official_mode=True` requires
**all four** of `issuer_identity`, `signing_key_provider`, `trust_store`,
and `publication_dir` — a partially-configured official request fails
closed at the first missing piece (`issuer_config` / `trust_anchor_set` /
`signing_provider` / `signing_key_match` stage, respectively) rather than
silently degrading to fixture behavior.

Official mode adds four preflight validation stages and two additional
pipeline stages (`verify_tc_signature`, `publication_record`) — see
§8 (Atomicity/Failure Semantics) below for the full ordering.

## 6. Publication (`mcc_certify.publication`)

Implements CP-001 §9.8/§8.8 Publication: static, reproducible,
package-testable, independently verifiable, reusing the existing Hash
Reference primitive (`mcc_evidence.hash_reference`) directly — no second
Hash Reference implementation.

**Publication Record** (`mcc-certify-publication-record/1`) — one per
issued certificate:

```json
{
  "publication_record_schema_version": "mcc-certify-publication-record/1",
  "certificate_id": "reference-fixture-official-1-certificate",
  "target_id": "reference-fixture",
  "issuer_id": "axlogiq-ca-1",
  "key_id": "issuer-key-1",
  "certification_manifest_reference": { "digest": "sha256:...", "algorithm": "sha256", "content_ref": "..." },
  "technical_certificate_reference": { "digest": "sha256:...", "algorithm": "sha256", "content_ref": "..." },
  "evidence_bundle_reference": { "digest": "sha256:...", "algorithm": "sha256", "content_ref": "..." },
  "status": "ACTIVE",
  "issuance_timestamp": 1785024000,
  "specification_version": "1.0",
  "artifact_location": "reference-fixture/official-1"
}
```

**Publication Index** (`mcc-certify-publication-index/1`) — a
deterministically-ordered (by `certificate_id`) collection of Publication
Records. `PublicationIndex.add()` is idempotent for a byte-identical
re-publication of the same `certificate_id` (safe to rerun), and raises
`PublicationConflictError` for a *different* record under the same
`certificate_id` — a certificate id is never silently overwritten.

Both the individual record file and the index file are written atomically
(temp file in the same directory + `os.replace`) — a reader never observes
a partially-written document. Publication **never modifies** an
already-issued Technical Certificate or Certification Manifest; it only
reads and hash-references them. There is no hosted registry, server, or
network service anywhere in this module — "publication" means writing a
static JSON document to local disk.

## 7. Offline Trusted Verification (`mcc_certify.verify.verify_certification_run_trusted`)

Extends (never duplicates) the existing offline verifier
(`verify_certification_run`, PR #67) by accepting an **explicit,
externally-supplied Trust Anchor set** instead of re-deriving the same key
the pipeline used:

```python
from mcc_certify import verify_certification_run_trusted, read_trust_store, read_publication_index

report = verify_certification_run_trusted(
    run_dir, trust_store=read_trust_store("trust-store.json"),
    publication_index=read_publication_index("publication-index.json"),
    require_published=True,
)
```

This checks, in one call: Technical Certificate structural validity,
signature verification against the *explicit* Trust Anchor set (not a
re-derived key), Manifest/Evidence-Bundle reference consistency, validity
period, revocation, target/profile/run identity consistency (reusing
`_check_run_identity`), the local `publication-record.json`'s own Hash
References against the run's real artifacts, and — when
`publication_index` is supplied — that the certificate is present in the
index with a Publication Record whose Hash References also verify.
`require_published=True` makes presence in the Publication Index
mandatory, not merely checked-if-present.

A missing or unloadable `trust_store` raises `RunVerificationError`
immediately (fail-closed — there is no default trust). Failure conditions
this function is exercised against (see `tests/test_mcc_certify_pr68.py`):
wrong/substituted trust anchor, tampered certificate, missing publication
entry, revoked/expired/not-yet-valid issuer, and missing run artifacts.

## 8. Atomicity / Failure Semantics (Official Mode)

`CertificationPipeline.run()` enforces this ordering for an official-mode
request — a failure at any step is a fail-closed, non-zero-exit,
diagnosable stage failure, and no step after it ever runs:

1. validate target (`preflight`)
2. validate issuer config (`issuer_config` — `issuer_identity` present)
3. validate trust anchor set (`trust_anchor_set` — the issuer/key pair is
   present in `trust_store` **and** currently active at the run's
   `issuance_timestamp`)
4. load signing provider (`signing_provider` — present, and
   `is_fixture is False`)
5. verify signing key matches the issuer's Trust Anchor (`signing_key_match`
   — provider's declared issuer/key id and its key's actual public-key
   bytes match `issuer_identity`; `publication_dir` also required here)
6. Conformance Run
7. Evidence Bundle
8. Certification Manifest
9. Technical Certificate (signed with the *validated* provider's key,
   `issuer_id` = the real `issuer_identity.issuer_id` — never the fixture
   `mcc-certify-issuer-<target_id>` convention)
10. verify TC signature (`verify_tc_signature` — an immediate self-check
    that the freshly-issued signature verifies against the key that
    produced it)
11. Publication Record (built and written into the run's own temp
    directory; a conflict against the **external** persistent index is
    detected here and fails closed before anything is committed)
12. final Offline Verification (`offline_verification` — the full
    `verify_technical_certificate` gate, now checked against
    `trust_store.to_trust_anchor_registry(issuance_timestamp)` instead of
    an ad hoc single anchor, plus the Publication Record's own Hash
    References)
13. report success — **only after step 12 passes** does the pipeline
    atomically rename the temp run directory into place, and **only after
    that rename** does it merge the Publication Record into the external,
    persistent Publication Index at `--publication-dir` (see
    `publish_certificate`). A run that fails at any earlier step never
    touches the external index — there is no partial-looking publication.

Every stage above is skipped entirely (no new stage, no filesystem write,
no behavior change) when `official_mode` is `False` — verified by
`tests/test_mcc_certify_pr68.py::test_non_official_mode_unaffected_by_new_fields_left_unset`.

## 9. Key Rotation and Supersession

A Trust Store may list multiple `IssuerIdentity` entries for the same
`issuer_id` under different `key_id`s (an old and a new key coexisting) —
`TrustStore` explicitly permits this as long as each `(issuer_id, key_id)`
pair is unique and no `key_id` is bound to conflicting public keys.
`IssuerIdentity.superseded_by_key_id` (optional) records that an entry has
been succeeded by a newer key id, for audit/traceability — it does not by
itself revoke the entry; set `status=REVOKED` (or an expired
`valid_until`) to actually stop `to_trust_anchor_registry` from resolving
it. Rotation is therefore: publish a Trust Store containing both the old
(now `superseded_by_key_id=<new>`) and new entries during a transition
window, then remove or revoke the old entry once every verifier has
adopted the new Trust Store.

## 10. Secure Operational Guidance

- **The private key file passed to `--signing-key` is never read into,
  logged by, or copied into any generated artifact.** `LocalFileSigningKeyProvider`
  holds the loaded `SigningKey` in memory only; nothing in
  `src/mcc_certify` ever calls `.private_bytes(` (the serialization/export
  operation) outside `signing_provider.py` itself, and even there only to
  *load*, never export (verified by
  `tests/test_mcc_certify_trust_publication_guards.py::test_private_bytes_never_called_outside_signing_provider`).
- Keep the private key file's permissions restrictive (`chmod 600`) and
  outside the repository and any `--output`/`--publication-dir` tree.
- `issuer.json` and `trust-store.json` contain **only public** material
  (public key bytes + fingerprint) — safe to commit, publish, or share
  with verifiers.
- Prefer a distinct signing key per Issuer identity; do not reuse a
  fixture-derived or test key for anything resembling production use.

## 11. No Production Keys Statement

**This PR ships no production Issuer private key anywhere in this
repository.** The CI job `certification-trust-publication` generates a
throwaway Ed25519 key entirely at runtime (never committed, never an
artifact upload target) purely to exercise the official-mode code path
end to end; it is deleted with the CI runner. `LocalFileSigningKeyProvider`
requires the caller to supply their own key file out of band — this
package never generates or embeds one.

## 12. Reproduction Commands

```bash
# Generate an Issuer Identity + Trust Store from a real Ed25519 key
python - <<'PY'
from cryptography.hazmat.primitives import serialization
from mcc_core.signing import SigningKey
from mcc_certify import build_issuer_identity, build_trust_store, write_issuer_identity, write_trust_store

key = SigningKey.generate("issuer-key-1")
with open("issuer-key.pem", "wb") as f:
    f.write(key._private_key.private_bytes(
        serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()))
issuer = build_issuer_identity(
    issuer_id="axlogiq-ca-1", display_name="AXLOGIQ Certification Authority",
    key_id="issuer-key-1", public_key=key.public_key(),
    valid_from=1785024000, created_at=1785024000)
write_issuer_identity(issuer, "issuer.json")
write_trust_store(build_trust_store((issuer,)), "trust-store.json")
PY

# Certify the reference fixture in OFFICIAL mode
python -m mcc_certify certify reference-fixture \
  --output artifacts/certification --run-id official-run-1 --timestamp 2026-07-26T00:00:00Z \
  --issuer-config issuer.json --signing-key issuer-key.pem \
  --trust-store trust-store.json --publication-dir artifacts/publication

# Independently re-verify against the explicit trust store + publication index
python -m mcc_certify verify artifacts/certification/reference-fixture/official-run-1 \
  --trust-store trust-store.json \
  --publication-index artifacts/publication/publication-index.json \
  --require-published
```

## Remaining Limitations

- **No official reference-ecosystem certificate has been issued by this
  PR.** `reference-fixture` remains the only registered Certification
  Target. Certifying Generic HTTP, LangGraph, CrewAI, AutoGen, and
  VoltAgent is the next, separate platform milestone (**PR #69**).
- **No cloud KMS/HSM/Vault-backed `SigningKeyProvider`.** Only
  `LocalFileSigningKeyProvider` (a local PEM file) exists; the abstract
  interface supports adding one later without changing callers.
- **No hosted registry, server, or network-based publication/discovery
  service.** Publication is a static, local JSON document tree.
- **Certificate id global uniqueness remains a single-producer-process
  concern** — `CertificateIdRegistry` (Wave C) is scoped per pipeline run,
  as documented since PR #65; this PR does not add a distributed identity
  registry.
- **No revocation registry wired into the pipeline.** `mcc_evidence`'s
  Wave C `RevocationRegistry` exists and is reused as an empty registry for
  every verification in this PR, exactly as in PR #67 — revoking an
  officially-issued certificate is out of this PR's scope.
- **Trust Store distribution to verifiers remains manual/out-of-band** —
  this PR defines the Trust Store *format* and *offline loading*, not a
  distribution channel (consistent with MCC-TC-001 Section 16.1
  explicitly leaving that mechanism unspecified).
