"""Round 19/21 — the ONE place every governed ``create_github_issue`` call in
this reference integration prepares its complete outbound payload (schema
validation + logical-operation marker) and arms the final-boundary payload
check, before the proposal is ever presented to attestation or
authorization.

This module exists specifically to close implementation defects found by
independent verification:

1. (Round 19) The reconciliation marker used to be appended to the payload
   by a wrapper actuator AFTER the Gate had already verified the (unmarked)
   payload's hash -- meaning the payload actually sent to GitHub was never
   the one that was cryptographically authorized. Here the marker becomes
   part of the payload BEFORE it is ever canonicalized, attested, hashed, or
   signed into a token -- see ``issue_contract.build_marked_payload`` -- so
   there is nothing left to mutate afterward.
2. (Round 19) A caller could reuse one long-lived actuator wrapper across
   two different logical operations without updating its marker/identity
   context. Every call here mints its own marked proposal and arms its own
   independently-bound, single-shot verifier immediately before its own
   governed call (``github_actuator.VerifiedDispatchSlot.expect``) -- there
   is no mutable, settable identity anywhere for a second, later call to
   accidentally inherit.
3. (Round 21) A payload could carry additional authorized fields (e.g.
   ``labels``) that generic canonicalization retained (so they were signed
   into the token) but the actuator's own field-by-field reconstruction
   silently dropped before the real HTTP POST. Here the payload is
   validated against ``create_github_issue``'s strict, closed request
   schema (title/body only) BEFORE canonicalization/attestation/hashing --
   see ``issue_contract.validate_github_issue_request_payload`` -- so an
   unsupported field is rejected outright, never silently forwarded or
   dropped.
"""

from __future__ import annotations

import dataclasses
from typing import Any, Callable, Dict, Optional

from mcc_core.signing import hash_payload

from .issue_contract import GITHUB_ISSUE_ACTION, prepare_complete_github_issue_payload
from .models import AstraProposal


def prepare_marked_call(
    proposal: AstraProposal,
    *,
    logical_operation_id: str,
    canonical_payload_fn: Callable[[Dict[str, Any]], Dict[str, Any]],
    actuator: Optional[Any] = None,
) -> AstraProposal:
    """Returns a NEW :class:`AstraProposal` (``proposal`` itself is never
    mutated). For the one action this reference integration's real actuator
    understands (``issue_contract.GITHUB_ISSUE_ACTION``), the returned
    proposal's payload has been schema-validated (unsupported fields
    rejected; ``body``'s ingress default materialized) AND already carries
    ``logical_operation_marker(logical_operation_id)`` in its body -- both
    built BEFORE this proposal is ever presented to attestation or
    authorization, so they are part of the SAME payload that gets
    canonicalized, attested, hashed, and signed into the decision token.
    Every OTHER action is returned unchanged: neither the schema nor the
    marker apply to it, and it never reaches the real GitHub actuator
    through this package's own wiring regardless.

    ``canonical_payload_fn`` is the caller's own
    ``stack.profiles.for_action(...).canonical_payload`` -- the SAME
    canonicalization the real ``ExecutionGate``/token-issuance path applies.
    This function never reimplements or guesses at it.

    If ``actuator`` is supplied and is not ``None``, it is armed here
    (``actuator.expect(action=..., payload_hash=...)``), immediately, with
    exactly the action and payload_hash this prepared proposal is about to
    present to authorization -- the value the real, trusted authorization
    path is about to independently compute and sign, not a value invented
    after the fact. Pass ``actuator=None`` for a call that never reaches the
    real governed GitHub actuator (e.g. a non-canonical action, or a
    canonical one presented against a resource outside the mandate's scope,
    in the adversarial harness)."""
    if proposal.action != GITHUB_ISSUE_ACTION:
        return proposal
    prepared_payload = prepare_complete_github_issue_payload(
        proposal.payload, logical_operation_id=logical_operation_id,
    )
    marked_proposal = dataclasses.replace(proposal, payload=prepared_payload)
    if actuator is not None:
        canonical = canonical_payload_fn(marked_proposal.payload)
        actuator.expect(action=marked_proposal.action, payload_hash=hash_payload(canonical))
    return marked_proposal


__all__ = ["prepare_marked_call"]
