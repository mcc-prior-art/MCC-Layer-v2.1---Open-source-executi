"""Durable logical-operation idempotency.

Distinct from nonce replay protection. The nonce makes a *single decision
token* one-time; this registry makes a *logical operation* — identified by an
opaque key the coordinator binds to the exact (action, resource, canonical
payload_hash) triple — safe against duplicate external side effects, even
across different, separately-signed, separately-nonced tokens that share that
key. See ``docs/DURABLE_OPERATION_SAFETY.md``.

State machine
-------------

    (absent)
        --reserve------------------> RESERVED           (pre-dispatch; TTL-bound)
    RESERVED
        --commit_dispatch----------> DISPATCH_OWNED      (durable; no TTL-based recovery)
        --release-------------------> (absent)           (only pre-dispatch; retry-eligible)
    DISPATCH_OWNED
        --mark_executed-------------> EXECUTED           (terminal; confirmed)
        --mark_unknown---------------> UNKNOWN            (durable; unresolved)
    UNKNOWN
        --resolve_unknown (positive external evidence)--> EXECUTED

EXECUTED and, short of independently verified positive evidence, UNKNOWN are
both terminal for the purpose of admitting a *new* dispatch attempt: neither
can be reserved again, and neither expires back into an admittable state
merely because time has passed (TTL is used ONLY for the pre-dispatch
``RESERVED`` state, to recover a reservation whose holder crashed before any
external call could possibly have been attempted — never for a state reached
after the durable dispatch boundary). Any TTL later applied to a terminal
record (``mark_executed`` accepts an optional ``ttl_seconds``) is a
retention/storage-GC decision an operator opts into explicitly — it is
never wired into ``reserve``'s admission logic, and by default no such TTL
is applied at all (the record persists). ``mark_unknown`` carries no such
knob at all: an unresolved operation is never eligible for GC-driven
expiry — only ``resolve_unknown`` (independently verified positive
evidence) may retire it.

Every state-mutating call after ``reserve`` is fenced by the opaque
``fence`` (generation) token ``reserve`` returns: a mutation only applies if
the record's current generation still matches the fence the caller was
issued. A stale caller — a crashed-then-recovered process replaying an old
attempt, or a second concurrent racer — can therefore never regress a newer
generation's state, mark someone else's operation executed, release it, or
overwrite its binding. Reconciliation (``resolve_unknown``) is fenced the
same way, using the generation observed via ``get_state``, so it composes
safely with a late-arriving legitimate completion of the very same
generation (exactly one of the two racing writers wins; neither invokes any
actuator).

Fail-closed: a registry that cannot give a definite answer denies the
reservation (``ReserveStatus.ERROR``), and ``get_state`` raises
:class:`IdempotencyBackendUnavailable` rather than returning ``None`` —
backend outage must never be interpreted as "operation not found" / "not
executed" / "safe to retry". ``idempotency_registry_from_env`` refuses to
silently fall back from Redis to in-memory in an enforcement deployment.
"""

from __future__ import annotations

import asyncio
import os
import time
import uuid
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Mapping, Optional, Tuple

DEFAULT_RESERVATION_TTL_SECONDS = 120
DEFAULT_OP_TIMEOUT_SECONDS = 0.5


class IdempotencyState(str, Enum):
    RESERVED = "RESERVED"              # admitted, pre-dispatch; TTL-bound crash recovery
    DISPATCH_OWNED = "DISPATCH_OWNED"  # durable dispatch commitment made; no TTL recovery
    UNKNOWN = "UNKNOWN"                # actuation outcome indeterminate; no TTL recovery
    EXECUTED = "EXECUTED"              # terminal; confirmed


class ReserveStatus(str, Enum):
    RESERVED = "RESERVED"                    # this caller won the reservation; proceed
    DUPLICATE_INFLIGHT = "DUPLICATE_INFLIGHT"  # RESERVED or DISPATCH_OWNED held by another
    DUPLICATE_UNKNOWN = "DUPLICATE_UNKNOWN"    # existing op UNKNOWN; needs reconciliation, not retry
    DUPLICATE_EXECUTED = "DUPLICATE_EXECUTED"  # operation already completed
    BINDING_CONFLICT = "BINDING_CONFLICT"      # same key, different action/resource/payload
    ERROR = "ERROR"                            # indeterminate -> fail closed


