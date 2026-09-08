"""Tenant-scoped reconciliation marker for the Phase 2 live sandbox proof.

Reuses ``examples.gpt6_astra_reference.issue_contract``'s marker MACHINERY
(reserved delimiters, safety validation, single-occurrence extraction
regex, the payload-preparation helper) completely unchanged -- this module
only chooses WHAT identifier gets embedded in it, never a second marker
format (Section 10: "reuse existing marker logic if possible").

Phase 1's ``github_actuator`` reference demo is single-tenant, so a bare
``logical_operation_id`` is a sufficient marker there. Phase 2's durable
identity is the PAIR ``(tenant_id, logical_operation_id)`` -- a bare
``logical_operation_id`` marker would be ambiguous between two tenants
that happen to use the identical id (an adversarial scenario this
repository's own Phase 2 test suite specifically proves independent), so
this module embeds a composite ``"tenant_id::logical_operation_id"``
identity into the SAME reserved marker syntax instead.

    MARKER != AUTHORITY.

Extracting a matching marker from an external issue proves only that the
issue's body carries this exact text -- it never establishes trust,
signature validity, or execution authority by itself. The real Gate/
coordinator/idempotency registry remain the sole source of authority and
durable state; this marker exists solely so reconciliation
(``gateway.proposal_execution_service.reconcile_proposal_operation``) can
locate a *candidate* to independently verify.
"""

from __future__ import annotations

from typing import Any, Dict, Tuple

from examples.gpt6_astra_reference.issue_contract import (
    MarkerSyntaxError,
    build_marked_payload,
    extract_single_marker_operation_id,
    logical_operation_marker,
    validate_github_issue_request_payload,
)

#: Reserved separator joining tenant_id and logical_operation_id inside the
#: single marker identity slot. Neither component may contain it.
_COMPOSITE_SEPARATOR = "::"


class TenantOperationMarkerError(Exception):
    """Raised when a tenant_id/logical_operation_id pair cannot safely form
    a composite marker identity -- fail-closed, never silently truncated
    or reinterpreted."""


def composite_identity(tenant_id: str, logical_operation_id: str) -> str:
    if not isinstance(tenant_id, str) or not tenant_id.strip():
        raise TenantOperationMarkerError("tenant_id must be a non-empty string")
    if not isinstance(logical_operation_id, str) or not logical_operation_id.strip():
        raise TenantOperationMarkerError("logical_operation_id must be a non-empty string")
    if _COMPOSITE_SEPARATOR in tenant_id or _COMPOSITE_SEPARATOR in logical_operation_id:
        raise TenantOperationMarkerError(
            f"tenant_id/logical_operation_id must not themselves contain the reserved "
            f"composite separator {_COMPOSITE_SEPARATOR!r}"
        )
    return f"{tenant_id}{_COMPOSITE_SEPARATOR}{logical_operation_id}"


def composite_marker(tenant_id: str, logical_operation_id: str) -> str:
    """The exact marker text embedded in a sandbox issue body -- reuses
    ``logical_operation_marker`` (delimiters + safety validation)
    unchanged, over the composite tenant+operation identity."""
    return logical_operation_marker(composite_identity(tenant_id, logical_operation_id))


def extract_composite_marker_identity(body: str) -> Tuple[str, str]:
    """Returns ``(tenant_id, logical_operation_id)`` from the SINGLE
    well-formed composite marker ``body`` carries. Fail-closed identically
    to ``extract_single_marker_operation_id`` (no marker, more than one, or
    malformed -> ``MarkerSyntaxError``), plus a further fail-closed check
    that the extracted identity is a well-formed two-part composite."""
    identity = extract_single_marker_operation_id(body)
    parts = identity.split(_COMPOSITE_SEPARATOR)
    if len(parts) != 2 or not parts[0] or not parts[1]:
        raise MarkerSyntaxError(
            f"marker identity {identity!r} is not a well-formed "
            f"tenant_id{_COMPOSITE_SEPARATOR}logical_operation_id composite"
        )
    return parts[0], parts[1]


def prepare_sandbox_issue_payload(
    payload: Dict[str, Any], *, tenant_id: str, logical_operation_id: str,
) -> Dict[str, Any]:
    """The complete outbound-payload preparation step for the sandbox
    proof's ``create_github_issue`` action: validate the strict request
    schema FIRST (reused unchanged from ``issue_contract``), THEN embed the
    tenant-scoped composite marker (reusing ``build_marked_payload``
    unchanged, over the composite identity). Both happen BEFORE
    canonicalization, proposal binding, or authorization -- this is the
    FINAL outbound payload from this point forward; nothing downstream may
    add, remove, normalize, or replace a field (Section 4)."""
    validated = validate_github_issue_request_payload(payload)
    identity = composite_identity(tenant_id, logical_operation_id)
    return build_marked_payload(validated, logical_operation_id=identity)


__all__ = [
    "TenantOperationMarkerError",
    "composite_identity",
    "composite_marker",
    "extract_composite_marker_identity",
    "prepare_sandbox_issue_payload",
]
