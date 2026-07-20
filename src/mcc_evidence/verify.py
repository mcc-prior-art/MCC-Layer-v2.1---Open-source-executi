"""Offline verification of a Governance Evidence Bundle.

Observational only. Verification opens a bundle (directory or ``.tar.gz``),
recomputes digests, cross-checks the manifest against the signed decision token,
re-verifies the audit-chain linkage, checks execution/denial consistency and,
when trusted issuer keys are supplied, verifies the Ed25519 signature. It never
executes, authorizes, consumes a nonce, evaluates policy, or mutates anything —
it only reads and reports a structured :class:`VerificationResult`.

A failure that affects integrity or authority evidence is always a blocking
failure, never a warning.
"""

from __future__ import annotations

import hashlib
import json
import tarfile
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from mcc_core.signing import (
    canonical_bytes,
    hash_action,
    hash_payload,
    public_key_from_b64,
    sha256_hex,
    verify_token,
)

from .schema import (
    AUDIT_ANCHOR_PATH,
    AUDIT_ENTRIES_PATH,
    DECISION_TOKEN_PATH,
    MANIFEST_NAME,
    PROPOSAL_PATH,
    RECEIPT_PATH,
    SUPPORTED_SCHEMA_VERSIONS,
    BundleFormatError,
    CheckResult,
    CheckStatus,
    EvidenceStatus,
    VerificationResult,
)

TrustedKeys = Dict[str, str]  # {kid: public_key_b64}


