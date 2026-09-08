"""Real, durable, Redis-backed Phase 2 stack for the live sandbox proof.

Builds the SAME components every other production/reference call site in
this repository uses (``mcc_core.core.DecisionEngine``,
``mcc_core.gate.ExecutionGate``, ``mcc_core.coordinator.EnforcementCoordinator``,
``mcc_core.authority.AuthorityModel``, ``mcc_proposal.MCCProposalService``,
``gateway.proposal_execution_service.ProposalExecutionService``) -- no new
decision logic, no second Gate, no second ``EnforcementCoordinator``, no
second durable execution registry.

Fail-closed: refuses to build a stack against an unreachable Redis
(Section 5: "must fail closed if Redis is unavailable. No durable backend:
NO ACTUATION.").
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

from mcc_core import (
    ActionPolicy,
    AuditLog,
    AuthorityModel,
    DecisionEngine,
    EnforcementCoordinator,
    ExecutionGate,
    InMemoryVelocityRegistry,
    MandateRegistry,
    ProfileRegistry,
    RedisIdempotencyRegistry,
    RedisNonceRegistry,
    SigningKey,
    Verdict,
)
from mcc_proposal import MCCProposalService, RedisProposalRegistry

from examples.gpt6_astra_reference.github_actuator import GitHubActuatorConfig, GitHubIssueActuator
from gateway.proposal_execution_service import ProposalExecutionService

from .actuator import GitHubSandboxUpstream
from .config import SandboxConfig, SandboxConfigError
from .evidence import make_sandbox_evidence_verifier


class RedisUnavailableError(SandboxConfigError):
    """Raised when the configured Redis backend cannot be reached at stack
    construction time -- fail-closed: zero durable admission, zero
    actuation is even reachable from this point."""


@dataclass(frozen=True)
class LiveSandboxStack:
    proposals: Any
    idempotency: Any
    nonces: Any
    authority: AuthorityModel
    engine: DecisionEngine
    coordinator: EnforcementCoordinator
    bridge: ProposalExecutionService
    svc: MCCProposalService
    evidence_verifier: Any
    repo: Optional[str]
    audit: AuditLog


async def _check_redis(client: Any) -> None:
    try:
        await client.ping()
    except Exception as exc:
        raise RedisUnavailableError(f"Redis backend unavailable: {exc!r}") from exc


async def build_live_sandbox_stack(
    *,
    config: Optional[SandboxConfig] = None,
    tenants: Dict[str, Dict[str, Any]],
    action: str = "create_github_issue",
    namespace_suffix: Optional[str] = None,
) -> LiveSandboxStack:
    """Builds the real, Redis-backed Phase 2 stack.

    ``tenants`` maps ``tenant_id -> constraints`` (``{}`` for none) -- each
    listed tenant is granted the sandbox ``execute`` authority for
    ``action`` via the SAME declarative ``AuthorityModel`` every other
    reference caller in this repository uses; an unlisted tenant_id has no
    authority (``DENY`` by default -- Section 8B: no authority -> zero
    external requests).
    """
    import redis.asyncio as redis

    config = config or SandboxConfig.from_env()
    if not config.redis_url:
        raise SandboxConfigError("a Redis URL is required to build the live sandbox stack")

    client = redis.from_url(config.redis_url, decode_responses=True)
    await _check_redis(client)

    ns = namespace_suffix or uuid.uuid4().hex[:8]
    proposals = RedisProposalRegistry(client, namespace=f"mcc:v1:phase2live-{ns}:proposal:")
    idem = RedisIdempotencyRegistry(client, namespace=f"mcc:idem:phase2live-{ns}:")
    nonces = RedisNonceRegistry(client, namespace=f"mcc:nonce:phase2live-{ns}:")

    signing_key = SigningKey.generate(f"phase2-live-{ns}")
    engine = DecisionEngine(
        signing_key=signing_key, issuer="mcc/phase2-live-sandbox", audience="phase2-live-sandbox-gate",
        policy_id="phase2-live-sandbox/v1", policy_hash="sha256:phase2-live-sandbox", token_ttl_seconds=60,
    )
    gate = ExecutionGate(
        trusted_keys={signing_key.kid: signing_key.public_key()}, audience="phase2-live-sandbox-gate",
        nonce_registry=nonces, policy_hash="sha256:phase2-live-sandbox",
    )
    audit = AuditLog(str(Path(f"/tmp/mcc-phase2-live-{ns}-audit.jsonl")))
    coordinator = EnforcementCoordinator(
        gate=gate, idempotency=idem, velocity=InMemoryVelocityRegistry(),
        audit=audit, profiles=ProfileRegistry(),
    )

    grants = {t: [{"authority": "execute", "constraints": constraints or {}}] for t, constraints in tenants.items()}
    authority = AuthorityModel(
        registry=MandateRegistry.from_config(grants),
        policies=[ActionPolicy(action=action, requires="execute", on_mandate=Verdict.ALLOW,
                               without_mandate=Verdict.DENY)],
        default=Verdict.DENY,
    )

    actuator_config = GitHubActuatorConfig(
        mode="live" if config.live else "disabled", repo=config.repo,
        base_url=config.base_url, token=config.token,
    )
    upstream = GitHubSandboxUpstream(GitHubIssueActuator(actuator_config))

    bridge = ProposalExecutionService(
        proposals=proposals, authority=authority, engine=engine,
        coordinator=coordinator, upstream=upstream,
    )
    svc = MCCProposalService(proposals=proposals, durable_execution_state=idem)

    evidence_verifier = None
    if config.repo:
        evidence_verifier = make_sandbox_evidence_verifier(
            base_url=config.base_url, repo=config.repo, token=config.token,
        )

    return LiveSandboxStack(
        proposals=proposals, idempotency=idem, nonces=nonces, authority=authority,
        engine=engine, coordinator=coordinator, bridge=bridge, svc=svc,
        evidence_verifier=evidence_verifier, repo=config.repo, audit=audit,
    )


__all__ = ["LiveSandboxStack", "build_live_sandbox_stack", "RedisUnavailableError"]
