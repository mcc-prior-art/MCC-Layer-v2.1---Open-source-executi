"""PR #68 -- MCC Certification Trust Anchor, Issuer Key Management &
Publication Foundation.

Covers: Issuer Identity / Trust Store, the Signing-Key Provider contract,
the Publication mechanism, trusted offline verification against an
explicit trust-anchor set, and the CLI's official-mode gating. None of
these tests issue an official certificate for any of the five production
reference ecosystems -- ``reference-fixture`` remains the only registered
target (see ``docs/CERTIFICATION_PIPELINE.md``).
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from mcc_core.signing import SigningKey
from mcc_certify import (
    CertificationOutcome,
    CertificationPipeline,
    CertificationRequest,
    FixtureSigningKeyProvider,
    IssuerIdentity,
    IssuerIdentityError,
    IssuerStatus,
    LocalFileSigningKeyProvider,
    PublicationConflictError,
    PublicationError,
    PublicationRecord,
    REFERENCE_FIXTURE_TARGET_ID,
    RunVerificationError,
    SigningKeyProviderError,
    TrustStore,
    TrustStoreError,
    build_issuer_identity,
    build_publication_record,
    build_trust_store,
    empty_publication_index,
    publish_certificate,
    read_issuer_identity,
    read_publication_index,
    read_trust_store,
    verify_certification_run_trusted,
    verify_publication_record,
    write_issuer_identity,
    write_trust_store,
)
from mcc_certify.cli import main as cli_main

FIXED_TS = "2026-07-26T00:00:00Z"
FIXED_TS_UNIX = 1785024000  # matches FIXED_TS


def _pem_bytes(signing_key: SigningKey) -> bytes:
    return signing_key._private_key.private_bytes(
        serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()
    )


def _make_issuer(tmp_path: Path, *, issuer_id="axlogiq-ca-1", key_id="issuer-key-1", **overrides):
    signing_key = SigningKey.generate(key_id)
    key_path = tmp_path / f"{key_id}.pem"
    key_path.write_bytes(_pem_bytes(signing_key))
    issuer = build_issuer_identity(
        issuer_id=issuer_id, display_name="AXLOGIQ Certification Authority", key_id=key_id,
        public_key=signing_key.public_key(), valid_from=FIXED_TS_UNIX - 1000, created_at=FIXED_TS_UNIX - 1000,
        **overrides,
    )
    return issuer, key_path, signing_key


# ---------------------------------------------------------------------------
# Issuer Identity
# ---------------------------------------------------------------------------


def test_issuer_identity_round_trips_through_dict(tmp_path):
    issuer, _, _ = _make_issuer(tmp_path)
    assert IssuerIdentity.from_dict(issuer.to_dict()) == issuer


def test_issuer_identity_round_trips_through_file(tmp_path):
    issuer, _, _ = _make_issuer(tmp_path)
    path = tmp_path / "issuer.json"
    write_issuer_identity(issuer, path)
    assert read_issuer_identity(path) == issuer


def test_issuer_identity_rejects_tampered_fingerprint(tmp_path):
    issuer, _, _ = _make_issuer(tmp_path)
    d = issuer.to_dict()
    d["public_key_fingerprint"] = "sha256:" + "0" * 64
    with pytest.raises(IssuerIdentityError):
        IssuerIdentity.from_dict(d)


def test_issuer_identity_rejects_unsupported_schema_version(tmp_path):
    issuer, _, _ = _make_issuer(tmp_path)
    d = issuer.to_dict()
    d["issuer_identity_schema_version"] = "mcc-certify-issuer/999"
    with pytest.raises(IssuerIdentityError):
        IssuerIdentity.from_dict(d)


@pytest.mark.parametrize("field", ["issuer_id", "display_name", "key_id"])
def test_issuer_identity_rejects_empty_required_string_fields(tmp_path, field):
    issuer, _, _ = _make_issuer(tmp_path)
    d = issuer.to_dict()
    d[field] = ""
    with pytest.raises(IssuerIdentityError):
        IssuerIdentity.from_dict(d)


def test_issuer_identity_rejects_unsupported_signing_algorithm(tmp_path):
    issuer, _, _ = _make_issuer(tmp_path)
    d = issuer.to_dict()
    d["signing_algorithm"] = "HS256"
    with pytest.raises(IssuerIdentityError):
        IssuerIdentity.from_dict(d)


def test_issuer_identity_rejects_malformed_public_key_b64(tmp_path):
    issuer, _, _ = _make_issuer(tmp_path)
    d = issuer.to_dict()
    d["public_key_b64"] = "not-valid-base64!!!"
    with pytest.raises(IssuerIdentityError):
        IssuerIdentity.from_dict(d)


def test_issuer_identity_rejects_valid_until_not_after_valid_from(tmp_path):
    with pytest.raises(IssuerIdentityError):
        _make_issuer(tmp_path, valid_until=FIXED_TS_UNIX - 1000)


def test_issuer_identity_rejects_missing_required_field(tmp_path):
    issuer, _, _ = _make_issuer(tmp_path)
    d = issuer.to_dict()
    del d["specification_version"]
    with pytest.raises(IssuerIdentityError):
        IssuerIdentity.from_dict(d)


def test_issuer_identity_rejects_non_dict_input():
    with pytest.raises(IssuerIdentityError):
        IssuerIdentity.from_dict(["not", "a", "dict"])


def test_issuer_identity_status_defaults_active(tmp_path):
    issuer, _, _ = _make_issuer(tmp_path)
    assert issuer.status is IssuerStatus.ACTIVE


def test_issuer_identity_resolved_public_key_matches_original(tmp_path):
    issuer, _, signing_key = _make_issuer(tmp_path)
    resolved = issuer.resolved_public_key()
    raw_a = resolved.public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
    raw_b = signing_key.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
    assert raw_a == raw_b


def test_issuer_identity_never_infers_issuer_id_from_filename(tmp_path):
    # Writing to a file whose name has nothing to do with issuer_id must not
    # change what is read back.
    issuer, _, _ = _make_issuer(tmp_path, issuer_id="real-issuer-id")
    path = tmp_path / "totally-unrelated-filename.json"
    write_issuer_identity(issuer, path)
    assert read_issuer_identity(path).issuer_id == "real-issuer-id"


# ---------------------------------------------------------------------------
# Trust Store
# ---------------------------------------------------------------------------


def test_trust_store_round_trips_through_file(tmp_path):
    issuer, _, _ = _make_issuer(tmp_path)
    store = build_trust_store((issuer,))
    path = tmp_path / "trust-store.json"
    write_trust_store(store, path)
    assert read_trust_store(path) == store


def test_trust_store_rejects_duplicate_issuer_key_pair(tmp_path):
    issuer, _, _ = _make_issuer(tmp_path)
    with pytest.raises(TrustStoreError):
        TrustStore(trust_store_schema_version="mcc-certify-trust-store/1", issuers=(issuer, issuer))


def test_trust_store_rejects_conflicting_key_id_bound_to_two_public_keys(tmp_path):
    issuer_a, _, _ = _make_issuer(tmp_path, issuer_id="issuer-a", key_id="shared-key")
    issuer_b, _, _ = _make_issuer(tmp_path, issuer_id="issuer-b", key_id="shared-key")
    with pytest.raises(TrustStoreError):
        TrustStore(trust_store_schema_version="mcc-certify-trust-store/1", issuers=(issuer_a, issuer_b))


def test_trust_store_requires_at_least_one_issuer():
    with pytest.raises(TrustStoreError):
        TrustStore(trust_store_schema_version="mcc-certify-trust-store/1", issuers=())


def test_trust_store_rejects_unsupported_schema_version(tmp_path):
    issuer, _, _ = _make_issuer(tmp_path)
    with pytest.raises(TrustStoreError):
        TrustStore(trust_store_schema_version="mcc-certify-trust-store/999", issuers=(issuer,))


def test_trust_store_resolve_raises_for_unknown_issuer_key_pair(tmp_path):
    issuer, _, _ = _make_issuer(tmp_path)
    store = build_trust_store((issuer,))
    with pytest.raises(TrustStoreError):
        store.resolve("unknown-issuer", "issuer-key-1")


def test_trust_store_to_registry_active_anchor_resolves(tmp_path):
    issuer, _, signing_key = _make_issuer(tmp_path)
    store = build_trust_store((issuer,))
    registry = store.to_trust_anchor_registry(now=FIXED_TS_UNIX)
    anchor = registry.resolve(signing_key.kid)
    assert anchor is not None and anchor.issuer_id == issuer.issuer_id and not anchor.revoked


def test_trust_store_to_registry_not_yet_valid_anchor_excluded(tmp_path):
    issuer, _, signing_key = _make_issuer(tmp_path)
    store = build_trust_store((issuer,))
    registry = store.to_trust_anchor_registry(now=issuer.valid_from - 1)
    assert registry.resolve(signing_key.kid) is None


def test_trust_store_to_registry_expired_anchor_excluded(tmp_path):
    issuer, _, signing_key = _make_issuer(tmp_path, valid_until=FIXED_TS_UNIX - 500)
    store = build_trust_store((issuer,))
    registry = store.to_trust_anchor_registry(now=FIXED_TS_UNIX)
    assert registry.resolve(signing_key.kid) is None


def test_trust_store_to_registry_revoked_anchor_excluded(tmp_path):
    issuer, _, signing_key = _make_issuer(tmp_path, status=IssuerStatus.REVOKED)
    store = build_trust_store((issuer,))
    registry = store.to_trust_anchor_registry(now=FIXED_TS_UNIX)
    assert registry.resolve(signing_key.kid) is None


def test_trust_store_supports_multiple_issuer_keys_for_rotation(tmp_path):
    old_issuer, _, old_key = _make_issuer(tmp_path, issuer_id="axlogiq-ca-1", key_id="old-key")
    new_issuer, _, new_key = _make_issuer(tmp_path, issuer_id="axlogiq-ca-1", key_id="new-key")
    store = build_trust_store((old_issuer, new_issuer))
    registry = store.to_trust_anchor_registry(now=FIXED_TS_UNIX)
    assert registry.resolve(old_key.kid) is not None
    assert registry.resolve(new_key.kid) is not None


def test_trust_store_never_fetches_over_network():
    # A pure static-typing/behavioral guard: read_trust_store's signature
    # only accepts a local path, and this repository has no HTTP client
    # imported anywhere in trust_store.py (also covered by the AST guard in
    # test_mcc_certify_trust_publication_guards.py).
    with pytest.raises((TrustStoreError, OSError)):
        read_trust_store("https://example.invalid/trust-store.json")


# ---------------------------------------------------------------------------
# Signing-Key Provider
# ---------------------------------------------------------------------------


def test_local_file_signing_key_provider_loads_matching_key(tmp_path):
    issuer, key_path, signing_key = _make_issuer(tmp_path)
    provider = LocalFileSigningKeyProvider(key_path, issuer)
    assert provider.get_signing_key().kid == signing_key.kid
    assert provider.expected_issuer_id() == issuer.issuer_id
    assert provider.expected_key_id() == issuer.key_id
    assert provider.is_fixture is False


def test_local_file_signing_key_provider_rejects_mismatched_key(tmp_path):
    issuer, _, _ = _make_issuer(tmp_path)
    other_key = SigningKey.generate(issuer.key_id)
    other_path = tmp_path / "other.pem"
    other_path.write_bytes(_pem_bytes(other_key))
    with pytest.raises(SigningKeyProviderError):
        LocalFileSigningKeyProvider(other_path, issuer)


def test_local_file_signing_key_provider_rejects_missing_file(tmp_path):
    issuer, _, _ = _make_issuer(tmp_path)
    with pytest.raises(SigningKeyProviderError):
        LocalFileSigningKeyProvider(tmp_path / "does-not-exist.pem", issuer)


def test_local_file_signing_key_provider_rejects_malformed_pem(tmp_path):
    issuer, _, _ = _make_issuer(tmp_path)
    bad_path = tmp_path / "bad.pem"
    bad_path.write_bytes(b"not a pem file")
    with pytest.raises(SigningKeyProviderError):
        LocalFileSigningKeyProvider(bad_path, issuer)


def test_fixture_signing_key_provider_is_flagged_as_fixture():
    provider = FixtureSigningKeyProvider(REFERENCE_FIXTURE_TARGET_ID, "run-1")
    assert provider.is_fixture is True
    key = provider.get_signing_key()
    assert key.kid == f"mcc-certify-{REFERENCE_FIXTURE_TARGET_ID}"


def test_fixture_signing_key_provider_is_deterministic():
    a = FixtureSigningKeyProvider("t1", "r1").get_signing_key()
    b = FixtureSigningKeyProvider("t1", "r1").get_signing_key()
    assert a.public_key_b64() == b.public_key_b64()


def test_fixture_signing_key_provider_differs_across_targets():
    a = FixtureSigningKeyProvider("t1", "r1").get_signing_key()
    b = FixtureSigningKeyProvider("t2", "r1").get_signing_key()
    assert a.public_key_b64() != b.public_key_b64()


def test_signing_key_provider_base_class_defaults_not_fixture(tmp_path):
    issuer, key_path, _ = _make_issuer(tmp_path)
    provider = LocalFileSigningKeyProvider(key_path, issuer)
    assert LocalFileSigningKeyProvider.is_fixture.fget(provider) is False


# ---------------------------------------------------------------------------
# Publication
# ---------------------------------------------------------------------------


def _write_fake_artifacts(tmp_path):
    manifest_path = tmp_path / "certification-manifest.json"
    cert_path = tmp_path / "technical-certificate.json"
    integrity_path = tmp_path / "integrity_record.json"
    manifest_path.write_bytes(b'{"manifest": 1}')
    cert_path.write_bytes(b'{"cert": 1}')
    integrity_path.write_bytes(b'{"integrity": 1}')
    return manifest_path, cert_path, integrity_path


def test_build_publication_record_rejects_missing_manifest(tmp_path):
    _, cert_path, integrity_path = _write_fake_artifacts(tmp_path)
    with pytest.raises(PublicationError):
        build_publication_record(
            certificate_id="c1", target_id="t1", issuer_id="i1", key_id="k1",
            certification_manifest_path=tmp_path / "missing.json",
            technical_certificate_path=cert_path,
            evidence_bundle_integrity_record_path=integrity_path,
            evidence_bundle_id="eb1", issuance_timestamp=1000, specification_version="1.0",
            artifact_location="t1/r1",
        )


def test_build_publication_record_rejects_missing_certificate(tmp_path):
    manifest_path, _, integrity_path = _write_fake_artifacts(tmp_path)
    with pytest.raises(PublicationError):
        build_publication_record(
            certificate_id="c1", target_id="t1", issuer_id="i1", key_id="k1",
            certification_manifest_path=manifest_path,
            technical_certificate_path=tmp_path / "missing.json",
            evidence_bundle_integrity_record_path=integrity_path,
            evidence_bundle_id="eb1", issuance_timestamp=1000, specification_version="1.0",
            artifact_location="t1/r1",
        )


def test_verify_publication_record_detects_tampered_manifest(tmp_path):
    manifest_path, cert_path, integrity_path = _write_fake_artifacts(tmp_path)
    record = build_publication_record(
        certificate_id="c1", target_id="t1", issuer_id="i1", key_id="k1",
        certification_manifest_path=manifest_path, technical_certificate_path=cert_path,
        evidence_bundle_integrity_record_path=integrity_path, evidence_bundle_id="eb1",
        issuance_timestamp=1000, specification_version="1.0", artifact_location="t1/r1",
    )
    manifest_path.write_bytes(b'{"manifest": "TAMPERED"}')
    failures = verify_publication_record(
        record, certification_manifest_path=manifest_path, technical_certificate_path=cert_path,
        evidence_bundle_integrity_record_path=integrity_path,
    )
    assert failures


def test_verify_publication_record_detects_missing_artifact_at_verify_time(tmp_path):
    manifest_path, cert_path, integrity_path = _write_fake_artifacts(tmp_path)
    record = build_publication_record(
        certificate_id="c1", target_id="t1", issuer_id="i1", key_id="k1",
        certification_manifest_path=manifest_path, technical_certificate_path=cert_path,
        evidence_bundle_integrity_record_path=integrity_path, evidence_bundle_id="eb1",
        issuance_timestamp=1000, specification_version="1.0", artifact_location="t1/r1",
    )
    cert_path.unlink()
    failures = verify_publication_record(
        record, certification_manifest_path=manifest_path, technical_certificate_path=cert_path,
        evidence_bundle_integrity_record_path=integrity_path,
    )
    assert any("not found" in f for f in failures)


def test_publication_index_rejects_conflicting_records_for_same_certificate_id(tmp_path):
    manifest_path, cert_path, integrity_path = _write_fake_artifacts(tmp_path)
    record = build_publication_record(
        certificate_id="c1", target_id="t1", issuer_id="i1", key_id="k1",
        certification_manifest_path=manifest_path, technical_certificate_path=cert_path,
        evidence_bundle_integrity_record_path=integrity_path, evidence_bundle_id="eb1",
        issuance_timestamp=1000, specification_version="1.0", artifact_location="t1/r1",
    )
    other = build_publication_record(
        certificate_id="c1", target_id="t1", issuer_id="i1-different", key_id="k1",
        certification_manifest_path=manifest_path, technical_certificate_path=cert_path,
        evidence_bundle_integrity_record_path=integrity_path, evidence_bundle_id="eb1",
        issuance_timestamp=1000, specification_version="1.0", artifact_location="t1/r1",
    )
    idx = empty_publication_index().add(record)
    with pytest.raises(PublicationConflictError):
        idx.add(other)


def test_publication_index_idempotent_for_identical_re_add(tmp_path):
    manifest_path, cert_path, integrity_path = _write_fake_artifacts(tmp_path)
    record = build_publication_record(
        certificate_id="c1", target_id="t1", issuer_id="i1", key_id="k1",
        certification_manifest_path=manifest_path, technical_certificate_path=cert_path,
        evidence_bundle_integrity_record_path=integrity_path, evidence_bundle_id="eb1",
        issuance_timestamp=1000, specification_version="1.0", artifact_location="t1/r1",
    )
    idx = empty_publication_index().add(record)
    idx2 = idx.add(record)
    assert idx2.to_dict() == idx.to_dict()


def test_read_publication_index_on_missing_path_returns_empty_index(tmp_path):
    idx = read_publication_index(tmp_path / "does-not-exist.json")
    assert idx.records == ()


def test_publish_certificate_writes_both_record_and_index(tmp_path):
    manifest_path, cert_path, integrity_path = _write_fake_artifacts(tmp_path)
    record = build_publication_record(
        certificate_id="c1", target_id="t1", issuer_id="i1", key_id="k1",
        certification_manifest_path=manifest_path, technical_certificate_path=cert_path,
        evidence_bundle_integrity_record_path=integrity_path, evidence_bundle_id="eb1",
        issuance_timestamp=1000, specification_version="1.0", artifact_location="t1/r1",
    )
    pub_dir = tmp_path / "publication"
    publish_certificate(empty_publication_index(), record, publication_dir=pub_dir)
    assert (pub_dir / "publication-index.json").exists()
    assert (pub_dir / "c1.publication-record.json").exists()
    reloaded = read_publication_index(pub_dir / "publication-index.json")
    assert reloaded.get("c1") == record


def test_publication_record_rejects_expiration_not_after_issuance(tmp_path):
    manifest_path, cert_path, integrity_path = _write_fake_artifacts(tmp_path)
    with pytest.raises(PublicationError):
        build_publication_record(
            certificate_id="c1", target_id="t1", issuer_id="i1", key_id="k1",
            certification_manifest_path=manifest_path, technical_certificate_path=cert_path,
            evidence_bundle_integrity_record_path=integrity_path, evidence_bundle_id="eb1",
            issuance_timestamp=1000, specification_version="1.0", artifact_location="t1/r1",
            expiration_timestamp=1000,
        )


def test_publication_index_write_leaves_no_stray_temp_files(tmp_path):
    manifest_path, cert_path, integrity_path = _write_fake_artifacts(tmp_path)
    record = build_publication_record(
        certificate_id="c1", target_id="t1", issuer_id="i1", key_id="k1",
        certification_manifest_path=manifest_path, technical_certificate_path=cert_path,
        evidence_bundle_integrity_record_path=integrity_path, evidence_bundle_id="eb1",
        issuance_timestamp=1000, specification_version="1.0", artifact_location="t1/r1",
    )
    pub_dir = tmp_path / "publication"
    publish_certificate(empty_publication_index(), record, publication_dir=pub_dir)
    leftover_tmp = list(pub_dir.glob(".tmp-*"))
    assert leftover_tmp == []


# ---------------------------------------------------------------------------
# End-to-end official-mode pipeline + trusted offline verification
# ---------------------------------------------------------------------------


def _run_official(tmp_path, *, run_id="official-1", issuer=None, key_path=None, trust_store=None,
                   publication_dir=None, timestamp=FIXED_TS):
    issuer_final, key_path_final, _ = (issuer, key_path, None) if issuer is not None else (None, None, None)
    if issuer is None:
        issuer_final, key_path_final, _ = _make_issuer(tmp_path)
    trust_store_final = trust_store if trust_store is not None else build_trust_store((issuer_final,))
    publication_dir_final = publication_dir or (tmp_path / "publication")
    provider = LocalFileSigningKeyProvider(key_path_final, issuer_final)
    request = CertificationRequest(
        target_id=REFERENCE_FIXTURE_TARGET_ID, output_dir=tmp_path / "out", run_id=run_id, timestamp=timestamp,
        official_mode=True, issuer_identity=issuer_final, signing_key_provider=provider,
        trust_store=trust_store_final, publication_dir=publication_dir_final,
    )
    result = CertificationPipeline().run(request)
    return result, issuer_final, trust_store_final, publication_dir_final


def test_official_mode_end_to_end_certifies(tmp_path):
    result, *_ = _run_official(tmp_path)
    assert result.outcome is CertificationOutcome.CERTIFIED
    assert result.run_dir is not None and result.run_dir.exists()
    assert (result.run_dir / "publication-record.json").exists()


def test_official_mode_requires_issuer_identity(tmp_path):
    issuer, key_path, _ = _make_issuer(tmp_path)
    provider = LocalFileSigningKeyProvider(key_path, issuer)
    request = CertificationRequest(
        target_id=REFERENCE_FIXTURE_TARGET_ID, output_dir=tmp_path / "out", run_id="r1", timestamp=FIXED_TS,
        official_mode=True, signing_key_provider=provider, trust_store=build_trust_store((issuer,)),
        publication_dir=tmp_path / "pub",
    )
    result = CertificationPipeline().run(request)
    assert result.outcome is CertificationOutcome.NOT_CERTIFIED
    assert result.failed_stage == "issuer_config"


def test_official_mode_rejects_fixture_signing_key_provider(tmp_path):
    issuer, _, _ = _make_issuer(tmp_path)
    request = CertificationRequest(
        target_id=REFERENCE_FIXTURE_TARGET_ID, output_dir=tmp_path / "out", run_id="r1", timestamp=FIXED_TS,
        official_mode=True, issuer_identity=issuer,
        signing_key_provider=FixtureSigningKeyProvider(REFERENCE_FIXTURE_TARGET_ID, "r1"),
        trust_store=build_trust_store((issuer,)), publication_dir=tmp_path / "pub",
    )
    result = CertificationPipeline().run(request)
    assert result.outcome is CertificationOutcome.NOT_CERTIFIED
    assert result.failed_stage == "signing_provider"


def test_official_mode_rejects_issuer_not_present_in_trust_store(tmp_path):
    issuer, key_path, _ = _make_issuer(tmp_path)
    other_issuer, _, _ = _make_issuer(tmp_path, issuer_id="someone-else", key_id="other-key")
    provider = LocalFileSigningKeyProvider(key_path, issuer)
    request = CertificationRequest(
        target_id=REFERENCE_FIXTURE_TARGET_ID, output_dir=tmp_path / "out", run_id="r1", timestamp=FIXED_TS,
        official_mode=True, issuer_identity=issuer, signing_key_provider=provider,
        trust_store=build_trust_store((other_issuer,)), publication_dir=tmp_path / "pub",
    )
    result = CertificationPipeline().run(request)
    assert result.outcome is CertificationOutcome.NOT_CERTIFIED
    assert result.failed_stage == "trust_anchor_set"


def test_official_mode_rejects_revoked_issuer(tmp_path):
    issuer, key_path, _ = _make_issuer(tmp_path, status=IssuerStatus.REVOKED)
    provider = LocalFileSigningKeyProvider(key_path, issuer)
    request = CertificationRequest(
        target_id=REFERENCE_FIXTURE_TARGET_ID, output_dir=tmp_path / "out", run_id="r1", timestamp=FIXED_TS,
        official_mode=True, issuer_identity=issuer, signing_key_provider=provider,
        trust_store=build_trust_store((issuer,)), publication_dir=tmp_path / "pub",
    )
    result = CertificationPipeline().run(request)
    assert result.outcome is CertificationOutcome.NOT_CERTIFIED
    assert result.failed_stage == "trust_anchor_set"


def test_official_mode_requires_publication_dir(tmp_path):
    issuer, key_path, _ = _make_issuer(tmp_path)
    provider = LocalFileSigningKeyProvider(key_path, issuer)
    request = CertificationRequest(
        target_id=REFERENCE_FIXTURE_TARGET_ID, output_dir=tmp_path / "out", run_id="r1", timestamp=FIXED_TS,
        official_mode=True, issuer_identity=issuer, signing_key_provider=provider,
        trust_store=build_trust_store((issuer,)),
    )
    result = CertificationPipeline().run(request)
    assert result.outcome is CertificationOutcome.NOT_CERTIFIED
    assert result.failed_stage == "signing_key_match"


def test_non_official_mode_unaffected_by_new_fields_left_unset(tmp_path):
    request = CertificationRequest(
        target_id=REFERENCE_FIXTURE_TARGET_ID, output_dir=tmp_path / "out", run_id="r1", timestamp=FIXED_TS,
    )
    result = CertificationPipeline().run(request)
    assert result.outcome is CertificationOutcome.CERTIFIED
    stage_names = [s.stage for s in result.stages]
    assert "issuer_config" not in stage_names
    assert "publication_record" not in stage_names


def test_verify_certification_run_trusted_requires_explicit_trust_store(tmp_path):
    result, *_ = _run_official(tmp_path)
    with pytest.raises(RunVerificationError):
        verify_certification_run_trusted(result.run_dir, trust_store=None)


def test_verify_certification_run_trusted_succeeds_against_matching_trust_store(tmp_path):
    result, issuer, trust_store, pub_dir = _run_official(tmp_path)
    idx = read_publication_index(pub_dir / "publication-index.json")
    report = verify_certification_run_trusted(
        result.run_dir, trust_store=trust_store, publication_index=idx, require_published=True,
    )
    assert report["valid"] is True


def test_verify_certification_run_trusted_rejects_wrong_trust_store(tmp_path):
    result, *_ = _run_official(tmp_path)
    other_issuer, _, _ = _make_issuer(tmp_path, issuer_id="axlogiq-ca-1", key_id="issuer-key-1")
    wrong_store = build_trust_store((other_issuer,))
    report = verify_certification_run_trusted(result.run_dir, trust_store=wrong_store)
    assert report["valid"] is False


def test_verify_certification_run_trusted_rejects_missing_publication_entry(tmp_path):
    result, issuer, trust_store, _ = _run_official(tmp_path)
    report = verify_certification_run_trusted(
        result.run_dir, trust_store=trust_store, publication_index=empty_publication_index(),
        require_published=True,
    )
    assert report["valid"] is False
    assert any("Publication Index" in f for f in report["failures"])


def test_verify_certification_run_trusted_detects_tampered_certificate(tmp_path):
    result, issuer, trust_store, pub_dir = _run_official(tmp_path)
    cert_path = result.run_dir / "technical-certificate.json"
    original = cert_path.read_bytes()
    tampered = json.loads(original)
    tampered["label"] = "tampered"
    cert_path.write_bytes(json.dumps(tampered).encode())
    try:
        report = verify_certification_run_trusted(result.run_dir, trust_store=trust_store)
        assert report["valid"] is False
    finally:
        cert_path.write_bytes(original)


def test_verify_certification_run_trusted_raises_for_missing_run_artifacts(tmp_path):
    with pytest.raises(RunVerificationError):
        verify_certification_run_trusted(tmp_path / "no-such-run", trust_store=build_trust_store(
            (_make_issuer(tmp_path)[0],)
        ))


# ---------------------------------------------------------------------------
# CLI official-mode gating
# ---------------------------------------------------------------------------


def test_cli_certify_official_mode_end_to_end(tmp_path):
    issuer, key_path, _ = _make_issuer(tmp_path)
    issuer_path = tmp_path / "issuer.json"
    trust_store_path = tmp_path / "trust-store.json"
    write_issuer_identity(issuer, issuer_path)
    write_trust_store(build_trust_store((issuer,)), trust_store_path)

    exit_code = cli_main([
        "certify", REFERENCE_FIXTURE_TARGET_ID,
        "--output", str(tmp_path / "out"), "--run-id", "cli-official-1", "--timestamp", FIXED_TS,
        "--issuer-config", str(issuer_path), "--signing-key", str(key_path),
        "--trust-store", str(trust_store_path), "--publication-dir", str(tmp_path / "publication"),
    ])
    assert exit_code == 0
    assert (tmp_path / "publication" / "publication-index.json").exists()


def test_cli_certify_rejects_partial_official_flags(tmp_path):
    issuer, key_path, _ = _make_issuer(tmp_path)
    issuer_path = tmp_path / "issuer.json"
    write_issuer_identity(issuer, issuer_path)
    exit_code = cli_main([
        "certify", REFERENCE_FIXTURE_TARGET_ID,
        "--output", str(tmp_path / "out"), "--run-id", "cli-partial", "--timestamp", FIXED_TS,
        "--issuer-config", str(issuer_path),
    ])
    assert exit_code == 2


def test_cli_certify_rejects_mismatched_signing_key(tmp_path):
    issuer, _, _ = _make_issuer(tmp_path)
    other_key = SigningKey.generate(issuer.key_id)
    other_path = tmp_path / "other.pem"
    other_path.write_bytes(_pem_bytes(other_key))
    issuer_path = tmp_path / "issuer.json"
    trust_store_path = tmp_path / "trust-store.json"
    write_issuer_identity(issuer, issuer_path)
    write_trust_store(build_trust_store((issuer,)), trust_store_path)
    exit_code = cli_main([
        "certify", REFERENCE_FIXTURE_TARGET_ID,
        "--output", str(tmp_path / "out"), "--run-id", "cli-mismatch", "--timestamp", FIXED_TS,
        "--issuer-config", str(issuer_path), "--signing-key", str(other_path),
        "--trust-store", str(trust_store_path), "--publication-dir", str(tmp_path / "publication"),
    ])
    assert exit_code == 2


def test_cli_verify_uses_trusted_path_when_trust_store_given(tmp_path):
    issuer, key_path, _ = _make_issuer(tmp_path)
    issuer_path = tmp_path / "issuer.json"
    trust_store_path = tmp_path / "trust-store.json"
    write_issuer_identity(issuer, issuer_path)
    write_trust_store(build_trust_store((issuer,)), trust_store_path)
    pub_dir = tmp_path / "publication"

    cli_main([
        "certify", REFERENCE_FIXTURE_TARGET_ID,
        "--output", str(tmp_path / "out"), "--run-id", "cli-verify-1", "--timestamp", FIXED_TS,
        "--issuer-config", str(issuer_path), "--signing-key", str(key_path),
        "--trust-store", str(trust_store_path), "--publication-dir", str(pub_dir),
    ])
    run_dir = tmp_path / "out" / REFERENCE_FIXTURE_TARGET_ID / "cli-verify-1"
    exit_code = cli_main(["verify", str(run_dir), "--trust-store", str(trust_store_path),
                          "--publication-index", str(pub_dir / "publication-index.json"),
                          "--require-published"])
    assert exit_code == 0


def test_cli_verify_publication_index_requires_trust_store(tmp_path):
    exit_code = cli_main(["verify", str(tmp_path), "--publication-index", str(tmp_path / "idx.json")])
    assert exit_code == 2


def test_cli_verify_require_published_requires_deps(tmp_path):
    exit_code = cli_main(["verify", str(tmp_path), "--require-published"])
    assert exit_code == 2


def test_cli_fixture_mode_unaffected(tmp_path, capsys):
    exit_code = cli_main([
        "certify", REFERENCE_FIXTURE_TARGET_ID,
        "--output", str(tmp_path / "out"), "--run-id", "cli-fixture-1", "--timestamp", FIXED_TS,
        "--format", "json",
    ])
    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["outcome"] == "CERTIFIED"


# ---------------------------------------------------------------------------
# Security / packaging
# ---------------------------------------------------------------------------


def test_no_hmac_reference_in_new_pr68_modules():
    repo_root = Path(__file__).resolve().parents[1]
    for name in ("issuer.py", "trust_store.py", "signing_provider.py", "publication.py"):
        source = (repo_root / "src" / "mcc_certify" / name).read_text(encoding="utf-8")
        assert "hmac" not in source.lower(), f"{name} references HMAC"


def test_no_private_key_pem_committed_under_mcc_certify():
    repo_root = Path(__file__).resolve().parents[1]
    for path in (repo_root / "src" / "mcc_certify").rglob("*.py"):
        source = path.read_text(encoding="utf-8")
        assert "BEGIN PRIVATE KEY" not in source


def test_issuer_and_trust_store_documents_never_contain_private_key_material(tmp_path):
    issuer, _, _ = _make_issuer(tmp_path)
    store = build_trust_store((issuer,))
    for blob in (json.dumps(issuer.to_dict()), json.dumps(store.to_dict())):
        assert "PRIVATE KEY" not in blob
        assert "private_key" not in blob.lower()


def test_official_certification_run_artifacts_contain_no_private_key_material(tmp_path):
    result, *_ = _run_official(tmp_path)
    for path in result.run_dir.rglob("*.json"):
        content = path.read_text(encoding="utf-8")
        assert "PRIVATE KEY" not in content, path
        assert "BEGIN PRIVATE" not in content, path


def test_mcc_certify_still_excluded_from_curated_wheel_packaging():
    repo_root = Path(__file__).resolve().parents[1]
    pyproject = (repo_root / "pyproject.toml").read_text(encoding="utf-8")
    assert "mcc_certify" not in pyproject, (
        "mcc_certify must remain excluded from the curated mcc-core wheel packaging list "
        "(same exclusion as mcc_conformance/mcc_evidence) unless a packaging decision explicitly changes this"
    )


def test_publication_directory_files_contain_no_pem_material(tmp_path):
    result, issuer, trust_store, pub_dir = _run_official(tmp_path)
    for path in pub_dir.rglob("*.json"):
        content = path.read_text(encoding="utf-8")
        assert "PRIVATE KEY" not in content


def test_certification_result_json_never_serializes_a_signing_key_provider():
    # Static/behavioral guard: CertificationRequest's signing_key_provider
    # field must never appear in CertificationResult.to_dict()'s output.
    from mcc_certify.pipeline import CertificationResult, CertificationOutcome as _Outcome

    result = CertificationResult(
        target_id="t", certification_profile="p", run_id="r",
        outcome=_Outcome.CERTIFIED, stages=[], run_dir=None, certificate_id="c",
    )
    d = result.to_dict()
    assert "signing_key_provider" not in d
    assert "issuer_identity" not in d
    assert "trust_store" not in d
