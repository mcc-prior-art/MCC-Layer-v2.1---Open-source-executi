"""AdapterRunner — the thin façade that drives the mandatory ingress path (PR #50).

    native request → CanonicalProposal → CanonicalIngressPipeline → GovernanceDecision
    → native response

The runner submits **exclusively** through :class:`mcc_protocol.CanonicalIngressPipeline`
— there is no alternate authorization or gateway shortcut. It preserves the existing
Decision, Decision Token, and Verdict semantics (it only wraps them via
``GovernanceDecision``) and never authorizes, executes, or enforces. Every failure is
fail-closed: a translation error, a pipeline rejection, or a response-translation
error yields a non-``ok`` result with **no** native response.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Optional

from mcc_protocol import (
    AdapterRegistry,
    CanonicalIngressPipeline,
    CanonicalProposal,
    Decision,
    GovernanceDecision,
    IngressResult,
)
from mcc_protocol.pipeline import PolicyContextResolver

from .adapter import Adapter
from .metadata import AdapterMetadata
from .registration import _descriptor

#: A router submits a validated proposal to the authoritative gateway and returns
#: the canonical Decision. In production this wraps ``mcc_client.MCCClient.evaluate``.
Router = Callable[[CanonicalProposal], Decision]


@dataclass(frozen=True)
class AdapterRunResult:
    """The outcome of one native request driven through governance."""

    adapter_metadata: AdapterMetadata
    ok: bool
    proposal_id: Optional[str] = None
    proposal_hash: Optional[str] = None
    governance_decision: Optional[GovernanceDecision] = None
    native_response: Any = None
    pipeline_summary: Dict[str, Any] = field(default_factory=dict)
    observability: Dict[str, Any] = field(default_factory=dict)
    evidence_reference: Optional[str] = None
    error: Optional[Dict[str, Any]] = None

    @property
    def verdict(self) -> Optional[str]:
        return self.governance_decision.verdict.value if self.governance_decision else None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "adapter": self.adapter_metadata.adapter_id,
            "ok": self.ok,
            "proposal_id": self.proposal_id,
            "proposal_hash": self.proposal_hash,
            "verdict": self.verdict,
            "governance_decision": (self.governance_decision.to_dict()
                                    if self.governance_decision else None),
            "pipeline_summary": dict(self.pipeline_summary),
            "observability": dict(self.observability),
            "evidence_reference": self.evidence_reference,
            "error": self.error,
        }


class AdapterRunner:
    """Drives an adapter's native request through the one mandatory ingress path."""

    def __init__(self, adapter: Adapter, router: Router, *,
                 registry: Optional[AdapterRegistry] = None,
                 policy_context_resolver: Optional[PolicyContextResolver] = None) -> None:
        self._adapter = adapter
        self._metadata = adapter.describe().validate()
        self._registry = registry if registry is not None else AdapterRegistry()
        # Ensure the adapter is known to the pipeline's registry (informational).
        self._registry.register(_descriptor(self._metadata))
        # The ONE mandatory pipeline. The router is the only path to the gateway.
        self._pipeline = CanonicalIngressPipeline(
            self._registry, router, policy_context_resolver=policy_context_resolver)

    @property
    def metadata(self) -> AdapterMetadata:
        return self._metadata

    def run(self, context, native_request: Any) -> AdapterRunResult:
        """native → proposal → pipeline → decision → native, fail-closed throughout."""
        # 1. Translate (adapter). A translation failure fails closed.
        try:
            proposal = self._adapter.to_proposal(context, native_request)
        except Exception as exc:  # noqa: BLE001
            return self._failed(error={"stage": "to_proposal",
                                       "error": f"{type(exc).__name__}: {exc}"})
        if not isinstance(proposal, CanonicalProposal):
            return self._failed(error={"stage": "to_proposal",
                                       "error": "adapter did not return a CanonicalProposal"})

        # 2. Submit ONLY through the mandatory pipeline (no bypass).
        result: IngressResult = self._pipeline.process(proposal)
        summary = {"stages_completed": [s.value for s in result.stages_completed],
                   "ok": result.ok}
        if not result.ok:
            # Pipeline rejection prevents any successful response (fail-closed).
            return self._failed(proposal=proposal, pipeline_summary=summary,
                                error=(result.error.to_dict() if result.error else
                                       {"stage": "pipeline", "error": "rejected"}))

        decision = result.decision
        # 3. Translate the decision back to native (adapter). Failure fails closed —
        #    the governance decision stands, but no native response is produced.
        try:
            native = self._adapter.to_response(decision)
        except Exception as exc:  # noqa: BLE001
            return self._failed(proposal=proposal, pipeline_summary=summary,
                                error={"stage": "to_response",
                                       "error": f"{type(exc).__name__}: {exc}"})

        return AdapterRunResult(
            adapter_metadata=self._metadata, ok=True,
            proposal_id=proposal.proposal_id, proposal_hash=proposal.action_hash,
            governance_decision=decision, native_response=native,
            pipeline_summary=summary,
            observability={"verdict": decision.verdict.value,
                           "executable": decision.executable,
                           "has_decision_token": decision.has_decision_token})

    def _failed(self, *, proposal: Optional[CanonicalProposal] = None,
                pipeline_summary: Optional[Dict[str, Any]] = None,
                error: Optional[Dict[str, Any]] = None) -> AdapterRunResult:
        return AdapterRunResult(
            adapter_metadata=self._metadata, ok=False,
            proposal_id=getattr(proposal, "proposal_id", None),
            proposal_hash=getattr(proposal, "action_hash", None),
            governance_decision=None, native_response=None,
            pipeline_summary=pipeline_summary or {}, error=error)


__all__ = ["AdapterRunner", "AdapterRunResult", "Router"]
