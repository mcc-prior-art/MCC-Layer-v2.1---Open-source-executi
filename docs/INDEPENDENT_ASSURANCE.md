# MCC-Core Independent Adversarial Assurance Baseline (PR #71)

A hermetic, implementation-independent, black-box assurance system that
tests MCC-Core's central invariant — *"no verified authority, no
execution"* — strictly through its public protocol/API boundary, against a
real, live, multi-process deployment. No test under `assurance/tests/`
imports MCC-Core's internal authority, policy, gate, nonce, audit,
certification, or execution modules (enforced by an AST-based CI guard,
`assurance/tests/test_boundary_guards.py`).

## Start here

- **Running it yourself:** `docs/THIRD_PARTY_RUNBOOK.md` (self-contained
  and genuine external-target modes)
- **What is claimed, precisely:** `docs/ASSURANCE_CLAIMS.md`
- **Who the assumed adversary is:** `docs/THREAT_MODEL.md`
- **What is NOT covered:** `docs/ASSUMPTIONS_AND_LIMITS.md`
- **Deep dives:** `docs/EXCLUSIVE_EXECUTION_PATH.md` (Workstream A),
  `docs/EXECUTION_STATE_MACHINE.md` (B/I), `docs/CANONICAL_ACTION_FORMAT.md`
  (D)

```bash
make independent-assurance          # the whole black-box suite -> signed evidence bundle
model/run_tlc.sh                    # the formal model (Workstream I)
python -m mutation                  # the 13 targeted mutations (Workstream J)
```

## Architecture

```
assurance/
├── sut/                  # PROVISIONING (may import MCC-Core internals --
│   ├── harness.py        # it is DEPLOYING the system, not testing it)
│   ├── actuator_process.py    real egress_proxy actuator, as a genuine OS subprocess
│   ├── notify_process.py      real pilot_notify external-effect sink
│   ├── replay_cluster.py      two actuators + one real redis-server (Workstream E)
│   └── vulnerable_target.py   the DELIBERATELY broken negative control
├── tests/                # BLACK-BOX ONLY (AST-guarded: no MCC-Core internals)
│   ├── test_boundary_guards.py         the guard itself
│   ├── test_exclusive_execution_path.py       Workstream A (8 attacks)
│   ├── test_execution_atomicity.py            Workstream B (state machine + fault injection)
│   ├── test_decision_authority_containment.py Workstream C
│   ├── test_canonical_action_differential.py  Workstream D
│   ├── test_replay_resistance.py              Workstream E
│   ├── test_constraint_enforcement.py         Workstream F
│   ├── test_audit_survivability.py            Workstream G
│   ├── test_property_based.py                 Workstream H (hypothesis)
│   ├── test_formal_model.py                   Workstream I wrapper (shells to model/)
│   ├── test_mutation_score.py                 Workstream J wrapper (shells to mutation/)
│   ├── test_semantic_equivalence.py           Workstream K (5 adapters)
│   └── test_negative_control.py               the control arm
├── canonical_action.py   # independent reimplementation (Workstream D)
├── state_machine.py      # the 8-state reference model (Workstream B)
├── evidence.py            # signed evidence bundle builder/verifier (Workstream M)
├── runner.py              # discovers + runs every workstream module (Workstream L)
└── cli.py                 # `python -m assurance {run,verify,list-workstreams}`

model/                     # Workstream I: TLA+ formal model + TLC runner
mutation/                  # Workstream J: 13 targeted mutations + harness
```

## The provisioning/test boundary, precisely

`assurance/sut/` constructs the real deployment as literal, separate OS
processes reached only over real loopback HTTP — it needs MCC-Core
internals (`mcc_core.signing`, `mcc_core.consensus.issue_vote`) to build
that deployment and to construct attacker-side artifacts (a forged vote is
signed with the SAME public Ed25519 primitives a real attacker has
access to — see `assurance/sut/harness.py::forge_vote`'s docstring for
why that is not a governance bypass).

