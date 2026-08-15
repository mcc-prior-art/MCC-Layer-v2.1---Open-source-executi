from __future__ import annotations

import sys
from pathlib import Path

import pytest

CONTROL_ROOM_DIR = Path(__file__).resolve().parents[1]
ROOT = CONTROL_ROOM_DIR.parents[1]
for _p in (str(ROOT), str(ROOT / "src"), str(ROOT / "sdk" / "python" / "src"), str(CONTROL_ROOM_DIR)):
    if _p not in sys.path:
        sys.path.insert(0, _p)


@pytest.fixture(scope="session")
def runtime():
    """One real MCC-Core gateway + mock upstream for the whole test session.

    ``backend.runtime.start_demo_runtime`` imports ``gateway.app`` at module
    level, so it can only meaningfully run once per process -- session scope
    here matches that constraint and avoids re-binding ports/state.
    """
    from backend.runtime import start_demo_runtime

    rt = start_demo_runtime()
    yield rt
    rt.stop()
