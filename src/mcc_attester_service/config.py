"""AttesterServiceConfig — the Attester service's own trusted configuration.

Owns exactly what the service itself controls: signing identity, the
validity-window bound, scope templating, optional policy binding, and the
service-to-service authentication secret. None of this is caller-supplied
at request time; every field here is trusted, server-side configuration,
loaded once at process start.

The private signing key configured here is the whole point of PR-4's trust
boundary: it exists ONLY in this module's caller (the Attester process),
never in ``gateway/*`` or ``src/mcc_core/*`` -- see
``tests/test_attester_service_architecture_guards.py``.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Mapping, Optional

from mcc_core.signing import SigningKey

from .errors import AttesterServiceConfigError

MIN_VALIDITY_SECONDS = 1
MAX_VALIDITY_SECONDS = 3600
DEFAULT_VALIDITY_SECONDS = 300

#: The service-to-service auth secret must not be a trivially short/guessable
#: string. This is a floor, not a strength guarantee -- see
#: specs/MCC-AT-004.md for what this authentication boundary does and does
#: not prove.
MIN_AUTH_SECRET_LENGTH = 16


@dataclass(frozen=True)
class AttesterServiceConfig:
    """Trusted configuration for one Attester service process.

    ``auth_secret`` is deliberately a SEPARATE value from ``signing_key``:
    it authenticates HTTP callers to this service's ``/attest`` endpoint
    (design rule 7) and carries no cryptographic relationship whatsoever to
    the Ed25519 key that signs attestations. Compromising one must not
    compromise the other.
    """

    attester_id: str
    signing_key: SigningKey
    auth_secret: str
    scope_template: str
    validity_seconds: int = DEFAULT_VALIDITY_SECONDS
    policy_hash: Optional[str] = None
    policy_version: Optional[str] = None

    def __post_init__(self) -> None:
        if not self.attester_id:
            raise AttesterServiceConfigError("attester_id must be non-empty")
        if not isinstance(self.signing_key, SigningKey):
            raise AttesterServiceConfigError(
                "signing_key must be a mcc_core.signing.SigningKey instance"
            )
        if not self.auth_secret or len(self.auth_secret) < MIN_AUTH_SECRET_LENGTH:
            raise AttesterServiceConfigError(
                f"auth_secret must be a non-empty string of at least "
                f"{MIN_AUTH_SECRET_LENGTH} characters -- this is the "
                f"service-to-service authentication secret, and it MUST be "
                f"distinct from the Attester's Ed25519 signing key"
            )
        if not self.scope_template:
            raise AttesterServiceConfigError("scope_template must be non-empty")
        if not isinstance(self.validity_seconds, int) or isinstance(self.validity_seconds, bool):
            raise AttesterServiceConfigError("validity_seconds must be an integer")
        if not (MIN_VALIDITY_SECONDS <= self.validity_seconds <= MAX_VALIDITY_SECONDS):
            raise AttesterServiceConfigError(
                f"validity_seconds must be within [{MIN_VALIDITY_SECONDS}, "
                f"{MAX_VALIDITY_SECONDS}], got {self.validity_seconds}"
            )

    def resolve_scope(self, *, action: str, resource: Optional[str]) -> str:
        """Deterministic scope resolution -- the SAME templating convention
        ``gateway.pre_execution_control.AttestationRequirement.resolve_scope``
        uses (plain ``str.format`` over two trusted, service-derived fields
        only; no DSL). The caller supplies ``action``/``resource`` to
        describe the operation, but the template itself is trusted
        server-side configuration the caller cannot alter."""
        return self.scope_template.format(action=action, resource=resource or "")


def attester_service_config_from_env(
    env: Optional[Mapping[str, str]] = None,
) -> AttesterServiceConfig:
    """Build a trusted config from environment variables. Fails closed:
    every required value must be explicitly set. There is no silent
    signing-key generation, no default auth secret, and no default scope
    template -- a service that cannot be configured safely refuses to
    start, mirroring the repository's existing fail-closed-startup
    convention (``gateway.governance_api._build_pre_execution_control``,
    ``MCC_REQUIRE_CONSENSUS``).
    """
    env = os.environ if env is None else env

    attester_id = env.get("MCC_ATTESTER_ID", "").strip()
    if not attester_id:
        raise AttesterServiceConfigError("MCC_ATTESTER_ID is required")

    key_path = env.get("MCC_ATTESTER_SIGNING_KEY_PATH", "").strip()
    if not key_path:
        raise AttesterServiceConfigError(
            "MCC_ATTESTER_SIGNING_KEY_PATH is required -- refusing to generate "
            "or otherwise silently materialize an Attester signing key at startup"
        )
    kid = env.get("MCC_ATTESTER_KEY_ID", "").strip()
    if not kid:
        raise AttesterServiceConfigError("MCC_ATTESTER_KEY_ID is required")
    try:
        signing_key = SigningKey.from_pem_file(key_path, kid)
    except Exception as exc:  # noqa: BLE001 -- any load failure is fail-closed config error
        raise AttesterServiceConfigError(
            f"could not load Attester signing key from {key_path!r}: {exc!r}"
        ) from exc

    auth_secret = env.get("MCC_ATTESTER_SERVICE_AUTH_SECRET", "").strip()
    if not auth_secret:
        raise AttesterServiceConfigError("MCC_ATTESTER_SERVICE_AUTH_SECRET is required")

    scope_template = env.get("MCC_ATTESTER_SCOPE_TEMPLATE", "").strip()
    if not scope_template:
        raise AttesterServiceConfigError("MCC_ATTESTER_SCOPE_TEMPLATE is required")

    validity_raw = env.get("MCC_ATTESTER_VALIDITY_SECONDS", "").strip()
    if validity_raw:
        try:
            validity_seconds = int(validity_raw)
        except ValueError as exc:
            raise AttesterServiceConfigError(
                f"MCC_ATTESTER_VALIDITY_SECONDS must be an integer, got {validity_raw!r}"
            ) from exc
    else:
        validity_seconds = DEFAULT_VALIDITY_SECONDS

    policy_hash = env.get("MCC_ATTESTER_POLICY_HASH", "").strip() or None
    policy_version = env.get("MCC_ATTESTER_POLICY_VERSION", "").strip() or None

    return AttesterServiceConfig(
        attester_id=attester_id,
        signing_key=signing_key,
        auth_secret=auth_secret,
        scope_template=scope_template,
        validity_seconds=validity_seconds,
        policy_hash=policy_hash,
        policy_version=policy_version,
    )


__all__ = [
    "AttesterServiceConfig",
    "attester_service_config_from_env",
    "MIN_VALIDITY_SECONDS",
    "MAX_VALIDITY_SECONDS",
    "DEFAULT_VALIDITY_SECONDS",
    "MIN_AUTH_SECRET_LENGTH",
]
