"""MCP ingress adapter: ``mcc_submit_proposal`` / ``mcc_get_operation_status``.

This is the ONE thin adapter MCP gets in Phase 1 (Section 12). It exposes
exactly two tools, both of which do nothing but translate a JSON-RPC
``tools/call`` into a call on a :class:`~integrations.mcp.backend.ProposalBackend`
(which itself only ever reaches ``MCCProposalService``, in-process or over the
real Gateway HTTP boundary — see ``backend.py``). This module contains no
binding logic, no authority logic, no policy logic, no status inference, no
execution, and no reconciliation: every one of those questions is answered
downstream, identically for every other adapter.

Authentication is the caller transport's job, not this module's: whoever
calls :func:`handle_message` supplies ``credential`` (already extracted from
an HTTP header, an environment variable for local stdio, or whatever the
transport uses) — this module never invents, defaults, or waives it.

    MCP client
        -> tools/call {"name": "mcc_submit_proposal", "arguments": {...}}
        -> handle_message(msg, credential=<transport-authenticated caller>)
        -> ProposalBackend.submit_proposal(credential=..., request=...)
        -> MCCProposalService.submit_proposal(...)   (in-process or via HTTP)
"""

from __future__ import annotations

import sys
from typing import Any, Dict

from . import protocol
from .backend import ProposalBackend, ProposalBackendError

SERVER_NAME = "mcc-proposal-service"
SERVER_VERSION = "0.1.0-phase1"
MCP_PROTOCOL_VERSION = "2024-11-05"

TOOLS = [
    {
        "name": "mcc_submit_proposal",
        "description": (
            "Submit a governance proposal for a logical operation. This ONLY "
            "registers the proposal (status PROPOSED) — it never authorizes, "
            "signs, or executes anything. PROPOSAL != PERMISSION."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "logical_operation_id": {"type": "string", "minLength": 1},
                "actor": {"type": "string", "minLength": 1},
                "action": {"type": "string", "minLength": 1},
                "resource": {"type": ["string", "null"]},
                "payload": {"type": "object"},
            },
            "required": ["logical_operation_id", "actor", "action"],
            "additionalProperties": False,
        },
    },
    {
        "name": "mcc_get_operation_status",
        "description": (
            "Look up the status of a previously-submitted logical operation "
            "(PROPOSED/RESERVED/DISPATCH_OWNED/UNKNOWN/EXECUTED/NOT_FOUND/"
            "UNAVAILABLE). Read-only; performs zero state writes."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {"logical_operation_id": {"type": "string", "minLength": 1}},
            "required": ["logical_operation_id"],
            "additionalProperties": False,
        },
    },
]

_TOOL_NAMES = {t["name"] for t in TOOLS}


class McpProposalServer:
    def __init__(self, backend: ProposalBackend) -> None:
        self._backend = backend

    async def handle_message(self, message: Dict[str, Any], *, credential: str) -> Dict[str, Any]:
        if not isinstance(message, dict) or message.get("jsonrpc") != protocol.JSONRPC_VERSION:
            return protocol.error_response(message.get("id") if isinstance(message, dict) else None,
                                           protocol.INVALID_REQUEST, "not a JSON-RPC 2.0 request")
        request_id = message.get("id")
        method = message.get("method")
        params = message.get("params") or {}

        if method == "initialize":
            return protocol.result_response(request_id, {
                "protocolVersion": MCP_PROTOCOL_VERSION,
                "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION},
                "capabilities": {"tools": {}},
            })

        if method == "tools/list":
            return protocol.result_response(request_id, {"tools": TOOLS})

        if method == "tools/call":
            return await self._tools_call(request_id, params, credential=credential)

        return protocol.error_response(request_id, protocol.METHOD_NOT_FOUND, f"unknown method {method!r}")

    async def _tools_call(self, request_id: Any, params: Dict[str, Any], *, credential: str) -> Dict[str, Any]:
        name = params.get("name")
        arguments = params.get("arguments") or {}
        if name not in _TOOL_NAMES:
            return protocol.error_response(request_id, protocol.METHOD_NOT_FOUND, f"unknown tool {name!r}")
        if not isinstance(arguments, dict):
            return protocol.error_response(request_id, protocol.INVALID_PARAMS, "arguments must be an object")
        if not credential:
            return protocol.error_response(request_id, protocol.APPLICATION_ERROR,
                                           "no authenticated credential for this MCP session")

        try:
            if name == "mcc_submit_proposal":
                request = {k: v for k, v in arguments.items()
                          if k in ("logical_operation_id", "actor", "action", "resource", "payload")}
                payload = await self._backend.submit_proposal(credential=credential, request=request)
            else:  # mcc_get_operation_status
                logical_operation_id = arguments.get("logical_operation_id")
                if not isinstance(logical_operation_id, str) or not logical_operation_id.strip():
                    return protocol.error_response(request_id, protocol.INVALID_PARAMS,
                                                   "logical_operation_id must be a non-empty string")
                payload = await self._backend.get_operation_status(
                    credential=credential, logical_operation_id=logical_operation_id,
                )
        except ProposalBackendError as exc:
            return protocol.result_response(request_id, protocol.tool_result(
                {"status": "UNAVAILABLE", "reason": str(exc)}, is_error=True,
            ))

        return protocol.result_response(request_id, protocol.tool_result(payload))


async def _run_stdio(server: McpProposalServer, credential: str) -> None:  # pragma: no cover - manual dev entrypoint
    import json

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            message = json.loads(line)
        except json.JSONDecodeError:
            sys.stdout.write(json.dumps(
                protocol.error_response(None, protocol.PARSE_ERROR, "invalid JSON")) + "\n")
            sys.stdout.flush()
            continue
        response = await server.handle_message(message, credential=credential)
        sys.stdout.write(json.dumps(response) + "\n")
        sys.stdout.flush()


def main() -> None:  # pragma: no cover - manual dev entrypoint
    """Local stdio development entrypoint (Section 12: "Local stdio may be
    provided for development"). Never used in tests or CI; the Gateway base
    URL and credential come from the environment."""
    import asyncio
    import os

    from .backend import HttpProposalBackend

    base_url = os.environ.get("MCC_GATEWAY_URL", "http://127.0.0.1:8001")
    credential = os.environ.get("MCC_MCP_API_KEY", "")
    if not credential:
        print("FAILED: MCC_MCP_API_KEY is not set; refusing to start unauthenticated (fail-closed).",
              file=sys.stderr)
        raise SystemExit(1)
    server = McpProposalServer(HttpProposalBackend(base_url=base_url))
    asyncio.run(_run_stdio(server, credential))


if __name__ == "__main__":  # pragma: no cover
    main()


__all__ = ["McpProposalServer", "TOOLS", "SERVER_NAME", "SERVER_VERSION", "MCP_PROTOCOL_VERSION"]
