"""Deterministic interoperability evidence bundle (PR #48).

Builds the machine-readable multi-adapter matrix from real scenario results and the
shared Gateway identity, plus the capability→evidence mapping. Evidence generation
**fails** (overall FAIL) rather than emitting PASS when provenance, scenario results,
audit correlation, or a declared capability's proof is missing.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from mcc_core.signing import canonical_bytes, sha256_hex

from .harness import SCENARIOS, AdapterEvidence, SharedGovernedGateway

PROOF_FORMAT_VERSION = "1"

#: Which common scenario proves each declared capability. Capabilities mapped to a
#: scenario outside the common suite (escalation/constrain) are only provable by an
#: adapter that exercises them — declaring them without evidence FAILS the matrix.
CAPABILITY_SCENARIO_MAP: Dict[str, List[str]] = {
    "verdict_authorizes": ["ALLOW", "DENY"],
    "signature_verified": ["MISMATCH", "INVALID_OR_EXPIRED"],
    "decision_authority_valid": ["ALLOW"],
    "scope_matches": ["MISMATCH"],
    "actor_matches": ["MISMATCH"],
    "resource_matches": ["MISMATCH"],
    "action_hash_matches": ["MISMATCH"],
    "nonce_matches": ["REPLAY"],
    "nonce_not_replayed": ["REPLAY"],
    "within_validity_window": ["INVALID_OR_EXPIRED"],
    "not_revoked": ["ALLOW"],
    "policy_hash_matches": ["MISMATCH"],
    "durably_recorded_before_enforce": ["AUDIT"],
    "tamper_evident_audit_evidence": ["AUDIT"],
    "human_in_the_loop_escalation": ["ESCALATE"],
    "constraint_enforcement": ["CONSTRAIN"],
}


def capability_evidence_map(profile: Dict[str, Any],
                            evidence: AdapterEvidence) -> Dict[str, Any]:
    """Map each declared capability → required scenario → result → PASS/UNPROVEN.

    A capability is UNPROVEN if it has no known mapping, or its scenario is not a
    passing result in this adapter's evidence."""
    passing = {s.scenario for s in evidence.scenarios if s.status == "PASS"}
    declared = list(profile.get("runtime_capabilities", [])) + \
        list(profile.get("optional_capabilities", []))
    mapping: Dict[str, Any] = {}
    for cap in sorted(set(declared)):
        scenarios = CAPABILITY_SCENARIO_MAP.get(cap)
        proven = bool(scenarios) and all(s in passing for s in scenarios)
        mapping[cap] = {
            "required_scenarios": scenarios or [],
            "result": "PASS" if proven else "UNPROVEN",
        }
    return mapping


def _adapter_entry(gw: SharedGovernedGateway, ev: AdapterEvidence,
                   profile: Dict[str, Any]) -> Dict[str, Any]:
    identity = gw.identity()
    cap_map = capability_evidence_map(profile, ev)
    caps_ok = all(v["result"] == "PASS" for v in cap_map.values())
    scenarios_ok = ev.passed
    return {
        "adapter": ev.adapter_name,
        "classification": ev.classification,
        "adapter_module": ev.provenance.get("adapter_module"),
        "adapter_version": ev.provenance.get("adapter_version"),
        "framework_provenance": ev.provenance,
        "integration_contract_version": profile.get("integration_contract", {}).get("version"),
        "capability_profile_version": ev.capability_profile_version,
        # Shared-instance provenance (identical for every adapter in a run).
        "shared_gateway": identity,
        "scenarios": [s.to_dict() for s in ev.scenarios],
        "capability_evidence_map": cap_map,
        "result": "PASS" if (scenarios_ok and caps_ok) else "FAIL",
    }


