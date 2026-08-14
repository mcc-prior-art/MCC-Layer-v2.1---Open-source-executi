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

Also registers the ``assurance`` Hypothesis profile (Workstream H):
redirects the example database from the default ``.hypothesis/`` (repo
root, git-ignored -- so a failing example found on one machine/CI run
never reaches another) to ``assurance/tests/hypothesis_seed_corpus/``,
which is NOT git-ignored -- a genuine, durable, committed regression
corpus, not merely "relies on Hypothesis's own local cache." Also enables
``print_blob=True`` so any failure prints a copy-pasteable
``@reproduce_failure`` decorator in CI logs even before anyone fetches
the corpus directory.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest
from hypothesis import settings
from hypothesis.database import DirectoryBasedExampleDatabase

from assurance.sut.harness import build_system_under_test, connect_external

_SEED_CORPUS_DIR = Path(__file__).resolve().parent / "hypothesis_seed_corpus"
settings.register_profile(
    "assurance",
    database=DirectoryBasedExampleDatabase(str(_SEED_CORPUS_DIR)),
    print_blob=True,
)
settings.load_profile("assurance")


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
            gateway_notify_url=os.environ.get("MCC_ASSURANCE_GATEWAY_NOTIFY_URL") or None,
        )
        yield s
        return

    with build_system_under_test() as s:
        yield s