class _Reader:
    """Read file bytes + list members from a bundle directory or tar.gz."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self._tar: Optional[tarfile.TarFile] = None
        if path.is_dir():
            self._names = [
                str(p.relative_to(path)).replace("\\", "/")
                for p in sorted(path.rglob("*"))
                if p.is_file()
            ]
        elif path.exists():
            try:
                self._tar = tarfile.open(path, "r:*")
            except tarfile.TarError as e:
                raise BundleFormatError(f"corrupt archive: {e}") from e
            self._names = sorted(m.name for m in self._tar.getmembers() if m.isfile())
        else:
            raise BundleFormatError(f"bundle not found: {path}")

    def names(self) -> List[str]:
        return list(self._names)

    def read(self, name: str) -> bytes:
        if self._tar is not None:
            member = self._tar.extractfile(name)
            if member is None:
                raise KeyError(name)
            return member.read()
        return (self.path / name).read_bytes()

    def has(self, name: str) -> bool:
        return name in self._names

    def close(self) -> None:
        if self._tar is not None:
            self._tar.close()


def _audit_entry_hash(prev_hash: str, body: Dict[str, Any]) -> str:
    return hashlib.sha256(prev_hash.encode("utf-8") + canonical_bytes(body)).hexdigest()


def verify_bundle(
    path: Path | str,
    *,
    trusted_keys: Optional[TrustedKeys] = None,
) -> VerificationResult:
    """Verify a bundle offline and return a structured result.

    ``trusted_keys`` maps a signing ``kid`` to its raw base64 Ed25519 public key.
    When supplied, the decision token signature is verified against the trusted
    key (a mismatch is a blocking failure). When omitted, the signature cannot be
    anchored and the overall status is ``INTACT_UNTRUSTED_SIGNER`` — structurally
    intact but NOT trusted governance evidence (``trusted`` is False), provided
    every integrity/binding/audit/consistency check holds.
    """
    path = Path(path)
    checks: List[CheckResult] = []
    failures: List[str] = []
    warnings: List[str] = []

    def add(name: str, status: CheckStatus, detail: str = "") -> None:
        checks.append(CheckResult(name, status, detail))
        if status is CheckStatus.FAIL:
            failures.append(f"{name}: {detail}")
        elif status is CheckStatus.WARN:
            warnings.append(f"{name}: {detail}")

    try:
        reader = _Reader(path)
    except BundleFormatError as e:
        return VerificationResult(
            overall_status=EvidenceStatus.INVALID, schema_supported=False,
            checks=[CheckResult("bundle_readable", CheckStatus.FAIL, str(e))],
            failures=[str(e)])

    try:
        return _verify(reader, trusted_keys, checks, failures, warnings, add)
    finally:
        reader.close()


def _verify(
    reader: _Reader,
    trusted_keys: Optional[TrustedKeys],
    checks: List[CheckResult],
    failures: List[str],
    warnings: List[str],
    add: Callable[..., None],
) -> VerificationResult:
    # ---- manifest ---------------------------------------------------------- #
    if not reader.has(MANIFEST_NAME):
        add("manifest_integrity", CheckStatus.FAIL, "manifest.json missing")
        return _finish(checks, failures, warnings, token_present=False, schema_supported=False)
    try:
        manifest = json.loads(reader.read(MANIFEST_NAME))
    except Exception as e:  # noqa: BLE001
        add("manifest_integrity", CheckStatus.FAIL, f"malformed manifest: {e}")
        return _finish(checks, failures, warnings, token_present=False, schema_supported=False)

    schema = manifest.get("schema_version")
    bundle_id = manifest.get("bundle_id")
    decision = manifest.get("decision") or {}
    execution = manifest.get("execution") or {}
    decision_id = decision.get("decision_id")
    outcome = execution.get("outcome")

    if schema not in SUPPORTED_SCHEMA_VERSIONS:
        add("schema_support", CheckStatus.FAIL, f"unsupported schema version {schema!r}")
        res = VerificationResult(
            overall_status=EvidenceStatus.UNSUPPORTED_SCHEMA, schema_supported=False,
            checks=checks, failures=list(failures), warnings=list(warnings))
        res.bundle_id, res.decision_id, res.outcome = bundle_id, decision_id, outcome
        return res
    add("schema_support", CheckStatus.PASS, schema)

    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, list):
        add("manifest_integrity", CheckStatus.FAIL, "artifacts list missing/invalid")
        return _finish(checks, failures, warnings, token_present=False,
                       schema_supported=True, bundle_id=bundle_id,
                       decision_id=decision_id, outcome=outcome)
    ids = [a.get("logical_id") for a in artifacts]
    paths = [a.get("path") for a in artifacts]
    if len(set(ids)) != len(ids) or len(set(paths)) != len(paths):
        add("manifest_integrity", CheckStatus.FAIL, "duplicate logical id or path in manifest")
    else:
        add("manifest_integrity", CheckStatus.PASS, f"{len(artifacts)} artifact(s)")

    # ---- artifact integrity (digests, missing, unexpected) ----------------- #
    manifest_paths = {a.get("path") for a in artifacts}
    actual = set(reader.names()) - {MANIFEST_NAME}
    missing = manifest_paths - actual
    unexpected = actual - manifest_paths
    art_ok = True
    for a in artifacts:
        p, expected = a.get("path"), a.get("sha256")
        if p not in actual:
            continue
        got = sha256_hex(reader.read(p))
        if got != expected:
            art_ok = False
            add("artifact_integrity", CheckStatus.FAIL, f"digest mismatch for {p}")
    if missing:
        art_ok = False
        add("artifact_integrity", CheckStatus.FAIL, f"missing manifested file(s): {sorted(missing)}")
    if unexpected:
        art_ok = False
        add("artifact_integrity", CheckStatus.FAIL, f"unexpected file(s): {sorted(unexpected)}")
    if art_ok:
        add("artifact_integrity", CheckStatus.PASS, "all digests match; no missing/extra files")

    # ---- load the signed token (if any) ------------------------------------ #
    token: Optional[Dict[str, Any]] = None
    if reader.has(DECISION_TOKEN_PATH):
        try:
            token = json.loads(reader.read(DECISION_TOKEN_PATH))
        except Exception as e:  # noqa: BLE001
            add("manifest_integrity", CheckStatus.FAIL, f"malformed decision token: {e}")

    # ---- decision / policy / action / payload binding ---------------------- #
    _binding_checks(reader, manifest, decision, execution, token, add)

    # ---- signature --------------------------------------------------------- #
    _signature_check(token, trusted_keys, add)

    # ---- audit chain ------------------------------------------------------- #
    _audit_check(reader, add)

    # ---- execution / denial consistency ------------------------------------ #
    _execution_consistency(execution, token, decision, add)

    return _finish(checks, failures, warnings, token_present=token is not None,
                   schema_supported=True, bundle_id=bundle_id,
                   decision_id=decision_id, outcome=outcome)


def _status_of(checks: List[CheckResult], name: str) -> Optional[CheckStatus]:
    c = next((c for c in checks if c.name == name), None)
    return c.status if c else None


def _finish(
    checks: List[CheckResult],
    failures: List[str],
    warnings: List[str],
    *,
    token_present: bool,
    schema_supported: bool,
    bundle_id: Optional[str] = None,
    decision_id: Optional[str] = None,
    outcome: Optional[str] = None,
) -> VerificationResult:
    """Roll the per-check results up into the structured, multi-dimensional result.

    A blocking failure is never downgraded: any FAIL yields INVALID. An intact
    bundle whose signer is not verified against a trusted key is reported as
    INTACT_UNTRUSTED_SIGNER (``trusted`` is False) — never as trusted evidence.
    """
    def ok(name: str, *, allow_na: bool = True) -> bool:
        st = _status_of(checks, name)
        return st is CheckStatus.PASS or (allow_na and st is CheckStatus.NA)

    integrity_valid = (
        schema_supported
        and _status_of(checks, "manifest_integrity") is CheckStatus.PASS
        and _status_of(checks, "artifact_integrity") is CheckStatus.PASS
    )
    bindings_ok = all(ok(n) for n in
                      ("decision_binding", "policy_binding", "action_binding", "payload_binding"))
    audit_present = _status_of(checks, "audit_chain") not in (None, CheckStatus.NA)
    audit_chain_valid = ok("audit_chain")
    # execution_consistency, when it fails, is already a blocking failure (INVALID).
    signer_verified = _status_of(checks, "signature") is CheckStatus.PASS
    signer_trusted = signer_verified  # only trusted keys are ever accepted
    authority_evidence_verified = (
        token_present and integrity_valid and bindings_ok and signer_trusted
    )

    if failures:
        status = EvidenceStatus.INVALID
    elif token_present:
        status = EvidenceStatus.VERIFIED if signer_trusted else EvidenceStatus.INTACT_UNTRUSTED_SIGNER
    else:
        status = EvidenceStatus.DENIAL_VERIFIED

    return VerificationResult(
        overall_status=status,
        schema_supported=schema_supported,
        integrity_valid=integrity_valid,
        audit_chain_valid=audit_chain_valid,
        audit_present=audit_present,
        signer_verified=signer_verified,
        signer_trusted=signer_trusted,
        authority_evidence_verified=authority_evidence_verified,
        checks=checks,
        failures=list(failures),
        warnings=list(warnings),
        bundle_id=bundle_id,
        decision_id=decision_id,
        outcome=outcome,
    )


def _binding_checks(reader: _Reader, manifest: Dict[str, Any], decision: Dict[str, Any],
                    execution: Dict[str, Any], token: Optional[Dict[str, Any]],
                    add: Callable[..., None]) -> None:
    if token is None:
        # A DENY (or ESCALATE without approval) carries no token; bindings are
        # verified from the manifest + audit/denial instead.
        add("decision_binding", CheckStatus.NA, "no signed token (non-executable verdict)")
        add("policy_binding", CheckStatus.NA, "no signed token")
        add("action_binding", CheckStatus.NA, "no signed token")
        add("payload_binding", CheckStatus.NA, "no signed token")
        return

    def eq(check: str, a: Any, b: Any, what: str) -> None:
        if a == b:
            add(check, CheckStatus.PASS, what)
        else:
            add(check, CheckStatus.FAIL, f"{what}: manifest {a!r} != token {b!r}")

    # Cross-check every authority-bearing field of the manifest against the SIGNED
    # token, so tampering the manifest alone is caught even without a trusted key.
    ok = (decision.get("verdict") == token.get("decision")
          and decision.get("decision_id") == token.get("jti")
          and decision.get("actor_id") == token.get("actor_id")
          and decision.get("resource_id") == token.get("resource_id")
          and decision.get("action") == token.get("action"))
    add("decision_binding", CheckStatus.PASS if ok else CheckStatus.FAIL,
        "verdict/actor/resource/action/id match token" if ok
        else "manifest decision fields do not match the signed token")

    eq("policy_binding", decision.get("policy_hash"), token.get("policy_hash"), "policy_hash")

    # action_hash must match the manifest AND recompute from the action string.
    a_ok = (decision.get("action_hash") == token.get("action_hash")
            and token.get("action_hash") == hash_action(token.get("action", "")))
    add("action_binding", CheckStatus.PASS if a_ok else CheckStatus.FAIL,
        "action_hash consistent" if a_ok else "action_hash inconsistent with action")

    # payload_hash must match the manifest, the proposal (if present) and the
    # receipt fingerprint (if present).
    ph = token.get("payload_hash")
    p_fail = []
    if decision.get("payload_hash") != ph:
        p_fail.append("manifest payload_hash != token")
    if reader.has(PROPOSAL_PATH):
        try:
            proposal = json.loads(reader.read(PROPOSAL_PATH))
            if hash_payload(proposal) != ph:
                p_fail.append("proposal does not hash to token payload_hash")
        except Exception as e:  # noqa: BLE001
            p_fail.append(f"unreadable proposal: {e}")
    if reader.has(RECEIPT_PATH):
        try:
            receipt = json.loads(reader.read(RECEIPT_PATH))
            rp = receipt.get("payload_sha256")
            if rp is not None and rp != ph:
                p_fail.append("receipt payload hash != token payload_hash")
        except Exception as e:  # noqa: BLE001
            p_fail.append(f"unreadable receipt: {e}")
    add("payload_binding", CheckStatus.PASS if not p_fail else CheckStatus.FAIL,
        "payload_hash consistent" if not p_fail else "; ".join(p_fail))


def _signature_check(token: Optional[Dict[str, Any]], trusted_keys: Optional[TrustedKeys],
                     add: Callable[..., None]) -> bool:
    """Return True iff the signature was verified against a TRUSTED key."""
    if token is None:
        add("signature", CheckStatus.NA, "no signed token to verify")
        return True  # nothing to anchor; not a downgrade of authority evidence
    kid = token.get("kid")
    if not trusted_keys:
        add("signature", CheckStatus.WARN,
            "no trusted issuer key supplied; signer not anchored (supply --trusted-key)")
        return False
    b64 = trusted_keys.get(str(kid))
    if b64 is None:
        add("signature", CheckStatus.FAIL, f"no trusted key for signer kid {kid!r}")
        return False
    try:
        pub = public_key_from_b64(b64)
    except Exception as e:  # noqa: BLE001
        add("signature", CheckStatus.FAIL, f"invalid trusted key for {kid!r}: {e}")
        return False
    if verify_token(token, pub):
        add("signature", CheckStatus.PASS, f"Ed25519 signature valid for kid {kid!r}")
        return True
    add("signature", CheckStatus.FAIL, f"Ed25519 signature INVALID for kid {kid!r}")
    return False


def _audit_check(reader: _Reader, add: Callable[..., None]) -> None:
    if not reader.has(AUDIT_ENTRIES_PATH):
        add("audit_chain", CheckStatus.NA, "no audit entries in bundle")
        return
    try:
        entries = [json.loads(ln) for ln in reader.read(AUDIT_ENTRIES_PATH).splitlines() if ln.strip()]
    except Exception as e:  # noqa: BLE001
        add("audit_chain", CheckStatus.FAIL, f"unreadable audit entries: {e}")
        return
    anchor_prev = None
    if reader.has(AUDIT_ANCHOR_PATH):
        try:
            anchor = json.loads(reader.read(AUDIT_ANCHOR_PATH))
            anchor_prev = anchor.get("anchor_prev_hash")
            if anchor.get("entry_count") != len(entries):
                add("audit_chain", CheckStatus.FAIL, "anchor entry_count != actual entries")
                return
            if entries and anchor.get("last_hash") != entries[-1].get("hash"):
                add("audit_chain", CheckStatus.FAIL, "anchor last_hash != last entry")
                return
        except Exception as e:  # noqa: BLE001
            add("audit_chain", CheckStatus.FAIL, f"unreadable audit anchor: {e}")
            return
    prev = anchor_prev
    for i, entry in enumerate(entries):
        declared = entry.get("hash")
        prev_hash = entry.get("prev_hash")
        if declared is None or prev_hash is None:
            add("audit_chain", CheckStatus.FAIL, f"entry {i} missing hash/prev_hash")
            return
        if prev is not None and prev_hash != prev:
            add("audit_chain", CheckStatus.FAIL, f"entry {i} linkage broken (reorder/delete/tamper)")
            return
        body = {k: v for k, v in entry.items() if k != "hash"}
        if _audit_entry_hash(str(prev_hash), body) != declared:
            add("audit_chain", CheckStatus.FAIL, f"entry {i} hash does not recompute (tampered)")
            return
        prev = declared
    add("audit_chain", CheckStatus.PASS, f"{len(entries)} entr(y/ies) link and recompute")


def _execution_consistency(execution: Dict[str, Any], token: Optional[Dict[str, Any]],
                           decision: Dict[str, Any], add: Callable[..., None]) -> None:
    outcome = execution.get("outcome")
    receipt_present = execution.get("receipt_present")
    verdict = decision.get("verdict")
    problems = []
    if outcome == "EXECUTED" and not receipt_present:
        problems.append("EXECUTED outcome without a receipt")
    if outcome == "DENIED" and receipt_present:
        problems.append("DENIED outcome must not carry a receipt")
    if verdict == "DENY":
        if receipt_present:
            problems.append("DENY must never carry an execution receipt")
        if token is not None:
            problems.append("DENY must not carry a signed decision token")
        if outcome != "DENIED":
            problems.append("DENY must have a DENIED outcome")
    if outcome == "EXECUTED" and token is None:
        problems.append("EXECUTED outcome without a signed decision token")
    add("execution_consistency", CheckStatus.PASS if not problems else CheckStatus.FAIL,
        "consistent" if not problems else "; ".join(problems))
