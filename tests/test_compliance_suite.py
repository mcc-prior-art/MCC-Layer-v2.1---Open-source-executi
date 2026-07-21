"""Tests for the Integration Contract Compliance & Certification Suite (PR #44).

Deterministic and offline: every certification run drives a real, in-process
governed stack (via ``mcc_compliance``). The reference and VoltAgent adapters must
certify through the SAME framework-neutral boundary; a battery of deliberately
non-compliant test doubles must be rejected. A certification suite that only proves
the reference adapter passes would be insufficient — the negative adapters are the
point.
"""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
for p in (ROOT / "src", ROOT / "sdk" / "python" / "src", ROOT):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from mcc_client.contract import CONTRACT_VERSION  # noqa: E402

import mcc_compliance as mc  # noqa: E402
from mcc_compliance import (  # noqa: E402
    AdapterMetadata,
    AdapterOutcome,
    CaseStatus,
    CertificationStatus,
    ComplianceError,
    ComplianceErrorCode,
    run_compliance,
)
from mcc_compliance.adapters import ReferenceComplianceAdapter  # noqa: E402
from mcc_compliance.certification import certification_fingerprint  # noqa: E402
from mcc_compliance.registry import load_vectors, parse_manifest, register_adapter  # noqa: E402
from mcc_compliance.reporting import (  # noqa: E402
    certification_manifest,
    report_to_json,
    report_to_markdown,
)


# --------------------------------------------------------------------------- #
# Deliberately non-compliant test doubles (test-only; never registered as prod).
# --------------------------------------------------------------------------- #

def _meta(name: str, *, version: str = "0.0.1", cv: str = CONTRACT_VERSION) -> AdapterMetadata:
    return AdapterMetadata(name=name, version=version, implementation_id=f"test/{name}",
                           claimed_contract_version=cv, framework=None)


class AlwaysAllowAdapter:
    """Claims a successful execution for every scenario — including DENY/tamper."""
    def describe(self): return _meta("always-allow")
    def run_scenario(self, ctx): return AdapterOutcome(verdict="ALLOW", executed=True,
                                                       audit_valid=True)


class BypassAdapter:
    """Ignores the authorizer and fabricates an execution (a bypass claim)."""
    def describe(self): return _meta("bypass")
    def run_scenario(self, ctx):
        # Never touches the gate; just asserts it ran.
        return AdapterOutcome(verdict="ALLOW", executed=True, audit_valid=True)


class MalformedAdapter:
    """Returns something that is not an AdapterOutcome."""
    def describe(self): return _meta("malformed")
    def run_scenario(self, ctx): return {"verdict": "ALLOW", "executed": True}


class ExceptionAdapter:
    """Raises during evaluation."""
    def describe(self): return _meta("boom")
    def run_scenario(self, ctx): raise RuntimeError("adapter blew up")


class SkipAdapter:
    """Skips mandatory cases."""
    def describe(self): return _meta("skipper")
    def run_scenario(self, ctx):
        return AdapterOutcome(verdict="ALLOW", executed=False, skipped=True,
                              skip_reason="declined")


class UnknownVerdictAdapter:
    """Returns a verdict outside the contract's set."""
    def describe(self): return _meta("unknown-verdict")
    def run_scenario(self, ctx): return AdapterOutcome(verdict="MAYBE", executed=False)


class WrongVersionAdapter:
    """Behaves conformantly but claims a contract version it is not tested against."""
    def __init__(self): self._inner = ReferenceComplianceAdapter()
    def describe(self): return _meta("wrong-version", cv="2.0")
    def run_scenario(self, ctx): return self._inner.run_scenario(ctx)


class MissingAuditAdapter:
    """Conformant execution but never provides audit evidence."""
    def __init__(self): self._inner = ReferenceComplianceAdapter()
    def describe(self): return _meta("missing-audit")
    def run_scenario(self, ctx):
        out = self._inner.run_scenario(ctx)
        out.audit_valid = None
        return out


# --------------------------------------------------------------------------- #
# Module-scoped certification runs (each stands up a governed stack once).     #
# --------------------------------------------------------------------------- #

