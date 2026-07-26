"""Production reference-ecosystem Certification Targets (PR #69).

Registers five real ``CertificationTarget``s -- ``generic-http``,
``langgraph``, ``crewai``, ``autogen``, ``voltagent`` -- as CP-001 Section
7.2 Certification Subjects. Each target's conformance entry point EXECUTES
the real, already-proven adapter integration built for the Multi-Adapter
Interoperability Proof (PR #48, ``tests/interoperability/``) through the
one shared governed MCC Gateway and the same seven common governance
scenarios every adapter in that proof already runs -- this module adds
**no** new adapter, rewrites **no** existing adapter, and creates **no**
second governance path. It is a thin translation layer: real
``AdapterEvidence``/``ScenarioResult`` objects (from
``tests.interoperability.harness.run_common_scenarios``) become
``mcc_certify.target.RequirementResult`` values the certification pipeline
already knows how to carry through Evidence Bundle -> Certification
Manifest -> Technical Certificate -> Publication -> Offline Verification,
completely unchanged.

Why ``tests.interoperability`` from ``src/mcc_certify``: the five real
ecosystem integrations exist in exactly one place in this repository
(``tests/interoperability/adapters/``), built and proven by PR #48. The
task governing this milestone explicitly forbids adding a new adapter or
redesigning an existing one; duplicating ~600 lines of adapter code into
``src/`` would itself be a prohibited "parallel adapter" and would
immediately drift from the adapters PR #48's own tests keep exercising.
Reusing them directly is the only option consistent with "one identical
certification process" and "no ecosystem may ... partially reimplement
the certification process". This is a deliberate, disclosed layering
choice: ``mcc_certify`` is not part of the curated ``mcc-core`` wheel (see
``pyproject.toml`` -- excluded exactly like ``mcc_conformance`` and
``mcc_evidence``), so this does not leak into anything distributed.

Every framework-specific import (``langgraph``, ``autogen_core``,
``crewai``, and the Node/VoltAgent subprocess bridge) happens **lazily**,
inside each target's ``conformance_entry_point`` closure -- never at this
module's top level. ``import mcc_certify`` therefore never requires any of
the five frameworks to be installed; only actually *running* one target's
conformance checks does. A missing framework fails closed with a clear,
specific error (``EcosystemDependencyUnavailableError``, a
``MalformedCertificationTargetError`` subtype) rather than a fake PASS,
consistent with CP-001 Section 7.2 (a Certification Subject is registered
/ identity-known independently of whether it currently evaluates
successfully) and this module's own design goal: a target is always
*known*; running it against a missing dependency is a *conformance run
failure*, not an unknown target.
"""

from __future__ import annotations

import platform
import sys
from typing import Any, Callable, Dict, Tuple

from mcc_core.signing import canonical_bytes, sha256_hex

from .target import (
    CertificationTarget,
    MalformedCertificationTargetError,
    RequirementOutcome,
    RequirementResult,
)

#: The Integration Contract / normative specification version these targets
#: are certified against -- reused, not reinvented (matches
#: ``pipeline.CP001_SPECIFICATION_VERSION`` and ``mcc_client.contract.CONTRACT_VERSION``).
NORMATIVE_SPECIFICATION_VERSION = "1.0"

#: The seven PR #48 common governance scenarios, mapped to stable, shared
#: requirement identifiers. The same identifier is reused across all five
#: targets -- it names the same governance invariant being verified; only
#: the Certification Subject differs per target (CP-001's own conformance
#: model: the same requirement, evaluated per Subject).
_SCENARIO_REQUIREMENT_IDS: Dict[str, str] = {
    "ALLOW": "ECO-GOV-ALLOW-001",
    "DENY": "ECO-GOV-DENY-001",
    "REPLAY": "ECO-GOV-REPLAY-001",
    "MISMATCH": "ECO-GOV-MISMATCH-001",
    "AUDIT": "ECO-GOV-AUDIT-001",
    "GATEWAY_UNAVAILABLE": "ECO-GOV-AVAILABILITY-001",
    "INVALID_OR_EXPIRED": "ECO-GOV-VALIDITY-001",
}

