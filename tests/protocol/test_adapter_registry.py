"""Adapter Registry: descriptive, fail-closed, grants no authority (PR #49)."""

from __future__ import annotations

import pytest

import mcc_protocol as mp
from mcc_compliance.capability_profile import BASELINE_CAPABILITIES
from mcc_protocol.registry import AdapterRegistryError


def _desc(**kw):
    base = dict(adapter_id="voltagent", framework="voltagent", adapter_version="1.0.0",
                supported_protocol_versions=(mp.PROTOCOL_VERSION,))
    base.update(kw)
    return mp.AdapterDescriptor(**base)


def test_register_and_lookup():
    reg = mp.AdapterRegistry()
    reg.register(_desc())
    assert reg.is_registered("voltagent")
    d = reg.get("voltagent")
    assert d.framework == "voltagent" and d.supports_version(mp.PROTOCOL_VERSION)


def test_unknown_adapter_lookup_fails_closed():
    reg = mp.AdapterRegistry()
    with pytest.raises(AdapterRegistryError):
        reg.get("ghost")


def test_capabilities_validated_against_the_pr47_vocabulary():
    reg = mp.AdapterRegistry()
    # A baseline capability is accepted...
    reg.register(_desc(capabilities=(BASELINE_CAPABILITIES[0],)))
    # ...an invented one is rejected (single vocabulary; no parallel set).
    with pytest.raises(AdapterRegistryError):
        reg.register(_desc(adapter_id="bad", capabilities=("teleport_execution",)))


def test_unsupported_declared_protocol_version_rejected():
    with pytest.raises(AdapterRegistryError):
        _desc(supported_protocol_versions=("2.0",)).validate()


def test_empty_supported_versions_rejected():
    with pytest.raises(AdapterRegistryError):
        _desc(supported_protocol_versions=()).validate()


def test_registry_exposes_no_authorization_surface():
    reg = mp.AdapterRegistry()
    desc = _desc()
    # The registry (and descriptors) must not offer authorize/execute/sign/verify/
    # certify/decide surfaces — registration is not permission.
    for forbidden in ("authorize", "execute", "sign", "verify_token", "certify",
                      "decide", "issue_token", "grant"):
        assert not hasattr(reg, forbidden)
        assert not hasattr(desc, forbidden)


def test_descriptor_serialization_roundtrips_fields():
    d = _desc(capabilities=(BASELINE_CAPABILITIES[0],),
              conformance={"certification": "reference@1.0", "status": "CERTIFIED"})
    out = d.to_dict()
    assert out["adapter_id"] == "voltagent"
    assert out["conformance"]["status"] == "CERTIFIED"  # informational only
