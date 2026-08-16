"""Lightweight, static CI guard for the Gateway API Contract (PR #79):
``openapi/mcc-gateway.yaml`` + ``docs/integration/GATEWAY_API_CONTRACT.md`` +
``docs/integration/examples/``.

Deliberately does NOT boot the gateway or regenerate the example files --
those were generated once, by hand, against the real running gateway when
this contract was authored (see the file docstrings/history for how). This
suite only proves the *documents* stay structurally intact: the OpenAPI file
stays valid, the four canonical verdicts and required endpoints stay present,
every documented example file still exists and is valid JSON, the contract
doc still covers its required sections, and the README still links to both.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml
from openapi_spec_validator import validate as validate_openapi_spec

ROOT = Path(__file__).resolve().parents[1]
OPENAPI_PATH = ROOT / "openapi" / "mcc-gateway.yaml"
CONTRACT_DOC_PATH = ROOT / "docs" / "integration" / "GATEWAY_API_CONTRACT.md"
EXAMPLES_DIR = ROOT / "docs" / "integration" / "examples"

REQUIRED_ENDPOINTS = ["/evaluate", "/execute", "/health", "/ready"]

CANONICAL_VERDICTS = ["ALLOW", "DENY", "ESCALATE", "CONSTRAIN"]

REQUIRED_EXAMPLE_FILES = [
    "allow.request.json",
    "allow.response.json",
    "deny.request.json",
    "deny.response.json",
    "escalate.request.json",
    "escalate.response.json",
    "constrain.request.json",
    "constrain.response.json",
    "replay-deny.request.json",
    "idempotency-conflict.response.json",
    "malformed-request.response.json",
]

REQUIRED_DOC_SECTIONS = [
    "## 1. Purpose",
    "## 2. Architecture",
    "## 3. Trust boundary",
    "## 4. Agent-to-MCC flow",
    "## 5. Difference between",
    "## 6. Request envelope",
    "## 7. Decision envelope",
    "## 8. Verdict behavior",
    "## 9. Fail-closed rules",
    "## 10. Idempotency",
    "## 11. Nonce",
    "## 12. Policy and payload binding",
    "## 13. Mandate / authority context",
    "## 14. Approval and escalation references",
    "## 15. Constraints",
    "## 16. Audit correlation",
    "## 17. Redis/multi-instance notes",
    "## 18. Error model",
    "## 19. Security expectations for integrators",
    "## 20. Current implementation status",
    "## 21. Known gaps",
    "## 22. Residual risks",
    "## 23. Example integration flow",
]

CANONICAL_DOCTRINE = (
    "The model proposes.\n"
    "MCC decides.\n"
    "The gate enforces.\n"
    "The audit chain records."
)

EXECUTOR_RULE = "The executor must act only after a verified MCC decision."

# The doc must explicitly *disclaim* these (adapter certification is out of
# scope for this PR -- see the module docstring and the PR task), so the
# guard checks for the disclaiming phrase, not bare absence of the words
# (the disclaimer itself has to name what it is disclaiming).
REQUIRED_CERTIFICATION_DISCLAIMERS = [
    "makes no claim of certified adapters, AXLOGIQ-certified status, a "
    "production signing ceremony, an official certification program, "
    "issued technical certificates, or any legal/commercial certification",
]


@pytest.fixture(scope="module")
def openapi_spec() -> dict:
    with OPENAPI_PATH.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def test_openapi_file_exists():
    assert OPENAPI_PATH.is_file(), f"missing: {OPENAPI_PATH}"


def test_openapi_file_is_valid_yaml(openapi_spec):
    assert isinstance(openapi_spec, dict)
    assert openapi_spec.get("openapi", "").startswith("3.")


def test_openapi_spec_is_valid_openapi_3(openapi_spec):
    # Raises on failure; a passing call is the assertion.
    validate_openapi_spec(openapi_spec)


@pytest.mark.parametrize("endpoint", REQUIRED_ENDPOINTS)
def test_required_endpoint_present_in_spec(openapi_spec, endpoint):
    paths = openapi_spec.get("paths", {})
    assert endpoint in paths, f"openapi/mcc-gateway.yaml is missing required path: {endpoint}"


def test_execute_endpoint_marked_not_implemented(openapi_spec):
    """PR #79 requires /execute to be defined as a *target* contract with the
    implementation gap clearly marked, not silently presented as working."""
    execute_post = openapi_spec["paths"]["/execute"]["post"]
    assert execute_post.get("x-implementation-status") == "not-implemented"


@pytest.mark.parametrize("verdict", CANONICAL_VERDICTS)
def test_canonical_verdict_present_in_spec(openapi_spec, verdict):
    verdict_schema = openapi_spec["components"]["schemas"]["Verdict"]
    assert verdict in verdict_schema["enum"]


def test_verdict_enum_has_exactly_four_values(openapi_spec):
    verdict_schema = openapi_spec["components"]["schemas"]["Verdict"]
    assert sorted(verdict_schema["enum"]) == sorted(CANONICAL_VERDICTS)


def test_openapi_carries_canonical_doctrine(openapi_spec):
    doctrine = openapi_spec["info"]["x-doctrine"]
    normalized = " ".join(doctrine.split())
    expected = " ".join(CANONICAL_DOCTRINE.split())
    assert normalized == expected


def test_openapi_carries_executor_rule(openapi_spec):
    assert openapi_spec["info"]["x-executor-rule"].strip() == EXECUTOR_RULE


@pytest.mark.parametrize("filename", REQUIRED_EXAMPLE_FILES)
def test_required_example_file_exists(filename):
    path = EXAMPLES_DIR / filename
    assert path.is_file(), f"missing required example file: {path}"


@pytest.mark.parametrize("filename", REQUIRED_EXAMPLE_FILES)
def test_required_example_file_is_valid_json(filename):
    path = EXAMPLES_DIR / filename
    with path.open(encoding="utf-8") as f:
        json.load(f)  # raises on invalid JSON


@pytest.mark.parametrize(
    "filename,expected_decision",
    [
        ("allow.response.json", "ALLOW"),
        ("deny.response.json", "DENY"),
        ("escalate.response.json", "ESCALATE"),
        ("constrain.response.json", "CONSTRAIN"),
    ],
)
def test_evaluate_response_example_matches_its_verdict(filename, expected_decision):
    data = json.loads((EXAMPLES_DIR / filename).read_text(encoding="utf-8"))
    assert data["decision"] == expected_decision


def test_constrain_response_forward_context_differs_from_original():
    """CONSTRAIN must never authorize the original, unclamped payload."""
    request = json.loads((EXAMPLES_DIR / "constrain.request.json").read_text(encoding="utf-8"))
    response = json.loads((EXAMPLES_DIR / "constrain.response.json").read_text(encoding="utf-8"))
    assert response["forward_context"] != request["context"]
    assert response["applied_constraints"], "CONSTRAIN example has no applied_constraints"


def test_deny_and_escalate_examples_carry_no_decision_token():
    for filename in ("deny.response.json", "escalate.response.json"):
        data = json.loads((EXAMPLES_DIR / filename).read_text(encoding="utf-8"))
        assert data["decision_token"] is None, f"{filename} must not carry a Decision Token"
        assert data["signature"] is None, f"{filename} must not carry a signature"


def test_idempotency_conflict_example_is_blocked():
    data = json.loads((EXAMPLES_DIR / "idempotency-conflict.response.json").read_text(encoding="utf-8"))
    assert data["status"] == "BLOCKED"


def test_malformed_request_example_is_a_validation_error():
    data = json.loads((EXAMPLES_DIR / "malformed-request.response.json").read_text(encoding="utf-8"))
    assert "detail" in data


def test_contract_doc_exists():
    assert CONTRACT_DOC_PATH.is_file(), f"missing: {CONTRACT_DOC_PATH}"


def test_contract_doc_has_all_required_sections_in_order():
    text = CONTRACT_DOC_PATH.read_text(encoding="utf-8")
    positions = []
    for heading in REQUIRED_DOC_SECTIONS:
        idx = text.find(heading)
        assert idx != -1, f"docs/integration/GATEWAY_API_CONTRACT.md is missing required section: {heading!r}"
        positions.append(idx)
    assert positions == sorted(positions), (
        "docs/integration/GATEWAY_API_CONTRACT.md sections are present but out of order"
    )


def test_contract_doc_carries_canonical_doctrine_verbatim():
    text = CONTRACT_DOC_PATH.read_text(encoding="utf-8")
    assert CANONICAL_DOCTRINE in text


def test_contract_doc_carries_executor_rule_verbatim():
    text = CONTRACT_DOC_PATH.read_text(encoding="utf-8")
    assert EXECUTOR_RULE in text


def test_contract_doc_disclaims_adapter_certification():
    text = CONTRACT_DOC_PATH.read_text(encoding="utf-8")
    normalized = " ".join(text.split())
    assert "not adapter certification" in normalized
    for phrase in REQUIRED_CERTIFICATION_DISCLAIMERS:
        assert " ".join(phrase.split()) in normalized, (
            f"docs/integration/GATEWAY_API_CONTRACT.md is missing the required "
            f"certification-scope disclaimer: {phrase!r}"
        )


def test_contract_doc_references_all_required_example_files():
    text = CONTRACT_DOC_PATH.read_text(encoding="utf-8")
    for filename in REQUIRED_EXAMPLE_FILES:
        assert filename in text, (
            f"docs/integration/GATEWAY_API_CONTRACT.md never references example file: {filename}"
        )


def test_readme_links_to_gateway_api_contract():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "docs/integration/GATEWAY_API_CONTRACT.md" in readme, (
        "README.md does not link to docs/integration/GATEWAY_API_CONTRACT.md"
    )
    assert "openapi/mcc-gateway.yaml" in readme, (
        "README.md does not link to openapi/mcc-gateway.yaml"
    )
