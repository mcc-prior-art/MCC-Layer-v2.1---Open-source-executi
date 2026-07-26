"""MCC-TC-001 Technical Certificate — Certificate Model, Schema, Signature,
Trust, Revocation, and Verification (Wave C).

Implements a minimal, real, end-to-end Technical Certificate producer and
fail-closed verifier binding a single Technical Certificate to exactly one
Certification Manifest (Wave B, ``cm001_manifest.py``), which is itself
bound to exactly one Evidence Bundle (Wave A, ``eb001_export.py`` /
``eb001_verify.py``) — the full transitive chain Evidence Bundle →
Certification Manifest → Technical Certificate required by MCC-TC-001
Section 3.3 and verified per Section 15.5.

Reuses, without duplication:

- ``mcc_core.signing`` (``SigningKey``, ``verify_token``, ``canonical_bytes``)
  for Ed25519 signing/verification (Section 14) — the same primitive every
  other signed artifact in this repository uses. No second signature
  implementation.
- ``hash_reference.py`` (``HashReference``, ``compute_hash_reference``,
  ``verify_hash_reference``) for every Digest binding (Section 13).
- ``cm001_manifest.py`` (``read_cm001_manifest``, ``verify_cm001_manifest``,
  ``verify_evidence_bundle_reference``) to resolve and verify the
  referenced Certification Manifest and, transitively, its Evidence Bundle
  Reference — never re-implemented here.
- ``eb001_schema.py`` / ``eb001_verify.py`` for Evidence Bundle identity and
  structural verification.

Trust Anchors (Section 16) and the Revocation Registry (Section 12) are
new, minimal, in-memory constructs scoped to Technical Certificates. They
are deliberately NOT ``gateway.trust.TrustSet`` / a runtime revocation
registry: MCC-TC-001 Section 3.4 draws Technical Certificates as a distinct
trust domain from MCC-Core runtime governance, and this package's own
layering rule (see ``__init__.py``) is that ``mcc_evidence`` never imports
``gateway`` / ``mcc_core.gate`` / ``mcc_core.authority`` / executor
internals. This module does not do so. Both constructs implement only the
normative *content and effect* MCC-TC-001 requires (Sections 12.6, 16.2) —
this specification explicitly declines to mandate a specific persistence,
distribution, or revocation-registry technology (Section 12.6), so no
Redis-backed or otherwise durable backend is introduced here; that remains
a legitimate, separate, future extension, exactly as MCC-CM-001's full
Certification Metadata and Requirement Results remain deferred past Wave B.

Explicitly NOT implemented by this module (see the Wave C scope manifest
for the full, requirement-ID-linked rationale):

- the Extension Model (Section 20) — no extension-declaration mechanism
  exists anywhere in this repository yet (also true, cross-cuttingly, of
  MCC-CP-001/EB-001/CM-001's own Extension Models);
- Subject/Result cross-verification against the Certification Manifest
  (Sections 8.3, 9.3, 15.6, in part) — Wave B's minimal ``CM001Manifest``
  carries no Certification Metadata (no subject or result field) to check
  against; the Certificate's own self-consistency (exactly one Subject,
  result == PASS) is fully implemented and verified.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field, replace
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

from mcc_core.signing import SigningKey, canonical_bytes, verify_token

from .cm001_manifest import (
    EvidenceBundleReference as _CMEvidenceBundleReference,
    EvidenceBundleReferenceKind as _CMEvidenceBundleReferenceKind,
    read_cm001_manifest,
    verify_cm001_manifest,
    verify_evidence_bundle_reference as _cm_verify_evidence_bundle_reference,
)
from .eb001_schema import BUNDLE_DESCRIPTOR_NAME, INTEGRITY_RECORD_NAME
from .hash_reference import (
    HashReference,
    HashReferenceError,
    compute_hash_reference,
    verify_hash_reference,
)
from .schema import CheckResult, CheckStatus

#: Certificate Schema Version for this minimal MCC-TC-001 model. Distinct
#: from CM001_MANIFEST_SCHEMA_VERSION ("mcc-cm-001/1"), EB001_SCHEMA_VERSION
#: ("mcc-eb-001/1"), and MCC-CP-001's own specification version (TC-VSN-003).
TC001_CERT_SCHEMA_VERSION = "mcc-tc-001/1"
SUPPORTED_TC001_CERT_SCHEMA_VERSIONS = frozenset({TC001_CERT_SCHEMA_VERSION})

#: The only signature algorithm this minimal model issues or accepts —
#: Ed25519, the specification's RECOMMENDED reference algorithm (Section
#: 14.2), reused from mcc_core.signing. A closed set: never a symmetric-key
#: or shared-secret authentication mechanism (TC-SIG-002).
SUPPORTED_SIGNATURE_ALGORITHMS = frozenset({"Ed25519"})


class TC001Error(Exception):
    """Base error for Wave C production and registry operations."""


class IncompleteTC001CertificateError(TC001Error):
    """Production refused — no partial or internally inconsistent
    Technical Certificate is ever built, signed, or written."""


class TC001StructuralError(TC001Error):
    """Section 15.2: a Technical Certificate fails structural verification.
    Raised by ``TechnicalCertificate.from_dict``; ``verify_technical_certificate``
    catches this specifically as the first, mandatory verification step."""


class TC001Status(str, Enum):
    """Fail-closed overall verification outcome (Section 15.8): there is no
    partial-pass status."""

    VALID = "VALID"
    INVALID = "INVALID"
    UNSUPPORTED_SCHEMA = "UNSUPPORTED_SCHEMA"


class CertificationResult(str, Enum):
    """Section 9.2: "No Certificate model exists for a FAIL outcome, since
    Certificates are never issued for a FAIL certification result." PASS is
    deliberately the only member — there is no value a producer could set
    to represent FAIL (TC-RES-001, TC-MODEL-001, TC-CONF-002)."""

    PASS = "PASS"


# ---------------------------------------------------------------------------
# Manifest Reference / direct Evidence Bundle Reference (Section 6.5 / 6.6)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ManifestReference:
    """Section 6.5: identifies, and Hash-Reference-binds to, exactly one
    Certification Manifest (TC-RFLD-004)."""

    manifest_id: str
    manifest_schema_version: str
    hash_reference: HashReference

    def to_dict(self) -> Dict[str, Any]:
        return {
            "manifest_id": self.manifest_id,
            "manifest_schema_version": self.manifest_schema_version,
            "hash_reference": self.hash_reference.to_dict(),
        }

    @classmethod
    def from_dict(cls, d: Any) -> "ManifestReference":
        if not isinstance(d, dict):
            raise TC001StructuralError("Manifest Reference must be a JSON object")
        for f in ("manifest_id", "manifest_schema_version", "hash_reference"):
            if f not in d:
                raise TC001StructuralError(f"Manifest Reference missing required field {f!r}")
        if not isinstance(d["manifest_id"], str) or not d["manifest_id"]:
            raise TC001StructuralError("Manifest Reference manifest_id must be a non-empty string")
        if not isinstance(d["manifest_schema_version"], str) or not d["manifest_schema_version"]:
            raise TC001StructuralError("Manifest Reference manifest_schema_version must be a non-empty string")
        try:
            hash_reference = HashReference.from_dict(d["hash_reference"])
        except HashReferenceError as e:
            raise TC001StructuralError(f"Manifest Reference hash_reference invalid: {e}") from e
        return cls(
            manifest_id=d["manifest_id"],
            manifest_schema_version=d["manifest_schema_version"],
            hash_reference=hash_reference,
        )


@dataclass(frozen=True)
class CertEvidenceBundleReference:
    """Section 6.6: the Certificate's DIRECT Evidence Bundle Reference —
    distinct Certificate content, never satisfiable only by transitive
    resolution through the Manifest (TC-RFLD-006)."""

    bundle_id: str
    schema_version: str
    hash_reference: HashReference

    def to_dict(self) -> Dict[str, Any]:
        return {
            "bundle_id": self.bundle_id,
            "schema_version": self.schema_version,
            "hash_reference": self.hash_reference.to_dict(),
        }

    @classmethod
    def from_dict(cls, d: Any) -> "CertEvidenceBundleReference":
        if not isinstance(d, dict):
            raise TC001StructuralError("Evidence Bundle Reference must be a JSON object")
        for f in ("bundle_id", "schema_version", "hash_reference"):
            if f not in d:
                raise TC001StructuralError(f"Evidence Bundle Reference missing required field {f!r}")
        if not isinstance(d["bundle_id"], str) or not d["bundle_id"]:
            raise TC001StructuralError("Evidence Bundle Reference bundle_id must be a non-empty string")
        if not isinstance(d["schema_version"], str) or not d["schema_version"]:
            raise TC001StructuralError("Evidence Bundle Reference schema_version must be a non-empty string")
        try:
            hash_reference = HashReference.from_dict(d["hash_reference"])
        except HashReferenceError as e:
            raise TC001StructuralError(f"Evidence Bundle Reference hash_reference invalid: {e}") from e
        return cls(bundle_id=d["bundle_id"], schema_version=d["schema_version"], hash_reference=hash_reference)


def build_direct_evidence_bundle_reference(bundle_path: Path | str) -> CertEvidenceBundleReference:
    """Build the Certificate's direct Evidence Bundle Reference (Section
    6.6) from a real MCC-EB-001 Bundle: identifier and Schema Version come
    from the Bundle's own Bundle Descriptor, and the Hash Reference binds to
    the Bundle's actual Integrity Record bytes — the same binding convention
    Wave B's ``build_evidence_bundle_reference`` uses for the Manifest-side
    reference, reused here for the Certificate-side direct reference."""
    bundle_path = Path(bundle_path)
    descriptor_path = bundle_path / BUNDLE_DESCRIPTOR_NAME
    integrity_path = bundle_path / INTEGRITY_RECORD_NAME
    if not descriptor_path.exists() or not integrity_path.exists():
        raise IncompleteTC001CertificateError(
            f"cannot build a direct Evidence Bundle Reference: {bundle_path} is not a readable MCC-EB-001 Bundle"
        )
    descriptor = json.loads(descriptor_path.read_bytes())
    bundle_id = descriptor.get("bundle_id")
    schema_version = descriptor.get("schema_version")
    if not bundle_id or not schema_version:
        raise IncompleteTC001CertificateError(
            f"Bundle Descriptor at {bundle_path} is missing bundle_id or schema_version"
        )
    integrity_bytes = integrity_path.read_bytes()
    ref = compute_hash_reference(integrity_bytes, content_ref=bundle_id)
    return CertEvidenceBundleReference(bundle_id=bundle_id, schema_version=schema_version, hash_reference=ref)


# ---------------------------------------------------------------------------
# Trust Model (Section 16)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class TrustAnchor:
    """Section 16.2: a verification key associated with an Issuer that a
    verifier relies upon to authenticate a Technical Certificate's
    Signature. A distinct trust domain from ``gateway.trust.TrustSet``
    (runtime governance mandate/approval trust) per Section 3.4 — this
    module holds no reference to, and imports nothing from, ``gateway``."""

    issuer_id: str
    kid: str
    public_key: Ed25519PublicKey
    revoked: bool = False


class TrustAnchorRegistry:
    """The set of Trust Anchors a verifier recognizes (Sections 16.2–16.5).
    Fail-closed: an unrecognized or revoked key id resolves to nothing
    (TC-TRUST-001); trust is never inferred from a Certificate's
    self-declared ``issuer_id`` alone (TC-TRUST-002) — callers must resolve
    by ``kid`` and independently compare the resolved anchor's
    ``issuer_id`` against the Certificate's declared one."""

    def __init__(self, anchors: Optional[List[TrustAnchor]] = None) -> None:
        self._by_kid: Dict[str, TrustAnchor] = {}
        for a in anchors or []:
            self.add(a)

    def add(self, anchor: TrustAnchor) -> None:
        if anchor.kid in self._by_kid:
            raise TC001Error(f"duplicate Trust Anchor kid {anchor.kid!r}")
        self._by_kid[anchor.kid] = anchor

    def resolve(self, kid: Optional[str]) -> Optional[TrustAnchor]:
        if not kid:
            return None
        anchor = self._by_kid.get(kid)
        if anchor is None or anchor.revoked:
            return None
        return anchor

    def revoke_key(self, kid: str) -> None:
        """Section 16.4: rotation/revocation of a Trust Anchor. Ceases
        recognizing ``kid`` for *new* verification without erasing it from
        the registry or altering any previously-issued Certificate's
        content — the historical fact of issuance is untouched
        (TC-TRUST-003); only future ``resolve()`` calls are affected."""
        anchor = self._by_kid.get(kid)
        if anchor is None:
            raise TC001Error(f"cannot revoke unknown Trust Anchor kid {kid!r}")
        self._by_kid[kid] = replace(anchor, revoked=True)


