"""PR #105 — MANDATORY tenant_id at the core execution boundary.

Target invariant: NO VALID TENANT_ID -> ZERO ACTUATOR INVOCATIONS.

Mirrors ``test_coordinator_mandatory_logical_operation_id.py`` exactly in
spirit: ``EnforcementCoordinator.enforce()`` is the ONE domain-neutral
enforcement point shared by every governed domain in this repository, and
this proves it -- not `GovernanceService`, not any reference integration's
own pipeline helper -- is the unavoidable authority for the tenant-identity
invariant. A genuinely valid, signed, executable decision token carrying no
``tenant_id`` (missing, None, empty, or whitespace-only) must be BLOCKED
before durable admission, velocity reservation, and audit-before-actuation
-- never merely before the executor call alone.

These tests call ``EnforcementCoordinator.enforce()`` DIRECTLY with a
genuinely valid signed executable token, varying only ``tenant_id``.
"""

import asyncio
import json

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


def valid_executable_token(engine, *, tenant_id, idempotency_key="op-1", nonce="n-1"):
    """A genuinely valid, signed, executable (ALLOW) token: real signature,
    real action/resource/payload binding, real policy hash, real
    (non-expired) time window, real nonce, and a real, non-empty
    idempotency_key -- the ONLY thing under test is the value of
    ``tenant_id`` itself."""
    payload = {"amount": 100}
    return engine.issue_token(
        verdict="ALLOW", subject="agent/x", action="do_thing", payload=payload,
        actor_id="agent/x", resource_id="res-1", nonce=nonce,
        idempotency_key=idempotency_key, tenant_id=tenant_id, now=NOW,
    )


def counting_executor(calls):
    async def executor():
        calls.append(1)
        return {"ok": True}
    return executor


@pytest.mark.parametrize("bad_tenant", [None, "", "   ", "\t\n"])
def test_missing_or_blank_tenant_id_blocks_before_executor(tmp_path, bad_tenant):
    engine, coord, idempotency = build(tmp_path)
    token = valid_executable_token(engine, tenant_id=bad_tenant)
    calls = []

    result = run(coord.enforce(
        token=token, action="do_thing", payload={"amount": 100},
        executor=counting_executor(calls),
        request_binding={"actor_id": "agent/x", "resource_id": "res-1"},
        now=NOW,
    ))

    assert result.status == ActuationStatus.BLOCKED
    assert "MISSING_TENANT_IDENTITY" in result.reason
    assert calls == [], "the executor must NEVER be invoked without a valid tenant_id"
    # No durable dispatch ownership was ever created for any (tenant, key).
    assert idempotency._store == {}  # type: ignore[attr-defined]


def test_non_string_tenant_id_blocks_before_executor(tmp_path):
    """A token whose tenant_id is present but not a string is exactly as
    invalid as a missing one -- never coerced, never silently accepted."""
    engine, coord, idempotency = build(tmp_path)
    token = valid_executable_token(engine, tenant_id=12345)
    calls = []

    result = run(coord.enforce(
        token=token, action="do_thing", payload={"amount": 100},
        executor=counting_executor(calls),
        request_binding={"actor_id": "agent/x", "resource_id": "res-1"},
        now=NOW,
    ))

    assert result.status == ActuationStatus.BLOCKED
    assert "MISSING_TENANT_IDENTITY" in result.reason
    assert calls == []


def test_valid_non_empty_tenant_id_still_executes(tmp_path):
    """Positive control: the mandatory check does not regress the ordinary,
    correct path -- a genuinely valid token WITH a real tenant_id still
    actuates exactly as before."""
    engine, coord, idempotency = build(tmp_path)
    token = valid_executable_token(engine, tenant_id="tenant-real-1")
    calls = []

    result = run(coord.enforce(
        token=token, action="do_thing", payload={"amount": 100},
        executor=counting_executor(calls),
        request_binding={"actor_id": "agent/x", "resource_id": "res-1"},
        now=NOW,
    ))

    assert result.status == ActuationStatus.EXECUTED
    assert calls == [1]
    assert run(idempotency.get_state("op-1", tenant_id="tenant-real-1")).state.value == "EXECUTED"


@pytest.mark.parametrize("bad_tenant", [None, "", "  "])
def test_no_audit_dispatch_or_velocity_side_effects_on_missing_tenant(tmp_path, bad_tenant):
    """Zero executor invocations is necessary but not sufficient -- confirm
    no durable admission/dispatch-ownership record and no pre_actuation audit
    entry were created either (the rejection happens before ALL of that:
    durable admission, velocity reservation, and audit-before-actuation, not
    merely before the executor call)."""
    engine, coord, idempotency = build(tmp_path)
    token = valid_executable_token(engine, tenant_id=bad_tenant)
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


def test_two_fresh_missing_tenant_tokens_never_collide_into_a_single_admission(tmp_path):
    """Distinct tokens, each missing a tenant_id, are independently
    rejected -- confirming the block is per-invocation and not itself somehow
    keyed off of a shared "no tenant" bucket that could let a second one
    slip through as a false duplicate or false admit."""
    engine, coord, idempotency = build(tmp_path)
    calls = []

    for nonce in ("n-a", "n-b"):
        token = valid_executable_token(engine, tenant_id=None, nonce=nonce)
        result = run(coord.enforce(
            token=token, action="do_thing", payload={"amount": 100},
            executor=counting_executor(calls),
            request_binding={"actor_id": "agent/x", "resource_id": "res-1"},
            now=NOW,
        ))
        assert result.status == ActuationStatus.BLOCKED
        assert "MISSING_TENANT_IDENTITY" in result.reason

    assert calls == []
    assert idempotency._store == {}  # type: ignore[attr-defined]


def test_missing_tenant_id_checked_even_with_valid_logical_operation_id(tmp_path):
    """The two mandatory checks (logical_operation_id, tenant_id) are
    independent -- a token with a perfectly valid idempotency_key but a
    missing tenant_id is still blocked, never let through because "at
    least one" identity field was present."""
    engine, coord, idempotency = build(tmp_path)
    token = valid_executable_token(engine, tenant_id="", idempotency_key="op-well-formed")
    calls = []

    result = run(coord.enforce(
        token=token, action="do_thing", payload={"amount": 100},
        executor=counting_executor(calls),
        request_binding={"actor_id": "agent/x", "resource_id": "res-1"},
        now=NOW,
    ))

    assert result.status == ActuationStatus.BLOCKED
    assert "MISSING_TENANT_IDENTITY" in result.reason
    assert calls == []
    assert idempotency._store == {}  # type: ignore[attr-defined]
