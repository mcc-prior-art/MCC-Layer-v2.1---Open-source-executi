"""LangGraph interoperability adapter (PR #48b, adapter 2/5).

A **real** LangGraph integration: it builds and runs a native
``langgraph.graph.StateGraph`` (compiled to a ``CompiledStateGraph``) and extracts
the proposal the graph's node emits, then normalizes it into the canonical
Integration Contract proposal. The framework is genuinely exercised through its
public API (``StateGraph`` → ``add_node``/``add_edge`` → ``compile`` → ``invoke``);
no LLM and no network are involved, so the run is deterministic and offline.

Framework-specific code stops at proposal normalization. The adapter authorizes
nothing, executes nothing, verifies nothing, and mints no decisions — everything
past normalization is the shared governance path reached over real HTTP.

Classification: REAL FRAMEWORK INTEGRATION.
"""

from __future__ import annotations

import importlib.metadata
import uuid
from typing import Any, Dict, Optional, TypedDict

from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from mcc_compliance.capability_profile import BASELINE_CAPABILITIES

from tests.interoperability.harness import CONTRACT_VERSION, CanonicalProposal

ACTOR = "agent/notify-bot"
RESOURCE = "notifications"


class _NotifyState(TypedDict):
    request: str
    channel: str
    proposal: Optional[Dict[str, Any]]


def _plan_node(state: _NotifyState) -> Dict[str, Any]:
    """A native LangGraph node: deterministically turn the request into a tool-call
    proposal. This is where the framework originates the intent."""
    return {"proposal": {
        "action": "send_notification",
        "recipient": "customer-123",
        "message": "appointment confirmed",
        "channel": state["channel"],
    }}


def _build_graph() -> CompiledStateGraph:
    g = StateGraph(_NotifyState)
    g.add_node("plan_notification", _plan_node)
    g.add_edge(START, "plan_notification")
    g.add_edge("plan_notification", END)
    return g.compile()


class LangGraphAdapter:
    adapter_name = "langgraph"
    adapter_classification = "REAL FRAMEWORK INTEGRATION"
    framework_name = "langgraph"
    framework_distribution = "langgraph"
    framework_version = importlib.metadata.version("langgraph")
    native_object_type = "langgraph.graph.state.CompiledStateGraph"
    native_api_entrypoint = "langgraph.graph.StateGraph.compile().invoke"
    adapter_module = "tests.interoperability.adapters.langgraph_adapter"
    adapter_version = "1.0.0"

    def __init__(self) -> None:
        # Build the native compiled graph once; every scenario invokes it.
        self._graph = _build_graph()

    def framework_provenance(self) -> Dict[str, Any]:
        return {
            "classification": self.adapter_classification,
            "framework_name": self.framework_name,
            "framework_distribution": self.framework_distribution,
            "framework_ecosystem": "pypi",
            "framework_version": self.framework_version,
            "imported_module": "langgraph",
            "native_object_type": self.native_object_type,
            "native_api_entrypoint": self.native_api_entrypoint,
            "graph_nodes": sorted(self._graph.get_graph().nodes.keys()),
            "adapter_module": self.adapter_module,
            "adapter_version": self.adapter_version,
        }

    def capability_profile(self) -> Dict[str, Any]:
        return {
            "profile_version": "1",
            "adapter": {"name": self.adapter_name, "version": self.adapter_version,
                        "implementation_id": self.adapter_module, "framework": "langgraph"},
            "integration_contract": {"version": CONTRACT_VERSION},
            "compliance": {"suite_version": "1.0.0", "vector_set_version": "1"},
            "certification": {"claimed_status": "SELF_DECLARED", "evidence_digest": None},
            "runtime_capabilities": list(BASELINE_CAPABILITIES),
            "optional_capabilities": ["tamper_evident_audit_evidence"],
            "unsupported_capabilities": [],
            "constraints": {},
            "metadata": {"note": "Real LangGraph integration."},
        }

    def _normalize(self, native_proposal: Dict[str, Any]) -> CanonicalProposal:
        # Adapter-specific normalization: the native node emits intent; the adapter
        # maps it to the canonical Integration Contract proposal (adds the contract
        # fields the governed action requires). It does not authorize or execute.
        payload = {
            "recipient": native_proposal["recipient"],
            "message": native_proposal["message"],
            "priority": 2,
            "channel": native_proposal["channel"],
            "correlation_id": f"langgraph-{uuid.uuid4().hex[:12]}",
        }
        return CanonicalProposal(actor_id=ACTOR, action=native_proposal["action"],
                                 resource=RESOURCE, payload=payload)

    def proposal_for(self, scenario: str) -> CanonicalProposal:
        # 1. Exercise the native framework: run the compiled LangGraph graph.
        channel = "pager" if scenario == "DENY" else "email"
        final_state = self._graph.invoke(
            {"request": "notify the customer", "channel": channel, "proposal": None})
        native = final_state["proposal"]
        if not native:
            raise RuntimeError("LangGraph graph did not emit a proposal")
        # 2. Adapter-specific normalization into the canonical contract proposal.
        return self._normalize(native)


__all__ = ["LangGraphAdapter"]
