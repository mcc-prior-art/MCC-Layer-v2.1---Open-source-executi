"""CanonicalProposal — the normative framework-neutral governance *request*.

Reconciled with PR #43
----------------------
The Integration Contract (PR #43) reuses the SDK's shipped models and defines no
parallel wire models. It already provides the canonical *response* side
(:class:`mcc_client.Decision` / :class:`mcc_client.Verdict`) but had **no**
first-class *request* type — adapters built ad-hoc proposals (e.g. the interop
harness's lightweight test proposal). ``CanonicalProposal`` fills exactly that gap:
it is an **additive promotion** of that proven proposal shape into one normative,
installable request object. It is not a competing hierarchy — its version is the
contract version, its failures classify into the contract error taxonomy, and its
verdict/decision counterpart is the existing :class:`mcc_client.Decision` (wrapped,
not replaced, by :class:`mcc_protocol.GovernanceDecision`).

What it is / is not
-------------------
* Pure data + deterministic hashing. Building or validating a proposal **never**
  authorizes anything (schema validity is not authorization).
* ``action_hash`` is a proposal-integrity / trace hash computed with the *same*
  canonicalization the rest of the platform uses (:mod:`mcc_core.signing`), so
  there is one hashing implementation. It is **not** the Gate's authoritative
  binding — the Gate recomputes and verifies its own bindings and its result cannot
  be overridden by anything in the proposal.
* Fails closed: missing/invalid required fields raise
  :class:`ProposalValidationError`; the pipeline maps that to a blocking contract
  error code.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

from mcc_core.signing import canonical_bytes, sha256_hex

from .version import PROTOCOL_VERSION


class ProposalValidationError(ValueError):
    """A canonical proposal is structurally invalid (fail-closed). Carries a short
    machine-usable ``field`` hint; the pipeline maps it to a blocking contract
    code."""

    def __init__(self, reason: str, *, field: str = "") -> None:
        self.reason = reason
        self.field = field
        super().__init__(reason)


def _utcnow_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def compute_action_hash(action: str, resource: str, actor: str,
                        payload: Dict[str, Any]) -> str:
    """Deterministic proposal-integrity hash over the action binding, using the
    platform's single canonicalization. Not the Gate's authoritative binding."""
    return sha256_hex(canonical_bytes({
        "action": action, "resource": resource, "actor": actor, "payload": payload,
    }))


# Required top-level string fields that must be non-empty for a proposal to be
# structurally valid (fail-closed).
_REQUIRED_STR_FIELDS = (
    "contract_version", "proposal_id", "trace_id", "correlation_id",
    "adapter_id", "adapter_version", "framework", "actor", "action",
    "resource", "action_hash", "nonce", "issued_at",
)


@dataclass(frozen=True)
class CanonicalProposal:
    """The one canonical governance request every adapter produces.

    Frameworks remain responsible for planning/orchestration/memory/prompts; the
    adapter's only job is to normalize the framework's intent into this object and
    hand it to the Canonical Ingress Pipeline. Nothing here authorizes, signs, or
    executes.
    """

    # -- protocol + identity --
    proposal_id: str
    trace_id: str
    correlation_id: str
    adapter_id: str
    adapter_version: str
    framework: str
    # -- the governed action --
    actor: str
    action: str
    resource: str
    action_hash: str
    nonce: str
    issued_at: str
    payload: Dict[str, Any]
    # -- optional / contextual --
    contract_version: str = PROTOCOL_VERSION
    framework_version: Optional[str] = None
    principal: Optional[str] = None
    requested_scope: Optional[str] = None
    authority_context: Dict[str, Any] = field(default_factory=dict)
    policy_context: Dict[str, Any] = field(default_factory=dict)
    risk_context: Dict[str, Any] = field(default_factory=dict)
    expires_at: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    # -- construction ------------------------------------------------------- #

    @classmethod
    def create(cls, *, adapter_id: str, adapter_version: str, framework: str,
               actor: str, action: str, resource: str, payload: Dict[str, Any],
               framework_version: Optional[str] = None,
               principal: Optional[str] = None,
               requested_scope: Optional[str] = None,
               correlation_id: Optional[str] = None,
               trace_id: Optional[str] = None,
               authority_context: Optional[Dict[str, Any]] = None,
               policy_context: Optional[Dict[str, Any]] = None,
               risk_context: Optional[Dict[str, Any]] = None,
               metadata: Optional[Dict[str, Any]] = None,
               ttl_seconds: Optional[int] = 300,
               contract_version: str = PROTOCOL_VERSION) -> "CanonicalProposal":
        """Build a proposal, filling protocol defaults (ids, nonce, timestamps,
        action hash). Deterministic given its inputs except for the generated
        identifiers/timestamps, which are trace handles only."""
        if not isinstance(payload, dict):
            raise ProposalValidationError("payload must be a JSON object", field="payload")
        issued = _utcnow_iso()
        expires = None
        if ttl_seconds is not None:
            expires = (datetime.now(timezone.utc).replace(microsecond=0)
                       + timedelta(seconds=int(ttl_seconds))).isoformat()
        prop = cls(
            proposal_id=f"prop-{uuid.uuid4().hex}",
            trace_id=trace_id or f"trace-{uuid.uuid4().hex}",
            correlation_id=correlation_id or f"corr-{uuid.uuid4().hex}",
            adapter_id=adapter_id,
            adapter_version=adapter_version,
            framework=framework,
            actor=actor,
            action=action,
            resource=resource,
            action_hash=compute_action_hash(action, resource, actor, payload),
            nonce=uuid.uuid4().hex,
            issued_at=issued,
            payload=dict(payload),
            contract_version=contract_version,
            framework_version=framework_version,
            principal=principal or actor,
            requested_scope=requested_scope,
            authority_context=dict(authority_context or {}),
            policy_context=dict(policy_context or {}),
            risk_context=dict(risk_context or {}),
            expires_at=expires,
            metadata=dict(metadata or {}),
        )
        prop.validate()
        return prop

    # -- validation --------------------------------------------------------- #

    def validate(self) -> "CanonicalProposal":
        """Fail-closed structural validation. Never authorizes; only checks shape."""
        for name in _REQUIRED_STR_FIELDS:
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ProposalValidationError(
                    f"required field {name!r} is missing or empty", field=name)
        if not isinstance(self.payload, dict):
            raise ProposalValidationError("payload must be a JSON object", field="payload")
        for name in ("authority_context", "policy_context", "risk_context", "metadata"):
            if not isinstance(getattr(self, name), dict):
                raise ProposalValidationError(f"{name} must be a JSON object", field=name)
        # The action hash must match the payload/action binding it claims (integrity).
        expected = compute_action_hash(self.action, self.resource, self.actor, self.payload)
        if self.action_hash != expected:
            raise ProposalValidationError(
                "action_hash does not match action/resource/actor/payload",
                field="action_hash")
        return self

    def is_expired(self, *, now: Optional[datetime] = None) -> bool:
        """Whether the proposal's own validity window has elapsed (fail-closed: an
        unparseable expiry is treated as expired)."""
        if not self.expires_at:
            return False
        now = now or datetime.now(timezone.utc)
        try:
            exp = datetime.fromisoformat(self.expires_at)
        except ValueError:
            return True
        if exp.tzinfo is None:
            exp = exp.replace(tzinfo=timezone.utc)
        return now >= exp

    # -- serialization ------------------------------------------------------ #

    def to_dict(self) -> Dict[str, Any]:
        return {
            "contract_version": self.contract_version,
            "proposal_id": self.proposal_id,
            "trace_id": self.trace_id,
            "correlation_id": self.correlation_id,
            "adapter_id": self.adapter_id,
            "adapter_version": self.adapter_version,
            "framework": self.framework,
            "framework_version": self.framework_version,
            "actor": self.actor,
            "principal": self.principal,
            "action": self.action,
            "resource": self.resource,
            "requested_scope": self.requested_scope,
            "authority_context": dict(self.authority_context),
            "policy_context": dict(self.policy_context),
            "risk_context": dict(self.risk_context),
            "action_hash": self.action_hash,
            "nonce": self.nonce,
            "issued_at": self.issued_at,
            "expires_at": self.expires_at,
            "payload": dict(self.payload),
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: Any) -> "CanonicalProposal":
        """Build (and validate) a proposal from a plain dict, failing closed on a
        malformed body or missing required field."""
        if not isinstance(data, dict):
            raise ProposalValidationError("proposal is not a JSON object")
        try:
            prop = cls(
                proposal_id=str(data.get("proposal_id", "")),
                trace_id=str(data.get("trace_id", "")),
                correlation_id=str(data.get("correlation_id", "")),
                adapter_id=str(data.get("adapter_id", "")),
                adapter_version=str(data.get("adapter_version", "")),
                framework=str(data.get("framework", "")),
                actor=str(data.get("actor", "")),
                action=str(data.get("action", "")),
                resource=str(data.get("resource", "")),
                action_hash=str(data.get("action_hash", "")),
                nonce=str(data.get("nonce", "")),
                issued_at=str(data.get("issued_at", "")),
                payload=data.get("payload") if isinstance(data.get("payload"), dict) else {},
                contract_version=str(data.get("contract_version", PROTOCOL_VERSION)),
                framework_version=data.get("framework_version"),
                principal=data.get("principal"),
                requested_scope=data.get("requested_scope"),
                authority_context=dict(data.get("authority_context") or {}),
                policy_context=dict(data.get("policy_context") or {}),
                risk_context=dict(data.get("risk_context") or {}),
                expires_at=data.get("expires_at"),
                metadata=dict(data.get("metadata") or {}),
            )
        except (TypeError, ValueError) as exc:
            raise ProposalValidationError(f"malformed proposal: {exc}") from exc
        return prop.validate()


__all__ = ["CanonicalProposal", "ProposalValidationError", "compute_action_hash"]
