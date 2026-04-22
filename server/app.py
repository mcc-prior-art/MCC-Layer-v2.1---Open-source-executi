#!/usr/bin/env python3
"""
MCC Policy Engine — production-grade single-file reference

Гарантии:
- Fail-closed: любой сбой => DENY
- Строгая схема (Pydantic, ограничения размеров)
- Tenant isolation + scopes (RBAC-lite)
- Idempotency (защита от повторных вызовов)
- Policy timeout
- Rate limiting (in-memory с блокировкой)
- Tamper-evident audit (hash chain)
- Структурированные error codes
- Correlation (trace_id + request_id)
- Health / Ready endpoints

NOTE:
- Для реального продакшена заменить:
  * API_KEYS → секрет-стор / KMS
  * rate limit → Redis / distributed
  * audit_log → append-only storage (DB / log pipeline)
"""

import os
import time
import json
import uuid
import hmac
import hashlib
import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional, Callable
from collections import defaultdict
from contextlib import suppress

from fastapi import FastAPI, HTTPException, Header, Depends
from pydantic import BaseModel, Field, root_validator

# =========================
# CONFIG
# =========================

MAX_INTENT_LENGTH = 64
MAX_ARGS_BYTES = 2048
POLICY_TIMEOUT_SEC = 0.2
RATE_LIMIT_PER_MIN = 60
BLOCK_WINDOW_SEC = 30

API_KEYS = {
    os.getenv("MCC_API_KEY", "demo-key"): {
        "tenant": "tenant_demo",
        "scopes": ["payments:write"]  # RBAC-lite
    }
}

# =========================
# LOGGING
# =========================

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("mcc")

# =========================
# MODELS
# =========================

class EvaluateRequest(BaseModel):
    session_id: str = Field(..., min_length=1, max_length=128)
    intent: str = Field(..., min_length=1, max_length=MAX_INTENT_LENGTH)
    args: Dict[str, Any]
    idempotency_key: Optional[str] = Field(default=None, max_length=128)

    @root_validator
    def check_args_size(cls, values):
        args = values.get("args", {})
        if len(json.dumps(args)) > MAX_ARGS_BYTES:
            raise ValueError("ARGS_TOO_LARGE")
        return values

class Reason(BaseModel):
    code: str
    message: str

class EvaluateResponse(BaseModel):
    decision: str  # ALLOW | DENY
    reason: Reason
    trace_id: str
    request_id: str

# =========================
# RATE LIMIT (thread-safe)
# =========================

rate_lock = asyncio.Lock()
rate_counters = defaultdict(list)
blocked_until = defaultdict(float)

async def check_rate_limit(tenant: str):
    async with rate_lock:
        now = time.time()

        if blocked_until[tenant] > now:
            raise HTTPException(status_code=429, detail="RATE_LIMIT_BLOCKED")

        window_start = now - 60
        rate_counters[tenant] = [t for t in rate_counters[tenant] if t > window_start]

        if len(rate_counters[tenant]) >= RATE_LIMIT_PER_MIN:
            blocked_until[tenant] = now + BLOCK_WINDOW_SEC
            raise HTTPException(status_code=429, detail="RATE_LIMIT_EXCEEDED")

        rate_counters[tenant].append(now)

# =========================
# AUTH
# =========================

def get_tenant(x_api_key: str = Header(...)):
    if x_api_key not in API_KEYS:
        raise HTTPException(status_code=401, detail="INVALID_API_KEY")
    return API_KEYS[x_api_key]

# =========================
# IDEMPOTENCY CACHE
# =========================

idempotency_cache: Dict[str, EvaluateResponse] = {}

# =========================
# MCC CORE
# =========================

class MCC:
    def __init__(self):
        self.prev_hash = "GENESIS"
        self.audit_log = []
        self.lock = asyncio.Lock()

    def _hash(self, payload: str) -> str:
        return hashlib.sha256(payload.encode()).hexdigest()

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    async def _audit(self, tenant: str, req: EvaluateRequest,
                     decision: str, reason: Reason,
                     trace_id: str, request_id: str):
        async with self.lock:
            record = {
                "timestamp": self._now(),
                "tenant": tenant,
                "request": req.dict(),
                "decision": decision,
                "reason": reason.dict(),
                "trace_id": trace_id,
                "request_id": request_id,
                "prev_hash": self.prev_hash
            }

            serialized = json.dumps(record, sort_keys=True)
            current_hash = self._hash(self.prev_hash + serialized)

            self.prev_hash = current_hash
            self.audit_log.append({**record, "hash": current_hash})

    async def evaluate(self, tenant_ctx: Dict[str, Any], req: EvaluateRequest) -> EvaluateResponse:
        tenant = tenant_ctx["tenant"]
        scopes = tenant_ctx["scopes"]
        request_id = str(uuid.uuid4())
        trace_id = hashlib.sha256((request_id + req.session_id).encode()).hexdigest()[:12]

        # Idempotency
        if req.idempotency_key and req.idempotency_key in idempotency_cache:
            return idempotency_cache[req.idempotency_key]

        try:
            result = await asyncio.wait_for(
                self._evaluate_internal(scopes, req, trace_id, request_id),
                timeout=POLICY_TIMEOUT_SEC
            )
        except asyncio.TimeoutError:
            result = EvaluateResponse(
                decision="DENY",
                reason=Reason(code="POLICY_TIMEOUT", message="timeout"),
                trace_id=trace_id,
                request_id=request_id
            )
        except Exception:
            result = EvaluateResponse(
                decision="DENY",
                reason=Reason(code="INTERNAL_ERROR", message="fail-closed"),
                trace_id=trace_id,
                request_id=request_id
            )

        await self._audit(tenant, req, result.decision, result.reason, trace_id, request_id)

        if req.idempotency_key:
            idempotency_cache[req.idempotency_key] = result

        logger.info(f"{tenant} {req.intent} -> {result.decision}")
        return result

    async def _evaluate_internal(self, scopes, req, trace_id, request_id):
        intent = req.intent
        args = req.args

        # POLICY: PAYMENT
        if intent == "send_payment":
            if "payments:write" not in scopes:
                return EvaluateResponse("DENY", Reason("FORBIDDEN_SCOPE", "scope required"), trace_id, request_id)

            amount = args.get("amount", 0)

            if amount <= 10000:
                return EvaluateResponse("ALLOW", Reason("PAYMENT_OK", "within limit"), trace_id, request_id)

            return EvaluateResponse("DENY", Reason("PAYMENT_LIMIT", "too large"), trace_id, request_id)

        # POLICY: DELETE USER
        if intent == "delete_user":
            return EvaluateResponse("DENY", Reason("DESTRUCTIVE_FORBIDDEN", "not allowed"), trace_id, request_id)

        # DEFAULT
        return EvaluateResponse("DENY", Reason("UNKNOWN_INTENT", "not allowed"), trace_id, request_id)

# =========================
# APP
# =========================

app = FastAPI(title="MCC Policy Engine", version="1.0")
mcc = MCC()

@app.post("/evaluate", response_model=EvaluateResponse)
async def evaluate(req: EvaluateRequest, tenant_ctx: Dict = Depends(get_tenant)):
    await check_rate_limit(tenant_ctx["tenant"])
    return await mcc.evaluate(tenant_ctx, req)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/ready")
def ready():
    return {"ready": True}
