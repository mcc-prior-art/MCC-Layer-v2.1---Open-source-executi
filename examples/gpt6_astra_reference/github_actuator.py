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

from mcc_core.signing import hash_payload

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


def build_marked_payload(payload: Dict[str, Any], *, logical_operation_id: str) -> Dict[str, Any]:
    """Returns a NEW dict -- ``payload`` itself is never mutated -- whose
    ``body`` has the exact, greppable ``logical_operation_marker`` appended.

    Round 19: this must be called BEFORE the payload is canonicalized,
    attested, hashed, or authorized -- never afterward. Calling it here, at
    proposal-preparation time, makes the marker part of the SAME payload the
    real ``ExecutionGate`` verifies and signs into the decision token's
    ``payload_hash`` -- so there is no longer any step, anywhere downstream
    of authorization, that changes the payload again before it reaches
    :class:`GitHubIssueActuator`. See ``governed_call.prepare_marked_call``
    for the one place every governed call in this reference integration
    calls this."""
    marked = dict(payload)
    body = marked.get("body", "")
    marked["body"] = f"{body}\n\n{logical_operation_marker(logical_operation_id)}"
    return marked


class PayloadBindingError(Exception):
    """Raised by :class:`VerifiedFinalPayloadActuator`, BEFORE any external
    call, when the action/payload about to be sent does not exactly match
    the action/payload_hash this call was armed (via ``.expect(...)``) to
    send -- or when nothing was armed at all. This is the final-boundary
    proof (Round 19 requirement 1) that the exact outbound payload is
    cryptographically bound to a real verified authorization, checked
    immediately before the real HTTP POST, never a value derived from the
    payload this very check is about to evaluate."""


class VerifiedFinalPayloadActuator:
    """The final safety net immediately before the real HTTP call. Wraps an
    upstream ``async def (action, payload)`` callable (typically a
    :class:`ResourceBoundActuator` wrapping the real
    :class:`GitHubIssueActuator`) and refuses to invoke it unless the caller
    has, immediately beforehand, armed this exact call via :meth:`expect`
    with the action and payload_hash it was actually authorized under.

    Deliberately single-use per call: :meth:`__call__` consumes (clears)
    whatever was armed as the very first thing it does, so a caller that
    forgets to re-arm before a subsequent call fails closed with
    :class:`PayloadBindingError` rather than silently reusing a PRIOR call's
    expectation. This is what makes a shared, long-lived actuator instance
    safe to reuse across two different governed calls (Round 19 requirement
    2): there is no persistent, settable "current operation identity" left
    on this object for a second call to accidentally inherit from the
    first -- every call must present its own expectation, every time.

    ``expect(...)`` should be armed with values that come from the real
    verified authorization -- for the two-step
    ``issue_authority``/``enforce_authority`` path, the actual signed
    ``issued.token["action"]``/``issued.token["payload_hash"]``; for the
    one-step ``run_positive_path`` convenience path (where no token exists
    yet at call time), the exact canonical payload about to be submitted,
    hashed with the SAME ``hash_payload`` the real ``ExecutionGate`` uses.
    Either way this is never a value derived from the payload AFTER this
    check runs -- see ``governed_call.prepare_marked_call``, the one place
    every governed call in this reference integration arms this."""

    def __init__(self, actuator: Any) -> None:
        self._actuator = actuator
        self._expected: Optional[Dict[str, str]] = None

    def expect(self, *, action: str, payload_hash: str) -> None:
        self._expected = {"action": action, "payload_hash": payload_hash}

    async def __call__(self, action: str, payload: Dict[str, Any]) -> Any:
        expected = self._expected
        self._expected = None  # single-use: always consumed, whether armed or not
        if expected is None:
            raise PayloadBindingError(
                "no verified action/payload_hash was armed for this call via expect(...) "
                "-- refusing before any external call; a shared actuator never reuses a "
                "prior call's expectation"
            )
        if action != expected["action"]:
            raise PayloadBindingError(
                f"action {action!r} about to be sent does not match the verified "
                f"authorized action {expected['action']!r}; refusing before any "
                "external call"
            )
        actual_hash = hash_payload(payload)
        if actual_hash != expected["payload_hash"]:
            raise PayloadBindingError(
                f"the exact payload about to be sent hashes to {actual_hash!r}, which "
                f"does not match the verified authorized payload_hash "
                f"{expected['payload_hash']!r}; refusing before any external call"
            )
        return await self._actuator(action, payload)


__all__ = [
    "GitHubActuatorConfig", "GitHubActuatorConfigError", "GitHubActuatorDisabledError",
    "GitHubIssueActuator", "ResourceBindingError", "ResourceBoundActuator",
    "LOGICAL_OPERATION_MARKER_PREFIX", "LOGICAL_OPERATION_MARKER_SUFFIX",
    "logical_operation_marker", "build_marked_payload", "PayloadBindingError",
    "VerifiedFinalPayloadActuator", "DISABLED", "LIVE",
]
