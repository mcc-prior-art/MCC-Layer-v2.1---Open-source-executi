"""Ingress-pipeline failure handling (PR #49) — reconciled with PR #43.

The Canonical Ingress Pipeline introduces **no new stable error taxonomy**. Every
failure is classified into the *existing* contract error taxonomy
(:class:`mcc_client.contract.ContractErrorCode`) so there is exactly one set of
stable, machine-readable codes across the platform. What this module adds is only
an :class:`IngressStage` label (observability — *where* a proposal was rejected)
and a fail-closed exception type that always carries a blocking contract code.

A pipeline failure is never an authorization. Fail-closed is the default: when no
more-specific contract code applies, a failure resolves to
``CONTRACT_FIELD_INVALID`` (a blocking, pre-governance classification) or
``INTERNAL_ERROR`` — never to permission.
"""

from __future__ import annotations

from enum import Enum

from mcc_client.contract import ContractErrorCode, category_of


class IngressStage(str, Enum):
    """The ordered stages of the Canonical Ingress Pipeline. The value is an
    observability label only; it never affects authorization."""

    SCHEMA_VALIDATION = "schema_validation"
    PROTOCOL_VALIDATION = "protocol_validation"
    VERSION_NEGOTIATION = "version_negotiation"
    ADAPTER_REGISTRY_LOOKUP = "adapter_registry_lookup"
    CAPABILITY_VALIDATION = "capability_validation"
    METADATA_ENRICHMENT = "metadata_enrichment"
    POLICY_CONTEXT_RESOLUTION = "policy_context_resolution"
    ROUTING = "routing"
    COMPLETE = "complete"


#: Ordered pipeline stages executed before governance evaluation (COMPLETE is the
#: terminal marker after routing returns a decision — not a validation stage).
PIPELINE_STAGES = (
    IngressStage.SCHEMA_VALIDATION,
    IngressStage.PROTOCOL_VALIDATION,
    IngressStage.VERSION_NEGOTIATION,
    IngressStage.ADAPTER_REGISTRY_LOOKUP,
    IngressStage.CAPABILITY_VALIDATION,
    IngressStage.METADATA_ENRICHMENT,
    IngressStage.POLICY_CONTEXT_RESOLUTION,
    IngressStage.ROUTING,
)


class IngressError(Exception):
    """A fail-closed ingress rejection. Always carries a *blocking* contract error
    code (reused from PR #43) plus the stage where the rejection happened.

    Raising or returning an ``IngressError`` never authorizes anything — it is the
    canonical way the pipeline says "this proposal did not reach governance, and it
    must not be executed."
    """

    def __init__(self, stage: IngressStage, code: ContractErrorCode, reason: str) -> None:
        self.stage = stage
        self.code = code
        self.reason = reason
        super().__init__(f"[{stage.value}] {code.value}: {reason}")

    @property
    def category(self) -> str:
        """The contract error category for this failure (reused taxonomy)."""
        return category_of(self.code).value

    def to_dict(self) -> dict:
        return {
            "stage": self.stage.value,
            "error_code": self.code.value,
            "error_category": self.category,
            "reason": self.reason,
        }


__all__ = ["IngressStage", "PIPELINE_STAGES", "IngressError"]
