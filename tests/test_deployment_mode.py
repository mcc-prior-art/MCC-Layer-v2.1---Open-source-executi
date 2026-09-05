"""mcc_core.deployment_mode — the reference/enforcement posture switch
(Production Trust Hardening Phase 1, Workstream 1).

This module answers exactly one question ("which posture is configured?")
and is deliberately narrow: it does not decide, execute, or replay-protect
anything itself. See src/mcc_core/deployment_mode.py's own docstring for
why this is a separate, minimal switch rather than an overload of the
existing MCC_ENV (gateway.trust.trust_set_from_env).
"""

import pytest

from mcc_core import DeploymentModeConfigError, deployment_mode_from_env, is_enforcement_mode


def test_defaults_to_reference():
    assert deployment_mode_from_env({}) == "reference"
    assert is_enforcement_mode({}) is False


def test_explicit_reference():
    assert deployment_mode_from_env({"MCC_DEPLOYMENT_MODE": "reference"}) == "reference"
    assert is_enforcement_mode({"MCC_DEPLOYMENT_MODE": "reference"}) is False


def test_explicit_enforcement():
    assert deployment_mode_from_env({"MCC_DEPLOYMENT_MODE": "enforcement"}) == "enforcement"
    assert is_enforcement_mode({"MCC_DEPLOYMENT_MODE": "enforcement"}) is True


def test_case_and_whitespace_insensitive():
    assert deployment_mode_from_env({"MCC_DEPLOYMENT_MODE": "  Enforcement  "}) == "enforcement"


def test_unknown_mode_fails_closed():
    with pytest.raises(DeploymentModeConfigError):
        deployment_mode_from_env({"MCC_DEPLOYMENT_MODE": "production"})
    with pytest.raises(DeploymentModeConfigError):
        is_enforcement_mode({"MCC_DEPLOYMENT_MODE": "prod"})


def test_reads_real_os_environ_when_no_mapping_given(monkeypatch):
    monkeypatch.setenv("MCC_DEPLOYMENT_MODE", "enforcement")
    assert is_enforcement_mode() is True
    monkeypatch.delenv("MCC_DEPLOYMENT_MODE")
    assert is_enforcement_mode() is False
