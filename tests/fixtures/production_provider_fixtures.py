"""Importable fixtures for tests/test_attester_provider_loader.py.

Live at a real, importable dotted path (``tests.fixtures.production_provider_fixtures``)
so they can be named by ``MCC_ATTESTER_PROVIDER_CLASS`` exactly the way a
genuine operator-supplied provider would be -- these are not mocks of the
loader's own internals, they are ordinary Python classes the loader knows
nothing about in advance.
"""

from __future__ import annotations

from typing import Any, Mapping, Optional

from mcc_attester_service.provider import AssessmentProvider, AssessmentResult


class FakeProductionProvider(AssessmentProvider):
    """A well-behaved, trivial stand-in for a real operator-supplied
    production provider: a genuine AssessmentProvider subclass, no
    constructor arguments, deterministic output. Good enough to prove the
    loader accepts a legitimate class -- not a claim that this is fit for
    any real production use."""

    async def assess(
        self, *, action: str, resource: Optional[str], payload: Mapping[str, Any],
    ) -> AssessmentResult:
        return AssessmentResult(evidence_type="fixture", claims={"ok": True})


class NotAProvider:
    """Deliberately NOT an AssessmentProvider subclass."""


class RaisingConstructorProvider(AssessmentProvider):
    """Raises during construction -- the loader must fail closed rather
    than propagate a half-built provider."""

    def __init__(self) -> None:
        raise RuntimeError("fixture: construction deliberately fails")

    async def assess(
        self, *, action: str, resource: Optional[str], payload: Mapping[str, Any],
    ) -> AssessmentResult:  # pragma: no cover - never reached
        raise NotImplementedError


NOT_A_CLASS = object()
