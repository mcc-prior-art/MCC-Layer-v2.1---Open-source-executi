"""Structured Hash Reference — the reusable integrity-binding primitive
defined normatively by MCC-CM-001, Section 13 (``CM-HASH-001..004``).

A Hash Reference identifies a Digest, the hash algorithm used to produce it,
and the content it corresponds to, such that a validator can independently
recompute the Digest and verify the binding without trusting the party that
produced it. This module is the ONE canonical Hash Reference implementation
in this repository: MCC-EB-001's Integrity Record (``eb001_export.py`` /
``eb001_verify.py``) uses it to bind every Bundle file to its Digest, and it
is written to be reusable, unchanged, by a future MCC-CM-001 Certification
Manifest Evidence Bundle Reference (Wave B) — which this module does NOT
implement.

Reuses MCC-Core's existing canonical-serialization and digest primitives
(``mcc_core.signing.sha256_hex``) rather than inventing new cryptographic
code.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Dict, List

from mcc_core.signing import sha256_hex

#: The only hash algorithm this repository treats as collision-resistant
#: (CM-HASH-002 / MCC-CM-001 Section 13.3: "MUST be a collision-resistant
#: cryptographic hash function"). Deliberately a closed set: a Hash
#: Reference naming any other algorithm is rejected, never silently
#: accepted.
SUPPORTED_HASH_ALGORITHMS = frozenset({"sha256"})

_DIGEST_RE = {
    "sha256": re.compile(r"^sha256:[0-9a-f]{64}$"),
}


class HashReferenceError(Exception):
    """A Hash Reference is malformed or cannot be parsed. Fail closed:
    callers must treat this the same as an invalid reference, never as an
    absent (NA) one."""


@dataclass(frozen=True)
class HashReference:
    """CM-HASH-001: identifies a Digest, a hash algorithm, and the content it
    corresponds to."""

    digest: str
    algorithm: str
    content_ref: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "digest": self.digest,
            "algorithm": self.algorithm,
            "content_ref": self.content_ref,
        }

    @classmethod
    def from_dict(cls, d: Any) -> "HashReference":
        if not isinstance(d, dict):
            raise HashReferenceError("Hash Reference must be a JSON object")
        for field in ("digest", "algorithm", "content_ref"):
            if field not in d:
                raise HashReferenceError(f"Hash Reference missing required field {field!r}")
            if not isinstance(d[field], str) or not d[field]:
                raise HashReferenceError(f"Hash Reference field {field!r} must be a non-empty string")
        return cls(digest=d["digest"], algorithm=d["algorithm"], content_ref=d["content_ref"])

    def validate(self) -> List[str]:
        """Semantic validation beyond structural parsing. Returns a list of
        problem strings; empty means valid. Never raises."""
        problems: List[str] = []
        if self.algorithm not in SUPPORTED_HASH_ALGORITHMS:
            problems.append(
                f"hash algorithm {self.algorithm!r} is not collision-resistant / not supported "
                f"(supported: {sorted(SUPPORTED_HASH_ALGORITHMS)})"
            )
            return problems  # digest syntax is algorithm-dependent; nothing further to check
        pattern = _DIGEST_RE[self.algorithm]
        if not pattern.match(self.digest):
            problems.append(
                f"digest {self.digest!r} is not valid {self.algorithm} syntax "
                f"(expected {self.algorithm}:<hex>)"
            )
        return problems


def compute_hash_reference(data: bytes, content_ref: str, *, algorithm: str = "sha256") -> HashReference:
    """CM-HASH-001 construction. Rejects (raises) a non-collision-resistant
    algorithm at construction time rather than producing an invalid
    reference (CM-HASH-002)."""
    if algorithm not in SUPPORTED_HASH_ALGORITHMS:
        raise HashReferenceError(
            f"refusing to compute a Hash Reference with non-collision-resistant "
            f"algorithm {algorithm!r} (supported: {sorted(SUPPORTED_HASH_ALGORITHMS)})"
        )
    return HashReference(digest=sha256_hex(data), algorithm=algorithm, content_ref=content_ref)


def verify_hash_reference(ref: HashReference, data: bytes) -> bool:
    """CM-HASH-004: independent recomputation and verification. Fail closed
    — an unsupported algorithm or malformed digest is never treated as a
    match, regardless of the supplied data."""
    if ref.validate():
        return False
    if ref.algorithm == "sha256":
        return sha256_hex(data) == ref.digest
    return False  # unreachable while SUPPORTED_HASH_ALGORITHMS == {"sha256"}
