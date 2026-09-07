"""Round 21 — the ``create_github_issue`` request contract: the strict
payload schema, the reconciliation-marker syntax, and the operation-context
coherence rules built on both.

This lives in its OWN module, deliberately separate from
``github_actuator.py``, so the protected pipeline boundary (``pipeline.py``)
can validate the schema and operation-context coherence itself,
independently of any actuator-preparation helper, WITHOUT importing the
actuator — ``pipeline.py`` is architecturally forbidden from importing
``github_actuator`` at all (see
``tests/test_gpt6_astra_reference_architecture_guards.py::
test_pipeline_module_never_imports_the_actuator_directly``). Everything here
still lives in the REFERENCE INTEGRATION, never in domain-neutral
``mcc_core`` — these are GitHub-specific rules for the one real actuator
this package ships, not a generic governance primitive.

Two closed contracts:

1. **Payload schema** (Round 21 Blocker 1). ``create_github_issue`` accepts
   EXACTLY ``title`` (required, non-empty string) and ``body`` (optional,
   materialized to ``""`` if absent) — no other field. Validated BEFORE
   canonicalization, attestation, hashing, or authorization, so an
   authorized field can never silently disappear between what gets signed
   and what the actuator ultimately sends: the schema guarantees the two
   are always the identical set of keys.

2. **Marker syntax and operation-context coherence** (Round 21 Blocker 2).
   The reconciliation marker is reserved syntax: a raw body must never
   already contain it, an operation id must never be able to break out of
   or inject its fixed delimiters, and a payload presented at a protected
   boundary must carry EXACTLY ONE well-formed marker naming the EXACT
   ``logical_operation_id`` being presented for admission at that boundary.
   Marker text is DATA, never authority — none of this establishes
   signature validity or trust; the real Gate still performs the actual
   cryptographic verification independently.
"""

from __future__ import annotations

import re
from typing import Any, Dict

#: The one real actuator action this reference integration ships. Named
#: here (not only in ``_localstack.py``/``adversarial.py``) so ``pipeline.py``
#: can recognize it without depending on either of those higher-level
#: modules.
GITHUB_ISSUE_ACTION = "create_github_issue"

LOGICAL_OPERATION_MARKER_PREFIX = "<!-- mcc-logical-operation-id: "
LOGICAL_OPERATION_MARKER_SUFFIX = " -->"


# ---------------------------------------------------------------------------
# 1. Payload schema.
# ---------------------------------------------------------------------------


class GitHubIssuePayloadError(Exception):
    """Raised, before any attestation/authorization/network call, when a
    proposal's payload for ``create_github_issue`` does not conform to the
    reference actuator's own strict request schema: exactly ``title``
    (required, non-empty string) and ``body`` (optional string, materialized
    to ``""`` if absent) — no other field is ever accepted. An unsupported
    field is a hard rejection, never silently discarded, and a value is
    never coerced (e.g. an int title is never stringified)."""


_GITHUB_ISSUE_ALLOWED_FIELDS = frozenset({"title", "body"})


