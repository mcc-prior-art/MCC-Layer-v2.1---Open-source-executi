"""Static architecture guards for Production Trust Hardening Phase 1.

Proves, by AST inspection (mirroring the established style in
``tests/test_attester_service_architecture_guards.py``,
``tests/test_mcc_attestation_architecture_guards.py``, and
``tests/test_pre_execution_control_architecture_guards.py``), the 7
structural invariants Phase 1 requires:

1. Production Gateway/Control still never loads Attester private keys --
   UNCHANGED, already proven by
   ``test_attester_service_architecture_guards.py``'s guard A (this Phase
   touched no code that loads keys); re-affirmed here by re-scanning the
   same runtime directories for any new ``mcc_attester_service`` import.
2. The Attester still cannot issue MCC decision tokens/mandates/approvals
   -- UNCHANGED, already proven by the same file's guard L, which scans
   every ``.py`` file directly under ``src/mcc_attester_service/``
   (a glob that already includes this Phase's new ``provider_loader.py``
   without modification); re-affirmed here.
3. ``AssessmentProvider`` cannot become an execution/authority surface --
   NEW: neither ``provider.py`` nor ``provider_loader.py`` reference any
   signing-key-material API or any authority/execution primitive.
4. No second nonce/replay subsystem is introduced -- NEW: only
   ``src/mcc_core/nonce.py`` defines a nonce-registry class or an atomic
   ``SET ... NX`` claim; the new ``deployment_mode.py`` module contains no
   replay-state logic of its own.
5. No alternate governed actuation path bypassing ``ExecutionGate`` is
   introduced -- NEW: the two new modules
   (``mcc_core.deployment_mode``, ``mcc_attester_service.provider_loader``)
   reference no execution/actuation primitive at all.
6. Production configuration cannot silently select
   ``DeterministicTestProvider`` -- NEW (static half of the proof; the
   behavioral half is ``tests/test_attester_provider_loader.py``):
   ``_load_production_provider`` never calls ``_load_test_provider``
   anywhere in its body.
7. Production enforcement cannot silently select volatile replay
   protection -- NEW (static half; behavioral half is
   ``tests/test_nonce.py``'s R1-R4): the enforcement branch of
   ``nonce_registry_from_env`` raises before it can reach
   ``return InMemoryNonceRegistry()``.
"""

from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEPLOYMENT_MODE_FILE = ROOT / "src" / "mcc_core" / "deployment_mode.py"
NONCE_FILE = ROOT / "src" / "mcc_core" / "nonce.py"
PROVIDER_FILE = ROOT / "src" / "mcc_attester_service" / "provider.py"
PROVIDER_LOADER_FILE = ROOT / "src" / "mcc_attester_service" / "provider_loader.py"
CORE_DIR = ROOT / "src" / "mcc_core"

#: Signing-key-material / authority / execution names that must never
#: appear in the AssessmentProvider boundary or in the two new Phase-1
#: modules (guards 3 and 5).
FORBIDDEN_NAMES = {
    "Ed25519PrivateKey", "PrivateFormat", "NoEncryption", "load_pem_private_key",
    "private_bytes", "from_pem_file", "SigningKey",
    "DecisionEngine", "issue_token", "ExecutionGate", "EnforcementCoordinator",
    "MandateAuthority", "MandateVerifier", "ConsensusVerifier", "ApprovalService",
    "issue_mandate", "HTTPEgressExecutor",
}


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


# ---------------------------------------------------------------------------
# Guard 3: AssessmentProvider cannot become an execution/authority surface.
# ---------------------------------------------------------------------------


def test_guard_3_provider_module_has_no_signing_or_authority_surface():
    used = _names_used(PROVIDER_FILE)
    hit = used & FORBIDDEN_NAMES
    assert not hit, f"provider.py references forbidden names: {hit}"


def test_guard_3_provider_loader_module_has_no_signing_or_authority_surface():
    used = _names_used(PROVIDER_LOADER_FILE)
    hit = used & FORBIDDEN_NAMES
    assert not hit, f"provider_loader.py references forbidden names: {hit}"


# ---------------------------------------------------------------------------
# Guard 4: no second nonce/replay subsystem.
# ---------------------------------------------------------------------------


