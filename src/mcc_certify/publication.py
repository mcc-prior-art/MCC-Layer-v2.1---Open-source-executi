"""Certificate Publication Mechanism (PR #68) -- MCC-CP-001 Section 9.8 /
8.8 Publication.

CP-001's own Publication text is deliberately minimal and permissive:
"Certification outputs MAY be published. Publication SHALL NOT modify
certification results. Published artifacts SHALL remain reproducible."
No format is mandated. This module implements the smallest secure,
interoperable, offline, package-testable contract that satisfies exactly
that text:

- a canonical **Publication Record** per issued Technical Certificate,
  binding the certificate id, target id, issuer id/key id, Hash References
  to the Technical Certificate and Certification Manifest, an Evidence
  Bundle reference, status, timestamps, validity, and specification
  version;
- a canonical **Publication Index** collecting Publication Records,
  rejecting duplicate certificate ids and conflicting re-publication of the
  same certificate id with different content;
- offline verification of a record (or the whole index) against the real
  artifact bytes it references, reusing ``hash_reference.py`` directly --
  no second Hash Reference implementation.

There is no hosted registry, server, or network service anywhere in this
module: "publication" means writing a static, reproducible JSON document
to local disk, exactly as the existing run-directory artifacts already
are. Publication never modifies an already-issued Technical Certificate or
Certification Manifest -- it only reads and references them.
"""

from __future__ import annotations

import json
import os
import tempfile
from dataclasses import dataclass, replace
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from mcc_core.signing import canonical_bytes

from mcc_evidence.hash_reference import (
    HashReference,
    HashReferenceError,
    compute_hash_reference,
    verify_hash_reference,
)

from .target import CertifyError

PUBLICATION_RECORD_SCHEMA_VERSION = "mcc-certify-publication-record/1"
PUBLICATION_INDEX_SCHEMA_VERSION = "mcc-certify-publication-index/1"
PUBLICATION_INDEX_FILE_NAME = "publication-index.json"


class PublicationError(CertifyError):
    """A Publication Record or Index is malformed, references a missing
    artifact, or fails a Hash Reference check. Fails closed."""


class PublicationConflictError(PublicationError):
    """Raised when a Publication Index already contains a different
    Publication Record for the same ``certificate_id`` -- a certificate id
    is never silently overwritten or duplicated with divergent content."""


class PublicationStatus(str, Enum):
    """A closed set mirroring the Technical Certificate's own Trust Model
    states (MCC-TC-001 Section 16.4/12): a Publication Record's status is
    fixed at publication time and is never mutated in place -- a status
    change (e.g. later revocation) requires a new Publication Record for a
    *new* certificate_id, or an out-of-band, independently-authorized
    Revocation Record exactly as MCC-TC-001 Section 12 already defines;
    this module never reinterprets or re-implements that mechanism."""

    ACTIVE = "ACTIVE"
    REVOKED = "REVOKED"


