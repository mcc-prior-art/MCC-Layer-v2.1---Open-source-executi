"""Governance Evidence Bundle — ALLOW/DENY export + offline verification (PR #42).

Proves the happy paths and the ALLOW/DENY evidence semantics, determinism, the
archive form, and the CLI. Tamper detection is in test_evidence_tamper.py; the
observational security boundary is in test_evidence_security.py.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from mcc_evidence import (
    BUNDLE_SCHEMA_VERSION,
    EvidenceStatus,
    IncompleteEvidenceError,
    build_manifest,
    export_bundle,
    verify_bundle,
)
from mcc_evidence.export import canonical_manifest_for_compare

from tests._evidence_fixtures import allow_input, deny_input, signing_key, trusted_keys

ROOT = Path(__file__).resolve().parents[1]


# ---- ALLOW ---------------------------------------------------------------- #

def test_allow_bundle_verifies_with_trusted_key(tmp_path):
    key = signing_key()
    out = export_bundle(allow_input(key, tmp_path=tmp_path), tmp_path / "b")
    r = verify_bundle(out, trusted_keys=trusted_keys(key))
    assert r.trusted and r.overall_status is EvidenceStatus.VERIFIED
    names = {c.name: c.status.value for c in r.checks}
    for c in ("manifest_integrity", "artifact_integrity", "signature", "policy_binding",
              "action_binding", "payload_binding", "audit_chain", "execution_consistency"):
        assert names[c] == "PASS", (c, names[c])
    assert r.outcome == "EXECUTED"


def test_allow_bundle_untrusted_signer_is_warning_not_pass(tmp_path):
    key = signing_key()
    out = export_bundle(allow_input(key, tmp_path=tmp_path), tmp_path / "b")
    r = verify_bundle(out)  # no trusted key
    assert (not r.trusted) and r.overall_status is EvidenceStatus.INTACT_UNTRUSTED_SIGNER and r.integrity_valid
    assert any("signer not anchored" in w for w in r.warnings)


def test_allow_archive_roundtrip(tmp_path):
    key = signing_key()
    arc = export_bundle(allow_input(key, tmp_path=tmp_path), tmp_path / "b", archive=True)
    assert str(arc).endswith(".tar.gz")
    assert verify_bundle(arc, trusted_keys=trusted_keys(key)).trusted


# ---- DENY ----------------------------------------------------------------- #

def test_deny_bundle_verifies_and_has_no_receipt(tmp_path):
    out = export_bundle(deny_input(tmp_path=tmp_path), tmp_path / "b")
    r = verify_bundle(out)
    # DENY has no signed token to anchor; its trusted status is DENIAL_VERIFIED.
    assert r.trusted and r.overall_status is EvidenceStatus.DENIAL_VERIFIED
    assert r.outcome == "DENIED"
    assert not (out / "execution/receipt.json").exists(), "DENY must have no receipt"
    assert (out / "execution/denial.json").exists()
    names = {c.name: c.status.value for c in r.checks}
    assert names["signature"] == "NA"
    assert names["execution_consistency"] == "PASS"


def test_deny_with_receipt_is_refused_at_export(tmp_path):
    ev = deny_input(tmp_path=tmp_path)
    ev.receipt = {"received": True, "payload_sha256": "sha256:x"}
    with pytest.raises(IncompleteEvidenceError, match="must not contain an execution receipt"):
        export_bundle(ev, tmp_path / "b")


def test_executable_verdict_without_token_refused(tmp_path):
    ev = allow_input(signing_key(), tmp_path=tmp_path)
    ev.decision_token = None
    with pytest.raises(IncompleteEvidenceError, match="requires its signed decision token"):
        export_bundle(ev, tmp_path / "b")


def test_inconsistent_proposal_refused(tmp_path):
    ev = allow_input(signing_key(), tmp_path=tmp_path)
    ev.proposal = {"amount": 999999}  # does not hash to the token payload_hash
    with pytest.raises(IncompleteEvidenceError, match="payload_hash"):
        export_bundle(ev, tmp_path / "b")


# ---- schema + determinism ------------------------------------------------- #

def test_schema_version_stamped(tmp_path):
    key = signing_key()
    out = export_bundle(allow_input(key, tmp_path=tmp_path), tmp_path / "b")
    manifest = json.loads((out / "manifest.json").read_bytes())
    assert manifest["schema_version"] == BUNDLE_SCHEMA_VERSION


def test_manifest_is_deterministic_excluding_documented_fields(tmp_path):
    key = signing_key()
    ev = allow_input(key, tmp_path=tmp_path)
    m1 = build_manifest(ev, created_at="2026-01-01T00:00:00Z", bundle_id="fixed-1")
    m2 = build_manifest(ev, created_at="2026-01-01T00:00:00Z", bundle_id="fixed-1")
    assert canonical_manifest_for_compare(m1) == canonical_manifest_for_compare(m2)
    # Different non-deterministic fields do not change the compared canonical form.
    m3 = build_manifest(ev, created_at="2099-12-31T23:59:59Z", bundle_id="other")
    assert canonical_manifest_for_compare(m1) == canonical_manifest_for_compare(m3)


def test_unsupported_schema_version_rejected(tmp_path):
    key = signing_key()
    out = export_bundle(allow_input(key, tmp_path=tmp_path), tmp_path / "b")
    manifest = json.loads((out / "manifest.json").read_bytes())
    manifest["schema_version"] = "mcc-evidence/999"
    (out / "manifest.json").write_text(json.dumps(manifest))
    r = verify_bundle(out, trusted_keys=trusted_keys(key))
    assert (not r.trusted) and r.overall_status is EvidenceStatus.UNSUPPORTED_SCHEMA


# ---- CLI ------------------------------------------------------------------ #

def _run_cli(*args):
    env = dict(os.environ, PYTHONPATH=str(ROOT / "src"))
    return subprocess.run(
        [sys.executable, "-m", "mcc_evidence", *args],
        cwd=str(ROOT), capture_output=True, text=True, env=env)


def test_cli_verify_json_and_exit_codes(tmp_path):
    key = signing_key()
    out = export_bundle(allow_input(key, tmp_path=tmp_path), tmp_path / "b")
    kid, b64 = key.kid, key.public_key_b64()

    ok = _run_cli("verify", str(out), "--trusted-key", f"{kid}={b64}", "--json")
    assert ok.returncode == 0, ok.stderr
    payload = json.loads(ok.stdout)
    assert payload["overall_status"] == "VERIFIED" and payload["trusted"] is True

    # Untrusted signer (no key) -> distinct exit code 1, not trusted.
    untrusted = _run_cli("verify", str(out), "--json")
    assert untrusted.returncode == 1
    up = json.loads(untrusted.stdout)
    assert up["overall_status"] == "INTACT_UNTRUSTED_SIGNER" and up["trusted"] is False

    # Tamper (malformed manifest) -> INVALID -> non-zero exit.
    (out / "manifest.json").write_text("{ not valid json")
    bad = _run_cli("verify", str(out), "--trusted-key", f"{kid}={b64}", "--json")
    assert bad.returncode == 2
    assert json.loads(bad.stdout)["overall_status"] == "INVALID"
