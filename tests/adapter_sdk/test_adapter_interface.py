"""Adapter interface: translation contract, fail-closed (PR #50)."""

from __future__ import annotations

from typing import Any

import pytest

import mcc_protocol as mp
from mcc_adapter_sdk import Adapter, AdapterMetadata, AdapterSDKError
from mcc_adapter_sdk.validation import FORBIDDEN_METHODS
from tests.adapter_sdk.conftest import GoodAdapter


def test_valid_adapter_translates_both_ways(context):
    a = GoodAdapter()
    proposal = a.to_proposal(context, "hi")
    assert isinstance(proposal, mp.CanonicalProposal)
    assert proposal.action == "send_notification" and proposal.actor == "agent/notify-bot"
    proposal.validate()


def test_adapter_exposes_no_authoritative_verbs():
    a = GoodAdapter()
    for verb in FORBIDDEN_METHODS:
        assert not hasattr(a, verb), f"adapter exposes forbidden {verb!r}"


def test_missing_translation_method_is_a_type_error():
    # An Adapter subclass that does not implement the abstract methods cannot be built.
    class Incomplete(Adapter):
        def describe(self) -> AdapterMetadata:
            return AdapterMetadata.create(adapter_id="x", adapter_version="1", framework_name="f")
        # missing to_proposal / to_response
    with pytest.raises(TypeError):
        Incomplete()  # type: ignore[abstract]


def test_make_proposal_fails_closed_on_bad_payload(context):
    class BadPayload(GoodAdapter):
        def to_proposal(self, ctx, native):
            return self.make_proposal(ctx, action="send_notification",
                                      resource="notifications", payload="not-a-dict")  # type: ignore[arg-type]
    with pytest.raises(AdapterSDKError):
        BadPayload().to_proposal(context, "x")


def test_sample_request_optional_default_raises():
    class NoSample(GoodAdapter):
        def sample_request(self) -> Any:
            return Adapter.sample_request(self)
    with pytest.raises(AdapterSDKError):
        NoSample().sample_request()
