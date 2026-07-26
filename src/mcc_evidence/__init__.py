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

Since Wave C (PR #65), this package also produces and verifies MCC-TC-001
Technical Certificates (``tc001_certificate.py``): a minimal Certificate
model, producer, and fail-closed verifier binding one Technical Certificate
to exactly one Certification Manifest (Wave B), which is itself bound to
exactly one Evidence Bundle (Wave A) -- the full transitive chain Evidence
Bundle → Certification Manifest → Technical Certificate. Reuses this
package's own ``HashReference`` / ``verify_cm001_manifest`` /
``verify_eb001_bundle`` and ``mcc_core.signing`` (Ed25519) directly; the
Trust Anchor and Revocation Registry constructs are new, minimal,
Technical-Certificate-scoped, and never import ``gateway`` / runtime
governance internals -- see ``tc001_certificate.py``'s module docstring.
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
from .tc001_certificate import (
    SUPPORTED_SIGNATURE_ALGORITHMS,
    SUPPORTED_TC001_CERT_SCHEMA_VERSIONS,
    TC001_CERT_SCHEMA_VERSION,
    CertEvidenceBundleReference,
    CertificationResult,
    IncompleteTC001CertificateError,
    CertificateIdRegistry,
    ManifestReference,
    RevocationRecord,
    RevocationRegistry,
    TC001Error,
    TC001Status,
    TC001StructuralError,
    TC001VerificationResult,
    TechnicalCertificate,
    TrustAnchor,
    TrustAnchorRegistry,
    build_direct_evidence_bundle_reference,
    build_technical_certificate,
    read_tc001_certificate,
    revoke_certificate,
    sign_technical_certificate,
    verify_technical_certificate,
    write_tc001_certificate,
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
    # MCC-TC-001 Technical Certificate (Wave C). Minimal model only; see
    # tc001_certificate.py's module docstring for what is explicitly
    # deferred to a future wave.
    "TC001_CERT_SCHEMA_VERSION",
    "SUPPORTED_TC001_CERT_SCHEMA_VERSIONS",
    "SUPPORTED_SIGNATURE_ALGORITHMS",
    "TC001Error",
    "IncompleteTC001CertificateError",
    "TC001StructuralError",
    "TC001Status",
    "CertificationResult",
    "ManifestReference",
    "CertEvidenceBundleReference",
    "build_direct_evidence_bundle_reference",
    "TrustAnchor",
    "TrustAnchorRegistry",
    "RevocationRecord",
    "RevocationRegistry",
    "revoke_certificate",
    "CertificateIdRegistry",
    "TechnicalCertificate",
    "build_technical_certificate",
    "sign_technical_certificate",
    "write_tc001_certificate",
    "read_tc001_certificate",
    "TC001VerificationResult",
    "verify_technical_certificate",
]