# ---------------------------------------------------------------------------
# Revocation Model (Section 12)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class RevocationRecord:
    """Section 12.3: identifies the revoked Certificate, the revocation
    timestamp, and the authorizing Issuer."""

    certificate_id: str
    revoked_at: int
    issuer_id: str
    reason: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {
            "certificate_id": self.certificate_id,
            "revoked_at": self.revoked_at,
            "issuer_id": self.issuer_id,
        }
        if self.reason is not None:
            d["reason"] = self.reason
        return d


class RevocationRegistry:
    """Section 12.6: "This specification does NOT define a specific
    revocation registry technology or distribution mechanism; it defines
    only the normative content and effect of a Revocation Record." This is
    a minimal, in-memory implementation of exactly that content and effect
    — not a persistence or distribution mechanism, which remains a
    legitimate future extension (analogous to ``mcc_core.nonce`` /
    ``idempotency`` / ``mandate`` shipping both InMemory and Redis-backed
    registries at the runtime-governance layer; this module imports none
    of them)."""

    def __init__(self) -> None:
        self._records: Dict[str, RevocationRecord] = {}

    def revoke(self, record: RevocationRecord, *, issuing_trust_anchor: TrustAnchor) -> RevocationRecord:
        # TC-REV-004: only the Issuer that issued the Certificate, or its
        # designated authority, may produce a valid Revocation Record —
        # enforced here by requiring a currently-resolved TrustAnchor whose
        # issuer_id matches the record's declared issuer_id.
        if issuing_trust_anchor.issuer_id != record.issuer_id:
            raise TC001Error(
                f"revocation refused: record issuer_id {record.issuer_id!r} does not match the "
                f"authorizing Trust Anchor's issuer_id {issuing_trust_anchor.issuer_id!r}"
            )
        # TC-REV-001: a Certificate is never mutated to represent
        # revocation; a Revocation Record, once recorded, is not replaced.
        existing = self._records.get(record.certificate_id)
        if existing is not None:
            return existing
        self._records[record.certificate_id] = record
        return record

    def get(self, certificate_id: str) -> Optional[RevocationRecord]:
        # TC-REV-006: revoked Certificates and their Revocation Records
        # remain available for audit/traceability — this is a plain lookup,
        # never a destructive/erasing operation.
        return self._records.get(certificate_id)

    def is_revoked(self, certificate_id: str) -> bool:
        return certificate_id in self._records


