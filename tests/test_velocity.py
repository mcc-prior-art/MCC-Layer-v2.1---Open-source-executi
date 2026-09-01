"""Velocity / aggregate control tests.

Covers cumulative ceilings across separately-signed transactions (anti-
splitting), per-window count and new-destination caps, configurable outcomes,
the concurrency safety property (total reserved never exceeds the ceiling), and
fail-closed on registry outage.
"""

import asyncio

import pytest

from mcc_core import (
    InMemoryVelocityRegistry,
    RedisVelocityRegistry,
    VelocityDescriptor,
    VelocityLimit,
    Verdict,
)
from mcc_core.velocity import _RELEASE_LUA

run = asyncio.run


class VelFakeRedis:
    """Faithful Python equivalent of velocity._RESERVE_LUA / _RELEASE_LUA
    (atomic by virtue of running without awaiting). Lets the unit tests
    exercise the same atomic sliding-window-log reserve semantics the real
    Redis runs as a Lua script, backed here by a plain dict of
    ``key -> {member: score}`` standing in for a Redis ZSET."""

    def __init__(self):
        self.zsets: dict = {}

    async def eval(self, script, numkeys, *args):
        keys = list(args[:numkeys])
        a = list(args[numkeys:])
        (key,) = keys
        z = self.zsets.setdefault(key, {})

        if script == _RELEASE_LUA:
            now = float(a[0])
            for member, score in z.items():
                if score == now:
                    del z[member]
                    return 1
            return 0

        now = float(a[0])
        window = int(a[1])
        cutoff = now - window
        # Matches ZREMRANGEBYSCORE(key, '-inf', '(' .. cutoff): removes only
        # scores STRICTLY less than cutoff; a score exactly == cutoff survives
        # (an event exactly window_seconds old still counts).
        for member in [m for m, s in z.items() if s < cutoff]:
            del z[member]

        count = len(z)
        total_amount = 0.0
        dests: dict = {}
        for member in z:
            _id, amt_str, dest_str = member.split(":", 2)
            if amt_str:
                total_amount += float(amt_str)
            if dest_str:
                dests[dest_str] = True

        breaches = []
        prospective_count = count + 1
        if a[2] == "1" and float(a[3]) >= 0 and prospective_count > float(a[3]):
            breaches.append(f"count {prospective_count} > max {a[3]}")

        use_amount = a[4] == "1"
        prospective_amount = total_amount
        if use_amount:
            prospective_amount = total_amount + float(a[5])
            if float(a[6]) >= 0 and prospective_amount > float(a[6]):
                breaches.append(f"amount {prospective_amount} > max {a[6]}")

        dest_val = a[8]
        new_dest = bool(dest_val) and dest_val not in dests
        prospective_dests = len(dests) + (1 if new_dest else 0)
        if a[7] == "1" and new_dest and float(a[9]) >= 0 and prospective_dests > float(a[9]):
            breaches.append(f"new destinations {prospective_dests} > max {a[9]}")

        if breaches:
            return [0, "; ".join(breaches)]

        amount_repr = a[5] if use_amount else ""
        member = f"{a[10]}:{amount_repr}:{dest_val}"
        z[member] = now
        return [1, "ok"]


class DownRedis:
    def __getattr__(self, _name):
        async def boom(*a, **k):
            raise ConnectionError("down")

        return boom


def both():
    return [InMemoryVelocityRegistry(), RedisVelocityRegistry(VelFakeRedis())]


def desc(actor="a1", source="s1", amount=None, destination=None, action="send_payment"):
    return VelocityDescriptor(
        dimensions={"actor": actor, "source": source, "action": action, "policy_scope": "p"},
        amount=amount,
        destination=destination,
    )


# ---- Cumulative amount ceiling / anti-splitting ----

@pytest.mark.parametrize("reg", both())
def test_four_transactions_cannot_bypass_cumulative_ceiling(reg):
    # Each 3000 is individually fine; together they must not exceed 10000.
    limit = VelocityLimit(name="amt", window_seconds=3600, max_amount=10000,
                          aggregate_by=("actor",))
    outcomes = [run(reg.reserve(limit, desc(amount=3000), now=1000.0)) for _ in range(4)]
    verdicts = [o.verdict for o in outcomes]
    assert verdicts[:3] == [Verdict.ALLOW, Verdict.ALLOW, Verdict.ALLOW]
    assert verdicts[3] == Verdict.DENY  # 12000 > 10000


