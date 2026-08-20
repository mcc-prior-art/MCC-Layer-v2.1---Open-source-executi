"""External Checkpoint Anchoring -- Mitigating Scenario G (Detectable
Full-Chain Rewrite via External Checkpoint Anchoring).

Required areas, each independently testable, real fault injection over
mocks (matching Gate 1 / Gate 2 discipline):

  1. Checkpoint generated correctly at N-record and T-time triggers.
  2. The checkpoint chain (``prev_checkpoint_hash``) itself detects
     tampering of a non-tail checkpoint.
  3. A simulated full-storage rewrite of a non-tail audit record ->
     ``verify_anchors`` raises ``AuditAnchorMismatchError``.
  4. Layer A: a REAL protected git branch (local bare repo + pre-receive
     hook, the exact mechanism GitHub branch protection uses server-side)
     blocks a force-push rewrite of the anchor branch. This validates
     append-only interaction semantics only -- it is NOT a claim about
     real GitHub infrastructure (see docs/AUDIT_CHECKPOINT_ANCHORING.md
     for the Layer B distinction and its PENDING EXTERNAL-ANCHOR
     CONFIGURATION status).
  5. Negative control: a valid, untampered chain + valid anchors ->
     ``verify_anchors`` passes clean, zero false positives.
  6. Startup verification path: cold start with N checkpoints present,
     one deliberately corrupted -> the Gateway's ``/ready`` endpoint
     refuses to reach ready state (fail-closed, latched, not
     degrade-and-continue).
  7. Signing-key separation: checkpoints are signed by a DEDICATED Audit
     Checkpoint key, never the Decision Token key; a checkpoint signed
     with the wrong key is rejected.
  8. Canonical-serialization / malformed-input regression coverage: field
     ordering, unsupported checkpoint versions, malformed signatures,
     altered payloads.
"""

from __future__ import annotations

import hashlib
import json
import os
import stat
import subprocess
from pathlib import Path

import pytest

from mcc_core.audit import AuditLog
from mcc_core.signing import SigningKey, canonical_bytes
from mcc_checkpoint import (
    AuditAnchorMismatchError,
    CheckpointGenerator,
    CheckpointSigningKeyError,
    GitBranchAnchorStore,
    InMemoryAnchorStore,
    load_checkpoint_signing_key,
    verify_anchors,
    verify_checkpoint_chain_linkage,
    verify_checkpoint_signature,
)
from mcc_checkpoint.checkpoint import build_checkpoint, checkpoint_hash
from mcc_checkpoint.errors import AnchorStoreError, CheckpointGenerationError
from mcc_checkpoint.schema import CHECKPOINT_SCHEMA_VERSION

CHAIN_ID = "test-chain"
ENVIRONMENT = "test"


def _seed_audit(path: str, count: int) -> AuditLog:
    audit = AuditLog(path)
    for i in range(count):
        audit.append({"seq": i, "action": f"test-action-{i}"})
    return audit


def _entry_hash(prev_hash: str, body: dict) -> str:
    return hashlib.sha256(prev_hash.encode("utf-8") + canonical_bytes(body)).hexdigest()


def _rewrite_record_and_recompute_forward(audit_path: str, tamper_index: int, mutate) -> None:
    """Simulate the Scenario G attack: an actor with full write access to
    audit storage alters record ``tamper_index`` (via ``mutate``, applied
    to that record's dict) and recomputes every subsequent hash so the
    resulting file is internally self-consistent -- i.e. this is NOT a
    corrupt/garbage rewrite; ``AuditLog.verify_chain`` must still return
    True afterwards (asserted by callers), matching the disclosed threat
    model exactly."""
    with open(audit_path, encoding="utf-8") as fh:
        entries = [json.loads(line) for line in fh if line.strip()]

    mutate(entries[tamper_index])
    prev_hash = entries[tamper_index - 1]["hash"] if tamper_index > 0 else "GENESIS"
    for i in range(tamper_index, len(entries)):
        body = {k: v for k, v in entries[i].items() if k != "hash"}
        body["prev_hash"] = prev_hash
        new_hash = _entry_hash(prev_hash, body)
        entries[i] = {**body, "hash": new_hash}
        prev_hash = new_hash

    with open(audit_path, "w", encoding="utf-8") as fh:
        for entry in entries:
            fh.write(json.dumps(entry, sort_keys=True) + "\n")


