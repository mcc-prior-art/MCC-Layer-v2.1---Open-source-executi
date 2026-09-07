"""AutoGen proposal/status facade (Section 13).

    AutoGen FunctionTool call
        -> ProposalRequestV1
        -> MCCProposalService (via a ProposalBackend)
        -> AutoGen-native tool result (JSON-serializable dict/string)

Same shape as ``langgraph.py``/``crewai.py``: framework-neutral action
functions (conformance-suite tested without AutoGen installed) plus an
optional native tool-builder gated on ``autogen_core`` being importable.
"""

from __future__ import annotations

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


def build_autogen_tools(backend: ProposalBackend, credential: str) -> List[Any]:
    """Native AutoGen ``FunctionTool`` pair. Requires the optional
    ``autogen_core`` dependency; raises ``ImportError`` if unavailable."""
    from autogen_core.tools import FunctionTool  # optional dependency

    async def _submit(logical_operation_id: str, actor: str, action: str,
                      resource: Optional[str] = None, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Submit an MCC governance proposal (PROPOSED only; never executes)."""
        return await submit_proposal(
            backend, credential, logical_operation_id=logical_operation_id, actor=actor,
            action=action, resource=resource, payload=payload,
        )

    async def _status(logical_operation_id: str) -> Dict[str, Any]:
        """Read the status of an MCC logical operation (read-only)."""
        return await get_operation_status(backend, credential, logical_operation_id=logical_operation_id)

    return [
        FunctionTool(_submit, description="Submit an MCC governance proposal (PROPOSED only).",
                    name="mcc_submit_proposal"),
        FunctionTool(_status, description="Read the status of an MCC logical operation (read-only).",
                    name="mcc_get_operation_status"),
    ]


__all__ = ["submit_proposal", "get_operation_status", "build_autogen_tools"]
