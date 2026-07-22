"""Version negotiation reuses the PR #43 rule and fails closed (PR #49)."""

from __future__ import annotations

import mcc_client.contract as contract
import mcc_protocol as mp
from mcc_client.contract import ContractErrorCode


def test_protocol_version_is_the_contract_version():
    # Exactly one version axis — no parallel protocol version number.
    assert mp.PROTOCOL_VERSION == contract.CONTRACT_VERSION


def test_negotiate_delegates_to_the_contract_rule():
    assert mp.negotiate(mp.PROTOCOL_VERSION).compatible is True
    # Same result object shape as the contract's own check.
    assert mp.negotiate("1.0").compatible == contract.check_version_compatibility("1.0").compatible


def test_unsupported_major_fails_closed():
    c = mp.negotiate("2.0")
    assert c.compatible is False
    assert c.error_code == ContractErrorCode.CONTRACT_VERSION_UNSUPPORTED


def test_malformed_version_fails_closed():
    c = mp.negotiate("banana")
    assert c.compatible is False
    assert c.error_code == ContractErrorCode.CONTRACT_VERSION_MALFORMED


def test_higher_minor_is_compatible_but_flagged():
    c = mp.negotiate("1.9")
    assert c.compatible is True
    assert c.newer_minor is True
