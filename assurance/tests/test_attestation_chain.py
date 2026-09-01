"""PR-5 -- Independent Assurance of the Attestation-to-Execution Chain.

Adversarial end-to-end tests through the REAL production classes for the
PR-1->4 chain:

    Independent Attester Service (real, separate OS process)
        -> raw EvidenceAttestation
        -> real Gateway subprocess (GovernanceService / PreExecutionControl,
           unmodified since PR-2)
        -> DecisionEngine (signed, evidence-bound decision token, PR-3,
           unmodified)
        -> ExecutionGate (exact evidence-digest enforcement, PR-3,
           unmodified)
        -> EnforcementCoordinator -> real external-effect sink

Every negative case proves BOTH the reported outcome is non-executable AND
the independently observed external-effect counter never advances -- the
SAME dual-oracle discipline Workstream A/C already use, applied to the
attestation dimension those workstreams predate and do not cover (see
``docs/ATTESTATION_INDEPENDENT_ASSURANCE.md`` for the full gap matrix this
file closes).

This module reaches the SUT only through
``assurance.sut.attestation_harness`` over real HTTP -- it never imports
``mcc_core``/``gateway``/``mcc_attestation``/``mcc_attester_service``
directly (enforced by ``test_boundary_guards.py``).
"""

from __future__ import annotations

import time
import uuid
from typing import Any, Dict

import pytest

from assurance.sut.attestation_harness import (
    ATTESTED_ACTION,
    ATTESTED_RESOURCE,
    build_attestation_system_under_test,
)

ACTOR = "agent/attestation-assurance-bot"


def _context(**overrides: Any) -> Dict[str, Any]:
    base = {"recipient": "customer-attn-1", "message": "assurance-attestation-probe",
            "priority": 2, "channel": "email", "correlation_id": str(uuid.uuid4())}
    base.update(overrides)
    return base


@pytest.fixture(scope="module")
def asut():
    with build_attestation_system_under_test() as a:
        yield a


@pytest.fixture()
def mandate(asut):
    return asut.issue_mandate(subject=ACTOR, action_scope=[ATTESTED_ACTION],
                               resource_scope=[ATTESTED_RESOURCE])


# ---------------------------------------------------------------------------
# Positive control: exactly one legitimate operation traverses the full
# chain and actuates exactly once.
# ---------------------------------------------------------------------------


def test_positive_baseline_full_chain_executes_exactly_once(asut, mandate):
    before = asut.gateway_notification_receipt_count()
    ctx = _context()
    att = asut.get_attestation(context=ctx)

    result = asut.execute_with_mandate_and_attestation(
        mandate=mandate, attestation=att, actor=ACTOR, context=ctx,
    )

    assert result["status"] == "EXECUTED", result
    assert result["decision"] == "ALLOW"
    assert asut.gateway_notification_receipt_count() == before + 1


# ---------------------------------------------------------------------------
# A. Forged attestation: wrong signing key / untrusted kid / caller-
#    manufactured "verified" state.
# ---------------------------------------------------------------------------


def test_a1_forged_attestation_untrusted_key_blocked_no_actuation(asut, mandate):
    """A syntactically valid, correctly bound attestation signed by a key
    NEVER registered in the real Gateway's attestation trust config. This
    is also the concrete evidence for Invariant K (attester trust
    removal/unknown attester): the real trust-store semantics ARE
    registration-based -- an attester that was never registered is
    indistinguishable, to Control, from one that was removed. There is no
    separate live "revocation" mechanism for Attester trust in the current
    architecture (unlike mandates, which DO have a real revoke endpoint --
    see test_k below) -- this test IS the accurate evidence for that
    boundary, not a placeholder for a feature that does not exist."""
    before = asut.gateway_notification_receipt_count()
    ctx = _context()
    forged = asut.forge_attestation(context=ctx)

    result = asut.execute_with_mandate_and_attestation(
        mandate=mandate, attestation=forged, actor=ACTOR, context=ctx,
    )

    assert result["status"] == "BLOCKED", result
    assert "ATTESTER_UNTRUSTED" in result["reason"]
    assert asut.gateway_notification_receipt_count() == before


