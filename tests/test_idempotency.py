"""Idempotency registry tests: durable logical-operation state machine.

Covers admission (same-key duplicate denial, BINDING_CONFLICT, exactly-one
concurrent winner), the durable dispatch boundary (DISPATCH_OWNED/UNKNOWN/
EXECUTED never becoming TTL-eligible for a fresh admission), fenced state
transitions (a stale generation can neither finalize nor release/fail an
operation it no longer owns), reconciliation (UNKNOWN -> EXECUTED on positive
evidence, safely racing with a late completion or another reconciliation
worker), restart/durability semantics, and fail-closed backend-outage
behavior (never conflated with "not found" / "safe to retry").
"""

import asyncio

import pytest

from mcc_core import (
    IdempotencyBackendUnavailable,
    IdempotencyConfigError,
    IdempotencyState,
    InMemoryIdempotencyRegistry,
    ReconcileStatus,
    RedisIdempotencyRegistry,
    ReserveStatus,
    idempotency_registry_from_env,
)
from mcc_core.idempotency import (
    _COMMIT_DISPATCH_LUA,
    _MARK_EXECUTED_LUA,
    _MARK_UNKNOWN_LUA,
    _RELEASE_LUA,
    _RESERVE_LUA,
    _RESOLVE_UNKNOWN_LUA,
)

run = asyncio.run


class IdemFakeRedis:
    """Faithful Python re-implementation of every idempotency Lua script,
    against an injectable clock and a shared ``store`` dict so two registry
    instances can model the same Redis (cross-instance durability tests)."""

    def __init__(self, store=None, clock=None):
        self.store = store if store is not None else {}
        self.clock = clock or (lambda: 0.0)

    def _expired(self, key, now):
        cur = self.store.get(key)
        return cur is not None and cur[1] is not None and cur[1] <= now

    def _get(self, key):
        now = self.clock()
        if self._expired(key, now):
            del self.store[key]
        cur = self.store.get(key)
        return None if cur is None else cur[0]

    async def set(self, key, value, nx=False, ex=None):
        now = self.clock()
        if self._expired(key, now):
            del self.store[key]
        if nx and key in self.store:
            return None
        self.store[key] = (value, (now + ex) if ex else None)
        return True

    async def get(self, key):
        return self._get(key)

    async def delete(self, key):
        self.store.pop(key, None)
        return 1

    async def eval(self, script, numkeys, *args):
        key = args[0]
        argv = args[1:]
        cur = self._get(key)

        if script == _RESERVE_LUA:
            binding, ttl_seconds, generation = argv
            if cur is None:
                self.store[key] = (f"RESERVED|{generation}|{binding}|", self.clock() + int(ttl_seconds))
                return ["RESERVED", generation]
            state, gen, held_binding = cur.split("|", 3)[:3]
            if held_binding != binding:
                return ["BINDING_CONFLICT", gen, held_binding]
            if state == "EXECUTED":
                return ["DUPLICATE_EXECUTED", gen]
            if state == "UNKNOWN":
                return ["DUPLICATE_UNKNOWN", gen]
            return ["DUPLICATE_INFLIGHT", gen]

        if script == _COMMIT_DISPATCH_LUA:
            (expected_gen,) = argv
            if cur is None:
                return 0
            state, gen, binding = cur.split("|", 3)[:3]
            if state != "RESERVED" or gen != expected_gen:
                return 0
            self.store[key] = (f"DISPATCH_OWNED|{gen}|{binding}|", None)
            return 1

        if script == _MARK_EXECUTED_LUA:
            expected_gen, result_ref, ttl_seconds = argv
            if cur is None:
                return 0
            state, gen, binding = cur.split("|", 3)[:3]
            if state != "DISPATCH_OWNED" or gen != expected_gen:
                return 0
            val = f"EXECUTED|{gen}|{binding}|{result_ref}"
            expires = (self.clock() + int(ttl_seconds)) if ttl_seconds else None
            self.store[key] = (val, expires)
            return 1

        if script == _MARK_UNKNOWN_LUA:
            (expected_gen,) = argv
            if cur is None:
                return 0
            state, gen, binding = cur.split("|", 3)[:3]
            if state != "DISPATCH_OWNED" or gen != expected_gen:
                return 0
            self.store[key] = (f"UNKNOWN|{gen}|{binding}|", None)
            return 1

        if script == _RELEASE_LUA:
            (expected_gen,) = argv
            if cur is None:
                return 1
            state, gen = cur.split("|", 3)[:2]
            if state != "RESERVED" or gen != expected_gen:
                return 0
            self.store.pop(key, None)
            return 1

        if script == _RESOLVE_UNKNOWN_LUA:
            expected_gen, result_ref = argv
            if cur is None:
                return ["NOT_FOUND", ""]
            state, gen, binding = cur.split("|", 3)[:3]
            if gen != expected_gen:
                return ["STALE_GENERATION", state]
            if state == "EXECUTED":
                return ["ALREADY_EXECUTED", state]
            if state != "UNKNOWN":
                return ["NOT_UNKNOWN", state]
            self.store[key] = (f"EXECUTED|{gen}|{binding}|{result_ref}", None)
            return ["RESOLVED", "EXECUTED"]

        raise AssertionError(f"unrecognized script passed to fake eval: {script!r}")


