#!/usr/bin/env python3
"""Generate the evaluator keyset for the VoltAgent governed-integration stack.

Writes into an output directory (git-ignored, e.g. a shared Docker volume):

    evaluator_{1..N}.pem     N independent consensus evaluator PRIVATE keys (0600)
    consensus_trust.json     consensus evaluator trust set (PUBLIC keys only)

The gateway loads ``consensus_trust.json`` (public keys) via
``MCC_CONSENSUS_TRUST_CONFIG``; the evaluator quorum loads the private ``.pem``
keys via ``MCC_EVALUATOR_KEYS_DIR``. Private keys never leave the output dir and
are never committed. The VoltAgent process gets neither — it holds no key.

Usage:
    python -m integrations.voltagent.mcc_side.generate_config --out DIR [--evaluators N] [--force]
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from mcc_core import SigningKey


def _write_key(path: Path, force: bool) -> SigningKey:
    if path.exists() and not force:
        sys.exit(f"refusing to overwrite existing key: {path} (use --force)")
    key = Ed25519PrivateKey.generate()
    pem = key.private_bytes(
        serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption())
    if path.exists():
        path.unlink()
    fd = os.open(str(path), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "wb") as fh:
        fh.write(pem)
    return SigningKey.from_pem_file(str(path), path.stem)


def generate(
    out_dir: Path, *, evaluators: int = 3, force: bool = False,
    gateway_signing_key: bool = False,
) -> Path:
    if evaluators < 1:
        raise ValueError("--evaluators must be >= 1")
    out_dir.mkdir(parents=True, exist_ok=True)
    os.chmod(out_dir, 0o700)

    # A persistent gateway decision-token signing key (production-style: the
    # gateway is not ephemeral, so decision tokens remain verifiable across
    # restarts). PUBLIC key is not distributed here — the gateway trusts its own.
    if gateway_signing_key:
        _write_key(out_dir / "gateway_signing.pem", force)

    keys = [_write_key(out_dir / f"evaluator_{i + 1}.pem", force) for i in range(evaluators)]
    trust = {
        "issuers": [
            {"issuer_id": f"evaluator-{i + 1}", "enabled": True,
             "keys": [{"kid": k.kid, "public_key_b64": k.public_key_b64(), "not_after": None}]}
            for i, k in enumerate(keys)
        ]
    }
    trust_path = out_dir / "consensus_trust.json"
    trust_path.write_text(json.dumps(trust, indent=2), encoding="utf-8")
    return trust_path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True, help="output directory (shared volume)")
    ap.add_argument("--evaluators", type=int, default=3)
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--gateway-signing-key", action="store_true",
                    help="also generate a persistent gateway decision-token signing key")
    args = ap.parse_args()

    out = Path(args.out)
    trust_path = generate(out, evaluators=args.evaluators, force=args.force,
                          gateway_signing_key=args.gateway_signing_key)
    print(f"wrote {args.evaluators} evaluator keys (0600) + {trust_path.name} to {out}")
    if args.gateway_signing_key:
        print("  gateway  -> MCC_GATEWAY_SIGNING_KEY_PATH=" + str(out / "gateway_signing.pem"))
    print("  gateway  -> MCC_CONSENSUS_TRUST_CONFIG=" + str(trust_path))
    print("  quorum   -> MCC_EVALUATOR_KEYS_DIR=" + str(out))
    print("  VoltAgent-> holds NO key (proposes only)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
