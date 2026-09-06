"""The ONE safe real external actuator this reference integration adds.

``GitHubIssueActuator`` is a plain callable of the exact shape
``gateway.governance_service.Upstream`` (``async def (action, payload) ->
Any``) — the SAME upstream-executor contract every other governed
executor in this repository already uses
(``pilot_notify.receipt_verifying_upstream``,
``clinic_service``'s equivalent). It is never called directly by Astra or
by this package's own pipeline code; it is only ever reachable as the
``upstream=`` this demo's ``GovernanceService`` is constructed with, which
in turn is only ever invoked from inside
``EnforcementCoordinator.enforce`` — i.e. strictly after a genuine ALLOW
verdict has been fully verified by the real, unmodified Gate. See
``tests/test_gpt6_astra_reference_architecture_guards.py``.

Safety gates, all fail-closed:

* ``MCC_ASTRA_DEMO_MODE`` defaults to ``"disabled"``. In that mode this
  actuator raises on every call and makes no HTTP request whatsoever --
  the reference demo and every test in this package run with the actuator
  disabled unless a scenario explicitly enables it.
* ``MCC_ASTRA_GITHUB_REPO`` (``owner/repo``) must be explicitly configured
  when enabled. There is no default repository, and in particular this
  never defaults to ``mcc-prior-art/mcc-layer`` (or any other real
  production repository) -- an unset value is refused, not silently
  interpreted as "this repo".
* The target repository is fixed at actuator-construction time, not read
  from the proposal or the governed payload -- even a proposal or
  mandate that somehow named a different resource cannot redirect this
  actuator to a different repository at call time.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Dict, Mapping, Optional

DISABLED = "disabled"
LIVE = "live"
_VALID_MODES = (DISABLED, LIVE)


class GitHubActuatorConfigError(Exception):
    """Raised at construction time for a missing/invalid actuator configuration."""


class GitHubActuatorDisabledError(Exception):
    """Raised at call time when the actuator is not enabled. No HTTP request
    is ever made when this is raised."""


@dataclass(frozen=True)
class GitHubActuatorConfig:
    mode: str
    repo: Optional[str]
    base_url: str
    token: Optional[str]

    @classmethod
    def from_env(cls, env: Optional[Mapping[str, str]] = None) -> "GitHubActuatorConfig":
        env = os.environ if env is None else env
        mode = env.get("MCC_ASTRA_DEMO_MODE", DISABLED).strip().lower()
        if mode not in _VALID_MODES:
            raise GitHubActuatorConfigError(
                f"unknown MCC_ASTRA_DEMO_MODE={mode!r}; expected 'disabled' or 'live'"
            )
        repo = env.get("MCC_ASTRA_GITHUB_REPO", "").strip() or None
        if mode == LIVE and not repo:
            raise GitHubActuatorConfigError(
                "MCC_ASTRA_DEMO_MODE=live requires MCC_ASTRA_GITHUB_REPO=owner/repo "
                "to be explicitly configured -- there is no default repository, and "
                "this actuator never infers or falls back to any repository"
            )
        if repo is not None and repo.strip().lower() in (
            "mcc-prior-art/mcc-layer", "mcc-prior-art/mcc-astra-demo".lower()
        ) and env.get("MCC_ASTRA_ALLOW_CORE_REPO", "").strip().lower() not in ("1", "true", "yes"):
            # Extra guard: refuse the MCC-Core repo itself by default even if
            # an operator mistakenly points MCC_ASTRA_GITHUB_REPO at it.
            if repo.strip().lower() == "mcc-prior-art/mcc-layer":
                raise GitHubActuatorConfigError(
                    "MCC_ASTRA_GITHUB_REPO must not be the MCC-Core repository itself "
                    "(mcc-prior-art/mcc-layer); configure an explicit sandbox/demo repo"
                )
        base_url = env.get("MCC_ASTRA_GITHUB_BASE_URL", "https://api.github.com").strip()
        token = env.get("GITHUB_TOKEN", "").strip() or None
        return cls(mode=mode, repo=repo, base_url=base_url.rstrip("/"), token=token)


class GitHubIssueActuator:
    """Calls ``POST {base_url}/repos/{repo}/issues``. The ONLY action this
    actuator supports is ``create_github_issue`` -- there is no dispatch
    table to extend, deliberately, since widening this actuator's
    capability set is out of scope for this reference integration."""

    def __init__(self, config: GitHubActuatorConfig) -> None:
        self._config = config

    @classmethod
    def from_env(cls, env: Optional[Mapping[str, str]] = None) -> "GitHubIssueActuator":
        return cls(GitHubActuatorConfig.from_env(env))

    async def __call__(self, action: str, payload: Dict[str, Any]) -> Any:
        if self._config.mode != LIVE:
            raise GitHubActuatorDisabledError(
                "MCC_ASTRA_DEMO_MODE is not 'live' -- refusing to make any external "
                "call (this is the default, safe posture)"
            )
        if action != "create_github_issue":
            # Defense in depth: even a governed call for an action this
            # actuator was never wired for is refused, never guessed at.
            raise GitHubActuatorDisabledError(
                f"GitHubIssueActuator does not support action {action!r}"
            )
        title = payload.get("title")
        body = payload.get("body", "")
        if not title:
            raise GitHubActuatorDisabledError("payload missing required 'title'")

        import httpx

        headers = {"Accept": "application/vnd.github+json"}
        if self._config.token:
            headers["Authorization"] = f"Bearer {self._config.token}"
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(
                f"{self._config.base_url}/repos/{self._config.repo}/issues",
                headers=headers, json={"title": title, "body": body},
            )
            resp.raise_for_status()
            return resp.json()


__all__ = [
    "GitHubActuatorConfig", "GitHubActuatorConfigError", "GitHubActuatorDisabledError",
    "GitHubIssueActuator", "DISABLED", "LIVE",
]
