#!/usr/bin/env python3
"""Generate the REAL production Issuer identity for MCC Official
Certification (PR #70).

This is OPERATOR TOOLING, run manually, OFFLINE, by an authorized human --
never by CI, never automatically, never as part of any pull-request or
protected-workflow run. Nothing in this repository invokes this script for
you: it is the one place a real production Ed25519 key pair is ever
generated for this purpose, and it exists precisely so that generation
happens outside CI and outside any automated process.

What it does:
  1. Generates a fresh Ed25519 key pair (or loads an existing PEM you
     already hold, via --existing-key, e.g. for key rotation/continuity).
  2. Writes the PRIVATE key to a local file, mode 0600. This file is
     NEVER printed, NEVER committed, and this script never uploads it
     anywhere. YOU are responsible for storing it securely (e.g. as the
     GitHub Environment secret MCC_PRODUCTION_ISSUER_PRIVATE_KEY_B64 --
     see docs/certification/OFFICIAL_SIGNING_CEREMONY.md) and for deleting
     any local copy you don't need to retain.
  3. Builds and writes the PUBLIC Issuer Identity document and a Trust
     Store containing it (config/official-issuer.json /
     config/official-trust-store.json by default) -- this is public
     material, safe to commit and safe to publish.
  4. Prints the public-key fingerprint for independent, out-of-band
     verification (see docs/certification/OFFICIAL_SIGNING_CEREMONY.md,
     "Verify the fingerprint before the first ceremony").

Usage:
    python scripts/generate_production_issuer_identity.py \\
        --private-key-out /secure/path/mcc-official-issuer-key.pem \\
        --issuer-config-out config/official-issuer.json \\
        --trust-store-out config/official-trust-store.json \\
        --valid-from 2026-08-01T00:00:00Z

    # Rotation: reuse an existing key, only regenerate the public documents
    python scripts/generate_production_issuer_identity.py \\
        --existing-key /secure/path/mcc-official-issuer-key.pem \\
        --key-id prod-key-2 --valid-from 2027-01-01T00:00:00Z
"""

from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from cryptography.hazmat.primitives import serialization  # noqa: E402
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey  # noqa: E402
from mcc_core.signing import SigningKey  # noqa: E402
from mcc_certify.issuer import build_issuer_identity, public_key_fingerprint, write_issuer_identity  # noqa: E402
from mcc_certify.trust_store import build_trust_store, write_trust_store  # noqa: E402

#: Stable production issuer identity -- reused everywhere PR #70's
#: official-eligibility gate checks issuer identity (mcc_certify.official).
PRODUCTION_ISSUER_ID = "mcc-official-certification-issuer-v1"
PRODUCTION_ISSUER_DISPLAY_NAME = "AXLOGIQ MCC Official Certification Issuer v1"


def _parse_rfc3339(value: str) -> int:
    normalized = value.strip()
    if normalized.endswith("Z"):
        normalized = normalized[:-1] + "+00:00"
    dt = datetime.fromisoformat(normalized)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return int(dt.timestamp())


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--private-key-out", default=None,
                         help="where to write a FRESH private key (mode 0600). Mutually exclusive with --existing-key.")
    parser.add_argument("--existing-key", default=None,
                         help="path to an EXISTING private key PEM to reuse (rotation/continuity). "
                              "Mutually exclusive with --private-key-out.")
    parser.add_argument("--key-id", default="prod-key-1", help="Trust Anchor key id for this key (default: prod-key-1)")
    parser.add_argument("--issuer-config-out", default="config/official-issuer.json")
    parser.add_argument("--trust-store-out", default="config/official-trust-store.json")
    parser.add_argument("--valid-from", required=True, help="RFC3339 timestamp this key becomes valid")
    parser.add_argument("--valid-until", default=None, help="RFC3339 timestamp this key stops being valid (optional)")
    args = parser.parse_args(argv)

    if bool(args.private_key_out) == bool(args.existing_key):
        parser.error("exactly one of --private-key-out or --existing-key is required")

    if args.existing_key:
        signing_key = SigningKey.from_pem_file(args.existing_key, kid=args.key_id)
        print(f"loaded existing private key from {args.existing_key} (NOT modified, NOT printed)")
    else:
        out_path = Path(args.private_key_out)
        if out_path.exists():
            print(f"STOP: refusing to overwrite existing file: {out_path}", file=sys.stderr)
            return 1
        private_key = Ed25519PrivateKey.generate()
        pem = private_key.private_bytes(
            serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption(),
        )
        fd = os.open(str(out_path), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "wb") as fh:
            fh.write(pem)
        signing_key = SigningKey(private_key, args.key_id)
        print(f"written: {out_path} (mode 0600) -- KEEP THIS FILE SECRET. Store it as the GitHub Environment "
              "secret MCC_PRODUCTION_ISSUER_PRIVATE_KEY_B64 (base64-encoded) and then delete or secure this "
              "local copy. This script never prints or uploads it.")

    valid_from = _parse_rfc3339(args.valid_from)
    valid_until = _parse_rfc3339(args.valid_until) if args.valid_until else None

    issuer = build_issuer_identity(
        issuer_id=PRODUCTION_ISSUER_ID,
        display_name=PRODUCTION_ISSUER_DISPLAY_NAME,
        key_id=args.key_id,
        public_key=signing_key.public_key(),
        valid_from=valid_from,
        created_at=valid_from,
        valid_until=valid_until,
    )
    write_issuer_identity(issuer, args.issuer_config_out)
    write_trust_store(build_trust_store((issuer,)), args.trust_store_out)

    fingerprint = public_key_fingerprint(signing_key.public_key())
    print(f"issuer.json written to {args.issuer_config_out} (public material -- safe to commit)")
    print(f"trust-store.json written to {args.trust_store_out} (public material -- safe to commit)")
    print(f"issuer_id: {PRODUCTION_ISSUER_ID}")
    print(f"key_id: {args.key_id}")
    print(f"PUBLIC KEY FINGERPRINT (verify this independently before the first ceremony): {fingerprint}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
