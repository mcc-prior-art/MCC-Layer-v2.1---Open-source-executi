"""MCC-CM-001 Certification Manifest — Evidence Bundle Reference (Wave B).

Implements ONLY the minimum Certification Manifest container necessary to
hold and verify the Evidence Bundle Reference (MCC-CM-001 Section 14):
``CM-EBREF-001..004`` and ``CM-HASH-003``. This is deliberately NOT a
complete Certification Manifest -- Certification Metadata, Requirement
Results, and the overall certification decision (MCC-CP-001 Sections
8.5/9.5/10.4) are explicitly deferred to a future wave; see
``conformance/normative-v1.0/remediation/wave-b-evidence-bundle-reference-scope-manifest.md``.

A Certification Manifest is normatively "a single structured,
machine-readable document" that "SHALL NOT be a directory or multi-file
archive" (MCC-CM-001 Section 9.2) -- represented here as one JSON document,
never a bundle directory.

Reuses Wave A's structured Hash Reference (``hash_reference.py``) and
MCC-EB-001 Evidence Bundle verifier (``eb001_verify.py`` / ``eb001_schema.py``)
directly -- no second Hash Reference type, no second Evidence Bundle model,
no duplicate verifier. The pre-existing ``src/mcc_compliance/`` certification
manifest (``certifications/manifest.json``) is a different, Integration-
Contract-scoped artifact (adapter/contract-version/scenario fields, no
Evidence Bundle Reference concept at all) and is not reinterpreted or
touched by this module.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .eb001_schema import (
    BUNDLE_DESCRIPTOR_NAME,
    INTEGRITY_RECORD_NAME,
    EB001Status,
)
from .eb001_verify import verify_eb001_bundle
from .hash_reference import HashReference, HashReferenceError, compute_hash_reference, verify_hash_reference
from .schema import CheckResult, CheckStatus

#: Manifest schema version for this minimal MCC-CM-001 container. Distinct
#: from EB001_SCHEMA_VERSION ("mcc-eb-001/1") and from the pre-existing
#: mcc_compliance certification manifest (which carries no schema_version
#: field of this kind at all).
CM001_MANIFEST_SCHEMA_VERSION = "mcc-cm-001/1"
SUPPORTED_CM001_MANIFEST_SCHEMA_VERSIONS = frozenset({CM001_MANIFEST_SCHEMA_VERSION})


class EvidenceBundleReferenceKind(str, Enum):
    PRIMARY = "primary"
    SUPPLEMENTARY = "supplementary"


class CM001Error(Exception):
    """Base error for Wave B production."""


class IncompleteCM001ManifestError(CM001Error):
    """Production refused because the Manifest input was missing or
    internally inconsistent -- no partial Manifest is ever written."""


class CM001Status(str, Enum):
    VALID = "VALID"
    INVALID = "INVALID"
    UNSUPPORTED_SCHEMA = "UNSUPPORTED_SCHEMA"


@dataclass(frozen=True)
class EvidenceBundleReference:
    """MCC-CM-001 Section 14.2/14.3: identifies and binds to one Evidence
    Bundle. ``hash_references`` MUST carry at least one entry (CM-HASH-003);
    the first is always the binding to the referenced Bundle's Integrity
    Record required by Section 14.2 -- any further entries are for
    auxiliary content per Section 13.4 and are outside Wave B's selected
    scope."""

    bundle_id: str
    schema_version: str
    hash_references: Tuple[HashReference, ...]
    kind: EvidenceBundleReferenceKind = EvidenceBundleReferenceKind.PRIMARY

    def to_dict(self) -> Dict[str, Any]:
        return {
            "bundle_id": self.bundle_id,
            "schema_version": self.schema_version,
            "hash_references": [hr.to_dict() for hr in self.hash_references],
            "kind": self.kind.value,
        }

    @classmethod
    def from_dict(cls, d: Any, *, kind: EvidenceBundleReferenceKind) -> "EvidenceBundleReference":
        if not isinstance(d, dict):
            raise HashReferenceError("Evidence Bundle Reference must be a JSON object")
        for f in ("bundle_id", "schema_version", "hash_references"):
            if f not in d:
                raise HashReferenceError(f"Evidence Bundle Reference missing required field {f!r}")
        if not isinstance(d["bundle_id"], str) or not d["bundle_id"]:
            raise HashReferenceError("Evidence Bundle Reference bundle_id must be a non-empty string")
        if not isinstance(d["schema_version"], str) or not d["schema_version"]:
            raise HashReferenceError("Evidence Bundle Reference schema_version must be a non-empty string")
        raw_refs = d["hash_references"]
        if not isinstance(raw_refs, list) or not raw_refs:
            raise HashReferenceError(
                "Evidence Bundle Reference MUST include at least one Hash Reference (CM-HASH-003)"
            )
        refs = tuple(HashReference.from_dict(r) for r in raw_refs)
        return cls(bundle_id=d["bundle_id"], schema_version=d["schema_version"], hash_references=refs, kind=kind)


def build_evidence_bundle_reference(
    bundle_path: Path | str,
    *,
    kind: EvidenceBundleReferenceKind = EvidenceBundleReferenceKind.PRIMARY,
) -> EvidenceBundleReference:
    """Build an Evidence Bundle Reference to a real MCC-EB-001 Bundle at
    ``bundle_path``. The Bundle is read (never re-derived/guessed): the
    Bundle identifier and Schema Version come from its own Bundle
    Descriptor (MCC-EB-001 Section 12.1 / 17.2), and the single required
    Hash Reference binds to the Bundle's actual Integrity Record content
    (Section 14.2), with ``content_ref`` set to the Bundle identifier
    itself -- the exact example CM-HASH-001 gives for what a Hash
    Reference's content it corresponds to may be."""
    bundle_path = Path(bundle_path)
    descriptor_path = bundle_path / BUNDLE_DESCRIPTOR_NAME
    integrity_path = bundle_path / INTEGRITY_RECORD_NAME
    if not descriptor_path.exists() or not integrity_path.exists():
        raise IncompleteCM001ManifestError(
            f"cannot build an Evidence Bundle Reference: {bundle_path} is not a readable MCC-EB-001 Bundle"
        )
    descriptor = json.loads(descriptor_path.read_bytes())
    bundle_id = descriptor.get("bundle_id")
    schema_version = descriptor.get("schema_version")
    if not bundle_id or not schema_version:
        raise IncompleteCM001ManifestError(
            f"Bundle Descriptor at {bundle_path} is missing bundle_id or schema_version"
        )
    integrity_bytes = integrity_path.read_bytes()
    ref = compute_hash_reference(integrity_bytes, content_ref=bundle_id)
    return EvidenceBundleReference(
        bundle_id=bundle_id, schema_version=schema_version, hash_references=(ref,), kind=kind,
    )


