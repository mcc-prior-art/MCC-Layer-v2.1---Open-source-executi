"""Thirteen targeted, hand-authored security-critical mutations (PR #71,
Workstream J).

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
]

DEFECT_IDS = tuple(d.id for d in DEFECTS)

assert len(DEFECT_IDS) == 13, f"expected exactly 13 targeted defects, found {len(DEFECT_IDS)}"
assert len(set(DEFECT_IDS)) == 13, "defect ids must be unique"
