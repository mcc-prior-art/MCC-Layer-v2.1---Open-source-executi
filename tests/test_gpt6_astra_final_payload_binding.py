"""Round 19/21 surgical remediation — final outbound payload binding and
logical-operation context isolation, for the GPT-6 Astra reference
integration's ``create_github_issue`` action.

Round 20's independent re-verification (executing real
``DecisionEngine``/``ExecutionGate``/``EnforcementCoordinator``/actuator
code, not merely reading documentation) reproduced two remaining blocker
classes on top of Round 19's fix:

**Blocker 1 — payload projection after final hash verification.** A
proposal's payload could carry additional fields (e.g. ``labels``) that
generic canonicalization retained (so they were signed into the token and
checked by ``VerifiedFinalPayloadActuator``), but
``GitHubIssueActuator.__call__`` reconstructed a NEW ``{"title":..,
"body":..}`` object before POSTing -- silently dropping any other
authorized field. The payload actually sent to GitHub could therefore
differ from the payload that was cryptographically verified, even though
the object ``VerifiedFinalPayloadActuator`` itself checked was correct.

**Blocker 2 — operation id and marker not enforced as one context.** (A) An
input body already containing a marker, followed by a second marker being
appended for a different operation, could leave a request executing with
BOTH markers. (B) A payload prepared with marker A, but a genuine token
issued with a DIFFERENT ``idempotency_key`` (durable admission identity) B,
could still pass the Gate's own hash check (which only proves the payload
matches the token's ``payload_hash`` -- it says nothing about which
operation the payload's own marker names) and reach the actuator with the
wrong marker attached to the wrong operation's dispatch/result identity.

This file proves, at the ACTUAL outbound actuator/network boundary and
(where the requirement specifically calls for it) through the REAL local
authorization/Gate/coordinator path and the actual mock GitHub HTTP
receiver -- never merely a token-vs-registry comparison, a helper-level
hash, or a before-the-Gate denial -- that both blocker classes are closed.
"""

from __future__ import annotations

import asyncio
import json

import pytest

from mcc_core import IdempotencyState
from mcc_core.signing import hash_payload

from examples.gpt6_astra_reference._localstack import ACTION, ACTOR, LocalAstraDemoStack
from examples.gpt6_astra_reference.github_actuator import (
    GitHubActuatorConfig,
    GitHubIssueActuator,
    GitHubIssuePayloadError,
    LOGICAL_OPERATION_MARKER_PREFIX,
    MarkerSyntaxError,
    OperationContextMismatchError,
    PayloadBindingError,
    ResourceBindingError,
    VerifiedDispatchSlot,
    build_marked_payload,
    logical_operation_marker,
)
from examples.gpt6_astra_reference.governed_call import prepare_marked_call
from examples.gpt6_astra_reference.issue_contract import prepare_complete_github_issue_payload
from examples.gpt6_astra_reference.mock_github_service import recorded_issues
from examples.gpt6_astra_reference.models import AstraProposal
from examples.gpt6_astra_reference.pipeline import (
    IssuedAuthority, enforce_authority, issue_authority, obtain_attestation, run_positive_path,
)

run = asyncio.run
DEMO_REPO = "owner/mcc-astra-demo-sandbox"


def _live_config(stack: LocalAstraDemoStack) -> GitHubActuatorConfig:
    return GitHubActuatorConfig.from_env({
        "MCC_ASTRA_DEMO_MODE": "live",
        "MCC_ASTRA_GITHUB_REPO": stack.demo_repo,
        "MCC_ASTRA_GITHUB_BASE_URL": stack.github_base_url,
    })


def _build_dispatch_slot(stack: LocalAstraDemoStack, *, authorized_resource: str) -> VerifiedDispatchSlot:
    """The exact chain ``cli.py``/``adversarial.py`` build in production:
    ``GitHubIssueActuator`` wrapped in a ``VerifiedDispatchSlot`` (which
    itself wraps a ``ResourceBoundActuator`` internally) -- the final safety
    net immediately before the real HTTP POST."""
    raw = GitHubIssueActuator(_live_config(stack))
    return VerifiedDispatchSlot(raw, authorized_resource=authorized_resource)


