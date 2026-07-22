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
from pathlib import Path
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

    # Adapter-SDK certification ingress (PR #51) — the canonical certification path.
    cs = sub.add_parser("certify-sdk",
                        help="certify the reference Adapter-SDK adapter (SDK ingress)")
    cs.add_argument("--contract-version", required=True, help="e.g. 1.0")
    cs.add_argument("--output-dir", default=None,
                    help="write certification.json / evidence.json / certification-report.md here")
    cs.add_argument("--json", action="store_true", help="print the certification JSON to stdout")

    # Certified Adapter Program (PR #46).
    bm = sub.add_parser("build-manifest",
                        help="regenerate the repository certification manifest from real evidence")
    bm.add_argument("--contract-version", required=True, help="e.g. 1.0")

    vm = sub.add_parser("verify-manifest",
                        help="verify the committed manifest against freshly regenerated evidence")
    vm.add_argument("--contract-version", default=None,
                    help="override the manifest's own contract_version")

    # Governance Capability Profile (PR #47).
    vc = sub.add_parser("validate-capabilities",
                        help="schema + semantic validation of a Governance Capability Profile")
    vc.add_argument("profile", help="path to a capability profile JSON file")
    vc.add_argument("--json", action="store_true", help="print the structured result as JSON")
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

    if args.command == "build-manifest":
        from .program import MANIFEST_PATH, write_manifest
        try:
            manifest = write_manifest(contract_version=_normalize_version(args.contract_version))
        except ComplianceError as exc:
            print(f"ERROR: {exc.code.value}: {exc.message}", file=sys.stderr)
            return 2
        n = len(manifest["certifications"])
        print(f"wrote {MANIFEST_PATH} ({n} certified adapter(s))")
        for e in manifest["certifications"]:
            print(f"  - {e['adapter_key']}: {e['adapter']} v{e['adapter_version']} "
                  f"[{e['status']}] {e['evidence_digest']}")
        return 0

    if args.command == "verify-manifest":
        from .program import verify_manifest
        try:
            res = verify_manifest(
                contract_version=(_normalize_version(args.contract_version)
                                  if args.contract_version else None))
        except ComplianceError as exc:
            print(f"ERROR: {exc.code.value}: {exc.message}", file=sys.stderr)
            return 2
        if res.ok:
            print("MANIFEST OK: committed certifications match regenerated evidence")
            return 0
        print("MANIFEST MISMATCH:", file=sys.stderr)
        for d in res.differences:
            print(f"  - {d}", file=sys.stderr)
        return 1

    if args.command == "validate-capabilities":
        from .capability_profile import validate_profile
        try:
            profile = json.loads(Path(args.profile).read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            print(f"ERROR: could not read profile: {exc}", file=sys.stderr)
            return 2
        result = validate_profile(profile)
        if args.json:
            print(json.dumps(result.to_dict(), indent=2, sort_keys=True))
        elif result.valid:
            print("VALID: capability profile is well-formed and consistent")
            print(f"  profile digest: {result.digest}")
        else:
            print("INVALID: capability profile rejected", file=sys.stderr)
            for e in result.errors:
                print(f"  - {e.code.value}: {e.message}", file=sys.stderr)
        return 0 if result.valid else 1

    if args.command == "certify-sdk":
        from .program import ProgramStatus
        from .sdk_certification import (
            certification_document,
            run_sdk_certification,
            write_certification,
        )
        from .sdk_reference_adapter import SdkReferenceAdapter
        contract_version = _normalize_version(args.contract_version)
        try:
            result, _ = run_sdk_certification(SdkReferenceAdapter(),
                                              contract_version=contract_version)
        except ComplianceError as exc:
            print(f"ERROR: {exc.code.value}: {exc.message}", file=sys.stderr)
            return 2
        if args.json:
            print(json.dumps(certification_document(result), indent=2, sort_keys=True))
        else:
            print(f"Adapter          : {result.adapter_name} v{result.adapter_version}")
            print(f"Ingress          : adapter-sdk")
            print(f"Contract version : {result.contract_version}")
            print(f"Vectors          : {result.scenarios_total} total | "
                  f"{result.scenarios_passed} passed | {result.scenarios_failed} failed")
            print(f"Evidence digest  : {result.evidence_digest}")
            print(f"STATUS           : {result.status.value}")
        if args.output_dir:
            paths = write_certification(SdkReferenceAdapter(),
                                        contract_version=contract_version,
                                        out_dir=args.output_dir)
            if not args.json:
                print(f"\nwrote: {paths['certification']}\n       {paths['evidence']}\n"
                      f"       {paths['report']}")
        return 0 if result.status is ProgramStatus.CERTIFIED else 1

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
