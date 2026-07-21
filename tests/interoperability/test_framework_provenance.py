"""Native framework provenance checks (PR #48).

Each framework-backed adapter, when its optional distribution is installed, must be
a genuine native integration — not a stub, wrapper, or metadata-only label. These
checks are gated on the framework being importable so the base (framework-neutral)
job stays green; the dedicated per-framework CI job installs the framework, which
activates the gate and fails if the real package or native object is absent.
"""

from __future__ import annotations

import importlib.util

import pytest

from tests.interoperability.conftest import ADAPTERS

langgraph_installed = importlib.util.find_spec("langgraph") is not None
autogen_installed = importlib.util.find_spec("autogen_core") is not None


def _adapter(name: str):
    for a in ADAPTERS:
        if a.adapter_name == name:
            return a
    return None


@pytest.mark.skipif(not langgraph_installed, reason="langgraph not installed (base job)")
def test_langgraph_is_a_real_native_integration():
    a = _adapter("langgraph")
    assert a is not None, "LangGraph adapter not registered though langgraph is installed"
    assert a.adapter_classification == "REAL FRAMEWORK INTEGRATION"

    prov = a.framework_provenance()
    # Real, resolved distribution + version (not a placeholder).
    import importlib.metadata
    assert prov["framework_distribution"] == "langgraph"
    assert prov["framework_version"] == importlib.metadata.version("langgraph")
    assert prov["framework_ecosystem"] == "pypi"
    # A real native compiled graph was built and its node is present.
    assert prov["native_object_type"] == "langgraph.graph.state.CompiledStateGraph"
    assert "plan_notification" in prov["graph_nodes"]

    # The proposal genuinely originates from invoking the native graph.
    from langgraph.graph.state import CompiledStateGraph
    assert isinstance(a._graph, CompiledStateGraph)
    prop = a.proposal_for("ALLOW")
    assert prop.action == "send_notification"
    assert prop.payload["recipient"] == "customer-123"
    assert prop.payload["channel"] == "email"
    # DENY drives a different native path (channel the policy rejects).
    assert a.proposal_for("DENY").payload["channel"] == "pager"


@pytest.mark.skipif(not langgraph_installed, reason="langgraph not installed (base job)")
def test_langgraph_adapter_is_registered_in_the_matrix():
    names = {a.adapter_name for a in ADAPTERS}
    assert "langgraph" in names
    assert "generic-http" in names


@pytest.mark.skipif(not autogen_installed, reason="autogen not installed (base job)")
def test_autogen_is_a_real_native_integration():
    a = _adapter("autogen")
    assert a is not None, "AutoGen adapter not registered though autogen-core is installed"
    assert a.adapter_classification == "REAL FRAMEWORK INTEGRATION"

    prov = a.framework_provenance()
    import importlib.metadata
    assert prov["framework_distribution"] == "autogen-agentchat"
    assert prov["framework_version"] == importlib.metadata.version("autogen-agentchat")
    assert prov["autogen_core_version"] == importlib.metadata.version("autogen-core")
    assert prov["framework_ecosystem"] == "pypi"
    assert "AutoGen v0.4+" in prov["api_generation"]
    assert prov["native_object_type"].startswith("autogen_core.RoutedAgent")

    # The adapter's agent really subclasses the native RoutedAgent, and the proposal
    # genuinely originates from running it on the native runtime.
    from autogen_core import RoutedAgent
    from tests.interoperability.adapters.autogen_adapter import _NotifyAgent
    assert issubclass(_NotifyAgent, RoutedAgent)
    prop = a.proposal_for("ALLOW")
    assert prop.action == "send_notification"
    assert prop.payload["recipient"] == "customer-123"
    assert prop.payload["channel"] == "email"
    assert a.proposal_for("DENY").payload["channel"] == "pager"


@pytest.mark.skipif(not autogen_installed, reason="autogen not installed (base job)")
def test_autogen_adapter_is_registered_in_the_matrix():
    names = {a.adapter_name for a in ADAPTERS}
    assert "autogen" in names and "generic-http" in names
