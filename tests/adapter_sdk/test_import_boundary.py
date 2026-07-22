"""Import-boundary regression tests for the PR #50 decoupling.

Proves that the lazy decoupling holds: importing ``mcc_protocol`` or
``mcc_adapter_sdk`` does NOT eagerly load the governance engine (gate, authority,
consensus, audit, …) or the compliance suite, while existing public imports such as
``from mcc_core import ExecutionGate`` keep working. Each import-closure check runs
in a FRESH interpreter (subprocess) so a module loaded by another test can't mask a
regression.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

_ENGINE = ("gate", "authority", "consensus", "coordinator", "mandate", "audit",
           "approvals", "challenge", "velocity", "idempotency", "nonce", "policy",
           "redis_client", "core", "profiles")
_SUITE = ("runner", "reporting", "program", "registry", "adapters", "certification")


def _closure_probe(import_line: str) -> set:
    code = (
        "import sys\n"
        f"sys.path.insert(0, r'{ROOT}/src'); sys.path.insert(0, r'{ROOT}/sdk/python/src')\n"
        f"{import_line}\n"
        "eng = [m for m in sys.modules if m.startswith('mcc_core.') and "
        f"m.split('.')[1] in {_ENGINE!r}]\n"
        "suite = [m for m in sys.modules if m.startswith('mcc_compliance.') and "
        f"m.split('.')[1] in {_SUITE!r}]\n"
        "print('|'.join(sorted(eng + suite)))\n"
    )
    out = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True,
                         check=True)
    line = out.stdout.strip()
    return set(line.split("|")) if line else set()


def test_importing_mcc_protocol_does_not_load_engine_or_suite():
    assert _closure_probe("import mcc_protocol") == set()


def test_importing_adapter_sdk_is_lightweight():
    assert _closure_probe("import mcc_adapter_sdk") == set()


def test_backward_compatible_public_imports_still_work():
    code = (
        "import sys\n"
        f"sys.path.insert(0, r'{ROOT}/src'); sys.path.insert(0, r'{ROOT}/sdk/python/src')\n"
        "from mcc_core import ExecutionGate, SigningKey, EnforcementCoordinator, Verdict\n"
        "from mcc_core import canonical_bytes, sha256_hex\n"
        "from mcc_compliance import KNOWN_CAPABILITIES, run_compliance, available_adapters\n"
        "from mcc_core.signing import canonical_bytes as cb\n"
        "assert ExecutionGate.__name__ == 'ExecutionGate'\n"
        "print('OK')\n"
    )
    out = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
    assert out.returncode == 0, out.stderr
    assert "OK" in out.stdout


def test_mcc_core_all_matches_lazy_export_map():
    # __all__ is derived from the lazy export map; every public name resolves.
    import mcc_core
    for name in mcc_core.__all__:
        assert getattr(mcc_core, name) is not None
