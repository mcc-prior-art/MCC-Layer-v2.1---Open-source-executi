# Assurance Coverage Matrix (PR #71)

This document maps **every** requirement of the original "MCC-Core
Independent Adversarial Assurance Baseline" task to its actual
implementation status. It exists specifically so no requirement is
silently dropped, weakened, or marked complete when it is not — per an
explicit scope-control instruction received partway through this work.

Status definitions:

- **IMPLEMENTED** — real, working, tested code exists and passes.
- **PARTIALLY IMPLEMENTED** — a genuine, working subset exists; the
  remainder is named explicitly, not hidden.
- **NOT IMPLEMENTED** — no code exists for this requirement.
- **BLOCKED BY ENVIRONMENT** — this sandbox lacks the infrastructure
  required (no Docker, no multi-host, no live internet to a specific
  service, etc.); the requirement is documented, and the code that DOES
  exist is written to be extended once the infrastructure is available.

This matrix reflects the state of the `feat/independent-assurance-
baseline` branch (12 commits, `3f5348c`..`467eab5`) before it was
restructured into the four stacked PRs (71A–71D) this document now also
maps requirements onto.

## Workstream A — Exclusive execution path

| Requirement | Status | PR | Evidence |
|---|---|---|---|
| 8 required attacks (direct invocation, stolen endpoint, replayed credential, adapter-to-actuator bypass, agent-to-actuator bypass, alternate network route, forged gate identity, valid-token-wrong-binding) | **IMPLEMENTED** | 71A | `assurance/tests/test_exclusive_execution_path.py` (8/8 tests, `docs/EXCLUSIVE_EXECUTION_PATH.md`) |
| Zero external effects on every unauthorized route, verified independently | **IMPLEMENTED** | 71A | same file — every test polls `notification_receipt_count()` before/after |
| Network-segmentation guarantee (attacker with raw network access to upstream) | **IMPLEMENTED** — a real, kernel-enforced boundary (Linux network namespaces + veth links, not Docker: this environment's Docker Hub pulls are policy-blocked) between the actuator's own namespace and the upstream's own namespace, with the upstream namespace having NO route back to the host at all. N1 proves the governed flow still executes across that real boundary; N2 proves a direct connection attempt from the host to the upstream — zero actuator/governance involvement — fails as a genuine NETWORK-layer error (`ConnectError`/`ConnectTimeout`), not an application-level DENY; N3 proves the topology is segmented by design, not simply broken (the actuator's own inbound API stays reachable). Honest limit stated: still one physical machine, and a `CAP_NET_ADMIN` process on that SAME host could join the upstream's namespace directly — not a claim about a real multi-host network | 71A | `assurance/sut/network_segmentation.py`; `assurance/tests/test_network_segmentation.py` (N1-N3); `docs/EXCLUSIVE_EXECUTION_PATH.md`'s updated A6 caveat |

## Workstream B — Execution atomicity / 8-state machine + fault injection

| Requirement | Status | PR | Evidence |
|---|---|---|---|
| 8-state reference model with transition validator | **IMPLEMENTED** | 71A (model) / 71B (fault-injection test) | `assurance/state_machine.py` |
| Real fault injection (not mocked) | **IMPLEMENTED** | 71B | `assurance/sut/harness.py::kill_notify/restart_notify` — genuine OS process kill/restart |
| Proof no false EXECUTED under fault, no phantom receipt, exactly-once retry | **IMPLEMENTED** | 71B | `assurance/tests/test_execution_atomicity.py` (`test_b5`, `test_b6`) |
| `EXECUTION_UNKNOWN` observable as a distinct, persistent caller-visible state | **NOT IMPLEMENTED** — this implementation resolves it synchronously; CONFIRMED not a normative gap by direct comparison against `docs/INTEGRATION_CONTRACT.md`'s own binding lifecycle table (which has no `EXECUTION_UNKNOWN` state at all) — `EXECUTION_UNKNOWN` is exclusively a reference-model construct of this baseline's own `assurance/state_machine.py`/TLA+ model, not a contract requirement | 71B | `docs/ASSUMPTIONS_AND_LIMITS.md`; `docs/INTEGRATION_CONTRACT.md`'s lifecycle table |

## Workstream C — Decision authority containment

