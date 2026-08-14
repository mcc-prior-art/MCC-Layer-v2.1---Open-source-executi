# Assumptions and Limits — the honest boundary (PR #71)

> **PR #71D scope note:** this is the master limitations document for the
> whole baseline, delivered incrementally across stacked PRs 71A–71D (see
> `docs/ASSURANCE_COVERAGE_MATRIX.md` for exactly what lands where). As of
> this PR, ALL 13 workstreams (A–K), the negative control, the CI workflow,
> and all 8 required docs are implemented. This document remains, however,
> a record of GENUINE, PERMANENT scope limitations — it is not a checklist
> that empties out to zero; see `docs/ASSURANCE_COVERAGE_MATRIX.md` for the
> authoritative IMPLEMENTED / PARTIALLY IMPLEMENTED / NOT IMPLEMENTED /
> BLOCKED BY ENVIRONMENT status of every individual requirement, including
> several that remain permanently NOT or PARTIALLY implemented even at this
> final stage (e.g. genuine mandate-forgery containment, PlusCal, signed
> external audit checkpoints, 4/5 Workstream K adapters run only in CI, not
> locally).

Every workstream in the **MCC-Core Independent Adversarial Assurance
Baseline** makes a narrower, more specific claim than "MCC-Core is secure."
This document collects every scope limitation stated across the individual
workstream tests and docs into one place, so a reviewer never has to
reconstruct it from scattered comments. Read this together with
`docs/ASSURANCE_CLAIMS.md` (what is claimed) and `docs/THREAT_MODEL.md`
(who the assumed adversary is).

> If a limitation below is not acceptable for a given deployment, this
> baseline does not clear that deployment for that property. That is the
> point of writing it down.

## Environment and infrastructure

- **Single host, single process tree, for most of this suite.** Every test
  in `assurance/tests/` runs against processes on ONE machine. For most
  workstreams that means real loopback HTTP with no genuine network
  boundary between the Gateway, the actuator, and the external-effect
  sink — an attacker model that assumes a compromised host can intercept
  loopback traffic is out of scope there. **One exception:**
  `assurance/sut/network_segmentation.py` (Workstream A extension) builds a
  real, kernel-enforced network boundary using Linux network namespaces +
  veth links (still one physical machine, not Docker — this environment's
  Docker Hub pulls are policy-blocked, not multiple hosts) between the
  actuator and the upstream sink specifically, and proves a direct
  connection from the host to the upstream fails at the network layer, not
  merely the application layer. See
  `assurance/tests/test_network_segmentation.py`'s own module docstring for
  that proof's own stated limit: a `CAP_NET_ADMIN` process on the SAME host
  could still join the upstream's namespace directly (`ip netns exec`) —
  this is a real boundary against an attacker without that specific
  privilege, not a claim that no process anywhere on the host could ever
  reach it, and it remains one physical machine, not a real multi-host
  network.
- **Workstream E (replay resistance) is single-node**, and single-node for
  two INDEPENDENT reasons, both directly investigated rather than assumed:
  (1) a Docker daemon IS available in this environment, but Docker Hub
  image pulls are denied by this session's organization egress policy, so
  no multi-container Redis cluster can be built regardless of the
  daemon's presence; (2) `src/mcc_core/redis_client.py` has no
  Sentinel-awareness at all — even a real Sentinel cluster would not
  change the actuator's behavior without a `mcc_core` code change, which
  is out of scope for an assurance-only baseline. No multi-host
  infrastructure was available either. `assurance/sut/replay_cluster.py`
  proves cross-**process** replay rejection over one real, shared
  `redis-server` instance, and fail-closed behavior under TWO independent
  fault-injection mechanisms against that shared backend — process death
  (`kill_redis()`) and a genuine host-local network partition
  (`partition_from_redis()`/`heal_partition()`, an `iptables` `DROP` rule
  against the Redis port, exercising the client's connect/read timeout
  path rather than an immediate connection-refused signal, then healed and
  proven to recover) — but this is still not multi-node Redis
  Cluster/Sentinel failover, and not a real network partition **between
  hosts** (the iptables rule is host-wide, not namespace-scoped, and both
  actuator processes and the one Redis instance remain on the same
  machine; the Workstream A network-segmentation topology above uses
  proper network namespaces instead of a host-wide iptables rule, but it
  too remains one physical machine). See
  `assurance/tests/test_replay_resistance.py`'s own module docstring.
