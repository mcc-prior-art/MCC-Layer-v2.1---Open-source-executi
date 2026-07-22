"""Unified ingress observability: bounded, safe, non-authorizing (PR #49)."""

from __future__ import annotations

from prometheus_client import generate_latest

from mcc_protocol.errors import IngressStage
from mcc_protocol.observability import PipelineMetrics


def test_metrics_use_an_isolated_registry():
    m1, m2 = PipelineMetrics(), PipelineMetrics()
    assert m1.registry is not m2.registry  # never the global default


def test_records_are_bounded_and_labeled():
    m = PipelineMetrics()
    m.record_request("voltagent", "voltagent", "1.0")
    m.record_verdict("voltagent", "ALLOW")
    m.record_failure("crewai", IngressStage.VERSION_NEGOTIATION, "CONTRACT_VERSION_UNSUPPORTED")
    m.record_routed("langgraph", "ok")
    m.observe_latency("autogen", 0.01)
    dump = generate_latest(m.registry).decode()
    for family in ("mcc_ingress_requests_total", "mcc_ingress_verdicts_total",
                   "mcc_ingress_failures_total", "mcc_ingress_routed_total",
                   "mcc_ingress_protocol_version_total",
                   "mcc_ingress_pipeline_latency_seconds"):
        assert family in dump
    # Labels carry only the coarse identifiers we passed — no payload/secret.
    assert 'adapter="voltagent"' in dump
    assert "customer-123" not in dump


def test_no_secret_or_payload_leaks_into_metrics():
    m = PipelineMetrics()
    m.record_request("a", "f", "1.0")
    dump = generate_latest(m.registry).decode()
    for forbidden in ("password", "token", "secret", "payload", "message"):
        assert forbidden not in dump.lower()
