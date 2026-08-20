#!/usr/bin/env python3
"""Periodic Audit Checkpoint generation -- runs OUT OF PROCESS from the
Gateway (a cron entry or a sidecar container), not as a background task
inside the ASGI app. Polls the audit log and, when the N-record or
T-time trigger is due, signs and anchors one checkpoint.

Usage:
    MCC_CHECKPOINT_CHAIN_ID=mcc-layer-pilot \\
    MCC_CHECKPOINT_ENVIRONMENT=pilot \\
    MCC_CHECKPOINT_ANCHOR_BACKEND=git \\
    MCC_CHECKPOINT_ANCHOR_REMOTE_URL=<clone url of mcc-prior-art/mcc-audit-anchors> \\
    MCC_CHECKPOINT_ANCHOR_WORKDIR=/var/lib/mcc/checkpoint-anchor-workdir \\
    python scripts/run_checkpoint_generator.py \\
        --audit-path audit.jsonl \\
        --checkpoint-signing-key mcc_checkpoint_signing_key.pem \\
        --poll-seconds 30

``--once`` checks and (if due) issues a single checkpoint, then exits --
suited to being invoked directly by an external cron rather than looping.
Without ``--once`` it polls forever at ``--poll-seconds`` (default 30).

Never touches Decision Token signing, the Execution Gate, or nonce/replay
state -- this only calls ``CheckpointGenerator.maybe_checkpoint()``.
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from mcc_checkpoint import (  # noqa: E402
    AnchorStoreError,
    CheckpointGenerationError,
    anchor_store_from_env,
    checkpoint_generator_from_env,
    load_checkpoint_signing_key,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audit-path", required=True)
    parser.add_argument("--checkpoint-signing-key", default="",
                         help="PEM path; omit for an ephemeral key (dev/test only)")
    parser.add_argument("--checkpoint-signing-key-id", default="")
    parser.add_argument("--decision-token-key-path", default="",
                         help="if set, refuses to start when it matches --checkpoint-signing-key")
    parser.add_argument("--poll-seconds", type=float, default=30.0)
    parser.add_argument("--once", action="store_true",
                         help="check once and exit, instead of polling forever")
    args = parser.parse_args()

    try:
        signing_key = load_checkpoint_signing_key(
            key_path=args.checkpoint_signing_key,
            key_id=args.checkpoint_signing_key_id or "mcc-checkpoint-anchor-key-1",
            forbidden_key_path=args.decision_token_key_path or None,
        )
        store = anchor_store_from_env()
        generator = checkpoint_generator_from_env(
            audit_path=args.audit_path, signing_key=signing_key, anchor_store=store,
        )
    except Exception as exc:  # noqa: BLE001 -- refuse to start on any config error
        print(f"error: {exc}", file=sys.stderr)
        return 2

    def _tick() -> int:
        try:
            checkpoint = generator.maybe_checkpoint()
        except (CheckpointGenerationError, AnchorStoreError) as exc:
            print(f"checkpoint generation failed: {exc}", file=sys.stderr)
            return 1
        if checkpoint:
            print(f"anchored checkpoint: record_count={checkpoint['record_count']} "
                  f"chain_head_hash={checkpoint['chain_head_hash'][:16]}...")
        return 0

    if args.once:
        return _tick()

    while True:
        rc = _tick()
        if rc != 0:
            return rc
        time.sleep(args.poll_seconds)


if __name__ == "__main__":
    sys.exit(main())
