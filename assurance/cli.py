"""``mcc-assurance`` -- the third-party Independent Assurance CLI (PR #71,
Workstream L).

    python -m assurance run --output artifacts/independent-assurance
    python -m assurance run --output OUT --signing-key-pem KEY.pem --signing-key-id KID
    python -m assurance verify --bundle artifacts/independent-assurance --trusted-public-key B64
    python -m assurance list-workstreams

External-target mode (a genuine third party pointing this CLI at their OWN
already-running deployment, per ``THIRD_PARTY_RUNBOOK.md``) is selected two
ways, both ultimately setting the same ``MCC_ASSURANCE_*`` environment
variables ``assurance/tests/conftest.py`` reads:

1. Directly: ``MCC_ASSURANCE_EXTERNAL=1`` plus the ``MCC_ASSURANCE_*``
   variables, set before invoking this CLI (never a flag -- the original,
   still-supported path).
2. ``run --target <gateway-base-url> --actuator <actuator-base-url>
   --notify <notify-base-url> --external-config <config.json>``: the
   NON-secret target URLs are ordinary flags; every secret and key-file
   path (API keys, policy hashes, evaluator key-file paths) stays in
   ``--external-config`` (never shell history or a process listing) --
   see ``examples/assurance_external_config.example.json``. This mode
   internally sets the exact same environment variables mode 1 does; it
   is a convenience wrapper over the same mechanism, not a second one.
"""

from __future__ import annotations

import argparse
import json
import os
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


_EXTERNAL_CONFIG_REQUIRED_KEYS = (
    "api_key", "operator_key", "actuator_api_key", "policy_hash",
    "evaluator_keys_path", "actuator_evaluator_keys_path",
)


def _apply_external_target(args: argparse.Namespace) -> Optional[str]:
    """Translate --target/--actuator/--notify/--external-config into the
    MCC_ASSURANCE_* environment variables assurance/tests/conftest.py
    reads, exactly as if the operator had set them directly (mode 1 in
    this module's docstring) -- no new authorization mechanism, just a
    friendlier interface over the same one. Returns an error string, or
    None on success."""
    if args.target is None and args.actuator is None:
        return None
    if args.target is None or args.actuator is None:
        return "--target and --actuator must be supplied together"
    if not args.notify:
        return "--notify is required with --target/--actuator (the external-effect sink URL)"
    if not args.external_config:
        return "--external-config is required with --target/--actuator (API keys, policy hashes, evaluator key paths)"

    try:
        config = json.loads(Path(args.external_config).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return f"--external-config could not be read/parsed: {exc}"
    missing = [k for k in _EXTERNAL_CONFIG_REQUIRED_KEYS if k not in config]
    if missing:
        return f"--external-config is missing required keys: {', '.join(missing)}"

    os.environ["MCC_ASSURANCE_EXTERNAL"] = "1"
    os.environ["MCC_ASSURANCE_GATEWAY_URL"] = args.target
    os.environ["MCC_ASSURANCE_ACTUATOR_URL"] = args.actuator
    os.environ["MCC_ASSURANCE_NOTIFY_URL"] = args.notify
    os.environ["MCC_ASSURANCE_API_KEY"] = config["api_key"]
    os.environ["MCC_ASSURANCE_OPERATOR_KEY"] = config["operator_key"]
    os.environ["MCC_ASSURANCE_ACTUATOR_API_KEY"] = config["actuator_api_key"]
    os.environ["MCC_ASSURANCE_POLICY_HASH"] = config["policy_hash"]
    os.environ["MCC_ASSURANCE_ACTUATOR_POLICY_HASH"] = config.get("actuator_policy_hash", "")
    os.environ["MCC_ASSURANCE_EVALUATOR_KEYS_PATH"] = config["evaluator_keys_path"]
    os.environ["MCC_ASSURANCE_ACTUATOR_EVALUATOR_KEYS_PATH"] = config["actuator_evaluator_keys_path"]
    if config.get("gateway_notify_url"):
        os.environ["MCC_ASSURANCE_GATEWAY_NOTIFY_URL"] = config["gateway_notify_url"]
    return None


def _cmd_run(args: argparse.Namespace) -> int:
    error = _apply_external_target(args)
    if error is not None:
        print(f"error: {error}", file=sys.stderr)
        return 2

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
    p_run.add_argument("--target", default=None, metavar="GATEWAY_BASE_URL",
                        help="External mode: base URL of an already-running, third-party-operated Gateway "
                             "(requires --actuator, --notify, --external-config). Omit for self-contained mode.")
    p_run.add_argument("--actuator", default=None, metavar="ACTUATOR_BASE_URL",
                        help="External mode: base URL of the third party's protected actuator.")
    p_run.add_argument("--notify", default=None, metavar="NOTIFY_BASE_URL",
                        help="External mode: base URL of the third party's external-effect sink.")
    p_run.add_argument("--external-config", default=None, metavar="CONFIG_JSON",
                        help="External mode: path to a JSON file holding API keys, policy hashes, and "
                             "evaluator key-file paths -- see examples/assurance_external_config.example.json. "
                             "Never passed as flags, so secrets never appear in shell history.")
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
