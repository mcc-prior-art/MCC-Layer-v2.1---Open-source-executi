"""The synchronous MCC-Core client: :class:`MCCClient`."""

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

__all__ = ["MCCClient"]


class MCCClient:
    """A thin, typed, synchronous client over the MCC-Core Gateway's public
    ``POST /evaluate`` boundary.

    The model or application proposes an action by constructing an
    :class:`~mcc_sdk.models.EvaluateRequest` and calling :meth:`evaluate`.
    MCC-Core remains the decision authority; the Execution Gate remains the
    enforcement authority. This client has no execution path, no local
    policy evaluation, and no signature verification of its own — see
    the SDK README's security-boundary section.

    No automatic retries are performed. A single ``POST /evaluate`` call
    makes exactly one HTTP attempt; a transport failure, timeout, or
    ambiguous outcome is always surfaced as a typed exception, never
    silently retried (retrying could interact incorrectly with the
    Gateway's nonce/idempotency/audit semantics).

    Example::

        with MCCClient(base_url="http://localhost:8001", timeout=5.0, api_key="demo-key") as client:
            result = client.evaluate(EvaluateRequest(identity="agent/x", action="send_payment"))
            if result.decision == Verdict.ALLOW:
                ...
    """

    def __init__(
        self,
        base_url: str,
        *,
        timeout: float = 10.0,
        api_key: str | None = None,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        """
        Args:
            base_url: The MCC Gateway's base URL, e.g. ``http://localhost:8001``.
            timeout: Request timeout in seconds, applied to connect/read/write/pool.
            api_key: Sent as ``X-API-Key`` if the deployment requires it (the
                live Gateway's agent authentication boundary).
            transport: An optional ``httpx.BaseTransport`` (e.g.
                ``httpx.MockTransport``) for hermetic testing without a real
                network call. Not for production use.
        """
        self._base_url = validate_base_url(base_url)
        self._timeout = validate_timeout(timeout)
        self._api_key = api_key
        self._client = httpx.Client(timeout=self._timeout, transport=transport)
        self._closed = False

    def evaluate(self, request: EvaluateRequest) -> EvaluateResponse:
        """Submit a proposed action to ``POST /evaluate`` and return the
        typed governance verdict. Side-effect-free on the Gateway side: it
        never executes anything, and this method never retries."""
        if not isinstance(request, EvaluateRequest):
            raise TypeError(
                f"evaluate() requires an EvaluateRequest instance, got {type(request).__name__}"
            )
        body = build_evaluate_body(request)
        headers = build_headers(self._api_key)
        url = f"{self._base_url}{EVALUATE_PATH}"
        try:
            response = self._client.post(url, json=body, headers=headers, timeout=self._timeout)
        except Exception as exc:  # noqa: BLE001 -- classified by wrap_transport_exception
            wrap_transport_exception(exc, method="POST", path=EVALUATE_PATH)
        return classify_response(response)

    # -- resource lifecycle --

    def close(self) -> None:
        """Close the owned HTTP client. Safe to call more than once."""
        if not self._closed:
            self._client.close()
            self._closed = True

    def __enter__(self) -> MCCClient:  # noqa: PYI034 -- avoid a typing_extensions dep for py3.9
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.close()

    def __del__(self) -> None:  # best-effort; never raises during interpreter teardown
        try:
            self.close()
        except Exception:  # noqa: BLE001, S110 -- __del__ must never raise
            pass
