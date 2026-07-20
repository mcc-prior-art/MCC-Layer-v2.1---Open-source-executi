"""Governance Evidence Bundle — schema, status enums, and typed results.

This is the versioned, deterministic contract for a portable evidence bundle. It
is **observational only**: it describes evidence of an already-completed
governance path and carries no authority. It reuses MCC-Core's canonical
serialization and digest primitives — it does not invent new ones.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

#: Bundle schema version. The verifier refuses versions it does not support.
BUNDLE_SCHEMA_VERSION = "mcc-evidence/1"
SUPPORTED_SCHEMA_VERSIONS = frozenset({BUNDLE_SCHEMA_VERSION})

#: Canonical file names inside a bundle directory/archive.
MANIFEST_NAME = "manifest.json"
DECISION_TOKEN_PATH = "decision/token.json"
PROPOSAL_PATH = "proposal/proposal.json"
GATE_RESULT_PATH = "gate/result.json"
RECEIPT_PATH = "execution/receipt.json"
DENIAL_PATH = "execution/denial.json"
AUDIT_ENTRIES_PATH = "audit/entries.jsonl"
AUDIT_ANCHOR_PATH = "audit/anchor.json"

#: Fields that are legitimately non-deterministic across exports of the same
#: evidence (documented; excluded from equivalence comparison).
NON_DETERMINISTIC_MANIFEST_FIELDS = ("created_at", "bundle_id")


class Outcome(str, Enum):
    """Whether the governed path ended in execution or denial."""

    EXECUTED = "EXECUTED"
    DENIED = "DENIED"


class CheckStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    WARN = "WARN"
    NA = "NA"


class EvidenceStatus(str, Enum):
    #: Executable verdict: integrity + bindings + audit + a signature verified
    #: against a TRUSTED issuer key. Trusted governance evidence.
    VERIFIED = "VERIFIED"
    #: DENY evidence: integrity + audit + execution-consistency hold and it
    #: proves no authorization/execution. A denial has no signer to anchor.
    DENIAL_VERIFIED = "DENIAL_VERIFIED"
    #: Executable verdict, structurally intact (integrity + bindings + audit),
    #: but the signer could not be verified against a trusted key (none supplied,
    #: or the signer is not in the trusted set). NOT trusted governance evidence.
    INTACT_UNTRUSTED_SIGNER = "INTACT_UNTRUSTED_SIGNER"
    #: A blocking failure was found (tamper, missing evidence, broken chain,
    #: signature invalid against a supplied trusted key, …).
    INVALID = "INVALID"
    #: The bundle's schema version is not supported by this verifier.
    UNSUPPORTED_SCHEMA = "UNSUPPORTED_SCHEMA"


#: Statuses that constitute trusted governance evidence.
TRUSTED_STATUSES = frozenset({EvidenceStatus.VERIFIED, EvidenceStatus.DENIAL_VERIFIED})


@dataclass(frozen=True)
class CheckResult:
    name: str
    status: CheckStatus
    detail: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {"name": self.name, "status": self.status.value, "detail": self.detail}


@dataclass
class VerificationResult:
    """Structured result of offline bundle verification (never just a Boolean).

    The independent dimensions below are reported separately so an intact-but-
    untrusted bundle is never conflated with trusted governance evidence:

    * ``integrity_valid`` — schema supported, manifest well-formed, every artifact
      digest recomputes, no missing/unexpected files.
    * ``audit_chain_valid`` — the included audit slice links and recomputes (True
      when no audit slice is present — vacuously, see ``audit_present``).
    * ``signer_verified`` — the decision-token signature cryptographically
      verified against the key it was checked with.
    * ``signer_trusted`` — that key was in the caller's trusted set.
    * ``authority_evidence_verified`` — for an executable verdict: bindings hold
      AND the signature is trusted; for a denial: not applicable (no authority
      was granted — see ``overall_status``).
    * ``overall_status`` — the single roll-up (see :class:`EvidenceStatus`).

    ``trusted`` is a convenience: True only for trusted governance evidence.
    """

    overall_status: EvidenceStatus
    schema_supported: bool
    integrity_valid: bool = False
    audit_chain_valid: bool = False
    audit_present: bool = False
    signer_verified: bool = False
    signer_trusted: bool = False
    authority_evidence_verified: bool = False
    checks: List[CheckResult] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    failures: List[str] = field(default_factory=list)
    bundle_id: Optional[str] = None
    decision_id: Optional[str] = None
    outcome: Optional[str] = None

    @property
    def trusted(self) -> bool:
        """True only when this is trusted governance evidence."""
        return self.overall_status in TRUSTED_STATUSES

    # Backwards-friendly alias; equals ``trusted`` (trusted governance evidence).
    @property
    def valid(self) -> bool:
        return self.trusted

    def check(self, name: str) -> Optional[CheckResult]:
        return next((c for c in self.checks if c.name == name), None)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "overall_status": self.overall_status.value,
            "trusted": self.trusted,
            "schema_supported": self.schema_supported,
            "integrity_valid": self.integrity_valid,
            "audit_chain_valid": self.audit_chain_valid,
            "audit_present": self.audit_present,
            "signer_verified": self.signer_verified,
            "signer_trusted": self.signer_trusted,
            "authority_evidence_verified": self.authority_evidence_verified,
            "bundle_id": self.bundle_id,
            "decision_id": self.decision_id,
            "outcome": self.outcome,
            "checks": [c.to_dict() for c in self.checks],
            "warnings": list(self.warnings),
            "failures": list(self.failures),
        }


class EvidenceError(Exception):
    """Base error for the evidence subsystem (export/verify problems)."""


class IncompleteEvidenceError(EvidenceError):
    """Export refused because required evidence was missing or inconsistent."""


class BundleFormatError(EvidenceError):
    """A bundle could not be read (corrupt archive, unreadable manifest, …)."""
