"""Vector manifest loading + adapter registry.

Loads the versioned golden vectors for an explicitly selected Integration Contract
version and validates them strictly. There is no implicit fallback to another
version: an unsupported version fails closed. The manifest digest is computed with
the repository's canonical serialization so it is stable and reviewable.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable, Dict, List, Tuple

from mcc_core.signing import canonical_bytes, sha256_hex

from mcc_client.contract import check_version_compatibility

from .models import (
    ComplianceError,
    ComplianceErrorCode,
    ComplianceVector,
    ExpectedOutcome,
)
from .protocol import ComplianceAdapter

VECTORS_ROOT = Path(__file__).resolve().parent / "vectors"

# Contract version -> on-disk vector directory name.
_VERSION_DIRS: Dict[str, str] = {"1.0": "v1"}

_KNOWN_AUTHORIZATION = {
    "valid", "none", "expired", "replay", "scope", "actor",
    "policy_hash", "signature", "tamper",
}
_KNOWN_DRIVERS = {"allow", "deny", "constrain", "escalate"}
_KNOWN_REQUEST_MODES = {"normal", "malformed"}


def _fail(code: ComplianceErrorCode, msg: str) -> "ComplianceError":
    return ComplianceError(code, msg)


def resolve_version_dir(contract_version: str) -> str:
    """Map a contract version to its vector directory, fail-closed."""
    compat = check_version_compatibility(contract_version)
    if not compat.compatible:
        raise _fail(ComplianceErrorCode.UNSUPPORTED_CONTRACT_VERSION,
                    f"contract version {contract_version!r} is not compatible: {compat.reason}")
    if contract_version not in _VERSION_DIRS:
        raise _fail(ComplianceErrorCode.UNSUPPORTED_CONTRACT_VERSION,
                    f"no golden vectors are published for contract version {contract_version!r} "
                    f"(available: {sorted(_VERSION_DIRS)})")
    return _VERSION_DIRS[contract_version]


def manifest_digest(manifest: Dict[str, Any]) -> str:
    """Deterministic digest over the manifest's canonical serialization."""
    return sha256_hex(canonical_bytes(manifest))


def load_manifest(contract_version: str) -> Tuple[Dict[str, Any], str]:
    """Load and return (manifest, digest) for a contract version, fail-closed."""
    version_dir = resolve_version_dir(contract_version)
    path = VECTORS_ROOT / version_dir / "manifest.json"
    if not path.is_file():
        raise _fail(ComplianceErrorCode.MANIFEST_INVALID,
                    f"vector manifest not found for {contract_version!r}")
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except (ValueError, OSError) as exc:
        raise _fail(ComplianceErrorCode.MANIFEST_INVALID,
                    f"vector manifest is not valid JSON: {exc}") from exc
    if not isinstance(manifest, dict):
        raise _fail(ComplianceErrorCode.MANIFEST_INVALID, "manifest must be an object")
    return manifest, manifest_digest(manifest)


def load_vectors(contract_version: str) -> Tuple[List[ComplianceVector], str]:
    """Load, validate, and return (vectors, manifest_digest) in deterministic order.

    Strict: unsupported version, missing/invalid manifest, contract-version
    mismatch, duplicate IDs, unknown scenario types, and malformed vectors all
    fail closed."""
    manifest, digest = load_manifest(contract_version)
    return parse_manifest(manifest, contract_version, digest)


