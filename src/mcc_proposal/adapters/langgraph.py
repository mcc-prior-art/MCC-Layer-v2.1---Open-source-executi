"""LangGraph proposal/status facade (Section 13).

    LangGraph tool/node call
        -> ProposalRequestV1
        -> MCCProposalService (via a ProposalBackend)
        -> LangGraph-native tool result (a plain dict; LangChain tools return
           JSON-serializable values, so no further translation is needed)

``submit_proposal``/``get_operation_status`` below are framework-neutral
(only ``dict`` in, ``dict`` out) and are exercised directly by the
conformance suite without LangGraph installed. ``build_langgraph_tools`` is
the optional native convenience: it lazily imports ``langchain_core`` (the
tool abstraction LangGraph orchestrates) and is only exercised when that
package is available -- exactly the "registered only if importable"
convention ``tests/interoperability/adapters/langgraph_adapter.py`` already
uses for the (separate, execution-side) five-ecosystem proof.
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


def build_langgraph_tools(backend: ProposalBackend, credential: str) -> List[Any]:
    """Native LangChain/LangGraph ``StructuredTool`` pair. Requires the
    optional ``langchain_core`` dependency; raises ``ImportError`` with a
    clear message if it is not installed rather than degrading silently."""
    from langchain_core.tools import StructuredTool  # optional dependency

    async def _submit(logical_operation_id: str, actor: str, action: str,
                      resource: Optional[str] = None, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return await submit_proposal(
            backend, credential, logical_operation_id=logical_operation_id, actor=actor,
            action=action, resource=resource, payload=payload,
        )

    async def _status(logical_operation_id: str) -> Dict[str, Any]:
        return await get_operation_status(backend, credential, logical_operation_id=logical_operation_id)

    return [
        StructuredTool.from_function(
            coroutine=_submit, name="mcc_submit_proposal",
            description="Submit an MCC governance proposal (PROPOSED only; never executes).",
        ),
        StructuredTool.from_function(
            coroutine=_status, name="mcc_get_operation_status",
            description="Read the status of an MCC logical operation (read-only).",
        ),
    ]


__all__ = ["submit_proposal", "get_operation_status", "build_langgraph_tools"]
