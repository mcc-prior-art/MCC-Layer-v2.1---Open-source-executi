"""Export a Governance Evidence Bundle from already-produced governance artifacts.

Observational only: this consumes an existing decision token, gate result, audit
entries and receipt/denial — it performs **no** authorization, **no** execution,
and touches no gate/nonce/audit-write path. It fails closed on incomplete or
internally inconsistent evidence and never fabricates a missing artifact (in
particular, a DENY bundle can never contain an execution receipt).
"""

from __future__ import annotations

import json
import tarfile
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from mcc_core.signing import canonical_bytes, hash_action, hash_payload, sha256_hex
from mcc_core.version import RUNTIME_VERSION

from .schema import (
    AUDIT_ANCHOR_PATH,
    AUDIT_ENTRIES_PATH,
    BUNDLE_SCHEMA_VERSION,
    DECISION_TOKEN_PATH,
    DENIAL_PATH,
    GATE_RESULT_PATH,
    MANIFEST_NAME,
    PROPOSAL_PATH,
    RECEIPT_PATH,
    IncompleteEvidenceError,
    Outcome,
)

_EXECUTABLE = {"ALLOW", "CONSTRAIN"}
_KNOWN_VERDICTS = {"ALLOW", "DENY", "ESCALATE", "CONSTRAIN"}


@dataclass
class EvidenceInput:
    """Typed, already-produced governance data to package as evidence.

    Nothing here is re-decided or re-authorized; it is a faithful snapshot of a
    completed governance path.
    """

    verdict: str
    actor_id: str
    resource_id: str
    action: str
    correlation_id: Optional[str] = None
    decision_token: Optional[Dict[str, Any]] = None  # signed token (ALLOW/CONSTRAIN)
    proposal: Optional[Dict[str, Any]] = None  # canonical proposal payload
    gate_result: Optional[Dict[str, Any]] = None
    receipt: Optional[Dict[str, Any]] = None  # ALLOW execution receipt
    denial: Optional[Dict[str, Any]] = None  # DENY / no-execution evidence
    audit_entries: Optional[List[Dict[str, Any]]] = None
    audit_anchor_prev_hash: Optional[str] = None
    mcc_core_version: Optional[str] = None


@dataclass
class _Artifact:
    logical_id: str
    path: str
    obj: Any
    is_jsonl: bool = False
    raw: bytes = b""
    sha256: str = ""


def _entry_hash(prev_hash: str, body: Dict[str, Any]) -> str:
    # Mirror AuditLog._entry_hash without importing the writer (observational).
    import hashlib

    return hashlib.sha256(prev_hash.encode("utf-8") + canonical_bytes(body)).hexdigest()


def _verify_audit_slice(entries: List[Dict[str, Any]], anchor_prev: Optional[str]) -> None:
    """Refuse to export an audit slice whose internal linkage does not hold."""
    prev = anchor_prev
    for i, entry in enumerate(entries):
        declared = entry.get("hash")
        prev_hash = entry.get("prev_hash")
        if declared is None or prev_hash is None:
            raise IncompleteEvidenceError(f"audit entry {i} missing hash/prev_hash")
        if prev is not None and prev_hash != prev:
            raise IncompleteEvidenceError(f"audit entry {i} does not link to the previous entry")
        body = {k: v for k, v in entry.items() if k != "hash"}
        if _entry_hash(str(prev_hash), body) != declared:
            raise IncompleteEvidenceError(f"audit entry {i} hash does not recompute")
        prev = declared


