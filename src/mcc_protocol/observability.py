"""Unified ingress observability (PR #49).

Platform-wide, bounded-cardinality metrics for the Canonical Ingress Pipeline,
modeled on the egress proxy's observability discipline: an **isolated**
``CollectorRegistry`` (never the global default), fixed low-cardinality label sets,
and no secrets/payloads/PII in any label or value. Instrumentation only — recording
a metric never influences a decision.
"""

from __future__ import annotations

from typing import Optional

from prometheus_client import CollectorRegistry, Counter, Histogram

from .errors import IngressStage


class PipelineMetrics:
    """Bounded metrics for the ingress pipeline. All labels are low-cardinality and
    caller-controlled (adapter/framework/version/stage/verdict/outcome) — never raw
    identifiers, payloads, or user data."""

    def __init__(self, registry: Optional[CollectorRegistry] = None) -> None:
        self.registry = registry or CollectorRegistry()

        # Requests per adapter / framework / protocol version.
        self.requests = Counter(
            "mcc_ingress_requests_total",
            "Canonical proposals entering the ingress pipeline.",
            ["adapter", "framework", "protocol_version"], registry=self.registry)

        # Protocol version usage (independent of adapter, for fleet-wide view).
        self.protocol_versions = Counter(
            "mcc_ingress_protocol_version_total",
            "Protocol version seen at ingress.",
            ["protocol_version"], registry=self.registry)

        # Validation / pipeline failures, labeled by stage + stable error code.
        self.failures = Counter(
            "mcc_ingress_failures_total",
            "Ingress rejections before governance (fail-closed).",
            ["adapter", "stage", "error_code"], registry=self.registry)

        # Routing outcomes into the gateway.
        self.routed = Counter(
            "mcc_ingress_routed_total",
            "Proposals routed into the MCC Gateway.",
            ["adapter", "outcome"], registry=self.registry)

        # Governance verdict statistics (as observed at ingress egress).
        self.verdicts = Counter(
            "mcc_ingress_verdicts_total",
            "Governance verdicts returned through the pipeline.",
            ["adapter", "verdict"], registry=self.registry)

        # Pipeline latency (end-to-end, seconds).
        self.latency = Histogram(
            "mcc_ingress_pipeline_latency_seconds",
            "Ingress pipeline latency (schema->routing->decision).",
            ["adapter"], registry=self.registry)

    # -- recording helpers (never raise into the request path) -------------- #

    def record_request(self, adapter: str, framework: str, protocol_version: str) -> None:
        self.requests.labels(adapter, framework, protocol_version).inc()
        self.protocol_versions.labels(protocol_version).inc()

    def record_failure(self, adapter: str, stage: IngressStage, error_code: str) -> None:
        self.failures.labels(adapter, stage.value, error_code).inc()

    def record_routed(self, adapter: str, outcome: str) -> None:
        self.routed.labels(adapter, outcome).inc()

    def record_verdict(self, adapter: str, verdict: str) -> None:
        self.verdicts.labels(adapter, verdict).inc()

    def observe_latency(self, adapter: str, seconds: float) -> None:
        self.latency.labels(adapter).observe(seconds)


__all__ = ["PipelineMetrics"]
