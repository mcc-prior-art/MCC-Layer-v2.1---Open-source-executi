"""Partner-safe evidence export for the attestation-aware full-chain
reference pilot (PR-6).

Deliberately separate from ``evidence.py::PilotEvidenceCollector`` (the
evaluate-only pilot's evidence collector) -- the fields differ enough
(attester identity, attestation identifier, evidence digest, per-boundary
invocation counts) that overloading one schema would blur what each pilot
mode actually proves. Neither collector imports the other.

Never records: private keys, bearer credentials (the Attester auth
secret, the Gateway API key), raw Decision Tokens, raw attestation claims
or provenance (which MAY carry partner-specific risk-assessment content),
or raw candidate-action payload content -- only the non-secret identifiers
and references listed in this module's ``AttestationChainEvidence`` fields.
See ``docs/PILOT_RUNBOOK.md`` §21 for the authoritative field-by-field
description of what is and is not included, and why.
"""

from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from .attestation_config import AttestationChainConfig

EVIDENCE_SCHEMA_VERSION = "1"

ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = ROOT / "pilot" / "schema" / "pilot_attestation_evidence.schema.json"

#: Fields a caller might plausibly try to smuggle into the evidence bundle
#: (raw claims/provenance can carry partner-specific risk content; secrets
#: must never be recorded at all). Checked defensively in
#: :func:`build_attestation_summary` -- never trust the caller not to pass
#: these by accident.
_NEVER_RECORD_KEYS = frozenset({
    "sig", "claims", "provenance", "auth_secret", "attester_auth_secret",
    "gateway_api_key", "api_key", "token", "decision_token", "private_key",
})


def _git_commit_sha(*, override: Optional[str] = None) -> str:
    if override:
        return override
    try:
        out = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True,
            timeout=5, check=True,
        )
        return out.stdout.strip()
    except Exception:  # noqa: BLE001 -- evidence generation must never crash on this
        return "unknown"


def build_attestation_summary(attestation: Dict[str, Any]) -> Dict[str, Any]:
    """Extract ONLY the non-secret identifying fields of a raw
    EvidenceAttestation for evidence purposes -- never the full document
    (which carries ``claims``/``provenance``, and the Ed25519 ``sig``).
    Also computes the digest ``PreExecutionControl`` would derive from this
    EXACT artifact, using the SAME shared primitive
    (``mcc_core.signing.hash_document`` -- see ``gateway/pre_execution_control.py``),
    labeled honestly as client-computed: the current ``/mandates/execute``
    API contract does not echo the server's own computed digest back to the
    caller (see this module's docstring / known limitations).

    Imports ``mcc_core`` lazily (only when this function actually runs) so
    that importing ``pilot.reference_python`` -- and running the legacy
    evaluate-only pilot, which never calls this function -- never requires
    ``mcc_core`` to be importable. Only the opt-in full-chain mode needs it
    on ``PYTHONPATH`` (see docs/PILOT_RUNBOOK.md §18's prerequisites)."""
    from mcc_core import hash_document

    return {
        "attester_id": attestation.get("attester_id"),
        "kid": attestation.get("kid"),
        "attestation_id": attestation.get("attestation_id"),
        "evidence_type": attestation.get("evidence_type"),
        "issued_at": attestation.get("issued_at"),
        "expires_at": attestation.get("expires_at"),
        "evidence_digest_client_computed": hash_document(attestation),
    }