def revoke_certificate(
    registry: RevocationRegistry,
    certificate_id: str,
    revoked_at: int,
    *,
    issuing_trust_anchor: TrustAnchor,
    reason: Optional[str] = None,
) -> RevocationRecord:
    record = RevocationRecord(
        certificate_id=certificate_id, revoked_at=revoked_at,
        issuer_id=issuing_trust_anchor.issuer_id, reason=reason,
    )
    return registry.revoke(record, issuing_trust_anchor=issuing_trust_anchor)


# ---------------------------------------------------------------------------
# Certificate Identity uniqueness (Section 5.3, TC-ID-002/003)
# ---------------------------------------------------------------------------


class CertificateIdRegistry:
    """Tracks certificate identifiers already issued by this producer
    process, enforcing at the point of issuance that a certificate
    identifier is never reused, including after revocation (TC-ID-002). A
    single-process, in-memory implementation — true global uniqueness
    across independent Issuers is a deployment/distribution concern this
    specification does not mandate a mechanism for (Section 16.1/12.6's
    same pattern), and is documented as a limitation, not silently assumed."""

    def __init__(self) -> None:
        self._issued: Set[str] = set()

    def reserve(self, certificate_id: str) -> None:
        if certificate_id in self._issued:
            raise IncompleteTC001CertificateError(
                f"refusing to issue: certificate_id {certificate_id!r} has already been used by this "
                "Issuer (TC-ID-002: identifiers MUST NOT be reused, including after revocation)"
            )
        self._issued.add(certificate_id)


