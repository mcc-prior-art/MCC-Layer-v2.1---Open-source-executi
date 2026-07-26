"""Validates the Wave B scope manifest (conformance/normative-v1.0/
remediation/wave-b-evidence-bundle-reference-scope-manifest.json) and its
deterministic evidence artifact (wave-b-evidence.json) against their
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

from mcc_conformance.validate import _check_object, _load_schema

REPO_ROOT = Path(__file__).resolve().parents[1]
REMEDIATION_DIR = REPO_ROOT / "conformance" / "normative-v1.0" / "remediation"
MANIFEST_PATH = REMEDIATION_DIR / "wave-b-evidence-bundle-reference-scope-manifest.json"
EVIDENCE_PATH = REMEDIATION_DIR / "wave-b-evidence.json"
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
    errors = _check_object(manifest, schema, "wave-b-evidence-bundle-reference-scope-manifest.json")
    for i, entry in enumerate(manifest["selected_requirements"]):
        errors += _check_object(entry, schema["properties"]["selected_requirements"]["items"], f"entry #{i}")
    assert errors == [], errors


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


def test_no_candidates_were_excluded():
    manifest = _manifest()
    assert manifest["excluded_candidate_ids"] == []


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
        assert "conformance/normative-v1.0/remediation/wave-b-evidence.json" in r["evidence_references"]


def test_no_unexpected_status_transition_outside_selected_scope():
    manifest = _manifest()
    assert manifest["unexpected_transitions_outside_selected_scope"] == []
    reqs = _requirements()
    selected_ids = {e["requirement_id"] for e in manifest["selected_requirements"] if e.get("status_after") == "CONFORMANT"}
    # "13. Hash References" also contains Wave A's already-CONFORMANT
    # CM-HASH-001/002/004 (a prior, already-verified wave, not this one) --
    # those are expected, not "unexpected", promotions.
    wave_a_manifest = json.loads(
        (REMEDIATION_DIR / "wave-a-evidence-bundle-scope-manifest.json").read_text(encoding="utf-8")
    )
    already_conformant_ids = {
        e["requirement_id"] for e in wave_a_manifest["selected_requirements"] if e.get("status_after") == "CONFORMANT"
    }
    allowed_ids = selected_ids | already_conformant_ids
    shared_categories = {"13. Hash References", "14. Evidence Bundle References"}
    for r in reqs.values():
        if r["requirement_category"] in shared_categories and r["requirement_id"] not in allowed_ids:
            assert r["conformance_status"] != "CONFORMANT", (
                f"{r['requirement_id']} was unexpectedly promoted to CONFORMANT "
                "outside the Wave B selected scope"
            )


def test_wave_a_requirements_are_untouched_by_wave_b():
    # Regression guard: Wave B must not have altered any of Wave A's 13
    # promoted requirements or their evidence linkage.
    wave_a_manifest = json.loads(
        (REMEDIATION_DIR / "wave-a-evidence-bundle-scope-manifest.json").read_text(encoding="utf-8")
    )
    reqs = _requirements()
    for entry in wave_a_manifest["selected_requirements"]:
        if entry.get("status_after") != "CONFORMANT":
            continue
        rid = entry["requirement_id"]
        r = reqs[rid]
        assert r["conformance_status"] == "CONFORMANT", rid
        assert "conformance/normative-v1.0/remediation/wave-a-evidence.json" in r["evidence_references"], rid


def test_global_conformant_count_includes_wave_a_plus_wave_b():
    manifest = _manifest()
    reqs = _requirements()
    wave_b_conformant = {e["requirement_id"] for e in manifest["selected_requirements"] if e.get("status_after") == "CONFORMANT"}
    assert len(wave_b_conformant) == 5
    real_conformant_ids = {r["requirement_id"] for r in reqs.values() if r["conformance_status"] == "CONFORMANT"}
    assert wave_b_conformant <= real_conformant_ids
    assert manifest["global_status_delta"]["after"]["CONFORMANT"] == len(real_conformant_ids) == 18


# ---------------------------------------------------------------------------
# Deterministic evidence artifact
# ---------------------------------------------------------------------------


def test_evidence_artifact_exists_and_is_valid_json():
    assert EVIDENCE_PATH.exists()
    data = json.loads(EVIDENCE_PATH.read_text(encoding="utf-8"))
    assert data["requirement_count"] == len(data["records"])


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
    cmd = [sys.executable, str(REMEDIATION_DIR / "generate_wave_b_evidence.py")]
    before = EVIDENCE_PATH.read_bytes()
    result = subprocess.run(
        cmd, cwd=REPO_ROOT, capture_output=True, timeout=120,
        env={"PYTHONPATH": "src", "PATH": "/usr/bin:/bin:/usr/local/bin"},
    )
    assert result.returncode == 0, result.stderr.decode()
    after = EVIDENCE_PATH.read_bytes()
    assert before == after, "regenerating wave-b-evidence.json produced a different result (non-deterministic)"
