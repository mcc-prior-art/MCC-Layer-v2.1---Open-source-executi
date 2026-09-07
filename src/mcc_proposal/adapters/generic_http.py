"""Generic HTTP facade (Section 13/15) — for conformance-suite symmetry.

The Generic HTTP "adapter" for the Universal Proposal Service is simply a
real HTTP client calling ``POST /v1/proposals`` / ``GET
/v1/operations/{id}`` (``gateway/proposal_api.py``) with no framework
involved at all. This module gives it the exact same
``submit_proposal``/``get_operation_status`` signature as every other
facade in this package purely so the conformance suite and cross-adapter
parity tests can iterate over one uniform list of adapters — it adds no
behavior beyond ``HttpProposalBackend`` itself.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

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


__all__ = ["submit_proposal", "get_operation_status"]
