"""Shared fixtures for the mcc_sdk test suite.

Puts ``sdk/mcc-sdk/src`` on ``sys.path`` the same way ``tests/
test_mcc_client_sdk.py`` does for ``sdk/python/src`` -- no editable install
is required in the main CI ``tests`` job, matching the repo's existing
convention for the sibling SDK package.
"""

from __future__ import annotations

import socket
import sys
from pathlib import Path
from typing import Iterator, Tuple

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "sdk" / "mcc-sdk" / "src"))
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from examples._demo_server import DemoServer, free_port  # noqa: E402


@pytest.fixture(scope="module")
def gateway_url() -> Iterator[Tuple[str, str]]:
    """A real, running gateway.app instance on loopback, for genuine
    request/response integration testing (not a mock). Module-scoped (not
    session-scoped) to match the established precedent in
    tests/test_mcc_client_sdk.py's own gateway_url fixture -- a server held
    open for the whole test session adds avoidable thread/port contention
    across the full ~2000-test suite."""
    import gateway.app as gw

    port = free_port()
    server = DemoServer(gw.app, port)
    server.start()
    try:
        yield f"http://127.0.0.1:{port}", gw.settings.api_key
    finally:
        server.stop()


def _unused_port() -> int:
    """A bindable-but-currently-closed port, for genuine connection-refused
    transport-failure tests (nothing is listening there)."""
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


@pytest.fixture()
def closed_port_url() -> str:
    return f"http://127.0.0.1:{_unused_port()}"
