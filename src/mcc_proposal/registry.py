"""Proposal registry — durable inbox for logical operations that have been
PROPOSED but not yet admitted for execution.

Deliberately distinct from ``mcc_core.idempotency`` (Section 6): ``RESERVED``
there has a precise security meaning -- a durably admitted, pre-dispatch
logical operation on the real execution path. A proposal has not been
admitted for anything; it is purely informational bookkeeping proving "this
identity was already claimed for this exact binding." This module never
imports, calls, or wraps ``reserve``/``commit_dispatch``/``mark_executed``/
``mark_unknown``/``resolve_unknown`` -- those remain exclusively the
coordinator's.

Tenant isolation (Section 7): every operation is scoped by
``(tenant_id, logical_operation_id)``. ``tenant_id`` must be the caller's
AUTHENTICATED identity as established by the transport layer -- never a
value taken from proposal payload/actor fields.
"""

from __future__ import annotations

import asyncio
import os
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Mapping, Optional, Tuple


class ProposalRegisterStatus(str, Enum):
    REGISTERED = "REGISTERED"                    # first time; now PROPOSED
    IDEMPOTENT_DUPLICATE = "IDEMPOTENT_DUPLICATE"  # identical binding already registered
    BINDING_CONFLICT = "BINDING_CONFLICT"          # same key, different binding
    ERROR = "ERROR"                                # indeterminate -> fail closed


@dataclass(frozen=True)
class ProposalRegisterResult:
    status: ProposalRegisterStatus
    reason: str
    binding: Optional[str] = None

    @property
    def ok(self) -> bool:
        return self.status in (ProposalRegisterStatus.REGISTERED, ProposalRegisterStatus.IDEMPOTENT_DUPLICATE)


@dataclass(frozen=True)
class ProposalRecord:
    tenant_id: str
    logical_operation_id: str
    binding: str
    created_at: float


class ProposalBackendUnavailable(Exception):
    """Raised by ``get`` when the backend cannot give a definite answer.
    Callers MUST NOT treat this as "not found" -- see ``ProposalStatus``
    composition rules (Section 8/19): backend uncertainty is UNAVAILABLE,
    never NOT_FOUND, never "safe to retry"."""


class ProposalConfigError(Exception):
    """Raised when the proposal backend is misconfigured (fail-closed start)."""


def _tenant_key(tenant_id: str, logical_operation_id: str) -> str:
    # Delimiter-safe: tenant_id/logical_operation_id are caller-controlled
    # strings, so an in-process dict key uses a tuple (no injection surface);
    # the Redis backend below hashes both segments instead of concatenating
    # raw strings with a guessable separator.
    return f"{tenant_id}\x00{logical_operation_id}"


class InMemoryProposalRegistry:
    """Single-process proposal inbox (dev / tests). Atomic the same way
    ``InMemoryIdempotencyRegistry`` is: the whole critical section runs
    without an ``await`` in between, so no other coroutine on this event
    loop can interleave a conflicting write. NOT durable and NOT
    multi-instance -- a real deployment configures the Redis backend."""

    def __init__(self) -> None:
        self._store: Dict[str, ProposalRecord] = {}

    async def register(
        self, *, tenant_id: str, logical_operation_id: str, binding: str,
    ) -> ProposalRegisterResult:
        key = _tenant_key(tenant_id, logical_operation_id)
        existing = self._store.get(key)
        if existing is None:
            self._store[key] = ProposalRecord(
                tenant_id=tenant_id, logical_operation_id=logical_operation_id,
                binding=binding, created_at=time.time(),
            )
            return ProposalRegisterResult(ProposalRegisterStatus.REGISTERED, "registered", binding)
        if existing.binding == binding:
            return ProposalRegisterResult(
                ProposalRegisterStatus.IDEMPOTENT_DUPLICATE, "identical proposal already registered", binding,
            )
        return ProposalRegisterResult(
            ProposalRegisterStatus.BINDING_CONFLICT,
            "logical_operation_id is already bound to a different action/resource/payload",
            existing.binding,
        )

    async def get(self, *, tenant_id: str, logical_operation_id: str) -> Optional[ProposalRecord]:
        return self._store.get(_tenant_key(tenant_id, logical_operation_id))


_REGISTER_LUA = """
local cur = redis.call('GET', KEYS[1])
if not cur then
    redis.call('SET', KEYS[1], ARGV[1] .. '|' .. ARGV[2])
    return {'REGISTERED', ARGV[1]}
end
local binding, created = cur:match('^([^|]*)|(.*)$')
if binding == ARGV[1] then
    return {'IDEMPOTENT_DUPLICATE', binding}
end
return {'BINDING_CONFLICT', binding}
"""


