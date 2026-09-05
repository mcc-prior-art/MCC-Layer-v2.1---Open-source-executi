"""The Intelligence layer: GPT-6 Astra (or any OpenAI-compatible model) as a
pure proposal source.

Both providers below implement the SAME narrow interface -- ``propose(task)
-> AstraOutcome`` -- and neither one has, or can reach, anything MCC would
treat as trusted evidence or authority: no signing key, no attestation
material, no reference to ``mcc_core``/``mcc_attestation``/
``mcc_attester_service`` at all. See
``tests/test_gpt6_astra_reference_architecture_guards.py`` for the static
proof.

* ``OpenAIAstraProvider`` -- the REAL adapter. Calls the configured OpenAI
  Chat Completions endpoint over HTTPS. Requires ``OPENAI_API_KEY``
  (never embedded, never logged) and ``OPENAI_MODEL`` (no model identifier
  is hardcoded here -- an operator running this against a live GPT-6 Astra
  deployment sets ``OPENAI_MODEL`` to whatever the current, verified model
  identifier actually is on their account).
* ``DeterministicAstraProvider`` -- the reference/offline provider this
  repo's own demo, tests, and CI default to. Canned, task-keyed responses
  only; explicitly labeled ``is_live=False`` on every outcome it produces,
  exactly mirroring ``mcc_attester_service.provider.DeterministicTestProvider``'s
  own "reference/test harness, never a production source" framing.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any, Dict, Mapping, Optional, Protocol

from .models import AstraError, AstraOutcome, AstraSelfRefusal, parse_proposals


@dataclass(frozen=True)
class AstraResponse:
    """Wraps whatever :meth:`AstraProvider.propose` returns with the
    provenance the demo's evidence trail needs: was this a live model call
    or a labeled offline fixture, and (for a live call) which model."""

    outcome: AstraOutcome
    is_live: bool
    model: Optional[str] = None
    raw_note: Optional[str] = None


class AstraProvider(Protocol):
    async def propose(self, task: str) -> AstraResponse: ...


class AstraProviderError(Exception):
    """Configuration or transport failure building/using an AstraProvider."""


_SYSTEM_PROMPT = (
    "You propose exactly one action for an execution-governance system to "
    "evaluate. You do not have authority to execute anything yourself. "
    "Respond with ONLY a JSON object (or a JSON array of objects, if you "
    "believe more than one action is warranted) of the shape "
    '{"action": string, "resource": string, "payload": object, '
    '"reason": string (optional)}. Never include any field other than '
    "action, resource, payload, reason. If you decline to propose the "
    'requested action, respond with {"self_refusal": "<why>"} instead.'
)


class OpenAIAstraProvider:
    """Real adapter: calls the configured OpenAI-compatible Chat Completions
    endpoint. Provider-neutral -- ``OPENAI_BASE_URL`` may point this at any
    OpenAI-API-compatible endpoint a live GPT-6 Astra deployment exposes."""

    def __init__(self, *, api_key: str, model: str, base_url: str = "https://api.openai.com/v1",
                 timeout_seconds: float = 30.0) -> None:
        if not api_key:
            raise AstraProviderError("OPENAI_API_KEY is required")
        if not model:
            raise AstraProviderError("OPENAI_MODEL is required")
        self._api_key = api_key
        self._model = model
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout_seconds

    @classmethod
    def from_env(cls, env: Optional[Mapping[str, str]] = None) -> "OpenAIAstraProvider":
        env = os.environ if env is None else env
        api_key = env.get("OPENAI_API_KEY", "").strip()
        model = env.get("OPENAI_MODEL", "").strip()
        base_url = env.get("OPENAI_BASE_URL", "https://api.openai.com/v1").strip()
        if not api_key:
            raise AstraProviderError(
                "OPENAI_API_KEY is required for a live Astra run -- refusing to "
                "silently fall back to any default provider"
            )
        if not model:
            raise AstraProviderError(
                "OPENAI_MODEL is required for a live Astra run -- this adapter never "
                "hardcodes a model identifier; set it to the current, verified model "
                "identifier on your account (e.g. the current Astra model id)"
            )
        return cls(api_key=api_key, model=model, base_url=base_url)

    async def propose(self, task: str) -> AstraResponse:
        import httpx

        body = {
            "model": self._model,
            "messages": [
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": task},
            ],
            "response_format": {"type": "json_object"},
        }
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                resp = await client.post(
                    f"{self._base_url}/chat/completions",
                    headers={"Authorization": f"Bearer {self._api_key}"},
                    json=body,
                )
                resp.raise_for_status()
                data = resp.json()
        except Exception as exc:  # noqa: BLE001 -- any transport failure fails closed
            return AstraResponse(
                outcome=AstraError(f"OpenAI request failed: {exc!r}"),
                is_live=True, model=self._model,
            )

        try:
            content = data["choices"][0]["message"]["content"]
            parsed = json.loads(content)
        except Exception as exc:  # noqa: BLE001
            return AstraResponse(
                outcome=AstraError(f"model response was not valid JSON: {exc!r}"),
                is_live=True, model=self._model,
            )

        if isinstance(parsed, dict) and "self_refusal" in parsed and len(parsed) == 1:
            return AstraResponse(
                outcome=AstraSelfRefusal(str(parsed["self_refusal"])),
                is_live=True, model=self._model,
            )

        try:
            proposals = parse_proposals(parsed)
        except Exception as exc:  # noqa: BLE001 -- malformed/forbidden model output fails closed
            return AstraResponse(outcome=AstraError(str(exc)), is_live=True, model=self._model)

        return AstraResponse(outcome=proposals, is_live=True, model=self._model)


class DeterministicAstraProvider:
    """Reference/offline provider. Canned task -> RAW-model-output table,
    explicitly labeled non-live on every response. This is what the demo
    runner, and every test in this package, use by default -- no OpenAI
    credentials are ever required to exercise the full MCC chain end to
    end.

    Each table entry is exactly what a live model's response content would
    have been: a JSON-shaped ``dict``/``list`` (one proposal, or several --
    see Scenario F), or an :class:`AstraSelfRefusal`. Proposal entries are
    run through the IDENTICAL strict parser (:func:`parse_proposals`) the
    live :class:`OpenAIAstraProvider` uses, so a malformed or
    forbidden-field fixture fails exactly the same way a malformed live
    model response would -- this double never gets an easier path through
    validation than the real adapter."""

    def __init__(self, table: Dict[str, Any]) -> None:
        self._table = dict(table)

    async def propose(self, task: str) -> AstraResponse:
        note = "DeterministicAstraProvider (reference/offline fixture)"
        if task not in self._table:
            return AstraResponse(outcome=AstraError(f"no fixture configured for task {task!r}"),
                                 is_live=False, raw_note=note)
        raw = self._table[task]
        if isinstance(raw, AstraSelfRefusal):
            return AstraResponse(outcome=raw, is_live=False, raw_note=note)
        if isinstance(raw, AstraError):
            return AstraResponse(outcome=raw, is_live=False, raw_note=note)
        try:
            proposals = parse_proposals(raw)
        except Exception as exc:  # noqa: BLE001 -- malformed fixture fails closed, same as a live model
            return AstraResponse(outcome=AstraError(str(exc)), is_live=False, raw_note=note)
        return AstraResponse(outcome=proposals, is_live=False, raw_note=note)


__all__ = [
    "AstraProvider", "AstraProviderError", "AstraResponse",
    "OpenAIAstraProvider", "DeterministicAstraProvider",
]
