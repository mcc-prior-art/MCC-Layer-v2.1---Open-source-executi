"""System-Under-Test smoke test (PR #71).

Proves the real, three-subprocess deployment (real Gateway, real
``egress_proxy`` actuator, real ``pilot_notify`` external-effect sink, all
over genuine loopback HTTP) that every later workstream builds on actually
boots and completes one full authorized propose -> challenge -> vote ->
execute -> observe-external-effect cycle. This is not itself an adversarial
test; it is the harness's own positive-path proof of life, and doubles as
the baseline every attack test in Workstream A diffs against (an attack
that also fails to produce an external effect here proves nothing unless
this baseline first proves the effect CAN occur on an authorized path).
"""

from __future__ import annotations

import uuid


def test_authorized_notification_reaches_the_external_effect_sink(sut):
    before = sut.notification_receipt_count()

    tx = str(uuid.uuid4())
    proposal = sut.propose_notification(transaction_id=tx, idempotency_key=tx)
    assert proposal["outcome"] == "CONSENSUS_REQUIRED"
    assert proposal["executed"] is False

    votes = sut.actuator_votes(
        action="http.request", payload=sut.canonical_notification_action(proposal),
        actor="agent/egress", resource="notify", nonce=proposal["nonce"],
    )
    result = sut.submit_notification_votes(proposal, votes=votes)

    assert result["outcome"] == "ALLOW"
    assert result["executed"] is True
    assert result["upstream_status"] == 200

    after = sut.notification_receipt_count()
    assert after == before + 1


def test_unauthorized_notification_without_votes_produces_no_effect(sut):
    before = sut.notification_receipt_count()

    tx = str(uuid.uuid4())
    proposal = sut.propose_notification(transaction_id=tx, idempotency_key=tx)
    assert proposal["outcome"] == "CONSENSUS_REQUIRED"
    assert proposal["executed"] is False

    after = sut.notification_receipt_count()
    assert after == before
