"""Workstream L (extended) -- Genuine External/Third-Party Mode Exercise (PR #71).

``connect_external``/the CLI's ``--target``/``--actuator``/``--notify``/
``--external-config`` flags (``assurance/cli.py``) were, until this file,
written and reviewed but never actually exercised end-to-end -- a stated,
honest gap in ``docs/ASSUMPTIONS_AND_LIMITS.md``.

This closes that gap AS FAR AS IS ACTUALLY ACHIEVABLE in a single sandbox:
there is no genuinely separate organization or remote host here to act as
a third party. What this file DOES prove, honestly:

* The real ``mcc-assurance`` CLI entry point (invoked as a genuine OS
  subprocess: ``python -m assurance run --target ... --actuator ...
  --notify ... --external-config ...``, never an in-process function
  call) successfully attaches to an ALREADY-RUNNING deployment it did
  NOT itself provision (booted here via ``build_system_under_test`` to
  stand in for "a third party's own deployment"), using only the public
  HTTP URLs and a config file of credentials -- the exact mechanism a
  genuine external operator would use.
* The resulting evidence bundle's workstream results are genuine
  observations of THAT target (proposals reach it, receipts come from
  its own, separately-booted external-effect sink), not fabricated or
  copied from a self-contained run.
* Missing/malformed external-mode arguments fail closed with a clear
  error, never a silent fallback to self-contained mode.

What this file does NOT prove (see ``docs/ASSUMPTIONS_AND_LIMITS.md`` for
the complete, permanent statement): a genuinely remote, separately-hosted,
cross-organization-trust-boundary deployment. The "target" here is still a
process on this same machine; only the CODE PATH (HTTP + config file, no
subprocess spawned by the CLI, no teardown of infrastructure it doesn't
own) is genuinely exercised as an external operator would use it.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import httpx
import pytest

from assurance.sut.harness import build_system_under_test, export_evaluator_keys_for_external_mode

REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture(scope="module")
def external_target():
    """A real, self-contained SUT this test suite does NOT treat as its
    own -- deliberately booted the ordinary way, then addressed ONLY
    through public URLs + a config file, exactly as an external operator's
    already-running deployment would be."""
    with build_system_under_test() as s:
        yield s


def test_l1_cli_rejects_incomplete_external_arguments(tmp_path):
    """--target without --actuator (and vice versa) must fail closed with
    a clear error -- never silently fall back to self-contained mode."""
    result = subprocess.run(
        [sys.executable, "-m", "assurance", "run", "--output", str(tmp_path / "out"),
         "--target", "http://127.0.0.1:1"],
        cwd=str(REPO_ROOT), capture_output=True, text=True, timeout=30,
        env={**os.environ, "PYTHONPATH": f"{REPO_ROOT/'src'}:{REPO_ROOT}:{REPO_ROOT/'sdk'/'python'/'src'}"},
    )
    assert result.returncode == 2
    assert "--target and --actuator must be supplied together" in result.stderr
    assert not (tmp_path / "out").exists()


def test_l2_cli_rejects_missing_external_config(tmp_path):
    result = subprocess.run(
        [sys.executable, "-m", "assurance", "run", "--output", str(tmp_path / "out"),
         "--target", "http://127.0.0.1:1", "--actuator", "http://127.0.0.1:1",
         "--notify", "http://127.0.0.1:1"],
        cwd=str(REPO_ROOT), capture_output=True, text=True, timeout=30,
        env={**os.environ, "PYTHONPATH": f"{REPO_ROOT/'src'}:{REPO_ROOT}:{REPO_ROOT/'sdk'/'python'/'src'}"},
    )
    assert result.returncode == 2
    assert "--external-config is required" in result.stderr


def test_l3_external_config_missing_keys_fails_closed(tmp_path):
    bad_config = tmp_path / "config.json"
    bad_config.write_text(json.dumps({"api_key": "x"}))

    result = subprocess.run(
        [sys.executable, "-m", "assurance", "run", "--output", str(tmp_path / "out"),
         "--target", "http://127.0.0.1:1", "--actuator", "http://127.0.0.1:1",
         "--notify", "http://127.0.0.1:1", "--external-config", str(bad_config)],
        cwd=str(REPO_ROOT), capture_output=True, text=True, timeout=30,
        env={**os.environ, "PYTHONPATH": f"{REPO_ROOT/'src'}:{REPO_ROOT}:{REPO_ROOT/'sdk'/'python'/'src'}"},
    )
    assert result.returncode == 2
    assert "missing required keys" in result.stderr


def test_l4_external_mode_genuinely_attaches_and_observes_the_real_target(external_target, tmp_path):
    """The end-to-end proof: the real CLI subprocess, given only URLs and a
    config file, attaches to ``external_target`` (which it did not boot)
    and its evidence bundle reflects genuine observation of that target --
    verified independently via the target's OWN receipt endpoints, not by
    trusting the CLI's self-reported summary alone."""
    sut = external_target
    keys = export_evaluator_keys_for_external_mode(sut, str(tmp_path / "keys"))

    config = {
        "api_key": sut.api_key, "operator_key": sut.operator_key,
        "actuator_api_key": sut.actuator_api_key, "policy_hash": sut.policy_hash,
        "actuator_policy_hash": sut._actuator_policy_hash,  # noqa: SLF001 -- test-only, real attribute
        "evaluator_keys_path": keys["evaluator_keys_path"],
        "actuator_evaluator_keys_path": keys["actuator_evaluator_keys_path"],
        # The Gateway's OWN separate external-effect sink (see connect_external's
        # gateway_notify_url docstring) -- our stand-in "external" target happens
        # to know this (it built itself), exactly as a real third party would.
        "gateway_notify_url": sut._gateway_notify_base,  # noqa: SLF001 -- test-only, real attribute
    }
    config_path = tmp_path / "external_config.json"
    config_path.write_text(json.dumps(config))

    gateway_receipts_before = httpx.get(f"{sut._gateway_harness.notify_base}/receipts", timeout=5.0).json()["count"]  # noqa: SLF001
    actuator_receipts_before = sut.notification_receipt_count()

    output_dir = tmp_path / "external-run-evidence"
    result = subprocess.run(
        [sys.executable, "-m", "assurance", "run", "--output", str(output_dir),
         "--target", sut.gateway_url, "--actuator", sut.actuator_url, "--notify", sut.notify_url,
         "--external-config", str(config_path)],
        cwd=str(REPO_ROOT), capture_output=True, text=True, timeout=300,
        env={**os.environ, "PYTHONPATH": f"{REPO_ROOT/'src'}:{REPO_ROOT}:{REPO_ROOT/'sdk'/'python'/'src'}"},
    )

    assert output_dir.exists(), result.stderr
    manifest = json.loads((output_dir / "manifest.json").read_text())
    assert manifest["schema_version"] == "mcc-independent-assurance-evidence/1"

    summary = manifest["summary"]
    assert summary["modules_run"] > 0, result.stdout + result.stderr
    assert summary["passed"] > 0

    # Independent oracle: the TARGET's own two external-effect sinks (Gateway's
    # and the actuator's) actually recorded new receipts -- proving workstream
    # ALLOW-path tests genuinely dispatched through the external deployment,
    # not through a second, self-contained instance the CLI silently booted.
    gateway_receipts_after = httpx.get(f"{sut._gateway_harness.notify_base}/receipts", timeout=5.0).json()["count"]  # noqa: SLF001
    actuator_receipts_after = sut.notification_receipt_count()
    assert gateway_receipts_after > gateway_receipts_before
    assert actuator_receipts_after > actuator_receipts_before