@dataclass(frozen=True)
class PublicationRecord:
    publication_record_schema_version: str
    certificate_id: str
    target_id: str
    issuer_id: str
    key_id: str
    certification_manifest_reference: HashReference
    technical_certificate_reference: HashReference
    evidence_bundle_reference: HashReference
    status: PublicationStatus
    issuance_timestamp: int
    specification_version: str
    artifact_location: str
    expiration_timestamp: Optional[int] = None

    def __post_init__(self) -> None:
        if self.publication_record_schema_version != PUBLICATION_RECORD_SCHEMA_VERSION:
            raise PublicationError(
                f"unsupported publication_record_schema_version {self.publication_record_schema_version!r}"
            )
        for name, value in (
            ("certificate_id", self.certificate_id),
            ("target_id", self.target_id),
            ("issuer_id", self.issuer_id),
            ("key_id", self.key_id),
            ("specification_version", self.specification_version),
            ("artifact_location", self.artifact_location),
        ):
            if not value:
                raise PublicationError(f"Publication Record field {name!r} must be non-empty")
        for ref_name, ref in (
            ("certification_manifest_reference", self.certification_manifest_reference),
            ("technical_certificate_reference", self.technical_certificate_reference),
            ("evidence_bundle_reference", self.evidence_bundle_reference),
        ):
            problems = ref.validate()
            if problems:
                raise PublicationError(f"Publication Record {ref_name} invalid: {'; '.join(problems)}")
        if self.expiration_timestamp is not None and self.expiration_timestamp <= self.issuance_timestamp:
            raise PublicationError(
                f"expiration_timestamp ({self.expiration_timestamp}) must be strictly after "
                f"issuance_timestamp ({self.issuance_timestamp})"
            )

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {
            "publication_record_schema_version": self.publication_record_schema_version,
            "certificate_id": self.certificate_id,
            "target_id": self.target_id,
            "issuer_id": self.issuer_id,
            "key_id": self.key_id,
            "certification_manifest_reference": self.certification_manifest_reference.to_dict(),
            "technical_certificate_reference": self.technical_certificate_reference.to_dict(),
            "evidence_bundle_reference": self.evidence_bundle_reference.to_dict(),
            "status": self.status.value,
            "issuance_timestamp": self.issuance_timestamp,
            "specification_version": self.specification_version,
            "artifact_location": self.artifact_location,
        }
        if self.expiration_timestamp is not None:
            d["expiration_timestamp"] = self.expiration_timestamp
        return d

    @classmethod
    def from_dict(cls, d: Any) -> "PublicationRecord":
        if not isinstance(d, dict):
            raise PublicationError("Publication Record must be a JSON object")
        required = (
            "publication_record_schema_version", "certificate_id", "target_id", "issuer_id", "key_id",
            "certification_manifest_reference", "technical_certificate_reference", "evidence_bundle_reference",
            "status", "issuance_timestamp", "specification_version", "artifact_location",
        )
        missing = [f for f in required if f not in d]
        if missing:
            raise PublicationError(f"Publication Record missing required field(s): {missing}")
        try:
            status = PublicationStatus(d["status"])
        except ValueError as e:
            raise PublicationError(f"unsupported Publication Record status {d['status']!r}") from e
        try:
            cm_ref = HashReference.from_dict(d["certification_manifest_reference"])
            tc_ref = HashReference.from_dict(d["technical_certificate_reference"])
            eb_ref = HashReference.from_dict(d["evidence_bundle_reference"])
        except HashReferenceError as e:
            raise PublicationError(f"Publication Record contains a malformed Hash Reference: {e}") from e
        return cls(
            publication_record_schema_version=d["publication_record_schema_version"],
            certificate_id=d["certificate_id"],
            target_id=d["target_id"],
            issuer_id=d["issuer_id"],
            key_id=d["key_id"],
            certification_manifest_reference=cm_ref,
            technical_certificate_reference=tc_ref,
            evidence_bundle_reference=eb_ref,
            status=status,
            issuance_timestamp=d["issuance_timestamp"],
            specification_version=d["specification_version"],
            artifact_location=d["artifact_location"],
            expiration_timestamp=d.get("expiration_timestamp"),
        )


