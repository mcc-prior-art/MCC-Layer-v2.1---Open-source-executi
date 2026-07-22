"""AdapterMetadata — immutable, deterministic adapter description (PR #50).

Reuses the authoritative protocol/contract primitives: the capability vocabulary
(PR #47), the single version-compatibility rule (PR #43), and the one
canonicalization (``mcc_core.signing`` pure hashing). It defines no new capability,
version, or error model. Fail-closed: invalid metadata raises
:class:`AdapterSDKError` with an existing :class:`ContractErrorCode`.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple

from mcc_client.contract import CONTRACT_VERSION, ContractErrorCode, check_version_compatibility
from mcc_compliance.capability_profile import KNOWN_CAPABILITIES
from mcc_core.signing import canonical_bytes, sha256_hex
from mcc_protocol import PROTOCOL_VERSION

from .errors import AdapterSDKError

_REQUIRED = ("adapter_id", "adapter_version", "framework_name")


def _as_str_tuple(value: Any, field_name: str) -> Tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, str) or not isinstance(value, (list, tuple)):
        raise AdapterSDKError(f"{field_name} must be a list/tuple of strings")
    out = []
    for item in value:
        if not isinstance(item, str) or not item.strip():
            raise AdapterSDKError(f"{field_name} must contain non-empty strings")
        out.append(item)
    return tuple(out)


@dataclass(frozen=True)
class AdapterMetadata:
    """Immutable description of an adapter. Deterministic serialization + hashing."""

    adapter_id: str
    adapter_version: str
    framework_name: str
    framework_version: Optional[str] = None
    protocol_version: str = PROTOCOL_VERSION
    contract_version: str = CONTRACT_VERSION
    capabilities: Tuple[str, ...] = ()
    supported_input_modes: Tuple[str, ...] = ()
    supported_output_modes: Tuple[str, ...] = ()
    vendor: Optional[str] = None
    maintainer: Optional[str] = None
    documentation_url: Optional[str] = None
    source_url: Optional[str] = None

    @classmethod
    def create(cls, *, adapter_id: str, adapter_version: str, framework_name: str,
               framework_version: Optional[str] = None,
               protocol_version: str = PROTOCOL_VERSION,
               contract_version: str = CONTRACT_VERSION,
               capabilities: Any = (), supported_input_modes: Any = (),
               supported_output_modes: Any = (), vendor: Optional[str] = None,
               maintainer: Optional[str] = None, documentation_url: Optional[str] = None,
               source_url: Optional[str] = None) -> "AdapterMetadata":
        """Build and validate metadata, normalizing sequences to immutable tuples."""
        md = cls(
            adapter_id=adapter_id, adapter_version=adapter_version,
            framework_name=framework_name, framework_version=framework_version,
            protocol_version=protocol_version, contract_version=contract_version,
            capabilities=_as_str_tuple(capabilities, "capabilities"),
            supported_input_modes=_as_str_tuple(supported_input_modes, "supported_input_modes"),
            supported_output_modes=_as_str_tuple(supported_output_modes, "supported_output_modes"),
            vendor=vendor, maintainer=maintainer,
            documentation_url=documentation_url, source_url=source_url,
        )
        return md.validate()

    def validate(self) -> "AdapterMetadata":
        """Fail-closed structural validation. Never authorizes."""
        for name in _REQUIRED:
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise AdapterSDKError(
                    f"metadata field {name!r} is missing or empty",
                    code=ContractErrorCode.CONTRACT_FIELD_MISSING)
        # Versions reuse the single compatibility rule (fail-closed, no downgrade).
        for vfield in ("protocol_version", "contract_version"):
            compat = check_version_compatibility(getattr(self, vfield))
            if not compat.compatible:
                raise AdapterSDKError(
                    f"{vfield} {getattr(self, vfield)!r} is not supported: {compat.reason}",
                    code=compat.error_code or ContractErrorCode.CONTRACT_VERSION_UNSUPPORTED)
        # Capabilities reuse the single PR #47 vocabulary (no parallel set).
        unknown = [c for c in self.capabilities if c not in KNOWN_CAPABILITIES]
        if unknown:
            raise AdapterSDKError(f"unknown capabilities {unknown} (not in the capability vocabulary)")
        for tfield in ("capabilities", "supported_input_modes", "supported_output_modes"):
            _as_str_tuple(list(getattr(self, tfield)), tfield)
        return self

    def to_dict(self) -> Dict[str, Any]:
        return {
            "adapter_id": self.adapter_id,
            "adapter_version": self.adapter_version,
            "framework_name": self.framework_name,
            "framework_version": self.framework_version,
            "protocol_version": self.protocol_version,
            "contract_version": self.contract_version,
            "capabilities": list(self.capabilities),
            "supported_input_modes": list(self.supported_input_modes),
            "supported_output_modes": list(self.supported_output_modes),
            "vendor": self.vendor,
            "maintainer": self.maintainer,
            "documentation_url": self.documentation_url,
            "source_url": self.source_url,
        }

    def digest(self) -> str:
        """Reproducible content hash over the canonical serialization (one
        canonicalization; deterministic across runs and processes)."""
        return sha256_hex(canonical_bytes(self.to_dict()))

    @classmethod
    def from_dict(cls, data: Any) -> "AdapterMetadata":
        if not isinstance(data, dict):
            raise AdapterSDKError("metadata is not a JSON object")
        return cls.create(
            adapter_id=str(data.get("adapter_id", "")),
            adapter_version=str(data.get("adapter_version", "")),
            framework_name=str(data.get("framework_name", "")),
            framework_version=data.get("framework_version"),
            protocol_version=str(data.get("protocol_version", PROTOCOL_VERSION)),
            contract_version=str(data.get("contract_version", CONTRACT_VERSION)),
            capabilities=data.get("capabilities") or (),
            supported_input_modes=data.get("supported_input_modes") or (),
            supported_output_modes=data.get("supported_output_modes") or (),
            vendor=data.get("vendor"), maintainer=data.get("maintainer"),
            documentation_url=data.get("documentation_url"),
            source_url=data.get("source_url"),
        )


__all__ = ["AdapterMetadata"]
