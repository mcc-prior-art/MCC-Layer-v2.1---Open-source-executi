"""Round 19 surgical remediation — final outbound payload binding and
logical-operation context isolation, for the GPT-6 Astra reference
integration's ``create_github_issue`` action.

Round 18's independent verification found two remaining implementation
defects (both confirmed by direct code execution, not documentation):

1. ``LogicalOperationMarkerActuator`` appended the reconciliation marker to
   the payload AFTER ``ExecutionGate`` had already verified the (unmarked)
   payload's hash -- so the payload actually POSTed to GitHub was never the
   exact payload that was cryptographically authorized.
2. ``cli.py``'s ``run_autonomous_expansion`` built one shared, mutable
   actuator wrapper for its primary operation and later invoked a second
   logical operation without updating that wrapper's marker context --
   structurally permitting logical_operation_id/marker drift across two
   governed calls sharing one actuator instance.

This file proves, at the ACTUAL outbound actuator/network boundary (never
merely a token-vs-registry comparison, a helper-level hash, or a
before-the-Gate denial), that both are now closed:

* the exact bytes a governed call sends to the (mock) GitHub service hash to
  the exact ``payload_hash`` the real, signed decision token carries;
* modifying the title, body, or logical-operation marker -- or presenting a
  different destination -- strictly AFTER a call's payload/action was armed
  as verified/authorized makes the network call impossible
  (``PayloadBindingError``/``ResourceBindingError``), never merely detected
  after the fact;
* two distinct, in-scope logical operations reaching the SAME shared
  actuator instance never leak a marker or payload-hash expectation from one
  into the other.
"""

from __future__ import annotations

import asyncio

import pytest

from mcc_core.signing import hash_payload

from examples.gpt6_astra_reference._localstack import ACTION, ACTOR, LocalAstraDemoStack
from examples.gpt6_astra_reference.github_actuator import (
    GitHubActuatorConfig,
    GitHubIssueActuator,
    PayloadBindingError,
    ResourceBindingError,
    ResourceBoundActuator,
    VerifiedFinalPayloadActuator,
    build_marked_payload,
    logical_operation_marker,
)
from examples.gpt6_astra_reference.governed_call import prepare_marked_call
from examples.gpt6_astra_reference.mock_github_service import recorded_issues
from examples.gpt6_astra_reference.models import AstraProposal
from examples.gpt6_astra_reference.pipeline import enforce_authority, issue_authority, obtain_attestation

run = asyncio.run
DEMO_REPO = "owner/mcc-astra-demo-sandbox"


def _live_config(stack: LocalAstraDemoStack) -> GitHubActuatorConfig:
    return GitHubActuatorConfig.from_env({
        "MCC_ASTRA_DEMO_MODE": "live",
        "MCC_ASTRA_GITHUB_REPO": stack.demo_repo,
        "MCC_ASTRA_GITHUB_BASE_URL": stack.github_base_url,
    })


def _build_actuator_chain(stack: LocalAstraDemoStack, *, authorized_resource: str) -> VerifiedFinalPayloadActuator:
    """The exact chain ``cli.py``/``adversarial.py`` build in production:
    ``GitHubIssueActuator`` -> ``ResourceBoundActuator`` ->
    ``VerifiedFinalPayloadActuator`` -- the final safety net immediately
    before the real HTTP POST."""
    raw = GitHubIssueActuator(_live_config(stack))
    bound = ResourceBoundActuator(raw, authorized_resource=authorized_resource)
    return VerifiedFinalPayloadActuator(bound)


# ---------------------------------------------------------------------------
# Requirement 1 (a): capture the exact outbound HTTP payload; prove its
# canonical hash equals the real, signed token's payload_hash.
# ---------------------------------------------------------------------------


def test_outbound_payload_hash_equals_verified_token_payload_hash():
    """End-to-end through the real chain (attestation -> authority ->
    Gate -> coordinator -> the real actuator -> the mock GitHub service),
    never tampered. The mock service records exactly what was POSTed
    (``recorded_issues``) -- reconstructing that exact body/title and
    re-hashing it with the SAME ``hash_payload`` the Gate used must equal
    ``issued.token["payload_hash"]`` byte-for-byte."""
    with LocalAstraDemoStack(demo_repo=DEMO_REPO) as stack:
        logical_operation_id = "op-final-binding-proof-1"
        verified = _build_actuator_chain(stack, authorized_resource=DEMO_REPO)
        stack.upstream = verified

        proposal = AstraProposal(
            action=ACTION, resource=DEMO_REPO,
            payload={"title": "Final-binding proof issue", "body": "Exact payload proof."},
        )
        marked_proposal = prepare_marked_call(
            proposal, logical_operation_id=logical_operation_id,
            canonical_payload_fn=stack.profiles.for_action(proposal.action).canonical_payload,
            actuator=verified,
        )
        canonical = stack.profiles.for_action(marked_proposal.action).canonical_payload(marked_proposal.payload)
        att = run(obtain_attestation(stack.attester, proposal=marked_proposal, canonical_payload=canonical))
        issued = run(issue_authority(
            stack.service, mandate=stack.mandate, actor=ACTOR, proposal=marked_proposal,
            attestation=att.raw_attestation, logical_operation_id=logical_operation_id,
        ))
        outcome = run(enforce_authority(
            stack.service, issued=issued, actor=ACTOR, resource=DEMO_REPO, action=ACTION,
            attestation=att.raw_attestation,
        ))
        assert outcome.status == "EXECUTED"

        issues = recorded_issues()
        assert len(issues) == 1
        sent = {"title": issues[0]["title"], "body": issues[0]["body"]}

        # The literal proof point: hash(exact outbound payload) == the real,
        # signed authorization's own payload_hash.
        assert hash_payload(sent) == issued.token["payload_hash"]
        assert logical_operation_marker(logical_operation_id) in sent["body"]


