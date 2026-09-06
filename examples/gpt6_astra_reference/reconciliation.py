"""Reconciliation for the ``create_github_issue`` governed operation.

Round 17 (test scenario 8/17/18): when the external actuator's HTTP response
is lost after the side effect genuinely occurred (or the process crashes
mid-call), the coordinator leaves the logical operation ``UNKNOWN`` — see
``mcc_core.coordinator``/``mcc_core.idempotency``. This module is the ONLY
thing that may ever move such an operation forward, and it does so purely by
LOOKING: it queries the GitHub (or mock) service for an issue whose body
carries this exact ``logical_operation_id``'s marker
(``github_actuator.logical_operation_marker``), and only a POSITIVE, exact
match resolves ``UNKNOWN -> EXECUTED``.

Read/status evidence only. This module:

* NEVER creates an issue (no POST is ever made here);
* treats "not found", a transport error, a timeout, and an HTTP error
  response IDENTICALLY — as inconclusive — and in every one of those cases
  leaves the operation exactly as it was (``UNKNOWN``). None of them is ever
  treated as grounds to authorize a retry; only ``mcc_core.idempotency``'s
  own admission logic decides that, and reconciliation never calls anything
  that could make an UNKNOWN operation retry-eligible;
* is safe to race against a late-arriving completion of the very same
  dispatch, a fresh (blocked) retry attempt, or a second concurrent
  reconciliation worker — all fenced through the same ``expected_generation``
  compare-and-swap ``mcc_core.idempotency.resolve_unknown`` already provides.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from mcc_core.idempotency import ReconcileStatus
from mcc_core.signing import hash_document

from .github_actuator import logical_operation_marker


@dataclass(frozen=True)
class ReconciliationOutcome:
    found: bool          # positive external evidence located
    applied: bool         # the UNKNOWN -> EXECUTED transition was actually made by THIS call
    reason: str
    issue: Optional[Dict[str, Any]] = None


async def _find_issue_by_marker(
    *, base_url: str, repo: str, logical_operation_id: str,
    token: Optional[str] = None, timeout: float = 10.0,
) -> Optional[Dict[str, Any]]:
    """Read-only GET against the SAME ``/repos/{repo}/issues`` shape the real
    GitHub REST API and ``mock_github_service.py`` both expose. Any failure
    to definitively confirm a match (transport error, timeout, non-2xx, an
    unexpected response shape) returns ``None`` — treated identically to a
    genuine "not found", never distinguished for the purpose of authorizing
    anything further."""
    import httpx

    marker = logical_operation_marker(logical_operation_id)
    headers = {"Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.get(f"{base_url}/repos/{repo}/issues", headers=headers)
            resp.raise_for_status()
            data = resp.json()
    except Exception:
        return None  # inconclusive: negative evidence, never authorizes a retry

    issues: Optional[List[Dict[str, Any]]]
    if isinstance(data, dict):
        issues = data.get("issues")  # mock_github_service.py's shape
    elif isinstance(data, list):
        issues = data  # the real GitHub REST API's shape
    else:
        issues = None
    if not isinstance(issues, list):
        return None

    for issue in issues:
        if not isinstance(issue, dict):
            continue
        if marker in (issue.get("body") or ""):
            return issue
    return None


async def reconcile_github_issue_operation(
    *, idempotency: Any, key: str, expected_generation: str,
    base_url: str, repo: str, logical_operation_id: str,
    token: Optional[str] = None, timeout: float = 10.0,
) -> ReconciliationOutcome:
    """Look for positive external evidence for one logical operation and, if
    (and only if) found, resolve it. ``idempotency`` is the same registry
    (``mcc_core`` in-memory or Redis) the coordinator used; ``key`` is the
    token's ``idempotency_key``; ``expected_generation`` is the generation
    observed via ``idempotency.get_state(key)`` immediately before calling
    this — the same fencing every other durable-state mutation uses, so a
    late-arriving legitimate completion of the SAME dispatch attempt and this
    reconciliation call can race safely (exactly one of the two writes
    applies; see ``tests/test_idempotency.py``)."""
    issue = await _find_issue_by_marker(
        base_url=base_url, repo=repo, logical_operation_id=logical_operation_id,
        token=token, timeout=timeout,
    )
    if issue is None:
        return ReconciliationOutcome(
            found=False, applied=False,
            reason="no positive external evidence found; operation left UNKNOWN",
        )
    result_ref = hash_document({
        "issue_number": issue.get("number"), "html_url": issue.get("html_url"),
        "repo": issue.get("repo"),
    })
    result = await idempotency.resolve_unknown(
        key, expected_generation=expected_generation, result_ref=result_ref,
    )
    if result.status == ReconcileStatus.RESOLVED:
        return ReconciliationOutcome(found=True, applied=True, reason=result.reason, issue=issue)
    # Positive evidence exists, but this call did not itself apply the
    # transition -- either a racing writer already resolved it
    # (ALREADY_EXECUTED), the state moved on for another reason (NOT_UNKNOWN/
    # STALE_GENERATION), or the record disappeared (NOT_FOUND/ERROR). None of
    # these is "found=False": the external evidence genuinely exists.
    return ReconciliationOutcome(found=True, applied=False, reason=result.reason, issue=issue)


__all__ = ["ReconciliationOutcome", "reconcile_github_issue_operation"]
