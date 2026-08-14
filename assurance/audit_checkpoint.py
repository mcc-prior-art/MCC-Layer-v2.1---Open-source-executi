"""Signed External Audit Checkpoint (PR #71, Workstream G extension).

Closes a stated gap: this baseline's own evidence bundle is signed
(Workstream M), but nothing previously anchored the AUDIT CHAIN ITSELF to
an external, independent signer -- ``/verify`` recomputes and checks the
chain, but that recomputation runs in the SAME process/trust domain as the
Gateway being tested. A checkpoint here is signed by a SEPARATE key this
module owns (never the Gateway's own signing key), at a point in time this
module chooses -- so verifying a checkpoint later never depends on
trusting whatever the Gateway currently says about its own history.

Genuinely independent of ``mcc_core.audit.AuditLog``: the hash-chain
recomputation below is a SECOND implementation of the same algorithm
(matching ``AuditLog._entry_hash``/``verify_chain``), built here rather
than imported -- exactly the differential-testing posture Workstream D
already established for the canonical action format
(``assurance/canonical_action.py``). Reuses only ``mcc_core.signing``'s
pure hashing/signing primitives (not a security-decision module), the
same precedent ``canonical_action.py``/``evidence.py`` already set.

What this proves: a checkpoint signed at time T, over the chain's state at
that time, still verifies against the CURRENT chain later -- including
detecting when the checkpointed prefix was retroactively rewritten
(``verify_checkpoint`` fails) versus merely grown (``verify_checkpoint``
still passes; new entries appended after T are expected and fine).

What this does NOT prove (see ``docs/ASSUMPTIONS_AND_LIMITS.md``): this is
a self-contained-mode-only observation tool (it reads the audit log file
directly, the same class of operation ``corrupt_gateway_audit_chain``
already uses) -- it is not a production feature, does not run inside the
Gateway, and does not change ``mcc_core.audit``'s own runtime behavior in
any way. A genuinely external, always-on, third-party timestamping
service (e.g. RFC 3161) is a materially larger undertaking than this
baseline's scope covers; this closes the "no independent signer touches
the chain at all" gap, not the full production-grade external-anchoring
architecture a deployment might eventually want.
"""

from __future__ import annotations

import hashlib
import json
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

from mcc_core.signing import SigningKey, canonical_bytes, public_key_from_b64, verify_token

LEGACY_GENESIS_HASH = "genesis"


def generate_checkpoint_key(kid: str) -> SigningKey:
    """A fresh, throwaway checkpoint-signing key -- pure keygen, no SUT
    interaction at all. Exists so ``assurance/tests/`` modules never need
    ``mcc_core.signing`` directly (kept out of the allowed-import list by
    ``test_boundary_guards.py`` on purpose, mirroring ``forge_vote``/
    ``forge_mandate``'s identical rationale in ``assurance/sut/harness.py``)."""
    return SigningKey.generate(kid)


def read_audit_entries(path: str) -> List[Dict[str, Any]]:
    """Read raw JSONL entries from an audit log file. Direct filesystem
    access -- the same class of operation ``corrupt_gateway_audit_chain``
    already uses; self-contained mode only (see module docstring)."""
    entries: List[Dict[str, Any]] = []
    with open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                entries.append(json.loads(line))
    return entries


def _independent_entry_hash(prev_hash: str, body: Dict[str, Any]) -> str:
    """A SECOND, independent reimplementation of the audit chain's hash
    algorithm -- matches ``mcc_core.audit.AuditLog._entry_hash`` by
    construction (same inputs must produce the same chain), but is never
    imported from it, so a checkpoint's claim never trusts the same code
    path that wrote the chain to also verify it."""
    return hashlib.sha256(prev_hash.encode("utf-8") + canonical_bytes(body)).hexdigest()


