"""Append-only hash-chain audit log with fsync on every write.

Each entry binds to the previous entry's hash. The first line of an
existing log is treated as the trust anchor (the repository ships a
genesis record dated 2026-04-22).

Every append is serialized across independent OS processes by a
POSIX advisory lock (``fcntl.flock``) on a sidecar ``<path>.lock`` file.
The lock covers the ENTIRE critical section: reading the authoritative
persistent chain head, constructing the record, computing its hash,
appending, and fsyncing. No in-memory ``prev_hash`` is ever authoritative
across processes -- ``self.prev_hash`` is retained only as a best-effort
local cache (used for diagnostics and the constructor's initial value);
every real append re-reads the true chain head from disk while holding
the lock. A write/flush/fsync failure partway through an append rolls
back any bytes already handed to the OS before re-raising, so a caller
that sees a failed append never has to reconcile against a phantom
record left visible on disk.
"""

from __future__ import annotations

import contextlib
import errno
import fcntl
import hashlib
import json
import os
import time
from datetime import datetime, timezone
from typing import Any, Dict, Iterator, List

from .signing import canonical_bytes

GENESIS = "GENESIS"
LEGACY_GENESIS_HASH = "genesis"

# Default bound on how long append() will wait to acquire the inter-process
# lock before failing closed. Deliberately short: a caller blocked this long
# on the audit log should surface as a failure (see every call site's
# existing "except Exception: fail closed" handling in gateway/app.py,
# main.py, and src/mcc_core/coordinator.py), not hang the request.
DEFAULT_LOCK_TIMEOUT_SECONDS = 10.0
_LOCK_POLL_INTERVAL_SECONDS = 0.02


class AuditLockError(Exception):
    """Raised when the inter-process audit lock cannot be acquired within
    the configured timeout, or fails for an unexpected OS-level reason.

    Raising this always means: no record was appended, and the persistent
    chain head was not touched. Every existing caller of
    ``AuditLog.append()`` already treats any exception from it as a
    fail-closed condition (see gateway/app.py, main.py,
    src/mcc_core/coordinator.py) -- this is a subclass of ``Exception``
    specifically so those existing generic ``except Exception`` handlers
    catch it without modification.
    """


class AuditCorruptionError(Exception):
    """Raised when the audit file's last record cannot be parsed WHILE the
    inter-process lock is held (i.e. no cooperating writer could have been
    mid-write at that moment). This indicates real corruption, not a
    benign read/write race, and must never be silently treated as "no
    entries yet" -- doing so could silently restart the chain and mask
    tampering or storage corruption.
    """


