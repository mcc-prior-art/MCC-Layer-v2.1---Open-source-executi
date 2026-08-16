"""The asynchronous MCC-Core client: :class:`AsyncMCCClient`.

Mirrors :class:`mcc_sdk.client.MCCClient` exactly (same configuration, same
fail-closed classification via :mod:`mcc_sdk._shared`, same no-retry-by-default
policy) using ``httpx.AsyncClient`` instead of ``httpx.Client``. The
repository's supported dependency baseline (``httpx>=0.27``, already a base
runtime dependency of this monorepo) ships async support out of the box, so
there is no reason to omit it.
"""

from __future__ import annotations

import httpx

from ._shared import (
    EVALUATE_PATH,
    build_evaluate_body,
    build_headers,
    classify_response,
    validate_base_url,
    validate_timeout,
    wrap_transport_exception,
)
from .models import EvaluateRequest, EvaluateResponse

__all__ = ["AsyncMCCClient"]


class AsyncMCCClient:
    """The asynchronous counterpart to :class:`~mcc_sdk.client.MCCClient`.

    Example::

        async with AsyncMCCClient(base_url="http://localhost:8001", timeout=5.0) as client:
            result = await client.evaluate(EvaluateRequest(identity="agent/x", action="send_payment"))
    """

    def __init__(
        self,
        base_url: str,
        *,
        timeout: float = 10.0,
        api_key: str | None = None,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        """See :class:`mcc_sdk.client.MCCClient` for argument documentation
        (identical configuration surface)."""
        self._base_url = validate_base_url(base_url)
        self._timeout = validate_timeout(timeout)
        self._api_key = api_key
        self._client = httpx.AsyncClient(timeout=self._timeout, transport=transport)
        self._closed = False

    async def evaluate(self, request: EvaluateRequest) -> EvaluateResponse:
        """Submit a proposed action to ``POST /evaluate`` and return the
        typed governance verdict. Never retries."""
        if not isinstance(request, EvaluateRequest):
            raise TypeError(
                f"evaluate() requires an EvaluateRequest instance, got {type(request).__name__}"
            )
        body = build_evaluate_body(request)
        headers = build_headers(self._api_key)
        url = f"{self._base_url}{EVALUATE_PATH}"
        try:
            response = await self._client.post(
                url, json=body, headers=headers, timeout=self._timeout
            )
        except Exception as exc:  # noqa: BLE001 -- classified by wrap_transport_exception
            wrap_transport_exception(exc, method="POST", path=EVALUATE_PATH)
        return classify_response(response)

    # -- resource lifecycle --

    async def aclose(self) -> None:
        """Close the owned HTTP client. Safe to call more than once."""
        if not self._closed:
            await self._client.aclose()
            self._closed = True

    async def __aenter__(self) -> AsyncMCCClient:  # noqa: PYI034 -- avoid a typing_extensions dep for py3.9
        return self

    async def __aexit__(self, *exc_info: object) -> None:
        await self.aclose()
