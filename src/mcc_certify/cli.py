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

from .issuer import IssuerIdentityError, read_issuer_identity
from .pipeline import CertificationOutcome, CertificationPipeline, CertificationRequest
from .signing_provider import LocalFileSigningKeyProvider, SigningKeyProviderError
from .target import CertifyError, known_target_ids
from .trust_store import TrustStoreError, read_trust_store
from .verify import RunVerificationError, verify_certification_run, verify_certification_run_trusted

_EXIT = {CertificationOutcome.CERTIFIED: 0, CertificationOutcome.NOT_CERTIFIED: 1}

_OFFICIAL_MODE_FLAGS = ("issuer_config", "signing_key", "trust_store", "publication_dir")


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
    certify.add_argument("--issuer-config", default=None,
                          help="path to an Issuer Identity JSON document (PR #68). Supplying ANY of "
                               "--issuer-config/--signing-key/--trust-store/--publication-dir enables OFFICIAL "
                               "mode and then REQUIRES all four -- there is no partial official configuration "
                               "and no silent fallback to the fixture signing path.")
    certify.add_argument("--signing-key", default=None,
                          help="path to the Issuer's private key PEM file (official mode). Never committed to "
                               "this repository, never written into any generated artifact.")
    certify.add_argument("--trust-store", default=None,
                          help="path to a Trust Store JSON document (official mode) -- the explicit trust-anchor "
                               "set the final offline verification gate checks the freshly-issued certificate "
                               "against before certification is ever reported as successful.")
    certify.add_argument("--publication-dir", default=None,
                          help="directory for the Publication Record/Index (official mode); never mutated "
                               "until every other stage, including final offline verification, has passed.")

    verify = sub.add_parser("verify", help="independently re-verify an existing completed certification run directory")
    verify.add_argument("run_dir", help="path to a completed run directory (contains technical-certificate.json etc.)")
    verify.add_argument("--format", choices=["json"], default=None, help="print the machine-readable verification report to stdout")
    verify.add_argument("--trust-store", default=None,
                         help="path to a Trust Store JSON document. When supplied, verification checks the "
                              "certificate against THIS explicit trust-anchor set (PR #68) instead of the "
                              "reference pipeline's internal, self-consistency-only fixture check.")
    verify.add_argument("--publication-index", default=None,
                         help="path to a publication-index.json to additionally check that the certificate is "
                              "present in the published set (requires --trust-store).")
    verify.add_argument("--require-published", action="store_true",
                         help="fail verification unless the certificate is present in --publication-index "
                              "(requires --trust-store and --publication-index).")

    sub.add_parser("list-targets", help="list registered certification targets")

    aggregate = sub.add_parser(
        "aggregate-publish",
        help="build the all-or-nothing aggregate five-ecosystem Publication Index (PR #69) from five "
             "already-completed official certification run directories",
    )
    aggregate.add_argument(
        "--run", action="append", required=True, metavar="TARGET_ID=RUN_DIR", dest="runs",
        help="repeatable; exactly one per required ecosystem target id, e.g. "
             "--run generic-http=artifacts/certification/generic-http/run1",
    )
    aggregate.add_argument("--trust-store", required=True, help="path to the Trust Store JSON document")
    aggregate.add_argument("--publication-dir", required=True, help="directory to write the aggregate publication-index.json into")
    aggregate.add_argument("--format", choices=["json"], default=None)

    verify_aggregate = sub.add_parser(
        "verify-aggregate",
        help="independently re-verify an already-built aggregate five-ecosystem Publication Index",
    )
    verify_aggregate.add_argument("--publication-dir", required=True, help="directory containing the aggregate publication-index.json")
    verify_aggregate.add_argument(
        "--run", action="append", required=True, metavar="TARGET_ID=RUN_DIR", dest="runs",
        help="repeatable; exactly one per required ecosystem target id",
    )
    verify_aggregate.add_argument("--trust-store", required=True, help="path to the Trust Store JSON document")
    verify_aggregate.add_argument("--format", choices=["json"], default=None)

    return parser