class DownRedis:
    async def set(self, *a, **k):
        raise ConnectionError("down")

    async def get(self, *a, **k):
        raise ConnectionError("down")

    async def delete(self, *a, **k):
        raise ConnectionError("down")

    async def eval(self, *a, **k):
        raise ConnectionError("down")


def redis_reg(store=None, clock=None):
    return RedisIdempotencyRegistry(IdemFakeRedis(store, clock))


def registries():
    return [InMemoryIdempotencyRegistry(), redis_reg()]


# ---- First / duplicate / BINDING_CONFLICT ----

@pytest.mark.parametrize("reg", registries())
def test_first_reservation_succeeds(reg):
    res = run(reg.reserve("op-1"))
    assert res.ok
    assert res.status == ReserveStatus.RESERVED
    assert res.fence  # a fence/generation token is issued


@pytest.mark.parametrize("reg", registries())
def test_duplicate_reservation_denied(reg):
    assert run(reg.reserve("op-1")).ok
    second = run(reg.reserve("op-1"))
    assert not second.ok
    assert second.status == ReserveStatus.DUPLICATE_INFLIGHT


@pytest.mark.parametrize("reg", registries())
def test_different_binding_same_key_is_binding_conflict(reg):
    """Test scenarios 2/3/4: the SAME idempotency_key presented with a
    different operation binding (action/resource/payload_hash all fold into
    ``binding``) is a BINDING_CONFLICT, never a plain duplicate."""
    assert run(reg.reserve("dup-key", binding="payload-hash-A")).ok
    second = run(reg.reserve("dup-key", binding="payload-hash-B"))
    assert not second.ok
    assert second.status == ReserveStatus.BINDING_CONFLICT


# ---- Terminal EXECUTED / UNKNOWN ----

@pytest.mark.parametrize("reg", registries())
def test_executed_can_never_execute_again(reg):
    first = run(reg.reserve("op-1"))
    assert first.ok
    assert run(reg.commit_dispatch("op-1", fence=first.fence))
    assert run(reg.mark_executed("op-1", fence=first.fence))
    again = run(reg.reserve("op-1"))
    assert not again.ok
    assert again.status == ReserveStatus.DUPLICATE_EXECUTED


@pytest.mark.parametrize("reg", registries())
def test_unknown_blocks_reservation_pending_reconciliation(reg):
    first = run(reg.reserve("op-1"))
    assert run(reg.commit_dispatch("op-1", fence=first.fence))
    assert run(reg.mark_unknown("op-1", fence=first.fence))
    again = run(reg.reserve("op-1"))
    assert not again.ok
    assert again.status == ReserveStatus.DUPLICATE_UNKNOWN


@pytest.mark.parametrize("reg", registries())
def test_release_only_valid_pre_dispatch(reg):
    """Pre-dispatch (RESERVED) release frees the key for a legitimate retry;
    once DISPATCH_OWNED, release is refused (fenced rejection)."""
    first = run(reg.reserve("op-1"))
    assert run(reg.release("op-1", fence=first.fence))
    assert run(reg.reserve("op-1")).ok  # retryable after a pre-dispatch release

    second = run(reg.reserve("op-2"))
    assert run(reg.commit_dispatch("op-2", fence=second.fence))
    assert run(reg.release("op-2", fence=second.fence)) is False
    record = run(reg.get_state("op-2"))
    assert record.state == IdempotencyState.DISPATCH_OWNED


# ---- Concurrency: exactly one winner ----

@pytest.mark.parametrize("reg", registries())
def test_concurrent_duplicate_exactly_one_winner(reg):
    async def race():
        return await asyncio.gather(*[reg.reserve("op-1") for _ in range(50)])

    results = run(race())
    winners = [r for r in results if r.ok]
    assert len(winners) == 1
    assert all(r.status == ReserveStatus.DUPLICATE_INFLIGHT for r in results if not r.ok)


