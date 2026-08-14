"""Twenty-six targeted, hand-authored security-critical mutations (PR #71,
Workstream J; extended post-merge-review to close a disclosed mutation-
testing gap -- see the ``gate-*-fail-open`` block below).

Unlike generic mutation testing (which mutates arbitrary operators across a
whole codebase and requires heavy tuning to separate meaningful mutants
from noise), each ``Defect`` here is a SPECIFIC, deliberately chosen
regression of a named security property this repository claims to hold --
the kind of one-line, plausible-looking, code-review-survivable change a
real regression could actually look like. Each targets an EXACT, unique
source substring (verified present exactly once before mutating, so a
future refactor that moves the code makes this fail loudly rather than
silently mutating nothing) and names the workstream test(s) expected to
catch it.

"100% detection" is the required outcome, not an assumption: this module
only DEFINES the defects; ``mutation/harness.py`` actually applies each one
to an isolated copy of the repository, runs the named detector tests
against that mutated copy, and reports pass/fail per defect. A defect
whose detector tests do NOT fail against the mutated code is a genuine,
reportable gap in this assurance suite's coverage -- never silently
dropped or reclassified as "not applicable" to make the score look better.

The 13 original defects (below) are one hand-picked mutation per security
property, spread across the whole runtime. The trailing ``gate-*-fail-open``
block is a DIFFERENT, complementary kind of coverage: an exhaustive,
systematic sweep of every single ``GateResult(False, ...)`` fail-closed
return in ``src/mcc_core/gate.py``'s ``ExecutionGate._verify``/``verify`` --
i.e. every site where a one-line ``False`` -> ``True`` edit would flip the
gate from deny to allow. It was added after a direct-verification
mutation-testing addendum found that 2 of these 14 sites (the ``verify()``
exception handler and the ``nbf``/``exp`` type-check) were not caught by a
reasonable hand-selected test oracle, even though the gate's own explicit
rejection reasons made the bug look "obviously" covered. Both gaps were
closed with new regression tests in ``tests/test_mcc_core.py``
(``test_gate_denies_when_verify_raises_unexpectedly`` and
``test_gate_denies_malformed_time_window``) before these defects were added,
so this module now proves -- not assumes -- that all 14 fail-open sites in
the gate are genuinely detected, permanently, in CI.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple


@dataclass(frozen=True)
class Defect:
    id: str
    description: str
    file_path: str  # repo-relative
    find: str        # exact, unique source substring
    replace: str      # the mutated substring
    detector_tests: Tuple[str, ...]  # pytest node ids / paths expected to fail


DEFECTS: List[Defect] = [
    Defect(
        id="gate-fail-open",
        description="The execution gate's fail-closed exception handler is flipped to fail-open on any error.",
        file_path="src/mcc_core/gate.py",
        find='        except Exception:\n            return GateResult(False, "GATE_ERROR: fail-closed")',
        replace='        except Exception:\n            return GateResult(True, "GATE_ERROR: MUTATED-fail-open")',
        detector_tests=("mutation/detectors.py::test_gate_exception_path_fails_closed",),
    ),
    Defect(
        id="signature-verify-always-true",
        description="Ed25519 signature verification always reports valid, regardless of the signature bytes.",
        file_path="src/mcc_core/signing.py",
        find="        public_key.verify(signature, canonical_bytes(unsigned))\n        return True\n    except Exception:\n        return False",
        replace="        public_key.verify(signature, canonical_bytes(unsigned))\n        return True\n    except Exception:\n        return True  # MUTATED",
        detector_tests=("assurance/tests/test_exclusive_execution_path.py::test_a7_forged_gate_identity_tampered_signature",
                         "assurance/tests/test_exclusive_execution_path.py::test_a5_agent_to_actuator_bypass_self_signed_forged_evaluator"),
    ),
    Defect(
        id="nonce-replay-allowed",
        description="In-memory nonce registry no longer rejects a nonce it has already seen (replay accepted).",
        file_path="src/mcc_core/nonce.py",
        find="        if nonce in self._seen:\n            return False",
        replace="        if False:  # MUTATED: replay check disabled\n            return False",
        detector_tests=("mutation/detectors.py::test_in_memory_nonce_registry_rejects_replay",),
    ),
    Defect(
        id="consensus-threshold-bypassed",
        description="Consensus verification treats any vote count as meeting the threshold.",
        file_path="src/mcc_core/consensus.py",
        find="        if len(allow_ids) >= self.policy.threshold:",
        replace="        if True:  # MUTATED: threshold check disabled",
        detector_tests=("assurance/tests/test_decision_authority_containment.py::test_c2_below_threshold_votes_denied",),
    ),
    Defect(
        id="consensus-veto-disabled",
        description="A trusted evaluator's DENY vote no longer vetoes consensus.",
        file_path="src/mcc_core/consensus.py",
        find="        if self.policy.veto_on_deny and deny_ids:",
        replace="        if False:  # MUTATED: veto disabled",
        detector_tests=("assurance/tests/test_decision_authority_containment.py::test_c3_trusted_deny_vote_vetoes_despite_sufficient_allow_votes",),
    ),
    Defect(
        id="consensus-vote-binding-disabled",
        description="Votes are accepted regardless of which action/payload/actor they were actually signed for.",
        file_path="src/mcc_core/consensus.py",
        find='            if (vote.get("action_hash") != expected_action\n                    or vote.get("payload_hash") != expected_payload\n                    or vote.get("actor") != actor):',
        replace='            if False:  # MUTATED: operation binding check disabled',
        detector_tests=("assurance/tests/test_exclusive_execution_path.py::test_a8_valid_token_direct_to_actuator_wrong_binding",
                         "assurance/tests/test_decision_authority_containment.py::test_c5_votes_bound_to_a_different_actor_rejected"),
    ),
    Defect(
        id="audit-before-actuation-bypassed",
        description="A failed pre-actuation audit write no longer blocks actuation (audit-before-actuation invariant broken).",
        file_path="src/mcc_core/coordinator.py",
        find="        if pre_ref is None:\n            # Cannot confirm the pre-actuation record -> indeterminate before\n            # execution -> fail closed and release everything reserved.",
        replace="        if False:  # MUTATED: audit-before-actuation guard disabled\n            # Cannot confirm the pre-actuation record -> indeterminate before\n            # execution -> fail closed and release everything reserved.",
        detector_tests=("mutation/detectors.py::test_coordinator_denies_when_pre_actuation_audit_write_fails",),
    ),
    Defect(
        id="canonical-action-body-excluded",
        description="The request body no longer contributes to the canonical action hash -- two requests with different bodies bind identically.",
        file_path="egress_proxy/canonical_action.py",
        find="    action.update(_encode_body(body))\n    return action",
        replace="    pass  # MUTATED: action.update(_encode_body(body)) removed\n    return action",
        detector_tests=("tests/test_egress_canonical.py::test_material_difference_changes_hash",),
    ),
    Defect(
        id="ssrf-allowed-hosts-bypassed",
        description="The destination allowed_hosts allowlist is no longer enforced.",
        file_path="egress_proxy/ssrf.py",
        find='    if policy.allowed_hosts is not None and host not in policy.allowed_hosts:\n        raise SSRFError(f"host {host!r} not in allowed_hosts")',
        replace='    if False:  # MUTATED: allowed_hosts check disabled\n        raise SSRFError(f"host {host!r} not in allowed_hosts")',
        detector_tests=("tests/test_egress_ssrf.py::test_allowed_hosts_enforced",),
    ),
    Defect(
        id="api-key-check-disabled",
        description="The actuator's client API key check accepts any key.",
        file_path="egress_proxy/app.py",
        find='    def require_api_key(x_api_key: str = Header(...)) -> str:\n        if x_api_key != cfg.api_key:\n            raise HTTPException(status_code=401, detail="INVALID_API_KEY")',
        replace='    def require_api_key(x_api_key: str = Header(...)) -> str:\n        if False:  # MUTATED: API key check disabled\n            raise HTTPException(status_code=401, detail="INVALID_API_KEY")',
        detector_tests=("assurance/tests/test_exclusive_execution_path.py::test_a2_stolen_endpoint_wrong_client_credential",),
    ),
    Defect(
        id="idempotency-duplicate-allowed",
        description="The in-memory idempotency registry no longer rejects a duplicate reservation of an already-executed key.",
        file_path="src/mcc_core/idempotency.py",
        find='        state, held = _decode(encoded)\n        if state == IdempotencyState.EXECUTED:\n            return ReserveResult(ReserveStatus.DUPLICATE_EXECUTED, "operation already executed", held)\n        return ReserveResult(ReserveStatus.DUPLICATE_INFLIGHT, "operation already reserved", held)',
        replace='        state, held = _decode(encoded)\n        return ReserveResult(ReserveStatus.RESERVED, "MUTATED: duplicate check disabled", held)',
        detector_tests=("tests/test_idempotency.py::test_duplicate_reservation_denied",),
    ),
    Defect(
        id="challenge-replay-allowed",
        description=(
            "The in-memory challenge registry no longer rejects consuming an already-consumed "
            "challenge. InMemoryChallengeRegistry.consume has TWO independent single-use guards "
            "(the rec.state != ISSUED check, and the separate _consumed-set membership check); "
            "mutating only one alone is not observable (the other still fires first on a normal "
            "replay), so this defect disables both together, representing a single refactor that "
            "breaks single-use enforcement as a whole."
        ),
        file_path="src/mcc_core/challenge.py",
        find=(
            '        if rec.state == ChallengeState.ISSUED.value and rec.is_expired(now):\n'
            '            rec.state = ChallengeState.EXPIRED.value\n'
            '        if rec.state != ChallengeState.ISSUED.value:\n'
            '            return ConsumeResult(False, f"challenge not consumable in state {rec.state}", rec.state)\n'
            '        if challenge_id in self._consumed:\n'
            '            return ConsumeResult(False, "challenge already consumed (replay)",\n'
            '                                 ChallengeState.CONSUMED.value)'
        ),
        replace=(
            '        if rec.state == ChallengeState.ISSUED.value and rec.is_expired(now):\n'
            '            rec.state = ChallengeState.EXPIRED.value\n'
            '        if False:  # MUTATED: single-use state check disabled\n'
            '            return ConsumeResult(False, f"challenge not consumable in state {rec.state}", rec.state)\n'
            '        if False:  # MUTATED: _consumed-set check disabled\n'
            '            return ConsumeResult(False, "challenge already consumed (replay)",\n'
            '                                 ChallengeState.CONSUMED.value)'
        ),
        detector_tests=("tests/test_challenge.py::test_consume_exactly_once",),
    ),
    Defect(
        id="constraint-residual-violation-allowed",
        description="A constraint violation that clamping could not fully resolve is allowed through as CONSTRAIN instead of failing to DENY.",
        file_path="src/mcc_core/authority.py",
        find="            residual = _constraint_violations(constraints, constrained)\n            if residual:",
        replace="            residual = _constraint_violations(constraints, constrained)\n            if False:  # MUTATED: residual-violation guard disabled",
        detector_tests=("tests/test_authority.py::test_missing_constrained_field_cannot_be_constrained_so_denies",),
    ),
    # ------------------------------------------------------------------
    # Exhaustive gate.py fail-open sweep: every GateResult(False, ...) in
    # ExecutionGate._verify()/verify() gets its own False->True defect.
    # "gate-fail-open" above already covers the verify() except-handler
    # (site 1 of 14); the remaining 13 sites are below, in source order.
    # ------------------------------------------------------------------
    Defect(
        id="gate-no-token-fail-open",
        description="A missing/non-dict/empty token is treated as authorized instead of denied.",
        file_path="src/mcc_core/gate.py",
        find='        if not isinstance(token, dict) or not token:\n            return GateResult(False, "NO_TOKEN: no verified decision token, no execution")',
        replace='        if not isinstance(token, dict) or not token:\n            return GateResult(True, "NO_TOKEN: MUTATED-fail-open")',
        detector_tests=("tests/test_mcc_core.py::test_gate_denies_missing_token",),
    ),
    Defect(
        id="gate-untrusted-key-fail-open",
        description="A token signed by an unknown/revoked key id is treated as authorized instead of denied.",
        file_path="src/mcc_core/gate.py",
        find='        if public_key is None:\n            return GateResult(False, "UNTRUSTED_KEY: unknown or revoked key id")',
        replace='        if public_key is None:\n            return GateResult(True, "UNTRUSTED_KEY: MUTATED-fail-open")',
        detector_tests=("tests/test_mcc_core.py::test_gate_denies_unknown_kid",),
    ),
    Defect(
        id="gate-invalid-signature-fail-open",
        description="A token with an invalid Ed25519 signature is treated as authorized instead of denied (distinct from signature-verify-always-true: this mutates the GATE's handling of a correctly-computed False result, not signing.py's verification itself).",
        file_path="src/mcc_core/gate.py",
        find='        if not verify_token(token, public_key):\n            return GateResult(False, "INVALID_SIGNATURE: Ed25519 verification failed")',
        replace='        if not verify_token(token, public_key):\n            return GateResult(True, "INVALID_SIGNATURE: MUTATED-fail-open")',
        detector_tests=("tests/test_mcc_core.py::test_gate_denies_tampered_token",),
    ),
    Defect(
        id="gate-audience-mismatch-fail-open",
        description="A token bound to a different gate's audience is treated as authorized instead of denied.",
        file_path="src/mcc_core/gate.py",
        find='        if token.get("aud") != self.audience:\n            return GateResult(False, "AUDIENCE_MISMATCH: token bound to another gate")',
        replace='        if token.get("aud") != self.audience:\n            return GateResult(True, "AUDIENCE_MISMATCH: MUTATED-fail-open")',
        detector_tests=("tests/test_mcc_core.py::test_gate_denies_wrong_audience",),
    ),
    Defect(
        id="gate-invalid-time-window-fail-open",
        description="A token with a missing or non-integer nbf/exp is treated as authorized instead of denied. Previously an UNDETECTED survivor of the direct-verification mutation addendum -- closed by adding test_gate_denies_malformed_time_window.",
        file_path="src/mcc_core/gate.py",
        find='        if not isinstance(nbf, int) or not isinstance(exp, int):\n            return GateResult(False, "INVALID_TIME_WINDOW: missing nbf/exp")',
        replace='        if not isinstance(nbf, int) or not isinstance(exp, int):\n            return GateResult(True, "INVALID_TIME_WINDOW: MUTATED-fail-open")',
        detector_tests=("tests/test_mcc_core.py::test_gate_denies_malformed_time_window",),
    ),
    Defect(
        id="gate-not-yet-valid-fail-open",
        description="A token whose nbf is still in the future is treated as authorized instead of denied.",
        file_path="src/mcc_core/gate.py",
        find='        if ts < nbf:\n            return GateResult(False, "TOKEN_NOT_YET_VALID: nbf in the future")',
        replace='        if ts < nbf:\n            return GateResult(True, "TOKEN_NOT_YET_VALID: MUTATED-fail-open")',
        detector_tests=("tests/test_mcc_core.py::test_gate_denies_not_yet_valid_token",),
    ),
    Defect(
        id="gate-token-expired-fail-open",
        description="An expired token is treated as authorized instead of denied.",
        file_path="src/mcc_core/gate.py",
        find='        if ts >= exp:\n            return GateResult(False, "TOKEN_EXPIRED")',
        replace='        if ts >= exp:\n            return GateResult(True, "TOKEN_EXPIRED-MUTATED-fail-open")',
        detector_tests=("tests/test_mcc_core.py::test_gate_denies_expired_token",),
    ),
    Defect(
        id="gate-non-executable-verdict-fail-open",
        description="A signed DENY/ESCALATE verdict is executed instead of denied at the gate.",
        file_path="src/mcc_core/gate.py",
        find='        if token.get("decision") not in (Verdict.ALLOW.value, Verdict.CONSTRAIN.value):\n            return GateResult(False, "NON_EXECUTABLE_VERDICT: only ALLOW/CONSTRAIN execute")',
        replace='        if token.get("decision") not in (Verdict.ALLOW.value, Verdict.CONSTRAIN.value):\n            return GateResult(True, "NON_EXECUTABLE_VERDICT: MUTATED-fail-open")',
        detector_tests=("tests/test_mcc_core.py::test_gate_denies_signed_deny_verdict",),
    ),
    Defect(
        id="gate-policy-hash-mismatch-fail-open",
        description="A token issued under an untrusted/stale policy hash is treated as authorized instead of denied.",
        file_path="src/mcc_core/gate.py",
        find='        if self.policy_hash is not None and token.get("policy_hash") != self.policy_hash:\n            return GateResult(False, "POLICY_HASH_MISMATCH: token issued under untrusted policy")',
        replace='        if self.policy_hash is not None and token.get("policy_hash") != self.policy_hash:\n            return GateResult(True, "POLICY_HASH_MISMATCH: MUTATED-fail-open")',
        detector_tests=("tests/test_mcc_core.py::test_gate_denies_policy_hash_mismatch",),
    ),
    Defect(
        id="gate-action-hash-mismatch-fail-open",
        description="A token whose action_hash does not match the action actually being executed is treated as authorized instead of denied.",
        file_path="src/mcc_core/gate.py",
        find='        if action is not None and token.get("action_hash") != hash_action(action):\n            return GateResult(False, "ACTION_HASH_MISMATCH: token does not authorize this action")',
        replace='        if action is not None and token.get("action_hash") != hash_action(action):\n            return GateResult(True, "ACTION_HASH_MISMATCH: MUTATED-fail-open")',
        detector_tests=("tests/test_mcc_core.py::test_gate_denies_action_hash_mismatch",),
    ),
    Defect(
        id="gate-payload-hash-mismatch-fail-open",
        description="A token whose payload_hash does not match the payload actually being executed is treated as authorized instead of denied.",
        file_path="src/mcc_core/gate.py",
        find='        if payload is not None and token.get("payload_hash") != hash_payload(payload):\n            return GateResult(False, "PAYLOAD_HASH_MISMATCH: payload differs from authorized one")',
        replace='        if payload is not None and token.get("payload_hash") != hash_payload(payload):\n            return GateResult(True, "PAYLOAD_HASH_MISMATCH: MUTATED-fail-open")',
        detector_tests=("tests/test_mcc_core.py::test_gate_denies_payload_hash_mismatch",),
    ),
    Defect(
        id="gate-binding-mismatch-fail-open",
        description="A token whose bound operation fields (actor/resource/transaction/etc.) differ from the operation actually being executed is treated as authorized instead of denied.",
        file_path="src/mcc_core/gate.py",
        find='                if authorized is not None and authorized != expected:\n                    return GateResult(\n                        False,\n                        f"BINDING_MISMATCH: {field} differs from authorized operation",\n                    )',
        replace='                if authorized is not None and authorized != expected:\n                    return GateResult(\n                        True,\n                        f"BINDING_MISMATCH: MUTATED-fail-open ({field})",\n                    )',
        detector_tests=("tests/test_coordinator.py::test_binding_mismatch_blocks_before_execution",),
    ),
    Defect(
        id="gate-nonce-rejected-fail-open",
        description="A replayed nonce (or a nonce registry that is unavailable/errors) is treated as authorized instead of denied -- breaks both replay protection and the registry-down fail-closed guarantee.",
        file_path="src/mcc_core/gate.py",
        find='        if not await self.nonce_registry.consume(\n            token.get("nonce"), ttl_seconds=self._nonce_ttl(exp, ts)\n        ):\n            return GateResult(False, "NONCE_REJECTED: replay or registry unavailable (fail-closed)")',
        replace='        if not await self.nonce_registry.consume(\n            token.get("nonce"), ttl_seconds=self._nonce_ttl(exp, ts)\n        ):\n            return GateResult(True, "NONCE_REJECTED: MUTATED-fail-open")',
        detector_tests=("tests/test_mcc_core.py::test_gate_denies_replayed_nonce",
                         "tests/test_mcc_core.py::test_gate_fail_closed_when_redis_down"),
    ),
]

DEFECT_IDS = tuple(d.id for d in DEFECTS)

assert len(DEFECT_IDS) == 26, f"expected exactly 26 targeted defects, found {len(DEFECT_IDS)}"
assert len(set(DEFECT_IDS)) == 26, "defect ids must be unique"

GATE_FAIL_OPEN_DEFECT_IDS = tuple(d.id for d in DEFECTS if d.id == "gate-fail-open" or d.id.startswith("gate-") and d.id.endswith("-fail-open"))
assert len(GATE_FAIL_OPEN_DEFECT_IDS) == 14, (
    f"expected exactly 14 gate.py fail-open sites (one per GateResult(False, ...) "
    f"call site in ExecutionGate._verify()/verify()), found {len(GATE_FAIL_OPEN_DEFECT_IDS)}"
)
