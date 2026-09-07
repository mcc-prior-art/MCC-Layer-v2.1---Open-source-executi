"""Round 24 hardening — independent review of the Round 23 commit
(a4c4a32c7e13fd5a3d463d27450be26588cf3c75) reproduced four additional,
genuinely exploitable gaps in the GPT-6 Astra reference integration's own
code (as opposed to two others describing direct, undocumented bypass of
the reference integration's protected boundary by calling the
domain-neutral ``mcc_core``/``gateway`` layer directly -- never claimed
protected, and left as-is per the explicit Round 21 instruction to keep
GitHub-specific rules out of domain-neutral MCC-Core). This file proves,
with live reproductions matching exactly what the review demonstrated, that
each of the four is closed.

1. **TOCTOU via a mutable payload dict.** ``pipeline.enforce_authority``
   used the caller's own payload object, by reference, across several
   ``await`` points inside ``coordinator.enforce`` (idempotency reservation,
   velocity, audit) between the Gate's verification and the actual
   dispatch. A concurrent mutation of that SAME object during the window
   let a stale, never-consumed ``VerifiedDispatchSlot`` expectation from an
   unrelated operation accept content it was never armed for. Fixed by
   deep-copying the payload into a private snapshot BEFORE the first await.
2. **Resource binding not tied to the current token.** ``ResourceBoundActuator``
   only ever compared two values fixed at construction time against each
   other (the slot's own ``authorized_resource`` vs. the raw actuator's
   configured repo) -- never the CURRENT call's actual authorized resource.
   A genuinely signed token naming a different resource than the one the
   slot happened to be built for could still dispatch to the actuator's
   fixed destination. Fixed by binding ``VerifiedFinalPayloadActuator`` to
   the current call's resource too, verified every dispatch.
3. **Reconciliation resolved on marker+repo alone.** A candidate issue
   whose CONTENT never hashed to the authorized ``payload_hash`` could
   still resolve UNKNOWN/DISPATCH_OWNED -> EXECUTED, as long as its marker
   and repository matched. Fixed by hashing the candidate's own reported
   title/body and requiring it to equal ``payload_hash``.
4. **Reconciliation could never match real GitHub data.** The real GitHub
   REST API reports an issue's repository via ``repository_url``, never a
   bare ``repo`` field (that is this package's own mock service's
   convenience shape) -- so reconciliation's repository check could never
   succeed against genuine GitHub data. Fixed by recognizing both shapes.
"""

from __future__ import annotations

import asyncio

import pytest

from mcc_core import IdempotencyState
from mcc_core.signing import hash_document, hash_payload

from examples.gpt6_astra_reference._localstack import ACTION, ACTOR, LocalAstraDemoStack
from examples.gpt6_astra_reference.github_actuator import (
    GitHubActuatorConfig,
    GitHubIssueActuator,
    PayloadBindingError,
    ResourceBindingError,
    VerifiedDispatchSlot,
)
from examples.gpt6_astra_reference.issue_contract import (
    logical_operation_marker,
    prepare_complete_github_issue_payload,
)
from examples.gpt6_astra_reference import mock_github_service
from examples.gpt6_astra_reference.mock_github_service import recorded_issues
from examples.gpt6_astra_reference.models import AstraProposal
from examples.gpt6_astra_reference.pipeline import (
    IssuedAuthority, enforce_authority, issue_authority, obtain_attestation,
)
from examples.gpt6_astra_reference.reconciliation import (
    _issue_repository_identity, reconcile_github_issue_operation,
)

run = asyncio.run
DEMO_REPO = "owner/mcc-astra-demo-sandbox"


def _live_config(stack: LocalAstraDemoStack) -> GitHubActuatorConfig:
    return GitHubActuatorConfig.from_env({
        "MCC_ASTRA_DEMO_MODE": "live",
        "MCC_ASTRA_GITHUB_REPO": stack.demo_repo,
        "MCC_ASTRA_GITHUB_BASE_URL": stack.github_base_url,
    })


# ---------------------------------------------------------------------------
# Fix 1 — payload snapshotted before the first await; a concurrent mutation
# of the caller's own dict during coordinator.enforce's admission sequence
# can no longer change what actually gets verified/dispatched.
# ---------------------------------------------------------------------------


