"""MCC Attestation — EvidenceAttestation Schema (mcc-attestation/1).

Defines the versioned, immutable **PRE-EXECUTION** attestation contract this
package signs and verifies, plus the structured verification result and
error types shared by ``attester.py``, ``trust.py``, and ``verifier.py``.

This is deliberately independent of ``mcc_evidence``: ``mcc_evidence`` is
observational governance/assurance evidence describing an already-completed
governance path and carries no execution authority. ``EvidenceAttestation``
is the opposite in time — a cryptographically attributable assertion
supplied to Control *before* authorization is evaluated. See
``docs/ATTESTATION_ARCHITECTURE.md`` for the full doctrine. Concretely, this
module does not import anything from ``mcc_evidence`` — its own
``CheckResult``/``CheckStatus`` types below are a separate, minimal
definition scoped to this package, not a reuse of ``mcc_evidence.schema``.

Core doctrine, preserved verbatim wherever this package is described:

    Intelligence assesses.
    Attestation makes the assessment attributable.
    Control verifies.
    Execution acts.

A signature does NOT make an assessment true. It proves attribution and
integrity: who asserted what, about which bound action, under which
version/context, and during which validity interval. ``VERIFIED`` (see
:class:`AttestationStatus`) means only that an attestation is
cryptographically and structurally valid under the supplied trust and
expected bindings — it never means the underlying semantic assessment (the
``claims``) is objectively correct, and it never itself grants execution
authority.

**Immutability.** ``EvidenceAttestation`` is a frozen dataclass, and its
``claims``/``provenance`` fields are deep-frozen (recursively converted to
``types.MappingProxyType``/``tuple``) at construction time, independent of
whatever mutable object the caller originally supplied. Mutating the
caller's original dict *after* constructing an attestation, or attempting to
assign a new value to any field on the constructed object, cannot alter the
attestation's content. This is a structural guarantee, not merely a
documentation claim (see ``tests/test_mcc_attestation.py``'s immutability
tests) — signature verification is not relied upon as a substitute for it.
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Dict, List, Mapping, Optional, Tuple

#: Attestation schema version. The verifier refuses versions it does not
#: support (returns UNSUPPORTED_SCHEMA, never a partial/best-effort parse).
ATTESTATION_SCHEMA_VERSION = "mcc-attestation/1"
SUPPORTED_SCHEMA_VERSIONS = frozenset({ATTESTATION_SCHEMA_VERSION})

_REQUIRED_FIELDS: Tuple[str, ...] = (
    "schema_version",
    "attestation_id",
    "attester_id",
    "evidence_type",
    "claims",
    "action_hash",
    "scope",
    "provenance",
    "issued_at",
    "not_before",
    "expires_at",
    "nonce",
    "kid",
    "sig",
)
_OPTIONAL_FIELDS: Tuple[str, ...] = ("payload_hash", "policy_hash", "policy_version")
_ALL_ALLOWED_FIELDS = frozenset(_REQUIRED_FIELDS + _OPTIONAL_FIELDS)

#: Digest fields, and the format they must satisfy: "sha256:<64 lowercase hex
#: characters>" — the same convention ``mcc_core.signing.sha256_hex`` produces.
_DIGEST_FIELDS: Tuple[str, ...] = ("action_hash", "payload_hash", "policy_hash")
_SHA256_DIGEST_RE = re.compile(r"^sha256:[0-9a-f]{64}$")


class AttestationError(Exception):
    """Base error for the attestation subsystem (construction/verification)."""


class MalformedAttestationError(AttestationError):
    """Structural verification failure: missing/undeclared/malformed field,
    unsupported schema version, invalid timestamp ordering, a digest field
    not shaped like ``sha256:<64 lowercase hex>``, or ``claims``/
    ``provenance`` containing a value that is not canonically serializable.
    Raised by :meth:`EvidenceAttestation.from_dict` and by
    :meth:`EvidenceAttestation.__post_init__` (so it is raised identically
    whether an attestation is built from raw JSON or constructed directly,
    e.g. by ``attester.LocalAttester``); never a partially-valid object is
    returned."""


class IncompleteAttestationError(AttestationError):
    """Construction refused — no partial or internally inconsistent
    attestation is ever built or signed."""


class AttestationStatus(str, Enum):
    """Fail-closed overall verification outcome. There is no partial-pass
    status, and deliberately no "ALLOW"/"AUTHORIZED"-shaped member: an
    attestation carries no executable verdict and grants no execution
    authority (see the module docstring and
    ``docs/ATTESTATION_ARCHITECTURE.md``)."""

    VERIFIED = "VERIFIED"
    INVALID = "INVALID"
    UNSUPPORTED_SCHEMA = "UNSUPPORTED_SCHEMA"


class CheckStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    #: The check was not evaluated because the caller supplied no expected
    #: value to check against (an optional binding). NA is never rolled up
    #: as evidence of anything having been proven — see
    #: ``AttestationVerificationResult.payload_binding_valid`` /
    #: ``policy_binding_valid``, which are ``None`` (not ``True``) exactly
    #: when their corresponding check is NA.
    NA = "NA"


@dataclass(frozen=True)
class CheckResult:
    name: str
    status: CheckStatus
    detail: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {"name": self.name, "status": self.status.value, "detail": self.detail}


def _freeze(value: Any) -> Any:
    """Recursively convert ``value`` into an immutable structure: dict ->
    ``MappingProxyType`` (of recursively frozen values), list/tuple ->
    tuple (of recursively frozen values), everything else unchanged. This
    produces a genuinely independent, immutable copy — mutating the
    caller's original ``dict``/``list`` after this call has no effect on
    the frozen result, because new container objects are built here, never
    a view over the caller's originals."""
    if isinstance(value, Mapping):
        return MappingProxyType({k: _freeze(v) for k, v in value.items()})
    if isinstance(value, (list, tuple)):
        return tuple(_freeze(v) for v in value)
    return value


