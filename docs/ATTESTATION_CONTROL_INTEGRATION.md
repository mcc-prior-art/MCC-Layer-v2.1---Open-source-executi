# Pre-Execution Attestation Control Integration (PR-2)

**Status:** Implemented. This document describes
`gateway/pre_execution_control.py` and its wiring into
`gateway/governance_service.py` / `gateway/governance_api.py`, as they exist
after PR-2. See `specs/MCC-AT-002.md` for the normative specification and
`docs/ATTESTATION_ARCHITECTURE.md` for the PR-1 EvidenceAttestation
foundation this integration builds on (unchanged by PR-2).

## 1. What PR-2 adds

PR-1 built an independent, standalone Attester boundary: a versioned,
signed `EvidenceAttestation` and a deterministic cryptographic verifier.
Left there, it is inert — nothing in the runtime reads it, and a verified
attestation changes nothing about whether an executable decision token is
issued.

PR-2 closes that gap with exactly one new component,
`gateway.pre_execution_control.PreExecutionControl`, establishing the
runtime property:

```
VALID AUTHORITY
    +
REQUIRED VERIFIED ATTESTATION
    +
DETERMINISTIC CONTROL POLICY
    =
ELIGIBLE FOR DECISION-TOKEN ISSUANCE
```

For any action whose trusted Control policy requires pre-execution
attestation:

- **no required attestation → no executable decision token.**
- **invalid / untrusted / expired / mis-bound / replayed attestation → no
  executable decision token.**

Both directions of the non-authority boundary hold: a valid attestation with
no valid mandate/authority still yields no executable authority (the
caller's own authority check already denies first); a valid mandate with a
missing or invalid *required* attestation also yields no executable
authority (`PreExecutionControl` denies).

## 2. Where it sits

```
authority verification (MandateAuthority / ConsensusVerifier — UNCHANGED)
        |
        v
mandate CONSTRAIN rewrite, if any -> exact final forward_context
        |
        v
PreExecutionControl.evaluate()                      <-- NEW (PR-2)
        |
        |  1. resolve AttestationRequirement for the action
        |     (no match -> NOT_REQUIRED, proceed exactly as pre-PR-2)
        |  2. require a raw attestation document if one is needed
        |  3. compute expected action_hash / payload_hash / scope /
        |     policy_hash from TRUSTED inputs only
        |  4. invoke mcc_attestation.verify_attestation() itself
        |     (PR-1, unmodified — never trusts a caller-supplied
        |     "already verified" claim)
        |  5. evaluate the deterministic required-claims policy
        |  6. consume the attestation's nonce (mcc_core.nonce, shared
        |     registry, domain-separated key) -- LAST, only after every
        |     static check above already passed
        v
DecisionEngine.issue_token()                          (UNCHANGED)
        |
        v
ExecutionGate / EnforcementCoordinator (a-h order)     (UNCHANGED)
```

`PreExecutionControl` does not replace, wrap, or reimplement
`MandateAuthority`, `ConsensusVerifier`, `DecisionEngine`, `ExecutionGate`,
or `EnforcementCoordinator`. It is an additional precondition, evaluated
once per issuance attempt, strictly between authority resolution (including
any CONSTRAIN rewrite) and token issuance. It never issues a token, never
executes anything, and never grants authority itself.

## 3. AttestationRequirement — a small, declarative policy

`AttestationRequirement` is trusted Control configuration, never
caller-driven:

```python
AttestationRequirement(
    action_pattern="send_payment",         # fnmatch glob, first-match-wins
    evidence_type="risk_assessment",
    scope_template="payment:{resource}",   # str.format over trusted fields only
    require_payload_binding=True,          # default: bind to the exact final payload
    require_policy_binding=False,
    required_claims={"risk_class": ("low",)},
)
```

This is deliberately not a DSL. `required_claims` is evaluated as plain
deterministic equality/membership over the attestation's *signed* claims —
Control never recomputes risk, calls a model, or infers meaning; it checks
whether a signed claim value is inside a statically configured allowed set.
If a trusted Attester asserts `risk_class=low` and policy accepts `low`,
Control proceeds even if the Attester turned out to be wrong about the real
world — that is an attestation/policy failure, not a Control bypass (the
same doctrine PR-1 establishes for the Attester itself).

`AttestationRequirementRegistry.from_config(...)` builds a registry from a
JSON list (one dict per requirement, 1:1 field mapping) — see
`_build_pre_execution_control` in `gateway/governance_api.py` for the
`MCC_ATTESTATION_REQUIREMENTS_CONFIG` / `MCC_ATTESTATION_TRUST_CONFIG`
env-driven wiring, which mirrors the existing `MCC_REQUIRE_CONSENSUS`
fail-closed-startup convention: configuring requirements without a trust
config refuses to start rather than running with requirements no Attester
could ever satisfy.

## 4. The exact-payload rule

The single most important invariant this integration adds: an attestation
must apply to the payload that can actually execute.

If a mandate's constraints rewrite the proposed payload (a CONSTRAIN
verdict), the attestation's `payload_hash` — when the requirement mandates
payload binding, the default — must bind to `hash_payload(forward_context)`
computed **after** that rewrite, never the pre-constraint proposal. An
attestation bound to the original (pre-constraint) payload fails
`ATTESTATION_PAYLOAD_MISMATCH`, even though the rewritten payload is
strictly *safer* (e.g. a clamped-down amount). "Safer after constraining" is
not treated as sufficient — exact binding beats inference. A fresh
attestation, issued against the exact constrained payload, is required.

