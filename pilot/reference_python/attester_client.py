"""A minimal, synchronous HTTP client for the Independent Attester Service
(PR-4, ``src/mcc_attester_service``; ``POST /attest``).

This is transport only -- exactly the same posture as ``mcc_sdk.MCCClient``
for the Gateway. It never signs anything, never asserts a claim itself, and
never fabricates an attestation: every attestation returned here is the
Attester's own genuine, signed HTTP response, or this client raises.

The Attester is a SEPARATE process, in a separate trust domain, holding its
own Ed25519 private key -- this client only ever reaches it over HTTP (see
``specs/MCC-AT-004.md``). This module deliberately holds no signing key and
performs no verification of its own: verification of what the Attester
signed is the Gateway's ``PreExecutionControl``'s job (server-side, always
re-checked there), never this client's.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import httpx


class AttesterClientError(RuntimeError):
    """Transport-level failure talking to the Attester service, or a
    request the Attester itself declined (e.g. no assessment configured for
    the action -- HTTP 503 ``ATTESTATION_UNAVAILABLE``). Never a forged or
    partial attestation -- this is always raised instead."""


@dataclass(frozen=True)
class AttesterClient:
    """A synchronous client for a running Independent Attester Service.

    ``auth_secret`` is the service-to-service shared secret the Attester's
    own ``_require_service_auth`` dependency checks (constant-time compare,
    server-side) -- never a decision-making credential, and never included
    in any evidence this pilot exports (see ``attestation_evidence.py``)."""

    base_url: str
    auth_secret: str
    timeout_seconds: float = 10.0

    def attest(
        self, *, action: str, resource: str | None, payload: dict[str, Any],
    ) -> dict[str, Any]:
        """Request a genuine, signed EvidenceAttestation for exactly this
        ``(action, resource, payload)`` description. Returns the Attester's
        raw JSON response (an ``mcc-attestation/1`` document; see
        ``src/mcc_attestation/schema.py``) unmodified -- this client adds and
        removes nothing. Raises :class:`AttesterClientError` on any
        transport failure, non-2xx response, or non-JSON body; never
        returns a fabricated or partial attestation."""
        try:
            resp = httpx.post(
                f"{self.base_url.rstrip('/')}/attest",
                json={"action": action, "resource": resource, "payload": dict(payload)},
                headers={"X-Attester-Auth": self.auth_secret},
                timeout=self.timeout_seconds,
            )
        except httpx.HTTPError as exc:
            raise AttesterClientError(f"attester POST /attest failed: {exc}") from exc

        if resp.status_code == 401:
            raise AttesterClientError("INVALID_ATTESTER_AUTH: rejected by the Attester service")
        if resp.status_code != 200:
            raise AttesterClientError(
                f"attester declined to attest (HTTP {resp.status_code}): {resp.text[:500]}"
            )
        try:
            return resp.json()
        except Exception as exc:
            raise AttesterClientError(f"non-JSON response from attester (HTTP {resp.status_code})") from exc

    def health(self) -> dict[str, Any]:
        try:
            resp = httpx.get(f"{self.base_url.rstrip('/')}/health", timeout=self.timeout_seconds)
        except httpx.HTTPError as exc:
            raise AttesterClientError(f"attester GET /health failed: {exc}") from exc
        try:
            return resp.json()
        except Exception as exc:
            raise AttesterClientError(f"non-JSON /health response (HTTP {resp.status_code})") from exc


__all__ = ["AttesterClient", "AttesterClientError"]
