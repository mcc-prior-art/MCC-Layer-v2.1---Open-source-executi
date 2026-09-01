# MCC-AT-002

# Pre-Execution Attestation Control Integration Specification

Document ID: MCC-AT-002

Version: 0.1

Status: Draft

Category: Normative Specification (Draft)

Applies To: MCC-Core Pre-Execution Attestation Control Integration (PR-2)

Language: English (Normative)

---

# Status of This Specification

This document is a **Draft**. It defines the normative Control-layer
integration of MCC-AT-001 EvidenceAttestation into MCC-Core's existing
authority-to-decision-token issuance path, implemented by
`gateway/pre_execution_control.py` in PR-2. It has not undergone the Final
Acceptance Review process used elsewhere in this repository's Specification
Program (see `docs/MCC_SPECIFICATION_PROGRAM_NORMATIVE_V1_0.md`) and does
not carry Normative status.

This specification does not amend, weaken, or restate MCC-AT-001. MCC-AT-001
governs the EvidenceAttestation artifact itself (schema, signature,
immutability, trust, verification order, non-authority boundary). This
document governs a distinct, later concern: how a *verified* attestation
becomes an input to a Control decision about whether an executable decision
token MAY be issued. Where the two overlap (e.g. the verification order),
this document cross-references MCC-AT-001 by requirement ID rather than
duplicating it.

The key words MUST, MUST NOT, REQUIRED, SHALL, SHALL NOT, SHOULD, SHOULD NOT,
RECOMMENDED, MAY and OPTIONAL in this specification are to be interpreted as
described in RFC 2119 and RFC 8174.

Reference implementations are informative unless explicitly stated
otherwise.

---

# Abstract

PR-1 (MCC-AT-001) established EvidenceAttestation as a cryptographically
attributable, pre-execution evidence artifact that explicitly grants no
authority. Left on its own, a verified attestation is inert: nothing in the
runtime reads it, and nothing changes about whether a decision token is
issued.

This specification defines the Control-layer boundary — `PreExecutionControl`
— that closes that gap for actions whose trusted Control policy requires
pre-execution attestation, without altering the authority mechanisms
(`MandateAuthority`, `ConsensusVerifier`), the token issuer (`DecisionEngine`),
the gate (`ExecutionGate`), or the actuation coordinator
(`EnforcementCoordinator`) that already exist. It establishes the runtime
property:

```
VALID AUTHORITY
    +
REQUIRED VERIFIED ATTESTATION
    +
DETERMINISTIC CONTROL POLICY
    =
ELIGIBLE FOR DECISION-TOKEN ISSUANCE
```

Core doctrine, unchanged from MCC-AT-001 and preserved verbatim:

```
Intelligence assesses.
Attestation makes the assessment attributable.
Control verifies.
Execution acts.
```

**Control does not classify risk. Control does not decide whether an
Attester's semantic assessment is true.** Control deterministically verifies
whether required trusted evidence and authority exist for this exact action,
now. A signature does not make an assessment true: if a trusted Attester
asserts `risk_class=low` and trusted deterministic policy accepts `low`,
Control MAY proceed even if the Attester was wrong about the real world —
that is an attestation/policy failure, not a Control bypass.

---

# 1. Core Doctrine (ATC-DOC)

**ATC-DOC-001.** The MCC-AT-001 doctrine formula (AT-DOC-001) applies
unchanged and MUST be preserved verbatim wherever this integration is
described.

**ATC-DOC-002.** Control MUST NOT recompute risk, invoke a fraud model or
LLM, infer meaning from a claim's value, or compare a claim against a hidden
probabilistic judgment. Control's only permitted operation over `claims` is
deterministic equality/membership evaluation against a trusted, statically
configured allowed-value set (§5).

**ATC-DOC-003.** An EvidenceAttestation MUST NOT itself grant authority.
Authority is, and remains exclusively, the output of `MandateAuthority` or
`ConsensusVerifier` (or an equivalent existing authority mechanism), verified
independently of and never in place of attestation. Both of the following
MUST hold simultaneously for an action gated by an `AttestationRequirement`:

- a valid, verified attestation with **no** valid authority MUST NOT yield
  executable authority;
- valid authority with a **missing or invalid** required attestation MUST
  NOT yield executable authority.