def _make_generator(audit_path, checkpoint_key, store, **kwargs):
    kwargs.setdefault("record_interval", 5)
    kwargs.setdefault("time_interval_seconds", 10_000)
    kwargs.setdefault("repo_sha", "deadbeef")
    return CheckpointGenerator(
        audit_path=audit_path, signing_key=checkpoint_key, anchor_store=store,
        chain_id=CHAIN_ID, environment=ENVIRONMENT, **kwargs,
    )


# ---------------------------------------------------------------------
# 1. N-record and T-time trigger boundary conditions
# ---------------------------------------------------------------------

def test_checkpoint_triggers_at_n_record_boundary_not_before(tmp_path):
    audit_path = str(tmp_path / "audit.jsonl")
    _seed_audit(audit_path, 4)  # one below the N=5 threshold

    key = SigningKey.generate("ckpt-key-1")
    store = InMemoryAnchorStore()
    gen = _make_generator(audit_path, key, store)

    assert gen.maybe_checkpoint() is None, "must not fire below the N-record threshold"

    audit = AuditLog(audit_path)
    audit.append({"seq": 4})  # now exactly at the threshold (5 new records)
    checkpoint = gen.maybe_checkpoint()
    assert checkpoint is not None, "must fire exactly AT the N-record threshold"
    assert checkpoint["record_count"] == 5
    assert store.read_all_checkpoints() == [checkpoint]


def test_checkpoint_triggers_at_t_time_boundary_even_with_few_records(tmp_path):
    audit_path = str(tmp_path / "audit.jsonl")
    _seed_audit(audit_path, 2)  # far below any reasonable N

    fake_now = [1000.0]
    key = SigningKey.generate("ckpt-key-2")
    store = InMemoryAnchorStore()
    gen = _make_generator(
        audit_path, key, store, record_interval=500, time_interval_seconds=15 * 60,
        clock=lambda: fake_now[0],
    )

    assert gen.maybe_checkpoint() is None, "must not fire before T elapses"

    fake_now[0] += (15 * 60) - 1
    assert gen.maybe_checkpoint() is None, "must not fire 1 second before the T threshold"

    fake_now[0] += 1  # now exactly at 15 minutes elapsed
    checkpoint = gen.maybe_checkpoint()
    assert checkpoint is not None, "must fire exactly AT the T-time threshold"
    assert checkpoint["record_count"] == 2


def test_checkpoint_does_not_refire_with_zero_new_records_even_past_t(tmp_path):
    audit_path = str(tmp_path / "audit.jsonl")
    _seed_audit(audit_path, 3)

    fake_now = [0.0]
    key = SigningKey.generate("ckpt-key-3")
    store = InMemoryAnchorStore()
    gen = _make_generator(
        audit_path, key, store, record_interval=500, time_interval_seconds=60,
        clock=lambda: fake_now[0],
    )
    fake_now[0] += 61
    assert gen.maybe_checkpoint() is not None

    fake_now[0] += 1000  # T elapses again, but NO new audit records were appended
    assert gen.maybe_checkpoint() is None


def test_first_checkpoint_has_null_prev_checkpoint_hash(tmp_path):
    audit_path = str(tmp_path / "audit.jsonl")
    _seed_audit(audit_path, 5)
    key = SigningKey.generate("ckpt-key-4")
    store = InMemoryAnchorStore()
    gen = _make_generator(audit_path, key, store, record_interval=1)
    checkpoint = gen.maybe_checkpoint()
    assert checkpoint["prev_checkpoint_hash"] is None


def test_second_checkpoint_links_to_first_via_prev_checkpoint_hash(tmp_path):
    audit_path = str(tmp_path / "audit.jsonl")
    audit = _seed_audit(audit_path, 5)
    key = SigningKey.generate("ckpt-key-5")
    store = InMemoryAnchorStore()
    gen = _make_generator(audit_path, key, store)
    first = gen.maybe_checkpoint()
    for i in range(5):
        audit.append({"seq": 5 + i})
    second = gen.maybe_checkpoint()
    assert second["prev_checkpoint_hash"] == checkpoint_hash(first)


