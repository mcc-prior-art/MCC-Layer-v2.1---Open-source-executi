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
    _MIGRATE_LEGACY_LUA,
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
        if script == _MIGRATE_LEGACY_LUA:
            # PR #105 remediation (Blocker 3): faithful Python
            # re-implementation of the atomic migration script -- claim
            # key gates exclusivity; legacy/target reads and the
            # copy+claim+optional-delete all happen without any `await`
            # in between (this method never suspends mid-body), exactly
            # mirroring Redis's single-threaded Lua atomicity.
            legacy_key, scoped_key, claim_key = args[0], args[1], args[2]
            tenant_id, delete_flag = args[3], args[4]
            claim = self._get(claim_key)
            if claim is not None:
                if claim != tenant_id:
                    return ["CONFLICT", "legacy record already claimed by a different tenant"]
                existing = self._get(scoped_key)
                if existing is not None:
                    return ["ALREADY_MIGRATED", existing]
                return ["ERROR", "migration claim exists for this tenant but the scoped record is missing"]
            legacy = self._get(legacy_key)
            if legacy is None:
                existing = self._get(scoped_key)
                if existing is not None:
                    return ["ALREADY_MIGRATED", existing]
                return ["ABSENT", ""]
            existing = self._get(scoped_key)
            if existing is not None:
                if existing == legacy:
                    self.store[claim_key] = (tenant_id, None)
                    if delete_flag == "1":
                        self.store.pop(legacy_key, None)
                    return ["ALREADY_MIGRATED", existing]
                return ["CONFLICT", "target tenant-scoped record already holds different durable state"]
            self.store[scoped_key] = (legacy, None)
            self.store[claim_key] = (tenant_id, None)
            if delete_flag == "1":
                self.store.pop(legacy_key, None)
            return ["MIGRATED", legacy]

        if script == _RESERVE_LUA:
            # PR #105: KEYS[1] = tenant-scoped key, KEYS[2] = legacy
            # (pre-tenant-scoping) key -- the legacy key is checked FIRST,
            # mirroring the real Lua script exactly.
            scoped_key, legacy_key = args[0], args[1]
            argv = args[2:]
            if self._get(legacy_key) is not None:
                return ["LEGACY_UNMIGRATED", "", ""]
            cur = self._get(scoped_key)
            binding, ttl_seconds, generation = argv
            if cur is None:
                self.store[scoped_key] = (f"RESERVED|{generation}|{binding}|", self.clock() + int(ttl_seconds))
                return ["RESERVED", generation]
            state, gen, held_binding = cur.split("|", 3)[:3]
            if held_binding != binding:
                return ["BINDING_CONFLICT", gen, held_binding]
            if state == "EXECUTED":
                return ["DUPLICATE_EXECUTED", gen]
            if state == "UNKNOWN":
                return ["DUPLICATE_UNKNOWN", gen]
            return ["DUPLICATE_INFLIGHT", gen]

        key = args[0]
        argv = args[1:]
        cur = self._get(key)

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
            expected_gen, result_ref = argv
            if cur is None:
                return 0
            state, gen, binding = cur.split("|", 3)[:3]
            if state != "DISPATCH_OWNED" or gen != expected_gen:
                return 0
            self.store[key] = (f"EXECUTED|{gen}|{binding}|{result_ref}", None)
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
            if state != "UNKNOWN" and state != "DISPATCH_OWNED":
                return ["NOT_PENDING", state]
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
    res = run(reg.reserve("op-1", tenant_id="tenant-a"))
    assert res.ok
    assert res.status == ReserveStatus.RESERVED
    assert res.fence  # a fence/generation token is issued


@pytest.mark.parametrize("reg", registries())
def test_duplicate_reservation_denied(reg):
    assert run(reg.reserve("op-1", tenant_id="tenant-a")).ok
    second = run(reg.reserve("op-1", tenant_id="tenant-a"))
    assert not second.ok
    assert second.status == ReserveStatus.DUPLICATE_INFLIGHT


@pytest.mark.parametrize("reg", registries())
def test_different_binding_same_key_is_binding_conflict(reg):
    """Test scenarios 2/3/4: the SAME idempotency_key presented with a
    different operation binding (action/resource/payload_hash all fold into
    ``binding``) is a BINDING_CONFLICT, never a plain duplicate."""
    assert run(reg.reserve("dup-key", binding="payload-hash-A", tenant_id="tenant-a")).ok
    second = run(reg.reserve("dup-key", binding="payload-hash-B", tenant_id="tenant-a"))
    assert not second.ok
    assert second.status == ReserveStatus.BINDING_CONFLICT


# ---- Terminal EXECUTED / UNKNOWN ----

@pytest.mark.parametrize("reg", registries())
def test_executed_can_never_execute_again(reg):
    first = run(reg.reserve("op-1", tenant_id="tenant-a"))
    assert first.ok
    assert run(reg.commit_dispatch("op-1", fence=first.fence, tenant_id="tenant-a"))
    assert run(reg.mark_executed("op-1", fence=first.fence, tenant_id="tenant-a"))
    again = run(reg.reserve("op-1", tenant_id="tenant-a"))
    assert not again.ok
    assert again.status == ReserveStatus.DUPLICATE_EXECUTED


@pytest.mark.parametrize("reg", registries())
def test_unknown_blocks_reservation_pending_reconciliation(reg):
    first = run(reg.reserve("op-1", tenant_id="tenant-a"))
    assert run(reg.commit_dispatch("op-1", fence=first.fence, tenant_id="tenant-a"))
    assert run(reg.mark_unknown("op-1", fence=first.fence, tenant_id="tenant-a"))
    again = run(reg.reserve("op-1", tenant_id="tenant-a"))
    assert not again.ok
    assert again.status == ReserveStatus.DUPLICATE_UNKNOWN


@pytest.mark.parametrize("reg", registries())
def test_release_only_valid_pre_dispatch(reg):
    """Pre-dispatch (RESERVED) release frees the key for a legitimate retry;
    once DISPATCH_OWNED, release is refused (fenced rejection)."""
    first = run(reg.reserve("op-1", tenant_id="tenant-a"))
    assert run(reg.release("op-1", fence=first.fence, tenant_id="tenant-a"))
    assert run(reg.reserve("op-1", tenant_id="tenant-a")).ok  # retryable after a pre-dispatch release

    second = run(reg.reserve("op-2", tenant_id="tenant-a"))
    assert run(reg.commit_dispatch("op-2", fence=second.fence, tenant_id="tenant-a"))
    assert run(reg.release("op-2", fence=second.fence, tenant_id="tenant-a")) is False
    record = run(reg.get_state("op-2", tenant_id="tenant-a"))
    assert record.state == IdempotencyState.DISPATCH_OWNED


# ---- Concurrency: exactly one winner ----

@pytest.mark.parametrize("reg", registries())
def test_concurrent_duplicate_exactly_one_winner(reg):
    async def race():
        return await asyncio.gather(*[reg.reserve("op-1", tenant_id="tenant-a") for _ in range(50)])

    results = run(race())
    winners = [r for r in results if r.ok]
    assert len(winners) == 1
    assert all(r.status == ReserveStatus.DUPLICATE_INFLIGHT for r in results if not r.ok)


