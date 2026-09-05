# MCC-Core Execution Authority Boundary

This document defines the architectural distinction between **admission
control** (a policy decision about whether an action is acceptable) and
**execution authority** (a cryptographically attributable, action-bound
artifact that is independently re-verified at the execution boundary
before actuation).

It does not introduce a new authority system, a new protocol, or a new
runtime component. It names and cross-references components that already
exist and are already merged: `mcc_attestation` (PR-1), `PreExecutionControl`
(PR-2), the evidence-bound `DecisionEngine`/`ExecutionGate` (PR-3), the
Independent Attester Service (PR-4), and the independent assurance evidence
for the whole chain (PR-5). For full normative detail on any single stage,
follow the links in each section — this document is the conceptual map, not
the specification.

**Scope note.** This document describes the reference implementation in
this repository. It is a public reference architecture and reference
runtime, not a certified production system, a third-party-audited security
product, or evidence of a completed external deployment — see
[Claim Boundaries](#claim-boundaries) below.

---

## The conceptual chain

```
INTELLIGENCE
    |   proposes a candidate action (a proposal, not a permission)
    v
ATTESTATION
    |   an independent, signed, attributable assertion about the action
    |   ("Attestation makes the assessment attributable.")
    |   src/mcc_attestation/ (PR-1) + src/mcc_attester_service/ (PR-4)
    v
CONTROL
    |   verifies the attestation is authentic, trusted, current, and
    |   exactly bound to this action -- before any token is issued
    |   ("Control verifies.")
    |   gateway/pre_execution_control.py :: PreExecutionControl (PR-2)
    v
SIGNED AUTHORITY
    |   a signed, scoped, time-limited, replay-protected decision token,
    |   bound to the exact action_hash/payload_hash/policy_hash and,
    |   where an attestation was required, its evidence_digest
    |   src/mcc_core/core.py :: DecisionEngine.issue_token() (PR-3 extends
    |   this with evidence_digest)
    v
AUTHORITY VERIFICATION
    |   the execution gate independently re-verifies the token -- it does
    |   not trust that the token was issued correctly, it re-checks every
    |   binding itself, at the point of actuation
    |   src/mcc_core/gate.py :: ExecutionGate.verify() (PR-3 extends this
    |   with evidence_digest re-verification)
    v
GATE
    |   fail-closed enforcement order: token -> nonce -> idempotency ->
    |   velocity -> audit-before-actuation -> execute -> record -> finalize
    |   src/mcc_core/coordinator.py :: EnforcementCoordinator
    v
EXECUTION
        ("Execution acts.")
```

This extends, and does not replace, the existing PR-1 doctrine already
recorded in [`docs/ATTESTATION_ARCHITECTURE.md`](ATTESTATION_ARCHITECTURE.md):

```
Intelligence assesses.
Attestation makes the assessment attributable.
Control verifies.
Execution acts.
```

The additions here — **SIGNED AUTHORITY** and **AUTHORITY VERIFICATION** as
their own named stages — make explicit what was previously implicit inside
"Control verifies" and "Execution acts": that between a Control decision and
an actuation there is a distinct, cryptographically attributable artifact
(the decision token), and a distinct, independent re-verification of that
artifact (the gate), neither of which is the same operation as the
admission decision itself.

---

## Admission Control vs. Execution Authority

**Admission control** (a policy/rule engine, a classifier, an allow-list, an
approval workflow, or MCC-Core's own authority-resolution step in isolation)
answers, approximately:

> This action satisfies the admission criteria.

That answer is a decision. It can be logged, it can be correct or
incorrect, and it can be acted on directly by whatever produced it — but by
itself it is not a portable, independently checkable artifact. Nothing
stops the decision from being described differently by the time it reaches
an actuator, and nothing forces whatever executes the action to re-derive
or re-confirm that the decision was genuinely made, by whom, and for
exactly this action.

**MCC-Core execution authority** answers a different, narrower, and more
specific question:

> This exact action carries valid, attributable, action-bound execution
> authority under these specific conditions, and that authority has been
> verified at the execution boundary.

Concretely, in this runtime, that means:

1. An authorization decision (mandate/consensus/attestation-gated) is made.
2. That decision is turned into a **signed** artifact (the decision token) —
   not a log line, not a return value passed by reference, but an Ed25519-
   signed document.
3. That artifact is bound to the **exact** action, the **exact** payload,
   the **exact** policy under which it was issued, and — where configured
   — the **exact** attestation evidence it relied on.
4. Before actuation, the **execution gate independently re-verifies every
   one of those bindings itself** — it does not trust that step 1-3
   happened correctly; it re-derives the hashes, re-checks the signature,
   and re-checks the trust relationship, at the point of execution, not at
   the point of decision.

This is an architectural distinction, not a claim that admission control by
itself is inadequate for every purpose. A system that only needs step 1 may
not need steps 2-4. MCC-Core's claim is narrower and specific: **wherever an
action actually executes, this repository's reference implementation
requires steps 2-4, and step 4 cannot be skipped, weakened, or
short-circuited by whatever produced the admission decision.**

---

## Required security properties

Each property below is documented only to the extent the current reference
implementation actually supports it, with the exact enforcing code cited.
None of this is aspirational.

### 1. Cryptographic attribution

Execution authority (the decision token) and, independently, attestation
evidence are both signed with Ed25519 via the single shared primitive
`mcc_core.signing.SigningKey` (`src/mcc_core/signing.py`). The proven
relationship is: *this exact document was signed by the holder of this
exact private key, whose corresponding public key is present in the
verifier's trusted-key set* (`ExecutionGate`'s `trusted_keys` mapping kid →
public key; the Attester's separate trust set in
`gateway/trust.py`/`PreExecutionControl`'s `AttestationTrustStore`). A
signature does not prove the signed content is *true* — see
[Important Distinctions](#important-distinctions).

### 2. Exact-action binding

Every decision token carries `action_hash = hash_action(action)`
(`src/mcc_core/core.py::DecisionEngine.issue_token`). `ExecutionGate.verify`
independently recomputes this hash from the action the caller is actually
attempting and rejects on mismatch (`ACTION_HASH_MISMATCH`,
`src/mcc_core/gate.py`). An `EvidenceAttestation` separately carries its own
`action_hash` binding it to a specific action string
(`src/mcc_attestation/schema.py`).

### 3. Payload and evidence binding

The token also carries `payload_hash = hash_payload(payload)` over the
exact, final (post-constraint) forward context, re-checked by the gate
(`PAYLOAD_HASH_MISMATCH`). Where an attestation was required and verified,
`PreExecutionControl` derives `evidence_digest = hash_document(raw signed
attestation)` (`mcc_core.signing.hash_document`, the same canonicalize-then-
SHA-256 primitive `hash_payload` uses) and the token carries it as a claim
under its own signature (PR-3). `ExecutionGate` re-verifies the exact
artifact presented at execution time hashes to that digest
(`EVIDENCE_DIGEST_MISMATCH` / `EVIDENCE_REQUIRED` / `EVIDENCE_INVALID`,
`src/mcc_core/gate.py`).

**Evidence validity is not evidence truth.** A verified, correctly-bound
`evidence_digest` proves the exact attestation artifact `PreExecutionControl`
evaluated is the one presented to the gate — not that the attestation's
semantic claims (e.g. a risk assessment) are correct. See
[Important Distinctions](#important-distinctions).

### 4. Scope and policy binding

The token carries `policy_hash`, checked against the gate's own configured
policy hash (`POLICY_HASH_MISMATCH`). Mandates carry an explicit
`action_scope`/`resource_scope`, verified by `MandateVerifier`
(`src/mcc_core/mandate.py`) before a token is ever issued. Attestation
requirements (`gateway/pre_execution_control.py::AttestationRequirement`)
declare a `scope` string an attestation must match exactly
(`SCOPE_MISMATCH`) — this is deployment-declared, deterministic policy, not
inferred or best-effort matching.

### 5. Validity conditions

Decision tokens carry `iat`/`nbf`/`exp` (issued-at / not-before / expiry,
`src/mcc_core/core.py`); the gate rejects a token with a missing time
window, one presented before `nbf`, or after `exp`
(`INVALID_TIME_WINDOW`/`TOKEN_NOT_YET_VALID`/`TOKEN_EXPIRED`). Attestations
separately carry their own `issued_at`/`not_before`/`expires_at`
(`src/mcc_attestation/schema.py`), enforced by the attestation verifier
independently of the token's own time window.

### 6. Replay resistance

Each token carries a `nonce` (fresh per issuance, `uuid.uuid4().hex` unless
supplied). The nonce is **consumed** (atomically claimed, single use) by
`ExecutionGate.verify` via the shared `mcc_core.nonce` registry
(`NONCE_REJECTED` on replay or registry failure). Attestation nonces are
consumed separately by `PreExecutionControl`, domain-separated by key prefix
(`"attestation:<attester_id>:<nonce>"`) so the two nonce spaces cannot
collide even sharing one backing registry.

### 7. Execution-boundary (authority) verification

`ExecutionGate.verify` performs its checks in a fixed, deterministic order
(`src/mcc_core/gate.py`): token presence → trusted signing key → Ed25519
signature → audience → time window (`nbf`/`exp`) → verdict is executable
(`ALLOW`/`CONSTRAIN` only) → policy hash → action hash → payload hash →
evidence digest (only when the token is evidence-bound) → nonce consumption
(last, so a rejected token never burns its single-use nonce). This
verification happens **at the execution boundary**, independently of
whatever produced the token — the gate does not trust its own issuer's
process to have gotten it right.

### 8. Fail-closed behavior

Every one of the checks above returns a non-executable result
(`GateResult(False, reason)`) on failure — there is no code path in
`ExecutionGate.verify` that defaults to permitting execution on a missing,
malformed, expired, mismatched, or otherwise invalid authority artifact.
Infrastructure failure (a nonce registry that cannot be reached, an audit
write that cannot be confirmed) is treated the same way: fail closed, never
fail open (`src/mcc_core/coordinator.py`'s module docstring).

### 9. Trust-domain separation

The Independent Attester Service (`src/mcc_attester_service/`, PR-4) runs as
a genuinely separate OS process holding its own Ed25519 private key,
reachable only over HTTP by the Gateway and by callers. The proposing
model/agent has no code path to that private key or to the trusted claims it
signs (`AttestRequest` accepts only `action`/`resource`/`payload` —
`extra="forbid"` rejects any caller-supplied trusted-output field such as
`sig`, `kid`, `verified`, or `claims`). This separation is demonstrated, not
merely asserted, by a cross-process isolation test that generates the
Attester's key in a separate bootstrap subprocess and proves the parent
process never reads or generates the private key
(`tests/test_attester_service_process_isolation.py`). This does **not**
demonstrate physical machine isolation, network-level isolation, or
organizational separation of operators — those are deployment concerns
outside this repository's reference implementation; see
[Claim Boundaries](#claim-boundaries).

### 10. Audit-before-actuation

`EnforcementCoordinator`'s fixed enforcement order durably records the
pre-enforcement decision (step `e`) **before** the executor is invoked
(step `f`) — see the ordering comment at the top of
`src/mcc_core/coordinator.py`. An audit-write failure fails the operation
closed; it does not allow an unaudited actuation to proceed.

### 11. Compromised-Intelligence boundary

The precise, non-overclaiming guarantee this architecture makes about a
fully hostile Intelligence/agent caller (Production Trust Hardening Phase 1;
see `tests/test_compromised_intelligence_adversarial.py` for the 14-scenario
adversarial proof):

**MCC-Core MAY claim:** Compromise of the Intelligence layer does not give
the attacker the Attester signing key and does not permit it to forge a
trusted `EvidenceAttestation` or mint execution authority. Evidence remains
independently processed by the configured `AssessmentProvider`, verified by
Control, cryptographically bound into signed execution authority, and
independently checked at the execution boundary.

**MCC-Core MUST NOT claim:** that a compromised Intelligence layer can never
request or receive a valid assessment. That is not the architectural
boundary. A proposal is intentionally allowed to enter the assessment
pipeline — see [Admission Control vs. Execution Authority](#admission-control-vs-execution-authority)
above. What a compromised Intelligence layer cannot do is dictate the
trusted output of that assessment, bypass the configured
`AssessmentProvider`, forge or self-sign the resulting attestation, or turn
a genuine attestation into execution authority on its own.

A valid attestation does not itself grant execution authority — see
[Important Distinctions](#important-distinctions) below, which states this
independently of this section and is unchanged by it.

The semantic correctness of an assessment depends on the configured trusted
`AssessmentProvider`; MCC-Core guarantees attribution, integrity, binding,
and enforcement around that evidence, not the objective truth of the
assessment itself. A trusted `AssessmentProvider` that is wrong about the
real world produces a genuinely attributable, correctly bound, and
correctly enforced *wrong* decision — that is an assessment/policy failure,
not a boundary failure. See `mcc_attester_service/provider.py` for the
provider interface this applies to, and
[Production Trust Hardening Phase 1](#production-trust-hardening-phase-1)
below for the additional boundary around *which* provider a production
deployment may trust.

---

## Important distinctions

These boundaries are load-bearing, not stylistic, and this document does
not weaken any of them:

- **Attestation is evidence, not authority.** A valid attestation does not
  itself grant execution authority — see
  [`docs/ATTESTATION_ARCHITECTURE.md`](ATTESTATION_ARCHITECTURE.md) §3.
- **A valid signature does not make an assessment true.** It proves
  attribution and integrity — who asserted what, about which bound action,
  during which validity interval — never that the assessment's semantic
  content is correct.
- **A policy decision is not automatically an execution-authority
  artifact.** Only a signed, action-bound decision token, independently
  re-verified at the gate, is.
- **A model proposal is not permission.** The canonical doctrine —
  "A proposal is not permission." / "No verified decision — no execution."
  — is unchanged by this document.
- **External-to-the-model does not automatically mean "authorization."**
  A syntactically valid, correctly bound artifact signed by an untrusted or
  self-appointed key is not authority — trust is registration-based and
  explicit, never inferred from an artifact merely existing outside the
  model's own process.
- **A control becomes execution-authority enforcement only when the
  required authority is bound to the action and verified before
  execution.** Logging, monitoring, or advisory review of an action after
  the fact is not this boundary.

MCC-Core is not, and does not claim to replace:

- model alignment or safety training,
- runtime monitoring or observability tooling,
- content classifiers,
- enterprise security controls (IAM, network security, endpoint security),
- compliance or regulatory systems,
- legal or contractual controls.

It is a separate, narrower, pre-execution execution-authority boundary that
sits between a model's proposed action and that action's actuation.

---

## Claim boundaries

Consistent with the rest of this repository's documentation
(`docs/PILOT_ACCEPTANCE_CHECKLIST.md`, `docs/ATTESTATION_INDEPENDENT_ASSURANCE.md`,
the README's "Accurate Positioning" and "Claim Hygiene" sections):

- This is a **public reference architecture and reference runtime** for
  technical review, simulation, and local testing — not a certified
  production system.
- **Self-administered reproducible assurance is not a third-party audit.**
  `scripts/verify_assurance.sh` and the mutation/formal-model evidence it
  produces are reproducible by anyone who clones this repository; they are
  not an independent third-party attestation of security.
- **Repository tests are not production certification.** Passing this
  repository's test suite demonstrates the reference implementation behaves
  as documented against itself — it is not a certification, regulatory
  approval, or compliance determination.
- **Simulated/loopback actuation is not a completed external production
  pilot.** Every actuator exercised by this repository's own test suite and
  reference pilots (`pilot/reference_python/`) is local, simulated, or
  loopback-only — see `docs/PILOT_ACCEPTANCE_CHECKLIST.md` for what an
  externally attributable pilot result additionally requires.
- No wording in this document should be read as implying formal
  certification, regulatory approval, third-party security audit,
  production deployment, or a completed external pilot — none of those
  currently exist for this reference implementation.

---

## Production Trust Hardening Phase 1

Two production-hardening boundaries, added without altering the canonical
chain (`INTELLIGENCE → ATTESTATION → CONTROL → SIGNED EXECUTION AUTHORITY →
AUTHORITY VERIFICATION → GATE → EXECUTION`) or either PR-1 through PR-6
architecture:

**Durable replay protection.** `MCC_DEPLOYMENT_MODE` (`src/mcc_core/deployment_mode.py`)
is a minimal, explicit switch — `reference` (default) or `enforcement` —
kept deliberately separate from `MCC_ENV` (`gateway.trust.trust_set_from_env`),
which gates only the external-mandate trust-config requirement (see
`docs/PILOT_VOLTAGENT_DEPLOYMENT.md`'s own note that its Redis-backed
durability is "enforced by `MCC_*_BACKEND=redis`, independent of `MCC_ENV`").
In `enforcement` mode, `nonce_registry_from_env` (§6, Replay resistance,
above) refuses `MCC_NONCE_BACKEND=memory` — explicit or default — with the
same fail-closed `NonceConfigError` it already raises for a missing
`MCC_REDIS_URL`; it never silently substitutes one backend for another.
`scripts/redis_restart_replay_smoke.py` proves the resulting property
against a real Redis: a genuine signed `EvidenceAttestation` is executed to
completion, every Python object is destroyed and rebuilt from scratch
(simulating a Gateway restart), and the identical attestation is rejected
as a replay by the new instance — with an independent actuation counter
confirming no second side effect occurred.

**Production Attester provider boundary.** The shipped `DeterministicTestProvider`
(`mcc_attester_service/provider.py`) remains available for tests and local
reference runs, but `mcc_attester_service.provider_loader.assessment_provider_from_env`
refuses it outright in `enforcement` mode. A production/enforcement Attester
process must instead name its own trusted `AssessmentProvider` implementation
via `MCC_ATTESTER_PROVIDER_CLASS` (a dotted import path); the loader fails
closed if that variable is missing, unimportable, not an `AssessmentProvider`
subclass, is (or subclasses) `DeterministicTestProvider`, or raises during
construction. This package ships no concrete production provider — no LLM,
no ML classifier, no policy engine — consistent with PR-4's own non-goals;
the operator/application embedding MCC-Core supplies its own.

See [§11, Compromised-Intelligence boundary](#11-compromised-intelligence-boundary)
above for the precise claim this hardening does and does not extend, and
`tests/test_production_trust_hardening_architecture_guards.py` for the
static guards proving neither addition introduces a second replay
subsystem, a second authority/execution path, or a signing-key-adjacent
surface on the `AssessmentProvider` boundary.

**Phase 2 — durable revocation state.** A post-Phase-1 audit found that
`revocation_registry_from_env` (`src/mcc_core/mandate.py`) did not yet carry
the same `enforcement`-mode guard as `nonce_registry_from_env`: a mandate
issued with `revocation_required=True` and revoked via the default
in-memory backend would verify as `MANDATE_VERIFIED` again after a restart,
or on any other instance that never observed the revocation — the identical
risk shape Phase 1 closed for nonce replay, applied instead to revocation.
`revocation_registry_from_env` now refuses `MCC_REVOCATION_BACKEND=memory`
— explicit or default — under `MCC_DEPLOYMENT_MODE=enforcement`, mirroring
`nonce_registry_from_env`'s guard verbatim; no new registry type, backend
abstraction, or configuration mechanism was introduced.
`tests/test_mandate.py`'s revocation-durability tests prove restart
durability, cross-instance consistency (real Redis), and enforcement-mode
fail-closed behavior for both a missing-config and an unreachable-backend
configuration.

---

## See also

- [`docs/ATTESTATION_ARCHITECTURE.md`](ATTESTATION_ARCHITECTURE.md) — the
  full INTELLIGENCE → ATTESTER → CONTROL → EXECUTION architecture, PR-1
  through PR-4 in detail.
- [`docs/ATTESTATION_CONTROL_INTEGRATION.md`](ATTESTATION_CONTROL_INTEGRATION.md)
  — the normative PR-2 Control-integration specification.
- [`specs/MCC-AT-001.md`](../specs/MCC-AT-001.md) through
  [`specs/MCC-AT-004.md`](../specs/MCC-AT-004.md) — the normative
  specifications for each stage of the attestation-to-execution chain.
- [`docs/ATTESTATION_INDEPENDENT_ASSURANCE.md`](ATTESTATION_INDEPENDENT_ASSURANCE.md)
  — independent, reproducible adversarial assurance evidence for the
  complete chain (PR-5), including its own explicit gap matrix and claim
  boundaries.
- [`docs/REPRODUCING_ASSURANCE.md`](REPRODUCING_ASSURANCE.md) — how to
  reproduce the assurance evidence yourself.
- [`RUNTIME_DEPLOYMENT.md`](../RUNTIME_DEPLOYMENT.md) — `MCC_DEPLOYMENT_MODE`,
  `MCC_ATTESTER_PROVIDER_CLASS`, and the rest of the operational
  environment-variable reference.
- [`docs/PILOT_RUNBOOK.md`](PILOT_RUNBOOK.md) — the partner-facing pilot
  path that exercises this exact chain end to end (PR-6).
