# Governance Evidence Bundle (Core)

A **Governance Evidence Bundle** is a portable, deterministic package of evidence
for a single already-completed MCC-Core governance path. It lets an operator or
auditor export what happened and **verify it offline** — recomputing digests,
cross-checking the signed decision token, re-verifying the audit-chain linkage,
and (with a trusted issuer key) verifying the Ed25519 signature — without a
running MCC service and without a network connection.

```
Proposal → MCC decision → verified authority → gate enforcement →
execution or denial → portable evidence bundle → independent offline verification
```

The evidence layer is **observational and downstream** of decision, gate and
audit. It creates no authority, alters no verdict, authorizes no execution, and
is never part of the execution decision. **No verified decision — no execution**
remains entirely unchanged.

- Package: `src/mcc_evidence/` (reference-runtime subsystem).
- Export API: `mcc_evidence.export_bundle`.
- Offline verify API: `mcc_evidence.verify_bundle`.
- CLI: `python -m mcc_evidence verify <bundle>`.
- Supported schema version: **`mcc-evidence/1`**.

## What it is (and is not)

- It **is** an offline-capable verifier, a portable evidence format, and a
  reference-runtime evidence subsystem exposed as a source-tree API + CLI.
- It is **not**, in this PR, an independently `pip install`-able verifier for
  third parties. Verification currently runs from the repository / runtime source
  tree. A standalone `mcc-evidence` distribution is a deliberate, deferred
  follow-up (see [Operational limitations](#operational-limitations)). The module
  is architected with an extraction seam (minimal dependency footprint) to make
  that future step cheap.

## What a bundle proves

Given a bundle and a **trusted issuer public key**, verification establishes:

- **Integrity** — the manifest is well-formed, every artifact digest recomputes,
  and there are no missing or unexpected files.
- **Authority evidence (executable verdict)** — the decision token is a valid
  Ed25519 signature by a **trusted** issuer, and the verdict, actor, resource,
  action, `action_hash`, `payload_hash`, `policy_hash` and constraints are all
  consistent between the manifest, the signed token, the proposal (if included)
  and the receipt (if included).
- **Audit linkage** — the included audit-chain slice links (`prev_hash`) and each
  entry hash recomputes.
- **Execution / denial consistency** — an `EXECUTED` outcome carries a receipt and
  a signed token; a `DENIED`/DENY outcome carries **no** receipt and no token.

## What a bundle does NOT prove

- It does **not** provide formal non-repudiation, regulatory certification, or
  legal proof. It provides cryptographically checkable integrity + authority
  evidence, nothing more.
- It does **not** establish trust in the signer by itself. Without a trusted
  issuer key supplied to the verifier, a bundle can only be reported as
  *structurally intact with an unverified signer* — never as trusted evidence
  (status `INTACT_UNTRUSTED_SIGNER`).
- It does **not** prove completeness of the whole audit log — only that the
  **included** slice is internally consistent and linked to its stated anchor.
- It is **not** a re-authorization: verifying a bundle grants no authority and
  triggers no execution.

## Trust assumptions

1. The verifier obtains the **trusted issuer public key(s)** out-of-band (the same
   way a TLS client obtains a CA). Trust flows from that key, not from the bundle.
2. `sha256` and Ed25519 (via `cryptography`) are sound.
3. The MCC-Core signing/audit/canonicalization primitives the bundle reuses are
   the same ones that produced the evidence.

## Verification result (structured)

`verify_bundle` returns a structured result, never a bare Boolean. Independent
dimensions are reported separately so an intact-but-untrusted bundle is never
conflated with trusted evidence:

| Field | Meaning |
|-------|---------|
| `integrity_valid` | schema supported, manifest well-formed, digests match, no missing/extra files |
| `audit_chain_valid` / `audit_present` | included audit slice links + recomputes / whether a slice is present |
| `signer_verified` | the token signature verified against the key it was checked with |
| `signer_trusted` | that key was in the caller's trusted set |
| `authority_evidence_verified` | executable verdict: bindings hold **and** the signature is trusted |
| `overall_status` | the single roll-up (below) |
| `trusted` | convenience: True only for trusted governance evidence |

### `overall_status` values and CLI exit codes

| Status | Meaning | Exit |
|--------|---------|------|
| `VERIFIED` | executable verdict: integrity + bindings + audit + **trusted** signature | `0` |
| `DENIAL_VERIFIED` | DENY: integrity + audit + consistency; proves no authorization/execution (no signer to anchor) | `0` |
| `INTACT_UNTRUSTED_SIGNER` | structurally intact, but signer not verified against a trusted key — **not** trusted evidence | `1` |
| `INVALID` | a blocking failure (tamper, missing evidence, broken chain, signature invalid against a supplied trusted key) | `2` |
| `UNSUPPORTED_SCHEMA` | the bundle schema version is not supported | `3` |

A failure that affects integrity or authority evidence is always a blocking
failure — it is never downgraded to a warning.

## Bundle layout

A bundle is a directory (default) or a `.tar.gz` archive:

```
manifest.json            # canonical manifest: schema, decision, execution, audit, artifact digests
decision/token.json      # the signed decision token (executable verdicts only)
proposal/proposal.json   # canonical proposal payload (optional)
gate/result.json         # gate/actuation result summary (optional)
execution/receipt.json   # ALLOW: verified external receipt (never present for DENY)
execution/denial.json    # DENY: denial evidence (verdict + reason)
audit/entries.jsonl      # the relevant audit-chain slice
audit/anchor.json        # anchor: prev-hash, first/last hash, count
```

Every artifact is serialized with MCC-Core's canonical serializer and covered by
a `sha256:` digest in the manifest. The signed decision token is the trust
anchor; the manifest binds file integrity + the authority-bearing fields.

## Export flow

Export consumes already-produced governance data (a signed token, gate result,
audit slice, receipt/denial) as a typed `EvidenceInput`. It performs **no**
authorization or execution and **fails closed**:

```python
from mcc_evidence import EvidenceInput, export_bundle

ev = EvidenceInput(
    verdict="ALLOW", actor_id="agent/x", resource_id="acct-1", action="send_payment",
    correlation_id="corr-1", decision_token=signed_token, proposal=payload,
    receipt=receipt, gate_result=gate, audit_entries=slice_, audit_anchor_prev_hash=anchor)
export_bundle(ev, "out/bundle")            # directory
export_bundle(ev, "out/bundle", archive=True)  # out/bundle.tar.gz
```

Export refuses to emit inconsistent evidence, e.g.: an executable verdict without
its signed token; a DENY carrying a receipt; a proposal that does not hash to the
token's `payload_hash`; or an audit slice whose linkage does not verify.

## Offline verification flow

```python
from mcc_evidence import verify_bundle

result = verify_bundle("out/bundle", trusted_keys={kid: issuer_public_key_b64})
if result.overall_status.value == "VERIFIED":
    ...  # trusted governance evidence
```

## CLI usage

```bash
# Trusted verification (supply the issuer public key you trust, out-of-band):
PYTHONPATH=src python -m mcc_evidence verify out/bundle \
    --trusted-key evidence-kid-1=BASE64_ED25519_PUBKEY --json

# Integrity-only (no key): reports INTACT_UNTRUSTED_SIGNER, exit 1.
PYTHONPATH=src python -m mcc_evidence verify out/bundle
```

The CLI has no network dependency, no execution capability, and never mutates the
bundle. JSON output is machine-readable; the default is a concise human summary.

## ALLOW evidence

`Proposal → verified decision → gate allows → execution receipt → valid bundle.`
The bundle carries the signed token, proposal, gate result, receipt and audit
slice. With the trusted key, `overall_status` is `VERIFIED` and
`authority_evidence_verified` is true.

## DENY evidence

`Proposal → DENY → no execution → denial + audit evidence → valid bundle.` A DENY
bundle carries **no** signed token and **no** receipt — only `execution/denial.json`
and the audit slice. It **proves that execution did not receive authorization**;
it never fabricates a receipt. Its trusted status is `DENIAL_VERIFIED`.

## Tamper detection

Verification detects (and reports as `INVALID`, exit 2) at least: changed
verdict, actor, resource, action, `action_hash`, `payload_hash`, `policy_hash`,
constraints; a changed or re-signed decision token; a changed receipt; a deleted,
reordered, or body-changed audit entry; broken `prev_hash` linkage; a missing
manifested file; an unexpected unmanifested file; a digest mismatch; a malformed
manifest; a duplicate logical entry; conflicting decision identifiers; and a
corrupt archive. An unsupported schema version is reported as `UNSUPPORTED_SCHEMA`
(exit 3). These are covered by `tests/test_evidence_tamper.py`.

## Sensitive-data handling

The bundle preserves MCC-Core's hash-and-reference design: where the runtime
stores only **hashes or references** (e.g. `payload_hash`, receipt
`payload_sha256`), the bundle stores the same — it does **not** add raw secret
material to make the bundle self-contained. Include a raw `proposal` only when you
intend the payload to travel with the evidence; otherwise the `payload_hash`
binding alone proves integrity without disclosing the payload.

## Retention considerations

Bundles are immutable evidence artifacts — treat them as append-only records.
Retain them per your governance/compliance policy. Because verification is offline
and self-contained (given the trusted key), a stored bundle remains verifiable
independently of the producing system's lifecycle.

## Schema-version compatibility

The manifest carries `schema_version` (`mcc-evidence/1`). A verifier refuses a
version it does not support (`UNSUPPORTED_SCHEMA`). The bundle schema version is
**separate** from the MCC-Core runtime version (also stamped, as
`mcc_core_version`) and from any distribution version. A future evidence schema
change will bump the schema version and document a compatibility policy.

## Operational limitations

- **Not independently installable (yet).** In this PR the *bundle* is portable and
  the *verifier* is offline-capable, but the verifier runs from the repository /
  runtime source tree — it is not a standalone `pip install`-able tool for an
  external party. A standalone `mcc-evidence` distribution (with its own build,
  clean-wheel install, artifact inspection, release pipeline, OIDC publishing,
  dependency isolation, and an evidence-schema ↔ runtime-version compatibility
  policy) is explicitly deferred to a separate future PR.
- **Trust is external.** Verification is only as strong as the trusted issuer key
  supplied. Without it, the strongest result is `INTACT_UNTRUSTED_SIGNER`.
- **Not non-repudiation / not certification.** This subsystem provides checkable
  integrity + authority evidence; it makes no formal legal or regulatory claim.
- **Slice, not whole-log.** Audit verification covers the included slice and its
  stated anchor, not the entirety of a remote audit log.
