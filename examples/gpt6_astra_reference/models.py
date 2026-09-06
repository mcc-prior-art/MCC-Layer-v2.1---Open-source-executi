"""The closed Astra proposal schema and its strict, fail-closed parser.

An Intelligence provider (GPT-6 Astra or any other) proposes an action; it
does not, and structurally cannot, submit anything MCC-Core would treat as
trusted evidence or authority. ``AstraProposal`` carries only the four
fields a proposer may ever supply. Every trusted MCC field --
``verified``/``authority``/an execution token/an attestation
signature/``attester_id``/``kid``/``nonce``/hashes/``evidence_digest``/
``policy_hash``/validity timestamps -- is rejected if present, exactly as
``mcc_attester_service.app.AttestRequest`` (``extra="forbid"``) already
rejects the same class of field one layer downstream. This is the SAME
discipline applied one layer earlier, at the point Intelligence output
first becomes a Python object.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union

#: Fields a proposal is allowed to carry. Nothing else survives parsing.
_ALLOWED_KEYS = frozenset({"action", "resource", "payload", "reason"})

#: Trusted MCC fields a model output must never carry. Checked explicitly
#: (not merely implied by the allow-list above) so a caller of
#: ``parse_proposal`` gets a specific, honest reason naming exactly which
#: trusted field the model attempted to supply -- mirroring
#: ``tests/test_attester_service.py``'s own ``_BYPASS_FIELDS`` convention.
FORBIDDEN_TRUSTED_FIELDS = frozenset({
    "verified", "authority", "execution_token", "token", "decision_token",
    "attestation", "attestation_signature", "sig", "attester_id", "kid",
    "nonce", "action_hash", "payload_hash", "evidence_digest", "policy_hash",
    "policy_version", "issued_at", "not_before", "expires_at", "exp", "nbf",
    "iat", "mandate", "mandate_id",
})


@dataclass(frozen=True)
class AstraProposal:
    """One proposed action. Carries no trusted MCC field -- ``__post_init__``
    only checks shape; the actual security boundary is that nothing below
    this ever reads a trusted-sounding attribute off this object."""

    action: str
    resource: str
    payload: Dict[str, Any] = field(default_factory=dict)
    reason: Optional[str] = None

    def __post_init__(self) -> None:
        if not self.action or not isinstance(self.action, str):
            raise AstraProposalError("action must be a non-empty string")
        if not self.resource or not isinstance(self.resource, str):
            raise AstraProposalError("resource must be a non-empty string")
        if not isinstance(self.payload, dict):
            raise AstraProposalError("payload must be an object")


@dataclass(frozen=True)
class AstraSelfRefusal:
    """The model declined to propose the requested action at all. This is a
    MODEL ALIGNMENT outcome -- MCC is never invoked, so it can neither cause
    nor take credit for it. See docs/GPT6_ASTRA_REFERENCE_INTEGRATION.md
    §4 (Alignment != Authority)."""

    reason: str


@dataclass(frozen=True)
class AstraError:
    """The model's output could not be used at all: malformed JSON, a
    disallowed/forbidden field, an unexpected shape, or a transport/provider
    failure. Fail-closed -- this NEVER reaches governance."""

    detail: str


#: What one call to an AstraProvider returns. A non-empty list of proposals
#: is the normal case (almost always one element; more than one models an
#: agent that decided, in a single turn, to take an additional action --
#: see Scenario F / the autonomous-scope-expansion adversarial case).
AstraOutcome = Union[List[AstraProposal], AstraSelfRefusal, AstraError]


class AstraProposalError(Exception):
    """Raised by ``parse_proposal`` on any malformed or untrusted-field
    model output. Fail-closed: no partial proposal is ever returned."""


def parse_proposal(raw: Any) -> AstraProposal:
    """Strictly parse one model-emitted JSON object into an
    :class:`AstraProposal`. Raises :class:`AstraProposalError` on anything
    that is not exactly the closed shape -- extra keys, forbidden trusted
    fields, wrong types, or a non-object at all. Never returns a
    best-effort or partially-populated proposal."""
    if not isinstance(raw, dict):
        raise AstraProposalError(f"model output must be a JSON object, got {type(raw).__name__}")

    keys = set(raw.keys())
    forbidden_present = keys & FORBIDDEN_TRUSTED_FIELDS
    if forbidden_present:
        raise AstraProposalError(
            f"model output supplied forbidden trusted field(s): {sorted(forbidden_present)} "
            f"-- an Intelligence provider may never submit trusted MCC fields"
        )
    unknown = keys - _ALLOWED_KEYS
    if unknown:
        raise AstraProposalError(f"model output has unrecognized field(s): {sorted(unknown)}")

    if "action" not in raw or "resource" not in raw:
        raise AstraProposalError("model output missing required field(s): action, resource")

    try:
        return AstraProposal(
            action=raw["action"], resource=raw["resource"],
            payload=raw.get("payload") or {}, reason=raw.get("reason"),
        )
    except AstraProposalError:
        raise
    except Exception as exc:  # noqa: BLE001 -- any parse failure fails closed
        raise AstraProposalError(f"model output could not be parsed: {exc!r}") from exc


def parse_proposals(raw: Any) -> List[AstraProposal]:
    """Parse either a single proposal object or a JSON array of them. Fails
    closed (raises) the moment any element is malformed -- never returns a
    partially-parsed list."""
    if isinstance(raw, list):
        if not raw:
            raise AstraProposalError("model output is an empty proposal list")
        return [parse_proposal(item) for item in raw]
    return [parse_proposal(raw)]


class AstraNonCanonicalActionError(AstraProposalError):
    """Raised when a proposal's ``action`` is not EXACTLY the canonical
    action identifier a task requires. No alias, synonym, or namespaced
    variant is ever accepted -- a model that names the same real-world
    operation differently (e.g. ``"github.create_issue"`` in place of the
    canonical ``"create_github_issue"``) has NOT supplied the canonical
    identifier this mandate is scoped to, and is rejected at the proposal
    layer -- it is never forwarded to the Attester/Gate as if it required
    its own scope decision, and the mandate's action scope is never
    broadened or dynamically matched to accommodate it."""


def require_canonical_action(proposal: AstraProposal, canonical_action: str) -> AstraProposal:
    """Fail-closed proposal-contract check: ``proposal.action`` must equal
    ``canonical_action`` byte-for-byte. This performs no normalization, no
    case-folding, no alias table, and no fuzzy or prefix matching -- exact
    equality only. Returns ``proposal`` unchanged on success; raises
    :class:`AstraNonCanonicalActionError` (a subclass of
    :class:`AstraProposalError`) otherwise, so every existing "malformed
    Astra output" handling path already in this package also covers a
    non-canonical action."""
    if proposal.action != canonical_action:
        raise AstraNonCanonicalActionError(
            f"model proposed action {proposal.action!r}; this task requires exactly the "
            f"canonical action identifier {canonical_action!r} -- no alias is accepted"
        )
    return proposal


__all__ = [
    "AstraProposal", "AstraSelfRefusal", "AstraError", "AstraOutcome",
    "AstraProposalError", "AstraNonCanonicalActionError", "FORBIDDEN_TRUSTED_FIELDS",
    "parse_proposal", "parse_proposals", "require_canonical_action",
]
