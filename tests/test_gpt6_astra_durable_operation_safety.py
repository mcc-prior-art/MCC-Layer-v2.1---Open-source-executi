"""Round 17/18 remediation — durable logical-operation safety for the GPT-6
Astra reference integration's ``create_github_issue`` action.

Covers the Astra-layer-specific pieces of the remediation that sit on top of
the generic ``mcc_core.idempotency``/``mcc_core.coordinator`` state machine
(exercised directly in ``tests/test_idempotency.py`` /
``tests/test_coordinator.py``):

* Round 17 scenario 19 — a protected action's request missing
  ``logical_operation_id`` is rejected before governance is ever invoked;
* Round 18 requirement 1 — that check lives at the ACTUAL protected
  execution boundary (``pipeline.run_positive_path``/``issue_authority``
  themselves), not only in ``cli.py``;
* Round 17 scenario 20 — an authorized resource that does not match the
  actuator's configured destination is rejected before any external call;
* Round 17 scenario 8 / Round 18 requirement 7 — the external actuator
  succeeds but the coordinator's view of the outcome is lost (simulating a
  lost response, or a crash before ``UNKNOWN``/``EXECUTED`` could even be
  persisted, leaving the record at ``DISPATCH_OWNED``); reconciliation
  (read-only) resolves it to ``EXECUTED`` from independent, fully-validated
  positive evidence, and a fresh retry attempt afterward is blocked — zero
  duplicate GitHub issues;
* Round 18 requirement 6 — reconciliation validates candidate evidence
  against the STORED logical-operation record (logical_operation_id,
  action, resource, payload binding, generation), not a marker substring
  alone: a foreign marker, wrong repository, wrong id, wrong payload, or a
  stale generation must never resolve UNKNOWN/DISPATCH_OWNED to EXECUTED.
"""

from __future__ import annotations

import asyncio

import pytest

from mcc_core import IdempotencyConfigError, IdempotencyState, InMemoryIdempotencyRegistry
from mcc_core.signing import hash_document

from examples.gpt6_astra_reference._localstack import ACTION, ACTOR, LocalAstraDemoStack
from examples.gpt6_astra_reference.github_actuator import (
    GitHubActuatorConfig, GitHubIssueActuator, build_marked_payload,
    ResourceBindingError, ResourceBoundActuator, logical_operation_marker,
)
from examples.gpt6_astra_reference.mock_github_service import recorded_issues
from examples.gpt6_astra_reference.models import (
    AstraProposal, MissingLogicalOperationIdError, require_logical_operation_id,
)
from examples.gpt6_astra_reference.pipeline import (
    enforce_authority, issue_authority, obtain_attestation, run_positive_path,
)
from examples.gpt6_astra_reference.reconciliation import reconcile_github_issue_operation

run = asyncio.run
DEMO_REPO = "owner/mcc-astra-demo-sandbox"


def _real_actuator(stack: LocalAstraDemoStack, *, authorized_resource: str) -> GitHubIssueActuator:
    """Round 19: no longer appends any marker -- the marker is now embedded
    into the payload BEFORE authorization (see ``build_marked_payload``), so
    it must already be present in whatever payload the caller passes to this
    actuator."""
    raw = GitHubIssueActuator(GitHubActuatorConfig.from_env({
        "MCC_ASTRA_DEMO_MODE": "live",
        "MCC_ASTRA_GITHUB_REPO": stack.demo_repo,
        "MCC_ASTRA_GITHUB_BASE_URL": stack.github_base_url,
    }))
    return ResourceBoundActuator(raw, authorized_resource=authorized_resource)


class _CountingUpstream:
    def __init__(self, inner=None):
        self._inner = inner
        self.calls = 0

    async def __call__(self, action, payload):
        self.calls += 1
        if self._inner is not None:
            return await self._inner(action, payload)
        return {"ok": True}


async def _issue_and_dispatch(stack, proposal, logical_operation_id, upstream):
    stack.upstream = upstream
    canonical = stack.profiles.for_action(proposal.action).canonical_payload(proposal.payload)
    att = await obtain_attestation(stack.attester, proposal=proposal, canonical_payload=canonical)
    issued = await issue_authority(
        stack.service, mandate=stack.mandate, actor=ACTOR, proposal=proposal,
        attestation=att.raw_attestation, logical_operation_id=logical_operation_id,
    )
    outcome = await enforce_authority(
        stack.service, issued=issued, actor=ACTOR, resource=proposal.resource,
        action=proposal.action, attestation=att.raw_attestation,
    )
    return issued, outcome


