"""The OPT-IN attestation-aware full-chain reference pilot (PR-6).

    candidate action
      -> AttesterClient.attest()          (POST /attest on a SEPARATE,
                                            independently-running Attester
                                            service process; PR-4)
      -> signed EvidenceAttestation       (mcc-attestation/1; genuine, never
                                            fabricated by this module)
      -> MCCGatewayClient.execute_with_mandate(..., attestation=...)
                                           (POST /mandates/execute on the
                                            real Gateway; PR-6 exposes the
                                            already-existing ``attestation``
                                            field this call previously had
                                            no way to populate)
      -> [server-side, unchanged]: PreExecutionControl (PR-2) verifies the
         attestation and derives evidence_digest (PR-3) -> DecisionEngine
         issues an evidence-bound token -> EnforcementCoordinator ->
         ExecutionGate re-verifies signature/binding/nonce/evidence_digest
         (PR-3) -> governed (loopback/simulated) actuator -> audit
      -> AttestationChainEvidence            (partner-safe evidence record)

No governance logic is duplicated here, and none of PR-1 through PR-5's
components are reimplemented, wrapped, or bypassed: this module is a thin
orchestrator over two existing, unmodified HTTP surfaces (the Attester's
``/attest`` and the Gateway's ``/mandates/execute``). Every verdict, every
signature check, every replay/expiry/binding check happens exactly where it
already happened before this PR -- server-side, in the Attester and in the
real Gateway's existing PR-1/2/3 chain.

A signed ``mandate`` is a required input to :meth:`AttestationChainPilot.submit`
in enforced mode -- exactly like ``MCCGatewayClient.execute_with_mandate``
already requires one. This module never mints a mandate itself: in a real
deployment, a partner's mandate comes from their MCC operator (the existing,
documented mandate-issuance path -- see ``docs/SIGNED_MANDATES.md``), never
from pilot-integration code. The reference demo runner
(``attestation_runner.py``) mints ONE demo mandate using a clearly-labeled
local reference/demo issuer key, exactly mirroring the established
``deploy/pilot/generate_pilot_config.py`` convention -- that key management
lives in demo/operator tooling, never in this integration module.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from typing_extensions import Self

from pilot.client import ExecutionOutcome, MCCGatewayClient

from .attestation_config import AttestationChainConfig
from .attestation_evidence import AttestationChainEvidence, build_attestation_summary
from .attester_client import AttesterClient, AttesterClientError


@dataclass(frozen=True)
class AttestationChainOutcome:
    """The result of one candidate action submitted through the full-chain
    pilot. ``execution`` is ``None`` in observe mode (no execute call is
    ever made) or when the Gateway blocked the action."""

    mode: str
    attestation: dict[str, Any]
    execution: ExecutionOutcome | None
    evidence: dict[str, Any]
    evidence_path: Path | None = None

    @property
    def actuated(self) -> bool:
        return bool(self.execution and self.execution.executed)


class AttestationChainPilot:
    """Orchestrates one full-chain submission. Owns (and must close) its
    :class:`~pilot.client.MCCGatewayClient` unless one is injected for
    testing; the :class:`AttesterClient` is stateless (plain HTTP calls, no
    connection to own)."""

    def __init__(
        self,
        config: AttestationChainConfig,
        *,
        gateway_client: MCCGatewayClient | None = None,
        attester_client: AttesterClient | None = None,
        evidence_dir: str = "./artifacts/pilot-evidence",
    ) -> None:
        self.config = config
        self.evidence_dir = evidence_dir
        self._owns_gateway_client = gateway_client is None
        if gateway_client is None:
            gateway_client = MCCGatewayClient(
                config.gateway_url, api_key=config.gateway_api_key,
                timeout=config.timeout_seconds,
            )
        self.gateway_client = gateway_client
        self.attester_client = attester_client or AttesterClient(
            base_url=config.attester_url, auth_secret=config.attester_auth_secret,
            timeout_seconds=config.timeout_seconds,
        )

    def submit(
        self,
        *,
        actor: str,
        context: dict[str, Any] | None = None,
        resource: str | None = None,
        action: str | None = None,
        mandate: dict[str, Any] | None = None,
        transaction_id: str | None = None,
        idempotency_key: str | None = None,
        export_evidence: bool = False,
    ) -> AttestationChainOutcome:
        """Submit one candidate action through the full chain.

        Always obtains a genuine, signed attestation first (both modes --
        this is the "evidence generation" observe mode is required to
        exercise). In ``observe`` mode, stops there: no request is ever
        sent to ``POST /mandates/execute``, so there is structurally no way
        for this call to cause a real (or even simulated) side effect --
        this is a stronger guarantee than a server-side "dry run" flag,
        since the execute-capable HTTP call is simply never made.

        In ``enforced`` mode, requires ``mandate`` (fails closed --
        ``ValueError`` -- if omitted; this module does not silently proceed
        without one, and does not mint one itself; see the module
        docstring) and forwards the attestation to
        ``MCCGatewayClient.execute_with_mandate``, which reaches the real,
        unmodified PR-1/2/3 server-side chain."""
        action = action or self.config.action
        resource = resource if resource is not None else self.config.resource

        raw_attestation = self.attester_client.attest(
            action=action, resource=resource, payload=context or {},
        )
        attestation_summary = build_attestation_summary(raw_attestation)

        if self.config.mode == "observe":
            evidence = AttestationChainEvidence(
                config=self.config, mode="observe", action=action, resource=resource,
                attestation_summary=attestation_summary, attester_service_calls=1,
                gateway_calls=0, actuated=False,
            )
            path = evidence.finalize_and_export(self.evidence_dir) if export_evidence else None
            return AttestationChainOutcome(
                mode="observe", attestation=raw_attestation, execution=None,
                evidence=evidence.finalize(), evidence_path=path,
            )

        # enforced mode: fail closed without a mandate -- never silently
        # skip authority and never mint one on the caller's behalf.
        if mandate is None:
            raise ValueError(
                "enforced mode requires a signed mandate (this module never "
                "mints one itself); see docs/PILOT_RUNBOOK.md §19 and "
                "docs/SIGNED_MANDATES.md for how a partner obtains one"
            )

        execution = self.gateway_client.execute_with_mandate(
            mandate=mandate, actor=actor, action=action, resource=resource,
            context=context or {}, transaction_id=transaction_id,
            idempotency_key=idempotency_key, attestation=raw_attestation,
        )

        evidence = AttestationChainEvidence(
            config=self.config, mode="enforced", action=action, resource=resource,
            attestation_summary=attestation_summary,
            gateway_decision=execution.decision, gateway_status=execution.status,
            gateway_reason=execution.reason, audit_ref=execution.audit_ref,
            execution_receipt_present=execution.execution is not None,
            actuated=execution.executed, attester_service_calls=1, gateway_calls=1,
        )
        path = evidence.finalize_and_export(self.evidence_dir) if export_evidence else None
        return AttestationChainOutcome(
            mode="enforced", attestation=raw_attestation, execution=execution,
            evidence=evidence.finalize(), evidence_path=path,
        )

    # -- lifecycle --

    def close(self) -> None:
        if self._owns_gateway_client:
            self.gateway_client.close()

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.close()


__all__ = ["AttestationChainOutcome", "AttestationChainPilot", "AttesterClientError"]