@pytest.mark.parametrize("reg", both())
def test_cumulative_limit_spans_distinct_destinations(reg):
    # Splitting one large payment into several to different beneficiaries still
    # aggregates by actor against the amount ceiling.
    limit = VelocityLimit(name="amt", window_seconds=3600, max_amount=5000,
                          aggregate_by=("actor",))
    a = run(reg.reserve(limit, desc(amount=3000, destination="b1"), now=1000.0))
    b = run(reg.reserve(limit, desc(amount=3000, destination="b2"), now=1000.0))
    assert a.verdict == Verdict.ALLOW
    assert b.verdict == Verdict.DENY  # 6000 > 5000 even to a different beneficiary


# ---- Count + new-destination caps ----

@pytest.mark.parametrize("reg", both())
def test_max_count_per_window(reg):
    limit = VelocityLimit(name="cnt", window_seconds=3600, max_count=2)
    v = [run(reg.reserve(limit, desc(), now=1000.0)).verdict for _ in range(3)]
    assert v == [Verdict.ALLOW, Verdict.ALLOW, Verdict.DENY]


@pytest.mark.parametrize("reg", both())
def test_max_new_destinations_per_window(reg):
    limit = VelocityLimit(name="dst", window_seconds=3600, max_new_destinations=2)
    assert run(reg.reserve(limit, desc(destination="b1"), now=1000.0)).verdict == Verdict.ALLOW
    assert run(reg.reserve(limit, desc(destination="b2"), now=1000.0)).verdict == Verdict.ALLOW
    assert run(reg.reserve(limit, desc(destination="b3"), now=1000.0)).verdict == Verdict.DENY
    # A repeat of an already-seen destination is not a new one.
    assert run(reg.reserve(limit, desc(destination="b1"), now=1000.0)).verdict == Verdict.ALLOW


# ---- Aggregation scoping ----

@pytest.mark.parametrize("reg", both())
def test_different_actors_have_independent_budgets(reg):
    limit = VelocityLimit(name="amt", window_seconds=3600, max_amount=5000,
                          aggregate_by=("actor",))
    assert run(reg.reserve(limit, desc(actor="a1", amount=5000), now=1000.0)).verdict == Verdict.ALLOW
    assert run(reg.reserve(limit, desc(actor="a2", amount=5000), now=1000.0)).verdict == Verdict.ALLOW


@pytest.mark.parametrize("reg", both())
def test_window_resets_in_next_bucket(reg):
    limit = VelocityLimit(name="amt", window_seconds=100, max_amount=5000,
                          aggregate_by=("actor",))
    assert run(reg.reserve(limit, desc(amount=5000), now=1000.0)).verdict == Verdict.ALLOW
    assert run(reg.reserve(limit, desc(amount=5000), now=1000.0)).verdict == Verdict.DENY
    # The gap here (200s) is more than double window_seconds (100s), so budget
    # correctly refreshes under BOTH a fixed/tumbling window AND a sliding
    # window -- this test does not by itself distinguish the two designs
    # (see the boundary-straddle regressions below for that).
    assert run(reg.reserve(limit, desc(amount=5000), now=1200.0)).verdict == Verdict.ALLOW


# ---- Sliding-window boundary regressions -----------------------------------
#
# Regression coverage for the confirmed pre-existing defect: a fixed/tumbling
# window keyed by ``now // window_seconds`` resets the aggregate at a
# calendar-aligned boundary regardless of how recently prior reservations
# were made. Two individually-valid reservations placed a few seconds either
# side of such a boundary would each see an (incorrectly) empty aggregate and
# together exceed the ceiling by up to 2x -- a payment that should have been
# DENIED could reach the upstream side effect.
#
# Every test below is fully deterministic: all times are explicit ``now=``
# floats passed to ``reserve``/``release``. No ``time.sleep``, no dependence
# on real wall-clock timing, and no probabilistic/stress component -- this is
# the authoritative proof, not scripts/smoke_stress.sh (which is secondary,
# best-effort validation only).