`assurance/tests/` reaches the SUT **only** through `SystemUnderTest`'s
public HTTP-facing attributes and helper methods, or through raw `httpx`
calls to a documented endpoint — never through an import of `mcc_core.gate`,
`mcc_core.authority`, `egress_proxy`, `gateway`, or any other security
internal. This is checked mechanically, not just by convention: every
`.py` file under `assurance/tests/` is parsed with `ast` and checked
against both a forbidden-module denylist and an allowed-import-prefix
allowlist on every CI run.

## The thirteen workstreams

| Letter | Name | Doc |
|---|---|---|
| A | Exclusive execution path | `docs/EXCLUSIVE_EXECUTION_PATH.md` |
| B | Execution atomicity / state machine | `docs/EXECUTION_STATE_MACHINE.md` |
| C | Decision authority containment | (this doc + `docs/ASSURANCE_CLAIMS.md`) |
| D | Canonical action format | `docs/CANONICAL_ACTION_FORMAT.md` |
| E | Replay resistance | `docs/ASSUMPTIONS_AND_LIMITS.md` (scope) |
| F | Constraint enforcement | `docs/ASSURANCE_CLAIMS.md` |
| G | Audit survivability | `docs/THREAT_MODEL.md` (adversary #6) |
| H | Property-based / stateful testing | `docs/ASSURANCE_CLAIMS.md` |
| I | Formal model (TLA+) | `docs/EXECUTION_STATE_MACHINE.md` |
| J | Mutation testing | `mutation/defects.py`'s own docstrings |
| K | Five-adapter semantic equivalence | `docs/ASSUMPTIONS_AND_LIMITS.md` (scope) |
| — | Negative control | `docs/THREAT_MODEL.md` (adversary #7) |
| L/M | Runner spine + signed evidence bundle | this doc's Architecture section |

## Evidence bundle

`python -m assurance run --output DIR` writes a **Certification Candidate
Evidence Bundle**: `manifest.json` (schema `mcc-independent-assurance-
evidence/1`, a Hash Reference binding to the findings file, optionally
Ed25519-signed) plus `findings/workstream_results.json` (every test's
outcome). `python -m assurance verify --bundle DIR` recomputes and checks
it offline, reporting `INTACT`, `INTACT_UNTRUSTED_SIGNER`, or `INVALID` —
never fabricating a pass. This is deliberately NOT the same schema as
`mcc_evidence`'s Governance Evidence Bundle (evidence of one governed
decision) — see `assurance/evidence.py`'s module docstring for why a
second, structurally different bundle format was the correct choice
rather than forcing this into the existing one.

## CI

`.github/workflows/mcc-independent-assurance.yml` — a dedicated, isolated
workflow (read-only permissions throughout, every third-party action
pinned to a full commit SHA, no `GITHUB_TOKEN`/secrets referenced). The
mandatory `independent-assurance-core` job runs the black-box suite, the
formal model, and mutation testing; `assurance-architecture-guards` runs
the boundary guard standalone; one job per framework
(`assurance-langgraph`/`-autogen`/`-crewai`/`-voltagent`) proves Workstream
K's remaining four adapters are genuinely exercised, not silently skipped,
in an environment where each framework IS installed.

**Repository configuration this workflow file cannot itself perform:**
making it a required status check (so a failing run blocks merging/
release) is a GitHub branch-protection SETTING — a manual step for AX in
the repository's settings, not something achievable in YAML.

## Non-goals (repeated from the originating task, for completeness)

- This is not a claim of "unbreakable," "formally proven secure," or "all
  attacks covered." See `docs/ASSURANCE_CLAIMS.md`'s claim-hygiene rules.
- The final deliverable is a Certification Candidate Evidence Bundle, not
  independent certification. Genuine independent certification begins
  only when an unaffiliated third-party reviewer controls execution,
  reviews the threat model, verifies environment/source revision, signs
  their own findings, and publishes their own conclusions — see
  `docs/THIRD_PARTY_RUNBOOK.md`'s final section.
