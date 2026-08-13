"""Session-scoped System-Under-Test fixture for every assurance workstream
test module. Two modes, selected only by environment variables (never a
pytest CLI flag, so ``pytest assurance/tests/`` and
``python -m assurance run`` behave identically):

* Self-contained (default): boots a real, local, three-process deployment
  via ``assurance.sut.harness.build_system_under_test``.
* External (``MCC_ASSURANCE_EXTERNAL=1``): attaches to an already-running,
  externally provisioned deployment via
  ``assurance.sut.harness.connect_external`` -- the genuine third-party
  mode described in ``THIRD_PARTY_RUNBOOK.md``.
"""

from __future__ import annotations

import os

import pytest

from assurance.sut.harness import build_system_under_test, connect_external


@pytest.fixture(scope="session")
def sut():
    if os.environ.get("MCC_ASSURANCE_EXTERNAL") == "1":
        s = connect_external(
            gateway_url=os.environ["MCC_ASSURANCE_GATEWAY_URL"],
            actuator_url=os.environ["MCC_ASSURANCE_ACTUATOR_URL"],
            notify_url=os.environ["MCC_ASSURANCE_NOTIFY_URL"],
            api_key=os.environ["MCC_ASSURANCE_API_KEY"],
            operator_key=os.environ["MCC_ASSURANCE_OPERATOR_KEY"],
            actuator_api_key=os.environ["MCC_ASSURANCE_ACTUATOR_API_KEY"],
            policy_hash=os.environ["MCC_ASSURANCE_POLICY_HASH"],
            actuator_policy_hash=os.environ.get("MCC_ASSURANCE_ACTUATOR_POLICY_HASH", ""),
            evaluator_keys_path=os.environ["MCC_ASSURANCE_EVALUATOR_KEYS_PATH"],
            actuator_evaluator_keys_path=os.environ["MCC_ASSURANCE_ACTUATOR_EVALUATOR_KEYS_PATH"],
        )
        yield s
        return

    with build_system_under_test() as s:
        yield s