@dataclass
class CM001Manifest:
    """The minimum Certification Manifest container Wave B implements: only
    the primary and supplementary Evidence Bundle References. Every other
    Certification Manifest field (Certification Metadata, Requirement
    Results, the certification decision itself) is explicitly out of scope
    -- see this module's docstring."""

    primary_evidence_bundle_reference: EvidenceBundleReference
    supplementary_evidence_bundle_references: Tuple[EvidenceBundleReference, ...] = ()
    manifest_schema_version: str = CM001_MANIFEST_SCHEMA_VERSION

    def to_dict(self) -> Dict[str, Any]:
        return {
            "manifest_schema_version": self.manifest_schema_version,
            "primary_evidence_bundle_reference": self.primary_evidence_bundle_reference.to_dict(),
            "supplementary_evidence_bundle_references": [
                r.to_dict() for r in self.supplementary_evidence_bundle_references
            ],
        }

    @classmethod
    def from_dict(cls, d: Any) -> "CM001Manifest":
        if not isinstance(d, dict):
            raise HashReferenceError("Certification Manifest must be a JSON object")
        for f in ("manifest_schema_version", "primary_evidence_bundle_reference"):
            if f not in d:
                raise HashReferenceError(f"Certification Manifest missing required field {f!r}")
        primary = EvidenceBundleReference.from_dict(
            d["primary_evidence_bundle_reference"], kind=EvidenceBundleReferenceKind.PRIMARY
        )
        supplementary_raw = d.get("supplementary_evidence_bundle_references", [])
        if not isinstance(supplementary_raw, list):
            raise HashReferenceError("supplementary_evidence_bundle_references must be an array")
        supplementary = tuple(
            EvidenceBundleReference.from_dict(r, kind=EvidenceBundleReferenceKind.SUPPLEMENTARY)
            for r in supplementary_raw
        )
        return cls(
            primary_evidence_bundle_reference=primary,
            supplementary_evidence_bundle_references=supplementary,
            manifest_schema_version=d["manifest_schema_version"],
        )


def _validate_distinguishable(
    primary: EvidenceBundleReference, supplementary: Tuple[EvidenceBundleReference, ...]
) -> None:
    # CM-EBREF-003: a supplementary reference MUST be distinguishable from
    # the primary reference -- at minimum, it must not reference the same
    # Evidence Bundle (otherwise it is indistinguishable in substance, not
    # merely in storage location).
    if any(s.bundle_id == primary.bundle_id for s in supplementary):
        raise IncompleteCM001ManifestError(
            "a supplementary Evidence Bundle Reference is not distinguishable from the primary "
            "reference: both reference the same bundle_id"
        )
    seen = set()
    for s in supplementary:
        if s.bundle_id in seen:
            raise IncompleteCM001ManifestError(
                f"duplicate supplementary Evidence Bundle Reference for bundle_id {s.bundle_id!r}"
            )
        seen.add(s.bundle_id)