CAPABILITY_PROFILE_REQUIREMENT_ID = "ECO-CAP-PROFILE-001"
ESCALATE_REQUIREMENT_ID = "ECO-GOV-ESCALATE-001"
CONSTRAIN_REQUIREMENT_ID = "ECO-GOV-CONSTRAIN-001"
PROVENANCE_REQUIREMENT_ID = "ECO-PROVENANCE-001"


class EcosystemDependencyUnavailableError(MalformedCertificationTargetError):
    """The real ecosystem package/runtime this target requires is not
    importable/available in the current execution environment. Distinct
    from :class:`UnknownCertificationTargetError` -- the target IS
    registered and its identity is known; only *executing* its conformance
    checks requires the real dependency. Certification MUST fail closed
    here rather than substitute a stub or report a vacuous PASS."""


def _target_config_hash(config: Dict[str, Any]) -> str:
    """A stable digest binding a target's own declared configuration --
    used as the ``target_config_hash`` provenance field so tampering with,
    or substituting, a target's declared identity is independently
    detectable. Never derived from a filesystem path, PID, or random value."""
    return sha256_hex(canonical_bytes(config))


def _execution_environment_metadata() -> Dict[str, str]:
    return {
        "python_version": sys.version.split()[0],
        "platform": platform.platform(),
    }


def _run_ecosystem_conformance(
    adapter_factory: Callable[[], Any],
    *,
    import_dependency: Callable[[], None],
) -> Tuple[RequirementResult, ...]:
    """Shared conformance entry point body for all five ecosystem targets.

    1. Imports the real framework dependency (raises
       :class:`EcosystemDependencyUnavailableError` with a clear message if
       unavailable -- never silently substitutes a fake module).
    2. Boots one dedicated, isolated ``SharedGovernedGateway`` subprocess
       (PR #48's real out-of-process MCC Gateway; no Redis, no external
       service) for this single conformance run only, and tears it down
       unconditionally afterward.
    3. Builds the real adapter and runs the real, unmodified
       ``run_common_scenarios`` (PR #48) -- the SAME seven governance
       scenarios (ALLOW/DENY/REPLAY/MISMATCH/AUDIT/GATEWAY_UNAVAILABLE/
       INVALID_OR_EXPIRED) every adapter in the interoperability proof runs.
    4. Validates the adapter's own declared Governance Capability Profile
       via the existing, unmodified ``mcc_compliance.capability_profile.validate_profile``.
    5. Translates every real result into a :class:`RequirementResult` --
       this function fabricates none of them; a scenario that did not run
       or an unvalidated profile is FAIL, never silently PASS.
    """
    try:
        import_dependency()
    except ImportError as e:
        raise EcosystemDependencyUnavailableError(
            f"the real ecosystem dependency required by this target is not available "
            f"in the current execution environment: {e}. Certification of this target "
            f"requires installing the dependency this target declares (see its "
            f"documented requirements file) -- there is no substitute/stub path."
        ) from e

    from mcc_compliance.capability_profile import validate_profile
    from tests.interoperability.harness import SharedGovernedGateway, run_common_scenarios

    gw = SharedGovernedGateway()
    try:
        adapter = adapter_factory()
        evidence = run_common_scenarios(adapter, gw)
        profile = adapter.capability_profile()
    finally:
        gw.close()

    results = []
    seen_scenarios = set()
    for scenario_result in evidence.scenarios:
        requirement_id = _SCENARIO_REQUIREMENT_IDS.get(scenario_result.scenario)
        if requirement_id is None:
            raise MalformedCertificationTargetError(
                f"adapter evidence produced an unrecognized scenario {scenario_result.scenario!r}"
            )
        seen_scenarios.add(scenario_result.scenario)
        outcome = RequirementOutcome.PASS if scenario_result.status == "PASS" else RequirementOutcome.FAIL
        results.append(RequirementResult(
            requirement_id, outcome,
            detail=(
                f"scenario={scenario_result.scenario} verdict={scenario_result.verdict!r} "
                f"executed={scenario_result.executed} audit_chain_valid={scenario_result.audit_chain_valid} "
                f"detail={scenario_result.detail!r}"
            ),
        ))

    missing_scenarios = set(_SCENARIO_REQUIREMENT_IDS) - seen_scenarios
    if missing_scenarios:
        raise MalformedCertificationTargetError(
            f"adapter evidence is missing required scenario(s): {sorted(missing_scenarios)}"
        )

    profile_validation = validate_profile(profile)
    results.append(RequirementResult(
        CAPABILITY_PROFILE_REQUIREMENT_ID,
        RequirementOutcome.PASS if profile_validation.valid else RequirementOutcome.FAIL,
        detail=(
            "Governance Capability Profile is schema/semantically valid"
            if profile_validation.valid
            else f"Governance Capability Profile validation failed: {profile_validation.errors}"
        ),
    ))

    optional_capabilities = set(profile.get("optional_capabilities", []) or [])
    if "human_in_the_loop_escalation" in optional_capabilities:
        results.append(RequirementResult(
            ESCALATE_REQUIREMENT_ID, RequirementOutcome.FAIL,
            detail="adapter declares human_in_the_loop_escalation but the common scenario suite has no "
                   "ESCALATE scenario to verify it against -- an unverified capability claim MUST NOT pass",
        ))
    else:
        results.append(RequirementResult(
            ESCALATE_REQUIREMENT_ID, RequirementOutcome.NOT_APPLICABLE,
            detail="ESCALATE is not part of this adapter's currently declared capability profile "
                   "(CP-001 Section 11.6: unverified capability claims are never certified)",
        ))
    if "constraint_enforcement" in optional_capabilities:
        results.append(RequirementResult(
            CONSTRAIN_REQUIREMENT_ID, RequirementOutcome.FAIL,
            detail="adapter declares constraint_enforcement but the common scenario suite has no "
                   "CONSTRAIN scenario to verify it against -- an unverified capability claim MUST NOT pass",
        ))
    else:
        results.append(RequirementResult(
            CONSTRAIN_REQUIREMENT_ID, RequirementOutcome.NOT_APPLICABLE,
            detail="CONSTRAIN is not part of this adapter's currently declared capability profile "
                   "(CP-001 Section 11.6: unverified capability claims are never certified)",
        ))

    results.append(RequirementResult(
        PROVENANCE_REQUIREMENT_ID, RequirementOutcome.PASS,
        detail=f"framework_provenance recorded: {evidence.provenance}",
    ))

    return tuple(results)


