"""Validates the Wave C scope manifest (conformance/normative-v1.0/
remediation/wave-c-technical-certificate-scope-manifest.json) and its
deterministic evidence artifact (wave-c-evidence.json) against their
published schemas and cross-checks them against the real, current
requirements.json -- this is the CI guard that fails if the manifest is
invalid, drifts from the real baseline, or claims a status the baseline
does not actually carry.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from mcc_conformance.validate import _check_object

REPO_ROOT = Path(__file__).resolve().parents[1]
REMEDIATION_DIR = REPO_ROOT / "conformance" / "normative-v1.0" / "remediation"
MANIFEST_PATH = REMEDIATION_DIR / "wave-c-technical-certificate-scope-manifest.json"
EVIDENCE_PATH = REMEDIATION_DIR / "wave-c-evidence.json"
SCHEMA_DIR = REPO_ROOT / "conformance" / "normative-v1.0" / "schemas"


def _manifest() -> dict:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def _requirements() -> dict:
    d = json.loads((REPO_ROOT / "conformance" / "normative-v1.0" / "requirements.json").read_text(encoding="utf-8"))
    return {r["requirement_id"]: r for r in d["requirements"]}


def test_manifest_is_valid_json_and_exists():
    assert MANIFEST_PATH.exists()
    _manifest()


def test_manifest_matches_the_shared_remediation_wave_schema():
    schema = json.loads((SCHEMA_DIR / "remediation_wave_scope_manifest.schema.json").read_text(encoding="utf-8"))
    manifest = _manifest()
    errors = _check_object(manifest, schema, "wave-c-technical-certificate-scope-manifest.json")
    for i, entry in enumerate(manifest["selected_requirements"]):
        errors += _check_object(entry, schema["properties"]["selected_requirements"]["items"], f"entry #{i}")
    assert errors == [], errors


def test_selected_requirement_count_is_73():
    manifest = _manifest()
    assert len(manifest["selected_requirements"]) == 73


def test_every_selected_requirement_exists_in_the_real_baseline():
    manifest = _manifest()
    reqs = _requirements()
    for entry in manifest["selected_requirements"]:
        assert entry["requirement_id"] in reqs, f"{entry['requirement_id']} not in requirements.json"


def test_manifest_status_after_matches_the_real_baseline():
    manifest = _manifest()
    reqs = _requirements()
    for entry in manifest["selected_requirements"]:
        rid = entry["requirement_id"]
        expected = entry.get("status_after")
        actual = reqs[rid]["conformance_status"]
        assert actual == expected, (
            f"{rid}: manifest claims status_after={expected!r} but requirements.json has {actual!r}"
        )


def test_excluded_candidates_are_exactly_the_documented_seven():
    manifest = _manifest()
    assert set(manifest["excluded_candidate_ids"]) == {
        "TC-SUBJ-002", "TC-SUBJ-003", "TC-RES-002",
        "TC-EXT-001", "TC-EXT-002", "TC-EXT-003", "TC-EXT-004",
    }


def test_excluded_candidates_remain_at_their_pre_existing_status():
    # Excluded means "this wave did not implement or claim it" -- not
    # necessarily "permanently barred". Today none of these 7 has been
    # promoted by any wave; if a future wave legitimately promotes one
    # (once its dependency exists), this assertion is the one to relax,
    # exactly as Wave A's own excluded-candidate test was refined in Wave B.
    manifest = _manifest()
    reqs = _requirements()
    for rid in manifest["excluded_candidate_ids"]:
        assert reqs[rid]["conformance_status"] != "CONFORMANT", (
            f"{rid} is listed as excluded from Wave C but is already CONFORMANT -- "
            "if a later wave promoted it, update this test to attribute that explicitly"
        )


def test_conformant_requirements_have_direct_test_and_evidence_linkage():
    manifest = _manifest()
    reqs = _requirements()
    for entry in manifest["selected_requirements"]:
        if entry.get("status_after") != "CONFORMANT":
            continue
        r = reqs[entry["requirement_id"]]
        assert r["implementation_references"], entry["requirement_id"]
        assert r["test_references"], entry["requirement_id"]
        assert r["evidence_references"], entry["requirement_id"]
        assert "conformance/normative-v1.0/remediation/wave-c-evidence.json" in r["evidence_references"]


def test_no_unexpected_status_transition_outside_selected_scope():
    manifest = _manifest()
    assert manifest["unexpected_transitions_outside_selected_scope"] == []
    reqs = _requirements()
    selected_ids = {e["requirement_id"] for e in manifest["selected_requirements"] if e.get("status_after") == "CONFORMANT"}
    excluded_ids = set(manifest["excluded_candidate_ids"])
    allowed_ids = selected_ids | excluded_ids
    # MCC-TC-001 category names collide in string form with MCC-EB-001/
    # MCC-CM-001 category names of the same section number (e.g. both
    # "6. Required Fields") -- specification_id disambiguates them, so this
    # check is scoped to MCC-TC-001 requirements only. TC-RID-* (already
    # NOT_APPLICABLE) is exempt in the same spirit as EB-RID/CM-RID.
    for r in reqs.values():
        if (
            r["specification_id"] == "MCC-TC-001"
            and r["requirement_category"] != "22. Requirement Identifier Registry"
            and r["requirement_id"] not in allowed_ids
        ):
            assert r["conformance_status"] != "CONFORMANT", (
                f"{r['requirement_id']} was unexpectedly promoted to CONFORMANT "
                "outside the Wave C selected scope"
            )


def test_wave_a_and_wave_b_requirements_are_untouched_by_wave_c():
    # Regression guard: Wave C must not have altered any of Waves A/B's 18
    # previously-promoted requirements or their evidence linkage.
    reqs = _requirements()
    for manifest_name, evidence_marker in (
        ("wave-a-evidence-bundle-scope-manifest.json", "conformance/normative-v1.0/remediation/wave-a-evidence.json"),
        ("wave-b-evidence-bundle-reference-scope-manifest.json", "conformance/normative-v1.0/remediation/wave-b-evidence.json"),
    ):
        prior_manifest = json.loads((REMEDIATION_DIR / manifest_name).read_text(encoding="utf-8"))
        for entry in prior_manifest["selected_requirements"]:
            if entry.get("status_after") != "CONFORMANT":
                continue
            rid = entry["requirement_id"]
            r = reqs[rid]
            assert r["conformance_status"] == "CONFORMANT", rid
            assert evidence_marker in r["evidence_references"], rid


def test_global_conformant_count_includes_waves_a_b_and_c():
    manifest = _manifest()
    reqs = _requirements()
    wave_c_conformant = {e["requirement_id"] for e in manifest["selected_requirements"] if e.get("status_after") == "CONFORMANT"}
    assert len(wave_c_conformant) == 73
    real_conformant_ids = {r["requirement_id"] for r in reqs.values() if r["conformance_status"] == "CONFORMANT"}
    assert wave_c_conformant <= real_conformant_ids
    assert manifest["global_status_delta"]["after"]["CONFORMANT"] == len(real_conformant_ids) == 91


def test_global_status_delta_totals_are_internally_consistent():
    manifest = _manifest()
    delta = manifest["global_status_delta"]
    assert sum(delta["before"].values()) == 810
    assert sum(delta["after"].values()) == 810


# ---------------------------------------------------------------------------
# Deterministic evidence artifact
# ---------------------------------------------------------------------------


def test_evidence_artifact_exists_and_is_valid_json():
    assert EVIDENCE_PATH.exists()
    data = json.loads(EVIDENCE_PATH.read_text(encoding="utf-8"))
    assert data["requirement_count"] == len(data["records"]) == 73


def test_evidence_artifact_covers_every_conformant_requirement():
    evidence = json.loads(EVIDENCE_PATH.read_text(encoding="utf-8"))
    evidenced_ids = {r["requirement_id"] for r in evidence["records"]}
    manifest = _manifest()
    conformant_ids = {e["requirement_id"] for e in manifest["selected_requirements"] if e.get("status_after") == "CONFORMANT"}
    assert conformant_ids == evidenced_ids


def test_evidence_artifact_every_record_passed():
    evidence = json.loads(EVIDENCE_PATH.read_text(encoding="utf-8"))
    for record in evidence["records"]:
        assert record["verification_outcome"] == "PASS", record["requirement_id"]


def test_evidence_artifact_contains_no_host_specific_paths():
    text = EVIDENCE_PATH.read_text(encoding="utf-8")
    assert "/tmp" not in text
    assert str(REPO_ROOT) not in text


def test_evidence_generation_is_reproducible_and_deterministic():
    cmd = [sys.executable, str(REMEDIATION_DIR / "generate_wave_c_evidence.py")]
    before = EVIDENCE_PATH.read_bytes()
    result = subprocess.run(
        cmd, cwd=REPO_ROOT, capture_output=True, timeout=120,
        env={"PYTHONPATH": "src", "PATH": "/usr/bin:/bin:/usr/local/bin"},
    )
    assert result.returncode == 0, result.stderr.decode()
    after = EVIDENCE_PATH.read_bytes()
    assert before == after, "regenerating wave-c-evidence.json produced a different result (non-deterministic)"
