"""MCC-EB-001 Evidence Bundle — schema constants and structured results.

A distinct, explicitly-versioned bundle shape from the existing Governance
Evidence Bundle (``schema.py`` / ``BUNDLE_SCHEMA_VERSION = "mcc-evidence/1"``,
which substantiates an already-completed *runtime governance* decision — a
Decision Token, gate result, execution receipt/denial, audit slice). MCC-EB-001
defines a different artifact: it substantiates a *certification* decision,
collecting Evidence Items that each correspond to Certification Requirements
evaluated under MCC-CP-001. The two schemas are deliberately independent and
coexist in this package; producing or verifying one never touches the other's
files or logic (see ``docs/`` cross-reference in this module and the Wave A
implementation report under ``conformance/normative-v1.0/remediation/`` for
the full backward-compatibility rationale).

This module reuses the existing, generic ``CheckResult`` / ``CheckStatus``
structured-reporting pair from ``schema.py`` (name/status/detail; PASS/FAIL/
WARN/NA) rather than redefining an equivalent type.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional

from .schema import CheckResult, CheckStatus

#: Bundle schema version for the MCC-EB-001-conformant bundle shape. Distinct
#: from BUNDLE_SCHEMA_VERSION ("mcc-evidence/1") in schema.py.
EB001_SCHEMA_VERSION = "mcc-eb-001/1"
SUPPORTED_EB001_SCHEMA_VERSIONS = frozenset({EB001_SCHEMA_VERSION})

#: Required root-level names (EB-STR-002 / EB-FILE-001..003). Fixed constants
#: -- filenames are stable across regeneration of an equivalent Bundle
#: (EB-STR-004) and never contain machine- or run-specific data.
BUNDLE_DESCRIPTOR_NAME = "bundle_descriptor.json"
INTEGRITY_RECORD_NAME = "integrity_record.json"
PROVENANCE_RECORD_NAME = "provenance_record.json"
EVIDENCE_DIR_NAME = "evidence"

REQUIRED_ROOT_NAMES = (BUNDLE_DESCRIPTOR_NAME, INTEGRITY_RECORD_NAME, PROVENANCE_RECORD_NAME)


class EB001Status(str, Enum):
    """Overall MCC-EB-001 verification outcome. Fail-closed: any structural,
    integrity, or consistency problem yields INVALID -- there is no partial
    "mostly valid" outcome."""

    VALID = "VALID"
    INVALID = "INVALID"
    UNSUPPORTED_SCHEMA = "UNSUPPORTED_SCHEMA"


@dataclass
class EB001VerificationResult:
    overall_status: EB001Status
    schema_supported: bool
    bundle_id: Optional[str] = None
    checks: List[CheckResult] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    failures: List[str] = field(default_factory=list)

    @property
    def valid(self) -> bool:
        return self.overall_status is EB001Status.VALID

    def check(self, name: str) -> Optional[CheckResult]:
        return next((c for c in self.checks if c.name == name), None)

    def to_dict(self) -> dict:
        return {
            "overall_status": self.overall_status.value,
            "valid": self.valid,
            "schema_supported": self.schema_supported,
            "bundle_id": self.bundle_id,
            "checks": [c.to_dict() for c in self.checks],
            "warnings": list(self.warnings),
            "failures": list(self.failures),
        }


class EB001Error(Exception):
    """Base error for MCC-EB-001 bundle production."""


class IncompleteEB001BundleError(EB001Error):
    """Production refused because required Bundle content was missing or
    internally inconsistent -- no partial bundle is ever written."""


__all__ = [
    "EB001_SCHEMA_VERSION",
    "SUPPORTED_EB001_SCHEMA_VERSIONS",
    "BUNDLE_DESCRIPTOR_NAME",
    "INTEGRITY_RECORD_NAME",
    "PROVENANCE_RECORD_NAME",
    "EVIDENCE_DIR_NAME",
    "REQUIRED_ROOT_NAMES",
    "EB001Status",
    "EB001VerificationResult",
    "EB001Error",
    "IncompleteEB001BundleError",
    "CheckResult",
    "CheckStatus",
]
