"""Path + shared fixtures for the Canonical Governance Protocol tests (PR #49)."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
for p in (ROOT / "src", ROOT / "sdk" / "python" / "src", ROOT):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import mcc_protocol as mp  # noqa: E402


def make_proposal(**overrides):
    """A valid canonical proposal for the reference adapter, with overrides."""
    kw = dict(
        adapter_id="generic-http", adapter_version="1.0.0", framework="none",
        actor="agent/notify-bot", action="send_notification", resource="notifications",
        payload={"recipient": "customer-123", "message": "hi", "priority": 2,
                 "channel": "email"},
    )
    kw.update(overrides)
    return mp.CanonicalProposal.create(**kw)


def allow_router(proposal):
    """A fake router returning a canonical ALLOW Decision (no real gateway)."""
    return mp.Decision.from_response(
        {"decision": "ALLOW", "reason": "ok", "audit_id": "aud-1",
         "forward_context": dict(proposal.payload), "policy_ref": "sha256:pol",
         "trace_id": proposal.trace_id, "decision_token": {"kid": "k1", "sig": "x"}},
        requested_actor=proposal.actor, requested_action=proposal.action,
        requested_resource=proposal.resource, requested_payload=proposal.payload)


@pytest.fixture
def registry():
    reg = mp.AdapterRegistry()
    reg.register(mp.AdapterDescriptor(
        adapter_id="generic-http", framework="none", adapter_version="1.0.0",
        supported_protocol_versions=(mp.PROTOCOL_VERSION,)))
    return reg


@pytest.fixture
def pipeline(registry):
    return mp.CanonicalIngressPipeline(registry, allow_router)
