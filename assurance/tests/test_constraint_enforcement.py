"""Workstream F -- Constraint Enforcement (PR #71).

Proves the CONSTRAIN verdict black-box: given a request that exceeds an
authority's bound (here, the actuator's ``max_amount`` cap on
``body.amount`` -- see ``assurance/sut/actuator_process.py``), the ORIGINAL
excessive action is never executed, and execution -- when it happens at
all -- happens ONLY on the clamped value. Correctness is verified against
the OBSERVED ``action_hash`` of what was actually authorized, computed
independently by Workstream D's ``assurance.canonical_action`` module, not
by trusting the actuator's own claim that it clamped correctly.

The two-round protocol (proposal -> CONSTRAIN with a NEW challenge over the
clamped payload -> resubmit with ``constrained=True``) is exercised through
the real HTTP API only, via ``SystemUnderTest`` helpers.

This file does NOT use the shared, session-scoped ``sut`` fixture every
other workstream module depends on: the actuator's ``max_body.amount``
constraint must be present for these tests, but a ``max_`` constraint on a
field simply ABSENT from a request counts as an unclampable violation (see
``mcc_core.authority._constraint_violations``), which would turn every OTHER
workstream's amount-less proposals from ALLOW into DENY if applied to the
shared actuator. This file boots its own, separately constrained SUT instead.
"""

from __future__ import annotations

import uuid

import pytest

from assurance.canonical_action import action_hash, build_canonical_action
from assurance.sut.harness import DEFAULT_MAX_AMOUNT, build_system_under_test


@pytest.fixture(scope="module")
def sut():
    with build_system_under_test(max_amount=DEFAULT_MAX_AMOUNT) as constrained_sut:
        yield constrained_sut


def test_f1_within_cap_amount_executes_unconstrained(sut):
    """Baseline: a request already within the cap needs no clamp."""
    tx = str(uuid.uuid4())
    proposal = sut.propose_notification(transaction_id=tx, idempotency_key=tx, amount=sut.max_amount // 2)
    votes = sut.actuator_votes(
        action="http.request", payload=sut.canonical_notification_action(proposal),
        actor="agent/egress", resource="notify", nonce=proposal["nonce"],
    )
    result = sut.submit_notification_votes(proposal, votes=votes)

    assert result["outcome"] == "ALLOW"
    assert result["executed"] is True
    assert result["applied_constraints"] == []


def test_f2_excessive_amount_is_not_executed_and_returns_a_clamp(sut):
    """The first round over an excessive amount must never execute -- it
    returns CONSTRAIN with the clamped action, not an authorization."""
    tx = str(uuid.uuid4())
    excessive = sut.max_amount * 5
    proposal = sut.propose_notification(transaction_id=tx, idempotency_key=tx, amount=excessive)
    votes = sut.actuator_votes(
        action="http.request", payload=sut.canonical_notification_action(proposal),
        actor="agent/egress", resource="notify", nonce=proposal["nonce"],
    )
    result = sut.submit_notification_votes(proposal, votes=votes)

    assert result["outcome"] == "CONSTRAIN"
    assert result["executed"] is False
    assert result["constrained_action"]["body.amount"] == sut.max_amount
    assert any(str(excessive) in c and str(sut.max_amount) in c for c in result["applied_constraints"])


def test_f3_only_the_clamped_payload_ever_executes(sut):
    """Complete the two-round flow and verify -- independently -- that the
    EXECUTED action_hash corresponds exactly to the clamped payload, never
    to the original excessive one."""
    tx = str(uuid.uuid4())
    excessive = sut.max_amount * 5
    proposal = sut.propose_notification(transaction_id=tx, idempotency_key=tx, amount=excessive)
    votes1 = sut.actuator_votes(
        action="http.request", payload=sut.canonical_notification_action(proposal),
        actor="agent/egress", resource="notify", nonce=proposal["nonce"],
    )
    round1 = sut.submit_notification_votes(proposal, votes=votes1)
    assert round1["outcome"] == "CONSTRAIN" and round1["executed"] is False

    votes2 = sut.actuator_votes(
        action="http.request", payload=round1["constrained_action"],
        actor="agent/egress", resource="notify", nonce=round1["nonce"],
    )
    round2 = sut.submit_constrained_votes(round1, clamped_amount=sut.max_amount, votes=votes2)

    assert round2["executed"] is True

    independent_clamped_hash = action_hash(build_canonical_action(
        method="POST", url=round1["_request"]["url"], headers={},
        body={**{k: v for k, v in round1["_request"]["body"].items() if k != "amount"}, "amount": sut.max_amount},
    ))
    independent_original_hash = action_hash(build_canonical_action(
        method="POST", url=round1["_request"]["url"], headers={}, body=round1["_request"]["body"],
    ))

    assert round2["action_hash"] == independent_clamped_hash
    assert round2["action_hash"] != independent_original_hash


def test_f4_resubmitting_the_original_excessive_amount_as_constrained_is_refused(sut):
    """A caller cannot skip the clamp by resubmitting ``constrained=True``
    with the SAME original (still excessive) body -- ``execute_constrained``
    fail-closed-refuses a payload that would itself need further clamping."""
    tx = str(uuid.uuid4())
    excessive = sut.max_amount * 9
    proposal = sut.propose_notification(transaction_id=tx, idempotency_key=tx, amount=excessive)
    votes1 = sut.actuator_votes(
        action="http.request", payload=sut.canonical_notification_action(proposal),
        actor="agent/egress", resource="notify", nonce=proposal["nonce"],
    )
    round1 = sut.submit_notification_votes(proposal, votes=votes1)
    assert round1["outcome"] == "CONSTRAIN"

    # Vote for the (correctly) clamped payload, but then submit the ORIGINAL
    # excessive amount anyway with constrained=True -- a payload-hash
    # mismatch against what was voted on.
    votes2 = sut.actuator_votes(
        action="http.request", payload=round1["constrained_action"],
        actor="agent/egress", resource="notify", nonce=round1["nonce"],
    )
    round2 = sut.submit_constrained_votes(round1, clamped_amount=excessive, votes=votes2)

    assert not (round2["outcome"] in ("ALLOW", "CONSTRAIN") and round2["executed"] is True)
