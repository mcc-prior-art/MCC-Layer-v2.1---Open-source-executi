"""PR #67 — MCC End-to-End Certification Pipeline: direct tests for the
CertificationPipeline / CertificationTarget / offline verifier, exercised
through the same public API the CLI uses (``mcc_certify``).
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from mcc_certify import (
    CertificationOutcome,
    CertificationPipeline,
    CertificationRequest,
    CertificationTarget,
    MalformedCertificationTargetError,
    REFERENCE_FIXTURE_TARGET_ID,
    RequirementOutcome,
    RequirementResult,
    UnknownCertificationTargetError,
    known_target_ids,
    resolve_target,
    verify_certification_run,
)
from mcc_certify.pipeline import CERTIFICATE_FILE, EVIDENCE_BUNDLE_DIR, MANIFEST_FILE, RUN_METADATA_FILE

FIXED_TS = "2026-07-26T00:00:00Z"


def _certify(tmp_path, *, run_id="run-001", timestamp=FIXED_TS, target_id=REFERENCE_FIXTURE_TARGET_ID, **kwargs):
    request = CertificationRequest(
        target_id=target_id, output_dir=tmp_path / "out", run_id=run_id, timestamp=timestamp, **kwargs
    )
    return CertificationPipeline().run(request)


def _passing_target(target_id="test-target", **overrides):
    base = dict(
        target_id=target_id,
        target_type="test-fixture",
        implementation_version="1.0.0",
        certification_profile="test-profile",
        provenance={"source": "test"},
        declared_capabilities=("baseline",),
        conformance_entry_point=lambda: (
            RequirementResult("T-001", RequirementOutcome.PASS),
            RequirementResult("T-002", RequirementOutcome.NOT_APPLICABLE),
        ),
    )
    base.update(overrides)
    return CertificationTarget(**base)


# ---------------------------------------------------------------------------
# 1. Successful complete certification pipeline
# ---------------------------------------------------------------------------


def test_successful_complete_certification_pipeline(tmp_path):
    result = _certify(tmp_path)
    assert result.outcome is CertificationOutcome.CERTIFIED
    assert result.certificate_id
    assert result.run_dir is not None and result.run_dir.exists()
    stage_names = [s.stage for s in result.stages]
    assert stage_names == [
        "preflight", "conformance_run", "evidence_bundle",
        "certification_manifest", "technical_certificate", "offline_verification",
    ]
    assert all(s.status.value == "PASS" for s in result.stages)


def test_all_required_artifacts_are_generated(tmp_path):
    result = _certify(tmp_path)
    run_dir = result.run_dir
    for name in (
        "conformance/conformance-run.json", EVIDENCE_BUNDLE_DIR, MANIFEST_FILE,
        CERTIFICATE_FILE, "verification-report.json", "certification-result.json",
        RUN_METADATA_FILE, "README.txt",
    ):
        assert (run_dir / name).exists(), name


# ---------------------------------------------------------------------------
# 2. Unknown target rejection
# ---------------------------------------------------------------------------


def test_unknown_target_rejected(tmp_path):
    result = _certify(tmp_path, target_id="not-a-real-target")
    assert result.outcome is CertificationOutcome.NOT_CERTIFIED
    assert result.failed_stage == "preflight"
    assert "unknown certification target" in result.failure_reason


def test_resolve_target_raises_for_unknown_target():
    with pytest.raises(UnknownCertificationTargetError):
        resolve_target("crewai")


def test_resolve_target_raises_for_empty_target():
    with pytest.raises(UnknownCertificationTargetError):
        resolve_target("")


def test_known_target_ids_is_exactly_the_reference_fixture():
    assert known_target_ids() == (REFERENCE_FIXTURE_TARGET_ID,)


def test_five_production_ecosystems_are_not_registered():
    for name in ("generic-http", "langgraph", "crewai", "autogen", "voltagent"):
        with pytest.raises(UnknownCertificationTargetError):
            resolve_target(name)


# ---------------------------------------------------------------------------
# 3. Malformed target metadata
# ---------------------------------------------------------------------------


def test_malformed_target_empty_target_id_rejected():
    with pytest.raises(MalformedCertificationTargetError):
        _passing_target(target_id="")


def test_malformed_target_empty_capabilities_rejected():
    with pytest.raises(MalformedCertificationTargetError):
        _passing_target(declared_capabilities=())


def test_malformed_conformance_entry_point_output_rejected(tmp_path):
    from mcc_certify.pipeline import CertificationPipeline as _P

    target = _passing_target(conformance_entry_point=lambda: "not a tuple")
    with pytest.raises(MalformedCertificationTargetError):
        target.run_conformance_checks()


def test_conformance_entry_point_that_raises_is_wrapped_fail_closed():
    def boom():
        raise RuntimeError("boom")

    target = _passing_target(conformance_entry_point=boom)
    with pytest.raises(MalformedCertificationTargetError):
        target.run_conformance_checks()


# ---------------------------------------------------------------------------
# 4-5. Conformance failure prevents bundle/manifest/certificate issuance;
# missing direct test evidence is represented as a FAIL requirement result
# ---------------------------------------------------------------------------


def test_conformance_failure_prevents_certificate_issuance(tmp_path, monkeypatch):
    failing_target = _passing_target(conformance_entry_point=lambda: (
        RequirementResult("T-001", RequirementOutcome.FAIL, "no direct test evidence found"),
    ))
    import mcc_certify.target as target_module

    monkeypatch.setitem(target_module._KNOWN_TARGETS, "test-target", lambda: failing_target)
    result = _certify(tmp_path, target_id="test-target")
    assert result.outcome is CertificationOutcome.NOT_CERTIFIED
    assert result.certificate_id is None
    # Evidence Bundle IS still generated (CI-002: evidence precedes
    # certification) but no Manifest/Certificate exist in the failed run dir.
    assert result.run_dir is not None
    assert (result.run_dir / EVIDENCE_BUNDLE_DIR).exists()
    assert not (result.run_dir / MANIFEST_FILE).exists()
    assert not (result.run_dir / CERTIFICATE_FILE).exists()


def test_conformance_failure_run_dir_is_marked_failed_not_the_real_run_id(tmp_path, monkeypatch):
    failing_target = _passing_target(conformance_entry_point=lambda: (
        RequirementResult("T-001", RequirementOutcome.FAIL),
    ))
    import mcc_certify.target as target_module

    monkeypatch.setitem(target_module._KNOWN_TARGETS, "test-target", lambda: failing_target)
    result = _certify(tmp_path, target_id="test-target", run_id="run-x")
    assert result.run_dir.name == "run-x.failed"
    assert not (tmp_path / "out" / "test-target" / "run-x").exists()


# ---------------------------------------------------------------------------
# 6-7. Evidence Bundle generation failure / invalid Hash Reference
# ---------------------------------------------------------------------------


def test_evidence_bundle_generation_failure_is_caught(tmp_path, monkeypatch):
    import mcc_certify.pipeline as pl

    def boom(*a, **kw):
        raise RuntimeError("simulated Evidence Bundle build failure")

    monkeypatch.setattr(pl, "build_eb001_bundle", boom)
    result = _certify(tmp_path)
    assert result.outcome is CertificationOutcome.NOT_CERTIFIED
    assert result.failed_stage == "evidence_bundle"


def test_invalid_hash_reference_in_manifest_reference_detected_by_verify(tmp_path):
    result = _certify(tmp_path, run_id="run-hashref")
    assert result.outcome is CertificationOutcome.CERTIFIED
    cert_path = result.run_dir / CERTIFICATE_FILE
    cert = json.loads(cert_path.read_bytes())
    cert["manifest_reference"]["hash_reference"]["digest"] = "sha256:" + "0" * 64
    cert_path.write_text(json.dumps(cert), encoding="utf-8")
    report = verify_certification_run(result.run_dir)
    assert not report["valid"]


# ---------------------------------------------------------------------------
# 8-10. Manifest-to-bundle / certificate-to-bundle / certificate-to-manifest
# mismatch (tamper tests)
# ---------------------------------------------------------------------------


def test_tamper_evidence_bundle_content_fails_verification(tmp_path):
    result = _certify(tmp_path, run_id="run-tamper-eb")
    (result.run_dir / EVIDENCE_BUNDLE_DIR / "evidence" / "req-FIXTURE-IDENTITY-001.json").write_bytes(b"tampered")
    report = verify_certification_run(result.run_dir)
    assert not report["valid"]


def test_tamper_certification_manifest_fails_verification(tmp_path):
    result = _certify(tmp_path, run_id="run-tamper-cm")
    manifest_path = result.run_dir / MANIFEST_FILE
    manifest = json.loads(manifest_path.read_bytes())
    manifest["primary_evidence_bundle_reference"]["hash_references"][0]["digest"] = "sha256:" + "1" * 64
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    report = verify_certification_run(result.run_dir)
    assert not report["valid"]


def test_tamper_technical_certificate_fails_verification(tmp_path):
    result = _certify(tmp_path, run_id="run-tamper-tc")
    cert_path = result.run_dir / CERTIFICATE_FILE
    cert = json.loads(cert_path.read_bytes())
    cert["certified_capability_profiles"] = ["something-else"]
    cert_path.write_text(json.dumps(cert), encoding="utf-8")
    report = verify_certification_run(result.run_dir)
    assert not report["valid"]


def test_certificate_evidence_bundle_reference_pointing_elsewhere_fails(tmp_path):
    # Certificate-to-bundle mismatch: corrupt the direct Evidence Bundle
    # Reference's bundle_id so it no longer matches the Manifest's.
    result = _certify(tmp_path, run_id="run-mismatch-eb")
    cert_path = result.run_dir / CERTIFICATE_FILE
    cert = json.loads(cert_path.read_bytes())
    cert["evidence_bundle_reference"]["bundle_id"] = "a-different-bundle"
    cert_path.write_text(json.dumps(cert), encoding="utf-8")
    report = verify_certification_run(result.run_dir)
    assert not report["valid"]


def test_certificate_manifest_reference_pointing_elsewhere_fails(tmp_path):
    # Certificate-to-manifest mismatch: corrupt the Manifest Reference's
    # manifest_id (part of the signed content -> signature fails).
    result = _certify(tmp_path, run_id="run-mismatch-cm")
    cert_path = result.run_dir / CERTIFICATE_FILE
    cert = json.loads(cert_path.read_bytes())
    cert["manifest_reference"]["manifest_id"] = "a-different-manifest"
    cert_path.write_text(json.dumps(cert), encoding="utf-8")
    report = verify_certification_run(result.run_dir)
    assert not report["valid"]


# ---------------------------------------------------------------------------
# 11-13. Target / profile / run-ID identity mismatch across artifacts
# ---------------------------------------------------------------------------


def test_target_identity_mismatch_detected(tmp_path):
    result = _certify(tmp_path, run_id="run-target-mismatch")
    cert_path = result.run_dir / CERTIFICATE_FILE
    cert = json.loads(cert_path.read_bytes())
    cert["subject_id"] = "a-different-target"
    cert_path.write_text(json.dumps(cert), encoding="utf-8")
    report = verify_certification_run(result.run_dir)
    assert not report["valid"]
    assert any("target_id" in f for f in report["failures"]) or not report["valid"]


def test_profile_mismatch_detected(tmp_path):
    result = _certify(tmp_path, run_id="run-profile-mismatch")
    cert_path = result.run_dir / CERTIFICATE_FILE
    cert = json.loads(cert_path.read_bytes())
    cert["label"] = "a-different-profile"
    cert_path.write_text(json.dumps(cert), encoding="utf-8")
    report = verify_certification_run(result.run_dir)
    assert not report["valid"]


def test_run_id_mismatch_detected(tmp_path):
    result = _certify(tmp_path, run_id="run-id-mismatch")
    run_metadata_path = result.run_dir / RUN_METADATA_FILE
    run_metadata = json.loads(run_metadata_path.read_bytes())
    run_metadata["run_id"] = "a-different-run-id"
    run_metadata_path.write_text(json.dumps(run_metadata), encoding="utf-8")
    report = verify_certification_run(result.run_dir)
    # the signing key derivation itself depends on run_id, so tampering
    # run-metadata.json alone desynchronizes the expected Trust Anchor --
    # verification must fail, never silently re-derive a matching key.
    assert not report["valid"]


# ---------------------------------------------------------------------------
# 14-15. Offline verification failure -> no successful certificate remains
# ---------------------------------------------------------------------------


def test_no_successful_certificate_survives_verification_failure(tmp_path, monkeypatch):
    import mcc_certify.pipeline as pl

    class _FakeStatus:
        value = "INVALID"

    # Simplest deterministic way to force Stage 6 failure: monkeypatch the
    # module-level import used inside pipeline.run to always report invalid.
    class _AlwaysInvalid:
        overall_status = _FakeStatus()
        valid = False
        failures = ["forced verification failure"]
        checks = []

    monkeypatch.setattr(pl, "verify_technical_certificate", lambda *a, **kw: _AlwaysInvalid())
    result = _certify(tmp_path, run_id="run-forced-invalid")
    assert result.outcome is CertificationOutcome.NOT_CERTIFIED
    assert result.failed_stage == "offline_verification"
    assert result.certificate_id is None
    assert not (tmp_path / "out" / REFERENCE_FIXTURE_TARGET_ID / "run-forced-invalid").exists()
    assert (tmp_path / "out" / REFERENCE_FIXTURE_TARGET_ID / "run-forced-invalid.failed").exists()


# ---------------------------------------------------------------------------
# 16. Deterministic repeated generation
# ---------------------------------------------------------------------------


def test_deterministic_repeated_generation_produces_byte_identical_artifacts(tmp_path):
    r1 = _certify(tmp_path / "a", run_id="det-run", timestamp=FIXED_TS)
    r2 = _certify(tmp_path / "b", run_id="det-run", timestamp=FIXED_TS)
    assert r1.outcome is r2.outcome is CertificationOutcome.CERTIFIED
    for name in (MANIFEST_FILE, CERTIFICATE_FILE, RUN_METADATA_FILE, "verification-report.json"):
        assert (r1.run_dir / name).read_bytes() == (r2.run_dir / name).read_bytes(), name
    # certification-result.json differs only in that it has no host-specific
    # path fields to begin with -- also compare it directly.
    assert (r1.run_dir / "certification-result.json").read_bytes() == (r2.run_dir / "certification-result.json").read_bytes()


def test_deterministic_regeneration_runs_the_full_pipeline_at_least_twice(tmp_path):
    # Explicit requirement: the test must actually invoke the pipeline twice
    # end to end (not compare a cached single run against itself).
    outputs = [_certify(tmp_path / f"run{i}", run_id="twice", timestamp=FIXED_TS) for i in range(2)]
    assert len({o.certificate_id for o in outputs}) == 1
    hashes = [json.loads((o.run_dir / "certification-result.json").read_bytes())["artifact_hashes"] for o in outputs]
    assert hashes[0] == hashes[1]


# ---------------------------------------------------------------------------
# 17-18. Existing run overwrite rejection / --force behavior
# ---------------------------------------------------------------------------


def test_existing_run_overwrite_is_rejected_without_force(tmp_path):
    r1 = _certify(tmp_path, run_id="dup-run")
    assert r1.outcome is CertificationOutcome.CERTIFIED
    r2 = _certify(tmp_path, run_id="dup-run")
    assert r2.outcome is CertificationOutcome.NOT_CERTIFIED
    assert "already exists" in r2.failure_reason


def test_force_flag_allows_overwrite(tmp_path):
    r1 = _certify(tmp_path, run_id="dup-run-force")
    r2 = _certify(tmp_path, run_id="dup-run-force", force=True)
    assert r2.outcome is CertificationOutcome.CERTIFIED
    assert r1.run_dir == r2.run_dir


# ---------------------------------------------------------------------------
# 19. Interrupted / incomplete run handling
# ---------------------------------------------------------------------------


def test_incomplete_run_is_not_mistaken_for_a_completed_certification(tmp_path):
    # Simulate an interrupted run: a bare .tmp-* staging directory left
    # behind (as if the process died mid-pipeline) must never be picked up
    # as a completed run by verify_certification_run or block a fresh run.
    result = _certify(tmp_path, run_id="interrupted-run")
    assert result.outcome is CertificationOutcome.CERTIFIED
    target_dir = tmp_path / "out" / REFERENCE_FIXTURE_TARGET_ID
    stray_tmp = target_dir / ".tmp-interrupted-run-deadbeef"
    stray_tmp.mkdir()
    (stray_tmp / RUN_METADATA_FILE).write_bytes(b"{}")
    # A fresh certify() for a different run_id must succeed unaffected.
    result2 = _certify(tmp_path, run_id="another-run")
    assert result2.outcome is CertificationOutcome.CERTIFIED
    with pytest.raises(Exception):
        verify_certification_run(stray_tmp)


# ---------------------------------------------------------------------------
# 20-21. Machine-readable CLI output / non-zero exit codes
# ---------------------------------------------------------------------------


def test_cli_json_output_is_valid_json(tmp_path, capsys):
    from mcc_certify.cli import main

    exit_code = main(["certify", REFERENCE_FIXTURE_TARGET_ID, "--output", str(tmp_path / "out"),
                       "--run-id", "cli-run", "--timestamp", FIXED_TS, "--format", "json"])
    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["outcome"] == "CERTIFIED"


def test_cli_returns_nonzero_exit_code_for_unknown_target(tmp_path, capsys):
    from mcc_certify.cli import main

    exit_code = main(["certify", "not-a-real-target", "--output", str(tmp_path / "out")])
    assert exit_code != 0


def test_cli_returns_zero_for_successful_verify(tmp_path, capsys):
    from mcc_certify.cli import main

    main(["certify", REFERENCE_FIXTURE_TARGET_ID, "--output", str(tmp_path / "out"),
          "--run-id", "verify-cli-run", "--timestamp", FIXED_TS])
    capsys.readouterr()
    run_dir = tmp_path / "out" / REFERENCE_FIXTURE_TARGET_ID / "verify-cli-run"
    exit_code = main(["verify", str(run_dir), "--format", "json"])
    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["valid"] is True


def test_cli_list_targets(capsys):
    from mcc_certify.cli import main

    exit_code = main(["list-targets"])
    assert exit_code == 0
    out = capsys.readouterr().out
    assert REFERENCE_FIXTURE_TARGET_ID in out


# ---------------------------------------------------------------------------
# 22-23. Package/import smoke test
# ---------------------------------------------------------------------------


def test_package_imports_cleanly():
    import mcc_certify  # noqa: F401
    assert hasattr(mcc_certify, "CertificationPipeline")
    assert hasattr(mcc_certify, "resolve_target")


def test_module_is_runnable_as_a_script(tmp_path):
    import subprocess
    import sys

    result = subprocess.run(
        [sys.executable, "-m", "mcc_certify", "list-targets"],
        cwd=Path(__file__).resolve().parents[1],
        env={"PYTHONPATH": "src", "PATH": "/usr/bin:/bin:/usr/local/bin"},
        capture_output=True, timeout=60,
    )
    assert result.returncode == 0
    assert REFERENCE_FIXTURE_TARGET_ID in result.stdout.decode()


# ---------------------------------------------------------------------------
# 24-25. Existing conformance baseline / all 91 CONFORMANT linkages unchanged
# ---------------------------------------------------------------------------


def test_pr66_conformance_baseline_unchanged():
    import json as _json
    repo_root = Path(__file__).resolve().parents[1]
    data = _json.loads((repo_root / "conformance" / "normative-v1.0" / "requirements.json").read_bytes())
    from collections import Counter
    counts = Counter(r["conformance_status"] for r in data["requirements"])
    assert counts["CONFORMANT"] == 91
    assert data["requirement_count"] == 810


def test_no_conformant_requirement_lacks_evidence_after_this_pr():
    import json as _json
    repo_root = Path(__file__).resolve().parents[1]
    data = _json.loads((repo_root / "conformance" / "normative-v1.0" / "requirements.json").read_bytes())
    conformant = [r for r in data["requirements"] if r["conformance_status"] == "CONFORMANT"]
    assert len(conformant) == 91
    for r in conformant:
        assert r["implementation_references"] and r["test_references"] and r["evidence_references"]


# ---------------------------------------------------------------------------
# Additional: profile default, capability preservation, requirement outcome
# closed-set enforcement
# ---------------------------------------------------------------------------


def test_default_profile_comes_from_the_target_when_not_overridden(tmp_path):
    result = _certify(tmp_path)
    cert = json.loads((result.run_dir / CERTIFICATE_FILE).read_bytes())
    assert cert["label"] == "reference-fixture-profile-v1"


def test_explicit_profile_override_is_honored(tmp_path):
    result = _certify(tmp_path, profile="custom-profile")
    cert = json.loads((result.run_dir / CERTIFICATE_FILE).read_bytes())
    assert cert["label"] == "custom-profile"


def test_requirement_result_rejects_invalid_outcome():
    with pytest.raises(MalformedCertificationTargetError):
        RequirementResult("X-001", "GAP")  # not a RequirementOutcome member


def test_declared_capabilities_flow_into_certified_capability_profiles(tmp_path):
    result = _certify(tmp_path)
    cert = json.loads((result.run_dir / CERTIFICATE_FILE).read_bytes())
    assert cert["certified_capability_profiles"] == ["baseline"]


def test_verify_certification_run_raises_on_missing_artifacts(tmp_path):
    from mcc_certify.verify import RunVerificationError

    empty_dir = tmp_path / "empty-run"
    empty_dir.mkdir()
    with pytest.raises(RunVerificationError):
        verify_certification_run(empty_dir)
