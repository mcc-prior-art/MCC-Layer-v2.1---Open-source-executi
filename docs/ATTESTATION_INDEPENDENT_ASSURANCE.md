# Independent Assurance of the Attestation-to-Execution Chain (PR-5)

**Status:** Implemented. This document is the PR-5 counterpart to
`docs/REPRODUCING_ASSURANCE.md` (PRs #71-#74), scoped specifically to the
PR-1 through PR-4 attestation-to-execution chain those workstreams predate
and do not cover:

```
INTELLIGENCE / AGENT
        |
        v
INDEPENDENT ATTESTER            (PR-4, MCC-AT-004)
        |
        v
PRE-EXECUTION CONTROL           (PR-2, MCC-AT-002)
        |
        v
EVIDENCE-BOUND SIGNED EXECUTION AUTHORITY   (PR-3, MCC-AT-003)
        |
        v
EXECUTION GATE                  (PR-3, MCC-AT-003)
        |
        v
EXECUTION
```

**This is a self-administered harness, exactly like `docs/REPRODUCING_ASSURANCE.md`
already states of the original baseline, and that disclaimer applies here
without modification.** Every test, model, and mutant described below was
written by the same people who wrote the code it checks. Passing it means
the code does what its own authors, testing adversarially, could get it to
prove — not what an unaffiliated, independent auditor would find. Read
`docs/REPRODUCING_ASSURANCE.md`'s "Verified scope and limitations" section;
it applies to this document too.

This document does not use the words "impossible", "cannot ever", "formally
proven", or "independent" (in the sense of third-party) beyond what the
evidence in the tables below actually establishes.

---

## 1. Existing assurance inventory (before PR-5)

| Component | Scope |
|---|---|
| `assurance/tests/` (Workstreams A-K + negative control, PR #71-74) | The original governance runtime: mandate/consensus authority, decision-token nonce replay, canonical action hashing, constraint clamping, audit survivability, property-based/stateful testing, five-framework semantic equivalence. **Written before PR-1 existed; contains no reference to attestation, `PreExecutionControl`, evidence binding, or the Attester service.** |
| `model/MCCExecutionStateMachine.tla` | The generic PREPARED -> AUTHORIZED -> ... -> EXECUTED lifecycle and single decision-token nonce. **No attestation/evidence state at all.** |
| `mutation/defects.py` (26 entries, pre-PR-5) | Consensus/mandate/gate/nonce/audit/canonicalization/SSRF/API-key/idempotency/challenge/constraint properties, plus a systematic 14-site sweep of every `gate.py` fail-open branch **as `gate.py` existed before PR-3 added evidence binding to it**. Zero entries reference `mcc_attestation`, `pre_execution_control.py`, or `mcc_attester_service`. |
| `tests/test_mcc_attestation*.py`, `tests/test_pre_execution_control*.py`, `tests/test_evidence_bound_execution_ticket*.py`, `tests/test_attester_service*.py`, `tests/test_governance_service_attestation.py` (PR-1 through PR-4, and their owner-review fixes) | Thorough unit-level and in-process-E2E adversarial coverage of each PR's own claims, including a genuine cross-process private-key-isolation proof (PR-4) and a genuine concurrency exploit proof for the PR-3 TOCTOU fix. **Not run through the real, multi-process, HTTP-driven SUT the Workstream A-K tests use** -- every attestation obtained and every governed call made in these files happens inside one pytest process. |

**Conclusion:** the attestation-to-execution chain had rigorous unit/in-process-E2E coverage but had never been independently attacked through the SAME kind of real, multi-process, dual-oracle (reported status + independent external-effect counter) methodology the original assurance baseline applies to the rest of the runtime, had zero mutation-corpus representation, and had no formal-model representation at all.

---

## 2. Gap matrix

| Security property (PR-5 task ID) | Existing evidence | Actual gap | PR-5 action |
|---|---|---|---|
| A. Forged attestation (wrong key/kid/tampered field/caller-manufactured "verified") | `tests/test_mcc_attestation.py`, `tests/test_pre_execution_control.py` (unit, in-process) | No adversarial proof through the real, multi-process HTTP SUT | `assurance/tests/test_attestation_chain.py::test_a1/a2/a3` |
| B. Wrong action binding | `tests/test_pre_execution_control.py` (unit) | Same | `test_attestation_chain.py::test_b_wrong_action_binding_blocked_no_actuation` |
| C. Wrong payload binding | `tests/test_pre_execution_control.py`, `tests/test_governance_service_attestation.py` (unit/in-process) | Same | `test_attestation_chain.py::test_c_wrong_payload_binding_blocked_no_actuation` |
| D. Wrong scope | `tests/test_pre_execution_control.py` (unit) | Same | `test_attestation_chain.py::test_d_wrong_scope_blocked_no_actuation` |
| E. Policy binding | `tests/test_pre_execution_control.py` (unit, `require_policy_binding=True` case, thorough) | The PR-5 harness's own `AttestationRequirement` is configured with `require_policy_binding=False` (matching the actual deployed default). **No policy-binding property is claimed for this configuration**, per the task's own explicit instruction not to claim properties for configurations where policy binding is not required. The `require_policy_binding=True` case is NOT re-derived at assurance level: it would require a second, separate SUT boot (Gateway + Attester reconfigured) for marginal incremental value over the already-thorough unit coverage, which exercises the identical `verify_attestation()` code path this SUT's Control also calls. | Documented here as a deliberate, reasoned non-duplication, not silently omitted. |
| F. Stale/not-yet-valid evidence | `tests/test_mcc_attestation.py` (unit, controlled clock, covers BOTH expired and not-yet-valid) | E2E gap for expiry specifically; **not-yet-valid is structurally unreproducible at E2E** -- the real Attester always sets `not_before == issued_at == its own signing-time clock`, so no external caller can obtain a genuinely-signed not-yet-valid attestation from it to test against. This is not an oversight: it is the real Attester's request schema correctly refusing to let a caller dictate `not_before` (design rule 3, PR-4). | `test_attestation_chain.py::test_f_expired_evidence_blocked_no_actuation` (dedicated short-validity SUT + real `time.sleep` past genuine `expires_at` -- NOT a tampered field, which would only re-test signature detection). Not-yet-valid: cited to the existing unit test; E2E reproduction is not attempted because the architecture gives no honest way to attempt it. |
| G. Attestation replay | `tests/test_pre_execution_control.py` (unit, in-memory registry) | E2E gap | `test_attestation_chain.py::test_g_attestation_replay_second_use_blocked` (same attestation, two different mandates, dual-oracle: second attempt BLOCKED and the external-effect counter does not advance a second time) |
| H. Execution-ticket replay w/ evidence bound | `tests/test_evidence_bound_execution_ticket.py` (unit, direct `ExecutionGate.verify()` calls) | **Not reproducible at this SUT's HTTP surface at all, and this is itself informative.** The Gateway mints a fresh decision-token nonce server-side on every `/mandates/execute` call and never returns the token to the caller — there is no HTTP-reachable route by which an external caller could present an already-consumed decision token a second time through this deployment topology. The unit-level `ExecutionGate.verify()` tests remain the correct, and only, way to exercise this property, because they are the only place the token itself is an addressable object. | Cited, not duplicated; the absence of an external attack surface for this specific property is recorded as a positive finding, not a gap. |
| I. Evidence substitution (no evidence / evidence B / mutated A / canonically-different digest) | `tests/test_evidence_bound_execution_ticket.py::test_07-11` (unit, direct Gate calls, exhaustive) | "No evidence" and "evidence B" are exactly what B/C above already exercise through this SUT (a genuine attestation for the wrong action/payload IS "evidence B" presented in place of what was required). The specific formulation "a token already bound to A rejects B presented separately at the Gate" is, like H, only meaningfully separable from token issuance at the unit level (this SUT's `/mandates/execute` performs Control-evaluation, token-issuance, and Gate-verification in one opaque HTTP call, so there is no way to vary "what the token is bound to" independently of "what is presented" through this surface). | Cited; B/C/mutated-A (`test_a2`) above are this property's E2E instantiation to the extent the architecture exposes it. |
| J. TOCTOU | `tests/test_evidence_bound_execution_ticket.py::test_17_toctou_...` (a genuine concurrency exploit: a blocking nonce-registry double lands a real mutation inside Control's one `await` point, using `asyncio.Event`s, not a mock or a timing assumption) | **Assessed, not duplicated.** This existing test already IS an adversarial-quality proof — it does not merely assert the property, it constructs the actual race window PR-3's fix closes and drives a real mutation through it. An assurance-level HTTP reproduction would need to win an equivalent race against the real Gateway subprocess's internal `asyncio` scheduling from outside a process boundary, which is not a stronger proof than controlling the race directly in-process; it would only add flakiness. | No new test added; existing test cited as sufficient, non-duplicated evidence, per the task's own explicit instruction to make this determination rather than reflexively re-running the regression. |
| K. Attester trust removal / unknown attester | (none, before PR-5) | Investigated first, as instructed: the real trust-store semantics (`mcc_attestation.trust.AttesterTrustStore`, `gateway.governance_api._build_pre_execution_control`) are **registration-based, not revocation-based**. An attester's public key either is, or is not, present in the `MCC_ATTESTATION_TRUST_CONFIG` a Gateway loaded at startup. There is no live "remove this attester's trust at runtime" API analogous to `POST /mandates/{id}/revoke` — MCC-Core has a real revocation FEATURE for mandates, and does not have one for Attester trust. This is accurately documented here as a limitation, not built as a new feature (explicitly out of scope per the task's own instruction not to invent a revocation system merely because the word appears in a checklist). | `test_attestation_chain.py::test_a1_forged_attestation_untrusted_key_blocked_no_actuation` **is** the accurate evidence for this property: an attester that was never registered is, to Control, indistinguishable from one that has been removed — both resolve to "no trust anchor found." |
| L. Private-key isolation | `tests/test_attester_service_process_isolation.py` (PR-4, and its own owner-review fix: a genuine bootstrap-subprocess design, a runtime `open()`/`Path.read_bytes`/`Path.read_text` interception guard, and a static AST guard, all proving the TEST process itself never generates or reads the private key) | PR-4's own test is already the "honest subprocess pattern" this task asks PR-5 to reuse — it was not duplicated. The gap PR-5 closes is narrower: proving the **assurance SUT's own Gateway subprocess** (not merely a bespoke test harness) is configured with attestation trust from `MCC_ATTESTATION_TRUST_CONFIG` (public key only) and never receives `MCC_ATTESTER_SIGNING_KEY_PATH` or any other private-key-shaped environment variable. | `assurance/sut/attestation_harness.py`'s own construction (the Gateway subprocess's `extra_env` carries only the two `MCC_ATTESTATION_*_CONFIG` file paths — both pointing at JSON containing `public_key_b64`, never a PEM path) is the evidence; confirmed by inspection and by the fact that every E2E test in this file only ever obtains attestations by calling the SEPARATE Attester subprocess over HTTP. PR-4's own dedicated isolation test remains the primary, deeper proof and is cited, not re-derived. |
| M. Caller-controlled Attester output (17 trusted-output fields) | `tests/test_attester_service.py::test_b_*` (17-way parametrized, unit-level via `TestClient`, exhaustive) | Already thorough and precise at the correct boundary (the schema itself). An E2E reproduction through a real subprocess would exercise the identical Pydantic `extra="forbid"` code path with strictly more incidental variables (network, process boot) and no additional discriminating power. | Cited; the PR-5 mutation corpus (`attester-service-caller-controlled-field-permitted`, §5) additionally proves this specific unit test is not merely passing by accident -- it detects the schema's own strictness being removed. |
| N. Attester auth ordering | `tests/test_attester_service.py::test_g_*` (a spy `AssessmentProvider` proving zero invocations on auth failure -- already the strongest available proof: it does not infer non-invocation from a status code, it counts calls directly) | Already rigorous. | Cited; also given a mutation-corpus entry (`attester-service-unauthenticated-call-permitted`) for regression protection. |
| O. Provider failure (unavailable/raising/malformed/signing failure) | `tests/test_attester_service.py::test_e_*/test_f_*` (exhaustive: config-load-time key failure, request-time signing failure via a broken-key double, provider raising/returning malformed output/having no configured entry) | Already exhaustive against the interface the current `AssessmentProvider` contract actually defines. No new timeout infrastructure was invented, per the task's explicit instruction. | Cited, not duplicated. |
| P. Bypass / alternate execution path | `tests/test_pre_execution_control_architecture_guards.py`, `tests/test_evidence_bound_execution_ticket_architecture_guards.py`, `tests/test_attester_service_architecture_guards.py` (static AST guards, all three PRs); `assurance/tests/test_exclusive_execution_path.py` (Workstream A, the ORIGINAL non-attestation bypass surface) | The static guards already prove every `issue_token` call site in `governance_service.py` is gated by Control, and pin `main.py`/`gateway/app.py`'s pre-existing, documented, non-attestation-gated `/evaluate` route as a KNOWN, reviewed exception (not a bypass of a path claiming to be governed by attestation -- it never claimed to be). The remaining, genuinely NEW-to-PR-5 question was dynamic: does the real deployment actually refuse to actuate the attested action without attestation, end to end? | `test_attestation_chain.py`'s positive baseline + every negative test IS this dynamic proof for the one action this SUT configures. The documented legacy exception (`main.py`/`gateway/app.py`) was investigated and confirmed to be exactly what PR-3's own architecture guard already names it: pre-existing, out of PR-2/3/4's governed-attestation scope, not a violation of any contract those PRs published. Not "fixed" (Phase 8: it is not a defect). |
| Q. Fail-closed infrastructure failure | `tests/test_pre_execution_control.py` (`ATTESTATION_REPLAY_UNAVAILABLE` path, in-process fake-failing registry); `tests/test_attester_service.py::test_e/test_f` | The assurance SUT's attestation nonce registry is `InMemoryNonceRegistry` (the deployment default -- `MCC_NONCE_BACKEND` is unset, exactly mirroring how `assurance.sut.harness.build_system_under_test`'s own Gateway is already configured for every OTHER workstream, none of which set `MCC_NONCE_BACKEND=redis` either). A real-Redis-killed-mid-scenario fault injection (mirroring Workstream B's `kill_notify`) was assessed and NOT added: it would prove the SAME `mcc_core.nonce.RedisNonceRegistry` fail-closed code path Workstream E's own real-Redis replay-resistance tests already exercise, since `PreExecutionControl` and `ExecutionGate` share the identical registry instance and interface (`gateway.governance_api._build_pre_execution_control`'s `nonce_registry_from_env(env)`) -- a second real-Redis-outage test would repeat Workstream E's own infrastructure and finding, not add a new one specific to attestation. | Documented as a deliberate non-duplication. The IN-MEMORY registry's own fail-closed-on-replay behavior (distinct from a backend OUTAGE) is what `test_g_attestation_replay_second_use_blocked` already exercises. |
| R. Crash/recovery | `assurance/state_machine.py`, `docs/EXECUTION_STATE_MACHINE.md`, Workstream B's real-process-kill fault injection (`assurance/tests/test_execution_atomicity.py`) | Investigated: `PreExecutionControl.evaluate()` completes synchronously, in-process, entirely BEFORE `DecisionEngine.issue_token()` is ever called (see the runtime mapping in §4 below) -- there is no cross-process or network hop inside Control itself when the shared registry is in-memory (this deployment's actual configuration), so there is no NEW crash window Control introduces beyond "the Gateway process itself crashes," which is already exactly Workstream B's existing scenario, unmodified by attestation. Once a token IS issued, the REST of the pipeline (`EnforcementCoordinator.enforce`, audit-before-actuation, `EXECUTION_UNKNOWN`->`RECONCILED`) is the identical, already-crash-tested generic mechanism, and evidence binding adds no new state to it beyond an extra signed claim on the same token. No new compensation/rollback semantics were invented. | No PR-5 defect found; the generic Workstream B invariant is cited as already covering the extended chain, with the reasoning above recorded rather than assumed. |

> **Production Trust Hardening Phase 1 update (forward reference, does not
> alter the historical PR-5 record above):** item Q's `InMemoryNonceRegistry`
> deployment default was, at the time PR-5 recorded it, an accurate
> description of every existing deployment profile's actual configuration
> -- not a defect PR-5 was scoped to fix. Phase 1 subsequently closed it for
> production/enforcement deployments: `MCC_DEPLOYMENT_MODE=enforcement`
> makes `nonce_registry_from_env` refuse the in-memory backend outright.
> Item M's caller-controlled-output boundary is similarly extended, not
> superseded: Phase 1 adds a second, production-specific boundary — which
> *provider implementation* an Attester process may trust — on top of the
> unchanged per-field boundary this row documents. See
> `docs/EXECUTION_AUTHORITY_BOUNDARY.md`'s "Production Trust Hardening Phase
> 1" section for the current state of both.

---

## 3. Adversarial end-to-end matrix (Phase 2)

`assurance/tests/test_attestation_chain.py`, through the real production
classes (`gateway.governance_service.GovernanceService`,
`gateway.pre_execution_control.PreExecutionControl`,
`mcc_core.core.DecisionEngine`, `mcc_core.gate.ExecutionGate`,
`mcc_core.coordinator.EnforcementCoordinator`), a real Gateway OS
subprocess, and a real Independent Attester Service OS subprocess
(`assurance/sut/attestation_harness.py`):

| Test | Property | Result | Actuation count |
|---|---|---|---|
| `test_positive_baseline_full_chain_executes_exactly_once` | Positive control | EXECUTED | exactly +1 |
| `test_a1_forged_attestation_untrusted_key_blocked_no_actuation` | A, K | BLOCKED (`ATTESTER_UNTRUSTED`) | +0 |
| `test_a2_tampered_signature_covered_claim_blocked_no_actuation` | A | BLOCKED | +0 |
| `test_a3_caller_manufactured_verified_field_rejected_structurally` | A | BLOCKED (structural: undeclared field) | +0 |
| `test_b_wrong_action_binding_blocked_no_actuation` | B | BLOCKED (`ATTESTATION_ACTION_MISMATCH`) | +0 |
| `test_c_wrong_payload_binding_blocked_no_actuation` | C | BLOCKED (`ATTESTATION_PAYLOAD_MISMATCH`) | +0 |
| `test_d_wrong_scope_blocked_no_actuation` | D | BLOCKED (`ATTESTATION_SCOPE_MISMATCH`) | +0 |
| `test_f_expired_evidence_blocked_no_actuation` | F | BLOCKED (real wall-clock expiry) | +0 |
| `test_g_attestation_replay_second_use_blocked` | G | first EXECUTED, second BLOCKED (`...REPLAY...`) | +1 total, not +2 |

Every negative test asserts BOTH the reported outcome AND the independently
observed `gateway_notification_receipt_count()` (the real mock
external-effect sink's own receipt count, read over its own HTTP endpoint —
never the response body's self-reported status alone), per the task's dual-
oracle requirement.

`test_b`/`test_d` additionally use a mandate whose own scope is WIDER than
the specific action/resource under test, so the property isolated is
`PreExecutionControl`'s own binding check, not the mandate's independent
authority check incidentally failing for the same input.

---

## 4. Runtime mapping (concrete code, informative)

| Model/test concept | Concrete production code |
|---|---|
| `VerifyEvidence` / evidence nonce consumption | `gateway.pre_execution_control.PreExecutionControl.evaluate()` — steps 1-7 (MCC-AT-002 §5, ATC-ORDER-001), nonce consumed last |
| Evidence binding survives a concurrent mutation (TOCTOU) | `PreExecutionControl.evaluate()`'s `raw_attestation = copy.deepcopy(raw_attestation)` snapshot, taken before any `await` |
| `IssueToken` | `mcc_core.core.DecisionEngine.issue_token(..., evidence_digest=...)` |
| `PresentEvidence` | `gateway.governance_service.GovernanceService._run(..., evidence=attestation)` → `EnforcementCoordinator.enforce(..., evidence=...)` |
| `GateAccept` | `mcc_core.gate.ExecutionGate._verify()`'s evidence-binding block (after policy/action/payload/binding checks, before nonce consumption) |
| No explicit "gate reject" transition (mismatch = not-enabled, not a new state) | `gate.py` returning `GateResult(False, "EVIDENCE_DIGEST_MISMATCH...")` **without** calling `self.nonce_registry.consume(...)` |

---

## 5. Negative control (Phase 3)

`assurance/sut/vulnerable_attestation_control.py` — `VulnerableAttestationControl`,
a deliberately vulnerable stand-in for `PreExecutionControl` implementing the
identical `async def evaluate(...)` interface but skipping:

1. Ed25519 signature verification entirely.
2. Attester trust-store resolution entirely (`attester_id`/`kid` are never checked against any registered anchor).
3. Attestation nonce consumption entirely (replay is unlimited).

`assurance.sut.vulnerable_attestation_control.run_negative_control_scenario()`
constructs two REAL, live `GovernanceService`/`EnforcementCoordinator`/
`ExecutionGate` stacks (in-process — a control-arm comparison of two Control
implementations against the same governed stack does not need the
subprocess SUT), wired one to the real `PreExecutionControl`, one to
`VulnerableAttestationControl`, and drives the IDENTICAL forged (untrusted-
key) attestation through both:

| Stack | Result | Actuation count |
|---|---|---|
| Real `PreExecutionControl` | BLOCKED (`ATTESTER_UNTRUSTED`) | 0 |
| `VulnerableAttestationControl` | **EXECUTED** | **1** |

`assurance/tests/test_attestation_negative_control.py` asserts exactly
this. This proves the SAME construct-forge-present-observe methodology
`test_attestation_chain.py` uses against the real chain has genuine
discriminating power — a suite that always reported the attestation chain
as secure, without ever being shown capable of reporting an insecure one as
insecure, would not be evidence of anything.

The vulnerable stand-in is never imported by, or wired into, any production
code path; it exists only inside `assurance/sut/` and is constructed only
inside the two negative-control test functions.

---

## 6. Mutation results (Phase 4)

Twelve new, narrowly targeted `Defect` entries added to `mutation/defects.py`
(now 38 total), each a single-line, plausible, code-review-survivable
regression of one named PR-1→4 security-critical decision not previously
represented:

| Mutant ID | Security property | Test that kills it |
|---|---|---|
| `attester-trust-check-disabled` | Attester trust resolution | `assurance/tests/test_attestation_chain.py::test_a1_forged_attestation_untrusted_key_blocked_no_actuation` |
| `attester-signature-verification-disabled` | Ed25519 signature check | `tests/test_mcc_attestation.py::test_03_forged_signature_is_invalid` |
| `attestation-action-binding-disabled` | action_hash binding | `assurance/tests/test_attestation_chain.py::test_b_wrong_action_binding_blocked_no_actuation` |
| `attestation-payload-binding-disabled` | payload_hash binding | `assurance/tests/test_attestation_chain.py::test_c_wrong_payload_binding_blocked_no_actuation` |
| `attestation-scope-binding-disabled` | scope binding | `assurance/tests/test_attestation_chain.py::test_d_wrong_scope_blocked_no_actuation` |
| `attestation-expiry-check-disabled` | validity-window (expiry) check | `assurance/tests/test_attestation_chain.py::test_f_expired_evidence_blocked_no_actuation` |
| `attestation-replay-consumption-ignored` | attestation nonce replay | `assurance/tests/test_attestation_chain.py::test_g_attestation_replay_second_use_blocked` |
| `evidence-digest-computed-from-caller-object-not-snapshot` | PR-3 TOCTOU fix | `tests/test_evidence_bound_execution_ticket.py::test_17_toctou_concurrent_mutation_during_nonce_consume_cannot_bind_mutated_artifact` |
| `evidence-digest-omitted-from-issued-token` | evidence_digest bound into token | `tests/test_evidence_bound_execution_ticket.py::test_06a_issued_token_carries_the_exact_evidence_digest` |
| `gate-evidence-digest-mismatch-ignored` | Gate exact-digest enforcement | `tests/test_evidence_bound_execution_ticket.py::test_09/test_10` |
| `attester-service-caller-controlled-field-permitted` | Attester request schema strictness | `tests/test_attester_service.py::test_b_caller_cannot_supply_a_bypass_shaped_field` |
| `attester-service-unauthenticated-call-permitted` | Attester service-to-service auth | `tests/test_attester_service.py::test_g_missing_auth_header_rejected_before_provider_is_called`, `test_g_wrong_auth_header_rejected_before_provider_is_called` |

**One candidate mutation class was assessed and deliberately NOT added:**
"move evidence check after destructive nonce/state transition where
ordering matters." The harness's mutation mechanism is an exact-substring
find/replace of a SINGLE contiguous span — it cannot express "physically
relocate this block of statements to a different position in the function"
as a well-formed, syntactically valid one-line mutation. This ordering
property already has TWO forms of evidence that a literal reordering in a
future edit would themselves catch: a static AST guard
(`tests/test_evidence_bound_execution_ticket_architecture_guards.py::test_gate_checks_evidence_before_consuming_nonce`,
which asserts source-line order directly) and a behavioral proof
(`tests/test_evidence_bound_execution_ticket.py::test_11_retry_with_correct_evidence_after_mismatch_succeeds_same_token`).
Forcing an awkward mutation to fit the harness's mechanism, when the
property is already covered by a MORE precise structural check, was judged
worse than recording the honest reason it was skipped.

**Full corpus result** (`PYTHONPATH=. python -m mutation`):

```json
{
  "total": 38,
  "detected": 38,
  "mutation_score": 1.0,
  "survived_defect_ids": []
}
```

(One defect, `attester-signature-verification-disabled`, initially survived
against a first-draft detector test that tampered a `claims` field — because
`PreExecutionControl`'s SEPARATE claim-policy check still independently
rejects that tampered claim value even with signature verification fully
disabled, so the mutation's effect was masked by an unrelated check. The
detector was corrected to `tests/test_mcc_attestation.py`'s own PR-1 unit
test, which asserts the `signature_verification` named check's status
directly at the pure verifier boundary, unaffected by any Control-layer
claim policy. Recorded here per the mutation corpus's own stated discipline:
a survived mutant is a genuine, reportable finding, not silently corrected
without a trace.)

---

## 7. Formal model result (Phase 5)

`model/AttestationEvidenceBinding.tla` + `.cfg` — a new, small, separate
module (not a modification of `MCCExecutionStateMachine.tla`, which remains
exactly as PR #71 left it and continues to model the ORTHOGONAL generic
token lifecycle this module does not duplicate).

**Invariants checked** (all six; see §4 above for the runtime mapping):

1. `Inv_TypeOK` — well-formedness.
2. `Inv_ExecutedImpliesAuthorized` — execution implies valid authority (a token was issued).
3. `Inv_ExecutedImpliesEvidenceVerified` — where required, execution implies verified evidence was bound before the token existed.
4. `Inv_ExecutedImpliesEvidenceMatch` — the evidence bound to the token matches the evidence presented at the Gate (the central MCC-AT-003 claim).
5. `Inv_NoDoubleEvidenceNonceConsumption` — attestation-nonce replay cannot produce a second binding.
6. `Inv_NoDoubleTokenNonceConsumption` — token-nonce replay cannot produce a second execution.

**TLC result:**

```
Model checking completed. No error has been found.
89 states generated, 41 distinct states found, 0 states left on queue.
The depth of the complete state graph search is 6.
```

**Retry-after-mismatch** (PR-3's "wrong evidence first, correct evidence
second, same token, succeeds" property) is expressed structurally, not as a
separate transition: there is no explicit "gate reject" action in this
model — a mismatched `GateAccept` is simply not ENABLED, so the operation
remains in the `AUTHORIZED` state and a later `PresentEvidence` with the
correct artifact can still enable `GateAccept` for the identical,
still-unconsumed token nonce. This is a bounded, exhaustively-checked claim
about a small (2-operation, 2-evidence-value, 1-shared-nonce-each)
configuration — see §7's caveat below, and
`docs/REPRODUCING_ASSURANCE.md`'s identical caveat about
`MCCExecutionStateMachine.tla`'s own bound, which applies here without
modification: **this is evidence about the SHAPE of the evidence-binding
state machine and nonce single-use discipline, not proof that any
particular line of Python implements it correctly** — that remains the
adversarial E2E tests' (§3) and unit tests' job.

`model/run_tlc.sh` now runs both specs in sequence (§8), unconditionally,
with no new CLI flag — existing callers (`scripts/verify_assurance.sh`,
`docs/REPRODUCING_ASSURANCE.md`) are unaffected.

---

## 8. Integration with the existing assurance entry point (Phase 7)

No parallel framework was created:

* `assurance/tests/test_attestation_chain.py` and
  `test_attestation_negative_control.py` are discovered automatically by
  `assurance.runner.discover_test_modules()`'s existing `glob("test_*.py")`
  — zero changes to `assurance/runner.py`, `assurance/cli.py`, or
  `assurance/__main__.py` were needed.
* `model/run_tlc.sh` was extended (not replaced) to run the new spec after
  the existing one, preserving its exact single-CLI-argument backward
  compatibility for the first spec.
* `mutation/defects.py` gained 12 entries in the same list `python -m
  mutation` already iterates — zero changes to `mutation/harness.py`,
  `mutation/cli.py`, or `mutation/detectors.py`.
* `scripts/verify_assurance.sh` — **entirely unmodified.** Its existing
  three `run_stage` calls (`make independent-assurance`, `model/run_tlc.sh`,
  `make mutation-test`) transparently pick up all of the above, and its
  pre-flight/post-flight clean-tree checks are untouched and still pass.
* `assurance/sut/harness.py`'s `build_system_under_test()` gained one
  optional, backward-compatible parameter (`extra_env`, default `None` =
  byte-for-byte prior behavior) so `assurance/sut/attestation_harness.py`
  could wire PR-2's own, unmodified `MCC_ATTESTATION_REQUIREMENTS_CONFIG`/
  `MCC_ATTESTATION_TRUST_CONFIG` env vars onto the SAME real Gateway
  subprocess every other workstream already boots.
* `tests/interoperability/_gateway_process.py` gained a 4-line, additive
  forward of those same two env vars, mirroring its own pre-existing
  `MCC_TRUST_CONFIG` conditional-forward pattern exactly.

---

## 9. Discovered defects (Phase 8)

**None.** No real runtime/security defect in PR-1 through PR-4 was found
during this independent assurance effort. Every adversarial attempt in §3,
every mutant in §6, and every invariant in §7 either failed as designed
(negative test) or held as designed (positive test/invariant), on the
first correctly-constructed attempt, with two exceptions that were harness
bugs in THIS PR, not production defects, both caught and fixed before
being reported as passing:

1. An early draft of `test_d_wrong_scope_blocked_no_actuation` issued a
   mandate scoped ONLY to the first resource, so the MANDATE's own
   resource-scope check failed before `PreExecutionControl`'s scope-binding
   check was ever reached — the test was isolating the wrong boundary, not
   revealing a Control defect. Fixed by issuing a mandate scoped to BOTH
   resources.
2. The `attester-signature-verification-disabled` mutant's first-draft
   detector test used the wrong test (see §6) — a harness/detector-test
   defect in this PR, not a production defect, and is documented rather
   than silently corrected.

---

## 10. Conformance table

| Claim | Implementation boundary | Evidence | Known limitation |
|---|---|---|---|
| A forged, tampered, or unbound attestation cannot produce execution through the real, multi-process, HTTP-driven deployment this repository provisions and tests. | `PreExecutionControl.evaluate()` + `ExecutionGate._verify()`, as deployed by `gateway.governance_api.build_governance_service` (unmodified by PR-5) | §3 (9 E2E tests, dual-oracle), §6 (7 targeted mutants) | Self-administered harness (top of this document). A bypass technique nobody on this project has thought of is, by construction, untested — identical to `docs/REPRODUCING_ASSURANCE.md`'s own stated limitation for the original 24. |
| An unregistered/removed Attester's material is rejected identically to a forgery. | `AttesterTrustStore.resolve()` | §2 row K, §3 `test_a1` | There is no live Attester-trust REVOCATION feature (distinct from mandate revocation, which exists and is tested elsewhere). This is a documented architectural boundary, not a tested-and-passing revocation claim. |
| The Attester service's private signing key is not required by, loaded by, or reachable from the assurance SUT's Gateway process. | `assurance/sut/attestation_harness.py`'s `extra_env` construction (public-key-only config files) | §2 row L | The deeper, genuinely cross-process proof (a separate OS process, runtime file-read interception, static AST guard) is PR-4's own `tests/test_attester_service_process_isolation.py`, cited here, not re-derived. |
| The evidence-verification → token-binding → Gate-acceptance chain, as a state machine, satisfies six named safety invariants (authority-before-execution, evidence-match, nonce single-use in two separate domains) for a small, bounded instance. | `model/AttestationEvidenceBinding.tla` | §7 (TLC: 41 states, 0 errors) | Bounded model checking of a small instance (2 operations, 2 evidence values, 1 shared nonce per domain) — not an inductive proof for arbitrary N, exactly like the companion model's own stated limitation. |
| The test methodology used above can actually detect a broken attestation-control implementation. | `assurance/sut/vulnerable_attestation_control.py` | §5 (negative control: vulnerable stack wrongly EXECUTED, real stack correctly BLOCKED, on the identical input) | Demonstrates discriminating power for the specific properties (signature/trust/replay) the vulnerable stand-in violates — not a claim that every conceivable Control defect would be caught this way. |

---

## 11. Reference implementation and conformance evidence

* `assurance/sut/attestation_harness.py` — SUT provisioning (real Attester
  subprocess + real Gateway subprocess configured for PR-2's attestation
  requirement).
* `assurance/sut/vulnerable_attestation_control.py` — negative control.
* `assurance/tests/test_attestation_chain.py` — 9 adversarial E2E tests.
* `assurance/tests/test_attestation_negative_control.py` — 3 negative-control
  tests.
* `mutation/defects.py` — 12 new `Defect` entries (38 total).
* `model/AttestationEvidenceBinding.tla` / `.cfg` — formal model.
* `model/run_tlc.sh` — extended to run both specs.
* `scripts/verify_assurance.sh` — unmodified; runs all of the above
  transparently through its existing three stages.

See `docs/REPRODUCING_ASSURANCE.md` for the reproduction procedure (`make
verify-assurance`), unchanged in structure, now covering this document's
scope too.