@pytest.fixture(scope="module")
def reference_report():
    return run_compliance(ReferenceComplianceAdapter(), "1.0")


@pytest.fixture(scope="module")
def voltagent_report():
    from mcc_compliance.adapters import VoltAgentComplianceAdapter
    return run_compliance(VoltAgentComplianceAdapter(), "1.0")


# --------------------------------------------------------------------------- #
# 1. Vector & manifest tests (no stack).                                      #
# --------------------------------------------------------------------------- #

def test_valid_manifest_loads_deterministically():
    vectors, digest = load_vectors("1.0")
    assert len(vectors) >= 18
    assert digest.startswith("sha256:")
    ids = [v.id for v in vectors]
    assert ids == sorted(ids)                     # deterministic ordering
    assert all(v.id.startswith("IC-V1-") for v in vectors)
    assert all(v.invariant and v.requirement for v in vectors)  # every vector maps to a requirement


def test_manifest_digest_is_stable():
    _, d1 = load_vectors("1.0")
    _, d2 = load_vectors("1.0")
    assert d1 == d2


def test_unsupported_contract_version_rejected_no_fallback():
    with pytest.raises(ComplianceError) as ei:
        load_vectors("2.0")
    assert ei.value.code is ComplianceErrorCode.UNSUPPORTED_CONTRACT_VERSION


def test_unknown_minor_within_major_has_no_published_vectors():
    with pytest.raises(ComplianceError) as ei:
        load_vectors("1.9")
    assert ei.value.code is ComplianceErrorCode.UNSUPPORTED_CONTRACT_VERSION


def _base_manifest():
    m, _ = mc.registry.load_manifest("1.0")
    return copy.deepcopy(m)


def test_duplicate_vector_id_rejected():
    m = _base_manifest()
    m["vectors"].append(copy.deepcopy(m["vectors"][0]))
    with pytest.raises(ComplianceError) as ei:
        parse_manifest(m, "1.0")
    assert ei.value.code is ComplianceErrorCode.DUPLICATE_VECTOR_ID


def test_unknown_scenario_type_rejected():
    m = _base_manifest()
    m["vectors"][0]["scenario"]["driver"] = "teleport"
    with pytest.raises(ComplianceError) as ei:
        parse_manifest(m, "1.0")
    assert ei.value.code is ComplianceErrorCode.UNKNOWN_VECTOR_TYPE


def test_missing_required_vector_field_rejected():
    m = _base_manifest()
    del m["vectors"][0]["invariant"]
    with pytest.raises(ComplianceError) as ei:
        parse_manifest(m, "1.0")
    assert ei.value.code is ComplianceErrorCode.VECTOR_PARSE_ERROR


def test_manifest_contract_version_mismatch_rejected():
    m = _base_manifest()
    m["contract_version"] = "1.5"
    with pytest.raises(ComplianceError) as ei:
        parse_manifest(m, "1.0")
    assert ei.value.code is ComplianceErrorCode.MANIFEST_INVALID


# --------------------------------------------------------------------------- #
# 2. Runner tests — reference passes; negatives are rejected.                 #
# --------------------------------------------------------------------------- #

def test_reference_adapter_is_certified(reference_report):
    assert reference_report.status is CertificationStatus.CERTIFIED
    assert reference_report.totals.mandatory_total >= 18
    assert reference_report.totals.mandatory_passed == reference_report.totals.mandatory_total
    assert reference_report.totals.failed == 0 and reference_report.totals.errored == 0


def test_results_are_ordered_deterministically(reference_report):
    ids = [r.vector_id for r in reference_report.results]
    assert ids == sorted(ids)


def test_always_allow_is_not_certified():
    rep = run_compliance(AlwaysAllowAdapter(), "1.0")
    assert rep.status is CertificationStatus.NOT_CERTIFIED
    codes = {r.failure_code for r in rep.results if r.status is CaseStatus.FAIL}
    # It fabricated executions on fail-closed cases (DENY/tamper/expired/...).
    assert ComplianceErrorCode.FABRICATED_EXECUTION.value in codes