def _thaw(value: Any) -> Any:
    """Inverse of :func:`_freeze`: convert a frozen structure back into
    plain ``dict``/``list`` so it can be passed to
    ``mcc_core.signing.canonical_bytes`` (``json.dumps`` does not know how
    to serialize ``MappingProxyType``)."""
    if isinstance(value, Mapping):
        return {k: _thaw(v) for k, v in value.items()}
    if isinstance(value, tuple):
        return [_thaw(v) for v in value]
    return value


def _validate_canonical_structure(value: Any, path: str) -> None:
    """Recursively validate that ``value`` contains only types that
    ``mcc_core.signing.canonical_bytes`` (deterministic ``json.dumps``) can
    serialize unambiguously: ``None``, ``bool``, ``str``, finite ``int``/
    ``float``, and ``dict``/``list``/``tuple`` composed recursively of the
    same, with string-only object keys. Rejects non-finite floats (NaN/
    Infinity are not valid JSON), non-string mapping keys, and any other
    Python type (sets, custom objects, bytes, ...). Applied to ``claims``
    and ``provenance`` so a structurally malformed or non-canonical value
    fails closed at construction/verification time rather than producing a
    signature over an ambiguous or non-reproducible serialization."""
    if value is None or isinstance(value, (bool, str)):
        return
    if isinstance(value, int):
        return
    if isinstance(value, float):
        if not math.isfinite(value):
            raise MalformedAttestationError(f"{path}: non-finite float is not canonically serializable")
        return
    if isinstance(value, Mapping):
        for k, v in value.items():
            if not isinstance(k, str):
                raise MalformedAttestationError(f"{path}: object keys must be strings, got {type(k).__name__}")
            _validate_canonical_structure(v, f"{path}.{k}")
        return
    if isinstance(value, (list, tuple)):
        for i, v in enumerate(value):
            _validate_canonical_structure(v, f"{path}[{i}]")
        return
    raise MalformedAttestationError(f"{path}: value of type {type(value).__name__} is not canonically serializable")


def _validate_digest(field_name: str, value: str) -> None:
    if not _SHA256_DIGEST_RE.match(value):
        raise MalformedAttestationError(
            f"{field_name} must match 'sha256:<64 lowercase hex characters>', got {value!r}"
        )