# ---------------------------------------------------------------------------
# Requirement 1 (Round 18): the check lives at the pipeline boundary itself.
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


@pytest.mark.parametrize("bad_value", [None, "", "   "])
def test_run_positive_path_refuses_missing_id_actuator_never_invoked(bad_value):
    """Requirement 1: calling straight into the pipeline (not through
    cli.py) with a missing/empty id must be refused, and the actuator must
    never be invoked."""
    with LocalAstraDemoStack(demo_repo=DEMO_REPO) as stack:
        counting = _CountingUpstream()
        stack.upstream = counting
        proposal = AstraProposal(action=ACTION, resource=DEMO_REPO, payload={"title": "t", "body": "b"})
        canonical = stack.profiles.for_action(proposal.action).canonical_payload(proposal.payload)
        att = run(obtain_attestation(stack.attester, proposal=proposal, canonical_payload=canonical))
        with pytest.raises(MissingLogicalOperationIdError):
            run(run_positive_path(
                stack.service, mandate=stack.mandate, actor=ACTOR, proposal=proposal,
                attestation=att.raw_attestation, logical_operation_id=bad_value,
            ))
        assert counting.calls == 0


@pytest.mark.parametrize("bad_value", [None, "", "   "])
def test_issue_authority_refuses_missing_id_no_token_issued(bad_value):
    """Requirement 1: the OTHER pipeline entry point (used by tamper/replay/
    expired scenarios) enforces the identical contract, before any
    trust/authority/Control call, let alone the actuator."""
    with LocalAstraDemoStack(demo_repo=DEMO_REPO) as stack:
        counting = _CountingUpstream()
        stack.upstream = counting
        proposal = AstraProposal(action=ACTION, resource=DEMO_REPO, payload={"title": "t", "body": "b"})
        canonical = stack.profiles.for_action(proposal.action).canonical_payload(proposal.payload)
        att = run(obtain_attestation(stack.attester, proposal=proposal, canonical_payload=canonical))
        with pytest.raises(MissingLogicalOperationIdError):
            run(issue_authority(
                stack.service, mandate=stack.mandate, actor=ACTOR, proposal=proposal,
                attestation=att.raw_attestation, logical_operation_id=bad_value,
            ))
        assert counting.calls == 0


def test_enforce_authority_refuses_token_without_idempotency_key():
    """Defense in depth: even a hand-crafted ``IssuedAuthority`` whose token
    lacks an ``idempotency_key`` is refused by ``enforce_authority`` itself,
    before the coordinator or the actuator is ever reached."""
    from examples.gpt6_astra_reference.pipeline import IssuedAuthority

    with LocalAstraDemoStack(demo_repo=DEMO_REPO) as stack:
        counting = _CountingUpstream()
        stack.upstream = counting
        fake_issued = IssuedAuthority(
            token={"action": ACTION, "resource_id": DEMO_REPO, "idempotency_key": None},
            canonical_payload={"title": "t", "body": "b"}, evidence_digest=None,
        )
        with pytest.raises(MissingLogicalOperationIdError):
            run(enforce_authority(
                stack.service, issued=fake_issued, actor=ACTOR, resource=DEMO_REPO, action=ACTION,
            ))
        assert counting.calls == 0