def test_bypass_is_not_certified():
    rep = run_compliance(BypassAdapter(), "1.0")
    assert rep.status is CertificationStatus.NOT_CERTIFIED


def test_malformed_adapter_errors_never_certifies():
    rep = run_compliance(MalformedAdapter(), "1.0")
    assert rep.status is CertificationStatus.ERROR
    assert any(r.failure_code == ComplianceErrorCode.NORMALIZATION_FAILED.value
               for r in rep.results)


def test_exception_adapter_errors_never_certifies():
    rep = run_compliance(ExceptionAdapter(), "1.0")
    assert rep.status is CertificationStatus.ERROR
    assert all(r.status is CaseStatus.ERROR for r in rep.results)
    assert all(r.failure_code == ComplianceErrorCode.ADAPTER_EXCEPTION.value
               for r in rep.results)


def test_mandatory_skip_is_not_certified():
    rep = run_compliance(SkipAdapter(), "1.0")
    assert rep.status is CertificationStatus.NOT_CERTIFIED
    assert any(r.status is CaseStatus.SKIP and
               r.failure_code == ComplianceErrorCode.MANDATORY_SKIP.value
               for r in rep.results)


def test_unknown_verdict_is_not_certified():
    rep = run_compliance(UnknownVerdictAdapter(), "1.0")
    assert rep.status is CertificationStatus.NOT_CERTIFIED
    assert any(r.failure_code == ComplianceErrorCode.UNKNOWN_VERDICT.value
               for r in rep.results)


def test_wrong_version_is_not_certified():
    rep = run_compliance(WrongVersionAdapter(), "1.0")
    assert rep.status is CertificationStatus.NOT_CERTIFIED
    assert any("contract version" in reason for reason in rep.certification.reasons)


def test_missing_audit_is_not_certified():
    rep = run_compliance(MissingAuditAdapter(), "1.0")
    assert rep.status is CertificationStatus.NOT_CERTIFIED
    assert any(r.failure_code == ComplianceErrorCode.AUDIT_NOT_VERIFIED.value
               for r in rep.results)


# --------------------------------------------------------------------------- #
# 3. Report + fingerprint tests.                                              #
# --------------------------------------------------------------------------- #

def test_json_report_is_valid_and_clean(reference_report):
    body = report_to_json(reference_report)
    text = json.dumps(body)
    assert body["report_schema_version"] == "1"
    assert body["certification"]["status"] == "CERTIFIED"
    assert body["contract_version"] == "1.0"
    # No secrets / absolute paths / env noise. (Invariant *names* like
    # "signature_verified" are contract vocabulary, not leaked material.)
    for banned in (str(ROOT), "/home/", "api_key", "operator_key",
                   "-----BEGIN", "PRIVATE KEY", "public_key_b64"):
        assert banned not in text, f"report leaked {banned!r}"


def test_markdown_report_has_required_fields(reference_report):
    md = report_to_markdown(reference_report)
    for needed in ("reference-governed-agent", "Contract version", "Certification status",
                   "CERTIFIED", "Vector manifest digest", "Certification fingerprint",
                   "Totals", "the exact adapter version"):
        assert needed in md, f"markdown missing {needed!r}"


def test_fingerprint_is_stable_across_runs():
    a = run_compliance(ReferenceComplianceAdapter(), "1.0")
    b = run_compliance(ReferenceComplianceAdapter(), "1.0")
    assert a.certification.fingerprint == b.certification.fingerprint


def test_fingerprint_excludes_timestamp():
    a = run_compliance(ReferenceComplianceAdapter(), "1.0", include_timestamp=True)
    b = run_compliance(ReferenceComplianceAdapter(), "1.0", include_timestamp=False)
    assert a.generated_at is not None and b.generated_at is None
    assert a.certification.fingerprint == b.certification.fingerprint