# ---- TTL / stale-RESERVED recovery (pre-dispatch ONLY) ----

def test_stale_reserved_recovers_after_ttl():
    clock = {"t": 1000.0}
    reg = redis_reg(clock=lambda: clock["t"])
    assert run(reg.reserve("op-1", ttl_seconds=5, tenant_id="tenant-a")).ok
    assert not run(reg.reserve("op-1", ttl_seconds=5, tenant_id="tenant-a")).ok  # still reserved
    clock["t"] += 6  # the crashed holder's PRE-DISPATCH reservation lapses
    assert run(reg.reserve("op-1", ttl_seconds=5, tenant_id="tenant-a")).ok  # recovered


# ---- Test scenario 13/14: DISPATCH_OWNED/UNKNOWN/EXECUTED never expire ----

def test_dispatch_owned_does_not_expire_into_admittable_state():
    """Once dispatch ownership is committed, even a reservation TTL boundary
    that WOULD have applied pre-dispatch must have no effect: the operation
    remains blocking forever (until reconciliation), never becoming
    retry-eligible merely because time passed."""
    clock = {"t": 1000.0}
    reg = redis_reg(clock=lambda: clock["t"])
    first = run(reg.reserve("op-1", ttl_seconds=5, tenant_id="tenant-a"))
    assert run(reg.commit_dispatch("op-1", fence=first.fence, tenant_id="tenant-a"))
    clock["t"] += 10_000  # far past what would have been the reservation TTL
    retry = run(reg.reserve("op-1", tenant_id="tenant-a"))
    assert not retry.ok
    assert retry.status == ReserveStatus.DUPLICATE_INFLIGHT


def test_mark_executed_accepts_no_ttl_parameter_on_either_backend():
    """Round 18 requirement 3: the capability to reopen a terminal EXECUTED
    record via TTL is removed from the protected state machine entirely,
    not merely defaulted to off."""
    import inspect

    for reg in (InMemoryIdempotencyRegistry(), redis_reg()):
        params = inspect.signature(reg.mark_executed).parameters
        assert "ttl_seconds" not in params


def test_unknown_does_not_expire_into_admittable_state():
    """Test scenario 13: UNKNOWN must not become actuation-eligible through
    TTL expiry."""
    clock = {"t": 1000.0}
    reg = redis_reg(clock=lambda: clock["t"])
    first = run(reg.reserve("op-1", ttl_seconds=5, tenant_id="tenant-a"))
    assert run(reg.commit_dispatch("op-1", fence=first.fence, tenant_id="tenant-a"))
    assert run(reg.mark_unknown("op-1", fence=first.fence, tenant_id="tenant-a"))
    clock["t"] += 10_000
    retry = run(reg.reserve("op-1", tenant_id="tenant-a"))
    assert not retry.ok
    assert retry.status == ReserveStatus.DUPLICATE_UNKNOWN


def test_executed_does_not_expire_into_admittable_state():
    """Test scenario 14 / Round 18 requirement 3: EXECUTED must not
    silently become executable again through TTL expiry. ``mark_executed``
    accepts no ``ttl_seconds`` at all (Round 18 removed it) -- an EXECUTED
    record is unconditionally permanent; there is no parameter that could
    ever cause it to expire and be re-admitted."""
    clock = {"t": 1000.0}
    reg = redis_reg(clock=lambda: clock["t"])
    first = run(reg.reserve("op-1", ttl_seconds=5, tenant_id="tenant-a"))
    assert run(reg.commit_dispatch("op-1", fence=first.fence, tenant_id="tenant-a"))
    assert run(reg.mark_executed("op-1", fence=first.fence, tenant_id="tenant-a"))
    clock["t"] += 10_000
    retry = run(reg.reserve("op-1", tenant_id="tenant-a"))
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
    first = run(before.reserve("op-1", tenant_id="tenant-a"))
    assert run(before.commit_dispatch("op-1", fence=first.fence, tenant_id="tenant-a"))

    after = RedisIdempotencyRegistry(IdemFakeRedis(store))  # "process restart"
    record = run(after.get_state("op-1", tenant_id="tenant-a"))
    assert record.state == IdempotencyState.DISPATCH_OWNED
    assert run(after.reserve("op-1", tenant_id="tenant-a")).status == ReserveStatus.DUPLICATE_INFLIGHT


def test_unknown_persists_across_restart():
    store = {}
    before = RedisIdempotencyRegistry(IdemFakeRedis(store))
    first = run(before.reserve("op-1", tenant_id="tenant-a"))
    assert run(before.commit_dispatch("op-1", fence=first.fence, tenant_id="tenant-a"))
    assert run(before.mark_unknown("op-1", fence=first.fence, tenant_id="tenant-a"))

    after = RedisIdempotencyRegistry(IdemFakeRedis(store))
    record = run(after.get_state("op-1", tenant_id="tenant-a"))
    assert record.state == IdempotencyState.UNKNOWN
    assert run(after.reserve("op-1", tenant_id="tenant-a")).status == ReserveStatus.DUPLICATE_UNKNOWN


def test_executed_persists_across_restart():
    store = {}
    before = RedisIdempotencyRegistry(IdemFakeRedis(store))
    first = run(before.reserve("op-1", tenant_id="tenant-a"))
    assert run(before.commit_dispatch("op-1", fence=first.fence, tenant_id="tenant-a"))
    assert run(before.mark_executed("op-1", fence=first.fence, tenant_id="tenant-a"))

    after = RedisIdempotencyRegistry(IdemFakeRedis(store))
    record = run(after.get_state("op-1", tenant_id="tenant-a"))
    assert record.state == IdempotencyState.EXECUTED
    assert run(after.reserve("op-1", tenant_id="tenant-a")).status == ReserveStatus.DUPLICATE_EXECUTED


def test_inmemory_registry_is_not_durable_across_instances():
    """Test scenario 12: a genuinely durable claim requires a shared backend
    (proven above via a SHARED fake-Redis store across two registry
    instances). Two independent ``InMemoryIdempotencyRegistry`` instances do
    NOT share state -- this is the negative control proving the durability
    tests above are actually exercising cross-instance persistence, not an
    artifact of both sides happening to read the same in-process dict."""
    a = InMemoryIdempotencyRegistry()
    b = InMemoryIdempotencyRegistry()
    first = run(a.reserve("op-1", tenant_id="tenant-a"))
    run(a.commit_dispatch("op-1", fence=first.fence, tenant_id="tenant-a"))
    run(a.mark_executed("op-1", fence=first.fence, tenant_id="tenant-a"))
    assert run(a.get_state("op-1", tenant_id="tenant-a")).state == IdempotencyState.EXECUTED
    assert run(b.get_state("op-1", tenant_id="tenant-a")) is None  # instance B has no idea this happened
    assert run(b.reserve("op-1", tenant_id="tenant-a")).ok  # and would (wrongly, if relied on as durable) admit it again


# ---- Fenced state transitions: stale owners are rejected ----

