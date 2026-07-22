"""AdapterContext: immutable, deterministic, bounded, secret-free (PR #50)."""

from __future__ import annotations

import pytest

from mcc_adapter_sdk import AdapterContext, AdapterSDKError


def test_deterministic_representation():
    a = AdapterContext.create(actor_reference="x", tenant="t", framework_metadata={"k": 1})
    b = AdapterContext.create(actor_reference="x", tenant="t", framework_metadata={"k": 1})
    assert a.to_dict() == b.to_dict()


def test_actor_reference_required():
    with pytest.raises(AdapterSDKError):
        AdapterContext.create(actor_reference="")


def test_bounded_extension_data():
    big = {f"k{i}": i for i in range(33)}
    with pytest.raises(AdapterSDKError):
        AdapterContext.create(actor_reference="x", extension=big)


def test_rejects_unserializable_values():
    with pytest.raises(AdapterSDKError):
        AdapterContext.create(actor_reference="x", extension={"bad": object()})
    with pytest.raises(AdapterSDKError):
        AdapterContext.create(actor_reference="x", framework_metadata={"bad": {1, 2}})


def test_no_secrets_in_repr():
    ctx = AdapterContext.create(
        actor_reference="agent", framework_metadata={"api_key": "SUPER-SECRET-VALUE"},
        extension={"token": "TOP-SECRET-TOKEN"})
    r = repr(ctx)
    assert "SUPER-SECRET-VALUE" not in r
    assert "TOP-SECRET-TOKEN" not in r
    # Only key names may appear, never values.
    assert "api_key" in r and "token" in r


def test_extension_key_constraints():
    with pytest.raises(AdapterSDKError):
        AdapterContext.create(actor_reference="x", extension={"": 1})
    with pytest.raises(AdapterSDKError):
        AdapterContext.create(actor_reference="x", extension={"k" * 200: 1})