def _validate(ev: EvidenceInput) -> Outcome:
    verdict = ev.verdict
    if verdict not in _KNOWN_VERDICTS:
        raise IncompleteEvidenceError(f"unknown verdict {verdict!r}")

    executed = ev.receipt is not None
    if verdict == "DENY":
        if ev.receipt is not None:
            raise IncompleteEvidenceError("a DENY bundle must not contain an execution receipt")
        if ev.decision_token is not None:
            raise IncompleteEvidenceError("a DENY issues no signed decision token")
        outcome = Outcome.DENIED
    elif verdict in _EXECUTABLE:
        if ev.decision_token is None:
            raise IncompleteEvidenceError(
                f"an executable verdict ({verdict}) requires its signed decision token"
            )
        outcome = Outcome.EXECUTED if executed else Outcome.DENIED
    else:  # ESCALATE without approval -> no execution
        if ev.receipt is not None:
            raise IncompleteEvidenceError(f"{verdict} without approval must not carry a receipt")
        outcome = Outcome.DENIED

    tok = ev.decision_token
    if tok is not None:
        for req in ("sig", "kid", "decision", "action", "action_hash", "payload_hash"):
            if req not in tok:
                raise IncompleteEvidenceError(f"decision token missing claim {req!r}")
        if tok["decision"] != verdict:
            raise IncompleteEvidenceError("token verdict does not match the stated verdict")
        if tok["action"] != ev.action:
            raise IncompleteEvidenceError("token action does not match the stated action")
        if tok["action_hash"] != hash_action(ev.action):
            raise IncompleteEvidenceError("token action_hash is inconsistent with the action")
        for claim, value in (("actor_id", ev.actor_id), ("resource_id", ev.resource_id)):
            if tok.get(claim) is not None and tok.get(claim) != value:
                raise IncompleteEvidenceError(f"token {claim} does not match the stated {claim}")
        if ev.proposal is not None and hash_payload(ev.proposal) != tok["payload_hash"]:
            raise IncompleteEvidenceError("proposal does not hash to the token payload_hash")
        if ev.receipt is not None:
            rp = ev.receipt.get("payload_sha256")
            if rp is not None and rp != tok["payload_hash"]:
                raise IncompleteEvidenceError("receipt payload hash does not match the token")

    if ev.audit_entries:
        _verify_audit_slice(ev.audit_entries, ev.audit_anchor_prev_hash)
    return outcome


def _decision_manifest(ev: EvidenceInput) -> Dict[str, Any]:
    tok = ev.decision_token or {}
    return {
        "decision_id": tok.get("jti"),
        "correlation_id": ev.correlation_id,
        "actor_id": ev.actor_id,
        "resource_id": ev.resource_id,
        "action": ev.action,
        "verdict": ev.verdict,
        "issuer": tok.get("iss"),
        "audience": tok.get("aud"),
        "not_before": tok.get("nbf"),
        "not_after": tok.get("exp"),
        "policy_id": tok.get("policy_id"),
        "policy_hash": tok.get("policy_hash"),
        "action_hash": tok.get("action_hash") or hash_action(ev.action),
        "payload_hash": tok.get("payload_hash"),
        "constraints": tok.get("constraints", {}),
        "nonce": tok.get("nonce"),
        "mandate_id": tok.get("mandate_id"),
        "signed_token_present": ev.decision_token is not None,
        "signing_kid": tok.get("kid"),
    }


def _collect_artifacts(ev: EvidenceInput) -> List[_Artifact]:
    arts: List[_Artifact] = []
    if ev.decision_token is not None:
        arts.append(_Artifact("decision_token", DECISION_TOKEN_PATH, ev.decision_token))
    if ev.proposal is not None:
        arts.append(_Artifact("proposal", PROPOSAL_PATH, ev.proposal))
    if ev.gate_result is not None:
        arts.append(_Artifact("gate_result", GATE_RESULT_PATH, ev.gate_result))
    if ev.receipt is not None:
        arts.append(_Artifact("receipt", RECEIPT_PATH, ev.receipt))
    if ev.denial is not None:
        arts.append(_Artifact("denial", DENIAL_PATH, ev.denial))
    if ev.audit_entries:
        arts.append(_Artifact("audit_entries", AUDIT_ENTRIES_PATH, ev.audit_entries, is_jsonl=True))
        anchor = {
            "anchor_prev_hash": ev.audit_anchor_prev_hash,
            "first_hash": ev.audit_entries[0].get("hash"),
            "last_hash": ev.audit_entries[-1].get("hash"),
            "entry_count": len(ev.audit_entries),
        }
        arts.append(_Artifact("audit_anchor", AUDIT_ANCHOR_PATH, anchor))
    for a in arts:
        if a.is_jsonl:
            a.raw = b"".join(canonical_bytes(e) + b"\n" for e in a.obj)
        else:
            a.raw = canonical_bytes(a.obj)
        a.sha256 = sha256_hex(a.raw)
    return arts


