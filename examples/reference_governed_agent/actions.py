"""The pilot action the reference agent proposes: ``send_notification``.

A tiny, auditable mapping from a parsed request to the governed action payload
(recipient, message, priority, channel, correlation_id). No governance here.
"""

from __future__ import annotations

import re
import uuid
from typing import Any, Dict

ACTION = "send_notification"
RESOURCE = "notification-service"

# Priority words -> the numeric priority the policy bounds (max_priority cap).
_PRIORITY = {"low": 1, "normal": 2, "high": 9, "urgent": 9, "critical": 9}


def new_correlation_id() -> str:
    return f"corr-{uuid.uuid4().hex}"


def build_notification_payload(
    *, recipient: str, message: str, priority: str = "normal",
    channel: str = "email", correlation_id: str | None = None,
) -> Dict[str, Any]:
    prio = _PRIORITY.get(str(priority).strip().lower(), 2)
    return {
        "recipient": recipient,
        "message": message,
        "priority": prio,
        "channel": channel,
        "correlation_id": correlation_id or new_correlation_id(),
    }


def parse_request(request: str) -> Dict[str, str]:
    """Deterministically extract a recipient + message from a NL request.

    e.g. "Notify customer-123 that the appointment is confirmed" ->
         {recipient: customer-123, message: "the appointment is confirmed"}.
    Falls back to a default recipient/message so a proposal can always form."""
    text = request.strip()
    m = re.search(r"\b([A-Za-z][\w-]*-\d+|customer[\w-]*)\b", text)
    recipient = m.group(1) if m else "customer-000"
    msg = re.split(r"\bthat\b", text, maxsplit=1)
    message = msg[1].strip() if len(msg) > 1 and msg[1].strip() else text
    return {"recipient": recipient, "message": message}
