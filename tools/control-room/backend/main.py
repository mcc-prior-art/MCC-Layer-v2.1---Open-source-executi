"""Foreground process entrypoint for the Control Room demonstration.

Starts the real MCC-Core gateway + mock upstream (:mod:`runtime`), then the
Control Room's own backend-for-frontend (:mod:`server`) on top of it, all
bound to ``127.0.0.1``. Blocks until asked to stop (SIGTERM/SIGINT or
Ctrl+C), then tears everything down in reverse order.

Not meant to be imported by anything outside ``tools/control-room`` -- run
via ``start.py`` (which also supports a detached/background mode) or
directly with ``python tools/control-room/backend/main.py``.
"""

from __future__ import annotations

import json
import os
import signal
import sys
import threading
from pathlib import Path

_HERE = Path(__file__).resolve()
CONTROL_ROOM_DIR = _HERE.parents[1]  # tools/control-room (hyphenated; not a valid dotted package)
ROOT = _HERE.parents[3]
for _p in (str(ROOT), str(CONTROL_ROOM_DIR)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from examples._demo_server import DemoServer, free_port  # noqa: E402

from backend.runtime import start_demo_runtime  # noqa: E402
from backend.server import create_app  # noqa: E402

RUN_DIR = CONTROL_ROOM_DIR / ".run"
INSTANCE_FILE = RUN_DIR / "instance.json"
DEFAULT_PORT = 8765


def main() -> int:
    RUN_DIR.mkdir(parents=True, exist_ok=True)

    port_env = os.environ.get("MCC_CONTROL_ROOM_PORT", "").strip()
    port = int(port_env) if port_env else DEFAULT_PORT

    print("== MCC-Core Control Room: starting the REAL gateway + mock upstream ==")
    rt = start_demo_runtime()
    print(f"   real gateway:  {rt.gateway_url}")

    app = create_app(rt)
    try:
        bff_server = DemoServer(app, port).start()
    except RuntimeError:
        # Requested port taken; fall back to an OS-assigned free port.
        port = free_port()
        bff_server = DemoServer(app, port).start()

    url = f"http://127.0.0.1:{port}/"
    INSTANCE_FILE.write_text(json.dumps({
        "pid": os.getpid(), "control_room_port": port, "gateway_url": rt.gateway_url,
        "url": url,
    }, indent=2), encoding="utf-8")

    print(f"\n== MCC-Core Control Room is READY ==")
    print(f"   Local Self-Administered Demonstration — Not a Production Administrative Console")
    print(f"   Open in your browser: {url}")
    print(f"   Stop with: python tools/control-room/stop.py  (or Ctrl+C in this terminal)\n")

    stop_event = threading.Event()

    def _handle_stop(signum, frame) -> None:  # noqa: ANN001, ARG001
        stop_event.set()

    signal.signal(signal.SIGTERM, _handle_stop)
    signal.signal(signal.SIGINT, _handle_stop)

    try:
        stop_event.wait()
    finally:
        print("\n== MCC-Core Control Room: shutting down ==")
        try:
            bff_server.stop()
        finally:
            rt.stop()
        try:
            INSTANCE_FILE.unlink()
        except FileNotFoundError:
            pass
        print("== stopped ==")
    return 0


if __name__ == "__main__":
    sys.exit(main())