@dataclass(frozen=True)
class ReserveResult:
    status: ReserveStatus
    reason: str
    binding: Optional[str] = None  # binding recorded by the holder, if known
    fence: Optional[str] = None    # generation fence; set only when status == RESERVED

    @property
    def ok(self) -> bool:
        """May this caller proceed toward dispatch?"""
        return self.status == ReserveStatus.RESERVED


class ReconcileStatus(str, Enum):
    RESOLVED = "RESOLVED"                  # UNKNOWN/DISPATCH_OWNED -> EXECUTED applied
    ALREADY_EXECUTED = "ALREADY_EXECUTED"  # a racing writer (or earlier run) already resolved it
    NOT_PENDING = "NOT_PENDING"            # current state isn't UNKNOWN or DISPATCH_OWNED (e.g. still RESERVED)
    STALE_GENERATION = "STALE_GENERATION"  # the observed generation no longer holds the record
    NOT_FOUND = "NOT_FOUND"                # no record at all for this key
    ERROR = "ERROR"                        # indeterminate -> fail closed, no state change


@dataclass(frozen=True)
class ReconcileResult:
    status: ReconcileStatus
    reason: str

    @property
    def resolved(self) -> bool:
        return self.status == ReconcileStatus.RESOLVED


@dataclass(frozen=True)
class StateRecord:
    """A durable-state snapshot. ``get_state`` never mutates anything."""

    state: IdempotencyState
    generation: str
    binding: str
    result_ref: Optional[str] = None


class IdempotencyBackendUnavailable(Exception):
    """Raised by ``get_state`` when the backend cannot answer. Callers MUST
    NOT treat this as "not found" / "not executed" / "safe to retry" — it is
    a distinct, explicit UNAVAILABLE/INDETERMINATE signal."""


def _encode(state: IdempotencyState, generation: str, binding: str, result_ref: str = "") -> str:
    return f"{state.value}|{generation}|{binding}|{result_ref}"


def _decode(raw: str) -> Tuple[Optional[IdempotencyState], str, str, Optional[str]]:
    parts = raw.split("|", 3)
    if len(parts) != 4:
        return None, "", "", None
    head, generation, binding, result_ref = parts
    try:
        state = IdempotencyState(head)
    except ValueError:
        return None, generation, binding, (result_ref or None)
    return state, generation, binding, (result_ref or None)


