"""Safe, explicit configuration for the Phase 2 live sandbox proof.

Defaults to fully disabled: zero external requests unless every required
environment variable is explicitly set. Mirrors
``examples/gpt6_astra_reference/github_actuator.py``'s
``GitHubActuatorConfig`` safety posture exactly (disabled default, an
explicit sandbox repo required, the MCC-Core repository itself refused by
default) -- this is a deliberate, parallel config surface, not a
duplicated actuator architecture: the actual HTTP-dispatch implementation
is reused unchanged from that module (see ``actuator.py``).
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Mapping, Optional

#: Destinations this proof must never target, regardless of operator
#: configuration, unless explicitly (and dangerously) overridden.
FORBIDDEN_SANDBOX_REPOS = frozenset({"mcc-prior-art/mcc-layer"})


class SandboxConfigError(Exception):
    """Raised at construction time for missing/invalid/forbidden
    configuration. Fail-closed: no partial/best-effort configuration is
    ever accepted."""


@dataclass(frozen=True)
class SandboxConfig:
    live: bool
    repo: Optional[str]
    base_url: str
    token: Optional[str]
    redis_url: Optional[str]

    @classmethod
    def from_env(cls, env: Optional[Mapping[str, str]] = None) -> "SandboxConfig":
        env = os.environ if env is None else env
        live_raw = (env.get("MCC_PHASE2_LIVE_SANDBOX", "") or "").strip().lower()
        live = live_raw in ("1", "true", "yes")
        repo = (env.get("MCC_PHASE2_SANDBOX_REPO", "") or "").strip() or None
        base_url = (env.get("MCC_PHASE2_SANDBOX_GITHUB_BASE_URL", "") or "https://api.github.com").strip()
        token = (env.get("GITHUB_TOKEN", "") or "").strip() or None
        redis_url = (env.get("MCC_REDIS_URL", "") or "").strip() or None

        if not live:
            # Disabled is always a valid, safe configuration -- no further
            # validation needed; nothing below this point is ever reachable
            # by an actuator/stack built from a disabled config.
            return cls(live=False, repo=repo, base_url=base_url.rstrip("/"), token=token, redis_url=redis_url)

        if not repo:
            raise SandboxConfigError(
                "MCC_PHASE2_LIVE_SANDBOX=1 requires MCC_PHASE2_SANDBOX_REPO=owner/repo "
                "to be explicitly configured; there is no default sandbox repository"
            )
        allow_override = (env.get("MCC_PHASE2_ALLOW_CORE_REPO", "") or "").strip().lower() in ("1", "true", "yes")
        if repo.strip().lower() in FORBIDDEN_SANDBOX_REPOS and not allow_override:
            raise SandboxConfigError(
                f"MCC_PHASE2_SANDBOX_REPO must not be the MCC-Core repository itself "
                f"({repo!r}); configure a dedicated, isolated sandbox repository. "
                "(MCC_PHASE2_ALLOW_CORE_REPO=1 would override this -- do not set it.)"
            )
        if not token:
            raise SandboxConfigError("MCC_PHASE2_LIVE_SANDBOX=1 requires GITHUB_TOKEN to be set")
        if not redis_url:
            raise SandboxConfigError(
                "MCC_PHASE2_LIVE_SANDBOX=1 requires MCC_REDIS_URL to be set -- the live "
                "proof uses a real, durable, shared backend (Redis) in enforcement mode, "
                "never an unscoped in-memory fallback"
            )
        return cls(live=True, repo=repo, base_url=base_url.rstrip("/"), token=token, redis_url=redis_url)


__all__ = ["SandboxConfig", "SandboxConfigError", "FORBIDDEN_SANDBOX_REPOS"]