# ---------------------------------------------------------------------------
# Round 17 scenario 20 / Round 18 requirement 5: resource binding.
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
# Round 17 scenario 8 / Round 18 requirement 7: lost response / crash
# recovery via trusted reconciliation, never a duplicate create.
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
            payload=build_marked_payload(
                {"title": "Lost-response reference issue", "body": "Filed once."},
                logical_operation_id=logical_operation_id,
            ),
        )
        lossy = _LossyActuator(_real_actuator(stack, authorized_resource=DEMO_REPO))
        issued, outcome = run(_issue_and_dispatch(stack, proposal, logical_operation_id, lossy))
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

        # Reconciliation: read-only, fully-validated positive evidence
        # resolves UNKNOWN -> EXECUTED, using the SAME real token this
        # operation was authorized under.
        reconcile_outcome = run(reconcile_github_issue_operation(
            idempotency=stack.coordinator.idempotency, token=issued.token,
            expected_generation=record.generation, base_url=stack.github_base_url,
            actuator_repo=stack.demo_repo,
        ))
        assert reconcile_outcome.found and reconcile_outcome.applied
        resolved = run(stack.coordinator.idempotency.get_state(logical_operation_id))
        assert resolved.state == IdempotencyState.EXECUTED

        # A fresh, independently valid authorization for the SAME logical
        # operation must never trigger a second create -- even after the
        # operation is confirmed EXECUTED via reconciliation.
        second_att = run(obtain_attestation(stack.attester, proposal=proposal,
                                            canonical_payload=stack.profiles.for_action(
                                                proposal.action).canonical_payload(proposal.payload)))
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
        proposal = AstraProposal(action=ACTION, resource=DEMO_REPO, payload={"title": "t", "body": "b"})

        async def always_raises(action, payload):
            raise TimeoutError("upstream never responded")

        issued, outcome = run(_issue_and_dispatch(stack, proposal, logical_operation_id, always_raises))
        assert outcome.status == "EXECUTION_FAILED"
        record = run(stack.coordinator.idempotency.get_state(logical_operation_id))
        assert record.state == IdempotencyState.UNKNOWN
        assert recorded_issues() == []  # genuinely never happened

        reconcile_outcome = run(reconcile_github_issue_operation(
            idempotency=stack.coordinator.idempotency, token=issued.token,
            expected_generation=record.generation, base_url=stack.github_base_url,
            actuator_repo=stack.demo_repo,
        ))
        assert not reconcile_outcome.found
        assert not reconcile_outcome.applied
        still = run(stack.coordinator.idempotency.get_state(logical_operation_id))
        assert still.state == IdempotencyState.UNKNOWN  # unchanged; still not retry-eligible
        assert recorded_issues() == []  # reconciliation never created anything


def test_dispatch_owned_crash_recovers_via_reconciliation_to_executed():
    """Requirement 7: a crash after durable dispatch ownership but before
    UNKNOWN/EXECUTED could even be persisted (modeled here by driving the
    registry directly to DISPATCH_OWNED and making the real external call
    OUTSIDE the coordinator, exactly as if the coordinator process died
    right after the call returned) must still have a reconciliation path,
    and must never permanently strand the operation."""
    with LocalAstraDemoStack(demo_repo=DEMO_REPO) as stack:
        logical_operation_id = "op-crash-dispatch-owned"
        proposal = AstraProposal(
            action=ACTION, resource=DEMO_REPO,
            payload=build_marked_payload(
                {"title": "Crash-recovery reference issue", "body": "Filed once."},
                logical_operation_id=logical_operation_id,
            ),
        )
        canonical = stack.profiles.for_action(proposal.action).canonical_payload(proposal.payload)
        att = run(obtain_attestation(stack.attester, proposal=proposal, canonical_payload=canonical))
        issued = run(issue_authority(
            stack.service, mandate=stack.mandate, actor=ACTOR, proposal=proposal,
            attestation=att.raw_attestation, logical_operation_id=logical_operation_id,
        ))
        binding_ref = hash_document({
            "action": issued.token["action"], "resource": issued.token["resource_id"],
            "payload_hash": issued.token["payload_hash"],
        })
        reserved = run(stack.coordinator.idempotency.reserve(logical_operation_id, binding=binding_ref))
        assert reserved.ok
        assert run(stack.coordinator.idempotency.commit_dispatch(logical_operation_id, fence=reserved.fence))

        # The real external call actually happens (made directly here,
        # standing in for the coordinator's executor() call immediately
        # before the process dies -- mark_unknown never runs). The marker is
        # already present in ``issued.canonical_payload`` -- it was embedded
        # into the proposal before authorization, not applied here.
        actuator = _real_actuator(stack, authorized_resource=DEMO_REPO)
        run(actuator(ACTION, issued.canonical_payload))

        record = run(stack.coordinator.idempotency.get_state(logical_operation_id))
        assert record.state == IdempotencyState.DISPATCH_OWNED

        # No automatic redispatch: a fresh, independently valid
        # authorization through the REAL coordinator must be blocked.
        counting = _CountingUpstream()
        fresh_att = run(obtain_attestation(stack.attester, proposal=proposal, canonical_payload=canonical))
        stack.upstream = counting
        retry_outcome = run(run_positive_path(
            stack.service, mandate=stack.mandate, actor=ACTOR, proposal=proposal,
            attestation=fresh_att.raw_attestation, logical_operation_id=logical_operation_id,
        ))
        assert retry_outcome.status == "BLOCKED"
        assert counting.calls == 0

        # Reconciliation resolves DISPATCH_OWNED -> EXECUTED directly (no
        # intermediate UNKNOWN step required).
        reconcile_outcome = run(reconcile_github_issue_operation(
            idempotency=stack.coordinator.idempotency, token=issued.token,
            expected_generation=record.generation, base_url=stack.github_base_url,
            actuator_repo=stack.demo_repo,
        ))
        assert reconcile_outcome.found and reconcile_outcome.applied
        resolved = run(stack.coordinator.idempotency.get_state(logical_operation_id))
        assert resolved.state == IdempotencyState.EXECUTED
        assert len(recorded_issues()) == 1  # exactly one, ever


