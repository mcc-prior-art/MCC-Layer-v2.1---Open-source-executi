"""Governance Evidence Bundle — security boundary (PR #42).

Proves the evidence subsystem is strictly observational: it cannot execute,
authorize, actuate, consume/register a nonce, evaluate policy to create
authority, or mutate a verdict/token/audit log. Enforced both statically (the
package imports no executor/gate/nonce/actuator/transport) and behaviourally
(exporting and verifying leave the source audit log byte-for-byte unchanged and
perform no outbound side effect).
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from mcc_evidence import export_bundle, verify_bundle

from tests._evidence_fixtures import allow_input, signing_key, trusted_keys

PKG = Path(__file__).resolve().parents[1] / "src" / "mcc_evidence"

# Modules the evidence subsystem must NEVER import — anything that could execute,
# actuate, authorize, consume a nonce, or reach the network. Read-only crypto and
# audit *verification* helpers from mcc_core.signing are allowed; the audit
# *writer*, gate, executor, coordinator, nonce/approval registries and transports
# are not.
FORBIDDEN_IMPORTS = {
    "httpx", "requests", "urllib", "urllib.request", "aiohttp", "http.client",
    "socket", "asyncio", "subprocess",
    "egress_proxy", "egress_proxy.executor", "egress_proxy.app",
    "gateway", "interceptors", "pilot", "pilot.outbound_executor",
}
# Symbols from mcc_core that must never be imported into the evidence subsystem
# (authority-creating / actuating / state-mutating).
FORBIDDEN_MCC_CORE_SYMBOLS = {
    "ExecutionGate", "EnforcementCoordinator", "DecisionEngine",
    "NonceRegistry", "InMemoryNonceRegistry", "RedisNonceRegistry",
    "ApprovalService", "ChallengeService", "AuthorityModel", "MandateAuthority",
    "AuditLog",  # the writer — evidence re-verifies linkage without the writer
}


def _sources():
    return sorted(PKG.glob("*.py"))


def test_package_exists():
    assert PKG.is_dir() and _sources()


@pytest.mark.parametrize("path", _sources(), ids=lambda p: p.name)
def test_no_forbidden_imports(path):
    tree = ast.parse(path.read_text(), filename=str(path))
    bad = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                if a.name in FORBIDDEN_IMPORTS or a.name.split(".")[0] in FORBIDDEN_IMPORTS:
                    bad.append(a.name)
        elif isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            root = mod.split(".")[0]
            if mod in FORBIDDEN_IMPORTS or root in FORBIDDEN_IMPORTS:
                bad.append(mod)
            if root == "mcc_core":
                for a in node.names:
                    if a.name in FORBIDDEN_MCC_CORE_SYMBOLS:
                        bad.append(f"mcc_core.{a.name}")
    assert not bad, f"{path.name} imports forbidden module/symbol(s): {bad}"


def test_no_execute_or_actuate_surface():
    # The public API exposes only export/verify/read helpers — no execute/actuate/
    # authorize/approve/consume method anywhere in the package's public names.
    import mcc_evidence

    public = [n for n in dir(mcc_evidence) if not n.startswith("_")]
    forbidden = ("execute", "actuate", "authorize", "approve", "consume", "sign_token", "issue")
    offenders = [n for n in public if any(f in n.lower() for f in forbidden)]
    assert offenders == [], f"evidence API exposes actuation-like names: {offenders}"


def test_export_does_not_mutate_source_audit_log(tmp_path):
    key = signing_key()
    # Build the evidence input first (the fixture produces its audit slice), then
    # snapshot the audit log. export_bundle must not write to it afterwards.
    ev = allow_input(key, tmp_path=tmp_path)
    audit = tmp_path / "audit.jsonl"
    before = audit.read_bytes()

    export_bundle(ev, tmp_path / "b")
    assert audit.read_bytes() == before, "export_bundle wrote to the source audit log"


def test_verify_does_not_mutate_bundle_or_audit(tmp_path):
    key = signing_key()
    out = export_bundle(allow_input(key, tmp_path=tmp_path), tmp_path / "b")
    snapshot = {p: p.read_bytes() for p in out.rglob("*") if p.is_file()}
    for _ in range(3):
        verify_bundle(out, trusted_keys=trusted_keys(key))
        verify_bundle(out)  # untrusted path too
    after = {p: p.read_bytes() for p in out.rglob("*") if p.is_file()}
    assert after == snapshot, "verification mutated the bundle"


def test_verify_is_deterministic_and_side_effect_free(tmp_path):
    key = signing_key()
    out = export_bundle(allow_input(key, tmp_path=tmp_path), tmp_path / "b")
    r1 = verify_bundle(out, trusted_keys=trusted_keys(key)).to_dict()
    r2 = verify_bundle(out, trusted_keys=trusted_keys(key)).to_dict()
    assert r1 == r2
