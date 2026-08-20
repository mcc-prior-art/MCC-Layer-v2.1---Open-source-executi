"""Checkpoint generation: fires every N records OR T seconds, whichever
comes first. Both thresholds are configurable (constructor args or env),
never hardcoded into the trigger logic itself.
"""

from __future__ import annotations

import os
import time
from typing import Any, Callable, Dict, Mapping, Optional

from mcc_core.signing import SigningKey

from . import audit_reader
from .checkpoint import build_checkpoint, checkpoint_hash, resolve_repo_sha
from .errors import CheckpointGenerationError
from .store import AnchorStore

DEFAULT_RECORD_INTERVAL = 500
DEFAULT_TIME_INTERVAL_SECONDS = 15 * 60  # 15 minutes


class CheckpointGenerator:
    """Stateful trigger + issuance. One instance owns the "since the last
    checkpoint" bookkeeping (record count and wall-clock time); state is
    seeded from the anchor store's latest checkpoint on construction, so a
    process restart resumes the N/T windows rather than re-checkpointing
    immediately or losing track of elapsed time.
    """

    def __init__(
        self,
        *,
        audit_path: str,
        signing_key: SigningKey,
        anchor_store: AnchorStore,
        chain_id: str,
        environment: str,
        record_interval: int = DEFAULT_RECORD_INTERVAL,
        time_interval_seconds: float = DEFAULT_TIME_INTERVAL_SECONDS,
        repo_sha: Optional[str] = None,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        """``signing_key`` must be the dedicated Audit Checkpoint signing
        key (``checkpoint_signing.py``) -- never the Decision Token key.
        ``chain_id`` identifies which audit-chain/deployment this
        generator's checkpoints describe; ``environment`` labels the
        deployment tier (e.g. "production", "pilot"). Both are required,
        non-optional, and carried into every issued checkpoint."""
        if record_interval <= 0:
            raise CheckpointGenerationError("record_interval must be positive")
        if time_interval_seconds <= 0:
            raise CheckpointGenerationError("time_interval_seconds must be positive")
        if not chain_id:
            raise CheckpointGenerationError("chain_id must be non-empty")
        if not environment:
            raise CheckpointGenerationError("environment must be non-empty")
        self.audit_path = audit_path
        self.signing_key = signing_key
        self.anchor_store = anchor_store
        self.chain_id = chain_id
        self.environment = environment
        self.record_interval = record_interval
        self.time_interval_seconds = time_interval_seconds
        self._repo_sha_override = repo_sha
        self._clock = clock

        latest = anchor_store.read_latest_checkpoint()
        self._last_checkpoint: Optional[Dict[str, Any]] = latest
        self._last_record_count: int = int(latest["record_count"]) if latest else 0
        self._last_checkpoint_at: float = self._clock()

    def due(self) -> bool:
        record_count, _valid, _head = audit_reader.live_chain_state(self.audit_path)
        due_by_count = (record_count - self._last_record_count) >= self.record_interval
        due_by_time = (self._clock() - self._last_checkpoint_at) >= self.time_interval_seconds
        return record_count > self._last_record_count and (due_by_count or due_by_time)

    def maybe_checkpoint(self, *, force: bool = False) -> Optional[Dict[str, Any]]:
        """Issue and anchor a new checkpoint if due (or ``force=True``).
        Returns the signed checkpoint, or ``None`` if nothing was due.
        Raises ``CheckpointGenerationError`` if the live chain currently
        fails independent verification (never checkpoint a chain already
        known to be broken) and ``AnchorStoreError`` if anchoring fails."""
        record_count, valid, head_hash = audit_reader.live_chain_state(self.audit_path)
        if record_count == 0:
            return None
        if not valid:
            raise CheckpointGenerationError(
                "live audit chain fails independent verification; refusing "
                "to issue a checkpoint over a chain already known to be broken"
            )
        if record_count == self._last_record_count and not force:
            return None  # nothing new since the last checkpoint

        due_by_count = (record_count - self._last_record_count) >= self.record_interval
        due_by_time = (self._clock() - self._last_checkpoint_at) >= self.time_interval_seconds
        if not force and not due_by_count and not due_by_time:
            return None

        prev_hash = checkpoint_hash(self._last_checkpoint) if self._last_checkpoint else None
        repo_sha = resolve_repo_sha(override=self._repo_sha_override)
        checkpoint = build_checkpoint(
            self.signing_key,
            chain_id=self.chain_id,
            environment=self.environment,
            record_count=record_count,
            chain_head_hash=str(head_hash),
            prev_checkpoint_hash=prev_hash,
            repo_sha=repo_sha,
        )
        self.anchor_store.append_checkpoint(checkpoint)
        self._last_checkpoint = checkpoint
        self._last_record_count = record_count
        self._last_checkpoint_at = self._clock()
        return checkpoint


def checkpoint_generator_from_env(
    *, audit_path: str, signing_key: SigningKey, anchor_store: AnchorStore,
    env: Optional[Mapping[str, str]] = None,
) -> CheckpointGenerator:
    """Build a ``CheckpointGenerator`` with N/T thresholds read from
    ``MCC_CHECKPOINT_RECORD_INTERVAL`` / ``MCC_CHECKPOINT_TIME_INTERVAL_SECONDS``
    (defaults: 500 records / 900 seconds), ``chain_id`` from
    ``MCC_CHECKPOINT_CHAIN_ID`` (required -- raises if unset/empty),
    ``environment`` from ``MCC_CHECKPOINT_ENVIRONMENT`` (default
    "unspecified"), and ``repo_sha`` from ``MCC_CHECKPOINT_REPO_SHA`` if
    set (otherwise resolved from ``git`` lazily at issuance time)."""
    env = os.environ if env is None else env
    record_interval = int(env.get("MCC_CHECKPOINT_RECORD_INTERVAL", DEFAULT_RECORD_INTERVAL))
    time_interval_seconds = float(
        env.get("MCC_CHECKPOINT_TIME_INTERVAL_SECONDS", DEFAULT_TIME_INTERVAL_SECONDS)
    )
    chain_id = env.get("MCC_CHECKPOINT_CHAIN_ID", "").strip()
    if not chain_id:
        raise CheckpointGenerationError(
            "MCC_CHECKPOINT_CHAIN_ID must be set -- identifies which audit-chain "
            "instance this deployment's checkpoints describe"
        )
    environment = env.get("MCC_CHECKPOINT_ENVIRONMENT", "unspecified").strip() or "unspecified"
    repo_sha = env.get("MCC_CHECKPOINT_REPO_SHA", "").strip() or None
    return CheckpointGenerator(
        audit_path=audit_path,
        signing_key=signing_key,
        anchor_store=anchor_store,
        chain_id=chain_id,
        environment=environment,
        record_interval=record_interval,
        time_interval_seconds=time_interval_seconds,
        repo_sha=repo_sha,
    )