---

# 2. Conceptual Model (ATC-MODEL)

**ATC-MODEL-001.** This specification introduces exactly one new
architectural component, `PreExecutionControl`, positioned as follows:

```
authority verification (MandateAuthority / ConsensusVerifier, unchanged)
        |
        v
mandate CONSTRAIN rewrite (if any) -> exact final forward_context
        |
        v
PreExecutionControl.evaluate()   <-- THIS SPECIFICATION
        |  invokes mcc_attestation.verify_attestation() itself (MCC-AT-001)
        |  applies deterministic AttestationRequirement / claim policy
        |  consumes the attestation nonce (mcc_core.nonce, domain-separated)
        v
DecisionEngine.issue_token()      (unchanged)
        |
        v
ExecutionGate / EnforcementCoordinator (unchanged, a-h order)
```

**ATC-MODEL-002.** `PreExecutionControl` MUST NOT replace, wrap, or
reimplement `MandateAuthority`, `ConsensusVerifier`, `DecisionEngine`,
`ExecutionGate`, or `EnforcementCoordinator`. It is an additional
precondition inserted strictly between authority resolution (including any
mandate CONSTRAIN rewrite) and token issuance.

**ATC-MODEL-003.** `PreExecutionControl` MUST NOT itself issue a decision
token, execute an action, or grant authority. Its output (§4) is a
recommendation to proceed or a fail-closed refusal; the caller (the existing
`GovernanceService` issuance method) remains the only code path that invokes
`DecisionEngine.issue_token`.

**ATC-MODEL-004.** This specification does not alter, extend, or bind into
the decision-token schema itself. `PreExecutionControl` proves that a
required attestation was valid *before* token issuance; it does not
cryptographically bind the attestation into the issued token or make the
token's own validity depend on the attestation's continued existence after
issuance. See §9 (PR-3 Boundary) for what remains deferred.

---

# 3. Attestation Requirement Policy (ATC-REQ)

**ATC-REQ-001.** Whether an action requires attestation, and what that
attestation MUST assert, is determined exclusively by trusted Control
configuration (an `AttestationRequirement`, resolved by
`AttestationRequirementRegistry`), never by the caller and never by the
attestation document itself. An HTTP caller supplying an `attestation` field
for an action with no configured requirement has no effect beyond what the
requirement registry allows (§6, ATC-COMPAT-001).

**ATC-REQ-002.** An `AttestationRequirement` MUST express, at minimum:

