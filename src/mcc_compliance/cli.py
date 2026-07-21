"""Certification CLI: ``python -m mcc_compliance certify ...``.

Deterministic, offline, fail-closed. Exit codes:

* ``0`` — CERTIFIED
* ``1`` — NOT_CERTIFIED
* ``2`` — ERROR (suite/adapter/manifest error, or unknown adapter/version)
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import List, Optional

from .models import CertificationStatus, ComplianceError
from .registry import available_adapters, load_adapter
from .reporting import certification_manifest, report_to_json, write_reports
from .runner import ComplianceReport, run_compliance

# Importing the adapters module registers the built-in adapters.
from . import adapters as _adapters  # noqa: F401

_EXIT = {
    CertificationStatus.CERTIFIED: 0,
    CertificationStatus.NOT_CERTIFIED: 1,
    CertificationStatus.ERROR: 2,
}


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m mcc_compliance",
        description="MCC-Core Integration Contract compliance & certification suite")
    sub = parser.add_subparsers(dest="command", required=True)

    certify = sub.add_parser("certify", help="certify an adapter against a contract version")
    certify.add_argument("--adapter", required=True,
                         help=f"adapter to certify (available: {available_adapters()})")
    certify.add_argument("--contract-version", required=True,
                         help="Integration Contract version, e.g. 1.0")
    certify.add_argument("--output-dir", default=None,
                         help="write report.json / report.md / certification.json here")
    certify.add_argument("--json", action="store_true",
                         help="print the full JSON report to stdout")

    sub.add_parser("list-adapters", help="list registered adapters")
    return parser


def _normalize_version(v: str) -> str:
    # Accept "1" as a convenience for "1.0"; the runner still fails closed on
    # anything genuinely unsupported.
    return "1.0" if v.strip() == "1" else v.strip()


def main(argv: Optional[List[str]] = None) -> int:
    args = _build_parser().parse_args(argv)

    if args.command == "list-adapters":
        for name in available_adapters():
            print(name)
        return 0

    # certify
    try:
        adapter = load_adapter(args.adapter)
    except ComplianceError as exc:
        print(f"ERROR: {exc.code.value}: {exc.message}", file=sys.stderr)
        return 2

    contract_version = _normalize_version(args.contract_version)
    report = run_compliance(adapter, contract_version)

    if args.json:
        print(json.dumps(report_to_json(report), indent=2, sort_keys=True))
    else:
        _print_summary(report)

    if args.output_dir:
        paths = write_reports(report, args.output_dir)
        if not args.json:
            print(f"\nwrote: {paths['json']}\n       {paths['markdown']}\n"
                  f"       {paths['certification']}")

    return _EXIT[report.certification.status]


def _print_summary(report: "ComplianceReport") -> None:
    cert = certification_manifest(report)
    t = report.totals
    print(f"Adapter          : {cert['adapter_name']} v{cert['adapter_version']}")
    print(f"Framework        : {cert['target_framework'] or '-'}")
    print(f"Contract version : {report.contract_version} "
          f"(claimed {cert['claimed_contract_version']})")
    print(f"Suite version    : {cert['compliance_suite_version']}")
    print(f"Vectors          : {t.total} total | {t.passed} passed | {t.failed} failed "
          f"| {t.errored} errored | {t.skipped} skipped")
    print(f"Mandatory        : {t.mandatory_passed}/{t.mandatory_total} passed")
    print(f"Manifest digest  : {report.vector_manifest_digest or '-'}")
    print(f"Fingerprint      : {cert['certification_fingerprint']}")
    print(f"STATUS           : {cert['certification_status']}")
    for reason in report.certification.reasons:
        print(f"  - {reason}")


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
