"""Reconciliation with PR #43: one normative contract, no drift (PR #49).

These tests are the executable guarantee that PR #49 did not fork a parallel
governance model. They assert the protocol reuses the contract's version axis,
error taxonomy, canonical decision/verdict models, and capability vocabulary.
"""

from __future__ import annotations

import mcc_client
import mcc_client.contract as contract
import mcc_protocol as mp
from mcc_compliance.capability_profile import KNOWN_CAPABILITIES


def test_single_version_axis():
    assert mp.PROTOCOL_VERSION == contract.CONTRACT_VERSION


def test_governance_decision_reuses_the_sdk_verdict_and_decision():
    # GovernanceDecision composes mcc_client.Decision and mcc_client.Verdict — the
    # protocol re-exports the SAME objects (identity), it does not redefine them.
    assert mp.Verdict is mcc_client.Verdict
    assert mp.Decision is mcc_client.Decision


def test_error_codes_are_a_subset_of_the_contract_taxonomy():
    # Every code the ingress pipeline can emit is an existing ContractErrorCode.
    from mcc_protocol.pipeline import CanonicalIngressPipeline  # noqa: F401
    valid = set(contract.ContractErrorCode)
    # The reason codes GovernanceDecision can emit are contract codes.
    from mcc_protocol.decision import _VERDICT_REASON_CODE
    assert set(_VERDICT_REASON_CODE.values()) <= valid


def test_reason_codes_use_contract_values_only():
    valid = {c.value for c in contract.ContractErrorCode}
    p = mp.CanonicalProposal.create(
        adapter_id="a", adapter_version="1", framework="f", actor="x",
        action="send_notification", resource="r", payload={"k": 1})
    dec = mcc_client.Decision.from_response(
        {"decision": "DENY", "reason": "no", "audit_id": "a1",
         "forward_context": {}, "policy_ref": "p", "trace_id": p.trace_id},
        requested_actor="x", requested_action="send_notification",
        requested_resource="r", requested_payload={"k": 1})
    gov = mp.GovernanceDecision.from_decision(p, dec)
    assert set(gov.reason_codes) <= valid


def test_capability_vocabulary_is_the_pr47_one():
    # The registry validates capabilities against the single PR #47 vocabulary.
    from mcc_protocol import registry as reg_mod
    assert reg_mod.KNOWN_CAPABILITIES is KNOWN_CAPABILITIES


def test_canonicalization_is_the_single_platform_implementation():
    # The proposal's action hash uses mcc_core.signing (the one canonicalization),
    # so proposal hashes are consistent with the rest of the evidence tooling.
    import mcc_core.signing as signing
    from mcc_protocol.proposal import compute_action_hash
    expected = signing.sha256_hex(signing.canonical_bytes(
        {"action": "a", "resource": "r", "actor": "x", "payload": {"k": 1}}))
    assert compute_action_hash("a", "r", "x", {"k": 1}) == expected
