"""Real external-effect sink subprocess (PR #71).

Boots the existing, unmodified ``pilot_notify`` mock notification service --
the observable "external world" a governed action actually reaches.
Exposes ``POST /send_notification`` (what the actuator calls) and
``GET /receipts`` (what the assurance suite polls, over real HTTP, to
independently confirm whether an external effect occurred) so effect
counting never depends on in-process module state shared with the
service under test.

    python -m assurance.sut.notify_process --port N
"""

from __future__ import annotations

import argparse

from pilot_notify.service import build_notification_service


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, required=True)
    ap.add_argument("--host", default="127.0.0.1")
    args = ap.parse_args()

    import uvicorn

    uvicorn.run(build_notification_service(), host=args.host, port=args.port, log_level="warning")


if __name__ == "__main__":
    main()