This is exercised end-to-end in
`tests/test_governance_service_attestation.py::test_22_*` (original-payload
attestation rejected after CONSTRAIN) and `::test_23_*` (attestation bound
to the exact constrained payload succeeds).

## 5. Replay protection: reusing `mcc_core.nonce`, not duplicating it

PR-1 deliberately left the attestation's `nonce` field structurally required
but unconsumed — replay enforcement was explicitly deferred to Control. PR-2
closes that gap by **reusing** the existing `mcc_core.nonce` registry
(`RedisNonceRegistry` / `InMemoryNonceRegistry`), not by building a second
replay algorithm:

- **Domain separation by key, not by registry.** Attestation nonce records
  are stored under `attestation:<attester_id>:<nonce>`; decision-token nonce
  records are stored bare. The same registry *instance* is shared between
  `ExecutionGate` (token nonces) and `PreExecutionControl` (attestation
  nonces) in `gateway/governance_api.py`'s `build_governance_service` —
  safe, because the two key spaces can never collide.
- **TTL derived from the attestation's own validity window** —
  `expires_at - now + clock_skew`, clamped to `[min, max]` — the identical
  discipline `ExecutionGate._nonce_ttl` already applies to token nonces.
  Never zero, negative, or unbounded.
- **Consumed last.** Nonce consumption is the final step of
  `PreExecutionControl.evaluate()`, after every static check (crypto, trust,
  binding, claim policy) has already passed. A failing static check never
  burns the nonce; a successfully consumed nonce can never authorize a
  second issuance.
- **Fail-closed on an indeterminate result.** No registry configured, or the
  registry raises: `ATTESTATION_REPLAY_UNAVAILABLE`, no token. A normal
  "already consumed" `False` return: `ATTESTATION_REPLAYED`, no token. (The
  underlying `mcc_core.nonce` contract deliberately collapses "replay" and
  "backend failure" into a single `False` from `consume()`; this is a
  best-effort distinction bounded by what that contract can report — see
  §7 below and `specs/MCC-AT-002.md` §8/§11.)

## 6. HTTP / service wiring

The strict execute request schemas
(`MandateExecuteRequest`/`ApprovalExecuteRequest`/`ConsensusExecuteRequest`
in `gateway/governance_api.py`) gained one new optional field:

```python
attestation: Optional[Dict[str, Any]] = None
```

Optional *at the transport level* for backward compatibility — an action
with no configured `AttestationRequirement` ignores it exactly as before.
Whether it is required is exclusively a trusted Control-policy decision:
omitting it for an action that *does* require attestation still fails
closed (`ATTESTATION_REQUIRED`, no token). There is no `verified`,
`trusted`, or similar precomputed field on any schema — the server always
re-verifies the raw document itself; a caller cannot assert verification
happened elsewhere. `PreExecutionControl.evaluate()` calls
`mcc_attestation.verify_attestation()` itself, on the raw attestation, on
every evaluation — never a caller-supplied
`AttestationVerificationResult`, never a bare `verified=true` flag.

Route handlers in `gateway/governance_api.py` remain transport-only: they
validate the schema and delegate to `GovernanceService`. All attestation
policy interpretation lives in `PreExecutionControl`, never in a FastAPI
handler.

## 7. Known limitation carried forward from PR-1

After PR-2, `PreExecutionControl` proves that a required attestation was
valid **at decision-token issuance time**. Until a future PR (anticipated:
the Evidence-Bound Execution Ticket) extends the decision-token schema
itself:

- the issued token carries no cryptographic evidence digest — a party
  inspecting only the token cannot independently confirm attestation
  occurred; that fact is provable only from the audit trail at issuance
  time;
- `ExecutionGate` does not independently re-check Attester revocation or
  re-verify evidence at actuation time; a trust anchor revoked *after* a
  token was validly issued does not retroactively invalidate that token.

This is documented explicitly, not hidden, in `specs/MCC-AT-002.md` §11 and
§9 (PR-3 Boundary).

## 8. Reference implementation and conformance evidence

- `gateway/pre_execution_control.py` — `AttestationControlReason`,
  `AttestationRequirement`, `AttestationRequirementRegistry`,
  `ControlAttestationResult`, `PreExecutionControl`.
- `gateway/governance_service.py` — `_attestation_gate` helper, wired into
  `execute_with_mandate` and `execute_with_consensus`;
  `execute_with_approval` delegates to `execute_with_mandate` and forwards
  `attestation` through.
- `gateway/governance_api.py` — HTTP schema `attestation` field on the three
  execute requests; `_build_pre_execution_control` env-driven builder
  (`MCC_ATTESTATION_REQUIREMENTS_CONFIG` / `MCC_ATTESTATION_TRUST_CONFIG`).
- `tests/test_pre_execution_control.py` — unit-level Control decisions.
- `tests/test_governance_service_attestation.py` — end-to-end through the
  real `GovernanceService` (real signed mandates, real consensus quorum,
  real attestations).
- `tests/test_pre_execution_control_architecture_guards.py` — static AST
  guards: the HTTP layer never calls `issue_token` directly; every
  `issue_token` call site in `governance_service.py` is preceded by the
  attestation gate; no LLM/model/agent-framework dependency in the Control
  path; no bypass-shaped schema field.

See `specs/MCC-AT-002.md` for the full normative specification.
