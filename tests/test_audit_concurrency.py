"""Multi-process audit-chain concurrency regression tests.

Regression coverage for the confirmed historical defect: multiple
independent OS processes constructing AuditLog against the same file
could each observe the same persistent chain head and write competing
successor records, forking the supposedly linear audit chain. See the
module docstring of ``src/mcc_core/audit.py`` for the fix (an exclusive
``fcntl.flock`` on a ``<path>.lock`` sidecar, held for the entire
read-authoritative-head -> construct -> hash -> append -> fsync critical
section).

Uses ``multiprocessing.get_context("spawn")`` throughout -- genuine
independent OS processes with fresh interpreters, never threads and never
``fork()`` (which would share already-imported parent state and
understate the risk this regression guards against).

Every chain produced here is independently re-validated straight from the
raw on-disk bytes: hash recomputed via the real
``mcc_core.signing.canonical_bytes`` (never by calling back into
``AuditLog``'s own hashing/verification code, so a bug shared between the
writer and its own verifier cannot cancel out), genesis count, fork
detection (two distinct records both claiming the same predecessor),
broken-link detection, and full record-id accounting. The physical
on-disk order is validated exactly as written -- nothing is ever
reordered before validation.
"""

from __future__ import annotations

import fcntl
import hashlib
import json
import multiprocessing as mp
import os
import sys
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

import pytest

_SRC = str(Path(__file__).resolve().parents[1] / "src")
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

from mcc_core.audit import GENESIS, AuditLockError, AuditLog  # noqa: E402
from mcc_core.signing import canonical_bytes  # noqa: E402


# ---------------------------------------------------------------------
# Independent chain validator
# ---------------------------------------------------------------------


def _independent_entry_hash(prev_hash: str, body: Dict[str, Any]) -> str:
    return hashlib.sha256(prev_hash.encode("utf-8") + canonical_bytes(body)).hexdigest()


class ChainReport:
    def __init__(self) -> None:
        self.records: List[Dict[str, Any]] = []
        self.malformed_lines: List[str] = []
        self.genesis_count = 0
        self.broken_links: List[Dict[str, Any]] = []
        self.hash_mismatches: List[Dict[str, Any]] = []
        self.forks: List[Dict[str, Any]] = []
        self.duplicate_ids: List[str] = []

    @property
    def valid(self) -> bool:
        return (
            not self.malformed_lines
            and self.genesis_count == 1
            and not self.broken_links
            and not self.hash_mismatches
            and not self.forks
            and not self.duplicate_ids
        )


def independently_validate_chain(path: str) -> ChainReport:
    """Parse the file exactly as it sits on disk (never reordered) and
    validate genesis/linkage/hash/fork/duplicate properties."""
    report = ChainReport()
    text = Path(path).read_text(encoding="utf-8")
    lines = [ln for ln in text.split("\n") if ln.strip() != ""]

    records: List[Dict[str, Any]] = []
    for idx, line in enumerate(lines):
        try:
            obj = json.loads(line)
        except json.JSONDecodeError as exc:
            report.malformed_lines.append(f"line {idx}: {exc}")
            continue
        if not isinstance(obj, dict) or "hash" not in obj or "prev_hash" not in obj:
            report.malformed_lines.append(f"line {idx}: missing hash/prev_hash")
            continue
        records.append(obj)
    report.records = records

    seen_ids: Dict[str, int] = {}
    prev_hash_claims: Dict[str, List[int]] = {}
    prev_declared: Optional[str] = None
    for i, entry in enumerate(records):
        declared = entry.get("hash")
        prev_hash = entry.get("prev_hash")
        rid = entry.get("test_record_id")
        if rid is not None:
            if rid in seen_ids:
                report.duplicate_ids.append(rid)
            seen_ids[rid] = i
        prev_hash_claims.setdefault(str(prev_hash), []).append(i)

        is_genesis = i == 0 and prev_hash == GENESIS
        if is_genesis:
            report.genesis_count += 1
        else:
            if prev_declared is not None and prev_hash != prev_declared:
                report.broken_links.append(
                    {"index": i, "expected": prev_declared, "actual": prev_hash}
                )
            body = {k: v for k, v in entry.items() if k != "hash"}
            recomputed = _independent_entry_hash(str(prev_hash), body)
            if recomputed != declared:
                report.hash_mismatches.append(
                    {"index": i, "declared": declared, "recomputed": recomputed}
                )
        prev_declared = declared

    for claimed_prev, indices in prev_hash_claims.items():
        if len(indices) <= 1:
            continue
        distinct_hashes = {records[i].get("hash") for i in indices}
        if len(distinct_hashes) > 1:
            report.forks.append({"claimed_prev_hash": claimed_prev, "indices": indices})

    return report