@dataclass(frozen=True)
class EvidenceAttestation:
    """The complete EvidenceAttestation document (schema ``mcc-attestation/1``).

    A closed field set: :meth:`from_dict` rejects any field outside
    ``_ALL_ALLOWED_FIELDS``. ``claims`` and ``provenance`` are free-form,
    deterministic (canonically serializable) structured data — this schema
    carries no hard-coded evidence-type semantics (no payment/fraud/
    phishing/risk vocabulary); interpreting ``claims`` is a policy/Control
    concern, never this package's.

    Immutable: this dataclass is frozen, and ``claims``/``provenance`` are
    deep-frozen at construction (see :func:`_freeze`) regardless of how the
    object is built (:meth:`from_dict` or direct construction, e.g. by
    ``attester.LocalAttester``). ``__post_init__`` is the single place that
    enforces every field-level structural invariant this schema defines
    (digest format, timestamp ordering, canonical structure of ``claims``/
    ``provenance``), so both construction paths are validated identically.
    """

    schema_version: str
    attestation_id: str
    attester_id: str
    evidence_type: str
    claims: Mapping[str, Any]
    action_hash: str
    scope: str
    provenance: Mapping[str, Any]
    issued_at: int
    not_before: int
    expires_at: int
    nonce: str
    payload_hash: Optional[str] = None
    policy_hash: Optional[str] = None
    policy_version: Optional[str] = None
    kid: Optional[str] = None
    sig: Optional[str] = None

    def __post_init__(self) -> None:
        # --- temporal invariant: issued_at <= not_before < expires_at -------
        if self.issued_at > self.not_before:
            raise MalformedAttestationError(
                f"malformed timestamp ordering: issued_at ({self.issued_at}) must not be after "
                f"not_before ({self.not_before})"
            )
        if self.expires_at <= self.not_before:
            raise MalformedAttestationError(
                f"malformed timestamp ordering: expires_at ({self.expires_at}) must be after "
                f"not_before ({self.not_before})"
            )

        # --- digest fields must be shaped like sha256:<64 lowercase hex> ----
        for name in _DIGEST_FIELDS:
            value = getattr(self, name)
            if value is not None:
                _validate_digest(name, value)

        # --- claims/provenance must be recursively canonically serializable -
        _validate_canonical_structure(dict(self.claims), "claims")
        _validate_canonical_structure(dict(self.provenance), "provenance")

        # --- deep-freeze claims/provenance, independent of the caller's -----
        # --- original (possibly still-mutable-and-referenced) objects -------
        object.__setattr__(self, "claims", _freeze(self.claims))
        object.__setattr__(self, "provenance", _freeze(self.provenance))

    @property
    def is_signed(self) -> bool:
        return self.kid is not None and self.sig is not None

    def unsigned_dict(self) -> Dict[str, Any]:
        """Canonical Form input for signing/verification — excludes the
        signature field. ``kid`` is intentionally *not* included here either:
        ``mcc_core.signing.SigningKey.sign_token`` adds ``kid`` itself and
        signs over ``claims + kid`` as one unit (see ``attester.py``), the
        same convention every other signed artifact in this repository uses.
        Returns plain ``dict``/``list`` values (never ``MappingProxyType``)
        so the result is directly usable with
        ``mcc_core.signing.canonical_bytes``.
        """
        d: Dict[str, Any] = {
            "schema_version": self.schema_version,
            "attestation_id": self.attestation_id,
            "attester_id": self.attester_id,
            "evidence_type": self.evidence_type,
            "claims": _thaw(self.claims),
            "action_hash": self.action_hash,
            "scope": self.scope,
            "provenance": _thaw(self.provenance),
            "issued_at": self.issued_at,
            "not_before": self.not_before,
            "expires_at": self.expires_at,
            "nonce": self.nonce,
        }
        if self.payload_hash is not None:
            d["payload_hash"] = self.payload_hash
        if self.policy_hash is not None:
            d["policy_hash"] = self.policy_hash
        if self.policy_version is not None:
            d["policy_version"] = self.policy_version
        return d

    def to_dict(self) -> Dict[str, Any]:
        d = self.unsigned_dict()
        if self.kid is not None:
            d["kid"] = self.kid
        if self.sig is not None:
            d["sig"] = self.sig
        return d

    @classmethod
    def from_dict(cls, d: Any) -> "EvidenceAttestation":
        """Structural verification (must precede everything else). Raises
        :class:`MalformedAttestationError` — never returns a partially-valid
        object — on any missing required field, undeclared field, type
        problem, malformed digest field, invalid timestamp ordering, or
        non-canonical ``claims``/``provenance`` content (the last three are
        enforced by :meth:`__post_init__`, shared with direct construction).
        """
        if not isinstance(d, dict):
            raise MalformedAttestationError("EvidenceAttestation must be a JSON object")

        unknown = set(d) - _ALL_ALLOWED_FIELDS
        if unknown:
            raise MalformedAttestationError(f"EvidenceAttestation contains undeclared field(s): {sorted(unknown)}")
        missing = [f for f in _REQUIRED_FIELDS if f not in d]
        if missing:
            raise MalformedAttestationError(f"EvidenceAttestation missing required field(s): {missing}")

        if d["schema_version"] not in SUPPORTED_SCHEMA_VERSIONS:
            raise MalformedAttestationError(f"unsupported schema_version {d['schema_version']!r}")

        def _nonempty_str(name: str) -> str:
            v = d[name]
            if not isinstance(v, str) or not v:
                raise MalformedAttestationError(f"{name} must be a non-empty string")
            return v

        def _dict_field(name: str) -> Dict[str, Any]:
            v = d[name]
            if not isinstance(v, dict):
                raise MalformedAttestationError(f"{name} must be a JSON object")
            return v

        def _int_field(name: str) -> int:
            v = d[name]
            if not isinstance(v, int) or isinstance(v, bool):
                raise MalformedAttestationError(f"{name} must be an integer (unix seconds)")
            return v

        attestation_id = _nonempty_str("attestation_id")
        attester_id = _nonempty_str("attester_id")
        evidence_type = _nonempty_str("evidence_type")
        claims = _dict_field("claims")
        action_hash = _nonempty_str("action_hash")
        scope = _nonempty_str("scope")
        provenance = _dict_field("provenance")
        issued_at = _int_field("issued_at")
        not_before = _int_field("not_before")
        expires_at = _int_field("expires_at")
        nonce = _nonempty_str("nonce")
        kid = _nonempty_str("kid")
        sig = _nonempty_str("sig")

        payload_hash = d.get("payload_hash")
        if payload_hash is not None and (not isinstance(payload_hash, str) or not payload_hash):
            raise MalformedAttestationError("payload_hash must be a non-empty string when present")
        policy_hash = d.get("policy_hash")
        if policy_hash is not None and (not isinstance(policy_hash, str) or not policy_hash):
            raise MalformedAttestationError("policy_hash must be a non-empty string when present")
        policy_version = d.get("policy_version")
        if policy_version is not None and (not isinstance(policy_version, str) or not policy_version):
            raise MalformedAttestationError("policy_version must be a non-empty string when present")

        # __post_init__ (invoked by the constructor below) enforces the
        # timestamp-ordering, digest-format, and canonical-structure
        # invariants — not repeated here, so both this path and direct
        # construction share exactly one implementation of those rules.
        return cls(
            schema_version=d["schema_version"],
            attestation_id=attestation_id,
            attester_id=attester_id,
            evidence_type=evidence_type,
            claims=claims,
            action_hash=action_hash,
            scope=scope,
            provenance=provenance,
            issued_at=issued_at,
            not_before=not_before,
            expires_at=expires_at,
            nonce=nonce,
            payload_hash=payload_hash,
            policy_hash=policy_hash,
            policy_version=policy_version,
            kid=kid,
            sig=sig,
        )


