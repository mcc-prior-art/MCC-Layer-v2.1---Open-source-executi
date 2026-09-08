"""Phase 2 Live Sandbox Proof — deterministic CI suite.

Exercises the REAL, unmodified ``ProposalExecutionService.authorize_and_execute``
path end-to-end against a REAL HTTP server (a local mock GitHub service --
no live GitHub network access) and REAL Redis (``RedisProposalRegistry`` /
``RedisIdempotencyRegistry`` / ``RedisNonceRegistry`` -- never fakes).
Requires a reachable local Redis; skips (not fails) the whole module if
unavailable, exactly like the rest of this repository's real-Redis test
conventions.

No live GitHub credentials or network access are used or required by this
module -- see ``.github/workflows/phase2-live-sandbox-manual.yml`` for the
separate, explicitly-triggered live proof.
"""

from __future__ import annotations

import asyncio
import uuid
from typing import Any, Dict, List

import pytest

pytest.importorskip("redis")

from examples._demo_server import DemoServer, free_port  # noqa: E402
from examples.gpt6_astra_reference.github_actuator import (  # noqa: E402
    GitHubActuatorConfig,
    GitHubActuatorDisabledError,
    GitHubIssueActuator,
)
from examples.gpt6_astra_reference.mock_github_service import (  # noqa: E402
    build_mock_github_service,
    recorded_issues,
    reset_issues,
)
from examples.phase2_live_sandbox.actuator import GitHubSandboxUpstream  # noqa: E402
from examples.phase2_live_sandbox.config import SandboxConfig, SandboxConfigError  # noqa: E402
from examples.phase2_live_sandbox.marker import (  # noqa: E402
    composite_marker,
    prepare_sandbox_issue_payload,
)
from examples.phase2_live_sandbox.stack import (  # noqa: E402
    RedisUnavailableError,
    build_live_sandbox_stack,
)
from gateway.proposal_execution_service import (  # noqa: E402
    ProposalExecStatus,
    ProposalExecutionService,
    ReconcileOutcome,
    reconcile_proposal_operation,
)
from mcc_core import IdempotencyState, InMemoryIdempotencyRegistry  # noqa: E402

run = asyncio.run
REDIS_URL = "redis://127.0.0.1:6379/9"


def _redis_available() -> bool:
    try:
        import redis as redis_sync

        client = redis_sync.from_url(REDIS_URL, socket_connect_timeout=0.5)
        client.ping()
        return True
    except Exception:
        return False


pytestmark = pytest.mark.skipif(not _redis_available(), reason="real Redis not reachable at 127.0.0.1:6379")


@pytest.fixture(scope="module")
def mock_github():
    reset_issues()
    port = free_port()
    server = DemoServer(build_mock_github_service(), port).start()
    yield f"http://127.0.0.1:{port}"
    server.stop()


@pytest.fixture(autouse=True)
def _reset_issues_between_tests():
    reset_issues()
    yield


def _config(mock_github: str, *, repo: str = "sandbox-owner/sandbox-repo") -> SandboxConfig:
    return SandboxConfig(live=True, repo=repo, base_url=mock_github, token=None, redis_url=REDIS_URL)


async def _stack(mock_github: str, *, tenants: Dict[str, Dict[str, Any]], repo: str = "sandbox-owner/sandbox-repo"):
    return await build_live_sandbox_stack(
        config=_config(mock_github, repo=repo), tenants=tenants, namespace_suffix=uuid.uuid4().hex[:8],
    )


def _uid() -> str:
    return uuid.uuid4().hex[:8]


async def _propose(stack, tenant_id: str, op_id: str, *, resource: str, title: str = "Sandbox issue") -> Any:
    payload = prepare_sandbox_issue_payload(
        {"title": title, "body": f"proof run {op_id}"}, tenant_id=tenant_id, logical_operation_id=op_id,
    )
    return await stack.svc.submit_proposal(tenant_id=tenant_id, request={
        "logical_operation_id": op_id, "actor": "agent/sandbox-proof", "action": "create_github_issue",
        "resource": resource, "payload": payload,
    })


# --------------------------------------------------------------------------- #
# A. successful proposal -> authority -> real sandbox dispatch path
# --------------------------------------------------------------------------- #

def test_a_successful_proposal_authority_real_sandbox_dispatch(mock_github):
    tenant_id, op_id = f"tenant-{_uid()}", f"op-{_uid()}"

    async def go():
        stack = await _stack(mock_github, tenants={tenant_id: {}})
        r = await _propose(stack, tenant_id, op_id, resource=stack.repo)
        assert r.status == "PROPOSED"
        out = await stack.bridge.authorize_and_execute(tenant_id=tenant_id, logical_operation_id=op_id)
        return out

    out = run(go())
    assert out.status == ProposalExecStatus.EXECUTED
    issues = recorded_issues()
    assert len(issues) == 1
    assert composite_marker(tenant_id, op_id) in issues[0]["body"]


