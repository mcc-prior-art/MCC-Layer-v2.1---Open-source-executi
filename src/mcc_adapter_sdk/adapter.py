"""The public Adapter interface (PR #50).

An adapter is **purely translational**: it turns a framework-native request into
the authoritative :class:`mcc_protocol.CanonicalProposal`, and turns the returned
:class:`mcc_protocol.GovernanceDecision` back into a framework-native response. It
never authorizes, allows, approves, executes, enforces, evaluates policy, issues
tokens, or signs — those verbs are owned by the governance runtime, reached only
through the mandatory Canonical Ingress Pipeline (via :class:`AdapterRunner`).

Subclass :class:`Adapter` and implement three methods: :meth:`describe`,
:meth:`to_proposal`, and :meth:`to_response`. Use :meth:`make_proposal` to build a
well-formed proposal bound to the adapter's identity and the request context.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from mcc_protocol import CanonicalProposal, GovernanceDecision

from .context import AdapterContext
from .errors import AdapterSDKError
from .metadata import AdapterMetadata


class Adapter(ABC):
    """A framework-neutral, translational MCC-Core adapter."""

    @abstractmethod
    def describe(self) -> AdapterMetadata:
        """Return this adapter's immutable :class:`AdapterMetadata`."""

    @abstractmethod
    def to_proposal(self, context: AdapterContext, native_request: Any) -> CanonicalProposal:
        """Translate a framework-native request into a :class:`CanonicalProposal`.
        Implementations should build it with :meth:`make_proposal`. This method
        must not authorize, execute, or sign — it only translates."""

    @abstractmethod
    def to_response(self, decision: GovernanceDecision) -> Any:
        """Translate a :class:`GovernanceDecision` into a framework-native response.
        Read-only with respect to the decision; it must not re-decide or execute."""

    def sample_request(self) -> Any:
        """A representative native request used by structural validation and
        deterministic evidence. Optional — override to enable those checks."""
        raise AdapterSDKError("adapter provides no sample_request()")

    # -- construction helper (not overridable behavior; pure translation) ---- #

    def make_proposal(self, context: AdapterContext, *, action: str, resource: str,
                      payload: Dict[str, Any], requested_scope: Optional[str] = None,
                      risk_context: Optional[Dict[str, Any]] = None,
                      policy_context: Optional[Dict[str, Any]] = None,
                      metadata: Optional[Dict[str, Any]] = None) -> CanonicalProposal:
        """Build a well-formed :class:`CanonicalProposal` bound to this adapter's
        identity and the request context. Fail-closed on invalid input; never
        authorizes."""
        md = self.describe().validate()
        try:
            return CanonicalProposal.create(
                adapter_id=md.adapter_id, adapter_version=md.adapter_version,
                framework=md.framework_name, framework_version=md.framework_version,
                actor=context.actor_reference, action=action, resource=resource,
                payload=payload, requested_scope=requested_scope,
                principal=context.actor_reference,
                correlation_id=context.correlation_id, trace_id=context.trace_id,
                risk_context=risk_context, policy_context=policy_context,
                metadata=metadata, contract_version=md.contract_version)
        except Exception as exc:  # noqa: BLE001 — malformed translation fails closed
            raise AdapterSDKError(f"could not build canonical proposal: {exc}") from exc


__all__ = ["Adapter"]
