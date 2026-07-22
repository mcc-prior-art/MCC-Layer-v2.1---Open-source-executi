"""Built-artifact contract + genuine clean-install proof (PR #41).

Builds the real sdist + wheel once, then:
* asserts exactly one sdist and one wheel;
* enforces the wheel/sdist content contract (via scripts.release_checks);
* checks filename/metadata version agreement with the authoritative version;
* installs the built WHEEL into an isolated venv and proves, from OUTSIDE the
  repository checkout, that `from mcc import MCCClient` works, resolves to the
  installed venv (not the source tree), re-exports the identical class, and the
  runtime version equals the installed distribution metadata version.

These are heavier tests; they skip cleanly if `build` is unavailable. No network
publishing, no credentials, no external calls beyond local pip resolution of the
sibling `mcc-client` (installed from the in-repo sdist).
"""

from __future__ import annotations

import glob
import importlib.metadata as im
import importlib.util
import os
import subprocess
import sys
import venv
from pathlib import Path

import pytest

from scripts.release_checks import (
    inspect_wheel,
    validate_sdist,
    validate_wheel,
)

ROOT = Path(__file__).resolve().parents[1]

pytestmark = pytest.mark.skipif(
    importlib.util.find_spec("build") is None,
    reason="the `build` package is required to build artifacts",
)


@pytest.fixture(scope="module")
def dist(tmp_path_factory) -> dict:
    out = tmp_path_factory.mktemp("dist")
    subprocess.run([sys.executable, "-m", "build", "--outdir", str(out), str(ROOT)],
                   check=True, capture_output=True, text=True)
    wheels = glob.glob(str(out / "*.whl"))
    sdists = glob.glob(str(out / "*.tar.gz"))
    return {"dir": out, "wheels": wheels, "sdists": sdists}


def _authoritative_version() -> str:
    return im.version("mcc-core")


def test_exactly_one_wheel_and_one_sdist(dist):
    assert len(dist["wheels"]) == 1, dist["wheels"]
    assert len(dist["sdists"]) == 1, dist["sdists"]


def test_wheel_content_contract(dist):
    problems = validate_wheel(dist["wheels"][0], expected_version=_authoritative_version())
    assert problems == [], problems


def test_sdist_content_contract(dist):
    problems = validate_sdist(dist["sdists"][0], expected_version=_authoritative_version())
    assert problems == [], problems


def test_wheel_ships_public_packages_engine_free(dist):
    # PR #50: the wheel carries the facade + Adapter SDK + Canonical Protocol + the
    # governance-free curated subsets of mcc_core/mcc_compliance — and NEVER the
    # governance engine or the compliance suite.
    from scripts.release_checks import FORBIDDEN_WHEEL_MODULES, PUBLIC_PACKAGES
    info = inspect_wheel(dist["wheels"][0])
    assert info.top_level <= PUBLIC_PACKAGES, sorted(info.top_level)
    assert {"mcc", "mcc_adapter_sdk", "mcc_protocol"} <= info.top_level
    assert info.has_py_typed
    assert "mcc_client" not in info.top_level  # dependency, never vendored
    shipped_forbidden = sorted(m for m in FORBIDDEN_WHEEL_MODULES if m in set(info.names))
    assert shipped_forbidden == [], f"engine/suite modules leaked into wheel: {shipped_forbidden}"


def test_clean_wheel_install_outside_checkout(dist, tmp_path):
    """Install the built wheel into a fresh venv and prove imports come from it."""
    env_dir = tmp_path / "venv"
    venv.create(env_dir, with_pip=True)
    py = env_dir / ("Scripts" if os.name == "nt" else "bin") / "python"

    # Install the wheel ARTIFACT itself + the sibling client (mcc-client is not on
    # a public index yet, so provide it from the in-repo sdist — a real resolution
    # of the declared runtime dependency, not the source tree of `mcc`).
    subprocess.run([str(py), "-m", "pip", "install", "--quiet",
                    dist["wheels"][0], str(ROOT / "sdk" / "python")],
                   check=True, capture_output=True, text=True)

    # Run from a directory OUTSIDE the repo so the checkout is not importable.
    script = (
        "import importlib.metadata as im, mcc, mcc_client, pathlib\n"
        "root = pathlib.Path(r'%s').resolve()\n"
        "mf = pathlib.Path(mcc.__file__).resolve()\n"
        "assert root not in mf.parents, ('mcc imported from checkout: %%s' %% mf)\n"
        "from mcc import MCCClient\n"
        "from mcc_client import MCCClient as Orig\n"
        "assert MCCClient is Orig, 'facade must re-export identical class'\n"
        "assert mcc.__version__ == im.version('mcc-core'), 'runtime != metadata'\n"
        "assert mcc.client_version == mcc_client.__version__\n"
        # PR #50: the curated Adapter SDK public API imports from the clean install...
        "import mcc_adapter_sdk as sdk\n"
        "from mcc_adapter_sdk import (Adapter, AdapterMetadata, AdapterContext, "
        "AdapterRunner, register_adapter, validate_adapter, generate_adapter_evidence)\n"
        "sf = pathlib.Path(sdk.__file__).resolve()\n"
        "assert root not in sf.parents, ('sdk imported from checkout: %%s' %% sf)\n"
        # ...and the governance engine is NOT shippable from this wheel.
        "import importlib\n"
        "try:\n"
        "    importlib.import_module('mcc_core.gate'); raise SystemExit('engine shipped!')\n"
        "except ModuleNotFoundError:\n"
        "    pass\n"
        "print('CLEAN-INSTALL OK', mcc.__version__, sdk.SDK_VERSION, mf)\n"
    ) % str(ROOT)
    proc = subprocess.run([str(py), "-c", script], cwd=str(tmp_path),
                          capture_output=True, text=True)
    assert proc.returncode == 0, f"clean-install smoke failed:\n{proc.stdout}\n{proc.stderr}"
    assert "CLEAN-INSTALL OK" in proc.stdout