# --------------------------------------------------------------------------- #
# B. no authority -> zero external requests
# --------------------------------------------------------------------------- #

def test_b_no_authority_zero_external_requests(mock_github):
    tenant_id, op_id = f"tenant-{_uid()}", f"op-{_uid()}"

    async def go():
        stack = await _stack(mock_github, tenants={})  # tenant granted NO authority
        await _propose(stack, tenant_id, op_id, resource=stack.repo)
        return await stack.bridge.authorize_and_execute(tenant_id=tenant_id, logical_operation_id=op_id)

    out = run(go())
    assert out.status == ProposalExecStatus.DENIED
    assert recorded_issues() == []


# --------------------------------------------------------------------------- #
# C. wrong tenant -> zero external requests
# --------------------------------------------------------------------------- #

def test_c_wrong_tenant_zero_external_requests(mock_github):
    owner_tenant, other_tenant, op_id = f"tenant-owner-{_uid()}", f"tenant-other-{_uid()}", f"op-{_uid()}"

    async def go():
        stack = await _stack(mock_github, tenants={owner_tenant: {}, other_tenant: {}})
        await _propose(stack, owner_tenant, op_id, resource=stack.repo)
        return await stack.bridge.authorize_and_execute(tenant_id=other_tenant, logical_operation_id=op_id)

    out = run(go())
    assert out.status == ProposalExecStatus.NOT_FOUND
    assert recorded_issues() == []


# --------------------------------------------------------------------------- #
# D. resource mismatch -> zero external requests
# --------------------------------------------------------------------------- #

def test_d_resource_mismatch_zero_external_requests(mock_github):
    tenant_id, op_id = f"tenant-{_uid()}", f"op-{_uid()}"

    async def go():
        stack = await _stack(mock_github, tenants={tenant_id: {}}, repo="sandbox-owner/sandbox-repo")
        # Proposal authorized for a DIFFERENT repo than the actuator is configured for.
        await _propose(stack, tenant_id, op_id, resource="sandbox-owner/a-different-repo")
        return await stack.bridge.authorize_and_execute(tenant_id=tenant_id, logical_operation_id=op_id)

    out = run(go())
    assert out.status == ProposalExecStatus.RESOURCE_MISMATCH
    assert recorded_issues() == []


# --------------------------------------------------------------------------- #
# E. payload mismatch -> zero external requests
# --------------------------------------------------------------------------- #

def test_e_payload_mismatch_zero_external_requests(mock_github):
    tenant_id, op_id = f"tenant-{_uid()}", f"op-{_uid()}"

    async def go():
        stack = await _stack(mock_github, tenants={tenant_id: {}})
        await _propose(stack, tenant_id, op_id, resource=stack.repo)
        # Tamper with the stored record's payload without recomputing its binding.
        real = await stack.proposals.get(tenant_id=tenant_id, logical_operation_id=op_id)
        from mcc_proposal.registry import ProposalRecord

        tampered = ProposalRecord(
            tenant_id=real.tenant_id, logical_operation_id=real.logical_operation_id,
            binding=real.binding, created_at=real.created_at, action=real.action,
            resource=real.resource, payload={"title": "TAMPERED", "body": "tampered"},
        )
        key = stack.proposals._key(tenant_id, op_id)
        await stack.proposals._redis.set(
            key, __import__("json").dumps({
                "binding": tampered.binding, "created_at": tampered.created_at,
                "action": tampered.action, "resource": tampered.resource, "payload": tampered.payload,
            }),
        )
        return await stack.bridge.authorize_and_execute(tenant_id=tenant_id, logical_operation_id=op_id)

    out = run(go())
    assert out.status == ProposalExecStatus.REJECTED
    assert recorded_issues() == []


# --------------------------------------------------------------------------- #
# F. replay -> exactly one external side effect total
# --------------------------------------------------------------------------- #