def build_publication_record(
    *,
    certificate_id: str,
    target_id: str,
    issuer_id: str,
    key_id: str,
    certification_manifest_path: Path | str,
    technical_certificate_path: Path | str,
    evidence_bundle_integrity_record_path: Path | str,
    evidence_bundle_id: str,
    issuance_timestamp: int,
    specification_version: str,
    artifact_location: str,
    expiration_timestamp: Optional[int] = None,
    status: PublicationStatus = PublicationStatus.ACTIVE,
) -> PublicationRecord:
    """Build a Publication Record from the real, already-written artifacts
    of a completed, offline-verified certification run. Refuses (raises
    :class:`PublicationError`) if any referenced artifact file is missing
    -- a Publication Record is never built from artifacts that do not
    actually exist on disk."""
    manifest_path = Path(certification_manifest_path)
    cert_path = Path(technical_certificate_path)
    integrity_path = Path(evidence_bundle_integrity_record_path)
    for label, path in (
        ("Certification Manifest", manifest_path),
        ("Technical Certificate", cert_path),
        ("Evidence Bundle Integrity Record", integrity_path),
    ):
        if not path.exists():
            raise PublicationError(f"cannot build Publication Record: {label} not found at {path}")

    cm_ref = compute_hash_reference(manifest_path.read_bytes(), content_ref=certificate_id)
    tc_ref = compute_hash_reference(cert_path.read_bytes(), content_ref=certificate_id)
    eb_ref = compute_hash_reference(integrity_path.read_bytes(), content_ref=evidence_bundle_id)

    return PublicationRecord(
        publication_record_schema_version=PUBLICATION_RECORD_SCHEMA_VERSION,
        certificate_id=certificate_id,
        target_id=target_id,
        issuer_id=issuer_id,
        key_id=key_id,
        certification_manifest_reference=cm_ref,
        technical_certificate_reference=tc_ref,
        evidence_bundle_reference=eb_ref,
        status=status,
        issuance_timestamp=issuance_timestamp,
        specification_version=specification_version,
        artifact_location=artifact_location,
        expiration_timestamp=expiration_timestamp,
    )


def verify_publication_record(
    record: PublicationRecord,
    *,
    certification_manifest_path: Path | str,
    technical_certificate_path: Path | str,
    evidence_bundle_integrity_record_path: Path | str,
) -> list:
    """Recompute each Hash Reference in ``record`` against the actual bytes
    of the referenced artifacts on disk. Returns a list of failure strings
    (empty == fully verified). Never raises for a verification failure --
    only for a structurally malformed record/missing artifact, which is
    itself a failure worth surfacing distinctly."""
    failures = []
    manifest_path = Path(certification_manifest_path)
    cert_path = Path(technical_certificate_path)
    integrity_path = Path(evidence_bundle_integrity_record_path)

    checks = (
        ("certification_manifest_reference", record.certification_manifest_reference, manifest_path),
        ("technical_certificate_reference", record.technical_certificate_reference, cert_path),
        ("evidence_bundle_reference", record.evidence_bundle_reference, integrity_path),
    )
    for name, ref, path in checks:
        if not path.exists():
            failures.append(f"{name}: referenced artifact not found at {path}")
            continue
        if not verify_hash_reference(ref, path.read_bytes()):
            failures.append(f"{name}: Hash Reference does not match the actual artifact content at {path}")
    return failures


@dataclass(frozen=True)
class PublicationIndex:
    """A canonical, deterministically-ordered collection of Publication
    Records. Immutable: :meth:`add` returns a new index rather than
    mutating this one, consistent with every other frozen model in this
    package."""

    publication_index_schema_version: str
    records: Tuple[PublicationRecord, ...]

    def __post_init__(self) -> None:
        if self.publication_index_schema_version != PUBLICATION_INDEX_SCHEMA_VERSION:
            raise PublicationError(
                f"unsupported publication_index_schema_version {self.publication_index_schema_version!r}"
            )
        seen: Dict[str, PublicationRecord] = {}
        for record in self.records:
            if not isinstance(record, PublicationRecord):
                raise PublicationError("Publication Index entries must be PublicationRecord instances")
            prior = seen.get(record.certificate_id)
            if prior is not None and prior.to_dict() != record.to_dict():
                raise PublicationConflictError(
                    f"conflicting Publication Records for certificate_id {record.certificate_id!r}"
                )
            seen[record.certificate_id] = record

    def contains(self, certificate_id: str) -> bool:
        return any(r.certificate_id == certificate_id for r in self.records)

    def get(self, certificate_id: str) -> Optional[PublicationRecord]:
        return next((r for r in self.records if r.certificate_id == certificate_id), None)

    def add(self, record: PublicationRecord) -> "PublicationIndex":
        """Add a Publication Record. Idempotent for a byte-identical
        re-publication of the same certificate_id (safe to rerun); raises
        :class:`PublicationConflictError` if the same certificate_id is
        already present with *different* content -- a certificate id is
        never silently overwritten."""
        existing = self.get(record.certificate_id)
        if existing is not None:
            if existing.to_dict() != record.to_dict():
                raise PublicationConflictError(
                    f"Publication Index already contains a different Publication Record for "
                    f"certificate_id {record.certificate_id!r}"
                )
            return self  # already present, byte-identical: no-op
        new_records = tuple(sorted((*self.records, record), key=lambda r: r.certificate_id))
        return PublicationIndex(
            publication_index_schema_version=self.publication_index_schema_version,
            records=new_records,
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "publication_index_schema_version": self.publication_index_schema_version,
            "records": [r.to_dict() for r in self.records],
        }

    @classmethod
    def from_dict(cls, d: Any) -> "PublicationIndex":
        if not isinstance(d, dict):
            raise PublicationError("Publication Index must be a JSON object")
        if "publication_index_schema_version" not in d or "records" not in d:
            raise PublicationError("Publication Index missing required field(s)")
        if not isinstance(d["records"], list):
            raise PublicationError("Publication Index 'records' must be an array")
        records = tuple(PublicationRecord.from_dict(r) for r in d["records"])
        return cls(
            publication_index_schema_version=d["publication_index_schema_version"],
            records=records,
        )


