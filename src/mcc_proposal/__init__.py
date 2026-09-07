"""MCC Universal Proposal Service — Phase 1 (transport-neutral proposal/status).

    ANY AGENT / ANY FRAMEWORK / ANY TRANSPORT
                    |
                    v
            MCC PROPOSAL SERVICE          <-- this package; non-actuating
                    |
                    v
       INDEPENDENT AUTHORITY (future phase)
                    |
                    v
                  GATE
                    |
                    v
               EXECUTION

    PROPOSAL != PERMISSION.
    TRANSPORT != AUTHORITY.
    INTELLIGENCE != AUTHORITY != EXECUTION.

See ``docs/MCC_UNIVERSAL_PROPOSAL_SERVICE_PHASE1.md`` for the full contract.
"""

from __future__ import annotations

from .binding import BindingComputationError, compute_proposal_binding
from .models import (
    ALLOWED_REQUEST_FIELDS,
    AUTHORITY_BEARING_FIELDS,
    CONTRACT_VERSION,
    OperationStatusV1,
    OperationStatusValue,
    ProposalReceiptV1,
    ProposalRequestV1,
    ProposalStatus,
    ProposalValidationError,
)
from .registry import (
    InMemoryProposalRegistry,
    ProposalBackendUnavailable,
    ProposalConfigError,
    ProposalRecord,
    ProposalRegisterResult,
    ProposalRegisterStatus,
    RedisProposalRegistry,
    proposal_registry_from_env,
)
from .service import MCCProposalService
from .transport import (
    HttpProposalBackend,
    InProcessProposalBackend,
    ProposalBackend,
    ProposalBackendError,
)

__all__ = [
    "CONTRACT_VERSION",
    "ALLOWED_REQUEST_FIELDS",
    "AUTHORITY_BEARING_FIELDS",
    "ProposalValidationError",
    "ProposalRequestV1",
    "ProposalStatus",
    "ProposalReceiptV1",
    "OperationStatusValue",
    "OperationStatusV1",
    "BindingComputationError",
    "compute_proposal_binding",
    "ProposalRegisterStatus",
    "ProposalRegisterResult",
    "ProposalRecord",
    "ProposalBackendUnavailable",
    "ProposalConfigError",
    "InMemoryProposalRegistry",
    "RedisProposalRegistry",
    "proposal_registry_from_env",
    "MCCProposalService",
    "ProposalBackend",
    "ProposalBackendError",
    "HttpProposalBackend",
    "InProcessProposalBackend",
]
