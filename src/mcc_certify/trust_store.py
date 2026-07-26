"""Trust Anchor Model and Trust Store (PR #68).

MCC-TC-001 Section 16 defines the Trust Model concept -- a verifier relies
on a set of Trust Anchors (Issuer + key) it recognizes -- but explicitly
leaves the persisted, distributable *set* representation and its
distribution mechanism out of its own normative scope (Section 16.1: "the
mechanism by which a Trust Anchor is distributed to verifiers is outside
the scope of this specification"). This module implements exactly that
missing, versioned, schema-validated, offline representation: a durable
"Trust Store" document collecting one or more :class:`IssuerIdentity`
records (``issuer.py``) and converting them, at verification time, into the
existing, UNCHANGED Wave C runtime type
(:class:`mcc_evidence.tc001_certificate.TrustAnchorRegistry`) -- this module
never duplicates that verifier or its ``TrustAnchor``/``resolve`` semantics.

A Trust Store is loaded once, entirely from local disk, and never fetched
or refreshed from a network source (MCC-TC-001 Section 16.3's "trust MUST
NOT be established dynamically" is honored by construction: there is no
network client anywhere in this module). A Technical Certificate can never
add itself, or any of its own declared fields, to a Trust Store -- trust is
always supplied independently by the verifier's own configuration, never
self-established by the artifact being verified.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Tuple

from mcc_core.signing import canonical_bytes
from mcc_evidence.tc001_certificate import TrustAnchor, TrustAnchorRegistry

from .issuer import IssuerIdentity, IssuerIdentityError, IssuerStatus
from .target import CertifyError

TRUST_STORE_SCHEMA_VERSION = "mcc-certify-trust-store/1"
SUPPORTED_TRUST_STORE_SCHEMA_VERSIONS = frozenset({TRUST_STORE_SCHEMA_VERSION})


class TrustStoreError(CertifyError):
    """A Trust Store document is malformed, internally inconsistent (e.g. a
    duplicate or conflicting Issuer/key pair), or cannot be safely loaded.
    Fails closed -- never partially loaded, never silently deduplicated."""


@dataclass(frozen=True)
class TrustStore:
    """A versioned, canonical, offline collection of Issuer Identity /
    Trust Anchor records (MCC-TC-001 Section 16). Supports multiple issuer
    keys (Section 16.4 rotation: an old and a new key for the same
    ``issuer_id`` may coexist, distinguished by ``key_id``)."""

    trust_store_schema_version: str
    issuers: Tuple[IssuerIdentity, ...]

    def __post_init__(self) -> None:
        if self.trust_store_schema_version not in SUPPORTED_TRUST_STORE_SCHEMA_VERSIONS:
            raise TrustStoreError(
                f"unsupported trust_store_schema_version {self.trust_store_schema_version!r}"
            )
        if not self.issuers:
            raise TrustStoreError("Trust Store must declare at least one Issuer Identity")
        seen_pairs = set()
        seen_fingerprints: Dict[str, str] = {}
        for issuer in self.issuers:
            if not isinstance(issuer, IssuerIdentity):
                raise TrustStoreError("Trust Store entries must be IssuerIdentity records")
            pair = (issuer.issuer_id, issuer.key_id)
            if pair in seen_pairs:
                raise TrustStoreError(
                    f"duplicate (issuer_id, key_id) pair in Trust Store: {pair!r}"
                )
            seen_pairs.add(pair)
            # A single key_id must not be bound to two different public keys
            # (or two different issuer_ids) anywhere in the same store --
            # that would be a conflicting, ambiguous Trust Anchor.
            prior_fp = seen_fingerprints.get(issuer.key_id)
            if prior_fp is not None and prior_fp != issuer.public_key_fingerprint:
                raise TrustStoreError(
                    f"conflicting Trust Store entries: key_id {issuer.key_id!r} is bound to two "
                    "different public keys"
                )
            seen_fingerprints[issuer.key_id] = issuer.public_key_fingerprint

    def resolve(self, issuer_id: str, key_id: str) -> IssuerIdentity:
        """Look up exactly the (issuer_id, key_id) pair a caller expects --
        never resolves by key_id alone (an unknown issuer_id must not
        silently match a key_id that happens to exist for a different
        issuer)."""
        for issuer in self.issuers:
            if issuer.issuer_id == issuer_id and issuer.key_id == key_id:
                return issuer
        raise TrustStoreError(f"unknown Trust Anchor: issuer_id={issuer_id!r}, key_id={key_id!r}")

    def to_trust_anchor_registry(self, now: int) -> TrustAnchorRegistry:
        """Convert this Trust Store into the existing, unchanged Wave C
        :class:`TrustAnchorRegistry` runtime type used by
        ``verify_technical_certificate`` -- this is the ONLY place a
        :class:`TrustAnchor` is constructed from a :class:`TrustStore`, and
        it never bypasses or re-implements the Wave C verifier itself.

        A store entry is treated as effectively revoked (its
        ``TrustAnchor.revoked`` flag set) whenever any of the following
        holds, computed independently for each entry against ``now``:

        - its declared ``status`` is ``REVOKED``;
        - ``now`` precedes ``valid_from`` (not yet valid);
        - ``valid_until`` is set and ``now`` is after it (expired).
        """
        anchors = []
        for issuer in self.issuers:
            effectively_revoked = (
                issuer.status is IssuerStatus.REVOKED
                or now < issuer.valid_from
                or (issuer.valid_until is not None and now > issuer.valid_until)
            )
            anchors.append(TrustAnchor(
                issuer_id=issuer.issuer_id,
                kid=issuer.key_id,
                public_key=issuer.resolved_public_key(),
                revoked=effectively_revoked,
            ))
        return TrustAnchorRegistry(anchors)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "trust_store_schema_version": self.trust_store_schema_version,
            "issuers": [issuer.to_dict() for issuer in self.issuers],
        }

    @classmethod
    def from_dict(cls, d: Any) -> "TrustStore":
        if not isinstance(d, dict):
            raise TrustStoreError("Trust Store document must be a JSON object")
        if "trust_store_schema_version" not in d:
            raise TrustStoreError("Trust Store document missing trust_store_schema_version")
        if "issuers" not in d or not isinstance(d["issuers"], list):
            raise TrustStoreError("Trust Store document missing an 'issuers' array")
        try:
            issuers = tuple(IssuerIdentity.from_dict(entry) for entry in d["issuers"])
        except IssuerIdentityError as e:
            raise TrustStoreError(f"Trust Store contains a malformed Issuer Identity: {e}") from e
        return cls(
            trust_store_schema_version=d["trust_store_schema_version"],
            issuers=issuers,
        )


def build_trust_store(issuers: Tuple[IssuerIdentity, ...]) -> TrustStore:
    return TrustStore(trust_store_schema_version=TRUST_STORE_SCHEMA_VERSION, issuers=tuple(issuers))


def read_trust_store(path: Path | str) -> TrustStore:
    """Read a Trust Store document. Entirely local/offline -- ``path`` must
    be a filesystem path; this function never performs network I/O and
    never accepts a URL."""
    try:
        raw = json.loads(Path(path).read_bytes())
    except (OSError, json.JSONDecodeError) as e:
        raise TrustStoreError(f"cannot read Trust Store at {path}: {e}") from e
    return TrustStore.from_dict(raw)


def write_trust_store(store: TrustStore, dest: Path | str) -> Path:
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(canonical_bytes(store.to_dict()))
    return dest


__all__ = [
    "TRUST_STORE_SCHEMA_VERSION",
    "SUPPORTED_TRUST_STORE_SCHEMA_VERSIONS",
    "TrustStoreError",
    "TrustStore",
    "build_trust_store",
    "read_trust_store",
    "write_trust_store",
]
