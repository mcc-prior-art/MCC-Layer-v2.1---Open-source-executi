"""Mock clinic service — the controlled external system the clinic pilot acts on.

It receives the governed outbound call at ``POST /{action_type}`` (e.g.
``/appointment_book``, ``/discount_offer``), records the action, and returns a
deterministic receipt confirming exactly what it received:

    received, receipt_id, correlation_id, action_type, actor_id,
    payload_sha256, status, timestamp

The governed-executor adapter (``pilot_notify.receipt_verifying_upstream``, reused
unchanged) verifies ``received`` + ``correlation_id`` + ``payload_sha256`` before
EXECUTED is reported. A request without a correlation id is rejected (no receipt).

The ``payload_sha256`` is computed over the exact received body, so it binds the
receipt to the payload MCC-Core authorized (the CLAMPED body for CONSTRAIN, never
the original).
"""

from __future__ import annotations

import threading
import time
from typing import Any, Dict, List

from fastapi import FastAPI, HTTPException, Request

from pilot_notify.governed_upstream import payload_sha256


class _State:
    def __init__(self) -> None:
        self.lock = threading.Lock()
        self.actions: List[Dict[str, Any]] = []
        self.seq = 0

    def record(self, action_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        with self.lock:
            self.seq += 1
            receipt = {
                "received": True,
                "receipt_id": f"clinic-rcpt-{self.seq}",
                "correlation_id": payload.get("correlation_id"),
                "action_type": action_type,
                "actor_id": payload.get("actor_id"),
                "payload_sha256": payload_sha256(payload),
                "status": "executed",
                "timestamp": int(time.time()),
            }
            self.actions.append({"action_type": action_type, "payload": payload, "receipt": receipt})
            return receipt


_STATE = _State()


def reset_actions() -> None:
    global _STATE
    _STATE = _State()


def recorded_actions() -> List[Dict[str, Any]]:
    return list(_STATE.actions)


_KNOWN_ACTIONS = {
    "appointment_book", "appointment_confirm", "patient_message_send",
    "lead_qualify", "discount_offer", "priority_mark", "refund_request",
    "complaint_escalate",
}


def build_clinic_service() -> FastAPI:
    app = FastAPI(title="AXFlow Clinic Pilot — Mock Clinic Service")

    @app.get("/health")
    def health() -> Dict[str, Any]:
        return {"status": "ok", "service": "mock-clinic", "actions": len(_STATE.actions)}

    @app.get("/actions")
    def actions() -> Dict[str, Any]:
        return {"count": len(_STATE.actions), "actions": recorded_actions()}

    @app.post("/{action_type}")
    async def perform(action_type: str, request: Request) -> Dict[str, Any]:
        if action_type not in _KNOWN_ACTIONS:
            raise HTTPException(status_code=404, detail=f"unknown clinic action '{action_type}'")
        try:
            payload = await request.json()
        except Exception as exc:  # noqa: BLE001
            raise HTTPException(status_code=400, detail="body was not JSON") from exc
        if not isinstance(payload, dict) or not payload.get("correlation_id"):
            # Fail-closed: no correlation id -> no receipt (execution cannot verify).
            raise HTTPException(status_code=422, detail="missing correlation_id")
        return _STATE.record(action_type, payload)

    return app


app = build_clinic_service()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=9300, log_level="info")