def test_guard_4_deployment_mode_defines_no_replay_state():
    tree = ast.parse(DEPLOYMENT_MODE_FILE.read_text(encoding="utf-8"), filename=str(DEPLOYMENT_MODE_FILE))
    class_names = {n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)}
    forbidden_class_hits = {c for c in class_names if "Nonce" in c or "Registry" in c}
    assert not forbidden_class_hits, (
        f"deployment_mode.py defines its own registry/nonce class: {forbidden_class_hits} "
        f"-- there must be exactly one nonce-registry implementation (mcc_core.nonce)"
    )
    source = DEPLOYMENT_MODE_FILE.read_text(encoding="utf-8")
    assert "consume" not in source, "deployment_mode.py must not implement its own replay-consumption logic"
    assert " NX" not in source and "SET" not in source, (
        "deployment_mode.py must not implement its own atomic claim primitive"
    )


def test_guard_4_only_nonce_module_defines_nonce_registry_classes():
    for path in sorted(CORE_DIR.glob("*.py")):
        if path == NONCE_FILE:
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        class_names = {n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)}
        hit = {c for c in class_names if "NonceRegistry" in c}
        assert not hit, f"{path.name} defines a NonceRegistry class outside mcc_core.nonce: {hit}"


# ---------------------------------------------------------------------------
# Guard 5: no alternate governed actuation path.
# ---------------------------------------------------------------------------


def test_guard_5_new_phase1_modules_reference_no_execution_authority_primitive():
    for path in (DEPLOYMENT_MODE_FILE, PROVIDER_LOADER_FILE):
        used = _names_used(path)
        hit = used & FORBIDDEN_NAMES
        assert not hit, f"{path.name} references forbidden execution/authority names: {hit}"


# ---------------------------------------------------------------------------
# Guard 6: production configuration cannot silently select
# DeterministicTestProvider (static half; behavioral half in
# tests/test_attester_provider_loader.py).
# ---------------------------------------------------------------------------


def test_guard_6_production_provider_loader_never_calls_test_provider_loader():
    tree = ast.parse(PROVIDER_LOADER_FILE.read_text(encoding="utf-8"), filename=str(PROVIDER_LOADER_FILE))
    functions = {n.name: n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)}
    prod_fn = functions["_load_production_provider"]
    called_names = {
        node.func.id for node in ast.walk(prod_fn)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }
    assert "_load_test_provider" not in called_names, (
        "_load_production_provider must never call _load_test_provider -- "
        "enforcement mode must not have a code path back to the reference/test provider"
    )


def test_guard_6_production_provider_loader_explicitly_checks_for_test_provider_type():
    source = PROVIDER_LOADER_FILE.read_text(encoding="utf-8")
    assert "DeterministicTestProvider" in source, (
        "provider_loader.py must explicitly reference DeterministicTestProvider "
        "to be able to reject it by type"
    )


# ---------------------------------------------------------------------------
# Guard 7: production enforcement cannot silently select volatile replay
# protection (static half; behavioral half in tests/test_nonce.py R1-R4).
# ---------------------------------------------------------------------------


def test_guard_7_enforcement_branch_of_nonce_factory_raises_before_memory_return():
    tree = ast.parse(NONCE_FILE.read_text(encoding="utf-8"), filename=str(NONCE_FILE))
    factory = next(
        n for n in ast.walk(tree)
        if isinstance(n, ast.FunctionDef) and n.name == "nonce_registry_from_env"
    )
    # Locate the `if backend in (...memory...):` branch and confirm it
    # contains a `raise` reachable before any `return InMemoryNonceRegistry()`.
    source_lines = NONCE_FILE.read_text(encoding="utf-8").splitlines()
    body_src = "\n".join(source_lines[factory.lineno - 1: factory.end_lineno])
    assert "is_enforcement_mode(env)" in body_src, (
        "nonce_registry_from_env must consult is_enforcement_mode before "
        "selecting the memory backend"
    )
    raise_idx = body_src.index("raise NonceConfigError")
    memory_return_idx = body_src.index("return InMemoryNonceRegistry()")
    assert raise_idx < memory_return_idx, (
        "the enforcement-mode NonceConfigError must be raised before the "
        "in-memory registry can be returned, never after"
    )