def test_stale_fence_rejected_for_every_mutation():
    """Test scenarios 15/16: a stale fence (from a superseded generation)
    cannot mark executed, mark unknown, or release/regress the CURRENT
    generation's state."""
    reg = InMemoryIdempotencyRegistry()
    gen1 = run(reg.reserve("op-1", tenant_id="tenant-a"))
    stale_fence = gen1.fence
    assert run(reg.release("op-1", fence=stale_fence, tenant_id="tenant-a"))  # legitimate pre-dispatch release
    gen2 = run(reg.reserve("op-1", tenant_id="tenant-a"))
    assert gen2.fence != stale_fence
    assert run(reg.commit_dispatch("op-1", fence=gen2.fence, tenant_id="tenant-a"))

    assert run(reg.mark_executed("op-1", fence=stale_fence, tenant_id="tenant-a")) is False
    assert run(reg.mark_unknown("op-1", fence=stale_fence, tenant_id="tenant-a")) is False
    assert run(reg.release("op-1", fence=stale_fence, tenant_id="tenant-a")) is False
    # current state is unaffected by any of the stale attempts
    record = run(reg.get_state("op-1", tenant_id="tenant-a"))
    assert record.state == IdempotencyState.DISPATCH_OWNED
    assert record.generation == gen2.fence


def test_stale_fence_cannot_regress_executed_to_unknown():
    reg = InMemoryIdempotencyRegistry()
    gen = run(reg.reserve("op-1", tenant_id="tenant-a"))
    run(reg.commit_dispatch("op-1", fence=gen.fence, tenant_id="tenant-a"))
    run(reg.mark_executed("op-1", fence=gen.fence, tenant_id="tenant-a"))
    # An attempt using a fabricated/foreign fence cannot regress EXECUTED.
    assert run(reg.mark_unknown("op-1", fence="not-a-real-fence", tenant_id="tenant-a")) is False
    assert run(reg.get_state("op-1", tenant_id="tenant-a")).state == IdempotencyState.EXECUTED


# ---- Round 18 requirement 2: no unfenced ownership deletion. ``release`` is
# the only remaining deletion-capable call (``mark_failed`` is removed
# entirely -- it deleted DISPATCH_OWNED/UNKNOWN/EXECUTED records
# unconditionally, regardless of fence). ``release`` itself only ever
# succeeds from RESERVED with the correct, current fence; every other
# (state, fence) combination is rejected and the protected record survives
# unchanged. ----

def test_mark_failed_no_longer_exists_on_either_backend():
    """Requirement 2: the unsafe, unfenced deletion API is removed
    entirely, not merely restricted -- there is no ``mark_failed`` to call
    at all."""
    assert not hasattr(InMemoryIdempotencyRegistry(), "mark_failed")
    assert not hasattr(redis_reg(), "mark_failed")


@pytest.mark.parametrize("reg", registries())
def test_release_deletion_attempt_against_dispatch_owned_preserves_record(reg):
    gen = run(reg.reserve("op-1", binding="b", tenant_id="tenant-a"))
    run(reg.commit_dispatch("op-1", fence=gen.fence, tenant_id="tenant-a"))
    # Even with the CORRECT, current fence, release() refuses once the
    # state has moved past RESERVED.
    assert run(reg.release("op-1", fence=gen.fence, tenant_id="tenant-a")) is False
    record = run(reg.get_state("op-1", tenant_id="tenant-a"))
    assert record.state == IdempotencyState.DISPATCH_OWNED
    assert record.generation == gen.fence


@pytest.mark.parametrize("reg", registries())
def test_release_deletion_attempt_against_unknown_preserves_record(reg):
    gen = run(reg.reserve("op-1", binding="b", tenant_id="tenant-a"))
    run(reg.commit_dispatch("op-1", fence=gen.fence, tenant_id="tenant-a"))
    run(reg.mark_unknown("op-1", fence=gen.fence, tenant_id="tenant-a"))
    assert run(reg.release("op-1", fence=gen.fence, tenant_id="tenant-a")) is False
    record = run(reg.get_state("op-1", tenant_id="tenant-a"))
    assert record.state == IdempotencyState.UNKNOWN
    assert record.generation == gen.fence


@pytest.mark.parametrize("reg", registries())
def test_release_deletion_attempt_against_executed_preserves_record(reg):
    gen = run(reg.reserve("op-1", binding="b", tenant_id="tenant-a"))
    run(reg.commit_dispatch("op-1", fence=gen.fence, tenant_id="tenant-a"))
    run(reg.mark_executed("op-1", fence=gen.fence, binding="b", tenant_id="tenant-a"))
    assert run(reg.release("op-1", fence=gen.fence, tenant_id="tenant-a")) is False
    record = run(reg.get_state("op-1", tenant_id="tenant-a"))
    assert record.state == IdempotencyState.EXECUTED
    assert record.generation == gen.fence


@pytest.mark.parametrize("reg", registries())
def test_stale_generation_deletion_attempt_preserves_record(reg):
    """A stale (superseded) generation can never delete the CURRENT
    generation's record, regardless of which state it is in."""
    first = run(reg.reserve("op-1", binding="b", tenant_id="tenant-a"))
    stale_fence = first.fence
    assert run(reg.release("op-1", fence=stale_fence, tenant_id="tenant-a"))  # legitimate: still RESERVED at this point
    second = run(reg.reserve("op-1", binding="b", tenant_id="tenant-a"))
    assert second.fence != stale_fence
    run(reg.commit_dispatch("op-1", fence=second.fence, tenant_id="tenant-a"))
    # The stale fence from the FIRST (superseded) generation can never
    # delete/regress the SECOND (current) generation's record.
    assert run(reg.release("op-1", fence=stale_fence, tenant_id="tenant-a")) is False
    record = run(reg.get_state("op-1", tenant_id="tenant-a"))
    assert record.state == IdempotencyState.DISPATCH_OWNED
    assert record.generation == second.fence


# ---- Reconciliation ----

def test_resolve_unknown_to_executed():
    reg = InMemoryIdempotencyRegistry()
    gen = run(reg.reserve("op-1", binding="b", tenant_id="tenant-a"))
    run(reg.commit_dispatch("op-1", fence=gen.fence, tenant_id="tenant-a"))
    run(reg.mark_unknown("op-1", fence=gen.fence, tenant_id="tenant-a"))
    result = run(reg.resolve_unknown("op-1", expected_generation=gen.fence, result_ref="issue-42", tenant_id="tenant-a"))
    assert result.resolved
    record = run(reg.get_state("op-1", tenant_id="tenant-a"))
    assert record.state == IdempotencyState.EXECUTED
    assert record.result_ref == "issue-42"


def test_reconciliation_never_creates_only_resolves_existing_unknown():
    reg = InMemoryIdempotencyRegistry()
    result = run(reg.resolve_unknown("never-admitted", expected_generation="whatever", tenant_id="tenant-a"))
    assert result.status == ReconcileStatus.NOT_FOUND


