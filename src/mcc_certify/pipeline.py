"""The MCC End-to-End Certification Pipeline (PR #67).

Orchestrates the complete normative certification chain for one
Certification Target, reusing Waves A/B/C's existing Evidence Bundle /
Certification Manifest / Technical Certificate producers and verifiers
directly -- this module contains **no** parallel Hash Reference, Evidence
Bundle, Certification Manifest, or Technical Certificate implementation,
and **no** parallel signing/trust/revocation system. It is orchestration
and lifecycle integration over MCC-CP-001's Section 9 Certification
Pipeline, MCC-EB-001, MCC-CM-001, and MCC-TC-001 -- not a second
certification system.

Stage mapping to MCC-CP-001 Section 9 (documented explicitly, not silently
reinterpreted):

    Stage 1 Preflight            -> CP-001 9.1 Registration + 9.2 Environment Validation
    Stage 2 Conformance Run      -> CP-001 9.3 Conformance Evaluation
    Stage 3 Evidence Bundle      -> CP-001 9.4 Evidence Generation
    Stage 4 Certification Manifest -> CP-001 9.7 Artifact Generation (manifest half)
    Stage 5 Technical Certificate   -> CP-001 9.7 Artifact Generation (certificate half),
                                        gated by CP-001 9.5 Conformance Assessment /
                                        9.6 Certification Decision (folded into Stage 2's
                                        own PASS/FAIL/NOT_APPLICABLE result set, since a
                                        FAIL there means Stages 4-5 never run -- CI-003
                                        "Certification precedes Technical Certificate
                                        issuance")
    Stage 6 Offline Verification -> not a numbered CP-001 pipeline stage; an additional
                                     safety gate over Goal G3 "Independent Verification"
                                     / Invariant CI-008 "Certification SHALL be
                                     independently verifiable" -- this pipeline never
                                     reports success without it.

CP-001 9.8 Publication is explicitly OPTIONAL ("Certification outputs MAY be
published") and is not implemented by this PR -- writing the run's artifact
tree to ``--output`` already satisfies Stage 7 Artifact Generation; nothing
further is "published" (no registry, no distribution).
"""

from __future__ import annotations

import hashlib
import json
import shutil
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from mcc_core.signing import SigningKey, canonical_bytes
from mcc_evidence.cm001_manifest import build_cm001_manifest, verify_cm001_manifest, write_cm001_manifest
from mcc_evidence.eb001_export import EB001BundleInput, EvidenceItemInput, build_eb001_bundle
from mcc_evidence.eb001_verify import verify_eb001_bundle
from mcc_evidence.tc001_certificate import (
    CertificateIdRegistry,
    IncompleteTC001CertificateError,
    RevocationRegistry,
    TC001StructuralError,
    TrustAnchor,
    TrustAnchorRegistry,
    build_technical_certificate,
    read_tc001_certificate,
    sign_technical_certificate,
    verify_technical_certificate,
    write_tc001_certificate,
)

from .target import (
    CertificationTarget,
    CertifyError,
    MalformedCertificationTargetError,
    RequirementOutcome,
    UnknownCertificationTargetError,
    resolve_target,
)

TOOL_NAME = "mcc-certify"
TOOL_VERSION = "0.1.0"
CP001_SPECIFICATION_VERSION = "1.0"

CONFORMANCE_DIR = "conformance"
EVIDENCE_BUNDLE_DIR = "evidence-bundle"
MANIFEST_FILE = "certification-manifest.json"
CERTIFICATE_FILE = "technical-certificate.json"
VERIFICATION_REPORT_FILE = "verification-report.json"
RESULT_FILE = "certification-result.json"
RUN_METADATA_FILE = "run-metadata.json"
README_FILE = "README.txt"


class CertificationOutcome(str, Enum):
    CERTIFIED = "CERTIFIED"
    NOT_CERTIFIED = "NOT_CERTIFIED"


class StageStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"


class RunAlreadyExistsError(CertifyError):
    """Raised when the target run directory already exists and --force was
    not supplied. Fail closed: an existing completed (or failed) run is
    never silently overwritten."""


class OutputLocationError(CertifyError):
    """Raised when the requested output location is unsafe or unusable
    (e.g. a file exists where a directory is required)."""