def test_payload_mutation_during_await_window_cannot_smuggle_stale_content():
    """Recreates the exact reported exploit: leave the slot armed (but
    never consumed) for operation A; start enforcement of a genuinely
    signed token for operation B built on a caller-held mutable dict; while
    enforcement is suspended mid-admission (inside idempotency.reserve),
    mutate that SAME dict back to A's content. Before the Round 24 fix this
    produced EXECUTED with A's content actually sent under B's token/audit
    trail. After the fix: the Gate/coordinator operate on a private,
    already-frozen snapshot taken before any await, so the later mutation
    has no effect on what is verified or dispatched -- the stale slot (A)
    correctly refuses B's (unmutated) content, fail-closed."""
    with LocalAstraDemoStack(demo_repo=DEMO_REPO) as stack:
        raw = GitHubIssueActuator(_live_config(stack))
        slot = VerifiedDispatchSlot(raw, authorized_resource=DEMO_REPO)
        stack.upstream = slot

        payload_a = prepare_complete_github_issue_payload({"title": "A", "body": "bodyA"}, logical_operation_id="op-toctou-A")
        slot.expect(action=ACTION, resource=DEMO_REPO, payload_hash=hash_payload(payload_a))  # armed, never consumed

        payload_b = prepare_complete_github_issue_payload({"title": "B", "body": "bodyB"}, logical_operation_id="op-toctou-B")
        canonical_b = dict(payload_b)
        token_b = stack.engine.issue_token(
            verdict="ALLOW", subject=ACTOR, action=ACTION, payload=canonical_b,
            actor_id=ACTOR, resource_id=DEMO_REPO, auth_claims={}, idempotency_key="op-toctou-B",
        )
        issued_b = IssuedAuthority(token=token_b, canonical_payload=canonical_b, evidence_digest=None)

        real_reserve = stack.coordinator.idempotency.reserve

        async def mutating_reserve(*args, **kwargs):
            canonical_b.clear()
            canonical_b.update(payload_a)  # attempt to smuggle A's content into B's dispatch
            return await real_reserve(*args, **kwargs)

        stack.coordinator.idempotency.reserve = mutating_reserve

        outcome = run(enforce_authority(
            stack.service, issued=issued_b, actor=ACTOR, resource=DEMO_REPO, action=ACTION, attestation=None,
        ))
        assert outcome.status != "EXECUTED"
        assert recorded_issues() == []


def test_frozen_snapshot_does_not_break_the_normal_golden_path():
    """Positive control: an UNMUTATED, correctly-armed call still executes
    normally and dispatches the exact authorized content -- the freeze is
    transparent to honest callers."""
    with LocalAstraDemoStack(demo_repo=DEMO_REPO) as stack:
        raw = GitHubIssueActuator(_live_config(stack))
        slot = VerifiedDispatchSlot(raw, authorized_resource=DEMO_REPO)
        stack.upstream = slot

        payload = prepare_complete_github_issue_payload({"title": "t", "body": "b"}, logical_operation_id="op-toctou-control")
        token = stack.engine.issue_token(
            verdict="ALLOW", subject=ACTOR, action=ACTION, payload=payload,
            actor_id=ACTOR, resource_id=DEMO_REPO, auth_claims={}, idempotency_key="op-toctou-control",
        )
        issued = IssuedAuthority(token=token, canonical_payload=payload, evidence_digest=None)
        slot.expect(action=ACTION, resource=DEMO_REPO, payload_hash=hash_payload(payload))

        outcome = run(enforce_authority(
            stack.service, issued=issued, actor=ACTOR, resource=DEMO_REPO, action=ACTION, attestation=None,
        ))
        assert outcome.status == "EXECUTED"
        issues = recorded_issues()
        assert len(issues) == 1
        sent = {"title": issues[0]["title"], "body": issues[0]["body"]}
        assert hash_payload(sent) == token["payload_hash"]


# ---------------------------------------------------------------------------
# Fix 2 — VerifiedFinalPayloadActuator/VerifiedDispatchSlot bind to the
# CURRENT call's resource (from the real armed expectation), not merely
# whatever the slot happened to be constructed with.
# ---------------------------------------------------------------------------


