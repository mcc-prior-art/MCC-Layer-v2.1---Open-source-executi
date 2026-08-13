# Assurance Claims Register (PR #71)

This document is the authoritative register of exactly what the
Independent Adversarial Assurance Baseline claims, per workstream, and
exactly what language is and is not permitted when describing it. When
this document and any other prose (a commit message, a README, a
marketing page) disagree, THIS document controls.

## Non-negotiable claim hygiene

**Never claim:** "perfect", "unbreakable", "formally proven secure", "all
attacks covered", "fully verified", "guaranteed secure", or any
unqualified absolute.

**The only permitted conclusion:**

> MCC-Core, at commit `<source_commit_sha>`, satisfies the tested
> normative invariants under the declared threat model
> (`docs/THREAT_MODEL.md`), the stated deployment assumptions and limits
> (`docs/ASSUMPTIONS_AND_LIMITS.md`), the implementation version, and the
> test environment recorded in the evidence bundle.

Every claim below is written to fit inside that sentence. If a sentence in
this document could not be truthfully appended after "MCC-Core satisfies
the tested normative invariant that...", it does not belong here.

## Per-workstream claims

| Workstream | Claim | Evidence | Does NOT claim |
|---|---|---|---|
| **A** Exclusive execution path | The actuator never reports `executed=true` without a verified consensus, against 8 named attack classes | `assurance/tests/test_exclusive_execution_path.py`, `docs/EXCLUSIVE_EXECUTION_PATH.md` | Immunity to attacks outside the 8 named classes; network-segmentation guarantees (A6 caveat) |
| **B** Execution state machine | Real fault injection (a hard-killed external-effect process) never causes a false `executed=true`; a same-idempotency-key retry after recovery executes exactly once | `assurance/tests/test_execution_atomicity.py`, `docs/EXECUTION_STATE_MACHINE.md` | That `EXECUTION_UNKNOWN` is ever externally observable as a distinct status (documented as an implementation choice, not tested as absent) |
| **C** Decision authority containment | The Gateway's own `/consensus/*` API enforces the same containment property as the actuator, against 7 attacks plus one documented mandate-path limitation | `assurance/tests/test_decision_authority_containment.py` | Genuine-vs-forged SIGNED MANDATE containment (no mandate trust is configured in this SUT — C8) |
| **D** Canonical action format | An independently written second implementation of the canonical action format agrees with the real actuator on action_hash for a 25-case corpus (15 valid, 10 malformed) | `assurance/tests/test_canonical_action_differential.py`, `docs/CANONICAL_ACTION_FORMAT.md` | Agreement on inputs outside the corpus; absence of a shared blind spot both implementations happen to share |
| **E** Replay resistance | A nonce/challenge consumed on one actuator process cannot be reused on a second, independent process sharing one real Redis instance; the actuator fails closed if that backend is unreachable | `assurance/tests/test_replay_resistance.py` | Multi-node cluster/failover behavior, or a real network partition between hosts (no such infrastructure was available — see `docs/ASSUMPTIONS_AND_LIMITS.md`) |
| **F** Constraint enforcement | The original, excessive value in a CONSTRAIN scenario never executes; only the clamp — verified via an independently computed hash — ever does; resubmitting the original value as "constrained" is refused | `assurance/tests/test_constraint_enforcement.py` | Constraint enforcement for constraint types other than the one configured (`max_body.amount`) |
| **G** Audit survivability | The audit chain stays internally consistent across a mix of successful and rejected operations, and is genuinely tamper-EVIDENT (a direct on-disk edit flips verification to invalid) | `assurance/tests/test_audit_survivability.py` | Tamper-*proof* (the on-disk tamper test assumes filesystem access — a materially different, weaker guarantee than network-attacker resistance; see `docs/THREAT_MODEL.md`) |
| **H** Property-based / stateful testing | 200 generated canonicalization examples are internally consistent; 25 generated inputs agree with the real actuator; an 8-example, 6-step randomized interleaving of genuine/forged/replayed votes never produces an execution count exceeding the model's own count of genuine authorizations | `assurance/tests/test_property_based.py` | Coverage of the full input space (Hypothesis explores a bounded, randomly-seeded slice per run) |
| **I** Formal model (TLA+) | Six named properties (type-safety, no double nonce consumption, terminal-state stability, fail-closed while the backend is down, executed-implies-authorized, eventual termination under fairness) hold across every reachable state of a small, bounded, abstract model | `model/MCCExecutionStateMachine.tla`, `docs/EXECUTION_STATE_MACHINE.md` | That the Python implementation follows this model (a SEPARATE, black-box claim — see the B row above); anything about instances larger than the checked configurations |
| **J** Mutation testing | 13 specific, hand-authored, security-critical code mutations are each independently detected by a named test | `mutation/defects.py`, `mutation/harness.py` | Coverage of mutations outside this named set of 13; that the detector tests themselves are bug-free |
| **K** Five-adapter semantic equivalence | The same containment properties (authorized execution, forged-vote rejection, replay rejection) hold for proposals originated by five different frameworks | `assurance/tests/test_semantic_equivalence.py` | That all five ran in this specific environment (only generic-http did locally — the other four are CI-job-gated; see `docs/ASSUMPTIONS_AND_LIMITS.md`) |
| **Negative control** | The identical test methodology correctly reports FAILURE against a system missing the invariants (auth, SSRF, consensus, replay protection) | `assurance/tests/test_negative_control.py` | Anything about the real system — this is the control arm, proving the methodology discriminates |

## What "Certification Candidate Evidence Bundle" means

The signed output of `python -m assurance run` (see
`assurance/evidence.py`) is called a **Certification Candidate Evidence
Bundle**, deliberately — never "certification," never "certified." It is
evidence a reviewer can inspect and verify offline; it becomes
independent certification only through the process described in
`docs/THIRD_PARTY_RUNBOOK.md`'s final section, which no automated system
can perform on its own behalf.

## Relationship to other certification artifacts in this repository

This baseline is distinct from, and does not supersede or duplicate:

- `mcc_certify`'s ecosystem certification (PR #69) — certifies that FIVE
  ADAPTERS conform to the Integration Contract, using a KNOWN-GOOD
  reference implementation as the test oracle. This baseline instead asks
  whether MCC-Core's OWN invariants survive ADVERSARIAL pressure.
- `mcc_evidence`'s Governance Evidence Bundle (PR #42) — evidence of one
  ALREADY-COMPLETED governed decision. This baseline's evidence bundle is
  evidence of an ASSURANCE RUN, a structurally different artifact (see
  `assurance/evidence.py`'s own module docstring).
- The official signing ceremony (PR #70) — a PRODUCTION KEY / RELEASE
  PACKAGING process for certified adapters. This baseline never touches
  production signing material and has no bearing on official certificate
  issuance.
