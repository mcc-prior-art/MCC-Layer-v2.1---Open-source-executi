"""Transport-neutral canonical models — MCC Universal Proposal Service (Phase 1).

These are pure data: constructing or validating one of these objects never
authorizes, signs, or executes anything. They are the ONE wire-shape every
adapter (Generic HTTP, MCP, LangGraph, CrewAI, AutoGen, VoltAgent, the native
SDKs, and any future transport) converges on before reaching
``mcc_proposal.service.MCCProposalService``.

    PROPOSAL != PERMISSION.
    TRANSPORT != AUTHORITY.

Nothing in this module imports a framework, a transport library, or any MCC
authority/execution primitive (gate, coordinator, signing key, actuator).
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional

CONTRACT_VERSION = "v1"

#: The exact allow-list of top-level fields a caller may supply on a proposal
#: submission. Anything else is rejected outright (never silently dropped,
#: never silently honored) -- this is what keeps a transport from ever
#: manufacturing authority by smuggling in an authority-bearing field.
ALLOWED_REQUEST_FIELDS = frozenset({
    "logical_operation_id", "actor", "action", "resource", "payload",
})

#: Fields that would let a caller manufacture authority if honored. Listed
#: explicitly (rather than relying solely on the allow-list above) so a
#: rejection can name exactly what was refused and why -- this is not the
#: enforcement mechanism itself (the allow-list is), it is why the allow-list
#: is drawn where it is drawn.
AUTHORITY_BEARING_FIELDS = frozenset({
    "decision_token", "signed_authority", "mandate", "approval_mandate",
    "private_key", "signing_key", "trusted_issuer", "policy_override",
    "policy_hash_override", "nonce_override", "generation", "fence",
    "dispatch_owner", "resolve_unknown", "mark_executed", "actuator",
    "executor", "execute", "force", "retry_anyway",
})

# Remote-ingress bounds (Section 21). Deliberately generous but finite: these
# exist to give a deterministic, fail-closed rejection to a pathological
# caller, not to constrain any legitimate domain payload.
MAX_ID_LENGTH = 512
MAX_ACTOR_LENGTH = 512
MAX_ACTION_LENGTH = 512
MAX_RESOURCE_LENGTH = 1024
MAX_PAYLOAD_BYTES = 262_144  # 256 KiB serialized
MAX_JSON_DEPTH = 32


class ProposalValidationError(ValueError):
    """A submitted proposal is structurally invalid or attempted to smuggle in
    an authority-bearing field -- fail closed, never silently repaired."""

    def __init__(self, code: str, reason: str) -> None:
        self.code = code
        self.reason = reason
        super().__init__(f"{code}: {reason}")


def _json_depth(value: Any, _depth: int = 0) -> int:
    if _depth > MAX_JSON_DEPTH:
        return _depth
    if isinstance(value, dict):
        if not value:
            return _depth + 1
        return max(_json_depth(v, _depth + 1) for v in value.values())
    if isinstance(value, list):
        if not value:
            return _depth + 1
        return max(_json_depth(v, _depth + 1) for v in value)
    return _depth + 1


def _require_nonempty_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ProposalValidationError(
            "INVALID_FIELD", f"{field_name!r} must be a non-empty string"
        )
    return value


@dataclass(frozen=True)
class ProposalRequestV1:
    """The one canonical governance-agnostic proposal request.

    ``logical_operation_id`` is mandatory, caller-supplied, and never
    generated, inferred, or substituted by this layer (see
    ``docs/DURABLE_OPERATION_SAFETY.md`` and Rounds 25-27) -- it is the exact
    same identity the coordinator will later require as ``idempotency_key``
    if this operation is ever proposed for real execution.
    """

    logical_operation_id: str
    actor: str
    action: str
    resource: Optional[str]
    payload: Dict[str, Any]

    @classmethod
    def from_dict(cls, data: Any) -> "ProposalRequestV1":
        if not isinstance(data, dict):
            raise ProposalValidationError("INVALID_REQUEST", "request body must be a JSON object")

        unknown = set(data.keys()) - ALLOWED_REQUEST_FIELDS
        if unknown:
            authority_bearing = sorted(unknown & AUTHORITY_BEARING_FIELDS)
            if authority_bearing:
                raise ProposalValidationError(
                    "AUTHORITY_FIELD_REJECTED",
                    f"field(s) {authority_bearing} cannot be supplied by a caller; "
                    "a proposal transport never carries authority",
                )
            raise ProposalValidationError(
                "UNKNOWN_FIELD", f"unrecognized field(s): {sorted(unknown)}"
            )

        logical_operation_id = data.get("logical_operation_id")
        if not isinstance(logical_operation_id, str) or not logical_operation_id.strip():
            raise ProposalValidationError(
                "MISSING_LOGICAL_OPERATION_ID",
                "logical_operation_id is required, must be a non-empty, non-whitespace "
                "string, explicitly supplied by the caller; it is never generated, "
                "inferred from payload, or substituted from any other identifier",
            )
        if len(logical_operation_id) > MAX_ID_LENGTH:
            raise ProposalValidationError(
                "FIELD_TOO_LONG", f"logical_operation_id exceeds {MAX_ID_LENGTH} characters"
            )

        actor = _require_nonempty_string(data.get("actor"), "actor")
        if len(actor) > MAX_ACTOR_LENGTH:
            raise ProposalValidationError("FIELD_TOO_LONG", f"actor exceeds {MAX_ACTOR_LENGTH} characters")

        action = _require_nonempty_string(data.get("action"), "action")
        if len(action) > MAX_ACTION_LENGTH:
            raise ProposalValidationError("FIELD_TOO_LONG", f"action exceeds {MAX_ACTION_LENGTH} characters")

        resource = data.get("resource")
        if resource is not None:
            if not isinstance(resource, str) or not resource.strip():
                raise ProposalValidationError("INVALID_FIELD", "resource must be a non-empty string or null")
            if len(resource) > MAX_RESOURCE_LENGTH:
                raise ProposalValidationError(
                    "FIELD_TOO_LONG", f"resource exceeds {MAX_RESOURCE_LENGTH} characters"
                )

        payload = data.get("payload", {})
        if not isinstance(payload, dict):
            raise ProposalValidationError("INVALID_FIELD", "payload must be a JSON object")
        if _json_depth(payload) > MAX_JSON_DEPTH:
            raise ProposalValidationError("PAYLOAD_TOO_DEEP", f"payload nesting exceeds {MAX_JSON_DEPTH}")

        from mcc_core.signing import canonical_bytes

        try:
            size = len(canonical_bytes(payload))
        except (TypeError, ValueError) as exc:
            raise ProposalValidationError(
                "PAYLOAD_NOT_SERIALIZABLE", f"payload must be JSON-serializable: {exc}"
            ) from exc
        if size > MAX_PAYLOAD_BYTES:
            raise ProposalValidationError("PAYLOAD_TOO_LARGE", f"payload exceeds {MAX_PAYLOAD_BYTES} bytes")

        return cls(
            logical_operation_id=logical_operation_id,
            actor=actor,
            action=action,
            resource=resource,
            payload=dict(payload),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "logical_operation_id": self.logical_operation_id,
            "actor": self.actor,
            "action": self.action,
            "resource": self.resource,
            "payload": dict(self.payload),
        }


class ProposalStatus(str, Enum):
    """The stable external status vocabulary for a submission receipt.
    Distinct from ``OperationStatusValue`` below -- a receipt describes the
    *submission* outcome, not the operation's durable execution lifecycle."""

    PROPOSED = "PROPOSED"
    BINDING_CONFLICT = "BINDING_CONFLICT"
    REJECTED = "REJECTED"
    UNAVAILABLE = "UNAVAILABLE"


