"""Production AssessmentProvider selection boundary (Production Trust
Hardening Phase 1, Workstream 2).

The Attester service's own reference entrypoint (``__main__.py``) wires the
``DeterministicTestProvider`` — a reference/test harness, explicitly
documented as never a production assessment source (see
``provider.py``'s own docstring). This module is the one, explicit place
that decides *which* provider an Attester process may start with, per
``mcc_core.deployment_mode``:

    MCC_DEPLOYMENT_MODE=reference (default)
        -> the existing behavior, unchanged: load a DeterministicTestProvider
           from MCC_ATTESTER_TEST_ASSESSMENT_TABLE.

    MCC_DEPLOYMENT_MODE=enforcement
        -> DeterministicTestProvider is refused outright, even if a test
           assessment table is configured (that combination is itself a
           startup error -- a mix of "production posture" and "test
           provider config" is exactly the misconfiguration this module
           exists to catch, not to silently resolve). A trusted, concrete
           :class:`~mcc_attester_service.provider.AssessmentProvider`
           implementation must instead be named by
           MCC_ATTESTER_PROVIDER_CLASS as a dotted import path
           ("package.module:ClassName" or "package.module.ClassName"),
           importable, a subclass of AssessmentProvider, and NOT
           DeterministicTestProvider itself. It is instantiated with no
           constructor arguments -- the operator's class is responsible for
           obtaining whatever configuration/credentials it needs (e.g. from
           its own environment variables), entirely outside this module and
           outside mcc_core; this module never reaches into that provider's
           internals and never grants it access to signing material.

This module does not implement, ship, or endorse a concrete production
provider (an LLM, an ML classifier, a policy engine, ...) -- see PR-4's own
non-goals, reaffirmed by Phase 1's task scope. It implements only the
configuration/trust boundary: fail closed if no trustworthy provider is
named, fail closed if the named class cannot be loaded or is not a real
AssessmentProvider, and refuse the reference test double outright.
"""

from __future__ import annotations

import importlib
import os
from typing import Mapping, Optional

from .errors import AttesterServiceConfigError
from .provider import AssessmentProvider, AssessmentResult, DeterministicTestProvider


def _load_test_provider(env: Mapping[str, str]) -> DeterministicTestProvider:
    """Reference-mode provider loading — unchanged from the pre-Phase-1
    behavior of ``__main__.py``'s own ``_load_test_provider``."""
    import json

    table_path = env.get("MCC_ATTESTER_TEST_ASSESSMENT_TABLE", "").strip()
    if not table_path:
        raise AttesterServiceConfigError(
            "MCC_ATTESTER_TEST_ASSESSMENT_TABLE is required in reference mode "
            "(MCC_DEPLOYMENT_MODE=reference, the default) -- it wires the "
            "DeterministicTestProvider ONLY; a production/enforcement "
            "deployment must set MCC_DEPLOYMENT_MODE=enforcement and "
            "MCC_ATTESTER_PROVIDER_CLASS instead"
        )
    with open(table_path, "r", encoding="utf-8") as fh:
        raw = json.load(fh)
    if not isinstance(raw, dict):
        raise AttesterServiceConfigError(
            f"{table_path!r} must contain a JSON object mapping action patterns "
            f"to assessment entries"
        )
    table = {}
    for pattern, item in raw.items():
        table[pattern] = AssessmentResult(
            evidence_type=item["evidence_type"],
            claims=item.get("claims", {}),
            provenance=item.get("provenance", {}),
        )
    return DeterministicTestProvider(table)


def _import_dotted(path: str) -> object:
    """Import ``path`` as either ``module:Attr`` or ``module.Attr``. Raises
    on any failure -- never returns a partial or best-guess result."""
    if ":" in path:
        module_name, _, attr = path.partition(":")
    else:
        module_name, _, attr = path.rpartition(".")
    if not module_name or not attr:
        raise AttesterServiceConfigError(
            f"MCC_ATTESTER_PROVIDER_CLASS={path!r} is not a valid dotted path "
            f"(expected 'package.module:ClassName' or 'package.module.ClassName')"
        )
    try:
        module = importlib.import_module(module_name)
    except Exception as exc:  # noqa: BLE001 -- any import failure is fail-closed config error
        raise AttesterServiceConfigError(
            f"could not import module {module_name!r} for "
            f"MCC_ATTESTER_PROVIDER_CLASS={path!r}: {exc!r}"
        ) from exc
    try:
        return getattr(module, attr)
    except AttributeError as exc:
        raise AttesterServiceConfigError(
            f"module {module_name!r} has no attribute {attr!r} for "
            f"MCC_ATTESTER_PROVIDER_CLASS={path!r}"
        ) from exc