def test_a2_tampered_signature_covered_claim_blocked_no_actuation(asut, mandate):
    """A GENUINELY signed attestation with one claim rewritten after the
    fact, without re-signing -- the signature no longer covers the mutated
    field."""
    before = asut.gateway_notification_receipt_count()
    ctx = _context()
    att = asut.get_attestation(context=ctx)
    tampered = asut.tamper_attestation(att, claims={**att["claims"], "risk_class": "high"})

    result = asut.execute_with_mandate_and_attestation(
        mandate=mandate, attestation=tampered, actor=ACTOR, context=ctx,
    )

    assert result["status"] == "BLOCKED", result
    assert asut.gateway_notification_receipt_count() == before


def test_a3_caller_manufactured_verified_field_rejected_structurally(asut, mandate):
    """A caller cannot smuggle a self-declared 'verified'/'trusted' flag
    into the raw attestation document to shortcut Control's own
    verification -- MCC-AT-001's EvidenceAttestation schema is CLOSED
    (``_ALL_ALLOWED_FIELDS``): any undeclared field makes the WHOLE
    document structurally malformed, rejected before signature/trust/
    binding checks even run. This is a DIFFERENT boundary from PR-4's own
    request-schema rejection (tested at the Attester's HTTP surface in
    tests/test_attester_service.py) -- this one is PreExecutionControl's
    own defense, reached here via the real Gateway HTTP surface, proving
    the SAME property holds independently at the SECOND boundary."""
    before = asut.gateway_notification_receipt_count()
    ctx = _context()
    att = asut.get_attestation(context=ctx)
    poisoned = dict(att)
    poisoned["verified"] = True

    result = asut.execute_with_mandate_and_attestation(
        mandate=mandate, attestation=poisoned, actor=ACTOR, context=ctx,
    )

    assert result["status"] == "BLOCKED", result
    assert asut.gateway_notification_receipt_count() == before


# ---------------------------------------------------------------------------
# B. Wrong action binding: valid (TRUSTED, genuinely signed) evidence for
#    action A cannot authorize action B.
# ---------------------------------------------------------------------------


def test_b_wrong_action_binding_blocked_no_actuation(asut, mandate):
    """A GENUINELY signed, trust-store-verified attestation -- but bound
    (via action_hash) to a DIFFERENT action string than the one actually
    being executed. Uses the real, trusted Attester (not a forgery) so
    this isolates the action-binding check specifically, independent of
    signature/trust."""
    before = asut.gateway_notification_receipt_count()
    ctx = _context()
    wrong_action_att = asut.get_attestation(action="a_completely_different_action", context=ctx)

    result = asut.execute_with_mandate_and_attestation(
        mandate=mandate, attestation=wrong_action_att, actor=ACTOR, context=ctx,
    )

    assert result["status"] == "BLOCKED", result
    assert "ATTESTATION_ACTION_MISMATCH" in result["reason"]
    assert asut.gateway_notification_receipt_count() == before


# ---------------------------------------------------------------------------
# C. Wrong payload binding: valid evidence for payload A cannot authorize
#    mutated payload B.
# ---------------------------------------------------------------------------


def test_c_wrong_payload_binding_blocked_no_actuation(asut, mandate):
    before = asut.gateway_notification_receipt_count()
    ctx_a = _context(message="original-content")
    att_for_a = asut.get_attestation(context=ctx_a)

    ctx_b = _context(message="mutated-content-different-from-what-was-attested")
    result = asut.execute_with_mandate_and_attestation(
        mandate=mandate, attestation=att_for_a, actor=ACTOR, context=ctx_b,
    )

    assert result["status"] == "BLOCKED", result
    assert "ATTESTATION_PAYLOAD_MISMATCH" in result["reason"]
    assert asut.gateway_notification_receipt_count() == before


# ---------------------------------------------------------------------------
# D. Wrong scope: evidence valid for one trusted scope cannot be reused
#    for another.
# ---------------------------------------------------------------------------


def test_d_wrong_scope_blocked_no_actuation(asut):
    """The MANDATE authorizes BOTH resources (so the mandate's own
    resource-scope check is not what fails here -- isolating
    PreExecutionControl's own scope-binding check specifically). An
    attestation genuinely obtained for resource R1 must not authorize an
    otherwise-identical operation against resource R2, even though the
    mandate itself permits both."""
    resource_one = "notifications-resource-one"
    resource_two = "notifications-resource-two"
    wide_mandate = asut.issue_mandate(subject=ACTOR, action_scope=[ATTESTED_ACTION],
                                       resource_scope=[resource_one, resource_two])

    before = asut.gateway_notification_receipt_count()
    ctx = _context()
    att_for_r1 = asut.get_attestation(resource=resource_one, context=ctx)

    result = asut.execute_with_mandate_and_attestation(
        mandate=wide_mandate, attestation=att_for_r1, actor=ACTOR, resource=resource_two, context=ctx,
    )

    assert result["status"] == "BLOCKED", result
    assert "ATTESTATION_SCOPE_MISMATCH" in result["reason"]
    assert asut.gateway_notification_receipt_count() == before


