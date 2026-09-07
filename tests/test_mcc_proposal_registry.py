"""ProposalRegistry tests: Redis-backed atomicity/fail-closed semantics (via
a hand-rolled fake Redis client implementing exactly the Lua scripts
``RedisProposalRegistry`` sends -- the same convention
``tests/test_idempotency.py`` uses for ``RedisIdempotencyRegistry``, so a
live Redis server is not required for the suite), plus the
``MCC_PROPOSAL_BACKEND`` environment factory (Section 19).
"""

from __future__ import annotations

import asyncio

import pytest

from mcc_proposal.registry import (
    ProposalBackendUnavailable,
    ProposalConfigError,
    ProposalRegisterStatus,
    RedisProposalRegistry,
    proposal_registry_from_env,
)
from mcc_proposal.registry import InMemoryProposalRegistry, _REGISTER_LUA

run = asyncio.run


class FakeRedis:
    """Minimal fake matching exactly the ``eval``/``get`` calls
    ``RedisProposalRegistry`` makes -- no live Redis server needed."""

    def __init__(self) -> None:
        self.store: dict[str, str] = {}

    async def eval(self, script, numkeys, key, binding, created):
        assert script == _REGISTER_LUA
        cur = self.store.get(key)
        if cur is None:
            self.store[key] = f"{binding}|{created}"
            return ["REGISTERED", binding]
        existing_binding, _ = cur.split("|", 1)
        if existing_binding == binding:
            return ["IDEMPOTENT_DUPLICATE", existing_binding]
        return ["BINDING_CONFLICT", existing_binding]

    async def get(self, key):
        return self.store.get(key)


class DownRedis:
    async def eval(self, *a, **k):
        raise ConnectionError("down")

    async def get(self, *a, **k):
        raise ConnectionError("down")


def reg(fake=None) -> RedisProposalRegistry:
    return RedisProposalRegistry(fake or FakeRedis(), namespace="mcc:v1:test:proposal:")


def test_redis_first_registration_succeeds():
    r = run(reg().register(tenant_id="t", logical_operation_id="op-1", binding="b1"))
    assert r.status == ProposalRegisterStatus.REGISTERED
    assert r.binding == "b1"


def test_redis_identical_binding_is_idempotent_duplicate():
    fake = FakeRedis()
    r1 = run(reg(fake).register(tenant_id="t", logical_operation_id="op-2", binding="b1"))
    r2 = run(reg(fake).register(tenant_id="t", logical_operation_id="op-2", binding="b1"))
    assert r1.status == ProposalRegisterStatus.REGISTERED
    assert r2.status == ProposalRegisterStatus.IDEMPOTENT_DUPLICATE
    assert r2.binding == "b1"


def test_redis_different_binding_is_conflict_and_never_overwrites():
    fake = FakeRedis()
    run(reg(fake).register(tenant_id="t", logical_operation_id="op-3", binding="b1"))
    r2 = run(reg(fake).register(tenant_id="t", logical_operation_id="op-3", binding="b2"))
    assert r2.status == ProposalRegisterStatus.BINDING_CONFLICT
    assert r2.binding == "b1"  # the ORIGINAL binding, never overwritten
    got = run(reg(fake).get(tenant_id="t", logical_operation_id="op-3"))
    assert got.binding == "b1"


def test_redis_pipe_in_binding_is_rejected():
    r = run(reg().register(tenant_id="t", logical_operation_id="op-4", binding="has|pipe"))
    assert r.status == ProposalRegisterStatus.ERROR


def test_redis_down_register_is_error_fail_closed():
    r = run(reg(DownRedis()).register(tenant_id="t", logical_operation_id="op-5", binding="b1"))
    assert r.status == ProposalRegisterStatus.ERROR


def test_redis_down_get_raises_backend_unavailable_never_none():
    with pytest.raises(ProposalBackendUnavailable):
        run(reg(DownRedis()).get(tenant_id="t", logical_operation_id="op-6"))


def test_redis_tenant_scoping_keys_are_distinct():
    r = reg()
    key_a = r._key("tenant-a", "same-id")
    key_b = r._key("tenant-b", "same-id")
    assert key_a != key_b


# -- env factory (Section 19) ------------------------------------------------- #

def test_env_default_is_in_memory():
    r = proposal_registry_from_env({})
    assert isinstance(r, InMemoryProposalRegistry)


def test_env_enforcement_mode_refuses_memory_default():
    with pytest.raises(ProposalConfigError):
        proposal_registry_from_env({"MCC_DEPLOYMENT_MODE": "enforcement"})


def test_env_enforcement_mode_refuses_explicit_memory():
    with pytest.raises(ProposalConfigError):
        proposal_registry_from_env({
            "MCC_DEPLOYMENT_MODE": "enforcement", "MCC_PROPOSAL_BACKEND": "memory",
        })


def test_env_redis_requires_url_no_silent_fallback():
    with pytest.raises(ProposalConfigError):
        proposal_registry_from_env({"MCC_PROPOSAL_BACKEND": "redis"})


def test_env_redis_with_url_builds_redis_registry():
    r = proposal_registry_from_env({
        "MCC_PROPOSAL_BACKEND": "redis", "MCC_REDIS_URL": "redis://localhost:6379/0",
    })
    assert isinstance(r, RedisProposalRegistry)


def test_env_unknown_backend_rejected():
    with pytest.raises(ProposalConfigError):
        proposal_registry_from_env({"MCC_PROPOSAL_BACKEND": "carrier-pigeon"})