class InMemoryIdempotencyRegistry:
    """Single-process idempotency (dev / tests). Atomic by virtue of running
    its whole critical section without awaiting.

    NOT durable: this dict lives in one process's memory. A restart, or a
    second process, sees no record at all — it does not, and must not,
    stand in for a shared/durable backend in an enforcement deployment (see
    ``deployment_mode.is_enforcement_mode``, which refuses in-memory
    registries there). Its purpose here is local development and the
    single-process test suite.
    """

    def __init__(self) -> None:
        self._store: Dict[str, Tuple[str, Optional[float]]] = {}  # key -> (encoded, expires_at|None)

    def _live(self, key: str, now: float) -> Optional[str]:
        entry = self._store.get(key)
        if entry is None:
            return None
        encoded, expires_at = entry
        if expires_at is not None and expires_at <= now:
            self._store.pop(key, None)
            return None
        return encoded

    async def reserve(
        self,
        key: str,
        *,
        binding: str = "",
        ttl_seconds: int = DEFAULT_RESERVATION_TTL_SECONDS,
    ) -> ReserveResult:
        if not key or not isinstance(key, str):
            return ReserveResult(ReserveStatus.ERROR, "invalid idempotency key")
        now = time.monotonic()
        encoded = self._live(key, now)
        if encoded is None:
            generation = uuid.uuid4().hex
            self._store[key] = (_encode(IdempotencyState.RESERVED, generation, binding), now + ttl_seconds)
            return ReserveResult(ReserveStatus.RESERVED, "reserved", binding, fence=generation)
        state, generation, held_binding, _ = _decode(encoded)
        if held_binding != binding:
            return ReserveResult(ReserveStatus.BINDING_CONFLICT, "logical operation bound to a different "
                                  "action/resource/payload", held_binding)
        if state == IdempotencyState.EXECUTED:
            return ReserveResult(ReserveStatus.DUPLICATE_EXECUTED, "operation already executed", held_binding)
        if state == IdempotencyState.UNKNOWN:
            return ReserveResult(ReserveStatus.DUPLICATE_UNKNOWN,
                                  "operation outcome UNKNOWN; requires reconciliation, not retry", held_binding)
        return ReserveResult(ReserveStatus.DUPLICATE_INFLIGHT, "operation already reserved", held_binding)

    async def commit_dispatch(self, key: str, *, fence: str) -> bool:
        now = time.monotonic()
        encoded = self._live(key, now)
        if encoded is None:
            return False
        state, generation, binding, _ = _decode(encoded)
        if state != IdempotencyState.RESERVED or generation != fence:
            return False
        self._store[key] = (_encode(IdempotencyState.DISPATCH_OWNED, generation, binding), None)
        return True

    async def mark_executed(
        self, key: str, *, fence: str, binding: str = "", result_ref: Optional[str] = None,
    ) -> bool:
        """Terminal, unconditional, permanent: EXECUTED is never written
        with an expiry (Round 18 — a terminal record must never silently
        reopen through TTL semantics; retention/archival, if ever needed,
        must be a separate, explicit, out-of-band operation, never a
        parameter of this call)."""
        now = time.monotonic()
        encoded = self._live(key, now)
        if encoded is None:
            return False
        state, generation, held_binding, _ = _decode(encoded)
        if state != IdempotencyState.DISPATCH_OWNED or generation != fence:
            return False
        self._store[key] = (
            _encode(IdempotencyState.EXECUTED, generation, held_binding, result_ref or ""), None,
        )
        return True

    async def mark_unknown(self, key: str, *, fence: str) -> bool:
        now = time.monotonic()
        encoded = self._live(key, now)
        if encoded is None:
            return False
        state, generation, binding, _ = _decode(encoded)
        if state != IdempotencyState.DISPATCH_OWNED or generation != fence:
            return False
        self._store[key] = (_encode(IdempotencyState.UNKNOWN, generation, binding), None)
        return True

    async def release(self, key: str, *, fence: str) -> bool:
        """Free the key for a legitimate retry. Only valid pre-dispatch
        (state RESERVED): once dispatch ownership has been committed, the
        operation can never be released back to an admittable state — see
        ``mark_unknown``."""
        now = time.monotonic()
        encoded = self._live(key, now)
        if encoded is None:
            return True  # already gone
        state, generation, _binding, _ = _decode(encoded)
        if state != IdempotencyState.RESERVED or generation != fence:
            return False
        self._store.pop(key, None)
        return True

    async def resolve_unknown(
        self, key: str, *, expected_generation: str, result_ref: Optional[str] = None,
    ) -> ReconcileResult:
        """Fenced CAS: ``UNKNOWN`` OR ``DISPATCH_OWNED`` -> ``EXECUTED``,
        given independently verified positive external evidence (the
        CALLER, e.g. ``reconciliation.py``, is responsible for that
        verification -- this only performs the state transition). Accepting
        ``DISPATCH_OWNED`` as a source state too (Round 18) closes the gap
        where a crash after durable dispatch commitment but before
        ``mark_unknown``/``mark_executed`` ever ran would otherwise strand
        the operation with no reconciliation path at all: both states mean
        exactly the same thing to a reconciliation worker -- "the actuation
        outcome for this generation is not yet durably confirmed" -- and
        differ only in what the ORIGINAL dispatcher itself managed to
        persist before disappearing. Absence of positive evidence never
        reaches this far (the caller simply does not call this); this
        method itself has no "not found -> proceed anyway" branch."""
        now = time.monotonic()
        encoded = self._live(key, now)
        if encoded is None:
            return ReconcileResult(ReconcileStatus.NOT_FOUND, "no record for this key")
        state, generation, binding, _ = _decode(encoded)
        if generation != expected_generation:
            return ReconcileResult(ReconcileStatus.STALE_GENERATION,
                                    "observed generation no longer holds this record")
        if state == IdempotencyState.EXECUTED:
            return ReconcileResult(ReconcileStatus.ALREADY_EXECUTED, "already resolved (racing writer won)")
        if state not in (IdempotencyState.UNKNOWN, IdempotencyState.DISPATCH_OWNED):
            return ReconcileResult(ReconcileStatus.NOT_PENDING, f"current state is {state.value if state else '?'}")
        self._store[key] = (_encode(IdempotencyState.EXECUTED, generation, binding, result_ref or ""), None)
        return ReconcileResult(ReconcileStatus.RESOLVED, "positive external evidence confirmed execution")

    async def get_state(self, key: str) -> Optional[StateRecord]:
        encoded = self._live(key, time.monotonic())
        if encoded is None:
            return None
        state, generation, binding, result_ref = _decode(encoded)
        if state is None:
            return None
        return StateRecord(state=state, generation=generation, binding=binding, result_ref=result_ref)


