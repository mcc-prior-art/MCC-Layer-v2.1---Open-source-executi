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

Since Wave A of the MCC Normative v1.0 Certification Program (PR #63), this
package also produces and verifies a second, explicitly distinct bundle
schema: the MCC-EB-001 Evidence Bundle (``EB001_SCHEMA_VERSION``,
``build_eb001_bundle`` / ``verify_eb001_bundle``), which substantiates a
*certification* decision rather than a runtime governance decision. The two
schemas coexist deliberately and never interpret each other's files -- see
``eb001_schema.py``'s module docstring and
``conformance/normative-v1.0/remediation/`` for the full rationale. The
MCC-CM-001 structured Hash Reference (``HashReference`` /
``compute_hash_reference`` / ``verify_hash_reference``) is a new, reusable
primitive introduced for the MCC-EB-001 Integrity Record; the pre-existing
Governance Evidence Bundle's own digest fields are unchanged (still bare
``sha256:<hex>`` strings in its manifest) to preserve exact backward
compatibility.
"""

from __future__ import annotations

from .cm001_manifest import (
    CM001_MANIFEST_SCHEMA_VERSION,
    SUPPORTED_CM001_MANIFEST_SCHEMA_VERSIONS,
    CM001Error,
    CM001Manifest,
    CM001ManifestVerificationResult,
    CM001Status,
    EvidenceBundleReference,
    EvidenceBundleReferenceKind,
    EvidenceBundleReferenceVerificationResult,
    IncompleteCM001ManifestError,
    build_cm001_manifest,
    build_evidence_bundle_reference,
    read_cm001_manifest,
    verify_cm001_manifest,
    verify_evidence_bundle_reference,
    write_cm001_manifest,
)
from .eb001_export import EB001BundleInput, EvidenceItemInput, build_eb001_bundle
from .eb001_schema import (
    EB001_SCHEMA_VERSION,
    SUPPORTED_EB001_SCHEMA_VERSIONS,
    EB001Error,
    EB001Status,
    EB001VerificationResult,
    IncompleteEB001BundleError,
)
from .eb001_verify import verify_eb001_bundle
from .export import EvidenceInput, build_manifest, export_bundle, read_manifest_from
from .hash_reference import (
    SUPPORTED_HASH_ALGORITHMS,
    HashReference,
    HashReferenceError,
    compute_hash_reference,
    verify_hash_reference,
)
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
    # MCC-CM-001 Hash Reference (Wave A) -- reusable by a future Wave B.
    "HashReference",
    "HashReferenceError",
    "SUPPORTED_HASH_ALGORITHMS",
    "compute_hash_reference",
    "verify_hash_reference",
    # MCC-EB-001 Evidence Bundle (Wave A) -- distinct schema/artifact from the
    # Governance Evidence Bundle above; see eb001_schema.py's module docstring.
    "EB001_SCHEMA_VERSION",
    "SUPPORTED_EB001_SCHEMA_VERSIONS",
    "EB001Status",
    "EB001VerificationResult",
    "EB001Error",
    "IncompleteEB001BundleError",
    "EvidenceItemInput",
    "EB001BundleInput",
    "build_eb001_bundle",
    "verify_eb001_bundle",
    # MCC-CM-001 Certification Manifest -- Evidence Bundle Reference (Wave B).
    # Minimal container only; see cm001_manifest.py's module docstring for
    # what is explicitly deferred to a future wave.
    "CM001_MANIFEST_SCHEMA_VERSION",
    "SUPPORTED_CM001_MANIFEST_SCHEMA_VERSIONS",
    "CM001Status",
    "CM001Error",
    "IncompleteCM001ManifestError",
    "EvidenceBundleReferenceKind",
    "EvidenceBundleReference",
    "CM001Manifest",
    "EvidenceBundleReferenceVerificationResult",
    "CM001ManifestVerificationResult",
    "build_evidence_bundle_reference",
    "build_cm001_manifest",
    "write_cm001_manifest",
    "read_cm001_manifest",
    "verify_evidence_bundle_reference",
    "verify_cm001_manifest",
]
