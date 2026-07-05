"""MCC-Core Python client SDK.

The supported, typed Python client for MCC-Core governance. It is the canonical
integration path for an external AI agent or application:

    Agent -> MCCClient -> MCC Gateway -> Governance Decision -> Execution Gate
          -> Governed Executor -> External System

The model proposes. MCC decides. The gate enforces. The audit chain records.
Proposal is not permission.

The SDK is a client, not a policy engine: it makes no decisions locally, signs
nothing, bypasses neither the gateway nor the execution gate, and never treats a
network success as governance approval.
"""

from __future__ import annotations

from .client import Authorization, MCCClient
from .exceptions import (
    MCCAmbiguousExecutionError,
    MCCApprovalRequiredError,
    MCCAuthenticationError,
    MCCDeniedError,
    MCCError,
    MCCExecutionError,
    MCCInvalidDecisionError,
    MCCProtocolError,
    MCCReplayError,
    MCCTimeoutError,
    MCCTransportError,
)
from .models import (
    Approval,
    ApprovalAuthorization,
    ConsensusAuthorization,
    Decision,
    ExecutionResult,
    MandateAuthorization,
    Payload,
    Verdict,
)
from .transport import Transport

__version__ = "0.1.0"

__all__ = [
    "__version__",
    "MCCClient",
    "Authorization",
    "Transport",
    # models
    "Verdict",
    "Decision",
    "Approval",
    "ExecutionResult",
    "ApprovalAuthorization",
    "MandateAuthorization",
    "ConsensusAuthorization",
    "Payload",
    # exceptions
    "MCCError",
    "MCCTransportError",
    "MCCTimeoutError",
    "MCCProtocolError",
    "MCCAuthenticationError",
    "MCCDeniedError",
    "MCCApprovalRequiredError",
    "MCCInvalidDecisionError",
    "MCCReplayError",
    "MCCExecutionError",
    "MCCAmbiguousExecutionError",
]