def test_checkpoint_carries_chain_id_environment_and_signing_key_id(tmp_path):
    audit_path = str(tmp_path / "audit.jsonl")
    _seed_audit(audit_path, 5)
    key = SigningKey.generate("ckpt-key-fields")
    store = InMemoryAnchorStore()
    gen = _make_generator(audit_path, key, store)
    checkpoint = gen.maybe_checkpoint()
    assert checkpoint["chain_id"] == CHAIN_ID
    assert checkpoint["environment"] == ENVIRONMENT
    assert checkpoint["signing_key_id"] == "ckpt-key-fields"
    assert checkpoint["kid"] == "ckpt-key-fields"
    assert checkpoint["checkpoint_version"] == CHECKPOINT_SCHEMA_VERSION


# ---------------------------------------------------------------------
# 2. Checkpoint-chain self-tamper detection
# ---------------------------------------------------------------------

def _anchor_n_checkpoints(tmp_path, n=4, per=5):
    audit_path = str(tmp_path / "audit.jsonl")
    audit = _seed_audit(audit_path, per)
    key = SigningKey.generate("ckpt-key-chain")
    store = InMemoryAnchorStore()
    gen = _make_generator(audit_path, key, store, record_interval=per)
    gen.maybe_checkpoint()
    for _ in range(n - 1):
        for i in range(per):
            audit.append({"seq": i})
        gen.maybe_checkpoint()
    return audit_path, key, store


def test_checkpoint_chain_linkage_passes_clean_when_untampered(tmp_path):
    _audit_path, _key, store = _anchor_n_checkpoints(tmp_path)
    verify_checkpoint_chain_linkage(store.read_all_checkpoints())  # must not raise


def test_checkpoint_chain_linkage_detects_tampered_non_tail_checkpoint_claims(tmp_path):
    _audit_path, _key, store = _anchor_n_checkpoints(tmp_path)
    checkpoints = store.read_all_checkpoints()
    assert len(checkpoints) >= 3
    tampered = dict(checkpoints[1])
    tampered["record_count"] = tampered["record_count"] + 999  # attacker edits a claim field
    store._checkpoints[1] = tampered

    with pytest.raises(AuditAnchorMismatchError):
        verify_checkpoint_chain_linkage(store.read_all_checkpoints())


def test_checkpoint_chain_linkage_detects_tampered_non_tail_checkpoint_signature(tmp_path):
    _audit_path, _key, store = _anchor_n_checkpoints(tmp_path)
    checkpoints = store.read_all_checkpoints()
    tampered = dict(checkpoints[1])
    tampered["sig"] = "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
    store._checkpoints[1] = tampered

    with pytest.raises(AuditAnchorMismatchError):
        verify_checkpoint_chain_linkage(store.read_all_checkpoints())


# ---------------------------------------------------------------------
# 3. Self-consistent audit-record rewrite -> AuditAnchorMismatchError
# ---------------------------------------------------------------------

def test_self_consistent_rewrite_of_non_tail_record_is_detected(tmp_path):
    audit_path = str(tmp_path / "audit.jsonl")
    _seed_audit(audit_path, 10)
    key = SigningKey.generate("ckpt-key-g")
    store = InMemoryAnchorStore()
    gen = _make_generator(audit_path, key, store, record_interval=10)
    gen.maybe_checkpoint()  # anchors record_count=10

    _rewrite_record_and_recompute_forward(
        audit_path, tamper_index=3, mutate=lambda e: e.__setitem__("action", "TAMPERED")
    )

    # Confirms this really is "Scenario G": the internal chain still
    # validates on its own after the self-consistent rewrite.
    assert AuditLog.verify_chain(audit_path) is True

    with pytest.raises(AuditAnchorMismatchError):
        verify_anchors(audit_path=audit_path, anchor_store=store,
                        trusted_public_key=key.public_key())