- an action pattern (an `fnmatch` glob over the action name, first-match-wins
  in registration order — the same convention as
  `mcc_core.authority.AuthorityModel`'s policy resolution);
- the required `evidence_type`;
- a deterministic scope template or equivalent deterministic scope
  resolution, evaluated only over trusted inputs (the action name and the
  resource identifier already established by the caller's own authority
  check) — never over caller- or attestation-supplied scope;
- whether exact final-payload binding (`payload_hash`) is mandatory;
- whether policy binding (`policy_hash`/`policy_version`) is mandatory;
- a deterministic required-claims policy: a mapping from claim name to a
  closed set of allowed values.

**ATC-REQ-003.** This specification does not define, and a conforming
implementation MUST NOT introduce, a general-purpose claim-policy expression
language. Deterministic equality/membership over top-level, canonically
serializable scalar claim values (MCC-AT-001 AT-SCHEMA-007) is sufficient and
REQUIRED; no additional expressiveness (arithmetic, regex, nested-path
matching, external lookups) is in scope.

**ATC-REQ-004.** The expected scope value used for the MCC-AT-001
`scope`-binding check (AT-VERIFY-009, item 11) MUST be computed by the
`AttestationRequirement` from trusted Control inputs only. Neither the HTTP
caller nor the attestation document may choose, override, or influence the
expected scope value.

---

# 4. Control Decision (ATC-RESULT)

**ATC-RESULT-001.** `PreExecutionControl.evaluate()` MUST return a
structured result (`ControlAttestationResult`) carrying at minimum: a
Boolean `ok`, a closed-enumeration `reason_code`
(`AttestationControlReason`), a human-readable `reason`, and — whenever
MCC-AT-001 verification was actually attempted — the underlying
`AttestationVerificationResult` for audit. A bare Boolean return does not
conform.

**ATC-RESULT-002.** `reason_code` MUST be a closed enumeration. At minimum
the following distinct, machine-readable reasons MUST be distinguishable:

`NOT_REQUIRED`, `VERIFIED`, `ATTESTATION_REQUIRED`, `ATTESTATION_INVALID`,
`ATTESTER_UNTRUSTED`, `ATTESTATION_EVIDENCE_TYPE_MISMATCH`,
`ATTESTATION_ACTION_MISMATCH`, `ATTESTATION_PAYLOAD_MISMATCH`,
`ATTESTATION_SCOPE_MISMATCH`, `ATTESTATION_POLICY_MISMATCH`,
`ATTESTATION_NOT_YET_VALID`, `ATTESTATION_EXPIRED`,
`ATTESTATION_CLAIM_POLICY_MISMATCH`, `ATTESTATION_REPLAYED`,
`ATTESTATION_REPLAY_UNAVAILABLE`, `ATTESTATION_CONTROL_ERROR`.

**ATC-RESULT-003.** `ok=True` MUST correspond to exactly the reason codes
`NOT_REQUIRED` and `VERIFIED`; every other reason code MUST correspond to
`ok=False`. A conforming implementation MUST enforce this correspondence
structurally (e.g. reject construction of an inconsistent result), not by
convention alone.

**ATC-RESULT-004.** An `ok=False` result MUST NOT carry a token, a signed
authorization, or any artifact usable by the caller to proceed with
issuance. The only effect of `ok=False` is that the caller's existing
issuance method returns a BLOCKED/DENY outcome without ever calling
`DecisionEngine.issue_token`.

---

# 5. Required Evaluation Order (ATC-ORDER)

**ATC-ORDER-001.** For an action with a configured `AttestationRequirement`,
`PreExecutionControl.evaluate()` MUST perform the following steps in order.
A conforming implementation MUST NOT skip a step because a caller believes
an earlier step already passed:

1. Resolve the `AttestationRequirement` for the action (`NOT_REQUIRED` short
   circuit if none matches — proceed to §6 unchanged behavior).
2. Reject a missing or non-document `attestation` input as
   `ATTESTATION_REQUIRED`.
3. Compute the expected binding values from trusted inputs only: expected
   `action_hash` (from the action name), expected `payload_hash` (from the
   exact final `forward_context` — see §7, only when the requirement mandates
   payload binding), expected `scope` (§3, ATC-REQ-004), expected
   `policy_hash`/`policy_version` (only when the requirement mandates policy
   binding).
4. Invoke `mcc_attestation.verify_attestation()` itself, over the raw
   attestation document, with those expected values (ATC-VERIFY-001). This
   performs the full MCC-AT-001 AT-VERIFY-001 order (structural validation,
   trust resolution, signature, evidence-type authorization, validity
   window, action/payload/scope/policy binding).
5. On a non-`VERIFIED` MCC-AT-001 result, translate the failing named check
   into the corresponding `AttestationControlReason` (§4) and return
   `ok=False`. No further step executes.
6. Evaluate the deterministic required-claims policy (§3, ATC-REQ-002)
   against the attestation's signed `claims`. A missing required claim or a
   claim value outside its allowed set returns
   `ATTESTATION_CLAIM_POLICY_MISMATCH`, `ok=False`. No further step
   executes.
7. Consume the attestation's nonce against the replay registry (§8). Only on
   successful, first-use consumption does evaluation return `ok=True,
   VERIFIED`.

**ATC-ORDER-002.** Nonce consumption (step 7) MUST be the last action
`PreExecutionControl.evaluate()` performs before returning `ok=True`. Every
static check (structural, cryptographic, trust, binding, claim policy) MUST
already have passed before the nonce is consumed. A failing static check
MUST NOT consume the nonce.

**ATC-ORDER-003.** The caller (the existing `GovernanceService` issuance
method) MUST invoke `PreExecutionControl.evaluate()` strictly after
resolving authority and applying any mandate CONSTRAIN rewrite, and strictly
before calling `DecisionEngine.issue_token()`. No code path that reaches
`DecisionEngine.issue_token()` for an action governed by an
`AttestationRequirement` may do so without an intervening `ok=True`
`PreExecutionControl.evaluate()` call.

**ATC-VERIFY-001.** `PreExecutionControl` MUST invoke MCC-AT-001's
`verify_attestation()` itself, over the raw (untrusted) attestation
document, on every evaluation. It MUST NOT trust, and MUST NOT accept as a
substitute for its own call, any caller-supplied `verified=true` flag,
pre-built `AttestationVerificationResult`, "already checked" claim, unsigned
risk result, or model-reported confidence value. The HTTP transport schema
(§6) accordingly carries no such field (ATC-COMPAT-003).

---

# 6. Exact-Payload Binding (ATC-PAYLOAD)

**ATC-PAYLOAD-001.** When an `AttestationRequirement.require_payload_binding`
is true (the default), the expected `payload_hash` supplied to
`verify_attestation()` MUST be computed over the **exact final payload** the
caller is about to pass to `DecisionEngine.issue_token()` — i.e. the mandate
authority's `forward_context` **after** any CONSTRAIN rewrite, or the
canonicalized payload for a consensus-authorized action with no mandate
rewrite step. It MUST NOT be computed over the pre-constraint proposed
payload.

**ATC-PAYLOAD-002.** An attestation whose `payload_hash` was computed over a
payload that a mandate's constraints subsequently rewrote MUST fail
`payload_hash` binding (MCC-AT-001 AT-VERIFY-009/010,
`ATTESTATION_PAYLOAD_MISMATCH`) and MUST NOT be treated as authorizing the
rewritten payload, even when the rewritten payload is a strict narrowing
(e.g. a clamped-down amount) of the original. "Safer after constraining" is
explicitly not a substitute for exact binding (ATC-DOC-002,
AT-VERIFY-010/AT-AUTH-001 in spirit: a signature proves attribution to a
specific bound payload, not to "any payload no more permissive than this
one"). A fresh attestation bound to the exact constrained payload is
required.

---

# 7. HTTP / Service Wiring (ATC-COMPAT)

**ATC-COMPAT-001.** Every governed runtime issuance path capable of calling
`DecisionEngine.issue_token()` for an action that MAY be governed by an
`AttestationRequirement` MUST route through `PreExecutionControl` before
issuance. As of this specification's reference implementation, this is
`GovernanceService.execute_with_mandate` and
`GovernanceService.execute_with_consensus` (the latter reached directly by
`/consensus/execute`; `/mandates/execute` and `/approvals/{id}/execute` both
resolve to `execute_with_mandate`). This requirement is a structural,
testable property (`tests/test_pre_execution_control_architecture_guards.py`),
not a matter of code review alone.

**ATC-COMPAT-002.** The strict HTTP execute request schemas (mandate,
approval, consensus) MUST accept an optional raw attestation document field
(reference implementation: `attestation: Optional[Dict[str, Any]]`). This
field being optional at the transport level MUST NOT be read as attestation
being optional in general: whether it is required is exclusively a trusted
Control-policy decision (§3). Omitting it for an action with a configured
`AttestationRequirement` MUST result in a BLOCKED/DENY outcome
(`ATTESTATION_REQUIRED`), never in silent issuance.

**ATC-COMPAT-003.** No execute request schema may carry a field whose
purpose is to assert that an attestation has already been verified, is
trusted, or may bypass Control's own verification (e.g. `verified`,
`attestation_verified`, `trusted`, `skip_attestation`). This is a structural,
testable requirement.

**ATC-COMPAT-004.** For an action with no configured `AttestationRequirement`,
runtime behavior MUST be identical to the pre-PR-2 behavior in every
observable respect: same verdicts, same reasons, same audit shape. This
applies equally when no `PreExecutionControl` is configured at all (the
Control boundary itself is optional deployment configuration).

**ATC-COMPAT-005.** FastAPI route handlers MUST NOT contain attestation
policy-interpretation or verification logic. They MUST remain limited to
request/response schema validation and delegation to `GovernanceService`.

---

# 8. Attestation Replay Protection (ATC-REPLAY)

**ATC-REPLAY-001.** `PreExecutionControl` MUST consume the attestation's
`nonce` exactly once per attestation, using the *existing*
`mcc_core.nonce` replay-protection primitive (`RedisNonceRegistry` /
`InMemoryNonceRegistry` / any conforming implementation of the same
interface). A conforming implementation MUST NOT introduce a second,
independent replay algorithm or registry (this closes MCC-AT-001's
AT-REPLAY-002 deferral; AT-REPLAY-003's prohibition on a competing registry
continues to apply and is satisfied by reuse).

**ATC-REPLAY-002.** The attestation nonce's registry key MUST be
domain-separated from the decision-token nonce's registry key, so that the
same underlying registry instance (and, where deployed, the same Redis
backend) MAY be safely shared between `ExecutionGate` (token nonces) and
`PreExecutionControl` (attestation nonces) with no possibility of collision.
The reference implementation's key form is
`attestation:<attester_id>:<nonce>`; any conforming key scheme MUST make an
attestation-domain key unconstructible as a bare token-domain key and vice
versa.

**ATC-REPLAY-003.** The replay-record TTL MUST be derived from the
attestation's own validity window (`expires_at`) plus a bounded clock-skew
margin, clamped to a configured `[min, max]` range — the same design
discipline `mcc_core.gate.ExecutionGate` already applies to decision-token
nonce TTLs. The TTL MUST NOT be unbounded, zero, or negative.

**ATC-REPLAY-004.** Nonce consumption MUST occur only after every check in
§5 (ATC-ORDER-001, steps 1–6) has passed, and MUST be the final step before
returning `ok=True` (ATC-ORDER-002). A successfully consumed nonce MUST NOT
be usable to authorize a second issuance: a second `evaluate()` call with
the identical attestation MUST fail with `ATTESTATION_REPLAYED`.

**ATC-REPLAY-005.** When the replay registry is unavailable, unconfigured,
raises during consumption, or otherwise cannot produce a definite
first-use/not-first-use answer, `PreExecutionControl` MUST fail closed
(`ATTESTATION_REPLAY_UNAVAILABLE` or `ATTESTATION_CONTROL_ERROR`, as
applicable) and MUST NOT return `ok=True`. Because the underlying
`mcc_core.nonce` registry contract deliberately collapses "replay detected"
and "backend failure" into a single `False` return from `consume()` (by
design — see `mcc_core.nonce`), a normal `False` return is reported as
`ATTESTATION_REPLAYED`; `ATTESTATION_REPLAY_UNAVAILABLE` is reserved for the
cases a conforming implementation can distinguish (no registry configured,
or the registry call itself raises). This is a best-effort distinction,
documented here rather than overstated: it does not claim to distinguish
every possible backend-failure mode from every possible replay from the
caller's perspective, only the ones structurally observable at this
boundary. See §11 (Known Limitations).

---

# 9. PR-3 Boundary (ATC-BOUNDARY)

**ATC-BOUNDARY-001.** This specification defines only that Control requires
and verifies attestation **before** issuance is permitted. It does **not**
define, and PR-2's reference implementation does **not** implement:

- binding an evidence digest into the decision-token schema itself;
- any change to `ExecutionGate`'s token-verification logic to check for an
  evidence digest;
- an Evidence-Bound Execution Ticket or any cryptographic binding between
  the issued token and the attestation that gated its issuance, beyond the
  fact that issuance did not proceed without it.

**ATC-BOUNDARY-002.** A future specification (anticipated: MCC-AT-003 or
equivalent, covering PR-3's Evidence-Bound Execution Ticket) is expected to
extend the decision-token schema and `ExecutionGate` to carry and verify a
cryptographic binding to the gating evidence. This specification explicitly
reserves that work and MUST NOT be read as having already implemented it. A
reference implementation MUST NOT present a partial mechanism (e.g. an
unsigned `attestation_id` copied onto the token) as if it were that
cryptographic binding.

---

# 10. Backward Compatibility (ATC-COMPAT continued)

**ATC-BC-001.** Deploying `gateway/pre_execution_control.py` and wiring it
into `GovernanceService` MUST NOT change any observable behavior for:
mandate verification, signed-mandate authority resolution, the ESCALATE
approval loop, Multi-Context Consensus, the consensus challenge flow,
decision-token verification and replay protection at `ExecutionGate`,
idempotency, velocity limits, revocation, audit-before-actuation, or any
existing adapter/SDK/pilot integration — for any action with no configured
`AttestationRequirement`, and in any deployment with no
`PreExecutionControl` configured at all.

**ATC-BC-002.** Configuring `MCC_ATTESTATION_REQUIREMENTS_CONFIG` without a
corresponding `MCC_ATTESTATION_TRUST_CONFIG` MUST refuse startup (fail
closed), mirroring the existing `MCC_REQUIRE_CONSENSUS` convention, rather
than silently running with requirements no Attester could ever satisfy.

---

# 11. Known Limitations (Informative)

*(Non-normative. Recorded here so the intermediate state after PR-2 is
documented explicitly, not discovered by omission.)*

After PR-2, `PreExecutionControl` proves that a required attestation was
valid **at decision-token issuance time**. Until a future PR implements the
ATC-BOUNDARY-002 extension:

- The issued decision token itself carries no cryptographic evidence digest.
  A party inspecting only the token cannot independently confirm attestation
  occurred; that fact is provable only from the audit trail produced at
  issuance time.
- `ExecutionGate` does not independently re-check Attester revocation or
  re-verify evidence at actuation time (the a-h coordinator order is
  unchanged by this specification). A trust anchor revoked *after* a token
  was validly issued does not retroactively invalidate that already-issued
  token.
- The replay-vs-backend-failure distinction in §8 (ATC-REPLAY-005) is
  best-effort, bounded by what the underlying `mcc_core.nonce` registry
  contract can distinguish.

---

# 12. Relationship to Existing MCC-Core Artifacts (ATC-REL)

**ATC-REL-001.** This specification does not alter, and PR-2's
implementation does not modify, `mcc_core.gate`, `mcc_core.authority`,
`mcc_core.mandate`, `mcc_core.consensus`, `mcc_core.coordinator`,
`mcc_core.core` (`DecisionEngine`), or `mcc_core.nonce`'s existing interface.

**ATC-REL-002.** This specification does not alter MCC-AT-001. Every
MCC-AT-001 requirement continues to apply unchanged to the EvidenceAttestation
artifact and to `mcc_attestation.verify_attestation()`, which
`PreExecutionControl` calls without modification.

**ATC-REL-003.** `mcc_attestation.verifier` remains, unchanged, the sole
cryptographic/structural verifier. This specification's deterministic claim
policy (§3, §5 step 6) is Control-layer interpretation performed by
`gateway/pre_execution_control.py`, never added to
`mcc_attestation.verifier`.

---

# 13. Conformance

**ATC-CONF-001.** An implementation conforms to this specification's PR-2
scope if it satisfies ATC-DOC-001 through ATC-DOC-003, ATC-MODEL-001 through
ATC-MODEL-004, ATC-REQ-001 through ATC-REQ-004, ATC-RESULT-001 through
ATC-RESULT-004, ATC-ORDER-001 through ATC-ORDER-003, ATC-VERIFY-001,
ATC-PAYLOAD-001 through ATC-PAYLOAD-002, ATC-COMPAT-001 through
ATC-COMPAT-005, ATC-REPLAY-001 through ATC-REPLAY-005, ATC-BOUNDARY-001
through ATC-BOUNDARY-002, ATC-BC-001 through ATC-BC-002, and ATC-REL-001
through ATC-REL-003.

**ATC-CONF-002.** `gateway/pre_execution_control.py`, together with its
wiring into `gateway/governance_service.py` and
`gateway/governance_api.py`, is the reference implementation of this Draft
specification as of PR-2 (version 0.1 of this document). See
`tests/test_pre_execution_control.py`,
`tests/test_governance_service_attestation.py`, and
`tests/test_pre_execution_control_architecture_guards.py` for the executable
conformance evidence.

---

# 14. Future Work (Informative)

The following are explicitly out of scope for this Draft and for PR-2, and
are noted here only to record intended direction, not as normative
requirements:

- Evidence-Bound Execution Ticket: cryptographically binding a verified
  evidence digest into the signed decision token / capability itself (§9).
- `ExecutionGate` independently re-checking Attester revocation or evidence
  validity at actuation time.
- A remote Attester trust-store service, HSM/KMS-backed key custody, or
  hardware-enforced key isolation.
- Promotion of this document from Draft to Normative via the repository's
  Final Acceptance Review process.
