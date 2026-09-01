"""A small async FakeRedis used by the multi-instance governance tests.

It models the subset of Redis commands the governance registries use, with TTL
honored against an injectable clock and an ``eval`` that faithfully runs the
velocity reserve script. A *shared* instance behind two registries models two
MCC runtime instances pointed at one Redis server.

This is test scaffolding only — never imported by runtime code.
"""

from __future__ import annotations

from typing import Any, Dict, Optional


class FakeRedis:
    def __init__(self, store: Optional[dict] = None, clock=None) -> None:
        # key -> (value, expires_at|None)
        self.kv: Dict[str, Any] = store if store is not None else {}
        self.sets: Dict[str, set] = {}
        self.ttls: Dict[str, int] = {}
        # key -> {member: score}, standing in for a Redis ZSET (velocity's
        # sliding-window reservation log).
        self.zsets: Dict[str, Dict[str, float]] = {}
        self.clock = clock or (lambda: 0.0)

    # --- expiry helpers ---
    def _expired(self, key: str) -> bool:
        cur = self.kv.get(key)
        return cur is not None and cur[1] is not None and cur[1] <= self.clock()

    def _evict(self, key: str) -> None:
        if self._expired(key):
            del self.kv[key]

    # --- string ops ---
    async def set(self, key, value, nx=False, ex=None, px=None):
        self._evict(key)
        if nx and key in self.kv:
            return None
        exp = None
        if ex is not None:
            exp = self.clock() + ex
        elif px is not None:
            exp = self.clock() + px / 1000.0
        self.kv[key] = (value, exp)
        return True

    async def get(self, key):
        self._evict(key)
        cur = self.kv.get(key)
        return None if cur is None else cur[0]

    async def delete(self, *keys):
        n = 0
        for k in keys:
            if k in self.kv:
                del self.kv[k]
                n += 1
            self.sets.pop(k, None)
        return n

    async def incr(self, key):
        self._evict(key)
        val = int(self.kv.get(key, (0, None))[0]) + 1
        _, exp = self.kv.get(key, (0, None))
        self.kv[key] = (val, exp)
        return val

    async def decr(self, key):
        self._evict(key)
        val = int(self.kv.get(key, (0, None))[0]) - 1
        _, exp = self.kv.get(key, (0, None))
        self.kv[key] = (val, exp)
        return val

    async def incrbyfloat(self, key, amt):
        self._evict(key)
        val = float(self.kv.get(key, (0.0, None))[0]) + float(amt)
        _, exp = self.kv.get(key, (0.0, None))
        self.kv[key] = (val, exp)
        return val

    async def expire(self, key, ttl):
        self.ttls[key] = ttl
        if key in self.kv:
            v, _ = self.kv[key]
            self.kv[key] = (v, self.clock() + ttl)
        return True

    async def ttl(self, key):
        return self.ttls.get(key, -1)

    # --- set ops ---
    async def sadd(self, key, *members):
        s = self.sets.setdefault(key, set())
        added = 0
        for m in members:
            if m not in s:
                s.add(m)
                added += 1
        return added

    async def srem(self, key, *members):
        s = self.sets.get(key, set())
        n = 0
        for m in members:
            if m in s:
                s.discard(m)
                n += 1
        return n

    async def scard(self, key):
        return len(self.sets.get(key, set()))

    async def sismember(self, key, member):
        return member in self.sets.get(key, set())

    # --- scripting (velocity sliding-window reserve / release) ---
    async def eval(self, script, numkeys, *args):
        """Faithful Python equivalent of ``velocity._RESERVE_LUA`` /
        ``velocity._RELEASE_LUA`` (atomic by virtue of running without
        awaiting), backed by ``self.zsets`` standing in for a Redis ZSET."""
        from mcc_core.velocity import _RELEASE_LUA

        keys = list(args[:numkeys])
        a = list(args[numkeys:])
        (key,) = keys
        z = self.zsets.setdefault(key, {})

        if script == _RELEASE_LUA:
            now = float(a[0])
            target_amount, target_dest = a[1], a[2]
            for member, score in z.items():
                if score != now:
                    continue
                _id, amt_str, dest_str = member.split(":", 2)
                if amt_str == target_amount and dest_str == target_dest:
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
        dests: Dict[str, bool] = {}
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
    """Every command raises — models a Redis outage (fail-closed expectation)."""

    def __getattr__(self, _name):
        async def boom(*a, **k):
            raise ConnectionError("redis down")

        return boom
