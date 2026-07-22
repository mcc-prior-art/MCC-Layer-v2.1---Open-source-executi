"""Minimal MCC-Core Adapter SDK example (PR #50).

A third-party-style adapter built using ONLY the public Adapter SDK. It demonstrates
the full, framework-neutral lifecycle:

    native request → CanonicalProposal → CanonicalIngressPipeline → GovernanceDecision
    → native response → structural validation → deterministic evidence

The adapter is purely translational: it never authorizes, executes, evaluates policy,
or signs. No credentials, no execution, no external side effects. The ``router`` here
is an illustrative in-process decision source standing in for the MCC Gateway; a real
integration passes a router backed by ``mcc_client.MCCClient.evaluate``.

Run:  python examples/adapter_sdk/minimal_adapter.py
"""

from __future__ import annotations

import json
from typing import Any

import mcc_protocol as mp
from mcc_adapter_sdk import (
    Adapter,
    AdapterContext,
    AdapterMetadata,
    AdapterRunner,
    generate_adapter_evidence,
    validate_adapter,
)
from mcc_compliance.capability_profile import BASELINE_CAPABILITIES


class GreetingAdapter(Adapter):
    """Translates a plain-text greeting request into a governed notification."""

    def describe(self) -> AdapterMetadata:
        return AdapterMetadata.create(
            adapter_id="example-greeting", adapter_version="1.0.0",
            framework_name="none", capabilities=(BASELINE_CAPABILITIES[0],),
            supported_input_modes=("text",), supported_output_modes=("json",),
            vendor="Example Corp", maintainer="dev@example.com",
            documentation_url="https://example.com/docs")

    def to_proposal(self, context: AdapterContext, native_request: Any) -> mp.CanonicalProposal:
        # The framework produced `native_request`; the adapter only translates it.
        return self.make_proposal(
            context, action="send_notification", resource="notifications",
            payload={"recipient": "customer-123", "message": str(native_request),
                     "priority": 2, "channel": "email"})

    def to_response(self, decision: mp.GovernanceDecision) -> Any:
        return {"verdict": decision.verdict.value, "delivered": decision.executable,
                "reason_codes": decision.reason_codes}

    def sample_request(self) -> Any:
        return "your appointment is confirmed"


def _illustrative_router(proposal: mp.CanonicalProposal) -> mp.Decision:
    """Stands in for the MCC Gateway (in production: mcc_client.MCCClient.evaluate).
    It performs NO authorization — it only returns a canonical Decision shape so the
    example is self-contained and offline."""
    return mp.Decision.from_response(
        {"decision": "ALLOW", "reason": "example policy allows greetings",
         "audit_id": "example-audit", "forward_context": dict(proposal.payload),
         "policy_ref": "sha256:example-policy", "trace_id": proposal.trace_id,
         "decision_token": {"kid": "example-kid"}},
        requested_actor=proposal.actor, requested_action=proposal.action,
        requested_resource=proposal.resource, requested_payload=proposal.payload)


def main() -> int:
    adapter = GreetingAdapter()

    # 1. Structural validation (NOT certification).
    report = validate_adapter(adapter)
    print("validation:", report.status, "| structurally_valid:", report.structurally_valid)

    # 2. Drive a native request through the mandatory ingress path.
    runner = AdapterRunner(adapter, _illustrative_router)
    context = AdapterContext.create(actor_reference="agent/notify-bot",
                                    tenant="example", namespace="demo")
    result = runner.run(context, "your appointment is confirmed")
    print("run ok:", result.ok, "| verdict:", result.verdict,
          "| stages:", len(result.pipeline_summary.get("stages_completed", [])))
    print("native response:", json.dumps(result.native_response, sort_keys=True))

    # 3. Deterministic, sanitized SDK evidence (distinct from certification).
    evidence = generate_adapter_evidence(adapter, run_result=result,
                                         validation_report=report)
    print("evidence written:", evidence["evidence_format"],
          "digest:", evidence["adapter_metadata_digest"][:23])
    return 0 if (result.ok and report.structurally_valid) else 1


if __name__ == "__main__":
    raise SystemExit(main())
