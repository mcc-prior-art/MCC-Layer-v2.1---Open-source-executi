"""Round 23 remediation — marker-safety validation on the EXTERNAL expected
operation identity, unavoidable at the actual protected boundary, for the
GPT-6 Astra reference integration's ``create_github_issue`` action.

Round 21 introduced ``issue_contract.validate_operation_id_for_marker``,
which rejects a ``logical_operation_id`` containing marker-breaking syntax
(``-->``, ``<!--``, a newline, a carriage return) — but that validation was
only ever invoked from ``build_marked_payload`` (the WRITE side, reached
only through ``governed_call.prepare_marked_call``). A direct caller who
skips ``prepare_marked_call`` entirely and hand-constructs its own proposal/
payload/token could still present an unsafe id straight to
``pipeline.run_positive_path``/``issue_authority``/``enforce_authority``:
``issue_contract.require_coherent_marker_context`` (the READ/acceptance
side, the only marker check those three functions actually call) never
independently validated the id it was comparing against — only whether it
matched whatever the payload's own marker happened to say.

This file proves that gap is closed: the EXTERNAL expected identity
(``run_positive_path``/``issue_authority``'s explicit ``logical_operation_id``
argument; ``enforce_authority``'s real, signed ``token["idempotency_key"]``)
is now validated BEFORE the payload's marker is even inspected, so an unsafe
id is refused at all three protected boundaries regardless of what a
hand-constructed body does or does not contain — and, symmetrically, that
any id actually accepted through protected execution is guaranteed safe for
``reconciliation.py``'s later marker reconstruction too.

None of these tests route through ``governed_call.prepare_marked_call`` or
``issue_contract.build_marked_payload`` — every proposal/token/payload below
is hand-constructed, exactly modeling a caller who bypasses the preparation
helper entirely.
"""

from __future__ import annotations

import asyncio
import json

import pytest

from mcc_core import IdempotencyState
from mcc_core.signing import hash_payload

from examples.gpt6_astra_reference._localstack import ACTION, ACTOR, LocalAstraDemoStack
from examples.gpt6_astra_reference.github_actuator import (
    GitHubActuatorConfig,
    GitHubIssueActuator,
    VerifiedDispatchSlot,
    logical_operation_marker,
)
from examples.gpt6_astra_reference.issue_contract import (
    LOGICAL_OPERATION_MARKER_PREFIX,
    LOGICAL_OPERATION_MARKER_SUFFIX,
    MarkerSyntaxError,
    require_coherent_marker_context,
    validate_operation_id_for_marker,
)
from examples.gpt6_astra_reference.mock_github_service import recorded_issues
from examples.gpt6_astra_reference.models import AstraProposal
from examples.gpt6_astra_reference.pipeline import (
    IssuedAuthority, enforce_authority, issue_authority, obtain_attestation, run_positive_path,
)

run = asyncio.run
DEMO_REPO = "owner/mcc-astra-demo-sandbox"

#: The four mandatory unsafe ids the task requires coverage for.
UNSAFE_IDS = [
    "op-->breakout",
    "op<!--inject",
    "op\nbreak",
    "op\rbreak",
]


def _raw_marker_text(operation_id: str) -> str:
    """Constructs marker text by direct string interpolation -- NEVER via
    ``logical_operation_marker()``/``build_marked_payload()``, which would
    themselves raise for an unsafe id. This is exactly what a caller who
    hand-crafts a body, bypassing every helper this package provides, could
    produce: a body whose marker text superficially "names" the unsafe id."""
    return f"{LOGICAL_OPERATION_MARKER_PREFIX}{operation_id}{LOGICAL_OPERATION_MARKER_SUFFIX}"


class _CountingUpstream:
    def __init__(self, actuator) -> None:
        self._actuator = actuator
        self.calls = 0

    def expect(self, *, action: str, resource: str, payload_hash: str) -> None:
        self._actuator.expect(action=action, resource=resource, payload_hash=payload_hash)

    async def __call__(self, action: str, payload):
        self.calls += 1
        return await self._actuator(action, payload)


def _build_dispatch_slot(stack: LocalAstraDemoStack) -> VerifiedDispatchSlot:
    raw = GitHubIssueActuator(GitHubActuatorConfig.from_env({
        "MCC_ASTRA_DEMO_MODE": "live",
        "MCC_ASTRA_GITHUB_REPO": stack.demo_repo,
        "MCC_ASTRA_GITHUB_BASE_URL": stack.github_base_url,
    }))
    return VerifiedDispatchSlot(raw, authorized_resource=DEMO_REPO)


def _pre_actuation_audit_entries(stack: LocalAstraDemoStack) -> list:
    entries = []
    try:
        fh = open(stack._audit_path, "r", encoding="utf-8")
    except FileNotFoundError:
        # Nothing was ever recorded -- a rejection this early never even
        # creates the audit file.
        return entries
    with fh:
        for line in fh:
            if not line.strip():
                continue
            entry = json.loads(line)
            if entry.get("kind") == "pre_actuation":
                entries.append(entry)
    return entries


