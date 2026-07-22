"""AdapterContext — immutable, ingress-safe context for building a proposal (PR #50).

Carries only the information an adapter needs to construct a
:class:`mcc_protocol.CanonicalProposal`. It makes **no** authority, policy, or
execution decision, exposes no gateway internals, and never lets a secret reach its
``repr()`` or the SDK evidence. Extension fields are bounded and must be
JSON-serializable (unserializable values are rejected, fail-closed).
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Tuple

from .errors import AdapterSDKError

#: Bounded extension data: at most this many keys, each a short string key.
_MAX_EXTENSION_KEYS = 32
_MAX_KEY_LEN = 128


def _ensure_json_serializable(value: Any, where: str) -> Any:
    try:
        json.dumps(value, sort_keys=True)
    except (TypeError, ValueError) as exc:
        raise AdapterSDKError(f"{where} contains an unserializable value: {exc}") from exc
    return value


@dataclass(frozen=True)
class AdapterContext:
    """Immutable, deterministic, secret-free context."""

    actor_reference: str
    tenant: Optional[str] = None
    namespace: Optional[str] = None
    trace_id: Optional[str] = None
    correlation_id: Optional[str] = None
    request_timestamp: Optional[str] = None
    framework_metadata: Dict[str, Any] = field(default_factory=dict)
    declared_capabilities: Tuple[str, ...] = ()
    extension: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def create(cls, *, actor_reference: str, tenant: Optional[str] = None,
               namespace: Optional[str] = None, trace_id: Optional[str] = None,
               correlation_id: Optional[str] = None, request_timestamp: Optional[str] = None,
               framework_metadata: Optional[Dict[str, Any]] = None,
               declared_capabilities: Any = (),
               extension: Optional[Dict[str, Any]] = None) -> "AdapterContext":
        if not isinstance(actor_reference, str) or not actor_reference.strip():
            raise AdapterSDKError("actor_reference is required")
        fm = dict(framework_metadata or {})
        ext = dict(extension or {})
        _ensure_json_serializable(fm, "framework_metadata")
        _ensure_json_serializable(ext, "extension")
        if len(ext) > _MAX_EXTENSION_KEYS:
            raise AdapterSDKError(
                f"extension has too many keys ({len(ext)} > {_MAX_EXTENSION_KEYS})")
        for k in ext:
            if not isinstance(k, str) or not k or len(k) > _MAX_KEY_LEN:
                raise AdapterSDKError("extension keys must be short non-empty strings")
        caps = tuple(str(c) for c in (declared_capabilities or ()))
        return cls(actor_reference=actor_reference, tenant=tenant, namespace=namespace,
                   trace_id=trace_id, correlation_id=correlation_id,
                   request_timestamp=request_timestamp, framework_metadata=fm,
                   declared_capabilities=caps, extension=ext)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "actor_reference": self.actor_reference,
            "tenant": self.tenant,
            "namespace": self.namespace,
            "trace_id": self.trace_id,
            "correlation_id": self.correlation_id,
            "request_timestamp": self.request_timestamp,
            "framework_metadata": dict(self.framework_metadata),
            "declared_capabilities": list(self.declared_capabilities),
            "extension": dict(self.extension),
        }

    def __repr__(self) -> str:
        # Deterministic, secret-free repr: never dumps framework_metadata/extension
        # values (which may carry sensitive framework state) — only their key names.
        return (f"AdapterContext(actor_reference={self.actor_reference!r}, "
                f"tenant={self.tenant!r}, namespace={self.namespace!r}, "
                f"framework_metadata_keys={sorted(self.framework_metadata)!r}, "
                f"extension_keys={sorted(self.extension)!r})")


__all__ = ["AdapterContext"]
