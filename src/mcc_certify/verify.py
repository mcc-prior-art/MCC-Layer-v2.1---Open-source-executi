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
from typing import List, Optional, Union

from mcc_evidence.cm001_manifest import read_cm001_manifest
from mcc_evidence.eb001_schema import INTEGRITY_RECORD_NAME
from mcc_evidence.tc001_certificate import RevocationRegistry, TrustAnchor, TrustAnchorRegistry, verify_technical_certificate

from .pipeline import (
    CERTIFICATE_FILE,
    EVIDENCE_BUNDLE_DIR,
    MANIFEST_FILE,
    PUBLICATION_RECORD_FILE,
    RUN_METADATA_FILE,
    _check_run_identity,
    _derive_signing_key,
)
from .publication import (
    PublicationIndex,
    PublicationRecord,
    read_publication_index,
    verify_publication_record,
)
from .target import CertifyError
from .trust_store import TrustStore, read_trust_store


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


def verify_certification_run_trusted(
    run_dir: Path | str,
    *,
    trust_store: Union[TrustStore, Path, str],
    publication_index: Optional[Union[PublicationIndex, Path, str]] = None,
    require_published: bool = False,
) -> dict:
    """Offline verification of a completed certification run **against an
    explicit, externally-supplied Trust Anchor set** (PR #68 Section F) --
    the real trust boundary a production deployment uses, in contrast to
    :func:`verify_certification_run`'s internal, self-consistency-only
    fixture check (which re-derives the same key the pipeline used and so
    cannot detect an untrusted issuer).

    ``trust_store`` and (if supplied) ``publication_index`` may be passed
    as already-loaded objects or as filesystem paths -- this function never
    performs network I/O and never fetches trust dynamically (MCC-TC-001
    Section 16.3). A missing or malformed Trust Store fails closed
    (``RunVerificationError``) rather than silently proceeding without
    trust.

    When ``require_published`` is True, the Technical Certificate's
    ``certificate_id`` MUST be present in ``publication_index`` with a
    Publication Record whose Hash References verify against this run's own
    artifacts -- absence, or a mismatching record, is a verification
    failure, not an error.
    """
    run_dir = Path(run_dir)
    required = (RUN_METADATA_FILE, CERTIFICATE_FILE, MANIFEST_FILE, EVIDENCE_BUNDLE_DIR)
    missing = [name for name in required if not (run_dir / name).exists()]
    if missing:
        raise RunVerificationError(f"run directory {run_dir} is missing required artifact(s): {missing}")

    if trust_store is None:
        raise RunVerificationError(
            "verify_certification_run_trusted requires an explicit trust_store -- "
            "there is no fixture/default trust fallback"
        )
    if isinstance(trust_store, (str, Path)):
        try:
            trust_store = read_trust_store(trust_store)
        except CertifyError as e:
            raise RunVerificationError(f"cannot load trust_store: {e}") from e
    if not isinstance(trust_store, TrustStore):
        raise RunVerificationError("trust_store must be a TrustStore instance or a path to one")

    if publication_index is not None and isinstance(publication_index, (str, Path)):
        try:
            publication_index = read_publication_index(publication_index)
        except CertifyError as e:
            raise RunVerificationError(f"cannot load publication_index: {e}") from e

    run_metadata = json.loads((run_dir / RUN_METADATA_FILE).read_bytes())
    cert_dict = json.loads((run_dir / CERTIFICATE_FILE).read_bytes())
    bundle_path = run_dir / EVIDENCE_BUNDLE_DIR
    manifest_path = run_dir / MANIFEST_FILE

    trust = trust_store.to_trust_anchor_registry(run_metadata["issuance_timestamp"])
    verification = verify_technical_certificate(
        cert_dict, trust_anchors=trust, revocation_registry=RevocationRegistry(),
        manifest_path=manifest_path, primary_evidence_bundle_path=bundle_path,
        now=run_metadata["issuance_timestamp"],
    )
    identity_errors = _check_run_identity(cert_dict, run_metadata, run_metadata["certification_profile"])

    publication_failures: List[str] = []
    certificate_id = cert_dict.get("certificate_id")
    local_publication_record_path = run_dir / PUBLICATION_RECORD_FILE
    if local_publication_record_path.exists():
        try:
            local_record = PublicationRecord.from_dict(json.loads(local_publication_record_path.read_bytes()))
        except CertifyError as e:
            publication_failures.append(f"local Publication Record is malformed: {e}")
            local_record = None
        if local_record is not None:
            if local_record.certificate_id != certificate_id:
                publication_failures.append(
                    f"local Publication Record certificate_id {local_record.certificate_id!r} does not match "
                    f"this run's certificate_id {certificate_id!r}"
                )
            record_failures = verify_publication_record(
                local_record,
                certification_manifest_path=manifest_path,
                technical_certificate_path=run_dir / CERTIFICATE_FILE,
                evidence_bundle_integrity_record_path=bundle_path / INTEGRITY_RECORD_NAME,
            )
            publication_failures.extend(record_failures)

    if publication_index is not None:
        indexed_record = publication_index.get(certificate_id) if certificate_id else None
        if indexed_record is None:
            if require_published:
                publication_failures.append(
                    f"certificate_id {certificate_id!r} is not present in the supplied Publication Index"
                )
        else:
            indexed_failures = verify_publication_record(
                indexed_record,
                certification_manifest_path=manifest_path,
                technical_certificate_path=run_dir / CERTIFICATE_FILE,
                evidence_bundle_integrity_record_path=bundle_path / INTEGRITY_RECORD_NAME,
            )
            publication_failures.extend(f"publication_index entry: {f}" for f in indexed_failures)
    elif require_published:
        publication_failures.append("require_published=True but no publication_index was supplied")

    all_failures = list(verification.failures) + identity_errors + publication_failures
    return {
        "run_dir": str(run_dir),
        "overall_status": verification.overall_status.value,
        "valid": verification.valid and not identity_errors and not publication_failures,
        "checks": [c.to_dict() for c in verification.checks],
        "failures": all_failures,
    }
