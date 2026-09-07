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


#: Round 17, test scenario 22: the Astra-facing/reference request path must
#: never expose a capability to reset logical-operation state, release
#: ownership, delete an UNKNOWN record, force a retry, overwrite a binding,
#: alter trust/policy, or mint/sign authority. Checked as substrings of every
#: function/method name DEFINED anywhere in this package (case-insensitive) --
#: a name containing one of these is presumed to be exactly the kind of
#: privileged operation this boundary must never carry.
_FORBIDDEN_NAME_FRAGMENTS = (
    "reset_logical", "reset_operation", "force_retry", "force_redispatch",
    "release_ownership", "release_operation", "delete_unknown", "delete_operation",
    "overwrite_binding", "set_trust", "mint_token", "sign_token", "issue_token",
    "bypass_gate", "skip_gate", "clear_idempotency",
)


def test_astra_package_exposes_no_privileged_reset_or_bypass_capability():
    for path in _all_py_files():
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                lowered = node.name.lower()
                hit = [f for f in _FORBIDDEN_NAME_FRAGMENTS if f in lowered]
                assert not hit, (
                    f"{path.name}::{node.name} looks like a privileged reset/bypass "
                    f"capability ({hit}) -- the Astra-facing layer must never expose one"
                )


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


def test_localstack_never_constructs_in_memory_idempotency_directly():
    """Round 18 requirement 4: the stack must select its idempotency
    backend through ``idempotency_registry_from_env`` (the same
    enforcement-aware factory production code uses), never by calling
    ``InMemoryIdempotencyRegistry()`` itself -- doing so would silently
    bypass the enforcement-mode fail-closed gate entirely."""
    tree = ast.parse((PKG_DIR / "_localstack.py").read_text(encoding="utf-8"))
    called_names = set()
    imported_names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            called_names.add(node.func.id)
        if isinstance(node, ast.ImportFrom):
            for alias in node.names:
                imported_names.add(alias.asname or alias.name)
    assert "InMemoryIdempotencyRegistry" not in called_names, (
        "_localstack.py must not call InMemoryIdempotencyRegistry() directly"
    )
    assert "InMemoryIdempotencyRegistry" not in imported_names, (
        "_localstack.py must not even import InMemoryIdempotencyRegistry -- "
        "idempotency_registry_from_env is the only supported construction path"
    )
    assert "idempotency_registry_from_env" in imported_names


def test_every_raw_github_issue_actuator_construction_is_resource_bound():
    """Round 18 requirement 5: no alternative raw ``GitHubIssueActuator``
    path may bypass ``ResourceBoundActuator``/``LogicalOperationMarkerActuator``.
    Every file in this package that constructs a ``GitHubIssueActuator`` at
    all must ALSO import ``ResourceBoundActuator`` -- a purely structural
    proxy for "wraps it", cheap and stable against refactors, that would
    fail loudly the moment a new raw construction site is added anywhere
    in this package without the guard."""
    sites = []
    for path in _all_py_files():
        if path.name == "github_actuator.py":
            continue  # defines the class; does not construct/dispatch through it
        text = path.read_text(encoding="utf-8")
        tree = ast.parse(text, filename=str(path))
        constructs = any(
            isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
            and node.func.id == "GitHubIssueActuator"
            for node in ast.walk(tree)
        )
        if not constructs:
            continue
        sites.append(path.name)
        imported_names = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    imported_names.add(alias.asname or alias.name)
        assert "ResourceBoundActuator" in imported_names, (
            f"{path.name} constructs GitHubIssueActuator directly but does not import "
            f"ResourceBoundActuator -- every raw construction site must wrap it"
        )
    # Sanity: this guard is only meaningful if it actually found the known
    # construction sites -- a refactor that moved them without updating
    # this test would otherwise silently pass on zero sites checked.
    assert set(sites) == {"cli.py", "adversarial.py"}, (
        f"expected raw GitHubIssueActuator construction in exactly cli.py and "
        f"adversarial.py, found: {sorted(sites)} -- update this guard if that changed"
    )
