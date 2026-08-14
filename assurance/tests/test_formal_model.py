"""Workstream I -- Formal Model Checking (PR #71).

A thin wrapper, not a black-box SUT test: unlike every other module in
this directory, this one never touches the live three-process deployment
at all (no ``sut`` fixture) -- it shells out to TLC (``model/run_tlc.sh``)
against ``model/MCCExecutionStateMachine.tla``, the independent formal
model of the execution lifecycle (see that file's own docstring for what
it does and does not prove). Included here so ``python -m assurance run``
surfaces the formal-model result in the SAME evidence bundle as every
black-box workstream, rather than as a separate, easy-to-forget step.

TLC downloads its own tool jar on first run (git-ignored, never vendored --
see ``model/run_tlc.sh``); that download requires outbound network access.
If it is unavailable, this test is skipped (not silently passed) with an
explicit reason, and CI's dedicated formal-model job -- which runs on a
runner with network access -- remains the authoritative check.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
RUN_TLC = REPO_ROOT / "model" / "run_tlc.sh"


def _java_available() -> bool:
    return shutil.which("java") is not None


@pytest.mark.skipif(not _java_available(), reason="java is not installed in this environment")
def test_i1_tla_model_checks_clean_with_no_violations():
    result = subprocess.run(
        [str(RUN_TLC)], cwd=str(REPO_ROOT), capture_output=True, text=True, timeout=180,
    )
    if result.returncode == 3 and "TLC_JAR_DOWNLOAD_FAILED" in result.stderr:
        pytest.skip("no outbound network access to download tla2tools.jar in this environment")

    assert result.returncode == 0, (
        f"TLC reported a property violation or error (exit {result.returncode}):\n"
        f"{result.stdout[-4000:]}\n{result.stderr[-2000:]}"
    )
    assert "Model checking completed. No error has been found." in result.stdout
