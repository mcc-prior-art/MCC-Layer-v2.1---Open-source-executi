"""Versioned Issuer Identity model (PR #68).

MCC-TC-001 defines the normative *concepts* this model represents --
Issuer Information (Section 10: "a stable Issuer identifier associated
with a Trust Anchor"), Signature Requirements (Section 14: "declare the
signature algorithm used and the Issuer identity"), and the Trust Model
(Section 16: Trust Anchors, rotation/revocation) -- but leaves the
*persisted, distributable representation* of an Issuer/Trust Anchor
entirely open (Section 16.1: "outside the scope of this specification").
This module implements the smallest secure, interoperable, schema-
validated contract for that representation: not a new Technical
Certificate field, not a new signature algorithm, not a new trust
concept -- a durable, versioned, canonically-serialized record of exactly
what MCC-TC-001 Sections 10/14/16 already require an Issuer/Trust Anchor
to carry.

Issuer identity is intentionally NOT inferred from filenames, local
paths, process state, or private-key contents: every field below is
either supplied explicitly or independently derived from the actual
public key bytes (the fingerprint), never guessed.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

from mcc_core.signing import public_key_from_b64, sha256_hex
from mcc_evidence.tc001_certificate import SUPPORTED_SIGNATURE_ALGORITHMS

from .target import CertifyError

ISSUER_IDENTITY_SCHEMA_VERSION = "mcc-certify-issuer/1"
SUPPORTED_ISSUER_IDENTITY_SCHEMA_VERSIONS = frozenset({ISSUER_IDENTITY_SCHEMA_VERSION})


class IssuerIdentityError(CertifyError):
    """A persisted Issuer Identity record is malformed, internally
    inconsistent, or declares something this repository does not support
    (e.g. a non-Ed25519 algorithm). Fails closed -- never partially parsed."""


class IssuerStatus(str, Enum):
    """MCC-TC-001 Section 16 Trust Model status. A closed set matching
    exactly what the specification's Trust Model actually distinguishes
    (Section 16.4 rotation/revocation) -- no additional status is invented."""

    ACTIVE = "ACTIVE"
    REVOKED = "REVOKED"


def public_key_fingerprint(public_key: Ed25519PublicKey) -> str:
    """A stable, independently-recomputable fingerprint derived only from
    the actual public key bytes -- never from a filename, kid string, or
    any other declared metadata."""
    from cryptography.hazmat.primitives import serialization

    raw = public_key.public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
    return sha256_hex(raw)


@dataclass(frozen=True)
class IssuerIdentity:
    """A versioned, schema-validated Issuer Identity / Trust Anchor record
    (MCC-TC-001 Sections 10, 14, 16). One record == one (issuer_id, key_id)
    pair recognized as a Trust Anchor."""

    issuer_identity_schema_version: str
    issuer_id: str
    display_name: str
    key_id: str
    signing_algorithm: str
    public_key_b64: str
    public_key_fingerprint: str
    valid_from: int
    specification_version: str
    created_at: int
    status: IssuerStatus = IssuerStatus.ACTIVE
    valid_until: Optional[int] = None
    superseded_by_key_id: Optional[str] = None

    def __post_init__(self) -> None:
        if self.issuer_identity_schema_version not in SUPPORTED_ISSUER_IDENTITY_SCHEMA_VERSIONS:
            raise IssuerIdentityError(
                f"unsupported issuer_identity_schema_version {self.issuer_identity_schema_version!r}"
            )
        if not self.issuer_id:
            raise IssuerIdentityError("issuer_id must be non-empty")
        if not self.display_name:
            raise IssuerIdentityError("display_name must be non-empty")
        if not self.key_id:
            raise IssuerIdentityError("key_id must be non-empty")
        if self.signing_algorithm not in SUPPORTED_SIGNATURE_ALGORITHMS:
            raise IssuerIdentityError(
                f"unsupported signing_algorithm {self.signing_algorithm!r} "
                f"(supported: {sorted(SUPPORTED_SIGNATURE_ALGORITHMS)})"
            )
        if not self.public_key_b64:
            raise IssuerIdentityError("public_key_b64 must be non-empty")
        try:
            resolved_key = public_key_from_b64(self.public_key_b64)
        except Exception as e:  # noqa: BLE001 - fail closed on any malformed key encoding
            raise IssuerIdentityError(f"public_key_b64 is not a valid Ed25519 public key: {e}") from e
        expected_fingerprint = public_key_fingerprint(resolved_key)
        if self.public_key_fingerprint != expected_fingerprint:
            raise IssuerIdentityError(
                f"public_key_fingerprint {self.public_key_fingerprint!r} does not match the actual "
                f"public key's fingerprint {expected_fingerprint!r} -- declared fingerprint is not trusted at face value"
            )
        if self.valid_until is not None and self.valid_until <= self.valid_from:
            raise IssuerIdentityError(
                f"valid_until ({self.valid_until}) must be strictly after valid_from ({self.valid_from})"
            )
        if not self.specification_version:
            raise IssuerIdentityError("specification_version must be non-empty")

    def resolved_public_key(self) -> Ed25519PublicKey:
        return public_key_from_b64(self.public_key_b64)

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {
            "issuer_identity_schema_version": self.issuer_identity_schema_version,
            "issuer_id": self.issuer_id,
            "display_name": self.display_name,
            "key_id": self.key_id,
            "signing_algorithm": self.signing_algorithm,
            "public_key_b64": self.public_key_b64,
            "public_key_fingerprint": self.public_key_fingerprint,
            "valid_from": self.valid_from,
            "specification_version": self.specification_version,
            "created_at": self.created_at,
            "status": self.status.value,
        }
        if self.valid_until is not None:
            d["valid_until"] = self.valid_until
        if self.superseded_by_key_id is not None:
            d["superseded_by_key_id"] = self.superseded_by_key_id
        return d

    @classmethod
    def from_dict(cls, d: Any) -> "IssuerIdentity":
        if not isinstance(d, dict):
            raise IssuerIdentityError("Issuer Identity record must be a JSON object")
        required = (
            "issuer_identity_schema_version", "issuer_id", "display_name", "key_id",
            "signing_algorithm", "public_key_b64", "public_key_fingerprint",
            "valid_from", "specification_version", "created_at",
        )
        missing = [f for f in required if f not in d]
        if missing:
            raise IssuerIdentityError(f"Issuer Identity record missing required field(s): {missing}")
        status_raw = d.get("status", IssuerStatus.ACTIVE.value)
        try:
            status = IssuerStatus(status_raw)
        except ValueError as e:
            raise IssuerIdentityError(f"unsupported issuer status {status_raw!r}") from e
        return cls(
            issuer_identity_schema_version=d["issuer_identity_schema_version"],
            issuer_id=d["issuer_id"],
            display_name=d["display_name"],
            key_id=d["key_id"],
            signing_algorithm=d["signing_algorithm"],
            public_key_b64=d["public_key_b64"],
            public_key_fingerprint=d["public_key_fingerprint"],
            valid_from=d["valid_from"],
            specification_version=d["specification_version"],
            created_at=d["created_at"],
            status=status,
            valid_until=d.get("valid_until"),
            superseded_by_key_id=d.get("superseded_by_key_id"),
        )


def build_issuer_identity(
    *,
    issuer_id: str,
    display_name: str,
    key_id: str,
    public_key: Ed25519PublicKey,
    valid_from: int,
    created_at: int,
    specification_version: str = "1.0",
    valid_until: Optional[int] = None,
    status: IssuerStatus = IssuerStatus.ACTIVE,
    superseded_by_key_id: Optional[str] = None,
) -> IssuerIdentity:
    """Build an Issuer Identity record from a real public key -- the
    fingerprint and base64 encoding are always independently derived from
    the key itself, never supplied by the caller."""
    from cryptography.hazmat.primitives import serialization
    import base64

    raw = public_key.public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
    return IssuerIdentity(
        issuer_identity_schema_version=ISSUER_IDENTITY_SCHEMA_VERSION,
        issuer_id=issuer_id,
        display_name=display_name,
        key_id=key_id,
        signing_algorithm="Ed25519",
        public_key_b64=base64.b64encode(raw).decode("ascii"),
        public_key_fingerprint=public_key_fingerprint(public_key),
        valid_from=valid_from,
        specification_version=specification_version,
        created_at=created_at,
        status=status,
        valid_until=valid_until,
        superseded_by_key_id=superseded_by_key_id,
    )


def read_issuer_identity(path) -> IssuerIdentity:
    import json
    from pathlib import Path

    return IssuerIdentity.from_dict(json.loads(Path(path).read_bytes()))


def write_issuer_identity(issuer: IssuerIdentity, dest) -> None:
    from pathlib import Path

    from mcc_core.signing import canonical_bytes

    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(canonical_bytes(issuer.to_dict()))
