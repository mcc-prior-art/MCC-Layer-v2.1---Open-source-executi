"""Remote HTTP-capable MCP transport (Section 12).

A standalone FastAPI app — NOT mounted into ``gateway/app.py`` and not
started by anything in this phase (Section 12: "Do NOT deploy the MCP server
in this phase"; MCC must remain fully usable with this module never
imported). It exists so the JSON-RPC dispatch in ``server.py`` has a real,
remote-reachable transport to run over, and so the conformance suite and
targeted tests can exercise it via ``TestClient`` without a live process.

    POST /mcp   {"jsonrpc": "2.0", "id": ..., "method": "tools/call", ...}
    GET  /health
"""

from __future__ import annotations

from typing import Any, Dict

from fastapi import FastAPI, Header, Request

from .backend import ProposalBackend
from .server import MCP_PROTOCOL_VERSION, McpProposalServer, SERVER_NAME, SERVER_VERSION


def build_mcp_http_app(backend: ProposalBackend) -> FastAPI:
    app = FastAPI(
        title="MCC Proposal Service — MCP ingress (Phase 1, not deployed)",
        version=SERVER_VERSION,
        description=(
            "Ingress-only MCP adapter over the Universal Proposal Service. "
            "Carries no authority: it converges on the same MCCProposalService "
            "every other adapter reaches. See docs/MCC_UNIVERSAL_PROPOSAL_SERVICE_PHASE1.md."
        ),
    )
    mcp_server = McpProposalServer(backend)

    @app.post("/mcp")
    async def mcp_endpoint(
        request: Request, x_api_key: str = Header(default=""),
    ) -> Dict[str, Any]:
        message = await request.json()
        return await mcp_server.handle_message(message, credential=x_api_key)

    @app.get("/health")
    async def health() -> Dict[str, Any]:
        return {"status": "ok", "server": SERVER_NAME, "version": SERVER_VERSION,
                "protocolVersion": MCP_PROTOCOL_VERSION, "deployed": False}

    return app


__all__ = ["build_mcp_http_app"]