def test_resource_binding_rejects_a_token_for_a_different_resource_than_the_slot():
    """The slot/actuator are built for REPO_A (matching, unremarkably); a
    genuinely signed token names REPO_B. Before the Round 24 fix this still
    dispatched to REPO_A. After: refused before the network call."""
    repo_a = DEMO_REPO
    repo_b = "owner/some-other-repo-entirely"
    with LocalAstraDemoStack(demo_repo=repo_a) as stack:
        raw = GitHubIssueActuator(_live_config(stack))
        slot = VerifiedDispatchSlot(raw, authorized_resource=repo_a)
        stack.upstream = slot

        payload = prepare_complete_github_issue_payload({"title": "t", "body": "b"}, logical_operation_id="op-resource-bind-1")
        token = stack.engine.issue_token(
            verdict="ALLOW", subject=ACTOR, action=ACTION, payload=payload,
            actor_id=ACTOR, resource_id=repo_b, auth_claims={}, idempotency_key="op-resource-bind-1",
        )
        issued = IssuedAuthority(token=token, canonical_payload=payload, evidence_digest=None)
        slot.expect(action=ACTION, resource=repo_b, payload_hash=hash_payload(payload))

        outcome = run(enforce_authority(
            stack.service, issued=issued, actor=ACTOR, resource=repo_b, action=ACTION, attestation=None,
        ))
        assert outcome.status != "EXECUTED"
        assert recorded_issues() == []


def test_verified_final_payload_actuator_raises_resource_binding_error_directly():
    """Unit-level: arming with a resource that doesn't match the raw
    actuator's configured destination raises ResourceBindingError directly
    from the boundary check, before any network call."""
    with LocalAstraDemoStack(demo_repo=DEMO_REPO) as stack:
        raw = GitHubIssueActuator(_live_config(stack))
        slot = VerifiedDispatchSlot(raw, authorized_resource=DEMO_REPO)
        payload = prepare_complete_github_issue_payload({"title": "t", "body": "b"}, logical_operation_id="op-resource-bind-2")
        slot.expect(action=ACTION, resource="owner/mismatched-repo", payload_hash=hash_payload(payload))

        with pytest.raises(ResourceBindingError):
            run(slot(ACTION, payload))
        assert recorded_issues() == []


def test_resource_binding_still_passes_for_the_matching_case():
    """Positive control: resource correctly matches the actuator's real
    configured destination -- dispatch proceeds normally."""
    with LocalAstraDemoStack(demo_repo=DEMO_REPO) as stack:
        raw = GitHubIssueActuator(_live_config(stack))
        slot = VerifiedDispatchSlot(raw, authorized_resource=DEMO_REPO)
        payload = prepare_complete_github_issue_payload({"title": "t", "body": "b"}, logical_operation_id="op-resource-bind-3")
        slot.expect(action=ACTION, resource=DEMO_REPO, payload_hash=hash_payload(payload))

        result = run(slot(ACTION, payload))
        assert result is not None
        assert len(recorded_issues()) == 1


# ---------------------------------------------------------------------------
# Fix 3 — reconciliation hashes the candidate's own reported content and
# requires it to equal the authorized payload_hash.
# ---------------------------------------------------------------------------


async def _park_operation_unknown(stack, *, op_id, title, body):
    """Admits and durably dispatch-owns a logical operation, then leaves it
    at UNKNOWN without ever actually calling any actuator -- models a lost
    response/crash, exactly like the existing Round 17/18 reconciliation
    tests. Returns the real, signed token."""
    payload = prepare_complete_github_issue_payload({"title": title, "body": body}, logical_operation_id=op_id)
    proposal = AstraProposal(action=ACTION, resource=DEMO_REPO, payload=payload)
    canonical = stack.profiles.for_action(ACTION).canonical_payload(payload)
    att = await obtain_attestation(stack.attester, proposal=proposal, canonical_payload=canonical)
    issued = await issue_authority(
        stack.service, mandate=stack.mandate, actor=ACTOR, proposal=proposal,
        attestation=att.raw_attestation, logical_operation_id=op_id,
    )
    binding_ref = hash_document({
        "action": issued.token["action"], "resource": issued.token["resource_id"],
        "payload_hash": issued.token["payload_hash"],
    })
    reserved = await stack.coordinator.idempotency.reserve(op_id, binding=binding_ref)
    await stack.coordinator.idempotency.commit_dispatch(op_id, fence=reserved.fence)
    await stack.coordinator.idempotency.mark_unknown(op_id, fence=reserved.fence)
    record = await stack.coordinator.idempotency.get_state(op_id)
    return issued, record


