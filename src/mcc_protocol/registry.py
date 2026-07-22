"""Adapter Registry — descriptors for adapters that speak the canonical protocol.

Reconciled with PR #43/#44/#46/#47
----------------------------------
This registry holds **descriptive** metadata about adapters (identity, framework,
version, supported protocol versions, capabilities, conformance/compatibility). It
is deliberately distinct from :mod:`mcc_compliance.registry` (which registers
compliance-test *adapter factories* for the certification suite); this one is the
platform-level ingress descriptor. Capabilities are validated against the **single**
capability vocabulary already established in PR #47
(:data:`mcc_compliance.capability_profile.KNOWN_CAPABILITIES`) — no parallel
vocabulary.

Hard boundary (enforced by an architecture guard)
-------------------------------------------------
The registry is **informational only**. It does not — and must not — grant
authority, certify trust by itself, authorize execution, verify signatures, or
become a governance decision boundary. Registration is not permission. Conformance
or certification metadata carried here is a *claim/reference* (e.g. to a PR #46
certification), never a trust decision made by the registry. The Gateway, policy,
authority model, and Gate remain the sole deciders; nothing here changes a verdict.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Tuple

from mcc_compliance.capability_profile import KNOWN_CAPABILITIES

from .version import negotiate


class AdapterRegistryError(ValueError):
    """A descriptor is invalid, or a lookup failed (fail-closed)."""


@dataclass(frozen=True)
class AdapterDescriptor:
    """Descriptive metadata for one adapter. Purely informational."""

    adapter_id: str
    framework: str
    adapter_version: str
    supported_protocol_versions: Tuple[str, ...]
    capabilities: Tuple[str, ...] = ()
    #: Informational conformance/certification claim (e.g. a reference to a PR #46
    #: certification evidence digest). Never a trust decision by the registry.
    conformance: Dict[str, Any] = field(default_factory=dict)
    compatibility: Dict[str, Any] = field(default_factory=dict)

    def validate(self) -> "AdapterDescriptor":
        """Fail-closed structural validation. Validating a descriptor authorizes
        nothing."""
        for name in ("adapter_id", "framework", "adapter_version"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise AdapterRegistryError(f"descriptor field {name!r} is missing or empty")
        if not self.supported_protocol_versions:
            raise AdapterRegistryError("adapter declares no supported protocol versions")
        for v in self.supported_protocol_versions:
            compat = negotiate(v)
            if not compat.compatible:
                raise AdapterRegistryError(
                    f"declared protocol version {v!r} is not supported: {compat.reason}")
        unknown = [c for c in self.capabilities if c not in KNOWN_CAPABILITIES]
        if unknown:
            raise AdapterRegistryError(
                f"unknown capabilities {unknown} (not in the PR #47 vocabulary)")
        return self

    def supports_version(self, version: str) -> bool:
        return version in self.supported_protocol_versions

    def to_dict(self) -> Dict[str, Any]:
        return {
            "adapter_id": self.adapter_id,
            "framework": self.framework,
            "adapter_version": self.adapter_version,
            "supported_protocol_versions": list(self.supported_protocol_versions),
            "capabilities": list(self.capabilities),
            "conformance": dict(self.conformance),
            "compatibility": dict(self.compatibility),
        }


class AdapterRegistry:
    """An in-memory registry of adapter descriptors. Informational only."""

    def __init__(self) -> None:
        self._by_id: Dict[str, AdapterDescriptor] = {}

    def register(self, descriptor: AdapterDescriptor) -> AdapterDescriptor:
        """Register (or replace) a validated descriptor. Fail-closed on invalid
        metadata. Registration grants no authority."""
        descriptor.validate()
        self._by_id[descriptor.adapter_id] = descriptor
        return descriptor

    def get(self, adapter_id: str) -> AdapterDescriptor:
        """Look up a descriptor, failing closed on an unknown adapter."""
        try:
            return self._by_id[adapter_id]
        except KeyError as exc:
            raise AdapterRegistryError(
                f"adapter {adapter_id!r} is not registered "
                f"(known: {sorted(self._by_id)})") from exc

    def is_registered(self, adapter_id: str) -> bool:
        return adapter_id in self._by_id

    def all(self) -> Tuple[AdapterDescriptor, ...]:
        return tuple(self._by_id[k] for k in sorted(self._by_id))

    def to_dict(self) -> Dict[str, Any]:
        return {"adapters": [d.to_dict() for d in self.all()]}


__all__ = ["AdapterDescriptor", "AdapterRegistry", "AdapterRegistryError"]
