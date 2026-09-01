"""Configuration for the OPT-IN attestation-aware full-chain reference
pilot (PR-6). Separate from, and additive to, ``config.py::PilotConfig`` --
constructing this does not change anything about the existing evaluate-only
``PilotIntegration`` path; a pilot operator who never imports this module
sees no behavior change at all (see docs/PILOT_RUNBOOK.md §18-19 for when
to use which).

Twelve-factor style, same convention as ``PilotConfig``: every value is
settable via an ``MCC_PILOT_*`` environment variable, fails closed (raises
``AttestationChainConfigError``) rather than silently defaulting when a
required value is missing -- there is no "assume unattested" fallback.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

from .config import Mode


class AttestationChainConfigError(ValueError):
    """Invalid or missing attestation-chain pilot configuration."""


@dataclass(frozen=True)
class AttestationChainConfig:
    """Configuration for the full-chain reference pilot. Immutable once
    constructed.

    ``attester_auth_secret`` is intentionally excluded from evidence export
    (see ``attestation_evidence.py``) -- it is a service-to-service
    credential, never a decision-making artifact and never partner-visible
    in an evidence bundle.
    """

    gateway_url: str
    attester_url: str
    attester_auth_secret: str
    gateway_api_key: str
    mode: Mode = "observe"
    timeout_seconds: float = 10.0
    action: str = "send_notification"
    resource: str = "notifications"

    def __post_init__(self) -> None:
        for field_name, value in (
            ("gateway_url", self.gateway_url), ("attester_url", self.attester_url),
        ):
            if not value or not (value.startswith(("http://", "https://"))):
                raise AttestationChainConfigError(
                    f"{field_name} must start with http:// or https://: {value!r}"
                )
        if not self.attester_auth_secret:
            raise AttestationChainConfigError("attester_auth_secret is required")
        if not self.gateway_api_key:
            raise AttestationChainConfigError("gateway_api_key is required")
        if self.mode not in ("observe", "enforced"):
            raise AttestationChainConfigError(f"mode must be 'observe' or 'enforced': {self.mode!r}")
        if self.timeout_seconds <= 0:
            raise AttestationChainConfigError(
                f"timeout_seconds must be positive: {self.timeout_seconds!r}"
            )
        if not self.action:
            raise AttestationChainConfigError("action is required")
        if not self.resource:
            raise AttestationChainConfigError("resource is required")

    @classmethod
    def from_env(cls, env: dict[str, str] | None = None) -> AttestationChainConfig:
        """Build a config from ``MCC_PILOT_ATTESTATION_*``/``MCC_PILOT_*``
        environment variables. Pass ``env`` explicitly in tests instead of
        mutating ``os.environ``. Raises :class:`AttestationChainConfigError`
        (never silently proceeds with a placeholder) when a required
        variable is absent."""
        e = os.environ if env is None else env
        missing = [
            name for name in (
                "MCC_PILOT_GATEWAY_URL", "MCC_PILOT_ATTESTATION_ATTESTER_URL",
                "MCC_PILOT_ATTESTATION_ATTESTER_AUTH_SECRET", "MCC_PILOT_API_KEY",
            )
            if name not in e
        ]
        if missing:
            raise AttestationChainConfigError(
                f"missing required environment variable(s) for the attestation-aware "
                f"full-chain pilot: {', '.join(missing)}"
            )
        kwargs: dict[str, object] = {
            "gateway_url": e["MCC_PILOT_GATEWAY_URL"],
            "attester_url": e["MCC_PILOT_ATTESTATION_ATTESTER_URL"],
            "attester_auth_secret": e["MCC_PILOT_ATTESTATION_ATTESTER_AUTH_SECRET"],
            "gateway_api_key": e["MCC_PILOT_API_KEY"],
        }
        if "MCC_PILOT_MODE" in e:
            kwargs["mode"] = e["MCC_PILOT_MODE"]
        if "MCC_PILOT_TIMEOUT_SECONDS" in e:
            kwargs["timeout_seconds"] = float(e["MCC_PILOT_TIMEOUT_SECONDS"])
        if "MCC_PILOT_ATTESTATION_ACTION" in e:
            kwargs["action"] = e["MCC_PILOT_ATTESTATION_ACTION"]
        if "MCC_PILOT_ATTESTATION_RESOURCE" in e:
            kwargs["resource"] = e["MCC_PILOT_ATTESTATION_RESOURCE"]
        return cls(**kwargs)  # type: ignore[arg-type]


__all__ = ["AttestationChainConfig", "AttestationChainConfigError"]
