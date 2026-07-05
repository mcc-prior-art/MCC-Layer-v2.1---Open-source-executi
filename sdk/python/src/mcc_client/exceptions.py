"""Exception hierarchy for the MCC-Core Python client SDK.

Every failure mode is a distinct, typed exception. No error, timeout, malformed
response, or network success is ever interpreted as permission — the SDK fails
closed. A governance DENY / ESCALATE is surfaced as a typed exception on
execution (never silently downgraded to success).
"""

from __future__ import annotations

from typing import Any, Optional


class MCCError(Exception):
    """Base class for all MCC client errors."""


class MCCTransportError(MCCError):
    """A network/transport failure talking to the gateway (connection, DNS, TLS)."""


class MCCTimeoutError(MCCTransportError):
    """A request to the gateway timed out."""


class MCCProtocolError(MCCError):
    """The gateway response was malformed, schema-invalid, or carried an unknown
    verdict / missing decision material (fail-closed)."""


class MCCAuthenticationError(MCCError):
    """The gateway rejected the API key / operator key (HTTP 401/403)."""


class MCCDeniedError(MCCError):
    """Execution was attempted on a DENY decision (governance refused the action)."""

    def __init__(self, reason: str, *, audit_id: Optional[str] = None) -> None:
        super().__init__(reason)
        self.reason = reason
        self.audit_id = audit_id


class MCCApprovalRequiredError(MCCError):
    """Execution was attempted on an ESCALATE decision without a valid approval."""

    def __init__(self, reason: str, *, authority_required: Optional[str] = None,
                 audit_id: Optional[str] = None) -> None:
        super().__init__(reason)
        self.reason = reason
        self.authority_required = authority_required
        self.audit_id = audit_id


class MCCInvalidDecisionError(MCCError):
    """The decision cannot authorize this execution: missing decision material, a
    decision that cannot be bound to the requested action, or an attempt to change
    actor/action/resource/payload-bound fields."""


class MCCReplayError(MCCError):
    """The gateway rejected a replayed / already-consumed decision or nonce."""


class MCCExecutionError(MCCError):
    """The governed execution ran but did not complete (BLOCKED / EXECUTION_FAILED)."""

    def __init__(self, reason: str, *, status: Optional[str] = None,
                 audit_ref: Optional[str] = None, raw: Any = None) -> None:
        super().__init__(reason)
        self.reason = reason
        self.status = status
        self.audit_ref = audit_ref
        self.raw = raw


class MCCAmbiguousExecutionError(MCCError):
    """The SDK cannot determine whether execution occurred (e.g. a transport
    failure after the request was sent). The caller MUST NOT assume success and
    MUST NOT blindly retry — reconcile via the audit chain."""

    def __init__(self, reason: str, *, correlation_id: Optional[str] = None) -> None:
        super().__init__(reason)
        self.reason = reason
        self.correlation_id = correlation_id


__all__ = [
    "MCCError", "MCCTransportError", "MCCTimeoutError", "MCCProtocolError",
    "MCCAuthenticationError", "MCCDeniedError", "MCCApprovalRequiredError",
    "MCCInvalidDecisionError", "MCCReplayError", "MCCExecutionError",
    "MCCAmbiguousExecutionError",
]
