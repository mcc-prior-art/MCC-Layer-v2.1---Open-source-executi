"""Independent Attester Service (PR-4, MCC-AT-004).

Makes the Attester a REAL independent trust boundary: a separately
runnable service/process that owns the Attester's Ed25519 PRIVATE signing
key, so the model/agent proposing an action never possesses or controls
that key and cannot dictate the trusted claims the Attester signs.

    INTELLIGENCE / AGENT
            |  proposal / assessment input
            v
    INDEPENDENT ATTESTER SERVICE      <-- this package
            |  signed EvidenceAttestation (PR-1 / MCC-AT-001, unmodified)
            v
    PRE-EXECUTION CONTROL             <-- gateway.pre_execution_control (PR-2, unmodified)
            |  verified evidence_digest
            v
    SIGNED EXECUTION AUTHORITY        <-- mcc_core.core.DecisionEngine (PR-3, unmodified)
            |
            v
    EXECUTION GATE                    <-- mcc_core.gate.ExecutionGate (PR-3, unmodified)
            |
            v
    EXECUTION

This package is a deployment/trust-boundary extension, not a replacement
protocol: it reuses the existing PR-1 ``EvidenceAttestation`` schema,
canonicalization, Ed25519 signing semantics, and the existing
``mcc_attestation.attester.LocalAttester`` unchanged. It never issues MCC
decision tokens, mandates, approvals, or consensus authority, and never
calls ``ExecutionGate``/``EnforcementCoordinator`` -- attestation remains
evidence, not authority. See ``specs/MCC-AT-004.md``.
"""

from .app import AttestRequest, HealthResponse, build_attester_app
from .config import (
    DEFAULT_VALIDITY_SECONDS,
    MAX_VALIDITY_SECONDS,
    MIN_AUTH_SECRET_LENGTH,
    MIN_VALIDITY_SECONDS,
    AttesterServiceConfig,
    attester_service_config_from_env,
)
from .errors import (
    AssessmentProviderError,
    AttesterServiceConfigError,
    AttesterServiceError,
    BindingDerivationError,
)
from .provider import AssessmentProvider, AssessmentResult, DeterministicTestProvider
from .provider_loader import assessment_provider_from_env
from .service import AttesterService, SigningFailedError

__all__ = [
    "AttestRequest",
    "HealthResponse",
    "build_attester_app",
    "AttesterServiceConfig",
    "attester_service_config_from_env",
    "DEFAULT_VALIDITY_SECONDS",
    "MAX_VALIDITY_SECONDS",
    "MIN_VALIDITY_SECONDS",
    "MIN_AUTH_SECRET_LENGTH",
    "AttesterServiceError",
    "AttesterServiceConfigError",
    "AssessmentProviderError",
    "BindingDerivationError",
    "SigningFailedError",
    "AssessmentProvider",
    "AssessmentResult",
    "DeterministicTestProvider",
    "assessment_provider_from_env",
    "AttesterService",
]
