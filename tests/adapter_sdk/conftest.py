"""Adapter SDK test fixtures (PR #50)."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[2]
for p in (ROOT / "src", ROOT / "sdk" / "python" / "src", ROOT):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import mcc_protocol as mp  # noqa: E402
from mcc_adapter_sdk import Adapter, AdapterContext, AdapterMetadata  # noqa: E402
from mcc_compliance.capability_profile import BASELINE_CAPABILITIES  # noqa: E402


class GoodAdapter(Adapter):
    """A minimal, well-formed adapter for the tests."""

    def describe(self) -> AdapterMetadata:
        return AdapterMetadata.create(
            adapter_id="test-good", adapter_version="1.0.0", framework_name="none",
            capabilities=(BASELINE_CAPABILITIES[0],),
            supported_input_modes=("text",), supported_output_modes=("json",),
            vendor="ACME", maintainer="dev@acme.test")

    def to_proposal(self, context: AdapterContext, native_request: Any) -> mp.CanonicalProposal:
        return self.make_proposal(
            context, action="send_notification", resource="notifications",
            payload={"recipient": "customer-123", "message": str(native_request),
                     "priority": 2, "channel": "email"})

    def to_response(self, decision: mp.GovernanceDecision) -> Any:
        return {"verdict": decision.verdict.value, "executable": decision.executable}

    def sample_request(self) -> Any:
        return "hello"


def make_router(verdict: str = "ALLOW", *, raises: Exception | None = None):
    """A local deterministic router standing in for the gateway (no authorization)."""
    def router(proposal: mp.CanonicalProposal) -> mp.Decision:
        if raises is not None:
            raise raises
        return mp.Decision.from_response(
            {"decision": verdict, "reason": "test", "audit_id": "test-audit",
             "forward_context": dict(proposal.payload), "policy_ref": "sha256:pol",
             "trace_id": proposal.trace_id,
             "decision_token": ({"kid": "k1"} if verdict in ("ALLOW", "CONSTRAIN") else None)},
            requested_actor=proposal.actor, requested_action=proposal.action,
            requested_resource=proposal.resource, requested_payload=proposal.payload)
    return router


@pytest.fixture
def good_adapter() -> GoodAdapter:
    return GoodAdapter()


@pytest.fixture
def context() -> AdapterContext:
    return AdapterContext.create(actor_reference="agent/notify-bot", tenant="t1")
