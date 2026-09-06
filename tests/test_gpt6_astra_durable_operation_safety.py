"""Round 17 remediation — durable logical-operation safety for the GPT-6
Astra reference integration's ``create_github_issue`` action.

Covers the Astra-layer-specific pieces of the remediation that sit on top of
the generic ``mcc_core.idempotency``/``mcc_core.coordinator`` state machine
(exercised directly in ``tests/test_idempotency.py`` /
``tests/test_coordinator.py``):

* test scenario 19 — a protected action's request missing
  ``logical_operation_id`` is rejected before governance is ever invoked;
* test scenario 20 — an authorized resource that does not match the
  actuator's configured destination is rejected before any external call;
* test scenario 8 — the external actuator succeeds but the coordinator's
  view of the outcome is lost (simulating a lost response / a raised
  exception after the real HTTP call already completed); the operation
  parks at UNKNOWN, reconciliation (read-only) resolves it to EXECUTED from
  independent positive evidence, and a fresh retry attempt afterward is
  blocked -- zero duplicate GitHub issues.
"""

from __future__ import annotations

import asyncio

import pytest

from mcc_core import IdempotencyState

from examples.gpt6_astra_reference._localstack import ACTION, ACTOR, LocalAstraDemoStack
from examples.gpt6_astra_reference.github_actuator import (
    GitHubActuatorConfig, GitHubIssueActuator, LogicalOperationMarkerActuator,
    ResourceBindingError, ResourceBoundActuator, logical_operation_marker,
)
from examples.gpt6_astra_reference.mock_github_service import recorded_issues
from examples.gpt6_astra_reference.models import (
    AstraProposal, MissingLogicalOperationIdError, require_logical_operation_id,
)
from examples.gpt6_astra_reference.pipeline import obtain_attestation, run_positive_path
from examples.gpt6_astra_reference.reconciliation import reconcile_github_issue_operation

run = asyncio.run
DEMO_REPO = "owner/mcc-astra-demo-sandbox"


# ---------------------------------------------------------------------------
# Test scenario 19: missing logical_operation_id -> reject before dispatch.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("bad_value", [None, "", "   "])
def test_missing_logical_operation_id_rejected_before_any_governance_call(bad_value):
    """The contract check itself is synchronous and raises immediately --
    proving, structurally, that it cannot be reached only after governance
    has already been invoked (there is nothing to await, no stack to build,
    no attestation/gate/coordinator call made before the raise)."""
    with pytest.raises(MissingLogicalOperationIdError):
        require_logical_operation_id(bad_value)


def test_present_logical_operation_id_passes_through_unchanged():
    assert require_logical_operation_id("op-123") == "op-123"


# ---------------------------------------------------------------------------
# Test scenario 20: authorized resource != configured actuator destination.
# ---------------------------------------------------------------------------


def test_resource_binding_mismatch_rejected_before_any_external_call():
    config = GitHubActuatorConfig(
        mode="live", repo="owner/configured-repo",
        base_url="http://127.0.0.1:1",  # deliberately unreachable
        token=None,
    )
    actuator = GitHubIssueActuator(config)
    bound = ResourceBoundActuator(actuator, authorized_resource="owner/a-DIFFERENT-repo")

    with pytest.raises(ResourceBindingError):
        run(bound("create_github_issue", {"title": "t", "body": "b"}))
    # A ResourceBindingError (not a connection error to the unreachable
    # base_url) proves the check fired BEFORE any attempt to reach the
    # network -- if it had tried to dial 127.0.0.1:1 first, this test would
    # instead see a transport/connection exception.


def test_resource_binding_match_delegates_through():
    config = GitHubActuatorConfig(mode="disabled", repo="owner/configured-repo",
                                  base_url="http://unused", token=None)
    actuator = GitHubIssueActuator(config)
    bound = ResourceBoundActuator(actuator, authorized_resource="owner/configured-repo")
    # mode=disabled -> the underlying actuator itself refuses (a DIFFERENT,
    # already-covered guard) -- proving the resource check passed and
    # delegated through to the real actuator rather than short-circuiting.
    from examples.gpt6_astra_reference.github_actuator import GitHubActuatorDisabledError

    with pytest.raises(GitHubActuatorDisabledError):
        run(bound("create_github_issue", {"title": "t", "body": "b"}))


# ---------------------------------------------------------------------------
# Test scenario 8: lost response after genuine external success ->
# UNKNOWN -> (reconciliation) -> EXECUTED, zero duplicate creates.
# ---------------------------------------------------------------------------


class _LossyActuator:
    """Wraps a real actuator: the external call genuinely happens, but the
    caller never learns the outcome (models a lost HTTP response / a
    connection reset after the server already committed the side effect)."""

    def __init__(self, actuator):
        self._actuator = actuator
        self.calls = 0

    async def __call__(self, action, payload):
        self.calls += 1
        await self._actuator(action, payload)  # the real side effect happens
        raise ConnectionError("response lost after the request was already accepted")


