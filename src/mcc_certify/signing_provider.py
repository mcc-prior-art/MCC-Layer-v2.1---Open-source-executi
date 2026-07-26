"""Issuer Signing-Key Contract (PR #68).

Replaces PR #67's implicit "the pipeline derives its own signing key"
behavior with an explicit, pluggable ``SigningKeyProvider`` boundary. No
production private key is ever generated, derived, or embedded by this
module -- a provider either loads real key material the caller supplies out
of band (:class:`LocalFileSigningKeyProvider`) or is the explicitly-named,
non-production fixture path (:class:`FixtureSigningKeyProvider`) that PR
#67's reference/test pipeline already used.

This module defines only an in-process, local-file abstraction. It
introduces no cloud KMS/HSM/Vault client -- but ``SigningKeyProvider`` is
an ABC precisely so a future provider (e.g. a KMS-backed one) can be added
without changing any caller of this interface.
"""

from __future__ import annotations

import abc
from pathlib import Path

from cryptography.hazmat.primitives import serialization

from mcc_core.signing import SigningKey

from .issuer import IssuerIdentity, public_key_fingerprint
from .target import CertifyError


class SigningKeyProviderError(CertifyError):
    """A signing key could not be loaded, or does not match the Issuer
    Identity it is supposed to correspond to. Fails closed -- a provider
    that cannot be validated never yields a usable signing key."""


class SigningKeyProvider(abc.ABC):
    """Abstract boundary between the certification pipeline and wherever a
    real Ed25519 private key actually lives. The pipeline calls only this
    interface -- it never reads private-key material directly."""

    @abc.abstractmethod
    def get_signing_key(self) -> SigningKey:
        """Return the (already-validated) signing key this provider holds."""

    @abc.abstractmethod
    def expected_issuer_id(self) -> str:
        """The ``issuer_id`` a Technical Certificate signed by this
        provider's key MUST declare."""

    @abc.abstractmethod
    def expected_key_id(self) -> str:
        """The ``kid`` (Trust Anchor key id) this provider's key MUST sign
        with -- must equal ``get_signing_key().kid``."""

    @property
    def is_fixture(self) -> bool:
        """True only for the explicit, non-production fixture provider.
        Official-mode certification refuses any provider for which this is
        True (see ``pipeline.py``'s official-mode gating) -- there is no
        silent fallback from a real issuer configuration to fixture keys."""
        return False


class LocalFileSigningKeyProvider(SigningKeyProvider):
    """Loads a real Ed25519 private key from a local PEM file and verifies,
    at construction time (fail closed, before any certificate is ever
    built), that it actually corresponds to the supplied
    :class:`IssuerIdentity` -- same algorithm, same declared public key,
    same recomputed fingerprint, same key id. A key that does not match is
    never returned to a caller; construction itself raises."""

    def __init__(self, private_key_path: Path | str, issuer_identity: IssuerIdentity) -> None:
        self._issuer_identity = issuer_identity
        try:
            signing_key = SigningKey.from_pem_file(str(private_key_path), kid=issuer_identity.key_id)
        except (OSError, ValueError) as e:
            raise SigningKeyProviderError(
                f"cannot load signing key from {private_key_path}: {e}"
            ) from e

        loaded_public_raw = signing_key.public_key().public_bytes(
            serialization.Encoding.Raw, serialization.PublicFormat.Raw
        )
        expected_public_raw = issuer_identity.resolved_public_key().public_bytes(
            serialization.Encoding.Raw, serialization.PublicFormat.Raw
        )
        if loaded_public_raw != expected_public_raw:
            raise SigningKeyProviderError(
                f"signing key at {private_key_path} does not match the public key declared by "
                f"Issuer Identity issuer_id={issuer_identity.issuer_id!r} key_id={issuer_identity.key_id!r}"
            )

        loaded_fingerprint = public_key_fingerprint(signing_key.public_key())
        if loaded_fingerprint != issuer_identity.public_key_fingerprint:
            raise SigningKeyProviderError(
                f"signing key at {private_key_path} has fingerprint {loaded_fingerprint!r}, which does not "
                f"match the Issuer Identity's declared fingerprint {issuer_identity.public_key_fingerprint!r}"
            )

        self._signing_key = signing_key

    def get_signing_key(self) -> SigningKey:
        return self._signing_key

    def expected_issuer_id(self) -> str:
        return self._issuer_identity.issuer_id

    def expected_key_id(self) -> str:
        return self._issuer_identity.key_id

    @property
    def is_fixture(self) -> bool:
        return False


class FixtureSigningKeyProvider(SigningKeyProvider):
    """The explicitly-named, non-production fixture provider: wraps PR
    #67's deterministic ``pipeline._derive_signing_key`` so the reference-
    fixture / isolated-test certification path keeps working unchanged.
    ``is_fixture`` is True, which official-mode certification checks and
    refuses -- this provider must never be selected implicitly."""

    def __init__(self, target_id: str, run_id: str) -> None:
        self._target_id = target_id
        self._run_id = run_id

    def get_signing_key(self) -> SigningKey:
        # Imported lazily (not at module scope) to avoid a circular import:
        # pipeline.py itself needs to reference SigningKeyProvider types.
        from .pipeline import _derive_signing_key

        return _derive_signing_key(self._target_id, self._run_id)

    def expected_issuer_id(self) -> str:
        return f"mcc-certify-issuer-{self._target_id}"

    def expected_key_id(self) -> str:
        return f"mcc-certify-{self._target_id}"

    @property
    def is_fixture(self) -> bool:
        return True


__all__ = [
    "SigningKeyProviderError",
    "SigningKeyProvider",
    "LocalFileSigningKeyProvider",
    "FixtureSigningKeyProvider",
]
