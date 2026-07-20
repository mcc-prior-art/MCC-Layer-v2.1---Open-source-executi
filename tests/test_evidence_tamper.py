"""Governance Evidence Bundle — tamper detection (PR #42).

Every mutation of a valid bundle must be detected: verification must never accept
tampered evidence as VALID. Signature-anchored tampers (re-signing) are caught
because the attacker cannot produce a signature under the verifier's trusted key;
manifest/binding/audit tampers are caught by cross-checks and digest recompute.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from mcc_evidence import EvidenceStatus, export_bundle, verify_bundle

from tests._evidence_fixtures import allow_input, signing_key, trusted_keys


def _bundle(tmp_path):
    key = signing_key()
    out = export_bundle(allow_input(key, tmp_path=tmp_path), tmp_path / "b")
    return out, trusted_keys(key)


def _load(p: Path) -> dict:
    return json.loads(p.read_bytes())


def _write(p: Path, obj) -> None:
    p.write_text(json.dumps(obj))


def _assert_rejected(out, tk, *, expect_status=EvidenceStatus.INVALID):
    r = verify_bundle(out, trusted_keys=tk)
    assert not r.valid, f"tamper accepted as valid: {r.to_dict()}"
    assert r.overall_status is expect_status
    return r


# ---- decision-token / binding tampers ------------------------------------ #

def test_changed_verdict_in_token(tmp_path):
    out, tk = _bundle(tmp_path)
    tok = _load(out / "decision/token.json")
    tok["decision"] = "DENY"
    _write(out / "decision/token.json", tok)
    _assert_rejected(out, tk)  # digest mismatch + signature + binding all fire


def test_changed_verdict_in_manifest_only(tmp_path):
    out, tk = _bundle(tmp_path)
    m = _load(out / "manifest.json")
    m["decision"]["verdict"] = "DENY"
    _write(out / "manifest.json", m)
    r = _assert_rejected(out, tk)
    assert r.check("decision_binding").status.value == "FAIL"


@pytest.mark.parametrize("field", ["actor_id", "resource_id", "action"])
def test_changed_actor_resource_action_in_manifest(tmp_path, field):
    out, tk = _bundle(tmp_path)
    m = _load(out / "manifest.json")
    m["decision"][field] = "TAMPERED"
    _write(out / "manifest.json", m)
    _assert_rejected(out, tk)


@pytest.mark.parametrize("field,check", [
    ("action_hash", "action_binding"),
    ("payload_hash", "payload_binding"),
    ("policy_hash", "policy_binding"),
])
def test_changed_hashes_in_manifest(tmp_path, field, check):
    out, tk = _bundle(tmp_path)
    m = _load(out / "manifest.json")
    m["decision"][field] = "sha256:deadbeef"
    _write(out / "manifest.json", m)
    r = _assert_rejected(out, tk)
    assert r.check(check).status.value == "FAIL"


def test_changed_constraints_in_token(tmp_path):
    out, tk = _bundle(tmp_path)
    tok = _load(out / "decision/token.json")
    tok["constraints"] = {"max_amount": 1}
    _write(out / "decision/token.json", tok)
    _assert_rejected(out, tk)  # digest + signature break


def test_changed_decision_token_signature(tmp_path):
    out, tk = _bundle(tmp_path)
    tok = _load(out / "decision/token.json")
    tok["sig"] = "AAAA" + tok["sig"][4:]
    _write(out / "decision/token.json", tok)
    r = _assert_rejected(out, tk)
    assert r.check("signature").status.value == "FAIL"


def test_resign_with_untrusted_key_is_not_valid(tmp_path):
    # Attacker re-signs a changed token with THEIR key and updates the manifest
    # consistently. Without a matching trusted key this can never be VALID.
    out, tk = _bundle(tmp_path)
    attacker = signing_key()
    tok = _load(out / "decision/token.json")
    tok["decision"] = "ALLOW"  # (already allow, but re-sign under attacker key)
    unsigned = {k: v for k, v in tok.items() if k != "sig"}
    unsigned["kid"] = attacker.kid
    from mcc_core.signing import canonical_bytes
    import base64
    sig = attacker._private_key.sign(canonical_bytes(unsigned))  # noqa: SLF001
    forged = {**unsigned, "sig": base64.b64encode(sig).decode()}
    _write(out / "decision/token.json", forged)
    # Fix the manifest digest + signer so integrity/binding pass, but the trusted
    # key does not match the attacker kid.
    m = _load(out / "manifest.json")
    from mcc_core.signing import sha256_hex
    for a in m["artifacts"]:
        if a["path"] == "decision/token.json":
            a["sha256"] = sha256_hex((out / "decision/token.json").read_bytes())
    m["decision"]["signing_kid"] = attacker.kid
    _write(out / "manifest.json", m)
    r = verify_bundle(out, trusted_keys=tk)  # tk is the ORIGINAL trusted key
    assert not r.valid
    assert r.check("signature").status.value == "FAIL"


# ---- receipt / execution tampers ----------------------------------------- #

def test_changed_execution_receipt(tmp_path):
    out, tk = _bundle(tmp_path)
    rec = _load(out / "execution/receipt.json")
    rec["payload_sha256"] = "sha256:deadbeef"
    _write(out / "execution/receipt.json", rec)
    _assert_rejected(out, tk)  # digest mismatch (+ payload_binding if manifest fixed)


# ---- audit-chain tampers -------------------------------------------------- #

def _audit_lines(out):
    return [json.loads(x) for x in (out / "audit/entries.jsonl").read_text().splitlines() if x.strip()]


def _write_audit(out, entries):
    (out / "audit/entries.jsonl").write_bytes(
        b"".join(json.dumps(e, sort_keys=True, separators=(",", ":")).encode() + b"\n" for e in entries))
    # keep the manifest digest honest so we exercise audit_chain, not just digests
    m = _load(out / "manifest.json")
    from mcc_core.signing import sha256_hex
    for a in m["artifacts"]:
        if a["path"] == "audit/entries.jsonl":
            a["sha256"] = sha256_hex((out / "audit/entries.jsonl").read_bytes())
    _write(out / "manifest.json", m)


def test_deleted_audit_entry(tmp_path):
    out, tk = _bundle(tmp_path)
    entries = _audit_lines(out)
    _write_audit(out, entries[:1])  # drop the last, break anchor.count/last_hash
    r = _assert_rejected(out, tk)
    assert r.check("audit_chain").status.value == "FAIL"


def test_reordered_audit_entries(tmp_path):
    out, tk = _bundle(tmp_path)
    entries = _audit_lines(out)
    _write_audit(out, list(reversed(entries)))
    r = _assert_rejected(out, tk)
    assert r.check("audit_chain").status.value == "FAIL"


def test_changed_prev_hash_linkage(tmp_path):
    out, tk = _bundle(tmp_path)
    entries = _audit_lines(out)
    entries[1]["prev_hash"] = "0" * 64
    _write_audit(out, entries)
    r = _assert_rejected(out, tk)
    assert r.check("audit_chain").status.value == "FAIL"


def test_changed_audit_entry_body(tmp_path):
    out, tk = _bundle(tmp_path)
    entries = _audit_lines(out)
    entries[0]["event"] = "tampered"
    _write_audit(out, entries)
    r = _assert_rejected(out, tk)
    assert r.check("audit_chain").status.value == "FAIL"


# ---- manifest / file-set tampers ----------------------------------------- #

def test_added_unmanifested_file(tmp_path):
    out, tk = _bundle(tmp_path)
    (out / "sneaky.json").write_text("{}")
    r = _assert_rejected(out, tk)
    assert r.check("artifact_integrity").status.value == "FAIL"


def test_removed_manifested_file(tmp_path):
    out, tk = _bundle(tmp_path)
    (out / "execution/receipt.json").unlink()
    r = _assert_rejected(out, tk)
    assert r.check("artifact_integrity").status.value == "FAIL"


def test_digest_mismatch(tmp_path):
    out, tk = _bundle(tmp_path)
    (out / "gate/result.json").write_text('{"allowed": false}')  # content changed, digest not
    r = _assert_rejected(out, tk)
    assert r.check("artifact_integrity").status.value == "FAIL"


def test_malformed_manifest(tmp_path):
    out, tk = _bundle(tmp_path)
    (out / "manifest.json").write_text("{ not json")
    _assert_rejected(out, tk)


def test_duplicate_logical_entries(tmp_path):
    out, tk = _bundle(tmp_path)
    m = _load(out / "manifest.json")
    m["artifacts"].append(dict(m["artifacts"][0]))
    _write(out / "manifest.json", m)
    r = _assert_rejected(out, tk)
    assert r.check("manifest_integrity").status.value == "FAIL"


def test_unsupported_schema_version(tmp_path):
    out, tk = _bundle(tmp_path)
    m = _load(out / "manifest.json")
    m["schema_version"] = "mcc-evidence/999"
    _write(out / "manifest.json", m)
    _assert_rejected(out, tk, expect_status=EvidenceStatus.UNSUPPORTED_SCHEMA)


def test_corrupt_archive(tmp_path):
    key = signing_key()
    arc = export_bundle(allow_input(key, tmp_path=tmp_path), tmp_path / "b", archive=True)
    Path(arc).write_bytes(b"not a gzip tar at all")
    r = verify_bundle(arc, trusted_keys=trusted_keys(key))
    assert not r.valid


def test_conflicting_decision_ids(tmp_path):
    out, tk = _bundle(tmp_path)
    m = _load(out / "manifest.json")
    m["decision"]["decision_id"] = "different-jti"
    _write(out / "manifest.json", m)
    r = _assert_rejected(out, tk)
    assert r.check("decision_binding").status.value == "FAIL"