def test_f_replay_exactly_one_external_side_effect(mock_github):
    tenant_id, op_id = f"tenant-{_uid()}", f"op-{_uid()}"

    async def go():
        stack = await _stack(mock_github, tenants={tenant_id: {}})
        await _propose(stack, tenant_id, op_id, resource=stack.repo)
        first = await stack.bridge.authorize_and_execute(tenant_id=tenant_id, logical_operation_id=op_id)
        second = await stack.bridge.authorize_and_execute(tenant_id=tenant_id, logical_operation_id=op_id)
        third = await stack.bridge.authorize_and_execute(tenant_id=tenant_id, logical_operation_id=op_id)
        return first, second, third

    first, second, third = run(go())
    assert first.status == ProposalExecStatus.EXECUTED
    assert second.status != ProposalExecStatus.EXECUTED
    assert third.status != ProposalExecStatus.EXECUTED
    assert len(recorded_issues()) == 1


# --------------------------------------------------------------------------- #
# G. concurrent duplicate -> at most one external side effect
# --------------------------------------------------------------------------- #

def test_g_concurrent_duplicate_at_most_one_external_side_effect(mock_github):
    tenant_id, op_id = f"tenant-{_uid()}", f"op-{_uid()}"

    async def go():
        stack = await _stack(mock_github, tenants={tenant_id: {}})
        await _propose(stack, tenant_id, op_id, resource=stack.repo)
        return await asyncio.gather(
            stack.bridge.authorize_and_execute(tenant_id=tenant_id, logical_operation_id=op_id),
            stack.bridge.authorize_and_execute(tenant_id=tenant_id, logical_operation_id=op_id),
        )

    r1, r2 = run(go())
    statuses = [r1.status, r2.status]
    assert statuses.count(ProposalExecStatus.EXECUTED) == 1
    assert len(recorded_issues()) == 1


# --------------------------------------------------------------------------- #
# H. Redis/backend unavailable -> zero external requests
# --------------------------------------------------------------------------- #

def test_h_redis_unavailable_zero_external_requests(mock_github):
    async def go():
        bad_config = SandboxConfig(
            live=True, repo="sandbox-owner/sandbox-repo", base_url=mock_github, token=None,
            redis_url="redis://127.0.0.1:1/0",  # unreachable
        )
        with pytest.raises(RedisUnavailableError):
            await build_live_sandbox_stack(config=bad_config, tenants={"tenant-x": {}})

    run(go())
    assert recorded_issues() == []


# --------------------------------------------------------------------------- #
# I. ambiguous post-dispatch outcome -> durable UNKNOWN
# --------------------------------------------------------------------------- #

async def _crash_after_real_dispatch(stack, base_url, repo, tenant_id, op_id):
    """A REAL request reaches the mock server (so an issue genuinely
    exists), but the coordinator observes an exception -- exactly the
    "server accepted the request but the response was lost" ambiguous
    failure mode Section 8 describes."""
    from gateway.proposal_execution_service import ResourceBoundUpstream

    async def crashing(*, resource, action, payload):
        import httpx

        async with httpx.AsyncClient() as client:
            await client.post(f"{base_url}/repos/{repo}/issues", json=payload)
        raise ConnectionError("simulated ambiguous post-dispatch failure")

    stack.bridge._upstream = ResourceBoundUpstream(resource=repo, dispatch=crashing)
    return await stack.bridge.authorize_and_execute(tenant_id=tenant_id, logical_operation_id=op_id)


def test_i_ambiguous_post_dispatch_outcome_durable_unknown(mock_github):
    tenant_id, op_id = f"tenant-{_uid()}", f"op-{_uid()}"

    async def go():
        stack = await _stack(mock_github, tenants={tenant_id: {}})
        await _propose(stack, tenant_id, op_id, resource=stack.repo)
        out = await _crash_after_real_dispatch(stack, mock_github, stack.repo, tenant_id, op_id)
        state = await stack.idempotency.get_state(op_id, tenant_id=tenant_id)
        return out, state

    out, state = run(go())
    assert out.status == ProposalExecStatus.EXECUTION_FAILED
    assert state.state == IdempotencyState.UNKNOWN
    assert len(recorded_issues()) == 1  # the real request DID land


# --------------------------------------------------------------------------- #
# J. UNKNOWN replay/retry -> zero new external side effect
# --------------------------------------------------------------------------- #

def test_j_unknown_replay_zero_new_external_side_effect(mock_github):
    tenant_id, op_id = f"tenant-{_uid()}", f"op-{_uid()}"

    async def go():
        stack = await _stack(mock_github, tenants={tenant_id: {}})
        await _propose(stack, tenant_id, op_id, resource=stack.repo)
        await _crash_after_real_dispatch(stack, mock_github, stack.repo, tenant_id, op_id)
        issues_after_crash = len(recorded_issues())
        retry = await stack.bridge.authorize_and_execute(tenant_id=tenant_id, logical_operation_id=op_id)
        return retry, issues_after_crash

    retry, issues_after_crash = run(go())
    assert retry.status != ProposalExecStatus.EXECUTED
    assert issues_after_crash == 1
    assert len(recorded_issues()) == 1  # no NEW side effect from the retry attempt