def test_dispatch_owned_without_evidence_stays_pending_never_reopens():
    """Requirement 7 (negative half): absence of external evidence for a
    DISPATCH_OWNED operation must not reopen admission."""
    with LocalAstraDemoStack(demo_repo=DEMO_REPO) as stack:
        logical_operation_id = "op-crash-no-evidence"
        proposal = AstraProposal(action=ACTION, resource=DEMO_REPO, payload={"title": "t", "body": "b"})
        canonical = stack.profiles.for_action(proposal.action).canonical_payload(proposal.payload)
        att = run(obtain_attestation(stack.attester, proposal=proposal, canonical_payload=canonical))
        issued = run(issue_authority(
            stack.service, mandate=stack.mandate, actor=ACTOR, proposal=proposal,
            attestation=att.raw_attestation, logical_operation_id=logical_operation_id,
        ))
        binding_ref = hash_document({
            "action": issued.token["action"], "resource": issued.token["resource_id"],
            "payload_hash": issued.token["payload_hash"],
        })
        reserved = run(stack.coordinator.idempotency.reserve(logical_operation_id, binding=binding_ref))
        assert run(stack.coordinator.idempotency.commit_dispatch(logical_operation_id, fence=reserved.fence))
        # No external call is ever made -- genuinely no evidence exists.

        record = run(stack.coordinator.idempotency.get_state(logical_operation_id))
        reconcile_outcome = run(reconcile_github_issue_operation(
            idempotency=stack.coordinator.idempotency, token=issued.token,
            expected_generation=record.generation, base_url=stack.github_base_url,
            actuator_repo=stack.demo_repo,
        ))
        assert not reconcile_outcome.found
        assert not reconcile_outcome.applied
        still = run(stack.coordinator.idempotency.get_state(logical_operation_id))
        assert still.state == IdempotencyState.DISPATCH_OWNED  # unchanged
        assert recorded_issues() == []


# ---------------------------------------------------------------------------
# Round 18 requirement 6: trusted reconciliation attribution -- a marker
# substring alone is insufficient; every candidate must match the STORED
# logical-operation record.
# ---------------------------------------------------------------------------


def _setup_unknown_operation(stack, *, logical_operation_id: str, payload=None):
    """Drives one operation through issue+dispatch with a lossy actuator so
    it parks at UNKNOWN with a real, marker-tagged issue behind it, and
    returns (issued, record)."""
    base_payload = payload or {"title": "Trusted-reconciliation reference issue", "body": "Filed once."}
    proposal = AstraProposal(
        action=ACTION, resource=DEMO_REPO,
        payload=build_marked_payload(base_payload, logical_operation_id=logical_operation_id),
    )
    lossy = _LossyActuator(_real_actuator(stack, authorized_resource=DEMO_REPO))
    issued, outcome = run(_issue_and_dispatch(stack, proposal, logical_operation_id, lossy))
    assert outcome.status == "EXECUTION_FAILED"
    record = run(stack.coordinator.idempotency.get_state(logical_operation_id))
    assert record.state == IdempotencyState.UNKNOWN
    return issued, record


