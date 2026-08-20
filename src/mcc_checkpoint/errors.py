"""Exception types for external checkpoint anchoring.

All failure modes here are fail-closed by convention: nothing in this
package ever downgrades a verification failure to a warning. A caller that
wires ``verify_anchors`` into a startup/readiness path (see
``docs/AUDIT_CHECKPOINT_ANCHORING.md``) can rely on catching
``CheckpointAnchorError`` (or letting it propagate) to refuse readiness --
the same fail-closed discipline ``mcc_core.audit.AuditLockError`` /
``AuditCorruptionError`` already establish for the audit log itself.
"""

from __future__ import annotations


class CheckpointAnchorError(Exception):
    """Base class for every error this package raises."""


class CheckpointGenerationError(CheckpointAnchorError):
    """Raised when a checkpoint cannot be honestly generated -- e.g. the
    live audit chain is empty or already fails independent verification.
    A checkpoint must never be issued over a chain this package cannot
    itself confirm is currently valid."""


class AnchorStoreError(CheckpointAnchorError):
    """Raised when the external anchor store cannot durably record or
    retrieve a checkpoint (git command failure, unreachable remote,
    misconfiguration). Fail-closed: a caller must treat this the same as
    a verification failure, never as "anchoring is best-effort, continue
    anyway"."""


class AuditAnchorMismatchError(CheckpointAnchorError):
    """Raised by ``verify_anchors`` when a live audit-chain segment no
    longer matches what an externally anchored checkpoint signed for it.

    This is the detection signal for Scenario G (a self-consistent,
    full-storage rewrite of a non-tail audit record): the rewritten
    in-storage chain still validates *internally*, but it can no longer
    reproduce the ``chain_head_hash`` an earlier checkpoint committed to
    an external, independently-timestamped anchor store. Always
    fail-closed -- never caught and reduced to a log line by this
    package itself.
    """
