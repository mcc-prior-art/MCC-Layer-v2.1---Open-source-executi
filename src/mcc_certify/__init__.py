"""MCC End-to-End Certification Pipeline (PR #67).

Orchestrates the complete MCC Normative v1.0 certification chain for one
Certification Target:

    Certification Target
        -> Conformance Run
        -> Evidence Bundle
        -> Certification Manifest
        -> Technical Certificate
        -> Offline Verification

This package is orchestration and lifecycle integration over the existing,
unchanged Wave A/B/C implementations in ``mcc_evidence`` (Hash Reference,
Evidence Bundle, Certification Manifest, Technical Certificate producers
and verifiers) -- it contains no parallel certification system, no
runtime-governance authority, and no PKI/CA.

This module imports no runtime-governance internals (``mcc_core.gate``,
``mcc_core.authority``, ``mcc_core.coordinator``, ``gateway``,
``egress_proxy``, ``interceptors``) and no optional adapter-framework
packages at import time — see ``tests/test_mcc_certify_architecture_guards.py``.

Public API:

    CertificationTarget, RequirementResult, RequirementOutcome, resolve_target
    CertificationRequest, CertificationPipeline, CertificationResult, CertificationStageResult
    verify_certification_run

PR #68 adds the trust and publication foundation required before official
certification: a versioned Issuer Identity model (``issuer.py``), an
offline Trust Store (``trust_store.py``) that converts into the existing,
unchanged ``mcc_evidence`` Trust Anchor Registry, a pluggable Issuer
signing-key contract (``signing_provider.py``) that replaces implicit
fixture-key derivation in official mode, a static Publication mechanism
(``publication.py``), and trusted offline verification against an explicit
trust-anchor set (``verify_certification_run_trusted``). None of this
issues an official certificate for any of the five production reference
ecosystems -- that remains the next, separate platform milestone.

Registered targets: exactly one, ``reference-fixture`` -- an internal,
deterministic test/reference fixture. Certification of the five production
reference ecosystems (Generic HTTP, LangGraph, CrewAI, AutoGen, VoltAgent)
is the next, separate platform milestone; this package does not certify
them.
"""

from __future__ import annotations

from .issuer import (
    IssuerIdentity,
    IssuerIdentityError,
    IssuerStatus,
    build_issuer_identity,
    public_key_fingerprint,
    read_issuer_identity,
    write_issuer_identity,
)
from .pipeline import (
    CertificationOutcome,
    CertificationPipeline,
    CertificationRequest,
    CertificationResult,
    CertificationStageResult,
    StageStatus,
)
from .publication import (
    PublicationConflictError,
    PublicationError,
    PublicationIndex,
    PublicationRecord,
    PublicationStatus,
    build_publication_record,
    empty_publication_index,
    publish_certificate,
    read_publication_index,
    read_publication_record,
    verify_publication_record,
    write_publication_index,
    write_publication_record,
)
from .signing_provider import (
    FixtureSigningKeyProvider,
    LocalFileSigningKeyProvider,
    SigningKeyProvider,
    SigningKeyProviderError,
)
from .target import (
    CertificationTarget,
    CertifyError,
    MalformedCertificationTargetError,
    REFERENCE_FIXTURE_TARGET_ID,
    RequirementOutcome,
    RequirementResult,
    UnknownCertificationTargetError,
    known_target_ids,
    resolve_target,
)
from .trust_store import (
    TrustStore,
    TrustStoreError,
    build_trust_store,
    read_trust_store,
    write_trust_store,
)
from .verify import RunVerificationError, verify_certification_run, verify_certification_run_trusted

__all__ = [
    "CertifyError",
    "UnknownCertificationTargetError",
    "MalformedCertificationTargetError",
    "RunVerificationError",
    "RequirementOutcome",
    "RequirementResult",
    "CertificationTarget",
    "REFERENCE_FIXTURE_TARGET_ID",
    "known_target_ids",
    "resolve_target",
    "CertificationOutcome",
    "StageStatus",
    "CertificationRequest",
    "CertificationStageResult",
    "CertificationResult",
    "CertificationPipeline",
    "verify_certification_run",
    "verify_certification_run_trusted",
    # PR #68 -- Issuer Identity
    "IssuerIdentity",
    "IssuerIdentityError",
    "IssuerStatus",
    "build_issuer_identity",
    "public_key_fingerprint",
    "read_issuer_identity",
    "write_issuer_identity",
    # PR #68 -- Trust Store
    "TrustStore",
    "TrustStoreError",
    "build_trust_store",
    "read_trust_store",
    "write_trust_store",
    # PR #68 -- Signing-Key Provider
    "SigningKeyProvider",
    "SigningKeyProviderError",
    "LocalFileSigningKeyProvider",
    "FixtureSigningKeyProvider",
    # PR #68 -- Publication
    "PublicationError",
    "PublicationConflictError",
    "PublicationStatus",
    "PublicationRecord",
    "PublicationIndex",
    "build_publication_record",
    "verify_publication_record",
    "empty_publication_index",
    "read_publication_index",
    "write_publication_index",
    "read_publication_record",
    "write_publication_record",
    "publish_certificate",
]
