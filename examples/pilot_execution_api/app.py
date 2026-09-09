"""Reference composition: Phase 1 (proposal submission/status) + PR #111's
Pilot Execution API, correctly sharing ONE ``proposals``/``idempotency``
pair (docs/PILOT_EXECUTION_API.md §11) -- the pattern a real deployment
must follow, demonstrated runnably.

Not wired into ``gateway/app.py``'s default startup (see
docs/PILOT_EXECUTION_API.md §12: no production actuator decision has been
made for this repository). The default actuator here is a deterministic,
in-process "echo" dispatcher -- it makes no real external I/O, so this
example is safe to run with zero configuration:

    PYTHONPATH=src:.:sdk/python/src uvicorn examples.pilot_execution_api.app:app --port 8000

A real deployment replaces ``echo_upstream`` with a genuine
``ResourceBoundUpstream`` (e.g. adapting ``examples/phase2_live_sandbox/actuator.py``'s
``GitHubSandboxUpstream`` pattern, or any other controlled actuator) and
supplies real Redis-backed registries via
``mcc_proposal.registry.proposal_registry_from_env()`` /
``mcc_core.idempotency.idempotency_registry_from_env()`` /
``mcc_core.nonce.nonce_registry_from_env()``.
"""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import FastAPI

from mcc_core import InMemoryIdempotencyRegistry, InMemoryNonceRegistry
from mcc_proposal import InMemoryProposalRegistry, MCCProposalService

from gateway.proposal_api import mount_proposal_routes, tenants_from_env
from gateway.proposal_execution_api import mount_proposal_execution_routes
from gateway.proposal_execution_service import ResourceBoundUpstream
from gateway.proposal_execution_stack import build_proposal_execution_stack

ACTION = "send_notification"


async def echo_upstream(*, resource: Optional[str], action: str, payload: Dict[str, Any]) -> Any:
    """The default demo actuator: records nothing external, returns a
    deterministic acknowledgement. Replace this with a real
    ``ResourceBoundUpstream`` dispatch for an actual deployment."""
    return {"acknowledged": True, "resource": resource, "action": action}


def build_app(
    *,
    tenants_credentials: Optional[Dict[str, str]] = None,
    tenants_authority: Optional[Dict[str, Dict[str, Any]]] = None,
    upstream: Optional[ResourceBoundUpstream] = None,
    action: str = ACTION,
) -> FastAPI:
    """Build the full example app. Uses in-memory registries by default
    (override ``proposals``/``idempotency``/``nonces`` construction below
    with real Redis-backed instances for a durable deployment)."""
    tenants_credentials = tenants_credentials or tenants_from_env() or {"demo-key": "demo-tenant"}
    tenant_ids = sorted(set(tenants_credentials.values()))
    tenants_authority = tenants_authority or {t: {} for t in tenant_ids}

    proposals = InMemoryProposalRegistry()
    idempotency = InMemoryIdempotencyRegistry()
    nonces = InMemoryNonceRegistry()

    upstream = upstream or ResourceBoundUpstream(resource=None, dispatch=echo_upstream)
    audit_log_path = str(Path(tempfile.mkdtemp(prefix="mcc-pilot-execution-api-")) / "audit.jsonl")

    stack = build_proposal_execution_stack(
        proposals=proposals, idempotency=idempotency, nonces=nonces,
        tenants=tenants_authority, action=action, upstream=upstream,
        audit_log_path=audit_log_path,
    )

    # The SAME proposals/idempotency instances flow into Phase 1's status
    # service -- the shared-instance requirement docs/PILOT_EXECUTION_API.md
    # §11 documents.
    proposal_service = MCCProposalService(proposals=proposals, durable_execution_state=idempotency)

    app = FastAPI(title="MCC Pilot Execution API (example)")
    mount_proposal_routes(app, proposal_service, tenants=tenants_credentials)
    mount_proposal_execution_routes(app, stack.service, tenants=tenants_credentials)

    @app.get("/health")
    async def health() -> Dict[str, str]:
        return {"status": "ok"}

    return app


app = build_app()


__all__ = ["build_app", "app", "echo_upstream", "ACTION"]
