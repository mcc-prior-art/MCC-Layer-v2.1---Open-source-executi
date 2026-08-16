"""Request/response handling: EvaluateRequest / EvaluateResponse / Verdict.

Offline, no network. Proves serialization matches the Gateway contract,
required fields are enforced, unknown fields are rejected locally, and
response parsing fails closed on every malformed shape.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from mcc_sdk import EvaluateRequest, EvaluateResponse, Verdict

# --------------------------------------------------------------------------
# Request handling
# --------------------------------------------------------------------------


def test_valid_minimal_request():
    req = EvaluateRequest(identity="agent/x", action="send_payment")
    assert req.identity == "agent/x"
    assert req.action == "send_payment"
    assert req.context == {}
    assert req.transaction_id is None


def test_valid_complete_request():
    req = EvaluateRequest(
        identity="agent/payments-bot",
        action="send_payment",
        context={"amount": 1000, "currency": "USD"},
        transaction_id="txn-1",
        idempotency_key="op-1",
        actor_id="agent/payments-bot",
        resource_id="acct-ops-1",
        mode="inline",
    )
    assert req.context == {"amount": 1000, "currency": "USD"}
    assert req.mode == "inline"


def test_serialization_matches_gateway_contract():
    """Field names in the serialized body must exactly match
    gateway/app.py::EvaluateRequest -- no renaming, no extra wrapper keys."""
    req = EvaluateRequest(
        identity="agent/x", action="send_payment", context={"amount": 1},
        transaction_id="t1", idempotency_key="i1", actor_id="a1",
        resource_id="r1", mode="observe",
    )
    body = req.model_dump(mode="json", exclude_none=True)
    assert body == {
        "identity": "agent/x",
        "action": "send_payment",
        "context": {"amount": 1},
        "transaction_id": "t1",
        "idempotency_key": "i1",
        "actor_id": "a1",
        "resource_id": "r1",
        "mode": "observe",
    }


def test_serialization_omits_unset_optional_fields():
    req = EvaluateRequest(identity="agent/x", action="send_payment")
    body = req.model_dump(mode="json", exclude_none=True)
    assert body == {"identity": "agent/x", "action": "send_payment", "context": {}}
    for optional in ("transaction_id", "idempotency_key", "actor_id", "resource_id", "mode"):
        assert optional not in body


@pytest.mark.parametrize("missing_field", ["identity", "action"])
def test_required_fields_are_enforced(missing_field):
    fields = {"identity": "agent/x", "action": "send_payment"}
    del fields[missing_field]
    with pytest.raises(ValidationError):
        EvaluateRequest(**fields)


def test_empty_identity_rejected():
    with pytest.raises(ValidationError):
        EvaluateRequest(identity="", action="send_payment")


def test_empty_action_rejected():
    with pytest.raises(ValidationError):
        EvaluateRequest(identity="agent/x", action="")


def test_unknown_top_level_request_field_rejected_locally():
    with pytest.raises(ValidationError) as exc_info:
        EvaluateRequest(identity="agent/x", action="send_payment", not_a_real_field="x")
    assert "not_a_real_field" in str(exc_info.value)


def test_nested_context_field_is_not_restricted():
    """context stays a generic, unvalidated object -- matches the live
    Gateway's EvaluateRequest.context (Dict[str, Any]), not a fixed schema."""
    req = EvaluateRequest(
        identity="agent/x", action="send_payment",
        context={"anything": "goes", "nested": {"a": 1}},
    )
    assert req.context == {"anything": "goes", "nested": {"a": 1}}


def test_invalid_mode_value_rejected_locally():
    with pytest.raises(ValidationError):
        EvaluateRequest(identity="agent/x", action="send_payment", mode="bogus")


def test_request_is_immutable_after_construction_does_not_mutate_context():
    """Governance-sensitive values must not be silently modified: mutating
    the dict passed in should not retroactively change a request that has
    already captured its own copy semantics via Pydantic validation."""
    original_context = {"amount": 50}
    req = EvaluateRequest(identity="agent/x", action="send_payment", context=original_context)
    original_context["amount"] = 999999
    # Pydantic validates/copies dict values on construction; mutating the
    # caller's original dict afterward must not retroactively alter the
    # value this SDK will serialize and send.
    assert req.context["amount"] == 50


