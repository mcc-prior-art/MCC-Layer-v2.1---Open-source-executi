"""AttesterService — orchestrates one ``/attest`` request into one signed
``EvidenceAttestation`` (PR-4, MCC-AT-004).

Owns every piece of trusted, security-relevant construction:

* calls the configured :class:`~mcc_attester_service.provider.AssessmentProvider`
  for assessment content ONLY (``evidence_type``/``claims``/``provenance``);
* derives ``action_hash``/``payload_hash``/``scope`` itself, from the actual
  submitted operation, reusing ``mcc_core.signing``'s existing canonical
  hashing primitives (the SAME ones ``gateway.pre_execution_control`` and
  ``mcc_core.core.DecisionEngine`` use) -- never a caller-supplied hash;
* generates ``attestation_id``/``nonce``/the validity window itself;
* signs via the existing, unmodified PR-1 ``mcc_attestation.attester.LocalAttester``
  (no second signing implementation).

Fail-closed throughout (design rule 8): every documented failure mode
raises before any signing occurs, and no unsigned or partially-trusted
artifact is ever returned as a success.

This module never imports, calls, or references ``DecisionEngine``,
``ExecutionGate``, ``EnforcementCoordinator``, ``PreExecutionControl``, or
any mandate/approval/consensus authority primitive -- an Attester signs
evidence, never authority (design rule: "Attestation remains evidence, NOT
authority"). See ``tests/test_attester_service_architecture_guards.py``.
"""

from __future__ import annotations

import secrets
import time
from typing import Any, Callable, Dict, Optional

from mcc_attestation import AttestationError, LocalAttester
from mcc_core.signing import hash_action, hash_payload

from .config import AttesterServiceConfig
from .errors import AssessmentProviderError, AttesterServiceError, BindingDerivationError
from .provider import AssessmentProvider, AssessmentResult

#: Nonce entropy, matching the existing repository convention
#: (``mcc_core.challenge.NONCE_BYTES``): 32 bytes of ``secrets``-sourced
#: randomness, URL-safe encoded.
NONCE_BYTES = 32


class SigningFailedError(AttesterServiceError):
    """The signing step itself failed (as distinct from a missing/malformed
    key, which fails closed earlier, at config-load time -- see
    ``config.py``). Defense in depth: no signed artifact is returned
    regardless of why signing failed."""


class AttesterService:
    """Independent Attester Service core logic (transport-agnostic — see
    ``app.py`` for the HTTP boundary that calls this)."""

    def __init__(
        self,
        *,
        config: AttesterServiceConfig,
        provider: AssessmentProvider,
        clock: Callable[[], float] = time.time,
    ) -> None:
        self._config = config
        self._provider = provider
        self._clock = clock
        # The ONLY place in this whole service that touches the private
        # signing key: constructing the reference PR-1 Attester with it.
        # Nothing above this line, and nothing in provider.py, ever sees it.
        self._attester = LocalAttester(config.attester_id, config.signing_key)

    async def attest(
        self, *, action: str, resource: Optional[str], payload: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Produce one signed ``EvidenceAttestation`` (as ``to_dict()``) for
        the described operation, or raise -- never a partial result."""
        assessment = await self._assess(action=action, resource=resource, payload=payload)

        try:
            action_hash = hash_action(action)
            payload_hash = hash_payload(payload)
            scope = self._config.resolve_scope(action=action, resource=resource)
        except Exception as exc:  # noqa: BLE001 -- any binding-derivation failure fails closed
            raise BindingDerivationError(
                f"could not derive action/payload/scope binding: {exc!r}"
            ) from exc

        now = int(self._clock())
        nonce = secrets.token_urlsafe(NONCE_BYTES)

        try:
            attestation = self._attester.attest(
                evidence_type=assessment.evidence_type,
                claims=dict(assessment.claims),
                action_hash=action_hash,
                scope=scope,
                provenance=dict(assessment.provenance),
                issued_at=now,
                not_before=now,
                expires_at=now + self._config.validity_seconds,
                nonce=nonce,
                payload_hash=payload_hash,
                policy_hash=self._config.policy_hash,
                policy_version=self._config.policy_version,
            )
        except AttestationError as exc:
            # A malformed assessment (non-canonical claims/provenance, etc.)
            # surfaces here as PR-1's own construction-time validation
            # failing. Still fail-closed -- never a partially built artifact.
            raise AssessmentProviderError(
                f"assessment produced a malformed attestation: {exc!r}"
            ) from exc
        except Exception as exc:  # noqa: BLE001 -- signing itself failed
            raise SigningFailedError(f"signing failed: {exc!r}") from exc

        return attestation.to_dict()

    async def _assess(
        self, *, action: str, resource: Optional[str], payload: Dict[str, Any],
    ) -> AssessmentResult:
        try:
            result = await self._provider.assess(action=action, resource=resource, payload=payload)
        except AssessmentProviderError:
            raise
        except Exception as exc:  # noqa: BLE001 -- ANY provider exception fails closed
            raise AssessmentProviderError(f"assessment provider raised: {exc!r}") from exc
        if not isinstance(result, AssessmentResult):
            raise AssessmentProviderError(
                f"assessment provider returned {type(result).__name__}, "
                f"expected AssessmentResult"
            )
        return result


__all__ = ["AttesterService", "SigningFailedError", "NONCE_BYTES"]
