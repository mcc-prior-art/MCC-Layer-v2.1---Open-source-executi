"""Public API contract for the ``mcc`` facade (PR #40).

``mcc`` is a thin, stable import namespace that re-exports the supported
``mcc_client`` SDK unchanged. These tests pin that contract:

* every documented symbol imports;
* each re-export is the *identical* object from ``mcc_client`` (not a copy);
* the facade adds NO governance surface of its own — no local ``authorize``,
  no transport/signing/policy logic, no extra public functions or classes.

This is what keeps the facade honest: it cannot drift into a second SDK or make
local governance decisions, because it defines no behavior of its own.
"""

from __future__ import annotations

import mcc
import mcc_client

# The stable public names the facade promises (mirrors mcc.__all__ minus dunder).
_PUBLIC = [
    "MCCClient", "Authorization", "Transport",
    "Verdict", "Decision", "Approval", "ExecutionResult",
    "ApprovalAuthorization", "MandateAuthorization", "ConsensusAuthorization",
    "Payload",
    "MCCError", "MCCTransportError", "MCCTimeoutError", "MCCProtocolError",
    "MCCAuthenticationError", "MCCDeniedError", "MCCApprovalRequiredError",
    "MCCInvalidDecisionError", "MCCReplayError", "MCCExecutionError",
    "MCCAmbiguousExecutionError",
]


def test_facade_imports_and_versions():
    from mcc import MCCClient  # noqa: F401 — the headline import must work

    assert isinstance(mcc.__version__, str) and mcc.__version__
    assert isinstance(mcc.client_version, str) and mcc.client_version
    assert mcc.client_version == mcc_client.__version__


def test_every_public_symbol_is_exported_and_identical():
    for name in _PUBLIC:
        assert hasattr(mcc, name), f"mcc is missing public symbol {name!r}"
        assert getattr(mcc, name) is getattr(mcc_client, name), (
            f"mcc.{name} must be the SAME object as mcc_client.{name} (no copies)"
        )


def test_all_matches_and_covers_client_public_surface():
    assert set(mcc.__all__) == set(_PUBLIC) | {"__version__", "client_version"}
    # Nothing the client exports publicly is silently dropped by the facade.
    for name in mcc_client.__all__:
        if name.startswith("__"):
            continue
        assert name in mcc.__all__, f"facade drops client symbol {name!r}"


def test_facade_defines_no_logic_of_its_own():
    # The facade module must not define its own functions/classes (only
    # re-exports + version constants). This structurally prevents it from
    # growing local governance/transport/signing behavior.
    import types

    owned = [
        n for n, v in vars(mcc).items()
        if not n.startswith("__")
        and isinstance(v, (types.FunctionType, type))
        and getattr(v, "__module__", "").startswith("mcc")
        and not getattr(v, "__module__", "").startswith("mcc_client")
    ]
    assert owned == [], f"facade defines its own objects (must only re-export): {owned}"


def test_no_misleading_local_authorize_api():
    # Authorization is performed remotely by the gateway. The facade must not
    # expose a local ``authorize`` that would misrepresent the architecture.
    assert not hasattr(mcc, "authorize")
    assert not hasattr(mcc, "MCC")
    # The client evaluates (proposes) and executes through the governed path;
    # it does not locally decide.
    assert hasattr(mcc.MCCClient, "evaluate")
    assert hasattr(mcc.MCCClient, "execute")
    assert not hasattr(mcc.MCCClient, "authorize")


def test_client_surface_unchanged_by_facade():
    # The facade re-exports the exact class; its public method set is the
    # client's, unmodified.
    facade_methods = {m for m in dir(mcc.MCCClient) if not m.startswith("_")}
    client_methods = {m for m in dir(mcc_client.MCCClient) if not m.startswith("_")}
    assert facade_methods == client_methods
