"""Static guard: MCC-Core never imports, depends on, or references the
Control Room.

Mirrors the existing pattern in ``tests/test_mcc_agent_no_direct_egress.py``.
Scans every ``.py`` file under the trusted computing base / canonical
execution path / security enforcement boundary / protocol runtime packages
for any reference (import OR literal string, e.g. a path built at runtime)
to ``tools/control-room`` or its Python package name ``control_room``. If
this test ever fails, the Control Room has stopped being purely an external
observer and something in the governed runtime has started to depend on it
-- exactly the coupling the architecture forbids.
"""

from __future__ import annotations

import ast
from pathlib import Path
from typing import List

import pytest

ROOT = Path(__file__).resolve().parents[3]

# Every package that is part of the trusted computing base / canonical
# execution path / security enforcement boundary / protocol runtime.
CORE_PACKAGES = [
    ROOT / "src" / "mcc_core",
    ROOT / "src" / "mcc_evidence",
    ROOT / "src" / "mcc_compliance",
    ROOT / "src" / "mcc_protocol",
    ROOT / "src" / "mcc_adapter_sdk",
    ROOT / "src" / "mcc_agent",
    ROOT / "gateway",
    ROOT / "egress_proxy",
    ROOT / "interceptors",
    ROOT / "sdk" / "python" / "src" / "mcc_client",
]

FORBIDDEN_SUBSTRINGS = ("control_room", "control-room", "Control Room", "control room")


def _core_sources() -> List[Path]:
    out: List[Path] = []
    for pkg in CORE_PACKAGES:
        if pkg.is_dir():
            out.extend(sorted(pkg.rglob("*.py")))
    return out


def test_core_packages_exist():
    found = [p for p in CORE_PACKAGES if p.is_dir()]
    assert len(found) >= 5, f"expected to find the core packages, only found: {found}"


@pytest.mark.parametrize("path", _core_sources(), ids=lambda p: str(p.relative_to(ROOT)))
def test_core_file_never_mentions_control_room(path: Path):
    text = path.read_text(encoding="utf-8")
    hits = [s for s in FORBIDDEN_SUBSTRINGS if s in text]
    assert not hits, (
        f"{path.relative_to(ROOT)} references the Control Room ({hits}) -- "
        f"MCC-Core must never import, depend on, start, or require it"
    )


@pytest.mark.parametrize("path", _core_sources(), ids=lambda p: str(p.relative_to(ROOT)))
def test_core_file_never_imports_tools_package(path: Path):
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    bad = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.split(".")[0] == "tools":
                    bad.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            if mod.split(".")[0] == "tools":
                bad.append(mod)
    assert not bad, f"{path.relative_to(ROOT)} imports from tools/: {bad}"


def test_control_room_lives_in_its_own_isolated_directory():
    control_room = ROOT / "tools" / "control-room"
    assert control_room.is_dir()
    assert (control_room / "backend").is_dir()
    assert (control_room / "README.md").is_file()


def test_control_room_backend_imports_no_engine_internals():
    """The Control Room's own logic (scenarios.py / server.py -- NOT the
    launcher, runtime.py, whose entire job is starting the real gateway
    process, exactly like examples/governance_http_demo.py already does)
    must never import the decision/gate/coordinator/audit-write internals
    directly -- it may only reach MCC-Core as an external HTTP client."""
    forbidden_symbols = {
        "AuthorityModel", "DecisionEngine", "ExecutionGate", "EnforcementCoordinator",
        "AuditLog",
    }
    for name in ("scenarios.py", "server.py", "main.py"):
        path = ROOT / "tools" / "control-room" / "backend" / name
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        imported: List[str] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module == "mcc_core":
                imported += [a.name for a in node.names]
        bad = forbidden_symbols & set(imported)
        assert not bad, f"{name} imports governance-authority symbols directly: {bad}"
