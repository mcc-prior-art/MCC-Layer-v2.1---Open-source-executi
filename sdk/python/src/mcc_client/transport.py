"""HTTP transport for the MCC-Core client SDK.

Thin, typed wrapper over ``httpx``. It performs no governance — it only carries
requests to the gateway and translates transport outcomes into typed errors.

Retries are permitted ONLY for clearly safe, side-effect-free, pre-execution
requests (GET, and evaluate). Governed execution is never retried here: an
uncertain execution outcome is surfaced (by the client) as an ambiguous-execution
error, never as a silent retry.
"""

from __future__ import annotations

import time
import uuid
from typing import Any, Dict, Optional

import httpx

from .exceptions import (
    MCCAuthenticationError,
    MCCProtocolError,
    MCCTimeoutError,
    MCCTransportError,
)

CORRELATION_HEADER = "X-MCC-Correlation-Id"


class Transport:
    """Synchronous transport to a running MCC-Core gateway."""

    def __init__(
        self,
        base_url: str,
        *,
        api_key: Optional[str] = None,
        operator_key: Optional[str] = None,
        timeout: float = 10.0,
        max_safe_retries: int = 2,
        client: Optional[httpx.Client] = None,
    ) -> None:
        if not base_url:
            raise ValueError("base_url is required")
        self.base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._operator_key = operator_key
        self._timeout = timeout
        self._max_safe_retries = max(0, int(max_safe_retries))
        self._owns_client = client is None
        self._client = client or httpx.Client(timeout=timeout)

    # -- lifecycle --

    def close(self) -> None:
        if self._owns_client:
            self._client.close()

    def __enter__(self) -> "Transport":
        return self

    def __exit__(self, *exc: Any) -> None:
        self.close()

    # -- headers --

    def _headers(self, *, operator: bool, correlation_id: str) -> Dict[str, str]:
        headers = {"content-type": "application/json", CORRELATION_HEADER: correlation_id}
        if self._api_key:
            headers["x-api-key"] = self._api_key
        if operator:
            if not self._operator_key:
                raise MCCAuthenticationError(
                    "operator action requires an operator key; none configured")
            headers["x-operator-key"] = self._operator_key
        return headers

    @staticmethod
    def new_correlation_id() -> str:
        return f"corr-{uuid.uuid4().hex}"

    # -- requests --

    def post(self, path: str, body: Dict[str, Any], *, operator: bool = False,
             correlation_id: Optional[str] = None, retry_safe: bool = False) -> Dict[str, Any]:
        cid = correlation_id or self.new_correlation_id()
        headers = self._headers(operator=operator, correlation_id=cid)
        return self._json(self._send("POST", path, headers, json=body, retry_safe=retry_safe), cid)

    def get(self, path: str, *, params: Optional[Dict[str, Any]] = None,
            operator: bool = False, correlation_id: Optional[str] = None,
            text: bool = False) -> Any:
        cid = correlation_id or self.new_correlation_id()
        headers = self._headers(operator=operator, correlation_id=cid)
        resp = self._send("GET", path, headers, params=params, retry_safe=True)
        if text:
            return resp.text
        return self._json(resp, cid)

    # -- internals --

    def _send(self, method: str, path: str, headers: Dict[str, str], *,
              json: Optional[Dict[str, Any]] = None, params: Optional[Dict[str, Any]] = None,
              retry_safe: bool = False) -> httpx.Response:
        url = f"{self.base_url}{path}"
        attempts = self._max_safe_retries + 1 if retry_safe else 1
        last_exc: Optional[Exception] = None
        for i in range(attempts):
            try:
                resp = self._client.request(method, url, headers=headers, json=json,
                                            params=params, timeout=self._timeout)
            except httpx.TimeoutException:
                # Only side-effect-free requests may retry a timeout.
                last_exc = MCCTimeoutError(f"{method} {path} timed out")
            except httpx.HTTPError as exc:
                last_exc = MCCTransportError(f"{method} {path} transport error: {type(exc).__name__}")
            else:
                if resp.status_code in (401, 403):
                    raise MCCAuthenticationError(f"gateway rejected credentials (HTTP {resp.status_code})")
                return resp
            if i < attempts - 1:
                time.sleep(0.1 * (2 ** i))
        assert last_exc is not None
        raise last_exc

    @staticmethod
    def _json(resp: httpx.Response, correlation_id: str) -> Dict[str, Any]:
        try:
            data = resp.json()
        except Exception as exc:  # noqa: BLE001 — any decode failure is fail-closed
            raise MCCProtocolError(
                f"gateway returned a non-JSON / malformed body (HTTP {resp.status_code})") from exc
        if not isinstance(data, dict):
            raise MCCProtocolError("gateway response is not a JSON object")
        data.setdefault("_correlation_id", correlation_id)
        return data


__all__ = ["Transport", "CORRELATION_HEADER"]
