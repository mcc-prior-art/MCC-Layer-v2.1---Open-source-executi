"""Signed, offline-verifiable Evidence Bundle for an independent assurance
run (PR #71, Workstream M).

This is deliberately NOT the same thing as ``mcc_evidence``'s Governance
Evidence Bundle (which is evidence of a single already-completed governed
decision). This bundle is evidence of an *assurance run itself*: which
workstream test modules executed, against which source revision, with what
pass/fail/skip outcome per test, bound together by MCC-CM-001's Hash
Reference primitive (``mcc_evidence.hash_reference``, reused unchanged) and
optionally signed with an assurance-run Ed25519 key so a reviewer can detect
post-run tampering of the findings offline, without re-running anything.

Signing here proves only "these findings were not altered after the run
that produced them" -- it is not an MCC-Core Decision Token, carries no
governance authority, and a signature verifying does not by itself mean the
assurance run's own findings are correct (a reviewer still has to read the
threat model and the findings, per ``THIRD_PARTY_RUNBOOK.md``).
"""

from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from mcc_core.signing import SigningKey, canonical_bytes, public_key_from_b64, verify_token
from mcc_evidence.hash_reference import HashReference, compute_hash_reference, verify_hash_reference

BUNDLE_SCHEMA_VERSION = "mcc-independent-assurance-evidence/1"
MANIFEST_NAME = "manifest.json"
FINDINGS_DIR = "findings"

#: Fields legitimately non-deterministic across two runs of the identical
#: suite against the identical source revision (documented, excluded from
#: byte-for-byte comparison -- mirrors mcc_evidence's own convention).
NON_DETERMINISTIC_MANIFEST_FIELDS = ("run_id", "started_at", "finished_at")


class EvidenceBundleError(Exception):
    """The bundle could not be built or is structurally invalid. Fail
    closed: callers must never treat a raised error as an absent bundle."""


def source_commit_sha(repo_root: Path) -> str:
    """Best-effort provenance only -- never load-bearing for a security
    conclusion. Returns ``"unknown"`` rather than raising when git metadata
    is unavailable (matches ``mcc_certify.ecosystems._source_commit_sha``)."""
    try:
        out = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=str(repo_root), capture_output=True,
            text=True, timeout=5, check=True,
        )
        return out.stdout.strip() or "unknown"
    except Exception:  # noqa: BLE001
        return "unknown"


@dataclass
class EvidenceVerificationResult:
    schema_supported: bool
    integrity_valid: bool
    findings_hash_valid: bool
    signature_present: bool
    signature_valid: Optional[bool]
    signer_trusted: Optional[bool]
    overall_status: str
    problems: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "schema_supported": self.schema_supported,
            "integrity_valid": self.integrity_valid,
            "findings_hash_valid": self.findings_hash_valid,
            "signature_present": self.signature_present,
            "signature_valid": self.signature_valid,
            "signer_trusted": self.signer_trusted,
            "overall_status": self.overall_status,
            "problems": self.problems,
        }


def build_evidence_bundle(*, output_dir: Path, run_report: Dict[str, Any], repo_root: Path,
                           signing_key: Optional[SigningKey] = None) -> Dict[str, Any]:
    """Write ``run_report`` (a ``assurance.runner.RunReport.to_dict()``) plus
    a manifest binding it to a Hash Reference, into ``output_dir``. Returns
    the manifest dict. Fail-closed: an incomplete/malformed ``run_report``
    raises rather than producing a bundle that looks complete."""
    if "modules" not in run_report or "run_id" not in run_report:
        raise EvidenceBundleError("run_report is missing required fields (modules/run_id)")

    output_dir = Path(output_dir)
    findings_dir = output_dir / FINDINGS_DIR
    findings_dir.mkdir(parents=True, exist_ok=True)

    findings_path = findings_dir / "workstream_results.json"
    findings_bytes = canonical_bytes(run_report)
    findings_path.write_bytes(findings_bytes)

    findings_ref = compute_hash_reference(findings_bytes, f"{FINDINGS_DIR}/workstream_results.json")

    manifest: Dict[str, Any] = {
        "schema_version": BUNDLE_SCHEMA_VERSION,
        "run_id": run_report["run_id"],
        "started_at": run_report.get("started_at"),
        "finished_at": run_report.get("finished_at"),
        "source_commit_sha": source_commit_sha(repo_root),
        "summary": run_report.get("summary", {}),
        "findings_hash_reference": findings_ref.to_dict(),
    }

    if signing_key is not None:
        manifest = signing_key.sign_token(manifest)

    (output_dir / MANIFEST_NAME).write_text(
        json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8"
    )
    return manifest


def verify_evidence_bundle(bundle_dir: Path, *,
                            trusted_public_keys_b64: Optional[List[str]] = None) -> EvidenceVerificationResult:
    """Offline, read-only verification: recomputes the findings Hash
    Reference independently and, if a signature is present, checks it
    against ``trusted_public_keys_b64``. Never mutates the bundle, never
    re-runs anything, never executes governed actions."""
    bundle_dir = Path(bundle_dir)
    problems: List[str] = []
    manifest_path = bundle_dir / MANIFEST_NAME

    if not manifest_path.is_file():
        return EvidenceVerificationResult(
            schema_supported=False, integrity_valid=False, findings_hash_valid=False,
            signature_present=False, signature_valid=None, signer_trusted=None,
            overall_status="INVALID", problems=["manifest.json missing"],
        )

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        return EvidenceVerificationResult(
            schema_supported=False, integrity_valid=False, findings_hash_valid=False,
            signature_present=False, signature_valid=None, signer_trusted=None,
            overall_status="INVALID", problems=[f"manifest.json is not valid JSON: {exc}"],
        )

    schema_supported = manifest.get("schema_version") == BUNDLE_SCHEMA_VERSION
    if not schema_supported:
        problems.append(f"unsupported schema_version {manifest.get('schema_version')!r}")

    findings_hash_valid = False
    try:
        ref = HashReference.from_dict(manifest["findings_hash_reference"])
        findings_bytes = (bundle_dir / ref.content_ref).read_bytes()
        findings_hash_valid = verify_hash_reference(ref, findings_bytes)
        if not findings_hash_valid:
            problems.append("findings file digest does not match manifest Hash Reference")
    except Exception as exc:  # noqa: BLE001
        problems.append(f"findings integrity check failed: {exc}")

    signature_present = "sig" in manifest
    signature_valid: Optional[bool] = None
    signer_trusted: Optional[bool] = None
    if signature_present:
        signature_valid = False
        signer_trusted = False
        kid = manifest.get("kid")
        for pub_b64 in trusted_public_keys_b64 or []:
            try:
                if verify_token(manifest, public_key_from_b64(pub_b64)):
                    signature_valid = True
                    signer_trusted = True
                    break
            except Exception:  # noqa: BLE001
                continue
        if not signature_valid:
            problems.append(
                f"signature (kid={kid!r}) did not verify against any supplied trusted public key"
            )

    integrity_valid = schema_supported and findings_hash_valid

    if not integrity_valid:
        overall_status = "INVALID"
    elif signature_present and not signer_trusted:
        overall_status = "INTACT_UNTRUSTED_SIGNER"
    else:
        overall_status = "INTACT"

    return EvidenceVerificationResult(
        schema_supported=schema_supported, integrity_valid=integrity_valid,
        findings_hash_valid=findings_hash_valid, signature_present=signature_present,
        signature_valid=signature_valid, signer_trusted=signer_trusted,
        overall_status=overall_status, problems=problems,
    )