def test_fingerprint_changes_with_adapter_version(reference_report):
    results = reference_report.results
    m1 = _meta("x", version="1.0.0")
    m2 = _meta("x", version="2.0.0")
    fp1 = certification_fingerprint(m1, "1.0", "sha256:d", results)
    fp2 = certification_fingerprint(m2, "1.0", "sha256:d", results)
    assert fp1 != fp2


def test_fingerprint_changes_with_manifest_digest(reference_report):
    results = reference_report.results
    m = _meta("x")
    fp1 = certification_fingerprint(m, "1.0", "sha256:aaa", results)
    fp2 = certification_fingerprint(m, "1.0", "sha256:bbb", results)
    assert fp1 != fp2


def test_fingerprint_changes_with_contract_version(reference_report):
    results = reference_report.results
    m = _meta("x")
    assert (certification_fingerprint(m, "1.0", "sha256:d", results)
            != certification_fingerprint(m, "1.1", "sha256:d", results))


# --------------------------------------------------------------------------- #
# 4. CLI tests.                                                               #
# --------------------------------------------------------------------------- #

def test_cli_certified_exit_zero():
    from mcc_compliance.cli import main
    assert main(["certify", "--adapter", "reference", "--contract-version", "1.0"]) == 0


def test_cli_not_certified_exit_one():
    from mcc_compliance.cli import main
    register_adapter("test-always-allow", AlwaysAllowAdapter)
    assert main(["certify", "--adapter", "test-always-allow", "--contract-version", "1"]) == 1


def test_cli_error_exit_two_on_unsupported_version():
    from mcc_compliance.cli import main
    assert main(["certify", "--adapter", "reference", "--contract-version", "2.0"]) == 2


def test_cli_error_exit_two_on_unknown_adapter():
    from mcc_compliance.cli import main
    assert main(["certify", "--adapter", "does-not-exist", "--contract-version", "1.0"]) == 2


def test_cli_writes_reports(tmp_path):
    from mcc_compliance.cli import main
    rc = main(["certify", "--adapter", "reference", "--contract-version", "1.0",
               "--output-dir", str(tmp_path)])
    assert rc == 0
    base = tmp_path / "reference-governed-agent" / "1.0"
    for name in ("report.json", "report.md", "certification.json"):
        assert (base / name).is_file()
    cert = json.loads((base / "certification.json").read_text())
    assert cert["certification_status"] == "CERTIFIED"
    assert cert["certified_contract_version"] == "1.0"


def test_cli_json_mode_is_valid(capsys):
    from mcc_compliance.cli import main
    main(["certify", "--adapter", "reference", "--contract-version", "1.0", "--json"])
    out = capsys.readouterr().out
    body = json.loads(out)
    assert body["certification"]["status"] == "CERTIFIED"


# --------------------------------------------------------------------------- #
# 5. Integration + neutrality.                                               #
# --------------------------------------------------------------------------- #

def test_voltagent_certified_through_same_boundary(voltagent_report):
    assert voltagent_report.status is CertificationStatus.CERTIFIED
    assert voltagent_report.adapter_metadata.name == "voltagent"
    assert voltagent_report.adapter_metadata.framework == "voltagent"


def test_voltagent_and_reference_use_the_same_protocol():
    from mcc_compliance.adapters import VoltAgentComplianceAdapter
    from mcc_compliance.protocol import ComplianceAdapter
    assert isinstance(ReferenceComplianceAdapter(), ComplianceAdapter)
    assert isinstance(VoltAgentComplianceAdapter(), ComplianceAdapter)


def test_no_framework_specific_names_in_normative_vectors():
    m, _ = mc.registry.load_manifest("1.0")
    text = json.dumps(m).lower()
    for fw in ("voltagent", "langgraph", "crewai", "autogen", "semantic_kernel", "openai"):
        assert fw not in text, f"normative vectors leaked framework name {fw!r}"


def test_certification_manifest_never_claims_adapter_certified_on_failure():
    rep = run_compliance(AlwaysAllowAdapter(), "1.0")
    cert = certification_manifest(rep)
    assert cert["certification_status"] == "NOT_CERTIFIED"
    assert cert["certified_contract_version"] is None
