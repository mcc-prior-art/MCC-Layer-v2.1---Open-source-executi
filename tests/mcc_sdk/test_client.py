"""MCCClient (synchronous): HTTP behavior, error classification, resource
handling. Uses httpx.MockTransport -- deterministic, no real network -- for
everything except the real-transport-failure tests, which target a genuinely
closed loopback port.
"""

from __future__ import annotations

import httpx
import pytest

from mcc_sdk import (
    EvaluateRequest,
    MCCAuthenticationError,
    MCCClient,
    MCCConfigurationError,
    MCCContractError,
    MCCGatewayError,
    MCCTimeoutError,
    MCCTransportError,
    Verdict,
)

_OK_BODY = {
    "decision": "ALLOW", "reason": "ok", "audit_id": "a1", "signature": "sig",
    "decision_token": {"sig": "sig"}, "constraints": {}, "forward_context": {"amount": 1},
    "applied_constraints": [], "enforce": True, "mode": "inline",
    "authority_required": "payments.send", "policy_ref": "p@h", "trace_id": "t1",
    "transaction_id": None, "idempotency_key": None, "actor_id": "agent/x", "resource_id": None,
}


def _client(handler, **kw) -> MCCClient:
    return MCCClient(base_url="http://gw.test", transport=httpx.MockTransport(handler), **kw)


def _req(**over) -> EvaluateRequest:
    kw = dict(identity="agent/x", action="send_payment", context={"amount": 1})
    kw.update(over)
    return EvaluateRequest(**kw)


# --------------------------------------------------------------------------
# Configuration
# --------------------------------------------------------------------------


def test_empty_base_url_rejected():
    with pytest.raises(MCCConfigurationError):
        MCCClient(base_url="")


def test_base_url_without_scheme_rejected():
    with pytest.raises(MCCConfigurationError):
        MCCClient(base_url="gw.test")


@pytest.mark.parametrize("bad_timeout", [0, -1, "5"])
def test_invalid_timeout_rejected(bad_timeout):
    with pytest.raises(MCCConfigurationError):
        MCCClient(base_url="http://gw.test", timeout=bad_timeout)


def test_trailing_slash_in_base_url_is_normalized():
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["path"] = request.url.path
        return httpx.Response(200, json=_OK_BODY)

    with MCCClient(base_url="http://gw.test/", transport=httpx.MockTransport(handler)) as client:
        client.evaluate(_req())
    assert seen["path"] == "/evaluate"


# --------------------------------------------------------------------------
# HTTP behavior
# --------------------------------------------------------------------------


def test_posts_to_evaluate_path_with_json_content_type():
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["method"] = request.method
        seen["path"] = request.url.path
        seen["content_type"] = request.headers.get("content-type")
        return httpx.Response(200, json=_OK_BODY)

    with _client(handler) as client:
        client.evaluate(_req())
    assert seen["method"] == "POST"
    assert seen["path"] == "/evaluate"
    assert seen["content_type"] == "application/json"


def test_api_key_header_applied_when_configured():
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["key"] = request.headers.get("x-api-key")
        return httpx.Response(200, json=_OK_BODY)

    with _client(handler, api_key="secret-key") as client:
        client.evaluate(_req())
    assert seen["key"] == "secret-key"


def test_no_api_key_header_when_not_configured():
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["has_key"] = "x-api-key" in request.headers
        return httpx.Response(200, json=_OK_BODY)

    with _client(handler) as client:
        client.evaluate(_req())
    assert seen["has_key"] is False


def test_api_key_never_appears_in_exception_message():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(401, json={"detail": "INVALID_API_KEY"})

    with _client(handler, api_key="super-secret-value") as client:
        with pytest.raises(MCCAuthenticationError) as exc_info:
            client.evaluate(_req())
        assert "super-secret-value" not in str(exc_info.value)
        assert "super-secret-value" not in repr(exc_info.value)


def test_configured_timeout_is_applied():
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=_OK_BODY)

    client = MCCClient(base_url="http://gw.test", timeout=3.5, transport=httpx.MockTransport(handler))
    try:
        assert client._timeout == 3.5
    finally:
        client.close()


def test_allow_parses_correctly_over_http():
    with _client(lambda r: httpx.Response(200, json=_OK_BODY)) as client:
        resp = client.evaluate(_req())
    assert resp.decision == Verdict.ALLOW
    assert resp.executable is True


def test_http_422_surfaced_as_structured_gateway_error():
    body = {"detail": [{"type": "missing", "loc": ["body", "action"], "msg": "Field required"}]}

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(422, json=body)

    with _client(handler) as client:
        with pytest.raises(MCCGatewayError) as exc_info:
            client.evaluate(_req())
        assert exc_info.value.status_code == 422
        assert exc_info.value.detail == body["detail"]


