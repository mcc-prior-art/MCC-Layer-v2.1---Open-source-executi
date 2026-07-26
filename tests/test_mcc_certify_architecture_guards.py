"""PR #67 architecture guards: the certification pipeline is an assessment
and artifact-issuance system built ABOVE the existing governance runtime --
it must never import, bypass, or duplicate it.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
PACKAGE_DIR = REPO_ROOT / "src" / "mcc_certify"

FORBIDDEN_MODULES = {
    "gateway", "mcc_core.gate", "mcc_core.authority", "mcc_core.coordinator",
    "mcc_core.nonce", "mcc_core.idempotency", "mcc_core.velocity", "mcc_core.mandate",
    "mcc_core.approvals", "mcc_core.consensus", "mcc_core.challenge",
    "egress_proxy", "interceptors", "pilot", "pilot_api",
}

# Optional adapter-framework packages that must never be imported at module
# (package-import-time) scope by this package -- consistent with the
# next-milestone boundary (Generic HTTP / LangGraph / CrewAI / AutoGen /
# VoltAgent are not yet certified, and this package must not need them).
FORBIDDEN_FRAMEWORK_MODULES = {
    "langgraph", "autogen_core", "autogen_agentchat", "crewai", "voltagent",
    "httpx", "fastapi", "uvicorn",
}


def _py_files():
    return sorted(PACKAGE_DIR.rglob("*.py"))


def _imported_modules(source: str) -> set:
    tree = ast.parse(source)
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module)
    return imported


@pytest.mark.parametrize("path", _py_files(), ids=lambda p: p.name)
def test_no_runtime_governance_imports(path: Path):
    imported = _imported_modules(path.read_text(encoding="utf-8"))
    hits = {m for m in imported if any(m == f or m.startswith(f + ".") for f in FORBIDDEN_MODULES)}
    assert not hits, f"{path}: imports runtime-governance internals: {hits}"


@pytest.mark.parametrize("path", _py_files(), ids=lambda p: p.name)
def test_no_adapter_framework_imports_at_module_scope(path: Path):
    imported = _imported_modules(path.read_text(encoding="utf-8"))
    hits = {m for m in imported if any(m == f or m.startswith(f + ".") for f in FORBIDDEN_FRAMEWORK_MODULES)}
    assert not hits, f"{path}: imports an adapter-framework package at module scope: {hits}"


def test_package_does_not_define_a_verdict_or_decision_token_surface():
    forbidden_names = {"ALLOW", "DENY", "ESCALATE", "CONSTRAIN", "DecisionToken", "ExecutionGate", "sign_token"}
    for path in _py_files():
        tree = ast.parse(path.read_text(encoding="utf-8"))
        defined = set()
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                defined.add(node.name)
        hits = defined & forbidden_names
        assert not hits, f"{path}: defines a runtime-governance-shaped symbol: {hits}"


def test_certification_only_reuses_the_existing_eb_cm_tc_producers_and_verifiers():
    pipeline_source = (PACKAGE_DIR / "pipeline.py").read_text(encoding="utf-8")
    imported = _imported_modules(pipeline_source)
    # Reuses mcc_evidence's Wave A/B/C modules directly; never a parallel
    # Hash Reference / Evidence Bundle / Manifest / Certificate implementation.
    assert "mcc_evidence.eb001_export" in imported
    assert "mcc_evidence.eb001_verify" in imported
    assert "mcc_evidence.cm001_manifest" in imported
    assert "mcc_evidence.tc001_certificate" in imported
    # No second hash/signing primitive defined in this package, and no
    # randomly-generated signing key (deterministic derivation only -- see
    # pipeline._derive_signing_key's own module docstring for why).
    for path in _py_files():
        source = path.read_text(encoding="utf-8")
        assert "def compute_hash_reference" not in source, path
        assert "def sign_token" not in source, path
        assert "Ed25519PrivateKey.generate(" not in source, path


def test_certification_target_carries_no_authorization_or_execution_surface():
    from mcc_certify.target import CertificationTarget

    field_names = set(CertificationTarget.__dataclass_fields__.keys())
    forbidden = {"authorize", "execute", "approve", "policy", "decision", "token", "gate"}
    hits = {f for f in field_names if any(word in f.lower() for word in forbidden)}
    assert not hits, hits


def test_pipeline_never_reports_certified_before_offline_verification_stage():
    # Static guard: within CertificationPipeline.run, the assignment of
    # outcome=CertificationOutcome.CERTIFIED must textually follow the
    # offline_verification stage append -- i.e. there is exactly one success
    # path and it is provably the last thing before finalization.
    source = (PACKAGE_DIR / "pipeline.py").read_text(encoding="utf-8")
    verify_stage_idx = source.index('"offline_verification", StageStatus.PASS')
    certified_idx = source.index("outcome=CertificationOutcome.CERTIFIED,")
    assert certified_idx > verify_stage_idx