def _load_production_provider(env: Mapping[str, str]) -> AssessmentProvider:
    """Enforcement-mode provider loading. Fails closed on every ambiguous
    or untrustworthy configuration -- see module docstring for the full
    list of refused conditions."""
    if env.get("MCC_ATTESTER_TEST_ASSESSMENT_TABLE", "").strip():
        raise AttesterServiceConfigError(
            "MCC_DEPLOYMENT_MODE=enforcement refuses "
            "MCC_ATTESTER_TEST_ASSESSMENT_TABLE -- a test assessment table has "
            "no place in a production/enforcement configuration; remove it or "
            "run this process with MCC_DEPLOYMENT_MODE=reference instead"
        )

    dotted_path = env.get("MCC_ATTESTER_PROVIDER_CLASS", "").strip()
    if not dotted_path:
        raise AttesterServiceConfigError(
            "MCC_DEPLOYMENT_MODE=enforcement requires MCC_ATTESTER_PROVIDER_CLASS "
            "-- a dotted import path to the operator's own trusted "
            "AssessmentProvider implementation. This service ships no "
            "concrete production provider (no LLM, no ML classifier, no "
            "policy engine); the operator/application embedding MCC-Core "
            "must supply one."
        )

    candidate = _import_dotted(dotted_path)

    if not isinstance(candidate, type) or not issubclass(candidate, AssessmentProvider):
        raise AttesterServiceConfigError(
            f"MCC_ATTESTER_PROVIDER_CLASS={dotted_path!r} does not resolve to a "
            f"subclass of mcc_attester_service.provider.AssessmentProvider "
            f"(got {candidate!r})"
        )

    if issubclass(candidate, DeterministicTestProvider):
        raise AttesterServiceConfigError(
            f"MCC_ATTESTER_PROVIDER_CLASS={dotted_path!r} resolves to "
            f"DeterministicTestProvider (or a subclass of it) -- this is a "
            f"reference/test-only provider and is explicitly refused as a "
            f"production/enforcement assessment source"
        )

    try:
        provider = candidate()
    except Exception as exc:  # noqa: BLE001 -- construction failure is fail-closed config error
        raise AttesterServiceConfigError(
            f"MCC_ATTESTER_PROVIDER_CLASS={dotted_path!r} raised while "
            f"constructing with no arguments: {exc!r}"
        ) from exc

    if not isinstance(provider, AssessmentProvider):
        raise AttesterServiceConfigError(
            f"MCC_ATTESTER_PROVIDER_CLASS={dotted_path!r} constructed an "
            f"instance that is not an AssessmentProvider (got {provider!r})"
        )
    return provider


def assessment_provider_from_env(env: Optional[Mapping[str, str]] = None) -> AssessmentProvider:
    """Select the Attester's AssessmentProvider per ``MCC_DEPLOYMENT_MODE``.

    * ``reference`` (default) — unchanged reference behavior: a
      ``DeterministicTestProvider`` built from
      ``MCC_ATTESTER_TEST_ASSESSMENT_TABLE``.
    * ``enforcement`` — refuses ``DeterministicTestProvider`` outright and
      requires an operator-supplied, importable ``AssessmentProvider``
      subclass named by ``MCC_ATTESTER_PROVIDER_CLASS``.

    Fails closed (``AttesterServiceConfigError``) on every missing or
    untrustworthy configuration; never falls back to the test provider from
    an enforcement configuration, and never invents a permissive default.
    """
    from mcc_core.deployment_mode import is_enforcement_mode

    env = os.environ if env is None else env
    if is_enforcement_mode(env):
        return _load_production_provider(env)
    return _load_test_provider(env)


__all__ = ["assessment_provider_from_env"]