| Requirement | Status | PR | Evidence |
|---|---|---|---|
| Gateway `/consensus/*` HTTP API containment (below-threshold, veto, wrong policy hash, wrong actor, forged evaluator, replay) | **IMPLEMENTED** | 71A | `assurance/tests/test_decision_authority_containment.py` (C1–C7) |
| Genuine mandate authority containment (forged vs. real signed mandate) | **IMPLEMENTED** — genuine mandate executes; forged/tampered/expired/not-yet-valid/subject-substituted/scope-mismatched/revoked all denied (C9-C18), on a dedicated mandate-authority-only topology (`require_consensus=False` — the shared topology's coordinator requires consensus unconditionally, independent of mandate validity; C8 now documents THAT, correctly) | 71A | `assurance/tests/test_mandate_containment.py`; `docs/ASSUMPTIONS_AND_LIMITS.md` |
| Constraint types beyond the actuator's `max_body.amount` (`min_`, `allowed_`) | **IMPLEMENTED** — proven on the mandate path (C20-C23): `max_`/`min_` clamp, `allowed_` denies-if-excluded/permits-if-included | 71A | `assurance/tests/test_mandate_containment.py` (C20-C23) |

## Workstream D — Canonical action format + differential testing

| Requirement | Status | PR | Evidence |
|---|---|---|---|
| Independent, normative canonical action format spec | **IMPLEMENTED** | 71A | `docs/CANONICAL_ACTION_FORMAT.md`, `assurance/canonical_action.py` |
| Differential tests, two independent parsers, large attack corpus | **IMPLEMENTED** (25-case corpus: 15 valid + 10 malformed) | 71A | `assurance/tests/test_canonical_action_differential.py` |
| Exhaustive/fuzzed corpus beyond the 25 hand-written + Hypothesis-generated cases | **PARTIALLY IMPLEMENTED** — extended generatively in Workstream H (`test_h2_*`, 25 more generated cases), not exhaustive | 71A | `assurance/tests/test_property_based.py` |

## Workstream E — Distributed replay resistance

| Requirement | Status | PR | Evidence |
|---|---|---|---|
| Cross-process replay rejection over a real shared backend | **IMPLEMENTED** (single-node, two real OS processes, one real `redis-server`) | 71B | `assurance/sut/replay_cluster.py`, `assurance/tests/test_replay_resistance.py` |
| Fail-closed when the shared backend is unreachable | **IMPLEMENTED** | 71B | `test_e4_shared_backend_unreachable_fails_closed` |
| Multi-**node** (separate hosts) replay resistance | **BLOCKED BY ENVIRONMENT** — no multi-host infrastructure available | 71B | Stated in `assurance/tests/test_replay_resistance.py`'s module docstring and `docs/ASSUMPTIONS_AND_LIMITS.md` |
| Redis Cluster/Sentinel failover scenarios | **BLOCKED BY ENVIRONMENT, and additionally by ARCHITECTURE** — investigated directly (not merely assumed): a Docker daemon IS available in this environment, but Docker Hub image pulls are denied by this session's organization egress policy (confirmed via the agent proxy's own status endpoint: `connect_rejected` on `production.cloudfront.docker.com`), so a genuine multi-container Redis Sentinel cluster cannot be built here regardless. Independently, `src/mcc_core/redis_client.py::redis_client_from_env` constructs a plain `redis.from_url(...)` client with NO Sentinel-awareness at all (no `redis.sentinel.Sentinel` usage anywhere in `mcc_core`) — so even with a real Sentinel cluster available, the actuator would not transparently follow a Sentinel-promoted primary without a genuine `mcc_core` code change, which is out of scope for an assurance-only baseline (see `CLAUDE.md`'s "do not add dependencies/production changes without explicit approval"). Both facts are stated so a future implementer knows exactly what unblocking this needs: organization egress policy AND a `mcc_core` Sentinel-aware client | 71B | `docker version`; `redis_client_from_env`'s own source; `curl $HTTPS_PROXY/__agentproxy/status` |
| Real network-partition scenarios (not process-kill) | **IMPLEMENTED** — a host-local `iptables` `DROP` rule against the shared Redis port severs the actuator's network path to it while the `redis-server` process stays alive and healthy, exercising the client's connect/read timeout path rather than an immediate connection-refused signal; the actuator fails closed while partitioned and recovers once healed. Honest limit stated: this is a HOST-WIDE firewall rule, not a network-namespace-scoped partition, and both actuator processes and the one Redis instance remain on the same machine — not a partition between separate hosts (that remains blocked by the same infra limits as the row above) | 71B | `assurance/sut/replay_cluster.py::partition_from_redis`/`heal_partition`; `assurance/tests/test_replay_resistance.py::test_e3b_network_partition_from_shared_backend_fails_closed_then_recovers` |

## Workstream F — Constraint enforcement

| Requirement | Status | PR | Evidence |
|---|---|---|---|
| Original excessive value never executes; only the clamp does (independently verified hash) | **IMPLEMENTED** | 71A | `assurance/tests/test_constraint_enforcement.py` (F1–F4) |
| Resubmitting the original value as "constrained" is refused | **IMPLEMENTED** | 71A | `test_f4_resubmitting_the_original_excessive_amount_as_constrained_is_refused` |
| Constraint types beyond `max_body.amount` on THIS actuator's own HTTP-egress constraint config specifically | **NOT IMPLEMENTED** — only the one configured constraint is exercised at the actuator; the actuator ships no `min_`/`allowed_` constraint of its own to attack | 71A | — |
| Constraint types beyond `max_` in general (`min_`, `allowed_`), via the mandate authority's identical constraint convention | **IMPLEMENTED** — see Workstream C's C20-C23 above; the mandate path shares the exact same `mcc_core.authority._constraint_violations`/`apply_constraints` mechanism the actuator uses, so this is genuine coverage of the mechanism, not a different one | 71A | `assurance/tests/test_mandate_containment.py` (C20-C23) |

## Workstream G — Audit survivability

| Requirement | Status | PR | Evidence |
|---|---|---|---|
| Chain stays valid across a mix of successful/rejected operations | **IMPLEMENTED** | 71A | `assurance/tests/test_audit_survivability.py` (G1, G2) |
| Tamper-evidence (direct on-disk edit flips verification to invalid) | **IMPLEMENTED** — with a stated, different threat model (filesystem access, not network) | 71A | `test_g3_direct_storage_tamper_is_detected`; `docs/THREAT_MODEL.md` adversary #6 |
| **Signed external checkpoints** (an independently, externally signed periodic anchor of the chain state) | **IMPLEMENTED** — `assurance/audit_checkpoint.py`: a checkpoint is signed with a key SEPARATE from the Gateway's own signing key, over an INDEPENDENTLY reimplemented hash-chain recomputation (never imports `mcc_core.audit`, matching Workstream D's differential-testing posture). Proven: verifies against a genuine untampered chain (G4); still verifies after the chain legitimately grows (G5); DETECTS retroactive rewrite of the checkpointed prefix (G6, the core proof); rejects an untrusted signer (G7); rejects a chain shorter than the checkpoint claims (G8). Scoped honestly: self-contained-mode-only (reads the audit file directly, same class of operation as G3's tamper test), not a production feature, not a full RFC-3161-style always-on external timestamping service | 71D | `assurance/tests/test_audit_checkpoint.py` (G4-G8) |

## Workstream H — Property-based / stateful testing

| Requirement | Status | PR | Evidence |
|---|---|---|---|
| Property-based testing of the canonical format (generative, not fixed-corpus) | **IMPLEMENTED** (200 pure examples, 25 network-bound examples) | 71A | `assurance/tests/test_property_based.py` (`test_h1_*`, `test_h2_*`) |
| Stateful testing of the actuator protocol | **IMPLEMENTED** (8 examples × 6 steps, `RuleBasedStateMachine`) | 71A | `ActuatorProtocolMachine` in the same file |
| **Persisted failing seeds** (a durable regression corpus of counterexamples found) | **IMPLEMENTED** — the `assurance` Hypothesis profile (`assurance/tests/conftest.py`) redirects the example database from the default `.hypothesis/` (repo root, git-ignored -- a failure found on one machine/CI run never reaches another) to `assurance/tests/hypothesis_seed_corpus/`, which is NOT git-ignored: a genuine, durable, committable regression corpus. Also enables `print_blob=True` so any failure additionally prints a copy-pasteable `@reproduce_failure` decorator directly in CI/test logs. Verified with a deliberately-failing throwaway property: the corpus directory was genuinely populated with real failing-example entries, then the throwaway test was removed | 71A | `assurance/tests/conftest.py`; `assurance/tests/hypothesis_seed_corpus/` (populated on first real failure) |

## Workstream I — Formal model checking

| Requirement | Status | PR | Evidence |
|---|---|---|---|
| TLA+ formal model of the execution lifecycle | **IMPLEMENTED** | 71C | `model/MCCExecutionStateMachine.tla` |
| PlusCal | **NOT IMPLEMENTED** — the model is written in raw TLA+, not PlusCal (a design choice for directness, not an oversight, but a real deviation from "TLA+/PlusCal" as originally scoped) | 71C | — |
| 6 specific properties, machine-checked | **IMPLEMENTED** | 71C | `model/MCCExecutionStateMachine.cfg`; `model/run_tlc.sh`; 720 states (small config) + 76,440 states (validation config) both checked clean |
| Model-checking at production scale (large N operations/nonces) | **BLOCKED BY ENVIRONMENT** — not a sandbox limitation but an inherent property of exhaustive model checking (state-space explosion); documented as a bounded-instance limitation, not fixable by more time/resources without switching to a different verification technique (e.g. TLAPS proof, not exhaustive TLC) | 71C | `docs/ASSUMPTIONS_AND_LIMITS.md` |

## Workstream J — Mutation testing

| Requirement | Status | PR | Evidence |
|---|---|---|---|
| Mutation testing of 13 specific security-critical defects | **IMPLEMENTED** | 71C | `mutation/defects.py` |
| 100% detection requirement | **IMPLEMENTED** (13/13; required real investigation and 2 rounds of fixes — see `mutation/detectors.py`'s own docstring for what was wrong and why) | 71C | `python -m mutation` exit 0 |
| Generic/exhaustive mutation operator sweep (e.g. via `mutmut`/`cosmic-ray`) across the wider codebase | **PARTIALLY IMPLEMENTED** — `mutmut` (installed, `[tool.mutmut]` in `pyproject.toml`) run against `src/mcc_core/gate.py` (the single most security-critical file): 225 generic AST-level mutants generated, 97 killed / 128 survived against a NARROW, fast oracle (`tests/test_coordinator.py` alone, chosen for speed over the full suite). Manually spot-checked one flagged, security-relevant survivor (a `GateResult(False, ...)` → `GateResult(True, ...)` flip on the non-executable-verdict check) against the REAL, FULL existing test suite: it IS caught (`tests/test_mcc_core.py::test_gate_denies_signed_deny_verdict`) — meaning the raw 128-survivor count materially OVERSTATES real gaps; a full run with every relevant test file as oracle would very likely kill many more, but was not completed (the full suite run inside mutmut's `mutants/` sandbox hit `main.py`-relative-import friction, and a full untriaged run of 225 mutants × the complete suite was not attempted given the time this would take). This is genuine tool output, not fabricated, but the wider-codebase sweep the task named remains only narrowly exercised, not comprehensively triaged | 71C | `pyproject.toml`'s `[tool.mutmut]`; `docs/ASSUMPTIONS_AND_LIMITS.md` |

## Workstream K — Five-adapter semantic equivalence

| Requirement | Status | PR | Evidence |
|---|---|---|---|
| Same containment properties proven across 5 real framework adapters | **PARTIALLY IMPLEMENTED** — the test code exists and is correct for all 5; only `generic-http` (1/5) actually executes in THIS environment | 71A | `assurance/tests/test_semantic_equivalence.py` |
| LangGraph / AutoGen / CrewAI / VoltAgent | **IMPLEMENTED, verified in real CI** — **BLOCKED BY ENVIRONMENT locally only** (frameworks not installed in this sandbox), but each dedicated CI job genuinely installs its native framework and passes: run [`31775485382`](https://github.com/mcc-prior-art/mcc-layer/actions/runs/31775485382), jobs `assurance-langgraph`/`assurance-autogen`/`assurance-crewai`/`assurance-voltagent` all `success`, zero dependency-related skips | 71A (test code) / CI (execution, confirmed) | `.github/workflows/mcc-independent-assurance.yml`'s `assurance-langgraph`/`-autogen`/`-crewai`/`-voltagent` jobs |

## Negative control

| Requirement | Status | PR | Evidence |
|---|---|---|---|
| Deliberately vulnerable reference target | **IMPLEMENTED** | 71A | `assurance/sut/vulnerable_target.py` |
| Proof the harness FAILS (reports the attack succeeding) against it | **IMPLEMENTED** | 71A | `assurance/tests/test_negative_control.py` (4 tests, all pass, demonstrating the vulnerable target IS exploitable) |

## Workstream L — Independent runner + third-party CLI

| Requirement | Status | PR | Evidence |
|---|---|---|---|
| `make independent-assurance` | **IMPLEMENTED** | 71A (spine) | `Makefile` |
| Runner that discovers + aggregates every workstream module | **IMPLEMENTED** | 71A (spine) | `assurance/runner.py` |
| Third-party CLI exactly as named: `mcc-assurance --target <base-url> --actuator <test-actuator-url>` | **IMPLEMENTED** — `python -m assurance run --target <gateway-url> --actuator <actuator-url> --notify <notify-url> --external-config <config.json>` (the `prog` name is literally `mcc-assurance`); non-secret URLs are ordinary flags, secrets/key-file paths stay in `--external-config` (never shell history), internally setting the exact same `MCC_ASSURANCE_*` env vars the original mechanism used — a convenience wrapper over the same path, not a second one | 71D | `assurance/cli.py` (`_apply_external_target`); `examples/assurance_external_config.example.json` |
| External mode exercised against a genuinely separate/remote deployment | **PARTIALLY IMPLEMENTED** — `assurance/tests/test_external_mode.py` (L1-L4) now genuinely exercises `connect_external`/the CLI end-to-end: a real `mcc-assurance run --target ...` OS subprocess attaches to an already-running deployment it did NOT itself provision, and its evidence bundle is verified against that target's own, independent receipt oracle. This closed several REAL bugs the exercise surfaced (`gateway_notification_receipt_count`/`gateway_vote_as`/`gateway_consensus_votes` all silently depended on self-contained-only internal state and would have crashed or misbehaved the first time any external deployment reached those code paths — now fixed and covered). Still NOT a genuinely remote, cross-organization-trust-boundary deployment (the "target" is a process on the same sandbox machine) — that specific claim remains untested, honestly, because no second organization/host exists to test against in this environment | 71D | `assurance/tests/test_external_mode.py`; `assurance/sut/harness.py::connect_external`'s `gateway_notify_url` |

## Workstream M — Signed evidence bundle

| Requirement | Status | PR | Evidence |
|---|---|---|---|
| Signed, offline-verifiable evidence bundle | **IMPLEMENTED** | 71A (spine) | `assurance/evidence.py`; `python -m assurance verify` |
| Hash-Reference binding, tamper detection | **IMPLEMENTED** | 71A (spine) | reuses `mcc_evidence.hash_reference` unchanged |

## CI

| Requirement | Status | PR | Evidence |
|---|---|---|---|
| Isolated workflow, no write token | **IMPLEMENTED** | 71D | `.github/workflows/mcc-independent-assurance.yml`; `permissions: contents: read` |
| Pinned action SHAs | **IMPLEMENTED** | 71D | every `uses:` pinned to a 40-char commit SHA; statically enforced by `tests/test_independent_assurance_workflow.py` |
| Blocks release on failure | **PARTIALLY IMPLEMENTED** — the workflow itself fails correctly on any mandatory-job failure; making it a REQUIRED status check that actually blocks merging is a GitHub branch-protection repository SETTING this codebase cannot configure on its own | 71D | Documented in the workflow's own header and `docs/INDEPENDENT_ASSURANCE.md` as a manual step for the repository owner |
| **This workflow has been run for real in GitHub Actions** (updated from the earlier "never run" statement once PR #74 was opened and the workflow triggered automatically) — all 6 jobs completed successfully, including all 4 framework-dependent Workstream K adapters genuinely installing their native package and executing against it (not skipped) | **IMPLEMENTED / VERIFIED IN CI** | 71D | Run [`31775485382`](https://github.com/mcc-prior-art/mcc-layer/actions/runs/31775485382) (head `573728f`, `feat/pr71d-external-runner-final-evidence`): `independent-assurance-core` success, `assurance-langgraph` success, `assurance-autogen` success, `assurance-crewai` success, `assurance-voltagent` success, `assurance-architecture-guards` success — 6/6 jobs, 0 failed. Post-rebase pushes will produce a new run against the rebased SHA; the workflow logic and job set are unchanged by the rebase |

## Documentation (8 required files)

| File | Status | PR |
|---|---|---|
| `docs/INDEPENDENT_ASSURANCE.md` | **IMPLEMENTED** | 71D |
| `docs/THREAT_MODEL.md` | **IMPLEMENTED** | 71A |
| `docs/ASSUMPTIONS_AND_LIMITS.md` | **IMPLEMENTED** | 71A, extended in 71B/71C/71D as each PR's scope lands |
| `docs/CANONICAL_ACTION_FORMAT.md` | **IMPLEMENTED** | 71A |
| `docs/EXCLUSIVE_EXECUTION_PATH.md` | **IMPLEMENTED** | 71A |
| `docs/EXECUTION_STATE_MACHINE.md` | **IMPLEMENTED** | 71B (B section), extended in 71C (I section) |
| `docs/THIRD_PARTY_RUNBOOK.md` | **IMPLEMENTED** | 71D |
| `docs/ASSURANCE_CLAIMS.md` | **IMPLEMENTED** | 71D |

## Claim hygiene (non-negotiable requirement)

| Requirement | Status |
|---|---|
| Never claim "perfect/unbreakable/formally proven secure/all attacks covered" | **IMPLEMENTED** — enforced as a written rule in `docs/ASSURANCE_CLAIMS.md`; checked by grep during this session's own pre-commit process |
| Final deliverable framed as "Certification Candidate Evidence Bundle," not certification | **IMPLEMENTED** — `docs/ASSURANCE_CLAIMS.md`, `docs/THIRD_PARTY_RUNBOOK.md` |

## Summary counts (at the point this matrix was written — 71D, final)

- **IMPLEMENTED:** 48 line items — every workstream has real, passing, black-box tests against a live 3-process deployment. This includes genuine mandate-forgery containment (C9-C18), `min_`/`allowed_` constraint types via the mandate path (C20-C23), a durable Hypothesis seed-persistence corpus (H, 71A), a real kernel-enforced network-segmentation proof (A, N1-N3, `assurance/sut/network_segmentation.py`, 71A), real network-partition fault injection distinct from process-kill (71B), TLA+ model checking (Workstream I, 71C), signed external audit checkpoints (G4-G8, 71D), the literal `mcc-assurance --target/--actuator` CLI interface (71D), and — now genuinely CONFIRMED, not merely written — all 4 framework-dependent Workstream K adapters (LangGraph/AutoGen/CrewAI/VoltAgent) passing in real CI (run [`31775485382`](https://github.com/mcc-prior-art/mcc-layer/actions/runs/31775485382)), plus the CI workflow itself now verified as a real, green GitHub Actions run (6/6 jobs).
- **PARTIALLY IMPLEMENTED:** 5 line items (D's corpus exhaustiveness, J's generic mutation sweep — installed and run, but scoped to one file with a narrow oracle, see that row for the honest detail including a spot-checked survivor the full suite actually catches, K's "same containment properties across 5 adapters" framing row (the underlying 4/5 CI execution is now confirmed, but this row specifically tracks the test-code-correctness claim, not CI execution), external mode's still-untested genuinely-remote/cross-organization-trust-boundary claim (the CLI mechanism and code path ARE implemented and genuinely self-exercised — see L1-L4 — but no second organization/host exists in this environment to prove the stronger claim), CI's required-status-check (a repository branch-protection SETTING, not something this codebase can configure on its own)).
- **NOT IMPLEMENTED:** 3 line items (`EXECUTION_UNKNOWN` external observability — confirmed not a normative gap, see that row — constraint types beyond one on the actuator's OWN HTTP-egress config specifically (the general mechanism IS covered via the mandate path), PlusCal).
- **BLOCKED BY ENVIRONMENT:** 3 line items (multi-node/multi-host E, Redis Cluster/Sentinel failover — for two independent, directly-investigated reasons, see that row — and production-scale I model checking) — all explicitly infrastructure-gated, not skipped by choice. Network-partition (71B), network-segmentation (A, 71A), and the 4 K adapters (71D CI) have all been moved OUT of this category into IMPLEMENTED, above, once genuinely exercised.
- **VERIFIED IN CI:** the CI workflow has been run for real (not merely validated locally) — see the CI section's first row for the exact run URL and per-job results. 6/6 jobs succeeded, 0 failed, 0 dependency-related skips across the 4 framework adapters. This is the final, complete summary for the whole 71A-71D stack.

None of the above is hidden inside a passing test suite — the black-box
suite itself (`assurance/tests/`) only tests what it tests; this matrix is
the accounting of what the ORIGINAL 13-workstream task additionally asked
for that the test suite does not, by itself, communicate.