# ---- TTL / stale-RESERVED recovery (pre-dispatch ONLY) ----

def test_stale_reserved_recovers_after_ttl():
    clock = {"t": 1000.0}
    reg = redis_reg(clock=lambda: clock["t"])
    assert run(reg.reserve("op-1", ttl_seconds=5)).ok
    assert not run(reg.reserve("op-1", ttl_seconds=5)).ok  # still reserved
    clock["t"] += 6  # the crashed holder's PRE-DISPATCH reservation lapses
    assert run(reg.reserve("op-1", ttl_seconds=5)).ok  # recovered


# ---- Test scenario 13/14: DISPATCH_OWNED/UNKNOWN/EXECUTED never expire ----

def test_dispatch_owned_does_not_expire_into_admittable_state():
    """Once dispatch ownership is committed, even a reservation TTL boundary
    that WOULD have applied pre-dispatch must have no effect: the operation
    remains blocking forever (until reconciliation), never becoming
    retry-eligible merely because time passed."""
    clock = {"t": 1000.0}
    reg = redis_reg(clock=lambda: clock["t"])
    first = run(reg.reserve("op-1", ttl_seconds=5))
    assert run(reg.commit_dispatch("op-1", fence=first.fence))
    clock["t"] += 10_000  # far past what would have been the reservation TTL
    retry = run(reg.reserve("op-1"))
    assert not retry.ok
    assert retry.status == ReserveStatus.DUPLICATE_INFLIGHT


def test_unknown_does_not_expire_into_admittable_state():
    """Test scenario 13: UNKNOWN must not become actuation-eligible through
    TTL expiry."""
    clock = {"t": 1000.0}
    reg = redis_reg(clock=lambda: clock["t"])
    first = run(reg.reserve("op-1", ttl_seconds=5))
    assert run(reg.commit_dispatch("op-1", fence=first.fence))
    assert run(reg.mark_unknown("op-1", fence=first.fence))
    clock["t"] += 10_000
    retry = run(reg.reserve("op-1"))
    assert not retry.ok
    assert retry.status == ReserveStatus.DUPLICATE_UNKNOWN


def test_executed_does_not_expire_into_admittable_state():
    """Test scenario 14: EXECUTED must not silently become executable again
    through TTL expiry (retention/GC is a distinct, explicit, opt-in
    mechanism -- ``mark_executed``'s ``ttl_seconds`` is never wired into
    ``reserve``'s admission logic by default, i.e. ``ttl_seconds=None``)."""
    clock = {"t": 1000.0}
    reg = redis_reg(clock=lambda: clock["t"])
    first = run(reg.reserve("op-1", ttl_seconds=5))
    assert run(reg.commit_dispatch("op-1", fence=first.fence))
    assert run(reg.mark_executed("op-1", fence=first.fence))
    clock["t"] += 10_000
    retry = run(reg.reserve("op-1"))
    assert not retry.ok
    assert retry.status == ReserveStatus.DUPLICATE_EXECUTED


# ---- Durability across restart (shared backend) vs. NOT durable (in-memory) ----

def test_dispatch_owned_persists_and_blocks_after_restart():
    """Test scenario 6/11: a crash after durable dispatch ownership (or
    after the operation is marked UNKNOWN) leaves the operation unresolved
    across a process restart -- modeled here as a fresh registry instance
    sharing the same backing store -- with no automatic redispatch."""
    store = {}
    before = RedisIdempotencyRegistry(IdemFakeRedis(store))
    first = run(before.reserve("op-1"))
    assert run(before.commit_dispatch("op-1", fence=first.fence))

    after = RedisIdempotencyRegistry(IdemFakeRedis(store))  # "process restart"
    record = run(after.get_state("op-1"))
    assert record.state == IdempotencyState.DISPATCH_OWNED
    assert run(after.reserve("op-1")).status == ReserveStatus.DUPLICATE_INFLIGHT


def test_unknown_persists_across_restart():
    store = {}
    before = RedisIdempotencyRegistry(IdemFakeRedis(store))
    first = run(before.reserve("op-1"))
    assert run(before.commit_dispatch("op-1", fence=first.fence))
    assert run(before.mark_unknown("op-1", fence=first.fence))

    after = RedisIdempotencyRegistry(IdemFakeRedis(store))
    record = run(after.get_state("op-1"))
    assert record.state == IdempotencyState.UNKNOWN
    assert run(after.reserve("op-1")).status == ReserveStatus.DUPLICATE_UNKNOWN


