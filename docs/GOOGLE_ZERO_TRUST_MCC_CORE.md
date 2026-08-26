# Google Zero-Trust Agents — MCC-Core Architecture Mapping

**Status:** Architecture / positioning document. Documentation only — no runtime
code, no new dependency, no adapter, and no new assurance stand accompany this
file.

**Primary source:** [Build zero-trust AI agents with Google's Agent Development
Kit](https://developers.googleblog.com/build-zero-trust-ai-agents-with-googles-agent-development-kit/)
(Google Developers Blog), and Google's accompanying reference implementation,
[`GoogleCloudPlatform/generative-ai — agents/adk/zero-trust-agents`](https://github.com/GoogleCloudPlatform/generative-ai/tree/main/agents/adk/zero-trust-agents).
Every claim below about Google's pattern is scoped to that published article and
reference implementation — it is not a claim about Google's broader security,
IAM, payment, ADK, or enterprise infrastructure. **A sourcing note on Rule 3's
exact wording is recorded at the end of this document** — this environment's
network egress policy blocked a direct fetch of the primary blog post, so
Rule 3's description here is reconstructed from Google's own public reference
repository plus multiple independent secondary summaries of the same article,
not from a verified verbatim quote of the blog text itself. Readers relying on
this document for a technical decision should confirm the exact wording against
the primary URL above.

---

## 1. Executive Summary

The LLM should not be the security boundary. A system prompt instructing an
agent "never refund more than an order's value" is not a hard security
guarantee — it is a request the model can be talked out of. Google's published
zero-trust agent pattern demonstrates exactly this principle in a concrete,
open-sourced reference implementation: hard security guarantees are moved
**outside** the model, into cryptographic write signing, isolated code
execution, and a deterministic gateway that checks proposed actions against
fixed rules before they reach the database.

MCC-Core is complementary to that pattern, not a competitor to it. Google's
published gateway answers whether a proposed operation falls inside a
deterministic, pre-configured policy envelope (transaction bounds, PII/secret
patterns, jailbreak signatures). MCC-Core answers a distinct question: **what
verified decision authority authorized this exact proposed action to execute
now** — bound to a specific actor, action, scope, policy state, nonce, and
validity window, with audit written before actuation.

The core distinction this document exists to make precise:

> **A permitted action is not necessarily an action authorized by the correct
> decision authority.**

---

## 2. What Google's Published Pattern Already Provides

Google's published architecture is real, working, external, pre-execution
enforcement — not a description of what agent security *should* look like, but
a reference implementation of what it *does* look like when the model is
removed from the trust boundary. Accurately, the published pattern provides:

- **Cryptographic provenance / integrity for writes.** Each state-changing
  database write is signed by the identity of the agent responsible for it
  before the database will commit the transaction, giving the database a
  cryptographic basis for attributing a mutation to a signing identity and for
  detecting later tampering with that record.
- **Isolated execution.** Agent-generated code (e.g. dynamically generated
  Python) runs inside a sandboxed, isolated environment rather than directly
  on infrastructure the agent could otherwise reach, containing what a
  compromised or misled generation step can do.
- **A deterministic semantic gateway.** A gateway sits between the model and
  the systems it can affect, applying fixed, non-model rules to both incoming
  prompts and outgoing tool calls/writes — evaluated deterministically, not by
  asking a second model to judge the first model's output.
- **Policy enforcement outside the model.** The rules the gateway applies
  (pattern-matching for PII/secrets, jailbreak-pattern detection, and hard
  numeric transaction bounds) are fixed, external, and cannot be argued with
  by a cleverly worded prompt.
- **Checks before external state mutation.** The gateway's transaction-bounds
  rule is evaluated **before** a proposed database write is permitted to
  proceed, not after.

**Rule 3 specifically performs deterministic hard transaction-bounds
enforcement on proposed SQL updates before the database mutation proceeds** —
for example, rejecting a proposed order/refund-affecting SQL update whose
transaction value does not match the bound associated with the order, with a
rejection reason to that effect. **This is real pre-execution enforcement.**
It is not merely advisory, and it is not a post-hoc detection mechanism: the
proposed write does not reach the database if Rule 3 rejects it.

Rule 3 is **not** described in this document as generic decision-authority
verification. It is a deterministic bounds/policy check on the shape and
magnitude of a proposed write — a distinct and narrower control question from
the one MCC-Core addresses (Section 3).

---

## 3. MCC-Core's Distinct Control Question

> **POLICY PERMISSION != DECISION AUTHORITY**

Concrete example: a proposed **$149 refund** may:

- come from a valid cryptographic identity,
- be correctly signed,
- satisfy the configured transaction limit (Google's Rule 3 would pass it —
  it is within bounds and well-formed),
- pass every deterministic gateway policy check.

All of that establishes that the operation falls **inside a permitted
envelope**. It does not, by itself, answer a separate question:

> **What verified authority authorized this exact $149 refund?**

Passing a bounds or policy check tells you the *shape* of the request is
acceptable. It does not tell you whether the specific decision to execute
*this* action, for *this* actor, under *this* policy state, within *this*
validity window, has not already been consumed (replay), has not been altered
in transit (action-binding), and was recorded as authorized before the write
was attempted (audit-before-actuation). MCC-Core's decision boundary exists to
make that second question an independently enforced, fail-closed invariant —
regardless of whether the deployment also has a gateway like Google's in front
of the database.

---

## 4. Control-Layer Comparison

| Control question | Google published pattern | MCC-Core |
|---|---|---|
| LLM treated as security boundary? | No | No |
| Cryptographic provenance/integrity? | Yes | Compatible |
| Execution isolation? | Yes | Compatible |
| Deterministic policy before mutation? | Yes | Compatible |
| Hard transaction bounds before mutation? | Yes, Rule 3 | Compatible |
| Explicit decision-authority verification? | Not the primary focus of this published pattern | Yes |
| Authorization bound to exact proposed action? | Not the primary focus of this published pattern | Yes |
| Replay / nonce validation? | Separate / implementation-specific concern | MCC-Core invariant |
| Authority validity window? | Separate / implementation-specific concern | MCC-Core invariant |
| Audit-before-actuation? | Separate / implementation-specific concern | MCC-Core invariant |

Every "Google published pattern" cell above is scoped strictly to the
published article and reference implementation cited at the top of this
document — not to Google's security, IAM, or infrastructure offerings in
general.

---

## 5. Architectural Composition

The two layers are composable, not competing. Conceptually:

```text
Enterprise / Human / System Authority
              |
              v
       Decision Authority
              |
      signed authorization
              |
              v
          AI Agent
              |
       proposed action
              |
              v
      MCC-Core Boundary
      -----------------
      authority valid
      action binding
      scope
      policy binding
      nonce / replay
      validity window
      audit-before-actuation
              |
           ALLOW
              |
              v
   Deterministic Semantic Gateway
      --------------------------
      deterministic policy
      transaction bounds
      Rule 1 / Rule 2 / Rule 3
              |
              v
      API / Database / Tool
```

The exact ordering of MCC-Core and the semantic gateway can depend on
deployment architecture — a gateway-in-front-of-database topology and an
authority-boundary-in-front-of-agent topology are not mutually exclusive, and
either could sit closer to the agent or closer to the database depending on
where an integrator wants each check enforced. **The claim here is
composability, not a mandated topology.**

---

## 6. Core Invariants

> **IDENTITY != AUTHORITY**
> **POLICY PERMISSION != DECISION AUTHORITY**

- **Identity** establishes the principal — who (or what agent/service) is
  making the request. Google's cryptographic write-signing establishes this
  for a database mutation.
- **Signature** establishes provenance/integrity — that the request as
  received is the request as sent, unaltered, from that identity.
- **Policy** establishes whether an operation is inside permitted bounds —
  Google's Semantic Gateway (Rules 1–3) establishes this for a proposed
  prompt, tool call, or write.
- **MCC-Core** independently verifies whether the appropriate decision
  authority authorized the *exact* proposed action — a check that identity,
  signature, and policy-bounds checks do not by themselves answer, because
  each of them can hold true for an action nobody with the right authority
  actually decided to authorize (a replayed request, a stale approval, a
  request whose payload was altered after authorization was granted).

None of the four bullets above is a superset of another; they compose.

---

## 7. MCC-Core Execution Invariant

Represented conceptually (see the repository's canonical implementation —
`src/mcc_core/gate.py`, `src/mcc_core/coordinator.py`, `src/mcc_core/nonce.py`,
`src/mcc_core/audit.py` — for the actual enforced semantics; this section does
not modify or restate those modules' behavior, only names the invariant they
implement):

```text
EXECUTE only if:
    signature_verified
    AND decision_authority_valid
    AND scope_matches
    AND action_hash_matches
    AND nonce_not_replayed
    AND within_validity_window
    AND policy_hash_matches
    AND audit_before_actuation

Otherwise:
    FAIL CLOSED
```

This is a conceptual restatement for the purpose of this comparison document,
using repository-canonical terminology where it differs slightly from the
generic wording above (e.g. `ExecutionGate` verification, `EnforcementCoordinator`
a–h ordering, `RedisNonceRegistry` replay rejection, append-only audit written
before actuation). No runtime semantics were changed to produce this section.

---

## 8. What MCC-Core Does Not Replace

MCC-Core provides a framework-neutral pre-execution authority and enforcement
boundary between autonomous decision-making and actuation. It explicitly does
**not** replace:

- IAM
- cryptographic identity
- sandboxing
- deterministic semantic gateways (such as Google's published pattern)
- policy engines
- payment authorization
- zero-trust infrastructure

MCC-Core is the layer that answers "was the correct authority verified for
this exact action, right now" — a question that sits alongside, not instead
of, the systems above. See also
[`docs/RELATIONSHIP_TO_EXISTING_SYSTEMS.md`](RELATIONSHIP_TO_EXISTING_SYSTEMS.md)
for the repository's general positioning against policy engines, workload
identity, IAM, agent frameworks, observability, and functional safety systems
— the same "adds a layer, does not replace the layer below it" posture applies
here.

---

## 9. Future Interoperability Proof — Document Only

The scenarios below are a **future interoperability/demo specification only**.
They are not implemented by this change, and this document does not create,
plan, or schedule an assurance stand, benchmark, or Google ADK adapter to
implement them. They exist to make MCC-Core's testable claims about a
composed Google-pattern + MCC-Core deployment precise, for the benefit of a
future pilot, design partner, Google ADK integration, or external technical
reviewer who asks "would this actually compose, concretely?"

**Scenario 1 — bounds check passes, decision authority is missing**
```
Google-style transaction-bounds check: PASS
MCC authority: MISSING

Expected:
EXECUTION = DENY
```

**Scenario 2 — bounds check passes, decision authority and action binding are both valid**
```
Google-style transaction-bounds check: PASS
MCC authority: VALID
Exact action binding: VALID

Expected:
EXECUTION = ALLOW
```

**Scenario 3 — a previously valid authorization is reused**
```
EXECUTION = DENY
REASON = REPLAY
```

**Scenario 4 — the authorized action and the proposed action no longer match**
```
Authorization: refund = 149
Proposed action changed to: refund = 148

Expected:
EXECUTION = DENY
REASON = ACTION_BINDING_MISMATCH
```

**Scenario 5 — an originally valid authorization no longer matches current bound constraints**
```
Authorization was originally valid, but policy binding, validity window,
or another bound constraint no longer matches at execution time.

Expected:
EXECUTION = DENY
```

Implement these scenarios only if required by a pilot, a design partner, a
Google ADK integration, or external technical validation — not as a
speculative engineering task following from this document.

---

## Non-Goals of This Document

This document does not, and is not accompanied by:

- new runtime code
- a Google ADK dependency
- a Google adapter
- a new assurance stand or benchmark
- a change to cryptographic primitives, authorization semantics, or audit
  semantics
- new tests
- new tooling
- a duplicate of existing assurance documentation (see
  [`docs/ASSURANCE_INDEX.md`](ASSURANCE_INDEX.md) and
  [`docs/RELATIONSHIP_TO_EXISTING_SYSTEMS.md`](RELATIONSHIP_TO_EXISTING_SYSTEMS.md)
  for the repository's existing assurance and positioning documentation, which
  this file supplements rather than restates)

---

## Sourcing Note

This environment's network egress policy blocked a direct fetch of
`developers.googleblog.com` at the time this document was written. The
description of Google's three-layer pattern (cryptographic write signing,
isolated/sandboxed execution, and the Semantic Gateway's Rule 1 / Rule 2 /
Rule 3) is reconstructed from:

1. Google's own public reference implementation repository,
   [`GoogleCloudPlatform/generative-ai — agents/adk/zero-trust-agents`](https://github.com/GoogleCloudPlatform/generative-ai/tree/main/agents/adk/zero-trust-agents)
   (fetched directly), and
2. multiple independent secondary summaries of the same blog post (search
   results reporting on Google's article), used only to corroborate details
   already visible in (1).

Rule 3's characterization in Section 2 — hard transaction-bounds enforcement
on a proposed order/refund-affecting SQL update, evaluated before the
database write proceeds — is corroborated by both sources but is **not**
presented here as a verbatim quotation of the blog post's exact prose, since
that prose could not be directly fetched in this environment. A reader citing
this document in an external, bank/fintech, or pilot context should confirm
the exact wording against the primary URL at the top of this document before
quoting Rule 3 verbatim.