def test_reconciliation_rejects_candidate_with_wrong_content_even_with_right_marker_and_repo():
    with LocalAstraDemoStack(demo_repo=DEMO_REPO) as stack:
        op_id = "op-recon-content-1"
        issued, record = run(_park_operation_unknown(
            stack, op_id=op_id, title="AUTHORIZED TITLE", body="authorized body",
        ))
        forged_body = f"NOTHING TO DO WITH THE REAL PAYLOAD\n\n{logical_operation_marker(op_id)}"
        mock_github_service._STATE.create("owner", "mcc-astra-demo-sandbox", "COMPLETELY DIFFERENT TITLE", forged_body)

        outcome = run(reconcile_github_issue_operation(
            idempotency=stack.coordinator.idempotency, token=issued.token,
            expected_generation=record.generation, base_url=stack.github_base_url,
            actuator_repo=stack.demo_repo,
        ))
        assert not outcome.found
        assert not outcome.applied
        assert "content" in outcome.reason.lower()
        still = run(stack.coordinator.idempotency.get_state(op_id))
        assert still.state == IdempotencyState.UNKNOWN


def test_reconciliation_accepts_candidate_whose_content_matches_exactly():
    """Positive control: the real fix does not break the honest case --
    when the candidate's reported content genuinely hashes to the
    authorized payload_hash, reconciliation still resolves normally."""
    with LocalAstraDemoStack(demo_repo=DEMO_REPO) as stack:
        op_id = "op-recon-content-2"
        title, body_prefix = "AUTHORIZED TITLE 2", "authorized body 2"
        issued, record = run(_park_operation_unknown(stack, op_id=op_id, title=title, body=body_prefix))
        # The exact content the coordinator actually authorized (marker included).
        authorized_body = issued.canonical_payload["body"]
        mock_github_service._STATE.create("owner", "mcc-astra-demo-sandbox", title, authorized_body)

        outcome = run(reconcile_github_issue_operation(
            idempotency=stack.coordinator.idempotency, token=issued.token,
            expected_generation=record.generation, base_url=stack.github_base_url,
            actuator_repo=stack.demo_repo,
        ))
        assert outcome.found and outcome.applied
        resolved = run(stack.coordinator.idempotency.get_state(op_id))
        assert resolved.state == IdempotencyState.EXECUTED


# ---------------------------------------------------------------------------
# Fix 4 — reconciliation recognizes the real GitHub REST API's
# repository_url shape, not only this package's mock "repo" field.
# ---------------------------------------------------------------------------


def test_issue_repository_identity_recognizes_mock_shape():
    assert _issue_repository_identity({"repo": "owner/repo-a"}) == "owner/repo-a"


def test_issue_repository_identity_recognizes_real_github_repository_url_shape():
    assert _issue_repository_identity({
        "repository_url": "https://api.github.com/repos/owner/repo-a",
    }) == "owner/repo-a"


def test_issue_repository_identity_returns_none_for_neither_shape():
    assert _issue_repository_identity({"number": 1, "title": "t"}) is None


def test_reconciliation_resolves_candidate_reported_only_via_repository_url():
    """End-to-end: a candidate carrying ONLY the real GitHub REST API's
    repository_url field (no mock-specific "repo" field at all) is still
    correctly recognized and resolves the operation."""
    with LocalAstraDemoStack(demo_repo=DEMO_REPO) as stack:
        op_id = "op-recon-repo-url-1"
        title = "GITHUB-SHAPED ISSUE"
        issued, record = run(_park_operation_unknown(stack, op_id=op_id, title=title, body="x"))
        authorized_body = issued.canonical_payload["body"]

        # Inject a candidate directly, bypassing the mock's own create()
        # helper (which always adds "repo"), to reproduce the REAL GitHub
        # REST API's response shape exactly: repository_url, no repo field.
        mock_github_service._STATE.issues.append({
            "number": 9001,
            "title": title,
            "body": authorized_body,
            "html_url": "https://github.com/owner/mcc-astra-demo-sandbox/issues/9001",
            "repository_url": "https://api.github.com/repos/owner/mcc-astra-demo-sandbox",
            # deliberately no "repo" field
        })

        outcome = run(reconcile_github_issue_operation(
            idempotency=stack.coordinator.idempotency, token=issued.token,
            expected_generation=record.generation, base_url=stack.github_base_url,
            actuator_repo=stack.demo_repo,
        ))
        assert outcome.found and outcome.applied, outcome.reason
        resolved = run(stack.coordinator.idempotency.get_state(op_id))
        assert resolved.state == IdempotencyState.EXECUTED
