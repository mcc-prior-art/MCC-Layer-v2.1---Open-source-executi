"""Operation-bound reconciliation evidence lookup for the Phase 2 live
sandbox proof.

Builds an ``EvidenceVerifier`` for
``gateway.proposal_execution_service.reconcile_proposal_operation`` (the
existing, unmodified Phase 2 reconciliation entry point -- Section 9: "must
use the existing reconcile_proposal_operation"). Queries the SAME
GitHub-shaped ``GET /repos/{owner}/{repo}/issues`` endpoint the real (or
mock) actuator's HTTP peer exposes, looks for the tenant-scoped composite
marker (``marker.py``), and -- only on a genuine match -- returns evidence
in the EXACT operation-bound shape ``reconcile_proposal_operation``
requires: ``{"tenant_id", "logical_operation_id", "action", "resource",
"payload"}``. Never returns a bare marker string or boolean (Section 9:
"The external verifier must not return only {'found': true}").
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from examples.gpt6_astra_reference.issue_contract import GITHUB_ISSUE_ACTION, MarkerSyntaxError

from .marker import composite_marker, extract_composite_marker_identity


def _issue_repository_identity(issue: Dict[str, Any]) -> Optional[str]:
    """Recognizes both this repo's mock service shape (a ``repo`` field)
    and the real GitHub REST API shape (``repository_url``), matching
    ``examples/gpt6_astra_reference/reconciliation.py``'s own equivalent."""
    repo_field = issue.get("repo")
    if isinstance(repo_field, str) and repo_field:
        return repo_field
    repo_url = issue.get("repository_url")
    if isinstance(repo_url, str) and repo_url:
        parts = repo_url.rstrip("/").split("/")
        if len(parts) >= 2 and parts[-1] and parts[-2]:
            return f"{parts[-2]}/{parts[-1]}"
    return None


async def _find_issue_by_composite_marker(
    *, base_url: str, repo: str, tenant_id: str, logical_operation_id: str,
    token: Optional[str] = None, timeout: float = 10.0,
) -> Optional[Dict[str, Any]]:
    """Read-only GET, scoped to ``repo``. Any failure to definitively
    confirm a match (transport error, timeout, non-2xx, an unexpected
    response shape, or a marker-safety violation) returns ``None`` --
    treated identically to a genuine "not found", never distinguished for
    the purpose of authorizing anything further."""
    import httpx

    try:
        marker = composite_marker(tenant_id, logical_operation_id)
    except Exception:
        return None
    headers = {"Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.get(f"{base_url}/repos/{repo}/issues", headers=headers)
            resp.raise_for_status()
            data = resp.json()
    except Exception:
        return None

    issues: Optional[Any]
    if isinstance(data, dict):
        issues = data.get("issues")  # mock service shape
    elif isinstance(data, list):
        issues = data  # real GitHub REST API shape
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


def make_sandbox_evidence_verifier(*, base_url: str, repo: str, token: Optional[str] = None, timeout: float = 10.0):
    """Returns an ``EvidenceVerifier`` bound to this exact sandbox
    destination -- the SAME contract
    ``gateway.proposal_execution_service.reconcile_proposal_operation``
    requires: called WITH the trusted operation context, and returning
    either ``None`` or an operation-bound evidence dict. Never dispatches
    to the actuator (a pure, read-only GET)."""

    async def verify(
        *, tenant_id: str, logical_operation_id: str, action: str,
        resource: Optional[str], payload_hash: str,
    ) -> Optional[Dict[str, Any]]:
        if action != GITHUB_ISSUE_ACTION:
            return None
        try:
            issue = await _find_issue_by_composite_marker(
                base_url=base_url, repo=repo, tenant_id=tenant_id,
                logical_operation_id=logical_operation_id, token=token, timeout=timeout,
            )
        except MarkerSyntaxError:
            return None
        if issue is None:
            return None

        # Defense in depth: the query is already scoped to `repo`, but a
        # candidate whose own reported repository disagrees is never
        # trusted regardless.
        candidate_repo = _issue_repository_identity(issue)
        if candidate_repo != repo:
            return None

        # The marker match alone (Section 10: MARKER != AUTHORITY) proves
        # only that a candidate carries the right composite identity text.
        # Independently re-derive that identity from the candidate's own
        # body and require it to agree exactly -- never trust the query
        # parameters as a substitute for re-reading the evidence itself.
        try:
            found_tenant, found_op = extract_composite_marker_identity(issue.get("body") or "")
        except MarkerSyntaxError:
            return None
        if found_tenant != tenant_id or found_op != logical_operation_id:
            return None

        return {
            "tenant_id": tenant_id,
            "logical_operation_id": logical_operation_id,
            "action": action,
            "resource": resource,
            "payload": {"title": issue.get("title"), "body": issue.get("body")},
        }

    return verify


__all__ = ["make_sandbox_evidence_verifier"]