def _build_target(
    *,
    target_id: str,
    target_type: str,
    ecosystem_name: str,
    ecosystem_package: str,
    adapter_module: str,
    adapter_version: str,
    native_api_entrypoint: str,
    implementation_version_lookup: Callable[[], str],
    adapter_factory: Callable[[], Any],
    import_dependency: Callable[[], None],
) -> CertificationTarget:
    """Shared builder for all five ecosystem targets -- identical shape,
    only identity/provenance/entry-point details differ per ecosystem."""

    def implementation_version() -> str:
        try:
            return implementation_version_lookup()
        except Exception:  # noqa: BLE001 - version lookup failure is provenance-only, not fatal
            return "unknown (dependency not installed in this environment)"

    resolved_implementation_version = implementation_version()

    provenance: Dict[str, str] = {
        "ecosystem_name": ecosystem_name,
        "ecosystem_package": ecosystem_package,
        "ecosystem_version": resolved_implementation_version,
        "adapter_module": adapter_module,
        "adapter_version": adapter_version,
        "native_api_entrypoint": native_api_entrypoint,
        "mcc_facade_version": _safe_import_version("mcc"),
        "integration_contract_version": _safe_import_version("mcc_client.contract", attr="CONTRACT_VERSION"),
        "canonical_protocol_version": _safe_import_version("mcc_protocol.version", attr="PROTOCOL_VERSION"),
        "adapter_sdk_version": _safe_import_version("mcc_adapter_sdk", attr="SDK_VERSION"),
        "normative_specification_version": NORMATIVE_SPECIFICATION_VERSION,
        "certification_code_source": "tests/interoperability (PR #48 Multi-Adapter Interoperability Proof)",
        **{f"execution_environment.{k}": v for k, v in _execution_environment_metadata().items()},
    }
    provenance["target_config_hash"] = _target_config_hash({
        "target_id": target_id, "target_type": target_type,
        "ecosystem_name": ecosystem_name, "ecosystem_package": ecosystem_package,
        "adapter_module": adapter_module, "adapter_version": adapter_version,
    })

    def conformance_entry_point() -> Tuple[RequirementResult, ...]:
        return _run_ecosystem_conformance(adapter_factory, import_dependency=import_dependency)

    return CertificationTarget(
        target_id=target_id,
        target_type=target_type,
        implementation_version=resolved_implementation_version,
        certification_profile=f"{target_id}-reference-ecosystem-profile-v1",
        provenance=provenance,
        declared_capabilities=("baseline",),
        conformance_entry_point=conformance_entry_point,
    )


