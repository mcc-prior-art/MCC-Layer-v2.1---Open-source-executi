"""Result models, enums, and the stable error taxonomy for the compliance suite.

Pure data + stable string codes. No governance logic, no I/O. Certification is
fail-closed: any error path resolves to ERROR/NOT_CERTIFIED, never CERTIFIED.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

#: Version of the compliance & certification suite itself (distinct from the
#: contract version and from any package/distribution version). Bound into the
#: certification fingerprint.
SUITE_VERSION = "1.0.0"

#: Schema version of the generated JSON report.
REPORT_SCHEMA_VERSION = "1"


class CaseStatus(str, Enum):
    """Outcome of a single compliance case."""

    PASS = "PASS"
    FAIL = "FAIL"
    ERROR = "ERROR"
    SKIP = "SKIP"


class CertificationStatus(str, Enum):
    """Overall certification outcome. Fail-closed: only PASS-everything CERTIFIES."""

    CERTIFIED = "CERTIFIED"
    NOT_CERTIFIED = "NOT_CERTIFIED"
    ERROR = "ERROR"


class ComplianceErrorCode(str, Enum):
    """Stable, machine-readable failure codes. Values are part of the suite
    contract and MUST remain stable. Every non-PASS outcome carries one."""

    # Loading / metadata / version.
    ADAPTER_LOAD_FAILED = "ADAPTER_LOAD_FAILED"
    ADAPTER_METADATA_INCOMPLETE = "ADAPTER_METADATA_INCOMPLETE"
    ADAPTER_VERSION_MISMATCH = "ADAPTER_VERSION_MISMATCH"
    UNSUPPORTED_CONTRACT_VERSION = "UNSUPPORTED_CONTRACT_VERSION"
    # Manifest / vectors.
    MANIFEST_INVALID = "MANIFEST_INVALID"
    MANIFEST_DIGEST_MISMATCH = "MANIFEST_DIGEST_MISMATCH"
    VECTOR_PARSE_ERROR = "VECTOR_PARSE_ERROR"
    DUPLICATE_VECTOR_ID = "DUPLICATE_VECTOR_ID"
    UNKNOWN_VECTOR_TYPE = "UNKNOWN_VECTOR_TYPE"
    # Runner / normalization / adapter behavior.
    ADAPTER_EXCEPTION = "ADAPTER_EXCEPTION"
    NORMALIZATION_FAILED = "NORMALIZATION_FAILED"
    UNKNOWN_VERDICT = "UNKNOWN_VERDICT"
    MANDATORY_SKIP = "MANDATORY_SKIP"
    MISSING_EVIDENCE = "MISSING_EVIDENCE"
    # Verdict / execution mismatches (ground-truth cross-checked).
    WRONG_VERDICT = "WRONG_VERDICT"
    EXPECTED_EXECUTED_BUT_NOT = "EXPECTED_EXECUTED_BUT_NOT"
    EXPECTED_NOT_EXECUTED_BUT_WAS = "EXPECTED_NOT_EXECUTED_BUT_WAS"
    FABRICATED_EXECUTION = "FABRICATED_EXECUTION"
    UNREPORTED_EXECUTION = "UNREPORTED_EXECUTION"
    CONSTRAINT_NOT_APPLIED = "CONSTRAINT_NOT_APPLIED"
    REPLAY_NOT_BLOCKED = "REPLAY_NOT_BLOCKED"
    AUDIT_NOT_VERIFIED = "AUDIT_NOT_VERIFIED"
    # Suite integrity.
    REPORT_INTEGRITY_FAILED = "REPORT_INTEGRITY_FAILED"
    RUNNER_ERROR = "RUNNER_ERROR"


class ComplianceError(Exception):
    """A fail-closed compliance error carrying a stable code."""

    def __init__(self, code: ComplianceErrorCode, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


# --------------------------------------------------------------------------- #
# Adapter-facing value objects.                                               #
# --------------------------------------------------------------------------- #

@dataclass(frozen=True)
class AdapterMetadata:
    """Stable identity an adapter declares. Required for certification."""

    name: str
    version: str
    implementation_id: str
    claimed_contract_version: str
    framework: Optional[str] = None

    def missing_fields(self) -> List[str]:
        missing = []
        for f in ("name", "version", "implementation_id", "claimed_contract_version"):
            v = getattr(self, f)
            if not isinstance(v, str) or not v.strip():
                missing.append(f)
        return missing

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "version": self.version,
            "implementation_id": self.implementation_id,
            "framework": self.framework,
            "claimed_contract_version": self.claimed_contract_version,
        }


@dataclass
class AdapterOutcome:
    """Normalized result an adapter reports for one scenario. The adapter reports
    what it did; the runner independently cross-checks against the governed
    stack's ground truth (receipts + audit), so a false claim is detectable."""

    verdict: str
    executed: bool
    applied_constraints: List[str] = field(default_factory=list)
    audit_valid: Optional[bool] = None
    error: Optional[str] = None
    skipped: bool = False
    skip_reason: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "verdict": self.verdict,
            "executed": bool(self.executed),
            "applied_constraints": list(self.applied_constraints),
            "audit_valid": self.audit_valid,
            "error": self.error,
            "skipped": bool(self.skipped),
        }


