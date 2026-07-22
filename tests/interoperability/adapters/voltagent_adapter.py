"""VoltAgent interoperability adapter (PR #48e, adapter 1/5 — completes the matrix).

A **real** VoltAgent integration. VoltAgent is a Node/TypeScript agent framework,
so — unlike the in-process Python framework adapters — this adapter exercises the
native framework across a language boundary: it runs the real ``@voltagent/core``
``Agent`` in a Node subprocess (``integrations/voltagent/src/interop-originate.ts``,
part of the existing VoltAgent governed integration), using the same deterministic,
offline model the rest of that integration uses. The native agent genuinely SELECTS
its governed tool and fills the notification arguments; the subprocess prints that
proposal as JSON, and this adapter normalizes it into the canonical Integration
Contract proposal.

Framework-specific code stops at proposal normalization. The Node side captures the
proposal and does **not** run the TypeScript governed path — in the interoperability
proof the one and only governance path is the shared MCC Gateway reached from Python
over real HTTP, identical for every adapter. The adapter authorizes nothing, executes
nothing, verifies nothing, and mints no decisions.

Availability is gated: if Node, the ``tsx`` runner, or the ``@voltagent/core``
package are not present, importing this module raises ``ImportError`` so the base
interoperability job simply does not register the adapter (a dedicated ``interop-
voltagent`` CI job installs Node + the package and asserts it is genuinely
exercised). This mirrors the optional-dependency gating of the Python adapters.

Classification: REAL FRAMEWORK INTEGRATION.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import uuid
from pathlib import Path
from typing import Any, Dict

from mcc_compliance.capability_profile import BASELINE_CAPABILITIES

from tests.interoperability.harness import CONTRACT_VERSION, CanonicalProposal

ACTOR = "agent/notify-bot"
RESOURCE = "notifications"

_REPO_ROOT = Path(__file__).resolve().parents[3]
_VOLT_DIR = _REPO_ROOT / "integrations" / "voltagent"
_TSX_BIN = _VOLT_DIR / "node_modules" / ".bin" / "tsx"
_ORIGINATOR = _VOLT_DIR / "src" / "interop-originate.ts"
_VOLT_CORE_PKG = _VOLT_DIR / "node_modules" / "@voltagent" / "core" / "package.json"

# Gate registration on the Node toolchain + the real VoltAgent package being present.
# A missing piece raises ImportError → the base job skips this adapter (the dedicated
# interop-voltagent CI job installs everything and asserts it is exercised).
_NODE = shutil.which("node")
if _NODE is None:
    raise ImportError("node runtime not available for the VoltAgent adapter")
if not _TSX_BIN.exists() or not _ORIGINATOR.exists() or not _VOLT_CORE_PKG.exists():
    raise ImportError("VoltAgent integration (node_modules/@voltagent/core + tsx) not installed")

try:
    _VOLT_CORE_VERSION = json.loads(_VOLT_CORE_PKG.read_text(encoding="utf-8"))["version"]
except Exception as exc:  # pragma: no cover - defensive
    raise ImportError(f"could not read @voltagent/core version: {exc}") from exc


def _run_native(channel: str) -> Dict[str, Any]:
    """Run the real native VoltAgent Agent (Node subprocess) offline and return the
    proposal it emitted. Deterministic model — no LLM, no network, no key."""
    proc = subprocess.run(
        [_NODE, str(_TSX_BIN), str(_ORIGINATOR), channel],
        cwd=str(_VOLT_DIR),
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(
            f"VoltAgent originator failed (rc={proc.returncode}): {proc.stderr.strip()[-400:]}")
    # The originator prints framework banners too; find the single JSON line it emits.
    emitted = None
    for line in proc.stdout.splitlines():
        line = line.strip()
        if not (line.startswith("{") and line.endswith("}")):
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        if obj.get("framework") == "voltagent":
            emitted = obj
            break
    if emitted is None:
        raise RuntimeError("VoltAgent originator emitted no parseable proposal")
    return emitted


class VoltAgentAdapter:
    adapter_name = "voltagent"
    adapter_classification = "REAL FRAMEWORK INTEGRATION"
    framework_name = "voltagent"
    framework_distribution = "@voltagent/core"
    framework_version = _VOLT_CORE_VERSION
    framework_ecosystem = "npm"
    native_object_type = "@voltagent/core.Agent"
    native_api_entrypoint = "@voltagent/core.Agent.generateText (Node subprocess)"
    adapter_module = "tests.interoperability.adapters.voltagent_adapter"
    adapter_version = "1.0.0"

    def framework_provenance(self) -> Dict[str, Any]:
        return {
            "classification": self.adapter_classification,
            "framework_name": self.framework_name,
            "framework_distribution": self.framework_distribution,
            "framework_ecosystem": self.framework_ecosystem,
            "framework_version": self.framework_version,
            "language": "typescript/node",
            "imported_module": "@voltagent/core",
            "native_object_type": self.native_object_type,
            "native_api_entrypoint": self.native_api_entrypoint,
            "bridge": "node subprocess (integrations/voltagent/src/interop-originate.ts)",
            "adapter_module": self.adapter_module,
            "adapter_version": self.adapter_version,
        }

    def capability_profile(self) -> Dict[str, Any]:
        return {
            "profile_version": "1",
            "adapter": {"name": self.adapter_name, "version": self.adapter_version,
                        "implementation_id": self.adapter_module, "framework": "voltagent"},
            "integration_contract": {"version": CONTRACT_VERSION},
            "compliance": {"suite_version": "1.0.0", "vector_set_version": "1"},
            "certification": {"claimed_status": "SELF_DECLARED", "evidence_digest": None},
            "runtime_capabilities": list(BASELINE_CAPABILITIES),
            "optional_capabilities": ["tamper_evident_audit_evidence"],
            "unsupported_capabilities": [],
            "constraints": {},
            "metadata": {"note": "Real VoltAgent (@voltagent/core) integration via Node bridge."},
        }

    def _normalize(self, native: Dict[str, Any]) -> CanonicalProposal:
        # Adapter-specific normalization: the native VoltAgent agent emitted the
        # notification content; wrap it with the shared canonical actor/resource
        # and a fresh correlation id. It does not authorize or execute.
        payload = {
            "recipient": native["recipient"],
            "message": native["message"],
            "priority": native.get("priority", 2),
            "channel": native["channel"],
            "correlation_id": f"voltagent-{uuid.uuid4().hex[:12]}",
        }
        return CanonicalProposal(actor_id=ACTOR, action=native["action"],
                                 resource=RESOURCE, payload=payload)

    def proposal_for(self, scenario: str) -> CanonicalProposal:
        # 1. Exercise the native framework: run the real VoltAgent Agent (Node).
        channel = "pager" if scenario == "DENY" else "email"
        native = _run_native(channel)
        if not native.get("action"):
            raise RuntimeError("VoltAgent agent did not emit a proposal")
        # 2. Adapter-specific normalization into the canonical contract proposal.
        return self._normalize(native)


__all__ = ["VoltAgentAdapter"]
