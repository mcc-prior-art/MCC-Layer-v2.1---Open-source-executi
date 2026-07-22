"""MCC-Core Integration Contract Compliance & Certification Suite (PR #44).

An official, reusable, deterministic system that independently determines whether
an adapter conforms to a specific version of the framework-neutral MCC-Core
Integration Contract (``docs/INTEGRATION_CONTRACT.md``).

    The Integration Contract defines required behavior.
    Adapters implement the Integration Contract.
    The Compliance Suite verifies adapter conformance.
    No adapter — including VoltAgent — defines the specification.

The suite is observational and downstream of governance: it adds no authorization
semantics, no execution path, and no bypass. It reuses the repository's canonical
primitives — ``mcc_core.signing`` for canonical digests, ``mcc_client.contract`` for
the normative contract metadata.

Import model (PR #50 decoupling)
--------------------------------
Public names resolve **lazily** (PEP 562 ``__getattr__``). Importing
``mcc_compliance`` — or importing the pure ``mcc_compliance.capability_profile``
submodule (the only part the Canonical Protocol / Adapter SDK need) — no longer
eagerly loads the whole suite (runner, reporting, program) or its built-in adapters
(which pull example agent code). The suite behaves exactly as before: the first
access to a suite name (registry/runner/program/reporting/certification) registers
the built-in conforming adapters, just as the old eager ``from . import adapters``
did. The lightweight ``capability_profile`` path never triggers that.

Like ``mcc_evidence`` it lives in the runtime source tree.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

# Public name -> submodule that defines it (single source of truth for re-exports).
_EXPORTS: dict[str, str] = {
    # models (light — no adapter registration needed)
    "SUITE_VERSION": "models", "REPORT_SCHEMA_VERSION": "models",
    "AdapterMetadata": "models", "AdapterOutcome": "models", "ExpectedOutcome": "models",
    "ComplianceVector": "models", "CaseResult": "models", "CaseStatus": "models",
    "CertificationDecision": "models", "CertificationStatus": "models", "Totals": "models",
    "ComplianceError": "models", "ComplianceErrorCode": "models",
    # protocol / boundary (light)
    "ComplianceAdapter": "protocol", "AdapterContext": "protocol",
    # capability profile (light — the SDK / canonical-protocol path)
    "validate_profile": "capability_profile", "canonicalize_profile": "capability_profile",
    "profile_digest": "capability_profile", "capability_registry": "capability_profile",
    "ProfileValidation": "capability_profile", "ProfileError": "capability_profile",
    "ProfileErrorCode": "capability_profile", "PROFILE_VERSION": "capability_profile",
    "BASELINE_CAPABILITIES": "capability_profile", "OPTIONAL_CAPABILITIES": "capability_profile",
    "KNOWN_CAPABILITIES": "capability_profile",
    # registry (suite)
    "load_vectors": "registry", "register_adapter": "registry",
    "available_adapters": "registry", "load_adapter": "registry",
    # runner / certification / reporting (suite)
    "run_compliance": "runner", "ComplianceReport": "runner",
    "certification_fingerprint": "certification", "decide_certification": "certification",
    "report_to_json": "reporting", "report_to_markdown": "reporting",
    "certification_manifest": "reporting", "write_reports": "reporting",
    # Certified Adapter Program (PR #46) (suite)
    "ProgramStatus": "program", "ScenarioOutcome": "program", "CertificationResult": "program",
    "ManifestVerification": "program", "certify": "program", "certify_report": "program",
    "build_manifest": "program", "write_manifest": "program", "verify_manifest": "program",
    "OFFICIAL_ADAPTERS": "program", "MANIFEST_PATH": "program", "CERTIFICATION_NOTE": "program",
    "link_capability_profile": "program",
}

# The pure, SDK-relevant modules that must NOT trigger built-in adapter registration.
_LIGHT_MODULES = frozenset({"models", "protocol", "capability_profile"})

__all__ = sorted(_EXPORTS)


def _ensure_builtin_adapters() -> None:
    """Register the built-in conforming adapters (reference + VoltAgent), exactly as
    the old eager ``from . import adapters`` did. Idempotent; triggered only when a
    suite name is first accessed, never on the lightweight capability path."""
    import importlib
    importlib.import_module(".adapters", __name__)


def __getattr__(name: str) -> Any:
    module = _EXPORTS.get(name)
    if module is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    if module not in _LIGHT_MODULES:
        _ensure_builtin_adapters()
    import importlib
    submodule = importlib.import_module(f".{module}", __name__)
    value = getattr(submodule, name)
    globals()[name] = value
    return value


def __dir__() -> list[str]:
    return sorted(set(globals()) | set(_EXPORTS))


if TYPE_CHECKING:  # static type-checkers / IDEs see the re-exported names
    from .capability_profile import (  # noqa: F401
        BASELINE_CAPABILITIES,
        KNOWN_CAPABILITIES,
        OPTIONAL_CAPABILITIES,
        PROFILE_VERSION,
        ProfileError,
        ProfileErrorCode,
        ProfileValidation,
        canonicalize_profile,
        capability_registry,
        profile_digest,
        validate_profile,
    )
    from .certification import certification_fingerprint, decide_certification  # noqa: F401
    from .models import (  # noqa: F401
        REPORT_SCHEMA_VERSION,
        SUITE_VERSION,
        AdapterMetadata,
        AdapterOutcome,
        CaseResult,
        CaseStatus,
        CertificationDecision,
        CertificationStatus,
        ComplianceError,
        ComplianceErrorCode,
        ComplianceVector,
        ExpectedOutcome,
        Totals,
    )
    from .program import (  # noqa: F401
        CERTIFICATION_NOTE,
        MANIFEST_PATH,
        OFFICIAL_ADAPTERS,
        CertificationResult,
        ManifestVerification,
        ProgramStatus,
        ScenarioOutcome,
        build_manifest,
        certify,
        certify_report,
        link_capability_profile,
        verify_manifest,
        write_manifest,
    )
    from .protocol import AdapterContext, ComplianceAdapter  # noqa: F401
    from .registry import (  # noqa: F401
        available_adapters,
        load_adapter,
        load_vectors,
        register_adapter,
    )
    from .reporting import (  # noqa: F401
        certification_manifest,
        report_to_json,
        report_to_markdown,
        write_reports,
    )
    from .runner import ComplianceReport, run_compliance  # noqa: F401