# ---------------------------------------------------------------------------
# Technical Certificate (Sections 4, 5, 6, 7, 8, 9, 10, 11)
# ---------------------------------------------------------------------------

_REQUIRED_FIELDS: Tuple[str, ...] = (
    "certificate_schema_version",
    "certificate_id",
    "cp001_specification_version",
    "subject_id",
    "certification_result",
    "certified_capability_profiles",
    "manifest_reference",
    "evidence_bundle_reference",
    "issuer_id",
    "signature_algorithm",
    "issuance_timestamp",
    "kid",
    "sig",
)
_OPTIONAL_FIELDS: Tuple[str, ...] = ("expiration_timestamp", "label", "superseded_certificate_ids")
_ALL_ALLOWED_FIELDS = frozenset(_REQUIRED_FIELDS + _OPTIONAL_FIELDS)


@dataclass
class TechnicalCertificate:
    """The complete Technical Certificate document (Section 4.2). A single
    structured, machine-readable document (TC-SCHEMA-001) with a closed
    field set — any field outside ``_ALL_ALLOWED_FIELDS`` is rejected by
    structural verification, since no Extension Model is implemented by
    this wave (see the module docstring)."""

    certificate_id: str
    subject_id: str
    cp001_specification_version: str
    certification_result: str
    certified_capability_profiles: Tuple[str, ...]
    manifest_reference: ManifestReference
    evidence_bundle_reference: CertEvidenceBundleReference
    issuer_id: str
    issuance_timestamp: int
    certificate_schema_version: str = TC001_CERT_SCHEMA_VERSION
    signature_algorithm: str = "Ed25519"
    expiration_timestamp: Optional[int] = None
    label: Optional[str] = None
    superseded_certificate_ids: Optional[Tuple[str, ...]] = None
    kid: Optional[str] = None
    sig: Optional[str] = None

    @property
    def is_signed(self) -> bool:
        return self.kid is not None and self.sig is not None

    def unsigned_dict(self) -> Dict[str, Any]:
        """Canonical Form input for signing/verification — excludes the
        Signature field (``kid``/``sig``) per TC-SCHEMA-004."""
        d: Dict[str, Any] = {
            "certificate_schema_version": self.certificate_schema_version,
            "certificate_id": self.certificate_id,
            "cp001_specification_version": self.cp001_specification_version,
            "subject_id": self.subject_id,
            "certification_result": self.certification_result,
            "certified_capability_profiles": list(self.certified_capability_profiles),
            "manifest_reference": self.manifest_reference.to_dict(),
            "evidence_bundle_reference": self.evidence_bundle_reference.to_dict(),
            "issuer_id": self.issuer_id,
            "signature_algorithm": self.signature_algorithm,
            "issuance_timestamp": self.issuance_timestamp,
        }
        if self.expiration_timestamp is not None:
            d["expiration_timestamp"] = self.expiration_timestamp
        if self.label is not None:
            d["label"] = self.label
        if self.superseded_certificate_ids is not None:
            d["superseded_certificate_ids"] = list(self.superseded_certificate_ids)
        return d

    def to_dict(self) -> Dict[str, Any]:
        d = self.unsigned_dict()
        if self.kid is not None:
            d["kid"] = self.kid
        if self.sig is not None:
            d["sig"] = self.sig
        return d

    @classmethod
    def from_dict(cls, d: Any) -> "TechnicalCertificate":
        """Section 15.2 Structural Verification. Raises
        :class:`TC001StructuralError` — never returns a partially-valid
        object — on any missing Required Field, undeclared field, or
        type ambiguity (TC-SCHEMA-002, TC-RFLD-003)."""
        if not isinstance(d, dict):
            raise TC001StructuralError("Technical Certificate must be a JSON object")

        unknown = set(d) - _ALL_ALLOWED_FIELDS
        if unknown:
            raise TC001StructuralError(f"Technical Certificate contains undeclared field(s): {sorted(unknown)}")
        missing = [f for f in _REQUIRED_FIELDS if f not in d]
        if missing:
            raise TC001StructuralError(f"Technical Certificate missing required field(s): {missing}")

        if d["certificate_schema_version"] not in SUPPORTED_TC001_CERT_SCHEMA_VERSIONS:
            raise TC001StructuralError(
                f"unsupported certificate_schema_version {d['certificate_schema_version']!r}"
            )
        if not isinstance(d["certificate_id"], str) or not d["certificate_id"]:
            raise TC001StructuralError("certificate_id must be a non-empty string")
        if not isinstance(d["cp001_specification_version"], str) or not d["cp001_specification_version"]:
            raise TC001StructuralError("cp001_specification_version must be a non-empty string")
        if not isinstance(d["subject_id"], str) or not d["subject_id"]:
            raise TC001StructuralError("subject_id must be a non-empty string")
        if d["certification_result"] != CertificationResult.PASS.value:
            raise TC001StructuralError(
                f"certification_result must be {CertificationResult.PASS.value!r} — no Certificate model "
                f"exists for a non-PASS result (Section 9.2); got {d['certification_result']!r}"
            )
        profiles = d["certified_capability_profiles"]
        if not isinstance(profiles, list) or not profiles or not all(
            isinstance(p, str) and p for p in profiles
        ):
            raise TC001StructuralError(
                "certified_capability_profiles must be a non-empty array of non-empty strings"
            )
        if not isinstance(d["issuer_id"], str) or not d["issuer_id"]:
            raise TC001StructuralError("issuer_id must be a non-empty string")
        if d["signature_algorithm"] not in SUPPORTED_SIGNATURE_ALGORITHMS:
            raise TC001StructuralError(f"unsupported signature_algorithm {d['signature_algorithm']!r}")
        if not isinstance(d["issuance_timestamp"], int) or isinstance(d["issuance_timestamp"], bool):
            raise TC001StructuralError("issuance_timestamp must be an integer (unix seconds)")
        if not isinstance(d["kid"], str) or not d["kid"]:
            raise TC001StructuralError("kid must be a non-empty string")
        if not isinstance(d["sig"], str) or not d["sig"]:
            raise TC001StructuralError("sig must be a non-empty string")

        expiration_timestamp = d.get("expiration_timestamp")
        if expiration_timestamp is not None and (
            not isinstance(expiration_timestamp, int) or isinstance(expiration_timestamp, bool)
        ):
            raise TC001StructuralError("expiration_timestamp must be an integer (unix seconds) when present")
        label = d.get("label")
        if label is not None and not isinstance(label, str):
            raise TC001StructuralError("label must be a string when present")
        superseded = d.get("superseded_certificate_ids")
        if superseded is not None and (
            not isinstance(superseded, list) or not all(isinstance(s, str) and s for s in superseded)
        ):
            raise TC001StructuralError(
                "superseded_certificate_ids must be an array of non-empty strings when present"
            )

        manifest_reference = ManifestReference.from_dict(d["manifest_reference"])
        evidence_bundle_reference = CertEvidenceBundleReference.from_dict(d["evidence_bundle_reference"])

        return cls(
            certificate_schema_version=d["certificate_schema_version"],
            certificate_id=d["certificate_id"],
            cp001_specification_version=d["cp001_specification_version"],
            subject_id=d["subject_id"],
            certification_result=d["certification_result"],
            certified_capability_profiles=tuple(profiles),
            manifest_reference=manifest_reference,
            evidence_bundle_reference=evidence_bundle_reference,
            issuer_id=d["issuer_id"],
            signature_algorithm=d["signature_algorithm"],
            issuance_timestamp=d["issuance_timestamp"],
            expiration_timestamp=expiration_timestamp,
            label=label,
            superseded_certificate_ids=tuple(superseded) if superseded is not None else None,
            kid=d["kid"],
            sig=d["sig"],
        )


