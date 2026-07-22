"""AdapterMetadata: immutable, deterministic, version-compatible, fail-closed (PR #50)."""

from __future__ import annotations

import dataclasses

import pytest

from mcc_adapter_sdk import AdapterMetadata, AdapterSDKError
from mcc_compliance.capability_profile import BASELINE_CAPABILITIES


def _md(**kw):
    base = dict(adapter_id="a", adapter_version="1.0.0", framework_name="none")
    base.update(kw)
    return AdapterMetadata.create(**base)


def test_valid_metadata():
    md = _md(capabilities=(BASELINE_CAPABILITIES[0],), vendor="ACME")
    assert md.adapter_id == "a" and md.vendor == "ACME"


def test_metadata_is_immutable():
    md = _md()
    with pytest.raises(dataclasses.FrozenInstanceError):
        md.adapter_id = "b"  # type: ignore[misc]


def test_missing_required_field_fails_closed():
    with pytest.raises(AdapterSDKError):
        _md(adapter_id="")


def test_unsupported_protocol_version_fails_closed():
    with pytest.raises(AdapterSDKError):
        _md(protocol_version="2.0")


def test_unsupported_contract_version_fails_closed():
    with pytest.raises(AdapterSDKError):
        _md(contract_version="9.9")


def test_malformed_capability_fails_closed():
    with pytest.raises(AdapterSDKError):
        _md(capabilities=("not_a_real_capability",))


def test_capabilities_not_a_list_fails_closed():
    with pytest.raises(AdapterSDKError):
        _md(capabilities="a-string")


def test_deterministic_serialization_and_hashing():
    md = _md(capabilities=(BASELINE_CAPABILITIES[0],))
    assert md.to_dict() == md.to_dict()
    assert md.digest() == md.digest()
    # A different adapter has a different digest.
    assert _md(adapter_id="other").digest() != md.digest()


def test_roundtrip_from_dict():
    md = _md(capabilities=(BASELINE_CAPABILITIES[0],), maintainer="x")
    assert AdapterMetadata.from_dict(md.to_dict()).to_dict() == md.to_dict()


def test_digest_is_stable_across_key_order():
    # to_dict is canonicalized before hashing, so field construction order is irrelevant.
    a = AdapterMetadata.create(adapter_id="a", adapter_version="1", framework_name="f",
                               vendor="V", maintainer="M")
    b = AdapterMetadata.create(maintainer="M", vendor="V", framework_name="f",
                               adapter_version="1", adapter_id="a")
    assert a.digest() == b.digest()
