"""Shared fixtures for the pilot/reference_python acceptance test suite.

Puts ``sdk/mcc-sdk/src`` and ``pilot/reference_python``'s parent on
``sys.path`` the same way ``tests/mcc_sdk/conftest.py`` does -- no editable
install required. The real-gateway fixture reuses ``examples._demo_server``
and is module-scoped (never session-scoped), matching the fix established in
PR #81 for ``tests/mcc_sdk/conftest.py``'s own ``gateway_url`` fixture: a
server held open for the whole test session interferes with
``tests/test_demo_server.py``'s own lifecycle tests elsewhere in the suite.
"""

from __future__ import annotations

import sys
from collections.abc import Iterator
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "sdk" / "mcc-sdk" / "src"))
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from examples._demo_server import DemoServer, free_port


@pytest.fixture(scope="module")
def gateway_url() -> Iterator[tuple[str, str]]:
    """A real, running gateway.app instance on loopback. Module-scoped to
    avoid the cross-test interference documented in PR #81 for a
    session-scoped equivalent."""
    import gateway.app as gw

    port = free_port()
    server = DemoServer(gw.app, port)
    server.start()
    try:
        yield f"http://127.0.0.1:{port}", gw.settings.api_key
    finally:
        server.stop()
