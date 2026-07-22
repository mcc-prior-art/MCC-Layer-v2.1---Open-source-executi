"""Canonical Ingress Pipeline: ordered stages, fail-closed, no bypass (PR #49)."""

from __future__ import annotations

from dataclasses import replace

import pytest

import mcc_protocol as mp
from mcc_client.contract import ContractErrorCode
from mcc_client.exceptions import MCCTransportError
from mcc_protocol.errors import PIPELINE_STAGES, IngressStage
from tests.protocol.conftest import allow_router, make_proposal


def test_success_traverses_every_stage_in_order(pipeline):
    res = pipeline.process(make_proposal())
    assert res.ok
    assert res.stages_completed == PIPELINE_STAGES
    assert res.decision.verdict is mp.Verdict.ALLOW


def test_all_five_adapter_identities_share_the_same_pipeline(registry):
    # Register the five PR #48 adapters; each proposal traverses identical stages.
    for aid, fw in [("generic-http", "none"), ("langgraph", "langgraph"),
                    ("autogen", "autogen"), ("crewai", "crewai"), ("voltagent", "voltagent")]:
        registry.register(mp.AdapterDescriptor(
            adapter_id=aid, framework=fw, adapter_version="1.0.0",
            supported_protocol_versions=(mp.PROTOCOL_VERSION,)))
    pipe = mp.CanonicalIngressPipeline(registry, allow_router)
    seen = []
    for aid, fw in [("generic-http", "none"), ("langgraph", "langgraph"),
                    ("autogen", "autogen"), ("crewai", "crewai"), ("voltagent", "voltagent")]:
        res = pipe.process(make_proposal(adapter_id=aid, framework=fw))
        assert res.ok
        seen.append(tuple(res.stages_completed))
    # Every adapter traversed the identical ordered pipeline.
    assert len(set(seen)) == 1
    assert seen[0] == PIPELINE_STAGES


def test_router_is_never_called_on_a_rejection(registry):
    def exploding_router(_):
        raise AssertionError("router must not be reached on a fail-closed rejection")
    pipe = mp.CanonicalIngressPipeline(registry, exploding_router)
    # Unregistered adapter is rejected before routing.
    res = pipe.process(make_proposal(adapter_id="ghost"))
    assert not res.ok
    assert res.error.stage == IngressStage.ADAPTER_REGISTRY_LOOKUP
    assert IngressStage.ROUTING not in res.stages_completed


def test_unsupported_version_fails_closed_at_negotiation(pipeline):
    res = pipeline.process(make_proposal(contract_version="2.0"))
    assert not res.ok
    assert res.error.stage == IngressStage.VERSION_NEGOTIATION
    assert res.error.code == ContractErrorCode.CONTRACT_VERSION_UNSUPPORTED


def test_malformed_version_fails_closed(pipeline):
    res = pipeline.process(make_proposal(contract_version="xx"))
    assert not res.ok
    assert res.error.code == ContractErrorCode.CONTRACT_VERSION_MALFORMED


def test_expired_proposal_fails_closed_before_routing(pipeline):
    p = replace(make_proposal(), expires_at="2000-01-01T00:00:00+00:00")
    res = pipeline.process(p)
    assert not res.ok
    assert res.error.stage == IngressStage.PROTOCOL_VALIDATION


def test_schema_invalid_fails_closed(pipeline):
    # An action_hash that doesn't match the payload is caught at schema validation.
    p = replace(make_proposal(), action_hash="sha256:00")
    res = pipeline.process(p)
    assert not res.ok
    assert res.error.stage == IngressStage.SCHEMA_VALIDATION


def test_gateway_failure_fails_closed_at_routing(registry):
    def boom(_):
        raise MCCTransportError("gateway unavailable")
    pipe = mp.CanonicalIngressPipeline(registry, boom)
    res = pipe.process(make_proposal())
    assert not res.ok
    assert res.error.stage == IngressStage.ROUTING
    assert res.error.code == ContractErrorCode.TRANSPORT_UNAVAILABLE


def test_router_returning_non_decision_fails_closed(registry):
    pipe = mp.CanonicalIngressPipeline(registry, lambda p: {"decision": "ALLOW"})
    res = pipe.process(make_proposal())
    assert not res.ok
    assert res.error.code == ContractErrorCode.INTERNAL_ERROR


def test_required_capability_not_declared_fails_closed(registry):
    from mcc_compliance.capability_profile import BASELINE_CAPABILITIES
    pipe = mp.CanonicalIngressPipeline(registry, allow_router)
    # generic-http was registered with NO capabilities; require one -> fail closed.
    p = make_proposal(policy_context={"required_capabilities": [BASELINE_CAPABILITIES[0]]})
    res = pipe.process(p)
    assert not res.ok
    assert res.error.stage == IngressStage.CAPABILITY_VALIDATION


def test_metadata_enrichment_adds_ingress_metadata_without_touching_binding(registry):
    seen = {}

    def capturing_router(p):
        seen["proposal"] = p
        return allow_router(p)

    pipe = mp.CanonicalIngressPipeline(registry, capturing_router)
    original = make_proposal(metadata={"caller": "x"})
    res = pipe.process(original)
    assert res.ok
    enriched = seen["proposal"]
    # Enrichment added standardized ingress metadata...
    assert enriched.metadata["caller"] == "x"  # original metadata preserved
    assert enriched.metadata["ingress"]["ingress_protocol_version"] == mp.PROTOCOL_VERSION
    assert enriched.metadata["ingress"]["ingress_adapter_registered"] is True
    assert enriched.policy_context["policy_context_resolved"] is True
    # ...but never altered the action binding (action/resource/actor/payload/hash).
    assert enriched.action_hash == original.action_hash
    assert enriched.action == original.action and enriched.payload == original.payload


def test_unregistered_allowed_when_not_required(registry):
    pipe = mp.CanonicalIngressPipeline(registry, allow_router,
                                       require_registered_adapter=False)
    res = pipe.process(make_proposal(adapter_id="unknown-but-allowed"))
    assert res.ok  # traverses, unregistered metadata recorded, still governed


def test_metrics_recorded_for_success_and_failure(registry):
    pipe = mp.CanonicalIngressPipeline(registry, allow_router)
    pipe.process(make_proposal())
    pipe.process(make_proposal(adapter_id="ghost"))
    # Metric families exist and collected samples are non-empty (bounded labels).
    from prometheus_client import generate_latest
    dump = generate_latest(pipe.metrics.registry).decode()
    assert "mcc_ingress_requests_total" in dump
    assert "mcc_ingress_failures_total" in dump
    assert "mcc_ingress_verdicts_total" in dump