@dataclass
class CertificationStageResult:
    stage: str
    status: StageStatus
    detail: str = ""
    artifacts: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "stage": self.stage,
            "status": self.status.value,
            "detail": self.detail,
            "artifacts": dict(self.artifacts),
        }


@dataclass
class CertificationRequest:
    """Public request model. ``run_id`` and ``timestamp`` default to
    deterministic-friendly values only if the caller supplies them --
    reproducibility across two runs REQUIRES the caller to pass the same
    explicit ``run_id`` and ``timestamp`` both times (see
    docs/CERTIFICATION_PIPELINE.md, "Determinism and Reproducibility")."""

    target_id: str
    output_dir: Path
    run_id: Optional[str] = None
    timestamp: Optional[str] = None
    profile: Optional[str] = None
    verify: bool = True
    force: bool = False


@dataclass
class CertificationResult:
    target_id: str
    certification_profile: str
    run_id: str
    outcome: CertificationOutcome
    stages: List[CertificationStageResult]
    run_dir: Optional[Path]
    certificate_id: Optional[str] = None
    failure_reason: Optional[str] = None
    failed_stage: Optional[str] = None

    @property
    def success(self) -> bool:
        return self.outcome is CertificationOutcome.CERTIFIED

    def to_dict(self) -> dict:
        # "run_dir_relative" is target_id/run_id -- deterministic and
        # reproducible. The absolute filesystem path is deliberately NOT
        # part of this canonical dict (it is a volatile, host-specific
        # value); callers that need the real path on disk use
        # CertificationResult.run_dir directly (a Path, not serialized here).
        return {
            "target_id": self.target_id,
            "certification_profile": self.certification_profile,
            "run_id": self.run_id,
            "outcome": self.outcome.value,
            "stages": [s.to_dict() for s in self.stages],
            "run_dir_relative": f"{self.target_id}/{self.run_id}" if self.run_dir is not None else None,
            "certificate_id": self.certificate_id,
            "failure_reason": self.failure_reason,
            "failed_stage": self.failed_stage,
        }