def test_self_consistent_rewrite_of_the_tail_record_is_also_detected(tmp_path):
    audit_path = str(tmp_path / "audit.jsonl")
    _seed_audit(audit_path, 8)
    key = SigningKey.generate("ckpt-key-g2")
    store = InMemoryAnchorStore()
    gen = _make_generator(audit_path, key, store, record_interval=8)
    gen.maybe_checkpoint()

    _rewrite_record_and_recompute_forward(
        audit_path, tamper_index=7, mutate=lambda e: e.__setitem__("action", "TAMPERED_TAIL")
    )
    assert AuditLog.verify_chain(audit_path) is True

    with pytest.raises(AuditAnchorMismatchError):
        verify_anchors(audit_path=audit_path, anchor_store=store,
                        trusted_public_key=key.public_key())


def test_rewrite_before_any_checkpoint_boundary_still_detected_at_next_checkpoint(tmp_path):
    """Rewriting a record BEFORE the anchored prefix's boundary (not just
    within it) must still be caught -- the whole prefix up to
    ``record_count`` is recomputed, not merely the boundary record."""
    audit_path = str(tmp_path / "audit.jsonl")
    _seed_audit(audit_path, 20)
    key = SigningKey.generate("ckpt-key-g3")
    store = InMemoryAnchorStore()
    gen = _make_generator(audit_path, key, store, record_interval=20)
    gen.maybe_checkpoint()  # anchors record_count=20

    _rewrite_record_and_recompute_forward(
        audit_path, tamper_index=0, mutate=lambda e: e.__setitem__("action", "TAMPERED_GENESIS_AREA")
    )
    assert AuditLog.verify_chain(audit_path) is True

    with pytest.raises(AuditAnchorMismatchError):
        verify_anchors(audit_path=audit_path, anchor_store=store,
                        trusted_public_key=key.public_key())


# ---------------------------------------------------------------------
# 4. Layer A: a real protected git branch blocks a force-push rewrite
#    attempt. NOT a claim about live GitHub infrastructure -- see
#    docs/AUDIT_CHECKPOINT_ANCHORING.md's Layer A/Layer B distinction.
# ---------------------------------------------------------------------

_PRE_RECEIVE_HOOK = """#!/bin/sh
# Reject any non-fast-forward ref update -- the exact server-side check
# GitHub branch protection ("require linear history" + "block force
# pushes") performs, reimplemented literally so this test exercises a
# REAL protected branch's append-only interaction semantics, not a mock
# of one. This does NOT stand in for real GitHub ruleset enforcement --
# see docs/AUDIT_CHECKPOINT_ANCHORING.md Layer A vs Layer B.
zero="0000000000000000000000000000000000000000"
while read oldrev newrev refname; do
  if [ "$oldrev" != "$zero" ] && [ "$newrev" != "$zero" ]; then
    if ! git merge-base --is-ancestor "$oldrev" "$newrev"; then
      echo "REJECTED: non-fast-forward update to $refname" >&2
      exit 1
    fi
  fi
done
exit 0
"""


def _make_protected_bare_remote(path: Path) -> str:
    subprocess.run(["git", "init", "--bare", "-q", str(path)], check=True)
    hook_path = path / "hooks" / "pre-receive"
    hook_path.write_text(_PRE_RECEIVE_HOOK, encoding="utf-8")
    hook_path.chmod(hook_path.stat().st_mode | stat.S_IEXEC)
    return str(path)


def test_git_branch_anchor_store_normal_append_is_a_fast_forward_push(tmp_path):
    remote = _make_protected_bare_remote(tmp_path / "remote.git")
    store = GitBranchAnchorStore(
        remote_url=remote, branch="audit-checkpoint-anchors", workdir=str(tmp_path / "workdir"),
    )
    checkpoint = {
        "checkpoint_version": "1.0", "chain_id": CHAIN_ID, "environment": ENVIRONMENT,
        "record_count": 10, "chain_head_hash": "abc", "prev_checkpoint_hash": None,
        "timestamp": "2026-08-20T00:00:00Z", "signing_key_id": "k1", "repo_sha": "deadbeef",
        "kid": "k1", "sig": "sig1",
    }
    store.append_checkpoint(checkpoint)  # must succeed against the protected branch
    assert store.read_all_checkpoints() == [checkpoint]