_RESERVE_LUA = """
local cur = redis.call('GET', KEYS[1])
if not cur then
    local gen = ARGV[3]
    local val = 'RESERVED|' .. gen .. '|' .. ARGV[1] .. '|'
    redis.call('SET', KEYS[1], val, 'EX', ARGV[2])
    return {'RESERVED', gen}
end
local state, gen, binding = cur:match('^([^|]*)|([^|]*)|([^|]*)|')
if binding ~= ARGV[1] then
    return {'BINDING_CONFLICT', gen, binding}
end
if state == 'EXECUTED' then
    return {'DUPLICATE_EXECUTED', gen}
end
if state == 'UNKNOWN' then
    return {'DUPLICATE_UNKNOWN', gen}
end
return {'DUPLICATE_INFLIGHT', gen}
"""

_COMMIT_DISPATCH_LUA = """
local cur = redis.call('GET', KEYS[1])
if not cur then return 0 end
local state, gen, binding = cur:match('^([^|]*)|([^|]*)|([^|]*)|')
if state ~= 'RESERVED' or gen ~= ARGV[1] then return 0 end
redis.call('SET', KEYS[1], 'DISPATCH_OWNED|' .. gen .. '|' .. binding .. '|')
return 1
"""

_MARK_EXECUTED_LUA = """
local cur = redis.call('GET', KEYS[1])
if not cur then return 0 end
local state, gen, binding = cur:match('^([^|]*)|([^|]*)|([^|]*)|')
if state ~= 'DISPATCH_OWNED' or gen ~= ARGV[1] then return 0 end
local val = 'EXECUTED|' .. gen .. '|' .. binding .. '|' .. ARGV[2]
redis.call('SET', KEYS[1], val)
return 1
"""

_MARK_UNKNOWN_LUA = """
local cur = redis.call('GET', KEYS[1])
if not cur then return 0 end
local state, gen, binding = cur:match('^([^|]*)|([^|]*)|([^|]*)|')
if state ~= 'DISPATCH_OWNED' or gen ~= ARGV[1] then return 0 end
redis.call('SET', KEYS[1], 'UNKNOWN|' .. gen .. '|' .. binding .. '|')
return 1
"""

_RELEASE_LUA = """
local cur = redis.call('GET', KEYS[1])
if not cur then return 1 end
local state, gen = cur:match('^([^|]*)|([^|]*)|')
if state ~= 'RESERVED' or gen ~= ARGV[1] then return 0 end
redis.call('DEL', KEYS[1])
return 1
"""

_RESOLVE_UNKNOWN_LUA = """
local cur = redis.call('GET', KEYS[1])
if not cur then return {'NOT_FOUND', ''} end
local state, gen, binding = cur:match('^([^|]*)|([^|]*)|([^|]*)|')
if gen ~= ARGV[1] then return {'STALE_GENERATION', state} end
if state == 'EXECUTED' then return {'ALREADY_EXECUTED', state} end
if state ~= 'UNKNOWN' and state ~= 'DISPATCH_OWNED' then return {'NOT_PENDING', state} end
redis.call('SET', KEYS[1], 'EXECUTED|' .. gen .. '|' .. binding .. '|' .. ARGV[2])
return {'RESOLVED', 'EXECUTED'}
"""


