"""Reconciliation for the ``create_github_issue`` governed operation.

Round 17 (test scenario 8/17/18): when the external actuator's HTTP response
is lost after the side effect genuinely occurred (or the process crashes
mid-call), the coordinator leaves the logical operation ``UNKNOWN`` (or,
after Round 18, possibly still ``DISPATCH_OWNED`` if the crash happened
before ``mark_unknown`` itself could run) — see
``mcc_core.coordinator``/``mcc_core.idempotency``. This module is the ONLY
thing that may ever move such an operation forward, and it does so purely by
LOOKING: it queries the GitHub (or mock) service for an issue whose body
carries this exact operation's marker
(``github_actuator.logical_operation_marker``), cross-checks that candidate
against the STORED logical-operation record, and only when EVERY check
passes does it resolve ``UNKNOWN``/``DISPATCH_OWNED -> EXECUTED``.

Round 18 hardening — trusted reconciliation attribution
--------------------------------------------------------

A marker substring match alone is not trusted evidence: a marker is an
opaque string embedded in a body, and treating its mere presence as proof
of completion would let a mismatched key, a foreign operation's issue, a
wrong repository, or a tampered/forged payload silently resolve the wrong
record to ``EXECUTED``. This function therefore takes the single, real,
gate-verified signed decision **token** the operation was authorized under
— never a caller-supplied bundle of loose strings that could independently
drift from what was actually admitted — and derives everything it checks
from it:

* ``logical_operation_id`` — ``token["idempotency_key"]``, used as BOTH the
  idempotency-registry key and the exact marker content; there is no
  second, independently-suppliable id anywhere in this function;
* ``action`` — ``token["action"]``, must be exactly ``create_github_issue``
  (the only action this reconciliation path understands);
* ``resource``/repository — ``token["resource_id"]``, which must equal the
  actuator's own configured lookup destination (``actuator_repo``) —
  checked BEFORE any network call, and re-checked against the repository
  field the candidate evidence itself reports;
* the authorized payload — represented by ``token["payload_hash"]``, folded
  (with action and resource) into the same ``hash_document`` binding
  ``EnforcementCoordinator`` computed at admission time, and compared
  against the STORED record's own ``binding`` (via ``idempotency.get_state``)
  — a token whose action/resource/payload_hash does not match what was
  actually admitted under this id is refused before any external call;
* the operation generation/fence — ``expected_generation``, compared
  against the stored record's current generation, so a stale caller (an
  operation that has since moved to a new generation, e.g. because it was
  already reconciled or released and re-admitted) cannot resolve a record
  it no longer describes.

Every one of these must hold. Any single mismatch — or the complete absence
of positive external evidence — leaves the record exactly as it was
(``UNKNOWN``/``DISPATCH_OWNED``, never reopened, never resolved to
``EXECUTED``, and never itself grounds for a fresh admission): this module
never creates an issue, and never applies ``resolve_unknown`` on anything
less than a full match.

Round 24 hardening — candidate CONTENT is bound to the authorized payload
--------------------------------------------------------------------------

Round 18 bound the candidate to the STORED REGISTRY RECORD's own binding
(``action``/``resource``/``payload_hash``, matched against ``record.binding``)
and to the candidate's reported repository — but never hashed the
candidate's own reported ``title``/``body`` and compared that hash against
``payload_hash``. A candidate carrying the exact right marker and the exact
right repository, but DIFFERENT content than what was ever authorized,
would previously still resolve UNKNOWN/DISPATCH_OWNED -> EXECUTED. This is
now checked explicitly, using the SAME ``hash_payload`` the Gate itself
uses: the candidate's own ``{"title", "body"}`` must hash to exactly
``payload_hash`` (extracted here from the same real, verified token every
other check in this function reads from), or reconciliation refuses,
leaving the record exactly as it was.

Round 24 hardening — the real GitHub REST API's repository field
--------------------------------------------------------------------------

The real GitHub REST API's issue response reports its repository via
``repository_url`` (e.g. ``"https://api.github.com/repos/{owner}/{repo}"``),
never a bare ``repo`` field — that field is this package's own mock
service's convenience shape. Without support for the real shape, this
reconciliation path could never resolve anything against genuine GitHub
data at all (a functional gap, not a security one -- it fails closed).
``_issue_repository_identity`` recognizes both.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from mcc_core.idempotency import ReconcileStatus
from mcc_core.signing import hash_document, hash_payload

from .github_actuator import logical_operation_marker

#: The only action this reconciliation path understands. Kept as an
#: explicit constant (rather than inferred from whatever the token says)
#: so a token naming any other action is refused by an exact equality
#: check, never silently accepted.
RECONCILABLE_ACTION = "create_github_issue"


@dataclass(frozen=True)
class ReconciliationOutcome:
    found: bool          # positive, fully-validated external evidence located
    applied: bool         # the UNKNOWN/DISPATCH_OWNED -> EXECUTED transition was actually made by THIS call
    reason: str
    issue: Optional[Dict[str, Any]] = None


def _issue_repository_identity(issue: Dict[str, Any]) -> Optional[str]:
    """Returns the ``"{owner}/{repo}"`` identity a candidate issue actually
    reports -- supporting both this package's own mock service shape (a
    direct ``repo`` field) and the real GitHub REST API shape (no ``repo``
    field at all; a ``repository_url`` of the form
    ``"https://api.github.com/repos/{owner}/{repo}"`` instead). Returns
    ``None`` if neither shape is present or parseable -- never guesses."""
    repo_field = issue.get("repo")
    if isinstance(repo_field, str) and repo_field:
        return repo_field
    repo_url = issue.get("repository_url")
    if isinstance(repo_url, str) and repo_url:
        parts = repo_url.rstrip("/").split("/")
        if len(parts) >= 2 and parts[-1] and parts[-2]:
            return f"{parts[-2]}/{parts[-1]}"
    return None


async def _find_issue_by_marker(
    *, base_url: str, repo: str, logical_operation_id: str,
    token: Optional[str] = None, timeout: float = 10.0,
) -> Optional[Dict[str, Any]]:
    """Read-only GET against the SAME ``/repos/{repo}/issues`` shape the real
    GitHub REST API and ``mock_github_service.py`` both expose. Any failure
    to definitively confirm a match (transport error, timeout, non-2xx, an
    unexpected response shape) returns ``None`` — treated identically to a
    genuine "not found", never distinguished for the purpose of authorizing
    anything further. The query itself is already scoped to ``repo`` — an
    issue filed under a different repository is never even returned."""
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
    *, idempotency: Any, token: Dict[str, Any], expected_generation: str,
    base_url: str, actuator_repo: str,
    github_api_token: Optional[str] = None, timeout: float = 10.0,
) -> ReconciliationOutcome:
    """Reconcile ONE logical operation from the single verified execution
    context (``token``) it was actually authorized under.

    ``token`` must be the real, gate-verified signed decision token this
    exact operation ran under (the same dict ``enforce_authority``/the
    coordinator used) — this function reads ``idempotency_key``, ``action``,
    ``resource_id``, ``payload_hash``, and (PR #105) ``tenant_id`` from it
    and nowhere else; it never accepts an independently-suppliable id/
    action/resource/tenant that could drift from what was actually admitted
    (Round 18's "bind verified context to the final call" requirement,
    applied symmetrically at the reconciliation end of the same operation's
    lifecycle — now including the tenant scope the operation was durably
    admitted under).

    PR #105: durable identity is tenant-scoped, so both the ``get_state``
    lookup below and the terminal ``resolve_unknown`` call are scoped to
    ``token["tenant_id"]`` — reconciliation for one tenant's operation can
    never observe or resolve a different tenant's durable record, even one
    that happens to share the same raw ``logical_operation_id``. A token
    missing ``tenant_id`` is refused before any durable lookup, exactly as a
    token missing ``idempotency_key``/``action``/``resource_id``/
    ``payload_hash`` already is.

    ``expected_generation`` is the generation observed via
    ``idempotency.get_state(logical_operation_id)`` immediately before
    calling this — the same fencing every other durable-state mutation
    uses, so a late-arriving legitimate completion of the very same dispatch
    attempt and this reconciliation call can race safely (exactly one of the
    two writes applies).

    ``actuator_repo`` is the actuator's OWN configured destination (never
    read from ``token`` alone as the sole authority) — the authorized
    resource and the lookup destination must be the identical value, or
    this refuses before any network call, exactly as
    ``github_actuator.ResourceBoundActuator`` does at dispatch time.

    Round 24: a candidate's own reported repository is recognized in either
    this package's mock service shape (``repo``) or the real GitHub REST
    API shape (``repository_url``) — see ``_issue_repository_identity`` —
    and, once repository/marker match, the candidate's own reported
    ``title``/``body`` must ALSO hash (via the same ``hash_payload`` the
    Gate uses) to exactly this ``payload_hash``. A matching marker and
    repository alone are never sufficient to resolve UNKNOWN/DISPATCH_OWNED
    to EXECUTED."""
    logical_operation_id = token.get("idempotency_key")
    action = token.get("action")
    resource = token.get("resource_id")
    payload_hash = token.get("payload_hash")
    tenant_id = token.get("tenant_id")

    if not logical_operation_id or not action or not resource or not payload_hash:
        return ReconciliationOutcome(
            found=False, applied=False,
            reason="token is missing a required binding field (idempotency_key/action/resource_id/"
                   "payload_hash); refusing to reconcile",
        )
    if not isinstance(tenant_id, str) or not tenant_id.strip():
        return ReconciliationOutcome(
            found=False, applied=False,
            reason="token is missing a valid tenant_id; refusing to reconcile (PR #105: durable "
                   "identity is tenant-scoped)",
        )
    if action != RECONCILABLE_ACTION:
        return ReconciliationOutcome(
            found=False, applied=False,
            reason=f"reconciliation only supports {RECONCILABLE_ACTION!r}, token names {action!r}",
        )
    if resource != actuator_repo:
        return ReconciliationOutcome(
            found=False, applied=False,
            reason=f"authorized resource {resource!r} does not match the actuator's configured "
                   f"destination {actuator_repo!r}; refusing before any external call",
        )

    expected_binding = hash_document({"action": action, "resource": resource, "payload_hash": payload_hash})

    record = await idempotency.get_state(logical_operation_id, tenant_id=tenant_id)
    if record is None:
        return ReconciliationOutcome(
            found=False, applied=False, reason="no stored logical-operation record for this id",
        )
    if record.generation != expected_generation:
        return ReconciliationOutcome(
            found=False, applied=False,
            reason="observed generation no longer holds this record; refusing to reconcile",
        )
    if record.binding != expected_binding:
        return ReconciliationOutcome(
            found=False, applied=False,
            reason="token action/resource/payload does not match the stored logical-operation "
                   "binding; refusing to reconcile",
        )

    issue = await _find_issue_by_marker(
        base_url=base_url, repo=actuator_repo, logical_operation_id=logical_operation_id,
        token=github_api_token, timeout=timeout,
    )
    if issue is None:
        return ReconciliationOutcome(
            found=False, applied=False,
            reason="no positive external evidence found; operation left pending",
        )
    candidate_repo = _issue_repository_identity(issue)
    if candidate_repo != actuator_repo:
        # Defense in depth: the lookup query is already scoped to
        # actuator_repo, so this should be unreachable against a real or
        # the mock GitHub service -- but a candidate whose own reported
        # repository disagrees is never trusted regardless. Recognizes both
        # this package's mock service shape (a "repo" field) and the real
        # GitHub REST API shape ("repository_url").
        return ReconciliationOutcome(
            found=False, applied=False,
            reason="candidate evidence's own repository field does not match the authorized "
                   "resource; refusing to reconcile",
        )

    # Round 24: the candidate's own reported CONTENT must hash to the exact
    # payload_hash this operation was authorized under -- a matching marker
    # and repository alone are not sufficient. Marker text is data, never
    # authority; only the real Gate-verified payload_hash establishes what
    # content was actually signed for, and this is the same hash_payload
    # function the Gate itself uses.
    candidate_content = {"title": issue.get("title"), "body": issue.get("body")}
    if hash_payload(candidate_content) != payload_hash:
        return ReconciliationOutcome(
            found=False, applied=False,
            reason="candidate evidence's own content does not hash to the authorized "
                   "payload_hash; refusing to reconcile",
        )

    result_ref = hash_document({
        "issue_number": issue.get("number"), "html_url": issue.get("html_url"), "repo": candidate_repo,
    })
    result = await idempotency.resolve_unknown(
        logical_operation_id, expected_generation=expected_generation, result_ref=result_ref,
        tenant_id=tenant_id,
    )
    if result.status == ReconcileStatus.RESOLVED:
        return ReconciliationOutcome(found=True, applied=True, reason=result.reason, issue=issue)
    # Fully-validated positive evidence exists, but this call did not itself
    # apply the transition -- either a racing writer already resolved it
    # (ALREADY_EXECUTED), the state moved on for another reason (NOT_PENDING/
    # STALE_GENERATION), or the record disappeared (NOT_FOUND/ERROR). None of
    # these is "found=False": the external evidence genuinely matched.
    return ReconciliationOutcome(found=True, applied=False, reason=result.reason, issue=issue)


__all__ = ["RECONCILABLE_ACTION", "ReconciliationOutcome", "reconcile_github_issue_operation"]
