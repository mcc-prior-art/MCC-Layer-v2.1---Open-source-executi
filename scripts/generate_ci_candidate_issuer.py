#!/usr/bin/env python3
"""Generate the disposable, NON-PRODUCTION CI candidate Issuer used by the
``certification-<ecosystem>``/``certification-five-ecosystems-aggregate``
CI jobs (PR #69) to exercise the full official-mode certification code
path in CI without any real Issuer signing material.

The key is derived DETERMINISTICALLY from a fixed, publicly-disclosed seed
string -- not randomly generated -- so every isolated per-ecosystem CI job
(each a separate runner, unable to share files or secrets with the others)
independently regenerates the exact same Ed25519 keypair, and the
aggregate job's Trust Store therefore recognizes every ecosystem's
signature. This is safe specifically because the key is deterministic,
disclosed, never claimed official, and never used outside CI: it is NOT a
production signing ceremony (see
``.github/workflows/mcc-official-certification.yml`` and
``docs/CERTIFICATION_FIVE_ECOSYSTEMS.md``, "Secure signing ceremony", for
the real, protected path). Every certificate this issuer signs is
NON_OFFICIAL / CANDIDATE by construction -- its own ``issuer_id`` says so.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from cryptography.hazmat.primitives import serialization  # noqa: E402
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey  # noqa: E402
from mcc_core.signing import sha256_hex  # noqa: E402
from mcc_certify.issuer import build_issuer_identity, write_issuer_identity  # noqa: E402
from mcc_certify.trust_store import build_trust_store, write_trust_store  # noqa: E402

#: Fixed, publicly-disclosed (not secret) seed -- this key is deterministic
#: on purpose (see module docstring). Changing this string rotates the CI
#: candidate key; it has no bearing on any production Issuer.
CI_CANDIDATE_SEED = "mcc-ci-candidate-issuer-v1-disposable-non-production"
CI_CANDIDATE_ISSUER_ID = "mcc-ci-candidate-issuer"
CI_CANDIDATE_KEY_ID = "ci-candidate-key-1"
CI_CANDIDATE_VALID_FROM = 1785024000  # 2026-07-26T00:00:00Z, matches the fixed issuance timestamp CI certifies with


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", required=True, help="directory to write issuer.json/issuer-key.pem/trust-store.json into")
    args = parser.parse_args(argv)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    seed = bytes.fromhex(sha256_hex(CI_CANDIDATE_SEED.encode("utf-8")).split(":", 1)[1])
    private_key = Ed25519PrivateKey.from_private_bytes(seed)
    key_path = output_dir / "issuer-key.pem"
    key_path.write_bytes(
        private_key.private_bytes(
            serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()
        )
    )
    key_path.chmod(0o600)

    issuer = build_issuer_identity(
        issuer_id=CI_CANDIDATE_ISSUER_ID,
        display_name="MCC CI Candidate Issuer (NON-OFFICIAL, disposable, deterministic, never production)",
        key_id=CI_CANDIDATE_KEY_ID,
        public_key=private_key.public_key(),
        valid_from=CI_CANDIDATE_VALID_FROM,
        created_at=CI_CANDIDATE_VALID_FROM,
    )
    write_issuer_identity(issuer, output_dir / "issuer.json")
    write_trust_store(build_trust_store((issuer,)), output_dir / "trust-store.json")

    print(f"CI candidate issuer generated at {output_dir} (issuer_id={CI_CANDIDATE_ISSUER_ID!r}, NON-OFFICIAL)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
