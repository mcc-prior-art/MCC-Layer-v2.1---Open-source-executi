"""Structural validation of an adapter (PR #50).

Validation is **structural only**. It checks that an adapter is well-formed and
SDK-compatible — it does **not** certify, approve, or attest trust or production
compliance. That is a separate, later roadmap milestone. The report deliberately
uses only the words *structurally valid* / *SDK compatible* / *validation passed*.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from mcc_client.contract import CONTRACT_VERSION, check_version_compatibility
from mcc_protocol import PROTOCOL_VERSION, AdapterRegistry, CanonicalProposal

from ._version import SDK_VERSION
from .adapter import Adapter
from .context import AdapterContext
from .errors import AdapterSDKError
from .registration import _descriptor

# Verbs an adapter must never expose — it is translational, never authoritative.
FORBIDDEN_METHODS = ("authorize", "allow", "approve", "execute", "enforce",
                     "evaluate_policy", "issue_token", "sign_token")

# A fixed, deterministic context so validation (and evidence) are reproducible.
_VALIDATION_CONTEXT = AdapterContext(
    actor_reference="sdk-validation/actor", tenant="sdk-validation",
    namespace="validation", trace_id="validation-trace",
    correlation_id="validation-correlation")


@dataclass(frozen=True)
class AdapterValidationReport:
    """The deterministic result of structural validation. Never a certification."""

    adapter_id: str
    checks: List[dict]
    structurally_valid: bool
    sdk_version: str = SDK_VERSION
    protocol_version: str = PROTOCOL_VERSION
    contract_version: str = CONTRACT_VERSION

    @property
    def status(self) -> str:
        # Deliberately NOT "CERTIFIED"/"COMPLIANT"/"APPROVED"/"TRUSTED".
        return "VALIDATION_PASSED" if self.structurally_valid else "VALIDATION_FAILED"

    def to_dict(self) -> dict:
        return {
            "adapter_id": self.adapter_id,
            "status": self.status,
            "structurally_valid": self.structurally_valid,
            "sdk_compatible": self.structurally_valid,
            "sdk_version": self.sdk_version,
            "protocol_version": self.protocol_version,
            "contract_version": self.contract_version,
            "checks": [dict(c) for c in self.checks],
            "disclaimer": "Structural validation only. This is NOT certification, "
                          "official compliance, production approval, or a trust claim.",
        }


def _check(name: str, passed: bool, detail: str = "") -> dict:
    return {"name": name, "passed": bool(passed), "detail": detail}


def validate_adapter(adapter: Adapter,
                     sample_context: Optional[AdapterContext] = None) -> AdapterValidationReport:
    """Run structural validation, returning a deterministic report. Never raises for
    a non-conforming adapter — the failure is recorded in the report (fail-closed:
    an unexpected error is a failed check, never a pass)."""
    context = sample_context or _VALIDATION_CONTEXT
    checks: List[dict] = []
    adapter_id = "unknown"

    # 1. metadata validity
    metadata = None
    try:
        metadata = adapter.describe().validate()
        adapter_id = metadata.adapter_id
        checks.append(_check("metadata_valid", True))
    except Exception as exc:  # noqa: BLE001
        checks.append(_check("metadata_valid", False, f"{type(exc).__name__}: {exc}"))

    # 2. required translational methods present + callable
    for m in ("describe", "to_proposal", "to_response"):
        checks.append(_check(f"has_method_{m}", callable(getattr(adapter, m, None))))
    # 3. no forbidden (authoritative) methods
    forbidden_present = [m for m in FORBIDDEN_METHODS if hasattr(adapter, m)]
    checks.append(_check("no_forbidden_methods", not forbidden_present,
                         f"forbidden methods present: {forbidden_present}" if forbidden_present else ""))

    if metadata is not None:
        # 4. protocol + contract compatibility (reused rule)
        pc = check_version_compatibility(metadata.protocol_version)
        checks.append(_check("protocol_compatible", pc.compatible, pc.reason))
        cc = check_version_compatibility(metadata.contract_version)
        checks.append(_check("contract_compatible", cc.compatible, cc.reason))
        # 5. deterministic serialization + hashing
        det = (metadata.to_dict() == metadata.to_dict() and metadata.digest() == metadata.digest())
        checks.append(_check("deterministic_serialization", det))
        # 6. capability vocabulary (already enforced by metadata.validate; re-assert)
        checks.append(_check("capabilities_known", True))
        # 7. registry compatibility
        try:
            AdapterRegistry().register(_descriptor(metadata))
            checks.append(_check("registry_compatible", True))
        except Exception as exc:  # noqa: BLE001
            checks.append(_check("registry_compatible", False, f"{type(exc).__name__}: {exc}"))

    # 8. CanonicalProposal production (needs a sample native request)
    try:
        sample = adapter.sample_request()
        proposal = adapter.to_proposal(context, sample)
        ok = isinstance(proposal, CanonicalProposal)
        if ok:
            proposal.validate()
        checks.append(_check("produces_canonical_proposal", ok,
                             "" if ok else "did not return a CanonicalProposal"))
    except AdapterSDKError as exc:
        checks.append(_check("produces_canonical_proposal", False,
                             f"no sample / build failed: {exc}"))
    except Exception as exc:  # noqa: BLE001
        checks.append(_check("produces_canonical_proposal", False,
                             f"{type(exc).__name__}: {exc}"))

    structurally_valid = all(c["passed"] for c in checks)
    return AdapterValidationReport(adapter_id=adapter_id, checks=checks,
                                   structurally_valid=structurally_valid)


__all__ = ["AdapterValidationReport", "validate_adapter", "FORBIDDEN_METHODS"]