def test_protected_branch_rejects_force_push_after_history_rewrite(tmp_path):
    """The core Layer A requirement: even if an attacker has full local
    write access to the anchor workdir's git history (able to amend/
    rebase commits, mirroring "full write access to audit-chain storage"
    for the anchor side too), a REAL protected branch's pre-receive hook
    rejects the non-fast-forward push. This is a real subprocess git push
    against a real bare repository with a real hook -- no mocking. This
    proves append-only interaction semantics; it is explicitly NOT a
    substitute for real GitHub ruleset/branch-protection evidence
    (Layer B, see docs/AUDIT_CHECKPOINT_ANCHORING.md)."""
    remote = _make_protected_bare_remote(tmp_path / "remote.git")
    workdir = tmp_path / "workdir"
    store = GitBranchAnchorStore(
        remote_url=remote, branch="audit-checkpoint-anchors", workdir=str(workdir),
    )
    for i in range(3):
        store.append_checkpoint({
            "checkpoint_version": "1.0", "chain_id": CHAIN_ID, "environment": ENVIRONMENT,
            "record_count": (i + 1) * 10, "chain_head_hash": f"head-{i}",
            "prev_checkpoint_hash": None, "timestamp": "2026-08-20T00:00:00Z",
            "signing_key_id": "k1", "repo_sha": "deadbeef", "kid": "k1", "sig": f"sig-{i}",
        })

    # Simulate the attacker: locally rewrite history (amend a non-tail
    # commit) and attempt to force-push over the already-anchored commits.
    subprocess.run(["git", "checkout", "audit-checkpoint-anchors"], cwd=workdir, check=True,
                    capture_output=True)
    subprocess.run(
        ["git", "rebase", "-i", "HEAD~2", "--exec",
         'git commit --amend -m "TAMPERED" --allow-empty -q'],
        cwd=workdir, check=True, capture_output=True, env={**os.environ, "GIT_SEQUENCE_EDITOR": "true"},
    )
    force_push = subprocess.run(
        ["git", "push", "--force", "origin", "audit-checkpoint-anchors"],
        cwd=workdir, capture_output=True, text=True,
    )
    assert force_push.returncode != 0, "the protected branch must reject the force-push"
    assert "rejected" in (force_push.stderr or "").lower()

    # The rejected force-push above is the actual assertion under test.
    # append_checkpoint() itself always fetches+resets to origin before
    # committing, so a SUBSEQUENT honest append from a fresh store would
    # self-heal rather than reproduce the rejection -- what matters is
    # confirming the remote's true history was never altered by the
    # attacker's rejected force-push, checked by re-reading it fresh below.
    reader = GitBranchAnchorStore(
        remote_url=remote, branch="audit-checkpoint-anchors", workdir=str(tmp_path / "reader"),
    )
    checkpoints = reader.read_all_checkpoints()
    assert len(checkpoints) == 3, "the rejected force-push must not have altered anchored history"
    assert checkpoints[0]["record_count"] == 10
    assert checkpoints[-1]["record_count"] == 30


# ---------------------------------------------------------------------
# 5. Negative control -- valid chain, valid anchors, zero false positives
# ---------------------------------------------------------------------

def test_negative_control_untampered_chain_and_anchors_verify_clean(tmp_path):
    audit_path, key, store = _anchor_n_checkpoints(tmp_path, n=5, per=7)
    result = verify_anchors(audit_path=audit_path, anchor_store=store,
                             trusted_public_key=key.public_key())
    assert result.ok is True
    assert result.checkpoints_verified == 5
    assert result.reason == "ALL_ANCHORED_CHECKPOINTS_VERIFIED"


def test_negative_control_chain_growth_after_last_checkpoint_is_not_a_false_positive(tmp_path):
    audit_path, key, store = _anchor_n_checkpoints(tmp_path, n=2, per=5)
    audit = AuditLog(audit_path)
    for i in range(3):  # grow the chain past the last checkpoint's record_count
        audit.append({"seq": 100 + i})
    result = verify_anchors(audit_path=audit_path, anchor_store=store,
                             trusted_public_key=key.public_key())
    assert result.ok is True  # growth after the checkpointed prefix is expected and fine


def test_negative_control_no_anchored_checkpoints_yet_is_not_a_failure(tmp_path):
    audit_path = str(tmp_path / "audit.jsonl")
    _seed_audit(audit_path, 3)
    key = SigningKey.generate("ckpt-key-empty")
    store = InMemoryAnchorStore()
    result = verify_anchors(audit_path=audit_path, anchor_store=store,
                             trusted_public_key=key.public_key())
    assert result.ok is True
    assert result.checkpoints_verified == 0


