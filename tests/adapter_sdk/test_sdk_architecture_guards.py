"""Architecture guards for the Adapter SDK (PR #50).

Static (AST) guarantees that the SDK is a thin, translational layer: it may use the
public protocol interfaces and pure hashing, but it MUST NOT import the gateway,
execution gate, authority, policy engine, audit-chain mutation, runtime executor, or
private signing internals, and it MUST expose no method behaving like
authorize/allow/approve/execute/enforce/evaluate_policy/issue_token/sign_token. It
must not introduce a parallel decision/proposal/verdict/error model. CI fails if
violated.
"""

from __future__ import annotations

import ast
from pathlib import Path

import mcc_adapter_sdk as sdk

PKG_DIR = Path(sdk.__file__).resolve().parent

# Internal implementation modules a thin SDK must never import.
FORBIDDEN_MODULE_PREFIXES = (
    "mcc_core.core", "mcc_core.gate", "mcc_core.coordinator", "mcc_core.authority",
    "mcc_core.consensus", "mcc_core.mandate", "mcc_core.approvals", "mcc_core.nonce",
    "mcc_core.policy", "mcc_core.audit", "mcc_core.challenge", "mcc_core.velocity",
    "mcc_core.idempotency", "mcc_core.profiles", "mcc_core.redis_client",
    "gateway", "egress_proxy", "interceptors", "server", "pilot_notify",
    "clinic_service", "pilot_api", "mcc_compliance.runner", "mcc_compliance.program",
    "mcc_compliance.registry", "mcc_compliance.reporting", "mcc_compliance.certification",
)
# Only these pure hash names may come from mcc_core.signing (no signing/verification).
ALLOWED_SIGNING_NAMES = {"canonical_bytes", "sha256_hex", "hash_payload", "hash_action"}
FORBIDDEN_NAMES = {"SigningKey", "verify_token", "issue_vote", "EnforcementCoordinator",
                   "ExecutionGate", "MandateAuthority", "build_governance_service",
                   "HTTPEgressExecutor", "DecisionEngine"}
FORBIDDEN_ATTRS = {"authorize", "allow", "approve", "execute", "enforce",
                   "evaluate_policy", "issue_token", "sign_token", "sign", "mint", "decide"}


def _py_files():
    return sorted(PKG_DIR.glob("*.py"))


def _imports(path: Path):
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    modules, from_pairs, names = set(), [], set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                modules.add(a.name)
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.add(node.module)
            for a in node.names:
                names.add(a.name)
                from_pairs.append((node.module, a.name))
    return modules, from_pairs, names


def test_sdk_does_not_import_forbidden_internals():
    assert _py_files()
    for path in _py_files():
        modules, _, _ = _imports(path)
        for mod in modules:
            for bad in FORBIDDEN_MODULE_PREFIXES:
                assert not (mod == bad or mod.startswith(bad + ".")), \
                    f"{path.name} imports forbidden internal {mod!r}"
        assert "mcc_core" not in modules, f"{path.name} imports the whole mcc_core package"


def test_sdk_only_imports_pure_hashing_from_signing():
    for path in _py_files():
        _, from_pairs, _ = _imports(path)
        for mod, name in from_pairs:
            if mod == "mcc_core.signing":
                assert name in ALLOWED_SIGNING_NAMES, \
                    f"{path.name} imports non-hash {name!r} from mcc_core.signing"


def test_sdk_imports_no_signing_or_token_surface():
    for path in _py_files():
        _, _, names = _imports(path)
        leaked = names & FORBIDDEN_NAMES
        assert not leaked, f"{path.name} imports forbidden name(s) {leaked}"


def test_public_objects_expose_no_authorization_surface():
    from mcc_adapter_sdk import (
        AdapterContext,
        AdapterMetadata,
        AdapterRegistration,
        AdapterValidationReport,
    )
    from tests.adapter_sdk.conftest import GoodAdapter, make_router
    from mcc_adapter_sdk import AdapterRunner
    runner = AdapterRunner(GoodAdapter(), make_router("ALLOW"))
    for obj in (GoodAdapter(), runner, AdapterMetadata, AdapterContext,
                AdapterRegistration, AdapterValidationReport):
        for attr in FORBIDDEN_ATTRS:
            assert not hasattr(obj, attr), f"{obj!r} exposes forbidden {attr!r}"


def test_sdk_reuses_authoritative_models_no_parallel_hierarchy():
    # The SDK must not define its own Decision/Verdict/CanonicalProposal/GovernanceDecision.
    import inspect
    import mcc_client
    own = {name for name, obj in vars(sdk).items()
           if inspect.isclass(obj) and getattr(obj, "__module__", "").startswith("mcc_adapter_sdk")}
    forbidden = {"Decision", "Verdict", "CanonicalProposal", "GovernanceDecision",
                 "ContractErrorCode", "AdapterRegistry"}
    assert not (own & forbidden), f"SDK defines parallel model(s): {own & forbidden}"
    # And the ones it re-exposes are the SAME objects.
    import mcc_protocol
    assert sdk.runner.Decision is mcc_client.Decision
    assert mcc_protocol.CanonicalProposal.__module__ == "mcc_protocol.proposal"


def test_curated_public_api_no_wildcards():
    expected = {"SDK_VERSION", "Adapter", "AdapterMetadata", "AdapterContext",
                "AdapterRunner", "AdapterRunResult", "AdapterRegistration",
                "AdapterValidationReport", "AdapterSDKError", "Router",
                "register_adapter", "validate_adapter", "generate_adapter_evidence"}
    assert set(sdk.__all__) == expected