def test_reconciliation_races_with_late_completion_exactly_one_wins():
    """Test scenario 17: reconciliation (positive external evidence) racing
    with the ORIGINAL dispatcher's own late-arriving completion. Exactly one
    write applies; the other observes it is no longer UNKNOWN and no-ops --
    in particular, reconciliation never itself invokes any actuator, so
    "coherent final state, zero duplicate actuator calls" holds trivially."""
    reg = InMemoryIdempotencyRegistry()
    gen = run(reg.reserve("op-1", tenant_id="tenant-a"))
    run(reg.commit_dispatch("op-1", fence=gen.fence, tenant_id="tenant-a"))
    run(reg.mark_unknown("op-1", fence=gen.fence, tenant_id="tenant-a"))

    async def race():
        return await asyncio.gather(
            reg.resolve_unknown("op-1", expected_generation=gen.fence, result_ref="from-reconciliation", tenant_id="tenant-a"),
            reg.mark_executed("op-1", fence=gen.fence, result_ref="from-late-dispatcher", tenant_id="tenant-a"),
        )

    reconcile_result, late_dispatcher_ok = run(race())
    # Exactly one of the two writers actually applies the UNKNOWN -> EXECUTED
    # transition (asyncio's cooperative scheduling still means one Python
    # coroutine's synchronous critical section runs to completion before the
    # other starts; this pins the invariant that matters -- never both).
    applied = int(reconcile_result.resolved) + int(late_dispatcher_ok)
    assert applied == 1
    final = run(reg.get_state("op-1", tenant_id="tenant-a"))
    assert final.state == IdempotencyState.EXECUTED  # coherent final state either way


