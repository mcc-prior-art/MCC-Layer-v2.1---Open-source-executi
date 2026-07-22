"""GovernanceDecision — the canonical governance *response* envelope.

Reconciled with PR #43
----------------------
This is **not** a parallel decision model. The authoritative decision is, and
remains, :class:`mcc_client.Decision`, and the authoritative execution-authorization
artifact is, and remains, the existing **Decision Token** carried inside it.
``GovernanceDecision`` is a *promotion / envelope*: it **composes** a
:class:`mcc_client.Decision` and re-exposes it in the canonical protocol's response
shape (decision id, proposal id, verdict, reason codes, constraints, token
reference, policy/action/nonce bindings, validity window, audit reference,
timestamp). It holds the underlying ``Decision`` by reference and never re-derives,
re-signs, or overrides it.

* Verdicts are the existing :class:`mcc_client.Verdict` values — no new verdict set.
* Reason codes are drawn from the existing
  :class:`mcc_client.contract.ContractErrorCode` taxonomy — no new codes.
* Constructing an envelope authorizes nothing; it only *describes* a decision the
  Gateway already made.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from mcc_client import Decision, Verdict
from mcc_client.contract import ContractErrorCode

from .proposal import CanonicalProposal

# Blocking verdicts map to the existing stable reason codes; executable verdicts
# (ALLOW / CONSTRAIN) carry no blocking reason code.
_VERDICT_REASON_CODE = {
    Verdict.DENY: ContractErrorCode.VERDICT_DENY,
    Verdict.ESCALATE: ContractErrorCode.VERDICT_ESCALATE_REQUIRED,
}


@dataclass(frozen=True)
class GovernanceDecision:
    """Canonical response describing a governance result. Wraps a
    :class:`mcc_client.Decision`; the wrapped decision stays authoritative."""

    decision_id: str
    proposal_id: str
    verdict: Verdict
    reason_codes: List[str]
    reason: str
    constraints: Dict[str, Any]
    applied_constraints: List[str]
    #: Reference to the existing Decision Token (the authoritative execution-auth
    #: artifact). Carried as-is from the wrapped Decision — never a new token.
    decision_token: Optional[Dict[str, Any]]
    policy_hash: str
    action_hash: str
    nonce: str
    audit_reference: str
    contract_version: str
    validity_window: Dict[str, Optional[str]]
    timestamp: str
    #: The wrapped canonical decision (authoritative). Not serialized into the
    #: envelope dict twice — exposed for callers that need the full SDK model.
    decision: Decision = field(repr=False, default=None)  # type: ignore[assignment]

    # -- classification (delegates to the wrapped Decision's semantics) ------ #

    @property
    def executable(self) -> bool:
        return self.verdict in (Verdict.ALLOW, Verdict.CONSTRAIN)

    @property
    def denied(self) -> bool:
        return self.verdict == Verdict.DENY

    @property
    def needs_approval(self) -> bool:
        return self.verdict == Verdict.ESCALATE

    @property
    def has_decision_token(self) -> bool:
        return bool(self.decision_token)

    # -- construction ------------------------------------------------------- #

    @classmethod
    def from_decision(cls, proposal: CanonicalProposal, decision: Decision,
                      *, decision_id: Optional[str] = None) -> "GovernanceDecision":
        """Promote a gateway :class:`mcc_client.Decision` into the canonical
        response envelope, binding it to the originating proposal. Copies nothing
        semantic — the verdict, token, constraints and audit id all come straight
        from the authoritative decision."""
        reason_codes: List[str] = []
        code = _VERDICT_REASON_CODE.get(decision.verdict)
        if code is not None:
            reason_codes.append(code.value)
        return cls(
            decision_id=decision_id or (decision.audit_id or proposal.proposal_id),
            proposal_id=proposal.proposal_id,
            verdict=decision.verdict,
            reason_codes=reason_codes,
            reason=decision.reason,
            constraints=dict(decision.constraints),
            applied_constraints=list(decision.applied_constraints),
            decision_token=decision.decision_token,
            policy_hash=decision.policy_ref,
            action_hash=proposal.action_hash,
            nonce=proposal.nonce,
            audit_reference=decision.audit_id,
            contract_version=proposal.contract_version,
            validity_window={"issued_at": proposal.issued_at,
                             "expires_at": proposal.expires_at},
            timestamp=datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
            decision=decision,
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "decision_id": self.decision_id,
            "proposal_id": self.proposal_id,
            "verdict": self.verdict.value,
            "reason_codes": list(self.reason_codes),
            "reason": self.reason,
            "constraints": dict(self.constraints),
            "applied_constraints": list(self.applied_constraints),
            "has_decision_token": self.has_decision_token,
            "policy_hash": self.policy_hash,
            "action_hash": self.action_hash,
            "nonce": self.nonce,
            "audit_reference": self.audit_reference,
            "contract_version": self.contract_version,
            "validity_window": dict(self.validity_window),
            "timestamp": self.timestamp,
        }


__all__ = ["GovernanceDecision"]
