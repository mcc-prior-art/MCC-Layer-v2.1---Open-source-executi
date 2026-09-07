"""MCP ingress adapter for the MCC Universal Proposal Service (Phase 1).

Ingress-only: no execution authority, no executor of its own, no direct
upstream calls. Every tool call converges on ``MCCProposalService`` —
in-process (dev/tests) or over a real Gateway's HTTP boundary
(``HttpProposalBackend``), never a second decision path.

Not deployed by anything in this phase (see ``http_app.py``); importing this
package has no side effects on the Gateway or any other running service.
"""

from __future__ import annotations

from .backend import HttpProposalBackend, InProcessProposalBackend, ProposalBackendError
from .server import TOOLS, McpProposalServer

__all__ = [
    "McpProposalServer", "TOOLS",
    "HttpProposalBackend", "InProcessProposalBackend", "ProposalBackendError",
]
