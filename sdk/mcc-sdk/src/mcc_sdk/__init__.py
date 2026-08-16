"""``mcc_sdk`` — the official Python SDK for MCC-Core's public Gateway API.

A thin, typed, framework-neutral client over the existing
``POST /evaluate`` boundary documented in
``docs/integration/GATEWAY_API_CONTRACT.md`` and
``openapi/mcc-gateway.yaml``:

    Agent / application -> MCCClient / AsyncMCCClient -> MCC Gateway
        -> Governance Decision (ALLOW / DENY / ESCALATE / CONSTRAIN)

The model proposes. MCC decides. The gate enforces. The audit chain records.

This package is a transport, not a decision authority: it makes no local
governance decisions, holds no signing key, verifies no signatures, and has
no execution path of any kind. A proposal is never permission — see the
"Security boundary" section of this package's README for the full statement.
"""

from __future__ import annotations

from .async_client import AsyncMCCClient
from .client import MCCClient
from .exceptions import (
    MCCAuthenticationError,
    MCCConfigurationError,
    MCCContractError,
    MCCGatewayError,
    MCCSDKError,
    MCCTimeoutError,
    MCCTransportError,
)
from .models import EvaluateRequest, EvaluateResponse, Verdict

__version__ = "0.1.0"

__all__ = [
    "AsyncMCCClient",
    # models
    "EvaluateRequest",
    "EvaluateResponse",
    "MCCAuthenticationError",
    "MCCClient",
    "MCCConfigurationError",
    "MCCContractError",
    "MCCGatewayError",
    # exceptions
    "MCCSDKError",
    "MCCTimeoutError",
    "MCCTransportError",
    "Verdict",
    "__version__",
]
