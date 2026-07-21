"""Certification decision + deterministic fingerprint.

Fail-closed: an adapter is CERTIFIED only when the version matches, metadata is
complete, and every mandatory vector passed with no error/skip. A percentage is
computed for information only and never controls the decision.
"""

from __future__ import annotations

from typing import List

from mcc_core.signing import canonical_bytes, sha256_hex

from .models import (
    SUITE_VERSION,
    AdapterMetadata,
    CaseResult,
    CaseStatus,
    CertificationDecision,
    CertificationStatus,
    Totals,
)


def certification_fingerprint(metadata: AdapterMetadata, contract_version: str,
                              vector_manifest_digest: str,
                              results: List[CaseResult]) -> str:
    """Stable fingerprint binding adapter identity + adapter version + contract
    version + suite version + vector manifest digest + stable case outcomes.

    Excludes timestamps, durations, and any environment-specific field, so it is
    identical across repeated identical runs."""
    payload = {
        "adapter": {
            "name": metadata.name,
            "version": metadata.version,
            "implementation_id": metadata.implementation_id,
            "framework": metadata.framework,
            "claimed_contract_version": metadata.claimed_contract_version,
        },
        "contract_version": contract_version,
        "suite_version": SUITE_VERSION,
        "vector_manifest_digest": vector_manifest_digest,
        "cases": sorted(
            [{"id": r.vector_id, "status": r.status.value,
              "failure_code": r.failure_code} for r in results],
            key=lambda c: str(c["id"]),
        ),
    }
    return sha256_hex(canonical_bytes(payload))


def decide_certification(metadata: AdapterMetadata, contract_version: str,
                         results: List[CaseResult], totals: Totals,
                         fingerprint: str) -> CertificationDecision:
    """Compute the fail-closed certification decision."""
    reasons: List[str] = []

    missing = metadata.missing_fields()
    if missing:
        reasons.append(f"adapter metadata incomplete: missing {missing}")
    if metadata.claimed_contract_version != contract_version:
        reasons.append(
            f"adapter claims contract version {metadata.claimed_contract_version!r} "
            f"but certification target is {contract_version!r}")

    has_error = False
    for r in results:
        if not r.mandatory:
            continue
        if r.status is CaseStatus.ERROR:
            has_error = True
            reasons.append(f"{r.vector_id}: ERROR ({r.failure_code})")
        elif r.status is CaseStatus.FAIL:
            reasons.append(f"{r.vector_id}: FAIL ({r.failure_code})")
        elif r.status is CaseStatus.SKIP:
            reasons.append(f"{r.vector_id}: mandatory vector was skipped")

    if metadata.claimed_contract_version != contract_version or missing:
        status = CertificationStatus.NOT_CERTIFIED
    elif has_error:
        # An indeterminate result must never certify.
        status = CertificationStatus.ERROR
    elif reasons:
        status = CertificationStatus.NOT_CERTIFIED
    elif totals.mandatory_total == 0:
        status = CertificationStatus.ERROR
        reasons.append("no mandatory vectors were executed")
    else:
        status = CertificationStatus.CERTIFIED

    return CertificationDecision(
        status=status, reasons=reasons, fingerprint=fingerprint,
        informational_pass_percentage=totals.pass_percentage)


__all__ = ["certification_fingerprint", "decide_certification"]