# --------------------------------------------------------------------------- #
# K. unrelated reconciliation evidence -> no resolution
# --------------------------------------------------------------------------- #

def test_k_unrelated_reconciliation_evidence_no_resolution(mock_github):
    tenant_id, op_id, unrelated_op_id = f"tenant-{_uid()}", f"op-{_uid()}", f"unrelated-op-{_uid()}"

    async def go():
        stack = await _stack(mock_github, tenants={tenant_id: {}})
        await _propose(stack, tenant_id, op_id, resource=stack.repo)
        # Crash WITHOUT the request actually landing (pure network failure).
        from gateway.proposal_execution_service import ResourceBoundUpstream

        async def pure_crash(*, resource, action, payload):
            raise ConnectionError("never reached the server")

        stack.bridge._upstream = ResourceBoundUpstream(resource=stack.repo, dispatch=pure_crash)
        await stack.bridge.authorize_and_execute(tenant_id=tenant_id, logical_operation_id=op_id)

        # Only an UNRELATED issue exists.
        import httpx

        async with httpx.AsyncClient() as client:
            await client.post(f"{mock_github}/repos/{stack.repo}/issues", json={
                "title": "unrelated", "body": composite_marker(tenant_id, unrelated_op_id),
            })

        recon = await reconcile_proposal_operation(
            proposals=stack.proposals, idempotency=stack.idempotency, authority=stack.authority,
            tenant_id=tenant_id, logical_operation_id=op_id, verify_external_evidence=stack.evidence_verifier,
        )
        state = await stack.idempotency.get_state(op_id, tenant_id=tenant_id)
        return recon, state

    recon, state = run(go())
    assert recon.outcome == ReconcileOutcome.NO_EVIDENCE
    assert state.state == IdempotencyState.UNKNOWN


# --------------------------------------------------------------------------- #
# L. cross-tenant reconciliation -> no resolution
# --------------------------------------------------------------------------- #

def test_l_cross_tenant_reconciliation_no_resolution(mock_github):
    tenant_a, tenant_b, op_id = f"tenant-a-{_uid()}", f"tenant-b-{_uid()}", f"op-{_uid()}"

    async def go():
        stack = await _stack(mock_github, tenants={tenant_a: {}, tenant_b: {}})
        await _propose(stack, tenant_a, op_id, resource=stack.repo)
        await _propose(stack, tenant_b, op_id, resource=stack.repo)
        await _crash_after_real_dispatch(stack, mock_github, stack.repo, tenant_a, op_id)
        from gateway.proposal_execution_service import ResourceBoundUpstream

        async def pure_crash(*, resource, action, payload):
            raise ConnectionError("never reached the server")

        stack.bridge._upstream = ResourceBoundUpstream(resource=stack.repo, dispatch=pure_crash)
        await stack.bridge.authorize_and_execute(tenant_id=tenant_b, logical_operation_id=op_id)

        # tenant-b reconciles the IDENTICAL logical_operation_id -- the only
        # real issue that exists carries tenant-a's composite marker, which
        # tenant-b's own scoped search can never match.
        recon_b = await reconcile_proposal_operation(
            proposals=stack.proposals, idempotency=stack.idempotency, authority=stack.authority,
            tenant_id=tenant_b, logical_operation_id=op_id, verify_external_evidence=stack.evidence_verifier,
        )
        state_a = await stack.idempotency.get_state(op_id, tenant_id=tenant_a)
        state_b = await stack.idempotency.get_state(op_id, tenant_id=tenant_b)
        return recon_b, state_a, state_b

    recon_b, state_a, state_b = run(go())
    assert recon_b.outcome == ReconcileOutcome.NO_EVIDENCE
    assert state_a.state == IdempotencyState.UNKNOWN  # tenant-a's real issue, untouched by this call
    assert state_b.state == IdempotencyState.UNKNOWN  # tenant-b's own record, never resolved


# --------------------------------------------------------------------------- #
# M. exact reconciliation evidence -> UNKNOWN -> EXECUTED
# --------------------------------------------------------------------------- #

