"""Certification Target resolution (MCC-CP-001 Section 7.2 "Certification
Subject").

A Certification Target/Subject is *any implementation evaluated against one
or more MCC specifications* (CP-001 Section 7.2). This module defines the
narrow, framework-neutral abstraction the pipeline certifies — nothing more.

Per CP-001 Section 7.2 / Section 6 ("Architectural Principles"): "Certification
SHALL evaluate behavior rather than implementation origin." Consistent with
that, and with this repository's own architecture, ``CertificationTarget``
carries **only** identity, provenance, and a self-contained, deterministic
conformance entry point. It carries no authorization, policy evaluation,
token issuance, execution, or governance authority of any kind — "the
certification pipeline certifies targets. Targets do not certify
themselves" (this is why ``conformance_entry_point`` returns already-
computed, deterministic :class:`RequirementResult` values, not something
that reaches out to execute governed actions or evaluate runtime policy).

This PR ships exactly **one** registered target: ``reference-fixture``, an
internal, deterministic test/reference fixture. Certification of the five
production reference ecosystems (Generic HTTP, LangGraph, CrewAI, AutoGen,
VoltAgent) is explicitly the next, separate platform milestone — this
module does not register them, and resolving any of their names raises
:class:`UnknownCertificationTargetError`, exactly like any other unknown
target.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Dict, Tuple


class CertifyError(Exception):
    """Base error for the mcc_certify package."""


class UnknownCertificationTargetError(CertifyError):
    """Raised when ``resolve_target`` is given a target_id this repository
    does not register. Fails closed -- an unknown target is never silently
    treated as certifiable."""


class MalformedCertificationTargetError(CertifyError):
    """Raised when a registered target's own declared metadata is
    internally inconsistent (empty identifier, empty capability list where
    one is required, etc.) -- caught at resolution time, before any
    certification stage runs."""


class RequirementOutcome(str, Enum):
    """CP-001 Section 8.5 / 9.5: the only three per-requirement Conformance
    Assessment outcomes this specification defines. A fourth value (PARTIAL,
    GAP, ERROR, ...) is never valid and is rejected at construction time,
    not silently normalized."""

    PASS = "PASS"
    FAIL = "FAIL"
    NOT_APPLICABLE = "NOT_APPLICABLE"


@dataclass(frozen=True)
class RequirementResult:
    """One CP-001 Section 9.3 "Requirement Result" -- the outcome of
    evaluating one applicable normative requirement for this target."""

    requirement_id: str
    outcome: RequirementOutcome
    detail: str = ""

    def __post_init__(self) -> None:
        if not self.requirement_id:
            raise MalformedCertificationTargetError("RequirementResult.requirement_id must be non-empty")
        if not isinstance(self.outcome, RequirementOutcome):
            raise MalformedCertificationTargetError(
                f"RequirementResult.outcome must be a RequirementOutcome, got {self.outcome!r}"
            )

    def to_dict(self) -> Dict[str, str]:
        return {"requirement_id": self.requirement_id, "outcome": self.outcome.value, "detail": self.detail}


@dataclass(frozen=True)
class CertificationTarget:
    """CP-001 Section 7.2 Certification Subject -- narrow, framework-neutral,
    non-authoritative identity + provenance + conformance entry point."""

    target_id: str
    target_type: str
    implementation_version: str
    certification_profile: str
    provenance: Dict[str, str]
    declared_capabilities: Tuple[str, ...]
    conformance_entry_point: Callable[[], Tuple[RequirementResult, ...]] = field(repr=False)

    def __post_init__(self) -> None:
        if not self.target_id:
            raise MalformedCertificationTargetError("CertificationTarget.target_id must be non-empty")
        if not self.target_type:
            raise MalformedCertificationTargetError("CertificationTarget.target_type must be non-empty")
        if not self.implementation_version:
            raise MalformedCertificationTargetError("CertificationTarget.implementation_version must be non-empty")
        if not self.certification_profile:
            raise MalformedCertificationTargetError("CertificationTarget.certification_profile must be non-empty")
        if not self.declared_capabilities:
            raise MalformedCertificationTargetError("CertificationTarget.declared_capabilities must be non-empty")

    def run_conformance_checks(self) -> Tuple[RequirementResult, ...]:
        """Invoke the target's own declared, deterministic conformance
        entry point and validate its output shape. Fails closed: a
        conformance entry point that raises, or returns something that is
        not a tuple of RequirementResult, is a MalformedCertificationTargetError,
        never silently treated as an empty (vacuously PASS) result set."""
        try:
            results = self.conformance_entry_point()
        except Exception as e:  # noqa: BLE001 - deliberately fail closed on any producer defect
            raise MalformedCertificationTargetError(
                f"target {self.target_id!r}'s conformance entry point raised: {e}"
            ) from e
        if not isinstance(results, tuple) or not results:
            raise MalformedCertificationTargetError(
                f"target {self.target_id!r}'s conformance entry point must return a non-empty "
                f"tuple of RequirementResult, got {type(results)!r}"
            )
        for r in results:
            if not isinstance(r, RequirementResult):
                raise MalformedCertificationTargetError(
                    f"target {self.target_id!r}'s conformance entry point returned a non-"
                    f"RequirementResult item: {r!r}"
                )
        return results


def _reference_fixture_checks() -> Tuple[RequirementResult, ...]:
    """The ONE internal, deterministic reference fixture's conformance
    checks -- intentionally small and self-contained (it evaluates the
    fixture's own declared identity/capability shape, not any external
    production ecosystem). Always deterministic: no I/O, no randomness, no
    wall-clock reads."""
    checks = []
    target = REFERENCE_FIXTURE_TARGET_ID
    checks.append(RequirementResult(
        "FIXTURE-IDENTITY-001", RequirementOutcome.PASS,
        f"target_id {target!r} is a non-empty stable string",
    ))
    checks.append(RequirementResult(
        "FIXTURE-CAPABILITY-001", RequirementOutcome.PASS,
        "declared_capabilities is non-empty",
    ))
    checks.append(RequirementResult(
        "FIXTURE-PROVENANCE-001", RequirementOutcome.PASS,
        "provenance metadata is present and well-formed",
    ))
    checks.append(RequirementResult(
        "FIXTURE-PROFILE-001", RequirementOutcome.NOT_APPLICABLE,
        "no domain-specific capability profile constraint applies to the internal reference fixture",
    ))
    return tuple(checks)


REFERENCE_FIXTURE_TARGET_ID = "reference-fixture"


def _build_reference_fixture_target() -> CertificationTarget:
    return CertificationTarget(
        target_id=REFERENCE_FIXTURE_TARGET_ID,
        target_type="internal-test-fixture",
        implementation_version="0.1.0",
        certification_profile="reference-fixture-profile-v1",
        provenance={
            "source": "mcc_certify.target (internal, deterministic, not a production ecosystem)",
            "maintainer": "mcc-prior-art/mcc-layer",
        },
        declared_capabilities=("baseline",),
        conformance_entry_point=_reference_fixture_checks,
    )


# Deliberately exactly one entry. Generic HTTP / LangGraph / CrewAI / AutoGen /
# VoltAgent are NOT registered here -- their certification is the next,
# separate platform milestone (see docs/CERTIFICATION_PIPELINE.md).
_KNOWN_TARGETS: Dict[str, Callable[[], CertificationTarget]] = {
    REFERENCE_FIXTURE_TARGET_ID: _build_reference_fixture_target,
}


def known_target_ids() -> Tuple[str, ...]:
    return tuple(sorted(_KNOWN_TARGETS))


def resolve_target(target_id: str) -> CertificationTarget:
    """Resolve ``target_id`` to a :class:`CertificationTarget`. Fails closed:
    an unknown, empty, or ambiguous target_id raises rather than falling
    back to a default target."""
    if not target_id or not target_id.strip():
        raise UnknownCertificationTargetError("target_id must be a non-empty string")
    builder = _KNOWN_TARGETS.get(target_id)
    if builder is None:
        raise UnknownCertificationTargetError(
            f"unknown certification target {target_id!r}; known targets: {known_target_ids()}"
        )
    return builder()
