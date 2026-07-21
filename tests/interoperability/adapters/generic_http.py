"""Generic HTTP interoperability adapter (PR #48, adapter 5/5).

The framework-neutral integration: it originates a canonical Integration Contract
proposal with no agent framework at all, and submits it over a **real HTTP transport
boundary** (real ``httpx`` client → the shared out-of-process Gateway's bound
loopback endpoint). It never invokes a route handler, ASGI transport, or service
object directly, and it never authorizes, executes, verifies, or mints decisions.

Classification: FRAMEWORK-NEUTRAL HTTP INTEGRATION.
"""

from __future__ import annotations

import uuid
from typing import Any, Dict, Optional

from mcc_compliance.capability_profile import BASELINE_CAPABILITIES

from tests.interoperability.harness import CONTRACT_VERSION, CanonicalProposal

ACTOR = "agent/notify-bot"
RESOURCE = "notifications"
ACTION = "send_notification"


class GenericHttpAdapter:
    adapter_name = "generic-http"
    adapter_classification = "FRAMEWORK-NEUTRAL HTTP INTEGRATION"
    framework_name = "none"
    framework_distribution: Optional[str] = None
    framework_version: Optional[str] = None
    native_object_type: Optional[str] = None
    native_api_entrypoint = "httpx.Client -> POST {gateway}/evaluate + /consensus/*"
    adapter_module = "tests.interoperability.adapters.generic_http"
    adapter_version = "1.0.0"

    def framework_provenance(self) -> Dict[str, Any]:
        return {
            "classification": self.adapter_classification,
            "framework_name": self.framework_name,
            "framework_distribution": self.framework_distribution,
            "framework_version": self.framework_version,
            "native_object_type": self.native_object_type,
            "native_api_entrypoint": self.native_api_entrypoint,
            "transport": "real HTTP over loopback TCP via an httpx client to an "
                         "out-of-process gateway server",
            "adapter_module": self.adapter_module,
            "adapter_version": self.adapter_version,
        }

    def capability_profile(self) -> Dict[str, Any]:
        return {
            "profile_version": "1",
            "adapter": {"name": self.adapter_name, "version": self.adapter_version,
                        "implementation_id": self.adapter_module, "framework": None},
            "integration_contract": {"version": CONTRACT_VERSION},
            "compliance": {"suite_version": "1.0.0", "vector_set_version": "1"},
            "certification": {"claimed_status": "SELF_DECLARED", "evidence_digest": None},
            "runtime_capabilities": list(BASELINE_CAPABILITIES),
            "optional_capabilities": ["tamper_evident_audit_evidence"],
            "unsupported_capabilities": [],
            "constraints": {},
            "metadata": {"note": "Framework-neutral HTTP integration."},
        }

    def _payload(self, *, channel: str = "email") -> Dict[str, Any]:
        return {"recipient": "customer-123", "message": "appointment confirmed",
                "priority": 2, "channel": channel,
                "correlation_id": f"generic-http-{uuid.uuid4().hex[:12]}"}

    def proposal_for(self, scenario: str) -> CanonicalProposal:
        # No framework: the canonical proposal is built directly. DENY uses a
        # channel the shared policy rejects; all other scenarios use an allowed one.
        channel = "pager" if scenario == "DENY" else "email"
        return CanonicalProposal(actor_id=ACTOR, action=ACTION, resource=RESOURCE,
                                 payload=self._payload(channel=channel))


__all__ = ["GenericHttpAdapter"]
