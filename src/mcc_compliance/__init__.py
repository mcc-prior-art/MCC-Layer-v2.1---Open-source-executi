"""MCC-Core Integration Contract Compliance & Certification Suite (PR #44).

An official, reusable, deterministic system that independently determines whether
an adapter conforms to a specific version of the framework-neutral MCC-Core
Integration Contract (``docs/INTEGRATION_CONTRACT.md``).

    The Integration Contract defines required behavior.
    Adapters implement the Integration Contract.
    The Compliance Suite verifies adapter conformance.
    No adapter — including VoltAgent — defines the specification.

The suite is observational and downstream of governance: it adds no authorization
semantics, no execution path, and no bypass. Adapters are evaluated only through
the framework-neutral boundary (:mod:`mcc_compliance.protocol`) and run against a
real, in-process governed stack, with every claim cross-checked against ground
truth. It reuses the repository's canonical primitives — ``mcc_core.signing`` for
canonical digests, ``mcc_client.contract`` for the normative contract metadata.

Like ``mcc_evidence`` it lives in the runtime source tree and is **not** shipped in
the ``mcc-core`` wheel.
"""

from __future__ import annotations

from .certification import certification_fingerprint, decide_certification
from .models import (
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
from .protocol import AdapterContext, ComplianceAdapter
from .registry import (
    available_adapters,
    load_adapter,
    load_vectors,
    register_adapter,
)
from .reporting import (
    certification_manifest,
    report_to_json,
    report_to_markdown,
    write_reports,
)
from .runner import ComplianceReport, run_compliance
from .capability_profile import (
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
from .program import (
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

# Register the built-in conforming adapters (reference + VoltAgent).
from . import adapters as _adapters  # noqa: E402,F401

__all__ = [
    "SUITE_VERSION", "REPORT_SCHEMA_VERSION",
    # protocol / boundary
    "ComplianceAdapter", "AdapterContext",
    # models
    "AdapterMetadata", "AdapterOutcome", "ExpectedOutcome", "ComplianceVector",
    "CaseResult", "CaseStatus", "CertificationDecision", "CertificationStatus",
    "Totals", "ComplianceError", "ComplianceErrorCode",
    # registry
    "load_vectors", "register_adapter", "available_adapters", "load_adapter",
    # runner / certification / reporting
    "run_compliance", "ComplianceReport",
    "certification_fingerprint", "decide_certification",
    "report_to_json", "report_to_markdown", "certification_manifest", "write_reports",
    # Certified Adapter Program (PR #46)
    "ProgramStatus", "ScenarioOutcome", "CertificationResult", "ManifestVerification",
    "certify", "certify_report", "build_manifest", "write_manifest", "verify_manifest",
    "OFFICIAL_ADAPTERS", "MANIFEST_PATH", "CERTIFICATION_NOTE",
    # Governance Capability Profile (PR #47)
    "validate_profile", "canonicalize_profile", "profile_digest", "capability_registry",
    "ProfileValidation", "ProfileError", "ProfileErrorCode", "PROFILE_VERSION",
    "BASELINE_CAPABILITIES", "OPTIONAL_CAPABILITIES", "KNOWN_CAPABILITIES",
    "link_capability_profile",
]