# ---------------------------------------------------------------------------
# Requirement 1 (b)/(c)/(d): title/body/marker mutation strictly AFTER a
# call was armed as verified/authorized must make the network call
# impossible -- exercised directly at the actuator boundary, recreating
# exactly the class of bug ``LogicalOperationMarkerActuator`` used to
# introduce (a wrapper mutating the payload downstream of verification).
# ---------------------------------------------------------------------------


def _armed_chain_and_original_payload(stack: LocalAstraDemoStack):
    verified = _build_actuator_chain(stack, authorized_resource=DEMO_REPO)
    original_payload = build_marked_payload(
        {"title": "Armed-and-verified issue", "body": "Original, authorized body."},
        logical_operation_id="op-tamper-boundary-1",
    )
    verified.expect(action=ACTION, payload_hash=hash_payload(original_payload))
    return verified, original_payload


def test_title_mutation_after_arming_blocked_before_network_call():
    with LocalAstraDemoStack(demo_repo=DEMO_REPO) as stack:
        verified, original_payload = _armed_chain_and_original_payload(stack)
        tampered = dict(original_payload)
        tampered["title"] = "TAMPERED TITLE — never authorized"

        with pytest.raises(PayloadBindingError):
            run(verified(ACTION, tampered))
        assert recorded_issues() == []


def test_body_mutation_after_arming_blocked_before_network_call():
    with LocalAstraDemoStack(demo_repo=DEMO_REPO) as stack:
        verified, original_payload = _armed_chain_and_original_payload(stack)
        tampered = dict(original_payload)
        tampered["body"] = tampered["body"] + "\n\nTAMPERED APPEND — never authorized"

        with pytest.raises(PayloadBindingError):
            run(verified(ACTION, tampered))
        assert recorded_issues() == []


def test_marker_addition_after_arming_blocked_before_network_call():
    """Recreates exactly the historical defect: a wrapper appending the
    logical-operation marker to an ALREADY-armed/verified payload. This is
    the specific pattern ``LogicalOperationMarkerActuator`` used to apply
    downstream of Gate verification -- it must now be refused before any
    network call, not merely produce a mismatched audit trail."""
    with LocalAstraDemoStack(demo_repo=DEMO_REPO) as stack:
        verified, original_payload = _armed_chain_and_original_payload(stack)
        # original_payload already carries its own marker; simulate a SECOND,
        # independently-appended marker being tacked on after arming.
        mutated = build_marked_payload(original_payload, logical_operation_id="op-injected-later")

        with pytest.raises(PayloadBindingError):
            run(verified(ACTION, mutated))
        assert recorded_issues() == []


def test_marker_removal_after_arming_blocked_before_network_call():
    with LocalAstraDemoStack(demo_repo=DEMO_REPO) as stack:
        verified, original_payload = _armed_chain_and_original_payload(stack)
        stripped = dict(original_payload)
        stripped["body"] = "Original, authorized body."  # marker stripped out

        with pytest.raises(PayloadBindingError):
            run(verified(ACTION, stripped))
        assert recorded_issues() == []


def test_marker_content_change_after_arming_blocked_before_network_call():
    with LocalAstraDemoStack(demo_repo=DEMO_REPO) as stack:
        verified, _ = _armed_chain_and_original_payload(stack)
        changed = build_marked_payload(
            {"title": "Armed-and-verified issue", "body": "Original, authorized body."},
            logical_operation_id="op-DIFFERENT-id-entirely",
        )

        with pytest.raises(PayloadBindingError):
            run(verified(ACTION, changed))
        assert recorded_issues() == []


# ---------------------------------------------------------------------------
# Requirement 1 (e): destination mismatch still prevents network invocation
# -- proven again here, alongside the payload-binding proofs, at the same
# actuator-chain boundary (Round 17 scenario 20 covers this independently;
# this is the SAME guarantee, re-verified as part of this final-boundary
# suite so the whole boundary is proven together).
# ---------------------------------------------------------------------------


