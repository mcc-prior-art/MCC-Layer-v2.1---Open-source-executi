"""Orchestrates ONE Astra proposal through the real, unmodified MCC chain.

    ASTRA PROPOSAL
        -> INDEPENDENT ATTESTER  (mcc_attester_service.AttesterService.attest)
        -> CONTROL               (gateway.pre_execution_control.PreExecutionControl.evaluate,
                                   reached via GovernanceService)
        -> SIGNED EXECUTION AUTHORITY (mcc_core.core.DecisionEngine.issue_token)
        -> AUTHORITY VERIFICATION + GATE (mcc_core.gate.ExecutionGate,
                                   via mcc_core.coordinator.EnforcementCoordinator.enforce)
        -> EXECUTION             (the configured upstream -- GitHubIssueActuator
                                   in this demo, but this module never imports it)

Two entry points, both composed ENTIRELY from real, existing, public
MCC-Core/gateway primitives -- no new decision logic, no new token format,
no second Gate:

* :func:`run_positive_path` -- the single supported public path,
  ``GovernanceService.execute_with_mandate``, unchanged and untouched. Used
  for the positive, wrong-scope, and autonomous-expansion scenarios, all of
  which need exactly one governed call per proposal.
* :func:`run_with_explicit_steps` -- the SAME sequence
  ``execute_with_mandate`` performs internally
  (authority -> control -> issue_token -> enforce), exposed as separate
  awaitable steps so the tamper/replay/expiry adversarial scenarios can
  observe or reuse an intermediate artifact (an already-issued token)
  exactly as ``tests/test_compromised_intelligence_adversarial.py`` and
  ``tests/test_evidence_bound_execution_ticket.py`` already do throughout
  this repository. This function calls the identical
  ``MandateAuthority``/``PreExecutionControl``/``DecisionEngine``/
  ``EnforcementCoordinator`` objects the convenience wrapper uses; it does
  not reimplement any of their decision logic.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from gateway.governance_service import ExecOutcome, GovernanceService
from mcc_attester_service import AttesterService
from mcc_core.signing import hash_document

from .models import AstraProposal


@dataclass(frozen=True)
class AttestationOutcome:
    ok: bool
    raw_attestation: Optional[Dict[str, Any]]
    reason: str


async def obtain_attestation(
    attester: AttesterService, *, proposal: AstraProposal, canonical_payload: Dict[str, Any],
) -> AttestationOutcome:
    """The Attester independently assesses the PROPOSED action -- it knows
    nothing about Astra, and nothing here reads a caller-supplied "trusted"
    field off ``proposal`` (there isn't one; see ``models.AstraProposal``).
    A proposal is intentionally allowed to enter the assessment pipeline;
    this does not itself grant authority (see
    ``docs/EXECUTION_AUTHORITY_BOUNDARY.md`` §11)."""
    try:
        raw = await attester.attest(
            action=proposal.action, resource=proposal.resource, payload=canonical_payload,
        )
        return AttestationOutcome(True, raw, "VERIFIED")
    except Exception as exc:  # noqa: BLE001 -- any Attester-side refusal fails closed
        return AttestationOutcome(False, None, f"ATTESTER_REFUSED: {exc!r}")


async def run_positive_path(
    service: GovernanceService, *, mandate: Any, actor: str, proposal: AstraProposal,
    attestation: Optional[Dict[str, Any]], logical_operation_id: Optional[str] = None,
) -> ExecOutcome:
    """The single supported public path. Used whenever a scenario needs
    exactly one governed call — positive, wrong-scope, and
    autonomous-scope-expansion.

    ``logical_operation_id`` becomes the signed token's ``idempotency_key`` —
    the durable logical-operation identity ``EnforcementCoordinator`` binds
    to the exact (action, resource, payload_hash) triple (Round 17: see
    ``docs/DURABLE_OPERATION_SAFETY.md``). Optional here because not every
    action this pipeline exercises is a real external side effect requiring
    that protection; ``cli.py`` enforces it (via
    ``models.require_logical_operation_id``) for the one action that is
    (``create_github_issue``), before this function is ever called."""
    return await service.execute_with_mandate(
        mandate=mandate, actor=actor, action=proposal.action, resource=proposal.resource,
        context=proposal.payload, attestation=attestation, idempotency_key=logical_operation_id,
    )


@dataclass(frozen=True)
class IssuedAuthority:
    """An intermediate artifact of the real chain, exposed only so the
    adversarial scenarios can present it more than once (replay) or
    against a mutated action/payload (tamper) -- never a new authority
    format, just the real ``DecisionEngine``-signed token this repository
    already defines."""

    token: Dict[str, Any]
    canonical_payload: Dict[str, Any]
    evidence_digest: Optional[str]


class AuthorityDeniedError(Exception):
    """Raised by ``issue_authority`` when the mandate/control layer denies
    before any token is issued. Carries the real ``ExecOutcome`` so the
    caller can classify it precisely."""

    def __init__(self, outcome: ExecOutcome) -> None:
        super().__init__(outcome.reason)
        self.outcome = outcome


async def issue_authority(
    service: GovernanceService, *, mandate: Any, actor: str, proposal: AstraProposal,
    attestation: Optional[Dict[str, Any]], logical_operation_id: Optional[str] = None,
) -> IssuedAuthority:
    """Reproduces ``GovernanceService.execute_with_mandate``'s OWN sequence
    up to (and including) token issuance, stopping BEFORE
    ``EnforcementCoordinator.enforce`` — the exact seam the tamper/replay
    scenarios need. Built ENTIRELY from ``GovernanceService``'s own public
    attributes (``engine``/``trust_set``/``revocation_registry``/
    ``pre_execution_control``/``profiles``/``policy_hash``) and public
    classes (``MandateAuthority``/``MandateVerifier``/
    ``PreExecutionControl.evaluate``/``DecisionEngine.issue_token``) — no
    private method of ``GovernanceService`` is called, and no decision
    logic is reimplemented; this only sequences the same real calls
    ``execute_with_mandate`` itself makes. Raises
    :class:`AuthorityDeniedError` if the real mandate-authority or Control
    check denies, exactly as ``execute_with_mandate`` itself would have
    returned BLOCKED at that point."""
    import time

    from mcc_core import MandateAuthority, MandateVerifier, Verdict

    now = int(time.time())
    kid = mandate.get("kid") if isinstance(mandate, dict) else None
    resolution = service.trust_set.resolve(kid, now=now)
    if not resolution.ok:
        raise AuthorityDeniedError(
            ExecOutcome("BLOCKED", f"{resolution.status.value}: {resolution.reason}", decision="DENY")
        )
    authority = MandateAuthority(MandateVerifier(
        trusted_keys={resolution.kid: resolution.public_key},
        revocation_registry=service.revocation_registry,
    ))

    profile = service.profiles.for_action(proposal.action)
    canonical = profile.canonical_payload(proposal.payload)

    decision = await authority.authorize(
        mandate, subject=actor, action=proposal.action, resource=proposal.resource,
        context=canonical, now=now, policy_hash=service.policy_hash,
    )
    if decision.verdict not in (Verdict.ALLOW, Verdict.CONSTRAIN):
        raise AuthorityDeniedError(ExecOutcome("BLOCKED", decision.reason, decision=decision.verdict.value))

    forward_context = decision.forward_context or canonical

    evidence_digest = None
    if service.pre_execution_control is not None:
        result = await service.pre_execution_control.evaluate(
            action=proposal.action, forward_context=forward_context, resource=proposal.resource,
            raw_attestation=attestation, policy_hash=service.policy_hash,
        )
        if not result.ok:
            raise AuthorityDeniedError(
                ExecOutcome("BLOCKED", f"{result.reason_code.value}: {result.reason}", decision="DENY")
            )
        evidence_digest = result.evidence_digest

    auth_claims = dict(profile.auth_claims(forward_context))
    token = service.engine.issue_token(
        verdict=decision.verdict.value, subject=actor, action=proposal.action,
        payload=forward_context, constraints=decision.constraints,
        actor_id=actor, resource_id=proposal.resource,
        auth_claims=auth_claims, mandate_id=decision.mandate_id,
        evidence_digest=evidence_digest, idempotency_key=logical_operation_id,
    )
    return IssuedAuthority(token=token, canonical_payload=forward_context, evidence_digest=evidence_digest)


async def enforce_authority(
    service: GovernanceService, *, issued: IssuedAuthority, actor: str, resource: Optional[str],
    action: str, payload: Optional[Dict[str, Any]] = None,
    attestation: Optional[Dict[str, Any]] = None,
) -> ExecOutcome:
    """Presents ``issued.token`` to the real, public
    ``EnforcementCoordinator.enforce`` — the SAME call
    ``GovernanceService`` itself makes to reach the upstream, and the
    identical call ``main.py``'s own consensus ``/evaluate`` path already
    makes directly (this is not a new call shape). ``payload`` defaults to
    the token's own canonical payload; passing a DIFFERENT
    ``payload``/``action`` here is exactly how the tamper scenario is
    honestly reproduced — the Gate's own action_hash/payload_hash binding
    check is what then fires, nothing here decides that outcome."""
    async def executor():
        if service.upstream is None:
            raise RuntimeError("no upstream configured")
        effective_payload = payload if payload is not None else issued.canonical_payload
        return await service.upstream(action, effective_payload)

    result = await service.coordinator.enforce(
        token=issued.token, action=action,
        payload=payload if payload is not None else issued.canonical_payload,
        executor=executor,
        request_binding={"actor_id": actor, "resource_id": resource, "transaction_id": None},
        evidence=attestation,
    )
    return ExecOutcome(
        status=result.status.value, reason=result.reason,
        decision=result.decision.value if result.decision else None,
        audit_ref=result.audit_ref, execution=result.execution,
    )


def proposal_fingerprint(proposal: AstraProposal) -> str:
    return hash_document({"action": proposal.action, "resource": proposal.resource,
                          "payload": proposal.payload})


def attestation_fingerprint(raw_attestation: Optional[Dict[str, Any]]) -> Optional[str]:
    return hash_document(raw_attestation) if raw_attestation is not None else None


def authority_fingerprint(token: Optional[Dict[str, Any]]) -> Optional[str]:
    return hash_document(token) if token is not None else None


__all__ = [
    "AttestationOutcome", "obtain_attestation", "run_positive_path",
    "IssuedAuthority", "AuthorityDeniedError", "issue_authority", "enforce_authority",
    "proposal_fingerprint", "attestation_fingerprint", "authority_fingerprint",
]
