"""Verification: recompute live audit-chain segments and confirm they
still match what was externally anchored. Fail-closed throughout --
``verify_anchors`` always raises ``AuditAnchorMismatchError`` on any
inconsistency; it never downgrades a mismatch to a warning-only return
value (see ``errors.py``).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from . import audit_reader
from .checkpoint import checkpoint_hash, verify_checkpoint_signature
from .errors import AuditAnchorMismatchError
from .schema import validate_checkpoint_shape
from .store import AnchorStore


@dataclass(frozen=True)
class AnchorVerificationResult:
    ok: bool
    checkpoints_verified: int
    last_verified_record_count: Optional[int]
    last_verified_head_hash: Optional[str]
    reason: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ok": self.ok,
            "checkpoints_verified": self.checkpoints_verified,
            "last_verified_record_count": self.last_verified_record_count,
            "last_verified_head_hash": self.last_verified_head_hash,
            "reason": self.reason,
        }


def verify_checkpoint_chain_linkage(checkpoints: List[Dict[str, Any]]) -> None:
    """Verify the checkpoints' OWN hash-linked chain (``prev_checkpoint_hash``)
    is internally consistent, independent of the live audit log. Raises
    ``AuditAnchorMismatchError`` on the first break: a checkpoint whose
    ``prev_checkpoint_hash`` does not equal ``checkpoint_hash`` of the
    checkpoint immediately before it (genesis must have
    ``prev_checkpoint_hash is None``). This is what detects tampering of a
    non-tail *checkpoint* itself (as distinct from tampering of the audit
    log the checkpoints describe)."""
    prev_signed: Optional[Dict[str, Any]] = None
    for index, checkpoint in enumerate(checkpoints):
        try:
            validate_checkpoint_shape(checkpoint)
        except ValueError as exc:
            raise AuditAnchorMismatchError(
                f"anchored checkpoint at position {index} is malformed: {exc}"
            ) from exc
        expected_prev = checkpoint_hash(prev_signed) if prev_signed is not None else None
        if checkpoint["prev_checkpoint_hash"] != expected_prev:
            raise AuditAnchorMismatchError(
                f"checkpoint chain broken at position {index} "
                f"(record_count={checkpoint.get('record_count')}): "
                f"prev_checkpoint_hash={checkpoint['prev_checkpoint_hash']!r} does not "
                f"match the hash of the checkpoint anchored immediately before it "
                f"({expected_prev!r}) -- the checkpoint chain itself was tampered with"
            )
        prev_signed = checkpoint


def verify_anchors(
    *, audit_path: str, anchor_store: AnchorStore, trusted_public_key: Any,
) -> AnchorVerificationResult:
    """Walk the full checkpoint chain and confirm every anchored segment
    still matches the live audit log. Fail-closed: any signature failure,
    checkpoint-chain break, or live-chain mismatch raises
    ``AuditAnchorMismatchError`` -- this function never returns an "ok"
    result alongside an unresolved failure.

    An anchor store with zero checkpoints is not a failure (a fresh
    deployment, or one still short of its first N/T trigger) -- returns
    ``ok=True`` with ``checkpoints_verified=0``.
    """
    checkpoints = anchor_store.read_all_checkpoints()
    if not checkpoints:
        return AnchorVerificationResult(
            ok=True, checkpoints_verified=0, last_verified_record_count=None,
            last_verified_head_hash=None, reason="NO_ANCHORED_CHECKPOINTS",
        )

    verify_checkpoint_chain_linkage(checkpoints)

    for index, checkpoint in enumerate(checkpoints):
        if not verify_checkpoint_signature(checkpoint, trusted_public_key):
            raise AuditAnchorMismatchError(
                f"anchored checkpoint at position {index} "
                f"(record_count={checkpoint.get('record_count')}) failed Ed25519 "
                f"signature verification against the trusted key"
            )

    # Read the live chain once, fresh, then check every anchored checkpoint's
    # claimed prefix against it.
    entries = audit_reader.read_entries(audit_path)
    for index, checkpoint in enumerate(checkpoints):
        record_count = checkpoint["record_count"]
        valid, head_hash = audit_reader.chain_state_for_prefix(entries, record_count)
        if not valid:
            raise AuditAnchorMismatchError(
                f"AUDIT_ANCHOR_MISMATCH: live audit log at position {index} "
                f"(checkpoint record_count={record_count}) no longer forms a "
                f"valid hash-linked prefix -- possible storage rewrite. This is "
                f"exactly the Scenario G self-consistent-rewrite class: the live "
                f"chain segment can no longer reproduce a checkpoint signed and "
                f"externally anchored at an earlier point in time."
            )
        if head_hash != checkpoint["chain_head_hash"]:
            raise AuditAnchorMismatchError(
                f"AUDIT_ANCHOR_MISMATCH: live audit log's entry at position "
                f"{record_count - 1} has hash {head_hash!r}, but the checkpoint "
                f"anchored at that position signed chain_head_hash="
                f"{checkpoint['chain_head_hash']!r} -- the audit record at or "
                f"before this position was retroactively rewritten after the "
                f"checkpoint was externally anchored."
            )

    last = checkpoints[-1]
    return AnchorVerificationResult(
        ok=True, checkpoints_verified=len(checkpoints),
        last_verified_record_count=last["record_count"],
        last_verified_head_hash=last["chain_head_hash"],
        reason="ALL_ANCHORED_CHECKPOINTS_VERIFIED",
    )
