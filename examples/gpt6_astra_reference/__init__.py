"""GPT-6 Astra Reference Integration.

A thin reference integration demonstrating a frontier Intelligence
provider (GPT-6 Astra, or any OpenAI-compatible model) in front of the
existing, unmodified MCC-Core execution-authority chain:

    INTELLIGENCE (Astra) -> ATTESTATION -> CONTROL -> SIGNED EXECUTION
    AUTHORITY -> AUTHORITY VERIFICATION -> GATE -> EXECUTION

Astra proposes; it never possesses an MCC signing key, an Attester
signing key, or the ability to call the real actuator directly, and it
cannot decide that its own proposal is authorized. See
``docs/GPT6_ASTRA_REFERENCE_INTEGRATION.md``.
"""

from .models import AstraError, AstraProposal, AstraProposalError, AstraSelfRefusal

__all__ = ["AstraProposal", "AstraSelfRefusal", "AstraError", "AstraProposalError"]
