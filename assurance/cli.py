"""``mcc-assurance`` -- the third-party Independent Assurance CLI (PR #71,
Workstream L).

    python -m assurance run --output artifacts/independent-assurance
    python -m assurance run --output OUT --signing-key-pem KEY.pem --signing-key-id KID
    python -m assurance verify --bundle artifacts/independent-assurance --trusted-public-key B64
    python -m assurance list-workstreams

External-target mode (a genuine third party pointing this CLI at their OWN
already-running deployment, per ``THIRD_PARTY_RUNBOOK.md``) is selected by
setting ``MCC_ASSURANCE_EXTERNAL=1`` plus the ``MCC_ASSURANCE_*`` variables
consumed by ``assurance/tests/conftest.py`` -- never by a CLI flag, so
secrets and key paths never appear in shell history or process listings.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import List, Optional

from assurance.evidence import build_evidence_bundle, verify_evidence_bundle
from assurance.runner import REPO_ROOT, WORKSTREAM_LABELS, discover_test_modules, run_all


def _cmd_list_workstreams(_args: argparse.Namespace) -> int:
    modules = discover_test_modules()
    present = {m.name for m in modules}
    rows = sorted(WORKSTREAM_LABELS.items(), key=lambda kv: kv[1])
    for filename, label in rows:
        marker = "present" if filename in present else "not yet implemented"
        print(f"{label:<16} {filename:<45} {marker}")
    extra = present - set(WORKSTREAM_LABELS)
    for filename in sorted(extra):
        print(f"{filename:<16} {filename:<45} present")
    return 0


def _cmd_run(args: argparse.Namespace) -> int:
    output_dir = Path(args.output)
    report = run_all()

    signing_key = None
    if args.signing_key_pem:
        from mcc_core.signing import SigningKey

        if not args.signing_key_id:
            print("error: --signing-key-id is required with --signing-key-pem", file=sys.stderr)
            return 2
        signing_key = SigningKey.from_pem_file(args.signing_key_pem, args.signing_key_id)

    manifest = build_evidence_bundle(
        output_dir=output_dir, run_report=report.to_dict(), repo_root=REPO_ROOT,
        signing_key=signing_key,
    )

    summary = report.summary
    print(json.dumps(summary, indent=2, sort_keys=True))
    print(f"evidence bundle written to {output_dir} (schema {manifest['schema_version']})")

    if summary["modules_run"] == 0:
        print(
            "warning: no workstream test modules were discovered -- this run proves nothing "
            "yet (only the workstreams that exist under assurance/tests/ were executed)",
            file=sys.stderr,
        )
    return 1 if summary["overall_status"] != "PASS" else 0


def _cmd_verify(args: argparse.Namespace) -> int:
    result = verify_evidence_bundle(
        Path(args.bundle), trusted_public_keys_b64=args.trusted_public_key or [],
    )
    print(json.dumps(result.to_dict(), indent=2, sort_keys=True))
    if result.overall_status == "INVALID":
        return 2
    if result.overall_status == "INTACT_UNTRUSTED_SIGNER":
        return 1
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="mcc-assurance", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    p_run = sub.add_parser("run", help="Run every discovered workstream test module and write an evidence bundle.")
    p_run.add_argument("--output", required=True, help="Directory to write the evidence bundle into.")
    p_run.add_argument("--signing-key-pem", default=None, help="Optional Ed25519 PEM to sign the bundle's findings manifest.")
    p_run.add_argument("--signing-key-id", default=None, help="Key ID for --signing-key-pem (required if that flag is set).")
    p_run.set_defaults(func=_cmd_run)

    p_verify = sub.add_parser("verify", help="Offline-verify a previously produced evidence bundle.")
    p_verify.add_argument("--bundle", required=True, help="Path to a bundle directory produced by 'run'.")
    p_verify.add_argument("--trusted-public-key", action="append", default=None,
                           help="Base64 Ed25519 public key to trust (repeatable).")
    p_verify.set_defaults(func=_cmd_verify)

    p_list = sub.add_parser("list-workstreams", help="List known workstreams and whether their tests exist yet.")
    p_list.set_defaults(func=_cmd_list_workstreams)

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