def test_reconciliation_rejects_foreign_operation_marker():
    """A real issue exists in the SAME repository, but it was created for a
    DIFFERENT operation's marker -- it must never satisfy THIS operation's
    reconciliation. ``op-real-6a`` itself produced NO real evidence (its
    own upstream call never reached the network at all), so the only
    candidate reconciliation could possibly match is the foreign one."""
    with LocalAstraDemoStack(demo_repo=DEMO_REPO) as stack:
        logical_operation_id = "op-real-6a"
        proposal = AstraProposal(action=ACTION, resource=DEMO_REPO, payload={"title": "t", "body": "b"})

        async def always_raises(action, payload):
            raise TimeoutError("upstream never responded")

        issued, outcome = run(_issue_and_dispatch(stack, proposal, logical_operation_id, always_raises))
        assert outcome.status == "EXECUTION_FAILED"
        record = run(stack.coordinator.idempotency.get_state(logical_operation_id))
        assert record.state == IdempotencyState.UNKNOWN
        assert recorded_issues() == []  # op-real-6a genuinely never happened

        # A foreign operation's issue, filed directly (never through this
        # operation's own dispatch), carrying a DIFFERENT marker.
        foreign_actuator = _real_actuator(stack, authorized_resource=DEMO_REPO)
        run(foreign_actuator(ACTION, build_marked_payload(
            {"title": "unrelated", "body": "unrelated"}, logical_operation_id="op-foreign-999",
        )))
        assert len(recorded_issues()) == 1  # only the foreign one exists

        reconcile_outcome = run(reconcile_github_issue_operation(
            idempotency=stack.coordinator.idempotency, token=issued.token,
            expected_generation=record.generation, base_url=stack.github_base_url,
            actuator_repo=stack.demo_repo,
        ))
        assert not reconcile_outcome.found
        assert not reconcile_outcome.applied
        still = run(stack.coordinator.idempotency.get_state(logical_operation_id))
        assert still.state == IdempotencyState.UNKNOWN


def test_reconciliation_rejects_wrong_repository():
    """The authorized resource must equal the actuator's configured lookup
    destination -- a mismatch is refused BEFORE any external call."""
    with LocalAstraDemoStack(demo_repo=DEMO_REPO) as stack:
        logical_operation_id = "op-real-6b"
        issued, record = _setup_unknown_operation(stack, logical_operation_id=logical_operation_id)

        reconcile_outcome = run(reconcile_github_issue_operation(
            idempotency=stack.coordinator.idempotency, token=issued.token,
            expected_generation=record.generation, base_url=stack.github_base_url,
            actuator_repo="owner/a-completely-different-repo",
        ))
        assert not reconcile_outcome.found
        assert not reconcile_outcome.applied
        assert "resource" in reconcile_outcome.reason.lower()
        still = run(stack.coordinator.idempotency.get_state(logical_operation_id))
        assert still.state == IdempotencyState.UNKNOWN


def test_reconciliation_rejects_wrong_logical_operation_id():
    """A token naming an id that has no stored record at all must be
    refused, never treated as a fresh, reconcilable operation."""
    with LocalAstraDemoStack(demo_repo=DEMO_REPO) as stack:
        logical_operation_id = "op-real-6c"
        issued, record = _setup_unknown_operation(stack, logical_operation_id=logical_operation_id)

        forged_token = dict(issued.token)
        forged_token["idempotency_key"] = "op-that-was-never-admitted"
        reconcile_outcome = run(reconcile_github_issue_operation(
            idempotency=stack.coordinator.idempotency, token=forged_token,
            expected_generation=record.generation, base_url=stack.github_base_url,
            actuator_repo=stack.demo_repo,
        ))
        assert not reconcile_outcome.found
        assert not reconcile_outcome.applied
        assert "no stored" in reconcile_outcome.reason.lower()
        # the REAL operation is untouched
        still = run(stack.coordinator.idempotency.get_state(logical_operation_id))
        assert still.state == IdempotencyState.UNKNOWN


