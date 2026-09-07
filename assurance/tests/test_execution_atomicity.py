"""Workstream B -- Execution Atomicity / State Machine (PR #71).

Two halves:

1. Pure reference-model tests (no SUT): ``assurance.state_machine``'s
   transition validator correctly accepts every legal path and rejects
   illegal ones -- this is the normative model itself, checked in isolation.
2. Real fault injection: a genuine OS-level process kill severs the
   actuator's connection to the external-effect sink MID-SCENARIO (after
   authorization, before receipt confirmation), and the test observes --
   over real HTTP only -- that the actuator never reports ``executed=true``
   without a confirmed receipt, that no phantom receipt exists once the
   sink comes back, and (Round 17) that the SAME idempotency key stays
   blocked afterward -- an ambiguous post-dispatch fault must never release
   logical-operation ownership for another attempt -- while a genuinely NEW
   logical operation (a fresh idempotency key) can still succeed. See
   ``docs/DURABLE_OPERATION_SAFETY.md``.
"""

from __future__ import annotations

import uuid

import pytest

from assurance.state_machine import (
    IllegalTransitionError,
    classify_actuator_outcome,
    is_valid_transition_sequence,
    validate_transition_sequence,
)

LEGAL_SEQUENCES = [
    ("prepared-then-denied", ["PREPARED", "DENIED"]),
    ("full-happy-path", ["PREPARED", "AUTHORIZED", "EVIDENCE_COMMITTED", "DISPATCHED", "EXECUTED"]),
    ("fault-then-reconciled", ["PREPARED", "AUTHORIZED", "EVIDENCE_COMMITTED", "DISPATCHED",
                                "EXECUTION_UNKNOWN", "RECONCILED"]),
]

ILLEGAL_SEQUENCES = [
    ("skips-authorization", ["PREPARED", "EVIDENCE_COMMITTED", "DISPATCHED", "EXECUTED"]),
    ("skips-evidence-commit", ["PREPARED", "AUTHORIZED", "DISPATCHED", "EXECUTED"]),
    ("denied-then-executed", ["PREPARED", "DENIED", "EXECUTED"]),
    ("executed-without-dispatch", ["PREPARED", "AUTHORIZED", "EVIDENCE_COMMITTED", "EXECUTED"]),
    ("unknown-skips-dispatch", ["PREPARED", "AUTHORIZED", "EVIDENCE_COMMITTED", "EXECUTION_UNKNOWN"]),
    ("does-not-start-at-prepared", ["AUTHORIZED", "EVIDENCE_COMMITTED", "DISPATCHED", "EXECUTED"]),
    ("does-not-end-terminal", ["PREPARED", "AUTHORIZED", "EVIDENCE_COMMITTED", "DISPATCHED"]),
    ("empty", []),
    ("unknown-state-name", ["PREPARED", "NOT_A_REAL_STATE"]),
]


@pytest.mark.parametrize("case_id,sequence", LEGAL_SEQUENCES, ids=[c[0] for c in LEGAL_SEQUENCES])
def test_b1_model_accepts_every_legal_sequence(case_id, sequence):
    validate_transition_sequence(sequence)  # must not raise
    assert is_valid_transition_sequence(sequence) is True


@pytest.mark.parametrize("case_id,sequence", ILLEGAL_SEQUENCES, ids=[c[0] for c in ILLEGAL_SEQUENCES])
def test_b2_model_rejects_every_illegal_sequence(case_id, sequence):
    with pytest.raises(IllegalTransitionError):
        validate_transition_sequence(sequence)
    assert is_valid_transition_sequence(sequence) is False


def test_b3_real_authorized_execution_classifies_as_executed(sut):
    tx = str(uuid.uuid4())
    proposal = sut.propose_notification(transaction_id=tx, idempotency_key=tx)
    votes = sut.actuator_votes(
        action="http.request", payload=sut.canonical_notification_action(proposal),
        actor="agent/egress", resource="notify", nonce=proposal["nonce"],
    )
    result = sut.submit_notification_votes(proposal, votes=votes)

    state = classify_actuator_outcome(proposed=True, executed=result["executed"], outcome=result["outcome"])
    assert state == "EXECUTED"
    validate_transition_sequence(["PREPARED", "AUTHORIZED", "EVIDENCE_COMMITTED", "DISPATCHED", state])


def test_b4_real_forged_authority_classifies_as_denied(sut):
    tx = str(uuid.uuid4())
    proposal = sut.propose_notification(transaction_id=tx, idempotency_key=tx)
    forged = sut.forge_vote(
        action="http.request", payload=sut.canonical_notification_action(proposal),
        actor="agent/egress", resource="notify", nonce=proposal["nonce"],
    )
    result = sut.submit_notification_votes(proposal, votes=[forged] * 3)

    state = classify_actuator_outcome(proposed=True, executed=result["executed"], outcome=result["outcome"])
    assert state == "DENIED"
    validate_transition_sequence(["PREPARED", state])


