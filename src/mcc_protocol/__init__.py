"""MCC-Core Canonical Governance Protocol & Canonical Ingress Pipeline (PR #49).

This package promotes the proven interoperability pattern (PR #48) into the official,
reusable, framework-neutral platform layer:

* :class:`CanonicalProposal` — the one normative governance *request* every adapter
  produces (additive: the SDK previously had no first-class request type).
* :class:`GovernanceDecision` — the canonical *response* envelope that **wraps**
  (never replaces) the authoritative :class:`mcc_client.Decision` + Decision Token.
* :class:`CanonicalIngressPipeline` — the one mandatory in-process pipeline every
  proposal traverses before governance evaluation. It validates, normalizes,
  enriches, and routes into the *existing* MCC Gateway; it is not a second engine.
* :class:`AdapterRegistry` — informational adapter descriptors; grants no authority.

Reconciliation with PR #43 (no semantic drift)
----------------------------------------------
There is exactly **one** normative wire contract. This package does not introduce a
parallel model hierarchy: it reuses the Integration Contract's version rule
(:func:`mcc_client.contract.check_version_compatibility`), error taxonomy
(:class:`mcc_client.contract.ContractErrorCode`), canonical decision/verdict models
(:class:`mcc_client.Decision` / :class:`mcc_client.Verdict`), the single
capability vocabulary (PR #47), and the single canonicalization
(:mod:`mcc_core.signing`). ``PROTOCOL_VERSION`` *is* ``CONTRACT_VERSION``. Nothing
here authorizes, evaluates policy, signs, issues Decision Tokens, or runs the Gate.
"""

from __future__ import annotations

from mcc_client import Decision, Verdict
from mcc_client.contract import CONTRACT_VERSION, ContractErrorCode

from .decision import GovernanceDecision
from .errors import PIPELINE_STAGES, IngressError, IngressStage
from .pipeline import (
    CanonicalIngressPipeline,
    IngressResult,
    PolicyContextResolver,
    Router,
)
from .proposal import CanonicalProposal, ProposalValidationError, compute_action_hash
from .registry import AdapterDescriptor, AdapterRegistry, AdapterRegistryError
from .version import PROTOCOL_VERSION, negotiate

__all__ = [
    # protocol version (== contract version; single axis)
    "PROTOCOL_VERSION",
    "CONTRACT_VERSION",
    "negotiate",
    # request / response
    "CanonicalProposal",
    "ProposalValidationError",
    "compute_action_hash",
    "GovernanceDecision",
    # reused canonical models (re-exported for convenience, not redefined)
    "Decision",
    "Verdict",
    "ContractErrorCode",
    # pipeline
    "CanonicalIngressPipeline",
    "IngressResult",
    "IngressStage",
    "PIPELINE_STAGES",
    "IngressError",
    "Router",
    "PolicyContextResolver",
    # registry
    "AdapterRegistry",
    "AdapterDescriptor",
    "AdapterRegistryError",
]
