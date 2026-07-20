"""Operator-facing offline verification CLI for Governance Evidence Bundles.

    PYTHONPATH=src python -m mcc_evidence verify <bundle> [--trusted-key kid=BASE64 ...] [--json]

Read-only: it verifies a bundle and reports a structured result. It cannot
execute, authorize, mutate the bundle, or reach the network. Exit codes preserve
the trusted/untrusted distinction:

    0  VERIFIED (trusted executable evidence) or DENIAL_VERIFIED (trusted denial)
    1  INTACT_UNTRUSTED_SIGNER (structurally intact, signer NOT trusted)
    2  INVALID (a blocking failure was found)
    3  UNSUPPORTED_SCHEMA
    4  usage / unreadable bundle
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Dict, List, Optional

from .schema import EvidenceStatus, VerificationResult
from .verify import verify_bundle

_EXIT = {
    EvidenceStatus.VERIFIED: 0,
    EvidenceStatus.DENIAL_VERIFIED: 0,
    EvidenceStatus.INTACT_UNTRUSTED_SIGNER: 1,
    EvidenceStatus.INVALID: 2,
    EvidenceStatus.UNSUPPORTED_SCHEMA: 3,
}


def _parse_keys(pairs: Optional[List[str]]) -> Dict[str, str]:
    keys: Dict[str, str] = {}
    for p in pairs or []:
        if "=" not in p:
            raise SystemExit(f"--trusted-key must be kid=BASE64, got {p!r}")
        kid, b64 = p.split("=", 1)
        keys[kid.strip()] = b64.strip()
    return keys


def _human(result: 'VerificationResult') -> str:
    lines = [
        f"bundle:   {result.bundle_id}",
        f"decision: {result.decision_id}  outcome={result.outcome}",
        f"overall:  {result.overall_status.value}  (trusted={result.trusted})",
        "dimensions:",
        f"  integrity_valid            = {result.integrity_valid}",
        f"  audit_chain_valid          = {result.audit_chain_valid} (present={result.audit_present})",
        f"  signer_verified            = {result.signer_verified}",
        f"  signer_trusted             = {result.signer_trusted}",
        f"  authority_evidence_verified= {result.authority_evidence_verified}",
        "checks:",
    ]
    for c in result.checks:
        lines.append(f"  [{c.status.value:4}] {c.name}: {c.detail}")
    for w in result.warnings:
        lines.append(f"  ! warning: {w}")
    for f in result.failures:
        lines.append(f"  x FAIL:    {f}")
    return "\n".join(lines)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(prog="mcc_evidence", description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)
    v = sub.add_parser("verify", help="verify an evidence bundle offline")
    v.add_argument("bundle", help="path to a bundle directory or .tar.gz")
    v.add_argument("--trusted-key", action="append", metavar="kid=BASE64",
                   help="a trusted issuer Ed25519 public key (repeatable)")
    v.add_argument("--json", action="store_true", help="machine-readable JSON output")
    args = parser.parse_args(argv)

    if args.cmd == "verify":
        result = verify_bundle(args.bundle, trusted_keys=_parse_keys(args.trusted_key))
        if args.json:
            print(json.dumps(result.to_dict(), indent=2, sort_keys=True))
        else:
            print(_human(result))
        return _EXIT.get(result.overall_status, 2)
    return 4


if __name__ == "__main__":
    sys.exit(main())
