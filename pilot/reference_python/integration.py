"""The reference pilot integration.

    candidate action
      -> mcc_sdk.MCCClient.evaluate()   (POST /evaluate on the real Gateway)
      -> decision validation             (mcc_sdk itself: fails closed on
                                           malformed/unknown-verdict responses)
      -> pilot-side mode gate            (observe: never actuates; enforced:
                                           only ALLOW/CONSTRAIN may actuate)
      -> SimulatedActuator               (local only; see actuator.py)

No governance logic is duplicated here: this module never decides ALLOW,
DENY, ESCALATE, or CONSTRAIN -- it only reacts to what the real Gateway,
through the real official SDK, already decided. No retries are added at
this layer either (``mcc_sdk.MCCClient`` already makes exactly one attempt
per call).
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Any

from mcc_sdk import (
    EvaluateRequest,
    EvaluateResponse,
    MCCContractError,
    MCCGatewayError,
    MCCSDKError,
    MCCTimeoutError,
    MCCTransportError,
    Verdict,
)
from mcc_sdk.client import MCCClient

from .actuator import SimulatedActuator, SimulatedReceipt
from .config import PilotConfig
from .evidence import PilotEvidenceCollector


@dataclass(frozen=True)
class PilotOutcome:
    """The result of submitting one candidate action through the pilot."""

    decision: EvaluateResponse
    receipt: SimulatedReceipt | None
    actuated: bool


class PilotIntegration:
    """Orchestrates one pilot run: submit candidate actions, react to the
    real Gateway's decisions, and collect evidence. Owns (and must close)
    its :class:`~mcc_sdk.MCCClient` unless one is injected for testing."""

    def __init__(
        self,
        config: PilotConfig,
        *,
        client: MCCClient | None = None,
        actuator: SimulatedActuator | None = None,
        evidence: PilotEvidenceCollector | None = None,
    ) -> None:
        self.config = config
        self._owns_client = client is None
        self.client = client or MCCClient(
            base_url=config.gateway_url, timeout=config.timeout_seconds, api_key=config.api_key,
        )
        self.actuator = actuator or SimulatedActuator()
        self.evidence = evidence or PilotEvidenceCollector(config=config)

    def submit(
        self,
        *,
        identity: str,
        action: str,
        context: dict[str, Any] | None = None,
        actor_id: str | None = None,
        resource_id: str | None = None,
    ) -> PilotOutcome:
        """Submit one candidate action. Fails closed (raises) on transport
        failure, timeout, or any response ``mcc_sdk`` cannot validate --
        never returns a fabricated outcome."""
        run_op_id = f"{self.config.run_correlation_id}-{uuid.uuid4().hex[:8]}"
        gateway_mode = "inline" if self.config.mode == "enforced" else "observe"
        request = EvaluateRequest(
            identity=identity, action=action, context=context or {},
            actor_id=actor_id, resource_id=resource_id,
            transaction_id=run_op_id, idempotency_key=run_op_id, mode=gateway_mode,
        )

        try:
            decision = self.client.evaluate(request)
        except MCCTimeoutError:
            self.evidence.record_timeout()
            raise
        except MCCTransportError:
            self.evidence.record_unavailable()
            raise
        except MCCContractError:
            self.evidence.record_malformed()
            raise
        except MCCGatewayError:
            self.evidence.record_malformed()
            raise
        except MCCSDKError:
            self.evidence.record_malformed()
            raise

        self.evidence.record_decision(
            action=action, decision=decision.decision.value,
            audit_id=decision.audit_id, trace_id=decision.trace_id,
        )

        if self.config.mode == "observe":
            # Observe mode NEVER actuates, regardless of the verdict -- it
            # only records what would have happened.
            receipt = self.actuator.observe(
                action=action, actor_id=actor_id or identity,
                payload=decision.forward_context, decision=decision,
            )
            return PilotOutcome(decision=decision, receipt=receipt, actuated=False)

        # Enforced mode: only ALLOW/CONSTRAIN may reach the (simulated)
        # actuator, and only with the Gateway's own forward_context -- see
        # SimulatedActuator.execute for the payload-binding enforcement.
        if decision.decision in (Verdict.ALLOW, Verdict.CONSTRAIN):
            receipt = self.actuator.execute(action=action, actor_id=actor_id or identity, decision=decision)
            self.evidence.record_executed()
            return PilotOutcome(decision=decision, receipt=receipt, actuated=True)

        return PilotOutcome(decision=decision, receipt=None, actuated=False)

    # -- lifecycle --

    def close(self) -> None:
        if self._owns_client:
            self.client.close()

    def __enter__(self) -> PilotIntegration:  # noqa: PYI034 -- avoid a typing_extensions dep for py3.9
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.close()


__all__ = ["PilotIntegration", "PilotOutcome"]
