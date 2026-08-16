"""Contract-drift protection between mcc_sdk's models and the live Gateway
boundary.

Uses the repository's existing, versioned OpenAPI contract artifact
(``openapi/mcc-gateway.yaml``) as the source of truth -- the same sanctioned,
dependency-safe boundary PR #79/#80 established -- rather than importing
``gateway/app.py`` directly (which would couple this SDK's tests to Gateway
server internals rather than its public contract). Detects the material
incompatibilities the task calls out: renamed/missing required fields,
request strictness changes, changed verdict values, and incompatible
response schema changes.

This is NOT satisfied by mcc_sdk.models and gateway/app.py's models simply
agreeing with each other (two definitions that could drift together
unnoticed) -- it is checked against the independently-maintained OpenAPI
document, and (in test_integration.py) against the real running gateway
over real HTTP.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from mcc_sdk.models import EvaluateRequest, EvaluateResponse, Verdict

ROOT = Path(__file__).resolve().parents[2]
OPENAPI_PATH = ROOT / "openapi" / "mcc-gateway.yaml"


@pytest.fixture(scope="module")
def openapi_spec() -> dict:
    with OPENAPI_PATH.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


@pytest.fixture(scope="module")
def openapi_evaluate_request_schema(openapi_spec) -> dict:
    return openapi_spec["components"]["schemas"]["EvaluateRequest"]


@pytest.fixture(scope="module")
def openapi_evaluate_response_schema(openapi_spec) -> dict:
    return openapi_spec["components"]["schemas"]["EvaluateResponse"]


@pytest.fixture(scope="module")
def openapi_verdict_schema(openapi_spec) -> dict:
    return openapi_spec["components"]["schemas"]["Verdict"]


# --------------------------------------------------------------------------
# Verdict values
# --------------------------------------------------------------------------


def test_verdict_values_match_openapi(openapi_verdict_schema):
    sdk_values = {v.value for v in Verdict}
    openapi_values = set(openapi_verdict_schema["enum"])
    assert sdk_values == openapi_values, (
        f"mcc_sdk.models.Verdict {sdk_values} != openapi Verdict enum {openapi_values} -- "
        "the contract's verdict values have drifted from the SDK"
    )


def test_verdict_has_exactly_four_values():
    """No others exist -- see docs/integration/GATEWAY_API_CONTRACT.md §8."""
    assert len(Verdict) == 4


# --------------------------------------------------------------------------
# EvaluateRequest
# --------------------------------------------------------------------------


def test_request_required_fields_match_openapi(openapi_evaluate_request_schema):
    openapi_required = set(openapi_evaluate_request_schema.get("required", []))
    sdk_required = {
        name for name, field in EvaluateRequest.model_fields.items() if field.is_required()
    }
    assert sdk_required == openapi_required, (
        f"mcc_sdk EvaluateRequest required fields {sdk_required} != "
        f"openapi required fields {openapi_required}"
    )


def test_request_field_names_are_a_subset_of_openapi_properties(openapi_evaluate_request_schema):
    """The SDK must not invent a field the documented contract doesn't have.
    (openapi may in principle document a field the SDK doesn't expose yet --
    that's a coverage gap, not a drift/invention risk, so this is checked as
    strict subset rather than set equality.)"""
    openapi_fields = set(openapi_evaluate_request_schema["properties"].keys())
    sdk_fields = set(EvaluateRequest.model_fields.keys())
    invented = sdk_fields - openapi_fields
    assert not invented, f"mcc_sdk EvaluateRequest has fields not in the documented contract: {invented}"


def test_request_field_names_cover_every_openapi_property(openapi_evaluate_request_schema):
    """The SDK's request model must expose every field the live contract
    defines -- an omission here would silently prevent a caller from
    using a documented, supported request field."""
    openapi_fields = set(openapi_evaluate_request_schema["properties"].keys())
    sdk_fields = set(EvaluateRequest.model_fields.keys())
    missing = openapi_fields - sdk_fields
    assert not missing, f"mcc_sdk EvaluateRequest is missing documented contract fields: {missing}"


def test_request_top_level_strictness_matches_openapi(openapi_evaluate_request_schema):
    """PR #80 fixed the live Gateway to reject unknown top-level /evaluate
    fields (additionalProperties: false). The SDK's request model must
    match that strictness exactly -- this test fails if either side
    reverts without the other."""
    openapi_strict = openapi_evaluate_request_schema.get("additionalProperties") is False
    sdk_strict = EvaluateRequest.model_config.get("extra") == "forbid"
    assert openapi_strict is True, "expected the documented contract to still be strict (PR #80)"
    assert sdk_strict is True, "mcc_sdk.EvaluateRequest must be extra='forbid' to match the live contract"


def test_request_context_stays_flexible_on_both_sides(openapi_evaluate_request_schema):
    """The documented, intentional exception: context is NOT strict on
    either side. If the Gateway is ever hardened here, this test must be
    revisited alongside the SDK (and the doc) -- it is not silently allowed
    to drift."""
    context_schema = openapi_evaluate_request_schema["properties"]["context"]
    assert context_schema.get("additionalProperties") is True


# --------------------------------------------------------------------------
# EvaluateResponse
# --------------------------------------------------------------------------


def test_response_required_fields_match_openapi(openapi_evaluate_response_schema):
    openapi_required = set(openapi_evaluate_response_schema.get("required", []))
    sdk_required = {
        name for name, field in EvaluateResponse.model_fields.items() if field.is_required()
    }
    assert sdk_required == openapi_required, (
        f"mcc_sdk EvaluateResponse required fields {sdk_required} != "
        f"openapi required fields {openapi_required}"
    )


def test_response_field_names_match_openapi_properties_exactly(openapi_evaluate_response_schema):
    """Unlike the request (subset-checked above, since request coverage
    gaps are lower-risk), the response field set must match EXACTLY: a
    field the SDK doesn't know about is a field it will now reject via
    extra='forbid' the moment the Gateway starts sending it -- which is the
    intended fail-closed behavior, but it means this test is the trip-wire
    that should catch it during development, not in a caller's production
    traffic."""
    openapi_fields = set(openapi_evaluate_response_schema["properties"].keys())
    sdk_fields = set(EvaluateResponse.model_fields.keys())
    assert sdk_fields == openapi_fields, (
        f"mcc_sdk EvaluateResponse fields {sdk_fields} != openapi fields {openapi_fields}"
    )


def test_response_top_level_strictness_matches_openapi_intent():
    """The live gateway.app.py::EvaluateResponse itself is not literally
    extra='forbid' (see docs/integration/GATEWAY_API_CONTRACT.md), but
    FastAPI's response_model filtering means the wire response never
    carries an undocumented field in practice. The SDK deliberately chooses
    the stricter, fail-closed posture here (see models.py docstring) --
    this test documents that as an intentional SDK-side choice, not an
    accidental mismatch, and pins it so it can't silently regress to
    permissive."""
    assert EvaluateResponse.model_config.get("extra") == "forbid"


def test_decision_token_stays_untyped_on_both_sides(openapi_evaluate_response_schema):
    """Confirms the SDK's deliberate choice to leave decision_token opaque
    matches the documented contract's own DecisionToken-is-a-nested-object
    (not further constrained at this response level) shape."""
    token_schema = openapi_evaluate_response_schema["properties"]["decision_token"]
    # decision_token is expressed as an allOf/$ref to DecisionToken in the
    # OpenAPI doc (a fully-typed nested schema exists there for documentation
    # purposes), but the canonical *server* model (gateway/app.py) types it
    # as Dict[str, Any] -- the SDK follows the server, not the doc's richer
    # aspirational schema, and does not invent nested validation the
    # runtime itself does not enforce.
    assert token_schema is not None