def test_m_exact_reconciliation_evidence_unknown_to_executed(mock_github):
    tenant_id, op_id = f"tenant-{_uid()}", f"op-{_uid()}"

    async def go():
        stack = await _stack(mock_github, tenants={tenant_id: {}})
        await _propose(stack, tenant_id, op_id, resource=stack.repo)
        await _crash_after_real_dispatch(stack, mock_github, stack.repo, tenant_id, op_id)
        recon = await reconcile_proposal_operation(
            proposals=stack.proposals, idempotency=stack.idempotency, authority=stack.authority,
            tenant_id=tenant_id, logical_operation_id=op_id, verify_external_evidence=stack.evidence_verifier,
        )
        state = await stack.idempotency.get_state(op_id, tenant_id=tenant_id)
        return recon, state

    recon, state = run(go())
    assert recon.outcome == ReconcileOutcome.RESOLVED
    assert state.state == IdempotencyState.EXECUTED


# --------------------------------------------------------------------------- #
# N. reconciliation never invokes actuator
# --------------------------------------------------------------------------- #

def test_n_reconciliation_never_invokes_actuator(mock_github):
    tenant_id, op_id = f"tenant-{_uid()}", f"op-{_uid()}"

    async def go():
        stack = await _stack(mock_github, tenants={tenant_id: {}})
        await _propose(stack, tenant_id, op_id, resource=stack.repo)
        await _crash_after_real_dispatch(stack, mock_github, stack.repo, tenant_id, op_id)
        issues_before_recon = len(recorded_issues())

        dispatched = []

        async def spy(*, resource, action, payload):
            dispatched.append(1)
            return {"ok": True}

        from gateway.proposal_execution_service import ResourceBoundUpstream

        stack.bridge._upstream = ResourceBoundUpstream(resource=stack.repo, dispatch=spy)
        recon = await reconcile_proposal_operation(
            proposals=stack.proposals, idempotency=stack.idempotency, authority=stack.authority,
            tenant_id=tenant_id, logical_operation_id=op_id, verify_external_evidence=stack.evidence_verifier,
        )
        return recon, dispatched, issues_before_recon

    recon, dispatched, issues_before_recon = run(go())
    assert recon.outcome == ReconcileOutcome.RESOLVED
    assert dispatched == []
    assert len(recorded_issues()) == issues_before_recon  # no new issue from reconciliation itself


# --------------------------------------------------------------------------- #
# O. live mode disabled by default -> zero external requests
# --------------------------------------------------------------------------- #

def test_o_live_mode_disabled_by_default_zero_external_requests():
    config = SandboxConfig.from_env({})
    assert config.live is False

    actuator = GitHubIssueActuator(GitHubActuatorConfig(mode="disabled", repo=None, base_url="https://api.github.com", token=None))
    with pytest.raises(GitHubActuatorDisabledError):
        run(actuator("create_github_issue", {"title": "x", "body": "y"}))
    assert recorded_issues() == []


# --------------------------------------------------------------------------- #
# P. core repository cannot accidentally be selected as sandbox destination
# --------------------------------------------------------------------------- #

def test_p_core_repository_cannot_be_selected_as_sandbox_destination():
    with pytest.raises(SandboxConfigError):
        SandboxConfig.from_env({
            "MCC_PHASE2_LIVE_SANDBOX": "1", "MCC_PHASE2_SANDBOX_REPO": "mcc-prior-art/mcc-layer",
            "GITHUB_TOKEN": "fake", "MCC_REDIS_URL": REDIS_URL,
        })


def test_p_missing_repo_when_live_is_rejected():
    with pytest.raises(SandboxConfigError):
        SandboxConfig.from_env({"MCC_PHASE2_LIVE_SANDBOX": "1", "GITHUB_TOKEN": "fake", "MCC_REDIS_URL": REDIS_URL})


def test_p_missing_token_when_live_is_rejected():
    with pytest.raises(SandboxConfigError):
        SandboxConfig.from_env({
            "MCC_PHASE2_LIVE_SANDBOX": "1", "MCC_PHASE2_SANDBOX_REPO": "sandbox-owner/sandbox-repo",
            "MCC_REDIS_URL": REDIS_URL,
        })


def test_p_missing_redis_when_live_is_rejected():
    with pytest.raises(SandboxConfigError):
        SandboxConfig.from_env({
            "MCC_PHASE2_LIVE_SANDBOX": "1", "MCC_PHASE2_SANDBOX_REPO": "sandbox-owner/sandbox-repo",
            "GITHUB_TOKEN": "fake",
        })


# =========================================================================== #
# Section 13 -- non-vacuity probes.
# =========================================================================== #

