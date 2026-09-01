"""Typed, closed error surface for the Independent Attester Service (PR-4).

Every failure mode this service can hit maps to exactly one of these. None
of them ever carries a partially-built or partially-signed attestation --
see ``service.py``: on any of these, the service returns no artifact at
all.
"""

from __future__ import annotations


class AttesterServiceError(Exception):
    """Base class for every error this package raises."""


class AttesterServiceConfigError(AttesterServiceError):
    """The service's own configuration (signing key, auth secret, validity
    window, scope template) is missing or malformed. Raised at startup /
    config-load time -- the service must refuse to come up rather than run
    with an unusable or insecure configuration."""


class AssessmentProviderError(AttesterServiceError):
    """The configured :class:`~mcc_attester_service.provider.AssessmentProvider`
    is unavailable, raised, or returned a malformed result. No signed
    artifact is ever produced for this request; the caller sees a fail-closed
    rejection, never a fabricated or best-effort assessment."""


class BindingDerivationError(AttesterServiceError):
    """The action/payload/scope binding for the request could not be
    deterministically derived (e.g. a malformed payload that cannot be
    canonically hashed). Fail-closed -- never signs over an ambiguous or
    partially-derived binding."""


__all__ = [
    "AttesterServiceError",
    "AttesterServiceConfigError",
    "AssessmentProviderError",
    "BindingDerivationError",
]