def build_manifest(
    ev: EvidenceInput,
    *,
    created_at: Optional[str] = None,
    bundle_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Build the canonical manifest dict (also used for determinism tests)."""
    outcome = _validate(ev)
    arts = _collect_artifacts(ev)
    audit_meta = {}
    if ev.audit_entries:
        audit_meta = {
            "entry_count": len(ev.audit_entries),
            "anchor_prev_hash": ev.audit_anchor_prev_hash,
            "first_hash": ev.audit_entries[0].get("hash"),
            "last_hash": ev.audit_entries[-1].get("hash"),
        }
    return {
        "schema_version": BUNDLE_SCHEMA_VERSION,
        "bundle_id": bundle_id or uuid.uuid4().hex,
        "created_at": created_at or datetime.now(timezone.utc).isoformat(),
        "mcc_core_version": ev.mcc_core_version or RUNTIME_VERSION,
        "decision": _decision_manifest(ev),
        "execution": {
            "outcome": outcome.value,
            "gate_result_present": ev.gate_result is not None,
            "receipt_present": ev.receipt is not None,
            "receipt_payload_sha256": (ev.receipt or {}).get("payload_sha256"),
            "denial_present": ev.denial is not None,
        },
        "audit": audit_meta,
        "artifacts": [
            {
                "logical_id": a.logical_id,
                "path": a.path,
                "media_type": "application/x-ndjson" if a.is_jsonl else "application/json",
                "sha256": a.sha256,
            }
            for a in arts
        ],
    }


def export_bundle(
    evidence: EvidenceInput,
    dest: Path | str,
    *,
    archive: bool = False,
    created_at: Optional[str] = None,
    bundle_id: Optional[str] = None,
) -> Path:
    """Write a deterministic, portable evidence bundle. Fails closed.

    ``dest`` is a directory (default) or, with ``archive=True``, a ``.tar.gz``
    file. Returns the path written. Raises :class:`IncompleteEvidenceError` if the
    evidence is missing or internally inconsistent — no partial/inconsistent
    bundle is ever produced.
    """
    manifest = build_manifest(evidence, created_at=created_at, bundle_id=bundle_id)
    arts = _collect_artifacts(evidence)
    files: Dict[str, bytes] = {a.path: a.raw for a in arts}
    files[MANIFEST_NAME] = canonical_bytes(manifest)

    dest = Path(dest)
    if archive:
        if dest.suffix not in (".gz", ".tgz") and not str(dest).endswith(".tar.gz"):
            dest = dest.with_name(dest.name + ".tar.gz")
        with tarfile.open(dest, "w:gz") as tar:
            for name in sorted(files):
                data = files[name]
                info = tarfile.TarInfo(name=name)
                info.size = len(data)
                info.mtime = 0  # deterministic
                import io

                tar.addfile(info, io.BytesIO(data))
        return dest

    dest.mkdir(parents=True, exist_ok=True)
    for name in sorted(files):
        target = dest / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(files[name])
    return dest


def canonical_manifest_for_compare(manifest: Dict[str, Any]) -> bytes:
    """Canonical bytes of a manifest with documented non-deterministic fields
    blanked, for equivalence comparison across exports."""
    from .schema import NON_DETERMINISTIC_MANIFEST_FIELDS

    m = {k: v for k, v in manifest.items() if k not in NON_DETERMINISTIC_MANIFEST_FIELDS}
    return canonical_bytes(m)


def read_manifest_from(path: Path | str) -> Dict[str, Any]:
    """Read just the manifest from a bundle directory or archive."""
    path = Path(path)
    if path.is_dir():
        return dict(json.loads((path / MANIFEST_NAME).read_bytes()))
    with tarfile.open(path, "r:*") as tar:
        member = tar.extractfile(MANIFEST_NAME)
        if member is None:
            raise KeyError(MANIFEST_NAME)
        return dict(json.loads(member.read()))
