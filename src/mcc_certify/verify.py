"""Standalone offline verification of a completed certification run
directory -- independent of the pipeline/process that produced it.

Reads only what is on disk under a run directory (never an in-memory
"already verified" flag) and re-verifies the complete chain: Evidence
Bundle, Certification Manifest, Technical Certificate, every Hash
Reference, every cross-artifact binding, and target/profile/run identity
consistency against the run's own recorded ``run-metadata.json``. Reuses
``mcc_evidence``'s Wave A/B/C verifiers directly -- no parallel
verification logic.

Trust-anchor limitation (disclosed, not hidden): this reference pipeline
does not yet implement Trust Anchor distribution (MCC-TC-001 Section 16.2
explicitly leaves the distribution mechanism out of scope). This verifier
re-derives the expected signing key from the run's own recorded
``target_id``/``run_id`` using the same deterministic derivation the
pipeline used to produce it (see ``pipeline._derive_signing_key``) --
this proves the chain is internally self-consistent and untampered, but is
**not** a substitute for a real, independently-distributed Trust Anchor a
production deployment would use. See docs/CERTIFICATION_PIPELINE.md,
"Security and Trust Boundaries".
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from mcc_evidence.cm001_manifest import read_cm001_manifest
from mcc_evidence.tc001_certificate import RevocationRegistry, TrustAnchor, TrustAnchorRegistry, verify_technical_certificate

from .pipeline import CERTIFICATE_FILE, EVIDENCE_BUNDLE_DIR, MANIFEST_FILE, RUN_METADATA_FILE, _check_run_identity, _derive_signing_key
from .target import CertifyError


class RunVerificationError(CertifyError):
    """Raised when the run directory itself is malformed (missing a
    required artifact file) -- distinct from a verification *failure*,
    which is reported in the returned report, not raised."""


def verify_certification_run(run_dir: Path | str) -> dict:
    run_dir = Path(run_dir)
    required = (RUN_METADATA_FILE, CERTIFICATE_FILE, MANIFEST_FILE, EVIDENCE_BUNDLE_DIR)
    missing = [name for name in required if not (run_dir / name).exists()]
    if missing:
        raise RunVerificationError(f"run directory {run_dir} is missing required artifact(s): {missing}")

    run_metadata = json.loads((run_dir / RUN_METADATA_FILE).read_bytes())
    cert_dict = json.loads((run_dir / CERTIFICATE_FILE).read_bytes())
    bundle_path = run_dir / EVIDENCE_BUNDLE_DIR
    manifest_path = run_dir / MANIFEST_FILE

    signing_key = _derive_signing_key(run_metadata["target_id"], run_metadata["run_id"])
    trust = TrustAnchorRegistry([TrustAnchor(
        issuer_id=f"mcc-certify-issuer-{run_metadata['target_id']}", kid=signing_key.kid,
        public_key=signing_key.public_key(),
    )])

    verification = verify_technical_certificate(
        cert_dict, trust_anchors=trust, revocation_registry=RevocationRegistry(),
        manifest_path=manifest_path, primary_evidence_bundle_path=bundle_path,
        now=run_metadata["issuance_timestamp"],
    )
    identity_errors = _check_run_identity(cert_dict, run_metadata, run_metadata["certification_profile"])

    return {
        "run_dir": str(run_dir),
        "overall_status": verification.overall_status.value,
        "valid": verification.valid and not identity_errors,
        "checks": [c.to_dict() for c in verification.checks],
        "failures": list(verification.failures) + identity_errors,
    }
