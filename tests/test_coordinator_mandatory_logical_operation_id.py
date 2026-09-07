"""Round 25 remediation — MANDATORY logical_operation_id at the core execution
boundary.

Target invariant: NO VALID LOGICAL_OPERATION_ID -> ZERO ACTUATOR INVOCATIONS.

Before this round, ``EnforcementCoordinator.enforce()`` guarded every durable
step (``reserve``/``commit_dispatch``/``mark_executed``/``mark_unknown``) with
``if idem_key:`` -- purely optional. A genuinely valid, signed, executable
decision token carrying no idempotency_key (None, "", or whitespace) skipped
every durable admission/dispatch-ownership check entirely and still reached
the executor, with zero replay/duplicate protection.

These tests call ``EnforcementCoordinator.enforce()`` DIRECTLY (never routed
through the GPT-6 Astra reference integration's ``prepare_marked_call`` /
pipeline helpers, and never through ``GovernanceService``) with a genuinely
valid signed executable token, to prove the coordinator itself -- the one
domain-neutral enforcement point shared by every governed domain in this
repository -- is now the unavoidable authority for this invariant.
"""

import asyncio

import pytest

from mcc_core import (
    ActuationStatus,
    AuditLog,
    DecisionEngine,
    EnforcementCoordinator,
    ExecutionGate,
    InMemoryIdempotencyRegistry,
    InMemoryNonceRegistry,
    InMemoryVelocityRegistry,
    ProfileRegistry,
    SigningKey,
)

run = asyncio.run
NOW = 1_780_000_000


def build(tmp_path):
    key = SigningKey.generate("k1")
    engine = DecisionEngine(
        signing_key=key, issuer="mcc/test", audience="gate",
        policy_id="pilot/v1", policy_hash="sha256:p", token_ttl_seconds=60,
    )
    gate = ExecutionGate(
        trusted_keys={key.kid: key.public_key()}, audience="gate",
        nonce_registry=InMemoryNonceRegistry(), policy_hash="sha256:p",
    )
    audit = AuditLog(str(tmp_path / "audit.jsonl"))
    idempotency = InMemoryIdempotencyRegistry()
    coord = EnforcementCoordinator(
        gate=gate, idempotency=idempotency, velocity=InMemoryVelocityRegistry(),
        audit=audit, profiles=ProfileRegistry.default_pilot(),
    )
    return engine, coord, idempotency


def valid_executable_token(engine, *, idempotency_key, nonce="n-1"):
    """A genuinely valid, signed, executable (ALLOW) token: real signature,
    real action/resource/payload binding, real policy hash, real (non-expired)
    time window, real nonce -- the ONLY thing under test is the value of
    ``idempotency_key`` itself."""
    payload = {"amount": 100}
    return engine.issue_token(
        verdict="ALLOW", subject="agent/x", action="do_thing", payload=payload,
        actor_id="agent/x", resource_id="res-1", nonce=nonce,
        idempotency_key=idempotency_key, now=NOW,
    )


def counting_executor(calls):
    async def executor():
        calls.append(1)
        return {"ok": True}
    return executor


@pytest.mark.parametrize("bad_key", [None, "", "   ", "\t\n"])
def test_missing_or_blank_idempotency_key_blocks_before_executor(tmp_path, bad_key):
    engine, coord, idempotency = build(tmp_path)
    token = valid_executable_token(engine, idempotency_key=bad_key)
    calls = []

    result = run(coord.enforce(
        token=token, action="do_thing", payload={"amount": 100},
        executor=counting_executor(calls),
        request_binding={"actor_id": "agent/x", "resource_id": "res-1"},
        now=NOW,
    ))

    assert result.status == ActuationStatus.BLOCKED
    assert "MISSING_LOGICAL_OPERATION_ID" in result.reason
    assert calls == [], "the executor must NEVER be invoked without a valid logical_operation_id"
    # No durable dispatch ownership was ever created for any key.
    assert idempotency._store == {}  # type: ignore[attr-defined]


