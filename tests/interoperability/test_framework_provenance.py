"""Native framework provenance checks (PR #48).

Each framework-backed adapter, when its optional distribution is installed, must be
a genuine native integration — not a stub, wrapper, or metadata-only label. These
checks are gated on the adapter having actually *registered* (i.e. its framework
imported and the adapter constructed) rather than on ``find_spec``: for namespace
packages a partial/leftover install can make ``find_spec`` true while the real API
is absent, which must skip cleanly, not fail. The base (framework-neutral) job has
no framework installed → the adapter is not registered → these tests skip. The
dedicated per-framework CI job installs the framework AND asserts the native API is
importable, so an absent/broken framework fails there.
"""

from __future__ import annotations

import pytest

from tests.interoperability.conftest import ADAPTERS


def _adapter(name: str):
    for a in ADAPTERS:
        if a.adapter_name == name:
            return a
    return None


# Gate on the adapter being genuinely usable (registered), not on find_spec.
langgraph_present = _adapter("langgraph") is not None
autogen_present = _adapter("autogen") is not None
crewai_present = _adapter("crewai") is not None


@pytest.mark.skipif(not langgraph_present, reason="langgraph adapter not registered (base job)")
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


@pytest.mark.skipif(not langgraph_present, reason="langgraph adapter not registered (base job)")
def test_langgraph_adapter_is_registered_in_the_matrix():
    names = {a.adapter_name for a in ADAPTERS}
    assert "langgraph" in names
    assert "generic-http" in names


@pytest.mark.skipif(not autogen_present, reason="autogen adapter not registered (base job)")
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


@pytest.mark.skipif(not autogen_present, reason="autogen adapter not registered (base job)")
def test_autogen_adapter_is_registered_in_the_matrix():
    names = {a.adapter_name for a in ADAPTERS}
    assert "autogen" in names and "generic-http" in names


@pytest.mark.skipif(not crewai_present, reason="crewai adapter not registered (base job)")
def test_crewai_is_a_real_native_integration():
    a = _adapter("crewai")
    assert a is not None, "CrewAI adapter not registered though crewai is installed"
    assert a.adapter_classification == "REAL FRAMEWORK INTEGRATION"

    prov = a.framework_provenance()
    import importlib.metadata
    assert prov["framework_distribution"] == "crewai"
    assert prov["framework_version"] == importlib.metadata.version("crewai")
    assert prov["framework_ecosystem"] == "pypi"
    assert prov["native_object_type"] == "crewai.flow.flow.Flow"
    assert prov["flow_steps"] == ["plan", "compose"]

    # The adapter's flow really subclasses the native CrewAI Flow, and the proposal
    # genuinely originates from running it through the framework's kickoff entrypoint.
    from crewai.flow.flow import Flow
    from tests.interoperability.adapters.crewai_adapter import _NotifyFlow
    assert issubclass(_NotifyFlow, Flow)
    prop = a.proposal_for("ALLOW")
    assert prop.action == "send_notification"
    assert prop.payload["recipient"] == "customer-123"
    assert prop.payload["channel"] == "email"
    # DENY drives a different native path (channel the policy rejects).
    assert a.proposal_for("DENY").payload["channel"] == "pager"


@pytest.mark.skipif(not crewai_present, reason="crewai adapter not registered (base job)")
def test_crewai_adapter_is_registered_in_the_matrix():
    names = {a.adapter_name for a in ADAPTERS}
    assert "crewai" in names and "generic-http" in names
