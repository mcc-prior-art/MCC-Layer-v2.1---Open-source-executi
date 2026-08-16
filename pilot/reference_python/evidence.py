"""Deterministic, machine-readable pilot evidence export.

Collects what actually happened during one pilot run (verdict counts,
failure-mode counts, correlation references, final mode, pass/fail) and
writes it as JSON validated against
``pilot/schema/pilot_evidence.schema.json``. Never writes to a TRACKED
repository path -- the caller supplies ``evidence_dir`` (default
``artifacts/pilot-evidence/``, already git-ignored; tests always pass a
pytest ``tmp_path``).

This module makes no governance decision and holds no signing key -- it
only records outcomes the Gateway and this pilot's own code already
produced.
"""

from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import PilotConfig

EVIDENCE_SCHEMA_VERSION = "1"

ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = ROOT / "pilot" / "schema" / "pilot_evidence.schema.json"


def _git_commit_sha(*, override: str | None = None) -> str:
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


def _sdk_version() -> str:
    try:
        import mcc_sdk

        return mcc_sdk.__version__
    except Exception:  # noqa: BLE001
        return "unknown"


@dataclass
class CorrelationRef:
    action: str
    decision: str
    audit_id: str
    trace_id: str


@dataclass
class PilotEvidenceCollector:
    """Accumulates outcomes during a pilot run; call :meth:`record` after
    every evaluated action, then :meth:`finalize_and_export` once at the
    end."""

    config: PilotConfig
    commit_sha_override: str | None = None

    _start_utc: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    _allow: int = 0
    _deny: int = 0
    _escalate: int = 0
    _constrain: int = 0
    _malformed: int = 0
    _timeout: int = 0
    _unavailable: int = 0
    _attempted_bypass: int = 0
    _executed: int = 0
    _correlation_refs: list[CorrelationRef] = field(default_factory=list)

    @property
    def total_evaluated(self) -> int:
        return self._allow + self._deny + self._escalate + self._constrain

    def record_decision(self, *, action: str, decision: str, audit_id: str, trace_id: str) -> None:
        counters = {
            "ALLOW": "_allow", "DENY": "_deny",
            "ESCALATE": "_escalate", "CONSTRAIN": "_constrain",
        }
        attr = counters.get(decision)
        if attr is None:
            raise ValueError(f"unknown decision, refusing to record: {decision!r}")
        setattr(self, attr, getattr(self, attr) + 1)
        self._correlation_refs.append(
            CorrelationRef(action=action, decision=decision, audit_id=audit_id, trace_id=trace_id)
        )

    def record_malformed(self) -> None:
        self._malformed += 1

    def record_timeout(self) -> None:
        self._timeout += 1

    def record_unavailable(self) -> None:
        self._unavailable += 1

    def record_attempted_bypass(self) -> None:
        self._attempted_bypass += 1

    def record_executed(self) -> None:
        self._executed += 1

    def finalize(self) -> dict[str, Any]:
        """Build the evidence dict (does not write to disk)."""
        end_utc = datetime.now(timezone.utc).isoformat()

        status = "PASS"
        reason = "run completed; all evaluated actions produced a recognized verdict"
        if self._malformed or self._unavailable:
            status = "FAIL"
            reason = (
                f"run encountered {self._malformed} malformed response(s) and "
                f"{self._unavailable} gateway-unavailable event(s)"
            )
        elif self._attempted_bypass:
            status = "FAIL"
            reason = f"{self._attempted_bypass} direct-actuation bypass attempt(s) were made"
        elif self.total_evaluated == 0:
            status = "FAIL"
            reason = "no actions were evaluated during this run"

        return {
            "schema_version": EVIDENCE_SCHEMA_VERSION,
            "mcc_commit_sha": _git_commit_sha(override=self.commit_sha_override),
            "sdk_version": _sdk_version(),
            "pilot_id": self.config.pilot_id,
            "integration_id": self.config.integration_id,
            "run_correlation_id": self.config.run_correlation_id,
            "start_time_utc": self._start_utc,
            "end_time_utc": end_utc,
            "config_fingerprint": self.config.fingerprint(),
            "total_evaluated": self.total_evaluated,
            "allow_count": self._allow,
            "deny_count": self._deny,
            "escalate_count": self._escalate,
            "constrain_count": self._constrain,
            "malformed_count": self._malformed,
            "timeout_count": self._timeout,
            "unavailable_count": self._unavailable,
            "attempted_bypass_count": self._attempted_bypass,
            "executed_count": self._executed,
            "correlation_refs": [
                {
                    "action": r.action, "decision": r.decision,
                    "audit_id": r.audit_id, "trace_id": r.trace_id,
                }
                for r in self._correlation_refs
            ],
            "final_mode": self.config.mode,
            "status": status,
            "status_reason": reason,
        }

    def finalize_and_export(self, *, filename: str | None = None) -> Path:
        """Write the evidence bundle to ``config.evidence_dir`` and return
        the written path. Never overwrites an earlier run's evidence
        silently -- the filename embeds ``run_correlation_id``."""
        evidence = self.finalize()
        out_dir = Path(self.config.evidence_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        name = filename or f"pilot-evidence-{self.config.run_correlation_id}.json"
        out_path = out_dir / name
        if out_path.exists():
            raise FileExistsError(
                f"refusing to silently overwrite existing evidence file: {out_path}"
            )
        out_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return out_path


def validate_evidence(evidence: dict[str, Any]) -> None:
    """Validate an evidence dict against ``pilot/schema/pilot_evidence.schema.json``.
    Raises ``jsonschema.ValidationError`` (or ``jsonschema.SchemaError``) on
    failure."""
    import jsonschema

    with SCHEMA_PATH.open(encoding="utf-8") as f:
        schema = json.load(f)
    jsonschema.validate(instance=evidence, schema=schema)


__all__ = [
    "EVIDENCE_SCHEMA_VERSION",
    "SCHEMA_PATH",
    "CorrelationRef",
    "PilotEvidenceCollector",
    "validate_evidence",
]

if __name__ == "__main__":  # pragma: no cover -- manual invocation only
    sys.exit("this module is a library; see pilot/reference_python/runner.py")
