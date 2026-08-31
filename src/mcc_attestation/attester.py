"""LocalAttester — the reference PRE-EXECUTION Attester.

Constructs and signs a defined :class:`~mcc_attestation.schema.EvidenceAttestation`
from data supplied by the caller. This is the whole of what an Attester does
in this package:

    Intelligence assesses.
    Attestation makes the assessment attributable.

``LocalAttester`` receives an already-computed assessment (``claims``) as
plain data. It does not call an LLM, does not perform autonomous semantic
reasoning, and does not decide what the claims *mean* — it only binds them,
an action, a scope, and a validity window into one canonical structure and
signs it with Ed25519, reusing ``mcc_core.signing`` unchanged (no second
signature implementation). Whatever produced the assessment (a model, a
rule engine, a human reviewer) is the caller's concern, entirely outside
this class.

The Attester signing key is a trust boundary (see
``docs/ATTESTATION_ARCHITECTURE.md``): a model with access to this key could
sign attestations about itself, destroying the attribution guarantee this
package exists to provide. Nothing in this module exposes, logs, or
serializes the private key; ``mcc_core.signing.SigningKey`` already refuses
to do so.
"""

from __future__ import annotations

from dataclasses import replace
from typing import Any, Dict, Optional
from uuid import uuid4

from mcc_core.signing import SigningKey

from .schema import ATTESTATION_SCHEMA_VERSION, AttestationError, EvidenceAttestation


def sign_attestation(attestation: EvidenceAttestation, signing_key: SigningKey) -> EvidenceAttestation:
    """Sign the complete Canonical Form of ``attestation`` (excluding the
    signature field) with ``mcc_core.signing.SigningKey`` (Ed25519) — reused
    unchanged. ``kid`` is added by ``sign_token`` itself and is covered by
    the signature, exactly like every other signed artifact in this
    repository."""
    if attestation.is_signed:
        raise AttestationError(
            "attestation is already signed; build a new EvidenceAttestation with a new attestation_id "
            "instead of re-signing this one"
        )
    signed = signing_key.sign_token(attestation.unsigned_dict())
    return replace(attestation, kid=signed["kid"], sig=signed["sig"])


class LocalAttester:
    """Reference, in-process Attester. Purely translational: it never calls
    an LLM, never performs autonomous reasoning, and never grants execution
    authority — it only constructs and signs an :class:`EvidenceAttestation`
    from data the caller supplies."""

    def __init__(self, attester_id: str, signing_key: SigningKey) -> None:
        if not attester_id:
            raise AttestationError("LocalAttester requires a non-empty attester_id")
        self.attester_id = attester_id
        self._signing_key = signing_key

    def attest(
        self,
        *,
        evidence_type: str,
        claims: Dict[str, Any],
        action_hash: str,
        scope: str,
        provenance: Dict[str, Any],
        issued_at: int,
        not_before: int,
        expires_at: int,
        nonce: str,
        payload_hash: Optional[str] = None,
        policy_hash: Optional[str] = None,
        policy_version: Optional[str] = None,
        attestation_id: Optional[str] = None,
    ) -> EvidenceAttestation:
        """Build and sign an :class:`EvidenceAttestation`. Every argument is
        data supplied by the caller — this method makes no semantic
        judgment about any of it; it only binds and signs."""
        unsigned = EvidenceAttestation(
            schema_version=ATTESTATION_SCHEMA_VERSION,
            attestation_id=attestation_id or f"att-{uuid4()}",
            attester_id=self.attester_id,
            evidence_type=evidence_type,
            claims=dict(claims),
            action_hash=action_hash,
            scope=scope,
            provenance=dict(provenance),
            issued_at=issued_at,
            not_before=not_before,
            expires_at=expires_at,
            nonce=nonce,
            payload_hash=payload_hash,
            policy_hash=policy_hash,
            policy_version=policy_version,
        )
        return sign_attestation(unsigned, self._signing_key)


__all__ = ["LocalAttester", "sign_attestation"]
