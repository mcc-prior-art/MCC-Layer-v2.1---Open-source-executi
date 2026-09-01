"""Independent Attester Service — HTTP transport (PR-4, MCC-AT-004).

Thin transport only: strict request-schema validation, service-to-service
authentication, delegation to :class:`~mcc_attester_service.service.AttesterService`.
No assessment logic, no signing logic, no binding logic lives here.

Design rule 3 (no caller-supplied "trusted result"): :class:`AttestRequest`
below carries ONLY a description of the operation to assess (``action``,
``resource``, ``payload``). Every field the Attester itself must control --
``sig``, ``kid``, ``attester_id``, ``attestation_id``, ``nonce``,
``issued_at``, ``not_before``, ``expires_at``, ``action_hash``,
``payload_hash``, ``evidence_digest``, any ``verified``/verification-result
field, trusted provenance metadata, ``evidence_type``, ``claims`` -- is
deliberately absent from this schema. ``extra="forbid"`` additionally
rejects any attempt to smuggle one of these (or anything else) in under an
unmodeled field name; this is proven structurally in
``tests/test_attester_service_architecture_guards.py`` and behaviorally in
``tests/test_attester_service.py``.
"""

from __future__ import annotations

import secrets
from typing import Any, Dict, Optional

from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel, ConfigDict, Field

from .config import AttesterServiceConfig
from .errors import AttesterServiceError
from .provider import AssessmentProvider
from .service import AttesterService


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")


class AttestRequest(_Strict):
    """Describes ONLY the operation to be assessed. See the module
    docstring for the closed list of trusted-output fields this schema
    deliberately excludes."""

    action: str = Field(min_length=1)
    resource: Optional[str] = None
    payload: Dict[str, Any] = Field(default_factory=dict)


class HealthResponse(_Strict):
    status: str
    service: str


def _require_service_auth(auth_secret: str):
    """Service-to-service authentication dependency: a shared secret
    compared with ``secrets.compare_digest`` (constant-time, avoiding a
    timing side channel). Runs as a FastAPI dependency, which executes
    BEFORE the route body -- so authentication failure happens before any
    assessment or signing is attempted (design rule 7/8).

    What this proves: the caller possesses the configured shared secret.
    What this does NOT prove: the caller's individual identity beyond that
    (every holder of the secret is indistinguishable to this check), that
    the request's *content* is trustworthy (that remains the schema's and
    the AssessmentProvider's job), or anything about network-layer
    transport security (TLS termination is a deployment concern, out of
    scope for this boundary). See ``specs/MCC-AT-004.md`` §7.
    """

    def dependency(x_attester_auth: str = Header(default="")) -> str:
        if not x_attester_auth or not secrets.compare_digest(x_attester_auth, auth_secret):
            raise HTTPException(status_code=401, detail="INVALID_ATTESTER_AUTH")
        return "authenticated"

    return dependency


def build_attester_app(*, config: AttesterServiceConfig, provider: AssessmentProvider) -> FastAPI:
    """Assemble the Independent Attester Service as a standalone FastAPI
    app. Owns the private signing key (via ``config``, never re-exported)
    and the assessment provider. Nothing about MCC-Core's gateway/runtime
    (``gateway.*``, ``src/mcc_core.*``, ``ExecutionGate``,
    ``EnforcementCoordinator``) is imported or referenced anywhere in this
    module or its callees -- this app is meant to run as its own process,
    in its own trust domain, and never actuates anything itself."""
    service = AttesterService(config=config, provider=provider)
    require_auth = _require_service_auth(config.auth_secret)
    app = FastAPI(title="MCC Independent Attester Service")

    @app.get("/health")
    def health() -> HealthResponse:
        return HealthResponse(status="ok", service="mcc-attester")

    @app.post("/attest")
    async def attest(req: AttestRequest, _=Depends(require_auth)) -> Dict[str, Any]:
        try:
            return await service.attest(action=req.action, resource=req.resource, payload=req.payload)
        except AttesterServiceError as exc:
            # Never a partial/unsigned artifact on any failure path -- the
            # response is either a complete signed attestation (200) or no
            # attestation at all (503: the service could not produce one
            # right now -- provider/binding/signing failure, never the
            # caller's fault to guess at).
            raise HTTPException(status_code=503, detail=f"ATTESTATION_UNAVAILABLE: {exc}")

    return app


__all__ = ["AttestRequest", "HealthResponse", "build_attester_app"]
