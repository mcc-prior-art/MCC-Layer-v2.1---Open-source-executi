"""Typed models for the public ``POST /evaluate`` boundary.

These mirror ``gateway/app.py``'s ``EvaluateRequest``/``EvaluateResponse`` and
``openapi/mcc-gateway.yaml``'s ``EvaluateRequest``/``EvaluateResponse``/
``Verdict`` schemas field-for-field — see
``docs/integration/GATEWAY_API_CONTRACT.md`` for the normative prose. This
module defines no fields, verdicts, or defaults beyond what those two
sources document.

Both models reject unknown fields (``extra="forbid"``) except where the live
contract itself is intentionally permissive:

* ``EvaluateRequest.context`` stays a generic, unvalidated object — action
  payload shapes are domain-specific (see ``docs/integration/
  GATEWAY_API_CONTRACT.md`` §6, §21); the Gateway does not enforce one fixed
  nested schema for it, so this SDK does not invent one either.
* ``EvaluateResponse.decision_token`` stays a generic, unvalidated object —
  the canonical server model (``gateway/app.py::EvaluateResponse``) itself
  types it as ``Dict[str, Any]``, not a nested schema. The SDK does not
  interpret, verify, or act on its contents (that is the Execution Gate's
  job, never the SDK's); a caller that needs the raw decision token gets it
  unmodified.

``EvaluateResponse`` is strict about every OTHER field: an unrecognized
top-level field in a response is a **fail-closed contract error**, not a
silently-ignored extra — see ``mcc_sdk.exceptions.MCCContractError``.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

__all__ = ["EvaluateRequest", "EvaluateResponse", "Verdict"]


class Verdict(str, Enum):
    """The four canonical MCC-Core verdicts. No others exist (see
    ``docs/integration/GATEWAY_API_CONTRACT.md`` §8). Pydantic rejects any
    value outside this set when parsing an :class:`EvaluateResponse` —
    an unknown verdict fails closed by construction, not by extra logic."""

    ALLOW = "ALLOW"
    DENY = "DENY"
    ESCALATE = "ESCALATE"
    CONSTRAIN = "CONSTRAIN"


class EvaluateRequest(BaseModel):
    """The request body for ``POST /evaluate``.

    Strict at the top level (``extra="forbid"``), matching the live Gateway
    behavior fixed in PR #80 — an unrecognized top-level field is rejected
    locally by this model before any network call is made, the same way the
    Gateway itself rejects it with HTTP 422.
    """

    model_config = ConfigDict(extra="forbid")

    identity: str = Field(..., min_length=1, description="Who is asking to act")
    action: str = Field(..., min_length=1, description="What they want to do")
    context: dict[str, Any] = Field(default_factory=dict, description="Parameters of the action")
    transaction_id: str | None = None
    idempotency_key: str | None = None
    actor_id: str | None = None
    resource_id: str | None = None
    # The live gateway.app.py::EvaluateRequest.mode is an unconstrained
    # Optional[str] (no server-side enum check) -- see the PR #81 report for
    # that discovered, out-of-scope gap. This SDK intentionally constrains it
    # to the two values the deployed policy actually understands
    # ("inline"/"observe"; anything else silently behaves like "observe"
    # server-side today) as a client-side safety net against a typo, not
    # because the wire contract enforces it. This is stricter than the
    # server, never looser -- it can only ever reject a request the server
    # would otherwise silently misinterpret, never accept one the server
    # would reject.
    mode: Literal["inline", "observe"] | None = None


class EvaluateResponse(BaseModel):
    """The response body for ``POST /evaluate``.

    Strict (``extra="forbid"``) for every field except ``decision_token``
    (see module docstring). The live Gateway (``response_model=
    EvaluateResponse`` in ``gateway/app.py``) only ever emits exactly this
    field set; an additional field appearing in a future Gateway version is
    a genuine contract change this SDK must fail closed on, not silently
    accept.
    """

    model_config = ConfigDict(extra="forbid")

    decision: Verdict
    reason: str
    audit_id: str
    signature: str | None = None
    decision_token: dict[str, Any] | None = None
    constraints: dict[str, Any] = Field(default_factory=dict)
    forward_context: dict[str, Any] = Field(default_factory=dict)
    applied_constraints: list[str] = Field(default_factory=list)
    enforce: bool = True
    mode: str = "observe"
    authority_required: str | None = None
    policy_ref: str = ""
    trace_id: str = ""
    transaction_id: str | None = None
    idempotency_key: str | None = None
    actor_id: str | None = None
    resource_id: str | None = None

    # -- convenience classification, mirroring mcc_client.Decision --
    # (read-only derived properties; no governance logic, no local
    # decision-making -- these only describe the verdict the Gateway already
    # returned.)

    @property
    def executable(self) -> bool:
        """ALLOW or CONSTRAIN — an authorized ``forward_context`` exists.
        This does NOT mean the SDK executes anything; the SDK has no
        execution path at all (see the security-boundary section of the
        SDK README)."""
        return self.decision in (Verdict.ALLOW, Verdict.CONSTRAIN)

    @property
    def denied(self) -> bool:
        return self.decision == Verdict.DENY

    @property
    def needs_approval(self) -> bool:
        return self.decision == Verdict.ESCALATE

    @property
    def constrained(self) -> bool:
        return self.decision == Verdict.CONSTRAIN
