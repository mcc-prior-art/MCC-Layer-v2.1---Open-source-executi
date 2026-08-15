#!/usr/bin/env python3
"""Start the MCC-Core Control Room demonstration.

    python tools/control-room/start.py

Starts the real MCC-Core gateway, a local mock actuation target, and the
Control Room's browser UI, all bound to 127.0.0.1. Runs detached in the
background by default (like ``docker compose up -d``); prints the browser
URL once ready, then returns.

    python tools/control-room/start.py --foreground

Runs in the current terminal instead; stop with Ctrl+C.

Shutdown (background mode):

    python tools/control-room/stop.py
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUN_DIR = HERE / ".run"
INSTANCE_FILE = RUN_DIR / "instance.json"
LOG_FILE = RUN_DIR / "control-room.log"
READY_TIMEOUT_SECONDS = 60.0


def _wait_ready(timeout: float = READY_TIMEOUT_SECONDS) -> dict:
    deadline = time.monotonic() + timeout
    last_error: Exception | None = None
    while time.monotonic() < deadline:
        if INSTANCE_FILE.is_file():
            try:
                info = json.loads(INSTANCE_FILE.read_text(encoding="utf-8"))
                with urllib.request.urlopen(info["url"] + "api/health", timeout=2) as resp:
                    if resp.status == 200:
                        return info
            except (OSError, urllib.error.URLError, json.JSONDecodeError, KeyError) as exc:
                last_error = exc
        time.sleep(0.25)
    raise RuntimeError(
        f"Control Room did not become ready within {timeout:.0f}s"
        + (f" (last error: {last_error})" if last_error else "")
    )


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--foreground", action="store_true",
                    help="run in this terminal instead of detached in the background")
    args = ap.parse_args()

    if INSTANCE_FILE.is_file():
        print(f"already running: {INSTANCE_FILE} exists. "
              f"Run tools/control-room/stop.py first if this is stale.")
        return 1

    if args.foreground:
        return subprocess.call([sys.executable, str(HERE / "backend" / "main.py")])

    RUN_DIR.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "ab") as log:
        proc = subprocess.Popen(
            [sys.executable, str(HERE / "backend" / "main.py")],
            stdout=log, stderr=subprocess.STDOUT,
            cwd=str(HERE), start_new_session=True,
        )
    print(f"starting MCC-Core Control Room (pid {proc.pid}, logs: {LOG_FILE}) ...")
    try:
        info = _wait_ready()
    except RuntimeError as exc:
        print(f"FAILED: {exc}\nSee {LOG_FILE} for details.")
        return 1

    print("\nLocal Self-Administered Demonstration — Not a Production Administrative Console")
    print(f"Open in your browser: {info['url']}")
    print("Stop with: python tools/control-room/stop.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
