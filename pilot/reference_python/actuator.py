"""The pilot's ONLY side effect: a local, simulated actuator.

There is no production actuator here and none is added by this PR. The
actuator never makes a network call, never touches a real external system,
and never runs without a genuine, payload-bound ALLOW/CONSTRAIN decision
from the real Gateway -- see :meth:`SimulatedActuator.execute`.

This is the structural enforcement of "no direct execution path around the
gate": there is no public method on this class that performs the simulated
action without a verified :class:`mcc_sdk.EvaluateResponse` bound to the
exact payload being acted on. A caller cannot construct a bypass by hand --
``mcc_sdk.EvaluateResponse`` is a Pydantic model this module does not
control the construction rules of (identity/action/decision are validated
by ``mcc_sdk`` itself), and this module additionally re-checks the verdict
and payload binding independently before recording anything as executed.
"""

from __future__ import annotations

import copy
from dataclasses import dataclass, field
from typing import Any

from mcc_sdk import EvaluateResponse, Verdict


class DirectActuationRejected(Exception):
    """Raised when the actuator is asked to act without a valid,
    payload-bound permitting decision. This is the pilot's own bypass guard,
    independent of (and in addition to) the Execution Gate the real Gateway
    already enforces server-side."""


@dataclass(frozen=True)
class SimulatedReceipt:
    """What the simulated actuator "did" -- recorded locally, never sent
    anywhere. Mirrors the shape of a real actuator receipt (see
    ``pilot_notify``/``clinic_service``) without any real side effect."""

    executed: bool
    action: str
    actor_id: str | None
    payload: dict[str, Any]
    audit_id: str
    trace_id: str
    note: str


@dataclass
class SimulatedActuator:
    """A local, in-memory, side-effect-free stand-in for a real actuator.
    Records every attempt (observed and executed) for evidence collection;
    performs no I/O of any kind."""

    _log: list[SimulatedReceipt] = field(default_factory=list)

    @property
    def log(self) -> list[SimulatedReceipt]:
        return list(self._log)

    def observe(self, *, action: str, actor_id: str | None, payload: dict[str, Any],
                decision: EvaluateResponse) -> SimulatedReceipt:
        """Record what WOULD have happened, without performing it. Used in
        observe mode regardless of the verdict -- observe mode never
        actuates, by design."""
        receipt = SimulatedReceipt(
            executed=False, action=action, actor_id=actor_id, payload=dict(payload),
            audit_id=decision.audit_id, trace_id=decision.trace_id,
            note=f"observed only (mode=observe); decision={decision.decision.value}",
        )
        self._log.append(receipt)
        return receipt

    def execute(self, *, action: str, actor_id: str | None,
                decision: EvaluateResponse) -> SimulatedReceipt:
        """Perform the simulated action -- ENFORCED mode only, and only for
        a decision that actually permits it.

        Fails closed (raises :class:`DirectActuationRejected`) unless:
        * ``decision.decision`` is ALLOW or CONSTRAIN (never DENY/ESCALATE);
        * the payload acted on is EXACTLY ``decision.forward_context`` -- the
          caller cannot substitute a different payload than the one the
          Gateway actually authorized (this is what makes a CONSTRAIN
          decision unable to actuate outside its own returned constraints:
          there is no argument here for "the original payload").
        """
        if decision.decision not in (Verdict.ALLOW, Verdict.CONSTRAIN):
            raise DirectActuationRejected(
                f"refusing to actuate: decision is {decision.decision.value}, "
                "not ALLOW/CONSTRAIN"
            )
        if decision.decision_token is None:
            raise DirectActuationRejected(
                "refusing to actuate: decision carries no decision_token"
            )
        # The ONLY payload this actuator will ever act on is the Gateway's
        # own forward_context -- never a caller-supplied alternative.
        payload = copy.deepcopy(decision.forward_context)
        receipt = SimulatedReceipt(
            executed=True, action=action, actor_id=actor_id, payload=payload,
            audit_id=decision.audit_id, trace_id=decision.trace_id,
            note=f"simulated execution only; decision={decision.decision.value}",
        )
        self._log.append(receipt)
        return receipt


__all__ = ["DirectActuationRejected", "SimulatedActuator", "SimulatedReceipt"]
