# MCC Official Signing Ceremony — Operator Runbook

PR #70. This is the manual operator runbook for issuing REAL official
Technical Certificates for the five production reference ecosystems
(`generic-http`, `langgraph`, `crewai`, `autogen`, `voltagent`) and
publishing the official GitHub Release. It complements, and must be read
alongside:

- [`docs/CERTIFICATION_TRUST_AND_PUBLICATION.md`](../CERTIFICATION_TRUST_AND_PUBLICATION.md) (PR #68 — Issuer Identity, Trust Store, Signing-Key Provider, Publication)
- [`docs/CERTIFICATION_FIVE_ECOSYSTEMS.md`](../CERTIFICATION_FIVE_ECOSYSTEMS.md) (PR #69 — the five ecosystems, candidate certification)
- [`OFFICIAL_CERTIFICATION_RELEASE_CHECKLIST.md`](OFFICIAL_CERTIFICATION_RELEASE_CHECKLIST.md) (the step-by-step release checklist)

**As of this PR, no real production Issuer key exists.** Every section
below describes what an authorized operator (AX) must do — this
repository cannot and does not provision the real private key
automatically.

## 1. Official certification architecture

```
Production Issuer Identity (config/official-issuer.json, public)
  -> externally provisioned Production Signing Key (never in the repo)
  -> Protected Signing Ceremony (.github/workflows/mcc-official-certification.yml)
  -> Five Certification Runs (mcc certify <target> --issuer-config ... --official mode)
  -> Five Evidence Bundles / Certification Manifests / Technical Certificates
  -> Offline Verification (verify_certification_run_trusted)
  -> Centralized Official-Eligibility Gate (mcc_certify.official.evaluate_official_eligibility)
  -> Aggregate Release Verification (mcc_certify.aggregate)
  -> Official GitHub Certification Release (mcc_certify.release + gh release create)
```

Every stage above reuses the existing, unmodified PR #67/#68/#69
certification pipeline, Trust Store model, and `SigningKeyProvider`
contract. There is no second signing system, no ecosystem-specific
certification authority, and no new Technical Certificate format.

## 2. Candidate versus official certification

| | Candidate (`certification-<ecosystem>` CI jobs) | Official (this ceremony) |
|---|---|---|
| Issuer | `mcc-ci-candidate-issuer` (deterministic, disclosed, non-production) | `mcc-official-certification-issuer-v1` (real, externally held) |
| Trigger | every push/PR | manual `workflow_dispatch` only, from `main` |
| Trust Store | CI-generated at runtime | `config/official-trust-store.json` (committed, public) |
| Eligible for OFFICIAL status | **Never** — see `mcc_certify.official.evaluate_official_eligibility` | Yes, once the real ceremony succeeds |
| Publishes a GitHub Release | No | Yes (unless `dry_run: true`) |

`evaluate_official_eligibility` is the **one** place OFFICIAL status is
derived. It never trusts a string flag — it independently re-verifies the
certificate's signature against the real official Trust Store, checks the
declared `issuer_id` equals `PRODUCTION_ISSUER_ID`, checks a
`publication-record.json` exists (candidate/fixture runs never produce
one), and checks the run's own recorded `source_commit_sha` matches the
ceremony's requested commit.

## 3. Production Issuer identity

Stable issuer id: `mcc-official-certification-issuer-v1`
(`mcc_certify.official.PRODUCTION_ISSUER_ID`). Generated **once**, offline,
by an authorized operator, using:

```bash
python scripts/generate_production_issuer_identity.py \
  --private-key-out /secure/path/mcc-official-issuer-key.pem \
  --issuer-config-out config/official-issuer.json \
  --trust-store-out config/official-trust-store.json \
  --valid-from 2026-08-01T00:00:00Z
```

This writes the PRIVATE key locally (mode 0600, never printed, never
committed) and the PUBLIC `issuer.json`/`trust-store.json` documents,
which ARE safe to commit. The script prints the public-key fingerprint —
see §4 before trusting it.

## 4. Verify the fingerprint before the first ceremony

Before using a freshly generated (or received) production key for the
first time, independently verify its fingerprint out of band — e.g. read
it back over a separate communication channel from whoever generated it,
or recompute it yourself from the private key file directly:

```bash
python -c "
from mcc_core.signing import SigningKey
from mcc_certify.issuer import public_key_fingerprint
k = SigningKey.from_pem_file('/secure/path/mcc-official-issuer-key.pem', kid='prod-key-1')
print(public_key_fingerprint(k.public_key()))
"
```

Compare this against `public_key_fingerprint` in the committed
`config/official-issuer.json`. **Do not proceed if they don't match.**

## 5. Trust Store publication

`config/official-trust-store.json` is the versioned, offline, public Trust
Store the ceremony workflow and every verifier use. It is generated
alongside the Issuer Identity (§3) and is safe to commit and publish.
Adding a rotated/superseding key (§11) means regenerating this file to
include both the old and new `IssuerIdentity` entries under distinct
`key_id`s.

## 6. Production key custody boundary

The production private key:

- is **never** generated inside CI or any automated process;
- is **never** committed to Git;
- lives only as the GitHub Environment secret
  `MCC_PRODUCTION_ISSUER_PRIVATE_KEY_B64` (base64-encoded PEM) on the
  `mcc-production-signing` Environment, or in the operator's own secure,
  offline storage;
- inside the workflow, is decoded into an env var (never a command-line
  argument) and written to a `0600` temporary file under `$RUNNER_TEMP`,
  deleted in an `if: always()` step immediately after signing.

**No operator should ever paste the production private key into:** source
files, PR comments, issue comments, workflow_dispatch inputs, terminal
commands that land in shell history, logs, or chat messages (including to
an AI assistant). If you ever need to move the key, use a secure secret
manager or an encrypted channel — never plaintext chat or a public
workflow log.

## 7. GitHub Environment configuration (manual, one-time)

An authorized operator (AX) must, in the GitHub repository settings:

1. Create the Environment `mcc-production-signing` (Settings → Environments → New environment).
2. Add **required reviewers** (yourself, and/or other trusted approvers) so every dispatch of the ceremony workflow requires explicit human approval before running.
3. Add the secret `MCC_PRODUCTION_ISSUER_PRIVATE_KEY_B64` to that Environment:
   ```bash
   base64 -w0 /secure/path/mcc-official-issuer-key.pem
   # paste the output as the secret value
   ```
4. (Recommended) Restrict the Environment to the `main` branch only.

This repository's workflow file assumes this Environment and secret exist
by the name above — it does not, and cannot, create them for you.

## 8. Protected signing ceremony

Dispatch `.github/workflows/mcc-official-certification.yml`
(`MCC Official Certification & Release`) from the Actions tab, selecting
**Use workflow from: `main`**, with inputs:

| Input | Example | Notes |
|---|---|---|
| `ref` | the exact 40-character merged commit SHA | must already be merged into `main` |
| `release_version` | `1.0.0` | semver |
| `ceremony_timestamp` | `2026-08-01T00:00:00Z` | explicit RFC3339, for reproducibility |
| `dry_run` | `true` (default) | run the real signing chain but never publish |

Run with `dry_run: true` first. Inspect the uploaded
`official-release-1.0.0` workflow artifact and its `verification-summary.json`
before re-dispatching with `dry_run: false` to actually publish.

Each of the five `official-certify-<ecosystem>` jobs runs independently
(their frameworks cannot share one process), signs with the real
production key, and is individually approval-gated by the
`mcc-production-signing` Environment. `official-release-publish` only
starts once all five have succeeded.

## 9. Five-ecosystem release process

See [`OFFICIAL_CERTIFICATION_RELEASE_CHECKLIST.md`](OFFICIAL_CERTIFICATION_RELEASE_CHECKLIST.md)
for the exact step-by-step checklist.

## 10. Offline verification instructions

Anyone (no CI access, no secrets, no network required) can independently
verify a published release:

```bash
# Download the release assets, then:
python -m mcc_certify verify-aggregate \
  --trust-store official-trust-store.json \
  --publication-dir . \
  --run generic-http=generic-http --run langgraph=langgraph \
  --run crewai=crewai --run autogen=autogen --run voltagent=voltagent

python -c "
from mcc_certify import verify_release_checksums
valid, failures = verify_release_checksums('.')
print('valid:', valid)
print(failures)
"
```

## 11. Key rotation procedure

1. Generate the new key, reusing the SAME `issuer_id`
   (`mcc-official-certification-issuer-v1`) but a NEW `key_id`
   (e.g. `prod-key-2`):
   ```bash
   python scripts/generate_production_issuer_identity.py \
     --private-key-out /secure/path/mcc-official-issuer-key-2.pem \
     --key-id prod-key-2 --valid-from 2027-01-01T00:00:00Z \
     --issuer-config-out config/official-issuer.json \
     --trust-store-out /tmp/new-trust-store.json
   ```
2. Merge BOTH the old and new `IssuerIdentity` entries into
   `config/official-trust-store.json` (so historical certificates signed
   by the old key remain verifiable — see §12).
3. Update the `MCC_PRODUCTION_ISSUER_PRIVATE_KEY_B64` secret to the new key.
4. Optionally set the old key's `status: REVOKED` or a `valid_until` once
   the transition window ends — this stops it from resolving as an active
   Trust Anchor for *new* verifications without altering history.

## 12. Historical verification after rotation/revocation

- A new Issuer key version can be added to the Trust Store without
  rewriting any previously-issued certificate or release.
- A certificate signed by an old key remains verifiable as long as the
  Trust Store you verify against still lists that `(issuer_id, key_id)`
  pair as `ACTIVE` (or was active at the certificate's `issuance_timestamp`
  — `to_trust_anchor_registry(now)` evaluates status/validity window
  relative to the timestamp you pass in, not "now" at verification time,
  for historical checks — pass the certificate's own recorded issuance
  time).
- A revoked or expired Issuer key cannot issue **new** official
  certificates (the ceremony's `signing_key_match`/`trust_anchor_set`
  pipeline stages fail closed), but does not retroactively invalidate
  certificates it already issued while active.

## 13. Incident procedure

If the production private key is suspected compromised:

1. Immediately set that key's Trust Store entry `status: REVOKED` and
   commit the updated `config/official-trust-store.json`.
2. Rotate to a new key (§11) before any further ceremony runs.
3. Do NOT delete the compromised key's entry outright — a Trust Anchor's
   historical existence is part of the audit trail (TC-TRUST-003).
4. Assess whether any already-published release needs a public advisory;
   this repository does not auto-revoke already-published GitHub Releases.

## 14. Release rollback policy

Releases are immutable — the ceremony workflow refuses to overwrite an
existing release tag. To "roll back":

- Publish a NEW release with a new `release_version` — never edit or
  delete a prior release's tag or assets.
- If a published release is later found to be defective, mark it clearly
  (GitHub Release edit → "this release has been superseded by vX.Y.Z")
  rather than removing it, preserving the audit trail.

## 15. Exact milestone completion criteria

This milestone (official certification of the five ecosystems) is
complete ONLY when ALL of the following are true:

1. `config/official-issuer.json` / `config/official-trust-store.json` are
   committed with a REAL, externally-provisioned production key's public
   material (fingerprint independently verified per §4).
2. The `mcc-production-signing` GitHub Environment exists with required
   reviewers and the `MCC_PRODUCTION_ISSUER_PRIVATE_KEY_B64` secret set.
3. The protected ceremony ran with `dry_run: false` against the exact
   merged `main` commit intended for release.
4. All five `official-certify-<ecosystem>` jobs succeeded.
5. `evaluate_official_eligibility` reports `eligible: true` for all five.
6. Aggregate offline verification (`verify-aggregate`) passed.
7. `checksums.sha256` verifies (`verify_release_checksums`).
8. The immutable GitHub Release was created and its tag matches
   `mcc-certification-v<release_version>`.

Until all eight hold, the correct status is `PENDING PRODUCTION KEY
PROVISIONING` or `PENDING PROTECTED SIGNING CEREMONY` — never
`OFFICIALLY CERTIFIED AND RELEASED`.