class RedisIdempotencyRegistry:
    """Durable, multi-instance idempotency backed by Redis.

    The atomic moment that matters — winning the first reservation — is a
    single Lua script (``_RESERVE_LUA``): exactly one concurrent caller
    creates the key. Every subsequent state mutation
    (``commit_dispatch``/``mark_executed``/``mark_unknown``/``release``/
    ``resolve_unknown``) is likewise one atomic Lua script performing a
    compare-and-swap on both the current state AND the caller's fence
    (generation) token, so a stale or concurrent caller can never clobber a
    newer generation's state. ``DISPATCH_OWNED``/``UNKNOWN``/``EXECUTED`` are
    written with no TTL (``SET`` without ``EX``, which also clears the
    ``RESERVED`` reservation TTL) — they survive a restart and are never
    recovered into an admittable state by expiry; only the pre-dispatch
    ``RESERVED`` state carries a TTL, and only that TTL feeds ``reserve``'s
    admission logic.

    Fail-closed: any Redis error or timeout yields ``ReserveStatus.ERROR`` /
    ``False`` / :class:`IdempotencyBackendUnavailable`, never a value that
    could be mistaken for "not found" or "safe to retry".
    """

    def __init__(
        self,
        redis_client: Any,
        *,
        namespace: str = "mcc:idem:",
        op_timeout_seconds: float = DEFAULT_OP_TIMEOUT_SECONDS,
    ) -> None:
        self._redis = redis_client
        self._namespace = namespace
        self._op_timeout = op_timeout_seconds

    @classmethod
    def from_url(cls, url: str, **kwargs: Any) -> "RedisIdempotencyRegistry":
        import redis.asyncio as redis

        op_timeout = kwargs.get("op_timeout_seconds", DEFAULT_OP_TIMEOUT_SECONDS)
        client = redis.from_url(
            url,
            socket_timeout=op_timeout,
            socket_connect_timeout=kwargs.pop("connect_timeout_seconds", 1.0),
            decode_responses=True,
        )
        return cls(client, **kwargs)

    def _key(self, key: str) -> str:
        return self._namespace + key

    async def _call(self, coro):
        return await asyncio.wait_for(coro, timeout=self._op_timeout)

    @staticmethod
    def _text(value: Any) -> str:
        if isinstance(value, bytes):
            return value.decode("utf-8", "replace")
        return "" if value is None else str(value)

    async def reserve(
        self,
        key: str,
        *,
        binding: str = "",
        ttl_seconds: int = DEFAULT_RESERVATION_TTL_SECONDS,
    ) -> ReserveResult:
        if not key or not isinstance(key, str):
            return ReserveResult(ReserveStatus.ERROR, "invalid idempotency key")
        if "|" in binding:
            return ReserveResult(ReserveStatus.ERROR, "invalid binding: must not contain '|'")
        generation = uuid.uuid4().hex
        try:
            res = await self._call(self._redis.eval(
                _RESERVE_LUA, 1, self._key(key), binding, str(int(ttl_seconds)), generation,
            ))
        except Exception:
            return ReserveResult(ReserveStatus.ERROR, "idempotency registry unavailable; fail-closed")
        try:
            status = ReserveStatus(self._text(res[0]))
        except (IndexError, ValueError):
            return ReserveResult(ReserveStatus.ERROR, "malformed registry response; fail-closed")
        if status == ReserveStatus.RESERVED:
            return ReserveResult(ReserveStatus.RESERVED, "reserved", binding, fence=generation)
        held_generation = self._text(res[1]) if len(res) > 1 else None
        held_binding = self._text(res[2]) if len(res) > 2 else None
        if status == ReserveStatus.BINDING_CONFLICT:
            return ReserveResult(status, "logical operation bound to a different action/resource/payload",
                                  held_binding)
        if status == ReserveStatus.DUPLICATE_EXECUTED:
            return ReserveResult(status, "operation already executed", binding)
        if status == ReserveStatus.DUPLICATE_UNKNOWN:
            return ReserveResult(status, "operation outcome UNKNOWN; requires reconciliation, not retry", binding)
        return ReserveResult(ReserveStatus.DUPLICATE_INFLIGHT, "operation already reserved", binding)

    async def commit_dispatch(self, key: str, *, fence: str) -> bool:
        try:
            res = await self._call(self._redis.eval(_COMMIT_DISPATCH_LUA, 1, self._key(key), fence))
            return int(res) == 1
        except Exception:
            return False

    async def mark_executed(
        self, key: str, *, fence: str, binding: str = "", result_ref: Optional[str] = None,
    ) -> bool:
        """Terminal, unconditional, permanent — see the in-memory
        registry's identical docstring; no TTL is ever applied here."""
        try:
            res = await self._call(self._redis.eval(
                _MARK_EXECUTED_LUA, 1, self._key(key), fence, result_ref or "",
            ))
            return int(res) == 1
        except Exception:
            return False

    async def mark_unknown(self, key: str, *, fence: str) -> bool:
        try:
            res = await self._call(self._redis.eval(_MARK_UNKNOWN_LUA, 1, self._key(key), fence))
            return int(res) == 1
        except Exception:
            return False

    async def release(self, key: str, *, fence: str) -> bool:
        try:
            res = await self._call(self._redis.eval(_RELEASE_LUA, 1, self._key(key), fence))
            return int(res) == 1
        except Exception:
            return False

    async def resolve_unknown(
        self, key: str, *, expected_generation: str, result_ref: Optional[str] = None,
    ) -> ReconcileResult:
        try:
            res = await self._call(self._redis.eval(
                _RESOLVE_UNKNOWN_LUA, 1, self._key(key), expected_generation, result_ref or "",
            ))
        except Exception:
            return ReconcileResult(ReconcileStatus.ERROR, "idempotency registry unavailable; fail-closed")
        try:
            status = ReconcileStatus(self._text(res[0]))
        except (IndexError, ValueError):
            return ReconcileResult(ReconcileStatus.ERROR, "malformed registry response; fail-closed")
        return ReconcileResult(status, status.value.lower().replace("_", " "))

    async def get_state(self, key: str) -> Optional[StateRecord]:
        try:
            current = await self._call(self._redis.get(self._key(key)))
        except Exception as exc:
            raise IdempotencyBackendUnavailable(f"idempotency backend unavailable: {exc!r}") from exc
        if current is None:
            return None
        state, generation, binding, result_ref = _decode(self._text(current))
        if state is None:
            raise IdempotencyBackendUnavailable(f"malformed idempotency record for {key!r}")
        return StateRecord(state=state, generation=generation, binding=binding, result_ref=result_ref)

