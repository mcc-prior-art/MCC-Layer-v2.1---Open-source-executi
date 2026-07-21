"""Static architecture guards for interoperability adapters (PR #48).

Adapters are ingress-only. These AST/import-graph checks prove that adapter modules
cannot reach the governance internals directly: they may use the public client
boundary (``mcc_client``) and declarative helpers, but MUST NOT import the decision
engine, gate/coordinator, signing/token issuer, authority/mandate/consensus
verifier, the governed executor, or the gateway app — and MUST NOT expose local
authorize/execute/sign surfaces. Framework imports (langgraph/crewai/autogen/…) are
allowed; internal governance imports are not.
"""

from __future__ import annotations

import ast
from pathlib import Path


from tests.interoperability.conftest import ADAPTERS
from tests.interoperability.harness import AdapterProof

ADAPTERS_DIR = Path(__file__).resolve().parent / "adapters"

# Direct imports of these top-level modules are forbidden in adapter modules — they
# are the governance internals an ingress adapter must never touch.
FORBIDDEN_MODULE_PREFIXES = (
    "mcc_core", "gateway", "egress_proxy", "interceptors", "pilot_notify", "server",
)
# Names that would let an adapter mint/verify decisions or execute directly.
FORBIDDEN_NAMES = {
    "issue_vote", "SigningKey", "HTTPEgressExecutor", "EnforcementCoordinator",
    "MandateAuthority", "build_governance_service",
}
# Method names that would imply an adapter authorizes/executes/mints locally.
FORBIDDEN_METHODS = {"authorize", "execute", "sign", "mint", "verify_token", "decide"}


def _adapter_files():
    return [p for p in ADAPTERS_DIR.glob("*.py") if p.name != "__init__.py"]


def _imports(path: Path):
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    modules, names = set(), set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                modules.add(a.name)
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.add(node.module)
            for a in node.names:
                names.add(a.name)
    return modules, names


def test_adapters_do_not_import_governance_internals():
    assert _adapter_files(), "no adapter modules found"
    for path in _adapter_files():
        modules, names = _imports(path)
        for mod in modules:
            top = mod.split(".")[0]
            assert top not in FORBIDDEN_MODULE_PREFIXES, (
                f"{path.name} imports governance-internal module {mod!r}")
        leaked = names & FORBIDDEN_NAMES
        assert not leaked, f"{path.name} imports forbidden name(s) {leaked}"


def test_adapters_use_only_the_public_client_or_declarative_helpers():
    # Positive: any mcc_* import must be the public client SDK or the declarative
    # capability registry — never the governance runtime.
    for path in _adapter_files():
        modules, _ = _imports(path)
        for mod in modules:
            if mod.startswith("mcc_"):
                assert mod == "mcc_client" or mod.startswith("mcc_client.") \
                    or mod == "mcc_compliance.capability_profile", \
                    f"{path.name} imports non-public governance module {mod!r}"


def test_adapter_objects_expose_no_local_authorization_surface():
    for adapter in ADAPTERS:
        assert isinstance(adapter, AdapterProof)
        for m in FORBIDDEN_METHODS:
            assert not hasattr(adapter, m), (
                f"{adapter.adapter_name} exposes a local {m!r} surface")


def test_adapters_declare_a_classification():
    valid = {"REAL FRAMEWORK INTEGRATION", "FRAMEWORK-NEUTRAL HTTP INTEGRATION"}
    for adapter in ADAPTERS:
        assert adapter.adapter_classification in valid