def test_non_string_idempotency_key_blocks_before_executor(tmp_path):
    """A token whose idempotency_key is present but not a string (e.g. a
    caller/JSON layer that let a number or list through) is exactly as
    invalid as a missing one -- never coerced, never silently accepted."""
    engine, coord, idempotency = build(tmp_path)
    # A genuinely, validly signed token whose idempotency_key is a non-string
    # value (not a post-signing tamper -- the signature covers this field, so
    # this is what a caller/JSON layer that let a number through would
    # actually produce and get signed).
    token = valid_executable_token(engine, idempotency_key=12345)
    calls = []

    result = run(coord.enforce(
        token=token, action="do_thing", payload={"amount": 100},
        executor=counting_executor(calls),
        request_binding={"actor_id": "agent/x", "resource_id": "res-1"},
        now=NOW,
    ))

    assert result.status == ActuationStatus.BLOCKED
    assert "MISSING_LOGICAL_OPERATION_ID" in result.reason
    assert calls == []


def test_valid_non_empty_idempotency_key_still_executes(tmp_path):
    """Positive control: the mandatory check does not regress the ordinary,
    correct path -- a genuinely valid token WITH a real logical_operation_id
    still actuates exactly as before."""
    engine, coord, idempotency = build(tmp_path)
    token = valid_executable_token(engine, idempotency_key="op-real-1")
    calls = []

    result = run(coord.enforce(
        token=token, action="do_thing", payload={"amount": 100},
        executor=counting_executor(calls),
        request_binding={"actor_id": "agent/x", "resource_id": "res-1"},
        now=NOW,
    ))

    assert result.status == ActuationStatus.EXECUTED
    assert calls == [1]
    assert run(idempotency.get_state("op-real-1")).state.value == "EXECUTED"


@pytest.mark.parametrize("bad_key", [None, "", "  "])
def test_no_audit_dispatch_or_velocity_side_effects_on_missing_id(tmp_path, bad_key):
    """Zero executor invocations is necessary but not sufficient -- confirm
    no durable admission/dispatch-ownership record and no pre_actuation audit
    entry were created either (the rejection happens before ALL of that, per
    requirement 1: before durable admission, velocity reservation, and
    audit-before-actuation, not merely before the executor call)."""
    import json

    engine, coord, idempotency = build(tmp_path)
    token = valid_executable_token(engine, idempotency_key=bad_key)
    calls = []

    result = run(coord.enforce(
        token=token, action="do_thing", payload={"amount": 100},
        executor=counting_executor(calls),
        request_binding={"actor_id": "agent/x", "resource_id": "res-1"},
        now=NOW,
    ))

    assert result.status == ActuationStatus.BLOCKED
    assert calls == []
    assert idempotency._store == {}  # type: ignore[attr-defined]
    with open(coord.audit.path, "r", encoding="utf-8") as fh:
        entries = [json.loads(line) for line in fh if line.strip()]
    kinds = [e.get("kind") for e in entries]
    assert "pre_actuation" not in kinds
    assert "actuation_result" not in kinds
    assert any(e.get("kind") == "actuation_rejected" for e in entries)


def test_two_fresh_missing_id_tokens_never_collide_into_a_single_admission(tmp_path):
    """Distinct tokens, each missing an idempotency_key, are independently
    rejected -- confirming the block is per-invocation and not itself somehow
    keyed off of a shared "no id" bucket that could let a second one slip
    through as a false duplicate or false admit."""
    engine, coord, idempotency = build(tmp_path)
    calls = []

    for nonce in ("n-a", "n-b"):
        token = valid_executable_token(engine, idempotency_key=None, nonce=nonce)
        result = run(coord.enforce(
            token=token, action="do_thing", payload={"amount": 100},
            executor=counting_executor(calls),
            request_binding={"actor_id": "agent/x", "resource_id": "res-1"},
            now=NOW,
        ))
        assert result.status == ActuationStatus.BLOCKED
        assert "MISSING_LOGICAL_OPERATION_ID" in result.reason

    assert calls == []
    assert idempotency._store == {}  # type: ignore[attr-defined]