def build_matrix(gw: SharedGovernedGateway, evidences: List[AdapterEvidence],
                 profiles: Dict[str, Dict[str, Any]], *,
                 audit_chain_valid: bool) -> Dict[str, Any]:
    """Assemble the deterministic multi-adapter matrix. FAILs closed on any missing
    scenario, unproven capability, missing audit verification, or failed adapter."""
    entries = [_adapter_entry(gw, ev, profiles[ev.adapter_name])
               for ev in sorted(evidences, key=lambda e: e.adapter_name)]

    frameworks = {e["framework_provenance"]["framework_name"] for e in entries
                  if e["classification"] == "REAL FRAMEWORK INTEGRATION"}
    http_neutral = any(e["classification"] == "FRAMEWORK-NEUTRAL HTTP INTEGRATION"
                       for e in entries)

    body = {
        "proof_format_version": PROOF_FORMAT_VERSION,
        "generation_method": "executable end-to-end scenario runs through one shared "
                             "out-of-process MCC Gateway over real HTTP",
        "shared_gateway": gw.identity(),
        "adapters": entries,
        "totals": {
            "adapters": len(entries),
            "real_framework_ecosystems": len(frameworks),
            "framework_neutral_http": http_neutral,
            "scenarios_per_adapter": len(SCENARIOS),
            "scenario_results": sum(len(e["scenarios"]) for e in entries),
        },
        "audit_chain_verification": {"verified": bool(audit_chain_valid)},
        "limitations": [
            "Tested interoperability, not universal compatibility with every framework "
            "or version.",
            "Deterministic offline runs: no external/paid LLM calls.",
        ],
        "overall": "PASS" if (
            entries and all(e["result"] == "PASS" for e in entries) and audit_chain_valid
        ) else "FAIL",
    }
    # A deterministic run identifier over the stable evidence (excludes timestamps).
    body["run_id"] = sha256_hex(canonical_bytes(body))
    return body


def write_bundle(matrix: Dict[str, Any], out_dir: str | Path) -> Dict[str, str]:
    """Write the evidence bundle files. Returns written paths."""
    d = Path(out_dir)
    d.mkdir(parents=True, exist_ok=True)
    paths = {}
    matrix_path = d / "multi_adapter_matrix.json"
    matrix_path.write_text(json.dumps(matrix, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    paths["matrix"] = str(matrix_path)

    provenance = {e["adapter"]: e["framework_provenance"] for e in matrix["adapters"]}
    (d / "framework_provenance.json").write_text(
        json.dumps(provenance, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    paths["provenance"] = str(d / "framework_provenance.json")

    cap = {e["adapter"]: e["capability_evidence_map"] for e in matrix["adapters"]}
    (d / "capability_evidence_map.json").write_text(
        json.dumps(cap, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    paths["capability"] = str(d / "capability_evidence_map.json")

    (d / "audit_verification.json").write_text(
        json.dumps(matrix["audit_chain_verification"], indent=2, sort_keys=True) + "\n",
        encoding="utf-8")
    paths["audit"] = str(d / "audit_verification.json")
    return paths


# --------------------------------------------------------------------------- #
# Structural validation (pure Python; the JSON Schema is the published artifact).
# --------------------------------------------------------------------------- #

_REQUIRED_MATRIX = {"proof_format_version", "generation_method", "shared_gateway",
                    "adapters", "totals", "audit_chain_verification", "overall", "run_id"}
_REQUIRED_ADAPTER = {"adapter", "classification", "adapter_module", "adapter_version",
                     "framework_provenance", "integration_contract_version",
                     "capability_profile_version", "shared_gateway", "scenarios",
                     "capability_evidence_map", "result"}
_REQUIRED_GATEWAY = {"gateway_impl", "gate_impl", "audit_impl", "deployment_id",
                     "endpoint", "policy_hash", "trust_set_id", "nonce_registry_impl"}


def validate_matrix(matrix: Dict[str, Any]) -> List[str]:
    """Return a list of structural problems (empty == valid)."""
    problems: List[str] = []
    for k in sorted(_REQUIRED_MATRIX - set(matrix)):
        problems.append(f"matrix missing {k!r}")
    for k in sorted(_REQUIRED_GATEWAY - set(matrix.get("shared_gateway", {}))):
        problems.append(f"shared_gateway missing {k!r}")
    for e in matrix.get("adapters", []):
        for k in sorted(_REQUIRED_ADAPTER - set(e)):
            problems.append(f"adapter {e.get('adapter')!r} missing {k!r}")
        if len(e.get("scenarios", [])) != len(SCENARIOS):
            problems.append(f"adapter {e.get('adapter')!r} did not run all {len(SCENARIOS)} scenarios")
    return problems


__all__ = ["PROOF_FORMAT_VERSION", "CAPABILITY_SCENARIO_MAP", "capability_evidence_map",
           "build_matrix", "write_bundle", "validate_matrix"]
