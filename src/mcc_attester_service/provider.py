"""AssessmentProvider — the narrow boundary between "what produced the
assessment" and the Attester service's own cryptographic/binding/identity
responsibilities (PR-4, MCC-AT-004).

    proposal/action/payload
            ->
    AssessmentProvider
            ->
    Attester service constructs the trusted EvidenceAttestation
            ->
    Attester signs

A provider supplies ONLY the assessment-specific content it owns:
``evidence_type``, ``claims``, ``provenance`` -- exactly the fields
MCC-AT-001's :class:`~mcc_attestation.schema.EvidenceAttestation` already
defines as the assessment payload. It has no access to, and no say over,
signing, identity (``attester_id``/``kid``), ``attestation_id``, ``nonce``,
the validity window, or the action/payload/scope binding -- those remain
entirely the Attester service's own responsibility (see ``service.py``),
never delegated to or influenced by whatever produced the assessment.

This module deliberately does NOT integrate an LLM, an ML risk engine, a
payment-specific model, or a general policy language -- see PR-4's
non-goals. It defines only the interface shape and one deterministic,
explicitly test-only reference implementation. A real deployment supplies
its own :class:`AssessmentProvider` wired to whatever real assessment
source it trusts; this package neither ships nor endorses one.
"""

from __future__ import annotations

import fnmatch
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, Mapping, Optional

from .errors import AssessmentProviderError


@dataclass(frozen=True)
class AssessmentResult:
    """The assessment-specific content an :class:`AssessmentProvider`
    returns -- and the ONLY content it controls. Everything else in the
    eventual signed :class:`~mcc_attestation.schema.EvidenceAttestation`
    (identity, binding, nonce, validity window, signature) is added by the
    Attester service itself, never by the provider.
    """

    evidence_type: str
    claims: Mapping[str, Any]
    provenance: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.evidence_type or not isinstance(self.evidence_type, str):
            raise AssessmentProviderError(
                "AssessmentResult.evidence_type must be a non-empty string"
            )
        if not isinstance(self.claims, Mapping):
            raise AssessmentProviderError("AssessmentResult.claims must be a mapping")
        if not isinstance(self.provenance, Mapping):
            raise AssessmentProviderError("AssessmentResult.provenance must be a mapping")


class AssessmentProvider(ABC):
    """The interface every assessment source must implement to back the
    Attester service. Implementations may call out to whatever they like
    (a rule engine, a human review queue, a model -- this package takes no
    position), but must return only assessment content, never touch
    signing/identity/binding, and must raise on any failure rather than
    fabricate a result -- the service treats every exception raised here as
    a fail-closed provider failure (design rule 8), regardless of its
    concrete type.
    """

    @abstractmethod
    async def assess(
        self, *, action: str, resource: Optional[str], payload: Mapping[str, Any],
    ) -> AssessmentResult:
        """Produce an assessment for the described operation. ``action``,
        ``resource``, and ``payload`` describe ONLY what is being assessed
        -- never what to sign; the provider has no access to signing
        material and cannot influence identity, binding, or timing fields.
        Must raise (any exception) rather than return a best-effort or
        placeholder result when it cannot produce a real assessment.
        """
        raise NotImplementedError


class DeterministicTestProvider(AssessmentProvider):
    """Reference, deterministic provider for tests and local reference
    runs ONLY. Resolves ``action`` against a trusted, statically configured
    table of canned :class:`AssessmentResult` values (first matching
    ``fnmatch`` pattern wins, mirroring
    ``gateway.pre_execution_control.AttestationRequirementRegistry``'s
    resolution convention) and returns the same one every time for a given
    action pattern.

    Deliberately NOT a production default: an action with no configured
    entry raises :class:`AssessmentProviderError` -- fail closed -- rather
    than inventing an "always low risk" (or any other) assessment. There is
    no fallback branch here that fabricates content.
    """

    def __init__(self, table: Optional[Dict[str, AssessmentResult]] = None) -> None:
        self._table = dict(table or {})

    async def assess(
        self, *, action: str, resource: Optional[str], payload: Mapping[str, Any],
    ) -> AssessmentResult:
        for pattern, result in self._table.items():
            if fnmatch.fnmatchcase(action, pattern):
                return result
        raise AssessmentProviderError(
            f"DeterministicTestProvider has no configured assessment for action {action!r}; "
            "fail-closed (this provider never invents a result)"
        )


__all__ = ["AssessmentResult", "AssessmentProvider", "DeterministicTestProvider"]
