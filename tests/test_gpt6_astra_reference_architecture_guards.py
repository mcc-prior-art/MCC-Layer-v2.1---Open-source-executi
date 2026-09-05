"""Static architecture guards for the GPT-6 Astra Reference Integration.

Proves, by AST inspection (mirroring the established style in
``tests/test_attester_service_architecture_guards.py`` and
``tests/test_production_trust_hardening_architecture_guards.py``), that
this reference integration introduces no second authority/token/Gate/
replay architecture, and that Astra's own code never reaches signing
material, authority, or the actuator directly.
"""

from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PKG_DIR = ROOT / "examples" / "gpt6_astra_reference"

#: Names that would indicate a second execution-authority architecture, or
#: Astra-side code reaching for signing/authority material it must never
#: touch.
FORBIDDEN_NAMES = {
    "Ed25519PrivateKey", "PrivateFormat", "NoEncryption", "load_pem_private_key",
    "private_bytes", "from_pem_file", "SigningKey",
}

#: A second, parallel decision/authority/replay/Gate architecture would show
#: up as one of these class names being DEFINED somewhere in this package.
FORBIDDEN_CLASS_NAME_FRAGMENTS = (
    "ExecutionGate", "DecisionEngine", "NonceRegistry", "EnforcementCoordinator",
    "AttesterService", "MandateVerifier", "MandateAuthority",
)


def _all_py_files():
    return sorted(PKG_DIR.glob("*.py"))


def _names_used(path: Path) -> set:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
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


def test_astra_provider_and_models_never_touch_signing_material():
    for name in ("astra_provider.py", "models.py"):
        used = _names_used(PKG_DIR / name)
        hit = used & FORBIDDEN_NAMES
        assert not hit, f"{name} references forbidden signing-material names: {hit}"


def test_no_module_in_this_package_defines_a_second_core_primitive():
    for path in _all_py_files():
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        class_names = {n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)}
        for fragment in FORBIDDEN_CLASS_NAME_FRAGMENTS:
            hit = {c for c in class_names if fragment in c}
            assert not hit, f"{path.name} defines a class resembling a core primitive: {hit}"


def test_astra_provider_module_imports_no_governance_engine():
    """Astra proposes; it must never import the decision/gate/authority/
    coordinator engine at all -- not even to observe it."""
    forbidden_modules = {"mcc_core", "gateway", "mcc_attestation", "mcc_attester_service"}
    tree = ast.parse((PKG_DIR / "astra_provider.py").read_text(encoding="utf-8"))
    imported_modules = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            imported_modules.add(node.module.split(".")[0])
        elif isinstance(node, ast.Import):
            for alias in node.names:
                imported_modules.add(alias.name.split(".")[0])
    assert not (imported_modules & forbidden_modules), (
        f"astra_provider.py must never import a governance module, found: "
        f"{imported_modules & forbidden_modules}"
    )


def test_models_module_imports_no_governance_engine():
    tree = ast.parse((PKG_DIR / "models.py").read_text(encoding="utf-8"))
    imported_modules = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            imported_modules.add(node.module.split(".")[0])
        elif isinstance(node, ast.Import):
            for alias in node.names:
                imported_modules.add(alias.name.split(".")[0])
    forbidden_modules = {"mcc_core", "gateway", "mcc_attestation", "mcc_attester_service"}
    assert not (imported_modules & forbidden_modules)


def test_github_actuator_module_never_imports_astra_provider():
    """No direct Astra -> GitHub path may exist: the actuator module must
    not import (and therefore cannot call into) the Astra provider at all."""
    tree = ast.parse((PKG_DIR / "github_actuator.py").read_text(encoding="utf-8"))
    imported_modules = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            imported_modules.add(node.module)
    assert not any("astra_provider" in m for m in imported_modules)


def test_pipeline_module_never_imports_the_actuator_directly():
    """The orchestration layer wires the actuator in only as
    ``GovernanceService.upstream`` (a plain callable supplied by the
    caller, e.g. the CLI) -- it never imports the concrete GitHub actuator
    class itself, so it can never call it directly, bypassing the Gate."""
    tree = ast.parse((PKG_DIR / "pipeline.py").read_text(encoding="utf-8"))
    imported_modules = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            imported_modules.add(node.module)
    assert not any("github_actuator" in m for m in imported_modules)
