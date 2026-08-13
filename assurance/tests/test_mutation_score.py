"""Workstream J -- Mutation Testing (PR #71).

A thin wrapper, like ``test_formal_model.py``: this does not touch the
live SUT (no ``sut`` fixture). It runs the real mutation harness
(``mutation.harness.run_all_mutants``) against all 13 targeted defects and
asserts 100% detection, so ``python -m assurance run`` surfaces the
mutation score in the same evidence bundle as every other workstream.

Each mutant boots its own isolated repo copy and runs real pytest
subprocesses (see ``mutation/harness.py``), so this is slower than the
rest of the suite (~30s for all 13) -- deliberately not folded into a
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
    assert report.total == 13
