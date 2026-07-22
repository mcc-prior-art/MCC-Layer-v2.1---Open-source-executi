"""AdapterRunner: mandatory pipeline, no bypass, fail-closed (PR #50)."""

from __future__ import annotations

from typing import Any


import mcc_protocol as mp
from mcc_adapter_sdk import AdapterRunner
from mcc_client.exceptions import MCCTransportError
from tests.adapter_sdk.conftest import GoodAdapter, make_router


def test_full_flow_traverses_the_mandatory_pipeline(good_adapter, context):
    runner = AdapterRunner(good_adapter, make_router("ALLOW"))
    res = runner.run(context, "hello")
    assert res.ok
    # Every one of the 8 canonical ingress stages ran.
    assert res.pipeline_summary["stages_completed"] == [s.value for s in mp.PIPELINE_STAGES]
    assert res.native_response == {"verdict": "ALLOW", "executable": True}


def test_decision_token_and_verdict_semantics_preserved(good_adapter, context):
    runner = AdapterRunner(good_adapter, make_router("ALLOW"))
    res = runner.run(context, "hello")
    gd = res.governance_decision
    assert gd.verdict is mp.Verdict.ALLOW           # existing verdict set
    assert gd.decision is not None                  # wraps the authoritative Decision
    assert gd.has_decision_token                    # Decision Token preserved
    assert res.proposal_hash and res.proposal_hash.startswith("sha256:")


def test_deny_produces_no_execution_and_a_native_response(good_adapter, context):
    runner = AdapterRunner(good_adapter, make_router("DENY"))
    res = runner.run(context, "hello")
    assert res.ok  # the run completed (a DENY is a valid governed outcome)
    assert res.governance_decision.verdict is mp.Verdict.DENY
    assert res.native_response == {"verdict": "DENY", "executable": False}


def test_pipeline_failure_prevents_success(good_adapter, context):
    # A gateway/transport failure inside routing must fail closed — no native response.
    runner = AdapterRunner(good_adapter, make_router(raises=MCCTransportError("down")))
    res = runner.run(context, "hello")
    assert not res.ok
    assert res.native_response is None
    assert res.error and res.error["stage"] == "routing"


def test_translation_failure_fails_closed(context):
    class BadProposal(GoodAdapter):
        def to_proposal(self, ctx, native):
            raise RuntimeError("boom")
    res = AdapterRunner(BadProposal(), make_router("ALLOW")).run(context, "x")
    assert not res.ok and res.native_response is None
    assert res.error["stage"] == "to_proposal"


def test_response_translation_failure_fails_closed(context):
    class BadResponse(GoodAdapter):
        def to_response(self, decision):
            raise RuntimeError("boom")
    res = AdapterRunner(BadResponse(), make_router("ALLOW")).run(context, "x")
    assert not res.ok and res.native_response is None
    assert res.error["stage"] == "to_response"


def test_adapter_returning_non_proposal_fails_closed(context):
    class NotAProposal(GoodAdapter):
        def to_proposal(self, ctx, native) -> Any:
            return {"not": "a proposal"}
    res = AdapterRunner(NotAProposal(), make_router("ALLOW")).run(context, "x")
    assert not res.ok and res.error["stage"] == "to_proposal"


def test_runner_has_no_bypass_or_authorization_surface(good_adapter):
    runner = AdapterRunner(good_adapter, make_router("ALLOW"))
    for forbidden in ("authorize", "execute", "enforce", "sign", "issue_token",
                      "evaluate_policy", "allow", "approve"):
        assert not hasattr(runner, forbidden)


def test_result_to_dict_is_serializable(good_adapter, context):
    import json
    res = AdapterRunner(good_adapter, make_router("ALLOW")).run(context, "hello")
    json.dumps(res.to_dict())