def _safe_import_version(module_name: str, *, attr: str = None) -> str:
    try:
        import importlib
        mod = importlib.import_module(module_name)
        if attr is None:
            return str(getattr(mod, "__version__", "unknown"))
        return str(getattr(mod, attr))
    except Exception:  # noqa: BLE001 - provenance-only, never fatal to target construction
        return "unknown"


# ---------------------------------------------------------------------------
# generic-http
# ---------------------------------------------------------------------------

GENERIC_HTTP_TARGET_ID = "generic-http"


def _import_generic_http() -> None:
    import tests.interoperability.adapters.generic_http  # noqa: F401


def _generic_http_adapter_factory() -> Any:
    from tests.interoperability.adapters.generic_http import GenericHttpAdapter
    return GenericHttpAdapter()


def build_generic_http_target() -> CertificationTarget:
    return _build_target(
        target_id=GENERIC_HTTP_TARGET_ID,
        target_type="framework-neutral-http-integration",
        ecosystem_name="Generic HTTP",
        ecosystem_package="httpx",
        adapter_module="tests.interoperability.adapters.generic_http",
        adapter_version="1.0.0",
        native_api_entrypoint="httpx.Client -> POST {gateway}/evaluate + /consensus/*",
        implementation_version_lookup=lambda: _safe_import_version("httpx"),
        adapter_factory=_generic_http_adapter_factory,
        import_dependency=_import_generic_http,
    )


# ---------------------------------------------------------------------------
# langgraph
# ---------------------------------------------------------------------------

LANGGRAPH_TARGET_ID = "langgraph"


def _import_langgraph() -> None:
    import tests.interoperability.adapters.langgraph_adapter  # noqa: F401


def _langgraph_adapter_factory() -> Any:
    from tests.interoperability.adapters.langgraph_adapter import LangGraphAdapter
    return LangGraphAdapter()


def build_langgraph_target() -> CertificationTarget:
    return _build_target(
        target_id=LANGGRAPH_TARGET_ID,
        target_type="real-framework-integration",
        ecosystem_name="LangGraph",
        ecosystem_package="langgraph",
        adapter_module="tests.interoperability.adapters.langgraph_adapter",
        adapter_version="1.0.0",
        native_api_entrypoint="langgraph.graph.StateGraph -> CompiledStateGraph.invoke",
        implementation_version_lookup=lambda: _safe_import_version("langgraph"),
        adapter_factory=_langgraph_adapter_factory,
        import_dependency=_import_langgraph,
    )


# ---------------------------------------------------------------------------
# crewai
# ---------------------------------------------------------------------------

CREWAI_TARGET_ID = "crewai"


def _import_crewai() -> None:
    import tests.interoperability.adapters.crewai_adapter  # noqa: F401


def _crewai_adapter_factory() -> Any:
    from tests.interoperability.adapters.crewai_adapter import CrewAIAdapter
    return CrewAIAdapter()


