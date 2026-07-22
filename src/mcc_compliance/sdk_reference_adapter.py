"""Reference Adapter-SDK certification adapter (PR #51).

The canonical adapter the Compliance & Certification Suite exercises **through the
Adapter SDK** (PR #50). It is a reference/fixture — NOT a new framework integration
— that expresses the proven four-verdict reference behaviour as an
:class:`mcc_adapter_sdk.Adapter`: it translates a compliance scenario into the same
``send_notification`` :class:`~mcc_protocol.CanonicalProposal` the reference governed
agent produces (reusing the exact payload builder, so verdicts match), and translates
the returned :class:`~mcc_protocol.GovernanceDecision` back to a native response.

It is purely translational (the Adapter SDK contract): it never authorizes,
executes, evaluates policy, or signs. The governed execution + gate + audit remain
MCC-Core's, driven by the certification harness.
"""

from __future__ import annotations

from typing import Any, Dict

import mcc_protocol as mp
from mcc_adapter_sdk import Adapter, AdapterContext, AdapterMetadata
from mcc_compliance.capability_profile import BASELINE_CAPABILITIES

from examples.reference_governed_agent.actions import (
    ACTION,
    RESOURCE,
    build_notification_payload,
    parse_request,
)


class SdkReferenceAdapter(Adapter):
    """Reference Adapter-SDK integration used to certify the SDK ingress path."""

    adapter_id = "sdk-reference"

    def describe(self) -> AdapterMetadata:
        return AdapterMetadata.create(
            adapter_id=self.adapter_id, adapter_version="1.0.0",
            framework_name="none", capabilities=(BASELINE_CAPABILITIES[0],),
            supported_input_modes=("scenario",), supported_output_modes=("json",),
            vendor="AXLOGIQ", maintainer="mcc-core",
            source_url="https://github.com/mcc-prior-art/mcc-layer")

    def to_proposal(self, context: AdapterContext, native_request: Any) -> mp.CanonicalProposal:
        # The compliance harness hands {"request": <str>, "params": <driver config>}.
        # A malformed (empty) request yields no action — fail closed, nothing proposes.
        request = ""
        params: Dict[str, Any] = {}
        if isinstance(native_request, dict):
            request = str(native_request.get("request", ""))
            params = dict(native_request.get("params", {}))
        else:
            request = str(native_request)
        if not request.strip():
            raise ValueError("malformed request: no action to propose")
        parsed = parse_request(request)
        payload = build_notification_payload(
            recipient=parsed["recipient"], message=parsed["message"],
            priority=params.get("priority", "normal"), channel=params.get("channel", "email"))
        # The intent's actor (steers the four verdicts) rides on the context.
        return self.make_proposal(context, action=ACTION, resource=RESOURCE, payload=payload)

    def to_response(self, decision: mp.GovernanceDecision) -> Any:
        return {"verdict": decision.verdict.value, "executable": decision.executable,
                "reason_codes": list(decision.reason_codes)}

    def sample_request(self) -> Any:
        return {"request": "Notify customer-123 that the appointment is confirmed",
                "params": {"actor_id": "agent/notify-bot", "priority": "normal",
                           "channel": "email"}}


__all__ = ["SdkReferenceAdapter"]
