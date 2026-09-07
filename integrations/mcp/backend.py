"""Re-export of the shared proposal-backend abstraction (Section 12).

The actual implementation lives in ``mcc_proposal.transport`` so every
non-HTTP-native adapter (MCP here, plus the LangGraph/CrewAI/AutoGen facades
under ``mcc_proposal.adapters``) shares ONE backend implementation instead of
each reimplementing the same HTTP-forwarding / in-process-call logic. This
module keeps the original import path (``integrations.mcp.backend``) stable
for anything already depending on it.
"""

from __future__ import annotations

from mcc_proposal.transport import (
    HttpProposalBackend,
    InProcessProposalBackend,
    ProposalBackend,
    ProposalBackendError,
)

__all__ = ["ProposalBackendError", "ProposalBackend", "HttpProposalBackend", "InProcessProposalBackend"]