- **Workstream I (TLA+) checks small, bounded instances.** The default
  configuration model-checks 2 operations sharing 1 nonce (720 states); a
  validation run checked 3 operations / 2 nonces (76,440 states). This is
  how exhaustive model checking works — it is not a corner cut specific to
  this baseline, but it means TLC's "no error found" is a claim about
  those specific bounded instances, not an inductive proof for arbitrary
  N. See `model/MCCExecutionStateMachine.tla`'s module docstring.
- **Workstream J (mutation testing) covers 26 hand-picked defects** (the
  original 13, plus a later 13-defect extension — see below), not an
  exhaustive mutation operator sweep across the codebase. 26/26 are
  detected — see `mutation/defects.py`. A defect class nobody has
  imagined yet is still untested by construction. **A genuine generic
  sweep was ALSO run** (`mutmut` -- installed and configured,
  `[tool.mutmut]` in `pyproject.toml`): 225 AST-level mutants against
  `src/mcc_core/gate.py` (the single most security-critical file), against
  a narrow, fast oracle (`tests/test_coordinator.py` alone, chosen for
  speed) — 97 killed, 128 survived. A second, broadened-but-still-partial
  oracle (9 test files collectable inside mutmut's sandbox) raised this to
  116 killed / 109 survived. Of the ~225 generic mutants, the large
  majority are behaviorally inert by construction (`allowed: False→None`,
  `reason: str→None`/arg-drop mutants that crash into the gate's own
  `except Exception` catch-all, cosmetic string-literal recasing, unasserted
  numeric-constant tweaks) — not real coverage gaps.
  The one mutant *shape* that IS a genuine security regression is
  `GateResult(False, ...)` → `GateResult(True, ...)` (a fail-open flip).
  There are exactly 14 such call sites in `ExecutionGate._verify()`/
  `verify()`. A pre-merge direct-verification addendum applied each of the
  14 to the real (non-sandboxed) `gate.py` one at a time, reverting after
  each, against a real 7-file oracle (`tests/test_mcc_core.py`,
  `tests/test_gateway.py`, `tests/test_coordinator.py`,
  `tests/test_mandate.py`, `tests/test_mandate_http.py`,
  `assurance/tests/test_exclusive_execution_path.py`,
  `assurance/tests/test_decision_authority_containment.py`) and found
  12/14 caught — 2 survived (the `verify()` exception handler, and the
  `nbf`/`exp` type-check). **Both gaps are now closed**: two new
  regression tests were added
  (`tests/test_mcc_core.py::test_gate_denies_when_verify_raises_unexpectedly`
  and `tests/test_mcc_core.py::test_gate_denies_malformed_time_window`),
  and all 14 fail-open sites are now permanent, individually-named,
  CI-gated defects in `mutation/defects.py` (the `gate-*-fail-open`
  block), each verified via the isolated-repo-copy harness rather than
  mutmut's sandbox or a hand-run script — 14/14 detected, reproducibly, in
  `python -m mutation` / `python -m assurance run` going forward. The
  remaining ~211 generic survivors (the inert categories above) were not
  individually re-triaged one-by-one; that would be a much larger, lower-
  value undertaking than closing the 2 real gaps was, since none of them
  represent an unaudited fail-open shape. This remains a narrowly-scoped
  demonstration that generic mutation testing IS achievable here, not a
  comprehensive codebase-wide sweep.
- **Workstream H (property-based testing) uses bounded example counts**
  (200 for pure/fast properties, 25 for the network-bound differential
  test, 8 stateful sequences of 6 steps each) — Hypothesis explores a
  large but finite, randomly-seeded slice of the input space per run, not
  the whole space. **Failing examples now persist in a genuine, committed
  regression corpus**, not just Hypothesis's default git-ignored local
  cache: the `assurance` profile (`assurance/tests/conftest.py`)
  redirects the example database to `assurance/tests/
  hypothesis_seed_corpus/` (tracked in git) and enables `print_blob=True`
  so any failure also prints a reproducible decorator in logs.
- **Workstream K: only `generic-http` runs locally.** The other four
  adapters (LangGraph, AutoGen, CrewAI, VoltAgent) require their native
  framework installed; this environment has none of them. Their
  `assurance/tests/test_semantic_equivalence.py` cases SKIP with an
  explicit reason here and are exercised by dedicated, isolated CI jobs
  instead (`.github/workflows/mcc-independent-assurance.yml`).

## Design of the SUT itself

- **In-memory registries by default.** Every workstream except E runs the
  actuator with `MCC_NONCE_BACKEND`/`MCC_CHALLENGE_BACKEND` unset (the
  in-memory default) — a genuine, real code path (and the one this
  repository's own dev/pilot deployments use), but not the Redis-backed
  path a production multi-replica deployment would run under load.
- **`EXECUTION_UNKNOWN` is never directly observable, and this is
  confirmed NOT a normative gap** (checked directly against
  `docs/INTEGRATION_CONTRACT.md`'s own binding lifecycle table, which
  defines `CREATED`/`VALIDATED`/`SUBMITTED`/`DECIDED`/`ESCALATED`/
  `VERIFIED`/`ENFORCED`/`EXECUTING`/`COMPLETED`/`REFUSED`/`FAILED` and has
  **no** `EXECUTION_UNKNOWN` state at all — its closest terminal state is
  `FAILED` ("error/ambiguous"), not a distinct "unknown, come back later"
  status). `EXECUTION_UNKNOWN` is exclusively a reference-model construct
  of `assurance/state_machine.py`/`model/MCCExecutionStateMachine.tla`
  (built for this baseline's own black-box and formal checks), not
  something the actual contract requires this implementation to expose.
  Production code is therefore correctly left unchanged here: this
  implementation's receipt-verifying executor resolves a transport
  failure synchronously to `executed=false` within the same response — a
  stronger, more conservative guarantee than the reference model's 8
  states technically require, not a gap against either the reference
  model or (confirmed here) the normative contract.
- **Genuine mandate-forgery containment is now exercised**
  (`assurance/tests/test_mandate_containment.py`, C9-C23), closing what was
  previously a stated gap. A real mandate issuer trust config
  (`MCC_TRUST_CONFIG`) is provisioned on a dedicated, mandate-authority-only
  Gateway topology (`build_system_under_test(require_consensus=False)` —
  the shared topology's `EnforcementCoordinator` requires N-of-M consensus
  unconditionally for every actuation, which the mandate HTTP API never
  supplies, so mandate-only authority needs its own topology; see that
  file's module docstring). Genuine mandates execute (C9); forged
  (untrusted issuer), tampered-after-signing, expired, not-yet-valid,
  subject-substituted, scope-mismatched, and revoked mandates are all
  denied (C10-C18); `max_`/`min_`/`allowed_` constraint types are proven on
  the mandate path too (C20-C23), the first coverage in this baseline of
  constraint types beyond the actuator's `max_body.amount`. On the SHARED
  (`require_consensus=True`) topology, `/mandates/execute` still fails
  closed for every mandate regardless of trust configuration, because that
  topology's mandatory consensus gate blocks it independently of mandate
  validity — a real, different, and now correctly documented limitation
  (`test_c8_mandate_execute_fails_closed_on_the_consensus_required_topology`).
- **The negative control is deliberately minimal**, not a second
  implementation of `egress_proxy` with one bug — it removes FOUR
  invariants at once (auth, SSRF, consensus, replay) for clarity. It
  demonstrates the assurance methodology can fail a broken system; it is
  not itself a fuzzing target for "how many ways can a real system break."
- **Signed external audit checkpoints are now implemented**
  (`assurance/audit_checkpoint.py`, `assurance/tests/test_audit_checkpoint.py`
  G4-G8), closing a previously-stated gap. Scoped honestly: self-contained-
  mode-only (reads the audit log file directly — the same class of
  operation `corrupt_gateway_audit_chain` already uses, not a network
  observation), not a production feature (does not run inside the
  Gateway, does not change `mcc_core.audit`'s runtime behavior), and not
  a full always-on external timestamping service (e.g. RFC 3161) — this
  closes "no independent signer touches the chain at all," not the
  larger production-grade external-anchoring architecture a real
  deployment might eventually want.

## Third-party / external execution mode

- **`connect_external` (the genuine third-party CLI path,
  `MCC_ASSURANCE_EXTERNAL=1`) still requires the OPERATOR to hand this
  suite valid evaluator credentials** for every positive-path (ALLOW/
  CONSTRAIN) scenario. A system cannot prove "valid authorization works"
  without being handed valid authorization by its own operator — this is
  a structural property of black-box testing, not something this suite
  can design around. See `docs/THIRD_PARTY_RUNBOOK.md`.
- **External mode is now genuinely exercised end-to-end**
  (`assurance/tests/test_external_mode.py`, L1-L4): a real `mcc-assurance
  run --target ... --actuator ... --notify ... --external-config ...` OS
  subprocess (the literal, named CLI interface) attaches to an
  already-running deployment it did NOT itself provision, and its
  evidence bundle is independently verified against that target's own
  receipt oracle — not the CLI's self-reported summary. This exercise
  surfaced and fixed several REAL, previously-latent bugs:
  `gateway_notification_receipt_count`/`gateway_vote_as`/
  `gateway_consensus_votes` all silently depended on self-contained-mode-
  only internal state (`_gateway_harness`) and would have crashed
  (`AttributeError`) or misbehaved the first time any external deployment
  reached those code paths, because no prior test in this baseline ever
  exercised `connect_external` at all. **What remains genuinely untested**:
  a truly remote, separately-hosted, cross-organization-trust-boundary
  deployment — the "target" in this exercise is still a process on the
  same sandbox machine; only the CODE PATH (HTTP + config file, no
  subprocess spawned or torn down by the CLI) is genuinely exercised the
  way an external operator would use it, not the trust boundary itself.
  There is no second organization or separate host available in this
  environment to close that specific, narrower claim.

## What this baseline does not attempt at all

- **Cryptographic primitives are trusted, not re-verified.** This baseline
  does not attempt to break Ed25519 signatures or SHA-256 hashes — it
  assumes the `cryptography` library's implementation is correct and
  tests only how MCC-Core USES those primitives (binding, replay,
  single-use), never the primitives themselves.
- **Supply-chain and dependency compromise are out of scope** — a
  malicious `pip`/`npm` package substituted at install time is not
  something any test here would detect.
- **Host/OS-level compromise is out of scope** except where a workstream
  explicitly says otherwise (the audit-tamper test in Workstream G
  simulates ONE specific compromised-storage scenario as a stated
  exception — see that test's own docstring).
- **Side-channel attacks** (timing, power analysis) are not tested.
- **No claim of completeness.** "Satisfies the tested normative invariants
  under the declared threat model, deployment assumptions, implementation
  version, and test environment" is the entire permitted conclusion — see
  `docs/ASSURANCE_CLAIMS.md`'s claim-hygiene rules.
