"""Protocol version — reconciled with PR #43 (single version axis).

There is exactly **one** version for the canonical governance protocol, and it is
the existing Integration Contract version. This module does not introduce a second,
independent "protocol version" number; :data:`PROTOCOL_VERSION` *is*
:data:`mcc_client.contract.CONTRACT_VERSION`. Version negotiation reuses the PR #43
rule (:func:`mcc_client.contract.check_version_compatibility`) verbatim — an unknown
major fails closed, minor differences are backward-compatible.
"""

from __future__ import annotations

from mcc_client.contract import (
    CONTRACT_VERSION,
    SUPPORTED_MAJORS,
    VersionCompatibility,
    check_version_compatibility,
)

#: The canonical governance protocol version == the Integration Contract version.
#: A single source of truth; never a parallel number.
PROTOCOL_VERSION = CONTRACT_VERSION


def negotiate(requested_version: str) -> VersionCompatibility:
    """Negotiate a declared protocol version against this build.

    Thin, intentional pass-through to the PR #43 contract rule so there is exactly
    one negotiation implementation. Returns the deterministic, fail-closed
    :class:`VersionCompatibility` (``compatible=False`` carries a blocking
    ``error_code``; a caller MUST NOT silently downgrade)."""
    return check_version_compatibility(requested_version)


__all__ = ["PROTOCOL_VERSION", "SUPPORTED_MAJORS", "negotiate", "VersionCompatibility"]