def independent_chain_state(entries: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Independently recompute chain linkage/hashes over raw ``entries``
    (already read by the caller -- this function trusts no filesystem or
    network detail itself). Returns ``{"valid": bool, "entry_count": int,
    "head_hash": Optional[str]}``. ``head_hash`` is the last entry's
    declared hash IF every entry validated; ``None`` if the chain is
    empty or invalid at any point (a checkpoint can never be issued over
    an already-broken chain)."""
    prev: Optional[str] = None
    for entry in entries:
        declared = entry.get("hash")
        prev_hash = entry.get("prev_hash")
        if prev is not None and prev_hash != prev:
            return {"valid": False, "entry_count": len(entries), "head_hash": None}
        is_legacy_anchor = prev is None and declared == LEGACY_GENESIS_HASH
        if not is_legacy_anchor:
            body = {k: v for k, v in entry.items() if k != "hash"}
            if _independent_entry_hash(str(prev_hash), body) != declared:
                return {"valid": False, "entry_count": len(entries), "head_hash": None}
        prev = declared
    return {"valid": True, "entry_count": len(entries), "head_hash": prev}


def issue_checkpoint(checkpoint_key: SigningKey, *, entries: List[Dict[str, Any]],
                      deployment_id: str, checkpoint_id: Optional[str] = None,
                      issued_at: Optional[int] = None) -> Dict[str, Any]:
    """Sign a checkpoint claim over the independently-recomputed chain
    state, using ``checkpoint_key`` -- a key SEPARATE from the Gateway's
    own signing key, held only by this module. Raises ``ValueError`` if
    the chain is not currently valid (never checkpoint a chain already
    known to be broken)."""
    state = independent_chain_state(entries)
    if not state["valid"]:
        raise ValueError("cannot issue a checkpoint over an already-invalid chain")
    claims = {
        "checkpoint_id": checkpoint_id or f"ckpt-{uuid.uuid4().hex}",
        "deployment_id": deployment_id,
        "entry_count": state["entry_count"],
        "head_hash": state["head_hash"],
        "issued_at": int(issued_at if issued_at is not None else time.time()),
    }
    return checkpoint_key.sign_token(claims)


class CheckpointVerificationResult:
    def __init__(self, *, signature_valid: bool, signer_trusted: bool, chain_consistent: bool,
                 reason: str) -> None:
        self.signature_valid = signature_valid
        self.signer_trusted = signer_trusted
        self.chain_consistent = chain_consistent
        self.reason = reason

    @property
    def ok(self) -> bool:
        return self.signature_valid and self.signer_trusted and self.chain_consistent

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ok": self.ok, "signature_valid": self.signature_valid,
            "signer_trusted": self.signer_trusted, "chain_consistent": self.chain_consistent,
            "reason": self.reason,
        }


def verify_checkpoint(checkpoint: Dict[str, Any], *, trusted_public_key_b64: str,
                       current_entries: List[Dict[str, Any]]) -> CheckpointVerificationResult:
    """Verify a checkpoint two independent ways: (1) its signature, against
    a caller-supplied trusted public key (never a key read from the
    checkpoint or the chain itself); (2) the CURRENT chain
    (``current_entries``, read fresh by the caller) still has the
    checkpoint's claimed ``head_hash`` as an entry at position
    ``entry_count - 1`` -- proving the checkpointed prefix was never
    retroactively rewritten. A chain that has since GROWN (more entries
    appended after the checkpoint) still passes: only entries AT OR BEFORE
    the checkpointed position are required to match."""
    if not isinstance(checkpoint, dict) or "sig" not in checkpoint or "kid" not in checkpoint:
        return CheckpointVerificationResult(
            signature_valid=False, signer_trusted=False, chain_consistent=False,
            reason="MALFORMED_CHECKPOINT: missing signature/kid",
        )
    try:
        public_key = public_key_from_b64(trusted_public_key_b64)
    except Exception as exc:  # noqa: BLE001 -- fail closed on any decode error
        return CheckpointVerificationResult(
            signature_valid=False, signer_trusted=False, chain_consistent=False,
            reason=f"UNTRUSTED_KEY: could not decode trusted public key: {exc}",
        )
    signature_valid = bool(verify_token(checkpoint, public_key))
    if not signature_valid:
        return CheckpointVerificationResult(
            signature_valid=False, signer_trusted=False, chain_consistent=False,
            reason="INVALID_CHECKPOINT_SIGNATURE",
        )

    entry_count = checkpoint.get("entry_count")
    head_hash = checkpoint.get("head_hash")
    if not isinstance(entry_count, int) or entry_count <= 0 or not isinstance(head_hash, str):
        return CheckpointVerificationResult(
            signature_valid=True, signer_trusted=True, chain_consistent=False,
            reason="MALFORMED_CHECKPOINT: missing/invalid entry_count or head_hash",
        )
    if len(current_entries) < entry_count:
        return CheckpointVerificationResult(
            signature_valid=True, signer_trusted=True, chain_consistent=False,
            reason=f"CHAIN_SHORTER_THAN_CHECKPOINT: current chain has {len(current_entries)} "
                   f"entries, checkpoint claims {entry_count} existed",
        )

    prefix = current_entries[:entry_count]
    prefix_state = independent_chain_state(prefix)
    if not prefix_state["valid"]:
        return CheckpointVerificationResult(
            signature_valid=True, signer_trusted=True, chain_consistent=False,
            reason="CURRENT_CHAIN_PREFIX_INVALID: the entries up to the checkpointed "
                   "position no longer form a valid chain",
        )
    if prefix_state["head_hash"] != head_hash:
        return CheckpointVerificationResult(
            signature_valid=True, signer_trusted=True, chain_consistent=False,
            reason="CHECKPOINTED_PREFIX_REWRITTEN: the current chain's entry at the "
                   "checkpointed position no longer matches the checkpoint's signed hash "
                   "-- the chain was retroactively rewritten after the checkpoint was issued",
        )
    return CheckpointVerificationResult(
        signature_valid=True, signer_trusted=True, chain_consistent=True,
        reason="CHECKPOINT_VERIFIED",
    )
