"""Static guards for .github/workflows/mcc-independent-assurance.yml (PR #71).

Checks the isolation requirements the workflow's own header comment
claims, without needing to actually run it in GitHub Actions: valid YAML,
read-only permissions throughout, and every third-party action pinned to a
full 40-character commit SHA rather than a mutable tag.
"""

from __future__ import annotations

import re
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_PATH = REPO_ROOT / ".github" / "workflows" / "mcc-independent-assurance.yml"

_USES_SHA_RE = re.compile(r"^([^@]+)@([0-9a-f]{40})\s*(#.*)?$")


def _load() -> dict:
    return yaml.safe_load(WORKFLOW_PATH.read_text(encoding="utf-8"))


def _iter_uses(doc: dict):
    for job_name, job in doc["jobs"].items():
        for step in job.get("steps", []):
            if "uses" in step:
                yield job_name, step["uses"]


def test_workflow_is_valid_yaml_with_expected_jobs():
    doc = _load()
    assert set(doc["jobs"]) == {
        "independent-assurance-core", "assurance-architecture-guards",
        "assurance-langgraph", "assurance-autogen", "assurance-crewai", "assurance-voltagent",
    }


def test_top_level_permissions_are_read_only():
    doc = _load()
    assert doc["permissions"] == {"contents": "read"}


def test_no_job_overrides_permissions():
    doc = _load()
    for job_name, job in doc["jobs"].items():
        assert "permissions" not in job, f"{job_name} overrides the read-only top-level permissions"


def test_every_third_party_action_is_pinned_to_a_full_commit_sha():
    doc = _load()
    for job_name, uses in _iter_uses(doc):
        match = _USES_SHA_RE.match(uses)
        assert match, f"{job_name}: {uses!r} is not pinned to a full 40-character commit SHA"


def test_no_write_token_or_secret_referenced_anywhere():
    text = WORKFLOW_PATH.read_text(encoding="utf-8")
    assert "GITHUB_TOKEN" not in text
    assert "secrets." not in text
    assert "permissions: write" not in text and "contents: write" not in text


def test_mandatory_core_job_runs_all_three_hard_gates():
    doc = _load()
    steps_text = " ".join(
        str(s.get("run", "")) for s in doc["jobs"]["independent-assurance-core"]["steps"]
    )
    assert "python -m assurance run" in steps_text
    assert "model/run_tlc.sh" in steps_text
    assert "python -m mutation" in steps_text


def test_evidence_bundle_is_uploaded_even_on_failure():
    doc = _load()
    upload_steps = [
        s for s in doc["jobs"]["independent-assurance-core"]["steps"]
        if str(s.get("uses", "")).startswith("actions/upload-artifact@")
    ]
    assert upload_steps, "no upload-artifact step found in independent-assurance-core"
    assert upload_steps[0].get("if") == "always()"
