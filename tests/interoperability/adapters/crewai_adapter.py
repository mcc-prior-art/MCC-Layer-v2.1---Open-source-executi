"""CrewAI interoperability adapter (PR #48d, adapter 4/5).

A **real** CrewAI integration: it builds and runs a native ``crewai.Flow``
(``crewai.flow.flow.Flow`` with ``@start`` / ``@listen`` decorated steps, compiled
and executed through the framework's own ``kickoff`` entrypoint) and extracts the
proposal the flow emits, then normalizes it into the canonical Integration Contract
proposal. The flow's steps are deterministic Python — no model client, no LLM, no
network — so the run is reproducible offline.

CrewAI ships opt-out telemetry/tracing that otherwise phones home on ``kickoff``.
This module disables it **before** importing CrewAI so the native run stays fully
offline (a hard requirement of the interoperability proof).

Framework-specific code stops at proposal normalization. The adapter authorizes
nothing, executes nothing, verifies nothing, and mints no decisions — everything
past normalization is the shared governance path reached over real HTTP.

Classification: REAL FRAMEWORK INTEGRATION.
"""

from __future__ import annotations

import contextlib
import importlib.metadata
import io
import os
import uuid
from typing import Any, Dict, Optional

# Keep the native CrewAI run offline: opt out of telemetry / tracing / OTel export
# BEFORE crewai is imported. These are honored by CrewAI's telemetry layer, which
# otherwise attempts a network export on Flow.kickoff.
os.environ.setdefault("CREWAI_DISABLE_TELEMETRY", "true")
os.environ.setdefault("CREWAI_TELEMETRY_OPT_OUT", "true")
os.environ.setdefault("CREWAI_TRACING_ENABLED", "false")
os.environ.setdefault("OTEL_SDK_DISABLED", "true")

from pydantic import BaseModel  # noqa: E402
from crewai.flow.flow import Flow, listen, start  # noqa: E402

from mcc_compliance.capability_profile import BASELINE_CAPABILITIES  # noqa: E402

from tests.interoperability.harness import CONTRACT_VERSION, CanonicalProposal  # noqa: E402

ACTOR = "agent/notify-bot"
RESOURCE = "notifications"


class _NotifyState(BaseModel):
    channel: str = "email"
    recipient: str = ""
    message: str = ""


class _NotifyFlow(Flow[_NotifyState]):
    """A native CrewAI Flow. Its ``@start`` / ``@listen`` steps deterministically
    turn a request into a tool-call proposal — this is where the framework originates
    the intent (no agent LLM / model client involved)."""

    @start()
    def plan(self) -> str:
        self.state.recipient = "customer-123"
        return "planned"

    @listen(plan)
    def compose(self, _prev: str) -> Dict[str, Any]:
        self.state.message = "appointment confirmed"
        return {
            "action": "send_notification",
            "recipient": self.state.recipient,
            "message": self.state.message,
            "channel": self.state.channel,
        }


def _run_native(channel: str) -> Dict[str, Any]:
    # Exercise the framework through its own public entrypoint: build a native Flow
    # and kick it off. ``inputs`` seeds the native flow state; the flow's final step
    # returns the emitted proposal. stdout is captured only to keep the CrewAI rich
    # console banners out of the test log — exceptions still propagate.
    flow = _NotifyFlow()
    with contextlib.redirect_stdout(io.StringIO()):
        return flow.kickoff(inputs={"channel": channel})


class CrewAIAdapter:
    adapter_name = "crewai"
    adapter_classification = "REAL FRAMEWORK INTEGRATION"
    framework_name = "crewai"
    framework_distribution = "crewai"
    framework_version = importlib.metadata.version("crewai")
    native_object_type = "crewai.flow.flow.Flow"
    native_api_entrypoint = "crewai.flow.flow.Flow.kickoff"
    adapter_module = "tests.interoperability.adapters.crewai_adapter"
    adapter_version = "1.0.0"

    def framework_provenance(self) -> Dict[str, Any]:
        return {
            "classification": self.adapter_classification,
            "framework_name": self.framework_name,
            "framework_distribution": self.framework_distribution,
            "framework_ecosystem": "pypi",
            "framework_version": self.framework_version,
            "imported_module": "crewai",
            "native_object_type": self.native_object_type,
            "native_api_entrypoint": self.native_api_entrypoint,
            "flow_steps": ["plan", "compose"],
            "adapter_module": self.adapter_module,
            "adapter_version": self.adapter_version,
        }

    def capability_profile(self) -> Dict[str, Any]:
        return {
            "profile_version": "1",
            "adapter": {"name": self.adapter_name, "version": self.adapter_version,
                        "implementation_id": self.adapter_module, "framework": "crewai"},
            "integration_contract": {"version": CONTRACT_VERSION},
            "compliance": {"suite_version": "1.0.0", "vector_set_version": "1"},
            "certification": {"claimed_status": "SELF_DECLARED", "evidence_digest": None},
            "runtime_capabilities": list(BASELINE_CAPABILITIES),
            "optional_capabilities": ["tamper_evident_audit_evidence"],
            "unsupported_capabilities": [],
            "constraints": {},
            "metadata": {"note": "Real CrewAI (Flow) integration."},
        }

    def _normalize(self, native: Dict[str, Any]) -> CanonicalProposal:
        # Adapter-specific normalization: the native flow emits intent; the adapter
        # maps it to the canonical Integration Contract proposal (adds the contract
        # fields the governed action requires). It does not authorize or execute.
        payload = {
            "recipient": native["recipient"],
            "message": native["message"],
            "priority": 2,
            "channel": native["channel"],
            "correlation_id": f"crewai-{uuid.uuid4().hex[:12]}",
        }
        return CanonicalProposal(actor_id=ACTOR, action=native["action"],
                                 resource=RESOURCE, payload=payload)

    def proposal_for(self, scenario: str) -> CanonicalProposal:
        # 1. Exercise the native framework: run a real CrewAI Flow via kickoff.
        channel = "pager" if scenario == "DENY" else "email"
        native: Optional[Dict[str, Any]] = _run_native(channel)
        if not native or not native.get("action"):
            raise RuntimeError("CrewAI flow did not emit a proposal")
        # 2. Adapter-specific normalization into the canonical contract proposal.
        return self._normalize(native)


__all__ = ["CrewAIAdapter"]
