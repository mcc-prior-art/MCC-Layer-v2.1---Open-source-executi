"""Checkpoint payload schema -- versioned, deterministic, minimal.

A checkpoint is a small, signed claim about the audit chain's state at one
point in time: how many records existed, what the chain head hash was, and
what the previous checkpoint's hash was (forming the checkpoints' own
hash-linked chain, independent of the audit log's).

**Signing-key separation (required property).** Checkpoints are signed by
a dedicated Audit Checkpoint signing key -- NEVER the Decision Token
signing key (see ``checkpoint_signing.py``). Both reuse the same Ed25519
primitive and envelope (``mcc_core.signing.SigningKey.sign_token``/
``verify_token`` -- no new cryptographic primitive is introduced), but
they are different key material with different ``kid`` namespaces and
different trust domains: ``Decision Token signing authority !=
Audit Checkpoint signing authority``. Compromise of the Decision Token
issuer alone must not be sufficient to forge audit-anchor history.

**Canonical serialization (required property).** The signature covers
``mcc_core.signing.canonical_bytes`` -- deterministic JSON
(``sort_keys=True, separators=(",", ":"), ensure_ascii=True``) -- of the
claims dict, never an arbitrary/attacker-supplied byte string.
Verification (``checkpoint.py::verify_checkpoint_signature``,
``verifier.py``) always RECOMPUTES this canonical form from the parsed
Python object it receives and checks the signature against that
recomputation; it never trusts a byte representation carried alongside
the object. Because Python's ``json.loads`` collapses duplicate keys to
the last occurrence before any code here ever sees the object, "duplicate
JSON field" ambiguity cannot reach the signed claims at all -- there is
exactly one canonical encoding for any given claims dict, by construction
(see ``tests/test_checkpoint_anchoring.py`` canonicalization regression
coverage).

Naming note (deliberate): this package uses "checkpoint" as its primary
vocabulary and confines the word "anchor" to the external-storage concept
the task spec itself names ("external anchor", ``AnchorStore``,
``AuditAnchorMismatchError``). This is a different concept from
``mcc_evidence``'s ``AUDIT_ANCHOR_PATH`` (a per-bundle audit-slice starting
``prev_hash``, unrelated) and from ``mcc_evidence.tc001_certificate``'s
``TrustAnchor``/``TrustAnchorRegistry`` (trusted signer public keys, also
unrelated). All three live in separate modules with no shared code path;
the overlap is in English, not in the type system.
"""

from __future__ import annotations

from typing import Any, Dict, FrozenSet

CHECKPOINT_SCHEMA_VERSION = "1.0"
SUPPORTED_CHECKPOINT_SCHEMA_VERSIONS: FrozenSet[str] = frozenset({CHECKPOINT_SCHEMA_VERSION})

#: The exact claim fields signed inside every checkpoint (before
#: ``SigningKey.sign_token`` adds ``kid``/``sig``). Order here is
#: documentation only -- canonical serialization (below) governs the
#: actual signed/hashed byte representation; verification recomputes it
#: from the received object rather than trusting field order on the wire.
#:
#: ``chain_id`` identifies which audit-chain instance/deployment a
#: checkpoint describes (prevents a checkpoint anchored for one
#: deployment's chain from being replayed as if it verified a different
#: deployment's chain). ``environment`` labels the deployment tier (e.g.
#: "production", "pilot", "staging") -- informational, not a trust
#: boundary by itself. ``signing_key_id`` records the Audit Checkpoint
#: signing key's ``kid`` INSIDE the signed claims, redundantly with the
#: envelope's own ``kid`` field added by ``sign_token`` -- verification
#: checks both agree (see ``verifier.py``), so a token cannot be replayed
#: under a different ``kid`` without also being caught by canonical-byte
#: signature verification. ``repo_sha`` is build-provenance metadata for
#: cross-reference only -- it is signed (so it cannot be forged
#: independently of a valid signature) but it is NOT itself a root of
#: trust: nothing here treats "the repo_sha looks plausible" as evidence
#: of anything on its own.
CHECKPOINT_CLAIM_FIELDS = (
    "checkpoint_version",
    "chain_id",
    "environment",
    "chain_head_hash",
    "record_count",
    "prev_checkpoint_hash",
    "timestamp",
    "signing_key_id",
    "repo_sha",
)

#: Fields added by the Ed25519 signing envelope itself
#: (``mcc_core.signing.SigningKey.sign_token``).
CHECKPOINT_SIGNATURE_FIELDS = ("kid", "sig")


def is_supported_schema_version(version: Any) -> bool:
    return isinstance(version, str) and version in SUPPORTED_CHECKPOINT_SCHEMA_VERSIONS


def validate_checkpoint_shape(checkpoint: Dict[str, Any]) -> None:
    """Structural validation only (field presence/type) -- never signature
    or chain-consistency checks, which belong to ``verifier.py``. Raises
    ``ValueError`` on any structural defect."""
    if not isinstance(checkpoint, dict):
        raise ValueError("checkpoint must be a dict")
    for field in CHECKPOINT_CLAIM_FIELDS + CHECKPOINT_SIGNATURE_FIELDS:
        if field not in checkpoint:
            raise ValueError(f"checkpoint missing required field: {field!r}")
    if not is_supported_schema_version(checkpoint["checkpoint_version"]):
        raise ValueError(
            f"unsupported checkpoint_version: {checkpoint['checkpoint_version']!r}"
        )
    if not isinstance(checkpoint["chain_id"], str) or not checkpoint["chain_id"]:
        raise ValueError("chain_id must be a non-empty string")
    if not isinstance(checkpoint["environment"], str) or not checkpoint["environment"]:
        raise ValueError("environment must be a non-empty string")
    if not isinstance(checkpoint["chain_head_hash"], str) or not checkpoint["chain_head_hash"]:
        raise ValueError("chain_head_hash must be a non-empty string")
    if not isinstance(checkpoint["record_count"], int) or checkpoint["record_count"] <= 0:
        raise ValueError("record_count must be a positive int")
    prev = checkpoint["prev_checkpoint_hash"]
    if prev is not None and (not isinstance(prev, str) or not prev):
        raise ValueError("prev_checkpoint_hash must be null or a non-empty string")
    if not isinstance(checkpoint["timestamp"], str) or not checkpoint["timestamp"]:
        raise ValueError("timestamp must be a non-empty ISO 8601 string")
    if not isinstance(checkpoint["signing_key_id"], str) or not checkpoint["signing_key_id"]:
        raise ValueError("signing_key_id must be a non-empty string")
    if checkpoint["signing_key_id"] != checkpoint.get("kid"):
        raise ValueError(
            "signing_key_id (signed claim) does not match kid (envelope field) -- "
            "these must always agree"
        )
    if not isinstance(checkpoint["repo_sha"], str) or not checkpoint["repo_sha"]:
        raise ValueError("repo_sha must be a non-empty string")
