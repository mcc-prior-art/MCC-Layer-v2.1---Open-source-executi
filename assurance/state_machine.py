"""Normative Execution State Machine (PR #71, Workstream B).

The reference model for how one governed operation is meant to move from
proposal to a settled outcome. This module is a pure, dependency-free
reference: it validates transition SEQUENCES against the model; it does not
observe or drive the real system (that is
``assurance/tests/test_execution_atomicity.py``'s job, over real HTTP plus
real process-level fault injection).

## The eight states

``PREPARED`` -> the canonical action has been built and hashed; no
    authority decision has been made yet.
``AUTHORIZED`` -> a verified decision (consensus/mandate) grants execution;
    nothing has happened in the world yet.
``EVIDENCE_COMMITTED`` -> the audit entry for this authorization is durably
    written (fsync'd) BEFORE any attempt to act -- audit-before-actuation.
``DISPATCHED`` -> the governed side effect (the outbound call) has been
    attempted.
``EXECUTED`` -> a verified receipt confirms the side effect happened
    exactly as authorized.
``DENIED`` -> no authority was granted; nothing was dispatched. Terminal.
``EXECUTION_UNKNOWN`` -> dispatched, but no receipt was confirmed (the
    upstream call failed, timed out, or the connection dropped after the
    request may or may not have been received). Terminal from the caller's
    point of view within one request/response cycle -- see the honesty note
    below.
``RECONCILED`` -> a later, out-of-band process determined the true outcome
    of an ``EXECUTION_UNKNOWN`` operation (e.g. an idempotency-keyed retry,
    or an operator checking the upstream's own record). Terminal.

## Honesty note: what this repository's actuator actually exposes

``egress_proxy``'s receipt-verifying executor (see
``pilot_notify.governed_upstream.receipt_verifying_upstream``) never reports
``executed=true`` without an independently confirmed receipt. Concretely,
this collapses the caller-visible surface WITHIN ONE request/response cycle:
a transport failure between ``DISPATCHED`` and receipt confirmation is
reported synchronously, as ``executed=false`` (outcome ``UPSTREAM_ERROR``)
-- the caller never sees a distinct, persistent "unknown, come back later"
status inline in that response. ``EXECUTION_UNKNOWN`` is a real internal
possibility (a request may have reached the upstream before the connection
dropped) but is never a directly observable terminal state OF THAT ONE
RESPONSE; it resolves eagerly to "not executed" -- see
``ASSUMPTIONS_AND_LIMITS.md``.

Round 17 correction (previously this note also claimed the SAME
idempotency key "then permits exactly one further attempt" -- that was
the exact defect class Astra's Round 16/17 inspection identified, and it is
no longer true): internally, the coordinator now durably parks that
operation at ``EXECUTION_UNKNOWN`` (``mcc_core.idempotency.IdempotencyState.
UNKNOWN``) rather than releasing it, and a SUBSEQUENT presentation of the
SAME idempotency key -- however freshly and validly authorized -- is
BLOCKED, not re-admitted. ``RECONCILED`` is reached only via independently
verified positive evidence for that exact operation (see
``examples/gpt6_astra_reference/reconciliation.py`` for the one actuator
this repository ships with such a reconciliation path), or via a
genuinely NEW logical operation (a different idempotency key, a deliberate
caller/operator decision) -- never implicitly, via a blind retry of the
ambiguous one. ``assurance/tests/test_execution_atomicity.py``
(``test_b6_retry_with_same_idempotency_key_after_fault_stays_blocked`` /
``test_b6b_a_deliberate_new_logical_operation_can_still_succeed``) verifies
this directly. See ``docs/DURABLE_OPERATION_SAFETY.md`` for the full state
machine and durability model.
"""

from __future__ import annotations

from typing import Dict, FrozenSet, List, Sequence, Tuple

STATES: FrozenSet[str] = frozenset({
    "PREPARED", "AUTHORIZED", "EVIDENCE_COMMITTED", "DISPATCHED",
    "EXECUTED", "DENIED", "EXECUTION_UNKNOWN", "RECONCILED",
})

TERMINAL_STATES: FrozenSet[str] = frozenset({"DENIED", "EXECUTED", "RECONCILED"})

#: Directed edges: (from, to). Everything not listed is an illegal transition.
ALLOWED_TRANSITIONS: FrozenSet[Tuple[str, str]] = frozenset({
    ("PREPARED", "AUTHORIZED"),
    ("PREPARED", "DENIED"),
    ("AUTHORIZED", "EVIDENCE_COMMITTED"),
    ("EVIDENCE_COMMITTED", "DISPATCHED"),
    ("DISPATCHED", "EXECUTED"),
    ("DISPATCHED", "EXECUTION_UNKNOWN"),
    ("EXECUTION_UNKNOWN", "RECONCILED"),
})


class IllegalTransitionError(ValueError):
    """A proposed state sequence violates the reference model."""


def validate_transition_sequence(states: Sequence[str]) -> None:
    """Raise ``IllegalTransitionError`` if any step in ``states`` is not an
    edge in ``ALLOWED_TRANSITIONS``, if any state name is unknown, if the
    sequence is empty, if it does not start at ``PREPARED``, or if it does
    not end in a terminal state. Never returns a bool -- fail-closed callers
    should treat "did not raise" as the only pass condition."""
    if not states:
        raise IllegalTransitionError("a transition sequence must have at least one state")
    unknown = [s for s in states if s not in STATES]
    if unknown:
        raise IllegalTransitionError(f"unknown state(s): {unknown}")
    if states[0] != "PREPARED":
        raise IllegalTransitionError(f"a sequence must start at PREPARED, got {states[0]!r}")
    if states[-1] not in TERMINAL_STATES:
        raise IllegalTransitionError(f"a sequence must end in a terminal state, got {states[-1]!r}")
    for a, b in zip(states, states[1:]):
        if (a, b) not in ALLOWED_TRANSITIONS:
            raise IllegalTransitionError(f"illegal transition {a!r} -> {b!r}")


def is_valid_transition_sequence(states: Sequence[str]) -> bool:
    try:
        validate_transition_sequence(states)
        return True
    except IllegalTransitionError:
        return False


def classify_actuator_outcome(*, proposed: bool, executed: bool, outcome: str) -> str:
    """Map ONE observed HTTP round of this repository's actuator response
    onto the nearest reference-model terminal state, per the honesty note
    above (EXECUTION_UNKNOWN/RECONCILED are never directly observable here;
    a transport failure resolves eagerly to a DISPATCHED->EXECUTION_UNKNOWN
    reference-model reading, reported to the caller as "not executed").

    ``proposed=False`` (canonicalization/schema rejection, before any
    authority decision) has no reference-model terminal counterpart -- it
    never reached PREPARED in the first place; callers should not classify
    those responses with this function."""
    if not proposed:
        raise ValueError("classify_actuator_outcome is only for canonicalized proposals (proposed=True)")
    if executed:
        return "EXECUTED"
    if outcome in ("DENY", "INVALID_REQUEST", "CONSENSUS_REQUIRED"):
        # CONSENSUS_REQUIRED is an intermediate (still PREPARED/AUTHORIZED-pending)
        # response, not a terminal one -- see classify_actuator_outcome's caller
        # in the test module, which never terminally classifies it.
        return "DENIED" if outcome != "CONSENSUS_REQUIRED" else "PREPARED"
    # UPSTREAM_ERROR and any other non-executed, post-authorization outcome:
    # this implementation resolves DISPATCHED -> EXECUTION_UNKNOWN eagerly to
    # "not executed" within the same response -- see the module docstring.
    return "EXECUTION_UNKNOWN"
