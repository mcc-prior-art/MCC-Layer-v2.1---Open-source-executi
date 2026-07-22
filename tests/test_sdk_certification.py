"""Adapter-SDK Compliance & Certification (PR #51).

The Adapter SDK (PR #50) is the canonical certification ingress: an adapter is
certified exclusively through its public ``mcc_adapter_sdk.Adapter`` surface, driven
through the ONE existing certification engine (golden vectors, real governed stack,
ground-truth cross-check). Outputs are deterministic and reproducible.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path
from typing import Any


import mcc_protocol as mp
from mcc_adapter_sdk import Adapter, AdapterContext, AdapterMetadata
from mcc_client.contract import CONTRACT_VERSION
from mcc_compliance import certify_sdk_adapter  # stable public API
from mcc_compliance.capability_profile import BASELINE_CAPABILITIES
from mcc_compliance.program import ProgramStatus
from mcc_compliance.sdk_certification import (
    SDK_CERTIFICATION_SCHEMA_VERSION,
    certification_document,
    evidence_document,
    report_document,
    run_sdk_certification,
    write_certification,
)
from mcc_compliance.sdk_reference_adapter import SdkReferenceAdapter

ROOT = Path(__file__).resolve().parents[1]


# --------------------------------------------------------------------------- #
# 1. The SDK reference adapter certifies through the SDK ingress.             #
# --------------------------------------------------------------------------- #

def test_sdk_reference_adapter_is_certified():
    result = certify_sdk_adapter(SdkReferenceAdapter(), contract_version=CONTRACT_VERSION)
    assert result.status is ProgramStatus.CERTIFIED
    assert result.scenarios_total == 18
    assert result.scenarios_passed == 18 and result.scenarios_failed == 0
    assert result.evidence_digest.startswith("sha256:")


# --------------------------------------------------------------------------- #
# 2. Deterministic, reproducible outputs.                                     #
# --------------------------------------------------------------------------- #

def test_all_outputs_are_deterministic():
    r1, rep1 = run_sdk_certification(SdkReferenceAdapter(), contract_version=CONTRACT_VERSION)
    r2, rep2 = run_sdk_certification(SdkReferenceAdapter(), contract_version=CONTRACT_VERSION)
    assert certification_document(r1) == certification_document(r2)
    assert evidence_document(rep1) == evidence_document(rep2)
    assert report_document(rep1) == report_document(rep2)
    # The evidence digest is stable across runs (no wall-clock, no random ids).
    assert r1.evidence_digest == r2.evidence_digest


def test_written_files_are_byte_identical_across_runs(tmp_path):
    a = SdkReferenceAdapter()
    d1, d2 = tmp_path / "run1", tmp_path / "run2"
    write_certification(a, contract_version=CONTRACT_VERSION, out_dir=str(d1))
    write_certification(a, contract_version=CONTRACT_VERSION, out_dir=str(d2))
    for name in ("certification.json", "evidence.json", "certification-report.md"):
        assert (d1 / name).read_bytes() == (d2 / name).read_bytes(), name


def test_outputs_carry_no_wall_clock():
    r, rep = run_sdk_certification(SdkReferenceAdapter(), contract_version=CONTRACT_VERSION)
    for doc in (certification_document(r), evidence_document(rep)):
        assert "generated_at" not in json.dumps(doc)


# --------------------------------------------------------------------------- #
# 3. Versioned certification schema.                                          #
# --------------------------------------------------------------------------- #

def test_certification_document_matches_versioned_schema():
    schema = json.loads((ROOT / "schemas" / "adapter-certification-v1.schema.json").read_text())
    doc = certification_document(
        certify_sdk_adapter(SdkReferenceAdapter(), contract_version=CONTRACT_VERSION))
    assert doc["schema_version"] == SDK_CERTIFICATION_SCHEMA_VERSION == "1"
    assert doc["certification_ingress"] == "adapter-sdk"
    # Structural conformance to the published schema (required keys + enums).
    req = schema["properties"]["certification"]["required"]
    assert set(req) <= set(doc["certification"])
    assert doc["certification"]["status"] in ("CERTIFIED", "NOT_CERTIFIED")
    assert doc["certification"]["digest_algorithm"] == "sha256"


# --------------------------------------------------------------------------- #
# 4. A non-conforming SDK adapter fails closed (NOT_CERTIFIED).               #
# --------------------------------------------------------------------------- #

class _AlwaysEmailAdapter(Adapter):
    """Non-conforming: ignores the scenario and always proposes an allowed channel,
    so the DENY/CONSTRAIN/ESCALATE vectors do not produce their expected outcomes."""

    def describe(self) -> AdapterMetadata:
        return AdapterMetadata.create(adapter_id="bad-sdk", adapter_version="1.0.0",
                                      framework_name="none",
                                      capabilities=(BASELINE_CAPABILITIES[0],))

    def to_proposal(self, context: AdapterContext, native_request: Any) -> mp.CanonicalProposal:
        return self.make_proposal(
            context, action="send_notification", resource="notifications",
            payload={"recipient": "customer-123", "message": "x", "priority": 2,
                     "channel": "email"})

    def to_response(self, decision: mp.GovernanceDecision) -> Any:
        return {"verdict": decision.verdict.value}

    def sample_request(self) -> Any:
        return {"request": "x", "params": {}}


def test_non_conforming_sdk_adapter_is_not_certified():
    result = certify_sdk_adapter(_AlwaysEmailAdapter(), contract_version=CONTRACT_VERSION)
    assert result.status is ProgramStatus.NOT_CERTIFIED
    assert result.scenarios_failed > 0


# --------------------------------------------------------------------------- #
# 5. SDK is the exclusive ingress (structural guard).                         #
# --------------------------------------------------------------------------- #

def test_bridge_consumes_adapter_only_through_the_sdk():
    # The bridge drives the adapter via mcc_adapter_sdk (AdapterRunner) — never by
    # importing governance internals or calling adapter-private execution surfaces.
    src = (ROOT / "src" / "mcc_compliance" / "sdk_bridge.py").read_text()
    tree = ast.parse(src)
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module)
        elif isinstance(node, ast.Import):
            for a in node.names:
                imported.add(a.name)
    # It uses the public SDK + client boundary; never gate/authority/consensus/etc.
    assert "mcc_adapter_sdk" in imported
    forbidden = {"mcc_core.gate", "mcc_core.authority", "mcc_core.consensus",
                 "mcc_core.coordinator", "mcc_core.signing", "gateway", "egress_proxy"}
    assert not (imported & forbidden), imported & forbidden


def test_certify_sdk_adapter_is_the_public_stable_api():
    import mcc_compliance
    assert mcc_compliance.certify_sdk_adapter is certify_sdk_adapter
    assert callable(mcc_compliance.write_certification)


# --------------------------------------------------------------------------- #
# 6. Backward-compat: the existing ComplianceAdapter path still certifies.     #
# --------------------------------------------------------------------------- #

def test_existing_compliance_path_still_certifies():
    from mcc_compliance import certify
    from mcc_compliance.adapters import ReferenceComplianceAdapter
    result = certify(ReferenceComplianceAdapter(), contract_version=CONTRACT_VERSION)
    assert result.status is ProgramStatus.CERTIFIED
