"""CrewAI proposal/status facade (Section 13).

    CrewAI @tool call
        -> ProposalRequestV1
        -> MCCProposalService (via a ProposalBackend)
        -> CrewAI-native tool result (a string/dict; CrewAI tools conventionally
           return a string, so the dict receipt is JSON-encoded)

Same shape as ``langgraph.py``: framework-neutral action functions
(conformance-suite tested without CrewAI installed) plus an optional native
tool-builder gated on the ``crewai`` package being importable.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from ..transport import ProposalBackend
from ._common import get_operation_status_action, submit_proposal_action


async def submit_proposal(
    backend: ProposalBackend, credential: str, *, logical_operation_id: str,
    actor: str, action: str, resource: Optional[str] = None,
    payload: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    return await submit_proposal_action(
        backend, credential=credential, logical_operation_id=logical_operation_id,
        actor=actor, action=action, resource=resource, payload=payload,
    )


async def get_operation_status(backend: ProposalBackend, credential: str, *, logical_operation_id: str) -> Dict[str, Any]:
    return await get_operation_status_action(
        backend, credential=credential, logical_operation_id=logical_operation_id,
    )


def build_crewai_tools(backend: ProposalBackend, credential: str) -> List[Any]:
    """Native CrewAI ``@tool``-decorated pair. Requires the optional
    ``crewai`` dependency; raises ``ImportError`` if unavailable."""
    from crewai.tools import tool  # optional dependency

    @tool("mcc_submit_proposal")
    def _submit(logical_operation_id: str, actor: str, action: str,
               resource: Optional[str] = None, payload: Optional[Dict[str, Any]] = None) -> str:
        """Submit an MCC governance proposal (PROPOSED only; never executes)."""
        import asyncio

        result = asyncio.run(submit_proposal(
            backend, credential, logical_operation_id=logical_operation_id, actor=actor,
            action=action, resource=resource, payload=payload,
        ))
        return json.dumps(result, sort_keys=True)

    @tool("mcc_get_operation_status")
    def _status(logical_operation_id: str) -> str:
        """Read the status of an MCC logical operation (read-only)."""
        import asyncio

        result = asyncio.run(get_operation_status(backend, credential, logical_operation_id=logical_operation_id))
        return json.dumps(result, sort_keys=True)

    return [_submit, _status]


__all__ = ["submit_proposal", "get_operation_status", "build_crewai_tools"]
