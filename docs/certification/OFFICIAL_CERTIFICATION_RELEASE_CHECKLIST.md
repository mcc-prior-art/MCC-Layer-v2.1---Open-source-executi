# MCC Official Certification Release Checklist

PR #70. Use this checklist alongside
[`OFFICIAL_SIGNING_CEREMONY.md`](OFFICIAL_SIGNING_CEREMONY.md), which
explains the *why* and the full detail behind each step below.

## Pre-ceremony (one-time, before the first release)

- [ ] Generate the production Issuer key offline:
      `python scripts/generate_production_issuer_identity.py --private-key-out ... --issuer-config-out config/official-issuer.json --trust-store-out config/official-trust-store.json --valid-from <RFC3339>`
- [ ] Independently verify the printed public-key fingerprint out of band.
- [ ] Commit `config/official-issuer.json` and `config/official-trust-store.json` (public material only) via a normal reviewed PR.
- [ ] Create the GitHub Environment `mcc-production-signing`.
- [ ] Add required reviewers to that Environment.
- [ ] Add secret `MCC_PRODUCTION_ISSUER_PRIVATE_KEY_B64` (base64 of the private key PEM) to that Environment.
- [ ] Confirm the private key file is stored securely outside the repository and delete any unneeded local copies.

## Per-release

- [ ] Confirm the intended commit is merged into `main` and CI is green on it.
- [ ] Note the exact 40-character commit SHA.
- [ ] Decide the release version (semver, e.g. `1.0.0`).
- [ ] Decide the ceremony timestamp (RFC3339, explicit — not "now").
- [ ] Dispatch `MCC Official Certification & Release` from `main` with `dry_run: true`.
- [ ] Approve the `mcc-production-signing` Environment deployment when prompted (once per job that requires it).
- [ ] Wait for all five `official-certify-<ecosystem>` jobs and `official-release-publish` to succeed.
- [ ] Download the `official-release-<version>` workflow artifact.
- [ ] Inspect `verification-summary.json` — confirm `all_eligible: true` and every ecosystem's `eligible: true`.
- [ ] Run `python -c "from mcc_certify import verify_release_checksums; print(verify_release_checksums('<extracted-release-dir>'))"` — confirm `(True, [])`.
- [ ] Re-dispatch the SAME workflow with the SAME `ref`/`release_version`/`ceremony_timestamp` and `dry_run: false`.
- [ ] Approve the Environment deployment again.
- [ ] Confirm the workflow's "Refuse to overwrite an existing release tag" step passed (no prior release with this tag existed).
- [ ] Confirm the GitHub Release `mcc-certification-v<version>` was created, targeting the exact commit SHA.
- [ ] Verify the Release contains: `release-index.json`, `checksums.sha256`, `verification-summary.json`, `official-issuer.json`, `official-trust-store.json`.
- [ ] Independently download the published release assets (in a fresh, offline environment) and re-run `verify-aggregate` + `verify_release_checksums` against them.
- [ ] Announce the release, referencing the release-index.json's `production_issuer_id` and public-key fingerprint for anyone who wants to verify independently.

## If anything fails

- [ ] Do not re-dispatch with `dry_run: false` until the failure is understood and fixed.
- [ ] A failed ecosystem job leaves no partial release (the aggregate job never runs) — safe to retry after fixing the cause.
- [ ] If a Trust Store or Issuer mismatch is the cause, fix the committed `config/official-*.json` files via a normal PR before retrying — never bypass the eligibility gate.