def test_negative_control_wrong_trusted_key_is_rejected_not_silently_passed(tmp_path):
    audit_path, _key, store = _anchor_n_checkpoints(tmp_path, n=2, per=5)
    wrong_key = SigningKey.generate("some-other-key")
    with pytest.raises(AuditAnchorMismatchError):
        verify_anchors(audit_path=audit_path, anchor_store=store,
                        trusted_public_key=wrong_key.public_key())


# ---------------------------------------------------------------------
# 6. Startup / readiness fail-closed + latched path
# ---------------------------------------------------------------------

def _reset_gateway_audit(gw):
    audit_path = gw.settings.audit_log_path
    Path(audit_path).parent.mkdir(parents=True, exist_ok=True)
    if Path(audit_path).exists():
        Path(audit_path).unlink()
    if Path(audit_path + ".lock").exists():
        Path(audit_path + ".lock").unlink()
    return audit_path


def test_gateway_ready_endpoint_fails_closed_and_latches_on_anchor_mismatch(tmp_path, monkeypatch):
    import gateway.app as gw
    import mcc_checkpoint
    from fastapi.testclient import TestClient

    audit_path = _reset_gateway_audit(gw)
    audit = AuditLog(audit_path)
    for i in range(20):
        audit.append({"seq": i})

    store = InMemoryAnchorStore()
    # Use the REAL gateway checkpoint-signing key (never gateway.signing_key
    # -- the Decision Token key), matching what the production
    # _checkpoint_anchors_ok verifies against.
    gen = _make_generator(audit_path, gw.gateway.checkpoint_signing_key, store, record_interval=5)
    for _ in range(4):
        gen.maybe_checkpoint()
        for i in range(5):
            audit.append({"seq": i})

    # Exercise the REAL, unmodified _checkpoint_anchors_ok by making
    # anchor_store_from_env hand back this test's in-memory store -- not a
    # hand-rolled replacement of _checkpoint_anchors_ok itself, so the
    # test proves the actual fail-closed exception handling in
    # gateway/app.py, not a reimplementation of it.
    monkeypatch.setattr(mcc_checkpoint, "anchor_store_from_env", lambda env: store)
    monkeypatch.setenv("MCC_REQUIRE_CHECKPOINT_ANCHOR_VERIFICATION", "true")
    gw.gateway.checkpoint_anchor_mismatch_latched = False  # isolate from other tests

    client = TestClient(gw.app)

    # Cold-start with valid, untampered checkpoints: ready.
    resp = client.get("/ready")
    assert resp.json()["checks"]["checkpoint_anchors"] is True

    # Now deliberately corrupt one anchored checkpoint (simulating a
    # tampered/corrupted checkpoint being present at cold start).
    corrupted = dict(store._checkpoints[1])
    corrupted["chain_head_hash"] = "0" * 64
    store._checkpoints[1] = corrupted

    resp = client.get("/ready")
    body = resp.json()
    assert resp.status_code == 503, "must refuse ready state, not degrade-and-continue"
    assert body["ready"] is False
    assert body["checks"]["checkpoint_anchors"] is False
    assert gw.gateway.checkpoint_anchor_mismatch_latched is True

    # Repair the store back to a clean state -- the latch must NOT
    # silently un-latch just because a later check would look clean.
    store._checkpoints[1] = dict(store._checkpoints[1])  # no-op copy for clarity
    fixed_store = InMemoryAnchorStore()
    monkeypatch.setattr(mcc_checkpoint, "anchor_store_from_env", lambda env: fixed_store)
    resp = client.get("/ready")
    assert resp.status_code == 503, "a latched mismatch must never silently un-latch"
    assert resp.json()["checks"]["checkpoint_anchors"] is False

    gw.gateway.checkpoint_anchor_mismatch_latched = False  # cleanup for other tests


