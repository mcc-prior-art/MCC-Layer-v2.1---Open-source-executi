"""Architecture guard: every assurance WORKSTREAM test module (this
directory) must reach the system under test only over its public HTTP
API -- never by importing MCC-Core's authority/policy/gate/nonce/audit/
certification/execution internals. ``assurance/sut/`` (provisioning code
that constructs the real deployment as OS subprocesses) is explicitly
exempt -- see ``assurance/sut/harness.py``'s module docstring for why.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
TESTS_DIR = REPO_ROOT / "assurance" / "tests"

FORBIDDEN_MODULES = {
    "mcc_core.gate", "mcc_core.authority", "mcc_core.coordinator", "mcc_core.nonce",
    "mcc_core.idempotency", "mcc_core.velocity", "mcc_core.mandate", "mcc_core.approvals",
    "mcc_core.consensus", "mcc_core.challenge", "mcc_core.policy", "mcc_core.audit",
    "mcc_core.core", "gateway", "egress_proxy", "interceptors", "pilot", "pilot_api",
    "mcc_conformance", "mcc_evidence", "mcc_certify",
}


def _py_files():
    return sorted(p for p in TESTS_DIR.glob("*.py") if p.name != "test_boundary_guards.py")


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
def test_no_security_internal_imports(path: Path):
    imported = _imported_modules(path.read_text(encoding="utf-8"))
    hits = {m for m in imported if any(m == f or m.startswith(f + ".") for f in FORBIDDEN_MODULES)}
    assert not hits, f"{path}: imports MCC-Core security internals: {hits}"


@pytest.mark.parametrize("path", _py_files(), ids=lambda p: p.name)
def test_only_reaches_the_sut_through_the_harness_or_http(path: Path):
    imported = _imported_modules(path.read_text(encoding="utf-8"))
    allowed_prefixes = (
        "assurance.sut.harness", "assurance.sut.vulnerable_target", "assurance.canonical_action",
        "assurance.state_machine", "assurance.evidence", "httpx", "hypothesis",
        "tests.interoperability.adapters",  # test_semantic_equivalence.py: reuses the PR #48 adapters
        "mutation",  # test_mutation_score.py: runs the mutation harness, never touches the SUT
    )
    for m in imported:
        if m.startswith("mcc_client") or m.startswith("mcc_protocol") or m in ("json", "time", "os", "sys",
                "hashlib", "uuid", "threading", "concurrent", "concurrent.futures", "subprocess", "socket",
                "dataclasses", "typing", "pathlib", "re", "random", "string", "itertools", "collections",
                "pytest", "unicodedata", "decimal", "cbor2", "struct", "base64", "copy", "__future__",
                "importlib", "shutil", "tempfile"):
            continue
        assert any(m == p or m.startswith(p + ".") for p in allowed_prefixes) or m.startswith("assurance."), (
            f"{path}: unexpected import {m!r} -- workstream tests reach the SUT only via "
            "assurance.sut.harness/vulnerable_target over real HTTP"
        )
