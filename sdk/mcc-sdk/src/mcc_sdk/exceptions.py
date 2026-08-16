"""Exception hierarchy for ``mcc_sdk``.

Every failure mode is a distinct, typed exception. No transport failure,
timeout, malformed response, unknown verdict, or HTTP error is ever
represented as an ``ALLOW`` — the SDK fails closed on every path. A raw,
unvalidated dictionary is never returned to the caller after a validation
failure; either a fully-typed :class:`~mcc_sdk.models.EvaluateResponse` is
returned, or a typed exception is raised.

Exception messages never include the configured API key or any other
authorization header value.
"""

from __future__ import annotations

from typing import Any

__all__ = [
    "MCCAuthenticationError",
    "MCCConfigurationError",
    "MCCContractError",
    "MCCGatewayError",
    "MCCSDKError",
    "MCCTimeoutError",
    "MCCTransportError",
]


class MCCSDKError(Exception):
    """Base class for every error this SDK raises."""


class MCCConfigurationError(MCCSDKError):
    """The SDK was configured incorrectly (missing/invalid ``base_url``, a
    non-positive ``timeout``, etc.) — raised before any network call is made."""


class MCCTransportError(MCCSDKError):
    """A network/transport failure talking to the gateway (connection refused,
    DNS failure, TLS failure, or any other non-HTTP transport error). Never a
    permission to execute; never implies the request reached the gateway."""


class MCCTimeoutError(MCCTransportError):
    """The request to the gateway timed out. The outcome is unknown — the SDK
    never assumes success or failure of an operation it cannot confirm."""


class MCCGatewayError(MCCSDKError):
    """The gateway responded with an HTTP error status (4xx/5xx).

    Carries the safe diagnostic data needed to act on the failure without
    leaking secrets: the HTTP status code and, best-effort, the parsed
    response body's structured ``detail`` (e.g. FastAPI's HTTP 422 validation
    error array) or a short text snippet if the body was not JSON.
    """

    def __init__(
        self,
        message: str,
        *,
        status_code: int,
        detail: Any = None,
        body: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.detail = detail
        self.body = body


class MCCAuthenticationError(MCCGatewayError):
    """The gateway rejected the configured API key (HTTP 401/403)."""


class MCCContractError(MCCSDKError):
    """The gateway's response could not be trusted: malformed/non-JSON body,
    a response that does not match the documented ``/evaluate`` schema, a
    missing required field, or an unrecognized verdict. Always fail-closed —
    never a permission to execute, never coerced into a best-effort guess."""
