"""Offline, fail-closed verification of an MCC-EB-001 Evidence Bundle.

Reuses the existing directory/``.tar.gz`` reader (``verify._Reader``) rather
than writing a second bundle-reading abstraction. Never executes,
authorizes, or mutates anything -- it only reads and reports a structured
:class:`EB001VerificationResult`.

A bundle is reported VALID only when every structural requirement
(EB-STR-001/002/005), required-file requirement (EB-FILE-001..005), and
Hash Reference requirement (CM-HASH-001/002/004) holds. Any single
violation -- missing root artifact, unenumerated or unaccounted file,
digest mismatch, unsupported algorithm, malformed record, or inconsistent
bundle identity -- is a blocking failure, never a warning: verification
fails closed whenever validity cannot be positively established.
"""

from __future__ import annotations

import json
from collections import Counter
from typing import Any, Callable, Dict, List, Optional

from .eb001_schema import (
    BUNDLE_DESCRIPTOR_NAME,
    EVIDENCE_DIR_NAME,
    INTEGRITY_RECORD_NAME,
    PROVENANCE_RECORD_NAME,
    REQUIRED_ROOT_NAMES,
    SUPPORTED_EB001_SCHEMA_VERSIONS,
    CheckResult,
    CheckStatus,
    EB001Status,
    EB001VerificationResult,
)
from .hash_reference import HashReference, HashReferenceError, verify_hash_reference
from .verify import _Reader  # reused, not reimplemented (BundleFormatError on open failure)
from .schema import BundleFormatError


def verify_eb001_bundle(path) -> EB001VerificationResult:
    """Verify an MCC-EB-001 Bundle (directory or ``.tar.gz``) offline."""
    from pathlib import Path

    path = Path(path)
    checks: List[CheckResult] = []
    failures: List[str] = []
    warnings: List[str] = []

    def add(name: str, status: CheckStatus, detail: str = "") -> None:
        checks.append(CheckResult(name, status, detail))
        if status is CheckStatus.FAIL:
            failures.append(f"{name}: {detail}")
        elif status is CheckStatus.WARN:
            warnings.append(f"{name}: {detail}")

    try:
        reader = _Reader(path)
    except BundleFormatError as e:
        return EB001VerificationResult(
            overall_status=EB001Status.INVALID,
            schema_supported=False,
            checks=[CheckResult("bundle_readable", CheckStatus.FAIL, str(e))],
            failures=[str(e)],
        )
    try:
        return _verify(reader, checks, failures, warnings, add)
    finally:
        reader.close()


def _read_json(reader: _Reader, name: str, add: Callable[..., None], check_name: str) -> Optional[dict]:
    if not reader.has(name):
        add(check_name, CheckStatus.FAIL, f"{name} missing at Bundle Root")
        return None
    try:
        obj = json.loads(reader.read(name))
    except Exception as e:  # noqa: BLE001
        add(check_name, CheckStatus.FAIL, f"malformed {name}: {e}")
        return None
    if not isinstance(obj, dict):
        add(check_name, CheckStatus.FAIL, f"{name} is not a JSON object")
        return None
    return obj


def _verify(
    reader: _Reader,
    checks: List[CheckResult],
    failures: List[str],
    warnings: List[str],
    add: Callable[..., None],
) -> EB001VerificationResult:
    names = reader.names()

    # ---- schema (gate, mirrors schema.py's UNSUPPORTED_SCHEMA pattern) ---- #
    descriptor = _read_json(reader, BUNDLE_DESCRIPTOR_NAME, add, "bundle_descriptor")
    if descriptor is None:
        return _finish(checks, failures, warnings, schema_supported=False)
    schema_version = descriptor.get("schema_version")
    if schema_version not in SUPPORTED_EB001_SCHEMA_VERSIONS:
        add("schema_support", CheckStatus.FAIL, f"unsupported schema version {schema_version!r}")
        return EB001VerificationResult(
            overall_status=EB001Status.UNSUPPORTED_SCHEMA,
            schema_supported=False,
            bundle_id=descriptor.get("bundle_id"),
            checks=checks, failures=list(failures), warnings=list(warnings),
        )
    add("schema_support", CheckStatus.PASS, schema_version)

    # ---- EB-FILE-001..003: required root artifacts present, no duplicates - #
    name_counts = Counter(names)
    duplicates = sorted(n for n, c in name_counts.items() if c > 1)
    if duplicates:
        add("root_structure", CheckStatus.FAIL, f"duplicate bundle member name(s): {duplicates}")
    else:
        missing_root = [n for n in REQUIRED_ROOT_NAMES if n not in name_counts]
        if missing_root:
            add("root_structure", CheckStatus.FAIL, f"missing required root artifact(s): {missing_root}")
        elif not any(n == EVIDENCE_DIR_NAME or n.startswith(EVIDENCE_DIR_NAME + "/") for n in names):
            add("root_structure", CheckStatus.FAIL, "Evidence Directory is absent at the Bundle Root")
        else:
            unexpected = [
                n for n in names
                if n not in REQUIRED_ROOT_NAMES and not n.startswith(EVIDENCE_DIR_NAME + "/")
            ]
            if unexpected:
                add("root_structure", CheckStatus.FAIL,
                    f"unaccounted top-level content in the Bundle Root: {sorted(unexpected)}")
            else:
                add("root_structure", CheckStatus.PASS,
                    "exactly one Bundle Descriptor, Integrity Record, Provenance Record, "
                    "and Evidence Directory")

    provenance = _read_json(reader, PROVENANCE_RECORD_NAME, add, "provenance_record")
    integrity = _read_json(reader, INTEGRITY_RECORD_NAME, add, "integrity_record")

    # ---- bundle identity consistency -------------------------------------- #
    bundle_id = descriptor.get("bundle_id")
    if not isinstance(bundle_id, str) or not bundle_id:
        add("bundle_identity", CheckStatus.FAIL, "bundle_descriptor is missing a valid bundle_id")
    elif provenance is not None and integrity is not None:
        prov_id, integ_id = provenance.get("bundle_id"), integrity.get("bundle_id")
        if prov_id != bundle_id or integ_id != bundle_id:
            add("bundle_identity", CheckStatus.FAIL,
                f"inconsistent bundle_id across records: descriptor={bundle_id!r} "
                f"provenance={prov_id!r} integrity={integ_id!r}")
        else:
            add("bundle_identity", CheckStatus.PASS, f"bundle_id {bundle_id!r} consistent")

    # ---- EB-FILE-004 + CM-HASH-*: enumeration + Hash Reference integrity --- #
    if integrity is not None:
        _integrity_checks(reader, integrity, add)

    return _finish(checks, failures, warnings, schema_supported=True, bundle_id=bundle_id)