def parse_manifest(manifest: Dict[str, Any], contract_version: str,
                   digest: str | None = None) -> Tuple[List[ComplianceVector], str]:
    """Validate an in-memory manifest and return (vectors, digest), fail-closed.

    Split out from :func:`load_vectors` so the strict validation can be exercised
    directly (duplicate ids, unknown scenario types, malformed vectors) without a
    disk round-trip."""
    if digest is None:
        digest = manifest_digest(manifest)

    if manifest.get("contract_version") != contract_version:
        raise _fail(ComplianceErrorCode.MANIFEST_INVALID,
                    f"manifest contract_version {manifest.get('contract_version')!r} "
                    f"does not match requested {contract_version!r}")
    if manifest.get("contract_identifier") != "mcc-integration-contract":
        raise _fail(ComplianceErrorCode.MANIFEST_INVALID, "unexpected contract_identifier")
    raw = manifest.get("vectors")
    if not isinstance(raw, list) or not raw:
        raise _fail(ComplianceErrorCode.MANIFEST_INVALID, "manifest has no vectors")

    seen: set[str] = set()
    vectors: List[ComplianceVector] = []
    required = ("id", "requirement", "invariant", "category", "mandatory",
                "capability", "scenario", "expected")
    for i, item in enumerate(raw):
        if not isinstance(item, dict):
            raise _fail(ComplianceErrorCode.VECTOR_PARSE_ERROR, f"vector #{i} is not an object")
        for key in required:
            if key not in item:
                raise _fail(ComplianceErrorCode.VECTOR_PARSE_ERROR,
                            f"vector #{i} is missing required field {key!r}")
        vid = item["id"]
        if not isinstance(vid, str) or not vid.strip():
            raise _fail(ComplianceErrorCode.VECTOR_PARSE_ERROR, f"vector #{i} has an invalid id")
        if vid in seen:
            raise _fail(ComplianceErrorCode.DUPLICATE_VECTOR_ID, f"duplicate vector id {vid!r}")
        seen.add(vid)

        scenario = item["scenario"]
        if not isinstance(scenario, dict):
            raise _fail(ComplianceErrorCode.VECTOR_PARSE_ERROR, f"{vid}: scenario must be an object")
        driver = scenario.get("driver")
        if driver not in _KNOWN_DRIVERS:
            raise _fail(ComplianceErrorCode.UNKNOWN_VECTOR_TYPE,
                        f"{vid}: unknown driver {driver!r}")
        auth = scenario.get("authorization")
        if auth is not None and auth not in _KNOWN_AUTHORIZATION:
            raise _fail(ComplianceErrorCode.UNKNOWN_VECTOR_TYPE,
                        f"{vid}: unknown authorization mode {auth!r}")
        req_mode = scenario.get("request", "normal")
        if req_mode not in _KNOWN_REQUEST_MODES:
            raise _fail(ComplianceErrorCode.UNKNOWN_VECTOR_TYPE,
                        f"{vid}: unknown request mode {req_mode!r}")

        try:
            expected = ExpectedOutcome.from_dict(item["expected"])
        except (KeyError, TypeError, ValueError) as exc:
            raise _fail(ComplianceErrorCode.VECTOR_PARSE_ERROR,
                        f"{vid}: invalid expected outcome: {exc}") from exc

        vectors.append(ComplianceVector(
            id=vid, requirement=str(item["requirement"]), invariant=str(item["invariant"]),
            category=str(item["category"]), mandatory=bool(item["mandatory"]),
            capability=str(item["capability"]), scenario=dict(scenario), expected=expected))

    # Deterministic order: by id.
    vectors.sort(key=lambda v: v.id)
    return vectors, digest


# --------------------------------------------------------------------------- #
# Adapter registry.                                                           #
# --------------------------------------------------------------------------- #

_ADAPTERS: Dict[str, Callable[[], ComplianceAdapter]] = {}


def register_adapter(name: str, factory: Callable[[], ComplianceAdapter]) -> None:
    """Register a named adapter factory (no framework-specific coupling here)."""
    _ADAPTERS[name] = factory


def available_adapters() -> List[str]:
    return sorted(_ADAPTERS)


def load_adapter(name: str) -> ComplianceAdapter:
    """Instantiate a registered adapter, fail-closed on unknown names."""
    factory = _ADAPTERS.get(name)
    if factory is None:
        raise _fail(ComplianceErrorCode.ADAPTER_LOAD_FAILED,
                    f"unknown adapter {name!r} (available: {available_adapters()})")
    try:
        return factory()
    except Exception as exc:  # noqa: BLE001 - any construction failure fails closed
        raise _fail(ComplianceErrorCode.ADAPTER_LOAD_FAILED,
                    f"could not load adapter {name!r}: {type(exc).__name__}: {exc}") from exc


__all__ = [
    "VECTORS_ROOT", "resolve_version_dir", "manifest_digest", "load_manifest",
    "load_vectors", "parse_manifest", "register_adapter", "available_adapters",
    "load_adapter",
]
