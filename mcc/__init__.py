"""``mcc`` — the stable public import namespace for MCC-Core.

This is a **thin facade** over the supported :mod:`mcc_client` SDK. It exists so
application and agent code can depend on a short, stable import name::

    from mcc import MCCClient

    client = MCCClient("https://gateway.example", api_key="…")
    decision = client.evaluate(actor="agent/x", action="send_payment", …)
    result = client.execute(decision, authorization)

Every symbol below is **re-exported unchanged** from :mod:`mcc_client` — the same
class objects, not copies. The facade adds no transport, no signing, no policy,
no verification, and no local decision logic of any kind.

Architecture it faithfully represents (nothing here bypasses it):

    Agent -> MCCClient -> MCC Gateway -> Governance Decision -> Execution Gate
          -> Governed Executor -> External System

The model proposes. MCC decides. The gate enforces. The audit chain records.
**Proposal is not permission.** Authorization is performed **remotely by the
governance gateway**, never locally by this client — there is deliberately no
``MCC.authorize()`` that would imply otherwise.
"""

from __future__ import annotations

from mcc_client import __version__ as client_version
from mcc_client import (
    Approval,
    ApprovalAuthorization,
    Authorization,
    ConsensusAuthorization,
    Decision,
    ExecutionResult,
    MandateAuthorization,
    MCCAmbiguousExecutionError,
    MCCApprovalRequiredError,
    MCCAuthenticationError,
    MCCClient,
    MCCDeniedError,
    MCCError,
    MCCExecutionError,
    MCCInvalidDecisionError,
    MCCProtocolError,
    MCCReplayError,
    MCCTimeoutError,
    MCCTransportError,
    Payload,
    Transport,
    Verdict,
)

#: Version of the ``mcc-core`` facade distribution. The underlying client
#: version is available as :data:`client_version`.
__version__ = "0.1.0"

__all__ = [
    "__version__",
    "client_version",
    # client surface
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
