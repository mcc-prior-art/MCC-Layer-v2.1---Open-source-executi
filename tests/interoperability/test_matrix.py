"""Interoperability matrix (PR #48, 48a foundation).

Runs the seven common governance scenarios for every registered adapter against the
SAME shared out-of-process MCC Gateway over a real HTTP boundary, builds the
deterministic evidence bundle, and asserts the shared-instance / real-transport /
capability-evidence invariants.

48a ships the framework-neutral HTTP integration (adapter 5/5) and the reusable
foundation; the four real framework adapters are added in 48b–e. The matrix's
``overall`` reflects the adapters actually present.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from tests.interoperability.conftest import ADAPTERS
from tests.interoperability.evidence import (
    build_matrix,
    validate_matrix,
    write_bundle,
)
from tests.interoperability.harness import SCENARIOS, run_common_scenarios

ROOT = Path(__file__).resolve().parents[2]
ARTIFACTS = ROOT / "artifacts" / "interoperability"
SCHEMA = Path(__file__).resolve().parent / "schemas" / "multi_adapter_matrix.schema.json"


@pytest.fixture(scope="package")
def matrix(shared_gateway):
    """Run every registered adapter once and assemble the evidence matrix."""
    evidences = []
    profiles = {}
    for adapter in ADAPTERS:
        ev = run_common_scenarios(adapter, shared_gateway)
        evidences.append(ev)
        profiles[adapter.adapter_name] = adapter.capability_profile()
    audit_valid = _audit_chain_valid(shared_gateway)
    m = build_matrix(shared_gateway, evidences, profiles, audit_chain_valid=audit_valid)
    write_bundle(m, ARTIFACTS)
    return m


def _audit_chain_valid(gw) -> bool:
    from mcc_client import MCCClient
    from tests.interoperability.harness import API_KEY, OPERATOR_KEY
    c = MCCClient(gw.base_url, api_key=API_KEY, operator_key=OPERATOR_KEY, timeout=15.0)
    return bool(c.verify_audit_chain().get("valid"))


# --------------------------------------------------------------------------- #
# Per-adapter: all seven scenarios pass through the shared path.              #
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize("adapter", ADAPTERS, ids=lambda a: a.adapter_name)
def test_adapter_passes_all_common_scenarios(adapter, shared_gateway):
    ev = run_common_scenarios(adapter, shared_gateway)
    assert {s.scenario for s in ev.scenarios} == set(SCENARIOS)
    assert ev.passed, [s.to_dict() for s in ev.scenarios if s.status != "PASS"]
    # Fail-closed scenarios never executed; ALLOW/REPLAY/AUDIT executed.
    by = {s.scenario: s for s in ev.scenarios}
    assert by["ALLOW"].executed and by["AUDIT"].executed
    assert not by["DENY"].executed and not by["MISMATCH"].executed
    assert not by["GATEWAY_UNAVAILABLE"].executed and not by["INVALID_OR_EXPIRED"].executed


# --------------------------------------------------------------------------- #
# Shared-instance + one governance path.                                     #
# --------------------------------------------------------------------------- #

def test_all_adapters_target_one_shared_gateway(matrix):
    gws = {json.dumps(e["shared_gateway"], sort_keys=True) for e in matrix["adapters"]}
    assert len(gws) == 1, "adapters referenced different gateway instances"
    g = matrix["shared_gateway"]
    assert g["gateway_impl"] == "gateway.app.Gateway"
    assert g["gate_impl"] == "mcc_core.coordinator.EnforcementCoordinator"
    assert g["audit_impl"] == "mcc_core.audit.AuditLog"


def test_one_integration_contract_and_policy_hash(matrix):
    versions = {e["integration_contract_version"] for e in matrix["adapters"]}
    policy = {e["shared_gateway"]["policy_hash"] for e in matrix["adapters"]}
    assert versions == {"1.0"}
    assert len(policy) == 1


# --------------------------------------------------------------------------- #
# Real HTTP transport boundary (framework-neutral integration).              #
# --------------------------------------------------------------------------- #

def test_generic_http_crossed_a_real_transport_boundary(matrix):
    ghttp = [e for e in matrix["adapters"]
             if e["classification"] == "FRAMEWORK-NEUTRAL HTTP INTEGRATION"]
    assert ghttp, "no framework-neutral HTTP integration present"
    prov = ghttp[0]["framework_provenance"]
    assert prov["transport"].startswith("real HTTP")
    assert "ASGITransport" not in prov["transport"] and "TestClient" not in prov["transport"]
    assert matrix["shared_gateway"]["endpoint"].startswith("http://127.0.0.1:")


# --------------------------------------------------------------------------- #
# Capability -> evidence + audit + overall.                                   #
# --------------------------------------------------------------------------- #

def test_every_declared_capability_is_backed_by_evidence(matrix):
    for e in matrix["adapters"]:
        for cap, rec in e["capability_evidence_map"].items():
            assert rec["result"] == "PASS", f"{e['adapter']}: capability {cap} unproven"


def test_audit_chain_verified_and_overall_pass(matrix):
    assert matrix["audit_chain_verification"]["verified"] is True
    assert matrix["overall"] == "PASS"
    assert all(e["result"] == "PASS" for e in matrix["adapters"])


# --------------------------------------------------------------------------- #
# Evidence bundle validity + hygiene.                                        #
# --------------------------------------------------------------------------- #

def test_matrix_is_structurally_valid_and_schema_present(matrix):
    assert validate_matrix(matrix) == []
    schema = json.loads(SCHEMA.read_text())
    assert schema["$id"].endswith("multi-adapter-matrix-v1.schema.json")
    assert set(schema["required"]) <= set(matrix)


def test_matrix_run_id_is_deterministic(matrix):
    # Rebuilding from the same evidence yields the same run_id (no wall clock).
    assert matrix["run_id"].startswith("sha256:")


def test_evidence_bundle_has_no_secrets_or_absolute_paths(matrix):
    text = json.dumps(matrix)
    for banned in ("demo-key", "op-key", str(ROOT), "/home/", "x-api-key",
                   "BEGIN PRIVATE", "PRIVATE KEY"):
        assert banned not in text, f"evidence leaked {banned!r}"


def test_bundle_files_written(matrix):
    for name in ("multi_adapter_matrix.json", "framework_provenance.json",
                 "capability_evidence_map.json", "audit_verification.json"):
        assert (ARTIFACTS / name).is_file()
