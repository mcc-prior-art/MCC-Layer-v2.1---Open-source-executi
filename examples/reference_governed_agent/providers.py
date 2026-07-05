"""Reasoning providers: turn a natural-language request into a proposed action.

A provider is the agent's *reasoning* — and reasoning is never authority. A
provider only decides **what to propose**; MCC-Core decides whether it may run.
Two providers ship:

* :class:`DeterministicProvider` — the default. No external API, no key, no
  network, no nondeterminism. Used by every test, the default demo, CI, and the
  Docker E2E so the pipeline is reproducible offline.
* :class:`OptionalLLMProvider` — an opt-in extension point (env-configured) for
  wiring a real LLM. It carries **no mandatory external dependency**, and a
  provider failure raises :class:`ProviderError` — it can never bypass
  governance: with no proposal there is simply nothing to submit.

Neither provider signs anything, calls the gateway, or touches the notification
service. They emit intent only.
"""

from __future__ import annotations

import os
from typing import Callable, Optional, Protocol, runtime_checkable

from .actions import ACTION, RESOURCE, build_notification_payload, parse_request
from .models import ProposedAction, ProviderError

# The default actor the reference agent proposes as. It maps to the pilot
# ``notify.send`` mandate (agent/notify-bot) so the deterministic scenarios are
# reproducible; a different actor holds no mandate -> ESCALATE.
DEFAULT_ACTOR = "agent/notify-bot"


@runtime_checkable
class ReasoningProvider(Protocol):
    """Produce a structured :class:`ProposedAction` from a NL request.

    The proposal is intent, not permission. A provider must never execute, call
    the gateway, or reach an external system — it only proposes."""

    def propose(self, request: str) -> ProposedAction: ...


class DeterministicProvider:
    """Default provider: a fixed, auditable request -> proposal mapping.

    Requires no API key, no network, and no external service. Given the same
    request it always produces the same proposal, which is what makes the tests,
    the CI, and the Docker E2E reproducible.

    Priority / channel / actor may be pinned to steer the four verdict flows in
    demos; when unset they are parsed from the request (defaulting to a
    within-policy proposal that ALLOWs)."""

    def __init__(
        self,
        *,
        actor_id: str = DEFAULT_ACTOR,
        priority: str = "normal",
        channel: str = "email",
    ) -> None:
        self._actor_id = actor_id
        self._priority = priority
        self._channel = channel

    def propose(self, request: str) -> ProposedAction:
        if not request or not request.strip():
            raise ProviderError("empty request: nothing to propose")
        parsed = parse_request(request)
        payload = build_notification_payload(
            recipient=parsed["recipient"],
            message=parsed["message"],
            priority=self._priority,
            channel=self._channel,
        )
        return ProposedAction(
            action=ACTION, actor_id=self._actor_id, resource=RESOURCE, payload=payload
        )


class OptionalLLMProvider:
    """Opt-in LLM-backed provider (extension point).

    Enabled only when ``MCC_AGENT_LLM=1`` (or an explicit ``enabled=True``). It
    deliberately ships **no** hard dependency on any LLM client: the actual model
    call is injected as a ``complete`` callable so the reference agent has no
    required external dependency and CI stays offline. If the model is not
    configured or the call fails, it raises :class:`ProviderError` — the agent
    then has no proposal to submit. A provider failure NEVER results in an
    ungoverned action: reasoning cannot bypass MCC-Core.

    The callable is only trusted to shape *intent* (recipient/message). The
    resulting proposal still goes through the gateway like any other — the LLM's
    output is not authority.
    """

    def __init__(
        self,
        *,
        enabled: Optional[bool] = None,
        complete: Optional[Callable[[str], str]] = None,
        actor_id: str = DEFAULT_ACTOR,
        fallback: Optional[ReasoningProvider] = None,
    ) -> None:
        self._enabled = (
            enabled if enabled is not None else os.environ.get("MCC_AGENT_LLM") == "1"
        )
        self._complete = complete
        self._actor_id = actor_id
        # A deterministic fallback is NOT a governance bypass — it is just a
        # different (still-governed) source of intent. Off by default so a
        # misconfigured LLM surfaces loudly rather than silently degrading.
        self._fallback = fallback

    def propose(self, request: str) -> ProposedAction:
        if not self._enabled:
            raise ProviderError(
                "OptionalLLMProvider is not enabled (set MCC_AGENT_LLM=1 and inject a model)"
            )
        if self._complete is None:
            if self._fallback is not None:
                return self._fallback.propose(request)
            raise ProviderError(
                "OptionalLLMProvider has no model callable configured; cannot propose"
            )
        try:
            text = self._complete(request)
        except Exception as exc:  # noqa: BLE001 - any model failure -> no proposal
            raise ProviderError(f"LLM provider failed: {type(exc).__name__}: {exc}") from exc
        if not isinstance(text, str) or not text.strip():
            raise ProviderError("LLM provider returned no usable text")
        parsed = parse_request(text)
        payload = build_notification_payload(
            recipient=parsed["recipient"], message=parsed["message"]
        )
        return ProposedAction(
            action=ACTION, actor_id=self._actor_id, resource=RESOURCE, payload=payload
        )


__all__ = [
    "ReasoningProvider",
    "DeterministicProvider",
    "OptionalLLMProvider",
    "DEFAULT_ACTOR",
]
