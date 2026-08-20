"""External Checkpoint Anchoring for the MCC-Core audit hash-chain.

**Mitigating Scenario G -- Detectable Full-Chain Rewrite via External
Checkpoint Anchoring.** (Not "closing": a hash-chain with no reference
point outside the storage it protects cannot detect a "self-consistent
rewrite" -- an actor with full write access to audit storage alters a
non-tail record and recomputes every subsequent hash; the rewritten chain
still validates internally. This package gives the chain an external,
tamper-evident checkpoint anchor, so a full-storage-compromise rewrite of
anything at or before an anchored checkpoint becomes DETECTABLE via
``verify_anchors``.)

The precise, honest property this establishes: **a self-consistent
rewrite of the primary audit-chain storage becomes detectable as long as
the checkpoint signing authority and the external anchor store remain
outside attacker control.** It does not make full-chain rewriting
impossible, and it is not a cryptographically independent timestamp
(Git commit history is "externally persisted append-only checkpoint
history under separately configured repository protection", not an RFC
3161-grade timestamp authority -- see ``docs/AUDIT_CHECKPOINT_ANCHORING.md``
for the full scope statement, the two-layer validation evidence, and the
residual trust assumptions).

**Signing-key separation.** Checkpoints are signed by a dedicated Audit
Checkpoint signing key (``checkpoint_signing.py``) -- NEVER the Decision
Token signing key. ``Decision Token signing authority != Audit Checkpoint
signing authority``.

Observational and additive, downstream of the audit log -- mirrors the
``src/mcc_evidence`` architectural pattern (no gate/authority/nonce/
executor import; reuses ``mcc_core.signing`` for hashing/signing only).
Does not touch Decision Token schema, Execution Gate ALLOW/DENY/ESCALATE/
CONSTRAIN semantics, or nonce/replay protection.

Components:
  * ``schema``            -- the versioned checkpoint payload schema
                              (canonical, deterministic serialization).
  * ``checkpoint_signing`` -- the dedicated Audit Checkpoint Ed25519 key,
                              structurally distinct from the Decision
                              Token key.
  * ``checkpoint``        -- build/hash/sign one checkpoint.
  * ``generator``         -- N=500-record OR T=15-minute trigger
                              (configurable).
  * ``store``             -- ``AnchorStore``; ``GitBranchAnchorStore``
                              (Option A -- a configurable git remote,
                              recommended target
                              ``mcc-prior-art/mcc-audit-anchors``, a
                              SEPARATE repository from ``mcc-layer``) and
                              ``InMemoryAnchorStore`` (tests/dev only).
  * ``verifier``          -- ``verify_anchors``; raises
                              ``AuditAnchorMismatchError`` fail-closed on
                              any mismatch -- never a recoverable warning.
"""

from .checkpoint import build_checkpoint, checkpoint_hash, resolve_repo_sha, verify_checkpoint_signature
from .checkpoint_signing import (
    CHECKPOINT_KEY_PURPOSE,
    DEFAULT_CHECKPOINT_SIGNING_KEY_ID,
    CheckpointSigningKeyError,
    load_checkpoint_signing_key,
)
from .errors import (
    AnchorStoreError,
    AuditAnchorMismatchError,
    CheckpointAnchorError,
    CheckpointGenerationError,
)
from .generator import CheckpointGenerator, checkpoint_generator_from_env
from .schema import CHECKPOINT_SCHEMA_VERSION
from .store import AnchorStore, GitBranchAnchorStore, InMemoryAnchorStore, anchor_store_from_env
from .verifier import AnchorVerificationResult, verify_anchors, verify_checkpoint_chain_linkage

__all__ = [
    "AnchorStore",
    "AnchorStoreError",
    "AnchorVerificationResult",
    "AuditAnchorMismatchError",
    "CHECKPOINT_KEY_PURPOSE",
    "CHECKPOINT_SCHEMA_VERSION",
    "CheckpointAnchorError",
    "CheckpointGenerationError",
    "CheckpointGenerator",
    "CheckpointSigningKeyError",
    "DEFAULT_CHECKPOINT_SIGNING_KEY_ID",
    "GitBranchAnchorStore",
    "InMemoryAnchorStore",
    "anchor_store_from_env",
    "build_checkpoint",
    "checkpoint_generator_from_env",
    "checkpoint_hash",
    "load_checkpoint_signing_key",
    "resolve_repo_sha",
    "verify_anchors",
    "verify_checkpoint_chain_linkage",
    "verify_checkpoint_signature",
]