# ---------------------------------------------------------------------
# Multi-process worker
# ---------------------------------------------------------------------


def _worker_append(
    src_path: str, audit_path: str, results_path: str, spawn_index: int,
    writes: int, run_id: str, barrier: Any,
) -> None:
    if src_path not in sys.path:
        sys.path.insert(0, src_path)
    from mcc_core.audit import AuditLog as _AuditLog  # imported fresh in this process

    result: Dict[str, Any] = {"spawn_index": spawn_index, "successful": [], "failed": 0, "errors": []}
    try:
        barrier.wait(timeout=60)
        audit = _AuditLog(audit_path)
        for seq in range(writes):
            rid = f"{run_id}:{spawn_index}:{seq}:{uuid.uuid4().hex}"
            try:
                audit.append({"test_record_id": rid, "spawn_index": spawn_index, "sequence": seq})
                result["successful"].append(rid)
            except Exception as exc:  # noqa: BLE001 -- capture every failure mode
                result["failed"] += 1
                result["errors"].append(f"{type(exc).__name__}: {exc}")
    except Exception as exc:  # noqa: BLE001
        result["errors"].append(f"WORKER FATAL: {type(exc).__name__}: {exc}")
    finally:
        tmp = results_path + f".tmp{os.getpid()}"
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(result, fh)
        os.replace(tmp, results_path)


def _run_multiprocess(tmp_path: Path, num_processes: int, writes_per_process: int, run_tag: str):
    ctx = mp.get_context("spawn")
    audit_path = str(tmp_path / f"audit-{run_tag}.jsonl")
    results_dir = tmp_path / f"results-{run_tag}"
    results_dir.mkdir()

    run_id = uuid.uuid4().hex[:12]
    barrier = ctx.Barrier(num_processes)
    procs = []
    for i in range(num_processes):
        rp = str(results_dir / f"worker_{i:04d}.json")
        p = ctx.Process(
            target=_worker_append,
            args=(_SRC, audit_path, rp, i, writes_per_process, run_id, barrier),
        )
        p.start()
        procs.append(p)

    for p in procs:
        p.join(timeout=60)

    exit_codes = [p.exitcode for p in procs]
    worker_results = []
    for i in range(num_processes):
        rp = results_dir / f"worker_{i:04d}.json"
        with open(rp, encoding="utf-8") as fh:
            worker_results.append(json.load(fh))

    return audit_path, exit_codes, worker_results


# ---------------------------------------------------------------------
# A. Multi-process linearity: real hash linkage, not just line count.
# ---------------------------------------------------------------------


@pytest.mark.parametrize("num_processes", [2, 10])
def test_multiprocess_linearity(tmp_path, num_processes):
    writes_per_process = 6
    audit_path, exit_codes, worker_results = _run_multiprocess(
        tmp_path, num_processes, writes_per_process, f"linearity-{num_processes}"
    )
    assert all(c == 0 for c in exit_codes), exit_codes
    for wr in worker_results:
        assert wr["errors"] == [], wr["errors"]

    report = independently_validate_chain(audit_path)
    assert report.genesis_count == 1
    assert report.forks == [], report.forks
    assert report.broken_links == [], report.broken_links
    assert report.hash_mismatches == [], report.hash_mismatches
    assert report.malformed_lines == [], report.malformed_lines
    assert len(report.records) == num_processes * writes_per_process


# ---------------------------------------------------------------------
# B. Same-head race regression: the exact historical scenario.
# ---------------------------------------------------------------------


def test_same_head_race_no_competing_successors(tmp_path):
    """Maximizes contention at the exact race window that forked the
    chain historically: every process starts against a FRESH file (every
    one of them would, pre-fix, read prev_hash == GENESIS) and is
    released from a barrier at the same instant. Before the fix, this
    reliably produced >=2 records independently claiming GENESIS as
    their predecessor."""
    num_processes = 15
    audit_path, exit_codes, worker_results = _run_multiprocess(
        tmp_path, num_processes, 1, "same-head-race"
    )
    assert all(c == 0 for c in exit_codes), exit_codes
    for wr in worker_results:
        assert wr["errors"] == [], wr["errors"]

    report = independently_validate_chain(audit_path)
    assert report.genesis_count == 1, "more than one record claimed GENESIS as predecessor -- fork"
    assert report.forks == [], report.forks
    assert report.broken_links == [], report.broken_links
    assert len(report.records) == num_processes


