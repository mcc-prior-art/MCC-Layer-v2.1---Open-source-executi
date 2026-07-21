"""AutoGen interoperability adapter (PR #48c, adapter 3/5).

A **real** AutoGen integration using the modern Microsoft AutoGen v0.4+ line —
distributions ``autogen-agentchat`` + ``autogen-core``. It runs a genuine native
AutoGen agent on a native ``SingleThreadedAgentRuntime``: a ``RoutedAgent`` with a
``@message_handler`` receives a request over the runtime and emits a proposal, which
the adapter then normalizes into the canonical Integration Contract proposal. No
model client, no LLM, no network — the agent's handler is deterministic, so the run
is reproducible offline.

Framework-specific code stops at proposal normalization. The adapter authorizes
nothing, executes nothing, verifies nothing, and mints no decisions.

Classification: REAL FRAMEWORK INTEGRATION.
API generation: Microsoft AutoGen v0.4+ (autogen-core / autogen-agentchat), 0.7.x.
"""

from __future__ import annotations

import asyncio
import importlib.metadata
import uuid
from dataclasses import dataclass
from typing import Any, Dict

from autogen_core import (
    AgentId,
    MessageContext,
    RoutedAgent,
    SingleThreadedAgentRuntime,
    message_handler,
)

from mcc_compliance.capability_profile import BASELINE_CAPABILITIES

from tests.interoperability.harness import CONTRACT_VERSION, CanonicalProposal

ACTOR = "agent/notify-bot"
RESOURCE = "notifications"


@dataclass
class _NotifyRequest:
    channel: str


@dataclass
class _NotifyProposal:
    action: str
    recipient: str
    message: str
    channel: str


class _NotifyAgent(RoutedAgent):
    """A native AutoGen RoutedAgent. Its message handler deterministically turns a
    request into a tool-call proposal — this is where the framework originates the
    intent (no model client involved)."""

    def __init__(self) -> None:
        super().__init__("notify planner")

    @message_handler
    async def handle(self, message: _NotifyRequest, ctx: MessageContext) -> _NotifyProposal:
        return _NotifyProposal(action="send_notification", recipient="customer-123",
                               message="appointment confirmed", channel=message.channel)


async def _run_native(channel: str) -> _NotifyProposal:
    runtime = SingleThreadedAgentRuntime()
    await _NotifyAgent.register(runtime, "notify_agent", lambda: _NotifyAgent())
    runtime.start()
    try:
        return await runtime.send_message(_NotifyRequest(channel=channel),
                                          AgentId("notify_agent", "default"))
    finally:
        await runtime.stop()


class AutoGenAdapter:
    adapter_name = "autogen"
    adapter_classification = "REAL FRAMEWORK INTEGRATION"
    framework_name = "autogen"
    framework_distribution = "autogen-agentchat"
    framework_version = importlib.metadata.version("autogen-agentchat")
    autogen_core_version = importlib.metadata.version("autogen-core")
    native_object_type = "autogen_core.RoutedAgent on SingleThreadedAgentRuntime"
    native_api_entrypoint = "autogen_core.SingleThreadedAgentRuntime.send_message"
    adapter_module = "tests.interoperability.adapters.autogen_adapter"
    adapter_version = "1.0.0"

    def framework_provenance(self) -> Dict[str, Any]:
        return {
            "classification": self.adapter_classification,
            "framework_name": self.framework_name,
            "framework_distribution": self.framework_distribution,
            "framework_ecosystem": "pypi",
            "framework_version": self.framework_version,
            "api_generation": "Microsoft AutoGen v0.4+ (autogen-core/autogen-agentchat)",
            "autogen_core_version": self.autogen_core_version,
            "imported_module": "autogen_core",
            "native_object_type": self.native_object_type,
            "native_api_entrypoint": self.native_api_entrypoint,
            "adapter_module": self.adapter_module,
            "adapter_version": self.adapter_version,
        }

    def capability_profile(self) -> Dict[str, Any]:
        return {
            "profile_version": "1",
            "adapter": {"name": self.adapter_name, "version": self.adapter_version,
                        "implementation_id": self.adapter_module, "framework": "autogen"},
            "integration_contract": {"version": CONTRACT_VERSION},
            "compliance": {"suite_version": "1.0.0", "vector_set_version": "1"},
            "certification": {"claimed_status": "SELF_DECLARED", "evidence_digest": None},
            "runtime_capabilities": list(BASELINE_CAPABILITIES),
            "optional_capabilities": ["tamper_evident_audit_evidence"],
            "unsupported_capabilities": [],
            "constraints": {},
            "metadata": {"note": "Real AutoGen (v0.4+) integration."},
        }

    def _normalize(self, native: _NotifyProposal) -> CanonicalProposal:
        payload = {
            "recipient": native.recipient,
            "message": native.message,
            "priority": 2,
            "channel": native.channel,
            "correlation_id": f"autogen-{uuid.uuid4().hex[:12]}",
        }
        return CanonicalProposal(actor_id=ACTOR, action=native.action,
                                 resource=RESOURCE, payload=payload)

    def proposal_for(self, scenario: str) -> CanonicalProposal:
        # 1. Exercise the native framework: run a real AutoGen agent on a native
        #    SingleThreadedAgentRuntime and collect the proposal it emits.
        channel = "pager" if scenario == "DENY" else "email"
        native = asyncio.run(_run_native(channel))
        if not native or not native.action:
            raise RuntimeError("AutoGen agent did not emit a proposal")
        # 2. Adapter-specific normalization into the canonical contract proposal.
        return self._normalize(native)


__all__ = ["AutoGenAdapter"]