def test_checkpoint_anchor_check_is_opt_in_and_absent_by_default(tmp_path, monkeypatch):
    """Confirms this is purely additive: a deployment that never sets
    MCC_REQUIRE_CHECKPOINT_ANCHOR_VERIFICATION is entirely unaffected --
    the key is simply absent from /ready's checks, exactly like the
    existing consensus/challenge opt-in checks."""
    import gateway.app as gw
    from fastapi.testclient import TestClient

    monkeypatch.delenv("MCC_REQUIRE_CHECKPOINT_ANCHOR_VERIFICATION", raising=False)
    client = TestClient(gw.app)
    resp = client.get("/ready")
    assert "checkpoint_anchors" not in resp.json()["checks"]


# ---------------------------------------------------------------------
# 7. Signing-key separation
# ---------------------------------------------------------------------

def test_decision_token_key_and_checkpoint_key_are_cryptographically_distinct(tmp_path):
    import gateway.app as gw
    assert gw.gateway.signing_key.kid != gw.gateway.checkpoint_signing_key.kid
    assert (gw.gateway.signing_key.public_key_b64()
            != gw.gateway.checkpoint_signing_key.public_key_b64())


def test_checkpoint_signed_with_decision_token_key_does_not_verify_against_checkpoint_key(tmp_path):
    """Proves the trust domains are actually separate, not merely
    differently-named: a checkpoint issued with one key must be REJECTED
    when verified against a different key's public key."""
    decision_token_key = SigningKey.generate("decision-token-key")
    checkpoint_key = SigningKey.generate("checkpoint-key")

    forged = build_checkpoint(
        decision_token_key, chain_id=CHAIN_ID, environment=ENVIRONMENT,
        record_count=1, chain_head_hash="a" * 64, prev_checkpoint_hash=None,
        repo_sha="deadbeef",
    )
    assert verify_checkpoint_signature(forged, checkpoint_key.public_key()) is False
    assert verify_checkpoint_signature(forged, decision_token_key.public_key()) is True


def test_load_checkpoint_signing_key_refuses_same_file_as_forbidden_path(tmp_path):
    key_path = str(tmp_path / "shared.pem")
    # Materialize a real PEM at key_path first (from_pem_file requires one).
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

    raw = Ed25519PrivateKey.generate()
    pem = raw.private_bytes(
        serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()
    )
    Path(key_path).write_bytes(pem)

    with pytest.raises(CheckpointSigningKeyError):
        load_checkpoint_signing_key(key_path=key_path, forbidden_key_path=key_path)


def test_load_checkpoint_signing_key_ephemeral_generation_is_fine_without_a_path():
    key = load_checkpoint_signing_key(forbidden_key_path="/some/decision/token/key.pem")
    assert key.kid  # generated successfully, no collision possible without a real path


# ---------------------------------------------------------------------
# 8. Canonical-serialization / malformed-input regression coverage
# ---------------------------------------------------------------------

def test_canonicalization_is_independent_of_python_dict_insertion_order(tmp_path):
    key = SigningKey.generate("canon-key")
    claims_a = {
        "checkpoint_version": "1.0", "chain_id": CHAIN_ID, "environment": ENVIRONMENT,
        "chain_head_hash": "abc", "record_count": 5, "prev_checkpoint_hash": None,
        "timestamp": "2026-08-20T00:00:00Z", "signing_key_id": "canon-key", "repo_sha": "deadbeef",
    }
    claims_b = dict(reversed(list(claims_a.items())))  # same content, different insertion order
    assert canonical_bytes(claims_a) == canonical_bytes(claims_b)

    token_a = key.sign_token(dict(claims_a))
    # A token built from the reordered dict must verify identically --
    # canonical_bytes, not dict iteration order, governs the signed bytes.
    reordered_claims = {k: token_a[k] for k in reversed(list(token_a.keys())) if k not in ("kid", "sig")}
    reconstructed = {**reordered_claims, "kid": token_a["kid"], "sig": token_a["sig"]}
    assert verify_checkpoint_signature(reconstructed, key.public_key()) is True


def test_duplicate_json_keys_collapse_before_reaching_the_signed_object(tmp_path):
    """Python's json.loads already collapses duplicate keys to the last
    occurrence before any checkpoint code ever sees the object -- so
    there is no "ambiguous duplicate-field" representation a checkpoint
    can carry. This regression test pins that behavior explicitly."""
    raw = '{"a": 1, "a": 2, "b": 3}'
    parsed = json.loads(raw)
    assert parsed == {"a": 2, "b": 3}  # last write wins; no ambiguity survives parsing


