"""Reference pilot integration: two opt-in modes over the real MCC-Core
Gateway, never a mock.

**Legacy evaluate-only mode** (PR #82, the default): candidate action ->
the official ``mcc_sdk`` -> Gateway ``POST /evaluate`` -> decision
validation -> pilot-side mode gate -> a local, simulated actuator only.
This path issues a signed decision token but does not itself route through
the Execution Gate / EnforcementCoordinator -- see
:mod:`pilot.reference_python.integration` and
``docs/PILOT_RUNBOOK.md`` §3 for exactly what it does and does not exercise.

**Attestation-aware full-chain mode** (PR-6, opt-in): candidate action ->
a separate Independent Attester Service -> a signed EvidenceAttestation ->
Gateway ``POST /mandates/execute`` -> the real, unmodified PreExecutionControl
-> evidence-bound Decision Token -> ExecutionGate -> a governed
(loopback/simulated) actuator. See
:mod:`pilot.reference_python.attestation_integration` and
``docs/PILOT_RUNBOOK.md`` §18-24.

Neither mode constitutes, claims, or simulates a completed external pilot.
See ``docs/PILOT_RUNBOOK.md`` and ``docs/PILOT_ACCEPTANCE_CHECKLIST.md``.

No production actuator exists in either mode. No governance logic is
duplicated -- every verdict comes from the real Gateway (and, in full-chain
mode, the real Attester) through their real, unmodified HTTP surfaces.
"""

from __future__ import annotations

from .actuator import DirectActuationRejected, SimulatedActuator, SimulatedReceipt
from .attestation_config import AttestationChainConfig, AttestationChainConfigError
from .attestation_evidence import AttestationChainEvidence, validate_attestation_evidence
from .attestation_integration import AttestationChainOutcome, AttestationChainPilot
from .attester_client import AttesterClient, AttesterClientError
from .config import Mode, PilotConfig, PilotConfigError
from .evidence import PilotEvidenceCollector, validate_evidence
from .integration import PilotIntegration, PilotOutcome

__all__ = [
    "AttestationChainConfig",
    "AttestationChainConfigError",
    "AttestationChainEvidence",
    "AttestationChainOutcome",
    "AttestationChainPilot",
    "AttesterClient",
    "AttesterClientError",
    "DirectActuationRejected",
    "Mode",
    "PilotConfig",
    "PilotConfigError",
    "PilotEvidenceCollector",
    "PilotIntegration",
    "PilotOutcome",
    "SimulatedActuator",
    "SimulatedReceipt",
    "validate_attestation_evidence",
    "validate_evidence",
]