class IdempotencyConfigError(Exception):
    """Raised when the idempotency backend is misconfigured (fail-closed start)."""


def idempotency_registry_from_env(env: Optional[Mapping[str, str]] = None):
    """Select an idempotency registry from configuration.

    ``MCC_IDEMPOTENCY_BACKEND=memory`` (default) or ``redis`` (requires
    ``MCC_REDIS_URL``). Refuses to silently fall back to in-memory when Redis is
    requested but unconfigured.

    ``MCC_DEPLOYMENT_MODE=enforcement`` additionally refuses ``memory`` —
    explicit or default — with the same ``IdempotencyConfigError``, never a
    downgrade: an enforcement deployment must not come up with per-process,
    non-durable logical-operation state (see
    ``docs/DURABLE_OPERATION_SAFETY.md``; mirrors
    ``nonce.nonce_registry_from_env``'s identical guard).
    """
    env = os.environ if env is None else env
    backend = env.get("MCC_IDEMPOTENCY_BACKEND", "memory").strip().lower()
    if backend in ("memory", "inmemory", "in-memory"):
        from .deployment_mode import is_enforcement_mode

        if is_enforcement_mode(env):
            raise IdempotencyConfigError(
                "MCC_DEPLOYMENT_MODE=enforcement refuses MCC_IDEMPOTENCY_BACKEND=memory "
                "(explicit or default); enforcement deployments require "
                "MCC_IDEMPOTENCY_BACKEND=redis with a usable MCC_REDIS_URL — no silent "
                "downgrade to volatile, non-durable logical-operation state"
            )
        return InMemoryIdempotencyRegistry()
    if backend == "redis":
        from . import redis_keys
        from .redis_client import RedisConfigError, redis_client_from_env

        try:
            client = redis_client_from_env(env)
        except RedisConfigError as exc:
            raise IdempotencyConfigError(
                "MCC_IDEMPOTENCY_BACKEND=redis requires MCC_REDIS_URL; refusing to "
                f"fall back to in-memory idempotency ({exc})"
            )
        return RedisIdempotencyRegistry(client, namespace=redis_keys.prefix("idem", env))
    raise IdempotencyConfigError(
        f"unknown MCC_IDEMPOTENCY_BACKEND={backend!r}; expected 'memory' or 'redis'"
    )
