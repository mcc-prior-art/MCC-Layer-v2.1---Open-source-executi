"""Shared builders for evidence-bundle tests: real signed tokens + audit slices."""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Dict, Tuple

from mcc_core import AuditLog, DecisionEngine, SigningKey
from mcc_core.signing import hash_payload

from mcc_evidence import EvidenceInput

ISSUER = "mcc://issuer"
AUDIENCE = "mcc-gate"
KID = "evidence-kid-1"


def signing_key() -> SigningKey:
    return SigningKey.generate(KID)


def trusted_keys(key: SigningKey) -> Dict[str, str]:
    return {key.kid: key.public_key_b64()}


def _engine(key: SigningKey) -> DecisionEngine:
    return DecisionEngine(
        signing_key=key, issuer=ISSUER, audience=AUDIENCE,
        policy_id="pol-1", policy_hash="sha256:policy-abc", token_ttl_seconds=3600)


def _audit_slice(tmp: Path, decision_id: str, *, executed: bool) -> Tuple[list, str]:
    log = AuditLog(str(tmp / "audit.jsonl"))
    anchor_prev = log.prev_hash
    e1 = log.append({"event": "decision", "decision_id": decision_id})
    events = [e1]
    events.append(log.append(
        {"event": "executed" if executed else "denied", "decision_id": decision_id}))
    return events, anchor_prev


def allow_input(key: SigningKey, *, tmp_path: Path | None = None) -> EvidenceInput:
    tmp = tmp_path or Path(tempfile.mkdtemp())
    payload = {"amount": 100, "currency": "USD", "beneficiary_id": "ben-1"}
    tok = _engine(key).issue_token(
        verdict="ALLOW", subject="agent/payments", action="send_payment",
        payload=payload, actor_id="agent/payments", resource_id="acct-1")
    entries, anchor = _audit_slice(tmp, tok["jti"], executed=True)
    receipt = {"received": True, "receipt_id": "rcpt-1", "correlation_id": "corr-allow",
               "payload_sha256": hash_payload(payload), "status": "executed"}
    return EvidenceInput(
        verdict="ALLOW", actor_id="agent/payments", resource_id="acct-1",
        action="send_payment", correlation_id="corr-allow", decision_token=tok,
        proposal=payload, receipt=receipt, gate_result={"allowed": True},
        audit_entries=entries, audit_anchor_prev_hash=anchor)


def deny_input(*, tmp_path: Path | None = None) -> EvidenceInput:
    tmp = tmp_path or Path(tempfile.mkdtemp())
    # DENY: no signed token, no receipt — only denial + audit evidence.
    entries, anchor = _audit_slice(tmp, "deny-op-1", executed=False)
    return EvidenceInput(
        verdict="DENY", actor_id="agent/ops", resource_id="db/users",
        action="delete_resource", correlation_id="corr-deny",
        denial={"verdict": "DENY", "reason": "no mandate authorizes delete_resource",
                "decision_id": "deny-op-1"},
        gate_result={"allowed": False, "reason": "DENY"},
        audit_entries=entries, audit_anchor_prev_hash=anchor)