def test_old_fixed_window_arithmetic_would_have_misclassified_this_scenario():
    """Documents, independently of any registry, exactly why the pre-existing
    ``now // window_seconds`` bucket formula is wrong for this scenario --
    without resurrecting the old (removed) buggy code path. Three $4000
    reservations, 60s window: A and B a fraction of a second apart, C exactly
    at the next calendar-aligned 60s tick. Under the OLD formula, A/B fall in
    one bucket and C falls in the very next bucket, so a fixed-window
    registry would see C's aggregate as freshly empty (ALLOW) instead of
    correctly seeing 12000 > 10000 (DENY)."""
    window_seconds = 60
    t_a, t_b, t_c = 3599.0, 3599.5, 3600.5  # A, B before the :00 tick; C just after

    def old_bucket(now: float) -> int:
        return int(now // window_seconds)

    assert old_bucket(t_a) == old_bucket(t_b), "A and B must share the old fixed bucket"
    assert old_bucket(t_c) != old_bucket(t_a), (
        "C must land in a DIFFERENT old fixed bucket than A/B -- this is "
        "exactly the boundary condition that let C bypass the ceiling"
    )
    # Real elapsed time between the first and last reservation is well under
    # the configured window -- these are not legitimately 60+ seconds apart.
    assert (t_c - t_a) < window_seconds


@pytest.mark.parametrize("reg", both())
def test_boundary_bypass_regression_three_payments_straddling_a_tick(reg):
    """THE regression for the confirmed defect (CI report: 'op-3 $4000
    (cumulative 12000 > 10000): expected block, got HTTP 200' /
    'expected exactly 2 executed payments at upstream, saw 3').

    window=60s, cumulative limit=$10,000, three $4000 reservations placed
    exactly as in test_old_fixed_window_arithmetic_would_have_misclassified_
    this_scenario above (A/B before a would-be 60s tick, C just after it).
    A correct sliding window holds the ceiling regardless of that boundary:
    ALLOW, ALLOW, DENY. The old fixed-window implementation this replaces
    would have produced ALLOW, ALLOW, ALLOW (see the sibling test above for
    the arithmetic proof of why) -- i.e. a third payment reaching the
    upstream side effect while the cumulative ceiling was actually exceeded.
    """
    limit = VelocityLimit(name="amt", window_seconds=60, max_amount=10000,
                          aggregate_by=("actor",))
    a = run(reg.reserve(limit, desc(amount=4000), now=3599.0))
    b = run(reg.reserve(limit, desc(amount=4000), now=3599.5))
    c = run(reg.reserve(limit, desc(amount=4000), now=3600.5))
    assert [x.verdict for x in (a, b, c)] == [Verdict.ALLOW, Verdict.ALLOW, Verdict.DENY]
    assert a.reserved and b.reserved and not c.reserved
    assert "12000" in c.reason and "10000" in c.reason


@pytest.mark.parametrize("reg", both())
def test_boundary_bypass_regression_holds_across_many_ticks(reg):
    """The same regression, repeated across several different calendar-tick
    boundaries (not just one), so the fix isn't verified against a single
    coincidentally-safe pair of timestamps."""
    limit = VelocityLimit(name="amt", window_seconds=60, max_amount=10000,
                          aggregate_by=("actor",))
    for tick in (60, 120, 180, 3600, 86400):  # distinct 60s-aligned boundaries
        reg_fresh = InMemoryVelocityRegistry() if isinstance(reg, InMemoryVelocityRegistry) \
            else RedisVelocityRegistry(VelFakeRedis())
        a = run(reg_fresh.reserve(limit, desc(amount=4000), now=float(tick) - 1.0))
        b = run(reg_fresh.reserve(limit, desc(amount=4000), now=float(tick) - 0.5))
        c = run(reg_fresh.reserve(limit, desc(amount=4000), now=float(tick) + 0.5))
        assert [x.verdict for x in (a, b, c)] == [Verdict.ALLOW, Verdict.ALLOW, Verdict.DENY], (
            f"boundary bypass regressed at tick={tick}"
        )


@pytest.mark.parametrize("reg", both())
def test_event_just_before_expiry_still_counts(reg):
    limit = VelocityLimit(name="amt", window_seconds=60, max_amount=7999,
                          aggregate_by=("actor",))
    assert run(reg.reserve(limit, desc(amount=4000), now=1000.0)).verdict == Verdict.ALLOW
    # 59.999s later: the first event is still (barely) inside the window.
    out = run(reg.reserve(limit, desc(amount=4000), now=1059.999))
    assert out.verdict == Verdict.DENY  # 8000 > 7999 -- first event still counted


@pytest.mark.parametrize("reg", both())
def test_event_exactly_at_window_edge_still_counts(reg):
    """The trailing edge is inclusive: an event exactly ``window_seconds``
    old still counts (the more conservative reading for a governance
    ceiling -- only STRICTLY older events expire). InMemory and Redis must
    agree here exactly, not just approximately."""
    limit = VelocityLimit(name="amt", window_seconds=60, max_amount=7999,
                          aggregate_by=("actor",))
    assert run(reg.reserve(limit, desc(amount=4000), now=1000.0)).verdict == Verdict.ALLOW
    out = run(reg.reserve(limit, desc(amount=4000), now=1060.0))  # exactly 60s later
    assert out.verdict == Verdict.DENY  # 8000 > 7999 -- boundary event still counted


@pytest.mark.parametrize("reg", both())
def test_event_just_after_expiry_no_longer_counts(reg):
    limit = VelocityLimit(name="amt", window_seconds=60, max_amount=7999,
                          aggregate_by=("actor",))
    assert run(reg.reserve(limit, desc(amount=4000), now=1000.0)).verdict == Verdict.ALLOW
    # 60.001s later: the first event has just aged out of the window.
    out = run(reg.reserve(limit, desc(amount=4000), now=1060.001))
    assert out.verdict == Verdict.ALLOW  # only this event counts now: 4000 <= 7999


@pytest.mark.parametrize("reg", both())
def test_stale_entries_do_not_affect_a_much_later_decision(reg):
    """No residual state from long-expired reservations leaks into a later
    decision -- including the "new destination" dimension, not just amount."""
    limit = VelocityLimit(name="dst", window_seconds=60, max_new_destinations=1)
    assert run(reg.reserve(limit, desc(destination="b1"), now=1000.0)).verdict == Verdict.ALLOW
    # Long after the window has elapsed, "b1" must be treated as new again --
    # not still remembered from the expired reservation.
    out = run(reg.reserve(limit, desc(destination="b1"), now=100_000.0))
    assert out.verdict == Verdict.ALLOW


@pytest.mark.parametrize("reg", both())
def test_multiple_reservations_within_rolling_interval_aggregate_correctly(reg):
    """Several reservations at distinct timestamps, all genuinely within one
    trailing window, must sum correctly (not just two at an identical
    instant, as most other tests use for simplicity)."""
    limit = VelocityLimit(name="amt", window_seconds=60, max_amount=10000,
                          aggregate_by=("actor",))
    verdicts = [
        run(reg.reserve(limit, desc(amount=2000), now=1000.0 + offset)).verdict
        for offset in (0.0, 10.0, 20.0, 30.0, 40.0)
    ]
    # 2000 x 5 = 10000, exactly at the ceiling -- all five ALLOW.
    assert verdicts == [Verdict.ALLOW] * 5
    # A sixth, still within the same rolling window, must breach.
    sixth = run(reg.reserve(limit, desc(amount=2000), now=1050.0))
    assert sixth.verdict == Verdict.DENY


@pytest.mark.parametrize("reg", both())
def test_cumulative_count_limit_slides_across_a_boundary_too(reg):
    """The count dimension (not just amount) must also use sliding, not
    fixed-window, semantics."""
    limit = VelocityLimit(name="cnt", window_seconds=60, max_count=2)
    a = run(reg.reserve(limit, desc(), now=3599.0))
    b = run(reg.reserve(limit, desc(), now=3599.5))
    c = run(reg.reserve(limit, desc(), now=3600.5))  # just past a would-be tick
    assert [x.verdict for x in (a, b, c)] == [Verdict.ALLOW, Verdict.ALLOW, Verdict.DENY]


@pytest.mark.parametrize("reg", both())
def test_release_after_sliding_expiry_is_a_safe_tolerant_noop(reg):
    """Reservation/commit/release lifecycle: releasing a reservation whose
    window has since fully elapsed must not raise, resurrect stale state, or
    corrupt a later, unrelated reservation."""
    limit = VelocityLimit(name="amt", window_seconds=60, max_amount=10000,
                          aggregate_by=("actor",))
    out = run(reg.reserve(limit, desc(amount=1000), now=1000.0))
    assert out.ok
    # Released long after the window elapsed (mirrors the coordinator rolling
    # back an earlier-reserved dimension after a much-later, unrelated call --
    # tolerant no-op is the required behavior, not an exception).
    released = run(reg.release(limit, desc(amount=1000), now=1000.0))
    assert released is True
    # A fresh reservation afterward is unaffected.
    fresh = run(reg.reserve(limit, desc(amount=9000), now=200_000.0))
    assert fresh.verdict == Verdict.ALLOW


# ---- Configurable outcome ----

@pytest.mark.parametrize("reg", both())
def test_on_exceed_outcome_is_configurable(reg):
    limit = VelocityLimit(name="amt", window_seconds=3600, max_amount=1000,
                          on_exceed=Verdict.ESCALATE)
    assert run(reg.reserve(limit, desc(amount=500), now=1000.0)).verdict == Verdict.ALLOW
    over = run(reg.reserve(limit, desc(amount=5000), now=1000.0))
    assert over.verdict == Verdict.ESCALATE
    assert not over.reserved


# ---- Concurrency safety: never over-allow ----

@pytest.mark.parametrize("reg", both())
def test_concurrent_aggregate_race_never_exceeds_ceiling(reg):
    limit = VelocityLimit(name="amt", window_seconds=3600, max_amount=10000,
                          aggregate_by=("actor",))

    async def race():
        return await asyncio.gather(
            *[reg.reserve(limit, desc(amount=3000), now=1000.0) for _ in range(20)]
        )

    outcomes = run(race())
    winners = [o for o in outcomes if o.verdict == Verdict.ALLOW]
    # The safety property: the total reserved never exceeds the ceiling.
    assert len(winners) * 3000 <= 10000
    assert len(winners) >= 1


# ---- Fail-closed ----

def test_velocity_registry_outage_fails_closed():
    reg = RedisVelocityRegistry(DownRedis())
    limit = VelocityLimit(name="amt", window_seconds=3600, max_amount=10000)
    out = run(reg.reserve(limit, desc(amount=100), now=1000.0))
    assert out.verdict == Verdict.DENY
    assert not out.reserved


# ---- Input validation hardening (malformed / hostile amounts fail closed) ----

@pytest.mark.parametrize("reg", [InMemoryVelocityRegistry(), RedisVelocityRegistry(VelFakeRedis())])
def test_negative_amount_fails_closed(reg):
    limit = VelocityLimit(name="amt", window_seconds=3600, max_amount=1000.0)
    desc = VelocityDescriptor(dimensions={"actor": "a"}, amount=-500.0)
    out = run(reg.reserve(limit, desc))
    assert out.verdict == Verdict.DENY and not out.reserved


@pytest.mark.parametrize("reg", [InMemoryVelocityRegistry(), RedisVelocityRegistry(VelFakeRedis())])
def test_nan_amount_fails_closed(reg):
    limit = VelocityLimit(name="amt", window_seconds=3600, max_amount=1000.0)
    out = run(reg.reserve(limit, VelocityDescriptor(dimensions={"actor": "a"}, amount=float("nan"))))
    assert out.verdict == Verdict.DENY and not out.reserved


@pytest.mark.parametrize("reg", [InMemoryVelocityRegistry(), RedisVelocityRegistry(VelFakeRedis())])
def test_inf_amount_fails_closed(reg):
    limit = VelocityLimit(name="amt", window_seconds=3600, max_amount=1000.0)
    out = run(reg.reserve(limit, VelocityDescriptor(dimensions={"actor": "a"}, amount=float("inf"))))
    assert out.verdict == Verdict.DENY and not out.reserved


def test_negative_amount_cannot_reduce_aggregate():
    # A hostile negative amount must not decrement a shared counter to make room.
    shared = VelFakeRedis()
    reg = RedisVelocityRegistry(shared)
    limit = VelocityLimit(name="amt", window_seconds=3600, max_amount=100.0)
    desc_ok = VelocityDescriptor(dimensions={"actor": "a"}, amount=90.0)
    desc_bad = VelocityDescriptor(dimensions={"actor": "a"}, amount=-50.0)
    assert run(reg.reserve(limit, desc_ok)).ok            # sum=90
    assert not run(reg.reserve(limit, desc_bad)).ok        # rejected, sum unchanged
    # A legitimate 20 would still cross 100 (proves the -50 did not apply).
    assert not run(reg.reserve(limit, VelocityDescriptor(dimensions={"actor": "a"}, amount=20.0))).ok
