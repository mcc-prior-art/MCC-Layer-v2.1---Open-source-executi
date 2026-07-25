"""Deterministic validation of the Normative v1.0 conformance artifacts.

Fails closed: any structural problem is a validation failure, never a
warning. Returns a list of error strings; an empty list means valid.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import List

from mcc_conformance.extract import SPEC_FILES
from mcc_conformance.generate import BASELINE, OUT_DIR, build_requirements
from mcc_conformance.models import ALLOWED_STATUSES, Requirement

REQUIRES_RATIONALE = {"PARTIAL", "GAP", "NOT_APPLICABLE", "NOT_ASSESSED"}


def _load_schema(repo_root: Path, name: str) -> dict:
    return json.loads((repo_root / OUT_DIR / "schemas" / name).read_text(encoding="utf-8"))


def validate_requirements(reqs: List[Requirement], repo_root: Path) -> List[str]:
    """Structural validation of an arbitrary requirement list against an
    arbitrary repo root. Pulled out of validate_in_memory so tests can feed
    it deliberately invalid data without needing to re-extract the real
    specifications.
    """
    errors: List[str] = []

    if not reqs:
        errors.append("No requirements discovered — extraction produced an empty set.")
        return errors

    seen_ids = set()
    for r in reqs:
        if r.requirement_id in seen_ids:
            errors.append(f"Duplicate requirement_id: {r.requirement_id}")
        seen_ids.add(r.requirement_id)

        if r.conformance_status not in ALLOWED_STATUSES:
            errors.append(
                f"{r.requirement_id}: invalid conformance_status "
                f"{r.conformance_status!r} (allowed: {ALLOWED_STATUSES})"
            )

        if r.conformance_status == "CONFORMANT":
            if not r.implementation_references:
                errors.append(
                    f"{r.requirement_id}: CONFORMANT requires at least one "
                    "implementation_reference"
                )
            if not r.test_references:
                errors.append(
                    f"{r.requirement_id}: CONFORMANT requires at least one "
                    "test_reference"
                )

        if r.conformance_status in REQUIRES_RATIONALE and not r.rationale.strip():
            errors.append(
                f"{r.requirement_id}: status {r.conformance_status} requires a "
                "non-empty rationale"
            )

        if r.specification_version != "1.0":
            errors.append(
                f"{r.requirement_id}: specification_version must be '1.0', got "
                f"{r.specification_version!r}"
            )

        for ref in (
            list(r.implementation_references)
            + list(r.test_references)
            + list(r.evidence_references)
        ):
            path_part = ref.split("::", 1)[0].split(":", 1)[0]
            if not (repo_root / path_part).exists():
                errors.append(
                    f"{r.requirement_id}: referenced repository path does not "
                    f"exist: {path_part!r} (from {ref!r})"
                )

        if not (repo_root / r.source_file).exists():
            errors.append(
                f"{r.requirement_id}: source_file does not exist: {r.source_file!r}"
            )

    # Every discovered requirement must be represented exactly once — trivially
    # true given we generated `reqs` from a single extraction pass with the
    # duplicate check above, but re-assert the invariant explicitly for the
    # benefit of future refactors of this module.
    if len(seen_ids) != len(reqs):
        errors.append("Requirement count does not match unique requirement_id count.")

    return errors


def validate_baseline_provenance() -> List[str]:
    errors: List[str] = []
    if BASELINE["baseline_commit"] != "a65b2f375408dfbe8df86fbfc09724c5c45d3ba4":
        errors.append("baseline.json baseline_commit does not match the declared normative commit.")
    if len(BASELINE["specifications"]) != len(SPEC_FILES):
        errors.append("baseline.json does not list exactly the four normative specifications.")
    for spec in BASELINE["specifications"]:
        if spec["version"] != "1.0" or spec["status"] != "Normative":
            errors.append(
                f"baseline.json: {spec['specification_id']} must show version 1.0 / "
                "status Normative"
            )
    return errors


def validate_in_memory(repo_root: Path) -> List[str]:
    """Validate the requirement set as freshly (re)computed from the specs,
    plus baseline provenance.

    This is the check CI relies on: it does not trust any committed file,
    it recomputes from the four specification sources and validates the
    result. A separate determinism check (validate_committed_matches)
    additionally confirms the committed artifacts equal this output.
    """
    reqs = build_requirements(repo_root)
    return validate_requirements(reqs, repo_root) + validate_baseline_provenance()


def _check_object(obj: dict, schema: dict, label: str) -> List[str]:
    """Minimal, dependency-free structural check: required keys, unknown keys
    (when additionalProperties is false), enum membership, and basic type
    matching. Sufficient for this repository's flat, hand-authored schemas;
    matches the house convention (see mcc_compliance.capability_profile) of a
    pure-Python validator being authoritative over a published JSON Schema
    used for external documentation/tooling.
    """
    errors: List[str] = []
    props = schema.get("properties", {})
    for key in schema.get("required", []):
        if key not in obj:
            errors.append(f"{label}: missing required field {key!r}")
    if schema.get("additionalProperties") is False:
        for key in obj:
            if key not in props:
                errors.append(f"{label}: unexpected field {key!r}")
    for key, value in obj.items():
        prop_schema = props.get(key)
        if prop_schema is None:
            continue
        enum = prop_schema.get("enum")
        if enum is not None and value not in enum:
            errors.append(f"{label}: field {key!r} value {value!r} not in {enum}")
        ptype = prop_schema.get("type")
        if ptype == "array" and not isinstance(value, list):
            errors.append(f"{label}: field {key!r} must be an array")
        elif ptype == "string" and value is not None and not isinstance(value, str):
            errors.append(f"{label}: field {key!r} must be a string")
        elif ptype == ["string", "null"] and value is not None and not isinstance(value, str):
            errors.append(f"{label}: field {key!r} must be a string or null")
    return errors


def validate_schemas(repo_root: Path) -> List[str]:
    errors: List[str] = []
    req_schema = _load_schema(repo_root, "requirement.schema.json")
    base_schema = _load_schema(repo_root, "baseline.schema.json")

    baseline_path = repo_root / OUT_DIR / "baseline.json"
    requirements_path = repo_root / OUT_DIR / "requirements.json"
    if not baseline_path.exists() or not requirements_path.exists():
        errors.append("baseline.json / requirements.json not found; run generate first.")
        return errors

    baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
    errors += _check_object(baseline, base_schema, "baseline.json")

    payload = json.loads(requirements_path.read_text(encoding="utf-8"))
    for req in payload.get("requirements", []):
        errors += _check_object(req, req_schema, req.get("requirement_id", "?"))

    return errors


def validate_committed_matches_generated(repo_root: Path) -> List[str]:
    """Confirm the committed artifacts are byte-identical to a fresh generation.

    This is the determinism + drift check: CI runs generate() into a temp
    location conceptually by comparing in-memory output to the committed
    files, so uncommitted regeneration is always caught.
    """
    from mcc_conformance import generate as gen

    errors: List[str] = []
    reqs = build_requirements(repo_root)
    expected = {
        "baseline.json": gen._baseline_json(),
        "requirements.json": gen._requirements_json(reqs),
        "traceability_matrix.json": gen._matrix_json(reqs),
        "traceability_matrix.md": gen._matrix_md(reqs),
        "gap_report.md": gen._gap_report_md(reqs),
    }
    for name, expected_content in expected.items():
        path = repo_root / OUT_DIR / name
        if not path.exists():
            errors.append(f"{name} is missing; run: python -m mcc_conformance generate")
            continue
        actual = path.read_text(encoding="utf-8")
        if actual != expected_content:
            errors.append(
                f"{name} is stale relative to the specifications / assessment "
                "rules. Run: python -m mcc_conformance generate, then commit "
                "the result."
            )
    return errors


def validate_all(repo_root: Path) -> List[str]:
    errors: List[str] = []
    errors += validate_in_memory(repo_root)
    errors += validate_schemas(repo_root)
    errors += validate_committed_matches_generated(repo_root)
    return errors
