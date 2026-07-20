"""MCC-Core Governance Evidence Bundle — portable, offline-verifiable evidence.

A **downstream, observational** layer over MCC-Core's existing signed decision
tokens, hash-chain audit log and execution receipts. It exports evidence of an
already-completed governance path into a versioned, deterministic bundle and
verifies such a bundle offline, without trusting the application that produced
it.

    Proposal → MCC decision → verified authority → gate enforcement →
    execution or denial → portable evidence bundle → independent verification

It creates no authority, alters no verdict, authorizes no execution, and is never
part of the execution decision. Export and verification are read-only.
"""

from __future__ import annotations

from .export import EvidenceInput, build_manifest, export_bundle, read_manifest_from
from .schema import (
    BUNDLE_SCHEMA_VERSION,
    SUPPORTED_SCHEMA_VERSIONS,
    BundleFormatError,
    CheckResult,
    CheckStatus,
    EvidenceError,
    EvidenceStatus,
    IncompleteEvidenceError,
    Outcome,
    VerificationResult,
)
from .verify import verify_bundle

__all__ = [
    "BUNDLE_SCHEMA_VERSION",
    "SUPPORTED_SCHEMA_VERSIONS",
    "EvidenceInput",
    "export_bundle",
    "build_manifest",
    "read_manifest_from",
    "verify_bundle",
    "VerificationResult",
    "CheckResult",
    "CheckStatus",
    "EvidenceStatus",
    "Outcome",
    "EvidenceError",
    "IncompleteEvidenceError",
    "BundleFormatError",
]
