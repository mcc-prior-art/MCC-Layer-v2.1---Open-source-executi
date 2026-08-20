# External Checkpoint Anchoring — Mitigating Scenario G

**Mitigating Scenario G — Detectable Full-Chain Rewrite via External Checkpoint
Anchoring.** This is deliberately not called "Closing Scenario G": a hash-chain
with no reference point outside the storage it protects cannot detect a
*self-consistent rewrite* — an actor with full write access to audit-chain
storage alters a non-tail record and recomputes every subsequent hash, so the
rewritten chain still validates internally, exactly as before. This package
gives the chain an external, tamper-evident checkpoint anchor. It converts that
rewrite from **undetectable** to **detectable**. It does not make the rewrite
**impossible**.

> The model proposes. MCC-Core decides. The gate enforces. **The audit chain
> records — and an external checkpoint anchor proves the record hasn't been
> quietly rewritten.**

## The precise property established

> A self-consistent rewrite of the primary audit-chain storage becomes
> detectable **as long as the checkpoint signing authority and the external
> anchor store remain outside attacker control.**

That "as long as" is load-bearing. Read the [Residual trust assumptions](#residual-trust-assumptions)
section before treating this as a closed problem in any deployment.

This work does **not** touch Decision Token schema, Execution Gate
ALLOW/DENY/ESCALATE/CONSTRAIN semantics, or nonce/replay protection. It is a
new, additive, opt-in package (`src/mcc_checkpoint/`) downstream of the audit
log — the same architectural posture as `src/mcc_evidence/` (observational,
no gate/authority/nonce/executor import).

-----

## Architecture

```
AuditLog (src/mcc_core/audit.py)
        │  append-only hash-chain, unchanged
        ▼
CheckpointGenerator            (N=500 records OR T=15 min, whichever first)
        │  signs with the Audit Checkpoint key (NOT the Decision Token key)
        ▼
Checkpoint  { checkpoint_version, chain_id, environment, chain_head_hash,
              record_count, prev_checkpoint_hash, timestamp,
              signing_key_id, repo_sha, kid, sig }
        │  forms its OWN hash-linked chain via prev_checkpoint_hash
        ▼
AnchorStore  (GitBranchAnchorStore — Option A: a separate git repository)
        │
        ▼
verify_anchors()  ── recomputes live audit-chain segments, compares to
        │            every anchored checkpoint, fail-closed throughout
        ▼
AuditAnchorMismatchError  →  Gateway /ready refuses READY, latched
```

## Checkpoint payload

```json
{
  "checkpoint_version": "1.0",
  "chain_id": "mcc-layer-pilot",
  "environment": "pilot",
  "chain_head_hash": "<sha256 of the latest audit record at checkpoint time>",
  "record_count": 500,
  "prev_checkpoint_hash": "<sha256 of the previous checkpoint, or null for genesis>",
  "timestamp": "2026-08-20T00:00:00+00:00",
  "signing_key_id": "mcc-checkpoint-anchor-key-1",
  "repo_sha": "329fc04",
  "kid": "mcc-checkpoint-anchor-key-1",
  "sig": "<base64 Ed25519 signature>"
}
```

- `chain_id` identifies which audit-chain/deployment instance a checkpoint
  describes, so a checkpoint anchored for one deployment cannot be replayed as
  evidence for a different one's chain.
- `environment` labels the deployment tier (`production`/`pilot`/`staging`) —
  informational, not a trust boundary by itself.
- `signing_key_id` is carried **inside the signed claims**, redundantly with
  the envelope's own `kid` (added by `SigningKey.sign_token`).
  `schema.validate_checkpoint_shape` rejects any checkpoint where the two
  disagree — a structural check independent of the signature check.
- `repo_sha` is **build-provenance metadata for cross-reference only**. It is
  signed (so it can't be forged independently of a valid signature), but it is
  **not a root of trust** — nothing in `verify_anchors` treats "the repo_sha
  looks plausible" as evidence of anything.

### Canonical serialization (required property)

The signature covers `mcc_core.signing.canonical_bytes` — deterministic JSON
(`sort_keys=True, separators=(",", ":"), ensure_ascii=True`) — of the claims
dict, never an arbitrary or attacker-supplied byte string. Verification always
**recomputes** this canonical form from the parsed Python object it receives;
it never trusts a byte representation carried alongside the object. Because
`json.loads` collapses duplicate keys to the last occurrence before any code
here ever sees the object, "duplicate JSON field" ambiguity cannot reach the
signed claims at all — there is exactly one canonical encoding for any given
claims dict, by construction.

Regression coverage (`tests/test_checkpoint_anchoring.py`, area 8): field
ordering (canonicalization is insertion-order-independent), unsupported
`checkpoint_version`, malformed signatures, and every claim field individually
altered post-signing — each must invalidate the signature.

-----

## Signing-key separation (required property)

> Decision Token signing authority != Audit Checkpoint signing authority

Checkpoints are signed by a **dedicated Audit Checkpoint Ed25519 key**
(`src/mcc_checkpoint/checkpoint_signing.py`) — **never** the Decision Token
signing key the Gateway uses for `/evaluate`. Both reuse the identical
`mcc_core.signing.SigningKey` primitive and `sign_token`/`verify_token`
envelope (no new cryptographic primitive is introduced), but they are
different key material with different `kid` namespaces:

| Key | Default `kid` | Settings | Purpose |
|---|---|---|---|
| Decision Token key | `mcc-gateway-dev-key-1` | `MCC_GATEWAY_SIGNING_KEY_PATH` | signs `/evaluate` decision tokens |
| Audit Checkpoint key | `mcc-checkpoint-anchor-key-1` | `MCC_GATEWAY_CHECKPOINT_SIGNING_KEY_PATH` | signs checkpoints only |

Compromise of the Decision Token issuer alone is not, by itself, sufficient to
forge audit-anchor history. `load_checkpoint_signing_key(...,
forbidden_key_path=...)` structurally enforces this: if the Audit Checkpoint
key path resolves (by realpath) to the same file as the Decision Token key
path, the Gateway **refuses to start** — a misconfiguration cannot silently
collapse the two authorities back into one key.

Generate the checkpoint key with:

```
python scripts/generate_checkpoint_signing_key.py mcc_checkpoint_signing_key.pem
```

-----

## Trigger: N records OR T time, whichever first

`CheckpointGenerator` fires on `record_count - last_checkpoint_record_count >=
N` OR `now - last_checkpoint_time >= T`, both configurable (never hardcoded):

| Env var | Default |
|---|---|
| `MCC_CHECKPOINT_RECORD_INTERVAL` | 500 |
| `MCC_CHECKPOINT_TIME_INTERVAL_SECONDS` | 900 (15 min) |
| `MCC_CHECKPOINT_CHAIN_ID` | *(required, no default)* |
| `MCC_CHECKPOINT_ENVIRONMENT` | `unspecified` |
| `MCC_CHECKPOINT_REPO_SHA` | resolved via `git rev-parse --short HEAD` if unset |

A trigger with zero new audit records since the last checkpoint never fires,
even past `T` — there is nothing new to attest to.

Checkpoint **generation** runs out-of-process from the Gateway (a cron entry
or a sidecar container), not as a background task inside the ASGI app —
`scripts/run_checkpoint_generator.py --audit-path <path> --once` (invoke from
cron) or without `--once` to poll forever at `--poll-seconds`. This keeps the
request-serving process free of background-task lifecycle concerns; the
Gateway's own involvement is limited to `/ready` **verifying** anchors, never
generating them.

-----

## External anchor: Option A (git), Option B (deferred)

### Option A — a protected git branch on a **separate repository**

The recommended production target is **`mcc-prior-art/mcc-audit-anchors`** —
a repository separate from `mcc-layer`, not an orphan branch inside it. The
point of the exercise is to move checkpoint evidence outside `mcc-layer`'s own
storage/write-access trust boundary; an orphan branch in the same repository
shares that boundary and would not do that.

`GitBranchAnchorStore` never hardcodes a remote — `remote_url`, `branch`, and
`workdir` are explicit configuration (`MCC_CHECKPOINT_ANCHOR_REMOTE_URL`,
`MCC_CHECKPOINT_ANCHOR_BRANCH`, `MCC_CHECKPOINT_ANCHOR_WORKDIR` via
`anchor_store_from_env`). Each `append_checkpoint` call fetches and
fast-forward-resets to `origin/<branch>` before committing, and **pushes are
never `--force`** — a rejected (non-fast-forward) push is a hard
`AnchorStoreError`, never silently retried by forcing.

**Claim hygiene:** Git commit history here is *"externally persisted
append-only checkpoint history under separately configured repository
protection."* It is **not** an independently trusted timestamp authority in
the RFC 3161 sense — a git committer date is self-reported by whoever writes
the commit and is not cryptographically attested by a third party. What
protects it is the *anchor store being outside attacker control* and the
*server-side branch protection* rejecting rewrites — not the timestamp itself.

### Option B — RFC 3161 TSA / public blockchain anchor (deferred)

A genuinely independent, cryptographically-attested timestamp authority
remains a roadmap item, not implemented this pass. Nothing in this package
implements it; Option A's git-based anchor is the entire external-anchoring
mechanism shipped here.

-----

## Two-layer validation

**Layer A — automated, proves append-only interaction semantics (done, local).**
`tests/test_checkpoint_anchoring.py` creates a throwaway local bare git
repository, installs a server-side `pre-receive` hook that rejects any
non-fast-forward ref update (the literal check GitHub branch protection's
"require linear history" + "block force pushes" performs), publishes
checkpoints normally, then simulates an attacker with full local write access
to the anchor workdir's git history (`git rebase -i` + `commit --amend`)
attempting a `git push --force`. The push is rejected by the real hook (a real
subprocess `git push` against a real bare repository — not mocked), and a
fresh reader confirms the anchored history was never altered.

This proves the **mechanism** (fast-forward-only interaction is enforceable by
a real git server-side hook) works correctly. **It does not prove real GitHub
branch/repository protection** — GitHub's ruleset engine, its exact rejection
semantics, and its operational behavior are a different, real system that this
local test does not exercise.

**Layer B — real GitHub acceptance evidence: PENDING EXTERNAL-ANCHOR CONFIGURATION.**

This task attempted to create `mcc-prior-art/mcc-audit-anchors` directly via
the GitHub API available to this session. The attempt failed:

```
POST https://api.github.com/user/repos → 403 Resource not accessible by integration
```

This session's GitHub App installation is scoped to read/write on
`mcc-prior-art/mcc-layer` only; it does not carry repository-creation
permission for the `mcc-prior-art` account. Repository creation and branch
protection configuration therefore require **AX/admin action outside this
session**. Until that is done and a real, controlled non-fast-forward push
attempt against the live protected branch has been observed to be rejected by
GitHub itself, **Layer B is PENDING EXTERNAL-ANCHOR CONFIGURATION** and this
document does not claim real GitHub protection has been verified.

### Manual steps required (AX)

1. Create the repository: `mcc-prior-art/mcc-audit-anchors` (private is a
   reasonable default; visibility is a policy choice, not a security
   property here — protection against rewrite is).
2. Push an initial commit (e.g. `python -m mcc_checkpoint` will create the
   branch and an initializing `README.md` commit automatically on first use,
   or push one manually) and note the resulting default branch name.
3. Create the `audit-checkpoint-anchors` branch (or whichever branch name is
   configured via `MCC_CHECKPOINT_ANCHOR_BRANCH`).
4. Configure a GitHub ruleset (or classic branch protection) on that branch:
   - **Block force pushes.**
   - **Require linear history** (or equivalently, disallow any non-fast-forward
     update).
   - **Restrict deletions** (protect against `git push origin
     --delete audit-checkpoint-anchors`).
5. Perform **one controlled non-fast-forward push attempt** against the
   protected branch *before it contains any real pilot/production anchors* —
   e.g. push two commits, then attempt to force-push a rewritten first commit
   — and confirm GitHub rejects it. Capture the real rejection message and
   the real repository URL as Layer B evidence.
6. Set `MCC_CHECKPOINT_ANCHOR_BACKEND=git`, `MCC_CHECKPOINT_ANCHOR_REMOTE_URL`
   to the repository's clone URL, and `MCC_CHECKPOINT_ANCHOR_BRANCH` /
   `MCC_CHECKPOINT_ANCHOR_WORKDIR` as needed (read by
   `mcc_checkpoint.store.anchor_store_from_env`; not the `MCC_GATEWAY_`-
   prefixed pydantic settings used for the two signing keys above).

Until step 5 is performed and its real output captured, Scenario G mitigation
in production is **configured but not yet acceptance-tested against live
GitHub infrastructure**.

-----

## Verification and fail-closed / latched semantics

`verify_anchors(audit_path, anchor_store, trusted_public_key)`:

1. Reads every anchored checkpoint (empty anchor store → `ok=True,
   checkpoints_verified=0`; a fresh deployment or one short of its first
   trigger is not a failure).
2. Verifies the checkpoints' **own** hash-linked chain
   (`verify_checkpoint_chain_linkage`) — detects tampering of a non-tail
   checkpoint independent of the live audit log.
3. Verifies every checkpoint's Ed25519 signature against the **Audit
   Checkpoint** public key (never the Decision Token key).
4. Reads the live audit log fresh and, for every anchored checkpoint,
   independently recomputes the hash-linked prefix up to `record_count` and
   confirms it still produces `chain_head_hash` — this is the actual Scenario
   G detection: a self-consistent rewrite of anything at or before an
   anchored position breaks this recomputation even though the rewritten
   chain is still internally self-consistent on its own.

Any failure raises `AuditAnchorMismatchError`. This is never downgraded to a
recoverable warning:

- **Startup mismatch:** the Gateway's `/ready` endpoint (opt-in via
  `MCC_REQUIRE_CHECKPOINT_ANCHOR_VERIFICATION=true`) returns HTTP 503
  and `ready: false`. This is purely additive — a deployment that never sets
  the flag is unaffected, exactly like the existing consensus/challenge
  opt-in checks.
- **Latched, not just fail-closed:** once a genuine `AuditAnchorMismatchError`
  is observed, `Gateway.checkpoint_anchor_mismatch_latched` is set, and every
  subsequent `/ready` check returns not-ready **regardless of what a later
  check would otherwise find** — a transient read, an anchor store that
  "recovers," or a race never silently un-latches readiness within that
  process's lifetime. Clearing the latch requires an operator to restart the
  process after investigating and resolving the underlying integrity failure.
- **On-demand mismatch:** `python -m mcc_checkpoint verify-anchors` exits 1 on
  `AuditAnchorMismatchError` (never exit 0) and prints the reason.
- **No verified audit integrity → no execution.** This package does not
  itself gate the Decision Token / Execution Gate ALLOW-DENY-ESCALATE-CONSTRAIN
  path (that would violate the explicit "do not touch Execution Gate
  semantics" constraint on this work). The intended deployment posture is:
  wire `MCC_REQUIRE_CHECKPOINT_ANCHOR_VERIFICATION=true` so an
  orchestrator never routes traffic to a Gateway instance whose audit-anchor
  integrity is unresolved — readiness, not per-request gate logic, is the
  enforcement point, matching every other fail-closed `/ready` dependency
  already in this codebase (Redis, consensus, challenge).

-----

## What this proves, and what it does not

**Proven (this task, real fault injection, not mocked):**

- A self-consistent rewrite of a non-tail (and of the tail, and of a record
  before any anchored checkpoint) audit record is detected by
  `verify_anchors`, even though `AuditLog.verify_chain` on the rewritten file
  still returns `True`.
- Tampering with a non-tail *checkpoint itself* (either its claims or its
  signature) breaks the checkpoints' own forward hash chain and is detected
  independent of the live audit log.
- A real local git server (bare repo + `pre-receive` hook) rejects a
  force-push rewrite attempt against the anchor branch (Layer A).
- Decision Token and Audit Checkpoint signing authorities are
  cryptographically distinct keys; a checkpoint signed with the wrong key is
  rejected; the Gateway refuses to start if misconfigured to reuse one file
  for both.
- Canonical-serialization regression coverage: field-ordering independence,
  unsupported version rejection, malformed-signature rejection, and every
  claim field individually invalidating the signature when altered
  post-signing.
- `/ready` fails closed (503) and **latches** on a genuine anchor mismatch,
  and is purely additive/opt-in otherwise.

**NOT proven / explicitly out of scope this pass:**

- Real GitHub repository/branch protection rejecting a live non-fast-forward
  push — **PENDING EXTERNAL-ANCHOR CONFIGURATION** (see above; requires
  AX/admin action this session's GitHub permissions cannot perform).
- An independently trusted timestamp authority (RFC 3161 or similar) — Option
  B, deferred, roadmap only.
- Making full-chain rewriting impossible. It does not. It makes it
  detectable, contingent on the residual trust assumptions below.

-----

## Residual trust assumptions

1. **The Audit Checkpoint signing key must remain outside attacker control.**
   An attacker who additionally compromises this key (distinct from, but not
   automatically excluded by, compromising the Decision Token key) could sign
   a fraudulent checkpoint over rewritten history.
2. **The external anchor store must remain outside attacker control.** An
   attacker with write access to the configured git remote's repository
   (`mcc-prior-art/mcc-audit-anchors` once created) — as opposed to `mcc-layer`
   — could, in principle, rewrite anchored history too, unless real GitHub
   branch protection (Layer B, currently pending) is actually configured and
   enforced.
3. **Git commit history is not an independently trusted timestamp.** It
   proves *append-only persistence under separately configured repository
   protection*, not third-party-attested time-of-issuance (see claim hygiene
   above). RFC 3161 (Option B) would close this gap; it is not implemented.
4. **`repo_sha` is provenance metadata, not a root of trust.** It is signed,
   but nothing here treats it as evidence independent of the signature and
   the chain-linkage checks.
5. **This does not gate the Execution Gate's ALLOW/DENY/ESCALATE/CONSTRAIN
   path directly** — it gates deployment *readiness*. A deployment that does
   not wire `MCC_REQUIRE_CHECKPOINT_ANCHOR_VERIFICATION=true` into its
   orchestrator's traffic-routing decision gets no benefit from this package
   at request time.

-----

## Scope boundaries (unchanged by this work)

- Does **not** modify `src/mcc_core/audit.py`'s runtime append/verify
  behavior.
- Does **not** modify Decision Token schema, signing, or verification.
- Does **not** modify Execution Gate ALLOW/DENY/ESCALATE/CONSTRAIN semantics
  or the coordinator's `a`–`h` enforcement order.
- Does **not** modify nonce/replay protection.
- `src/mcc_checkpoint/` holds no gate/authority/nonce/executor import — the
  same architectural boundary `src/mcc_evidence/` already established.

## Future validation report entry (template — fill in only real values)

> Scenario G: Mitigated via external checkpoint anchoring (PR #<N>, merged
> `<SHA>`) — full-storage rewrite of a non-tail record now breaks
> verification against externally anchored checkpoints (Layer A proven
> locally; Layer B — real GitHub branch protection — PENDING EXTERNAL-ANCHOR
> CONFIGURATION until AX creates and protects
> `mcc-prior-art/mcc-audit-anchors`). Residual limitation: requires the
> Audit Checkpoint signing key and the external anchor store to remain
> outside attacker control.
