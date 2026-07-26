"""PR #69 -- Official Certification of the Five Reference Ecosystems.

Covers: the five production `CertificationTarget`s (registration, real
execution, fail-closed dependency handling), and the aggregate five-
ecosystem Publication Set (all-or-nothing build + trusted verification +
tamper/substitution rejection).

Only ``generic-http`` has zero optional framework dependencies, so it is
the only one of the five whose REAL end-to-end conformance run (a real
subprocess MCC Gateway + real HTTP scenarios) is exercised directly in
this test file -- exactly as it is in this actual CI environment (see
``docs/CERTIFICATION_FIVE_ECOSYSTEMS.md``, "Known limitations"). LangGraph/
CrewAI/AutoGen/VoltAgent are proven to fail closed with a clear,
non-fabricated error when their real package is not installed (which is
the true, honest state of this environment) -- their REAL end-to-end runs
happen in their own isolated CI jobs (``certification-langgraph`` etc.),
mirroring the existing ``interop-langgraph``/``interop-autogen``/
``interop-crewai``/``interop-voltagent`` isolation pattern from PR #48.

The aggregate Publication Set mechanism is exercised end-to-end using five
REAL, officially-signed, fully pipeline-produced run directories whose
``target_id``s are the five real ecosystem ids -- ``mcc_certify.pipeline``'s
own ``resolve_target`` is monkeypatched (a test-only seam) to serve a
trivial, deterministic fake ``CertificationTarget`` per ecosystem id
instead of running the real (unavailable) framework, so the aggregate
logic itself is tested against genuine Evidence Bundle / Certification
Manifest / Technical Certificate / Publication Record artifacts, not mocks
of the aggregate function's own inputs.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from cryptography.hazmat.primitives import serialization

from mcc_core.signing import SigningKey
from mcc_certify import (
    CertificationOutcome,
    CertificationPipeline,
    CertificationRequest,
    CertificationTarget,
    LocalFileSigningKeyProvider,
    REFERENCE_FIXTURE_TARGET_ID,
    RequirementOutcome,
    RequirementResult,
    UnknownCertificationTargetError,
    build_issuer_identity,
    build_trust_store,
    known_target_ids,
    resolve_target,
    verify_certification_run_trusted,
    write_issuer_identity,
    write_trust_store,
)
from mcc_certify.aggregate import (
    AggregatePublicationError,
    REQUIRED_ECOSYSTEM_TARGET_IDS,
    build_five_ecosystem_publication_set,
    verify_aggregate_publication_set,
)
from mcc_certify.cli import main as cli_main
from mcc_certify.ecosystems import (
    AUTOGEN_TARGET_ID,
    CREWAI_TARGET_ID,
    ECOSYSTEM_TARGET_IDS,
    EcosystemDependencyUnavailableError,
    GENERIC_HTTP_TARGET_ID,
    LANGGRAPH_TARGET_ID,
    VOLTAGENT_TARGET_ID,
)
from mcc_certify.target import MalformedCertificationTargetError

FIXED_TS = "2026-07-26T00:00:00Z"
FIXED_TS_UNIX = 1785024000


def _pem_bytes(signing_key: SigningKey) -> bytes:
    return signing_key._private_key.private_bytes(
        serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()
    )


def _make_issuer(tmp_path: Path, *, issuer_id="axlogiq-ca-1", key_id="issuer-key-1"):
    signing_key = SigningKey.generate(key_id)
    key_path = tmp_path / f"{key_id}.pem"
    key_path.write_bytes(_pem_bytes(signing_key))
    issuer = build_issuer_identity(
        issuer_id=issuer_id, display_name="AXLOGIQ Certification Authority (test)", key_id=key_id,
        public_key=signing_key.public_key(), valid_from=FIXED_TS_UNIX - 1000, created_at=FIXED_TS_UNIX - 1000,
    )
    return issuer, key_path


# ---------------------------------------------------------------------------
# 1. Target registration
# ---------------------------------------------------------------------------


def test_all_five_ecosystem_target_ids_register():
    for target_id in ECOSYSTEM_TARGET_IDS:
        target = resolve_target(target_id)
        assert target.target_id == target_id


def test_known_target_ids_contains_exactly_six_stable_entries():
    assert known_target_ids() == (
        "autogen", "crewai", "generic-http", "langgraph", REFERENCE_FIXTURE_TARGET_ID, "voltagent",
    )


def test_ecosystem_target_ids_are_stable_across_two_resolutions():
    for target_id in ECOSYSTEM_TARGET_IDS:
        a = resolve_target(target_id)
        b = resolve_target(target_id)
        assert a.target_id == b.target_id == target_id
        assert a.certification_profile == b.certification_profile


def test_ecosystem_target_descriptors_are_schema_valid_dataclasses():
    for target_id in ECOSYSTEM_TARGET_IDS:
        target = resolve_target(target_id)
        assert isinstance(target, CertificationTarget)
        assert target.target_id
        assert target.target_type
        assert target.implementation_version
        assert target.certification_profile
        assert isinstance(target.provenance, dict) and target.provenance
        assert target.declared_capabilities


def test_reference_fixture_target_remains_separate_and_unaffected():
    target = resolve_target(REFERENCE_FIXTURE_TARGET_ID)
    assert target.target_id == REFERENCE_FIXTURE_TARGET_ID
    assert REFERENCE_FIXTURE_TARGET_ID not in ECOSYSTEM_TARGET_IDS


def test_unknown_target_still_fails_closed():
    with pytest.raises(UnknownCertificationTargetError):
        resolve_target("not-a-real-target-id")


def test_no_target_is_officially_certified_merely_by_being_registered():
    # Registration/identity is independent of certification: resolving a
    # target must never itself produce a certificate or claim CERTIFIED.
    for target_id in ECOSYSTEM_TARGET_IDS:
        target = resolve_target(target_id)
        assert not hasattr(target, "certificate_id")
        assert not hasattr(target, "official_status")


def test_ecosystem_target_provenance_records_required_fields():
    target = resolve_target(GENERIC_HTTP_TARGET_ID)
    for key in (
        "ecosystem_name", "ecosystem_package", "ecosystem_version", "adapter_module", "adapter_version",
        "mcc_facade_version", "integration_contract_version", "canonical_protocol_version",
        "adapter_sdk_version", "normative_specification_version", "target_config_hash",
    ):
        assert key in target.provenance, key


def test_ecosystem_target_config_hash_changes_when_identity_changes():
    from mcc_certify.ecosystems import _target_config_hash

    a = _target_config_hash({"target_id": "x", "adapter_version": "1.0.0"})
    b = _target_config_hash({"target_id": "x", "adapter_version": "1.0.1"})
    assert a != b


# ---------------------------------------------------------------------------
# 2. Generic HTTP -- real end-to-end (no optional dependency)
# ---------------------------------------------------------------------------


def test_generic_http_conformance_crosses_a_real_network_boundary():
    target = resolve_target(GENERIC_HTTP_TARGET_ID)
    results = target.run_conformance_checks()
    assert len(results) >= 10
    # every required governance scenario present and PASS
    scenario_ids = {r.requirement_id for r in results}
    for req in ("ECO-GOV-ALLOW-001", "ECO-GOV-DENY-001", "ECO-GOV-REPLAY-001", "ECO-GOV-MISMATCH-001",
                "ECO-GOV-AUDIT-001", "ECO-GOV-AVAILABILITY-001", "ECO-GOV-VALIDITY-001",
                "ECO-CAP-PROFILE-001", "ECO-PROVENANCE-001"):
        assert req in scenario_ids, req
    for r in results:
        if r.outcome is RequirementOutcome.FAIL:
            pytest.fail(f"{r.requirement_id} FAILed: {r.detail}")


def test_generic_http_escalate_and_constrain_are_justified_not_applicable():
    target = resolve_target(GENERIC_HTTP_TARGET_ID)
    results = {r.requirement_id: r for r in target.run_conformance_checks()}
    assert results["ECO-GOV-ESCALATE-001"].outcome is RequirementOutcome.NOT_APPLICABLE
    assert results["ECO-GOV-CONSTRAIN-001"].outcome is RequirementOutcome.NOT_APPLICABLE
    assert results["ECO-GOV-ESCALATE-001"].detail
    assert results["ECO-GOV-CONSTRAIN-001"].detail


def test_generic_http_full_candidate_certification(tmp_path):
    request = CertificationRequest(
        target_id=GENERIC_HTTP_TARGET_ID, output_dir=tmp_path / "out",
        run_id="candidate-1", timestamp=FIXED_TS,
    )
    result = CertificationPipeline().run(request)
    assert result.outcome is CertificationOutcome.CERTIFIED
    assert result.run_dir is not None and result.run_dir.exists()


def test_generic_http_full_official_certification_and_trusted_verification(tmp_path):
    issuer, key_path = _make_issuer(tmp_path)
    trust_store = build_trust_store((issuer,))
    provider = LocalFileSigningKeyProvider(key_path, issuer)
    request = CertificationRequest(
        target_id=GENERIC_HTTP_TARGET_ID, output_dir=tmp_path / "out",
        run_id="official-1", timestamp=FIXED_TS, official_mode=True,
        issuer_identity=issuer, signing_key_provider=provider, trust_store=trust_store,
        publication_dir=tmp_path / "publication",
    )
    result = CertificationPipeline().run(request)
    assert result.outcome is CertificationOutcome.CERTIFIED, result.failure_reason
    report = verify_certification_run_trusted(result.run_dir, trust_store=trust_store)
    assert report["valid"] is True


# ---------------------------------------------------------------------------
# 3. LangGraph / CrewAI / AutoGen / VoltAgent -- real dependency required,
#    fail closed (not fabricated) when unavailable in this environment
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("target_id", [LANGGRAPH_TARGET_ID, CREWAI_TARGET_ID, AUTOGEN_TARGET_ID, VOLTAGENT_TARGET_ID])
def test_framework_ecosystem_fails_closed_without_its_real_dependency(target_id):
    target = resolve_target(target_id)
    try:
        import importlib
        importlib.import_module({
            LANGGRAPH_TARGET_ID: "langgraph",
            CREWAI_TARGET_ID: "crewai",
            AUTOGEN_TARGET_ID: "autogen_agentchat",
        }.get(target_id, "____never____"))
        pytest.skip(f"{target_id}'s real dependency is installed in this environment; "
                    "the fail-closed path is exercised elsewhere")
    except ImportError:
        pass
    with pytest.raises(MalformedCertificationTargetError) as exc_info:
        target.run_conformance_checks()
    assert isinstance(exc_info.value.__cause__ or exc_info.value, (EcosystemDependencyUnavailableError, MalformedCertificationTargetError))


def test_framework_ecosystem_never_reports_a_vacuous_pass_when_dependency_missing():
    # A missing dependency must raise, never return an empty/PASS-only
    # RequirementResult tuple that a caller could mistake for success.
    target = resolve_target(LANGGRAPH_TARGET_ID)
    with pytest.raises(MalformedCertificationTargetError):
        target.run_conformance_checks()


# ---------------------------------------------------------------------------
# 4. Aggregate five-ecosystem Publication Set
# ---------------------------------------------------------------------------


def _fake_conformance_entry_point():
    return (RequirementResult("FAKE-ECO-IDENTITY-001", RequirementOutcome.PASS, "deterministic fixture check"),)


def _fake_ecosystem_target(target_id: str) -> CertificationTarget:
    return CertificationTarget(
        target_id=target_id, target_type="test-fixture-standing-in-for-real-ecosystem",
        implementation_version="0.0.0-test", certification_profile=f"{target_id}-test-profile-v1",
        provenance={"source": "test fixture (real framework unavailable in this test environment)"},
        declared_capabilities=("baseline",),
        conformance_entry_point=_fake_conformance_entry_point,
    )


def _certify_all_five(tmp_path, monkeypatch, *, issuer, key_path, trust_store, drop=None, extra_target_id=None):
    """Produce five (or four+one-substitute, or six) REAL, officially-signed
    run directories -- one per required ecosystem id (unless `drop` names
    one to omit, in which case `extra_target_id` may add a different one in
    its place) -- using a monkeypatched `resolve_target` seam so the real,
    unavailable frameworks are never required."""
    fakes = {tid: _fake_ecosystem_target(tid) for tid in REQUIRED_ECOSYSTEM_TARGET_IDS}
    if extra_target_id:
        fakes[extra_target_id] = _fake_ecosystem_target(extra_target_id)

    def _resolve(target_id):
        if target_id not in fakes:
            raise UnknownCertificationTargetError(target_id)
        return fakes[target_id]

    monkeypatch.setattr("mcc_certify.pipeline.resolve_target", _resolve)

    provider = LocalFileSigningKeyProvider(key_path, issuer)
    run_dirs = {}
    target_ids = set(fakes) - ({drop} if drop else set())
    for target_id in sorted(target_ids):
        request = CertificationRequest(
            target_id=target_id, output_dir=tmp_path / "out", run_id=f"official-{target_id}",
            timestamp=FIXED_TS, official_mode=True, issuer_identity=issuer, signing_key_provider=provider,
            trust_store=trust_store, publication_dir=tmp_path / "publication",
        )
        result = CertificationPipeline().run(request)
        assert result.outcome is CertificationOutcome.CERTIFIED, (target_id, result.failure_reason)
        run_dirs[target_id] = result.run_dir
    return run_dirs


def test_aggregate_publication_set_all_five_succeed(tmp_path, monkeypatch):
    issuer, key_path = _make_issuer(tmp_path)
    trust_store = build_trust_store((issuer,))
    run_dirs = _certify_all_five(tmp_path, monkeypatch, issuer=issuer, key_path=key_path, trust_store=trust_store)

    index, outcomes = build_five_ecosystem_publication_set(
        run_dirs, trust_store=trust_store, aggregate_publication_dir=tmp_path / "aggregate",
    )
    assert len(index.records) == 5
    assert {r.target_id for r in index.records} == REQUIRED_ECOSYSTEM_TARGET_IDS
    assert all(o.valid for o in outcomes)


def test_aggregate_publication_set_verifies_offline(tmp_path, monkeypatch):
    issuer, key_path = _make_issuer(tmp_path)
    trust_store = build_trust_store((issuer,))
    run_dirs = _certify_all_five(tmp_path, monkeypatch, issuer=issuer, key_path=key_path, trust_store=trust_store)
    build_five_ecosystem_publication_set(run_dirs, trust_store=trust_store, aggregate_publication_dir=tmp_path / "aggregate")

    valid, failures = verify_aggregate_publication_set(
        tmp_path / "aggregate", trust_store=trust_store, run_dirs=run_dirs,
    )
    assert valid, failures


def test_aggregate_publication_set_missing_ecosystem_is_all_or_nothing(tmp_path, monkeypatch):
    issuer, key_path = _make_issuer(tmp_path)
    trust_store = build_trust_store((issuer,))
    run_dirs = _certify_all_five(
        tmp_path, monkeypatch, issuer=issuer, key_path=key_path, trust_store=trust_store, drop="voltagent",
    )
    assert len(run_dirs) == 4
    with pytest.raises(AggregatePublicationError):
        build_five_ecosystem_publication_set(run_dirs, trust_store=trust_store, aggregate_publication_dir=tmp_path / "aggregate")
    assert not (tmp_path / "aggregate" / "publication-index.json").exists()


def test_aggregate_publication_set_rejects_a_sixth_unexpected_certificate(tmp_path, monkeypatch):
    issuer, key_path = _make_issuer(tmp_path)
    trust_store = build_trust_store((issuer,))
    run_dirs = _certify_all_five(
        tmp_path, monkeypatch, issuer=issuer, key_path=key_path, trust_store=trust_store,
        extra_target_id="sixth-unexpected-ecosystem",
    )
    with pytest.raises(AggregatePublicationError):
        build_five_ecosystem_publication_set(run_dirs, trust_store=trust_store, aggregate_publication_dir=tmp_path / "aggregate")


def test_aggregate_publication_set_rejects_cross_target_publication_record_substitution(tmp_path, monkeypatch):
    issuer, key_path = _make_issuer(tmp_path)
    trust_store = build_trust_store((issuer,))
    run_dirs = _certify_all_five(tmp_path, monkeypatch, issuer=issuer, key_path=key_path, trust_store=trust_store)

    # Substitute langgraph's publication-record.json with crewai's (a
    # cross-target evidence-reuse attack).
    langgraph_record_path = run_dirs["langgraph"] / "publication-record.json"
    crewai_record_path = run_dirs["crewai"] / "publication-record.json"
    original = langgraph_record_path.read_bytes()
    langgraph_record_path.write_bytes(crewai_record_path.read_bytes())
    try:
        with pytest.raises(AggregatePublicationError):
            build_five_ecosystem_publication_set(run_dirs, trust_store=trust_store, aggregate_publication_dir=tmp_path / "aggregate")
    finally:
        langgraph_record_path.write_bytes(original)


def test_aggregate_publication_set_rejects_duplicate_certificate_id(tmp_path, monkeypatch):
    issuer, key_path = _make_issuer(tmp_path)
    trust_store = build_trust_store((issuer,))
    run_dirs = _certify_all_five(tmp_path, monkeypatch, issuer=issuer, key_path=key_path, trust_store=trust_store)

    # Force autogen's publication record to declare voltagent's certificate_id
    # (duplicate cert id across two "different" ecosystems).
    autogen_record_path = run_dirs["autogen"] / "publication-record.json"
    voltagent_record_path = run_dirs["voltagent"] / "publication-record.json"
    autogen_record = json.loads(autogen_record_path.read_bytes())
    voltagent_record = json.loads(voltagent_record_path.read_bytes())
    autogen_record["certificate_id"] = voltagent_record["certificate_id"]
    from mcc_core.signing import canonical_bytes
    original = autogen_record_path.read_bytes()
    autogen_record_path.write_bytes(canonical_bytes(autogen_record))
    try:
        with pytest.raises(AggregatePublicationError):
            build_five_ecosystem_publication_set(run_dirs, trust_store=trust_store, aggregate_publication_dir=tmp_path / "aggregate")
    finally:
        autogen_record_path.write_bytes(original)


def test_aggregate_publication_set_rejects_tampered_certificate(tmp_path, monkeypatch):
    issuer, key_path = _make_issuer(tmp_path)
    trust_store = build_trust_store((issuer,))
    run_dirs = _certify_all_five(tmp_path, monkeypatch, issuer=issuer, key_path=key_path, trust_store=trust_store)

    cert_path = run_dirs["crewai"] / "technical-certificate.json"
    original = cert_path.read_bytes()
    tampered = json.loads(original)
    tampered["label"] = "tampered-during-test"
    cert_path.write_bytes(json.dumps(tampered).encode())
    try:
        with pytest.raises(AggregatePublicationError):
            build_five_ecosystem_publication_set(run_dirs, trust_store=trust_store, aggregate_publication_dir=tmp_path / "aggregate")
    finally:
        cert_path.write_bytes(original)


def test_aggregate_publication_set_rejects_fixture_issuer_certificate(tmp_path, monkeypatch):
    # A candidate (non-official, fixture-signed) run must never enter the
    # official aggregate publication set -- it has no publication-record.json
    # at all (only official mode produces one), so it fails closed exactly
    # like a missing-ecosystem run.
    issuer, key_path = _make_issuer(tmp_path)
    trust_store = build_trust_store((issuer,))
    run_dirs = _certify_all_five(tmp_path, monkeypatch, issuer=issuer, key_path=key_path, trust_store=trust_store, drop="crewai")

    fakes = {tid: _fake_ecosystem_target(tid) for tid in REQUIRED_ECOSYSTEM_TARGET_IDS}
    monkeypatch.setattr("mcc_certify.pipeline.resolve_target", lambda tid: fakes[tid])
    candidate_request = CertificationRequest(
        target_id="crewai", output_dir=tmp_path / "out", run_id="candidate-not-official", timestamp=FIXED_TS,
    )
    candidate_result = CertificationPipeline().run(candidate_request)
    assert candidate_result.outcome is CertificationOutcome.CERTIFIED
    run_dirs["crewai"] = candidate_result.run_dir

    with pytest.raises(AggregatePublicationError):
        build_five_ecosystem_publication_set(run_dirs, trust_store=trust_store, aggregate_publication_dir=tmp_path / "aggregate")


def test_aggregate_publication_set_rejects_wrong_trust_store(tmp_path, monkeypatch):
    issuer, key_path = _make_issuer(tmp_path)
    trust_store = build_trust_store((issuer,))
    run_dirs = _certify_all_five(tmp_path, monkeypatch, issuer=issuer, key_path=key_path, trust_store=trust_store)

    other_issuer, _ = _make_issuer(tmp_path, issuer_id="axlogiq-ca-1", key_id="issuer-key-1")
    wrong_store = build_trust_store((other_issuer,))
    with pytest.raises(AggregatePublicationError):
        build_five_ecosystem_publication_set(run_dirs, trust_store=wrong_store, aggregate_publication_dir=tmp_path / "aggregate")


# ---------------------------------------------------------------------------
# 5. CLI
# ---------------------------------------------------------------------------


def test_cli_aggregate_publish_end_to_end(tmp_path, monkeypatch, capsys):
    issuer, key_path = _make_issuer(tmp_path)
    trust_store = build_trust_store((issuer,))
    trust_store_path = tmp_path / "trust-store.json"
    write_trust_store(trust_store, trust_store_path)
    run_dirs = _certify_all_five(tmp_path, monkeypatch, issuer=issuer, key_path=key_path, trust_store=trust_store)

    args = ["aggregate-publish", "--trust-store", str(trust_store_path),
            "--publication-dir", str(tmp_path / "aggregate"), "--format", "json"]
    for target_id, run_dir in run_dirs.items():
        args += ["--run", f"{target_id}={run_dir}"]
    exit_code = cli_main(args)
    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["outcome"] == "PUBLISHED"
    assert payload["record_count"] == 5


def test_cli_aggregate_publish_fails_closed_on_missing_ecosystem(tmp_path, monkeypatch):
    issuer, key_path = _make_issuer(tmp_path)
    trust_store = build_trust_store((issuer,))
    trust_store_path = tmp_path / "trust-store.json"
    write_trust_store(trust_store, trust_store_path)
    run_dirs = _certify_all_five(tmp_path, monkeypatch, issuer=issuer, key_path=key_path, trust_store=trust_store, drop="autogen")

    args = ["aggregate-publish", "--trust-store", str(trust_store_path), "--publication-dir", str(tmp_path / "aggregate")]
    for target_id, run_dir in run_dirs.items():
        args += ["--run", f"{target_id}={run_dir}"]
    exit_code = cli_main(args)
    assert exit_code == 1


def test_cli_verify_aggregate_end_to_end(tmp_path, monkeypatch):
    issuer, key_path = _make_issuer(tmp_path)
    trust_store = build_trust_store((issuer,))
    trust_store_path = tmp_path / "trust-store.json"
    write_trust_store(trust_store, trust_store_path)
    run_dirs = _certify_all_five(tmp_path, monkeypatch, issuer=issuer, key_path=key_path, trust_store=trust_store)
    build_five_ecosystem_publication_set(run_dirs, trust_store=trust_store, aggregate_publication_dir=tmp_path / "aggregate")

    args = ["verify-aggregate", "--trust-store", str(trust_store_path), "--publication-dir", str(tmp_path / "aggregate")]
    for target_id, run_dir in run_dirs.items():
        args += ["--run", f"{target_id}={run_dir}"]
    exit_code = cli_main(args)
    assert exit_code == 0


def test_cli_certify_all_five_target_ids_are_accepted_by_argument_parser():
    from mcc_certify.cli import _build_parser

    parser = _build_parser()
    for target_id in ECOSYSTEM_TARGET_IDS:
        args = parser.parse_args(["certify", target_id])
        assert args.target == target_id


def test_cli_certify_unknown_target_returns_nonzero(tmp_path):
    exit_code = cli_main(["certify", "not-a-real-target", "--output", str(tmp_path / "out")])
    assert exit_code != 0
