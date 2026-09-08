"""Adapts ``examples.gpt6_astra_reference.github_actuator.GitHubIssueActuator``
to the Phase 2 ``gateway.proposal_execution_service.ResourceBoundUpstream``
contract -- reusing its real HTTP-call implementation, disabled-by-default
mode gating, and forbidden-repo guard rather than building a second
actuator architecture (Section 2: "Use the existing GitHub actuator
implementation if practical, but adapt/wrap it to the Phase 2
ResourceBoundUpstream contract").
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from examples.gpt6_astra_reference.github_actuator import GitHubIssueActuator

from gateway.proposal_execution_service import ResourceMismatchError


class GitHubSandboxUpstream:
    """``resource`` is the actuator's own configured destination repository
    (``actuator.config.repo``) -- the ONLY destination this actuator
    instance can ever target, because the real HTTP call
    (``GitHubIssueActuator.__call__``) always POSTs to
    ``{base_url}/repos/{actuator.config.repo}/issues``, reading that value
    from the actuator's own immutable configuration, never from any
    argument a caller supplies. ``execute()`` compares the AUTHORIZED
    resource against this fixed value BEFORE delegating; since there is
    only one possible destination this actuator instance can ever reach,
    there is no second, independently-selected destination for the
    delegate to diverge to once that comparison passes (Section 3:
    "AUTHORIZED RESOURCE == ACTUAL EXTERNAL DESTINATION")."""

    def __init__(self, actuator: GitHubIssueActuator) -> None:
        self._actuator = actuator
        self.resource = actuator.config.repo

    async def execute(self, *, resource: Optional[str], action: str, payload: Dict[str, Any]) -> Any:
        if resource != self.resource:
            raise ResourceMismatchError(
                f"sandbox actuator configured for resource {self.resource!r} refuses to "
                f"dispatch to {resource!r}; refusing before any external call"
            )
        return await self._actuator(action, payload)


__all__ = ["GitHubSandboxUpstream"]
