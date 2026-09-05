"""mcc_attester_service.provider_loader — the production AssessmentProvider
selection boundary (Production Trust Hardening Phase 1, Workstream 2).

Covers: reference-mode behavior is unchanged; enforcement mode refuses the
DeterministicTestProvider outright, requires an explicit, importable,
well-typed operator-supplied provider class, and fails closed on every
missing/malformed/hostile configuration.
"""

from __future__ import annotations

import asyncio
import json
from pathlib import Path

import pytest

from mcc_attester_service.errors import AttesterServiceConfigError
from mcc_attester_service.provider import AssessmentResult, DeterministicTestProvider
from mcc_attester_service.provider_loader import assessment_provider_from_env

run = asyncio.run

FIXTURE_MODULE = "tests.fixtures.production_provider_fixtures"


def _table_file(tmp_path: Path) -> str:
    table = {"send_*": {"evidence_type": "risk_assessment", "claims": {"risk_class": "low"}}}
    p = tmp_path / "table.json"
    p.write_text(json.dumps(table), encoding="utf-8")
    return str(p)


# ---------------------------------------------------------------------------
# Reference mode: unchanged behavior.
# ---------------------------------------------------------------------------


def test_reference_mode_default_loads_deterministic_test_provider(tmp_path):
    provider = assessment_provider_from_env({
        "MCC_ATTESTER_TEST_ASSESSMENT_TABLE": _table_file(tmp_path),
    })
    assert isinstance(provider, DeterministicTestProvider)


def test_reference_mode_explicit_loads_deterministic_test_provider(tmp_path):
    provider = assessment_provider_from_env({
        "MCC_DEPLOYMENT_MODE": "reference",
        "MCC_ATTESTER_TEST_ASSESSMENT_TABLE": _table_file(tmp_path),
    })
    assert isinstance(provider, DeterministicTestProvider)


def test_reference_mode_requires_table():
    with pytest.raises(AttesterServiceConfigError):
        assessment_provider_from_env({"MCC_DEPLOYMENT_MODE": "reference"})


# ---------------------------------------------------------------------------
# Enforcement mode: production provider boundary.
# ---------------------------------------------------------------------------


def test_enforcement_mode_missing_provider_class_refuses():
    with pytest.raises(AttesterServiceConfigError):
        assessment_provider_from_env({"MCC_DEPLOYMENT_MODE": "enforcement"})


def test_enforcement_mode_rejects_deterministic_test_provider_explicitly():
    with pytest.raises(AttesterServiceConfigError) as excinfo:
        assessment_provider_from_env({
            "MCC_DEPLOYMENT_MODE": "enforcement",
            "MCC_ATTESTER_PROVIDER_CLASS": "mcc_attester_service.provider:DeterministicTestProvider",
        })
    assert "DeterministicTestProvider" in str(excinfo.value)


def test_enforcement_mode_rejects_test_assessment_table_even_with_valid_class(tmp_path):
    # A test table configured alongside enforcement mode is itself refused
    # -- this combination is a misconfiguration, not something to silently
    # resolve by picking one of the two.
    with pytest.raises(AttesterServiceConfigError):
        assessment_provider_from_env({
            "MCC_DEPLOYMENT_MODE": "enforcement",
            "MCC_ATTESTER_PROVIDER_CLASS": f"{FIXTURE_MODULE}:FakeProductionProvider",
            "MCC_ATTESTER_TEST_ASSESSMENT_TABLE": _table_file(tmp_path),
        })


def test_enforcement_mode_loads_a_real_operator_provider():
    provider = assessment_provider_from_env({
        "MCC_DEPLOYMENT_MODE": "enforcement",
        "MCC_ATTESTER_PROVIDER_CLASS": f"{FIXTURE_MODULE}:FakeProductionProvider",
    })
    result = run(provider.assess(action="send_x", resource=None, payload={}))
    assert isinstance(result, AssessmentResult)
    assert result.evidence_type == "fixture"


def test_enforcement_mode_rejects_unimportable_module():
    with pytest.raises(AttesterServiceConfigError):
        assessment_provider_from_env({
            "MCC_DEPLOYMENT_MODE": "enforcement",
            "MCC_ATTESTER_PROVIDER_CLASS": "no_such_module_at_all:Whatever",
        })


def test_enforcement_mode_rejects_missing_attribute():
    with pytest.raises(AttesterServiceConfigError):
        assessment_provider_from_env({
            "MCC_DEPLOYMENT_MODE": "enforcement",
            "MCC_ATTESTER_PROVIDER_CLASS": f"{FIXTURE_MODULE}:ThisDoesNotExist",
        })


def test_enforcement_mode_rejects_malformed_dotted_path():
    with pytest.raises(AttesterServiceConfigError):
        assessment_provider_from_env({
            "MCC_DEPLOYMENT_MODE": "enforcement",
            "MCC_ATTESTER_PROVIDER_CLASS": "not-a-dotted-path",
        })


def test_enforcement_mode_rejects_non_class_target():
    with pytest.raises(AttesterServiceConfigError):
        assessment_provider_from_env({
            "MCC_DEPLOYMENT_MODE": "enforcement",
            "MCC_ATTESTER_PROVIDER_CLASS": f"{FIXTURE_MODULE}:NOT_A_CLASS",
        })


def test_enforcement_mode_rejects_class_not_implementing_assessment_provider():
    with pytest.raises(AttesterServiceConfigError):
        assessment_provider_from_env({
            "MCC_DEPLOYMENT_MODE": "enforcement",
            "MCC_ATTESTER_PROVIDER_CLASS": f"{FIXTURE_MODULE}:NotAProvider",
        })


def test_enforcement_mode_rejects_provider_that_raises_on_construction():
    with pytest.raises(AttesterServiceConfigError):
        assessment_provider_from_env({
            "MCC_DEPLOYMENT_MODE": "enforcement",
            "MCC_ATTESTER_PROVIDER_CLASS": f"{FIXTURE_MODULE}:RaisingConstructorProvider",
        })


def test_enforcement_mode_never_falls_back_to_deterministic_test_provider_on_bad_config():
    # Every one of the above failures must raise, never quietly return a
    # DeterministicTestProvider (or anything else) as a fallback.
    for env in [
        {"MCC_DEPLOYMENT_MODE": "enforcement"},
        {"MCC_DEPLOYMENT_MODE": "enforcement", "MCC_ATTESTER_PROVIDER_CLASS": "bogus"},
    ]:
        with pytest.raises(AttesterServiceConfigError):
            assessment_provider_from_env(env)