# --------------------------------------------------------------------------- #
# Vectors.                                                                     #
# --------------------------------------------------------------------------- #

@dataclass(frozen=True)
class ExpectedOutcome:
    """What a conforming adapter's normalized outcome must satisfy."""

    executed: bool
    verdict: Optional[str] = None
    min_constraints: int = 0
    audit_valid: Optional[bool] = None
    replay_blocked: bool = False

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "ExpectedOutcome":
        return ExpectedOutcome(
            executed=bool(d["executed"]),
            verdict=d.get("verdict"),
            min_constraints=int(d.get("min_constraints", 0)),
            audit_valid=d.get("audit_valid"),
            replay_blocked=bool(d.get("replay_blocked", False)),
        )


@dataclass(frozen=True)
class ComplianceVector:
    """One executable, normative compliance case."""

    id: str
    requirement: str
    invariant: str
    category: str
    mandatory: bool
    capability: str
    scenario: Dict[str, Any]
    expected: ExpectedOutcome


# --------------------------------------------------------------------------- #
# Results.                                                                     #
# --------------------------------------------------------------------------- #

@dataclass
class CaseResult:
    """Structured result for one vector. ``duration_ms`` is informational and is
    excluded from deterministic report comparisons and the fingerprint."""

    vector_id: str
    contract_version: str
    requirement: str
    invariant: str
    category: str
    mandatory: bool
    status: CaseStatus
    expected: Dict[str, Any]
    actual: Dict[str, Any]
    failure_code: Optional[str] = None
    failure_explanation: Optional[str] = None
    evidence: Dict[str, Any] = field(default_factory=dict)
    duration_ms: Optional[float] = None

    def stable_dict(self) -> Dict[str, Any]:
        """Deterministic projection (no duration, no unstable fields)."""
        return {
            "vector_id": self.vector_id,
            "contract_version": self.contract_version,
            "requirement": self.requirement,
            "invariant": self.invariant,
            "category": self.category,
            "mandatory": self.mandatory,
            "status": self.status.value,
            "expected": self.expected,
            "actual": self.actual,
            "failure_code": self.failure_code,
            "failure_explanation": self.failure_explanation,
            "evidence": self.evidence,
        }


@dataclass
class Totals:
    total: int = 0
    passed: int = 0
    failed: int = 0
    errored: int = 0
    skipped: int = 0
    mandatory_total: int = 0
    mandatory_passed: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total": self.total,
            "passed": self.passed,
            "failed": self.failed,
            "errored": self.errored,
            "skipped": self.skipped,
            "mandatory_total": self.mandatory_total,
            "mandatory_passed": self.mandatory_passed,
        }

    @property
    def pass_percentage(self) -> float:
        return round(100.0 * self.passed / self.total, 2) if self.total else 0.0


@dataclass
class CertificationDecision:
    """Explicit certification result. Percentage is informational only — it never
    controls the decision."""

    status: CertificationStatus
    reasons: List[str]
    fingerprint: str
    informational_pass_percentage: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status.value,
            "reasons": list(self.reasons),
            "fingerprint": self.fingerprint,
            "informational_pass_percentage": self.informational_pass_percentage,
        }


__all__ = [
    "SUITE_VERSION", "REPORT_SCHEMA_VERSION",
    "CaseStatus", "CertificationStatus", "ComplianceErrorCode", "ComplianceError",
    "AdapterMetadata", "AdapterOutcome", "ExpectedOutcome", "ComplianceVector",
    "CaseResult", "Totals", "CertificationDecision",
]