def validate_github_issue_request_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Returns a NEW dict — ``payload`` itself is never mutated — with
    EXACTLY ``title``/``body``, ``body`` materialized to ``""`` if it was
    absent. Raises :class:`GitHubIssuePayloadError` on: a non-dict payload;
    any field other than title/body (e.g. ``labels``); a missing,
    non-string, or empty title; a non-string body. This is the ONLY place
    an ingress default (``body`` = ``""``) is ever materialized — BEFORE
    binding, never coerced or defaulted afterward."""
    if not isinstance(payload, dict):
        raise GitHubIssuePayloadError(f"payload must be an object, got {type(payload).__name__}")
    unsupported = set(payload.keys()) - _GITHUB_ISSUE_ALLOWED_FIELDS
    if unsupported:
        raise GitHubIssuePayloadError(
            f"payload carries unsupported field(s) {sorted(unsupported)} -- "
            f"{GITHUB_ISSUE_ACTION!r} accepts only {sorted(_GITHUB_ISSUE_ALLOWED_FIELDS)}; "
            "an unsupported field is rejected, never silently discarded"
        )
    title = payload.get("title")
    if not isinstance(title, str) or not title.strip():
        raise GitHubIssuePayloadError("title must be a non-empty string")
    body = payload.get("body", "")
    if not isinstance(body, str):
        raise GitHubIssuePayloadError("body must be a string")
    return {"title": title, "body": body}


# ---------------------------------------------------------------------------
# 2. Marker syntax.
# ---------------------------------------------------------------------------


class MarkerSyntaxError(Exception):
    """Raised, before any attestation/authorization/network call, when a
    payload's body carries a pre-existing marker, a malformed use of the
    reserved marker syntax, or when a logical_operation_id itself is unsafe
    to embed in a marker (could break out of or inject the reserved
    delimiters). Never silently deleted, replaced, or worked around."""


class OperationContextMismatchError(Exception):
    """Raised at a protected reference boundary when the SINGLE marker a
    payload's body actually carries does not name the exact
    logical_operation_id being presented for durable admission/
    authorization at that boundary — i.e. the marker and the id used for
    admission/the token/dispatch ownership have drifted apart. Reading the
    marker never establishes authority or signature validity by itself:
    this check only proves (or disproves) INTERNAL coherence between the
    payload a caller built and the id it is presenting alongside it. The
    real Gate/signature verification is unaffected and still mandatory."""


#: A logical_operation_id embedded in a marker must be safe to place
#: verbatim between the fixed prefix/suffix above without being able to
#: break out of them (inject a fake closing/opening sequence) or otherwise
#: make the marker ambiguous to parse back out. This is deliberately a
#: BLOCKLIST, not a narrow character whitelist: this package's own ids are
#: often long, descriptive, human-readable strings (built from a scenario
#: name, a proposed resource, or free-text carried through a test) -- only
#: the substrings that could actually break out of or inject the fixed
#: ``<!-- mcc-logical-operation-id: ``/`` -->`` delimiters are refused.
_UNSAFE_MARKER_SUBSTRINGS = (LOGICAL_OPERATION_MARKER_SUFFIX.strip(), "<!--", "\n", "\r")

#: The exact, closed shape a single well-formed marker occurrence must take.
#: A non-greedy ``.+?`` (never matching a newline, since a safe id can never
#: contain one) captures exactly the id content up to the FIRST following
#: suffix -- unambiguous as long as the id itself cannot reintroduce the
#: suffix sequence, which ``validate_operation_id_for_marker`` guarantees.
_MARKER_RE = re.compile(re.escape(LOGICAL_OPERATION_MARKER_PREFIX) + r"(.+?)" + re.escape(LOGICAL_OPERATION_MARKER_SUFFIX))


def validate_operation_id_for_marker(logical_operation_id: str) -> str:
    """Fail-closed: a logical_operation_id that could break out of or
    inject the marker's fixed delimiters (or is empty/not a string) is
    refused before it is ever embedded in a marker. Returns it unchanged on
    success."""
    if not isinstance(logical_operation_id, str) or not logical_operation_id:
        raise MarkerSyntaxError(
            f"logical_operation_id {logical_operation_id!r} must be a non-empty string "
            "to embed in a reconciliation marker"
        )
    hit = [s for s in _UNSAFE_MARKER_SUBSTRINGS if s in logical_operation_id]
    if hit:
        raise MarkerSyntaxError(
            f"logical_operation_id {logical_operation_id!r} contains substring(s) {hit} "
            "that could break out of or inject the reconciliation marker's reserved "
            "delimiters -- refusing to embed it"
        )
    return logical_operation_id


def logical_operation_marker(logical_operation_id: str) -> str:
    validate_operation_id_for_marker(logical_operation_id)
    return f"{LOGICAL_OPERATION_MARKER_PREFIX}{logical_operation_id}{LOGICAL_OPERATION_MARKER_SUFFIX}"


def reject_preexisting_marker(body: str) -> None:
    """Fail-closed: a raw, caller-supplied body that already contains
    anything shaped like the reserved marker syntax — a complete,
    well-formed marker, OR merely the bare prefix/suffix substring on its
    own (a malformed/partial use of the reserved syntax) — is refused
    BEFORE this package ever appends its own marker. Silently appending a
    second marker on top of an existing (or partial/malformed) one is
    exactly the Round 21 counterexample this closes: a caller must never be
    able to submit a body that ends up carrying more than one marker, or a
    marker this package did not itself construct for this exact call. An
    existing marker is never silently deleted or replaced."""
    if not isinstance(body, str):
        return
    if LOGICAL_OPERATION_MARKER_PREFIX in body or LOGICAL_OPERATION_MARKER_SUFFIX in body:
        raise MarkerSyntaxError(
            "payload body already contains reserved reconciliation-marker syntax -- "
            "refusing before this package appends its own marker"
        )


def build_marked_payload(payload: Dict[str, Any], *, logical_operation_id: str) -> Dict[str, Any]:
    """Returns a NEW dict — ``payload`` itself is never mutated — whose
    ``body`` has EXACTLY ONE, well-formed reconciliation marker appended.

    Fail-closed BEFORE appending anything: the id must be safe to embed
    (:func:`validate_operation_id_for_marker`), and the existing body must
    not already carry any marker-shaped syntax
    (:func:`reject_preexisting_marker`). Round 19/21: this must be called
    BEFORE the payload is canonicalized, attested, hashed, or authorized —
    never afterward."""
    validate_operation_id_for_marker(logical_operation_id)
    body = payload.get("body", "") if isinstance(payload, dict) else ""
    reject_preexisting_marker(body)
    marked = dict(payload)
    marked["body"] = f"{body}\n\n{logical_operation_marker(logical_operation_id)}"
    return marked


def extract_single_marker_operation_id(body: str) -> str:
    """Returns the logical_operation_id named by the SINGLE well-formed
    marker ``body`` carries. Fail-closed: raises :class:`MarkerSyntaxError`
    if there is no marker, more than one, or anything that looks like a
    partial/malformed/duplicated marker occurrence — never guesses, never
    picks "the first" out of several candidates."""
    if not isinstance(body, str):
        raise MarkerSyntaxError("payload body must be a string to contain a marker")
    matches = _MARKER_RE.findall(body)
    prefix_count = body.count(LOGICAL_OPERATION_MARKER_PREFIX)
    suffix_count = body.count(LOGICAL_OPERATION_MARKER_SUFFIX)
    if len(matches) != 1 or prefix_count != 1 or suffix_count != 1:
        raise MarkerSyntaxError(
            f"expected exactly one well-formed reconciliation marker in the payload "
            f"body; found {len(matches)} well-formed match(es), {prefix_count} prefix "
            f"occurrence(s), {suffix_count} suffix occurrence(s)"
        )
    return matches[0]


def require_coherent_marker_context(payload: Dict[str, Any], *, logical_operation_id: str) -> None:
    """Fail-closed context-coherence check (Round 21 requirement 1/3): the
    payload's body must carry EXACTLY ONE well-formed marker, and it must
    name EXACTLY ``logical_operation_id`` — the SAME id being presented for
    durable admission/the token at THIS call. ``logical_operation_id``
    always comes from the caller's own explicit argument (durable
    admission's id, or the real signed token's ``idempotency_key``) — never
    derived from the payload itself, which would be circular.

    This is marker-syntax/consistency validation only — it establishes
    nothing about signatures, trust, or authority; the real Gate still
    performs the actual cryptographic verification."""
    if not isinstance(payload, dict):
        raise MarkerSyntaxError("payload must be an object to check marker context coherence")
    marker_id = extract_single_marker_operation_id(payload.get("body", ""))
    if marker_id != logical_operation_id:
        raise OperationContextMismatchError(
            f"payload's marker names logical_operation_id {marker_id!r}, but this call "
            f"is presenting {logical_operation_id!r} for durable admission/authorization "
            "-- refusing before any attestation/authority/actuator call"
        )


def prepare_complete_github_issue_payload(payload: Dict[str, Any], *, logical_operation_id: str) -> Dict[str, Any]:
    """The complete Round 21 outbound-payload preparation step for
    ``create_github_issue``: validate the strict request schema FIRST (so
    an unsupported field is rejected before anything else, and ``body``'s
    ingress default is materialized before binding), THEN embed the
    reconciliation marker. Both happen BEFORE canonicalization, attestation,
    hashing, or authorization — this is the complete, final outbound
    payload from this point forward; nothing downstream may add, remove,
    normalize, or replace a field."""
    validated = validate_github_issue_request_payload(payload)
    return build_marked_payload(validated, logical_operation_id=logical_operation_id)


__all__ = [
    "GITHUB_ISSUE_ACTION",
    "LOGICAL_OPERATION_MARKER_PREFIX",
    "LOGICAL_OPERATION_MARKER_SUFFIX",
    "GitHubIssuePayloadError",
    "validate_github_issue_request_payload",
    "MarkerSyntaxError",
    "OperationContextMismatchError",
    "validate_operation_id_for_marker",
    "logical_operation_marker",
    "reject_preexisting_marker",
    "build_marked_payload",
    "extract_single_marker_operation_id",
    "require_coherent_marker_context",
    "prepare_complete_github_issue_payload",
]
