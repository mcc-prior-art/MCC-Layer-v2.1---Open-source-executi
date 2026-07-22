"""CanonicalProposal: shape, determinism, fail-closed validation (PR #49)."""

from __future__ import annotations

import pytest

import mcc_protocol as mp
from mcc_protocol.proposal import ProposalValidationError, compute_action_hash
from tests.protocol.conftest import make_proposal


def test_create_fills_protocol_defaults():
    p = make_proposal()
    assert p.contract_version == mp.PROTOCOL_VERSION
    assert p.proposal_id and p.trace_id and p.correlation_id and p.nonce
    assert p.issued_at and p.expires_at
    assert p.principal == p.actor  # defaults to actor
    # All the spec-required fields are present.
    for f in ("contract_version", "proposal_id", "trace_id", "correlation_id",
              "adapter_id", "framework", "actor", "principal", "action", "resource",
              "action_hash", "nonce", "issued_at", "expires_at", "payload", "metadata",
              "authority_context", "policy_context", "risk_context", "requested_scope"):
        assert hasattr(p, f)


def test_action_hash_is_deterministic_and_bound():
    p = make_proposal()
    assert p.action_hash == compute_action_hash(p.action, p.resource, p.actor, p.payload)
    # Changing the payload changes the hash.
    other = compute_action_hash(p.action, p.resource, p.actor, {"x": "different"})
    assert other != p.action_hash


def test_roundtrip_to_from_dict():
    p = make_proposal()
    again = mp.CanonicalProposal.from_dict(p.to_dict())
    assert again.to_dict() == p.to_dict()


def test_missing_required_field_fails_closed():
    p = make_proposal()
    with pytest.raises(ProposalValidationError):
        mp.CanonicalProposal(
            proposal_id="", trace_id=p.trace_id, correlation_id=p.correlation_id,
            adapter_id=p.adapter_id, adapter_version=p.adapter_version,
            framework=p.framework, actor=p.actor, action=p.action, resource=p.resource,
            action_hash=p.action_hash, nonce=p.nonce, issued_at=p.issued_at,
            payload=p.payload).validate()


def test_tampered_action_hash_rejected():
    d = make_proposal().to_dict()
    d["action_hash"] = "sha256:deadbeef"
    with pytest.raises(ProposalValidationError):
        mp.CanonicalProposal.from_dict(d)


def test_tampered_payload_invalidates_hash():
    d = make_proposal().to_dict()
    d["payload"] = {"recipient": "attacker", "message": "x", "priority": 2, "channel": "email"}
    # action_hash no longer matches the payload -> fail closed.
    with pytest.raises(ProposalValidationError):
        mp.CanonicalProposal.from_dict(d)


def test_non_dict_payload_rejected():
    with pytest.raises(ProposalValidationError):
        make_proposal(payload=["not", "a", "dict"])


def test_expiry_is_fail_closed_on_garbage():
    p = make_proposal()
    from dataclasses import replace
    assert replace(p, expires_at="not-a-timestamp").is_expired() is True


def test_from_dict_non_object_fails_closed():
    with pytest.raises(ProposalValidationError):
        mp.CanonicalProposal.from_dict("not a dict")
