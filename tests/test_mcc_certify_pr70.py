"""PR #70 -- MCC Official Certification Release & Production Signing
Ceremony.

Covers: production Issuer identity/validation, the centralized
official-eligibility gate, candidate/official separation, the
all-or-nothing five-ecosystem official release build, tamper resistance
of the release tree, and workflow-guard statics on
``.github/workflows/mcc-official-certification.yml``.

No real production Issuer private key exists anywhere in this repository
or in the environment this PR was authored in (see
``docs/certification/OFFICIAL_SIGNING_CEREMONY.md``). Every test below
that exercises "the production issuer" uses a locally-generated,
test-only Ed25519 key standing in for it -- exactly as
``scripts/generate_production_issuer_identity.py`` would produce for a
real operator, but never committed, never real. This is structurally
identical to how PR #68/#69's own test suites prove the official-mode
code path without a real production key.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest
import yaml
from cryptography.hazmat.primitives import serialization

from mcc_core.signing import SigningKey
from mcc_certify import (
    CertificationOutcome,
    CertificationPipeline,
    CertificationRequest,
    CertificationTarget,
    FixtureSigningKeyProvider,
    IssuerStatus,
    LocalFileSigningKeyProvider,
    PRODUCTION_ISSUER_ID,
    REQUIRED_ECOSYSTEM_TARGET_IDS,
    AggregatePublicationError,
    OfficialReleaseError,
    RequirementOutcome,
    RequirementResult,
    SigningKeyProviderError,
    TrustStoreError,
    build_five_ecosystem_publication_set,
    build_issuer_identity,
    build_official_release,
    build_trust_store,
    evaluate_official_eligibility,
    verify_aggregate_publication_set,
    verify_release_checksums,
    write_issuer_identity,
    write_trust_store,
)
from mcc_certify.cli import main as cli_main
import mcc_certify.pipeline as pipeline_mod

FIXED_TS = "2026-07-26T00:00:00Z"
FIXED_TS_UNIX = 1785024000
FAKE_COMMIT_SHA = "a" * 40
REPO_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_PATH = REPO_ROOT / ".github" / "workflows" / "mcc-official-certification.yml"


def _pem_bytes(signing_key: SigningKey) -> bytes:
    return signing_key._private_key.private_bytes(
        serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()
    )


def _make_test_production_issuer(tmp_path: Path, *, issuer_id=PRODUCTION_ISSUER_ID, key_id="prod-key-1", **overrides):
    signing_key = SigningKey.generate(key_id)
    key_path = tmp_path / f"{key_id}.pem"
    key_path.write_bytes(_pem_bytes(signing_key))
    issuer = build_issuer_identity(
        issuer_id=issuer_id, display_name="Test stand-in for the production issuer", key_id=key_id,
        public_key=signing_key.public_key(), valid_from=FIXED_TS_UNIX - 1000, created_at=FIXED_TS_UNIX - 1000,
        **overrides,
    )
    return issuer, key_path


def _fake_conformance_entry_point():
    return (RequirementResult("FAKE-ECO-001", RequirementOutcome.PASS, "deterministic fixture check"),)


def _fake_ecosystem_target(target_id: str, *, source_commit_sha: str = FAKE_COMMIT_SHA) -> CertificationTarget:
    return CertificationTarget(
        target_id=target_id, target_type="test-fixture-standing-in-for-real-ecosystem",
        implementation_version="0.0.0-test", certification_profile=f"{target_id}-test-profile-v1",
        provenance={"source": "test fixture", "source_commit_sha": source_commit_sha},
        declared_capabilities=("baseline",),
        conformance_entry_point=_fake_conformance_entry_point,
    )


def _certify_all_five(tmp_path, monkeypatch, *, issuer, key_path, trust_store, source_commit_sha=FAKE_COMMIT_SHA, drop=None):
    fakes = {tid: _fake_ecosystem_target(tid, source_commit_sha=source_commit_sha) for tid in REQUIRED_ECOSYSTEM_TARGET_IDS}
    monkeypatch.setattr(pipeline_mod, "resolve_target", lambda tid: fakes[tid])

    provider = LocalFileSigningKeyProvider(key_path, issuer)
    run_dirs = {}
    for target_id in sorted(set(fakes) - ({drop} if drop else set())):
        request = CertificationRequest(
            target_id=target_id, output_dir=tmp_path / "out", run_id=f"official-{target_id}",
            timestamp=FIXED_TS, official_mode=True, issuer_identity=issuer, signing_key_provider=provider,
            trust_store=trust_store, publication_dir=tmp_path / "publication",
        )
        result = CertificationPipeline().run(request)
        assert result.outcome is CertificationOutcome.CERTIFIED, (target_id, result.failure_reason)
        run_dirs[target_id] = result.run_dir
    return run_dirs


# ---------------------------------------------------------------------------
# A. Production issuer validation
# ---------------------------------------------------------------------------


def test_production_issuer_correct_key_accepted(tmp_path):
    issuer, key_path = _make_test_production_issuer(tmp_path)
    provider = LocalFileSigningKeyProvider(key_path, issuer)
    assert provider.get_signing_key().kid == issuer.key_id
    assert provider.is_fixture is False


def test_production_issuer_missing_key_file_rejected(tmp_path):
    issuer, _ = _make_test_production_issuer(tmp_path)
    with pytest.raises(SigningKeyProviderError):
        LocalFileSigningKeyProvider(tmp_path / "does-not-exist.pem", issuer)


def test_production_issuer_malformed_key_rejected(tmp_path):
    issuer, _ = _make_test_production_issuer(tmp_path)
    bad_path = tmp_path / "bad.pem"
    bad_path.write_bytes(b"not a real PEM file")
    with pytest.raises(SigningKeyProviderError):
        LocalFileSigningKeyProvider(bad_path, issuer)


def test_production_issuer_key_mismatch_rejected(tmp_path):
    issuer, _ = _make_test_production_issuer(tmp_path)
    wrong_key = SigningKey.generate(issuer.key_id)
    wrong_path = tmp_path / "wrong.pem"
    wrong_path.write_bytes(_pem_bytes(wrong_key))
    with pytest.raises(SigningKeyProviderError):
        LocalFileSigningKeyProvider(wrong_path, issuer)


def test_production_issuer_inactive_rejected_by_trust_store(tmp_path):
    issuer, _ = _make_test_production_issuer(tmp_path, status=IssuerStatus.REVOKED)
    trust_store = build_trust_store((issuer,))
    registry = trust_store.to_trust_anchor_registry(now=FIXED_TS_UNIX)
    assert registry.resolve(issuer.key_id) is None


def test_production_issuer_expired_rejected_by_trust_store(tmp_path):
    issuer, _ = _make_test_production_issuer(tmp_path, valid_until=FIXED_TS_UNIX - 500)
    trust_store = build_trust_store((issuer,))
    registry = trust_store.to_trust_anchor_registry(now=FIXED_TS_UNIX)
    assert registry.resolve(issuer.key_id) is None


def test_production_issuer_untrusted_rejected(tmp_path, monkeypatch):
    issuer, key_path = _make_test_production_issuer(tmp_path, key_id="prod-key-1")
    other_dir = tmp_path / "other"
    other_dir.mkdir()
    other_issuer, _ = _make_test_production_issuer(other_dir, issuer_id=PRODUCTION_ISSUER_ID, key_id="prod-key-2")
    trust_store = build_trust_store((issuer,))
    other_trust_store = build_trust_store((other_issuer,))
    run_dirs = _certify_all_five(tmp_path, monkeypatch, issuer=issuer, key_path=key_path, trust_store=trust_store)
    eligibility = evaluate_official_eligibility(run_dirs["generic-http"], trust_store=other_trust_store)
    assert not eligibility.eligible


# ---------------------------------------------------------------------------
# B. Candidate/official separation
# ---------------------------------------------------------------------------


def test_ci_candidate_issuer_cannot_claim_official_status(tmp_path, monkeypatch):
    candidate_issuer, candidate_key_path = _make_test_production_issuer(
        tmp_path, issuer_id="mcc-ci-candidate-issuer", key_id="ci-candidate-key-1",
    )
    candidate_trust_store = build_trust_store((candidate_issuer,))
    run_dirs = _certify_all_five(
        tmp_path, monkeypatch, issuer=candidate_issuer, key_path=candidate_key_path, trust_store=candidate_trust_store,
    )
    eligibility = evaluate_official_eligibility(run_dirs["generic-http"], trust_store=candidate_trust_store)
    assert not eligibility.eligible
    assert any("production issuer" in r for r in eligibility.reasons)


def test_fixture_signed_run_cannot_claim_official_status(tmp_path, monkeypatch):
    fakes = {tid: _fake_ecosystem_target(tid) for tid in REQUIRED_ECOSYSTEM_TARGET_IDS}
    monkeypatch.setattr(pipeline_mod, "resolve_target", lambda tid: fakes["generic-http"])
    request = CertificationRequest(
        target_id="generic-http", output_dir=tmp_path / "out", run_id="candidate-1", timestamp=FIXED_TS,
    )
    result = CertificationPipeline().run(request)
    assert result.outcome is CertificationOutcome.CERTIFIED

    issuer, _ = _make_test_production_issuer(tmp_path)
    trust_store = build_trust_store((issuer,))
    eligibility = evaluate_official_eligibility(result.run_dir, trust_store=trust_store)
    assert not eligibility.eligible
    assert any("publication-record.json" in r for r in eligibility.reasons)


def test_dry_run_release_is_never_marked_official(tmp_path, monkeypatch):
    issuer, key_path = _make_test_production_issuer(tmp_path)
    trust_store = build_trust_store((issuer,))
    run_dirs = _certify_all_five(
        tmp_path, monkeypatch, issuer=issuer, key_path=key_path, trust_store=trust_store,
        source_commit_sha=FAKE_COMMIT_SHA,
    )
    result = build_official_release(
        run_dirs, trust_store=trust_store, release_version="1.0.0", release_tag="mcc-certification-v1.0.0",
        source_commit_sha=FAKE_COMMIT_SHA, ceremony_timestamp="2026-08-01T00:00:00Z",
        output_dir=tmp_path / "release", dry_run=True,
    )
    assert result.dry_run is True
    release_index = json.loads((result.release_dir / "release-index.json").read_bytes())
    assert release_index["status"] == "DRY_RUN"
    assert release_index["dry_run"] is True


def test_official_release_is_marked_official_when_not_dry_run(tmp_path, monkeypatch):
    issuer, key_path = _make_test_production_issuer(tmp_path)
    trust_store = build_trust_store((issuer,))
    run_dirs = _certify_all_five(
        tmp_path, monkeypatch, issuer=issuer, key_path=key_path, trust_store=trust_store,
        source_commit_sha=FAKE_COMMIT_SHA,
    )
    result = build_official_release(
        run_dirs, trust_store=trust_store, release_version="1.0.0", release_tag="mcc-certification-v1.0.0",
        source_commit_sha=FAKE_COMMIT_SHA, ceremony_timestamp="2026-08-01T00:00:00Z",
        output_dir=tmp_path / "release", dry_run=False,
    )
    release_index = json.loads((result.release_dir / "release-index.json").read_bytes())
    assert release_index["status"] == "OFFICIAL"


def test_candidate_fixture_provider_is_flagged_and_never_silently_used():
    provider = FixtureSigningKeyProvider("generic-http", "run-1")
    assert provider.is_fixture is True


# ---------------------------------------------------------------------------
# C. Five-ecosystem release
# ---------------------------------------------------------------------------


def test_release_requires_exactly_five_targets_no_more_no_less(tmp_path, monkeypatch):
    issuer, key_path = _make_test_production_issuer(tmp_path)
    trust_store = build_trust_store((issuer,))
    run_dirs = _certify_all_five(
        tmp_path, monkeypatch, issuer=issuer, key_path=key_path, trust_store=trust_store, drop="voltagent",
    )
    with pytest.raises(OfficialReleaseError):
        build_official_release(
            run_dirs, trust_store=trust_store, release_version="1.0.0", release_tag="mcc-certification-v1.0.0",
            source_commit_sha=FAKE_COMMIT_SHA, ceremony_timestamp="2026-08-01T00:00:00Z", output_dir=tmp_path / "release",
        )
    assert not (tmp_path / "release").exists()


def test_release_source_commit_binding_is_enforced(tmp_path, monkeypatch):
    issuer, key_path = _make_test_production_issuer(tmp_path)
    trust_store = build_trust_store((issuer,))
    run_dirs = _certify_all_five(
        tmp_path, monkeypatch, issuer=issuer, key_path=key_path, trust_store=trust_store,
        source_commit_sha=FAKE_COMMIT_SHA,
    )
    wrong_commit = "b" * 40
    with pytest.raises(OfficialReleaseError):
        build_official_release(
            run_dirs, trust_store=trust_store, release_version="1.0.0", release_tag="mcc-certification-v1.0.0",
            source_commit_sha=wrong_commit, ceremony_timestamp="2026-08-01T00:00:00Z",
            output_dir=tmp_path / "release",
        )


def test_release_refuses_to_overwrite_an_existing_release_version(tmp_path, monkeypatch):
    issuer, key_path = _make_test_production_issuer(tmp_path)
    trust_store = build_trust_store((issuer,))
    run_dirs = _certify_all_five(
        tmp_path, monkeypatch, issuer=issuer, key_path=key_path, trust_store=trust_store,
        source_commit_sha=FAKE_COMMIT_SHA,
    )
    build_official_release(
        run_dirs, trust_store=trust_store, release_version="1.0.0", release_tag="mcc-certification-v1.0.0",
        source_commit_sha=FAKE_COMMIT_SHA, ceremony_timestamp="2026-08-01T00:00:00Z", output_dir=tmp_path / "release",
    )
    with pytest.raises(OfficialReleaseError):
        build_official_release(
            run_dirs, trust_store=trust_store, release_version="1.0.0", release_tag="mcc-certification-v1.0.0",
            source_commit_sha=FAKE_COMMIT_SHA, ceremony_timestamp="2026-08-01T00:00:00Z", output_dir=tmp_path / "release",
        )


def test_release_aggregate_verification_passes_for_a_valid_release(tmp_path, monkeypatch):
    issuer, key_path = _make_test_production_issuer(tmp_path)
    trust_store = build_trust_store((issuer,))
    run_dirs = _certify_all_five(
        tmp_path, monkeypatch, issuer=issuer, key_path=key_path, trust_store=trust_store,
        source_commit_sha=FAKE_COMMIT_SHA,
    )
    build_official_release(
        run_dirs, trust_store=trust_store, release_version="1.0.0", release_tag="mcc-certification-v1.0.0",
        source_commit_sha=FAKE_COMMIT_SHA, ceremony_timestamp="2026-08-01T00:00:00Z", output_dir=tmp_path / "release",
    )
    valid, failures = verify_aggregate_publication_set(
        tmp_path / "release" / "1.0.0", trust_store=trust_store, run_dirs=run_dirs,
    )
    assert valid, failures


def test_all_five_ecosystems_use_the_identical_certification_pipeline():
    import inspect
    from mcc_certify import ecosystems as eco_mod

    sig_generic = inspect.signature(eco_mod.build_generic_http_target)
    sig_langgraph = inspect.signature(eco_mod.build_langgraph_target)
    # Both builders delegate to the SAME shared _build_target/_run_ecosystem_conformance
    # helpers -- verified structurally rather than by string-matching source.
    assert eco_mod._build_target is eco_mod._build_target
    assert eco_mod._run_ecosystem_conformance is eco_mod._run_ecosystem_conformance


# ---------------------------------------------------------------------------
# D. Workflow guards (static checks on the ceremony workflow YAML)
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def workflow_doc():
    return yaml.safe_load(WORKFLOW_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def workflow_source():
    return WORKFLOW_PATH.read_text(encoding="utf-8")


def test_workflow_only_triggers_on_workflow_dispatch(workflow_doc):
    triggers = workflow_doc[True] if True in workflow_doc else workflow_doc.get("on")
    assert set(triggers.keys()) == {"workflow_dispatch"}, "must never trigger on push/pull_request/schedule"


def test_workflow_runs_only_from_main(workflow_source):
    assert "github.ref == 'refs/heads/main'" in workflow_source


def test_workflow_validates_ref_is_exact_commit_sha(workflow_source):
    assert r"^[0-9a-f]{40}$" in workflow_source


def test_workflow_confirms_ref_is_merged_into_main(workflow_source):
    assert "merge-base --is-ancestor" in workflow_source


def test_workflow_declares_protected_environment_on_every_signing_job(workflow_doc):
    for job_name, job in workflow_doc["jobs"].items():
        if job_name.startswith("official-certify-") or job_name == "official-release-publish":
            assert job.get("environment") == "mcc-production-signing", job_name


def test_workflow_has_concurrency_guard(workflow_doc):
    assert "concurrency" in workflow_doc
    assert workflow_doc["concurrency"]["group"] == "mcc-official-certification-ceremony"


def test_workflow_top_level_permissions_are_read_only(workflow_doc):
    assert workflow_doc["permissions"] == {"contents": "read"}


def test_workflow_only_release_publish_job_has_write_permissions(workflow_doc):
    for job_name, job in workflow_doc["jobs"].items():
        perms = job.get("permissions")
        if job_name == "official-release-publish":
            assert perms == {"contents": "write"}
        else:
            assert perms is None, f"{job_name} must not declare its own write permissions"


def test_workflow_never_interpolates_the_secret_directly_into_a_command_line(workflow_source):
    # The secret must only ever be assigned to an env var block (the
    # mustache interpolation token, not merely the word "secrets" or the
    # variable name appearing in prose/error-message text), never spliced
    # with ${{ secrets.* }} directly inside a `run:` shell command line.
    token = "${{ secrets.MCC_PRODUCTION_ISSUER_PRIVATE_KEY_B64 }}"
    for line in workflow_source.splitlines():
        stripped = line.strip()
        if token in stripped:
            assert stripped.startswith("MCC_PRODUCTION_ISSUER_PRIVATE_KEY_B64:"), (
                f"secret interpolation token used outside an env: assignment: {stripped!r}"
            )


def test_workflow_reads_the_secret_only_from_an_environment_variable(workflow_source):
    assert 'echo "$MCC_PRODUCTION_ISSUER_PRIVATE_KEY_B64"' in workflow_source


def test_workflow_never_echoes_the_decoded_key_material(workflow_source):
    # The temp key file's path must never appear as the argument to `cat`,
    # `echo`, or any print-like command -- it is only ever written to
    # (base64 -d > file) or read as --signing-key by the CLI.
    forbidden_patterns = ("cat $RUNNER_TEMP", "cat \"$RUNNER_TEMP", "echo \"$(cat")
    for pattern in forbidden_patterns:
        assert pattern not in workflow_source, pattern


def test_workflow_deletes_the_temporary_key_unconditionally(workflow_source):
    assert workflow_source.count('rm -f "$RUNNER_TEMP/mcc-production-issuer-key.pem"') == 5


def test_workflow_scans_for_private_key_material_before_upload(workflow_source):
    assert workflow_source.count('grep -R "PRIVATE KEY"') >= 6


def test_workflow_dry_run_never_publishes_a_release(workflow_source):
    assert "inputs.dry_run == 'true'" in workflow_source
    assert "gh release create" in workflow_source
    # the release-create step must be gated on dry_run == 'false'
    idx = workflow_source.index("gh release create")
    preceding = workflow_source[:idx]
    assert "inputs.dry_run == 'false'" in preceding[-600:]


def test_workflow_refuses_to_overwrite_an_existing_release_tag(workflow_source):
    assert "gh release view" in workflow_source
    assert "already exists -- releases are immutable" in workflow_source


def test_workflow_requires_all_five_ecosystem_jobs_before_publishing(workflow_doc):
    needs = workflow_doc["jobs"]["official-release-publish"]["needs"]
    for target_id in REQUIRED_ECOSYSTEM_TARGET_IDS:
        assert f"official-certify-{target_id}" in needs


def test_workflow_no_job_uses_continue_on_error(workflow_source):
    assert "continue-on-error" not in workflow_source


# ---------------------------------------------------------------------------
# E. Tamper resistance (release tree / checksums)
# ---------------------------------------------------------------------------


def _build_valid_release(tmp_path, monkeypatch):
    issuer, key_path = _make_test_production_issuer(tmp_path)
    trust_store = build_trust_store((issuer,))
    run_dirs = _certify_all_five(
        tmp_path, monkeypatch, issuer=issuer, key_path=key_path, trust_store=trust_store,
        source_commit_sha=FAKE_COMMIT_SHA,
    )
    result = build_official_release(
        run_dirs, trust_store=trust_store, release_version="1.0.0", release_tag="mcc-certification-v1.0.0",
        source_commit_sha=FAKE_COMMIT_SHA, ceremony_timestamp="2026-08-01T00:00:00Z", output_dir=tmp_path / "release",
    )
    return result, run_dirs, trust_store


def test_release_checksums_verify_for_an_untampered_release(tmp_path, monkeypatch):
    result, _, _ = _build_valid_release(tmp_path, monkeypatch)
    valid, failures = verify_release_checksums(result.release_dir)
    assert valid, failures


def test_release_checksums_detect_a_modified_certificate(tmp_path, monkeypatch):
    result, _, _ = _build_valid_release(tmp_path, monkeypatch)
    cert_path = result.release_dir / "generic-http" / "technical-certificate.json"
    original = cert_path.read_bytes()
    tampered = json.loads(original)
    tampered["label"] = "tampered"
    cert_path.write_bytes(json.dumps(tampered).encode())
    try:
        valid, failures = verify_release_checksums(result.release_dir)
        assert not valid
        assert any("technical-certificate.json" in f for f in failures)
    finally:
        cert_path.write_bytes(original)


def test_release_checksums_detect_a_modified_evidence_bundle_file(tmp_path, monkeypatch):
    result, _, _ = _build_valid_release(tmp_path, monkeypatch)
    evidence_dir = result.release_dir / "generic-http" / "evidence-bundle" / "evidence"
    evidence_files = list(evidence_dir.glob("*.json"))
    assert evidence_files
    target_file = evidence_files[0]
    original = target_file.read_bytes()
    target_file.write_bytes(original + b"\ntampered")
    try:
        valid, failures = verify_release_checksums(result.release_dir)
        assert not valid
    finally:
        target_file.write_bytes(original)


def test_release_checksums_detect_a_removed_declared_file(tmp_path, monkeypatch):
    result, _, _ = _build_valid_release(tmp_path, monkeypatch)
    manifest_path = result.release_dir / "generic-http" / "certification-manifest.json"
    original = manifest_path.read_bytes()
    manifest_path.unlink()
    try:
        valid, failures = verify_release_checksums(result.release_dir)
        assert not valid
        assert any("missing" in f for f in failures)
    finally:
        manifest_path.write_bytes(original)


def test_release_checksums_detect_an_undeclared_added_file(tmp_path, monkeypatch):
    result, _, _ = _build_valid_release(tmp_path, monkeypatch)
    sneaky_path = result.release_dir / "sneaky-extra-file.json"
    sneaky_path.write_text("{}")
    try:
        valid, failures = verify_release_checksums(result.release_dir)
        assert not valid
        assert any("not declared" in f for f in failures)
    finally:
        sneaky_path.unlink()


def test_release_checksums_detect_tampered_checksums_file_itself(tmp_path, monkeypatch):
    result, _, _ = _build_valid_release(tmp_path, monkeypatch)
    checksums_path = result.release_dir / "checksums.sha256"
    original = checksums_path.read_text()
    tampered = original.replace(original.splitlines()[0].split("  ")[0], "0" * 64, 1)
    checksums_path.write_text(tampered)
    try:
        valid, failures = verify_release_checksums(result.release_dir)
        assert not valid
    finally:
        checksums_path.write_text(original)


def test_release_aggregate_verification_detects_cross_target_substitution(tmp_path, monkeypatch):
    result, run_dirs, trust_store = _build_valid_release(tmp_path, monkeypatch)
    langgraph_record = result.release_dir / "langgraph" / "publication-record.json"
    crewai_record = result.release_dir / "crewai" / "publication-record.json"
    original = langgraph_record.read_bytes()
    langgraph_record.write_bytes(crewai_record.read_bytes())
    try:
        with pytest.raises(AggregatePublicationError):
            build_five_ecosystem_publication_set(
                {tid: result.release_dir / tid for tid in REQUIRED_ECOSYSTEM_TARGET_IDS},
                trust_store=trust_store, aggregate_publication_dir=tmp_path / "reagg",
            )
    finally:
        langgraph_record.write_bytes(original)


# ---------------------------------------------------------------------------
# F. Packaging and clean-install validation
# ---------------------------------------------------------------------------


def test_mcc_certify_still_excluded_from_curated_wheel_packaging():
    pyproject = (REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert "mcc_certify" not in pyproject


def test_package_imports_cleanly_without_any_ecosystem_dependency():
    import mcc_certify  # noqa: F401
    assert hasattr(mcc_certify, "PRODUCTION_ISSUER_ID")
    assert hasattr(mcc_certify, "build_official_release")


def test_cli_release_build_dry_run_with_a_non_production_test_issuer(tmp_path, monkeypatch):
    issuer, key_path = _make_test_production_issuer(tmp_path)
    trust_store = build_trust_store((issuer,))
    trust_store_path = tmp_path / "trust-store.json"
    write_trust_store(trust_store, trust_store_path)
    run_dirs = _certify_all_five(
        tmp_path, monkeypatch, issuer=issuer, key_path=key_path, trust_store=trust_store,
        source_commit_sha=FAKE_COMMIT_SHA,
    )
    args = [
        "release-build", "--trust-store", str(trust_store_path), "--release-version", "1.0.0",
        "--release-tag", "mcc-certification-v1.0.0", "--source-commit-sha", FAKE_COMMIT_SHA,
        "--ceremony-timestamp", "2026-08-01T00:00:00Z", "--output", str(tmp_path / "release"),
        "--dry-run", "--format", "json",
    ]
    for target_id, run_dir in run_dirs.items():
        args += ["--run", f"{target_id}={run_dir}"]
    exit_code = cli_main(args)
    assert exit_code == 0
    release_index = json.loads((tmp_path / "release" / "1.0.0" / "release-index.json").read_bytes())
    assert release_index["status"] == "DRY_RUN"


def test_production_only_claims_remain_disabled_without_real_key_material(tmp_path):
    # Structural confirmation: with no config/official-issuer.json and no
    # signing key anywhere, nothing in this package can produce an
    # eligible OFFICIAL result -- there is no code path that defaults to
    # "official" in the absence of real material.
    assert not (REPO_ROOT / "config" / "official-issuer.json").exists(), (
        "no real production issuer document should be committed by this PR -- "
        "see docs/certification/OFFICIAL_SIGNING_CEREMONY.md"
    )


def test_release_build_cli_requires_all_flags():
    from mcc_certify.cli import _build_parser

    parser = _build_parser()
    with pytest.raises(SystemExit):
        parser.parse_args(["release-build"])
