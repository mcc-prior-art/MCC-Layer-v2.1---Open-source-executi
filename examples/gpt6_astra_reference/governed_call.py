"""Round 19 — the ONE place every governed ``create_github_issue`` call in
this reference integration prepares its logical-operation marker and arms
the final-boundary payload check, before the proposal is ever presented to
attestation or authorization.

This module exists specifically to close two Round 18-independent-
verification defects:

1. The reconciliation marker used to be appended to the payload by a
   wrapper actuator AFTER the Gate had already verified the (unmarked)
   payload's hash -- meaning the payload actually sent to GitHub was never
   the one that was cryptographically authorized
   (``github_actuator.LogicalOperationMarkerActuator``, removed). Here the
   marker becomes part of the payload BEFORE it is ever canonicalized,
   attested, hashed, or signed into a token -- see
   ``github_actuator.build_marked_payload`` -- so there is nothing left to
   mutate afterward.
2. A caller could reuse one long-lived actuator wrapper across two
   different logical operations without updating its marker/identity
   context (``cli.py``'s ``run_autonomous_expansion``), risking drift
   between the id presented to durable admission/the token and the id
   embedded in the outbound payload. Every call here mints its own marked
   proposal and arms its own single-use expectation on the actuator
   (``github_actuator.VerifiedFinalPayloadActuator.expect``) immediately
   before its own governed call -- there is no mutable, settable identity
   left on the actuator for a second, later call to accidentally inherit.
"""

from __future__ import annotations

import dataclasses
from typing import Any, Callable, Dict, Optional

from mcc_core.signing import hash_payload

from .github_actuator import build_marked_payload
from .models import AstraProposal


def prepare_marked_call(
    proposal: AstraProposal,
    *,
    logical_operation_id: str,
    canonical_payload_fn: Callable[[Dict[str, Any]], Dict[str, Any]],
    actuator: Optional[Any] = None,
) -> AstraProposal:
    """Returns a NEW :class:`AstraProposal` (``proposal`` itself is never
    mutated) whose payload already carries
    ``logical_operation_marker(logical_operation_id)`` in its body -- built
    BEFORE this proposal is ever presented to attestation or authorization,
    so the marker is part of the SAME payload that gets canonicalized,
    attested, hashed, and signed into the decision token.

    ``canonical_payload_fn`` is the caller's own
    ``stack.profiles.for_action(...).canonical_payload`` -- the SAME
    canonicalization the real ``ExecutionGate``/token-issuance path applies.
    This function never reimplements or guesses at it.

    If ``actuator`` is supplied and is not ``None``, it is armed here
    (``actuator.expect(action=..., payload_hash=...)``), immediately, with
    exactly the action and payload_hash this marked proposal is about to
    present to authorization -- the value the real, trusted authorization
    path is about to independently compute and sign, not a value invented
    after the fact. Pass ``actuator=None`` for a call that never reaches the
    real governed GitHub actuator (e.g. a non-canonical action in the
    adversarial harness routed to a local recorder instead)."""
    marked_payload = build_marked_payload(proposal.payload, logical_operation_id=logical_operation_id)
    marked_proposal = dataclasses.replace(proposal, payload=marked_payload)
    if actuator is not None:
        canonical = canonical_payload_fn(marked_proposal.payload)
        actuator.expect(action=marked_proposal.action, payload_hash=hash_payload(canonical))
    return marked_proposal


__all__ = ["prepare_marked_call"]
