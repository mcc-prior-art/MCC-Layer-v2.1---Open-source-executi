"""Workstream J -- Mutation Testing (PR #71).

A thin wrapper, like ``test_formal_model.py``: this does not touch the
live SUT (no ``sut`` fixture). It runs the real mutation harness
(``mutation.harness.run_all_mutants``) against all 26 targeted defects and
asserts 100% detection, so ``python -m assurance run`` surfaces the
mutation score in the same evidence bundle as every other workstream.

The 26 = the original 13 hand-picked security defects + a later addition:
an exhaustive sweep of all 14 ``GateResult(False, ...)`` fail-open sites in
``src/mcc_core/gate.py`` (13 new + the pre-existing ``gate-fail-open``,
which already covered one of the 14 -- see ``mutation/defects.py``). That
addition closed a gap a direct-verification mutation-testing addendum
found: 2 of the 14 gate fail-open sites were not caught by a reasonable
hand-selected test oracle. Both are now permanently, individually asserted
here, not just informally re-checked once.

Each mutant boots its own isolated repo copy and runs real pytest
subprocesses (see ``mutation/harness.py``), so this is slower than the
rest of the suite (~40s for all 26) -- deliberately not folded into a
tighter loop, since a mutation result silently downgraded to "good enough"
would defeat the entire point of Workstream J.
"""

from __future__ import annotations

from mutation.harness import run_all_mutants


def test_j1_every_targeted_defect_is_detected():
    report = run_all_mutants(timeout=120.0)

    survived_detail = "\n".join(
        f"  - {r.defect_id}: {r.description}" for r in report.survived
    )
    assert not report.survived, (
        f"{len(report.survived)}/{report.total} targeted mutations SURVIVED "
        f"(not caught by their detector tests):\n{survived_detail}"
    )
    assert report.mutation_score == 1.0
    assert report.total == 26
