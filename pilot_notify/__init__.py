"""Real Governed Executor Pilot — mock notification service + receipt-verifying
governed-executor adapter.

The adapter plugs into the *existing* production governed execution path
(``GovernanceService.upstream`` -> ``coordinator.enforce``). It performs the real
outbound HTTP call to the mock notification service and verifies the returned
receipt; if the receipt is missing, non-2xx, or does not match the executed
payload + correlation id, it raises — so ``coordinator.enforce`` records a
non-EXECUTED result. EXECUTED therefore means a genuine, confirmed external
receipt, never a queued/assumed/attempted call.
"""

from .governed_upstream import UpstreamReceiptError, payload_sha256, receipt_verifying_upstream
from .service import build_notification_service, recorded_receipts, reset_receipts

__all__ = [
    "UpstreamReceiptError",
    "payload_sha256",
    "receipt_verifying_upstream",
    "build_notification_service",
    "recorded_receipts",
    "reset_receipts",
]