# ---------------------------------------------------------------------------
# Producer (Section 3.2, 6, 21.2)
# ---------------------------------------------------------------------------


def build_technical_certificate(
    *,
    certificate_id: str,
    subject_id: str,
    cp001_specification_version: str,
    certified_capability_profiles: Tuple[str, ...],
    manifest_path: Path | str,
    manifest_id: str,
    primary_evidence_bundle_path: Path | str,
    supplementary_evidence_bundle_paths: Optional[Dict[str, Path | str]] = None,
    issuer_id: str,
    issuance_timestamp: int,
    expiration_timestamp: Optional[int] = None,
    label: Optional[str] = None,
    superseded_certificate_ids: Optional[Tuple[str, ...]] = None,
    id_registry: Optional[CertificateIdRegistry] = None,
) -> TechnicalCertificate:
    """Build an unsigned Technical Certificate for a PASS certification
    outcome. Fails closed (raises :class:`IncompleteTC001CertificateError`)
    rather than building a partial or inconsistent Certificate:

    - refuses unless the Certification Manifest at ``manifest_path`` is
      itself independently verifiable (``verify_cm001_manifest`` ==
      VALID) against the supplied Evidence Bundle path(s) (TC-CONF-005);
    - refuses unless the Certificate's own direct Evidence Bundle
      Reference and the Manifest's primary Evidence Bundle Reference
      identify the exact same Evidence Bundle, checked *before* signing
      (Section 3.3 / TC-CONF-005 / TC-VERIFY-006);
    - refuses an empty ``certified_capability_profiles`` (TC-RES-003 has
      nothing to record);
    - refuses a reused ``certificate_id`` when an ``id_registry`` is
      supplied (TC-ID-002).

    There is no ``certification_result`` parameter: this producer can only
    ever build a PASS Certificate (TC-CONF-002); a FAIL outcome has no
    Certificate representation at all (Section 9.2).
    """
    if id_registry is not None:
        id_registry.reserve(certificate_id)

    manifest_path = Path(manifest_path)
    if not manifest_path.exists():
        raise IncompleteTC001CertificateError(f"Certification Manifest not found at {manifest_path}")
    manifest_bytes = manifest_path.read_bytes()
    try:
        manifest = read_cm001_manifest(manifest_path)
    except HashReferenceError as e:
        raise IncompleteTC001CertificateError(f"Certification Manifest at {manifest_path} is malformed: {e}") from e

    manifest_result = verify_cm001_manifest(
        manifest, primary_evidence_bundle_path, supplementary_evidence_bundle_paths,
    )
    if not manifest_result.valid:
        raise IncompleteTC001CertificateError(
            "refusing to issue a Technical Certificate for an unverifiable Certification Manifest: "
            f"{manifest_result.failures}"
        )

    direct_eb_ref = build_direct_evidence_bundle_reference(primary_evidence_bundle_path)
    manifest_primary = manifest.primary_evidence_bundle_reference
    if (direct_eb_ref.bundle_id, direct_eb_ref.schema_version) != (
        manifest_primary.bundle_id, manifest_primary.schema_version,
    ):
        raise IncompleteTC001CertificateError(
            "refusing to issue: the Certificate's direct Evidence Bundle Reference "
            f"({direct_eb_ref.bundle_id!r}, {direct_eb_ref.schema_version!r}) does not identify the same "
            "Evidence Bundle as the Certification Manifest's primary Evidence Bundle Reference "
            f"({manifest_primary.bundle_id!r}, {manifest_primary.schema_version!r})"
        )

    if not certified_capability_profiles:
        raise IncompleteTC001CertificateError("certified_capability_profiles must not be empty")

    manifest_hash_reference = compute_hash_reference(manifest_bytes, content_ref=manifest_id)
    manifest_reference = ManifestReference(
        manifest_id=manifest_id,
        manifest_schema_version=manifest.manifest_schema_version,
        hash_reference=manifest_hash_reference,
    )

    return TechnicalCertificate(
        certificate_id=certificate_id,
        subject_id=subject_id,
        cp001_specification_version=cp001_specification_version,
        certification_result=CertificationResult.PASS.value,
        certified_capability_profiles=tuple(certified_capability_profiles),
        manifest_reference=manifest_reference,
        evidence_bundle_reference=direct_eb_ref,
        issuer_id=issuer_id,
        issuance_timestamp=issuance_timestamp,
        expiration_timestamp=expiration_timestamp,
        label=label,
        superseded_certificate_ids=superseded_certificate_ids,
    )