def test_destination_mismatch_blocked_before_network_call():
    with LocalAstraDemoStack(demo_repo=DEMO_REPO) as stack:
        raw = GitHubIssueActuator(_live_config(stack))
        bound = ResourceBoundActuator(raw, authorized_resource="owner/a-DIFFERENT-unauthorized-repo")
        verified = VerifiedFinalPayloadActuator(bound)
        payload = build_marked_payload(
            {"title": "t", "body": "b"}, logical_operation_id="op-destination-mismatch-1",
        )
        verified.expect(action=ACTION, payload_hash=hash_payload(payload))

        with pytest.raises(ResourceBindingError):
            run(verified(ACTION, payload))
        assert recorded_issues() == []


# ---------------------------------------------------------------------------
# Requirement 1: never-armed calls fail closed too (no "unchecked assertion"
# that only fires when tampered with -- a call that never presented an
# expectation at all is refused identically).
# ---------------------------------------------------------------------------


def test_unarmed_call_blocked_before_network_call():
    with LocalAstraDemoStack(demo_repo=DEMO_REPO) as stack:
        verified = _build_actuator_chain(stack, authorized_resource=DEMO_REPO)
        payload = build_marked_payload({"title": "t", "body": "b"}, logical_operation_id="op-never-armed")

        with pytest.raises(PayloadBindingError):
            run(verified(ACTION, payload))
        assert recorded_issues() == []


def test_action_mismatch_after_arming_blocked_before_network_call():
    with LocalAstraDemoStack(demo_repo=DEMO_REPO) as stack:
        verified, original_payload = _armed_chain_and_original_payload(stack)

        with pytest.raises(PayloadBindingError):
            run(verified("some_other_action", original_payload))
        assert recorded_issues() == []


# ---------------------------------------------------------------------------
# Requirement 2: two distinct, in-scope logical operations reaching the
# SAME shared actuator instance never leak a marker/expectation from one
# into the other.
# ---------------------------------------------------------------------------


def test_two_operations_through_shared_actuator_no_context_leak():
    """Recreates the exact structural shape of ``cli.py``'s
    ``run_autonomous_expansion`` bug -- ONE actuator instance reused across
    TWO governed calls -- except both operations here are genuinely in
    scope and BOTH reach the real actuator (unlike ``run_autonomous_expansion``,
    where the second call is denied by mandate scope before ever reaching
    it). Proves: operation A's created issue carries marker A only; operation
    B's created issue carries marker B only; each outbound payload's hash is
    bound to its OWN verified authorization, never the other's."""
    with LocalAstraDemoStack(demo_repo=DEMO_REPO) as stack:
        shared_verified = _build_actuator_chain(stack, authorized_resource=DEMO_REPO)
        stack.upstream = shared_verified

        op_a_id = "op-shared-actuator-A"
        op_b_id = "op-shared-actuator-B"

        proposal_a = AstraProposal(action=ACTION, resource=DEMO_REPO,
                                   payload={"title": "Operation A", "body": "Body A."})
        proposal_b = AstraProposal(action=ACTION, resource=DEMO_REPO,
                                   payload={"title": "Operation B", "body": "Body B."})

        async def _run(proposal, logical_operation_id):
            marked = prepare_marked_call(
                proposal, logical_operation_id=logical_operation_id,
                canonical_payload_fn=stack.profiles.for_action(proposal.action).canonical_payload,
                actuator=shared_verified,
            )
            canonical = stack.profiles.for_action(marked.action).canonical_payload(marked.payload)
            att = await obtain_attestation(stack.attester, proposal=marked, canonical_payload=canonical)
            issued = await issue_authority(
                stack.service, mandate=stack.mandate, actor=ACTOR, proposal=marked,
                attestation=att.raw_attestation, logical_operation_id=logical_operation_id,
            )
            outcome = await enforce_authority(
                stack.service, issued=issued, actor=ACTOR, resource=DEMO_REPO, action=ACTION,
                attestation=att.raw_attestation,
            )
            return issued, outcome

        issued_a, outcome_a = run(_run(proposal_a, op_a_id))
        assert outcome_a.status == "EXECUTED"
        issued_b, outcome_b = run(_run(proposal_b, op_b_id))
        assert outcome_b.status == "EXECUTED"

        issues = recorded_issues()
        assert len(issues) == 2
        issue_a, issue_b = issues[0], issues[1]

        marker_a, marker_b = logical_operation_marker(op_a_id), logical_operation_marker(op_b_id)

        # No cross-contamination in either direction.
        assert marker_a in issue_a["body"] and marker_b not in issue_a["body"]
        assert marker_b in issue_b["body"] and marker_a not in issue_b["body"]

        # Each outbound payload's hash is bound to its OWN authorization only.
        sent_a = {"title": issue_a["title"], "body": issue_a["body"]}
        sent_b = {"title": issue_b["title"], "body": issue_b["body"]}
        assert hash_payload(sent_a) == issued_a.token["payload_hash"]
        assert hash_payload(sent_b) == issued_b.token["payload_hash"]
        assert issued_a.token["payload_hash"] != issued_b.token["payload_hash"]
        assert hash_payload(sent_a) != issued_b.token["payload_hash"]
        assert hash_payload(sent_b) != issued_a.token["payload_hash"]