# ---------------------------------------------------------------------------
# F. Stale evidence: expired attestation cannot reach actuation. Uses a
#    DEDICATED, short-validity deployment and the REAL wall clock (a real
#    sleep, not a mocked/injected clock) -- genuine expiry through the
#    actual HTTP surface, not a controlled-clock unit test repeated.
#    (Not-yet-valid evidence is not reproduced here: the real Attester
#    service always sets not_before == issued_at == its own signing-time
#    clock, so there is no way for an external caller to obtain a
#    genuinely-signed not-yet-valid attestation from it to test against --
#    that property remains proven only at the unit level, with a
#    controlled clock, in tests/test_mcc_attestation.py. See the gap
#    matrix in docs/ATTESTATION_INDEPENDENT_ASSURANCE.md.)
# ---------------------------------------------------------------------------


def test_f_expired_evidence_blocked_no_actuation():
    """Genuine wall-clock expiry through the real HTTP surface: a
    DEDICATED, short-validity deployment (its own SUT, not the shared
    module fixture, since every other test in this module needs the
    default 900s window to stay valid for the whole session) issues a
    genuinely, correctly signed attestation, this test waits past its real
    ``expires_at``, and only THEN presents it. This isolates the
    time-window check specifically from signature tamper-detection
    (``test_a2`` above already covers the latter) -- mutating
    ``expires_at`` on an otherwise genuine attestation would only
    re-exercise signature verification (the mutated field is no longer
    covered by the signature), not the time-window comparison itself."""
    from assurance.sut.attestation_harness import build_attestation_system_under_test as _build

    with _build(validity_seconds=2) as asut:
        mandate = asut.issue_mandate(subject=ACTOR, action_scope=[ATTESTED_ACTION],
                                     resource_scope=[ATTESTED_RESOURCE])
        ctx = _context()
        att = asut.get_attestation(context=ctx)
        time.sleep(3)  # past the 2-second validity window, real wall clock

        before = asut.gateway_notification_receipt_count()
        result = asut.execute_with_mandate_and_attestation(
            mandate=mandate, attestation=att, actor=ACTOR, context=ctx,
        )

        assert result["status"] == "BLOCKED", result
        assert "EXPIRED" in result["reason"]
        assert asut.gateway_notification_receipt_count() == before


# ---------------------------------------------------------------------------
# G. Attestation replay: the same attestation nonce cannot satisfy required
#    verification twice.
# ---------------------------------------------------------------------------


def test_g_attestation_replay_second_use_blocked(asut):
    """The SAME genuinely signed attestation is presented for two
    DIFFERENT execution attempts (two mandates, so the second is not
    rejected merely for reusing a transaction/idempotency key -- the
    variable under test is the attestation's own nonce, isolated from
    every other binding)."""
    mandate_1 = asut.issue_mandate(subject=ACTOR, action_scope=[ATTESTED_ACTION],
                                    resource_scope=[ATTESTED_RESOURCE])
    mandate_2 = asut.issue_mandate(subject=ACTOR, action_scope=[ATTESTED_ACTION],
                                    resource_scope=[ATTESTED_RESOURCE])
    ctx = _context()
    att = asut.get_attestation(context=ctx)

    before = asut.gateway_notification_receipt_count()
    first = asut.execute_with_mandate_and_attestation(
        mandate=mandate_1, attestation=att, actor=ACTOR, context=ctx,
    )
    assert first["status"] == "EXECUTED", first
    after_first = asut.gateway_notification_receipt_count()
    assert after_first == before + 1

    second = asut.execute_with_mandate_and_attestation(
        mandate=mandate_2, attestation=att, actor=ACTOR, context=ctx,
    )
    assert second["status"] == "BLOCKED", second
    assert "REPLAY" in second["reason"]
    assert asut.gateway_notification_receipt_count() == after_first, (
        "the replayed attestation must not have produced a second actuation"
    )