def test_reconciliation_rejects_wrong_payload():
    """A token claiming a DIFFERENT payload_hash than what was actually
    admitted under this id must be refused -- the stored binding is
    authoritative, not whatever the candidate token asserts."""
    with LocalAstraDemoStack(demo_repo=DEMO_REPO) as stack:
        logical_operation_id = "op-real-6d"
        issued, record = _setup_unknown_operation(stack, logical_operation_id=logical_operation_id)

        forged_token = dict(issued.token)
        forged_token["payload_hash"] = "sha256:" + "0" * 64
        reconcile_outcome = run(reconcile_github_issue_operation(
            idempotency=stack.coordinator.idempotency, token=forged_token,
            expected_generation=record.generation, base_url=stack.github_base_url,
            actuator_repo=stack.demo_repo,
        ))
        assert not reconcile_outcome.found
        assert not reconcile_outcome.applied
        assert "binding" in reconcile_outcome.reason.lower()
        still = run(stack.coordinator.idempotency.get_state(logical_operation_id))
        assert still.state == IdempotencyState.UNKNOWN


def test_reconciliation_rejects_stale_generation():
    with LocalAstraDemoStack(demo_repo=DEMO_REPO) as stack:
        logical_operation_id = "op-real-6e"
        issued, record = _setup_unknown_operation(stack, logical_operation_id=logical_operation_id)

        reconcile_outcome = run(reconcile_github_issue_operation(
            idempotency=stack.coordinator.idempotency, token=issued.token,
            expected_generation="not-the-real-generation", base_url=stack.github_base_url,
            actuator_repo=stack.demo_repo,
        ))
        assert not reconcile_outcome.found
        assert not reconcile_outcome.applied
        still = run(stack.coordinator.idempotency.get_state(logical_operation_id))
        assert still.state == IdempotencyState.UNKNOWN


def test_reconciliation_accepts_fully_matching_evidence():
    """The positive control: every check lines up -> resolves to EXECUTED."""
    with LocalAstraDemoStack(demo_repo=DEMO_REPO) as stack:
        logical_operation_id = "op-real-6f"
        issued, record = _setup_unknown_operation(stack, logical_operation_id=logical_operation_id)

        reconcile_outcome = run(reconcile_github_issue_operation(
            idempotency=stack.coordinator.idempotency, token=issued.token,
            expected_generation=record.generation, base_url=stack.github_base_url,
            actuator_repo=stack.demo_repo,
        ))
        assert reconcile_outcome.found and reconcile_outcome.applied
        resolved = run(stack.coordinator.idempotency.get_state(logical_operation_id))
        assert resolved.state == IdempotencyState.EXECUTED


# ---------------------------------------------------------------------------
# Round 18 requirement 4: durable backend construction. The Astra reference
# stack must not directly instantiate volatile in-memory idempotency storage
# for enforcement execution -- it must go through the same enforcement-aware
# factory production code uses, which fails closed in enforcement mode
# without a real, shared, durable backend configured.
# ---------------------------------------------------------------------------


def test_astra_stack_refuses_enforcement_mode_with_volatile_idempotency(monkeypatch):
    monkeypatch.setenv("MCC_DEPLOYMENT_MODE", "enforcement")
    monkeypatch.delenv("MCC_IDEMPOTENCY_BACKEND", raising=False)
    monkeypatch.delenv("MCC_REDIS_URL", raising=False)
    with pytest.raises(IdempotencyConfigError):
        LocalAstraDemoStack(demo_repo=DEMO_REPO)


def test_astra_stack_refuses_enforcement_mode_even_with_backend_explicitly_memory(monkeypatch):
    monkeypatch.setenv("MCC_DEPLOYMENT_MODE", "enforcement")
    monkeypatch.setenv("MCC_IDEMPOTENCY_BACKEND", "memory")
    with pytest.raises(IdempotencyConfigError):
        LocalAstraDemoStack(demo_repo=DEMO_REPO)


def test_astra_stack_starts_normally_in_reference_mode(monkeypatch):
    """Unaffected by Round 18: local demo/test runs -- which never invoke a
    real actuator against a live repository unless an operator separately
    opts into ``MCC_ASTRA_DEMO_MODE=live`` -- keep working exactly as
    before, with in-memory idempotency storage."""
    monkeypatch.delenv("MCC_DEPLOYMENT_MODE", raising=False)
    monkeypatch.delenv("MCC_IDEMPOTENCY_BACKEND", raising=False)
    with LocalAstraDemoStack(demo_repo=DEMO_REPO) as stack:
        assert isinstance(stack.coordinator.idempotency, InMemoryIdempotencyRegistry)
