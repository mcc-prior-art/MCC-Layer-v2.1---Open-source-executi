"""Certification CLI.

Public CLI contract requested for this milestone: ``mcc certify <target>``.
No top-level ``mcc`` console-script binary exists anywhere in this
repository today (every existing CLI in this codebase is invoked as
``python -m <package> ...`` -- see ``mcc_conformance/cli.py``,
``mcc_compliance/cli.py``) and the distributed ``mcc-core`` wheel
deliberately ships only a curated, governance-free module subset (see
``pyproject.toml`` / ``setup.py``), excluding ``mcc_conformance`` and
``mcc_evidence`` entirely. Adding a first-ever top-level console-script
entry point, or expanding the curated wheel's contents, is a packaging
decision this PR does not make without explicit approval (CLAUDE.md: "Do
not add dependencies without explicit approval"; this extends to modifying
what the released distribution ships).

The functional CLI contract is instead realized, consistent with this
repository's own established convention, as::

    python -m mcc_certify certify <target> [options]
    python -m mcc_certify verify <run-dir>

Every option name matches the task's requested contract exactly
(``--output``, ``--run-id``, ``--timestamp``, ``--profile``, ``--format``,
``--verify``, ``--force``). Exit codes:

* ``0`` -- CERTIFIED
* ``1`` -- NOT_CERTIFIED (a stage failed; see the printed/JSON result for
  ``failed_stage`` and ``failure_reason``)
* ``2`` -- ERROR (usage error, or an unexpected exception outside the
  pipeline's own fail-closed stage handling)
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .pipeline import CertificationOutcome, CertificationPipeline, CertificationRequest
from .target import known_target_ids
from .verify import RunVerificationError, verify_certification_run

_EXIT = {CertificationOutcome.CERTIFIED: 0, CertificationOutcome.NOT_CERTIFIED: 1}


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m mcc_certify",
        description="MCC End-to-End Certification Pipeline (Evidence Bundle -> "
                    "Certification Manifest -> Technical Certificate -> Offline Verification)",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    certify = sub.add_parser("certify", help=f"certify a target (available: {known_target_ids()})")
    certify.add_argument("target", help="certification target identifier")
    certify.add_argument("--output", default="artifacts/certification", help="output directory (default: artifacts/certification)")
    certify.add_argument("--run-id", default=None, help="explicit run identifier (required for reproducible regeneration)")
    certify.add_argument("--timestamp", default=None, help="explicit RFC3339 issuance timestamp (required for reproducible regeneration)")
    certify.add_argument("--profile", default=None, help="certification profile override (defaults to the target's own declared profile)")
    certify.add_argument("--format", choices=["json"], default=None, help="print the machine-readable certification-result.json to stdout")
    certify.add_argument("--verify", action="store_true",
                          help="accepted for CLI-contract compatibility; offline verification is always performed "
                               "before a successful result is ever reported, and cannot be disabled")
    certify.add_argument("--force", action="store_true", help="overwrite an existing run directory for this target_id/run_id")

    verify = sub.add_parser("verify", help="independently re-verify an existing completed certification run directory")
    verify.add_argument("run_dir", help="path to a completed run directory (contains technical-certificate.json etc.)")
    verify.add_argument("--format", choices=["json"], default=None, help="print the machine-readable verification report to stdout")

    sub.add_parser("list-targets", help="list registered certification targets")

    return parser


def _print_result_human(result) -> None:
    result_dict = result.to_dict()
    print(f"target: {result_dict['target_id']}")
    print(f"profile: {result_dict['certification_profile']}")
    print(f"run_id: {result_dict['run_id']}")
    print(f"outcome: {result_dict['outcome']}")
    for stage in result_dict["stages"]:
        print(f"  [{stage['status']}] {stage['stage']}: {stage['detail']}")
    if result_dict["outcome"] == "CERTIFIED":
        print(f"certificate_id: {result_dict['certificate_id']}")
        print(f"run_dir: {result.run_dir}")
    else:
        print(f"failed_stage: {result_dict['failed_stage']}")
        print(f"failure_reason: {result_dict['failure_reason']}")
        if result.run_dir is not None:
            print(f"failed_run_dir: {result.run_dir}")


def main(argv=None) -> int:
    parser = _build_parser()
    args = parser.parse_args(list(sys.argv[1:] if argv is None else argv))

    if args.command == "list-targets":
        for tid in known_target_ids():
            print(tid)
        return 0

    if args.command == "verify":
        try:
            report = verify_certification_run(Path(args.run_dir))
        except RunVerificationError as e:
            print(f"ERROR: {e}", file=sys.stderr)
            return 2
        if args.format == "json":
            print(json.dumps(report, indent=2, sort_keys=False))
        else:
            print(f"run_dir: {report['run_dir']}")
            print(f"overall_status: {report['overall_status']}")
            print(f"valid: {report['valid']}")
            if report["failures"]:
                print("failures:")
                for f in report["failures"]:
                    print(f"  - {f}")
        return 0 if report["valid"] else 1

    # command == "certify"
    request = CertificationRequest(
        target_id=args.target,
        output_dir=Path(args.output),
        run_id=args.run_id,
        timestamp=args.timestamp,
        profile=args.profile,
        verify=True,
        force=args.force,
    )
    result = CertificationPipeline().run(request)
    result_dict = result.to_dict()

    if args.format == "json":
        print(json.dumps(result_dict, indent=2, sort_keys=False))
    else:
        _print_result_human(result)

    return _EXIT[result.outcome]


if __name__ == "__main__":
    raise SystemExit(main())
