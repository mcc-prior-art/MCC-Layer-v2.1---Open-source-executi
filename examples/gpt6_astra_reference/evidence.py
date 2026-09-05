"""Explicit terminal-status attribution and evidence-trace building.

Phase 4's own requirement, restated precisely: every run must record an
explicit terminal source, and a denial must say WHO stopped it. This module
classifies an ``ExecOutcome`` (or an Astra-side outcome) into exactly one
:class:`TerminalStatus`, using ONLY the real reason strings the real
components already return -- ``mcc_core.mandate.MandateVerifier`` /
``gateway.trust.TrustSet`` (authority), ``gateway.pre_execution_control``'s
``AttestationControlReason`` (attestation/control), and
``mcc_core.gate.ExecutionGate`` / ``mcc_core.coordinator.EnforcementCoordinator``
(gate). No new deny code is invented; this only labels which already-real
component's reason string is present.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from gateway.pre_execution_control import AttestationControlReason

#: Reason codes belonging to PR-1's own cryptographic/structural verifier --
#: the ATTESTATION ARTIFACT's own validity (signature, trust, freshness,
#: replay), as opposed to CONTROL's policy interpretation of an artifact
#: that IS structurally valid. See ``docs/ATTESTATION_ARCHITECTURE.md`` §8
#: ("PR-1 cryptographic/structural verifier" vs "deterministic Control
#: policy interpretation *above* it").
_ATTESTATION_LAYER_REASONS = frozenset({
    AttestationControlReason.ATTESTER_UNTRUSTED.value,
    AttestationControlReason.ATTESTATION_INVALID.value,
    AttestationControlReason.ATTESTATION_EXPIRED.value,
    AttestationControlReason.ATTESTATION_NOT_YET_VALID.value,
    AttestationControlReason.ATTESTATION_REPLAYED.value,
    AttestationControlReason.ATTESTATION_REPLAY_UNAVAILABLE.value,
})

#: Every other AttestationControlReason member is CONTROL's own policy
#: interpretation (binding/claim-policy over an attestation that is, or
#: would be, structurally valid).
_CONTROL_LAYER_REASONS = frozenset(
    r.value for r in AttestationControlReason
) - _ATTESTATION_LAYER_REASONS - {AttestationControlReason.NOT_REQUIRED.value,
                                   AttestationControlReason.VERIFIED.value}

#: The exact, closed set of reason strings mcc_core.mandate.MandateVerifier
#: and gateway.trust.TrustSet.resolve() return. Enumerated from the source,
#: not guessed.
_AUTHORITY_LAYER_REASON_PREFIXES = (
    "UNTRUSTED_ISSUER", "INVALID_MANDATE_SIGNATURE", "MALFORMED_MANDATE",
    "MANDATE_NOT_YET_VALID", "MANDATE_EXPIRED", "SUBJECT_MISMATCH",
    "ACTION_SCOPE_MISMATCH", "RESOURCE_SCOPE_MISMATCH", "POLICY_BINDING_MISMATCH",
    "MANDATE_REVOKED", "REVOCATION_REQUIRED", "REVOCATION_UNAVAILABLE",
    "MANDATE_ERROR", "NO_MANDATE",
    # gateway.trust.TrustSet.resolve() statuses (docs/GOVERNANCE_HTTP_API.md):
    "UNKNOWN_KID", "DISABLED_ISSUER", "EXPIRED_KEY", "REVOKED_KEY",
)


class TerminalStatus(str, Enum):
    ASTRA_PROPOSAL = "ASTRA_PROPOSAL"
    ASTRA_SELF_REFUSAL = "ASTRA_SELF_REFUSAL"
    ASTRA_ERROR = "ASTRA_ERROR"
    MCC_ATTESTATION_DENY = "MCC_ATTESTATION_DENY"
    MCC_CONTROL_DENY = "MCC_CONTROL_DENY"
    MCC_AUTHORITY_DENY = "MCC_AUTHORITY_DENY"
    MCC_GATE_DENY = "MCC_GATE_DENY"
    EXECUTION_ATTEMPT = "EXECUTION_ATTEMPT"
    EXECUTED = "EXECUTED"
    EXECUTION_FAILED = "EXECUTION_FAILED"


def classify_exec_outcome(reason: str) -> TerminalStatus:
    """Classify a ``gateway.governance_service.ExecOutcome.reason`` (or the
    equivalent from ``EnforcementCoordinator.enforce``'s ``ActuationResult``)
    into exactly one denial layer. Falls back to ``MCC_GATE_DENY`` for
    anything not recognized as authority- or control-layer -- the Gate and
    the a-h ``EnforcementCoordinator`` order are the last, catch-all
    enforcement boundary for every reason string not already accounted for
    above (nonce/idempotency/velocity/binding/token-validity)."""
    head = reason.split(":", 1)[0].strip()
    if head in _ATTESTATION_LAYER_REASONS:
        return TerminalStatus.MCC_ATTESTATION_DENY
    if head in _CONTROL_LAYER_REASONS:
        return TerminalStatus.MCC_CONTROL_DENY
    if any(head == prefix or head.startswith(prefix) for prefix in _AUTHORITY_LAYER_REASON_PREFIXES):
        return TerminalStatus.MCC_AUTHORITY_DENY
    return TerminalStatus.MCC_GATE_DENY


@dataclass(frozen=True)
class RunTrace:
    """The human-readable + machine-readable evidence for one demo run.
    Excludes API keys, bearer tokens, private signing keys, raw Decision
    Tokens, and full raw payloads -- fingerprints (hashes) only, per
    Phase 7's explicit requirement."""

    scenario: str
    astra_is_live: bool
    astra_model: Optional[str]
    proposal_fingerprint: Optional[str]
    attestation_status: Optional[str]
    attestation_fingerprint: Optional[str]
    control_decision: Optional[str]
    authority_fingerprint: Optional[str]
    gate_accepted: Optional[bool]
    gate_reason: Optional[str]
    actuator_invocations: int
    actuator_result: Optional[Dict[str, Any]]
    terminal_status: TerminalStatus
    notes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        d = dict(self.__dict__)
        d["terminal_status"] = self.terminal_status.value
        return d

    def render(self) -> str:
        lines = [
            "[ASTRA]",
            f"live: {self.astra_is_live}" + (f"  model: {self.astra_model}" if self.astra_model else ""),
            f"proposal_fingerprint: {self.proposal_fingerprint}",
        ]
        if self.attestation_status is not None:
            lines += ["", "[ATTESTER]", f"status: {self.attestation_status}",
                      f"fingerprint: {self.attestation_fingerprint}"]
        if self.control_decision is not None:
            lines += ["", "[CONTROL]", f"decision: {self.control_decision}"]
        if self.authority_fingerprint is not None:
            lines += ["", "[AUTHORITY]", f"fingerprint: {self.authority_fingerprint}"]
        if self.gate_accepted is not None:
            lines += ["", "[GATE]", f"accepted: {self.gate_accepted}", f"reason: {self.gate_reason}"]
        lines += ["", "[ACTUATOR]", f"invocations: {self.actuator_invocations}"]
        if self.actuator_result is not None:
            lines.append(f"result: {self.actuator_result}")
        lines += ["", "[RESULT]", self.terminal_status.value]
        return "\n".join(lines)


__all__ = ["TerminalStatus", "RunTrace", "classify_exec_outcome"]
