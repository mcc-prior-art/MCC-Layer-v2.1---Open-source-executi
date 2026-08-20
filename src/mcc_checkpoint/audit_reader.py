"""Read-only, observational access to an ``mcc_core.audit.AuditLog`` file.

Mirrors ``AuditLog._entry_hash`` locally rather than importing it --
the same observational posture ``src/mcc_evidence/export.py`` and
``verify.py`` already establish ("Mirror AuditLog._entry_hash without
importing the writer"). This module never writes to the audit log, never
imports ``mcc_core.audit``, and holds no gate/authority/nonce/executor
import of any kind.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from mcc_core.signing import canonical_bytes

GENESIS = "GENESIS"
LEGACY_GENESIS_HASH = "genesis"


def _entry_hash(prev_hash: str, body: Dict[str, Any]) -> str:
    return hashlib.sha256(prev_hash.encode("utf-8") + canonical_bytes(body)).hexdigest()


def read_entries(audit_path: str) -> List[Dict[str, Any]]:
    """Read every well-formed JSON object line from the audit file, in
    on-disk order. Malformed lines are skipped rather than raising --
    callers that need "is the file well-formed" should use
    ``chain_state_for_prefix``'s ``valid`` result, which is sensitive to a
    truncated/short file (fewer entries than a checkpoint claims)."""
    path = Path(audit_path)
    if not path.exists():
        return []
    entries: List[Dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(obj, dict) and "hash" in obj and "prev_hash" in obj:
                entries.append(obj)
    return entries


def chain_state_for_prefix(entries: List[Dict[str, Any]], count: int) -> Tuple[bool, Optional[str]]:
    """Independently recompute hash linkage over ``entries[:count]``.

    Returns ``(valid, head_hash)``. ``valid`` is ``False`` if fewer than
    ``count`` entries exist, or if any entry in the prefix fails linkage
    or hash recomputation. ``head_hash`` is the declared ``hash`` of
    entry ``count - 1`` when (and only when) the whole prefix is valid.
    """
    if count <= 0 or len(entries) < count:
        return False, None
    prev: Optional[str] = None
    for entry in entries[:count]:
        declared = entry.get("hash")
        prev_hash = entry.get("prev_hash")
        if prev is not None and prev_hash != prev:
            return False, None
        is_legacy_anchor = prev is None and declared == LEGACY_GENESIS_HASH
        if not is_legacy_anchor:
            body = {k: v for k, v in entry.items() if k != "hash"}
            if _entry_hash(str(prev_hash), body) != declared:
                return False, None
        prev = declared
    return True, prev


def live_chain_state(audit_path: str) -> Tuple[int, bool, Optional[str]]:
    """Read the audit file fresh and return ``(record_count, valid,
    head_hash)`` for the FULL current file (``count = len(entries)``).
    ``valid``/``head_hash`` are as ``chain_state_for_prefix`` above."""
    entries = read_entries(audit_path)
    valid, head_hash = chain_state_for_prefix(entries, len(entries)) if entries else (True, None)
    return len(entries), valid, head_hash
