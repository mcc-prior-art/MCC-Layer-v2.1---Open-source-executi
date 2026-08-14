"""Workstream A extension -- Network Segmentation / Bypass Resistance (PR #71).

Closes the exact limitation ``docs/EXCLUSIVE_EXECUTION_PATH.md``'s A6 attack
states explicitly: A6 proves the actuator's OWN application-level
SSRF/allowlist works, but "does NOT prove that an attacker with raw network
access to the notify sink (bypassing the actuator's process entirely) could
not reach it directly." This module builds a REAL, kernel-enforced network
boundary (Linux network namespaces + veth links -- no Docker; this
environment's Docker Hub pulls are policy-blocked, see
``docs/ASSUMPTIONS_AND_LIMITS.md``) and proves both halves of the claim:

* N1 -- the governed path still works end-to-end ACROSS the real network
  boundary (the actuator reaches the segmented upstream and executes).
* N2 -- an attacker on the HOST, with a real HTTP client and zero
  cooperation from any MCC-Core code, cannot open a TCP connection to the
  protected upstream at all. This is a network-layer failure
  (``ConnectError``/``ConnectTimeout``), not an application-level DENY --
  the strictly stronger claim A6's own docstring said this single-host
  suite could not observe.

Requires ``CAP_NET_ADMIN`` (this environment runs as root) and ``iproute2``.
Skips cleanly if either is unavailable, matching this baseline's existing
environment-gating convention (see ``test_semantic_equivalence.py``).
"""

from __future__ import annotations

import pytest

from assurance.sut.network_segmentation import NetnsUnavailableError, build_segmented_topology


@pytest.fixture(scope="module")
def topology():
    try:
        with build_segmented_topology() as t:
            yield t
    except NetnsUnavailableError as e:
        pytest.skip(f"real network-namespace topology unavailable in this environment: {e}")


def test_n1_governed_flow_executes_across_the_real_network_boundary(topology):
    """Baseline: the actuator, running in its own network namespace, reaches
    the upstream sink -- ALSO in its own, separate network namespace, with
    no route back to the host -- across a real veth link and executes a
    fully governed action. Proves the segmented topology is not merely
    "unreachable," it is a genuine, working deployment."""
    before = topology.receipt_count_privileged()

    proposal = topology.propose()
    assert proposal["outcome"] == "CONSENSUS_REQUIRED"
    votes = topology.votes(payload=topology.canonical_action(proposal["_request"]), nonce=proposal["nonce"])
    result = topology.submit(proposal=proposal, votes=votes)

    assert result["outcome"] == "ALLOW"
    assert result["executed"] is True
    assert topology.receipt_count_privileged() == before + 1


def test_n2_direct_bypass_from_host_fails_at_the_network_layer(topology):
    """The core claim: from the HOST's default network namespace (where a
    real attacker on this machine would run), attempt to reach the
    protected upstream DIRECTLY -- no actuator, no governance, no consensus,
    no MCC-Core code involved in the attempt at all. This must fail as a
    NETWORK-layer error (no route / connection timeout), not merely an
    HTTP-layer rejection -- proving the boundary is enforced by the kernel's
    routing tables, independent of any governance decision the actuator
    could be tricked into skipping."""
    before = topology.receipt_count_privileged()

    error = topology.attempt_direct_bypass_from_host()

    assert error is not None, (
        "a direct connection from the host to the protected upstream "
        "SUCCEEDED -- the network segmentation boundary is not enforced"
    )
    assert error in ("ConnectError", "ConnectTimeout")
    assert topology.receipt_count_privileged() == before, "the bypass attempt must have zero external effect"


def test_n3_actuator_inbound_api_remains_reachable_from_the_host(topology):
    """Sanity check on the topology itself: the host's inability to reach
    the UPSTREAM (N2) is not an accident of a broken network -- the same
    host CAN, and must, still reach the actuator's own inbound API (that is
    the one legitimate path into this deployment). Distinguishes "the
    topology is segmented as designed" from "the topology is just broken"."""
    import httpx

    r = httpx.get(f"{topology.actuator_url}/health", timeout=5.0)
    assert r.status_code == 200