def test_executed_persists_across_restart():
    store = {}
    before = RedisIdempotencyRegistry(IdemFakeRedis(store))
    first = run(before.reserve("op-1"))
    assert run(before.commit_dispatch("op-1", fence=first.fence))
    assert run(before.mark_executed("op-1", fence=first.fence))

    after = RedisIdempotencyRegistry(IdemFakeRedis(store))
    record = run(after.get_state("op-1"))
    assert record.state == IdempotencyState.EXECUTED
    assert run(after.reserve("op-1")).status == ReserveStatus.DUPLICATE_EXECUTED


def test_inmemory_registry_is_not_durable_across_instances():
    """Test scenario 12: a genuinely durable claim requires a shared backend
    (proven above via a SHARED fake-Redis store across two registry
    instances). Two independent ``InMemoryIdempotencyRegistry`` instances do
    NOT share state -- this is the negative control proving the durability
    tests above are actually exercising cross-instance persistence, not an
    artifact of both sides happening to read the same in-process dict."""
    a = InMemoryIdempotencyRegistry()
    b = InMemoryIdempotencyRegistry()
    first = run(a.reserve("op-1"))
    run(a.commit_dispatch("op-1", fence=first.fence))
    run(a.mark_executed("op-1", fence=first.fence))
    assert run(a.get_state("op-1")).state == IdempotencyState.EXECUTED
    assert run(b.get_state("op-1")) is None  # instance B has no idea this happened
    assert run(b.reserve("op-1")).ok  # and would (wrongly, if relied on as durable) admit it again


# ---- Fenced state transitions: stale owners are rejected ----

def test_stale_fence_rejected_for_every_mutation():
    """Test scenarios 15/16: a stale fence (from a superseded generation)
    cannot mark executed, mark unknown, or release/regress the CURRENT
    generation's state."""
    reg = InMemoryIdempotencyRegistry()
    gen1 = run(reg.reserve("op-1"))
    stale_fence = gen1.fence
    assert run(reg.release("op-1", fence=stale_fence))  # legitimate pre-dispatch release
    gen2 = run(reg.reserve("op-1"))
    assert gen2.fence != stale_fence
    assert run(reg.commit_dispatch("op-1", fence=gen2.fence))

    assert run(reg.mark_executed("op-1", fence=stale_fence)) is False
    assert run(reg.mark_unknown("op-1", fence=stale_fence)) is False
    assert run(reg.release("op-1", fence=stale_fence)) is False
    # current state is unaffected by any of the stale attempts
    record = run(reg.get_state("op-1"))
    assert record.state == IdempotencyState.DISPATCH_OWNED
    assert record.generation == gen2.fence


def test_stale_fence_cannot_regress_executed_to_unknown():
    reg = InMemoryIdempotencyRegistry()
    gen = run(reg.reserve("op-1"))
    run(reg.commit_dispatch("op-1", fence=gen.fence))
    run(reg.mark_executed("op-1", fence=gen.fence))
    # An attempt using a fabricated/foreign fence cannot regress EXECUTED.
    assert run(reg.mark_unknown("op-1", fence="not-a-real-fence")) is False
    assert run(reg.get_state("op-1")).state == IdempotencyState.EXECUTED


# ---- Reconciliation ----

def test_resolve_unknown_to_executed():
    reg = InMemoryIdempotencyRegistry()
    gen = run(reg.reserve("op-1", binding="b"))
    run(reg.commit_dispatch("op-1", fence=gen.fence))
    run(reg.mark_unknown("op-1", fence=gen.fence))
    result = run(reg.resolve_unknown("op-1", expected_generation=gen.fence, result_ref="issue-42"))
    assert result.resolved
    record = run(reg.get_state("op-1"))
    assert record.state == IdempotencyState.EXECUTED
    assert record.result_ref == "issue-42"


def test_reconciliation_never_creates_only_resolves_existing_unknown():
    reg = InMemoryIdempotencyRegistry()
    result = run(reg.resolve_unknown("never-admitted", expected_generation="whatever"))
    assert result.status == ReconcileStatus.NOT_FOUND


