"""The framework-neutral adapter compliance boundary.

The compliance runner evaluates an adapter *only* through this minimal, typed
boundary. It exposes exactly the behavior the Integration Contract requires and
nothing framework-specific: an adapter declares stable metadata and runs a
governed scenario, returning a normalized outcome.

The boundary intentionally does NOT:

* expose VoltAgent- or framework-specific types or lifecycle hooks;
* let an adapter authorize locally, sign, or reach an executor directly;
* hand the adapter anything but the governed SDK client + the contract-standard
  reasoning/operator/authorizer wiring for the scenario.

Every future adapter (and VoltAgent) plugs in through this same protocol. It is
marked experimental/internal: it is a repo-internal certification seam, not part
of the supported public SDK surface.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional, Protocol, runtime_checkable

from .models import AdapterMetadata, AdapterOutcome


@dataclass
class AdapterContext:
    """The governed environment handed to an adapter for one scenario.

    ``client`` is a real ``mcc_client.MCCClient`` pointed at a real governed
    gateway. ``provider_config`` steers the deterministic reasoning provider (what
    intent to propose). ``operator`` is the human authority for ESCALATE.
    ``authorizer`` is the authorization-material source for ALLOW/CONSTRAIN — it
    may be a *tampered* variant supplied by the runner to exercise a fail-closed
    invariant; a conforming adapter uses it faithfully and the gate enforces.

    None of these let the adapter bypass MCC-Core: the only outward channel is the
    SDK client, and execution still passes through the gate + governed executor.
    """

    request: str
    client: Any                      # mcc_client.MCCClient
    provider_config: Dict[str, Any]
    operator: Any                    # reference_governed_agent.Operator
    authorizer: Optional[Any] = None  # reference_governed_agent.ExecutionAuthorizer


@runtime_checkable
class ComplianceAdapter(Protocol):
    """The only surface through which an adapter is certified."""

    def describe(self) -> AdapterMetadata:
        """Return stable adapter identity, including the contract version it
        claims to implement. Required for certification; incomplete metadata fails
        closed."""
        ...

    def run_scenario(self, ctx: AdapterContext) -> AdapterOutcome:
        """Run one governed scenario end-to-end and return the normalized outcome.

        A conforming adapter proposes, evaluates, dispatches on the verdict,
        obtains authorization material through the provided authorizer, executes
        ONLY through the governed path, and reports faithfully. It never fabricates
        an execution, never bypasses the gate, and fails closed on any error."""


__all__ = ["AdapterContext", "ComplianceAdapter"]