def test_non_vacuity_1_direct_actuator_bypass_around_proposal_execution_service(mock_github):
    """Proves WHY every side effect must be reachable ONLY through
    ProposalExecutionService: calling the actuator directly -- bypassing
    authority/durable-admission/audit entirely -- DOES create a real
    external side effect. This is never done by shipped code (the sandbox
    upstream is only ever installed on a ProposalExecutionService instance
    and never invoked directly elsewhere), but demonstrates the bypass
    this repository's own tests (and the architecture) must, and do,
    prevent by construction (Section 1: "must NOT call the external
    actuator directly")."""
    repo = "sandbox-owner/sandbox-repo"
    actuator = GitHubIssueActuator(GitHubActuatorConfig(mode="live", repo=repo, base_url=mock_github, token=None))
    upstream = GitHubSandboxUpstream(actuator)

    # Direct call, with NO proposal, NO authority evaluation, NO durable
    # admission, NO audit record -- exactly what a bypass would look like.
    result = run(upstream.execute(resource=repo, action="create_github_issue", payload={"title": "bypass", "body": "x"}))
    assert result is not None
    assert len(recorded_issues()) == 1  # the bypass DID create a real side effect

    # The real, shipped path never calls `upstream` this way -- it is only
    # ever installed on a ProposalExecutionService, reached exclusively via
    # authorize_and_execute (see every other test in this module).


def test_non_vacuity_2_resource_metadata_checked_but_not_used_to_select_destination(mock_github):
    """Reproduces the Phase 2 PR #106 defect this proof's actuator design
    inherits the fix for: a wrapper whose declared ``.resource`` metadata
    matches, but whose underlying dispatch is hardcoded to write somewhere
    else entirely -- shown here via a raw dict-based "other destination"
    that never goes through the real HTTP/marker path at all. The real,
    shipped GitHubSandboxUpstream cannot express this: its ``resource`` IS
    ``actuator.config.repo``, the one and only value its real HTTP call can
    ever target."""
    other_destination_log: List[Any] = []

    class _VulnerableMetadataOnlyUpstream:
        def __init__(self, resource, hardcoded_call):
            self.resource = resource
            self._call = hardcoded_call

        async def __call__(self, action, payload):
            return await self._call(action, payload)

    async def hardcoded_elsewhere(action, payload):
        other_destination_log.append((action, payload))
        return {"ok": True}

    vulnerable = _VulnerableMetadataOnlyUpstream(resource="sandbox-owner/sandbox-repo", hardcoded_call=hardcoded_elsewhere)
    assert vulnerable.resource == "sandbox-owner/sandbox-repo"
    run(vulnerable("create_github_issue", {"title": "x", "body": "y"}))
    assert other_destination_log == [("create_github_issue", {"title": "x", "body": "y"})]
    assert recorded_issues() == []  # never reached the real sandbox at all

    # The real, shipped ProposalExecutionService refuses to even construct
    # against this object (no `.execute`).
    with pytest.raises(TypeError):
        async def _try():
            stack = await _stack(mock_github, tenants={"tenant-x": {}})
            ProposalExecutionService(
                proposals=stack.proposals, authority=stack.authority, engine=stack.engine,
                coordinator=stack.coordinator, upstream=vulnerable,
            )

        run(_try())