def build_crewai_target() -> CertificationTarget:
    return _build_target(
        target_id=CREWAI_TARGET_ID,
        target_type="real-framework-integration",
        ecosystem_name="CrewAI",
        ecosystem_package="crewai",
        adapter_module="tests.interoperability.adapters.crewai_adapter",
        adapter_version="1.0.0",
        native_api_entrypoint="crewai.flow.flow.Flow.kickoff (@start/@listen)",
        implementation_version_lookup=lambda: _safe_import_version("crewai"),
        adapter_factory=_crewai_adapter_factory,
        import_dependency=_import_crewai,
    )


# ---------------------------------------------------------------------------
# autogen
# ---------------------------------------------------------------------------

AUTOGEN_TARGET_ID = "autogen"


def _import_autogen() -> None:
    import tests.interoperability.adapters.autogen_adapter  # noqa: F401


def _autogen_adapter_factory() -> Any:
    from tests.interoperability.adapters.autogen_adapter import AutoGenAdapter
    return AutoGenAdapter()


def build_autogen_target() -> CertificationTarget:
    return _build_target(
        target_id=AUTOGEN_TARGET_ID,
        target_type="real-framework-integration",
        ecosystem_name="AutoGen",
        ecosystem_package="autogen-agentchat",
        adapter_module="tests.interoperability.adapters.autogen_adapter",
        adapter_version="1.0.0",
        native_api_entrypoint="autogen_core.RoutedAgent on SingleThreadedAgentRuntime",
        implementation_version_lookup=lambda: _safe_import_version("autogen_agentchat"),
        adapter_factory=_autogen_adapter_factory,
        import_dependency=_import_autogen,
    )


# ---------------------------------------------------------------------------
# voltagent
# ---------------------------------------------------------------------------

VOLTAGENT_TARGET_ID = "voltagent"


def _import_voltagent() -> None:
    import tests.interoperability.adapters.voltagent_adapter  # noqa: F401


def _voltagent_adapter_factory() -> Any:
    from tests.interoperability.adapters.voltagent_adapter import VoltAgentAdapter
    return VoltAgentAdapter()


def _voltagent_version() -> str:
    from tests.interoperability.adapters.voltagent_adapter import VoltAgentAdapter
    return str(VoltAgentAdapter.framework_version)


def build_voltagent_target() -> CertificationTarget:
    return _build_target(
        target_id=VOLTAGENT_TARGET_ID,
        target_type="real-framework-integration",
        ecosystem_name="VoltAgent",
        ecosystem_package="@voltagent/core",
        adapter_module="tests.interoperability.adapters.voltagent_adapter",
        adapter_version="1.0.0",
        native_api_entrypoint="@voltagent/core Agent (Node subprocess) -> stdout JSON proposal",
        implementation_version_lookup=_voltagent_version,
        adapter_factory=_voltagent_adapter_factory,
        import_dependency=_import_voltagent,
    )


ECOSYSTEM_TARGET_IDS: Tuple[str, ...] = (
    GENERIC_HTTP_TARGET_ID, LANGGRAPH_TARGET_ID, CREWAI_TARGET_ID, AUTOGEN_TARGET_ID, VOLTAGENT_TARGET_ID,
)

ECOSYSTEM_TARGET_BUILDERS: Dict[str, Callable[[], CertificationTarget]] = {
    GENERIC_HTTP_TARGET_ID: build_generic_http_target,
    LANGGRAPH_TARGET_ID: build_langgraph_target,
    CREWAI_TARGET_ID: build_crewai_target,
    AUTOGEN_TARGET_ID: build_autogen_target,
    VOLTAGENT_TARGET_ID: build_voltagent_target,
}

__all__ = [
    "NORMATIVE_SPECIFICATION_VERSION",
    "EcosystemDependencyUnavailableError",
    "GENERIC_HTTP_TARGET_ID",
    "LANGGRAPH_TARGET_ID",
    "CREWAI_TARGET_ID",
    "AUTOGEN_TARGET_ID",
    "VOLTAGENT_TARGET_ID",
    "ECOSYSTEM_TARGET_IDS",
    "ECOSYSTEM_TARGET_BUILDERS",
    "build_generic_http_target",
    "build_langgraph_target",
    "build_crewai_target",
    "build_autogen_target",
    "build_voltagent_target",
]