class AuditLog:
    def __init__(self, path: str, *, lock_timeout_seconds: float = DEFAULT_LOCK_TIMEOUT_SECONDS) -> None:
        self.path = path
        self.lock_path = path + ".lock"
        self.lock_timeout_seconds = lock_timeout_seconds
        # Best-effort local cache only -- see append(), which never trusts
        # this value for a real write. A transient read race at
        # construction time (another process mid-write) must not crash
        # startup; it only degrades this diagnostic cache, never the
        # authoritative chain.
        self.prev_hash = GENESIS
        last = self._read_last_entry(tolerate_parse_errors=True)
        if last is not None:
            self.prev_hash = str(last.get("hash", GENESIS))

    def _read_last_entry(self, *, tolerate_parse_errors: bool) -> "Dict[str, Any] | None":
        try:
            last_line = None
            with open(self.path, "r", encoding="utf-8") as fh:
                for line in fh:
                    if line.strip():
                        last_line = line
        except FileNotFoundError:
            return None
        except OSError:
            # Any other storage-level failure reading the file (permission
            # denied, path is a directory, I/O error, ...). At construction
            # time (tolerate_parse_errors=True) this is a best-effort cache
            # read only -- degrade gracefully rather than crash the whole
            # process on startup; the AUTHORITATIVE path (append(), called
            # with tolerate_parse_errors=False) re-raises so the caller's
            # existing fail-closed handling applies.
            if tolerate_parse_errors:
                return None
            raise

        if not last_line:
            return None
        try:
            return json.loads(last_line)
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            if tolerate_parse_errors:
                # Constructor-time best-effort cache only; never
                # authoritative (see class docstring / append()).
                return None
            raise AuditCorruptionError(
                f"audit log's last record could not be parsed while the "
                f"inter-process lock was held (path={self.path!r}); this "
                f"indicates real corruption, not a benign race: {exc}"
            ) from exc

    @staticmethod
    def _entry_hash(prev_hash: str, body: Dict[str, Any]) -> str:
        return hashlib.sha256(
            prev_hash.encode("utf-8") + canonical_bytes(body)
        ).hexdigest()

    @contextlib.contextmanager
    def _locked(self) -> Iterator[None]:
        """Hold an exclusive, cross-process POSIX advisory lock on
        ``self.lock_path`` for the duration of the ``with`` block. Fails
        closed: if the lock cannot be acquired within
        ``self.lock_timeout_seconds``, raises ``AuditLockError`` and the
        body is never entered -- no read of chain state, no write, no
        mutation of ``self.prev_hash``.
        """
        lock_fd = os.open(self.lock_path, os.O_CREAT | os.O_RDWR, 0o600)
        acquired = False
        try:
            deadline = time.monotonic() + self.lock_timeout_seconds
            while True:
                try:
                    fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    acquired = True
                    break
                except OSError as exc:
                    if exc.errno not in (errno.EACCES, errno.EAGAIN):
                        raise AuditLockError(
                            f"unexpected OS error acquiring inter-process audit "
                            f"lock {self.lock_path!r}: {exc}"
                        ) from exc
                    if time.monotonic() >= deadline:
                        raise AuditLockError(
                            f"timed out after {self.lock_timeout_seconds}s "
                            f"acquiring inter-process audit lock {self.lock_path!r}; "
                            f"refusing to append without owning the lock"
                        )
                    time.sleep(_LOCK_POLL_INTERVAL_SECONDS)
            yield
        finally:
            if acquired:
                fcntl.flock(lock_fd, fcntl.LOCK_UN)
            os.close(lock_fd)

    def append(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Write one chained entry; fsync before returning.

        The full critical section -- acquiring the inter-process lock,
        reading the AUTHORITATIVE persistent chain head (never the
        in-memory cache), constructing the record, computing its hash,
        appending, and fsyncing -- happens atomically with respect to
        every other process sharing this audit file path. ``self.prev_hash``
        is advanced only after the durable append has actually succeeded;
        any failure (lock timeout, write error, corruption) leaves it
        untouched and propagates as an exception -- no record is
        fabricated as committed, and no stale/partial state becomes the
        next write's basis.

        If the write/flush/fsync sequence fails partway (e.g. the volume
        fills up -- ENOSPC -- exactly at fsync()), any bytes already handed
        to the OS by write()/flush() are rolled back (truncated) before the
        original exception is re-raised, so a caller that sees this failure
        never has to reconcile against a phantom, non-durable record left
        visible on disk.
        """
        with self._locked():
            last = self._read_last_entry(tolerate_parse_errors=False)
            authoritative_prev_hash = (
                str(last.get("hash", GENESIS)) if last is not None else GENESIS
            )
            body = {
                **record,
                "ts": datetime.now(timezone.utc).isoformat(),
                "prev_hash": authoritative_prev_hash,
            }
            entry = {**body, "hash": self._entry_hash(authoritative_prev_hash, body)}
            with open(self.path, "a", encoding="utf-8") as fh:
                start_pos = fh.tell()
                try:
                    fh.write(json.dumps(entry, sort_keys=True) + "\n")
                    fh.flush()
                    os.fsync(fh.fileno())
                except Exception:
                    try:
                        fh.truncate(start_pos)
                        fh.flush()
                    except Exception:
                        pass  # best-effort rollback; the original failure still propagates
                    raise
            # Only reached after a fully durable append -- safe to advance
            # the local cache now.
            self.prev_hash = entry["hash"]
        return entry

    @staticmethod
    def verify_chain(path: str) -> bool:
        """Recompute every entry hash and check linkage. The legacy genesis
        record is accepted as the trust anchor; everything else must verify."""
        try:
            entries: List[Dict[str, Any]] = []
            with open(path, "r", encoding="utf-8") as fh:
                for line in fh:
                    if line.strip():
                        entries.append(json.loads(line))
        except Exception:
            return False

        prev = None
        for entry in entries:
            declared = entry.get("hash")
            prev_hash = entry.get("prev_hash")
            if prev is not None and prev_hash != prev:
                return False
            is_legacy_anchor = (
                prev is None and declared == LEGACY_GENESIS_HASH
            )
            if not is_legacy_anchor:
                body = {k: v for k, v in entry.items() if k != "hash"}
                if AuditLog._entry_hash(str(prev_hash), body) != declared:
                    return False
            prev = declared
        return True
