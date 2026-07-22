"""The Canonical Ingress Pipeline (PR #49).

One mandatory, shared, in-process pipeline that every adapter's
:class:`CanonicalProposal` traverses **before** governance evaluation. It performs,
in a fixed order:

    schema validation -> protocol validation -> version negotiation ->
    adapter registry lookup -> capability validation -> metadata enrichment ->
    policy context resolution -> routing -> (fail-closed throughout)

Hard boundary (enforced by an architecture guard)
-------------------------------------------------
The pipeline is **not** a second governance engine. It validates, normalizes,
enriches, and routes proposals into the *existing* authoritative MCC Gateway. It
does **not** authorize, evaluate policy, issue Decision Tokens, verify signatures,
run the Gate, or replace the Gateway. The Gateway is reached only through an
injected ``router`` callable (the existing :class:`mcc_client.MCCClient` boundary in
production) — this module imports no gateway/gate/authority/consensus/signing
internals. Every failure fails closed: no router call happens after a rejection, and
a rejection is never an authorization.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, replace
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional, Tuple

from mcc_client import Decision
from mcc_client.contract import ContractErrorCode, error_code_for_exception

from .decision import GovernanceDecision
from .errors import IngressError, IngressStage
from .observability import PipelineMetrics
from .proposal import CanonicalProposal, ProposalValidationError
from .registry import AdapterRegistry, AdapterRegistryError
from .version import PROTOCOL_VERSION, negotiate

#: A router submits an (already validated/enriched) proposal to the authoritative
#: MCC Gateway and returns the canonical :class:`mcc_client.Decision`. In production
#: this wraps :class:`mcc_client.MCCClient`; the pipeline never talks to the gateway
#: any other way.
Router = Callable[[CanonicalProposal], Decision]

#: Optional, non-authorizing hook to resolve/normalize policy context. It MUST NOT
#: evaluate policy or authorize — it only shapes context the Gateway will use.
PolicyContextResolver = Callable[[CanonicalProposal], Dict[str, Any]]


@dataclass(frozen=True)
class IngressResult:
    """The outcome of one proposal traversing the pipeline. Either a
    :class:`GovernanceDecision` (routing succeeded and the Gateway decided) or an
    :class:`IngressError` (fail-closed rejection before/at a stage)."""

    proposal_id: str
    adapter_id: str
    stages_completed: Tuple[IngressStage, ...]
    decision: Optional[GovernanceDecision] = None
    error: Optional[IngressError] = None

    @property
    def ok(self) -> bool:
        return self.decision is not None and self.error is None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "proposal_id": self.proposal_id,
            "adapter_id": self.adapter_id,
            "stages_completed": [s.value for s in self.stages_completed],
            "ok": self.ok,
            "decision": self.decision.to_dict() if self.decision else None,
            "error": self.error.to_dict() if self.error else None,
        }


class CanonicalIngressPipeline:
    """The one shared ingress pipeline. Construct it with the adapter registry and a
    router into the Gateway; call :meth:`process` for each proposal."""

    def __init__(self, registry: AdapterRegistry, router: Router, *,
                 policy_context_resolver: Optional[PolicyContextResolver] = None,
                 metrics: Optional[PipelineMetrics] = None,
                 require_registered_adapter: bool = True) -> None:
        self.registry = registry
        self._router = router
        self._resolve_policy_context = policy_context_resolver
        self.metrics = metrics or PipelineMetrics()
        self._require_registered_adapter = require_registered_adapter

    # -- public API --------------------------------------------------------- #

    def process(self, proposal: CanonicalProposal) -> IngressResult:
        """Run a proposal through every stage, fail-closed. Never raises for an
        expected rejection — the rejection is returned inside the result."""
        completed: List[IngressStage] = []
        started = time.perf_counter()
        adapter_id = getattr(proposal, "adapter_id", "") or "unknown"
        try:
            self.metrics.record_request(
                adapter_id, getattr(proposal, "framework", "") or "unknown",
                getattr(proposal, "contract_version", "") or "unknown")
        except Exception:  # noqa: BLE001 — metrics must never break the path
            pass

        try:
            enriched = self._run_validation_stages(proposal, completed)
        except IngressError as err:
            self._record_failure(adapter_id, err)
            return IngressResult(
                proposal_id=getattr(proposal, "proposal_id", "") or "",
                adapter_id=adapter_id, stages_completed=tuple(completed), error=err)

        # ROUTING — the only stage that reaches the Gateway (via the injected router).
        try:
            decision = self._router(enriched)
            if not isinstance(decision, Decision):
                raise IngressError(
                    IngressStage.ROUTING, ContractErrorCode.INTERNAL_ERROR,
                    "router did not return a canonical Decision")
        except IngressError as err:
            self._record_failure(adapter_id, err)
            return IngressResult(
                proposal_id=enriched.proposal_id, adapter_id=adapter_id,
                stages_completed=tuple(completed), error=err)
        except Exception as exc:  # noqa: BLE001 — any gateway/transport failure fails closed
            err = IngressError(IngressStage.ROUTING,
                               error_code_for_exception(exc),
                               f"routing into the gateway failed: {type(exc).__name__}")
            self._record_failure(adapter_id, err)
            try:
                self.metrics.record_routed(adapter_id, "error")
            except Exception:  # noqa: BLE001
                pass
            return IngressResult(
                proposal_id=enriched.proposal_id, adapter_id=adapter_id,
                stages_completed=tuple(completed), error=err)

        completed.append(IngressStage.ROUTING)
        gov = GovernanceDecision.from_decision(enriched, decision)
        try:
            self.metrics.record_routed(adapter_id, "ok")
            self.metrics.record_verdict(adapter_id, gov.verdict.value)
            self.metrics.observe_latency(adapter_id, time.perf_counter() - started)
        except Exception:  # noqa: BLE001
            pass
        return IngressResult(
            proposal_id=enriched.proposal_id, adapter_id=adapter_id,
            stages_completed=tuple(completed), decision=gov)

    # -- validation/normalization stages (never touch the gateway) ---------- #

    def _run_validation_stages(self, proposal: CanonicalProposal,
                               completed: List[IngressStage]) -> CanonicalProposal:
        # 1. schema validation.
        try:
            proposal.validate()
        except ProposalValidationError as exc:
            code = (ContractErrorCode.CONTRACT_FIELD_MISSING
                    if "missing" in exc.reason else ContractErrorCode.CONTRACT_FIELD_INVALID)
            raise IngressError(IngressStage.SCHEMA_VALIDATION, code, exc.reason) from exc
        completed.append(IngressStage.SCHEMA_VALIDATION)

        # 2. protocol validation — the proposal must declare a protocol version and
        #    must not already be expired.
        if not proposal.contract_version:
            raise IngressError(IngressStage.PROTOCOL_VALIDATION,
                               ContractErrorCode.CONTRACT_FIELD_MISSING,
                               "proposal declares no contract_version")
        if proposal.is_expired():
            raise IngressError(IngressStage.PROTOCOL_VALIDATION,
                               ContractErrorCode.CONTRACT_FIELD_INVALID,
                               "proposal is already expired at ingress")
        completed.append(IngressStage.PROTOCOL_VALIDATION)

        # 3. version negotiation — reuse the PR #43 rule; unsupported fails closed.
        compat = negotiate(proposal.contract_version)
        if not compat.compatible:
            raise IngressError(IngressStage.VERSION_NEGOTIATION,
                               compat.error_code or ContractErrorCode.CONTRACT_VERSION_UNSUPPORTED,
                               compat.reason)
        completed.append(IngressStage.VERSION_NEGOTIATION)

        # 4. adapter registry lookup.
        descriptor = None
        if self.registry.is_registered(proposal.adapter_id):
            descriptor = self.registry.get(proposal.adapter_id)
            if not descriptor.supports_version(proposal.contract_version):
                raise IngressError(
                    IngressStage.ADAPTER_REGISTRY_LOOKUP,
                    ContractErrorCode.CONTRACT_VERSION_UNSUPPORTED,
                    f"adapter {proposal.adapter_id!r} does not support protocol "
                    f"version {proposal.contract_version!r}")
        elif self._require_registered_adapter:
            raise IngressError(
                IngressStage.ADAPTER_REGISTRY_LOOKUP,
                ContractErrorCode.CONTRACT_FIELD_INVALID,
                f"adapter {proposal.adapter_id!r} is not registered")
        completed.append(IngressStage.ADAPTER_REGISTRY_LOOKUP)

        # 5. capability validation — any capabilities the proposal *requires* (via
        #    policy_context.required_capabilities) must be declared by the adapter.
        required = proposal.policy_context.get("required_capabilities") or []
        if required:
            if not isinstance(required, (list, tuple)):
                raise IngressError(IngressStage.CAPABILITY_VALIDATION,
                                   ContractErrorCode.CONTRACT_FIELD_INVALID,
                                   "required_capabilities must be a list")
            declared = set(descriptor.capabilities) if descriptor else set()
            missing = [c for c in required if c not in declared]
            if missing:
                raise IngressError(
                    IngressStage.CAPABILITY_VALIDATION,
                    ContractErrorCode.CONTRACT_FIELD_INVALID,
                    f"adapter does not declare required capabilities {missing}")
        completed.append(IngressStage.CAPABILITY_VALIDATION)

        # 6. metadata enrichment — attach standardized, non-authorizing ingress
        #    metadata. Only metadata changes; action/payload/hash are untouched.
        enriched = self._enrich(proposal, descriptor)
        completed.append(IngressStage.METADATA_ENRICHMENT)

        # 7. policy context resolution — normalize/resolve context the Gateway will
        #    use. This never evaluates policy or authorizes.
        enriched = self._resolve_context(enriched)
        completed.append(IngressStage.POLICY_CONTEXT_RESOLUTION)

        return enriched

    def _enrich(self, proposal: CanonicalProposal, descriptor) -> CanonicalProposal:
        ingress_meta = {
            "ingress_protocol_version": PROTOCOL_VERSION,
            "ingress_received_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
            "ingress_adapter_id": proposal.adapter_id,
            "ingress_framework": proposal.framework,
            "ingress_trace_id": proposal.trace_id,
            "ingress_correlation_id": proposal.correlation_id,
        }
        if descriptor is not None:
            ingress_meta["ingress_adapter_registered"] = True
            ingress_meta["ingress_adapter_version"] = descriptor.adapter_version
        else:
            ingress_meta["ingress_adapter_registered"] = False
        merged = dict(proposal.metadata)
        merged.setdefault("ingress", {})
        merged["ingress"] = {**merged.get("ingress", {}), **ingress_meta}
        return replace(proposal, metadata=merged)

    def _resolve_context(self, proposal: CanonicalProposal) -> CanonicalProposal:
        base = dict(proposal.policy_context)
        base.setdefault("protocol_version", proposal.contract_version)
        base["policy_context_resolved"] = True
        if self._resolve_policy_context is not None:
            extra = self._resolve_policy_context(proposal)
            if isinstance(extra, dict):
                base.update(extra)
        return replace(proposal, policy_context=base)

    def _record_failure(self, adapter_id: str, err: IngressError) -> None:
        try:
            self.metrics.record_failure(adapter_id, err.stage, err.code.value)
        except Exception:  # noqa: BLE001
            pass


__all__ = ["CanonicalIngressPipeline", "IngressResult", "Router", "PolicyContextResolver"]
