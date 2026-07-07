"""Regression guard for smoke/demo port-race flakiness (PR #39).

The intermittent smoke failures were a port race: two demos run back-to-back by
``scripts/smoke_stress.sh`` bound the *same* hardcoded ports (8001/8080/9009), so
a slow-to-release socket from one run could be picked up by the next, splitting
in-memory state. The fix is ephemeral ports via ``examples._demo_server.free_port``.

These tests keep that fix in place:
* ``free_port`` returns distinct, bindable ports (never the same one twice);
* the smoke demos use ``free_port`` and do not hardcode a fixed listen port.
"""

from __future__ import annotations

import re
import socket
from pathlib import Path

import pytest

from examples._demo_server import free_port

ROOT = Path(__file__).resolve().parents[1]

# The exact demo set that scripts/smoke_stress.sh runs sequentially — the ones
# whose shared fixed ports caused the flake.
SMOKE_DEMOS = [
    "examples/egress_proxy_demo.py",
    "examples/transaction_governance_demo.py",
    "examples/governance_http_demo.py",
    "examples/pilot_reference_integration.py",
    "examples/enforced_egress_agent.py",
]

# A hardcoded four-digit listen port assigned to a *_PORT name, e.g.
# ``GATEWAY_PORT = 8001`` or ``GATEWAY_PORT, UPSTREAM_PORT = 8011, 9011``.
_HARDCODED_PORT = re.compile(r"_PORT\b[^=\n]*=\s*[^\n]*\b\d{4}\b")


def test_free_port_returns_distinct_bindable_ports():
    ports = [free_port() for _ in range(20)]
    assert len(set(ports)) == len(ports), "free_port handed out a duplicate port"
    for p in ports:
        assert 1024 <= p <= 65535
    # The most recently issued port is actually bindable.
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind(("127.0.0.1", ports[-1]))
    finally:
        s.close()


@pytest.mark.parametrize("demo", SMOKE_DEMOS)
def test_smoke_demo_uses_ephemeral_ports(demo):
    src = (ROOT / demo).read_text(encoding="utf-8")
    assert "free_port" in src, f"{demo} must derive ports from free_port"
    offenders = [ln for ln in src.splitlines()
                 if _HARDCODED_PORT.search(ln) and "free_port" not in ln]
    assert not offenders, f"{demo} hardcodes a fixed port: {offenders}"
