"""Certified Adapter Program (PR #46).

A narrow, repository-native layer on top of the existing Compliance & Certification
Suite. It turns an *official compliance result* into a deterministic, machine-
readable **certification** and records the repository's certified adapters in a
version-controlled manifest that CI regenerates and verifies.

Trust boundary (unchanged): certification is nothing more than a deterministic
representation of the compliance evidence produced by `run_compliance`. It grants
no execution authority, changes no governance/Gate/audit semantics, adds no
signing/PKI/network, and never trusts adapter self-attestation. A certification
fails closed whenever the evidence or version binding is invalid.

    The Integration Contract defines required behavior.
    Golden vectors test contract invariants.
    The Compliance Suite evaluates conformance.
    Certification is a deterministic representation of that compliance evidence.
    The manifest records verified repository-local certification state.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from mcc_core.signing import canonical_bytes, sha256_hex

from .models import (
    SUITE_VERSION,
    AdapterMetadata,
    CertificationStatus,
)
from .protocol import ComplianceAdapter
from .registry import load_adapter
from .runner import ComplianceReport, run_compliance

#: Repository root (…/src/mcc_compliance/program.py -> repo root).
REPO_ROOT = Path(__file__).resolve().parents[2]

#: The committed manifest of repository-certified adapters.
MANIFEST_PATH = REPO_ROOT / "certifications" / "manifest.json"

#: Adapters the repository officially certifies (registry keys). Only these enter
#: the manifest, and only if they genuinely pass the official suite.
OFFICIAL_ADAPTERS: Tuple[str, ...] = ("reference", "voltagent")

MANIFEST_SCHEMA_VERSION = "1"
CERT_REPORT_SCHEMA_VERSION = "1"
DIGEST_ALGORITHM = "sha256"

#: Exact meaning of a certification — no external/third-party accreditation.
CERTIFICATION_NOTE = (
    "Certified by the MCC-Core repository's official compliance suite for the "
    "stated contract and vector-set versions. This is a repository-local integrity "
    "statement, not a public, third-party, or legal accreditation, and it grants no "
    "execution authority."
)


class ProgramStatus(str, Enum):
    """Closed certification status. Fail-closed: anything other than a clean
    compliance CERTIFIED (including the suite's ERROR) is NOT_CERTIFIED here."""

    CERTIFIED = "CERTIFIED"
    NOT_CERTIFIED = "NOT_CERTIFIED"


@dataclass(frozen=True)
class ScenarioOutcome:
    id: str
    status: str
    invariant: str
    mandatory: bool

    def to_dict(self) -> Dict[str, Any]:
        return {"id": self.id, "status": self.status, "invariant": self.invariant,
                "mandatory": self.mandatory}


@dataclass(frozen=True)
class CertificationResult:
    """A deterministic certification derived solely from an official compliance
    result. Contains no wall-clock time, so it is fully reproducible."""

    adapter_name: str
    adapter_version: str
    implementation_id: str
    framework: Optional[str]
    contract_version: str
    compliance_suite_version: str
    vector_manifest_digest: str
    status: ProgramStatus
    scenarios_total: int
    scenarios_passed: int
    scenarios_failed: int
    covered_invariants: Tuple[str, ...]
    scenarios: Tuple[ScenarioOutcome, ...]
    evidence_digest: str
    digest_algorithm: str = DIGEST_ALGORITHM
    reasons: Tuple[str, ...] = field(default_factory=tuple)

    # --- serialization ------------------------------------------------------ #

    def manifest_entry(self) -> Dict[str, Any]:
        """The compact, deterministic record stored in the repository manifest."""
        return {
            "adapter": self.adapter_name,
            "adapter_version": self.adapter_version,
            "implementation_id": self.implementation_id,
            "framework": self.framework,
            "contract_version": self.contract_version,
            "compliance_suite_version": self.compliance_suite_version,
            "vector_manifest_digest": self.vector_manifest_digest,
            "status": self.status.value,
            "scenarios_total": self.scenarios_total,
            "scenarios_passed": self.scenarios_passed,
            "scenarios_failed": self.scenarios_failed,
            "covered_invariants": list(self.covered_invariants),
            "evidence_digest": self.evidence_digest,
            "digest_algorithm": self.digest_algorithm,
            "report_id": self.evidence_digest,
        }

    def report(self) -> Dict[str, Any]:
        """The full machine-readable certification report (scenario-level)."""
        entry = self.manifest_entry()
        entry.update({
            "report_schema_version": CERT_REPORT_SCHEMA_VERSION,
            "scenarios_detail": [s.to_dict() for s in self.scenarios],
            "reasons": list(self.reasons),
            "note": CERTIFICATION_NOTE,
        })
        return entry


# --------------------------------------------------------------------------- #
# Evidence digest.                                                            #
# --------------------------------------------------------------------------- #

def _evidence_digest(metadata: AdapterMetadata, contract_version: str,
                     vector_manifest_digest: str, status: ProgramStatus,
                     covered_invariants: Tuple[str, ...],
                     scenarios: Tuple[ScenarioOutcome, ...]) -> str:
    """Deterministic SHA-256 over the *semantic* certification evidence.

    Binds adapter identity + version, contract version, compliance/vector-set
    version, the vector manifest digest, the ordered scenario outcomes, the
    invariant coverage, and the overall status. Canonical serialization with stable
    ordering; no wall-clock time, no filesystem paths, no object repr. Reuses the
    repository's canonicalization — this is an integrity fingerprint, not a signing
    or trust scheme."""
    payload = {
        "adapter": {
            "name": metadata.name,
            "version": metadata.version,
            "implementation_id": metadata.implementation_id,
            "framework": metadata.framework,
            "claimed_contract_version": metadata.claimed_contract_version,
        },
        "contract_version": contract_version,
        "compliance_suite_version": SUITE_VERSION,
        "vector_manifest_digest": vector_manifest_digest,
        "status": status.value,
        "covered_invariants": sorted(covered_invariants),
        "scenarios": [
            {"id": s.id, "status": s.status, "invariant": s.invariant}
            for s in sorted(scenarios, key=lambda s: s.id)
        ],
    }
    return sha256_hex(canonical_bytes(payload))


# --------------------------------------------------------------------------- #
# Public API.                                                                 #
# --------------------------------------------------------------------------- #

def certify_report(report: ComplianceReport) -> CertificationResult:
    """Derive a certification from an *already-produced* official compliance
    result. This is the only place a certification is minted, and it is derived
    exclusively from the compliance evidence — never from adapter self-attestation."""
    md = report.adapter_metadata
    scenarios = tuple(
        ScenarioOutcome(id=r.vector_id, status=r.status.value, invariant=r.invariant,
                        mandatory=r.mandatory)
        for r in report.results
    )
    covered = tuple(sorted({r.invariant for r in report.results}))

    certified = (
        report.certification.status is CertificationStatus.CERTIFIED
        and md.claimed_contract_version == report.contract_version
        and not md.missing_fields()
    )
    status = ProgramStatus.CERTIFIED if certified else ProgramStatus.NOT_CERTIFIED

    digest = _evidence_digest(md, report.contract_version,
                              report.vector_manifest_digest, status, covered, scenarios)

    return CertificationResult(
        adapter_name=md.name, adapter_version=md.version,
        implementation_id=md.implementation_id, framework=md.framework,
        contract_version=report.contract_version,
        compliance_suite_version=report.suite_version,
        vector_manifest_digest=report.vector_manifest_digest,
        status=status,
        scenarios_total=report.totals.total,
        scenarios_passed=report.totals.passed,
        scenarios_failed=report.totals.failed + report.totals.errored,
        covered_invariants=covered, scenarios=scenarios,
        evidence_digest=digest,
        reasons=tuple(report.certification.reasons),
    )


def certify(adapter: ComplianceAdapter, *, contract_version: str) -> CertificationResult:
    """Certify an adapter against a contract version.

    Runs the official compliance evaluation (real governed stack, ground-truth
    cross-check) with no wall-clock time, then derives the certification. Pure of
    network and mutable global state; deterministic for the same adapter, contract
    version, vectors, and evidence."""
    report = run_compliance(adapter, contract_version, include_timestamp=False)
    return certify_report(report)


# --------------------------------------------------------------------------- #
# Repository certification manifest.                                          #
# --------------------------------------------------------------------------- #

def build_manifest(*, contract_version: str,
                   adapter_names: Tuple[str, ...] = OFFICIAL_ADAPTERS) -> Dict[str, Any]:
    """Deterministically build the repository manifest by actually certifying each
    official adapter. Only genuinely-CERTIFIED adapters are recorded; a regression
    drops an adapter from the fresh build, which CI detects against the committed
    manifest."""
    entries: List[Dict[str, Any]] = []
    for name in adapter_names:
        result = certify(load_adapter(name), contract_version=contract_version)
        if result.status is ProgramStatus.CERTIFIED:
            entry = result.manifest_entry()
            entry["adapter_key"] = name
            entries.append(entry)
    entries.sort(key=lambda e: e["adapter_key"])
    return {
        "manifest_schema_version": MANIFEST_SCHEMA_VERSION,
        "contract_version": contract_version,
        "compliance_suite_version": SUITE_VERSION,
        "note": CERTIFICATION_NOTE,
        "certifications": entries,
    }


def write_manifest(*, contract_version: str, path: Path = MANIFEST_PATH) -> Dict[str, Any]:
    import json
    manifest = build_manifest(contract_version=contract_version)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest


@dataclass(frozen=True)
class ManifestVerification:
    ok: bool
    differences: Tuple[str, ...]


def verify_manifest(*, contract_version: Optional[str] = None,
                    path: Path = MANIFEST_PATH) -> ManifestVerification:
    """Regenerate the manifest from real certification evidence and compare it to
    the committed file. Any difference — a stale entry, a tampered digest/status, an
    adapter that no longer conforms, or a non-CERTIFIED entry slipped in — makes
    verification fail. Fail-closed: a missing/invalid committed manifest fails."""
    import json

    differences: List[str] = []
    if not path.is_file():
        return ManifestVerification(False, (f"manifest not found at {path.name}",))
    try:
        committed = json.loads(path.read_text(encoding="utf-8"))
    except ValueError as exc:
        return ManifestVerification(False, (f"committed manifest is not valid JSON: {exc}",))

    version = contract_version or committed.get("contract_version")
    if not version:
        return ManifestVerification(False, ("committed manifest has no contract_version",))

    fresh = build_manifest(contract_version=version)

    # Canonical comparison catches every tamper/stale case deterministically.
    if canonical_bytes(committed) != canonical_bytes(fresh):
        differences.append(
            "committed manifest does not match freshly regenerated certification "
            "evidence (stale, tampered, or an adapter no longer conforms)")
        # Add per-entry detail to make CI output actionable.
        c_by = {e.get("adapter_key"): e for e in committed.get("certifications", [])}
        f_by = {e.get("adapter_key"): e for e in fresh.get("certifications", [])}
        for key in sorted(set(c_by) | set(f_by)):
            if key not in f_by:
                differences.append(f"'{key}': in committed manifest but not certified now")
            elif key not in c_by:
                differences.append(f"'{key}': newly certified but missing from committed manifest")
            elif canonical_bytes(c_by[key]) != canonical_bytes(f_by[key]):
                differences.append(f"'{key}': committed entry differs from regenerated evidence")

    return ManifestVerification(not differences, tuple(differences))


__all__ = [
    "ProgramStatus", "ScenarioOutcome", "CertificationResult",
    "certify", "certify_report",
    "build_manifest", "write_manifest", "verify_manifest", "ManifestVerification",
    "OFFICIAL_ADAPTERS", "MANIFEST_PATH", "MANIFEST_SCHEMA_VERSION",
    "CERT_REPORT_SCHEMA_VERSION", "DIGEST_ALGORITHM", "CERTIFICATION_NOTE",
]