def test_unsupported_checkpoint_version_is_rejected(tmp_path):
    key = SigningKey.generate("version-key")
    checkpoint = build_checkpoint(
        key, chain_id=CHAIN_ID, environment=ENVIRONMENT, record_count=1,
        chain_head_hash="a" * 64, prev_checkpoint_hash=None, repo_sha="deadbeef",
    )
    tampered = dict(checkpoint)
    tampered["checkpoint_version"] = "99.0"
    # Signature no longer matches the mutated claims either, but the
    # SHAPE check must reject the unsupported version independent of that.
    assert verify_checkpoint_signature(tampered, key.public_key()) is False


def test_malformed_signature_is_rejected(tmp_path):
    key = SigningKey.generate("sig-key")
    checkpoint = build_checkpoint(
        key, chain_id=CHAIN_ID, environment=ENVIRONMENT, record_count=1,
        chain_head_hash="a" * 64, prev_checkpoint_hash=None, repo_sha="deadbeef",
    )
    tampered = dict(checkpoint)
    tampered["sig"] = "not-valid-base64-signature!!"
    assert verify_checkpoint_signature(tampered, key.public_key()) is False


def test_altered_payload_after_signing_is_rejected(tmp_path):
    key = SigningKey.generate("alter-key")
    checkpoint = build_checkpoint(
        key, chain_id=CHAIN_ID, environment=ENVIRONMENT, record_count=1,
        chain_head_hash="a" * 64, prev_checkpoint_hash=None, repo_sha="deadbeef",
    )
    for field, new_value in [
        ("record_count", 999), ("chain_head_hash", "b" * 64),
        ("chain_id", "different-chain"), ("environment", "production"),
        ("repo_sha", "cafebabe"), ("timestamp", "2099-01-01T00:00:00Z"),
    ]:
        tampered = dict(checkpoint)
        tampered[field] = new_value
        assert verify_checkpoint_signature(tampered, key.public_key()) is False, (
            f"altering {field!r} after signing must invalidate the signature"
        )


def test_signing_key_id_claim_must_match_envelope_kid(tmp_path):
    key = SigningKey.generate("mismatch-key")
    checkpoint = build_checkpoint(
        key, chain_id=CHAIN_ID, environment=ENVIRONMENT, record_count=1,
        chain_head_hash="a" * 64, prev_checkpoint_hash=None, repo_sha="deadbeef",
    )
    tampered = dict(checkpoint)
    tampered["signing_key_id"] = "some-other-kid"
    # Shape validation alone (independent of signature) must catch this.
    from mcc_checkpoint.schema import validate_checkpoint_shape
    with pytest.raises(ValueError, match="signing_key_id"):
        validate_checkpoint_shape(tampered)


def test_missing_required_field_is_rejected(tmp_path):
    key = SigningKey.generate("missing-field-key")
    checkpoint = build_checkpoint(
        key, chain_id=CHAIN_ID, environment=ENVIRONMENT, record_count=1,
        chain_head_hash="a" * 64, prev_checkpoint_hash=None, repo_sha="deadbeef",
    )
    for field in ("chain_id", "environment", "signing_key_id", "repo_sha", "timestamp"):
        incomplete = dict(checkpoint)
        del incomplete[field]
        from mcc_checkpoint.schema import validate_checkpoint_shape
        with pytest.raises(ValueError):
            validate_checkpoint_shape(incomplete)


def test_generator_rejects_empty_chain_id_or_environment(tmp_path):
    audit_path = str(tmp_path / "audit.jsonl")
    _seed_audit(audit_path, 3)
    key = SigningKey.generate("empty-fields-key")
    store = InMemoryAnchorStore()
    with pytest.raises(CheckpointGenerationError):
        CheckpointGenerator(
            audit_path=audit_path, signing_key=key, anchor_store=store,
            chain_id="", environment=ENVIRONMENT,
        )
    with pytest.raises(CheckpointGenerationError):
        CheckpointGenerator(
            audit_path=audit_path, signing_key=key, anchor_store=store,
            chain_id=CHAIN_ID, environment="",
        )
