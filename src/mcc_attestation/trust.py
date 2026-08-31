"""AttesterTrustStore — the trust model for EvidenceAttestation signers.

Resolution is by the pair ``(attester_id, kid)``, exactly as the task
specification requires: "attester_id + kid -> trusted Ed25519 public key".
This is a deliberate design choice, not an implementation detail: a public
key registered under one ``attester_id`` simply does not exist under any
other ``attester_id``, so an attestation that *declares* one attester's
identity while carrying a ``kid`` that was only ever registered to a
*different* attester fails closed at resolution — trust is never inferred
from an attestation's self-declared ``attester_id`` alone.

Each trust anchor also carries the closed set of ``evidence_type`` values
that attester is permitted to assert, so a compromised or misconfigured
attester cannot silently start asserting a class of evidence nobody
authorized it for.

This is a minimal, in-memory registry — analogous to
``mcc_evidence.tc001_certificate.TrustAnchorRegistry`` in shape, but an
independent implementation (this package does not import ``mcc_evidence``;
see ``docs/ATTESTATION_ARCHITECTURE.md`` for why the two stay separate). A
distributed/persistent backend, and a first-class key-rotation workflow
beyond "add a new kid, revoke the old one", are out of scope for PR-1 and
remain a legitimate future extension — the abstraction below (resolve by
key, explicit revoke) is deliberately shaped so that can be added later
without changing this module's public surface.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Dict, FrozenSet, Iterable, Optional, Tuple

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

from .schema import AttestationError


@dataclass(frozen=True)
class AttesterTrustAnchor:
    """A verification key a verifier relies on to authenticate one
    attester's attestations, plus the closed set of ``evidence_type``
    values that attester may assert."""

    attester_id: str
    kid: str
    public_key: Ed25519PublicKey
    allowed_evidence_types: FrozenSet[str]
    revoked: bool = False

    def __post_init__(self) -> None:
        if not self.attester_id:
            raise AttestationError("AttesterTrustAnchor.attester_id must be non-empty")
        if not self.kid:
            raise AttestationError("AttesterTrustAnchor.kid must be non-empty")
        if not self.allowed_evidence_types:
            raise AttestationError(
                f"AttesterTrustAnchor for attester_id={self.attester_id!r} kid={self.kid!r} must declare at "
                "least one permitted evidence_type — an attester is never trusted for an unbounded set"
            )


class AttesterTrustStore:
    """The set of trust anchors a verifier recognizes. Fail-closed: an
    unrecognized ``(attester_id, kid)`` pair or a revoked anchor resolves to
    ``None`` — never a partial or best-guess match."""

    def __init__(self, anchors: Optional[Iterable[AttesterTrustAnchor]] = None) -> None:
        self._by_key: Dict[Tuple[str, str], AttesterTrustAnchor] = {}
        for a in anchors or []:
            self.add(a)

    def add(self, anchor: AttesterTrustAnchor) -> None:
        key = (anchor.attester_id, anchor.kid)
        if key in self._by_key:
            raise AttestationError(
                f"duplicate trust anchor for attester_id={anchor.attester_id!r} kid={anchor.kid!r}"
            )
        self._by_key[key] = anchor

    def resolve(self, attester_id: Optional[str], kid: Optional[str]) -> Optional[AttesterTrustAnchor]:
        """Fail-closed lookup: returns ``None`` unless ``attester_id`` and
        ``kid`` together resolve to a currently-active (non-revoked) anchor.
        """
        if not attester_id or not kid:
            return None
        anchor = self._by_key.get((attester_id, kid))
        if anchor is None or anchor.revoked:
            return None
        return anchor

    def revoke(self, attester_id: str, kid: str) -> None:
        """Cease recognizing ``(attester_id, kid)`` for *future*
        verification. Does not alter or erase any previously-issued
        attestation's content, and does not remove the anchor from the
        registry — only ``resolve()`` for this key is affected going
        forward."""
        key = (attester_id, kid)
        anchor = self._by_key.get(key)
        if anchor is None:
            raise AttestationError(f"cannot revoke unknown trust anchor attester_id={attester_id!r} kid={kid!r}")
        self._by_key[key] = replace(anchor, revoked=True)

    def evidence_type_allowed(self, anchor: AttesterTrustAnchor, evidence_type: str) -> bool:
        return evidence_type in anchor.allowed_evidence_types


__all__ = ["AttesterTrustAnchor", "AttesterTrustStore"]
