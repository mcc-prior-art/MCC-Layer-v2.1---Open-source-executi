"""Tests for the Governance Capability Profile (PR #47).

Declarative, framework-neutral, versioned, schema-validated, deterministic, and
fail-closed. Capability support is not execution permission; a raw profile may only
self-declare (never masquerade as trusted certification). Offline.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
for p in (ROOT / "src", ROOT / "sdk" / "python" / "src", ROOT):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from mcc_client.contract import REQUIRED_SECURITY_INVARIANTS  # noqa: E402

from mcc_compliance.capability_profile import (  # noqa: E402
    BASELINE_CAPABILITIES,
    KNOWN_CAPABILITIES,
    OPTIONAL_CAPABILITIES,
    ProfileErrorCode,
    canonicalize_profile,
    capability_registry,
    profile_digest,
    validate_profile,
)
from mcc_compliance.program import ProgramStatus, certify, link_capability_profile  # noqa: E402

FIXTURES = ROOT / "tests" / "capability_profiles"
SCHEMA = ROOT / "schemas" / "governance-capability-profile-v1.schema.json"


def _fx(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def _codes(profile: dict) -> set:
    return {e.code for e in validate_profile(profile).errors}


# --------------------------------------------------------------------------- #
# Vocabulary is single-sourced from the normative contract layer.             #
# --------------------------------------------------------------------------- #

def test_baseline_is_the_contract_invariant_set():
    assert BASELINE_CAPABILITIES == tuple(REQUIRED_SECURITY_INVARIANTS)


def test_schema_enum_matches_the_python_registry():
    schema = json.loads(SCHEMA.read_text())
    cap_enum = set(schema["$defs"]["capability"]["enum"])
    opt_enum = set(schema["$defs"]["optional_capability"]["enum"])
    assert cap_enum == set(KNOWN_CAPABILITIES)
    assert opt_enum == set(OPTIONAL_CAPABILITIES)


def test_capability_registry_is_deterministic():
    assert capability_registry() == capability_registry()
    reg = capability_registry()
    assert reg["baseline_capabilities"] == list(BASELINE_CAPABILITIES)
    assert reg["optional_capabilities"] == list(OPTIONAL_CAPABILITIES)


# --------------------------------------------------------------------------- #
# Valid profiles.                                                             #
# --------------------------------------------------------------------------- #

def test_minimal_profile_is_valid():
    r = validate_profile(_fx("minimal-valid.json"))
    assert r.valid and r.digest and r.digest.startswith("sha256:")


def test_full_profile_is_valid():
    assert validate_profile(_fx("full-capable.json")).valid


def test_unsupported_optional_is_valid():
    r = validate_profile(_fx("unsupported-optional.json"))
    assert r.valid


def test_voltagent_example_is_valid_and_non_normative():
    prof = _fx("voltagent-reference-example.json")
    assert validate_profile(prof).valid
    assert prof["adapter"]["framework"] == "voltagent"          # descriptive only
    assert "non-normative" in prof["metadata"]["note"].lower()  # explicitly labeled


# --------------------------------------------------------------------------- #
# Invalid profiles (each fixture triggers its specific code).                 #
# --------------------------------------------------------------------------- #

def test_overlap_rejected():
    assert ProfileErrorCode.SUPPORTED_UNSUPPORTED_OVERLAP in _codes(_fx("invalid-overlap.json"))


def test_unknown_capability_rejected():
    assert ProfileErrorCode.UNKNOWN_CAPABILITY in _codes(_fx("invalid-unknown-capability.json"))


def test_unsupported_profile_version_rejected():
    assert ProfileErrorCode.PROFILE_VERSION_UNSUPPORTED in _codes(_fx("invalid-profile-version.json"))


def test_false_certification_claim_rejected():
    assert ProfileErrorCode.FALSE_CERTIFICATION_CLAIM in _codes(_fx("invalid-false-certification.json"))


def test_constraint_referencing_unsupported_rejected():
    assert ProfileErrorCode.CONSTRAINT_UNKNOWN_CAPABILITY in _codes(_fx("invalid-constraint-ref.json"))


# --------------------------------------------------------------------------- #
# Additional semantic invariants.                                            #
# --------------------------------------------------------------------------- #

def test_missing_baseline_capability_rejected():
    prof = _fx("minimal-valid.json")
    prof["runtime_capabilities"] = [c for c in prof["runtime_capabilities"]
                                    if c != "signature_verified"]
    assert ProfileErrorCode.MISSING_BASELINE_CAPABILITY in _codes(prof)


def test_baseline_declared_unsupported_rejected():
    prof = _fx("minimal-valid.json")
    prof["unsupported_capabilities"] = ["not_revoked"]
    assert ProfileErrorCode.BASELINE_DECLARED_UNSUPPORTED in _codes(prof)


def test_duplicate_capability_rejected():
    prof = _fx("minimal-valid.json")
    prof["runtime_capabilities"] = prof["runtime_capabilities"] + ["signature_verified"]
    assert ProfileErrorCode.DUPLICATE_CAPABILITY in _codes(prof)


def test_unknown_top_level_field_rejected():
    prof = _fx("minimal-valid.json")
    prof["surprise"] = 1
    assert ProfileErrorCode.ADDITIONAL_PROPERTY in _codes(prof)


def test_missing_required_field_rejected():
    prof = _fx("minimal-valid.json")
    del prof["adapter"]
    assert ProfileErrorCode.FIELD_MISSING in _codes(prof)


def test_empty_adapter_identity_rejected():
    prof = _fx("minimal-valid.json")
    prof["adapter"]["name"] = "  "
    assert ProfileErrorCode.ADAPTER_IDENTITY_INVALID in _codes(prof)


def test_unsupported_contract_version_rejected():
    prof = _fx("minimal-valid.json")
    prof["integration_contract"]["version"] = "2.0"
    assert ProfileErrorCode.CONTRACT_VERSION_UNSUPPORTED in _codes(prof)


def test_non_object_profile_fails_closed():
    assert not validate_profile("not-an-object").valid
    assert not validate_profile(None).valid


def test_metadata_is_open_extension_namespace():
    prof = _fx("minimal-valid.json")
    prof["metadata"] = {"anything": {"nested": [1, 2, 3]}, "vendor_x": "ok"}
    assert validate_profile(prof).valid  # metadata does not fail forward-compat


# --------------------------------------------------------------------------- #
# Canonicalization + digest determinism.                                     #
# --------------------------------------------------------------------------- #

def test_canonicalization_is_order_independent():
    prof = _fx("full-capable.json")
    shuffled = dict(prof)
    shuffled["runtime_capabilities"] = list(reversed(prof["runtime_capabilities"]))
    shuffled["optional_capabilities"] = list(reversed(prof["optional_capabilities"]))
    assert canonicalize_profile(prof) == canonicalize_profile(shuffled)
    assert profile_digest(prof) == profile_digest(shuffled)


def test_digest_changes_with_semantic_content():
    a = _fx("minimal-valid.json")
    b = _fx("full-capable.json")
    assert profile_digest(a) != profile_digest(b)


# --------------------------------------------------------------------------- #
# Certification linkage (trust ladder: declared < validated < certified).     #
# --------------------------------------------------------------------------- #

@pytest.fixture(scope="module")
def ref_cert():
    from mcc_compliance.adapters import ReferenceComplianceAdapter
    return certify(ReferenceComplianceAdapter(), contract_version="1.0")


def test_linked_profile_is_certified_not_self_declared(ref_cert):
    prof = _fx("minimal-valid.json")  # adapter identity matches the reference cert
    link = link_capability_profile(ref_cert, prof)
    assert link["self_declared"] is False
    assert link["validation_status"] == "CERTIFIED"
    assert link["profile_digest"] == profile_digest(prof)
    assert ref_cert.status is ProgramStatus.CERTIFIED


def test_identity_mismatch_is_rejected(ref_cert):
    prof = _fx("voltagent-reference-example.json")  # different adapter identity
    link = link_capability_profile(ref_cert, prof)
    assert link["validation_status"] == "REJECTED"
    assert any(e["code"] == "ADAPTER_IDENTITY_MISMATCH" for e in link["errors"])


def test_invalid_profile_linkage_is_rejected(ref_cert):
    link = link_capability_profile(ref_cert, _fx("invalid-overlap.json"))
    assert link["validation_status"] == "REJECTED" and link["errors"]


# --------------------------------------------------------------------------- #
# CLI.                                                                         #
# --------------------------------------------------------------------------- #

def _cli(*args) -> subprocess.CompletedProcess:
    import os
    e = dict(os.environ)
    e["PYTHONPATH"] = f"{ROOT/'src'}:{ROOT/'sdk'/'python'/'src'}:{ROOT}"
    return subprocess.run([sys.executable, "-m", "mcc_compliance", *args],
                          capture_output=True, text=True, env=e, cwd=str(ROOT))


def test_cli_valid_profile_exit_zero():
    r = _cli("validate-capabilities", str(FIXTURES / "minimal-valid.json"))
    assert r.returncode == 0 and "VALID" in r.stdout


def test_cli_invalid_profile_exit_one():
    r = _cli("validate-capabilities", str(FIXTURES / "invalid-overlap.json"))
    assert r.returncode == 1 and "SUPPORTED_UNSUPPORTED_OVERLAP" in r.stderr


def test_cli_missing_file_exit_two():
    r = _cli("validate-capabilities", str(FIXTURES / "does-not-exist.json"))
    assert r.returncode == 2


def test_cli_json_output_is_valid():
    r = _cli("validate-capabilities", str(FIXTURES / "minimal-valid.json"), "--json")
    body = json.loads(r.stdout)
    assert body["valid"] is True and body["digest"]


# --------------------------------------------------------------------------- #
# Backward compatibility + no stack traces.                                   #
# --------------------------------------------------------------------------- #

def test_all_committed_fixtures_validate_as_labeled():
    for f in sorted(FIXTURES.glob("*.json")):
        expected_valid = not f.name.startswith("invalid-")
        assert validate_profile(_fx(f.name)).valid is expected_valid, f.name


def test_normal_validation_failure_has_no_stack_trace():
    r = _cli("validate-capabilities", str(FIXTURES / "invalid-unknown-capability.json"))
    assert "Traceback" not in (r.stdout + r.stderr)
