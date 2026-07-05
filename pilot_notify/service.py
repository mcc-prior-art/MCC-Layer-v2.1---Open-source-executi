"""Mock notification service — the local external system the pilot notifies.

A real, separate HTTP service (no governance logic). It receives the governed
outbound call at ``POST /send_notification``, records the notification, and
returns a receipt confirming exactly what it received: ``received``, a
``receipt_id``, the ``correlation_id``, and a ``payload_sha256`` fingerprint of
the received body. The governed-executor adapter verifies that receipt before
EXECUTED is reported. Malformed requests are rejected (no receipt).
"""

from __future__ import annotations

import threading
from typing import Any, Dict, List, Optional

from fastapi import FastAPI
from pydantic import BaseModel, ConfigDict, Field

from .governed_upstream import payload_sha256


class _State:
    def __init__(self) -> None:
        self.lock = threading.Lock()
        self.receipts: List[Dict[str, Any]] = []
        self.seq = 0

    def record(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        with self.lock:
            self.seq += 1
            receipt = {
                "received": True,
                "receipt_id": f"rcpt-{self.seq}",
                "correlation_id": payload.get("correlation_id"),
                "payload_sha256": payload_sha256(payload),
            }
            self.receipts.append({"payload": payload, "receipt": receipt})
            return receipt


_STATE = _State()


def reset_receipts() -> None:
    global _STATE
    _STATE = _State()


def recorded_receipts() -> List[Dict[str, Any]]:
    return list(_STATE.receipts)


class NotificationIn(BaseModel):
    model_config = ConfigDict(extra="forbid")
    recipient: str = Field(min_length=1)
    message: str = Field(min_length=1)
    correlation_id: str = Field(min_length=1)
    priority: Optional[int] = Field(default=None, ge=1, le=9)
    channel: Optional[str] = None


def build_notification_service() -> FastAPI:
    app = FastAPI(title="MCC-Core Pilot — Mock Notification Service")

    @app.get("/health")
    def health() -> Dict[str, Any]:
        return {"status": "ok", "service": "mock-notification",
                "receipts": len(_STATE.receipts)}

    @app.get("/receipts")
    def receipts() -> Dict[str, Any]:
        return {"count": len(_STATE.receipts), "receipts": recorded_receipts()}

    @app.post("/send_notification")
    def send_notification(body: NotificationIn) -> Dict[str, Any]:
        # Record and confirm exactly what was received.
        receipt = _STATE.record(body.model_dump(exclude_none=True))
        return receipt

    return app


app = build_notification_service()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=9200, log_level="info")