class _CountingUpstream:
    """Independent call counter, entirely separate from whatever MCC itself
    reports -- the dual-oracle side of every test below."""

    def __init__(self, actuator) -> None:
        self._actuator = actuator
        self.calls = 0

    def expect(self, *, action: str, payload_hash: str) -> None:
        self._actuator.expect(action=action, payload_hash=payload_hash)

    async def __call__(self, action: str, payload):
        self.calls += 1
        return await self._actuator(action, payload)


def _pre_actuation_audit_entries(stack: LocalAstraDemoStack) -> list:
    entries = []
    with open(stack._audit_path, "r", encoding="utf-8") as fh:
        for line in fh:
            if not line.strip():
                continue
            entry = json.loads(line)
            if entry.get("kind") == "pre_actuation":
                entries.append(entry)
    return entries


# ---------------------------------------------------------------------------
# Blocker 1 (a): capture the exact outbound HTTP payload through the REAL
# local authorization/Gate/coordinator path and the actual mock GitHub HTTP
# receiver; prove its canonical hash equals the real, signed token's
# payload_hash, and that the pre-actuation audit entry records the same
# hash.
# ---------------------------------------------------------------------------


def test_outbound_payload_hash_equals_verified_token_payload_hash_and_audit():
    """End-to-end through the real chain (attestation -> authority ->
    Gate -> coordinator -> the real actuator -> the mock GitHub service),
    never tampered. The mock service records exactly what was POSTed
    (``recorded_issues``) -- reconstructing that exact body/title and
    re-hashing it with the SAME ``hash_payload`` the Gate used must equal
    ``issued.token["payload_hash"]`` byte-for-byte, and the coordinator's
    OWN pre-actuation audit entry (written before any external call) must
    record that identical hash."""
    with LocalAstraDemoStack(demo_repo=DEMO_REPO) as stack:
        logical_operation_id = "op-final-binding-proof-1"
        slot = _build_dispatch_slot(stack, authorized_resource=DEMO_REPO)
        counting = _CountingUpstream(slot)
        stack.upstream = counting

        proposal = AstraProposal(
            action=ACTION, resource=DEMO_REPO,
            payload={"title": "Final-binding proof issue", "body": "Exact payload proof."},
        )
        marked_proposal = prepare_marked_call(
            proposal, logical_operation_id=logical_operation_id,
            canonical_payload_fn=stack.profiles.for_action(proposal.action).canonical_payload,
            actuator=counting,
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
        assert counting.calls == 1

        issues = recorded_issues()
        assert len(issues) == 1
        sent = {"title": issues[0]["title"], "body": issues[0]["body"]}

        # The literal proof point: hash(exact outbound payload) == the real,
        # signed authorization's own payload_hash.
        assert hash_payload(sent) == issued.token["payload_hash"]
        assert logical_operation_marker(logical_operation_id) in sent["body"]

        # The pre-actuation audit entry (written before the actuator was
        # ever called) records that identical payload_hash.
        pre_actuation = _pre_actuation_audit_entries(stack)
        assert len(pre_actuation) == 1
        assert pre_actuation[0]["payload_hash"] == issued.token["payload_hash"]
        assert pre_actuation[0]["idempotency_key"] == logical_operation_id

        record = run(stack.coordinator.idempotency.get_state(logical_operation_id))
        assert record.state == IdempotencyState.EXECUTED


# ---------------------------------------------------------------------------
# Blocker 1 (b)/(c): unsupported field ("labels") / invalid title-or-body
# type rejected BEFORE token issuance, zero POST invocations -- both via the
# normal preparation helper AND independently at the pipeline boundary
# (a direct caller that skips ``prepare_marked_call`` cannot bypass it).
# ---------------------------------------------------------------------------


def test_labels_field_rejected_before_token_issuance_via_prepare_marked_call():
    with LocalAstraDemoStack(demo_repo=DEMO_REPO) as stack:
        counting = _CountingUpstream(_build_dispatch_slot(stack, authorized_resource=DEMO_REPO))
        stack.upstream = counting
        proposal = AstraProposal(
            action=ACTION, resource=DEMO_REPO,
            payload={"title": "t", "body": "b", "labels": ["bug", "urgent"]},
        )
        with pytest.raises(GitHubIssuePayloadError):
            prepare_marked_call(
                proposal, logical_operation_id="op-labels-1",
                canonical_payload_fn=stack.profiles.for_action(ACTION).canonical_payload,
                actuator=counting,
            )
        assert counting.calls == 0
        assert recorded_issues() == []


def test_run_positive_path_rejects_unsupported_field_even_bypassing_prepare_marked_call():
    """Requirement: direct callers must not bypass validation by skipping
    the preparation helper. A payload with an unsupported field, presented
    directly to ``run_positive_path`` (never routed through
    ``prepare_marked_call``), is refused independently, before any
    attestation/authority/gate call -- and before token issuance."""
    with LocalAstraDemoStack(demo_repo=DEMO_REPO) as stack:
        counting = _CountingUpstream(_build_dispatch_slot(stack, authorized_resource=DEMO_REPO))
        stack.upstream = counting
        marked_body = build_marked_payload({"title": "t", "body": "b"}, logical_operation_id="op-bypass-labels")
        marked_body["labels"] = ["bug"]  # an unsupported field tacked on directly
        proposal = AstraProposal(action=ACTION, resource=DEMO_REPO, payload=marked_body)
        with pytest.raises(GitHubIssuePayloadError):
            run(run_positive_path(
                stack.service, mandate=stack.mandate, actor=ACTOR, proposal=proposal, attestation=None,
                logical_operation_id="op-bypass-labels",
            ))
        assert counting.calls == 0
        assert recorded_issues() == []


@pytest.mark.parametrize("bad_payload", [
    {"title": 12345, "body": "b"},
    {"body": "b"},
    {"title": "", "body": "b"},
    {"title": "   ", "body": "b"},
    {"title": "t", "body": 12345},
])
def test_invalid_title_or_body_type_rejected_before_token_issuance(bad_payload):
    with LocalAstraDemoStack(demo_repo=DEMO_REPO) as stack:
        counting = _CountingUpstream(_build_dispatch_slot(stack, authorized_resource=DEMO_REPO))
        stack.upstream = counting
        proposal = AstraProposal(action=ACTION, resource=DEMO_REPO, payload=bad_payload)
        with pytest.raises(GitHubIssuePayloadError):
            prepare_marked_call(
                proposal, logical_operation_id="op-bad-type",
                canonical_payload_fn=stack.profiles.for_action(ACTION).canonical_payload,
                actuator=counting,
            )
        assert counting.calls == 0
        assert recorded_issues() == []


def test_body_optional_default_materialized_before_binding():
    prepared = prepare_complete_github_issue_payload({"title": "t"}, logical_operation_id="op-default-body-1")
    assert prepared["title"] == "t"
    assert logical_operation_marker("op-default-body-1") in prepared["body"]
    # The materialized default is "" -- the marker is appended to nothing else.
    assert prepared["body"] == f"\n\n{logical_operation_marker('op-default-body-1')}"


# ---------------------------------------------------------------------------
# Blocker 1 (d): title/body/marker mutation strictly AFTER a call was armed
# as verified/authorized must make the network call impossible -- exercised
# directly at the actuator boundary, recreating exactly the class of bug
# the old field-projecting ``GitHubIssueActuator``/mutating marker actuator
# used to permit.
# ---------------------------------------------------------------------------


def _armed_slot_and_original_payload(stack: LocalAstraDemoStack):
    slot = _build_dispatch_slot(stack, authorized_resource=DEMO_REPO)
    original_payload = build_marked_payload(
        {"title": "Armed-and-verified issue", "body": "Original, authorized body."},
        logical_operation_id="op-tamper-boundary-1",
    )
    slot.expect(action=ACTION, payload_hash=hash_payload(original_payload))
    return slot, original_payload


def test_title_mutation_after_arming_blocked_before_network_call():
    with LocalAstraDemoStack(demo_repo=DEMO_REPO) as stack:
        slot, original_payload = _armed_slot_and_original_payload(stack)
        tampered = dict(original_payload)
        tampered["title"] = "TAMPERED TITLE — never authorized"

        with pytest.raises(PayloadBindingError):
            run(slot(ACTION, tampered))
        assert recorded_issues() == []


def test_body_mutation_after_arming_blocked_before_network_call():
    with LocalAstraDemoStack(demo_repo=DEMO_REPO) as stack:
        slot, original_payload = _armed_slot_and_original_payload(stack)
        tampered = dict(original_payload)
        tampered["body"] = tampered["body"] + "\n\nTAMPERED APPEND — never authorized"

        with pytest.raises(PayloadBindingError):
            run(slot(ACTION, tampered))
        assert recorded_issues() == []


def test_marker_addition_after_arming_blocked_before_network_call():
    """Recreates exactly the historical defect: a wrapper appending a
    SECOND logical-operation marker to an ALREADY-armed/verified payload.
    Must be refused before any network call, not merely produce a
    mismatched audit trail."""
    with LocalAstraDemoStack(demo_repo=DEMO_REPO) as stack:
        slot, original_payload = _armed_slot_and_original_payload(stack)
        mutated = dict(original_payload)
        mutated["body"] = mutated["body"] + f"\n\n{logical_operation_marker('op-injected-later')}"

        with pytest.raises(PayloadBindingError):
            run(slot(ACTION, mutated))
        assert recorded_issues() == []


def test_marker_removal_after_arming_blocked_before_network_call():
    with LocalAstraDemoStack(demo_repo=DEMO_REPO) as stack:
        slot, original_payload = _armed_slot_and_original_payload(stack)
        stripped = dict(original_payload)
        stripped["body"] = "Original, authorized body."  # marker stripped out

        with pytest.raises(PayloadBindingError):
            run(slot(ACTION, stripped))
        assert recorded_issues() == []


def test_marker_replacement_after_arming_blocked_before_network_call():
    with LocalAstraDemoStack(demo_repo=DEMO_REPO) as stack:
        slot, _ = _armed_slot_and_original_payload(stack)
        replaced = build_marked_payload(
            {"title": "Armed-and-verified issue", "body": "Original, authorized body."},
            logical_operation_id="op-DIFFERENT-id-entirely",
        )

        with pytest.raises(PayloadBindingError):
            run(slot(ACTION, replaced))
        assert recorded_issues() == []


def test_action_mismatch_after_arming_blocked_before_network_call():
    with LocalAstraDemoStack(demo_repo=DEMO_REPO) as stack:
        slot, original_payload = _armed_slot_and_original_payload(stack)

        with pytest.raises(PayloadBindingError):
            run(slot("some_other_action", original_payload))
        assert recorded_issues() == []


def test_destination_mismatch_blocked_before_network_call():
    with LocalAstraDemoStack(demo_repo=DEMO_REPO) as stack:
        slot = VerifiedDispatchSlot(
            GitHubIssueActuator(_live_config(stack)), authorized_resource="owner/a-DIFFERENT-unauthorized-repo",
        )
        payload = build_marked_payload(
            {"title": "t", "body": "b"}, logical_operation_id="op-destination-mismatch-1",
        )
        slot.expect(action=ACTION, payload_hash=hash_payload(payload))

        with pytest.raises(ResourceBindingError):
            run(slot(ACTION, payload))
        assert recorded_issues() == []


def test_unarmed_call_blocked_before_network_call():
    with LocalAstraDemoStack(demo_repo=DEMO_REPO) as stack:
        slot = _build_dispatch_slot(stack, authorized_resource=DEMO_REPO)
        payload = build_marked_payload({"title": "t", "body": "b"}, logical_operation_id="op-never-armed")

        with pytest.raises(PayloadBindingError):
            run(slot(ACTION, payload))
        assert recorded_issues() == []


# ---------------------------------------------------------------------------
# Blocker 2 — reject a raw body that already contains a marker: matching,
# foreign, duplicate, and malformed variants. Rejected before authorization
# (build_marked_payload itself refuses); zero POST invocations end-to-end.
# ---------------------------------------------------------------------------


def _matching_marker_body(mid: str) -> str:
    return f"pre-existing text\n\n{logical_operation_marker(mid)}"


def _foreign_marker_body(mid: str) -> str:
    return f"pre-existing text\n\n{logical_operation_marker('some-completely-other-op')}"


def _duplicate_marker_body(mid: str) -> str:
    marker = logical_operation_marker(mid)
    return f"pre-existing text\n\n{marker}\n\n{marker}"


def _malformed_marker_body(mid: str) -> str:
    return f"pre-existing text {LOGICAL_OPERATION_MARKER_PREFIX}truncated-no-suffix-here"


@pytest.mark.parametrize("case,body_builder", [
    ("matching", _matching_marker_body),
    ("foreign", _foreign_marker_body),
    ("duplicate", _duplicate_marker_body),
    ("malformed", _malformed_marker_body),
])
def test_build_marked_payload_rejects_preexisting_marker_variants(case, body_builder):
    mid = "op-preexisting-marker-1"
    raw_payload = {"title": "t", "body": body_builder(mid)}
    with pytest.raises(MarkerSyntaxError):
        build_marked_payload(raw_payload, logical_operation_id=mid)


@pytest.mark.parametrize("case,body_builder", [
    ("matching", _matching_marker_body),
    ("foreign", _foreign_marker_body),
    ("duplicate", _duplicate_marker_body),
    ("malformed", _malformed_marker_body),
])
def test_preexisting_marker_variants_rejected_end_to_end_zero_post(case, body_builder):
    with LocalAstraDemoStack(demo_repo=DEMO_REPO) as stack:
        counting = _CountingUpstream(_build_dispatch_slot(stack, authorized_resource=DEMO_REPO))
        stack.upstream = counting
        mid = "op-preexisting-marker-e2e-1"
        proposal = AstraProposal(action=ACTION, resource=DEMO_REPO, payload={"title": "t", "body": body_builder(mid)})
        with pytest.raises(MarkerSyntaxError):
            prepare_marked_call(
                proposal, logical_operation_id=mid,
                canonical_payload_fn=stack.profiles.for_action(ACTION).canonical_payload,
                actuator=counting,
            )
        assert counting.calls == 0
        assert recorded_issues() == []


# ---------------------------------------------------------------------------
# Blocker 2 — prepare context A, then attempt authorization/admission as B:
# rejected at the protected boundary; zero POST invocations; no EXECUTED
# (or any) record ever created for B.
# ---------------------------------------------------------------------------


def test_prepare_context_a_then_present_as_b_rejected_at_protected_boundary():
    with LocalAstraDemoStack(demo_repo=DEMO_REPO) as stack:
        counting = _CountingUpstream(_build_dispatch_slot(stack, authorized_resource=DEMO_REPO))
        stack.upstream = counting

        proposal = AstraProposal(action=ACTION, resource=DEMO_REPO, payload={"title": "t", "body": "b"})
        marked_for_a = prepare_marked_call(
            proposal, logical_operation_id="op-context-A-1", actuator=None,
            canonical_payload_fn=stack.profiles.for_action(ACTION).canonical_payload,
        )
        canonical = stack.profiles.for_action(ACTION).canonical_payload(marked_for_a.payload)
        att = run(obtain_attestation(stack.attester, proposal=marked_for_a, canonical_payload=canonical))

        with pytest.raises(OperationContextMismatchError):
            run(run_positive_path(
                stack.service, mandate=stack.mandate, actor=ACTOR, proposal=marked_for_a,
                attestation=att.raw_attestation, logical_operation_id="op-context-B-1",
            ))
        assert counting.calls == 0
        assert recorded_issues() == []
        assert run(stack.coordinator.idempotency.get_state("op-context-B-1")) is None
        assert run(stack.coordinator.idempotency.get_state("op-context-A-1")) is None

        # issue_authority (the OTHER protected boundary) independently
        # refuses the identical mismatch too, before any token is issued.
        with pytest.raises(OperationContextMismatchError):
            run(issue_authority(
                stack.service, mandate=stack.mandate, actor=ACTOR, proposal=marked_for_a,
                attestation=att.raw_attestation, logical_operation_id="op-context-B-1",
            ))
        assert counting.calls == 0


# ---------------------------------------------------------------------------
# Blocker 2 counterexample B — a genuinely signed token for operation B,
# presented alongside a payload whose marker actually names operation A.
# The Gate's own hash check alone cannot catch this (the hash matches
# perfectly fine, since the token was minted directly from this exact
# payload); enforce_authority's OWN independent context check must.
# ---------------------------------------------------------------------------


def test_enforce_authority_rejects_context_mismatch_even_when_gate_hash_matches():
    with LocalAstraDemoStack(demo_repo=DEMO_REPO) as stack:
        counting = _CountingUpstream(_build_dispatch_slot(stack, authorized_resource=DEMO_REPO))
        stack.upstream = counting

        payload_marked_a = prepare_complete_github_issue_payload(
            {"title": "t", "body": "b"}, logical_operation_id="op-hash-match-A",
        )
        canonical = stack.profiles.for_action(ACTION).canonical_payload(payload_marked_a)

        # A REAL, genuinely signed token -- reaches the real Gate's
        # signature/trust verification exactly as any other token would --
        # minted with idempotency_key B directly from A's marked payload,
        # bypassing issue_authority's own coherence check on purpose (to
        # prove enforce_authority's check is independent of it, not merely
        # relying on issue_authority never producing such a token).
        token = stack.engine.issue_token(
            verdict="ALLOW", subject=ACTOR, action=ACTION, payload=canonical,
            actor_id=ACTOR, resource_id=DEMO_REPO, auth_claims={},
            idempotency_key="op-hash-match-B",
        )
        assert hash_payload(canonical) == token["payload_hash"]  # the Gate's own check would pass fine

        issued = IssuedAuthority(token=token, canonical_payload=canonical, evidence_digest=None)
        with pytest.raises(OperationContextMismatchError):
            run(enforce_authority(
                stack.service, issued=issued, actor=ACTOR, resource=DEMO_REPO, action=ACTION, attestation=None,
            ))
        assert counting.calls == 0
        assert recorded_issues() == []
        assert run(stack.coordinator.idempotency.get_state("op-hash-match-B")) is None


# ---------------------------------------------------------------------------
# Blocker 2 — two distinct, in-scope operations through ONE shared actuator:
# each carries only its own marker, each outbound hash binds only to its
# own token, and admission/audit/result identities match per operation.
# ---------------------------------------------------------------------------


def test_two_operations_through_shared_actuator_no_context_leak():
    """Recreates the exact structural shape of ``cli.py``'s
    ``run_autonomous_expansion`` bug -- ONE actuator instance reused across
    TWO governed calls -- except both operations here are genuinely in
    scope and BOTH reach the real actuator."""
    with LocalAstraDemoStack(demo_repo=DEMO_REPO) as stack:
        shared_slot = _build_dispatch_slot(stack, authorized_resource=DEMO_REPO)
        counting = _CountingUpstream(shared_slot)
        stack.upstream = counting

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
                actuator=counting,
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
        assert counting.calls == 2

        issues = recorded_issues()
        assert len(issues) == 2
        issue_a, issue_b = issues[0], issues[1]

        marker_a, marker_b = logical_operation_marker(op_a_id), logical_operation_marker(op_b_id)

        # No cross-contamination in either direction, exactly once each.
        assert issue_a["body"].count(marker_a) == 1 and marker_b not in issue_a["body"]
        assert issue_b["body"].count(marker_b) == 1 and marker_a not in issue_b["body"]

        # Each outbound payload's hash is bound to its OWN authorization only.
        sent_a = {"title": issue_a["title"], "body": issue_a["body"]}
        sent_b = {"title": issue_b["title"], "body": issue_b["body"]}
        assert hash_payload(sent_a) == issued_a.token["payload_hash"]
        assert hash_payload(sent_b) == issued_b.token["payload_hash"]
        assert issued_a.token["payload_hash"] != issued_b.token["payload_hash"]
        assert hash_payload(sent_a) != issued_b.token["payload_hash"]
        assert hash_payload(sent_b) != issued_a.token["payload_hash"]

        # Admission/result identity matches each operation independently.
        record_a = run(stack.coordinator.idempotency.get_state(op_a_id))
        record_b = run(stack.coordinator.idempotency.get_state(op_b_id))
        assert record_a.state == IdempotencyState.EXECUTED
        assert record_b.state == IdempotencyState.EXECUTED

        # Audit identity matches each operation independently too.
        pre_actuation = _pre_actuation_audit_entries(stack)
        assert len(pre_actuation) == 2
        by_key = {e["idempotency_key"]: e for e in pre_actuation}
        assert by_key[op_a_id]["payload_hash"] == issued_a.token["payload_hash"]
        assert by_key[op_b_id]["payload_hash"] == issued_b.token["payload_hash"]


# ---------------------------------------------------------------------------
# Blocker 2 — forgetting to (re-)arm a shared slot before a subsequent call
# fails closed, whether the PRIOR attempt succeeded or was blocked before
# ever reaching the actuator; and overlapping arm calls preserve whichever
# context is currently installed, never a stale one.
# ---------------------------------------------------------------------------


def test_forget_to_arm_after_successful_attempt_fails_closed():
    with LocalAstraDemoStack(demo_repo=DEMO_REPO) as stack:
        slot = _build_dispatch_slot(stack, authorized_resource=DEMO_REPO)
        payload1 = build_marked_payload({"title": "first", "body": "b"}, logical_operation_id="op-forget-1")
        slot.expect(action=ACTION, payload_hash=hash_payload(payload1))
        result1 = run(slot(ACTION, payload1))
        assert result1 is not None
        assert len(recorded_issues()) == 1

        # A SECOND, different operation forgets to (re-)arm before its own
        # dispatch attempt -- must fail closed, zero additional POSTs.
        payload2 = build_marked_payload({"title": "second", "body": "b"}, logical_operation_id="op-forget-2")
        with pytest.raises(PayloadBindingError):
            run(slot(ACTION, payload2))
        assert len(recorded_issues()) == 1  # unchanged


def test_forget_to_arm_after_blocked_attempt_fails_closed():
    """The armed-but-never-consumed case: an attempt is armed (as
    ``prepare_marked_call`` would do before a governed call), but the
    coordinator never actually dispatches to the actuator (modeling a
    Gate/authority denial upstream of this slot). A LATER, unrelated
    operation must not be able to dispatch through the resulting stale,
    unconsumed expectation just because it forgot to arm its own."""
    with LocalAstraDemoStack(demo_repo=DEMO_REPO) as stack:
        slot = _build_dispatch_slot(stack, authorized_resource=DEMO_REPO)
        payload1 = build_marked_payload({"title": "blocked", "body": "b"}, logical_operation_id="op-blocked-1")
        slot.expect(action=ACTION, payload_hash=hash_payload(payload1))
        # ... the attempt this was armed for is blocked upstream and never
        # reaches this slot at all (no call happens here).

        payload2 = build_marked_payload({"title": "second", "body": "b"}, logical_operation_id="op-blocked-2")
        with pytest.raises(PayloadBindingError):
            run(slot(ACTION, payload2))
        assert recorded_issues() == []


def test_overlapping_arm_preserves_latest_context_never_a_stale_one():
    """Two ``expect(...)`` calls happen back-to-back with no dispatch in
    between (modeling overlapping preparation). The slot preserves ONLY the
    latest invocation's context -- the earlier one is discarded and can
    never be dispatched to, never silently substituted for the later one."""
    with LocalAstraDemoStack(demo_repo=DEMO_REPO) as stack:
        slot = _build_dispatch_slot(stack, authorized_resource=DEMO_REPO)
        payload_a = build_marked_payload({"title": "A", "body": "b"}, logical_operation_id="op-overlap-A")
        payload_b = build_marked_payload({"title": "B", "body": "b"}, logical_operation_id="op-overlap-B")

        slot.expect(action=ACTION, payload_hash=hash_payload(payload_a))
        slot.expect(action=ACTION, payload_hash=hash_payload(payload_b))  # overlap: replaces A's context

        # A's own payload can no longer be dispatched -- its context was discarded.
        with pytest.raises(PayloadBindingError):
            run(slot(ACTION, payload_a))
        assert recorded_issues() == []

        # A fresh arm+dispatch with B's real payload succeeds normally.
        slot.expect(action=ACTION, payload_hash=hash_payload(payload_b))
        result = run(slot(ACTION, payload_b))
        assert result is not None
        issues = recorded_issues()
        assert len(issues) == 1
        assert logical_operation_marker("op-overlap-B") in issues[0]["body"]
        assert logical_operation_marker("op-overlap-A") not in issues[0]["body"]