# --------------------------------------------------------------------------
# Response handling
# --------------------------------------------------------------------------

_BASE_RESPONSE = {
    "decision": "ALLOW",
    "reason": "verified mandate",
    "audit_id": "abc123",
    "signature": "sig",
    "decision_token": {"sig": "sig", "iss": "mcc/core"},
    "constraints": {},
    "forward_context": {"amount": 50},
    "applied_constraints": [],
    "enforce": True,
    "mode": "inline",
    "authority_required": "payments.send",
    "policy_ref": "p@h",
    "trace_id": "t1",
    "transaction_id": None,
    "idempotency_key": None,
    "actor_id": "agent/x",
    "resource_id": None,
}


@pytest.mark.parametrize(
    "decision,executable,denied,needs_approval,constrained",
    [
        ("ALLOW", True, False, False, False),
        ("DENY", False, True, False, False),
        ("ESCALATE", False, False, True, False),
        ("CONSTRAIN", True, False, False, True),
    ],
)
def test_each_canonical_verdict_parses_correctly(decision, executable, denied, needs_approval, constrained):
    body = dict(_BASE_RESPONSE, decision=decision)
    resp = EvaluateResponse.model_validate(body)
    assert resp.decision == Verdict(decision)
    assert resp.executable is executable
    assert resp.denied is denied
    assert resp.needs_approval is needs_approval
    assert resp.constrained is constrained


def test_deny_response_carries_no_token():
    body = dict(_BASE_RESPONSE, decision="DENY", signature=None, decision_token=None)
    resp = EvaluateResponse.model_validate(body)
    assert resp.signature is None
    assert resp.decision_token is None


def test_optional_response_fields_follow_the_contract_defaults():
    minimal = {"decision": "DENY", "reason": "no mandate", "audit_id": "a1"}
    resp = EvaluateResponse.model_validate(minimal)
    assert resp.signature is None
    assert resp.decision_token is None
    assert resp.constraints == {}
    assert resp.forward_context == {}
    assert resp.applied_constraints == []
    assert resp.enforce is True
    assert resp.mode == "observe"
    assert resp.policy_ref == ""
    assert resp.trace_id == ""


def test_unknown_verdict_fails_closed():
    body = dict(_BASE_RESPONSE, decision="MAYBE")
    with pytest.raises(ValidationError):
        EvaluateResponse.model_validate(body)


def test_unknown_response_field_fails_closed():
    """The contract does not permit an extra top-level response field --
    an unrecognized one must be rejected, not silently dropped."""
    body = dict(_BASE_RESPONSE, unexpected_new_field="surprise")
    with pytest.raises(ValidationError):
        EvaluateResponse.model_validate(body)


@pytest.mark.parametrize("missing_field", ["decision", "reason", "audit_id"])
def test_missing_required_response_field_fails_closed(missing_field):
    body = dict(_BASE_RESPONSE)
    del body[missing_field]
    with pytest.raises(ValidationError):
        EvaluateResponse.model_validate(body)


def test_decision_token_stays_opaque_dict():
    """decision_token is intentionally untyped, matching the canonical
    server model (gateway/app.py::EvaluateResponse.decision_token:
    Optional[Dict[str, Any]]) exactly -- the SDK does not interpret it."""
    body = dict(_BASE_RESPONSE, decision_token={"anything": "goes", "nested": {"x": 1}})
    resp = EvaluateResponse.model_validate(body)
    assert resp.decision_token == {"anything": "goes", "nested": {"x": 1}}


def test_malformed_response_not_a_dict_fails_closed():
    with pytest.raises(ValidationError):
        EvaluateResponse.model_validate(["not", "a", "dict"])


def test_wrong_type_field_fails_closed():
    body = dict(_BASE_RESPONSE, applied_constraints="should be a list, not a string")
    with pytest.raises(ValidationError):
        EvaluateResponse.model_validate(body)
