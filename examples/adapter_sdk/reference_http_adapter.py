"""Reference migration: the framework-neutral HTTP adapter on the Adapter SDK (PR #50).

This is the ONE existing adapter migrated to the public Adapter SDK surface. The PR
#48 interoperability suite already ships a framework-neutral ``GenericHttpAdapter``
(the smallest, framework-neutral integration) that originates a canonical
``send_notification`` proposal and submits it over real HTTP to the shared Gateway.
Here the same behaviour is expressed through the public :class:`Adapter` interface:
it translates a native request into a :class:`mcc_protocol.CanonicalProposal` with the
**identical** stable payload (recipient / message / priority / channel), traverses the
mandatory :class:`mcc_protocol.CanonicalIngressPipeline` via :class:`AdapterRunner`,
and translates the returned :class:`mcc_protocol.GovernanceDecision` back to a native
response. It authorizes nothing and executes nothing.

The migration preserves behaviour (same proposal content, same verdicts) and the
existing interoperability evidence is untouched — it only *adds* the SDK expression.
"""

from __future__ import annotations

from typing import Any, Dict

import mcc_protocol as mp
from mcc_adapter_sdk import Adapter, AdapterContext, AdapterMetadata
from mcc_compliance.capability_profile import BASELINE_CAPABILITIES

# The same stable identity + content the PR #48 GenericHttpAdapter uses.
ACTOR = "agent/notify-bot"
RESOURCE = "notifications"
ACTION = "send_notification"


class ReferenceHttpAdapter(Adapter):
    """Framework-neutral HTTP integration, expressed on the Adapter SDK."""

    adapter_id = "reference-http"

    def describe(self) -> AdapterMetadata:
        return AdapterMetadata.create(
            adapter_id=self.adapter_id, adapter_version="1.0.0", framework_name="none",
            capabilities=(BASELINE_CAPABILITIES[0],),
            supported_input_modes=("scenario",), supported_output_modes=("json",),
            vendor="AXLOGIQ", maintainer="mcc-core",
            source_url="https://github.com/mcc-prior-art/mcc-layer")

    def _payload(self, channel: str) -> Dict[str, Any]:
        # Identical stable content to the interop GenericHttpAdapter.
        return {"recipient": "customer-123", "message": "appointment confirmed",
                "priority": 2, "channel": channel}

    def to_proposal(self, context: AdapterContext, native_request: Any) -> mp.CanonicalProposal:
        # native_request is a scenario name; DENY drives the channel the policy rejects.
        scenario = str(native_request).upper()
        channel = "pager" if scenario == "DENY" else "email"
        return self.make_proposal(context, action=ACTION, resource=RESOURCE,
                                  payload=self._payload(channel))

    def to_response(self, decision: mp.GovernanceDecision) -> Any:
        return {"verdict": decision.verdict.value, "executable": decision.executable,
                "reason_codes": list(decision.reason_codes)}

    def sample_request(self) -> Any:
        return "ALLOW"


__all__ = ["ReferenceHttpAdapter", "ACTOR", "RESOURCE", "ACTION"]
