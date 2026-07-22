"""Architecture guards for the canonical protocol layer (PR #49).

Static (AST) guarantees that the protocol + ingress pipeline are a thin,
non-authorizing platform layer: they may validate/normalize/enrich/route and reuse
pure hashing, but they MUST NOT import the governance decision internals (gate,
coordinator, authority, consensus, mandate, policy engine, audit, the gateway app,
the executor) nor the signing/token-issuing surface, and they MUST expose no local
authorize/execute/sign/issue-token/decide surface. If violated, CI fails.
"""

from __future__ import annotations

import ast
from pathlib import Path

import mcc_protocol as mp

PKG_DIR = Path(mp.__file__).resolve().parent

# Governance internals a thin ingress layer must never import.
FORBIDDEN_MODULE_PREFIXES = (
    "mcc_core.core", "mcc_core.gate", "mcc_core.coordinator", "mcc_core.authority",
    "mcc_core.consensus", "mcc_core.mandate", "mcc_core.approvals", "mcc_core.nonce",
    "mcc_core.policy", "mcc_core.audit", "mcc_core.challenge", "mcc_core.velocity",
    "mcc_core.idempotency", "mcc_core.profiles",
    "gateway", "egress_proxy", "interceptors", "server", "pilot_notify",
    "clinic_service", "pilot_api",
)
# The ONLY mcc_core surface allowed: pure canonicalization/hash helpers (so proposal
# hashes match the rest of the platform). Signing/verification is NOT allowed.
ALLOWED_SIGNING_NAMES = {"canonical_bytes", "sha256_hex", "hash_payload", "hash_action"}
FORBIDDEN_NAMES = {
    "SigningKey", "verify_token", "issue_vote", "EnforcementCoordinator",
    "MandateAuthority", "build_governance_service", "HTTPEgressExecutor", "Gate",
}
# Local surfaces that would make the layer a governance boundary.
FORBIDDEN_ATTRS = {"authorize", "execute", "sign", "verify_token", "issue_token",
                   "mint", "decide", "evaluate_policy"}


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


def test_protocol_does_not_import_governance_internals():
    assert _py_files()
    for path in _py_files():
        modules, _, _ = _imports(path)
        for mod in modules:
            for bad in FORBIDDEN_MODULE_PREFIXES:
                assert not (mod == bad or mod.startswith(bad + ".")), (
                    f"{path.name} imports governance-internal module {mod!r}")
        # A bare `import mcc_core` (whole package) is too broad — forbid it.
        assert "mcc_core" not in modules, f"{path.name} imports the whole mcc_core"


def test_only_pure_hashing_is_imported_from_signing():
    for path in _py_files():
        _, from_pairs, _ = _imports(path)
        for mod, name in from_pairs:
            if mod == "mcc_core.signing":
                assert name in ALLOWED_SIGNING_NAMES, (
                    f"{path.name} imports non-hash name {name!r} from mcc_core.signing")


def test_protocol_imports_no_signing_or_token_surface():
    for path in _py_files():
        _, _, names = _imports(path)
        leaked = names & FORBIDDEN_NAMES
        assert not leaked, f"{path.name} imports forbidden name(s) {leaked}"


def test_public_objects_expose_no_authorization_surface():
    reg = mp.AdapterRegistry()
    router = lambda p: None  # noqa: E731
    pipe = mp.CanonicalIngressPipeline(reg, router)
    objs = [pipe, reg, mp.CanonicalProposal, mp.GovernanceDecision, mp.AdapterDescriptor]
    for obj in objs:
        for attr in FORBIDDEN_ATTRS:
            assert not hasattr(obj, attr), f"{obj!r} exposes forbidden {attr!r}"


def test_pipeline_reaches_the_gateway_only_through_an_injected_router():
    # The pipeline module must not import mcc_client.MCCClient/Transport directly —
    # the gateway is reached solely via the injected Router callable.
    _, _, names = _imports(PKG_DIR / "pipeline.py")
    assert "MCCClient" not in names and "Transport" not in names


def test_single_version_axis_guard():
    import mcc_client.contract as contract
    assert mp.PROTOCOL_VERSION == contract.CONTRACT_VERSION
