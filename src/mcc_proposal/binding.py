"""Exact proposal binding — the single canonicalization every transport shares.

Reuses the SAME primitives protected execution uses (Section 5): the action's
``ProfileRegistry`` canonical payload and the platform's one hashing
implementation (``mcc_core.signing``). No MCP-specific, HTTP-specific,
framework-specific, or TypeScript-only alternate serialization exists
anywhere in this module -- the identical semantic operation, presented
through any adapter, produces the identical ``proposal_binding``.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from mcc_core.profiles import ProfileError, ProfileRegistry
from mcc_core.signing import hash_document, hash_payload


class BindingComputationError(Exception):
    """Raised when the action's profile rejects the payload shape (e.g. a
    payment proposal missing a required field). Fail-closed: the caller must
    treat this as REJECTED, never as an accepted proposal with a fabricated
    binding."""


def compute_proposal_binding(
    *, action: str, resource: Optional[str], payload: Dict[str, Any],
    profiles: ProfileRegistry,
) -> str:
    """``proposal_binding = hash_document({action, resource, payload_hash})``
    where ``payload_hash = hash_payload(profile.canonical_payload(payload))``.

    Same logical_operation_id + identical binding -> idempotent duplicate.
    Any change to action, resource, or canonical payload changes the binding
    -> BINDING_CONFLICT for a reused logical_operation_id.
    """
    try:
        profile = profiles.for_action(action)
        canonical_payload = profile.canonical_payload(dict(payload))
    except ProfileError as exc:
        raise BindingComputationError(f"PROFILE_ERROR: {exc}") from exc
    payload_hash = hash_payload(canonical_payload)
    return hash_document({"action": action, "resource": resource, "payload_hash": payload_hash})


__all__ = ["BindingComputationError", "compute_proposal_binding"]