def build_cm001_manifest(
    primary_bundle_path: Path | str,
    supplementary_bundle_paths: Tuple[Path | str, ...] = (),
) -> CM001Manifest:
    """Build the minimal Certification Manifest container: exactly one
    primary Evidence Bundle Reference (CM-EBREF-001) plus zero or more
    distinguishable supplementary references (CM-EBREF-003). Fails closed
    (raises) rather than writing an inconsistent Manifest."""
    primary = build_evidence_bundle_reference(primary_bundle_path, kind=EvidenceBundleReferenceKind.PRIMARY)
    supplementary = tuple(
        build_evidence_bundle_reference(p, kind=EvidenceBundleReferenceKind.SUPPLEMENTARY)
        for p in supplementary_bundle_paths
    )
    _validate_distinguishable(primary, supplementary)
    return CM001Manifest(primary_evidence_bundle_reference=primary, supplementary_evidence_bundle_references=supplementary)


def write_cm001_manifest(manifest: CM001Manifest, dest: Path | str) -> Path:
    """Write the Manifest as one deterministic JSON document -- never a
    directory or multi-file archive (MCC-CM-001 Section 9.2)."""
    from mcc_core.signing import canonical_bytes

    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(canonical_bytes(manifest.to_dict()))
    return dest


def read_cm001_manifest(path: Path | str) -> CM001Manifest:
    return CM001Manifest.from_dict(json.loads(Path(path).read_bytes()))


# ---------------------------------------------------------------------------
# Verification
# ---------------------------------------------------------------------------


@dataclass
class EvidenceBundleReferenceVerificationResult:
    overall_status: CM001Status
    checks: List[CheckResult] = field(default_factory=list)
    failures: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    @property
    def valid(self) -> bool:
        return self.overall_status is CM001Status.VALID

    def to_dict(self) -> dict:
        return {
            "overall_status": self.overall_status.value,
            "valid": self.valid,
            "checks": [c.to_dict() for c in self.checks],
            "failures": list(self.failures),
            "warnings": list(self.warnings),
        }


def verify_evidence_bundle_reference(
    ref: EvidenceBundleReference, bundle_path: Path | str
) -> EvidenceBundleReferenceVerificationResult:
    """MCC-CM-001 Section 14.4: an Evidence Bundle Reference is satisfied
    only when its Hash Reference is independently verified against the
    referenced Evidence Bundle's actual Integrity Record. Fails closed:
    every check below must pass for VALID; any single failure is
    blocking."""
    bundle_path = Path(bundle_path)
    checks: List[CheckResult] = []
    failures: List[str] = []
    warnings: List[str] = []

    def add(name: str, status: CheckStatus, detail: str = "") -> None:
        checks.append(CheckResult(name, status, detail))
        if status is CheckStatus.FAIL:
            failures.append(f"{name}: {detail}")
        elif status is CheckStatus.WARN:
            warnings.append(f"{name}: {detail}")

    if not ref.hash_references:
        add("hash_reference_presence", CheckStatus.FAIL,
            "Evidence Bundle Reference has zero Hash References (CM-HASH-003)")
        return EvidenceBundleReferenceVerificationResult(CM001Status.INVALID, checks, failures, warnings)
    add("hash_reference_presence", CheckStatus.PASS, f"{len(ref.hash_references)} Hash Reference(s)")

    if not bundle_path.exists():
        add("bundle_resolution", CheckStatus.FAIL, f"referenced bundle not found at {bundle_path}")
        return EvidenceBundleReferenceVerificationResult(CM001Status.INVALID, checks, failures, warnings)

    eb_result = verify_eb001_bundle(bundle_path)
    if eb_result.overall_status is not EB001Status.VALID:
        add("bundle_structural_validity", CheckStatus.FAIL,
            f"referenced bundle is not a structurally valid MCC-EB-001 Bundle: {eb_result.failures}")
        return EvidenceBundleReferenceVerificationResult(CM001Status.INVALID, checks, failures, warnings)
    add("bundle_structural_validity", CheckStatus.PASS, "referenced bundle is a valid MCC-EB-001 Bundle")

    descriptor = json.loads((bundle_path / BUNDLE_DESCRIPTOR_NAME).read_bytes())
    actual_bundle_id = descriptor.get("bundle_id")
    actual_schema_version = descriptor.get("schema_version")

    if actual_bundle_id != ref.bundle_id:
        add("bundle_id_binding", CheckStatus.FAIL,
            f"Reference bundle_id {ref.bundle_id!r} does not match the actual Bundle's "
            f"bundle_id {actual_bundle_id!r} (wrong bundle or substitution)")
    else:
        add("bundle_id_binding", CheckStatus.PASS, f"bundle_id {ref.bundle_id!r} matches")

    if actual_schema_version != ref.schema_version:
        add("schema_version_binding", CheckStatus.FAIL,
            f"Reference schema_version {ref.schema_version!r} does not match the actual Bundle's "
            f"schema_version {actual_schema_version!r}")
    else:
        add("schema_version_binding", CheckStatus.PASS, f"schema_version {ref.schema_version!r} matches")

    primary_hr = ref.hash_references[0]
    problems = primary_hr.validate()
    if problems:
        add("hash_reference_integrity", CheckStatus.FAIL,
            f"primary Hash Reference invalid: {'; '.join(problems)}")
    elif primary_hr.content_ref != ref.bundle_id:
        add("hash_reference_integrity", CheckStatus.FAIL,
            f"primary Hash Reference content_ref {primary_hr.content_ref!r} is not bound to "
            f"this Evidence Bundle Reference's bundle_id {ref.bundle_id!r}")
    else:
        integrity_bytes = (bundle_path / INTEGRITY_RECORD_NAME).read_bytes()
        if verify_hash_reference(primary_hr, integrity_bytes):
            add("hash_reference_integrity", CheckStatus.PASS,
                "primary Hash Reference recomputes against the actual Integrity Record")
        else:
            add("hash_reference_integrity", CheckStatus.FAIL,
                "primary Hash Reference digest does not match the actual Integrity Record content "
                "(tampering, regeneration, or substitution)")

    status = CM001Status.INVALID if failures else CM001Status.VALID
    return EvidenceBundleReferenceVerificationResult(status, checks, failures, warnings)


