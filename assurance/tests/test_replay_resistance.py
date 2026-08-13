"""Workstream E -- Replay Resistance (PR #71).

Scope, stated honestly up front (see ``docs/ASSUMPTIONS_AND_LIMITS.md``):
this environment has no Docker daemon and no multi-host infrastructure, so
the task's full "multi-node/Redis-failover/network-partition" scope is NOT
exercised here. What IS exercised, over real HTTP against two genuinely
independent OS processes sharing one real ``redis-server`` instance (no
mocking): cross-INSTANCE replay rejection (a nonce/challenge consumed on
one actuator process cannot be reused on a second, independent process),
and fail-closed behavior when the shared backend becomes unreachable. This
is single-node, cross-process replay resistance -- a real, narrower, but
genuine property; not a substitute for multi-node cluster/failover testing.
"""

from __future__ import annotations

import uuid

import pytest

from assurance.sut.replay_cluster import build_replay_resistance_cluster


@pytest.fixture(scope="module")
def cluster():
    with build_replay_resistance_cluster() as c:
        yield c


def test_e1_cross_instance_execution_succeeds(cluster):
    """Baseline: a challenge issued by instance A can be completed on
    instance B -- proves the shared Redis backend genuinely unifies state
    across processes (not just that replay fails; that recognition ACROSS
    instances works at all)."""
    before = cluster.notification_receipt_count()
    tx = str(uuid.uuid4())

    proposal = cluster.propose(actuator_url=cluster.actuator_a_url, transaction_id=tx, idempotency_key=tx)
    assert proposal["outcome"] == "CONSENSUS_REQUIRED"
    votes = cluster.votes(payload=cluster.canonical_action(proposal["_request"]), nonce=proposal["nonce"])

    result = cluster.submit(actuator_url=cluster.actuator_b_url, proposal=proposal, votes=votes)

    assert result["outcome"] == "ALLOW"
    assert result["executed"] is True
    assert cluster.notification_receipt_count() == before + 1


def test_e2_replay_on_the_originating_instance_after_cross_instance_completion_is_rejected(cluster):
    """The core cross-instance property: consume a challenge on B, then
    replay the identical challenge_id + votes on A (the instance that
    ISSUED it) -- A must see it as already consumed via the shared backend,
    not honor it as if its own local state had never seen it."""
    before = cluster.notification_receipt_count()
    tx = str(uuid.uuid4())

    proposal = cluster.propose(actuator_url=cluster.actuator_a_url, transaction_id=tx, idempotency_key=tx)
    votes = cluster.votes(payload=cluster.canonical_action(proposal["_request"]), nonce=proposal["nonce"])
    first = cluster.submit(actuator_url=cluster.actuator_b_url, proposal=proposal, votes=votes)
    assert first["executed"] is True
    assert cluster.notification_receipt_count() == before + 1

    replay = cluster.submit(actuator_url=cluster.actuator_a_url, proposal=proposal, votes=votes)

    assert not (replay["outcome"] == "ALLOW" and replay["executed"] is True)
    assert cluster.notification_receipt_count() == before + 1


def test_e3_replay_on_the_same_instance_is_also_rejected(cluster):
    before = cluster.notification_receipt_count()
    tx = str(uuid.uuid4())

    proposal = cluster.propose(actuator_url=cluster.actuator_b_url, transaction_id=tx, idempotency_key=tx)
    votes = cluster.votes(payload=cluster.canonical_action(proposal["_request"]), nonce=proposal["nonce"])
    first = cluster.submit(actuator_url=cluster.actuator_b_url, proposal=proposal, votes=votes)
    assert first["executed"] is True

    replay = cluster.submit(actuator_url=cluster.actuator_b_url, proposal=proposal, votes=votes)

    assert not (replay["outcome"] == "ALLOW" and replay["executed"] is True)
    assert cluster.notification_receipt_count() == before + 1


def test_e4_shared_backend_unreachable_fails_closed(cluster):
    """When the shared Redis instance is unreachable, the actuator must
    DENY rather than silently fall back to an un-shared, un-safe local
    check (or, worse, fail open)."""
    tx = str(uuid.uuid4())
    proposal = cluster.propose(actuator_url=cluster.actuator_a_url, transaction_id=tx, idempotency_key=tx)
    votes = cluster.votes(payload=cluster.canonical_action(proposal["_request"]), nonce=proposal["nonce"])

    cluster.kill_redis()
    try:
        result = cluster.submit(actuator_url=cluster.actuator_b_url, proposal=proposal, votes=votes)
    finally:
        pass  # this cluster's Redis is deliberately not restarted -- see the module docstring's scope note

    assert not (result.get("outcome") == "ALLOW" and result.get("executed") is True)