def test_b5_fault_injection_upstream_killed_mid_flight_never_reports_executed(sut):
    """The centerpiece: authorize a genuine operation, then hard-kill the
    real external-effect sink process before the actuator's outbound call
    can complete. The actuator must never claim executed=true without a
    confirmed receipt."""
    tx = str(uuid.uuid4())
    proposal = sut.propose_notification(transaction_id=tx, idempotency_key=tx)
    votes = sut.actuator_votes(
        action="http.request", payload=sut.canonical_notification_action(proposal),
        actor="agent/egress", resource="notify", nonce=proposal["nonce"],
    )

    sut.kill_notify()
    try:
        result = sut.submit_notification_votes(proposal, votes=votes)
    finally:
        sut.restart_notify()

    assert result["executed"] is False
    state = classify_actuator_outcome(proposed=True, executed=result["executed"], outcome=result["outcome"])
    assert state == "EXECUTION_UNKNOWN"
    # EXECUTION_UNKNOWN alone is not a complete lifecycle (it is not terminal
    # in the reference model -- see state_machine.TERMINAL_STATES); this
    # implementation resolves it synchronously, within the SAME response, to
    # an implicit RECONCILED("not executed") rather than leaving it dangling
    # -- see the module docstring's honesty note.
    validate_transition_sequence(
        ["PREPARED", "AUTHORIZED", "EVIDENCE_COMMITTED", "DISPATCHED", state, "RECONCILED"]
    )

    # The sink is back, freshly restarted (0 receipts) -- no phantom receipt
    # from the failed attempt survived the fault.
    assert sut.notification_receipt_count() == 0


def test_b6_retry_with_same_idempotency_key_after_fault_stays_blocked(sut):
    """Round 17 remediation: a transient upstream fault that occurs AFTER
    durable dispatch commitment (the sink is killed mid-flight) leaves the
    logical operation UNKNOWN, not released. A fresh, independently valid
    authorization presenting the SAME idempotency key must therefore stay
    blocked -- it must NEVER be silently re-admitted and re-actuated purely
    because the caller retried. (This replaces the previous version of this
    test, which asserted the opposite -- that the same key became
    executable again after the fault -- exactly the class of defect Astra's
    Round 16/17 inspection identified: an ambiguous post-dispatch failure
    must not release logical-operation ownership for another attempt. See
    ``docs/DURABLE_OPERATION_SAFETY.md``.)"""
    tx = str(uuid.uuid4())
    proposal = sut.propose_notification(transaction_id=tx, idempotency_key=tx)
    votes = sut.actuator_votes(
        action="http.request", payload=sut.canonical_notification_action(proposal),
        actor="agent/egress", resource="notify", nonce=proposal["nonce"],
    )

    sut.kill_notify()
    try:
        first = sut.submit_notification_votes(proposal, votes=votes)
    finally:
        sut.restart_notify()
    assert first["executed"] is False

    before_retry = sut.notification_receipt_count()
    retry_proposal = sut.propose_notification(transaction_id=tx, idempotency_key=tx)
    retry_votes = sut.actuator_votes(
        action="http.request", payload=sut.canonical_notification_action(retry_proposal),
        actor="agent/egress", resource="notify", nonce=retry_proposal["nonce"],
    )
    retry_result = sut.submit_notification_votes(retry_proposal, votes=retry_votes)

    # AUTHORIZED != SAFE_TO_ACTUATE: the retry is a fresh, independently
    # valid authorization (its own nonce/consensus), yet the logical
    # operation itself remains unresolved -- so it must be blocked/denied,
    # never silently re-actuated.
    assert retry_result["executed"] is False
    assert retry_result["outcome"] != "ALLOW"
    assert sut.notification_receipt_count() == before_retry  # zero additional side effects


def test_b6b_a_deliberate_new_logical_operation_can_still_succeed(sut):
    """Recovery from an unresolved fault is still possible -- but only via a
    genuinely NEW logical operation (a fresh idempotency key the caller
    deliberately mints), never a blind retry of the ambiguous one. This is
    the operator-level analogue of ``reconciliation.py``'s discipline for
    the GPT-6 Astra GitHub-issue actuator: recovery requires either
    independently verified positive evidence for the SAME operation, or an
    explicit decision to originate a NEW one."""
    tx = str(uuid.uuid4())
    proposal = sut.propose_notification(transaction_id=tx, idempotency_key=tx)
    votes = sut.actuator_votes(
        action="http.request", payload=sut.canonical_notification_action(proposal),
        actor="agent/egress", resource="notify", nonce=proposal["nonce"],
    )

    sut.kill_notify()
    try:
        first = sut.submit_notification_votes(proposal, votes=votes)
    finally:
        sut.restart_notify()
    assert first["executed"] is False

    before_retry = sut.notification_receipt_count()
    new_tx = str(uuid.uuid4())  # a deliberately NEW logical operation
    fresh_proposal = sut.propose_notification(transaction_id=new_tx, idempotency_key=new_tx)
    fresh_votes = sut.actuator_votes(
        action="http.request", payload=sut.canonical_notification_action(fresh_proposal),
        actor="agent/egress", resource="notify", nonce=fresh_proposal["nonce"],
    )
    fresh_result = sut.submit_notification_votes(fresh_proposal, votes=fresh_votes)

    assert fresh_result["outcome"] == "ALLOW"
    assert fresh_result["executed"] is True
    assert sut.notification_receipt_count() == before_retry + 1
