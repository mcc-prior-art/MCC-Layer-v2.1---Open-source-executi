"""Workstream C -- Decision Authority Containment (PR #71).

Workstream A proves the ACTUATOR never executes without verified authority.
This workstream proves the same invariant one layer up, at the GATEWAY
itself: its ``/consensus/challenge`` + ``/consensus/execute`` HTTP API (the
authority source an actuator or adapter ultimately depends on) never reports
an executed decision without a genuine, correctly bound N-of-M evaluator
consensus, observed the same way -- by independently polling the Gateway's
own external-effect sink (a second, separate ``pilot_notify`` instance; see
``SharedGovernedGateway``), never by trusting the Gateway's self-reported
status alone.

C1 is the positive baseline (proves the effect CAN occur on a genuinely
authorized path, so every attack below is a meaningful negative, not a
tautology). C2-C7 are the adversarial containment attacks.

C8 documents, rather than tests around, a real scope limitation: this SUT
configures ONLY the consensus authority path (``MCC_CONSENSUS_TRUST_CONFIG``)
-- no mandate issuer trust is configured, so ``/mandates/execute`` fails
closed for EVERY mandate, forged or genuine alike. That proves fail-closed
behavior when no authority is configured, but it does NOT exercise
genuine-vs-forged SIGNED MANDATE containment (there is no genuine mandate
path to compare against in this deployment). Recorded honestly in
``ASSUMPTIONS_AND_LIMITS.md`` rather than presented as mandate coverage this
suite does not have.
"""

from __future__ import annotations

import uuid
from typing import Any, Dict

import httpx

ACTOR = "agent/notify-bot"
ACTION = "send_notification"
RESOURCE = "notifications"


def _payload(**overrides: Any) -> Dict[str, Any]:
    base = {"recipient": "customer-123", "message": "assurance-c-probe", "priority": 2,
            "channel": "email", "correlation_id": str(uuid.uuid4())}
    base.update(overrides)
    return base


def _challenge(sut, payload: Dict[str, Any], *, actor: str = ACTOR) -> Dict[str, Any]:
    r = httpx.post(
        f"{sut.gateway_url}/consensus/challenge", headers={"x-api-key": sut.api_key},
        json={"actor": actor, "action": ACTION, "resource": RESOURCE, "context": payload}, timeout=10.0,
    )
    r.raise_for_status()
    return r.json()


def _execute(sut, payload: Dict[str, Any], challenge: Dict[str, Any], votes, *, actor: str = ACTOR) -> Dict[str, Any]:
    r = httpx.post(
        f"{sut.gateway_url}/consensus/execute", headers={"x-api-key": sut.api_key},
        json={"votes": votes, "actor": actor, "action": ACTION, "resource": RESOURCE, "context": payload,
              "challenge_id": challenge["challenge_id"], "nonce": challenge["nonce"]}, timeout=10.0,
    )
    return r.json()


def test_c1_authorized_consensus_reaches_the_gateway_upstream(sut):
    before = sut.gateway_notification_receipt_count()

    payload = _payload()
    challenge = _challenge(sut, payload)
    votes = sut.gateway_consensus_votes(
        action=ACTION, payload=payload, actor=ACTOR, resource=RESOURCE,
        nonce=challenge["nonce"], policy_hash=challenge.get("policy_hash"),
    )
    result = _execute(sut, payload, challenge, votes)

    assert result["status"] == "EXECUTED"
    assert result["decision"] == "ALLOW"
    assert sut.gateway_notification_receipt_count() == before + 1


def test_c2_below_threshold_votes_denied(sut):
    before = sut.gateway_notification_receipt_count()

    payload = _payload()
    challenge = _challenge(sut, payload)
    votes = sut.gateway_consensus_votes(
        action=ACTION, payload=payload, actor=ACTOR, resource=RESOURCE,
        nonce=challenge["nonce"], policy_hash=challenge.get("policy_hash"),
    )[:1]
    result = _execute(sut, payload, challenge, votes)

    assert result["status"] != "EXECUTED"
    assert result["decision"] == "DENY"
    assert sut.gateway_notification_receipt_count() == before


