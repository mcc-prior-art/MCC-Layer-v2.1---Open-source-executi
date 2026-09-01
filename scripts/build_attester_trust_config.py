#!/usr/bin/env python3
"""Build/extend a gateway ``MCC_ATTESTATION_TRUST_CONFIG`` entry for an
Independent Attester Service (PR-4).

Takes ONLY public material on the command line -- an attester_id, a kid,
a base64-encoded Ed25519 PUBLIC key, and the evidence_type(s) that
attester is trusted to assert. This script has no code path that reads,
accepts, or handles a private key: it exists specifically to make the
gateway/Attester trust hand-off a public-key-only operation, matching the
design boundary "the MCC gateway/runtime must require only the Attester
PUBLIC key" (PR-4 design rule 1).

The Attester's own PRIVATE key is generated and kept entirely on the
Attester side, with the existing ``scripts/generate_signing_key.py``
(unchanged -- no new key-generation logic needed for PR-4). That script
already prints the base64 public key; paste that value into this script's
``--public-key-b64`` argument, run this script on (or for) the gateway
side, and point ``MCC_ATTESTATION_TRUST_CONFIG`` at the JSON file it
writes. The gateway process that loads that file never sees, and never
needs, the Attester's private key.

Usage::

    python scripts/build_attester_trust_config.py \\
        --attester-id attester.payment-risk.v1 \\
        --kid attester.payment-risk.v1-key-01 \\
        --public-key-b64 <output of generate_signing_key.py> \\
        --evidence-type risk_assessment \\
        --out config/attestation_trust.generated.json

Re-running with the same ``--out`` and a new ``--kid`` appends a second
trust anchor (key rotation: add the new key, then remove the old entry
once rotation is complete) rather than overwriting existing entries for a
different kid.
"""

from __future__ import annotations

import argparse
import base64
import json
import sys
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey


def _validate_public_key_b64(value: str) -> str:
    """Fail closed on a malformed/wrong-length value before writing it into
    a trust config a gateway might load -- never write an unusable or
    ambiguous entry."""
    try:
        raw = base64.b64decode(value, validate=True)
        Ed25519PublicKey.from_public_bytes(raw)
    except Exception as exc:  # noqa: BLE001
        raise SystemExit(f"--public-key-b64 is not a valid Ed25519 public key: {exc}")
    return value


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--attester-id", required=True)
    parser.add_argument("--kid", required=True)
    parser.add_argument("--public-key-b64", required=True)
    parser.add_argument(
        "--evidence-type", action="append", required=True, dest="evidence_types",
        help="repeatable; the evidence_type(s) this attester is trusted to assert",
    )
    parser.add_argument("--out", required=True, help="path to write/extend")
    args = parser.parse_args()

    public_key_b64 = _validate_public_key_b64(args.public_key_b64)

    out_path = Path(args.out)
    entries = []
    if out_path.exists():
        entries = json.loads(out_path.read_text(encoding="utf-8"))
        if not isinstance(entries, list):
            raise SystemExit(f"{out_path} does not contain a JSON array; refusing to overwrite")

    for existing in entries:
        if existing.get("attester_id") == args.attester_id and existing.get("kid") == args.kid:
            raise SystemExit(
                f"an entry for attester_id={args.attester_id!r} kid={args.kid!r} "
                f"already exists in {out_path}; refusing to silently duplicate/overwrite it"
            )

    entries.append({
        "attester_id": args.attester_id,
        "kid": args.kid,
        "public_key_b64": public_key_b64,
        "evidence_types": args.evidence_types,
    })

    out_path.write_text(json.dumps(entries, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {len(entries)} trust anchor(s) to {out_path}")


if __name__ == "__main__":
    main()
