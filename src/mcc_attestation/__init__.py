"""MCC Attestation — PRE-EXECUTION attestation foundation.

Target architecture this package is the foundation of:

    INTELLIGENCE -> ATTESTER -> CONTROL -> EXECUTION

This package implements ONLY the ATTESTER boundary: a versioned
EvidenceAttestation contract, deterministic canonical representation,
Ed25519 signing, an attester trust model, and deterministic verification.
It does **not** integrate into MCC-Control, ``AuthorityModel``, decision-token
issuance, ``ExecutionGate``, or the Gateway API — that runtime integration is
explicitly deferred to a future PR. Nothing in this package changes any
existing MCC-Core runtime behavior.

Core doctrine (preserve this wording wherever this package is described):

    Intelligence assesses.
    Attestation makes the assessment attributable.
    Control verifies.
    Execution acts.

Four concepts, kept structurally distinct:

    Assessment  — probabilistic semantic judgment.
    Attestation — a signed, attributable assertion *about* that assessment.
    Authority   — permission derived independently from trusted policy /
                  mandates (unaffected by this package).
    Execution   — actuation allowed only through the governed execution path
                  (unaffected by this package).

A signature does NOT make an assessment true. It proves attribution and
integrity: who asserted what, about which bound action, under which
version/context, and during which validity interval. The Attester may be
wrong about the world. The verifier in this package does not, and must not,
determine whether the semantic assessment is correct — only whether the
assertion is authentic, trusted, current, integrity-protected, and correctly
bound. **An EvidenceAttestation does not itself grant execution authority.**

Architectural separation from ``mcc_evidence`` (deliberate, not incidental):
``mcc_evidence`` is **observational** governance/assurance evidence
describing an already-completed governance path — it carries no execution
authority and looks *backward* in time. ``mcc_attestation`` is
**pre-execution** evidence supplied to Control *before* authorization is
evaluated — it looks *forward*. This package does not import from, and is
not an authority source derived from, ``mcc_evidence``. See
``docs/ATTESTATION_ARCHITECTURE.md`` for the full specification.

This package reuses ``mcc_core.signing`` (canonical serialization, SHA-256
digests, Ed25519 signing/verification) — the same primitive every other
signed artifact in this repository uses. It introduces no second
canonicalization scheme, no symmetric-key/shared-secret signature scheme,
and no new cryptographic primitive.
"""

from __future__ import annotations

from .attester import LocalAttester, sign_attestation
from .schema import (
    ATTESTATION_SCHEMA_VERSION,
    SUPPORTED_SCHEMA_VERSIONS,
    AttestationError,
    AttestationStatus,
    AttestationVerificationResult,
    CheckResult,
    CheckStatus,
    EvidenceAttestation,
    IncompleteAttestationError,
    MalformedAttestationError,
)
from .trust import AttesterTrustAnchor, AttesterTrustStore
from .verifier import verify_attestation

__all__ = [
    "ATTESTATION_SCHEMA_VERSION",
    "SUPPORTED_SCHEMA_VERSIONS",
    "AttestationError",
    "MalformedAttestationError",
    "IncompleteAttestationError",
    "AttestationStatus",
    "CheckStatus",
    "CheckResult",
    "EvidenceAttestation",
    "AttestationVerificationResult",
    "AttesterTrustAnchor",
    "AttesterTrustStore",
    "LocalAttester",
    "sign_attestation",
    "verify_attestation",
]