@dataclass
class CM001ManifestVerificationResult:
    overall_status: CM001Status
    primary: Optional[EvidenceBundleReferenceVerificationResult] = None
    supplementary: List[EvidenceBundleReferenceVerificationResult] = field(default_factory=list)
    failures: List[str] = field(default_factory=list)

    @property
    def valid(self) -> bool:
        return self.overall_status is CM001Status.VALID

    def to_dict(self) -> dict:
        return {
            "overall_status": self.overall_status.value,
            "valid": self.valid,
            "primary": self.primary.to_dict() if self.primary else None,
            "supplementary": [s.to_dict() for s in self.supplementary],
            "failures": list(self.failures),
        }


def verify_cm001_manifest(
    manifest: CM001Manifest,
    primary_bundle_path: Path | str,
    supplementary_bundle_paths: Optional[Dict[str, Path | str]] = None,
) -> CM001ManifestVerificationResult:
    """MCC-CM-001 Section 14.4 / CM-EBREF-004: a Certification Manifest
    whose primary Evidence Bundle Reference cannot be verified MUST NOT be
    treated as valid -- the whole Manifest is INVALID the moment the
    primary reference fails, regardless of supplementary references."""
    if manifest.manifest_schema_version not in SUPPORTED_CM001_MANIFEST_SCHEMA_VERSIONS:
        return CM001ManifestVerificationResult(
            CM001Status.UNSUPPORTED_SCHEMA,
            failures=[f"unsupported manifest_schema_version {manifest.manifest_schema_version!r}"],
        )

    primary_result = verify_evidence_bundle_reference(manifest.primary_evidence_bundle_reference, primary_bundle_path)
    if not primary_result.valid:
        return CM001ManifestVerificationResult(
            CM001Status.INVALID, primary=primary_result,
            failures=[f"primary Evidence Bundle Reference unverifiable: {primary_result.failures}"],
        )

    supplementary_results = []
    supplementary_bundle_paths = supplementary_bundle_paths or {}
    supp_failures: List[str] = []
    for ref in manifest.supplementary_evidence_bundle_references:
        path = supplementary_bundle_paths.get(ref.bundle_id)
        if path is None:
            supp_failures.append(f"no bundle path supplied for supplementary reference {ref.bundle_id!r}")
            continue
        result = verify_evidence_bundle_reference(ref, path)
        supplementary_results.append(result)
        if not result.valid:
            supp_failures.append(f"supplementary reference {ref.bundle_id!r} unverifiable: {result.failures}")

    status = CM001Status.INVALID if supp_failures else CM001Status.VALID
    return CM001ManifestVerificationResult(
        status, primary=primary_result, supplementary=supplementary_results, failures=supp_failures,
    )