def _parse_run_map(raw_runs) -> "dict[str, Path]":
    runs: "dict[str, Path]" = {}
    for entry in raw_runs:
        if "=" not in entry:
            raise CertifyError(f"--run must be TARGET_ID=RUN_DIR, got {entry!r}")
        target_id, _, run_dir = entry.partition("=")
        if not target_id or not run_dir:
            raise CertifyError(f"--run must be TARGET_ID=RUN_DIR, got {entry!r}")
        if target_id in runs:
            raise CertifyError(f"--run supplied more than once for target_id {target_id!r}")
        runs[target_id] = Path(run_dir)
    return runs


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

    if args.command == "aggregate-publish":
        from .aggregate import AggregatePublicationError, build_five_ecosystem_publication_set

        try:
            run_map = _parse_run_map(args.runs)
            trust_store = read_trust_store(args.trust_store)
        except (CertifyError, TrustStoreError) as e:
            print(f"ERROR: {e}", file=sys.stderr)
            return 2
        try:
            index, outcomes = build_five_ecosystem_publication_set(
                run_map, trust_store=trust_store, aggregate_publication_dir=Path(args.publication_dir),
            )
        except AggregatePublicationError as e:
            print(f"NOT_PUBLISHED: {e}", file=sys.stderr)
            return 1
        payload = {
            "outcome": "PUBLISHED", "record_count": len(index.records),
            "certificate_ids": [r.certificate_id for r in index.records],
            "target_ids": sorted(r.target_id for r in index.records),
        }
        if args.format == "json":
            print(json.dumps(payload, indent=2))
        else:
            print("outcome: PUBLISHED")
            print(f"record_count: {payload['record_count']}")
            for tid, cid in zip(payload["target_ids"], sorted(payload["certificate_ids"])):
                print(f"  {tid}")
        return 0

    if args.command == "verify-aggregate":
        from .aggregate import verify_aggregate_publication_set

        try:
            run_map = _parse_run_map(args.runs)
            trust_store = read_trust_store(args.trust_store)
        except (CertifyError, TrustStoreError) as e:
            print(f"ERROR: {e}", file=sys.stderr)
            return 2
        valid, failures = verify_aggregate_publication_set(
            Path(args.publication_dir), trust_store=trust_store, run_dirs=run_map,
        )
        payload = {"valid": valid, "failures": failures}
        if args.format == "json":
            print(json.dumps(payload, indent=2))
        else:
            print(f"valid: {valid}")
            for f in failures:
                print(f"  - {f}")
        return 0 if valid else 1

    if args.command == "verify":
        if args.require_published and not (args.trust_store and args.publication_index):
            print("ERROR: --require-published requires both --trust-store and --publication-index", file=sys.stderr)
            return 2
        if args.publication_index and not args.trust_store:
            print("ERROR: --publication-index requires --trust-store", file=sys.stderr)
            return 2
        try:
            if args.trust_store:
                report = verify_certification_run_trusted(
                    Path(args.run_dir),
                    trust_store=Path(args.trust_store),
                    publication_index=Path(args.publication_index) if args.publication_index else None,
                    require_published=args.require_published,
                )
            else:
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
    official_flag_values = {name: getattr(args, name.replace("-", "_")) for name in _OFFICIAL_MODE_FLAGS}
    supplied = {name: value for name, value in official_flag_values.items() if value is not None}
    official_mode = bool(supplied)
    if official_mode and len(supplied) != len(_OFFICIAL_MODE_FLAGS):
        missing = sorted(set(_OFFICIAL_MODE_FLAGS) - set(supplied))
        print(
            "ERROR: official mode requires --issuer-config, --signing-key, --trust-store, and "
            f"--publication-dir together; missing: {[m.replace('_', '-') for m in missing]}",
            file=sys.stderr,
        )
        return 2

    issuer_identity = None
    signing_key_provider = None
    trust_store = None
    publication_dir = None
    if official_mode:
        try:
            issuer_identity = read_issuer_identity(args.issuer_config)
            trust_store = read_trust_store(args.trust_store)
            signing_key_provider = LocalFileSigningKeyProvider(args.signing_key, issuer_identity)
        except (IssuerIdentityError, TrustStoreError, SigningKeyProviderError, CertifyError) as e:
            print(f"ERROR: {e}", file=sys.stderr)
            return 2
        publication_dir = Path(args.publication_dir)

    request = CertificationRequest(
        target_id=args.target,
        output_dir=Path(args.output),
        run_id=args.run_id,
        timestamp=args.timestamp,
        profile=args.profile,
        verify=True,
        force=args.force,
        official_mode=official_mode,
        issuer_identity=issuer_identity,
        signing_key_provider=signing_key_provider,
        trust_store=trust_store,
        publication_dir=publication_dir,
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
