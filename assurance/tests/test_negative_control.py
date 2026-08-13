"""Negative Control (PR #71).

A suite that always reports PASS is not evidence of anything -- it could
just as easily never be exercising the properties it claims to check. This
module runs a subset of Workstream A's real attacks against a DELIBERATELY
vulnerable reference actuator (``assurance/sut/vulnerable_target.py``,
never the real ``egress_proxy``) and asserts the attacks SUCCEED against
it, naming exactly which invariants the vulnerable target violates.

This is the control arm of the experiment: the real actuator's Workstream
A/B/C/D/F/G tests demonstrate the invariants hold there; this module
demonstrates the SAME test methodology correctly reports failure against a
system that does not hold them -- proving the suite has genuine
discriminating power, not just a tendency to pass.
"""

from __future__ import annotations

import uuid

import httpx

from assurance.sut.vulnerable_target import VIOLATED_INVARIANTS, spawn_negative_control_environment


def test_nc1_vulnerable_target_executes_with_no_authentication_and_no_consensus():
    """The real actuator requires an x-api-key AND a two-round N-of-M
    consensus handshake before ANY execution (Workstream A, A1/A2). This
    target has neither -- a single unauthenticated call must execute
    immediately."""
    with spawn_negative_control_environment() as env:
        before = env.notification_receipt_count()
        tx = str(uuid.uuid4())
        body = {"recipient": "ops", "message": "negative-control-probe", "correlation_id": tx}

        r = httpx.post(
            f"{env.target.base_url}/v1/http/execute",
            json={"method": "POST", "url": f"{env.notify_url}/send_notification", "headers": {}, "body": body,
                  "actor": "attacker-with-no-credentials", "resource": "anything"},
            timeout=15.0,
        )
        result = r.json()

        assert result["outcome"] == "ALLOW" and result["executed"] is True, (
            "the negative control was expected to be exploitable via unauthenticated, "
            "consensus-free execution, but it was not -- see assurance/sut/vulnerable_target.py"
        )
        assert env.notification_receipt_count() == before + 1


def test_nc2_vulnerable_target_has_no_replay_protection():
    """The real actuator's challenge is single-use (Workstream A, A3). This
    target has no challenge at all -- the identical request must execute
    again on resubmission."""
    with spawn_negative_control_environment() as env:
        before = env.notification_receipt_count()
        tx = str(uuid.uuid4())
        req = {"method": "POST", "url": f"{env.notify_url}/send_notification", "headers": {},
               "body": {"recipient": "ops", "message": "replay-probe", "correlation_id": tx},
               "actor": "attacker", "resource": "anything"}

        first = httpx.post(f"{env.target.base_url}/v1/http/execute", json=req, timeout=15.0).json()
        second = httpx.post(f"{env.target.base_url}/v1/http/execute", json=req, timeout=15.0).json()

        assert first["executed"] is True and second["executed"] is True, (
            "the negative control was expected to execute the identical request twice "
            "(no replay protection), but it did not"
        )
        assert env.notification_receipt_count() == before + 2


def test_nc3_vulnerable_target_accepts_garbage_votes():
    """The real actuator rejects a request bearing malformed/absent votes
    outright once consensus is required (Workstream A/C throughout). This
    target ignores the ``votes`` field entirely."""
    with spawn_negative_control_environment() as env:
        before = env.notification_receipt_count()
        tx = str(uuid.uuid4())
        req = {"method": "POST", "url": f"{env.notify_url}/send_notification", "headers": {},
               "body": {"recipient": "ops", "message": "garbage-votes-probe", "correlation_id": tx},
               "actor": "attacker", "resource": "anything",
               "challenge_id": "not-a-real-challenge", "votes": ["not", "even", "vote", "objects"]}

        result = httpx.post(f"{env.target.base_url}/v1/http/execute", json=req, timeout=15.0).json()

        assert result["executed"] is True, (
            "the negative control was expected to execute despite structurally invalid votes, "
            "but it did not"
        )
        assert env.notification_receipt_count() == before + 1


def test_nc4_violated_invariants_are_named():
    """The negative control documents, in one place, exactly which real
    invariants it deliberately violates -- reused as the failure_scenario
    text a reviewer sees, not left implicit."""
    assert len(VIOLATED_INVARIANTS) >= 4
    for invariant in VIOLATED_INVARIANTS:
        assert isinstance(invariant, str) and invariant
