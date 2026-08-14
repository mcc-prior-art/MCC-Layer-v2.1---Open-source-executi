"""PR #71 (Independent Adversarial Assurance Baseline) scaffolding tests:
the runner spine, the evidence bundle, and the CLI (Workstreams L, M).

These do NOT spin up the real three-process System Under Test (that is
exercised by the workstream test modules themselves, e.g.
``assurance/tests/test_boundary_guards.py``, and by the SUT harness smoke
coverage) -- this file locks in the reusable infrastructure those
workstream tests are built on top of.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from assurance.cli import build_parser, main as cli_main
from assurance.evidence import (
    EvidenceBundleError,
    build_evidence_bundle,
    source_commit_sha,
    verify_evidence_bundle,
)
from assurance.runner import REPO_ROOT, ModuleResult, RunReport, TestOutcome, discover_test_modules, run_all
from mcc_core.signing import SigningKey

REPO_ROOT_PATH = Path(__file__).resolve().parents[1]


# --------------------------------------------------------------------------
# runner
# --------------------------------------------------------------------------


def test_discover_test_modules_finds_boundary_guard():
    modules = discover_test_modules()
    names = {m.name for m in modules}
    assert "test_boundary_guards.py" in names
    assert "conftest.py" not in names
    assert "__init__.py" not in names


def test_run_all_executes_discovered_modules_and_reports_pass():
    report = run_all()
    assert isinstance(report, RunReport)
    summary = report.summary
    assert summary["modules_run"] >= 1
    assert summary["overall_status"] == "PASS"
    assert summary["failed"] == 0
    boundary = [m for m in report.modules if m.path.endswith("test_boundary_guards.py")]
    assert len(boundary) == 1
    assert boundary[0].status == "PASS"
    assert boundary[0].workstream == "ARCH-GUARD"


def test_run_report_to_dict_is_json_serializable():
    report = run_all()
    encoded = json.dumps(report.to_dict())
    decoded = json.loads(encoded)
    assert decoded["run_id"] == report.run_id
    assert decoded["summary"]["overall_status"] in ("PASS", "FAIL")


def test_module_result_status_reflects_failures():
    outcome = TestOutcome(nodeid="x::y", outcome="failed", duration=0.01, longrepr="boom")
    result = ModuleResult(path="assurance/tests/test_fake.py", workstream="Z", tests=[outcome])
    assert result.status == "FAIL"
    assert result.failed == 1 and result.passed == 0


def test_module_result_status_is_error_on_collection_error():
    result = ModuleResult(path="assurance/tests/test_fake.py", workstream="Z", collection_error="import error")
    assert result.status == "ERROR"


def test_module_result_status_is_empty_when_no_tests_collected():
    result = ModuleResult(path="assurance/tests/test_fake.py", workstream="Z")
    assert result.status == "EMPTY"


def test_run_all_reports_a_collection_error_without_crashing(tmp_path):
    broken = tmp_path / "test_broken_module.py"
    broken.write_text("this is not valid python (\n", encoding="utf-8")
    report = run_all(modules=[broken])
    assert len(report.modules) == 1
    assert report.modules[0].status == "ERROR"
    assert report.modules[0].collection_error


# --------------------------------------------------------------------------
# evidence bundle
# --------------------------------------------------------------------------


def _fake_run_report() -> dict:
    return {
        "run_id": "fixed-run-id-for-tests",
        "started_at": "2026-01-01T00:00:00Z",
        "finished_at": "2026-01-01T00:00:01Z",
        "modules": [{"path": "assurance/tests/test_boundary_guards.py", "workstream": "ARCH-GUARD",
                     "status": "PASS", "passed": 4, "failed": 0, "skipped": 0,
                     "collection_error": None, "tests": []}],
        "summary": {"total_tests": 4, "passed": 4, "failed": 0, "skipped": 0,
                    "modules_run": 1, "modules_errored": 0, "overall_status": "PASS"},
    }


def test_build_evidence_bundle_requires_run_id_and_modules(tmp_path):
    with pytest.raises(EvidenceBundleError):
        build_evidence_bundle(output_dir=tmp_path, run_report={"summary": {}}, repo_root=REPO_ROOT_PATH)


def test_build_and_verify_unsigned_bundle_is_intact(tmp_path):
    manifest = build_evidence_bundle(output_dir=tmp_path, run_report=_fake_run_report(), repo_root=REPO_ROOT_PATH)
    assert manifest["schema_version"] == "mcc-independent-assurance-evidence/1"
    assert "sig" not in manifest

    result = verify_evidence_bundle(tmp_path)
    assert result.overall_status == "INTACT"
    assert result.integrity_valid is True
    assert result.signature_present is False


def test_build_and_verify_signed_bundle_trusted(tmp_path):
    key = SigningKey.generate("assurance-test-key")
    build_evidence_bundle(output_dir=tmp_path, run_report=_fake_run_report(), repo_root=REPO_ROOT_PATH, signing_key=key)

    trusted = verify_evidence_bundle(tmp_path, trusted_public_keys_b64=[key.public_key_b64()])
    assert trusted.overall_status == "INTACT"
    assert trusted.signature_valid is True
    assert trusted.signer_trusted is True


def test_verify_signed_bundle_without_trust_is_untrusted_not_invalid(tmp_path):
    key = SigningKey.generate("assurance-test-key")
    build_evidence_bundle(output_dir=tmp_path, run_report=_fake_run_report(), repo_root=REPO_ROOT_PATH, signing_key=key)

    untrusted = verify_evidence_bundle(tmp_path, trusted_public_keys_b64=[])
    assert untrusted.overall_status == "INTACT_UNTRUSTED_SIGNER"
    assert untrusted.integrity_valid is True
    assert untrusted.signer_trusted is False


def test_verify_rejects_tampered_findings(tmp_path):
    key = SigningKey.generate("assurance-test-key")
    build_evidence_bundle(output_dir=tmp_path, run_report=_fake_run_report(), repo_root=REPO_ROOT_PATH, signing_key=key)

    findings_path = tmp_path / "findings" / "workstream_results.json"
    tampered = json.loads(findings_path.read_text(encoding="utf-8"))
    tampered["summary"]["overall_status"] = "PASS"
    tampered["summary"]["failed"] = 999
    findings_path.write_text(json.dumps(tampered), encoding="utf-8")

    result = verify_evidence_bundle(tmp_path, trusted_public_keys_b64=[key.public_key_b64()])
    assert result.overall_status == "INVALID"
    assert result.findings_hash_valid is False


def test_verify_rejects_tampered_manifest_signature(tmp_path):
    key = SigningKey.generate("assurance-test-key")
    build_evidence_bundle(output_dir=tmp_path, run_report=_fake_run_report(), repo_root=REPO_ROOT_PATH, signing_key=key)

    manifest_path = tmp_path / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["summary"] = {"total_tests": 0, "passed": 0, "failed": 0, "skipped": 0,
                            "modules_run": 0, "modules_errored": 0, "overall_status": "PASS"}
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    result = verify_evidence_bundle(manifest_path.parent, trusted_public_keys_b64=[key.public_key_b64()])
    assert result.signature_valid is False


def test_verify_missing_bundle_is_invalid(tmp_path):
    result = verify_evidence_bundle(tmp_path / "does-not-exist")
    assert result.overall_status == "INVALID"
    assert "manifest.json missing" in result.problems[0]


def test_verify_rejects_unsupported_schema_version(tmp_path):
    build_evidence_bundle(output_dir=tmp_path, run_report=_fake_run_report(), repo_root=REPO_ROOT_PATH)
    manifest_path = tmp_path / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["schema_version"] = "mcc-independent-assurance-evidence/999"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    result = verify_evidence_bundle(tmp_path)
    assert result.schema_supported is False
    assert result.overall_status == "INVALID"


def test_source_commit_sha_is_never_load_bearing_and_never_raises(tmp_path):
    # Not a git repo -> must degrade to "unknown", never raise.
    sha = source_commit_sha(tmp_path)
    assert sha == "unknown"


def test_source_commit_sha_on_this_real_repo_looks_like_a_commit():
    sha = source_commit_sha(REPO_ROOT_PATH)
    assert sha == "unknown" or (len(sha) == 40 and all(c in "0123456789abcdef" for c in sha))


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------


def test_cli_parser_requires_a_subcommand():
    parser = build_parser()
    with pytest.raises(SystemExit):
        parser.parse_args([])


def test_cli_run_then_verify_round_trip(tmp_path, capsys):
    out_dir = tmp_path / "bundle"
    exit_code = cli_main(["run", "--output", str(out_dir)])
    assert exit_code == 0
    assert (out_dir / "manifest.json").is_file()
    capsys.readouterr()

    exit_code = cli_main(["verify", "--bundle", str(out_dir)])
    assert exit_code == 0
    captured = json.loads(capsys.readouterr().out)
    assert captured["overall_status"] == "INTACT"


def test_cli_verify_missing_bundle_fails_closed(tmp_path):
    exit_code = cli_main(["verify", "--bundle", str(tmp_path / "nope")])
    assert exit_code == 2


def test_cli_list_workstreams_runs(capsys):
    exit_code = cli_main(["list-workstreams"])
    assert exit_code == 0
    out = capsys.readouterr().out
    assert "ARCH-GUARD" in out
    assert "present" in out


def test_cli_run_requires_signing_key_id_with_signing_key_pem(tmp_path):
    key = SigningKey.generate("k")
    from cryptography.hazmat.primitives import serialization

    pem_path = tmp_path / "key.pem"
    pem_bytes = key._private_key.private_bytes(  # noqa: SLF001 -- test-only introspection
        serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()
    )
    pem_path.write_bytes(pem_bytes)

    exit_code = cli_main(["run", "--output", str(tmp_path / "out"), "--signing-key-pem", str(pem_path)])
    assert exit_code == 2


def test_module_entrypoint_invokes_cli_via_subprocess(tmp_path):
    out_dir = tmp_path / "bundle-subprocess"
    env_pythonpath = f"src:.:{Path('sdk/python/src')}"
    proc = subprocess.run(
        [sys.executable, "-m", "assurance", "list-workstreams"],
        cwd=str(REPO_ROOT_PATH), capture_output=True, text=True,
        env={"PYTHONPATH": env_pythonpath, "PATH": "/usr/bin:/bin"},
        timeout=30,
    )
    assert proc.returncode == 0
    assert "ARCH-GUARD" in proc.stdout
