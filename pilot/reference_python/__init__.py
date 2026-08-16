"""Reference pilot integration (PR #82): candidate action -> the official
``mcc_sdk`` -> Gateway ``/evaluate`` -> decision validation -> execution
gate -> a local, simulated actuator only.

This package prepares MCC-Core for a real external pilot; it does not
itself constitute, claim, or simulate a completed pilot. See
``docs/PILOT_RUNBOOK.md`` and ``docs/PILOT_ACCEPTANCE_CHECKLIST.md``.

No production actuator exists here. No governance logic is duplicated --
every verdict comes from the real Gateway through the real official SDK.
"""

from __future__ import annotations

from .actuator import DirectActuationRejected, SimulatedActuator, SimulatedReceipt
from .config import Mode, PilotConfig, PilotConfigError
from .evidence import PilotEvidenceCollector, validate_evidence
from .integration import PilotIntegration, PilotOutcome

__all__ = [
    "DirectActuationRejected",
    "Mode",
    "PilotConfig",
    "PilotConfigError",
    "PilotEvidenceCollector",
    "PilotIntegration",
    "PilotOutcome",
    "SimulatedActuator",
    "SimulatedReceipt",
    "validate_evidence",
]
