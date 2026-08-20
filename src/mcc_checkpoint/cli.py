"""Operator-facing checkpoint-anchor CLI.

    PYTHONPATH=src python -m mcc_checkpoint verify-anchors \\
        --audit-path audit.jsonl --trusted-key BASE64 \\
        [--anchor-backend memory|git] [--anchor-remote-url URL] \\
        [--anchor-branch NAME] [--anchor-workdir DIR] [--json]

Read-only: recomputes the live audit-chain segments the anchored
checkpoints describe and confirms they still match. It never writes to
the audit log or issues a new checkpoint. Exit codes:

    0  every anchored checkpoint verified (including "zero anchored yet")
    1  AuditAnchorMismatchError -- a mismatch was found (fail-closed)
    2  usage / configuration error
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import List, Optional

from mcc_core.signing import public_key_from_b64

from .errors import AnchorStoreError, AuditAnchorMismatchError
from .store import GitBranchAnchorStore, InMemoryAnchorStore
from .verifier import verify_anchors


def _build_anchor_store(args: argparse.Namespace):
    if args.anchor_backend == "memory":
        return InMemoryAnchorStore()
    if not args.anchor_remote_url or not args.anchor_workdir:
        raise SystemExit(
            "--anchor-backend git requires --anchor-remote-url and --anchor-workdir"
        )
    return GitBranchAnchorStore(
        remote_url=args.anchor_remote_url,
        branch=args.anchor_branch,
        workdir=args.anchor_workdir,
    )


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(prog="mcc_checkpoint", description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)

    v = sub.add_parser("verify-anchors", help="verify every anchored checkpoint against the live audit log")
    v.add_argument("--audit-path", required=True, help="path to the audit.jsonl file")
    v.add_argument("--trusted-key", required=True, metavar="BASE64",
                   help="the trusted Ed25519 public key (base64) checkpoints must be signed with")
    v.add_argument("--anchor-backend", choices=["memory", "git"], default="git")
    v.add_argument("--anchor-remote-url", default="", help="git remote URL (anchor-backend=git)")
    v.add_argument("--anchor-branch", default="audit-checkpoint-anchors")
    v.add_argument("--anchor-workdir", default="", help="local clone dir (anchor-backend=git)")
    v.add_argument("--json", action="store_true", help="machine-readable JSON output")

    args = parser.parse_args(argv)

    if args.cmd == "verify-anchors":
        try:
            public_key = public_key_from_b64(args.trusted_key)
            store = _build_anchor_store(args)
            result = verify_anchors(
                audit_path=args.audit_path, anchor_store=store, trusted_public_key=public_key,
            )
        except AuditAnchorMismatchError as exc:
            if args.json:
                print(json.dumps({"ok": False, "error": "AuditAnchorMismatchError", "detail": str(exc)}, indent=2))
            else:
                print(f"AUDIT ANCHOR MISMATCH: {exc}", file=sys.stderr)
            return 1
        except (AnchorStoreError, ValueError, SystemExit) as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2

        if args.json:
            print(json.dumps(result.to_dict(), indent=2, sort_keys=True))
        else:
            print(f"ok: {result.ok}")
            print(f"checkpoints_verified: {result.checkpoints_verified}")
            print(f"last_verified_record_count: {result.last_verified_record_count}")
            print(f"last_verified_head_hash: {result.last_verified_head_hash}")
            print(f"reason: {result.reason}")
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(main())
