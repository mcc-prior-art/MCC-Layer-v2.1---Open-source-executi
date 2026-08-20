#!/usr/bin/env python3
"""Generate a persistent Ed25519 Audit Checkpoint signing key.

This is a SEPARATE key from the Decision Token signing key
(scripts/generate_signing_key.py) -- required property:

    Decision Token signing authority != Audit Checkpoint signing authority

Usage:
    python scripts/generate_checkpoint_signing_key.py [output_path]

Writes a PKCS8 PEM (mode 0600) and prints the base64-encoded public key
for distribution to checkpoint-anchor verifiers (``verify_anchors``'
``trusted_public_key``). Refuses to overwrite an existing file.
"""

import base64
import os
import sys

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey


def main() -> None:
    path = sys.argv[1] if len(sys.argv) > 1 else "mcc_checkpoint_signing_key.pem"
    if os.path.exists(path):
        sys.exit(f"refusing to overwrite existing key: {path}")

    decision_token_key_path = os.environ.get("MCC_GATEWAY_SIGNING_KEY_PATH", "")
    if decision_token_key_path and os.path.realpath(path) == os.path.realpath(
        decision_token_key_path
    ) if os.path.exists(decision_token_key_path) else False:
        sys.exit(
            f"refusing: output path {path!r} matches the Decision Token signing "
            f"key path ({decision_token_key_path!r}) -- these must be distinct keys"
        )

    key = Ed25519PrivateKey.generate()
    pem = key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    )

    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "wb") as fh:
        fh.write(pem)

    public_raw = key.public_key().public_bytes(
        serialization.Encoding.Raw, serialization.PublicFormat.Raw
    )
    print(f"written: {path} (mode 0600)")
    print("purpose: audit-checkpoint-anchor (NOT the Decision Token signing key)")
    print(f"public key (base64): {base64.b64encode(public_raw).decode('ascii')}")
    print(
        "distribute this public key to anything that runs verify_anchors "
        "(python -m mcc_checkpoint verify-anchors --trusted-key ...)"
    )


if __name__ == "__main__":
    main()