def test_non_vacuity_3_replay_path_allowing_a_second_external_issue(mock_github):
    """Reintroduces a non-atomic (always-succeeds) idempotency registry at
    the coordinator this stack drives, and shows a replay WRONGLY creates a
    second real issue -- proving test F (replay) is not vacuous."""
    tenant_id, op_id = f"tenant-{_uid()}", f"op-{_uid()}"

    class _AlwaysSucceedsIdempotency(InMemoryIdempotencyRegistry):
        async def reserve(self, key, *, tenant_id, binding=""):
            from mcc_core.idempotency import ReserveResult, ReserveStatus

            return ReserveResult(ReserveStatus.RESERVED, "reserved", binding=binding, fence="fence")

        async def commit_dispatch(self, key, *, tenant_id, fence):
            return True

        async def mark_executed(self, key, *, tenant_id, fence, binding="", result_ref=None):
            return True

    async def go():
        from mcc_core import (
            ActionPolicy, AuditLog, AuthorityModel, DecisionEngine, EnforcementCoordinator,
            ExecutionGate, InMemoryNonceRegistry, InMemoryVelocityRegistry, MandateRegistry,
            ProfileRegistry, SigningKey, Verdict,
        )
        from mcc_proposal import InMemoryProposalRegistry, MCCProposalService

        broken_idem = _AlwaysSucceedsIdempotency()
        proposals = InMemoryProposalRegistry()
        signing_key = SigningKey.generate("nv3-sandbox")
        engine = DecisionEngine(signing_key=signing_key, issuer="mcc/test", audience="test-gate",
                                policy_id="test/v1", policy_hash="sha256:test", token_ttl_seconds=60)
        gate = ExecutionGate(trusted_keys={signing_key.kid: signing_key.public_key()}, audience="test-gate",
                             nonce_registry=InMemoryNonceRegistry(), policy_hash="sha256:test")
        audit = AuditLog("/tmp/mcc-phase2-sandbox-nv3-audit.jsonl")
        coordinator = EnforcementCoordinator(gate=gate, idempotency=broken_idem, velocity=InMemoryVelocityRegistry(),
                                             audit=audit, profiles=ProfileRegistry())
        authority = AuthorityModel(
            registry=MandateRegistry.from_config({tenant_id: [{"authority": "execute"}]}),
            policies=[ActionPolicy(action="create_github_issue", requires="execute", on_mandate=Verdict.ALLOW,
                                   without_mandate=Verdict.DENY)],
            default=Verdict.DENY,
        )
        repo = "sandbox-owner/sandbox-repo"
        actuator = GitHubIssueActuator(GitHubActuatorConfig(mode="live", repo=repo, base_url=mock_github, token=None))
        upstream = GitHubSandboxUpstream(actuator)
        bridge = ProposalExecutionService(proposals=proposals, authority=authority, engine=engine,
                                          coordinator=coordinator, upstream=upstream)
        svc = MCCProposalService(proposals=proposals, durable_execution_state=broken_idem)

        payload = prepare_sandbox_issue_payload({"title": "nv3", "body": "x"}, tenant_id=tenant_id, logical_operation_id=op_id)
        await svc.submit_proposal(tenant_id=tenant_id, request={
            "logical_operation_id": op_id, "actor": "x", "action": "create_github_issue",
            "resource": repo, "payload": payload,
        })
        r1 = await bridge.authorize_and_execute(tenant_id=tenant_id, logical_operation_id=op_id)
        r2 = await bridge.authorize_and_execute(tenant_id=tenant_id, logical_operation_id=op_id)
        return r1, r2

    r1, r2 = run(go())
    assert r1.status == ProposalExecStatus.EXECUTED
    assert r2.status == ProposalExecStatus.EXECUTED  # WRONGLY executed again
    assert len(recorded_issues()) == 2  # a second real issue was WRONGLY created


def test_non_vacuity_4_unbound_reconciliation_accepting_any_matching_looking_issue(mock_github):
    """Reproduces the exact Blocker 1 defect this proof's evidence verifier
    is built to avoid: a vulnerable reconciler that treats ANY non-None
    evidence dict as sufficient, calling the real ``resolve_unknown``
    directly. Shows this WRONGLY resolves using unrelated evidence; the
    real, shipped ``reconcile_proposal_operation`` + sandbox evidence
    verifier correctly refuses the identical scenario."""
    tenant_id, op_id = f"tenant-{_uid()}", f"op-{_uid()}"

    async def go():
        stack = await _stack(mock_github, tenants={tenant_id: {}})
        await _propose(stack, tenant_id, op_id, resource=stack.repo)
        from gateway.proposal_execution_service import ResourceBoundUpstream

        async def pure_crash(*, resource, action, payload):
            raise ConnectionError("never reached the server")

        stack.bridge._upstream = ResourceBoundUpstream(resource=stack.repo, dispatch=pure_crash)
        await stack.bridge.authorize_and_execute(tenant_id=tenant_id, logical_operation_id=op_id)

        from mcc_core.signing import hash_document

        state = await stack.idempotency.get_state(op_id, tenant_id=tenant_id)
        unrelated_evidence = {"marker": "found"}  # the exact original defect
        result_ref = hash_document({"evidence": unrelated_evidence})
        vulnerable_result = await stack.idempotency.resolve_unknown(
            op_id, tenant_id=tenant_id, expected_generation=state.generation, result_ref=result_ref,
        )

        # The real, shipped path on a FRESH, otherwise-identical operation.
        stack2 = await _stack(mock_github, tenants={tenant_id: {}}, repo=stack.repo)
        op_id2 = f"{op_id}-real"
        await _propose(stack2, tenant_id, op_id2, resource=stack2.repo)
        stack2.bridge._upstream = ResourceBoundUpstream(resource=stack2.repo, dispatch=pure_crash)
        await stack2.bridge.authorize_and_execute(tenant_id=tenant_id, logical_operation_id=op_id2)

        async def unrelated_verifier(**kw):
            return {"marker": "found"}

        real_recon = await reconcile_proposal_operation(
            proposals=stack2.proposals, idempotency=stack2.idempotency, authority=stack2.authority,
            tenant_id=tenant_id, logical_operation_id=op_id2, verify_external_evidence=unrelated_verifier,
        )
        return vulnerable_result, real_recon

    vulnerable_result, real_recon = run(go())
    from mcc_core.idempotency import ReconcileStatus

    assert vulnerable_result.status == ReconcileStatus.RESOLVED  # WRONGLY resolved
    assert real_recon.outcome == ReconcileOutcome.EVIDENCE_MISMATCH  # correctly refused


