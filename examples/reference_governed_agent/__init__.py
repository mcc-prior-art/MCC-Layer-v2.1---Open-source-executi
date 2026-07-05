"""Framework-neutral reference governed agent for MCC-Core.

The canonical reference AI agent: it proposes actions, submits them to MCC-Core
through the supported SDK (``mcc_client``), obtains human approval when required,
and executes **only** through the governed path — never directly. Reasoning is not
authority; proposal is not permission; the agent has no direct execution route.

No agent framework (VoltAgent, LangGraph, CrewAI, OpenAI Agents SDK, …) appears
anywhere in the loop. Any of them can integrate later as an adapter that produces
a proposal and hands it to this same SDK boundary.

    The model proposes. MCC-Core decides. The gate enforces. The audit chain records.

Public surface (pure, dependency-light modules only — the in-process demo stack in
``_localstack`` is imported lazily by the CLI, not here):
"""

from __future__ import annotations

from .actions import ACTION, RESOURCE, build_notification_payload, parse_request
from .agent import ReferenceGovernedAgent
from .authorizers import ConsensusAuthorizer, ExecutionAuthorizer
from .models import AgentRunResult, ProposedAction, ProviderError
from .operator import (
    ApprovalRequest,
    CLIOperator,
    Operator,
    ProgrammaticOperator,
)
from .providers import (
    DEFAULT_ACTOR,
    DeterministicProvider,
    OptionalLLMProvider,
    ReasoningProvider,
)

__all__ = [
    "ReferenceGovernedAgent",
    # reasoning
    "ReasoningProvider",
    "DeterministicProvider",
    "OptionalLLMProvider",
    "DEFAULT_ACTOR",
    # operator
    "Operator",
    "ProgrammaticOperator",
    "CLIOperator",
    "ApprovalRequest",
    # authorization material
    "ExecutionAuthorizer",
    "ConsensusAuthorizer",
    # models + actions
    "ProposedAction",
    "AgentRunResult",
    "ProviderError",
    "ACTION",
    "RESOURCE",
    "build_notification_payload",
    "parse_request",
]
