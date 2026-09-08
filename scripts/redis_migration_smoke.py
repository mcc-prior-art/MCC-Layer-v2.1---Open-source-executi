#!/usr/bin/env python3
"""End-to-end Redis legacy-migration smoke (PR #105 remediation round).

Run against a real Redis (CI provides one as a service container):

    MCC_REDIS_URL=redis://127.0.0.1:6379/0 python scripts/redis_migration_smoke.py

Proves, against REAL Redis (not a fake), the properties the remediation's
three blockers require:

* Blocker 1 -- the tenant-scoped keyspace and the legacy keyspace are
  structurally disjoint: the exact former alias (a legacy raw key equal to
  ``hash_component(tenant_id) + ':' + operation_id``) no longer collides
  with the real tenant-scoped key, and a record planted under it neither
  leaks into, nor blocks, the real scoped state;
* Blocker 2 -- ``migrate_legacy_record`` validates ``tenant_id``/``key``
  before any Redis call; invalid input leaves the legacy record
  byte-for-byte untouched;
* Blocker 3 -- migration is one atomic operation: a legacy record blocks a
  fresh scoped reservation until migrated, a successful migration transfers
  it exactly once, concurrent migration attempts by two different tenants
  can never both succeed, and a migrated EXECUTED record is reported
  DUPLICATE_EXECUTED afterward (no duplicate-actuation window).

Exits non-zero on any miss.
"""

from __future__ import annotations

import asyncio
import os
import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from mcc_core import redis_keys  # noqa: E402
from mcc_core.idempotency import (  # noqa: E402
    IdempotencyState,
    MigrationStatus,
    RedisIdempotencyRegistry,
    ReserveStatus,
    migrate_legacy_record,
)

URL = os.environ.get("MCC_REDIS_URL", "redis://127.0.0.1:6379/0")


async def main() -> int:
    import redis.asyncio as redis

    run_id = uuid.uuid4().hex[:8]
    client = redis.from_url(URL, decode_responses=True)
    reg = RedisIdempotencyRegistry(client, namespace=f"mcc:idem:migsmoke-{run_id}:")
    failures = []

    # --- Blocker 1: the exact former alias no longer exists ---
    tenant, op = f"tenant-{run_id}", f"op-{run_id}"
    adversarial_raw_key = redis_keys.hash_component(tenant) + ":" + op
    old_style_alias_key = reg._namespace + adversarial_raw_key
    new_scoped_key = reg._key(tenant, op)
    print(f"blocker1: adversarial legacy key = {old_style_alias_key}")
    print(f"blocker1: new scoped key         = {new_scoped_key}")
    if old_style_alias_key == new_scoped_key:
        failures.append("Blocker 1: legacy/scoped keys still alias")

    await client.set(reg._legacy_key(adversarial_raw_key), "EXECUTED|gen-adv|adv-binding|adv-result")
    leaked_state = await reg.get_state(op, tenant_id=tenant)
    if leaked_state is not None:
        failures.append("Blocker 1: adversarial legacy record leaked into scoped get_state")
    fresh = await reg.reserve(op, tenant_id=tenant, binding="the-real-binding")
    if fresh.status != ReserveStatus.RESERVED:
        failures.append(f"Blocker 1: adversarial legacy record wrongly blocked scoped reserve ({fresh.status})")
    print(f"blocker1: leaked_state={leaked_state} fresh_reserve={fresh.status.value}")

    # --- Blocker 2: invalid tenant/key -> zero mutation ---
    legacy_op = f"op-legacy-{run_id}"
    await client.set(reg._legacy_key(legacy_op), "EXECUTED|gen-legacy|b|res")
    for bad_tenant in (None, "", "   "):
        r = await migrate_legacy_record(reg, tenant_id=bad_tenant, key=legacy_op)
        if r.status != MigrationStatus.INVALID_INPUT:
            failures.append(f"Blocker 2: bad tenant {bad_tenant!r} did not fail closed ({r.status})")
    for bad_key in ("", None):
        r = await migrate_legacy_record(reg, tenant_id="tenant-a", key=bad_key)
        if r.status != MigrationStatus.INVALID_INPUT:
            failures.append(f"Blocker 2: bad key {bad_key!r} did not fail closed ({r.status})")
    still_legacy = await client.get(reg._legacy_key(legacy_op))
    if still_legacy != "EXECUTED|gen-legacy|b|res":
        failures.append("Blocker 2: legacy record mutated by an invalid-input migration attempt")
    print(f"blocker2: legacy record after invalid attempts = {still_legacy!r}")

    # --- Blocker 3: legacy blocks reservation until migrated, exactly once ---
    real_op = f"op-real-{run_id}"
    await client.set(reg._legacy_key(real_op), "EXECUTED|gen-legacy|the-real-binding|issue-999")
    blocked = await reg.reserve(real_op, tenant_id="tenant-a", binding="the-real-binding")
    if blocked.status != ReserveStatus.LEGACY_UNMIGRATED:
        failures.append(f"Blocker 3: unmigrated legacy record did not block reserve ({blocked.status})")
    migrated = await migrate_legacy_record(reg, tenant_id="tenant-a", key=real_op)
    if migrated.status != MigrationStatus.MIGRATED:
        failures.append(f"Blocker 3: migration did not report MIGRATED ({migrated.status})")
    after = await reg.reserve(real_op, tenant_id="tenant-a", binding="the-real-binding")
    if after.status != ReserveStatus.DUPLICATE_EXECUTED:
        failures.append(f"Blocker 3: post-migration reserve did not report DUPLICATE_EXECUTED ({after.status})")
    print(f"blocker3: blocked={blocked.status.value} migrated={migrated.status.value} after={after.status.value}")

    # --- Blocker 3: concurrent two-tenant migration race ---
    race_op = f"op-race-{run_id}"
    await client.set(reg._legacy_key(race_op), "EXECUTED|gen-legacy|b|res")
    ra, rb = await asyncio.gather(
        migrate_legacy_record(reg, tenant_id=f"tenant-race-a-{run_id}", key=race_op),
        migrate_legacy_record(reg, tenant_id=f"tenant-race-b-{run_id}", key=race_op),
    )
    outcomes = sorted([ra.status.value, rb.status.value])
    expected = sorted([MigrationStatus.MIGRATED.value, MigrationStatus.CONFLICT.value])
    print(f"blocker3: concurrent race outcomes = {outcomes}")
    if outcomes != expected:
        failures.append(f"Blocker 3: concurrent two-tenant migration race gave {outcomes}, expected {expected}")
    a_state = await reg.get_state(race_op, tenant_id=f"tenant-race-a-{run_id}")
    b_state = await reg.get_state(race_op, tenant_id=f"tenant-race-b-{run_id}")
    if (a_state is not None) == (b_state is not None):
        failures.append("Blocker 3: concurrent migration produced zero or two scoped copies, expected exactly one")

    await client.aclose()

    if failures:
        print("\nREDIS MIGRATION SMOKE FAILED:")
        for f in failures:
            print("  -", f)
        return 1
    print("\nREDIS MIGRATION SMOKE PASSED: keyspace disjointness, input validation, and atomic migration all hold.")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
