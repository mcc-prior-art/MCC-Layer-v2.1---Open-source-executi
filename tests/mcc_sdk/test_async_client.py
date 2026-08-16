"""AsyncMCCClient: HTTP behavior, error classification, resource handling.

Mirrors test_client.py for the async client. Uses asyncio.run() directly
(matching the repo's existing convention -- see tests/test_gateway.py's
``run = asyncio.run`` -- no pytest-asyncio dependency needed for this small,
isolated async surface).
"""

from __future__ import annotations

import asyncio

import httpx
import pytest

from mcc_sdk import (
    AsyncMCCClient,
    EvaluateRequest,
    MCCAuthenticationError,
    MCCContractError,
    MCCGatewayError,
    MCCTimeoutError,
    MCCTransportError,
    Verdict,
)

_OK_BODY = {
    "decision": "CONSTRAIN", "reason": "clamped", "audit_id": "a2", "signature": "sig",
    "decision_token": {"sig": "sig"}, "constraints": {"max_amount": 5000},
    "forward_context": {"amount": 5000}, "applied_constraints": ["amount: 99999 -> 5000 (max)"],
    "enforce": True, "mode": "inline", "authority_required": "payments.send",
    "policy_ref": "p@h", "trace_id": "t2", "transaction_id": None,
    "idempotency_key": None, "actor_id": "agent/x", "resource_id": None,
}


def _req(**over) -> EvaluateRequest:
    kw = dict(identity="agent/x", action="send_payment", context={"amount": 99999})
    kw.update(over)
    return EvaluateRequest(**kw)


def run(coro):
    return asyncio.run(coro)


def test_async_allow_parses_correctly():
    async def go():
        transport = httpx.MockTransport(lambda r: httpx.Response(200, json=_OK_BODY))
        async with AsyncMCCClient(base_url="http://gw.test", transport=transport) as client:
            return await client.evaluate(_req())

    resp = run(go())
    assert resp.decision == Verdict.CONSTRAIN
    assert resp.constrained is True


def test_async_api_key_header_applied():
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["key"] = request.headers.get("x-api-key")
        return httpx.Response(200, json=_OK_BODY)

    async def go():
        transport = httpx.MockTransport(handler)
        async with AsyncMCCClient(base_url="http://gw.test", api_key="secret", transport=transport) as client:
            await client.evaluate(_req())

    run(go())
    assert seen["key"] == "secret"


def test_async_http_422_surfaced_as_structured_gateway_error():
    body = {"detail": [{"type": "missing", "loc": ["body", "action"], "msg": "Field required"}]}

    async def go():
        transport = httpx.MockTransport(lambda r: httpx.Response(422, json=body))
        async with AsyncMCCClient(base_url="http://gw.test", transport=transport) as client:
            await client.evaluate(_req())

    with pytest.raises(MCCGatewayError) as exc_info:
        run(go())
    assert exc_info.value.status_code == 422
    assert exc_info.value.detail == body["detail"]


def test_async_401_raises_authentication_error():
    async def go():
        transport = httpx.MockTransport(lambda r: httpx.Response(401, json={"detail": "INVALID_API_KEY"}))
        async with AsyncMCCClient(base_url="http://gw.test", transport=transport) as client:
            await client.evaluate(_req())

    with pytest.raises(MCCAuthenticationError):
        run(go())


def test_async_connection_failure_fails_closed():
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("connection refused", request=request)

    async def go():
        transport = httpx.MockTransport(handler)
        async with AsyncMCCClient(base_url="http://gw.test", transport=transport) as client:
            await client.evaluate(_req())

    with pytest.raises(MCCTransportError):
        run(go())


def test_async_timeout_fails_closed():
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("timed out", request=request)

    async def go():
        transport = httpx.MockTransport(handler)
        async with AsyncMCCClient(base_url="http://gw.test", transport=transport) as client:
            await client.evaluate(_req())

    with pytest.raises(MCCTimeoutError):
        run(go())


def test_async_malformed_json_fails_closed():
    async def go():
        transport = httpx.MockTransport(lambda r: httpx.Response(200, content=b"{{{not json"))
        async with AsyncMCCClient(base_url="http://gw.test", transport=transport) as client:
            await client.evaluate(_req())

    with pytest.raises(MCCContractError):
        run(go())


def test_async_no_automatic_retry_by_default():
    calls = {"count": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        calls["count"] += 1
        raise httpx.ConnectError("connection refused", request=request)

    async def go():
        transport = httpx.MockTransport(handler)
        async with AsyncMCCClient(base_url="http://gw.test", transport=transport) as client:
            await client.evaluate(_req())

    with pytest.raises(MCCTransportError):
        run(go())
    assert calls["count"] == 1


def test_async_real_closed_port_connection_failure(closed_port_url):
    async def go():
        async with AsyncMCCClient(base_url=closed_port_url, timeout=2.0) as client:
            await client.evaluate(_req())

    with pytest.raises(MCCTransportError):
        run(go())


# -- resource handling --


def test_async_aclose_is_idempotent():
    async def go():
        transport = httpx.MockTransport(lambda r: httpx.Response(200, json=_OK_BODY))
        client = AsyncMCCClient(base_url="http://gw.test", transport=transport)
        await client.aclose()
        await client.aclose()  # must not raise

    run(go())


def test_async_context_manager_closes_client():
    async def go():
        transport = httpx.MockTransport(lambda r: httpx.Response(200, json=_OK_BODY))
        client = AsyncMCCClient(base_url="http://gw.test", transport=transport)
        async with client as c:
            assert c is client
            assert client._closed is False
        assert client._closed is True

    run(go())


def test_async_evaluate_requires_an_evaluate_request_instance():
    async def go():
        transport = httpx.MockTransport(lambda r: httpx.Response(200, json=_OK_BODY))
        async with AsyncMCCClient(base_url="http://gw.test", transport=transport) as client:
            await client.evaluate({"identity": "agent/x", "action": "send_payment"})  # type: ignore[arg-type]

    with pytest.raises(TypeError):
        run(go())
