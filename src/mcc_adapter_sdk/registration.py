"""Adapter registration (PR #50) — reuses the protocol AdapterRegistry.

Registration is **informational only**: it records descriptive metadata about an
adapter so the ingress pipeline can look it up. It grants no authority, certifies
nothing, and never authorizes execution (guaranteed by
:class:`mcc_protocol.AdapterRegistry`). Duplicate adapter ids and incompatible
versions are rejected deterministically, fail-closed.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from mcc_protocol import (
    PROTOCOL_VERSION,
    AdapterDescriptor,
    AdapterRegistry,
    AdapterRegistryError,
)

from .adapter import Adapter
from .errors import AdapterSDKError
from .metadata import AdapterMetadata


def _descriptor(metadata: AdapterMetadata) -> AdapterDescriptor:
    """Build a protocol :class:`AdapterDescriptor` from SDK metadata."""
    versions = (metadata.protocol_version,)
    if PROTOCOL_VERSION not in versions:
        versions = versions + (PROTOCOL_VERSION,)
    return AdapterDescriptor(
        adapter_id=metadata.adapter_id, framework=metadata.framework_name,
        adapter_version=metadata.adapter_version,
        supported_protocol_versions=versions,
        capabilities=tuple(metadata.capabilities),
        conformance={"vendor": metadata.vendor, "maintainer": metadata.maintainer},
        compatibility={"contract_version": metadata.contract_version})


@dataclass(frozen=True)
class AdapterRegistration:
    """The informational record produced by registering an adapter."""

    metadata: AdapterMetadata
    descriptor: AdapterDescriptor

    def to_dict(self) -> dict:
        return {"metadata": self.metadata.to_dict(), "descriptor": self.descriptor.to_dict()}


def register_adapter(adapter: Adapter, registry: Optional[AdapterRegistry] = None,
                     *, replace: bool = False) -> AdapterRegistration:
    """Register an adapter's descriptor (informational). Rejects duplicate ids
    (unless ``replace=True``) and incompatible versions, fail-closed."""
    registry = registry if registry is not None else AdapterRegistry()
    metadata = adapter.describe().validate()
    if not replace and registry.is_registered(metadata.adapter_id):
        raise AdapterSDKError(f"adapter id {metadata.adapter_id!r} is already registered")
    try:
        descriptor = registry.register(_descriptor(metadata))
    except AdapterRegistryError as exc:
        raise AdapterSDKError(f"registration rejected: {exc}") from exc
    return AdapterRegistration(metadata=metadata, descriptor=descriptor)


__all__ = ["AdapterRegistration", "register_adapter"]
