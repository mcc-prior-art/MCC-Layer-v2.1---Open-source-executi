"""Static architecture guards for the Universal Proposal Service (Section 27).

Modeled on ``tests/test_mcc_agent_no_direct_egress.py``: these are AST-based
import/reference checks, not runtime behavior tests, so a future refactor
cannot silently reintroduce a second execution path, a second authority
system, or a second Gate through this layer.
"""

from __future__ import annotations

import ast
from pathlib import Path
from typing import Iterable, List, Set

ROOT = Path(__file__).resolve().parents[1]

# Modules that would make mcc_proposal / integrations.mcp / the framework
# facades an execution authority instead of a proposal/status boundary.
FORBIDDEN_MODULES = {
    "mcc_core.gate", "mcc_core.coordinator", "mcc_core.authority",
    "mcc_core.mandate", "mcc_core.approvals", "mcc_core.consensus",
    "mcc_core.velocity", "mcc_core.nonce", "mcc_core.policy",
    "gateway.governance_service", "gateway.governance_api",
    "egress_proxy.executor", "pilot_notify.governed_upstream",
    "clinic_service", "pilot.outbound_executor",
}
FORBIDDEN_NAMES = {
    "EnforcementCoordinator", "ExecutionGate", "MandateAuthority", "MandateVerifier",
    "ApprovalService", "ConsensusVerifier", "HTTPEgressExecutor", "GovernanceService",
    "SigningKey",  # private-key signing authority; mcc_proposal only ever hashes
}
# mcc_core.signing exposes pure-hash helpers (canonical_bytes/sha256_hex/
# hash_payload/hash_document/is_valid_digest) alongside signing-authority
# classes (SigningKey/verify_token/sign_token). Importing the module itself
# is fine; importing the signing-authority NAMES from it is not.
FORBIDDEN_SIGNING_NAMES = {"SigningKey", "verify_token", "public_key_from_b64"}


def _iter_py_files(*dirs: str) -> Iterable[Path]:
    for d in dirs:
        base = ROOT / d
        if not base.exists():
            continue
        yield from base.rglob("*.py")


def _imported_modules_and_names(source: str) -> "tuple[Set[str], Set[str]]":
    tree = ast.parse(source)
    modules: Set[str] = set()
    names: Set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                modules.add(alias.name)
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.add(node.module)
            for alias in node.names:
                names.add(alias.name)
    return modules, names


def _check_files(files: List[Path]) -> List[str]:
    violations: List[str] = []
    for path in files:
        source = path.read_text(encoding="utf-8")
        modules, names = _imported_modules_and_names(source)
        rel = path.relative_to(ROOT)
        for m in modules:
            if m in FORBIDDEN_MODULES or any(m == f or m.startswith(f + ".") for f in FORBIDDEN_MODULES):
                violations.append(f"{rel}: forbidden import of module {m!r}")
        for n in names:
            if n in FORBIDDEN_NAMES:
                violations.append(f"{rel}: forbidden import of name {n!r}")
        if "mcc_core.signing" in modules:
            bad = names & FORBIDDEN_SIGNING_NAMES
            if bad:
                violations.append(f"{rel}: imports signing-authority name(s) {sorted(bad)} from mcc_core.signing")
    return violations


PROPOSAL_SERVICE_FILES = list(_iter_py_files("src/mcc_proposal"))
MCP_ADAPTER_FILES = list(_iter_py_files("integrations/mcp"))


def test_mcc_proposal_package_has_no_governance_authority_imports():
    violations = _check_files(PROPOSAL_SERVICE_FILES)
    assert not violations, "\n".join(violations)


def test_mcp_adapter_has_no_governance_authority_imports():
    violations = _check_files(MCP_ADAPTER_FILES)
    assert not violations, "\n".join(violations)


def test_mcc_proposal_and_mcp_files_were_actually_found():
    """Non-vacuity guard for the two checks above: prove they scanned a
    non-trivial number of real files, not an empty/missing directory."""
    assert len(PROPOSAL_SERVICE_FILES) >= 8
    assert len(MCP_ADAPTER_FILES) >= 4


def test_service_module_never_references_durable_execution_mutators():
    """mcc_proposal.service is permitted to call ONLY ``get_state`` on the
    durable execution registry -- never reserve/commit_dispatch/
    mark_executed/mark_unknown/resolve_unknown (Section 6/9)."""
    source = (ROOT / "src" / "mcc_proposal" / "service.py").read_text(encoding="utf-8")
    forbidden_calls = ["reserve(", "commit_dispatch(", "mark_executed(", "mark_unknown(", "resolve_unknown("]
    found = [c for c in forbidden_calls if c in source]
    assert not found, f"mcc_proposal/service.py references durable-execution mutator(s): {found}"
    assert "get_state(" in source  # the one permitted read


def test_service_module_never_references_actuator_or_upstream_calls():
    source = (ROOT / "src" / "mcc_proposal" / "service.py").read_text(encoding="utf-8")
    for token in ("upstream(", "executor(", ".enforce(", "issue_token(", "sign_token("):
        assert token not in source, f"mcc_proposal/service.py references {token!r}"


def test_proposal_registry_module_never_references_idempotency_mutators():
    """Section 6: the proposal registry must never wrap or call the durable
    execution registry's admission verbs."""
    source = (ROOT / "src" / "mcc_proposal" / "registry.py").read_text(encoding="utf-8")
    for token in ("reserve(", "commit_dispatch(", "mark_executed(", "mark_unknown(", "resolve_unknown("):
        assert token not in source, f"mcc_proposal/registry.py references {token!r}"


def test_proposal_api_router_has_no_governance_decision_logic_imports():
    """Section 11: no MCC decision logic inside HTTP handlers -- the router
    may import mcc_proposal, fastapi, and pydantic, nothing governance-authoritative."""
    violations = _check_files([ROOT / "gateway" / "proposal_api.py"])
    assert not violations, "\n".join(violations)


def test_framework_facades_have_zero_actuator_or_gate_references():
    """AE-AH: LangGraph/CrewAI/AutoGen/generic_http facades never call an
    actuator or the Gate directly -- they only ever call a ProposalBackend."""
    facades_dir = ROOT / "src" / "mcc_proposal" / "adapters"
    for path in facades_dir.glob("*.py"):
        source = path.read_text(encoding="utf-8")
        for token in ("EnforcementCoordinator", ".enforce(", "upstream(", "HTTPEgressExecutor", "SigningKey"):
            assert token not in source, f"{path.relative_to(ROOT)} references {token!r}"