def test_reconciliation_races_with_fresh_retry_zero_second_create():
    """Test scenario 18: a fresh retry attempt racing with reconciliation
    must never be admitted while the operation is still UNKNOWN -- so no
    second "create" can occur no matter which happens first."""
    reg = InMemoryIdempotencyRegistry()
    gen = run(reg.reserve("op-1", binding="b", tenant_id="tenant-a"))
    run(reg.commit_dispatch("op-1", fence=gen.fence, tenant_id="tenant-a"))
    run(reg.mark_unknown("op-1", fence=gen.fence, tenant_id="tenant-a"))

    async def race():
        return await asyncio.gather(
            reg.resolve_unknown("op-1", expected_generation=gen.fence, result_ref="ev", tenant_id="tenant-a"),
            reg.reserve("op-1", binding="b", tenant_id="tenant-a"),
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
        run(reg.get_state("op-1", tenant_id="tenant-a"))


def test_get_state_absent_key_returns_none_not_unavailable():
    reg = InMemoryIdempotencyRegistry()
    assert run(reg.get_state("never-reserved", tenant_id="tenant-a")) is None


# ---- Fail-closed ----

def test_registry_outage_fails_closed():
    reg = RedisIdempotencyRegistry(DownRedis())
    res = run(reg.reserve("op-1", tenant_id="tenant-a"))
    assert not res.ok
    assert res.status == ReserveStatus.ERROR


def test_invalid_key_fails_closed():
    reg = InMemoryIdempotencyRegistry()
    assert not run(reg.reserve("", tenant_id="tenant-a")).ok


def test_invalid_binding_fails_closed_on_redis():
    """A binding containing the field delimiter must never be accepted --
    it could otherwise corrupt the encoded record and forge a state."""
    reg = redis_reg()
    res = run(reg.reserve("op-1", binding="has|a|pipe", tenant_id="tenant-a"))
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


# ===========================================================================
# PR #105 -- tenant-scoped durable execution identity.
#
# Durable identity is the PAIR (tenant_id, key), never key alone. Every test
# below proves a property that would NOT hold if the registry were still
# keyed by the raw key alone -- most importantly test matrix item A/
# requirement 7 (merge-blocking): two tenants sharing BOTH the identical raw
# key AND the identical binding must be fully independent.
# ===========================================================================

from mcc_core.idempotency import MigrationStatus, migrate_legacy_record  # noqa: E402


@pytest.mark.parametrize("reg", registries())
def test_a_identical_id_and_identical_binding_cross_tenant_fully_independent(reg):
    """Test matrix item A / requirement 1 & 7 (merge-blocking): tenant-a and
    tenant-b both present the SAME raw logical_operation_id AND the SAME
    binding (identical action/resource/payload). Neither may observe,
    block, or be blocked by the other's record -- each independently
    reaches its own EXECUTED."""
    key, binding = "op-alias-123", "same-action-resource-payload-hash"

    a_first = run(reg.reserve(key, tenant_id="tenant-a", binding=binding))
    b_first = run(reg.reserve(key, tenant_id="tenant-b", binding=binding))
    assert a_first.ok and a_first.status == ReserveStatus.RESERVED
    assert b_first.ok and b_first.status == ReserveStatus.RESERVED
    assert a_first.fence != b_first.fence  # structurally distinct records

    assert run(reg.commit_dispatch(key, tenant_id="tenant-a", fence=a_first.fence))
    assert run(reg.mark_executed(key, tenant_id="tenant-a", fence=a_first.fence, binding=binding,
                                 result_ref="tenant-a-result"))

    # tenant-b's record is COMPLETELY unaffected by tenant-a reaching EXECUTED.
    b_state = run(reg.get_state(key, tenant_id="tenant-b"))
    assert b_state.state == IdempotencyState.RESERVED

    assert run(reg.commit_dispatch(key, tenant_id="tenant-b", fence=b_first.fence))
    assert run(reg.mark_executed(key, tenant_id="tenant-b", fence=b_first.fence, binding=binding,
                                 result_ref="tenant-b-result"))

    a_state = run(reg.get_state(key, tenant_id="tenant-a"))
    b_state = run(reg.get_state(key, tenant_id="tenant-b"))
    assert a_state.state == IdempotencyState.EXECUTED and a_state.result_ref == "tenant-a-result"
    assert b_state.state == IdempotencyState.EXECUTED and b_state.result_ref == "tenant-b-result"


@pytest.mark.parametrize("reg", registries())
def test_b_reserve_by_one_tenant_never_blocks_the_same_id_for_another(reg):
    """Non-inheritance of RESERVED: tenant-a holding a RESERVED record for
    a key must never cause DUPLICATE_INFLIGHT for tenant-b presenting the
    identical key."""
    key = "op-shared-key"
    a = run(reg.reserve(key, tenant_id="tenant-a", binding="b"))
    assert a.ok
    b = run(reg.reserve(key, tenant_id="tenant-b", binding="b"))
    assert b.ok
    assert b.status == ReserveStatus.RESERVED


@pytest.mark.parametrize("reg", registries())
def test_b_dispatch_owned_does_not_inherit_across_tenants(reg):
    key = "op-dispatch-owned"
    a = run(reg.reserve(key, tenant_id="tenant-a", binding="b"))
    assert run(reg.commit_dispatch(key, tenant_id="tenant-a", fence=a.fence))
    # tenant-b, same raw key: sees no record at all, freely admits.
    assert run(reg.get_state(key, tenant_id="tenant-b")) is None
    b = run(reg.reserve(key, tenant_id="tenant-b", binding="b"))
    assert b.ok and b.status == ReserveStatus.RESERVED


@pytest.mark.parametrize("reg", registries())
def test_b_unknown_does_not_inherit_across_tenants(reg):
    key = "op-unknown-cross-tenant"
    a = run(reg.reserve(key, tenant_id="tenant-a", binding="b"))
    run(reg.commit_dispatch(key, tenant_id="tenant-a", fence=a.fence))
    run(reg.mark_unknown(key, tenant_id="tenant-a", fence=a.fence))
    assert run(reg.get_state(key, tenant_id="tenant-a")).state == IdempotencyState.UNKNOWN
    assert run(reg.get_state(key, tenant_id="tenant-b")) is None
    b = run(reg.reserve(key, tenant_id="tenant-b", binding="b"))
    assert b.ok  # tenant-a's UNKNOWN never blocks tenant-b


@pytest.mark.parametrize("reg", registries())
def test_b_executed_does_not_inherit_across_tenants(reg):
    key = "op-executed-cross-tenant"
    a = run(reg.reserve(key, tenant_id="tenant-a", binding="b"))
    run(reg.commit_dispatch(key, tenant_id="tenant-a", fence=a.fence))
    run(reg.mark_executed(key, tenant_id="tenant-a", fence=a.fence, binding="b"))
    assert run(reg.get_state(key, tenant_id="tenant-a")).state == IdempotencyState.EXECUTED
    assert run(reg.get_state(key, tenant_id="tenant-b")) is None
    b = run(reg.reserve(key, tenant_id="tenant-b", binding="b"))
    assert b.ok  # tenant-a's EXECUTED never blocks or is inherited by tenant-b


@pytest.mark.parametrize("reg", registries())
def test_c_same_tenant_duplicate_and_binding_conflict_semantics_unchanged(reg):
    """Requirement 9: same-tenant behavior (the entire pre-PR-105 test suite
    above) is unaffected -- re-asserted explicitly here alongside the new
    cross-tenant tests as a direct side-by-side regression guard."""
    key = "op-same-tenant-regression"
    first = run(reg.reserve(key, tenant_id="tenant-a", binding="b1"))
    assert first.ok
    dup = run(reg.reserve(key, tenant_id="tenant-a", binding="b1"))
    assert dup.status == ReserveStatus.DUPLICATE_INFLIGHT
    conflict = run(reg.reserve(key, tenant_id="tenant-a", binding="b2"))
    assert conflict.status == ReserveStatus.BINDING_CONFLICT


@pytest.mark.parametrize("reg", registries())
def test_d_fence_from_one_tenant_is_meaningless_against_another_tenants_record(reg):
    """A fence issued for (tenant-a, key) can never finalize/release/
    resolve (tenant-b, key)'s record, even when tenant-b's record happens
    to exist under the identical raw key."""
    key = "op-cross-tenant-fence"
    a = run(reg.reserve(key, tenant_id="tenant-a", binding="b"))
    b = run(reg.reserve(key, tenant_id="tenant-b", binding="b"))
    assert a.fence != b.fence

    # tenant-a's fence cannot commit-dispatch tenant-b's record.
    assert run(reg.commit_dispatch(key, tenant_id="tenant-b", fence=a.fence)) is False
    assert run(reg.get_state(key, tenant_id="tenant-b")).state == IdempotencyState.RESERVED

    # tenant-a's fence cannot release tenant-b's record either (the correct
    # fence for tenant-b's OWN record is the only one that can).
    assert run(reg.release(key, tenant_id="tenant-b", fence=a.fence)) is False
    assert run(reg.get_state(key, tenant_id="tenant-b")).state == IdempotencyState.RESERVED

    # The legitimate owner (tenant-b, its own fence) still works normally.
    assert run(reg.commit_dispatch(key, tenant_id="tenant-b", fence=b.fence))
    assert run(reg.get_state(key, tenant_id="tenant-a")).state == IdempotencyState.RESERVED  # untouched


@pytest.mark.parametrize("reg", registries())
def test_e_concurrent_cross_tenant_race_on_identical_id_and_binding_both_win(reg):
    """Test matrix item H: two tenants racing to reserve the IDENTICAL raw
    key with the IDENTICAL binding concurrently must BOTH independently
    succeed -- unlike the same-tenant race (`test_concurrent_duplicate_
    exactly_one_winner`), where exactly one wins."""
    key, binding = "op-concurrent-cross-tenant", "same-binding"

    async def race():
        return await asyncio.gather(
            reg.reserve(key, tenant_id="tenant-a", binding=binding),
            reg.reserve(key, tenant_id="tenant-b", binding=binding),
        )

    a_result, b_result = run(race())
    assert a_result.ok and a_result.status == ReserveStatus.RESERVED
    assert b_result.ok and b_result.status == ReserveStatus.RESERVED


def test_f_redis_restart_persistence_is_tenant_isolated():
    """Test matrix item I: cross-instance ("process restart") persistence
    holds per-tenant -- a restarted instance sees the CORRECT tenant's
    state and never the other tenant's, for the identical raw key."""
    store = {}
    before = RedisIdempotencyRegistry(IdemFakeRedis(store))
    key = "op-restart-tenant-isolation"
    a = run(before.reserve(key, tenant_id="tenant-a", binding="b"))
    run(before.commit_dispatch(key, tenant_id="tenant-a", fence=a.fence))
    run(before.mark_executed(key, tenant_id="tenant-a", fence=a.fence, binding="b"))
    b = run(before.reserve(key, tenant_id="tenant-b", binding="b"))
    run(before.commit_dispatch(key, tenant_id="tenant-b", fence=b.fence))
    # tenant-b left DISPATCH_OWNED (not yet EXECUTED) -- distinct state.

    after = RedisIdempotencyRegistry(IdemFakeRedis(store))  # "process restart"
    a_after = run(after.get_state(key, tenant_id="tenant-a"))
    b_after = run(after.get_state(key, tenant_id="tenant-b"))
    assert a_after.state == IdempotencyState.EXECUTED
    assert b_after.state == IdempotencyState.DISPATCH_OWNED
    # A fresh reservation attempt under tenant-a's scope is still blocked
    # (DUPLICATE_EXECUTED); under tenant-b's scope, still blocked
    # (DUPLICATE_INFLIGHT) -- neither leaked into or was satisfied by the
    # other's post-restart state.
    assert run(after.reserve(key, tenant_id="tenant-a", binding="b")).status == ReserveStatus.DUPLICATE_EXECUTED
    assert run(after.reserve(key, tenant_id="tenant-b", binding="b")).status == ReserveStatus.DUPLICATE_INFLIGHT


@pytest.mark.parametrize("reg", registries())
def test_g_reconciliation_resolve_unknown_is_tenant_isolated(reg):
    """Requirement 10 / test matrix item D (reconciliation half): tenant-a's
    ``resolve_unknown`` call, using tenant-a's own observed fence, must
    never resolve tenant-b's UNKNOWN record for the identical raw key --
    and vice versa. Each tenant's reconciliation is scoped exactly as
    tightly as every other durable mutation."""
    key, binding = "op-reconcile-cross-tenant", "same-binding"

    a = run(reg.reserve(key, tenant_id="tenant-a", binding=binding))
    run(reg.commit_dispatch(key, tenant_id="tenant-a", fence=a.fence))
    run(reg.mark_unknown(key, tenant_id="tenant-a", fence=a.fence))

    b = run(reg.reserve(key, tenant_id="tenant-b", binding=binding))
    run(reg.commit_dispatch(key, tenant_id="tenant-b", fence=b.fence))
    run(reg.mark_unknown(key, tenant_id="tenant-b", fence=b.fence))

    # tenant-a resolves ONLY its own record; tenant-b's stays UNKNOWN.
    resolved_a = run(reg.resolve_unknown(key, tenant_id="tenant-a", expected_generation=a.fence,
                                         result_ref="tenant-a-evidence"))
    assert resolved_a.resolved
    a_state = run(reg.get_state(key, tenant_id="tenant-a"))
    b_state = run(reg.get_state(key, tenant_id="tenant-b"))
    assert a_state.state == IdempotencyState.EXECUTED
    assert a_state.result_ref == "tenant-a-evidence"
    assert b_state.state == IdempotencyState.UNKNOWN  # completely unaffected

    # tenant-b's OWN resolve_unknown (its own fence) still works normally --
    # tenant-a's prior resolution did not consume or otherwise disturb it.
    resolved_b = run(reg.resolve_unknown(key, tenant_id="tenant-b", expected_generation=b.fence,
                                         result_ref="tenant-b-evidence"))
    assert resolved_b.resolved
    b_state_final = run(reg.get_state(key, tenant_id="tenant-b"))
    assert b_state_final.state == IdempotencyState.EXECUTED
    assert b_state_final.result_ref == "tenant-b-evidence"


@pytest.mark.parametrize("reg", registries())
def test_g_reconciliation_cannot_use_tenant_as_fence_substitute(reg):
    """A tenant's fence is meaningful only within its own (tenant_id, key)
    scope -- presenting tenant-a's genuinely-correct fence value against
    tenant-b's identity does not resolve tenant-b's record, because the
    generation values themselves are independent per tenant (distinct
    ``uuid4()`` draws), not merely because of a tenant check. This directly
    demonstrates why fencing plus tenant scoping together (never either
    alone) is what makes cross-tenant resolution structurally impossible."""
    key, binding = "op-reconcile-fence-cross-tenant", "same-binding"
    a = run(reg.reserve(key, tenant_id="tenant-a", binding=binding))
    run(reg.commit_dispatch(key, tenant_id="tenant-a", fence=a.fence))
    run(reg.mark_unknown(key, tenant_id="tenant-a", fence=a.fence))

    b = run(reg.reserve(key, tenant_id="tenant-b", binding=binding))
    run(reg.commit_dispatch(key, tenant_id="tenant-b", fence=b.fence))
    run(reg.mark_unknown(key, tenant_id="tenant-b", fence=b.fence))

    # tenant-a's own fence, presented under tenant-b's identity: addresses a
    # structurally different (tenant_id, key) record entirely, so it is
    # simply the WRONG fence for tenant-b's own generation -- STALE_GENERATION,
    # not a successful cross-tenant resolution.
    result = run(reg.resolve_unknown(key, tenant_id="tenant-b", expected_generation=a.fence,
                                     result_ref="attempted-cross-tenant-resolve"))
    assert result.status == ReconcileStatus.STALE_GENERATION
    assert run(reg.get_state(key, tenant_id="tenant-b")).state == IdempotencyState.UNKNOWN
    assert run(reg.get_state(key, tenant_id="tenant-a")).state == IdempotencyState.UNKNOWN


# ---- Mandatory tenant_id: no unscoped path ----

def test_missing_tenant_id_fails_closed_on_reserve_inmemory():
    reg = InMemoryIdempotencyRegistry()
    res = run(reg.reserve("op-1", tenant_id=""))
    assert res.status == ReserveStatus.ERROR


def test_missing_tenant_id_fails_closed_on_reserve_redis():
    reg = redis_reg()
    res = run(reg.reserve("op-1", tenant_id=""))
    assert res.status == ReserveStatus.ERROR


def test_missing_tenant_id_raises_on_get_state_inmemory():
    reg = InMemoryIdempotencyRegistry()
    with pytest.raises(ValueError):
        run(reg.get_state("op-1", tenant_id=""))


def test_missing_tenant_id_raises_on_get_state_redis():
    reg = redis_reg()
    with pytest.raises(ValueError):
        run(reg.get_state("op-1", tenant_id=""))


def test_reserve_requires_tenant_id_keyword_argument_no_default():
    """No default exists on either backend -- an omitted tenant_id is a
    caller bug caught immediately (TypeError), never a silently-scoped
    default."""
    with pytest.raises(TypeError):
        run(InMemoryIdempotencyRegistry().reserve("op-1"))
    with pytest.raises(TypeError):
        run(redis_reg().reserve("op-1"))


# ---- Legacy (pre-tenant-scoping) migration (requirement 11, security-critical) ----

def _legacy_store_with(key: str, state: str, generation: str, binding: str, result_ref: str = "") -> dict:
    """Writes ONE record under the OLD (pre-PR-105) unscoped key format
    (``namespace + key``, no tenant dimension) directly into a fake-Redis
    store -- modeling data written before this migration existed."""
    namespace = "mcc:idem:"
    return {namespace + key: (f"{state}|{generation}|{binding}|{result_ref}", None)}


def test_legacy_record_blocks_reserve_under_new_tenant_scope():
    """A pre-PR-105 record for the raw key must not be silently invisible
    to a tenant-scoped reserve() -- it fails closed with a distinct signal,
    never "not found -> safe to admit" (which would open a duplicate-
    actuation window)."""
    key = "op-legacy-1"
    store = _legacy_store_with(key, "EXECUTED", "gen-legacy", "b")
    reg = RedisIdempotencyRegistry(IdemFakeRedis(store))
    res = run(reg.reserve(key, tenant_id="tenant-a", binding="b"))
    assert res.status == ReserveStatus.LEGACY_UNMIGRATED
    assert not res.ok


def test_legacy_record_blocks_get_state_under_new_tenant_scope():
    key = "op-legacy-2"
    store = _legacy_store_with(key, "DISPATCH_OWNED", "gen-legacy", "b")
    reg = RedisIdempotencyRegistry(IdemFakeRedis(store))
    with pytest.raises(IdempotencyBackendUnavailable):
        run(reg.get_state(key, tenant_id="tenant-a"))


def test_legacy_record_never_silently_reopens_an_already_executed_operation():
    """Security-critical (requirement 11): the exact failure mode a naive
    re-key would introduce -- "no record at the new key -> safe to admit" --
    must never happen. Proven end-to-end: a legacy EXECUTED record blocks
    admission until explicit, operator-invoked migration; after migration,
    the SAME id under the SAME tenant scope still reports DUPLICATE_EXECUTED
    (never a fresh RESERVED) -- there is no window in which a second
    dispatch could be admitted."""
    key = "op-legacy-no-reopen"
    store = _legacy_store_with(key, "EXECUTED", "gen-legacy", "the-real-binding", "issue-999")
    reg = RedisIdempotencyRegistry(IdemFakeRedis(store))

    blocked = run(reg.reserve(key, tenant_id="tenant-a", binding="the-real-binding"))
    assert blocked.status == ReserveStatus.LEGACY_UNMIGRATED

    migrated = run(migrate_legacy_record(reg, tenant_id="tenant-a", key=key))
    assert migrated.status == MigrationStatus.MIGRATED
    assert migrated.ok

    # Immediately after migration -- no gap in which a fresh RESERVED could
    # have been admitted.
    after = run(reg.reserve(key, tenant_id="tenant-a", binding="the-real-binding"))
    assert after.status == ReserveStatus.DUPLICATE_EXECUTED

    state = run(reg.get_state(key, tenant_id="tenant-a"))
    assert state.state == IdempotencyState.EXECUTED
    assert state.result_ref == "issue-999"

    # The legacy key itself is gone (default delete_legacy=True).
    assert reg._legacy_key(key) not in reg._redis.store


def test_migrate_legacy_record_is_idempotent_and_safe_on_absent_legacy_record():
    key = "op-no-legacy-record-at-all"
    reg = RedisIdempotencyRegistry(IdemFakeRedis({}))
    first = run(migrate_legacy_record(reg, tenant_id="tenant-a", key=key))
    assert first.status == MigrationStatus.ABSENT and first.ok
    second = run(migrate_legacy_record(reg, tenant_id="tenant-a", key=key))
    assert second.status == MigrationStatus.ABSENT and second.ok  # still a safe no-op
    # And a fresh reservation is now cleanly admissible (nothing to block it).
    assert run(reg.reserve(key, tenant_id="tenant-a", binding="b")).ok


def test_migrate_legacy_record_does_not_claim_ownership_based_on_binding_alone():
    """Requirement 11: migration never inspects or matches on binding to
    "auto-detect" the owning tenant -- it is an explicit, operator-directed
    action naming the tenant outright. Migrating the SAME legacy record
    under a DIFFERENT (wrong) tenant is exactly as mechanically possible as
    the correct one -- there is no binding-based safety net baked into the
    function itself; correctness depends entirely on the operator's
    out-of-band verification, which this module deliberately does not
    second-guess. This test documents that boundary rather than asserting
    a (nonexistent) automatic protection."""
    key = "op-legacy-wrong-tenant"
    store = _legacy_store_with(key, "EXECUTED", "gen-legacy", "b")
    reg = RedisIdempotencyRegistry(IdemFakeRedis(store))
    run(migrate_legacy_record(reg, tenant_id="tenant-WRONG", key=key))
    # The record now lives under tenant-WRONG's scope -- the correct tenant
    # (tenant-a) sees nothing and would (incorrectly, if this operator error
    # went uncaught) be able to admit a fresh reservation. This is why
    # requirement 11 places the burden of correct attribution on the
    # operator's out-of-band verification, not on this function.
    assert run(reg.get_state(key, tenant_id="tenant-a")) is None
    assert run(reg.get_state(key, tenant_id="tenant-WRONG")).state == IdempotencyState.EXECUTED


def test_migrate_legacy_record_delete_legacy_false_preserves_legacy_key():
    key = "op-legacy-keep"
    store = _legacy_store_with(key, "EXECUTED", "gen-legacy", "b")
    reg = RedisIdempotencyRegistry(IdemFakeRedis(store))
    run(migrate_legacy_record(reg, tenant_id="tenant-a", key=key, delete_legacy=False))
    assert reg._legacy_key(key) in reg._redis.store
    # Scoped copy now exists too.
    assert run(reg.get_state(key, tenant_id="tenant-a")).state == IdempotencyState.EXECUTED


# ===========================================================================
# PR #105 remediation round -- mandatory adversarial tests A-E.
#
# Blocker 1 fix: the tenant-scoped root and the migration-claim root are
# each derived from the legacy namespace so that NEITHER can ever be
# produced by ``namespace + <any raw legacy key>`` (see
# ``_derive_disjoint_root`` in src/mcc_core/idempotency.py). Blocker 2 fix:
# migrate_legacy_record validates tenant_id/key BEFORE any Redis call.
# Blocker 3 fix: migration is one atomic Lua script gated by a per-legacy-key
# claim marker, so at most one tenant may ever successfully migrate a given
# legacy record, with no read-then-write race window.
# ===========================================================================

from mcc_core import redis_keys  # noqa: E402


# -- A: legacy/scoped key alias regression (the exact former alias) -------- #

def test_a_legacy_scoped_key_alias_no_longer_exists():
    """Reconstructs the EXACT former alias: a legacy raw key equal to
    ``hash_component(tenant_id) + ':' + operation_id`` used to collide
    byte-for-byte with the new tenant-scoped key for (tenant_id,
    operation_id) under the pre-remediation scheme (``namespace +
    hash(tenant_id) + ':' + key``). Proves the new keyspace design is
    structurally disjoint: the two keys differ, and a durable record
    planted under the adversarial legacy raw key is never returned as,
    never overwrites, and never blocks the real scoped record."""
    reg = RedisIdempotencyRegistry(IdemFakeRedis({}))
    tenant_id, operation_id = "tenant-a", "op-1"
    adversarial_raw_key = redis_keys.hash_component(tenant_id) + ":" + operation_id
    old_style_alias_key = reg._namespace + adversarial_raw_key  # the pre-fix formula
    new_scoped_key = reg._key(tenant_id, operation_id)

    assert old_style_alias_key != new_scoped_key, "Blocker 1 regression: keys alias again"

    # Plant a real EXECUTED record under the adversarial legacy raw key.
    reg._redis.store[reg._legacy_key(adversarial_raw_key)] = ("EXECUTED|gen-adv|adv-binding|adv-result", None)

    # The real (tenant_id, operation_id) scoped state is untouched: no
    # record, no leak, no false LEGACY_UNMIGRATED block.
    assert run(reg.get_state(operation_id, tenant_id=tenant_id)) is None
    fresh = run(reg.reserve(operation_id, tenant_id=tenant_id, binding="the-real-binding"))
    assert fresh.status == ReserveStatus.RESERVED, fresh
    # And the adversarial legacy record itself is completely undisturbed.
    assert reg._redis.store[reg._legacy_key(adversarial_raw_key)][0] == "EXECUTED|gen-adv|adv-binding|adv-result"


def test_a_scoped_and_claim_roots_are_pairwise_disjoint_from_legacy():
    """Directly proves the three key-family roots (legacy, tenant-scoped,
    migration-claim) are pairwise non-prefixing, for the actual configured
    namespace -- the general property `_derive_disjoint_root` relies on,
    not just one example."""
    reg = RedisIdempotencyRegistry(IdemFakeRedis({}))
    legacy_root = reg._namespace
    scoped_root = reg._scoped_root
    claim_root = reg._claim_root
    roots = [legacy_root, scoped_root, claim_root]
    for i, a in enumerate(roots):
        for j, b in enumerate(roots):
            if i == j:
                continue
            assert not b.startswith(a), (a, b)


# -- B: migration with a blank/invalid tenant leaves the legacy record untouched -- #

@pytest.mark.parametrize("bad_tenant", [None, "", "   ", "\t", 12345, [], {}])
def test_b_blank_or_invalid_tenant_migration_fails_closed(bad_tenant):
    key = "op-blank-tenant-migration"
    store = _legacy_store_with(key, "EXECUTED", "gen-legacy", "b", "issue-1")
    reg = RedisIdempotencyRegistry(IdemFakeRedis(store))
    original = dict(reg._redis.store)

    result = run(migrate_legacy_record(reg, tenant_id=bad_tenant, key=key))
    assert result.status == MigrationStatus.INVALID_INPUT
    assert not result.ok
    # Zero mutation: the entire store is byte-for-byte unchanged.
    assert reg._redis.store == original
    assert reg._legacy_key(key) in reg._redis.store


@pytest.mark.parametrize("bad_key", ["", None, 12345, [], {}])
def test_b_invalid_key_migration_fails_closed(bad_key):
    legacy_key = "op-invalid-key-migration"
    store = _legacy_store_with(legacy_key, "EXECUTED", "gen-legacy", "b", "issue-1")
    reg = RedisIdempotencyRegistry(IdemFakeRedis(store))
    original = dict(reg._redis.store)

    result = run(migrate_legacy_record(reg, tenant_id="tenant-a", key=bad_key))
    assert result.status == MigrationStatus.INVALID_INPUT
    assert not result.ok
    assert reg._redis.store == original


# -- C: concurrent two-tenant migration of the SAME legacy record ---------- #

def test_c_concurrent_two_tenant_migration_at_most_one_wins():
    """Requirement: exactly one of two tenants racing to migrate the
    IDENTICAL legacy record may claim/move it -- never both, no duplicate
    scoped copies, no silent overwrite. The fake's ``eval`` never awaits
    mid-body, so this exercises the SAME single-writer-wins guarantee the
    real atomic Lua script provides against real Redis (also proven
    directly against a real Redis server -- see the non-vacuity script)."""
    key = "op-concurrent-migration-race"
    store = _legacy_store_with(key, "EXECUTED", "gen-legacy", "b", "issue-race")
    reg = RedisIdempotencyRegistry(IdemFakeRedis(store))

    async def race():
        return await asyncio.gather(
            migrate_legacy_record(reg, tenant_id="tenant-race-a", key=key),
            migrate_legacy_record(reg, tenant_id="tenant-race-b", key=key),
        )

    result_a, result_b = run(race())
    statuses = sorted([result_a.status.value, result_b.status.value])
    assert statuses == sorted([MigrationStatus.MIGRATED.value, MigrationStatus.CONFLICT.value]), (result_a, result_b)

    a_state = run(reg.get_state(key, tenant_id="tenant-race-a"))
    b_state = run(reg.get_state(key, tenant_id="tenant-race-b"))
    got_a, got_b = a_state is not None, b_state is not None
    assert got_a != got_b, "duplicate scoped copies created by a concurrent migration race"
    # The legacy record was consumed exactly once (default delete_legacy=True).
    assert reg._legacy_key(key) not in reg._redis.store


def test_c_concurrent_same_tenant_double_migration_is_idempotent_not_duplicated():
    """The SAME tenant racing against itself (e.g. a retried operator
    script) must also never produce two divergent outcomes -- one MIGRATED,
    the other ALREADY_MIGRATED (or both referring to the identical
    record), never an error or a duplicate."""
    key = "op-concurrent-same-tenant-migration"
    store = _legacy_store_with(key, "EXECUTED", "gen-legacy", "b", "issue-x")
    reg = RedisIdempotencyRegistry(IdemFakeRedis(store))

    async def race():
        return await asyncio.gather(
            migrate_legacy_record(reg, tenant_id="tenant-a", key=key),
            migrate_legacy_record(reg, tenant_id="tenant-a", key=key),
        )

    r1, r2 = run(race())
    assert {r1.status, r2.status} <= {MigrationStatus.MIGRATED, MigrationStatus.ALREADY_MIGRATED}
    assert MigrationStatus.MIGRATED in (r1.status, r2.status)
    assert r1.ok and r2.ok
    state = run(reg.get_state(key, tenant_id="tenant-a"))
    assert state.state == IdempotencyState.EXECUTED


# -- D: migration target already holds a DIFFERENT durable record ---------- #

def test_d_migration_never_overwrites_a_differing_target_record():
    key = "op-target-conflict"
    store = _legacy_store_with(key, "EXECUTED", "gen-legacy", "legacy-binding", "legacy-result")
    reg = RedisIdempotencyRegistry(IdemFakeRedis(store))
    # tenant-a already independently holds ITS OWN, unrelated scoped record
    # for this exact id (e.g. from a genuinely fresh reservation).
    reg._redis.store[reg._key("tenant-a", key)] = ("RESERVED|gen-independent|independent-binding|", None)

    result = run(migrate_legacy_record(reg, tenant_id="tenant-a", key=key))
    assert result.status == MigrationStatus.CONFLICT
    assert not result.ok

    # Neither record was touched.
    assert reg._redis.store[reg._legacy_key(key)][0] == "EXECUTED|gen-legacy|legacy-binding|legacy-result"
    assert reg._redis.store[reg._key("tenant-a", key)][0] == "RESERVED|gen-independent|independent-binding|"
    still = run(reg.get_state(key, tenant_id="tenant-a"))
    assert still.state == IdempotencyState.RESERVED  # tenant-a's own record, unchanged


def test_d_migration_treats_exact_duplicate_target_as_safe_idempotent_equivalence():
    """The one carve-out: if the target ALREADY holds the byte-for-byte
    identical encoded record (e.g. a previous migration attempt partially
    observed but the caller never got the response), that is safe to
    recognize as already-migrated -- never a CONFLICT, never a second
    distinct write."""
    key = "op-target-exact-duplicate"
    store = _legacy_store_with(key, "EXECUTED", "gen-legacy", "b", "res-1")
    reg = RedisIdempotencyRegistry(IdemFakeRedis(store))
    reg._redis.store[reg._key("tenant-a", key)] = ("EXECUTED|gen-legacy|b|res-1", None)  # byte-for-byte identical

    result = run(migrate_legacy_record(reg, tenant_id="tenant-a", key=key))
    assert result.status == MigrationStatus.ALREADY_MIGRATED
    assert result.ok
    assert reg._legacy_key(key) not in reg._redis.store  # safe to clean up on exact equivalence


# -- E: backend interruption/failure never splits legacy-deleted from scoped-written -- #

def test_e_backend_failure_leaves_no_split_state():
    """No state may exist where the legacy record disappeared but the
    scoped target was not durably written, or vice versa -- because the
    migration is a SINGLE atomic call, a backend failure means the whole
    operation is refused before any of it (from the caller's observable
    point of view) takes effect."""
    key = "op-backend-failure-migration"
    store = _legacy_store_with(key, "EXECUTED", "gen-legacy", "b", "res-1")
    reg = RedisIdempotencyRegistry(IdemFakeRedis(store))

    class _BoomOnEval(IdemFakeRedis):
        async def eval(self, *a, **k):
            raise ConnectionError("simulated redis outage mid-migration")

    boom_redis = _BoomOnEval(reg._redis.store)  # SAME underlying store
    boom_reg = RedisIdempotencyRegistry(boom_redis, namespace=reg._namespace)

    result = run(migrate_legacy_record(boom_reg, tenant_id="tenant-a", key=key))
    assert result.status == MigrationStatus.ERROR
    assert not result.ok

    # No split state: legacy still present, scoped target still absent.
    assert reg._legacy_key(key) in reg._redis.store
    assert reg._key("tenant-a", key) not in reg._redis.store
    # The retained legacy record correctly still fails closed as UNAVAILABLE
    # (never silently "not found") -- exactly the pre-migration behavior,
    # proving the failed migration attempt left the world unchanged.
    with pytest.raises(IdempotencyBackendUnavailable):
        run(reg.get_state(key, tenant_id="tenant-a"))
