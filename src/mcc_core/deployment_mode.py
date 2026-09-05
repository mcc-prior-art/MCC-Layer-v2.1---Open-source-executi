"""Deployment-mode selection — the one explicit switch between
reference/development posture and production/enforcement posture for
subsystems whose *default* configuration is safe for development but must
never be silently reused in a real deployment.

This is deliberately narrow and does not replace or widen ``MCC_ENV``
(``gateway.trust.trust_set_from_env``). ``MCC_ENV=pilot`` gates exactly the
external-mandate trust-config requirement and Redis key-namespacing — see
``docs/PILOT_VOLTAGENT_DEPLOYMENT.md``'s own explicit statement that its
Redis-backed durability is "enforced by ``MCC_*_BACKEND=redis``, independent
of ``MCC_ENV``." Overloading ``MCC_ENV=pilot`` to also gate nonce-backend
durability or Attester assessment-provider trust would silently widen what
``MCC_ENV`` means and contradict that documented boundary. This module is
the additional, minimal switch those subsystems need instead:

    MCC_DEPLOYMENT_MODE=reference     (default) — development, local
                                       reference runs, single-instance
                                       pilots. Volatile backends and
                                       reference/test providers remain
                                       intentionally usable.
    MCC_DEPLOYMENT_MODE=enforcement   — production / enforcement
                                       deployment. Every subsystem that
                                       owns a durability- or trust-sensitive
                                       default consults ``is_enforcement_mode``
                                       and fails closed rather than silently
                                       accepting a development-grade default.

No decision, execution, or replay logic lives here — this module only
answers "which posture is configured," fail-closed on an unrecognized
value. It is deliberately excluded from the curated ``mcc-core`` wheel
(``setup.py``'s allow-list), the same as ``nonce``/``authority``/etc.
"""

from __future__ import annotations

import os
from typing import Mapping, Optional

_VALID_MODES = ("reference", "enforcement")


class DeploymentModeConfigError(Exception):
    """Raised when ``MCC_DEPLOYMENT_MODE`` is set to an unrecognized value."""


def deployment_mode_from_env(env: Optional[Mapping[str, str]] = None) -> str:
    """Return ``"reference"`` (default) or ``"enforcement"``.

    Fails closed on an unrecognized value rather than silently treating it
    as either posture.
    """
    env = os.environ if env is None else env
    mode = env.get("MCC_DEPLOYMENT_MODE", "reference").strip().lower()
    if mode not in _VALID_MODES:
        raise DeploymentModeConfigError(
            f"unknown MCC_DEPLOYMENT_MODE={mode!r}; expected 'reference' or 'enforcement'"
        )
    return mode


def is_enforcement_mode(env: Optional[Mapping[str, str]] = None) -> bool:
    """``True`` iff ``MCC_DEPLOYMENT_MODE=enforcement``."""
    return deployment_mode_from_env(env) == "enforcement"


__all__ = ["DeploymentModeConfigError", "deployment_mode_from_env", "is_enforcement_mode"]