def test_reconciliation_races_with_late_completion_exactly_one_wins():
    """Test scenario 17: reconciliation (positive external evidence) racing
    with the ORIGINAL dispatcher's own late-arriving completion. Exactly one
    write applies; the other observes it is no longer UNKNOWN and no-ops --
    in particular, reconciliation never itself invokes any actuator, so
    "coherent final state, zero duplicate actuator calls" holds trivially."""
    reg = InMemoryIdempotencyRegistry()
    gen = run(reg.reserve("op-1"))
    run(reg.commit_dispatch("op-1", fence=gen.fence))
    run(reg.mark_unknown("op-1", fence=gen.fence))

    async def race():
        return await asyncio.gather(
            reg.resolve_unknown("op-1", expected_generation=gen.fence, result_ref="from-reconciliation"),
            reg.mark_executed("op-1", fence=gen.fence, result_ref="from-late-dispatcher"),
        )

    reconcile_result, late_dispatcher_ok = run(race())
    # Exactly one of the two writers actually applies the UNKNOWN -> EXECUTED
    # transition (asyncio's cooperative scheduling still means one Python
    # coroutine's synchronous critical section runs to completion before the
    # other starts; this pins the invariant that matters -- never both).
    applied = int(reconcile_result.resolved) + int(late_dispatcher_ok)
    assert applied == 1
    final = run(reg.get_state("op-1"))
    assert final.state == IdempotencyState.EXECUTED  # coherent final state either way


def test_reconciliation_races_with_fresh_retry_zero_second_create():
    """Test scenario 18: a fresh retry attempt racing with reconciliation
    must never be admitted while the operation is still UNKNOWN -- so no
    second "create" can occur no matter which happens first."""
    reg = InMemoryIdempotencyRegistry()
    gen = run(reg.reserve("op-1", binding="b"))
    run(reg.commit_dispatch("op-1", fence=gen.fence))
    run(reg.mark_unknown("op-1", fence=gen.fence))

    async def race():
        return await asyncio.gather(
            reg.resolve_unknown("op-1", expected_generation=gen.fence, result_ref="ev"),
            reg.reserve("op-1", binding="b"),
        )

    resolve_result, retry_result = run(race())
    assert not retry_result.ok  # never admitted a second time
    assert retry_result.status in (ReserveStatus.DUPLICATE_UNKNOWN, ReserveStatus.DUPLICATE_EXECUTED)


# ---- Status lookup: backend outage is never "not found" / "safe to retry" ----

def test_get_state_backend_unavailable_raises_not_none():
    """Test scenario 21: a backend failure surfaces as an explicit,
    distinguishable UNAVAILABLE signal -- never conflated with "no such
    operation" (``None``) or any status that would suggest it is safe to
    retry."""
    reg = RedisIdempotencyRegistry(DownRedis())
    with pytest.raises(IdempotencyBackendUnavailable):
        run(reg.get_state("op-1"))


def test_get_state_absent_key_returns_none_not_unavailable():
    reg = InMemoryIdempotencyRegistry()
    assert run(reg.get_state("never-reserved")) is None


# ---- Fail-closed ----

def test_registry_outage_fails_closed():
    reg = RedisIdempotencyRegistry(DownRedis())
    res = run(reg.reserve("op-1"))
    assert not res.ok
    assert res.status == ReserveStatus.ERROR


def test_invalid_key_fails_closed():
    reg = InMemoryIdempotencyRegistry()
    assert not run(reg.reserve("")).ok


def test_invalid_binding_fails_closed_on_redis():
    """A binding containing the field delimiter must never be accepted --
    it could otherwise corrupt the encoded record and forge a state."""
    reg = redis_reg()
    res = run(reg.reserve("op-1", binding="has|a|pipe"))
    assert res.status == ReserveStatus.ERROR


# ---- Backend selection (no silent fallback) ----

def test_factory_defaults_to_memory():
    assert isinstance(idempotency_registry_from_env({}), InMemoryIdempotencyRegistry)


def test_factory_redis_requires_url():
    with pytest.raises(IdempotencyConfigError):
        idempotency_registry_from_env({"MCC_IDEMPOTENCY_BACKEND": "redis"})


def test_factory_unknown_backend_raises():
    with pytest.raises(IdempotencyConfigError):
        idempotency_registry_from_env({"MCC_IDEMPOTENCY_BACKEND": "etcd"})


def test_factory_enforcement_mode_refuses_memory():
    """Test scenario 12: an enforcement deployment must not silently come up
    with per-process, non-durable logical-operation state."""
    with pytest.raises(IdempotencyConfigError):
        idempotency_registry_from_env({"MCC_DEPLOYMENT_MODE": "enforcement"})
    with pytest.raises(IdempotencyConfigError):
        idempotency_registry_from_env({
            "MCC_DEPLOYMENT_MODE": "enforcement", "MCC_IDEMPOTENCY_BACKEND": "memory",
        })