def _integrity_checks(reader: _Reader, integrity: Dict[str, Any], add: Callable[..., None]) -> None:
    algorithm = integrity.get("algorithm")
    entries = integrity.get("entries")
    if not isinstance(entries, list):
        add("integrity_record_structure", CheckStatus.FAIL, "integrity_record.entries is missing/invalid")
        return
    add("integrity_record_structure", CheckStatus.PASS, f"{len(entries)} entrie(s) declared")

    actual_files = {n for n in reader.names() if n != INTEGRITY_RECORD_NAME}
    enumerated_paths = set()
    hash_ok = True
    for i, entry in enumerate(entries):
        if not isinstance(entry, dict) or "path" not in entry or "hash_reference" not in entry:
            hash_ok = False
            add("hash_reference_integrity", CheckStatus.FAIL, f"entry {i} is malformed")
            continue
        entry_path = entry["path"]
        enumerated_paths.add(entry_path)
        try:
            ref = HashReference.from_dict(entry["hash_reference"])
        except HashReferenceError as e:
            hash_ok = False
            add("hash_reference_integrity", CheckStatus.FAIL, f"entry for {entry_path!r}: {e}")
            continue
        problems = ref.validate()
        if problems:
            hash_ok = False
            add("hash_reference_integrity", CheckStatus.FAIL,
                f"entry for {entry_path!r}: {'; '.join(problems)}")
            continue
        if ref.content_ref != entry_path:
            hash_ok = False
            add("hash_reference_integrity", CheckStatus.FAIL,
                f"entry for {entry_path!r}: Hash Reference content_ref {ref.content_ref!r} "
                f"is bound to different content than its declared path")
            continue
        if entry_path not in actual_files:
            hash_ok = False
            add("hash_reference_integrity", CheckStatus.FAIL,
                f"entry for {entry_path!r}: content reference does not resolve to any actual file")
            continue
        data = reader.read(entry_path)
        if not verify_hash_reference(ref, data):
            hash_ok = False
            add("hash_reference_integrity", CheckStatus.FAIL,
                f"entry for {entry_path!r}: digest mismatch (tampered or regenerated content)")

    unenumerated = sorted(actual_files - enumerated_paths)
    missing_files = sorted(enumerated_paths - actual_files)
    if unenumerated:
        hash_ok = False
        add("integrity_enumeration_completeness", CheckStatus.FAIL,
            f"file(s) present but not enumerated by the Integrity Record: {unenumerated}")
    elif missing_files:
        hash_ok = False
        add("integrity_enumeration_completeness", CheckStatus.FAIL,
            f"enumerated file(s) not actually present in the Bundle: {missing_files}")
    else:
        add("integrity_enumeration_completeness", CheckStatus.PASS,
            "every non-Integrity-Record file is enumerated exactly once")

    if algorithm not in ("sha256",):
        hash_ok = False
        add("hash_algorithm", CheckStatus.FAIL,
            f"integrity_record declares non-collision-resistant/unsupported algorithm {algorithm!r}")
    else:
        add("hash_algorithm", CheckStatus.PASS, algorithm)

    if hash_ok:
        add("hash_reference_integrity", CheckStatus.PASS,
            f"all {len(entries)} Hash Reference(s) valid, bound, and recomputed")


def _finish(
    checks: List[CheckResult],
    failures: List[str],
    warnings: List[str],
    *,
    schema_supported: bool,
    bundle_id: Optional[str] = None,
) -> EB001VerificationResult:
    status = EB001Status.INVALID if failures else EB001Status.VALID
    return EB001VerificationResult(
        overall_status=status,
        schema_supported=schema_supported,
        bundle_id=bundle_id,
        checks=checks,
        failures=list(failures),
        warnings=list(warnings),
    )