def _parse_rfc3339(ts: str) -> int:
    normalized = ts.strip()
    if normalized.endswith("Z"):
        normalized = normalized[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(normalized)
    except ValueError as e:
        raise CertifyError(f"invalid RFC3339 timestamp {ts!r}: {e}") from e
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return int(dt.timestamp())


def _derive_signing_key(target_id: str, run_id: str) -> SigningKey:
    """Deterministic Ed25519 key derivation for the reference/internal
    certification path, so identical (target_id, run_id) inputs always
    produce byte-identical signatures across repeated runs (required for
    the deterministic-regeneration guarantee). This is NOT a production
    PKI/CA or key-management system: a real deployment SHOULD supply its
    own persistent Issuer signing key out of band; this derivation exists
    only so the reference fixture path is genuinely reproducible without
    requiring the caller to manage key material for internal test runs."""
    seed = hashlib.sha256(f"mcc-certify:{target_id}:{run_id}".encode("utf-8")).digest()
    kid = f"mcc-certify-{target_id}"
    return SigningKey(Ed25519PrivateKey.from_private_bytes(seed), kid)


class CertificationPipeline:
    """The one, public, reusable certification pipeline. The CLI
    (``mcc_certify.cli``) calls exactly this class -- there is no second
    implementation."""

    def run(self, request: CertificationRequest) -> CertificationResult:
        stages: List[CertificationStageResult] = []
        # Mutated as the pipeline progresses so `fail()` always reports the
        # actual resolved identity/failed-run-directory, not the raw request.
        progress = {
            "certification_profile": request.profile or "unknown",
            "run_id": request.run_id or "unknown",
            "failed_run_dir": None,
        }

        def fail(stage: str, reason: str) -> CertificationResult:
            stages.append(CertificationStageResult(stage, StageStatus.FAIL, reason))
            return CertificationResult(
                target_id=request.target_id,
                certification_profile=progress["certification_profile"],
                run_id=progress["run_id"],
                outcome=CertificationOutcome.NOT_CERTIFIED,
                stages=stages,
                run_dir=progress["failed_run_dir"],
                failure_reason=reason,
                failed_stage=stage,
            )

        # --- Stage 1: Preflight -------------------------------------------------
        try:
            target = resolve_target(request.target_id)
        except UnknownCertificationTargetError as e:
            return fail("preflight", str(e))

        certification_profile = request.profile or target.certification_profile
        run_id = request.run_id or uuid.uuid4().hex
        progress["certification_profile"] = certification_profile
        progress["run_id"] = run_id
        if request.timestamp is not None:
            try:
                issuance_timestamp = _parse_rfc3339(request.timestamp)
            except CertifyError as e:
                return fail("preflight", str(e))
        else:
            issuance_timestamp = int(time.time())

        output_dir = Path(request.output_dir)
        target_dir = output_dir / target.target_id
        final_run_dir = target_dir / run_id
        failed_run_dir = target_dir / f"{run_id}.failed"
        tmp_run_dir = target_dir / f".tmp-{run_id}-{uuid.uuid4().hex[:8]}"

        if final_run_dir.exists():
            if not request.force:
                return fail(
                    "preflight",
                    f"run directory already exists: {final_run_dir} (pass --force to overwrite)",
                )
            shutil.rmtree(final_run_dir)
        if failed_run_dir.exists() and request.force:
            shutil.rmtree(failed_run_dir)

        try:
            target_dir.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            return fail("preflight", f"cannot create output location {target_dir}: {e}")
        if target_dir.exists() and not target_dir.is_dir():
            return fail("preflight", f"output location exists and is not a directory: {target_dir}")

        tmp_run_dir.mkdir(parents=True, exist_ok=False)
        # From here on, any failure moves tmp_run_dir to failed_run_dir --
        # record that now so `fail()` reports the real diagnostic location.
        progress["failed_run_dir"] = failed_run_dir

        run_metadata = {
            "tool_name": TOOL_NAME,
            "tool_version": TOOL_VERSION,
            "cp001_specification_version": CP001_SPECIFICATION_VERSION,
            "target_id": target.target_id,
            "target_type": target.target_type,
            "implementation_version": target.implementation_version,
            "certification_profile": certification_profile,
            "run_id": run_id,
            "issuance_timestamp": issuance_timestamp,
            "provenance": dict(target.provenance),
            "declared_capabilities": list(target.declared_capabilities),
        }
        (tmp_run_dir / RUN_METADATA_FILE).write_bytes(canonical_bytes(run_metadata))
        stages.append(CertificationStageResult(
            "preflight", StageStatus.PASS,
            f"resolved target {target.target_id!r}, run_id={run_id!r}, profile={certification_profile!r}",
            artifacts={"run_metadata": RUN_METADATA_FILE},
        ))

        # --- Stage 2: Conformance Run -------------------------------------------
        try:
            requirement_results = target.run_conformance_checks()
        except MalformedCertificationTargetError as e:
            shutil.move(str(tmp_run_dir), str(failed_run_dir))
            return fail("conformance_run", str(e))

        conformance_dir = tmp_run_dir / CONFORMANCE_DIR
        conformance_dir.mkdir(parents=True, exist_ok=True)
        conformance_run_payload = {
            "target_id": target.target_id,
            "certification_profile": certification_profile,
            "run_id": run_id,
            "requirement_results": [r.to_dict() for r in requirement_results],
        }
        (conformance_dir / "conformance-run.json").write_bytes(canonical_bytes(conformance_run_payload))
        stages.append(CertificationStageResult(
            "conformance_run", StageStatus.PASS,
            f"evaluated {len(requirement_results)} requirement(s)",
            artifacts={"conformance_run": f"{CONFORMANCE_DIR}/conformance-run.json"},
        ))

        failed_requirements = [r for r in requirement_results if r.outcome is RequirementOutcome.FAIL]
        conformance_passed = not failed_requirements

        # --- Stage 3: Evidence Bundle (CI-002: evidence precedes certification,
        # generated regardless of the conformance outcome) ----------------------
        evidence_items = [
            EvidenceItemInput(
                name=f"req-{r.requirement_id}.json",
                content=canonical_bytes(r.to_dict()),
            )
            for r in sorted(requirement_results, key=lambda r: r.requirement_id)
        ]
        bundle_input = EB001BundleInput(
            cp001_specification_version=CP001_SPECIFICATION_VERSION,
            certification_run_id=run_id,
            certification_subject_id=target.target_id,
            evidence_items=evidence_items,
            bundle_id=f"{target.target_id}-{run_id}-evidence",
        )
        bundle_path = tmp_run_dir / EVIDENCE_BUNDLE_DIR
        try:
            build_eb001_bundle(bundle_input, bundle_path)
        except Exception as e:  # noqa: BLE001 - fail closed on any producer defect
            shutil.move(str(tmp_run_dir), str(failed_run_dir))
            return fail("evidence_bundle", f"Evidence Bundle generation failed: {e}")

        eb_result = verify_eb001_bundle(bundle_path)
        if not eb_result.valid:
            shutil.move(str(tmp_run_dir), str(failed_run_dir))
            return fail("evidence_bundle", f"generated Evidence Bundle failed self-verification: {eb_result.failures}")
        stages.append(CertificationStageResult(
            "evidence_bundle", StageStatus.PASS, f"bundle_id={bundle_input.bundle_id!r}",
            artifacts={"evidence_bundle": EVIDENCE_BUNDLE_DIR},
        ))

        if not conformance_passed:
            shutil.move(str(tmp_run_dir), str(failed_run_dir))
            reason = (
                f"{len(failed_requirements)} requirement(s) FAILed conformance evaluation: "
                f"{[r.requirement_id for r in failed_requirements]}"
            )
            stages.append(CertificationStageResult("certification_manifest", StageStatus.FAIL, "skipped: conformance did not PASS"))
            return CertificationResult(
                target_id=target.target_id, certification_profile=certification_profile, run_id=run_id,
                outcome=CertificationOutcome.NOT_CERTIFIED, stages=stages, run_dir=failed_run_dir,
                failure_reason=reason, failed_stage="conformance_run",
            )

        # --- Stage 4: Certification Manifest ------------------------------------
        try:
            manifest = build_cm001_manifest(bundle_path)
            manifest_path = write_cm001_manifest(manifest, tmp_run_dir / MANIFEST_FILE)
        except Exception as e:  # noqa: BLE001
            shutil.move(str(tmp_run_dir), str(failed_run_dir))
            return fail("certification_manifest", f"Certification Manifest generation failed: {e}")

        manifest_result = verify_cm001_manifest(manifest, bundle_path)
        if not manifest_result.valid:
            shutil.move(str(tmp_run_dir), str(failed_run_dir))
            return fail("certification_manifest", f"generated Manifest failed self-verification: {manifest_result.failures}")
        stages.append(CertificationStageResult(
            "certification_manifest", StageStatus.PASS, "manifest bound to the Evidence Bundle",
            artifacts={"certification_manifest": MANIFEST_FILE},
        ))

        # --- Stage 5: Technical Certificate --------------------------------------
        signing_key = _derive_signing_key(target.target_id, run_id)
        certificate_id = f"{target.target_id}-{run_id}-certificate"
        try:
            cert = build_technical_certificate(
                certificate_id=certificate_id,
                subject_id=target.target_id,
                cp001_specification_version=CP001_SPECIFICATION_VERSION,
                certified_capability_profiles=target.declared_capabilities,
                manifest_path=manifest_path,
                manifest_id=f"{target.target_id}-{run_id}-manifest",
                primary_evidence_bundle_path=bundle_path,
                issuer_id=f"mcc-certify-issuer-{target.target_id}",
                issuance_timestamp=issuance_timestamp,
                label=certification_profile,
                id_registry=CertificateIdRegistry(),
            )
            signed_cert = sign_technical_certificate(cert, signing_key)
            write_tc001_certificate(signed_cert, tmp_run_dir / CERTIFICATE_FILE)
        except (IncompleteTC001CertificateError, TC001StructuralError) as e:
            shutil.move(str(tmp_run_dir), str(failed_run_dir))
            return fail("technical_certificate", f"Technical Certificate generation failed: {e}")

        stages.append(CertificationStageResult(
            "technical_certificate", StageStatus.PASS, f"certificate_id={certificate_id!r}",
            artifacts={"technical_certificate": CERTIFICATE_FILE},
        ))

        # --- Stage 6: Offline Verification ---------------------------------------
        trust = TrustAnchorRegistry([TrustAnchor(
            issuer_id=f"mcc-certify-issuer-{target.target_id}", kid=signing_key.kid,
            public_key=signing_key.public_key(),
        )])
        verification = verify_technical_certificate(
            signed_cert.to_dict(), trust_anchors=trust, revocation_registry=RevocationRegistry(),
            manifest_path=manifest_path, primary_evidence_bundle_path=bundle_path,
            now=issuance_timestamp,
        )
        identity_errors = _check_run_identity(
            signed_cert.to_dict(), run_metadata, certification_profile,
        )
        verification_report = {
            "overall_status": verification.overall_status.value,
            "valid": verification.valid and not identity_errors,
            "checks": [c.to_dict() for c in verification.checks],
            "failures": list(verification.failures) + identity_errors,
        }
        (tmp_run_dir / VERIFICATION_REPORT_FILE).write_bytes(canonical_bytes(verification_report))

        if not verification.valid or identity_errors:
            shutil.move(str(tmp_run_dir), str(failed_run_dir))
            return fail("offline_verification", f"offline verification failed: {verification_report['failures']}")

        stages.append(CertificationStageResult(
            "offline_verification", StageStatus.PASS, "full chain independently verified",
            artifacts={"verification_report": VERIFICATION_REPORT_FILE},
        ))

        # --- Finalize: write the result, README, then atomically publish --------
        result = CertificationResult(
            target_id=target.target_id, certification_profile=certification_profile, run_id=run_id,
            outcome=CertificationOutcome.CERTIFIED, stages=stages, run_dir=final_run_dir,
            certificate_id=certificate_id,
        )
        artifact_hashes = _hash_artifacts(tmp_run_dir)
        result_payload = result.to_dict()
        result_payload["artifact_hashes"] = artifact_hashes
        (tmp_run_dir / RESULT_FILE).write_bytes(canonical_bytes(result_payload))
        (tmp_run_dir / README_FILE).write_text(_readme_text(target.target_id, run_id, certificate_id), encoding="utf-8")

        tmp_run_dir.rename(final_run_dir)
        result.run_dir = final_run_dir
        return result


def _check_run_identity(cert_dict: dict, run_metadata: dict, certification_profile: str) -> List[str]:
    """Independently re-derive expected identity fields from the Stage-1
    run-metadata record (written before any artifact existed) and compare
    against what the signed Certificate actually declares -- catches a
    target/profile/run mismatch that a purely internal cross-artifact check
    (already performed by verify_technical_certificate) would not, since
    that check only compares the Certificate against the Manifest/Bundle,
    never against the pipeline's own recorded intent."""
    errors = []
    if cert_dict.get("subject_id") != run_metadata["target_id"]:
        errors.append(
            f"identity mismatch: certificate subject_id {cert_dict.get('subject_id')!r} != "
            f"run target_id {run_metadata['target_id']!r}"
        )
    if cert_dict.get("label") != certification_profile:
        errors.append(
            f"identity mismatch: certificate label {cert_dict.get('label')!r} != "
            f"certification_profile {certification_profile!r}"
        )
    expected_certificate_id = f"{run_metadata['target_id']}-{run_metadata['run_id']}-certificate"
    if cert_dict.get("certificate_id") != expected_certificate_id:
        errors.append(
            f"identity mismatch: certificate_id {cert_dict.get('certificate_id')!r} != "
            f"expected {expected_certificate_id!r} (target_id+run_id derived)"
        )
    return errors


def _hash_artifacts(run_dir: Path) -> Dict[str, str]:
    """Deterministic sha256 of every generated top-level artifact file
    (not the evidence-bundle directory's individual files -- those are
    already covered by the Bundle's own Integrity Record)."""
    hashes = {}
    for name in (MANIFEST_FILE, CERTIFICATE_FILE, VERIFICATION_REPORT_FILE, RUN_METADATA_FILE):
        path = run_dir / name
        if path.exists():
            hashes[name] = "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()
    return hashes


def _readme_text(target_id: str, run_id: str, certificate_id: str) -> str:
    return (
        "MCC Normative v1.0 Certification Run\n"
        "=====================================\n\n"
        f"target_id: {target_id}\n"
        f"run_id: {run_id}\n"
        f"certificate_id: {certificate_id}\n\n"
        "This run was independently offline-verified before being reported as\n"
        "successful (see verification-report.json). It is NOT an official\n"
        "certificate for a production reference ecosystem -- see\n"
        "docs/CERTIFICATION_PIPELINE.md for current limitations.\n\n"
        "Reproduce offline verification with:\n"
        f"    python -m mcc_certify verify {run_id}\n"
        "(run from the parent of this directory's target_id folder, or pass\n"
        "the full run directory path -- see the documentation for the exact\n"
        "invocation).\n"
    )
