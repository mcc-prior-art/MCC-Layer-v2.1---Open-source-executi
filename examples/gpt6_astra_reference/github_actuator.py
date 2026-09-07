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

from .issue_contract import (
    GITHUB_ISSUE_ACTION,
    LOGICAL_OPERATION_MARKER_PREFIX,
    LOGICAL_OPERATION_MARKER_SUFFIX,
    GitHubIssuePayloadError,
    MarkerSyntaxError,
    OperationContextMismatchError,
    build_marked_payload,
    logical_operation_marker,
    require_coherent_marker_context,
    validate_github_issue_request_payload,
)

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
        if action != GITHUB_ISSUE_ACTION:
            # Defense in depth: even a governed call for an action this
            # actuator was never wired for is refused, never guessed at.
            raise GitHubActuatorDisabledError(
                f"GitHubIssueActuator does not support action {action!r}"
            )
        if not isinstance(payload, dict) or not payload.get("title"):
            raise GitHubActuatorDisabledError("payload missing required 'title'")

        import httpx

        headers = {"Accept": "application/vnd.github+json"}
        if self._config.token:
            headers["Authorization"] = f"Bearer {self._config.token}"
        async with httpx.AsyncClient(timeout=15.0) as client:
            # Round 21: send the EXACT validated payload this actuator was
            # called with -- no field projection/reconstruction. Reaching
            # this point already guarantees (via the strict request schema
            # validated at proposal-preparation time, before this call was
            # ever armed/verified) that the payload carries only the keys
            # GitHub's issue-creation endpoint understands; this actuator
            # itself no longer decides which fields survive the trip. A
            # defensive ``dict(...)`` copy only, never a reconstruction from
            # named fields, so an authorized field can never silently
            # disappear between what was verified and what is serialized.
            resp = await client.post(
                f"{self._config.base_url}/repos/{self._config.repo}/issues",
                headers=headers, json=dict(payload),
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


class PayloadBindingError(Exception):
    """Raised by :class:`VerifiedFinalPayloadActuator`/:class:`VerifiedDispatchSlot`,
    BEFORE any external call, when the action/payload about to be sent does
    not exactly match the action/payload_hash a call was verified/
    authorized to send -- or when no verified call is currently armed at
    all. This is the final-boundary proof (Round 19/21 requirement 1) that
    the exact outbound payload is cryptographically bound to a real
    verified authorization, checked immediately before the real HTTP POST,
    never a value derived from the payload this very check is about to
    evaluate."""


class VerifiedFinalPayloadActuator:
    """The final safety net immediately before the real HTTP call. Wraps an
    upstream ``async def (action, payload)`` callable (typically a
    :class:`ResourceBoundActuator` wrapping the real
    :class:`GitHubIssueActuator`) and is bound, AT CONSTRUCTION, to EXACTLY
    the one action/payload_hash it may ever forward.

    Round 21: this is now deliberately IMMUTABLE and single-shot -- there is
    no ``.expect(...)`` mutator, and no settable property, on this object at
    all. A given instance may be awaited (``__call__``ed) AT MOST ONCE: a
    second attempt raises :class:`PayloadBindingError` before touching the
    wrapped actuator, exactly like a mismatch does. This closes the Round 20
    counterexample where a single shared, RE-ARMABLE verifier could be left
    holding a stale, never-consumed expectation from an attempt that was
    blocked before ever reaching the actuator -- there is no shared mutable
    slot here for a later, unrelated call to accidentally inherit, because
    every governed call gets its OWN, independently-bound instance (see
    :class:`VerifiedDispatchSlot`, which installs a fresh one per call).

    The action/payload_hash bound at construction should come from the real
    verified authorization -- for the two-step
    ``issue_authority``/``enforce_authority`` path, the actual signed
    ``issued.token["action"]``/``issued.token["payload_hash"]``; for the
    one-step ``run_positive_path`` convenience path (where no token exists
    yet at call time), the exact canonical payload about to be submitted,
    hashed with the SAME ``hash_payload`` the real ``ExecutionGate`` uses.
    Either way this is never a value derived from the payload AFTER this
    check runs."""

    def __init__(self, actuator: Any, *, action: str, payload_hash: str) -> None:
        self._actuator = actuator
        self._action = action
        self._payload_hash = payload_hash
        self._consumed = False

    async def __call__(self, action: str, payload: Dict[str, Any]) -> Any:
        if self._consumed:
            raise PayloadBindingError(
                "this verified call has already been used once; refusing reuse -- "
                "each governed call is bound to its own, independently-constructed "
                "verifier, never a shared, re-armable one"
            )
        self._consumed = True
        if action != self._action:
            raise PayloadBindingError(
                f"action {action!r} about to be sent does not match the verified "
                f"authorized action {self._action!r}; refusing before any "
                "external call"
            )
        actual_hash = hash_payload(payload)
        if actual_hash != self._payload_hash:
            raise PayloadBindingError(
                f"the exact payload about to be sent hashes to {actual_hash!r}, which "
                f"does not match the verified authorized payload_hash "
                f"{self._payload_hash!r}; refusing before any external call"
            )
        return await self._actuator(action, payload)


class VerifiedDispatchSlot:
    """The invocation-local dispatch point every governed call routes
    through a real GitHub actuator via. Wraps a raw
    :class:`GitHubIssueActuator` in a :class:`ResourceBoundActuator`
    (config-only/stable -- constructed exactly once here, safe to share)
    and holds AT MOST ONE currently-armed, single-shot,
    :class:`VerifiedFinalPayloadActuator` at a time.

    ``expect(action=, payload_hash=)`` REPLACES whatever verifier was
    previously installed -- it never mutates an existing one (there is
    nothing on :class:`VerifiedFinalPayloadActuator` to mutate; each is
    immutable once constructed). Round 21 requirement 2: no persistent
    mutable operation identity survives from one governed call into a
    later, unrelated one. Whatever was installed (and never consumed --
    e.g. an attempt that was blocked before ever reaching this slot) before
    a NEW ``expect(...)`` call is simply discarded and can never be
    dispatched to again; ``__call__`` also clears the slot as the very
    first thing it does, so a caller that forgets to (re-)arm before a call
    that reaches this slot fails closed with :class:`PayloadBindingError`
    -- either because nothing at all is installed, or because whatever
    remains installed was bound to a DIFFERENT action/payload and the
    mismatch is caught exactly as for any other tamper. A shared instance
    of this slot is therefore safe to reuse across independent governed
    calls: the security-critical verification state is always
    invocation-local, never a value one call's preparation leaves lying
    around for a different call to silently benefit from."""

    def __init__(self, actuator: "GitHubIssueActuator", *, authorized_resource: str) -> None:
        self._bound = ResourceBoundActuator(actuator, authorized_resource=authorized_resource)
        self._current: Optional[VerifiedFinalPayloadActuator] = None

    def expect(self, *, action: str, payload_hash: str) -> None:
        self._current = VerifiedFinalPayloadActuator(self._bound, action=action, payload_hash=payload_hash)

    async def __call__(self, action: str, payload: Dict[str, Any]) -> Any:
        verifier = self._current
        self._current = None  # never reachable again after this dispatch attempt
        if verifier is None:
            raise PayloadBindingError(
                "no verified call is currently armed for this slot -- refusing before "
                "any external call; nothing was armed, or whatever was armed has "
                "already been used or replaced by a later call's own arming"
            )
        return await verifier(action, payload)


__all__ = [
    "GitHubActuatorConfig", "GitHubActuatorConfigError", "GitHubActuatorDisabledError",
    "GitHubIssueActuator", "ResourceBindingError", "ResourceBoundActuator",
    "GITHUB_ISSUE_ACTION", "LOGICAL_OPERATION_MARKER_PREFIX", "LOGICAL_OPERATION_MARKER_SUFFIX",
    "logical_operation_marker", "build_marked_payload", "GitHubIssuePayloadError",
    "validate_github_issue_request_payload", "MarkerSyntaxError", "OperationContextMismatchError",
    "require_coherent_marker_context", "PayloadBindingError",
    "VerifiedFinalPayloadActuator", "VerifiedDispatchSlot", "DISABLED", "LIVE",
]
