"""Build, hash, and sign individual checkpoints.

Reuses ``mcc_core.signing.SigningKey.sign_token``/``verify_token`` as the
generic signed-envelope mechanism. ``signing_key`` here is the dedicated
Audit Checkpoint signing key (``checkpoint_signing.py``) -- a SEPARATE
Ed25519 identity from the Decision Token signing key. This module adds no
new cryptographic primitive; it only shapes the claims dict
``sign_token`` signs, and the signature covers a deterministic canonical
byte representation (``mcc_core.signing.canonical_bytes``), never
arbitrary/ambiguous serialization -- see ``schema.py`` for the full
canonicalization contract.
"""

from __future__ import annotations

import subprocess
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from mcc_core.signing import SigningKey, canonical_bytes, sha256_hex, verify_token

from .errors import CheckpointGenerationError
from .schema import CHECKPOINT_SCHEMA_VERSION, validate_checkpoint_shape


def checkpoint_hash(signed_checkpoint: Dict[str, Any]) -> str:
    """SHA-256 over the FULL signed checkpoint (claims + ``kid`` + ``sig``),
    canonically serialized. Hashing the signature too, not just the claims,
    means tampering with a past checkpoint's signature -- not only its
    claims -- also breaks the forward ``prev_checkpoint_hash`` link of
    every checkpoint issued after it."""
    return sha256_hex(canonical_bytes(signed_checkpoint))


def resolve_repo_sha(*, repo_root: Optional[str] = None, override: Optional[str] = None) -> str:
    """Resolve the current short SHA for the ``repo_sha`` cross-reference
    field. ``override`` (e.g. from ``MCC_CHECKPOINT_REPO_SHA``) always
    wins. Otherwise shells out to ``git rev-parse --short HEAD`` in
    ``repo_root`` (defaults to the current working directory). Fails
    closed -- raises ``CheckpointGenerationError`` rather than fabricating
    a placeholder SHA, consistent with "no new hashes/SHAs... until
    captured from real git show/test output"."""
    if override:
        return override
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=repo_root, capture_output=True, text=True, timeout=10, check=True,
        )
    except Exception as exc:  # noqa: BLE001 -- any git/subprocess failure fails closed
        raise CheckpointGenerationError(
            f"could not resolve repo_sha via git rev-parse: {exc}"
        ) from exc
    sha = result.stdout.strip()
    if not sha:
        raise CheckpointGenerationError("git rev-parse --short HEAD returned empty output")
    return sha


def build_checkpoint(
    signing_key: SigningKey,
    *,
    chain_id: str,
    environment: str,
    record_count: int,
    chain_head_hash: str,
    prev_checkpoint_hash: Optional[str],
    repo_sha: str,
    timestamp: Optional[str] = None,
) -> Dict[str, Any]:
    """Construct and sign one checkpoint. ``signing_key`` must be the
    dedicated Audit Checkpoint signing key (never the Decision Token
    key). Raises ``CheckpointGenerationError`` on any structurally
    invalid input -- never silently coerces."""
    if not chain_id:
        raise CheckpointGenerationError("chain_id must be non-empty")
    if not environment:
        raise CheckpointGenerationError("environment must be non-empty")
    if not isinstance(record_count, int) or record_count <= 0:
        raise CheckpointGenerationError(f"invalid record_count: {record_count!r}")
    if not chain_head_hash:
        raise CheckpointGenerationError("chain_head_hash must be non-empty")
    if not repo_sha:
        raise CheckpointGenerationError("repo_sha must be non-empty")

    claims: Dict[str, Any] = {
        "checkpoint_version": CHECKPOINT_SCHEMA_VERSION,
        "chain_id": chain_id,
        "environment": environment,
        "chain_head_hash": chain_head_hash,
        "record_count": record_count,
        "prev_checkpoint_hash": prev_checkpoint_hash,
        "timestamp": timestamp or datetime.now(timezone.utc).isoformat(),
        "signing_key_id": signing_key.kid,
        "repo_sha": repo_sha,
    }
    signed = signing_key.sign_token(claims)
    validate_checkpoint_shape(signed)
    return signed


def verify_checkpoint_signature(checkpoint: Dict[str, Any], public_key: Any) -> bool:
    """Fail-closed signature check only (never chain consistency -- see
    ``verifier.py``). Delegates entirely to
    ``mcc_core.signing.verify_token``, which itself catches every
    exception and returns ``False``."""
    try:
        validate_checkpoint_shape(checkpoint)
    except ValueError:
        return False
    return bool(verify_token(checkpoint, public_key))
