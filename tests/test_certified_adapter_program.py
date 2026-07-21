"""Tests for the Certified Adapter Program (PR #46).

Certification is derived exclusively from official compliance evidence, is
deterministic (no wall-clock time), binds its contract + vector-set versions, and
fails closed. The repository manifest is regenerated from real evidence and any
tamper/stale/regression is detected. Offline and deterministic.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
for p in (ROOT / "src", ROOT / "sdk" / "python" / "src", ROOT):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from mcc_client.contract import CONTRACT_VERSION  # noqa: E402

from mcc_compliance import (  # noqa: E402
    AdapterMetadata,
    AdapterOutcome,
    ProgramStatus,
    build_manifest,
    certify,
    verify_manifest,
)
from mcc_compliance.adapters import (  # noqa: E402
    ReferenceComplianceAdapter,
    VoltAgentComplianceAdapter,
)
from mcc_compliance.program import (  # noqa: E402
    MANIFEST_PATH,
    ScenarioOutcome,
    _evidence_digest,
)
from mcc_compliance.protocol import ComplianceAdapter  # noqa: E402

PROGRAM_SRC = (ROOT / "src" / "mcc_compliance" / "program.py").read_text(encoding="utf-8")


# --- a deliberately non-compliant adapter (test-only) ---------------------- #

class NonConformingAdapter:
    """Fabricates a successful execution for every scenario — always-allow."""
    def describe(self):
        return AdapterMetadata("nonconforming", "0.0.1", "test/nonconforming",
                               CONTRACT_VERSION, None)
    def run_scenario(self, ctx):
        return AdapterOutcome(verdict="ALLOW", executed=True, audit_valid=True)


class RelabeledReference:
    """Conformant behavior, but declares a different adapter version."""
    def __init__(self, version="9.9.9"):
        self._inner = ReferenceComplianceAdapter()
        self._version = version
    def describe(self):
        m = self._inner.describe()
        return AdapterMetadata(m.name, self._version, m.implementation_id,
                               m.claimed_contract_version, m.framework)
    def run_scenario(self, ctx):
        return self._inner.run_scenario(ctx)


# --- module-scoped certifications (each spins the governed stack once) ------ #

@pytest.fixture(scope="module")
def ref_cert():
    return certify(ReferenceComplianceAdapter(), contract_version="1.0")


@pytest.fixture(scope="module")
def volt_cert():
    return certify(VoltAgentComplianceAdapter(), contract_version="1.0")


# --------------------------------------------------------------------------- #
# A. Successful certification.                                                #
# --------------------------------------------------------------------------- #

def test_reference_is_certified(ref_cert):
    assert ref_cert.status is ProgramStatus.CERTIFIED
    assert ref_cert.scenarios_failed == 0 and ref_cert.scenarios_passed >= 18
    assert ref_cert.evidence_digest.startswith("sha256:")
    assert ref_cert.covered_invariants  # invariant coverage recorded


def test_voltagent_is_certified(volt_cert):
    assert volt_cert.status is ProgramStatus.CERTIFIED
    assert volt_cert.adapter_name == "voltagent" and volt_cert.framework == "voltagent"


def test_report_states_repository_scope_and_algorithm(ref_cert):
    rep = ref_cert.report()
    assert rep["digest_algorithm"] == "sha256"
    assert rep["report_schema_version"] == "1"
    assert "official compliance suite" in rep["note"]
    assert "not a public" in rep["note"]  # honest scope
    assert rep["scenarios_detail"]  # scenario-level outcomes present


# --------------------------------------------------------------------------- #
# B. Failed certification.                                                     #
# --------------------------------------------------------------------------- #

def test_nonconforming_is_not_certified():
    result = certify(NonConformingAdapter(), contract_version="1.0")
    assert result.status is ProgramStatus.NOT_CERTIFIED
    assert result.scenarios_failed > 0
    # Failed scenario details are preserved.
    assert any(s.status != "PASS" for s in result.scenarios)


def test_failed_certification_never_enters_the_manifest():
    manifest = build_manifest(contract_version="1.0",
                              adapter_names=("reference", "voltagent"))
    keys = {e["adapter_key"] for e in manifest["certifications"]}
    assert "nonconforming" not in keys
    assert all(e["status"] == "CERTIFIED" for e in manifest["certifications"])


# --------------------------------------------------------------------------- #
# C. Version binding.                                                          #
# --------------------------------------------------------------------------- #

def test_certification_binds_contract_and_vectorset_version(ref_cert):
    assert ref_cert.contract_version == "1.0"
    assert ref_cert.compliance_suite_version  # vector-set/compliance version bound
    assert ref_cert.vector_manifest_digest.startswith("sha256:")


def test_unsupported_contract_version_fails_closed():
    result = certify(ReferenceComplianceAdapter(), contract_version="2.0")
    assert result.status is ProgramStatus.NOT_CERTIFIED


def test_build_manifest_for_unsupported_version_is_empty():
    manifest = build_manifest(contract_version="2.0")
    assert manifest["certifications"] == []


# --------------------------------------------------------------------------- #
# D. Determinism.                                                              #
# --------------------------------------------------------------------------- #

def test_repeated_certification_is_deterministic():
    a = certify(ReferenceComplianceAdapter(), contract_version="1.0")
    b = certify(ReferenceComplianceAdapter(), contract_version="1.0")
    assert a.evidence_digest == b.evidence_digest
    assert a.manifest_entry() == b.manifest_entry()


def test_digest_is_independent_of_scenario_input_order():
    md = ReferenceComplianceAdapter().describe()
    s = (ScenarioOutcome("IC-V1-B", "PASS", "x", True),
         ScenarioOutcome("IC-V1-A", "PASS", "y", True))
    d1 = _evidence_digest(md, "1.0", "sha256:v", ProgramStatus.CERTIFIED, ("x", "y"), s)
    d2 = _evidence_digest(md, "1.0", "sha256:v", ProgramStatus.CERTIFIED, ("y", "x"),
                          tuple(reversed(s)))
    assert d1 == d2  # canonical + sorted -> order-independent


def test_manifest_canonical_comparison_is_key_order_independent(tmp_path):
    manifest = build_manifest(contract_version="1.0")
    # Write with a different key order; verify_manifest compares canonically.
    p = tmp_path / "manifest.json"
    reordered = {k: manifest[k] for k in reversed(list(manifest.keys()))}
    p.write_text(json.dumps(reordered), encoding="utf-8")
    assert verify_manifest(path=p).ok


# --------------------------------------------------------------------------- #
# E. Tamper / stale detection.                                                #
# --------------------------------------------------------------------------- #

def _committed():
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def test_committed_manifest_verifies():
    assert verify_manifest().ok


def test_tampered_digest_is_rejected(tmp_path):
    m = _committed()
    m["certifications"][0]["evidence_digest"] = "sha256:deadbeef"
    p = tmp_path / "m.json"
    p.write_text(json.dumps(m))
    assert not verify_manifest(path=p).ok


def test_tampered_counts_are_rejected(tmp_path):
    m = _committed()
    m["certifications"][0]["scenarios_passed"] = 999
    p = tmp_path / "m.json"
    p.write_text(json.dumps(m))
    assert not verify_manifest(path=p).ok


def test_forged_certified_entry_is_rejected(tmp_path):
    m = _committed()
    m["certifications"].append({
        "adapter": "nonconforming", "adapter_key": "nonconforming",
        "adapter_version": "0.0.1", "implementation_id": "test/nonconforming",
        "framework": None, "contract_version": "1.0", "compliance_suite_version": "1.0.0",
        "vector_manifest_digest": "sha256:x", "status": "CERTIFIED",
        "scenarios_total": 18, "scenarios_passed": 18, "scenarios_failed": 0,
        "covered_invariants": [], "evidence_digest": "sha256:forged",
        "digest_algorithm": "sha256", "report_id": "sha256:forged"})
    p = tmp_path / "m.json"
    p.write_text(json.dumps(m))
    res = verify_manifest(path=p)
    assert not res.ok


def test_changed_adapter_version_changes_digest():
    a = certify(ReferenceComplianceAdapter(), contract_version="1.0")
    b = certify(RelabeledReference("9.9.9"), contract_version="1.0")
    assert a.status is ProgramStatus.CERTIFIED and b.status is ProgramStatus.CERTIFIED
    assert a.evidence_digest != b.evidence_digest  # version is bound


def test_changed_scenario_outcome_changes_digest():
    md = ReferenceComplianceAdapter().describe()
    base = (ScenarioOutcome("IC-V1-A", "PASS", "x", True),)
    flipped = (ScenarioOutcome("IC-V1-A", "FAIL", "x", True),)
    d1 = _evidence_digest(md, "1.0", "sha256:v", ProgramStatus.CERTIFIED, ("x",), base)
    d2 = _evidence_digest(md, "1.0", "sha256:v", ProgramStatus.NOT_CERTIFIED, ("x",), flipped)
    assert d1 != d2


def test_changed_contract_or_vectorset_changes_digest():
    md = ReferenceComplianceAdapter().describe()
    s = (ScenarioOutcome("IC-V1-A", "PASS", "x", True),)
    base = _evidence_digest(md, "1.0", "sha256:v", ProgramStatus.CERTIFIED, ("x",), s)
    diff_contract = _evidence_digest(md, "1.1", "sha256:v", ProgramStatus.CERTIFIED, ("x",), s)
    diff_vectors = _evidence_digest(md, "1.0", "sha256:w", ProgramStatus.CERTIFIED, ("x",), s)
    assert base != diff_contract and base != diff_vectors


# --------------------------------------------------------------------------- #
# F. Boundary integrity.                                                       #
# --------------------------------------------------------------------------- #

def test_certification_uses_the_framework_neutral_boundary():
    assert isinstance(ReferenceComplianceAdapter(), ComplianceAdapter)
    assert isinstance(VoltAgentComplianceAdapter(), ComplianceAdapter)


def test_no_framework_specific_logic_in_program():
    # OFFICIAL_ADAPTERS names adapters (data), but generic certification code must
    # contain no framework-specific import, type, or special-case branch.
    assert "integrations.voltagent" not in PROGRAM_SRC       # no import of the TS adapter's py side
    assert "import voltagent" not in PROGRAM_SRC
    for banned in ('== "voltagent"', "== 'voltagent'", 'if "voltagent"',
                   "langgraph", "crewai", "autogen"):
        assert banned not in PROGRAM_SRC
    # 'voltagent' may appear ONLY on the OFFICIAL_ADAPTERS definition line (data).
    volt_lines = [ln for ln in PROGRAM_SRC.splitlines() if "voltagent" in ln]
    assert volt_lines and all("OFFICIAL_ADAPTERS" in ln for ln in volt_lines)


def test_program_introduces_no_network_signing_or_execution():
    for banned in ("httpx", "requests", "import socket", "Ed25519", "SigningKey",
                   "subprocess", "HTTPEgressExecutor", "egress_proxy"):
        assert banned not in PROGRAM_SRC, f"program.py must not reference {banned!r}"


def test_adapter_self_attestation_is_ignored():
    # The metadata model has no 'certified' field an adapter could set; a
    # non-conforming adapter that *claims* success is still NOT_CERTIFIED because
    # certification is derived from real compliance evidence, not the adapter.
    assert "certified" not in AdapterMetadata.__dataclass_fields__
    assert certify(NonConformingAdapter(), contract_version="1.0").status \
        is ProgramStatus.NOT_CERTIFIED
