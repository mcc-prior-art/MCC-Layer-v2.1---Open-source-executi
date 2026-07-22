"""MCC-Core Adapter SDK (PR #50) — build MCC-Core adapters, framework-neutrally.

A small, stable, public façade over the Canonical Governance Protocol (PR #49). It
lets third-party developers build adapters that translate a framework-native request
into the authoritative :class:`mcc_protocol.CanonicalProposal`, submit it through the
one mandatory :class:`mcc_protocol.CanonicalIngressPipeline`, and translate the
returned :class:`mcc_protocol.GovernanceDecision` back into a native response —
**without** importing or depending on the gateway, execution gate, authority, policy
engine, audit chain, runtime executor, or private signing internals.

    Framework proposes. Adapter translates. CanonicalProposal is produced.
    CanonicalIngressPipeline executes. GovernanceDecision is returned. The Execution
    Gate enforces. The audit chain records.

An adapter never authorizes, executes, evaluates policy, or signs authority. The SDK
reuses the authoritative models (Verdict, Decision, GovernanceDecision, CanonicalProposal,
AdapterRegistry, ContractErrorCode, the capability vocabulary, and the single
version-compatibility rule) and defines no parallel decision/proposal/verdict model.
"""

from __future__ import annotations

from ._version import SDK_VERSION
from .adapter import Adapter
from .context import AdapterContext
from .errors import AdapterSDKError
from .evidence import generate_adapter_evidence
from .metadata import AdapterMetadata
from .registration import AdapterRegistration, register_adapter
from .runner import AdapterRunner, AdapterRunResult, Router
from .validation import AdapterValidationReport, validate_adapter

__all__ = [
    "SDK_VERSION",
    "Adapter",
    "AdapterMetadata",
    "AdapterContext",
    "AdapterRunner",
    "AdapterRunResult",
    "AdapterRegistration",
    "AdapterValidationReport",
    "AdapterSDKError",
    "Router",
    "register_adapter",
    "validate_adapter",
    "generate_adapter_evidence",
]
