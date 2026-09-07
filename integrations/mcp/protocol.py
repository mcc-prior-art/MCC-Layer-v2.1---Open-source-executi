"""Minimal, dependency-free JSON-RPC 2.0 message shapes for the MCP ingress
adapter (Section 12).

No third-party ``mcp`` SDK is used here. It is not installed in this
environment (``pip show mcp`` finds nothing), and CLAUDE.md's project rules
forbid adding a new dependency without explicit approval ("Do not add
dependencies without explicit approval"). This module implements the small,
stable subset of the MCP wire shape Phase 1 actually needs
(``initialize``, ``tools/list``, ``tools/call``) directly on top of the
standard JSON-RPC 2.0 envelope, which both the stdio and HTTP transports in
this package reuse unchanged. Adopting the official SDK later — once
approved — only touches this module and ``server.py``; it changes no
authority, binding, or status semantics, all of which live in
``mcc_proposal``.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

JSONRPC_VERSION = "2.0"

# Standard JSON-RPC 2.0 error codes, plus one MCP-shaped application error.
PARSE_ERROR = -32700
INVALID_REQUEST = -32600
METHOD_NOT_FOUND = -32601
INVALID_PARAMS = -32602
INTERNAL_ERROR = -32603
APPLICATION_ERROR = -32000


def error_response(request_id: Any, code: int, message: str, *, data: Optional[Any] = None) -> Dict[str, Any]:
    error: Dict[str, Any] = {"code": code, "message": message}
    if data is not None:
        error["data"] = data
    return {"jsonrpc": JSONRPC_VERSION, "id": request_id, "error": error}


def result_response(request_id: Any, result: Any) -> Dict[str, Any]:
    return {"jsonrpc": JSONRPC_VERSION, "id": request_id, "result": result}


def tool_result(payload: Dict[str, Any], *, is_error: bool = False) -> Dict[str, Any]:
    """The MCP ``tools/call`` result envelope: a list of content blocks plus
    an ``isError`` flag. We return one JSON text block carrying the exact
    ``ProposalReceiptV1``/``OperationStatusV1`` dict — no re-shaping, no
    second serialization of governance semantics."""
    import json

    return {
        "content": [{"type": "text", "text": json.dumps(payload, sort_keys=True)}],
        "isError": is_error,
    }


__all__ = [
    "JSONRPC_VERSION", "PARSE_ERROR", "INVALID_REQUEST", "METHOD_NOT_FOUND",
    "INVALID_PARAMS", "INTERNAL_ERROR", "APPLICATION_ERROR",
    "error_response", "result_response", "tool_result",
]
