"""Purpose-built detectors for defects the existing test suites do not
directly exercise (PR #71, Workstream J).

Investigating the first mutation run's surviving mutants showed each
survivor was a genuine detector-selection problem, not a real coverage
gap masked to inflate a score:

* ``gate-fail-open`` -- no existing test drives ``ExecutionGate._verify``'s
  bare ``except Exception`` catch-all specifically (every existing test
  triggers one of the EXPLICIT rejection branches, which never raise).
* ``nonce-replay-allowed`` -- ``tests/test_nonce.py::test_replay_is_denied``
  tests ``RedisNonceRegistry``, not ``InMemoryNonceRegistry`` (what this
  SUT actually uses by default) -- searching the whole repository found NO
  existing test of ``InMemoryNonceRegistry.consume``'s replay rejection at
  all. This is a genuine, reportable gap in the PRE-EXISTING suite,
  independent of this assurance baseline.
* ``audit-before-actuation-bypassed`` -- the existing ordering test only
  exercises the successful-write path, where ``pre_ref`` is never ``None``
  to begin with.
* ``challenge-replay-allowed`` -- ``InMemoryChallengeRegistry.consume`` has
  a SECOND, independent single-use guard (``rec.state != ISSUED``) that
  already rejects a second consume before the mutated ``_consumed``-set
  check is ever reached -- true within-function redundancy, not a
  cross-module defense-in-depth story. The defect target was moved to the
  state check, which is the one actually load-bearing for a normal replay.

Kept as its own small module (not inside ``assurance/``) because these are
neither black-box SUT tests nor a good fit for the existing ``tests/``
suite's own fixtures -- they exist specifically to give Workstream J's 13
targeted mutations complete, honest detection coverage.
"""

from __future__ import annotations

import asyncio

import pytest

from mcc_core import DecisionEngine, ExecutionGate, SigningKey, Verdict
from mcc_core.nonce import InMemoryNonceRegistry

run = asyncio.run
NOW = 1_780_000_000


def test_gate_exception_path_fails_closed():
    """A nonce registry that raises (rather than cleanly returning False,
    which ``RedisNonceRegistry``/``InMemoryNonceRegistry`` both already do
    internally) must still resolve to DENY via the outer catch-all -- never
    ALLOW."""

    class ExplodingNonceRegistry:
        async def consume(self, nonce, ttl_seconds=300):  # noqa: ARG002
            raise RuntimeError("simulated unexpected internal failure")

    signing_key = SigningKey.generate("test-key-1")
    engine = DecisionEngine(
        signing_key=signing_key, issuer="mcc/test", audience="execution-gate-1",
        policy_id="test-policy", policy_hash="sha256:policyhash", token_ttl_seconds=60,
    )
    token = engine.issue_token(
        verdict=Verdict.ALLOW, subject="agent/test", action="send_payment",
        payload={"amount": 100}, constraints={}, audit_ref="auditref", now=NOW,
    )
    gate = ExecutionGate(
        trusted_keys={signing_key.kid: signing_key.public_key()}, audience="execution-gate-1",
        nonce_registry=ExplodingNonceRegistry(), policy_hash="sha256:policyhash",
    )

    result = run(gate.verify(token, now=NOW))

    assert not result.allowed
    assert "fail-closed" in result.reason.lower() or "GATE_ERROR" in result.reason


def test_in_memory_nonce_registry_rejects_replay():
    """``InMemoryNonceRegistry`` -- the default this SUT actually runs --
    must reject a second ``consume`` of the same nonce, mirroring
    ``tests/test_nonce.py::test_replay_is_denied`` (which only covers
    ``RedisNonceRegistry``)."""
    registry = InMemoryNonceRegistry()

    first = run(registry.consume("n1"))
    second = run(registry.consume("n1"))

    assert first is True
    assert second is False


def test_coordinator_denies_when_pre_actuation_audit_write_fails(tmp_path):
    """When the durable pre-actuation audit write itself fails (``_record``
    returns ``None``), the coordinator must fail closed and never reach
    actuation -- audit-before-actuation is a hard gate, not best-effort."""
    from tests.test_coordinator import build, payment, runner  # reuse, not duplicate

    engine, coord, _audit = build(tmp_path)
    token, payload = payment(engine, idem="op-audit-fail")

    class AlwaysFailingAudit:
        path = str(tmp_path / "unused-audit.jsonl")

        def append(self, _fields):
            raise OSError("simulated durable-write failure")

    coord.audit = AlwaysFailingAudit()
    calls = []

    result = run(coord.enforce(
        token=token, action="send_payment", payload=payload,
        executor=runner(calls), now=NOW,
    ))

    assert result.status.name != "EXECUTED"
    assert calls == []  # the executor must never have been reached