def _assert_zero_side_effects(stack: LocalAstraDemoStack, counting: "_CountingUpstream", unsafe_id: str) -> None:
    assert counting.calls == 0
    assert recorded_issues() == []
    assert run(stack.coordinator.idempotency.get_state(unsafe_id)) is None
    assert not any(e.get("idempotency_key") == unsafe_id for e in _pre_actuation_audit_entries(stack))


#: The distinguishing substring of ``validate_operation_id_for_marker``'s
#: own rejection message -- asserting on this (rather than merely
#: ``pytest.raises(MarkerSyntaxError)``) proves the id-SAFETY check itself
#: fired, not some other, coincidental ``MarkerSyntaxError`` (e.g. "no
#: marker found in the body"), which -- for an id containing a raw newline
#: or carriage return -- could otherwise raise for an unrelated reason
#: (Python's default, non-DOTALL ``.`` cannot span a literal ``\n``/``\r``,
#: so a body with no marker at all "coincidentally" also raises
#: ``MarkerSyntaxError`` regardless of whether the id-safety gate exists).
#: Every assertion below pins the message to rule that ambiguity out.
_ID_SAFETY_MESSAGE_FRAGMENT = "break out of or inject the reconciliation marker"


def _assert_id_safety_rejection(excinfo) -> None:
    assert _ID_SAFETY_MESSAGE_FRAGMENT in str(excinfo.value), (
        f"expected the id-safety check's own message, got: {excinfo.value!r}"
    )


# ---------------------------------------------------------------------------
# Unit-level: validate_operation_id_for_marker / require_coherent_marker_context
# reject every mandatory unsafe id directly -- no pipeline involved.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("unsafe_id", UNSAFE_IDS)
def test_validate_operation_id_for_marker_rejects_every_mandatory_unsafe_id(unsafe_id):
    with pytest.raises(MarkerSyntaxError):
        validate_operation_id_for_marker(unsafe_id)


@pytest.mark.parametrize("unsafe_id", UNSAFE_IDS)
def test_require_coherent_marker_context_rejects_unsafe_id_even_with_no_marker_present(unsafe_id):
    """The id itself is refused BEFORE the payload's body is even
    inspected -- proven here with a payload that carries no marker at all
    (which, on its own, would ALSO raise ``MarkerSyntaxError`` for an
    unrelated "no marker found" reason), by pinning the raised message to
    the id-safety check's own wording specifically."""
    with pytest.raises(MarkerSyntaxError) as excinfo:
        require_coherent_marker_context({"title": "t", "body": "no marker here at all"}, logical_operation_id=unsafe_id)
    _assert_id_safety_rejection(excinfo)


@pytest.mark.parametrize("unsafe_id", [i for i in UNSAFE_IDS if "\n" not in i and "\r" not in i])
def test_require_coherent_marker_context_rejects_unsafe_id_even_when_marker_text_matches(unsafe_id):
    """The adversarial reproduction of the actual Round 23 bypass: a body
    hand-crafted (never through ``build_marked_payload``) so its marker text
    superficially NAMES the unsafe id -- coherence alone would have
    accepted this. The id-safety check must still refuse it."""
    body = f"pre-existing text\n\n{_raw_marker_text(unsafe_id)}"
    with pytest.raises(MarkerSyntaxError) as excinfo:
        require_coherent_marker_context({"title": "t", "body": body}, logical_operation_id=unsafe_id)
    _assert_id_safety_rejection(excinfo)


# ---------------------------------------------------------------------------
# Direct-bypass, protected-boundary tests. NONE of these call
# governed_call.prepare_marked_call or issue_contract.build_marked_payload --
# every proposal/token/payload is hand-constructed.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("unsafe_id", UNSAFE_IDS)
def test_run_positive_path_rejects_unsafe_id_direct_bypass(unsafe_id):
    with LocalAstraDemoStack(demo_repo=DEMO_REPO) as stack:
        counting = _CountingUpstream(_build_dispatch_slot(stack))
        stack.upstream = counting
        proposal = AstraProposal(action=ACTION, resource=DEMO_REPO, payload={"title": "t", "body": "b"})

        with pytest.raises(MarkerSyntaxError) as excinfo:
            run(run_positive_path(
                stack.service, mandate=stack.mandate, actor=ACTOR, proposal=proposal, attestation=None,
                logical_operation_id=unsafe_id,
            ))
        _assert_id_safety_rejection(excinfo)
        _assert_zero_side_effects(stack, counting, unsafe_id)


@pytest.mark.parametrize("unsafe_id", UNSAFE_IDS)
def test_issue_authority_rejects_unsafe_id_before_token_issuance_direct_bypass(unsafe_id):
    with LocalAstraDemoStack(demo_repo=DEMO_REPO) as stack:
        counting = _CountingUpstream(_build_dispatch_slot(stack))
        stack.upstream = counting
        proposal = AstraProposal(action=ACTION, resource=DEMO_REPO, payload={"title": "t", "body": "b"})

        with pytest.raises(MarkerSyntaxError) as excinfo:
            run(issue_authority(
                stack.service, mandate=stack.mandate, actor=ACTOR, proposal=proposal, attestation=None,
                logical_operation_id=unsafe_id,
            ))
        _assert_id_safety_rejection(excinfo)
        _assert_zero_side_effects(stack, counting, unsafe_id)


