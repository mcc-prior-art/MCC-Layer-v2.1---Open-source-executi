"""Internal, transport-agnostic plumbing shared by :class:`~mcc_sdk.client.MCCClient`
and :class:`~mcc_sdk.async_client.AsyncMCCClient`.

Not part of the public API (no leading-underscore-free re-export from
``mcc_sdk/__init__.py``). Kept as pure functions with no network/async
dependency of their own so the sync and async clients share exactly one
implementation of request-building and response-classification instead of
maintaining two copies that could silently drift apart.
"""

from __future__ import annotations

from typing import Any, NoReturn

import httpx
import pydantic

from .exceptions import (
    MCCAuthenticationError,
    MCCConfigurationError,
    MCCContractError,
    MCCGatewayError,
    MCCTimeoutError,
    MCCTransportError,
)
from .models import EvaluateRequest, EvaluateResponse

EVALUATE_PATH = "/evaluate"
API_KEY_HEADER = "X-API-Key"

#: Response bodies are truncated to this many characters in exception
#: diagnostics -- long enough to be useful, short enough to never dump a huge
#: unexpected payload (or a secret embedded in it by a misconfigured gateway)
#: into a log line.
_DIAGNOSTIC_BODY_LIMIT = 2000


def validate_base_url(base_url: str) -> str:
    if not base_url or not isinstance(base_url, str):
        raise MCCConfigurationError("base_url is required and must be a non-empty string")
    if not (base_url.startswith(("http://", "https://"))):
        raise MCCConfigurationError(f"base_url must start with http:// or https://: {base_url!r}")
    return base_url.rstrip("/")


def validate_timeout(timeout: float) -> float:
    if not isinstance(timeout, (int, float)) or isinstance(timeout, bool) or timeout <= 0:
        raise MCCConfigurationError(f"timeout must be a positive number of seconds: {timeout!r}")
    return float(timeout)


def build_headers(api_key: str | None) -> dict[str, str]:
    headers = {"content-type": "application/json"}
    if api_key:
        headers[API_KEY_HEADER] = api_key
    return headers


def build_evaluate_body(request: EvaluateRequest) -> dict[str, Any]:
    """Serialize a validated :class:`EvaluateRequest` to the exact JSON body
    the live Gateway accepts. Governance-sensitive values (identity, action,
    context, transaction_id, idempotency_key, actor_id, resource_id) are
    never regenerated or mutated here -- this is a pure field-for-field dump
    of what the caller supplied and Pydantic already validated."""
    return request.model_dump(mode="json", exclude_none=True)


def wrap_transport_exception(exc: Exception, *, method: str, path: str) -> NoReturn:
    """Translate an httpx-raised exception into the SDK's typed hierarchy.
    Never returns normally -- always raises."""
    if isinstance(exc, httpx.TimeoutException):
        raise MCCTimeoutError(f"{method} {path} timed out") from exc
    if isinstance(exc, httpx.HTTPError):
        raise MCCTransportError(f"{method} {path} transport error: {type(exc).__name__}") from exc
    raise MCCTransportError(
        f"{method} {path} unexpected transport failure: {type(exc).__name__}"
    ) from exc


def _safe_diagnostics(response: httpx.Response) -> tuple[Any, dict[str, Any] | None]:
    """Best-effort extraction of (detail, body) from an error response.
    Never raises -- a response that isn't JSON just yields a truncated text
    snippet as ``detail`` and ``body=None``."""
    try:
        body = response.json()
    except Exception:  # noqa: BLE001 -- diagnostics must never themselves fail
        text = response.text or ""
        return text[:_DIAGNOSTIC_BODY_LIMIT], None
    if isinstance(body, dict):
        return body.get("detail", body), body
    return body, None


def classify_response(response: httpx.Response) -> EvaluateResponse:
    """Turn a raw HTTP response from ``POST /evaluate`` into a validated
    :class:`EvaluateResponse`, or raise the matching typed exception.

    Fail-closed at every step: a non-200 status never returns a response
    object, a non-JSON or schema-mismatched 200 never returns a response
    object, and an unrecognized verdict never returns a response object.
    """
    status = response.status_code

    if status == 200:
        try:
            body = response.json()
        except Exception as exc:
            raise MCCContractError(
                f"gateway returned a non-JSON body for HTTP 200: {type(exc).__name__}"
            ) from exc
        if not isinstance(body, dict):
            raise MCCContractError("gateway response body is not a JSON object")
        try:
            return EvaluateResponse.model_validate(body)
        except pydantic.ValidationError as exc:
            raise MCCContractError(
                f"gateway response does not match the documented EvaluateResponse schema: {exc}"
            ) from exc

    if status in (401, 403):
        detail, body = _safe_diagnostics(response)
        raise MCCAuthenticationError(
            f"gateway rejected credentials (HTTP {status})",
            status_code=status,
            detail=detail,
            body=body,
        )

    detail, body = _safe_diagnostics(response)
    raise MCCGatewayError(
        f"gateway returned HTTP {status} for POST /evaluate",
        status_code=status,
        detail=detail,
        body=body,
    )


__all__ = [
    "API_KEY_HEADER",
    "EVALUATE_PATH",
    "build_evaluate_body",
    "build_headers",
    "classify_response",
    "validate_base_url",
    "validate_timeout",
    "wrap_transport_exception",
]
