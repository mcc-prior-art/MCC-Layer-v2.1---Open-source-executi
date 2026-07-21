"""Conforming reference adapters, plugged into the generic compliance boundary.

Both adapters drive the SAME framework-neutral governed path (the reference
governed agent over ``mcc_client``); the only difference is their declared
identity. There is deliberately **no** adapter-specific branch that makes either
one pass — the Integration Contract is framework-neutral, so a conforming
integration produces the same governed outcomes regardless of framework.

VoltAgent note: this adapter certifies VoltAgent's *contract behavior* — the
governed proposal → decision → verified execution path it uses — in-process and
offline, with VoltAgent adapter identity. It is not a re-run of the Node runtime;
that end-to-end path is covered by the existing VoltAgent vitest/Docker E2E. This
keeps VoltAgent a conforming reference integration, never the reference
specification.
"""

from __future__ import annotations

from mcc_client.contract import CONTRACT_VERSION

from examples.reference_governed_agent import (
    DeterministicProvider,
    ReferenceGovernedAgent,
)

from .models import AdapterMetadata, AdapterOutcome
from .protocol import AdapterContext
from .registry import register_adapter


class _GovernedAgentAdapter:
    """Base conforming adapter: run one governed scenario through the reference
    agent and normalize the result. Holds no signing key, no executor, and no
    direct route — its only channel is the injected SDK client."""

    def __init__(self, *, name: str, version: str, implementation_id: str,
                 framework: str | None) -> None:
        self._meta = AdapterMetadata(
            name=name, version=version, implementation_id=implementation_id,
            claimed_contract_version=CONTRACT_VERSION, framework=framework)

    def describe(self) -> AdapterMetadata:
        return self._meta

    def run_scenario(self, ctx: AdapterContext) -> AdapterOutcome:
        provider = DeterministicProvider(**ctx.provider_config)
        agent = ReferenceGovernedAgent(
            ctx.client, provider=provider, operator=ctx.operator,
            authorizer=ctx.authorizer)
        r = agent.handle(ctx.request)
        return AdapterOutcome(
            verdict=r.verdict,
            executed=bool(r.executed),
            applied_constraints=list(r.applied_constraints or []),
            audit_valid=r.audit_valid,
            error=r.error,
        )


class ReferenceComplianceAdapter(_GovernedAgentAdapter):
    """The canonical framework-neutral reference integration."""

    def __init__(self) -> None:
        super().__init__(name="reference-governed-agent", version="1.0.0",
                         implementation_id="examples/reference_governed_agent",
                         framework=None)


class VoltAgentComplianceAdapter(_GovernedAgentAdapter):
    """VoltAgent, certified through the same generic boundary as every adapter."""

    def __init__(self) -> None:
        super().__init__(name="voltagent", version="0.1.0",
                         implementation_id="integrations/voltagent",
                         framework="voltagent")


register_adapter("reference", ReferenceComplianceAdapter)
register_adapter("voltagent", VoltAgentComplianceAdapter)


__all__ = ["ReferenceComplianceAdapter", "VoltAgentComplianceAdapter"]
