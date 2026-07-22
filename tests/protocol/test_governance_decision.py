"""GovernanceDecision: envelope over the authoritative Decision (PR #49).

These tests pin the reconciliation with PR #43: GovernanceDecision wraps, never
replaces, mcc_client.Decision, and introduces no new verdicts or reason codes.
"""

from __future__ import annotations

import mcc_client
import mcc_protocol as mp
from mcc_client.contract import ContractErrorCode
from tests.protocol.conftest import allow_router, make_proposal


def _decision(verdict, **extra):
    p = make_proposal()
    data = {"decision": verdict, "reason": "r", "audit_id": "aud-9",
            "forward_context": dict(p.payload), "policy_ref": "sha256:pol",
            "trace_id": p.trace_id}
    data.update(extra)
    dec = mcc_client.Decision.from_response(
        data, requested_actor=p.actor, requested_action=p.action,
        requested_resource=p.resource, requested_payload=p.payload)
    return p, dec


def test_wraps_the_authoritative_decision():
    p, dec = _decision("ALLOW", decision_token={"kid": "k1"})
    gov = mp.GovernanceDecision.from_decision(p, dec)
    # The wrapped decision is held by reference — not re-derived.
    assert gov.decision is dec
    assert gov.verdict is dec.verdict
    assert gov.audit_reference == dec.audit_id
    assert gov.policy_hash == dec.policy_ref
    assert gov.decision_token == dec.decision_token
    assert gov.proposal_id == p.proposal_id
    assert gov.action_hash == p.action_hash and gov.nonce == p.nonce


def test_verdicts_are_the_existing_verdict_set():
    for v in ("ALLOW", "DENY", "ESCALATE", "CONSTRAIN"):
        p, dec = _decision(v)
        gov = mp.GovernanceDecision.from_decision(p, dec)
        assert gov.verdict in set(mcc_client.Verdict)


def test_reason_codes_are_from_the_existing_taxonomy():
    valid = {c.value for c in ContractErrorCode}
    p, dec = _decision("DENY")
    gov = mp.GovernanceDecision.from_decision(p, dec)
    assert gov.reason_codes == [ContractErrorCode.VERDICT_DENY.value]
    assert set(gov.reason_codes) <= valid
    # ESCALATE carries the escalate reason code.
    p, dec = _decision("ESCALATE")
    assert mp.GovernanceDecision.from_decision(p, dec).reason_codes == [
        ContractErrorCode.VERDICT_ESCALATE_REQUIRED.value]
    # ALLOW carries no blocking reason code.
    p, dec = _decision("ALLOW")
    assert mp.GovernanceDecision.from_decision(p, dec).reason_codes == []


def test_classification_helpers_match_verdict():
    p, dec = _decision("CONSTRAIN")
    gov = mp.GovernanceDecision.from_decision(p, dec)
    assert gov.executable and not gov.denied and not gov.needs_approval
    p, dec = _decision("DENY")
    assert mp.GovernanceDecision.from_decision(p, dec).denied


def test_to_dict_is_serializable_and_omits_the_raw_model():
    p = make_proposal()
    gov = mp.GovernanceDecision.from_decision(p, allow_router(p))
    d = gov.to_dict()
    import json
    json.dumps(d)  # must be JSON-serializable
    assert "decision" not in d  # the wrapped SDK model is not embedded in the dict
    assert d["verdict"] == "ALLOW" and d["has_decision_token"] is True
