"""Structural validation + deterministic evidence; never certification (PR #50)."""

from __future__ import annotations

from mcc_adapter_sdk import (
    AdapterContext,
    AdapterMetadata,
    AdapterRunner,
    generate_adapter_evidence,
    validate_adapter,
)
from tests.adapter_sdk.conftest import GoodAdapter, make_router


def test_valid_report():
    report = validate_adapter(GoodAdapter())
    assert report.structurally_valid
    assert report.status == "VALIDATION_PASSED"
    assert all(c["passed"] for c in report.checks)


def test_invalid_report_never_raises():
    class Broken(GoodAdapter):
        def describe(self):
            return AdapterMetadata.create(adapter_id="", adapter_version="1", framework_name="f")
    report = validate_adapter(Broken())  # must not raise
    assert not report.structurally_valid
    assert report.status == "VALIDATION_FAILED"


def test_deterministic_validation():
    a, b = validate_adapter(GoodAdapter()), validate_adapter(GoodAdapter())
    assert a.to_dict() == b.to_dict()


def test_validation_never_claims_certification():
    report = validate_adapter(GoodAdapter())
    text = str(report.to_dict()).lower()
    for banned in ("certified", "certification", "official compliance",
                   "production approval", "trusted", "approved"):
        # The only allowed occurrences are inside the explicit NEGATIVE disclaimer.
        if banned in text:
            assert "not " in text  # disclaimer present
    assert report.to_dict()["status"] in ("VALIDATION_PASSED", "VALIDATION_FAILED")
    assert "disclaimer" in report.to_dict()


def test_deterministic_evidence():
    a = GoodAdapter()
    report = validate_adapter(a)
    res = AdapterRunner(a, make_router("ALLOW")).run(
        AdapterContext.create(actor_reference="x"), "hello")
    e1 = generate_adapter_evidence(a, run_result=res, validation_report=report, write=False)
    e2 = generate_adapter_evidence(a, run_result=res, validation_report=report, write=False)
    assert e1 == e2


def test_evidence_is_sanitized_and_distinct_from_certification():
    e = generate_adapter_evidence(GoodAdapter(), write=False)
    import json
    text = json.dumps(e).lower()
    for bad in ("api_key", "operator_key", "secret", "private", "-----begin"):
        assert bad not in text
    assert e["evidence_format"] == "mcc-adapter-sdk-evidence/1"
    assert "certification" in e["note"].lower() and "not certification" in e["note"].lower()


def test_evidence_excludes_nondeterministic_identifiers():
    a = GoodAdapter()
    res = AdapterRunner(a, make_router("ALLOW")).run(
        AdapterContext.create(actor_reference="x"), "hello")
    e = generate_adapter_evidence(a, run_result=res, write=False)
    import json
    text = json.dumps(e)
    # No random proposal id / nonce / audit id / timestamp in the evidence.
    assert res.governance_decision.decision_id not in text
    assert "nonce" not in text
    assert res.proposal_id not in text
