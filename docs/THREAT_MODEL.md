# Threat Model — Independent Adversarial Assurance Baseline (PR #71)

> **PR #71A scope note:** this document describes the FULL, intended
> adversary model for the whole 13-workstream baseline (delivered across
> stacked PRs 71A–71D; see `docs/ASSURANCE_COVERAGE_MATRIX.md`). At this
> PR, Workstreams A, C, D, F, G, H, K and the negative control are
> implemented; B and E land in #71B, I and J in #71C. Table rows
> referencing those letters describe the target design, not something this
> PR itself tests — the coverage matrix is authoritative on what is
> actually implemented where.

This document states, explicitly, who the assumed adversary is for each
workstream in `assurance/`, and — just as importantly — who is explicitly
NOT modeled. A claim of "resistant to X" is only meaningful relative to a
stated adversary; see `docs/ASSUMPTIONS_AND_LIMITS.md` for the deployment
and infrastructure limits layered on top of this model.

## The central invariant under test

> The model proposes. MCC-Core decides. The gate enforces. The audit chain
> records.

Concretely: **no execution without a verified, correctly bound decision**
— consensus reached by trusted evaluators, over the exact action proposed,
within its validity window, consumed exactly once.

## Adversary classes

| # | Adversary | Capabilities assumed | Capabilities NOT assumed | Primary workstream(s) |
|---|---|---|---|---|
| 1 | **Network attacker, no credentials** | Can reach the actuator/Gateway's HTTP endpoints; can craft arbitrary request bodies; cannot read the API key or any private evaluator key | Cannot intercept/modify traffic between the actuator and its trusted internal collaborators (Redis, the notify sink) | A (exclusive execution path), D (canonical format) |
| 2 | **Network attacker holding a stolen/leaked credential** | Everything in (1), plus a valid API key OR a set of votes from a PREVIOUSLY authorized, now-expired operation | Cannot mint a new, validly-signed evaluator vote for a NEW operation (does not hold an evaluator's private key) | A (replay, A3), C, E |
| 3 | **A malicious or buggy evaluator** (one compromised trust-set member, below the consensus threshold) | Holds one legitimate evaluator private key; can sign arbitrary votes | Does not control enough evaluators to reach the N-of-M threshold alone; the OTHER evaluators are assumed honest | C (veto, threshold) |
| 4 | **A malicious or buggy adapter/framework** originating a proposal | Controls what payload/action a CanonicalProposal carries; can attempt to submit it through any code path it can reach | Cannot bypass the Canonical Ingress Pipeline's own construction — it can only submit what the SDK/pipeline allows it to construct | A4 (wrong trust domain), K (semantic equivalence) |
| 5 | **An operationally faulty environment** (not malicious): the shared authorization backend goes down, the external upstream drops the connection mid-call | Failures are assumed transient and eventually recoverable | Not modeled as adversarial (no attempt to exploit the outage beyond "does a normal request behave safely during it") | B (fault injection), E4 (backend unavailable) |
| 6 | **An insider with direct filesystem access to the audit log** | Can write arbitrary bytes to the on-disk audit file, bypassing the application entirely | Cannot alter what the LIVE, in-memory `AuditLog` object considers the correct chain state (only the on-disk artifact is tampered) | G3 (one explicit, stated exception — see below) |
| 7 | **A component asked to prove its own broken-ness** (the negative control) | The vulnerable target IS the adversary's dream system: no auth, no consensus, no replay protection | N/A — this is the control arm, proving the suite can fail a bad system | Negative control |

Adversary #6 is a genuine departure from "network attacker" and is called
out precisely because of that: it is the ONE test in this baseline
(`test_g3_direct_storage_tamper_is_detected`) that assumes filesystem
access rather than only network access. It exists to prove the audit chain
is tamper-**evident**, not tamper-proof — a materially different and
weaker guarantee, stated as such.

## What is explicitly OUT of scope

- **Breaking Ed25519 or SHA-256 themselves.** This baseline assumes the
  `cryptography` library's primitives are correctly implemented; it tests
  only how MCC-Core *uses* them.
- **Compromise of the host OS, container runtime, or hypervisor.** A
  root-level attacker on the machine running MCC-Core can trivially defeat
  any application-level control; no workstream claims otherwise.
- **Supply-chain compromise** of a Python/Node dependency at install time.
- **Denial of service / resource exhaustion.** No workstream measures
  throughput, rate limits, or resistance to flooding.
- **Multi-tenant isolation** between unrelated deployments sharing
  infrastructure (not applicable to this repository's architecture).
- **Physical access, side-channel (timing/power) attacks.**
- **The evaluators' own key-generation and storage practices** in a real
  production deployment — this baseline generates fresh, ephemeral test
  keys per run; it does not evaluate an operator's real key-management
  procedures (that is `docs/certification/OFFICIAL_SIGNING_CEREMONY.md`'s
  concern, a separate document for a separate process).

## Mapping adversaries to the eight required Workstream-A attacks

| Attack | Adversary class | What it tests |
|---|---|---|
| A1 direct invocation, no consensus | 1 | Nothing executes on proposal alone |
| A2 stolen endpoint, wrong API key | 1 | Client authentication is enforced |
| A3 reused credential (replay) | 2 | Single-use consumption |
| A4 wrong trust domain (Gateway votes on the actuator) | 4 | Trust sets are not interchangeable |
| A5 self-signed forged evaluator | 1/3 | Untrusted keys are never counted |
| A6 disallowed destination | 1 | Destination allowlist enforcement (network-segmentation caveat: see `docs/EXCLUSIVE_EXECUTION_PATH.md`) |
| A7 tampered signature | 1 | Signature verification is real, not decorative |
| A8 valid signature, wrong binding | 2 | Votes bind to the EXACT operation, not just "a" valid signature |

See `docs/EXCLUSIVE_EXECUTION_PATH.md` for the full detail on each attack
and `docs/ASSURANCE_CLAIMS.md` for the exact claim each one supports.