@pytest.mark.parametrize("unsafe_id", UNSAFE_IDS)
def test_enforce_authority_rejects_genuinely_signed_token_with_unsafe_idempotency_key(unsafe_id):
    """A REAL, genuinely signed token (would pass the Gate's own signature
    and hash checks fine) whose ``idempotency_key`` is itself unsafe --
    minted directly via ``stack.engine.issue_token``, bypassing
    ``issue_authority``'s own check on purpose, to prove
    ``enforce_authority``'s check is independent of it. Must be refused
    BEFORE ``coordinator.enforce`` (durable admission) is ever reached."""
    with LocalAstraDemoStack(demo_repo=DEMO_REPO) as stack:
        counting = _CountingUpstream(_build_dispatch_slot(stack))
        stack.upstream = counting

        canonical = {"title": "t", "body": "b"}
        token = stack.engine.issue_token(
            verdict="ALLOW", subject=ACTOR, action=ACTION, payload=canonical,
            actor_id=ACTOR, resource_id=DEMO_REPO, auth_claims={},
            idempotency_key=unsafe_id,
        )
        assert token["payload_hash"] == hash_payload(canonical)  # a real, well-formed, signed token
        issued = IssuedAuthority(token=token, canonical_payload=canonical, evidence_digest=None)

        with pytest.raises(MarkerSyntaxError) as excinfo:
            run(enforce_authority(
                stack.service, issued=issued, actor=ACTOR, resource=DEMO_REPO, action=ACTION, attestation=None,
            ))
        _assert_id_safety_rejection(excinfo)
        _assert_zero_side_effects(stack, counting, unsafe_id)


# ---------------------------------------------------------------------------
# Requirement 6: any operation id ACCEPTED by protected execution is also
# safe for reconciliation.py's marker reconstruction -- and, symmetrically,
# an id rejected at the protected boundary is rejected identically by
# reconciliation's own marker construction.
# ---------------------------------------------------------------------------


def test_id_accepted_by_protected_execution_is_safe_for_reconciliation_marker_reconstruction():
    """Runs one real, full golden-path operation (real attestation/
    authority/Gate/coordinator/actuator/mock HTTP receiver) and proves the
    SAME id ``reconciliation.py`` would later use
    (``logical_operation_marker(token["idempotency_key"])``, see
    ``reconciliation.reconcile_github_issue_operation``) reconstructs
    without error, and reproduces byte-for-byte the marker actually present
    in the real outbound body."""
    with LocalAstraDemoStack(demo_repo=DEMO_REPO) as stack:
        from examples.gpt6_astra_reference.governed_call import prepare_marked_call

        logical_operation_id = "op-safe-for-reconciliation-1"
        slot = _build_dispatch_slot(stack)
        counting = _CountingUpstream(slot)
        stack.upstream = counting

        proposal = AstraProposal(action=ACTION, resource=DEMO_REPO, payload={"title": "t", "body": "b"})
        marked = prepare_marked_call(
            proposal, logical_operation_id=logical_operation_id,
            canonical_payload_fn=stack.profiles.for_action(ACTION).canonical_payload,
            actuator=counting,
        )
        canonical = stack.profiles.for_action(ACTION).canonical_payload(marked.payload)
        att = run(obtain_attestation(stack.attester, proposal=marked, canonical_payload=canonical))
        issued = run(issue_authority(
            stack.service, mandate=stack.mandate, actor=ACTOR, proposal=marked,
            attestation=att.raw_attestation, logical_operation_id=logical_operation_id,
        ))
        outcome = run(enforce_authority(
            stack.service, issued=issued, actor=ACTOR, resource=DEMO_REPO, action=ACTION,
            attestation=att.raw_attestation,
        ))
        assert outcome.status == "EXECUTED"

        # The exact identity reconciliation.py would use: token["idempotency_key"].
        accepted_id = issued.token["idempotency_key"]
        assert accepted_id == logical_operation_id

        # Reconstructing the marker from that accepted id never raises --
        # and reproduces exactly what was actually sent.
        reconstructed = logical_operation_marker(accepted_id)
        issues = recorded_issues()
        assert len(issues) == 1
        assert reconstructed in issues[0]["body"]


@pytest.mark.parametrize("unsafe_id", UNSAFE_IDS)
def test_id_rejected_at_protected_boundary_is_also_rejected_by_reconciliation_marker_construction(unsafe_id):
    """The contrapositive, made explicit: every id the protected boundary
    refuses is refused by the IDENTICAL check reconciliation's own marker
    construction (``logical_operation_marker`` -> ``build_marked_payload``
    both call ``validate_operation_id_for_marker``) would apply -- there is
    one single validation gate, not two independently-maintained ones that
    could drift apart."""
    with pytest.raises(MarkerSyntaxError):
        logical_operation_marker(unsafe_id)
