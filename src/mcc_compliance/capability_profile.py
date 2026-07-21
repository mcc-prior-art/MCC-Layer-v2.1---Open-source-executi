"""Governance Capability Profile — canonical model + validator (PR #47).

A **declarative**, framework-neutral, versioned way for an adapter to state which
MCC-Core governance capabilities it supports. It is part of the Integration
Contract ecosystem and changes **no** runtime governance semantics.

Trust boundary — these four terms are NOT synonyms:

* **declared**   — the adapter says so in a profile (untrusted).
* **validated**  — the profile passed schema + semantic validation here.
* **certified**  — the Certified Adapter Program recorded real compliance evidence.
* **authorized** — the runtime Gate independently permitted a specific action.

    A Governance Capability Profile is a declarative statement of adapter
    capabilities. It does not grant execution authority, replace runtime
    authorization, or weaken fail-closed enforcement.

Capability support is **not** execution permission. A profile is fail-closed:
anything malformed, contradictory, or unrecognized is rejected.

Vocabulary is single-sourced from the normative contract layer
(`mcc_client.contract.REQUIRED_SECURITY_INVARIANTS`) plus a small closed set of
evidence-backed optional capabilities (ESCALATE, CONSTRAIN, PR #42 evidence
bundle). No capability is invented here. Canonicalization/digest reuse
`mcc_core.signing` — no second algorithm, no new trust scheme.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from mcc_core.signing import canonical_bytes, sha256_hex

from mcc_client.contract import (
    CONTRACT_VERSION,
    REQUIRED_SECURITY_INVARIANTS,
    check_version_compatibility,
)

from .models import SUITE_VERSION

#: Profile format version (distinct from contract/suite/package versions).
PROFILE_VERSION = "1"
SUPPORTED_PROFILE_VERSIONS: frozenset[str] = frozenset({"1"})
PROFILE_SCHEMA_ID = "mcc-governance-capability-profile/1"

#: Baseline (mandatory) runtime governance capabilities — the exact invariants the
#: Gate enforces. A conforming adapter for a given contract version passes through
#: the Gate, so all baseline capabilities MUST be declared supported.
BASELINE_CAPABILITIES: Tuple[str, ...] = tuple(REQUIRED_SECURITY_INVARIANTS)

#: Optional capabilities — closed set, each backed by a real repository feature:
#:   human_in_the_loop_escalation  -> the ESCALATE verdict + single-use approval loop
#:   constraint_enforcement        -> the CONSTRAIN verdict (server-clamped payload)
#:   tamper_evident_audit_evidence -> the portable Governance Evidence Bundle (PR #42)
OPTIONAL_CAPABILITIES: Tuple[str, ...] = (
    "human_in_the_loop_escalation",
    "constraint_enforcement",
    "tamper_evident_audit_evidence",
)

#: The full canonical registry. Any name outside this set is rejected.
KNOWN_CAPABILITIES: frozenset[str] = frozenset(BASELINE_CAPABILITIES) | frozenset(OPTIONAL_CAPABILITIES)

#: A raw adapter-authored profile may ONLY self-declare. Trusted VALIDATED/CERTIFIED
#: status is produced by the compliance/certification programs, never by the adapter.
RAW_CERTIFICATION_STATUS = "SELF_DECLARED"
_CERTIFICATION_STATUSES = frozenset({"SELF_DECLARED", "VALIDATED", "CERTIFIED"})


class ProfileErrorCode(str, Enum):
    """Stable, machine-readable validation failure codes. Fail-closed."""

    MALFORMED_PROFILE = "MALFORMED_PROFILE"
    FIELD_MISSING = "FIELD_MISSING"
    FIELD_INVALID = "FIELD_INVALID"
    ADDITIONAL_PROPERTY = "ADDITIONAL_PROPERTY"
    PROFILE_VERSION_UNSUPPORTED = "PROFILE_VERSION_UNSUPPORTED"
    ADAPTER_IDENTITY_INVALID = "ADAPTER_IDENTITY_INVALID"
    CONTRACT_VERSION_UNSUPPORTED = "CONTRACT_VERSION_UNSUPPORTED"
    COMPLIANCE_VERSION_UNKNOWN = "COMPLIANCE_VERSION_UNKNOWN"
    UNKNOWN_CAPABILITY = "UNKNOWN_CAPABILITY"
    DUPLICATE_CAPABILITY = "DUPLICATE_CAPABILITY"
    SUPPORTED_UNSUPPORTED_OVERLAP = "SUPPORTED_UNSUPPORTED_OVERLAP"
    MISSING_BASELINE_CAPABILITY = "MISSING_BASELINE_CAPABILITY"
    BASELINE_DECLARED_UNSUPPORTED = "BASELINE_DECLARED_UNSUPPORTED"
    CONSTRAINT_UNKNOWN_CAPABILITY = "CONSTRAINT_UNKNOWN_CAPABILITY"
    CONSTRAINT_INVALID = "CONSTRAINT_INVALID"
    FALSE_CERTIFICATION_CLAIM = "FALSE_CERTIFICATION_CLAIM"


@dataclass(frozen=True)
class ProfileError:
    code: ProfileErrorCode
    message: str

    def to_dict(self) -> Dict[str, str]:
        return {"code": self.code.value, "message": self.message}


@dataclass(frozen=True)
class ProfileValidation:
    """Structured result. ``valid`` is the only field that gates behavior; when
    False, ``errors`` is non-empty and ``canonical``/``digest`` are None."""

    valid: bool
    errors: Tuple[ProfileError, ...]
    canonical: Optional[Dict[str, Any]] = None
    digest: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "valid": self.valid,
            "errors": [e.to_dict() for e in self.errors],
            "digest": self.digest,
            "canonical": self.canonical,
        }


# --------------------------------------------------------------------------- #
# Canonicalization + digest.                                                  #
# --------------------------------------------------------------------------- #

def canonicalize_profile(profile: Dict[str, Any]) -> Dict[str, Any]:
    """Return a deterministic normalization: capability lists sorted + de-duplicated,
    optional blocks defaulted, so the same semantic profile always canonicalizes
    identically regardless of input key/list ordering. Does not validate."""
    adapter = profile.get("adapter", {}) or {}
    contract = profile.get("integration_contract", {}) or {}
    compliance = profile.get("compliance", {}) or {}
    certification = profile.get("certification", {}) or {}
    return {
        "profile_version": profile.get("profile_version"),
        "schema_id": PROFILE_SCHEMA_ID,
        "adapter": {
            "name": adapter.get("name"),
            "version": adapter.get("version"),
            "implementation_id": adapter.get("implementation_id"),
            "framework": adapter.get("framework"),
        },
        "integration_contract": {"version": contract.get("version")},
        "compliance": {
            "suite_version": compliance.get("suite_version"),
            "vector_set_version": compliance.get("vector_set_version"),
        },
        "certification": {
            "claimed_status": certification.get("claimed_status", RAW_CERTIFICATION_STATUS),
            "evidence_digest": certification.get("evidence_digest"),
        },
        "runtime_capabilities": sorted(set(profile.get("runtime_capabilities", []) or [])),
        "optional_capabilities": sorted(set(profile.get("optional_capabilities", []) or [])),
        "unsupported_capabilities": sorted(set(profile.get("unsupported_capabilities", []) or [])),
        "constraints": profile.get("constraints", {}) or {},
        "metadata": profile.get("metadata", {}) or {},
    }


def profile_digest(profile: Dict[str, Any]) -> str:
    """Deterministic SHA-256 over the canonical profile (integrity fingerprint)."""
    return sha256_hex(canonical_bytes(canonicalize_profile(profile)))


# --------------------------------------------------------------------------- #
# Validation (schema-shape + semantic, pure Python, fail-closed).             #
# --------------------------------------------------------------------------- #

_TOP_LEVEL = {
    "profile_version", "adapter", "integration_contract", "compliance",
    "certification", "runtime_capabilities", "optional_capabilities",
    "unsupported_capabilities", "constraints", "metadata",
}
_REQUIRED_TOP = {"profile_version", "adapter", "integration_contract",
                 "runtime_capabilities"}
_ADAPTER_FIELDS = {"name", "version", "implementation_id", "framework"}
_ADAPTER_REQUIRED = {"name", "version", "implementation_id"}


def _dups(items: List[Any]) -> List[Any]:
    seen: set[Any] = set()
    out: List[Any] = []
    for x in items:
        if x in seen and x not in out:
            out.append(x)
        seen.add(x)
    return out


def validate_profile(profile: Any) -> ProfileValidation:
    """Validate a Governance Capability Profile (schema shape + semantic invariants).

    Fail-closed: any structural or semantic problem yields ``valid=False`` with
    stable error codes and no digest. A raw profile may only self-declare
    certification; claiming VALIDATED/CERTIFIED without external evidence is
    rejected as a false certification claim."""
    errors: List[ProfileError] = []

    def err(code: ProfileErrorCode, msg: str) -> None:
        errors.append(ProfileError(code, msg))

    if not isinstance(profile, dict):
        return ProfileValidation(False, (ProfileError(
            ProfileErrorCode.MALFORMED_PROFILE, "profile must be a JSON object"),))

    # Top-level shape (strict: metadata is the only open extension namespace).
    for extra in sorted(set(profile) - _TOP_LEVEL):
        err(ProfileErrorCode.ADDITIONAL_PROPERTY, f"unknown top-level field {extra!r}")
    for missing in sorted(_REQUIRED_TOP - set(profile)):
        err(ProfileErrorCode.FIELD_MISSING, f"missing required field {missing!r}")

    # Profile version.
    pv = profile.get("profile_version")
    if pv is not None and pv not in SUPPORTED_PROFILE_VERSIONS:
        err(ProfileErrorCode.PROFILE_VERSION_UNSUPPORTED,
            f"profile_version {pv!r} not supported (supported: {sorted(SUPPORTED_PROFILE_VERSIONS)})")

    # Adapter identity.
    adapter = profile.get("adapter")
    if not isinstance(adapter, dict):
        err(ProfileErrorCode.ADAPTER_IDENTITY_INVALID, "adapter must be an object")
    else:
        for extra in sorted(set(adapter) - _ADAPTER_FIELDS):
            err(ProfileErrorCode.ADDITIONAL_PROPERTY, f"unknown adapter field {extra!r}")
        for f in sorted(_ADAPTER_REQUIRED):
            v = adapter.get(f)
            if not isinstance(v, str) or not v.strip():
                err(ProfileErrorCode.ADAPTER_IDENTITY_INVALID,
                    f"adapter.{f} must be a non-empty string")
        if "framework" in adapter and adapter["framework"] is not None \
                and not isinstance(adapter["framework"], str):
            err(ProfileErrorCode.FIELD_INVALID, "adapter.framework must be a string or null")

    # Integration contract version.
    contract = profile.get("integration_contract")
    if not isinstance(contract, dict) or "version" not in contract:
        err(ProfileErrorCode.FIELD_MISSING, "integration_contract.version is required")
    else:
        compat = check_version_compatibility(str(contract["version"]))
        if not compat.compatible:
            err(ProfileErrorCode.CONTRACT_VERSION_UNSUPPORTED,
                f"integration_contract.version {contract['version']!r}: {compat.reason}")

    # Compliance block (optional, but versions must be recognized when present).
    compliance = profile.get("compliance")
    if compliance is not None:
        if not isinstance(compliance, dict):
            err(ProfileErrorCode.FIELD_INVALID, "compliance must be an object")
        else:
            sv = compliance.get("suite_version")
            if sv is not None and sv != SUITE_VERSION:
                err(ProfileErrorCode.COMPLIANCE_VERSION_UNKNOWN,
                    f"compliance.suite_version {sv!r} != known {SUITE_VERSION!r}")

    # Certification block — a raw profile may only SELF_DECLARE.
    certification = profile.get("certification")
    if certification is not None:
        if not isinstance(certification, dict):
            err(ProfileErrorCode.FIELD_INVALID, "certification must be an object")
        else:
            status = certification.get("claimed_status", RAW_CERTIFICATION_STATUS)
            if status not in _CERTIFICATION_STATUSES:
                err(ProfileErrorCode.FIELD_INVALID,
                    f"certification.claimed_status {status!r} is not a known status")
            elif status != RAW_CERTIFICATION_STATUS:
                err(ProfileErrorCode.FALSE_CERTIFICATION_CLAIM,
                    "a profile may only self-declare; trusted VALIDATED/CERTIFIED "
                    "status comes from the Certified Adapter Program, not the adapter")

    # Capability lists.
    def _cap_list(key: str) -> List[str]:
        val = profile.get(key, [])
        if val is None:
            return []
        if not isinstance(val, list) or any(not isinstance(x, str) for x in val):
            err(ProfileErrorCode.FIELD_INVALID, f"{key} must be a list of strings")
            return []
        for d in _dups(val):
            err(ProfileErrorCode.DUPLICATE_CAPABILITY, f"{key} has duplicate {d!r}")
        for name in val:
            if name not in KNOWN_CAPABILITIES:
                err(ProfileErrorCode.UNKNOWN_CAPABILITY,
                    f"{key} has unknown capability {name!r}")
        return val

    runtime = _cap_list("runtime_capabilities")
    optional = _cap_list("optional_capabilities")
    unsupported = _cap_list("unsupported_capabilities")

    supported = set(runtime) | set(optional)
    overlap = supported & set(unsupported)
    if overlap:
        err(ProfileErrorCode.SUPPORTED_UNSUPPORTED_OVERLAP,
            f"capabilities declared both supported and unsupported: {sorted(overlap)}")

    # Baseline invariants are mandatory for a supported contract version.
    for base in BASELINE_CAPABILITIES:
        if base in unsupported:
            err(ProfileErrorCode.BASELINE_DECLARED_UNSUPPORTED,
                f"baseline capability {base!r} cannot be declared unsupported")
        elif base not in supported:
            err(ProfileErrorCode.MISSING_BASELINE_CAPABILITY,
                f"baseline capability {base!r} must be declared supported")

    # Constraints reference only supported, known capabilities; structured only.
    constraints = profile.get("constraints")
    if constraints is not None:
        if not isinstance(constraints, dict):
            err(ProfileErrorCode.CONSTRAINT_INVALID, "constraints must be an object")
        else:
            for cap, body in constraints.items():
                if cap not in KNOWN_CAPABILITIES:
                    err(ProfileErrorCode.CONSTRAINT_UNKNOWN_CAPABILITY,
                        f"constraint references unknown capability {cap!r}")
                elif cap not in supported:
                    err(ProfileErrorCode.CONSTRAINT_UNKNOWN_CAPABILITY,
                        f"constraint references unsupported capability {cap!r}")
                if not isinstance(body, dict):
                    err(ProfileErrorCode.CONSTRAINT_INVALID,
                        f"constraint for {cap!r} must be a structured object")

    if errors:
        # Deterministic error ordering (by code then message).
        ordered = tuple(sorted(errors, key=lambda e: (e.code.value, e.message)))
        return ProfileValidation(False, ordered)

    canonical = canonicalize_profile(profile)
    return ProfileValidation(True, (), canonical=canonical,
                             digest=sha256_hex(canonical_bytes(canonical)))


def capability_registry() -> Dict[str, Any]:
    """Deterministic, machine-readable snapshot of the canonical capability set."""
    return {
        "profile_version": PROFILE_VERSION,
        "schema_id": PROFILE_SCHEMA_ID,
        "integration_contract_version": CONTRACT_VERSION,
        "baseline_capabilities": list(BASELINE_CAPABILITIES),
        "optional_capabilities": list(OPTIONAL_CAPABILITIES),
    }


__all__ = [
    "PROFILE_VERSION", "SUPPORTED_PROFILE_VERSIONS", "PROFILE_SCHEMA_ID",
    "BASELINE_CAPABILITIES", "OPTIONAL_CAPABILITIES", "KNOWN_CAPABILITIES",
    "RAW_CERTIFICATION_STATUS",
    "ProfileErrorCode", "ProfileError", "ProfileValidation",
    "canonicalize_profile", "profile_digest", "validate_profile", "capability_registry",
]
