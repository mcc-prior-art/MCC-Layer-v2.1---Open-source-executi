"""The Audit Checkpoint signing key -- a SEPARATE Ed25519 identity from the
Decision Token signing key.

Required security property (see ``docs/AUDIT_CHECKPOINT_ANCHORING.md``):

    Decision Token signing authority != Audit Checkpoint signing authority

Compromise of the process/credential that signs Decision Tokens must not,
by itself, be sufficient to forge audit-checkpoint history. This module
does not introduce a new cryptographic primitive -- it reuses
``mcc_core.signing.SigningKey`` exactly as ``gateway/app.py`` already does
for Decision Tokens -- it only ensures the key MATERIAL and ``kid``
namespace are distinct, and provides a narrow, auditable loader that
refuses to silently reuse the Decision Token key's file.
"""

from __future__ import annotations

import os
from typing import Optional

from mcc_core.signing import SigningKey

from .errors import CheckpointAnchorError

#: Default ``kid`` prefix for Audit Checkpoint signing keys, distinct from
#: gateway's Decision Token default (``mcc-gateway-dev-key-1``) so the two
#: are never confusable at a glance in logs, trust configs, or checkpoints.
DEFAULT_CHECKPOINT_SIGNING_KEY_ID = "mcc-checkpoint-anchor-key-1"

#: Marker embedded nowhere cryptographically significant -- purely a
#: documentation/introspection aid confirming a given SigningKey instance
#: was constructed via this module's loader (and therefore went through
#: the same-file guard below), not a security boundary by itself. The
#: actual guarantee is structural: this module never reads the Decision
#: Token's own settings, so the two can only collide if an operator
#: explicitly points both paths at the same file -- which
#: ``load_checkpoint_signing_key``'s ``forbidden_key_path`` guard rejects.
CHECKPOINT_KEY_PURPOSE = "audit-checkpoint-anchor"


class CheckpointSigningKeyError(CheckpointAnchorError):
    """Raised when the Audit Checkpoint signing key cannot be safely
    loaded -- including the guard against reusing the Decision Token
    key's own file, which would defeat signing-key separation entirely."""


def load_checkpoint_signing_key(
    *,
    key_path: str = "",
    key_id: str = DEFAULT_CHECKPOINT_SIGNING_KEY_ID,
    forbidden_key_path: Optional[str] = None,
) -> SigningKey:
    """Load (or, if ``key_path`` is empty, generate an ephemeral) Audit
    Checkpoint signing key.

    ``forbidden_key_path`` -- when given (pass the Decision Token
    signing key's own configured path) -- causes this to raise
    ``CheckpointSigningKeyError`` if ``key_path`` resolves to the exact
    same file, so a misconfiguration cannot silently collapse the two
    signing authorities back into one key. Comparison is by realpath, so
    a symlink or relative-path alias is caught too.
    """
    if key_path and forbidden_key_path:
        try:
            same_file = os.path.realpath(key_path) == os.path.realpath(forbidden_key_path)
        except OSError:
            same_file = os.path.abspath(key_path) == os.path.abspath(forbidden_key_path)
        if same_file:
            raise CheckpointSigningKeyError(
                f"the Audit Checkpoint signing key path ({key_path!r}) resolves to "
                f"the SAME file as the Decision Token signing key "
                f"({forbidden_key_path!r}); this would collapse "
                f"'Decision Token signing authority != Audit Checkpoint signing "
                f"authority' back into a single key -- refusing to start. Generate "
                f"a distinct key, e.g. via scripts/generate_checkpoint_signing_key.py."
            )
    if key_path:
        return SigningKey.from_pem_file(key_path, key_id)
    return SigningKey.generate(key_id)