class RedisProposalRegistry:
    """Durable, multi-instance proposal inbox backed by Redis. The one atomic
    moment (first-writer-wins) is a single Lua script -- exactly one
    concurrent caller creates the key; every racing caller after that either
    observes IDEMPOTENT_DUPLICATE (same binding) or BINDING_CONFLICT
    (different binding), never a mixed/overwritten record."""

    def __init__(self, redis_client: Any, *, namespace: str) -> None:
        self._redis = redis_client
        self._namespace = namespace

    @classmethod
    def from_url(cls, url: str, *, namespace: str, connect_timeout_seconds: float = 1.0) -> "RedisProposalRegistry":
        import redis.asyncio as redis

        client = redis.from_url(
            url, socket_timeout=1.0, socket_connect_timeout=connect_timeout_seconds,
            decode_responses=True,
        )
        return cls(client, namespace=namespace)

    def _key(self, tenant_id: str, logical_operation_id: str) -> str:
        from mcc_core import redis_keys

        return (
            self._namespace
            + redis_keys.hash_component(tenant_id)
            + ":"
            + redis_keys.safe_segment(logical_operation_id)
        )

    async def register(
        self, *, tenant_id: str, logical_operation_id: str, binding: str,
    ) -> ProposalRegisterResult:
        if "|" in binding:
            return ProposalRegisterResult(ProposalRegisterStatus.ERROR, "invalid binding: must not contain '|'")
        key = self._key(tenant_id, logical_operation_id)
        try:
            res = await asyncio.wait_for(
                self._redis.eval(_REGISTER_LUA, 1, key, binding, repr(time.time())), timeout=1.0,
            )
        except Exception:
            return ProposalRegisterResult(ProposalRegisterStatus.ERROR, "proposal registry unavailable; fail-closed")
        try:
            status = ProposalRegisterStatus(res[0])
            observed_binding = res[1]
        except (IndexError, ValueError, KeyError):
            return ProposalRegisterResult(ProposalRegisterStatus.ERROR, "malformed registry response; fail-closed")
        reason = {
            ProposalRegisterStatus.REGISTERED: "registered",
            ProposalRegisterStatus.IDEMPOTENT_DUPLICATE: "identical proposal already registered",
            ProposalRegisterStatus.BINDING_CONFLICT: "logical_operation_id is already bound to a "
                                                      "different action/resource/payload",
        }[status]
        return ProposalRegisterResult(status, reason, observed_binding)

    async def get(self, *, tenant_id: str, logical_operation_id: str) -> Optional[ProposalRecord]:
        key = self._key(tenant_id, logical_operation_id)
        try:
            current = await asyncio.wait_for(self._redis.get(key), timeout=1.0)
        except Exception as exc:
            raise ProposalBackendUnavailable(f"proposal registry unavailable: {exc!r}") from exc
        if current is None:
            return None
        try:
            binding, created = current.split("|", 1)
            created_at = float(created)
        except (ValueError, AttributeError) as exc:
            raise ProposalBackendUnavailable(f"malformed proposal record for {key!r}") from exc
        return ProposalRecord(
            tenant_id=tenant_id, logical_operation_id=logical_operation_id,
            binding=binding, created_at=created_at,
        )


def proposal_registry_from_env(env: Optional[Mapping[str, str]] = None):
    """``MCC_PROPOSAL_BACKEND=memory`` (default) or ``redis`` (requires
    ``MCC_REDIS_URL``). Mirrors ``idempotency_registry_from_env``: refuses to
    silently fall back to in-memory when redis is requested but
    unconfigured, and refuses ``memory`` outright under
    ``MCC_DEPLOYMENT_MODE=enforcement``."""
    env = os.environ if env is None else env
    backend = env.get("MCC_PROPOSAL_BACKEND", "memory").strip().lower()
    if backend in ("memory", "inmemory", "in-memory"):
        from mcc_core.deployment_mode import is_enforcement_mode

        if is_enforcement_mode(env):
            raise ProposalConfigError(
                "MCC_DEPLOYMENT_MODE=enforcement refuses MCC_PROPOSAL_BACKEND=memory "
                "(explicit or default); enforcement deployments require "
                "MCC_PROPOSAL_BACKEND=redis with a usable MCC_REDIS_URL"
            )
        return InMemoryProposalRegistry()
    if backend == "redis":
        from mcc_core import redis_keys
        from mcc_core.redis_client import RedisConfigError, redis_client_from_env

        try:
            client = redis_client_from_env(env)
        except RedisConfigError as exc:
            raise ProposalConfigError(
                f"MCC_PROPOSAL_BACKEND=redis requires MCC_REDIS_URL; refusing to fall "
                f"back to in-memory proposal storage ({exc})"
            )
        return RedisProposalRegistry(client, namespace=redis_keys.prefix("proposal", env))
    raise ProposalConfigError(f"unknown MCC_PROPOSAL_BACKEND={backend!r}; expected 'memory' or 'redis'")


__all__ = [
    "ProposalRegisterStatus", "ProposalRegisterResult", "ProposalRecord",
    "ProposalBackendUnavailable", "ProposalConfigError",
    "InMemoryProposalRegistry", "RedisProposalRegistry", "proposal_registry_from_env",
]