# ---------------------------------------------------------------------
# C. Record completeness: expected == actual, no missing, no duplicate.
# ---------------------------------------------------------------------


def test_record_completeness_no_missing_no_duplicate(tmp_path):
    num_processes, writes_per_process = 10, 8
    audit_path, exit_codes, worker_results = _run_multiprocess(
        tmp_path, num_processes, writes_per_process, "completeness"
    )
    assert all(c == 0 for c in exit_codes), exit_codes

    reported_success_ids = set()
    reported_success_count = 0
    for wr in worker_results:
        assert wr["errors"] == [], wr["errors"]
        reported_success_count += len(wr["successful"])
        reported_success_ids.update(wr["successful"])

    expected_total = num_processes * writes_per_process
    assert reported_success_count == expected_total

    report = independently_validate_chain(audit_path)
    on_disk_ids = {r["test_record_id"] for r in report.records if "test_record_id" in r}
    assert len(report.records) == expected_total
    assert on_disk_ids == reported_success_ids, (
        "missing:", reported_success_ids - on_disk_ids, "unexpected:", on_disk_ids - reported_success_ids,
    )
    assert report.duplicate_ids == []
    assert report.valid


# ---------------------------------------------------------------------
# D. Lock timeout / acquisition failure -> fails closed.
# ---------------------------------------------------------------------


def _hold_lock(path: str, seconds: float, ready_path: str) -> None:
    fd = os.open(path, os.O_CREAT | os.O_RDWR, 0o600)
    fcntl.flock(fd, fcntl.LOCK_EX)
    Path(ready_path).write_text("locked", encoding="utf-8")
    time.sleep(seconds)
    fcntl.flock(fd, fcntl.LOCK_UN)
    os.close(fd)


def test_lock_held_by_another_process_fails_closed(tmp_path):
    """Hold the SAME inter-process lock AuditLog.append() itself acquires
    (the ``<path>.lock`` sidecar, exclusive flock) from a separate OS
    process, then attempt a real append from a second AuditLog instance.
    The second append must fail, must not write anything, must not
    advance its local prev_hash cache, and the pre-existing chain must
    remain valid afterward. Once the lock is released, a normal append
    must succeed again."""
    audit_path = str(tmp_path / "audit.jsonl")
    seed = AuditLog(audit_path)
    seed.append({"seq": 0})

    lock_path = audit_path + ".lock"
    hold_seconds = 3.0

    ctx = mp.get_context("spawn")
    ready_path = str(tmp_path / "lock_ready")
    holder = ctx.Process(target=_hold_lock, args=(lock_path, hold_seconds, ready_path))
    holder.start()

    deadline = time.monotonic() + 10
    while not Path(ready_path).exists():
        assert time.monotonic() < deadline, "lock holder never signaled acquisition"
        time.sleep(0.02)

    writer = AuditLog(audit_path, lock_timeout_seconds=1.0)
    prev_hash_before = writer.prev_hash

    with pytest.raises(AuditLockError):
        writer.append({"seq": 1})

    assert writer.prev_hash == prev_hash_before, "prev_hash must not advance on a failed append"

    with open(audit_path, encoding="utf-8") as fh:
        lines = [ln for ln in fh if ln.strip()]
    assert len(lines) == 1, "no record may be appended while the lock is held elsewhere"
    assert AuditLog.verify_chain(audit_path)

    holder.join(timeout=15)
    assert holder.exitcode == 0

    # Lock released -- a normal append now succeeds, chaining correctly
    # onto the ORIGINAL record (not a stale cached value).
    entry = writer.append({"seq": 1})
    assert entry["prev_hash"] != GENESIS
    with open(audit_path, encoding="utf-8") as fh:
        lines = [ln for ln in fh if ln.strip()]
    assert len(lines) == 2
    assert AuditLog.verify_chain(audit_path)
    report = independently_validate_chain(audit_path)
    assert report.valid


# ---------------------------------------------------------------------
# E. Existing single-process behavior unchanged.
# ---------------------------------------------------------------------


def test_single_process_behavior_unchanged(tmp_path):
    path = str(tmp_path / "audit.jsonl")
    log = AuditLog(path)
    assert log.prev_hash == GENESIS
    entries = [log.append({"decision": "ALLOW", "seq": i}) for i in range(5)]
    assert AuditLog.verify_chain(path)

    report = independently_validate_chain(path)
    assert report.valid
    assert len(report.records) == 5
    assert entries[0]["prev_hash"] == GENESIS
    for i in range(1, 5):
        assert entries[i]["prev_hash"] == entries[i - 1]["hash"]
