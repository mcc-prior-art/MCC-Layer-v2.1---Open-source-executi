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


class ResourceBindingError(Exception):
    """Raised BEFORE any external call when the authorized resource does not
    exactly match the actuator's own configured destination repository --
    the deployment-misconfiguration class this guards against is an
    authorization that says repository A while the actuator's own
    configuration/credentials target repository B. This is deliberately a
    plain equality check (no normalization, no case-folding, no alias
    table) -- see ``models.require_canonical_resource`` for the identical
    discipline applied one layer earlier, at the proposal boundary."""


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

    @property
    def config(self) -> GitHubActuatorConfig:
        return self._config

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


class ResourceBoundActuator:
    """Wraps a :class:`GitHubIssueActuator` (or any ``async def (action,
    payload)`` upstream callable) with an explicit, synchronous,
    pre-external-call check that the resource this call was AUTHORIZED for
    exactly matches the actuator's OWN configured destination.

    This deliberately does not thread ``resource`` through the generic
    ``gateway.governance_service.Upstream`` contract (``(action, payload) ->
    Any``, shared by every other governed executor in this repository) --
    doing so would change a call signature many unrelated actuators rely on.
    Instead the authorized resource is captured once, at construction time
    (the caller already knows it -- it is the resource a mandate/token was
    just verified against), so the check runs with zero change to the
    upstream call shape and therefore zero risk to any other actuator.

    Raises :class:`ResourceBindingError` synchronously, before awaiting
    anything, so no external call is ever attempted on a mismatch (test
    scenario 20)."""

    def __init__(self, actuator: GitHubIssueActuator, *, authorized_resource: str) -> None:
        self._actuator = actuator
        self._authorized_resource = authorized_resource

    async def __call__(self, action: str, payload: Dict[str, Any]) -> Any:
        configured = self._actuator.config.repo
        if self._authorized_resource != configured:
            raise ResourceBindingError(
                f"authorized resource {self._authorized_resource!r} does not match this "
                f"actuator's configured destination {configured!r}; refusing before any "
                "external call"
            )
        return await self._actuator(action, payload)


#: The exact, greppable marker reconciliation searches for in an issue body.
#: The real GitHub "create issue" API has no idempotency-key parameter (it is
#: not, in general, a safely-retriable endpoint) -- embedding the logical
#: operation's id in the body is the only way this reference actuator gives
#: reconciliation something to search for. This is the honest boundary: it
#: proves "an issue whose body names this exact logical_operation_id exists",
#: not "GitHub deduplicated the create for us".
LOGICAL_OPERATION_MARKER_PREFIX = "<!-- mcc-logical-operation-id: "
LOGICAL_OPERATION_MARKER_SUFFIX = " -->"


def logical_operation_marker(logical_operation_id: str) -> str:
    return f"{LOGICAL_OPERATION_MARKER_PREFIX}{logical_operation_id}{LOGICAL_OPERATION_MARKER_SUFFIX}"


class LogicalOperationMarkerActuator:
    """Wraps an upstream ``async def (action, payload)`` callable, appending
    the exact, greppable ``logical_operation_marker`` to the issue body
    before delegating -- purely so reconciliation (see
    ``reconciliation.py``) has independent, positive external evidence to
    search for later. Never changes ``title``; never invents an operation id
    on its own (the id is always supplied by the caller, the same one bound
    into the token's ``idempotency_key`` -- see ``models.py``).

    ``logical_operation_id`` is mutable (a plain settable property, not
    fixed at construction) so ONE long-lived wrapper instance -- e.g. one
    actuator shared across several governed calls in a single scenario,
    each with its own logical operation -- can still mark each call
    correctly: the caller sets ``.logical_operation_id`` to the id it is
    about to present to ``run_positive_path``/``issue_authority``
    immediately before making that call. There is no concurrency within one
    such call sequence (each governed call is awaited to completion before
    the next), so this ordering is safe. The two ids MUST be kept in sync by
    the caller -- see ``adversarial.py``'s ``build_multi_actuator`` for the
    reference pattern (Round 18 requirement 5: the marker must always
    reflect the SAME verified logical_operation_id as admission/the
    token/reconciliation, never an independently-drifting one)."""

    def __init__(self, actuator, *, logical_operation_id: str) -> None:
        self._actuator = actuator
        self._logical_operation_id = logical_operation_id

    @property
    def logical_operation_id(self) -> str:
        return self._logical_operation_id

    @logical_operation_id.setter
    def logical_operation_id(self, value: str) -> None:
        self._logical_operation_id = value

    async def __call__(self, action: str, payload: Dict[str, Any]) -> Any:
        marked = dict(payload)
        body = marked.get("body", "")
        marked["body"] = f"{body}\n\n{logical_operation_marker(self._logical_operation_id)}"
        return await self._actuator(action, marked)


__all__ = [
    "GitHubActuatorConfig", "GitHubActuatorConfigError", "GitHubActuatorDisabledError",
    "GitHubIssueActuator", "ResourceBindingError", "ResourceBoundActuator",
    "LOGICAL_OPERATION_MARKER_PREFIX", "LOGICAL_OPERATION_MARKER_SUFFIX",
    "logical_operation_marker", "LogicalOperationMarkerActuator", "DISABLED", "LIVE",
]
