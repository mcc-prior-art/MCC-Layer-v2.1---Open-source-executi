"""Phase 2 Live Sandbox Proof — connects the existing, unmodified
``gateway.proposal_execution_service.ProposalExecutionService`` path to a
real external sandbox side effect (a GitHub issue in an explicitly
isolated sandbox repository), without introducing a second Gate, a second
``EnforcementCoordinator``, a second durable execution registry, or any
duplicated authorization logic.

See ``docs/PHASE2_LIVE_SANDBOX_PROOF.md`` for the full design writeup.

    PROPOSAL != PERMISSION.
    MARKER != AUTHORITY.

Defaults to fully disabled: no external request is ever made unless
``MCC_PHASE2_LIVE_SANDBOX=1`` and every other required environment
variable is explicitly set (see ``config.py``).
"""

from __future__ import annotations

from .config import FORBIDDEN_SANDBOX_REPOS, SandboxConfig, SandboxConfigError
from .actuator import GitHubSandboxUpstream
from .evidence import make_sandbox_evidence_verifier
from .marker import (
    composite_marker,
    extract_composite_marker_identity,
    prepare_sandbox_issue_payload,
)
from .stack import LiveSandboxStack, build_live_sandbox_stack

__all__ = [
    "SandboxConfig",
    "SandboxConfigError",
    "FORBIDDEN_SANDBOX_REPOS",
    "GitHubSandboxUpstream",
    "make_sandbox_evidence_verifier",
    "composite_marker",
    "extract_composite_marker_identity",
    "prepare_sandbox_issue_payload",
    "LiveSandboxStack",
    "build_live_sandbox_stack",
]
