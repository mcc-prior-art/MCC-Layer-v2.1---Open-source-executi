"""The MCC-Core Integration Contract — canonical normative layer (PR #43).

This module is the **single machine-readable source of truth** for the parts of
the official Integration Contract that must not drift: the contract version, the
version-compatibility rule, the stable error taxonomy, and the conformance
manifest that PR #44 (Compliance & Certification Suite) consumes.

Reconcile, not reinvent
-----------------------
The canonical *data* models of the contract are the ones the SDK already ships —
:class:`mcc_client.Verdict`, :class:`mcc_client.Decision`,
:class:`mcc_client.ExecutionResult`, and the authorization artifacts
(:class:`~mcc_client.ConsensusAuthorization`,
:class:`~mcc_client.MandateAuthorization`,
:class:`~mcc_client.ApprovalAuthorization`). This module deliberately defines **no
parallel wire models** and duplicates none of them; it references them. There is
exactly **one** normative wire contract.

The Canonical Governance Protocol (PR #49, :mod:`mcc_protocol`) names a canonical
request object (``CanonicalProposal``) and a canonical response envelope
(``GovernanceDecision``). These are **not** a second competing hierarchy and do not
create the semantic drift the contract forbids: ``CanonicalProposal`` is an additive
request type (the SDK had none), and ``GovernanceDecision`` **wraps** — never
replaces — :class:`mcc_client.Decision` and the existing Decision Token, reusing
this module's version rule, error taxonomy, and the SDK's ``Verdict`` verbatim. The
authoritative decision and execution-authorization artifact remain ``Decision`` and
its Decision Token.

What this module is / is not
----------------------------
* It is pure: no network, no I/O, no clock-dependent behavior, no authorization
  logic. Validating a version or classifying an error **never** authorizes
  anything — schema validity is not authorization (see the negative guarantees in
  ``docs/INTEGRATION_CONTRACT.md``).
* It fails closed: an unknown/malformed contract version, or an unmapped error,
  resolves to a *blocking* classification, never to permission.

The normative prose (RFC-2119 requirements, traceability matrix, invariant
ownership matrix, state table) lives in ``docs/INTEGRATION_CONTRACT.md`` and is
kept in lock-step with the identifiers defined here.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional, Tuple

from .exceptions import (
    MCCAmbiguousExecutionError,
    MCCApprovalRequiredError,
    MCCAuthenticationError,
    MCCDeniedError,
    MCCError,
    MCCExecutionError,
    MCCInvalidDecisionError,
    MCCProtocolError,
    MCCReplayError,
    MCCTimeoutError,
    MCCTransportError,
)
from .models import Verdict

# --------------------------------------------------------------------------- #
# Contract identity + version.                                                #
# --------------------------------------------------------------------------- #

#: Stable identifier for the official contract (independent of any framework).
CONTRACT_IDENTIFIER = "mcc-integration-contract"

#: Contract version, ``MAJOR.MINOR``. This is the *contract* version — a distinct
#: concept from the package/distribution version (``mcc_client.__version__`` and
#: the ``mcc-core`` wheel version). A patch-level package release never silently
#: redefines contract semantics.
CONTRACT_MAJOR = 1
CONTRACT_MINOR = 0
CONTRACT_VERSION = f"{CONTRACT_MAJOR}.{CONTRACT_MINOR}"

#: Major versions this build understands. An unknown major fails closed.
SUPPORTED_MAJORS: frozenset[int] = frozenset({1})


# --------------------------------------------------------------------------- #
# Stable error taxonomy.                                                       #
# --------------------------------------------------------------------------- #

class ErrorCategory(str, Enum):
    """Coarse category of a contract failure. Categories separate *where* a
    failure originates so a transport failure is never confused with a governance
    decision, and a contract-validation failure is never confused with an
    authorization outcome."""

    CONTRACT = "CONTRACT"
    VERSION = "VERSION"
    CAPABILITY = "CAPABILITY"
    AUTHENTICATION = "AUTHENTICATION"
    DECISION = "DECISION"
    VERIFICATION = "VERIFICATION"
    CONSTRAINT = "CONSTRAINT"
    GATE = "GATE"
    AUDIT = "AUDIT"
    EXECUTION = "EXECUTION"
    TRANSPORT = "TRANSPORT"
    INTERNAL = "INTERNAL"


class ContractErrorCode(str, Enum):
    """Stable, machine-readable error codes. The *string values* are part of the
    contract and MUST remain stable across minor versions; human-readable messages
    may evolve. Authorization semantics depend on these codes and structured
    fields — never on free-text prose.

    The set is intentionally limited to failures the current runtime actually
    produces (no invented/aspirational codes)."""

    # Contract / version validation (pre-authorization; never an ALLOW).
    CONTRACT_VERSION_MALFORMED = "CONTRACT_VERSION_MALFORMED"
    CONTRACT_VERSION_UNSUPPORTED = "CONTRACT_VERSION_UNSUPPORTED"
    CONTRACT_FIELD_MISSING = "CONTRACT_FIELD_MISSING"
    CONTRACT_FIELD_INVALID = "CONTRACT_FIELD_INVALID"

    # Authentication of the caller to the gateway.
    AUTHENTICATION_FAILED = "AUTHENTICATION_FAILED"

    # Governance decision outcomes that block execution.
    VERDICT_DENY = "VERDICT_DENY"
    VERDICT_ESCALATE_REQUIRED = "VERDICT_ESCALATE_REQUIRED"

    # Gate-side verification failures.
    DECISION_BINDING_MISMATCH = "DECISION_BINDING_MISMATCH"
    NONCE_REPLAYED = "NONCE_REPLAYED"

    # Gate / executor outcomes.
    GATE_REJECTED = "GATE_REJECTED"
    EXECUTION_FAILED = "EXECUTION_FAILED"
    EXECUTION_AMBIGUOUS = "EXECUTION_AMBIGUOUS"

    # Transport.
    TRANSPORT_TIMEOUT = "TRANSPORT_TIMEOUT"
    TRANSPORT_UNAVAILABLE = "TRANSPORT_UNAVAILABLE"

    # Catch-all — always fails closed.
    INTERNAL_ERROR = "INTERNAL_ERROR"


#: Canonical category for each error code. Every code maps to exactly one category.
_CODE_CATEGORY: Dict[ContractErrorCode, ErrorCategory] = {
    ContractErrorCode.CONTRACT_VERSION_MALFORMED: ErrorCategory.VERSION,
    ContractErrorCode.CONTRACT_VERSION_UNSUPPORTED: ErrorCategory.VERSION,
    ContractErrorCode.CONTRACT_FIELD_MISSING: ErrorCategory.CONTRACT,
    ContractErrorCode.CONTRACT_FIELD_INVALID: ErrorCategory.CONTRACT,
    ContractErrorCode.AUTHENTICATION_FAILED: ErrorCategory.AUTHENTICATION,
    ContractErrorCode.VERDICT_DENY: ErrorCategory.DECISION,
    ContractErrorCode.VERDICT_ESCALATE_REQUIRED: ErrorCategory.DECISION,
    ContractErrorCode.DECISION_BINDING_MISMATCH: ErrorCategory.VERIFICATION,
    ContractErrorCode.NONCE_REPLAYED: ErrorCategory.VERIFICATION,
    ContractErrorCode.GATE_REJECTED: ErrorCategory.GATE,
    ContractErrorCode.EXECUTION_FAILED: ErrorCategory.EXECUTION,
    ContractErrorCode.EXECUTION_AMBIGUOUS: ErrorCategory.EXECUTION,
    ContractErrorCode.TRANSPORT_TIMEOUT: ErrorCategory.TRANSPORT,
    ContractErrorCode.TRANSPORT_UNAVAILABLE: ErrorCategory.TRANSPORT,
    ContractErrorCode.INTERNAL_ERROR: ErrorCategory.INTERNAL,
}

#: Whether a code is retryable *at the contract level*. Retryability is never a
#: permission to execute (a negative guarantee); it only tells a caller whether a
#: fresh, fully re-authorized attempt could plausibly succeed.
_CODE_RETRYABLE: Dict[ContractErrorCode, bool] = {
    ContractErrorCode.TRANSPORT_TIMEOUT: True,
    ContractErrorCode.TRANSPORT_UNAVAILABLE: True,
    # Everything else is not blindly retryable: a DENY stays denied, a replayed
    # nonce must not be replayed again, an ambiguous execution must be reconciled
    # via the audit chain rather than retried.
}

# Ordered most-specific first: exception subclasses are checked before their
# bases so, e.g., MCCTimeoutError resolves before its parent MCCTransportError.
_EXCEPTION_CODES: Tuple[Tuple[type, ContractErrorCode], ...] = (
    (MCCTimeoutError, ContractErrorCode.TRANSPORT_TIMEOUT),
    (MCCTransportError, ContractErrorCode.TRANSPORT_UNAVAILABLE),
    (MCCAuthenticationError, ContractErrorCode.AUTHENTICATION_FAILED),
    (MCCDeniedError, ContractErrorCode.VERDICT_DENY),
    (MCCApprovalRequiredError, ContractErrorCode.VERDICT_ESCALATE_REQUIRED),
    (MCCInvalidDecisionError, ContractErrorCode.DECISION_BINDING_MISMATCH),
    (MCCReplayError, ContractErrorCode.NONCE_REPLAYED),
    (MCCAmbiguousExecutionError, ContractErrorCode.EXECUTION_AMBIGUOUS),
    (MCCExecutionError, ContractErrorCode.EXECUTION_FAILED),
    (MCCProtocolError, ContractErrorCode.CONTRACT_FIELD_INVALID),
    (MCCError, ContractErrorCode.INTERNAL_ERROR),
)


def category_of(code: ContractErrorCode) -> ErrorCategory:
    """Return the canonical category for a stable error code."""
    return _CODE_CATEGORY[code]


def is_retryable(code: ContractErrorCode) -> bool:
    """Whether a code is retryable at the contract level (never a permission to
    execute — see the contract's negative guarantees)."""
    return _CODE_RETRYABLE.get(code, False)


def error_code_for_exception(exc: BaseException) -> ContractErrorCode:
    """Map an ``mcc_client`` exception to its stable contract error code.

    Fails closed: anything not an :class:`MCCError` (or unmapped) becomes
    :data:`ContractErrorCode.INTERNAL_ERROR`, which is a blocking classification —
    it is never treated as authorization."""
    for exc_type, code in _EXCEPTION_CODES:
        if isinstance(exc, exc_type):
            return code
    return ContractErrorCode.INTERNAL_ERROR


# --------------------------------------------------------------------------- #
# Version compatibility (deterministic, fail-closed).                         #
# --------------------------------------------------------------------------- #

@dataclass(frozen=True)
class VersionCompatibility:
    """Result of checking a declared contract version against this build.

    ``compatible`` is the only field that gates behavior. When ``False``,
    ``error_code`` is always populated with a blocking code — a caller MUST fail
    closed and MUST NOT silently downgrade to an unsupported version."""

    requested: str
    compatible: bool
    reason: str
    error_code: Optional[ContractErrorCode] = None
    requested_major: Optional[int] = None
    requested_minor: Optional[int] = None

    @property
    def newer_minor(self) -> bool:
        """True when the peer speaks a supported major but a *higher* minor than
        this build. Compatible (minor changes are additive), but the caller should
        not assume it understands optional additive fields it has never seen."""
        return (
            self.compatible
            and self.requested_major == CONTRACT_MAJOR
            and (self.requested_minor or 0) > CONTRACT_MINOR
        )


def _parse_version(version: str) -> Optional[Tuple[int, int]]:
    if not isinstance(version, str):
        return None
    parts = version.strip().split(".")
    if len(parts) != 2:
        return None
    try:
        major, minor = int(parts[0]), int(parts[1])
    except ValueError:
        return None
    if major < 0 or minor < 0:
        return None
    return major, minor


def check_version_compatibility(version: str) -> VersionCompatibility:
    """Check a declared ``MAJOR.MINOR`` contract version against this build.

    Rules (deterministic, fail-closed):

    * malformed  -> not compatible, ``CONTRACT_VERSION_MALFORMED``;
    * unknown major -> not compatible, ``CONTRACT_VERSION_UNSUPPORTED``;
    * known major -> compatible (minor differences are backward-compatible /
      additive). A *higher* minor is still compatible but flagged via
      :attr:`VersionCompatibility.newer_minor`.

    This never mutates state and never authorizes anything."""
    parsed = _parse_version(version)
    if parsed is None:
        return VersionCompatibility(
            requested=str(version), compatible=False,
            reason="contract version is not a valid MAJOR.MINOR string",
            error_code=ContractErrorCode.CONTRACT_VERSION_MALFORMED,
        )
    major, minor = parsed
    if major not in SUPPORTED_MAJORS:
        return VersionCompatibility(
            requested=version, compatible=False,
            reason=(f"contract major {major} is not supported "
                    f"(this build supports {sorted(SUPPORTED_MAJORS)})"),
            error_code=ContractErrorCode.CONTRACT_VERSION_UNSUPPORTED,
            requested_major=major, requested_minor=minor,
        )
    return VersionCompatibility(
        requested=version, compatible=True,
        reason="supported major; minor differences are backward-compatible",
        requested_major=major, requested_minor=minor,
    )


# --------------------------------------------------------------------------- #
# Conformance manifest (consumed by PR #44).                                  #
# --------------------------------------------------------------------------- #

#: The mandatory execution invariants the Gate verifies before actuation. These
#: names match the invariant-ownership matrix in ``docs/INTEGRATION_CONTRACT.md``.
#: An adapter MAY supply material toward them but MUST NOT mark any as satisfied;
#: the Gate is the sole verifier and its result cannot be overridden.
REQUIRED_SECURITY_INVARIANTS: Tuple[str, ...] = (
    "signature_verified",
    "decision_authority_valid",
    "verdict_authorizes",
    "scope_matches",
    "actor_matches",
    "resource_matches",
    "action_hash_matches",
    "nonce_matches",
    "nonce_not_replayed",
    "within_validity_window",
    "not_revoked",
    "policy_hash_matches",
    "durably_recorded_before_enforce",
)

#: Public, side-effect-free validation entry points an external adapter author or
#: PR #44 can call. None of these authorize, sign, or touch the network.
PUBLIC_VALIDATION_ENTRY_POINTS: Tuple[str, ...] = (
    "mcc_client.contract.check_version_compatibility",
    "mcc_client.contract.error_code_for_exception",
    "mcc_client.contract.category_of",
    "mcc_client.contract.is_retryable",
    "mcc_client.contract.conformance_manifest",
    "mcc_client.Verdict.parse",
    "mcc_client.Decision.from_response",
)

#: Canonical authorization artifacts the Gate accepts (existing SDK types — not a
#: new token format).
AUTHORIZATION_ARTIFACTS: Tuple[str, ...] = (
    "ConsensusAuthorization",
    "MandateAuthorization",
    "ApprovalAuthorization",
)


def conformance_manifest() -> Dict[str, Any]:
    """Return the deterministic, machine-readable conformance manifest.

    Reproducible: equal on every call, JSON-serializable, and derived entirely
    from the canonical identifiers above (single source of truth). PR #44 builds
    its certification matrix from this manifest. It asserts nothing about any
    specific adapter and never claims certification.
    """
    return {
        "contract_identifier": CONTRACT_IDENTIFIER,
        "contract_version": CONTRACT_VERSION,
        "supported_majors": sorted(SUPPORTED_MAJORS),
        "canonical_models": {
            # The contract reuses the SDK's shipped models; it defines no parallel
            # wire models. Fully-qualified so PR #44 can import them directly.
            "verdict": "mcc_client.Verdict",
            "decision": "mcc_client.Decision",
            "execution_result": "mcc_client.ExecutionResult",
            "approval": "mcc_client.Approval",
        },
        "supported_verdicts": [v.value for v in Verdict],
        "authorization_artifacts": list(AUTHORIZATION_ARTIFACTS),
        "error_categories": [c.value for c in ErrorCategory],
        "error_codes": [
            {"code": code.value, "category": category_of(code).value,
             "retryable": is_retryable(code)}
            for code in ContractErrorCode
        ],
        "required_security_invariants": list(REQUIRED_SECURITY_INVARIANTS),
        "public_validation_entry_points": list(PUBLIC_VALIDATION_ENTRY_POINTS),
        "golden_vectors": "tests/contract_vectors/",
        "normative_specification": "docs/INTEGRATION_CONTRACT.md",
        "framework_neutral": True,
        "transport_neutral": True,
        # Explicit non-claims — see docs/INTEGRATION_CONTRACT.md.
        "certifies_any_adapter": False,
    }


__all__ = [
    "CONTRACT_IDENTIFIER",
    "CONTRACT_VERSION",
    "CONTRACT_MAJOR",
    "CONTRACT_MINOR",
    "SUPPORTED_MAJORS",
    "ErrorCategory",
    "ContractErrorCode",
    "VersionCompatibility",
    "check_version_compatibility",
    "error_code_for_exception",
    "category_of",
    "is_retryable",
    "conformance_manifest",
    "REQUIRED_SECURITY_INVARIANTS",
    "PUBLIC_VALIDATION_ENTRY_POINTS",
    "AUTHORIZATION_ARTIFACTS",
]
