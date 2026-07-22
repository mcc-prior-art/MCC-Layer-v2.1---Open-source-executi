"""Registration: informational, deterministic, fail-closed (PR #50)."""

from __future__ import annotations

import pytest

from mcc_adapter_sdk import AdapterSDKError, register_adapter
from mcc_protocol import AdapterRegistry
from tests.adapter_sdk.conftest import GoodAdapter


def test_successful_registration_is_informational():
    reg = AdapterRegistry()
    result = register_adapter(GoodAdapter(), reg)
    assert result.metadata.adapter_id == "test-good"
    assert reg.is_registered("test-good")
    # A registration record grants no authority surface.
    for forbidden in ("authorize", "execute", "sign", "certify", "approve", "grant"):
        assert not hasattr(result, forbidden)
        assert not hasattr(reg, forbidden)


def test_duplicate_registration_rejected():
    reg = AdapterRegistry()
    register_adapter(GoodAdapter(), reg)
    with pytest.raises(AdapterSDKError):
        register_adapter(GoodAdapter(), reg)
    # ...unless explicitly replacing.
    register_adapter(GoodAdapter(), reg, replace=True)


def test_incompatible_version_rejected():
    # A descriptor declaring an unsupported protocol major is rejected, fail-closed.
    from mcc_protocol import AdapterDescriptor, AdapterRegistryError
    reg = AdapterRegistry()
    with pytest.raises(AdapterRegistryError):
        reg.register(AdapterDescriptor(adapter_id="x", framework="f", adapter_version="1",
                                       supported_protocol_versions=("2.0",)))


def test_registration_is_deterministic():
    a = register_adapter(GoodAdapter(), AdapterRegistry())
    b = register_adapter(GoodAdapter(), AdapterRegistry())
    assert a.to_dict() == b.to_dict()