def empty_publication_index() -> PublicationIndex:
    return PublicationIndex(publication_index_schema_version=PUBLICATION_INDEX_SCHEMA_VERSION, records=())


def read_publication_index(path: Path | str) -> PublicationIndex:
    path = Path(path)
    if not path.exists():
        return empty_publication_index()
    try:
        raw = json.loads(path.read_bytes())
    except (OSError, json.JSONDecodeError) as e:
        raise PublicationError(f"cannot read Publication Index at {path}: {e}") from e
    return PublicationIndex.from_dict(raw)


def write_publication_index(index: PublicationIndex, dest: Path | str) -> Path:
    """Atomic write: serialize to a temp file in the same directory, then
    ``os.replace`` into place -- a reader never observes a partially
    written index."""
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    data = canonical_bytes(index.to_dict())
    fd, tmp_name = tempfile.mkstemp(dir=str(dest.parent), prefix=".tmp-publication-index-")
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
        os.replace(tmp_name, dest)
    finally:
        if os.path.exists(tmp_name):
            os.remove(tmp_name)
    return dest


def write_publication_record(record: PublicationRecord, dest: Path | str) -> Path:
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(dir=str(dest.parent), prefix=".tmp-publication-record-")
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(canonical_bytes(record.to_dict()))
        os.replace(tmp_name, dest)
    finally:
        if os.path.exists(tmp_name):
            os.remove(tmp_name)
    return dest


def read_publication_record(path: Path | str) -> PublicationRecord:
    return PublicationRecord.from_dict(json.loads(Path(path).read_bytes()))


def publish_certificate(
    index: PublicationIndex,
    record: PublicationRecord,
    *,
    publication_dir: Path | str,
) -> PublicationIndex:
    """Add ``record`` to ``index``, write the individual record file and
    the updated index atomically, and return the new index. This is the
    single entry point the pipeline calls for 'publication' -- there is no
    other mutation path."""
    new_index = index.add(record)
    publication_dir = Path(publication_dir)
    write_publication_record(record, publication_dir / f"{record.certificate_id}.publication-record.json")
    write_publication_index(new_index, publication_dir / PUBLICATION_INDEX_FILE_NAME)
    return new_index


__all__ = [
    "PUBLICATION_RECORD_SCHEMA_VERSION",
    "PUBLICATION_INDEX_SCHEMA_VERSION",
    "PUBLICATION_INDEX_FILE_NAME",
    "PublicationError",
    "PublicationConflictError",
    "PublicationStatus",
    "PublicationRecord",
    "build_publication_record",
    "verify_publication_record",
    "PublicationIndex",
    "empty_publication_index",
    "read_publication_index",
    "write_publication_index",
    "write_publication_record",
    "read_publication_record",
    "publish_certificate",
]
