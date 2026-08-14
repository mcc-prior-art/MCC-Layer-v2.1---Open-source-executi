# Reproducing the Assurance Baseline

A truthful, clean-checkout reproduction path for what PRs #71-#74 (the MCC-Core
Independent Adversarial Assurance Baseline) actually verify. This document
exists because `docs/THIRD_PARTY_RUNBOOK.md` predates a single, tested,
one-command entry point (`make verify-assurance`) and because the repository
previously had no `make verify` target at all, despite that command appearing
in informal descriptions of "how to check this." This is the correct,
current, tested command.

If you take away one thing from this document, take the disclaimer in
["Verified scope and limitations"](#verified-scope-and-limitations) below.

## Prerequisites and required tool versions

- **Python 3.11+** (this repository is validated on 3.11)
- **`redis-server` and `redis-cli`** on `PATH` — Workstream E (replay
  resistance) drives a real, shared Redis instance
- **Java 11+** — Workstream I (TLA+ model checking); `model/run_tlc.sh`
  downloads the TLC jar itself on first run and this repository was
  validated on Java 21. Requires outbound network access on that first run
  only (to `github.com/tlaplus/tlaplus/releases`); the jar is cached
  in `model/tools/` (git-ignored) after that.
- Optional: **Node 22** + the framework packages in
  `tests/interoperability/requirements-{langgraph,autogen,crewai}.txt` if
  you want Workstream K's four framework-specific adapters to run locally
  instead of being skipped (they always run in CI regardless — see
  `.github/workflows/mcc-independent-assurance.yml`)

## Clean-clone instructions

```bash
git clone https://github.com/mcc-prior-art/mcc-layer
cd mcc-layer
```

## Exact commit-checkout procedure

Reproduction claims are only meaningful *at a specific commit* — this
document itself is not evidence of anything at a commit other than the one
it ships with. Find that commit and check it out explicitly:

```bash
# The exact commit this copy of the document was committed at:
git log -1 --format=%H -- docs/REPRODUCING_ASSURANCE.md

# Check out the commit you actually intend to verify (substitute the SHA
# you got from CI, a PR, or the line above):
git checkout <commit-sha>
git status --short   # must print nothing -- confirms a genuinely clean checkout
```

Never verify against a branch tip that can move under you (`main`,
`HEAD`) — always pin an exact, full 40-character commit SHA, and state that
SHA when you report a result.

## Install dependencies

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

## Run the reproducible entry point

```bash
make verify-assurance
```

This runs, in order, and fails immediately if any stage fails:

1. `make independent-assurance` — every workstream test module under
   `assurance/tests/` (Workstreams A-K + the negative control), against a
   real, locally-provisioned three-process deployment (Gateway, `egress_proxy`
   actuator, mock external-effect sink). Writes a signed evidence bundle to
   `artifacts/independent-assurance` (git-ignored).
2. `model/run_tlc.sh` — exhaustive, bounded TLA+ model checking of
   `model/MCCExecutionStateMachine.tla` against every `INVARIANT`/`PROPERTY`
   in `model/MCCExecutionStateMachine.cfg` (the default, small configuration:
   720 states).
3. `make mutation-test` — runs every `Defect` in `mutation/defects.py`
   (26 entries) through `mutation/harness.py`: each is applied to an
   isolated copy of the repository and a real pytest subprocess proves the
   named detector test(s) actually catch it.

`scripts/verify_assurance.sh` (what `make verify-assurance` calls) also
checks, before and after all three stages, that `git status --porcelain
--untracked-files=no` is empty — i.e. that the tracked working tree is
byte-for-byte unchanged. It never cleans, resets, restores, checks out, or
deletes anything to *produce* that result; if a stage genuinely leaves
tracked files modified, the script reports exactly which paths and fails
(exit 9) rather than repairing it. See that script's own header comment for
the complete exit-code table, and an important note: `make`'s own top-level
exit code is always `0` or `2` (a fixed GNU Make convention, not something
this repository controls) — invoke `scripts/verify_assurance.sh` directly
instead of through `make` if you need the *exact* originating exit code of
whichever stage failed.

## Expected successful results

- `make independent-assurance` exits `0`; the run prints a per-workstream
  pass count and `overall_status: PASS` in the written evidence bundle.
  Some tests are expected to be **skipped**, not failed, when optional
  local tooling (Docker, the four Workstream K frameworks) is absent — see
  `docs/ASSUMPTIONS_AND_LIMITS.md` for exactly which and why; those same
  paths run for real, unskipped, in CI.
- `model/run_tlc.sh` exits `0` and prints TLC's own "Model checking
  completed. No error has been found." for every checked `INVARIANT`/
  `PROPERTY`.
- `make mutation-test` exits `0` and prints
  `"total": 26, "detected": 26, "mutation_score": 1.0, "survived_defect_ids": []`.
- `make verify-assurance` prints `== verify-assurance: PASS ==` and exits
  `0`; `git status --short` is empty both before and after the whole run.

## Verified scope and limitations

> PRs #71-#74 verify, under this repository's self-administered harness and
> at the tested commit, the documented fail-closed properties, 24
> adversarial gate-bypass attempts, bounded TLC model properties, and the
> declared mutation corpus. They do not establish universal safety or
> constitute a third-party audit.

Read that sentence twice. Specifically:

- **This is a self-administered harness.** Every test, model, and mutant in
  this repository was written by the same people who wrote the code it
  checks. Passing it means the code does what its own authors, testing
  adversarially, could get it to prove — not what an unaffiliated,
  independent auditor would find. See ["What this is not"](#relationship-to-docsthird_party_runbookmd)
  below for how this differs from `docs/THIRD_PARTY_RUNBOOK.md`'s framing.
- **The 24 gate-bypass attempts are a specific, named, finite list** — see
  the table below. They are not exhaustive; a bypass technique nobody on
  this project has thought of is, by construction, untested.
- **The TLC model checks a small, bounded instance** (720 states by
  default; a documented, non-default 76,440-state validation configuration
  exists too). This is how exhaustive model checking works — TLC's "no
  error found" is a claim about the specific bounded instances checked, not
  an inductive proof for arbitrary N. See
  `model/MCCExecutionStateMachine.tla`'s own module docstring.
- **The mutation corpus is 26 specific, hand-authored (or systematically
  swept, for the 14-site gate.py block) mutants** — not a claim that every
  possible one-line regression in this codebase would be caught. A
  companion generic `mutmut` sweep exists (`pyproject.toml`'s
  `[tool.mutmut]`) and is scoped narrowly to `src/mcc_core/gate.py`; see
  `docs/ASSUMPTIONS_AND_LIMITS.md` for its own honest caveats.
- **Results apply only to the exact commit you checked out and the scope
  documented here.** A different commit, a different environment, or a
  claim broader than the sentence above is not something this reproduction
  procedure supports.

## The 24 documented gate-bypass attempts

Definition used: a test that attempts to execute an action without a valid
ALLOW-equivalent authorization — forged signature, replayed
nonce/challenge, wrong trust domain, or a direct call past canonical
ingress — through a real, live SUT, where the pass condition is both the
SUT's own reported status **and** an independently-observed external-effect
counter never advancing. Positive-baseline tests (proving the happy path
works) and payload-constraint tests (a *valid* token whose payload gets
clamped or denied) are deliberately excluded — they are not bypass attempts.

`assurance/tests/test_exclusive_execution_path.py` (Workstream A, 8 attacks):

| Line | Test |
|---|---|
| 57 | `test_a1_direct_actuator_invocation_without_consensus` |
| 69 | `test_a2_stolen_endpoint_wrong_client_credential` |
| 83 | `test_a3_reused_credential_replayed_challenge` |
| 104 | `test_a4_adapter_to_actuator_bypass_wrong_trust_domain` |
| 122 | `test_a5_agent_to_actuator_bypass_self_signed_forged_evaluator` |
| 142 | `test_a6_alternate_network_route_disallowed_host` |
| 158 | `test_a7_forged_gate_identity_tampered_signature` |
| 177 | `test_a8_valid_token_direct_to_actuator_wrong_binding` |

`assurance/tests/test_decision_authority_containment.py` (Workstream C, 7
attacks; `test_c1_authorized_consensus_reaches_the_gateway_upstream` is the
positive baseline and is not counted):

| Line | Test |
|---|---|
| 91 | `test_c2_below_threshold_votes_denied` |
| 107 | `test_c3_trusted_deny_vote_vetoes_despite_sufficient_allow_votes` |
| 129 | `test_c4_votes_bound_to_wrong_policy_hash_rejected` |
| 144 | `test_c5_votes_bound_to_a_different_actor_rejected` |
| 159 | `test_c6_forged_untrusted_evaluator_rejected_at_gateway` |
| 174 | `test_c7_replayed_challenge_and_votes_denied_after_first_use` |
| 192 | `test_c8_mandate_execute_fails_closed_on_the_consensus_required_topology` |

`assurance/tests/test_mandate_containment.py` (9 attacks;
`test_c9_genuine_mandate_executes` is the positive baseline,
`test_c19_replayed_mandate_still_only_executes_what_it_authorizes` documents
legitimate mandate reusability rather than testing a bypass, and
`test_c20`-`test_c23` test constraint-clamping of a *valid* mandate — none
of these four are counted):

| Line | Test |
|---|---|
| 89 | `test_c10_forged_mandate_untrusted_issuer_is_denied` |
| 102 | `test_c11_tampered_action_scope_is_denied` |
| 119 | `test_c12_tampered_subject_is_denied` |
| 135 | `test_c13_expired_mandate_is_denied` |
| 149 | `test_c14_not_yet_valid_mandate_is_denied` |
| 163 | `test_c15_wrong_subject_at_call_time_is_denied` |
| 178 | `test_c16_action_outside_scope_is_denied` |
| 192 | `test_c17_resource_outside_scope_is_denied` |
| 206 | `test_c18_revoked_mandate_is_denied` |

**Result at the time this document was written: 0 of these 24 succeeded** —
verified by direct execution, not inferred from the wider test suite.

**Not counted, and why:** a Redis-atomicity concurrency test exists —
`tests/test_nonce.py:167` (`test_concurrent_consumption_permits_exactly_one_winner`,
64 concurrent claims on one nonce, exactly 1 winner asserted) — but it
predates PRs #71-#74 entirely (added in commit `bef7f2d`, before the 71A-D
branch range) and is excluded from the 24 above for that reason, not because
it is unimportant. Its mechanism is Redis's atomic `SET NX EX`
(`src/mcc_core/nonce.py`) — **not a Lua script** — correct that assumption
if you see it stated elsewhere.

## The mutation corpus

Path: **`mutation/defects.py`** — 26 `Defect` entries (a frozen dataclass:
`id`, `description`, `file_path`, `find`, `replace`, `detector_tests`), run
by `mutation/harness.py` against an isolated repository copy per mutant, via
real `pytest` subprocesses. `python -m mutation` (what `make mutation-test`
runs) exits `0` only if every defect is detected.

### Structure of `mutation/defects.py`

Each `Defect` is one hand-chosen, plausible, one-line regression of a named
security property:

```python
Defect(
    id="short-unique-slug",                       # stable identifier
    description="What security property this regression breaks.",
    file_path="src/mcc_core/some_module.py",       # repo-relative
    find='exact source substring, present exactly once',
    replace='the mutated substring',
    detector_tests=("tests/test_some_module.py::test_that_should_fail",),
)
```

`mutation/harness.py`'s `apply_mutation` requires `find` to appear **exactly
once** in the target file — if a future refactor moves or duplicates that
text, the harness raises loudly (`MutationHarnessError`) instead of silently
mutating nothing or the wrong thing.

### How to add a new mutant

1. Pick a real, specific security-relevant one-line change — the kind of
   thing that could survive code review.
2. Add a `Defect(...)` entry to the `DEFECTS` list in `mutation/defects.py`,
   with a unique `id` and an exact, currently-unique `find` substring.
3. Identify (or write) the test(s) that must fail against the mutated code
   — these go in `detector_tests` as `path/to/test_file.py::test_name`
   node IDs. Reuse an existing test if one already proves the property;
   only add a new one (in `tests/`, `assurance/tests/`, or — if it needs a
   fixture specific to this mutation and doesn't fit either existing
   convention — `mutation/detectors.py`, following that module's own
   docstring) if none does.
4. Run the harness (below) and confirm your new defect shows `DETECTED`,
   not `SURVIVED`. A defect that survives its own detector test is not
   ready to submit — either the detector test is wrong, or you have found a
   genuine, reportable gap (in which case, fix the gap first, in a separate
   commit, then add the now-passing defect).

### How to run the harness

```bash
PYTHONPATH=. python -m mutation                          # human-readable + JSON summary
PYTHONPATH=. python -m mutation --output report.json      # also write the full report
```

### Expected result format

```json
{
  "total": 26,
  "detected": 26,
  "mutation_score": 1.0,
  "survived_defect_ids": []
}
```

Exit code `0` iff `survived_defect_ids` is empty. Any non-empty list there
is a genuine, reportable coverage gap — never silently dropped or
reclassified to make the score look better (see `mutation/defects.py`'s own
module docstring, which states this as a hard rule).

### How external contributors submit additions

There is no separate registration step or plugin system — `mutation/defects.py`
is a plain Python list. To propose a new mutant or a new gate-bypass test:

1. Fork the repository, create a branch.
2. Add your `Defect` entry (mutation) or test function (bypass attempt),
   following the conventions above and the existing file's style.
3. Run `PYTHONPATH=. python -m mutation` (for a new defect) and/or the
   relevant `pytest` file (for a new bypass test) locally and include the
   output in your pull request description.
4. Open a pull request against this repository. State explicitly, in the
   PR description, whether your addition is a new `Defect` (mutation), a
   new bypass-attempt test, or both, and update the relevant count in this
   document (the "24" and "26" above) if your PR changes it — a stale count
   here is itself a bug.
5. The repository owner reviews and is the sole merge authority — the same
   as every other change to this repository (see `README.md`'s "Reproduce
   the Assurance Baseline" section and the fact that every PR in this
   history says "do not merge" pending owner review).

This procedure is what makes the corpus **externally extensible**: a public
repository alone does not make something extensible if there is no
documented path to propose an addition. As of this document, that path
exists and is testable end-to-end with the two commands above.

## Relationship to `docs/THIRD_PARTY_RUNBOOK.md`

That document predates this one and describes the same underlying
mechanism (`assurance/`, `model/`, `mutation/`) but used "third-party" and
"independent" language more broadly than is accurate for a
self-administered test suite run by the same people who wrote the code.
This document is the current, corrected entry point;
`docs/THIRD_PARTY_RUNBOOK.md` has been updated to point here for the
one-command reproduction path and to state plainly which parts of its own
content are, and are not, evidence of genuine third-party operation. Use
this document for "how do I reproduce this," and that one for the external
(`--target`/`--actuator`) deployment mode it documents, which remains a
capability of this codebase, not a claim that anyone unaffiliated has
exercised it.

## A warning about scope

Every result in this document — the exit codes, the 24/24, the 26/26 —
applies **only** to the exact commit you checked out and **only** to the
scope stated above. It is not evidence about any other commit, any
deployment configuration this repository doesn't test, or any property not
named in the sentence at the top of ["Verified scope and
limitations"](#verified-scope-and-limitations). If you need a claim broader
than that, this reproduction procedure does not give you one, and neither
does the rest of this repository.