def test_non_vacuity_5_post_dispatch_failure_released_and_retried_instead_of_unknown(mock_github):
    """Reintroduces a coordinator whose executor-exception handling
    releases the durable reservation (instead of preserving UNKNOWN),
    allowing a retry to WRONGLY create a second real issue after an
    ambiguous post-dispatch failure -- proving test I/J are not vacuous."""
    tenant_id, op_id = f"tenant-{_uid()}", f"op-{_uid()}"

    class _ReleaseInsteadOfUnknownIdempotency(InMemoryIdempotencyRegistry):
        async def mark_unknown(self, key, *, tenant_id, fence):
            # THE DEFECT: instead of durably preserving UNKNOWN, discards
            # the record entirely -- freeing the (tenant_id, key) identity
            # for a fresh, unprotected admission, exactly as if the prior
            # attempt had never happened.
            self._store.pop((tenant_id, key), None)
            return True

    async def go():
        from mcc_core import (
            ActionPolicy, AuditLog, AuthorityModel, DecisionEngine, EnforcementCoordinator,
            ExecutionGate, InMemoryNonceRegistry, InMemoryVelocityRegistry, MandateRegistry,
            ProfileRegistry, SigningKey, Verdict,
        )
        from mcc_proposal import InMemoryProposalRegistry, MCCProposalService

        broken_idem = _ReleaseInsteadOfUnknownIdempotency()
        proposals = InMemoryProposalRegistry()
        signing_key = SigningKey.generate("nv5-sandbox")
        engine = DecisionEngine(signing_key=signing_key, issuer="mcc/test", audience="test-gate",
                                policy_id="test/v1", policy_hash="sha256:test", token_ttl_seconds=60)
        gate = ExecutionGate(trusted_keys={signing_key.kid: signing_key.public_key()}, audience="test-gate",
                             nonce_registry=InMemoryNonceRegistry(), policy_hash="sha256:test")
        audit = AuditLog("/tmp/mcc-phase2-sandbox-nv5-audit.jsonl")
        coordinator = EnforcementCoordinator(gate=gate, idempotency=broken_idem, velocity=InMemoryVelocityRegistry(),
                                             audit=audit, profiles=ProfileRegistry())
        authority = AuthorityModel(
            registry=MandateRegistry.from_config({tenant_id: [{"authority": "execute"}]}),
            policies=[ActionPolicy(action="create_github_issue", requires="execute", on_mandate=Verdict.ALLOW,
                                   without_mandate=Verdict.DENY)],
            default=Verdict.DENY,
        )
        repo = "sandbox-owner/sandbox-repo"

        async def pure_crash(*, resource, action, payload):
            raise ConnectionError("ambiguous failure")

        from gateway.proposal_execution_service import ResourceBoundUpstream

        crashing_upstream = ResourceBoundUpstream(resource=repo, dispatch=pure_crash)
        bridge = ProposalExecutionService(proposals=proposals, authority=authority, engine=engine,
                                          coordinator=coordinator, upstream=crashing_upstream)
        svc = MCCProposalService(proposals=proposals, durable_execution_state=broken_idem)

        payload = prepare_sandbox_issue_payload({"title": "nv5", "body": "x"}, tenant_id=tenant_id, logical_operation_id=op_id)
        await svc.submit_proposal(tenant_id=tenant_id, request={
            "logical_operation_id": op_id, "actor": "x", "action": "create_github_issue",
            "resource": repo, "payload": payload,
        })
        first = await bridge.authorize_and_execute(tenant_id=tenant_id, logical_operation_id=op_id)

        actuator = GitHubIssueActuator(GitHubActuatorConfig(mode="live", repo=repo, base_url=mock_github, token=None))
        bridge._upstream = GitHubSandboxUpstream(actuator)
        retry = await bridge.authorize_and_execute(tenant_id=tenant_id, logical_operation_id=op_id)
        return first, retry

    first, retry = run(go())
    assert first.status == ProposalExecStatus.EXECUTION_FAILED
    assert retry.status == ProposalExecStatus.EXECUTED  # WRONGLY retried and dispatched
    assert len(recorded_issues()) == 1  # the retry WRONGLY created a real issue
