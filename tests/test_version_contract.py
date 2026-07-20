"""Version contract for the `mcc-core` distribution (PR #41).

Proves ACTUAL equality (not just non-empty strings):

* ``mcc.__version__`` == ``importlib.metadata.version("mcc-core")``;
* the version is valid PEP 440;
* the single source is ``mcc._version`` and the runtime value matches it;
* ``client_version`` is the underlying ``mcc_client`` version, kept distinct from
  the ``mcc-core`` facade distribution version (PR #40 contract preserved).
"""

from __future__ import annotations

import importlib.metadata as im

import pytest

import mcc
import mcc._version
import mcc_client
from scripts.release_checks import is_valid_pep440


def _distribution_installed() -> bool:
    try:
        im.version("mcc-core")
        return True
    except im.PackageNotFoundError:
        return False


def test_version_is_valid_pep440():
    assert is_valid_pep440(mcc.__version__), f"{mcc.__version__!r} is not PEP 440"


def test_single_source_is_mcc_version_module():
    # The runtime value comes from the one authoritative source module.
    assert mcc.__version__ == mcc._version.__version__


@pytest.mark.skipif(not _distribution_installed(),
                    reason="mcc-core not installed as a distribution (pip install -e .)")
def test_runtime_version_equals_distribution_metadata():
    assert mcc.__version__ == im.version("mcc-core")


def test_client_version_is_distinct_concept_and_matches_client():
    # client_version tracks the underlying mcc_client package, not mcc-core.
    assert mcc.client_version == mcc_client.__version__
    assert hasattr(mcc, "client_version") and hasattr(mcc, "__version__")


@pytest.mark.skipif(not _distribution_installed(),
                    reason="mcc-client not resolvable without install")
def test_client_version_matches_client_distribution_metadata():
    # When installed as a distribution, the client module version agrees with its
    # own distribution metadata (kept separate from mcc-core's).
    assert mcc.client_version == im.version("mcc-client")