def sign_technical_certificate(cert: TechnicalCertificate, signing_key: SigningKey) -> TechnicalCertificate:
    """Section 14: signs the complete Canonical Form of the Certificate,
    excluding the Signature field, using ``mcc_core.signing.SigningKey``
    (Ed25519) — reused unchanged, no second signature implementation."""
    if cert.is_signed:
        raise TC001Error(
            "Certificate is already signed; a Technical Certificate is immutable after issuance (TC-REV-001) "
            "— build a new Certificate with a new certificate_id instead of re-signing this one"
        )
    signed = signing_key.sign_token(cert.unsigned_dict())
    return replace(cert, kid=signed["kid"], sig=signed["sig"])


def write_tc001_certificate(cert: TechnicalCertificate, dest: Path | str) -> Path:
    """Write the Certificate as one deterministic JSON document (Section
    4.2: "a single structured, machine-readable document")."""
    if not cert.is_signed:
        raise IncompleteTC001CertificateError("refusing to write an unsigned Technical Certificate")
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(canonical_bytes(cert.to_dict()))
    return dest


def read_tc001_certificate(path: Path | str) -> TechnicalCertificate:
    return TechnicalCertificate.from_dict(json.loads(Path(path).read_bytes()))


# ---------------------------------------------------------------------------
# Verification Procedure (Section 15)
# ---------------------------------------------------------------------------


