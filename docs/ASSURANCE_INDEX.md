# Assurance Index

Short navigation page for the MCC-Core assurance baseline. If you only read
one line here: **this is a self-administered reproducible assurance
baseline, not a third-party audit.**

## One-command verification

```bash
make verify-assurance
```

Runs, in order, and fails fast: `independent-assurance` (the black-box
adversarial test suite), `model/run_tlc.sh` (bounded TLA+ model checking),
`mutation-test` (the mutation corpus). See
[Reproducing Assurance](REPRODUCING_ASSURANCE.md) for prerequisites, the
exact clean-clone and pinned-commit checkout procedure, and expected
results before you run it.

## Where to go next

| If you want... | Go to |
|---|---|
| The full reproduction procedure (prerequisites, checkout, expected results, verified scope) | [docs/REPRODUCING_ASSURANCE.md](REPRODUCING_ASSURANCE.md) |
| The external-target (`Mode 2`) runbook and `MCC_ASSURANCE_*` environment variables | [docs/THIRD_PARTY_RUNBOOK.md](THIRD_PARTY_RUNBOOK.md) |
| The adversarial gate-bypass test suite itself | [assurance/tests/](../assurance/tests/) |
| The mutation-testing defect corpus | [mutation/defects.py](../mutation/defects.py) |
| The formal execution-state-machine model | [model/MCCExecutionStateMachine.tla](../model/MCCExecutionStateMachine.tla) |

## Boundary

This baseline is self-administered: every test, model, and mutant here was
written by the same people who wrote the code it checks. It verifies a
specific, documented, finite set of properties at the commit you check
out — not universal safety, and not third-party certification. See
[Reproducing Assurance § Verified scope and limitations](REPRODUCING_ASSURANCE.md#verified-scope-and-limitations)
for the exact, non-overstated claim.

## Reviewer flow

```text
README
  -> docs/ASSURANCE_INDEX.md
  -> docs/REPRODUCING_ASSURANCE.md
  -> make verify-assurance
```