@dataclass
class AttestationChainEvidence:
    """Accumulates one full-chain pilot submission's outcome, then exports
    a partner-safe evidence record. One instance per submission (unlike
    ``PilotEvidenceCollector``, which accumulates across a whole run) --
    ``finalize_and_export`` is normally called once per candidate action,
    since each carries its own attestation identity."""

    config: AttestationChainConfig
    mode: str  # "observe" | "enforced"
    action: str
    resource: Optional[str]
    attestation_summary: Dict[str, Any]
    gateway_decision: Optional[str] = None
    gateway_status: Optional[str] = None
    gateway_reason: Optional[str] = None
    audit_ref: Optional[str] = None
    execution_receipt_present: bool = False
    actuated: bool = False
    attester_service_calls: int = 1
    gateway_calls: int = 0
    commit_sha_override: Optional[str] = None
    run_correlation_id: str = field(
        default_factory=lambda: f"pilot-attestation-run-{datetime.now(timezone.utc).timestamp():.0f}"
    )

    _start_utc: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def _config_fingerprint(self) -> str:
        """A secret-free fingerprint of the attestation-chain config, mirroring
        ``PilotConfig.fingerprint()``'s exclusion convention -- both
        ``attester_auth_secret`` and ``gateway_api_key`` are dropped before
        hashing, and never appear in evidence output."""
        import hashlib

        d = asdict(self.config)
        d.pop("attester_auth_secret", None)
        d.pop("gateway_api_key", None)
        canonical = json.dumps(d, sort_keys=True, separators=(",", ":"))
        return "sha256:" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    def finalize(self) -> Dict[str, Any]:
        """Build the evidence dict (does not write to disk). Defensively
        strips any never-record key that might have leaked into
        ``attestation_summary`` (belt-and-braces on top of
        ``build_attestation_summary`` already never including them)."""
        end_utc = datetime.now(timezone.utc).isoformat()
        clean_attestation = {
            k: v for k, v in self.attestation_summary.items() if k not in _NEVER_RECORD_KEYS
        }

        status = "PASS"
        reason = "submission completed and produced a recognized outcome"
        if self.mode not in ("observe", "enforced"):
            status = "FAIL"
            reason = f"unrecognized mode: {self.mode!r}"
        elif self.mode == "enforced" and self.gateway_status is None:
            status = "FAIL"
            reason = "enforced mode completed with no recorded gateway execution outcome"

        known_limitations = [
            "decision_token_fingerprint is not included: the current "
            "POST /mandates/execute response contract (gateway/governance_api.py"
            "::ExecuteResponse) does not echo any reference to the signed Decision "
            "Token back to the caller, by design (the token is an internal "
            "artifact the Execution Gate consumes; it is not re-exposed after "
            "actuation). This PR does not add one, to avoid modifying a core "
            "gateway response contract for pilot convenience.",
            "policy_hash is not included: it is not independently obtainable "
            "from the POST /mandates/execute response in the current API "
            "contract (only POST /evaluate's legacy response exposes policy_ref).",
            "evidence_digest_client_computed is computed by this pilot from the "
            "exact attestation document it obtained, using the same shared "
            "mcc_core.signing.hash_document primitive PreExecutionControl uses "
            "server-side -- it is not read back from the server's own computation.",
        ]

        return {
            "schema_version": EVIDENCE_SCHEMA_VERSION,
            "mcc_commit_sha": _git_commit_sha(override=self.commit_sha_override),
            "run_correlation_id": self.run_correlation_id,
            "start_time_utc": self._start_utc,
            "end_time_utc": end_utc,
            "config_fingerprint": self._config_fingerprint(),
            "mode": self.mode,
            "action": self.action,
            "resource": self.resource,
            "attestation": clean_attestation,
            "gateway_decision": self.gateway_decision,
            "gateway_status": self.gateway_status,
            "gateway_reason": self.gateway_reason,
            "audit_ref": self.audit_ref,
            "execution_receipt_present": self.execution_receipt_present,
            "actuated": self.actuated,
            "independent_invocations": {
                "attester_service_calls": self.attester_service_calls,
                "gateway_calls": self.gateway_calls,
            },
            "status": status,
            "status_reason": reason,
            "known_limitations": known_limitations,
        }

    def finalize_and_export(self, evidence_dir: str, *, filename: Optional[str] = None) -> Path:
        evidence = self.finalize()
        out_dir = Path(evidence_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        name = filename or f"pilot-attestation-evidence-{self.run_correlation_id}.json"
        out_path = out_dir / name
        if out_path.exists():
            raise FileExistsError(
                f"refusing to silently overwrite existing evidence file: {out_path}"
            )
        out_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return out_path


def validate_attestation_evidence(evidence: Dict[str, Any]) -> None:
    """Validate an evidence dict against
    ``pilot/schema/pilot_attestation_evidence.schema.json``. Raises
    ``jsonschema.ValidationError``/``SchemaError`` on failure."""
    import jsonschema

    with SCHEMA_PATH.open(encoding="utf-8") as f:
        schema = json.load(f)
    jsonschema.validate(instance=evidence, schema=schema)


__all__ = [
    "EVIDENCE_SCHEMA_VERSION",
    "SCHEMA_PATH",
    "AttestationChainEvidence",
    "build_attestation_summary",
    "validate_attestation_evidence",
]

if __name__ == "__main__":  # pragma: no cover -- manual invocation only
    sys.exit("this module is a library; see pilot/reference_python/attestation_runner.py")