@dataclass
class TC001VerificationResult:
    overall_status: TC001Status
    checks: List[CheckResult] = field(default_factory=list)
    failures: List[str] = field(default_factory=list)

    @property
    def valid(self) -> bool:
        return self.overall_status is TC001Status.VALID

    def check(self, name: str) -> Optional[CheckResult]:
        return next((c for c in self.checks if c.name == name), None)

    def to_dict(self) -> dict:
        return {
            "overall_status": self.overall_status.value,
            "valid": self.valid,
            "checks": [c.to_dict() for c in self.checks],
            "failures": list(self.failures),
        }


def verify_technical_certificate(
    raw_certificate: Any,
    *,
    trust_anchors: TrustAnchorRegistry,
    revocation_registry: RevocationRegistry,
    manifest_path: Path | str,
    primary_evidence_bundle_path: Path | str,
    supplementary_evidence_bundle_paths: Optional[Dict[str, Path | str]] = None,
    now: int,
) -> TC001VerificationResult:
    """Section 15: the complete, ordered, fail-closed verification
    procedure (TC-VERIFY-001..006). ``raw_certificate`` may be a ``dict``
    (as read from storage) or an already-built :class:`TechnicalCertificate`
    — either way, Structural Verification (15.2) is performed independently
    and first, never skipped because a caller already believes the object
    is well-formed (TC-VERIFY-002). Any single failing step rejects the
    whole Certificate (TC-VERIFY-005); there is no partial-pass outcome
    (TC-VERIFY-001)."""
    checks: List[CheckResult] = []
    failures: List[str] = []

    def add(name: str, status: CheckStatus, detail: str = "") -> None:
        checks.append(CheckResult(name, status, detail))
        if status is CheckStatus.FAIL:
            failures.append(f"{name}: {detail}")

    def invalid() -> TC001VerificationResult:
        return TC001VerificationResult(TC001Status.INVALID, checks, failures)

    # --- 15.2 Structural verification (MUST precede everything else) -------
    raw = raw_certificate.to_dict() if isinstance(raw_certificate, TechnicalCertificate) else raw_certificate
    schema_version = raw.get("certificate_schema_version") if isinstance(raw, dict) else None
    if schema_version not in SUPPORTED_TC001_CERT_SCHEMA_VERSIONS:
        add("schema_version_supported", CheckStatus.FAIL,
            f"unsupported or missing certificate_schema_version {schema_version!r}")
        return TC001VerificationResult(TC001Status.UNSUPPORTED_SCHEMA, checks, failures)
    try:
        cert = TechnicalCertificate.from_dict(raw)
    except TC001StructuralError as e:
        add("structural_verification", CheckStatus.FAIL, str(e))
        return invalid()
    add("structural_verification", CheckStatus.PASS, "all Required Fields present and well-typed")

    # --- 15.3 Signature verification ----------------------------------------
    anchor = trust_anchors.resolve(cert.kid)
    if anchor is None:
        add("signature_verification", CheckStatus.FAIL,
            f"kid {cert.kid!r} does not resolve to a recognized, currently-active Trust Anchor")
        return invalid()
    if not verify_token(cert.to_dict(), anchor.public_key):
        add("signature_verification", CheckStatus.FAIL,
            "Ed25519 signature does not verify against the resolved Trust Anchor")
        return invalid()
    if anchor.issuer_id != cert.issuer_id:
        add("signature_verification", CheckStatus.FAIL,
            f"declared issuer_id {cert.issuer_id!r} does not match the signing Trust Anchor's "
            f"issuer_id {anchor.issuer_id!r} — trust is never inferred from the self-declared issuer_id alone")
        return invalid()
    add("signature_verification", CheckStatus.PASS,
        f"signature verified against Trust Anchor kid={cert.kid!r} (issuer_id={anchor.issuer_id!r})")

    # --- 15.4 Manifest Reference verification -------------------------------
    manifest_path = Path(manifest_path)
    if not manifest_path.exists():
        add("manifest_reference_verification", CheckStatus.FAIL,
            f"referenced Certification Manifest not found at {manifest_path}")
        return invalid()
    manifest_bytes = manifest_path.read_bytes()
    try:
        manifest = read_cm001_manifest(manifest_path)
    except HashReferenceError as e:
        add("manifest_reference_verification", CheckStatus.FAIL,
            f"referenced Certification Manifest is malformed: {e}")
        return invalid()

    mr = cert.manifest_reference
    hr_problems = mr.hash_reference.validate()
    if hr_problems:
        add("manifest_reference_verification", CheckStatus.FAIL,
            f"Manifest Reference Hash Reference invalid: {'; '.join(hr_problems)}")
        return invalid()
    if mr.hash_reference.content_ref != mr.manifest_id:
        add("manifest_reference_verification", CheckStatus.FAIL,
            f"Manifest Reference Hash Reference content_ref {mr.hash_reference.content_ref!r} is not bound "
            f"to this Certificate's manifest_id {mr.manifest_id!r}")
        return invalid()
    if not verify_hash_reference(mr.hash_reference, manifest_bytes):
        add("manifest_reference_verification", CheckStatus.FAIL,
            "Manifest Reference digest does not match the actual Certification Manifest content "
            "(tampering, regeneration, or substitution)")
        return invalid()

    manifest_result = verify_cm001_manifest(
        manifest, primary_evidence_bundle_path, supplementary_evidence_bundle_paths,
    )
    if not manifest_result.valid:
        add("manifest_reference_verification", CheckStatus.FAIL,
            f"referenced Certification Manifest itself fails verification: {manifest_result.failures}")
        return invalid()
    add("manifest_reference_verification", CheckStatus.PASS,
        "Manifest Reference recomputes against the actual Manifest content and the referenced Manifest is itself VALID")

    # --- 15.5 Evidence Bundle Reference Consistency verification ------------
    ebr = cert.evidence_bundle_reference
    manifest_primary = manifest.primary_evidence_bundle_reference
    if (ebr.bundle_id, ebr.schema_version) != (manifest_primary.bundle_id, manifest_primary.schema_version):
        add("evidence_bundle_reference_consistency", CheckStatus.FAIL,
            f"direct Evidence Bundle Reference ({ebr.bundle_id!r}, {ebr.schema_version!r}) does not identify "
            f"the same Evidence Bundle as the Manifest's primary reference "
            f"({manifest_primary.bundle_id!r}, {manifest_primary.schema_version!r})")
        return invalid()
    direct_ref_as_cm = _CMEvidenceBundleReference(
        bundle_id=ebr.bundle_id, schema_version=ebr.schema_version,
        hash_references=(ebr.hash_reference,), kind=_CMEvidenceBundleReferenceKind.PRIMARY,
    )
    direct_result = _cm_verify_evidence_bundle_reference(direct_ref_as_cm, primary_evidence_bundle_path)
    if not direct_result.valid:
        add("evidence_bundle_reference_consistency", CheckStatus.FAIL,
            f"direct Evidence Bundle Reference unverifiable against the actual Evidence Bundle: "
            f"{direct_result.failures}")
        return invalid()
    add("evidence_bundle_reference_consistency", CheckStatus.PASS,
        "direct and Manifest-transitive Evidence Bundle References identify the same, independently-verified "
        "Evidence Bundle")

    # --- 15.6 Subject and Result Consistency (self-consistency only; see ----
    # --- module docstring for the documented Manifest-side exclusion) ------
    add("subject_and_result_self_consistency", CheckStatus.PASS,
        "Certificate identifies exactly one Subject and a PASS certification result (structural)")

    # --- 15.7 Validity and Revocation verification --------------------------
    if now < cert.issuance_timestamp:
        add("validity_period", CheckStatus.FAIL,
            f"now ({now}) precedes issuance_timestamp ({cert.issuance_timestamp}); not yet valid")
        return invalid()
    if cert.expiration_timestamp is not None and now > cert.expiration_timestamp:
        add("validity_period", CheckStatus.FAIL,
            f"now ({now}) is after expiration_timestamp ({cert.expiration_timestamp}); expired")
        return invalid()
    add("validity_period", CheckStatus.PASS, "current time is within the declared Validity Period")

    revocation = revocation_registry.get(cert.certificate_id)
    if revocation is not None:
        add("revocation_check", CheckStatus.FAIL,
            f"a Revocation Record exists (revoked_at={revocation.revoked_at}, issuer_id={revocation.issuer_id!r})")
        return invalid()
    add("revocation_check", CheckStatus.PASS, "no Revocation Record found for this certificate_id")

    # --- 15.8 Fail-closed: every applicable step above succeeded ------------
    return TC001VerificationResult(TC001Status.VALID, checks, failures)


__all__ = [
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
