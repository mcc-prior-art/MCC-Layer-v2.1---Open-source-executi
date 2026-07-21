"""Interoperability suite fixtures (PR #48).

One shared out-of-process Gateway per test session (boot is expensive; every
adapter proof reuses the same real instance). The ADAPTERS registry is the single
place future framework adapters (48b–e) are added.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
for p in (ROOT / "src", ROOT / "sdk" / "python" / "src", ROOT):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from tests.interoperability.adapters.generic_http import GenericHttpAdapter  # noqa: E402
from tests.interoperability.harness import SharedGovernedGateway  # noqa: E402

# The adapter matrix. 48a ships the framework-neutral HTTP integration; the real
# framework adapters (VoltAgent / LangGraph / CrewAI / AutoGen) are added in 48b–e.
ADAPTERS = [GenericHttpAdapter()]


# Package scope (not session): the shared Gateway subprocess + the in-process mock
# upstream server are torn down as soon as the interoperability package finishes, so
# their background threads never pollute other test modules' thread-leak guards.
@pytest.fixture(scope="package")
def shared_gateway():
    gw = SharedGovernedGateway()
    try:
        yield gw
    finally:
        gw.close()