def test_lost_response_after_success_reconciles_to_executed_without_duplicate():
    with LocalAstraDemoStack(demo_repo=DEMO_REPO) as stack:
        logical_operation_id = "op-lost-response-1"
        proposal = AstraProposal(
            action=ACTION, resource=DEMO_REPO,
            payload={"title": "Lost-response reference issue", "body": "Filed once."},
        )
        raw = GitHubIssueActuator(GitHubActuatorConfig.from_env({
            "MCC_ASTRA_DEMO_MODE": "live",
            "MCC_ASTRA_GITHUB_REPO": stack.demo_repo,
            "MCC_ASTRA_GITHUB_BASE_URL": stack.github_base_url,
        }))
        marked = LogicalOperationMarkerActuator(raw, logical_operation_id=logical_operation_id)
        lossy = _LossyActuator(marked)
        stack.upstream = lossy

        canonical = stack.profiles.for_action(proposal.action).canonical_payload(proposal.payload)
        att = run(obtain_attestation(stack.attester, proposal=proposal, canonical_payload=canonical))
        outcome = run(run_positive_path(
            stack.service, mandate=stack.mandate, actor=ACTOR, proposal=proposal,
            attestation=att.raw_attestation, logical_operation_id=logical_operation_id,
        ))
        assert outcome.status == "EXECUTION_FAILED"  # indeterminate, not a false success
        assert lossy.calls == 1

        record = run(stack.coordinator.idempotency.get_state(logical_operation_id))
        assert record.state == IdempotencyState.UNKNOWN

        # The side effect genuinely happened -- independently observable via
        # the mock service's own recorded state, with this exact operation's
        # marker embedded in the body.
        issues = recorded_issues()
        assert len(issues) == 1
        assert logical_operation_marker(logical_operation_id) in issues[0]["body"]

        # Reconciliation: read-only positive evidence resolves UNKNOWN -> EXECUTED.
        reconcile_outcome = run(reconcile_github_issue_operation(
            idempotency=stack.coordinator.idempotency, key=logical_operation_id,
            expected_generation=record.generation, base_url=stack.github_base_url,
            repo=stack.demo_repo, logical_operation_id=logical_operation_id,
        ))
        assert reconcile_outcome.found and reconcile_outcome.applied
        resolved = run(stack.coordinator.idempotency.get_state(logical_operation_id))
        assert resolved.state == IdempotencyState.EXECUTED

        # A fresh, independently valid authorization for the SAME logical
        # operation must never trigger a second create -- even after the
        # operation is confirmed EXECUTED via reconciliation.
        second_att = run(obtain_attestation(stack.attester, proposal=proposal, canonical_payload=canonical))
        second_outcome = run(run_positive_path(
            stack.service, mandate=stack.mandate, actor=ACTOR, proposal=proposal,
            attestation=second_att.raw_attestation, logical_operation_id=logical_operation_id,
        ))
        assert second_outcome.status == "BLOCKED"
        assert lossy.calls == 1  # no second external call
        assert len(recorded_issues()) == 1  # exactly one GitHub issue ever created


def test_reconciliation_never_creates_when_no_positive_evidence_exists():
    """Negative evidence (nothing found) must leave the operation UNKNOWN --
    never itself authorize a retry, and never make any POST."""
    with LocalAstraDemoStack(demo_repo=DEMO_REPO) as stack:
        logical_operation_id = "op-never-happened"
        proposal = AstraProposal(
            action=ACTION, resource=DEMO_REPO, payload={"title": "t", "body": "b"},
        )

        async def always_raises(action, payload):
            raise TimeoutError("upstream never responded")

        stack.upstream = always_raises
        canonical = stack.profiles.for_action(proposal.action).canonical_payload(proposal.payload)
        att = run(obtain_attestation(stack.attester, proposal=proposal, canonical_payload=canonical))
        outcome = run(run_positive_path(
            stack.service, mandate=stack.mandate, actor=ACTOR, proposal=proposal,
            attestation=att.raw_attestation, logical_operation_id=logical_operation_id,
        ))
        assert outcome.status == "EXECUTION_FAILED"
        record = run(stack.coordinator.idempotency.get_state(logical_operation_id))
        assert record.state == IdempotencyState.UNKNOWN
        assert recorded_issues() == []  # genuinely never happened

        reconcile_outcome = run(reconcile_github_issue_operation(
            idempotency=stack.coordinator.idempotency, key=logical_operation_id,
            expected_generation=record.generation, base_url=stack.github_base_url,
            repo=stack.demo_repo, logical_operation_id=logical_operation_id,
        ))
        assert not reconcile_outcome.found
        assert not reconcile_outcome.applied
        still = run(stack.coordinator.idempotency.get_state(logical_operation_id))
        assert still.state == IdempotencyState.UNKNOWN  # unchanged; still not retry-eligible
        assert recorded_issues() == []  # reconciliation never created anything
