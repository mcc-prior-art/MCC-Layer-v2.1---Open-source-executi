"""Static architecture guards for ``src/mcc_attestation``.

Proves, by AST inspection (not just convention), that the pre-execution
Attester boundary stays exactly where the task specification puts it:

    INTELLIGENCE -> ATTESTER -> CONTROL -> EXECUTION

``mcc_attestation`` produces and verifies PRE-EXECUTION evidence only. It
must never become an execution authority, must never depend on an LLM/model
SDK or an agent framework, must never import execution/egress machinery,
must never import ``ExecutionGate`` (there is nothing for a deterministic
cryptographic verifier to decide by importing it), and must not treat
``mcc_evidence`` (observational, post-governance evidence) as an authority
source. This mirrors ``tests/test_mcc_agent_no_direct_egress.py``'s
AST-guard style.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

PKG = Path(__file__).resolve().parents[1] / "src" / "mcc_attestation"

# Root module names this package must never import, directly or transitively
# via its own source (this is a first-party-import guard, not a full
# transitive dependency scan): LLM/model SDKs, agent frameworks, execution/
# egress machinery, and MCC-Core's own gate/authority/gateway internals.
FORBIDDEN_ROOTS = {
    # LLM / model SDKs
    "anthropic", "openai", "google", "cohere", "transformers", "torch",
    "tensorflow", "llama_index", "langchain",
    # agent frameworks named explicitly by the task
    "langgraph", "crewai", "autogen_core", "autogen_agentchat", "voltagent",
    # networking / execution-adapter primitives (an Attester performs no
    # outbound call or actuation of its own)
    "httpx", "requests", "urllib3", "aiohttp", "pycurl", "subprocess",
    "socket",
    # MCC-Core runtime authority/execution/gateway internals
    "gateway", "egress_proxy", "interceptors", "pilot_api", "pilot_notify",
    "clinic_service",
}

# Specific dotted mcc_core submodules this package must never import: the
# Execution Gate and the Authority/decision-token machinery. mcc_core.signing
# (pure Ed25519/canonicalization primitives) is explicitly reused and is NOT
# forbidden.
FORBIDDEN_MCC_CORE_SUBMODULES = {
    "mcc_core.gate",
    "mcc_core.authority",
    "mcc_core.coordinator",
    "mcc_core.mandate",
    "mcc_core.approvals",
    "mcc_core.consensus",
    "mcc_core.challenge",
    "mcc_core.nonce",
    "mcc_core.idempotency",
    "mcc_core.velocity",
}

# mcc_evidence must never be treated as an authority source by this package
# (see the module docstring and docs/ATTESTATION_ARCHITECTURE.md for why the
# two stay architecturally separate).
FORBIDDEN_EXACT_ROOTS = {"mcc_evidence"}


def _sources():
    return sorted(PKG.glob("*.py")) if PKG.is_dir() else []


def test_package_exists():
    assert PKG.is_dir() and _sources(), "mcc_attestation package not found"


def _imported_module_names(tree: ast.AST):
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                yield alias.name
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                yield node.module


@pytest.mark.parametrize("path", _sources(), ids=lambda p: p.name)
def test_no_forbidden_imports(path: Path):
    tree = ast.parse(path.read_text(), filename=str(path))
    bad = []
    for mod in _imported_module_names(tree):
        root = mod.split(".")[0]
        if root in FORBIDDEN_ROOTS or mod in FORBIDDEN_ROOTS:
            bad.append(mod)
        if root in FORBIDDEN_EXACT_ROOTS or mod in FORBIDDEN_EXACT_ROOTS:
            bad.append(mod)
        if mod in FORBIDDEN_MCC_CORE_SUBMODULES:
            bad.append(mod)
        for forbidden_sub in FORBIDDEN_MCC_CORE_SUBMODULES:
            if mod == forbidden_sub or mod.startswith(forbidden_sub + "."):
                bad.append(mod)
    assert not bad, f"{path.name} imports forbidden module(s): {sorted(set(bad))}"


def test_does_not_import_execution_gate_class():
    """AST-level check that no source file even names ``ExecutionGate`` —
    not merely that ``mcc_core.gate`` isn't imported (covered above), but
    that the class itself is never referenced, so a future refactor of
    ``mcc_core`` (e.g. a re-export from a different module) can't quietly
    reintroduce the dependency this guard exists to prevent."""
    for path in _sources():
        tree = ast.parse(path.read_text(), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and node.id == "ExecutionGate":
                pytest.fail(f"{path.name} references ExecutionGate")
            if isinstance(node, ast.Attribute) and node.attr == "ExecutionGate":
                pytest.fail(f"{path.name} references ExecutionGate")


def test_only_allowed_mcc_core_submodule_is_signing():
    """This package's only permitted dependency on ``mcc_core`` is the pure,
    stateless ``signing`` module (canonical serialization + Ed25519), reused
    rather than reimplemented — never the authority/gate/runtime layer."""
    seen = set()
    for path in _sources():
        tree = ast.parse(path.read_text(), filename=str(path))
        for mod in _imported_module_names(tree):
            if mod == "mcc_core" or mod.startswith("mcc_core."):
                seen.add(mod)
    allowed = {"mcc_core.signing"}
    assert seen <= allowed, f"unexpected mcc_core dependency: {seen - allowed}"


def test_package_has_no_network_or_queue_or_redis_dependency():
    """PR-1 explicitly excludes an Attester network service, queues, and a
    Redis requirement (those are runtime-integration concerns for later
    PRs)."""
    forbidden = {"redis", "celery", "kombu", "pika", "kafka"}
    for path in _sources():
        tree = ast.parse(path.read_text(), filename=str(path))
        for mod in _imported_module_names(tree):
            root = mod.split(".")[0]
            assert root not in forbidden, f"{path.name} imports {mod}"


def test_verifier_module_defines_no_authorize_or_execute_function():
    import mcc_attestation.verifier as verifier

    public = {n for n in dir(verifier) if not n.startswith("_")}
    forbidden_names = {"authorize", "execute", "allow", "issue_token", "decide", "grant"}
    overlap = {n for n in public if n.lower() in forbidden_names}
    assert not overlap, overlap


def test_verifier_is_pure_and_takes_no_llm_or_reasoning_argument():
    """The verifier's public signature is closed over cryptographic/binding
    inputs only -- no ``model``, ``provider``, ``llm``, or ``prompt``
    argument exists for a caller to (mis)use to make it "reason" about
    truth."""
    import inspect

    from mcc_attestation.verifier import verify_attestation

    params = set(inspect.signature(verify_attestation).parameters)
    forbidden = {"model", "provider", "llm", "prompt", "reasoning", "client"}
    assert not (params & forbidden), params & forbidden


def test_local_attester_has_no_llm_or_network_surface():
    from mcc_attestation.attester import LocalAttester

    public = {n for n in dir(LocalAttester) if not n.startswith("_")}
    for forbidden in ("call_model", "invoke_llm", "session", "http", "client", "request"):
        assert forbidden not in public