@pytest.mark.parametrize("status", [400, 403, 409, 500, 503])
def test_other_error_statuses_fail_closed_as_gateway_error(status):
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(status, json={"detail": f"error-{status}"})

    with _client(handler) as client:
        with pytest.raises(MCCGatewayError) as exc_info:
            client.evaluate(_req())
        assert exc_info.value.status_code == status


def test_401_raises_authentication_error_specifically():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(401, json={"detail": "INVALID_API_KEY"})

    with _client(handler) as client:
        with pytest.raises(MCCAuthenticationError):
            client.evaluate(_req())


def test_connection_failure_fails_closed():
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("connection refused", request=request)

    with _client(handler) as client:
        with pytest.raises(MCCTransportError):
            client.evaluate(_req())


def test_timeout_fails_closed():
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("timed out", request=request)

    with _client(handler) as client:
        with pytest.raises(MCCTimeoutError):
            client.evaluate(_req())


def test_real_closed_port_connection_failure(closed_port_url):
    """A genuine (non-mocked) transport failure -- nothing is listening on
    this port -- fails closed with a real network error, not a mock."""
    with MCCClient(base_url=closed_port_url, timeout=2.0) as client:
        with pytest.raises(MCCTransportError):
            client.evaluate(_req())


def test_malformed_json_body_fails_closed():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, content=b"not json at all {{{")

    with _client(handler) as client:
        with pytest.raises(MCCContractError):
            client.evaluate(_req())


def test_response_not_a_json_object_fails_closed():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=["a", "list", "not", "an", "object"])

    with _client(handler) as client:
        with pytest.raises(MCCContractError):
            client.evaluate(_req())


def test_incompatible_response_schema_fails_closed():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"totally": "different", "shape": True})

    with _client(handler) as client:
        with pytest.raises(MCCContractError):
            client.evaluate(_req())


def test_no_automatic_retry_by_default():
    calls = {"count": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        calls["count"] += 1
        raise httpx.ConnectError("connection refused", request=request)

    with _client(handler) as client:
        with pytest.raises(MCCTransportError):
            client.evaluate(_req())
    assert calls["count"] == 1, "the SDK must make exactly one attempt by default"


def test_no_automatic_retry_on_timeout():
    calls = {"count": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        calls["count"] += 1
        raise httpx.ReadTimeout("timed out", request=request)

    with _client(handler) as client:
        with pytest.raises(MCCTimeoutError):
            client.evaluate(_req())
    assert calls["count"] == 1


def test_no_automatic_retry_on_5xx():
    calls = {"count": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        calls["count"] += 1
        return httpx.Response(503, json={"detail": "unavailable"})

    with _client(handler) as client:
        with pytest.raises(MCCGatewayError):
            client.evaluate(_req())
    assert calls["count"] == 1


@pytest.mark.parametrize("status", [401, 422, 500])
def test_no_error_ever_surfaces_as_allow(status):
    """Every non-2xx path must raise, never return a response object (which
    could otherwise be inspected for a spuriously-ALLOW decision)."""
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(status, json={"detail": "x"})

    with _client(handler) as client:
        raised = False
        try:
            result = client.evaluate(_req())
        except Exception:
            raised = True
        else:
            pytest.fail(f"expected an exception for status {status}, got {result!r}")
        assert raised


def test_evaluate_requires_an_evaluate_request_instance():
    with _client(lambda r: httpx.Response(200, json=_OK_BODY)) as client:
        with pytest.raises(TypeError):
            client.evaluate({"identity": "agent/x", "action": "send_payment"})  # type: ignore[arg-type]


# --------------------------------------------------------------------------
# Resource handling
# --------------------------------------------------------------------------


def test_close_is_idempotent():
    client = MCCClient(base_url="http://gw.test", transport=httpx.MockTransport(lambda r: httpx.Response(200, json=_OK_BODY)))
    client.close()
    client.close()  # must not raise


def test_context_manager_closes_client():
    client = MCCClient(base_url="http://gw.test", transport=httpx.MockTransport(lambda r: httpx.Response(200, json=_OK_BODY)))
    with client as c:
        assert c is client
        assert client._closed is False
    assert client._closed is True


def test_client_usable_within_context_manager():
    with _client(lambda r: httpx.Response(200, json=_OK_BODY)) as client:
        resp = client.evaluate(_req())
        assert resp.decision == Verdict.ALLOW
