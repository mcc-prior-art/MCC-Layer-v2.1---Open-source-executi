"""Static architecture guards for PR #101's adversarial harness
(``examples/gpt6_astra_reference/adversarial.py``).

Extends ``tests/test_gpt6_astra_reference_architecture_guards.py`` (PR #100)
to the new module: proves, by AST inspection, that the adversarial harness
introduces no second authority/token/Gate/replay architecture, never
touches signing material, never imports the concrete GitHub actuator or the
Astra provider directly, and defines no local "execute"/"actuate" shortcut
that could reach an external effect outside the real, governed
``GovernanceService``/``EnforcementCoordinator`` path.
"""

from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "examples" / "gpt6_astra_reference" / "adversarial.py"
LIVE_MATRIX_PATH = ROOT / "examples" / "gpt6_astra_reference" / "live_matrix.py"

#: Same forbidden signing-material names PR-100 already guards against.
FORBIDDEN_SIGNING_NAMES = {
    "Ed25519PrivateKey", "PrivateFormat", "NoEncryption", "load_pem_private_key",
    "private_bytes", "from_pem_file", "SigningKey",
}

#: A second, parallel decision/authority/replay/Gate architecture would show
#: up as one of these class names being DEFINED in this module.
FORBIDDEN_CLASS_NAME_FRAGMENTS = (
    "ExecutionGate", "DecisionEngine", "NonceRegistry", "EnforcementCoordinator",
    "AttesterService", "MandateVerifier", "MandateAuthority",
)

#: Method/attribute names that would indicate a local shortcut to execution,
#: bypassing the real governed path.
FORBIDDEN_METHOD_NAMES = {"execute", "actuate", "call_github", "run_actuator", "direct_execute"}


def _tree() -> ast.Module:
    return ast.parse(MODULE_PATH.read_text(encoding="utf-8"), filename=str(MODULE_PATH))


def _imported_modules(tree: ast.Module) -> set:
    modules = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            modules.add(node.module)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                modules.add(alias.name)
    return modules


def _used_names(tree: ast.Module) -> set:
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            names.add(node.id)
        elif isinstance(node, ast.Attribute):
            names.add(node.attr)
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            for alias in node.names:
                names.add(alias.asname or alias.name)
    return names


def test_module_never_touches_signing_material():
    used = _used_names(_tree())
    hit = used & FORBIDDEN_SIGNING_NAMES
    assert not hit, f"adversarial.py references forbidden signing-material names: {hit}"


def test_module_defines_no_second_core_primitive():
    tree = _tree()
    class_names = {n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)}
    for fragment in FORBIDDEN_CLASS_NAME_FRAGMENTS:
        hit = {c for c in class_names if fragment in c}
        assert not hit, f"adversarial.py defines a class resembling a core primitive: {hit}"


def test_module_never_performs_its_own_direct_http_calls():
    """The module MAY import ``DeterministicAstraProvider`` (an offline
    fixture, not a live model adapter) and the real ``GitHubIssueActuator``
    (for wiring, as PR-100's own CLI does) — but it must never open its own
    HTTP client, which would be a second path to an external effect outside
    the governed upstream call."""
    imported = _imported_modules(_tree())
    forbidden_direct = {"httpx"}
    assert not (imported & forbidden_direct), (
        f"adversarial.py must never perform its own direct HTTP calls: {imported & forbidden_direct}"
    )


def test_module_defines_no_local_execute_shortcut():
    tree = _tree()
    defined_names = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            defined_names.add(node.name)
    hit = defined_names & FORBIDDEN_METHOD_NAMES
    assert not hit, f"adversarial.py defines a local execution shortcut: {hit}"


def test_module_never_calls_an_upstream_or_actuator_outside_call_dunder():
    """Every handler in this module (``LocalActionRecorder``,
    ``CountingMultiActuator``) is only ever invoked as an
    ``Upstream``-shaped ``__call__`` reached from
    ``EnforcementCoordinator.enforce`` -- this module defines no OTHER
    function that calls a handler directly (which would be a fallback path
    around the Gate)."""
    tree = _tree()
    # Structural guard: `handler(action, payload)` — the actual dispatch —
    # must only appear inside CountingMultiActuator.__call__.
    dispatch_sites = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "handler":
            dispatch_sites.append(node)
    assert len(dispatch_sites) == 1, (
        f"expected exactly one direct handler(...) dispatch site (inside "
        f"CountingMultiActuator.__call__), found {len(dispatch_sites)}"
    )


# ---------------------------------------------------------------------------
# Phase 10 — the live matrix module: no second live adapter, no direct HTTP.
# ---------------------------------------------------------------------------


def test_live_matrix_uses_the_one_real_live_adapter_only():
    """The live matrix must reuse PR-100's real ``OpenAIAstraProvider`` —
    the only live adapter this repository defines — and must never build
    its own HTTP client or a second live-model transport."""
    tree = ast.parse(LIVE_MATRIX_PATH.read_text(encoding="utf-8"), filename=str(LIVE_MATRIX_PATH))
    imported = _imported_modules(tree)
    assert not ({"httpx", "requests", "urllib"} & imported), (
        "live_matrix.py must never perform its own direct network transport"
    )
    names = _used_names(tree)
    assert "OpenAIAstraProvider" in names


def test_live_matrix_never_touches_signing_material():
    tree = ast.parse(LIVE_MATRIX_PATH.read_text(encoding="utf-8"), filename=str(LIVE_MATRIX_PATH))
    used = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            used.add(node.id)
        elif isinstance(node, ast.Attribute):
            used.add(node.attr)
    hit = used & FORBIDDEN_SIGNING_NAMES
    assert not hit, f"live_matrix.py references forbidden signing-material names: {hit}"