@dataclass
class AttestationVerificationResult:
    """Structured result of :func:`verifier.verify_attestation` — never a
    bare Boolean. Each dimension is reported independently so a caller (or a
    future Control integration in PR-2/PR-3) can see exactly what was and
    was not established, rather than a single conflated pass/fail.

    ``overall_status`` is the single roll-up (:class:`AttestationStatus`).
    ``verified`` is a convenience — True only when ``overall_status`` is
    ``VERIFIED`` — and, like ``overall_status`` itself, means only that the
    attestation is cryptographically and structurally valid under the
    supplied trust and expected bindings. It is never a statement that the
    underlying semantic assessment is correct, and never itself an
    authorization to execute.

    ``payload_binding_valid`` and ``policy_binding_valid`` are
    ``Optional[bool]``, distinctly from every other dimension here, because
    those two bindings are themselves optional (the caller may or may not
    supply an expected value to check against — see ``verifier.py``):

    * ``None``  — NOT CHECKED / NOT APPLICABLE. Either the caller supplied
      no expected value for this binding, or verification did not reach
      this step. A caller MUST NOT interpret ``None`` as "proven."
    * ``True``  — the caller supplied an expected value and the attestation
      matched it.
    * ``False`` — the caller supplied an expected value and the attestation
      did NOT match it (verification already resolved to ``INVALID`` in
      this case).
    """

    overall_status: AttestationStatus
    schema_supported: bool = False
    structure_valid: bool = False
    signer_verified: bool = False
    signer_trusted: bool = False
    evidence_type_allowed: bool = False
    time_valid: bool = False
    action_binding_valid: bool = False
    payload_binding_valid: Optional[bool] = None
    scope_valid: bool = False
    policy_binding_valid: Optional[bool] = None
    checks: List[CheckResult] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    failures: List[str] = field(default_factory=list)
    attestation_id: Optional[str] = None
    attester_id: Optional[str] = None

    @property
    def verified(self) -> bool:
        return self.overall_status is AttestationStatus.VERIFIED

    def check(self, name: str) -> Optional[CheckResult]:
        return next((c for c in self.checks if c.name == name), None)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "overall_status": self.overall_status.value,
            "verified": self.verified,
            "schema_supported": self.schema_supported,
            "structure_valid": self.structure_valid,
            "signer_verified": self.signer_verified,
            "signer_trusted": self.signer_trusted,
            "evidence_type_allowed": self.evidence_type_allowed,
            "time_valid": self.time_valid,
            "action_binding_valid": self.action_binding_valid,
            "payload_binding_valid": self.payload_binding_valid,
            "scope_valid": self.scope_valid,
            "policy_binding_valid": self.policy_binding_valid,
            "attestation_id": self.attestation_id,
            "attester_id": self.attester_id,
            "checks": [c.to_dict() for c in self.checks],
            "warnings": list(self.warnings),
            "failures": list(self.failures),
        }


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
]
