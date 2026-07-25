"""Produce an MCC-EB-001-conformant Evidence Bundle.

Implements the selected Wave A structural requirements: exactly one Bundle
Root containing exactly one Bundle Descriptor, one Integrity Record, one
Provenance Record, and one Evidence Directory (EB-STR-001/002,
EB-FILE-001/002/003), with every non-Integrity-Record file enumerated by the
Integrity Record (EB-FILE-004) and no required file ever omitted
(EB-FILE-005). Both the directory form and the ``.tar.gz`` archive form are
produced from the same in-memory file set, so they are structurally
equivalent by construction (EB-STR-005).

Reuses ``mcc_core.signing.canonical_bytes`` for deterministic serialization
(MCC-EB-001's own "Canonical Form": identical logical content always
produces identical bytes) and this package's ``hash_reference`` module for
every Digest -- no cryptographic code is duplicated.
"""

from __future__ import annotations

import io
import tarfile
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from mcc_core.signing import canonical_bytes

from .eb001_schema import (
    BUNDLE_DESCRIPTOR_NAME,
    EB001_SCHEMA_VERSION,
    EVIDENCE_DIR_NAME,
    INTEGRITY_RECORD_NAME,
    PROVENANCE_RECORD_NAME,
    IncompleteEB001BundleError,
)
from .hash_reference import compute_hash_reference


@dataclass
class EvidenceItemInput:
    """One Evidence Item: a single discrete unit of evidence (MCC-EB-001,
    Section 7 Terminology). ``name`` MUST be unique within the Evidence
    Directory (Section 10.3); ``content`` is written verbatim as its file
    bytes -- callers that want JSON content pass
    ``mcc_core.signing.canonical_bytes(...)`` themselves, so this module
    does not guess an evidence item's internal shape (Section 10.3: "The
    internal structure of an individual Evidence Item MAY vary by
    requirement type")."""

    name: str
    content: bytes


@dataclass
class EB001BundleInput:
    """Typed input for one MCC-EB-001 Bundle. Nothing here is re-decided;
    it is the caller's already-produced certification evidence."""

    cp001_specification_version: str
    certification_run_id: str
    certification_subject_id: Optional[str] = None
    evidence_items: List[EvidenceItemInput] = field(default_factory=list)
    bundle_id: Optional[str] = None


def _validate(bundle_input: EB001BundleInput) -> None:
    if not bundle_input.cp001_specification_version:
        raise IncompleteEB001BundleError("cp001_specification_version is required")
    if not bundle_input.certification_run_id:
        raise IncompleteEB001BundleError("certification_run_id is required")
    names = [item.name for item in bundle_input.evidence_items]
    if len(names) != len(set(names)):
        raise IncompleteEB001BundleError(
            "duplicate Evidence Item name(s) within the Evidence Directory: "
            f"{[n for n in names if names.count(n) > 1]}"
        )
    for item in bundle_input.evidence_items:
        if not item.name or "/" in item.name or item.name in ("..", "."):
            raise IncompleteEB001BundleError(f"invalid Evidence Item name: {item.name!r}")


def _bundle_descriptor(bundle_id: str, bundle_input: EB001BundleInput) -> Dict[str, object]:
    # Section 11.1: MUST declare the Schema Version, a Bundle identifier, and
    # the MCC-CP-001 specification version.
    descriptor: Dict[str, object] = {
        "schema_version": EB001_SCHEMA_VERSION,
        "bundle_id": bundle_id,
        "cp001_specification_version": bundle_input.cp001_specification_version,
    }
    if bundle_input.certification_subject_id is not None:
        descriptor["certification_subject_id"] = bundle_input.certification_subject_id
    return descriptor


def _provenance_record(bundle_id: str, bundle_input: EB001BundleInput) -> Dict[str, object]:
    # Section 11.3 / Terminology: records the origin of the Bundle, including
    # the certification run and specification version that produced it.
    return {
        "schema_version": EB001_SCHEMA_VERSION,
        "bundle_id": bundle_id,
        "certification_run_id": bundle_input.certification_run_id,
        "cp001_specification_version": bundle_input.cp001_specification_version,
    }


def _integrity_record(
    bundle_id: str, files: Dict[str, bytes]
) -> Dict[str, object]:
    # Section 11.2 / 13.4: enumerate a Digest for every file other than the
    # Integrity Record itself (EB-FILE-004); deterministic (sorted) order
    # (EB-STR-003/004).
    entries = []
    for path in sorted(files):
        if path == INTEGRITY_RECORD_NAME:
            continue
        ref = compute_hash_reference(files[path], content_ref=path)
        entries.append({"path": path, "hash_reference": ref.to_dict()})
    return {
        "schema_version": EB001_SCHEMA_VERSION,
        "bundle_id": bundle_id,
        "algorithm": "sha256",
        "entries": entries,
    }


def build_bundle_files(bundle_input: EB001BundleInput) -> Dict[str, bytes]:
    """Build the complete in-memory {relative_path: bytes} file set for one
    Bundle, shared by both the directory and archive writers so they are
    structurally equivalent by construction (EB-STR-005)."""
    _validate(bundle_input)
    bundle_id = bundle_input.bundle_id or uuid.uuid4().hex

    files: Dict[str, bytes] = {
        BUNDLE_DESCRIPTOR_NAME: canonical_bytes(_bundle_descriptor(bundle_id, bundle_input)),
        PROVENANCE_RECORD_NAME: canonical_bytes(_provenance_record(bundle_id, bundle_input)),
    }
    for item in bundle_input.evidence_items:
        files[f"{EVIDENCE_DIR_NAME}/{item.name}"] = item.content

    # The Evidence Directory itself MAY be empty (Section 11.4) but MUST
    # still exist at the Bundle Root (Section 10.2) -- represented on disk by
    # a placeholder so an empty directory is never silently absent; the
    # placeholder is itself covered by the Integrity Record like any other
    # file, so it can never be used to smuggle unaccounted content.
    if not bundle_input.evidence_items:
        files[f"{EVIDENCE_DIR_NAME}/.keep"] = b""

    files[INTEGRITY_RECORD_NAME] = canonical_bytes(_integrity_record(bundle_id, files))
    return files


def build_eb001_bundle(
    bundle_input: EB001BundleInput,
    dest: Path | str,
    *,
    archive: bool = False,
) -> Path:
    """Write a deterministic MCC-EB-001 Evidence Bundle. Fails closed:
    raises :class:`IncompleteEB001BundleError` if the input is missing or
    internally inconsistent -- no partial bundle is ever written.

    ``dest`` is a directory (default) or, with ``archive=True``, a
    ``.tar.gz`` file. Returns the path written.
    """
    files = build_bundle_files(bundle_input)
    dest = Path(dest)

    if archive:
        if dest.suffix not in (".gz", ".tgz") and not str(dest).endswith(".tar.gz"):
            dest = dest.with_name(dest.name + ".tar.gz")
        with tarfile.open(dest, "w:gz") as tar:
            for name in sorted(files):
                data = files[name]
                info = tarfile.TarInfo(name=name)
                info.size = len(data)
                info.mtime = 0  # deterministic
                tar.addfile(info, io.BytesIO(data))
        return dest

    dest.mkdir(parents=True, exist_ok=True)
    for name in sorted(files):
        target = dest / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(files[name])
    return dest
