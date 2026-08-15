#!/usr/bin/env python3
"""Stop the MCC-Core Control Room demonstration.

    python tools/control-room/stop.py

Reads the PID written by ``start.py``, sends it a graceful shutdown signal
(SIGTERM), and waits for it to exit. The running process itself tears down
the real gateway, the mock upstream, and its own BFF server before exiting
(see ``backend/main.py``), so no separate cleanup step is needed here.
"""

from __future__ import annotations

import json
import os
import signal
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
INSTANCE_FILE = HERE / ".run" / "instance.json"
STOP_TIMEOUT_SECONDS = 15.0


def _pid_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True


def main() -> int:
    if not INSTANCE_FILE.is_file():
        print("not running: no tools/control-room/.run/instance.json found.")
        return 0

    info = json.loads(INSTANCE_FILE.read_text(encoding="utf-8"))
    pid = info["pid"]

    if not _pid_alive(pid):
        print(f"process {pid} is not running; removing stale instance file.")
        INSTANCE_FILE.unlink(missing_ok=True)
        return 0

    print(f"stopping MCC-Core Control Room (pid {pid}) ...")
    os.kill(pid, signal.SIGTERM)

    deadline = time.monotonic() + STOP_TIMEOUT_SECONDS
    while time.monotonic() < deadline:
        if not _pid_alive(pid):
            print("stopped.")
            return 0
        time.sleep(0.25)

    print(f"process {pid} did not exit within {STOP_TIMEOUT_SECONDS:.0f}s; "
          f"it may still be shutting down.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