def test_c3_trusted_deny_vote_vetoes_despite_sufficient_allow_votes(sut):
    before = sut.gateway_notification_receipt_count()

    payload = _payload()
    challenge = _challenge(sut, payload)
    allow_votes = sut.gateway_consensus_votes(
        action=ACTION, payload=payload, actor=ACTOR, resource=RESOURCE,
        nonce=challenge["nonce"], policy_hash=challenge.get("policy_hash"),
    )
    veto_vote = sut.gateway_vote_as(  # a genuinely TRUSTED evaluator casting DENY
        evaluator_index=2, verdict="DENY", action=ACTION, payload=payload, actor=ACTOR,
        resource=RESOURCE, nonce=challenge["nonce"], policy_hash=challenge.get("policy_hash"),
    )
    votes = allow_votes[:2] + [veto_vote]

    result = _execute(sut, payload, challenge, votes)

    assert result["status"] != "EXECUTED"
    assert "VETO" in result["reason"]
    assert sut.gateway_notification_receipt_count() == before


def test_c4_votes_bound_to_wrong_policy_hash_rejected(sut):
    before = sut.gateway_notification_receipt_count()

    payload = _payload()
    challenge = _challenge(sut, payload)
    votes = sut.gateway_consensus_votes(
        action=ACTION, payload=payload, actor=ACTOR, resource=RESOURCE,
        nonce=challenge["nonce"], policy_hash="sha256:" + "0" * 64,  # a stale/foreign policy version
    )
    result = _execute(sut, payload, challenge, votes)

    assert result["status"] != "EXECUTED"
    assert sut.gateway_notification_receipt_count() == before


def test_c5_votes_bound_to_a_different_actor_rejected(sut):
    before = sut.gateway_notification_receipt_count()

    payload = _payload()
    challenge = _challenge(sut, payload)
    votes = sut.gateway_consensus_votes(
        action=ACTION, payload=payload, actor="agent/ops-bot", resource=RESOURCE,
        nonce=challenge["nonce"], policy_hash=challenge.get("policy_hash"),
    )
    result = _execute(sut, payload, challenge, votes)

    assert result["status"] != "EXECUTED"
    assert sut.gateway_notification_receipt_count() == before


def test_c6_forged_untrusted_evaluator_rejected_at_gateway(sut):
    before = sut.gateway_notification_receipt_count()

    payload = _payload()
    challenge = _challenge(sut, payload)
    forged_vote = sut.forge_vote(
        action=ACTION, payload=payload, actor=ACTOR, resource=RESOURCE,
        nonce=challenge["nonce"], policy_hash=challenge.get("policy_hash"),
    )
    result = _execute(sut, payload, challenge, [forged_vote] * 3)

    assert result["status"] != "EXECUTED"
    assert sut.gateway_notification_receipt_count() == before


def test_c7_replayed_challenge_and_votes_denied_after_first_use(sut):
    before = sut.gateway_notification_receipt_count()

    payload = _payload()
    challenge = _challenge(sut, payload)
    votes = sut.gateway_consensus_votes(
        action=ACTION, payload=payload, actor=ACTOR, resource=RESOURCE,
        nonce=challenge["nonce"], policy_hash=challenge.get("policy_hash"),
    )
    first = _execute(sut, payload, challenge, votes)
    assert first["status"] == "EXECUTED"
    assert sut.gateway_notification_receipt_count() == before + 1

    replay = _execute(sut, payload, challenge, votes)
    assert replay["status"] != "EXECUTED"
    assert sut.gateway_notification_receipt_count() == before + 1


def test_c8_mandate_execute_fails_closed_when_no_mandate_authority_is_configured(sut):
    """See module docstring: this SUT has no mandate issuer trust configured,
    so this proves fail-closed-with-no-authority, not genuine-vs-forged
    mandate containment (a stated, documented limitation)."""
    before = sut.gateway_notification_receipt_count()

    r = httpx.post(
        f"{sut.gateway_url}/mandates/execute", headers={"x-api-key": sut.api_key},
        json={"mandate": {"mandate_id": "m1", "issuer_id": "nobody", "subject": ACTOR,
                           "authority": "notify.send", "sig": "AAAA"},
              "actor": ACTOR, "action": ACTION, "resource": RESOURCE, "context": _payload()},
        timeout=10.0,
    )
    body = r.json()

    assert body["status"] != "EXECUTED"
    assert sut.gateway_notification_receipt_count() == before