@dataclass(frozen=True)
class ProposalReceiptV1:
    contract_version: str
    accepted: bool
    logical_operation_id: str
    status: str
    proposal_binding: Optional[str] = None
    reason: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        out: Dict[str, Any] = {
            "contract_version": self.contract_version,
            "accepted": self.accepted,
            "logical_operation_id": self.logical_operation_id,
            "status": self.status,
        }
        if self.proposal_binding is not None:
            out["proposal_binding"] = self.proposal_binding
        if self.reason is not None:
            out["reason"] = self.reason
        return out

    @classmethod
    def proposed(cls, *, logical_operation_id: str, proposal_binding: str) -> "ProposalReceiptV1":
        return cls(
            contract_version=CONTRACT_VERSION, accepted=True,
            logical_operation_id=logical_operation_id, status=ProposalStatus.PROPOSED.value,
            proposal_binding=proposal_binding,
        )

    @classmethod
    def conflict(cls, *, logical_operation_id: str) -> "ProposalReceiptV1":
        return cls(
            contract_version=CONTRACT_VERSION, accepted=False,
            logical_operation_id=logical_operation_id, status=ProposalStatus.BINDING_CONFLICT.value,
            reason="logical_operation_id is already bound to a different action/resource/payload",
        )

    @classmethod
    def rejected(cls, *, logical_operation_id: str, reason: str) -> "ProposalReceiptV1":
        return cls(
            contract_version=CONTRACT_VERSION, accepted=False,
            logical_operation_id=logical_operation_id, status=ProposalStatus.REJECTED.value,
            reason=reason,
        )

    @classmethod
    def unavailable(cls, *, logical_operation_id: str, reason: str) -> "ProposalReceiptV1":
        return cls(
            contract_version=CONTRACT_VERSION, accepted=False,
            logical_operation_id=logical_operation_id, status=ProposalStatus.UNAVAILABLE.value,
            reason=reason,
        )


class OperationStatusValue(str, Enum):
    """The stable external operation-status vocabulary. Every adapter exposes
    exactly these names -- never a per-adapter renaming of the same concept."""

    PROPOSED = "PROPOSED"
    RESERVED = "RESERVED"
    DISPATCH_OWNED = "DISPATCH_OWNED"
    UNKNOWN = "UNKNOWN"
    EXECUTED = "EXECUTED"
    NOT_FOUND = "NOT_FOUND"
    UNAVAILABLE = "UNAVAILABLE"


@dataclass(frozen=True)
class OperationStatusV1:
    contract_version: str
    logical_operation_id: str
    status: str
    proposal_binding: Optional[str] = None
    detail: str = ""

    def to_dict(self) -> Dict[str, Any]:
        out: Dict[str, Any] = {
            "contract_version": self.contract_version,
            "logical_operation_id": self.logical_operation_id,
            "status": self.status,
        }
        if self.proposal_binding is not None:
            out["proposal_binding"] = self.proposal_binding
        if self.detail:
            out["detail"] = self.detail
        return out

    @classmethod
    def of(cls, *, logical_operation_id: str, status: OperationStatusValue,
           proposal_binding: Optional[str] = None, detail: str = "") -> "OperationStatusV1":
        return cls(
            contract_version=CONTRACT_VERSION, logical_operation_id=logical_operation_id,
            status=status.value, proposal_binding=proposal_binding, detail=detail,
        )


__all__ = [
    "CONTRACT_VERSION",
    "ALLOWED_REQUEST_FIELDS",
    "AUTHORITY_BEARING_FIELDS",
    "ProposalValidationError",
    "ProposalRequestV1",
    "ProposalStatus",
    "ProposalReceiptV1",
    "OperationStatusValue",
    "OperationStatusV1",
]
