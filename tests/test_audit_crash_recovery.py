"""Audit-log crash/durability-failure regression tests.

Regression coverage for two defects found by the Gate 2 (Crash & Recovery /
Fail-Closed) pre-pilot stand, both narrow extensions of the same hardening
PR #83 already did to ``src/mcc_core/audit.py``:

1. **Phantom record on a durability (fsync) failure.** ``append()`` used to
   call ``fh.write()`` + ``fh.flush()`` (handing bytes to the OS) BEFORE
   ``os.fsync()``. If ``fsync()`` itself failed (e.g. ENOSPC), the caller
   correctly saw the exception and treated the append as failed -- but the
   record was ALREADY visible in the file (a well-formed, chain-valid,
   but never-actually-confirmed-durable "phantom" entry the caller never
   agreed happened). Fixed: any exception during write/flush/fsync now
   rolls back (truncates) whatever bytes were already handed to the OS
   before re-raising, so a caller that sees a failed append never has to
   reconcile against a phantom record left on disk.

2. **Uncaught crash on a general storage OSError at construction.**
   ``AuditLog.__init__``'s best-effort last-entry read only tolerated
   ``FileNotFoundError``/``JSONDecodeError``/``UnicodeDecodeError`` (the
   PR #83 hardening). Any OTHER storage-level ``OSError`` -- e.g. the
   configured audit path resolving to a directory, or a permission
   failure -- propagated uncaught out of the constructor, crashing the
   whole process at startup instead of degrading gracefully. Fixed: the
   constructor's best-effort read now tolerates any ``OSError`` (not just
   the JSON-parsing-related subset), while the AUTHORITATIVE read inside
   ``append()`` still re-raises so the existing fail-closed handling at
   every call site applies.

Each test is verified as a genuine regression guard, not a vacuous one:
run against the pre-fix implementation, both fail with the exact defect
behavior described above (see the PR body / validation report for that
evidence) -- these tests are not merely checking "no exception," they
assert the SPECIFIC no-phantom-record / no-crash properties.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

_SRC = str(Path(__file__).resolve().parents[1] / "src")
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

from mcc_core.audit import AuditLog  # noqa: E402


def test_fsync_failure_rolls_back_no_phantom_record(tmp_path):
    path = str(tmp_path / "audit.jsonl")
    audit = AuditLog(path)
    audit.append({"seq": 0})

    before_bytes = Path(path).read_bytes()
    prev_hash_before = audit.prev_hash

    real_fsync = os.fsync

    def failing_fsync(fd):
        raise OSError(28, "No space left on device")  # ENOSPC

    os.fsync = failing_fsync
    try:
        with pytest.raises(OSError):
            audit.append({"seq": 1})
    finally:
        os.fsync = real_fsync

    assert audit.prev_hash == prev_hash_before, "prev_hash must not advance on a failed append"

    after_bytes = Path(path).read_bytes()
    assert after_bytes == before_bytes, (
        "the file must be restored to its exact pre-attempt state -- no "
        "phantom, non-durable record may remain visible on disk after a "
        "reported append failure"
    )
    assert AuditLog.verify_chain(path)

    # Normal operation resumes once the simulated durability failure clears.
    entry = audit.append({"seq": 1})
    assert entry["seq"] == 1
    assert Path(path).read_text().count("\n") == 2
    assert AuditLog.verify_chain(path)


def test_construction_against_storage_error_does_not_crash(tmp_path):
    """A misconfigured audit path (here: resolves to a directory, not a
    file) must not crash AuditLog's constructor -- it degrades the
    best-effort diagnostic cache only. The next real append still fails
    closed with the underlying OSError."""
    dir_path = tmp_path / "audit.jsonl"
    dir_path.mkdir()

    audit = AuditLog(str(dir_path))  # must not raise
    assert audit.prev_hash == "GENESIS"

    with pytest.raises(OSError):
        audit.append({"seq": 0})

    # No stray file was created inside the directory by the failed attempt
    # (only the lock sidecar, which is expected/harmless).
    assert set(os.listdir(dir_path)) <= {"audit.jsonl.lock"}


def test_construction_against_missing_parent_directory_fails_closed_on_append(tmp_path):
    path = str(tmp_path / "nonexistent_subdir" / "audit.jsonl")
    audit = AuditLog(path)  # construction: FileNotFoundError already tolerated pre-fix
    assert audit.prev_hash == "GENESIS"

    with pytest.raises(OSError):
        audit.append({"seq": 0})

    assert not os.path.exists(path)
