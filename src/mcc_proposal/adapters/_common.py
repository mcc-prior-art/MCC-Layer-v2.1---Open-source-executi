"""Shared translation core for every framework facade in this package.

Every framework module (``langgraph.py``, ``crewai.py``, ``autogen.py``)
wraps these two functions in nothing more than framework-conventional
argument/return shape (Section 13: "tool/node/function argument shape,
async conventions, framework exceptions" — nothing more). Neither function
here knows LangGraph, CrewAI, or AutoGen exist.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from ..transport import ProposalBackend


async def submit_proposal_action(
    backend: ProposalBackend, *, credential: str, logical_operation_id: str,
    actor: str, action: str, resource: Optional[str] = None,
    payload: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """``framework tool call -> ProposalRequestV1 -> backend.submit_proposal``.
    Returns the exact ``ProposalReceiptV1`` dict; never re-interprets it."""
    request = {
        "logical_operation_id": logical_operation_id,
        "actor": actor,
        "action": action,
        "resource": resource,
        "payload": dict(payload or {}),
    }
    return await backend.submit_proposal(credential=credential, request=request)


async def get_operation_status_action(
    backend: ProposalBackend, *, credential: str, logical_operation_id: str,
) -> Dict[str, Any]:
    """``framework tool call -> backend.get_operation_status``. Read-only;
    returns the exact ``OperationStatusV1`` dict."""
    return await backend.get_operation_status(
        credential=credential, logical_operation_id=logical_operation_id,
    )


__all__ = ["submit_proposal_action", "get_operation_status_action"]
