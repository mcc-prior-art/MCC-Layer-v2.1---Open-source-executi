# MCC-AT-003

# Evidence-Bound Execution Ticket Specification

Document ID: MCC-AT-003

Version: 0.1

Status: Draft

Category: Normative Specification (Draft)

Applies To: MCC-Core Evidence-Bound Execution Ticket (PR-3)

Language: English (Normative)

---

# Status of This Specification

This document is a **Draft**. It defines the normative cryptographic binding
between a verified `EvidenceAttestation` (MCC-AT-001) and the signed decision
token that `PreExecutionControl` (MCC-AT-002) permitted to be issued,
implemented by `src/mcc_core/signing.py`, `gateway/pre_execution_control.py`,
`src/mcc_core/core.py`, `src/mcc_core/gate.py`, `src/mcc_core/coordinator.py`,
and `gateway/governance_service.py` in PR-3. It has not undergone the Final
Acceptance Review process used elsewhere in this repository's Specification
Program (see `docs/MCC_SPECIFICATION_PROGRAM_NORMATIVE_V1_0.md`) and does not
carry Normative status.

This specification does not amend, weaken, or restate MCC-AT-001 or
MCC-AT-002. MCC-AT-001 governs the EvidenceAttestation artifact itself.
MCC-AT-002 governs whether Control requires and verifies an attestation
*before* token issuance may proceed. This document governs a distinct, later
concern, explicitly reserved by MCC-AT-002 §9 (ATC-BOUNDARY-001/002): once
Control has verified a required attestation, how the issued decision token
itself carries a cryptographic, tamper-evident record of *which exact*
attestation justified issuance, and how the execution boundary enforces that
binding. Where the two overlap, this document cross-references MCC-AT-001 /
MCC-AT-002 by requirement ID rather than duplicating them.

The key words MUST, MUST NOT, REQUIRED, SHALL, SHALL NOT, SHOULD, SHOULD NOT,
RECOMMENDED, MAY and OPTIONAL in this specification are to be interpreted as
described in RFC 2119 and RFC 8174.

Reference implementations are informative unless explicitly stated
otherwise.

---

# Abstract

MCC-AT-002 closed the gap between a verified `EvidenceAttestation` and
whether a decision token may be issued at all — but deliberately left the
issued token itself blind to *which* attestation gated it (ATC-BOUNDARY-001).
A verifier holding only the token could not distinguish "issued because
attestation A was verified" from "issued because some attestation was
verified" from "issued with no attestation at all" without consulting the
audit trail out-of-band.

This specification closes that gap using the **existing** signed decision
token — not a second, parallel authority or token system — by defining:

```
VERIFIED AUTHORITY
    +
VERIFIED ATTESTATION (MCC-AT-002)
    -> evidence_digest
    +
SIGNED DECISION TOKEN (carries evidence_digest under its existing signature)
    +
EXECUTION GATE (exact evidence-digest match required)
    =
EXECUTION
```

Core doctrine, unchanged from MCC-AT-001/MCC-AT-002 and preserved verbatim:

```
Intelligence assesses.
Attestation makes the assessment attributable.
Control verifies.
Execution acts.
```

**An evidence digest does not mean "the assessment is true."** It means only
"this exact signed evidence artifact is the artifact Control verified when
this execution authority was issued." Truth of the attestation's semantic
claims remains, as under MCC-AT-002, a matter for the trusted Attester and
Control's deterministic claim policy — never for `ExecutionGate`.

---

# 1. Core Doctrine (EBT-DOC)

**EBT-DOC-001.** The MCC-AT-001 doctrine formula (AT-DOC-001) and the
canonical MCC-Core four-line formula ("The model proposes. MCC-Core decides.
The gate enforces. The audit chain records.") apply unchanged and MUST be
preserved verbatim wherever this specification is described.

**EBT-DOC-002.** An `evidence_digest` bound into a decision token MUST NOT be
interpreted, by any component, as an assertion that the evidence's semantic
claims are true, that the action is safe, or that risk was assessed
correctly. It is exclusively a cryptographic identity binding: *this token
was issued against exactly this signed artifact*. Semantic interpretation of
`claims` remains entirely Control's responsibility (MCC-AT-002 ATC-DOC-002),
performed once, before issuance, and never repeated or second-guessed by
`ExecutionGate`.

**EBT-DOC-003.** An EvidenceAttestation, evidence-bound or not, MUST NOT
itself grant authority (MCC-AT-002 ATC-DOC-003, unchanged). Authority remains
exclusively the output of `MandateAuthority` or `ConsensusVerifier`. Valid
evidence with no valid authority MUST NOT yield executable authority, and
this specification introduces no new path by which it could.

---

# 2. Conceptual Model (EBT-MODEL)

**EBT-MODEL-001.** This specification introduces no new architectural
component. It extends three existing ones — `PreExecutionControl`'s result
type, `DecisionEngine.issue_token()`'s claim set, and `ExecutionGate`'s
verification order — and adds one new shared primitive
(`mcc_core.signing.hash_document`, §3). The governed execution path is
unchanged:

```
authority verification (MandateAuthority / ConsensusVerifier, unchanged)
        |
        v
mandate CONSTRAIN rewrite (if any) -> exact final forward_context
        |
        v
PreExecutionControl.evaluate()  (MCC-AT-002, unchanged decision logic)
        |  on ok=True + attestation REQUIRED and VERIFIED:
        |  derives evidence_digest = hash_document(raw attestation)  <-- NEW
        v
DecisionEngine.issue_token(..., evidence_digest=...)   <-- EXTENDED (§4)
        |  evidence_digest, when present, becomes a signed claim
        v
governed execution path carries the exact raw evidence artifact alongside
the token (unchanged transport; new optional argument only)
        |
        v
EnforcementCoordinator.enforce() -> ExecutionGate.verify(..., evidence=...)
        |  signature -> audience/time -> verdict -> policy/action/payload
        |  -> generic binding -> EVIDENCE BINDING (NEW, §5) -> nonce consume
        v
execution (only if every check, including evidence binding, passed)
```

**EBT-MODEL-002.** `ExecutionGate` MUST NOT replace, wrap, or reimplement any
part of `PreExecutionControl`'s semantic verification or claim-policy
evaluation. Its evidence-binding check (§5) is a deterministic canonical
document-hash comparison only. `PreExecutionControl` MUST NOT be re-invoked,
and MCC-AT-001's `verify_attestation()` MUST NOT be re-invoked, at actuation
time to obtain or re-derive `evidence_digest` — it is produced exactly once,
as an output of the single successful `PreExecutionControl.evaluate()` call
that already gated issuance (MCC-AT-002 §5).

**EBT-MODEL-003.** `EnforcementCoordinator` remains the single governed
actuation path (MCC-Core doctrine: "The gate enforces"). This specification
adds no second actuation path, no second `ExecutionGate`, and no route to
execution that bypasses `EnforcementCoordinator.enforce()`. This is a
structural, testable property
(`tests/test_evidence_bound_execution_ticket_architecture_guards.py`).

---

# 3. Evidence Digest Algorithm (EBT-DIGEST)

**EBT-DIGEST-001.** The evidence digest of a complete signed
`EvidenceAttestation` document MUST be computed as:

```
evidence_digest = "sha256:" + hex(SHA-256(canonical_bytes(document)))
```

using the **existing** `mcc_core.signing.canonical_bytes()` (deterministic
field ordering, MCC-AT-001 AT-SCHEMA-006-equivalent canonicalization) and
`sha256_hex()` primitives — the same canonicalization every other signed or
hashed structure in this repository already uses. A conforming
implementation MUST NOT introduce a second, independent JSON
canonicalization algorithm for this purpose.

**EBT-DIGEST-002.** The reference implementation exposes this as
`mcc_core.signing.hash_document(document: Dict[str, Any]) -> str`, a
semantically generic alias of the identical `canonical_bytes` +
`sha256_hex` composition `hash_payload()` already performs — named generically
so that Control and the Gate cannot accidentally implement two different
digest algorithms that happen to agree today and silently drift apart later.

**EBT-DIGEST-003.** The digested `document` MUST be the **complete signed
representation** of the `EvidenceAttestation` — every field MCC-AT-001
defines as part of the signed artifact, including `kid` and `sig`
(`schema_version`, `attestation_id`, `attester_id`, `evidence_type`,
`claims`, `action_hash`, `payload_hash` when present, `scope`, `provenance`,
`policy_hash`/`policy_version` when present, `issued_at`, `not_before`,
`expires_at`, `nonce`, `kid`, `sig`) — never the unsigned claim subset
(MCC-AT-001's `unsigned_dict()`, which excludes `sig` and `kid`). Binding the
complete signed representation, not merely the semantic claims, means a
mutation to *any* field — including the signature itself — changes the
digest and therefore fails the Gate's exact-match check (§5). The reference
implementation computes `evidence_digest` from the exact raw attestation
dictionary `PreExecutionControl` successfully verified (`raw_attestation`,
as received), not from a re-serialized reconstruction, so the digest is
guaranteed to correspond to the exact bytes MCC-AT-001's signature
verification actually checked.

**EBT-DIGEST-004.** `evidence_digest` MUST be format-stable:
`sha256:<64 lowercase hexadecimal characters>`, matching the existing
`hash_action`/`hash_payload` convention.

**EBT-DIGEST-005.** `evidence_digest` MUST be deterministic: computing it
twice from the same complete signed attestation document, regardless of the
in-memory key ordering of that document's dictionary representation, MUST
yield an identical digest (canonicalization is order-independent by
construction, MCC-AT-001 AT-SCHEMA-006-equivalent). This is a structural,
testable property.

**EBT-DIGEST-006.** `evidence_digest` MUST be sensitive to mutation of the
complete signed document: a mutation to `claims`, `provenance`, `kid`, `sig`,
or any other signed field MUST produce a different digest than the original.
This is a structural, testable property.

---

# 4. Control Result Extension (EBT-RESULT)

**EBT-RESULT-001.** `ControlAttestationResult` (MCC-AT-002 §4) MUST carry an
additional field, `evidence_digest: Optional[str]`, computed as EBT-DIGEST-001
over the exact raw attestation document `PreExecutionControl` verified,
produced as part of the **same** successful evaluation that already performs
MCC-AT-002 ATC-ORDER-001 steps 1–7 — never a second, independent verification
pass.

**EBT-RESULT-002.** `evidence_digest` MUST be present (non-`None`) if and
only if `reason_code == VERIFIED` (MCC-AT-002's `ok=True` case corresponding
to a required, successfully verified attestation). For `NOT_REQUIRED`
(MCC-AT-002's other `ok=True` case — no `AttestationRequirement` matched the
action), `evidence_digest` MUST be `None`: no attestation was required, so
none is bound. For every `ok=False` reason code, `evidence_digest` MUST be
`None`. A conforming implementation MUST enforce this correspondence
structurally (e.g. reject construction of an inconsistent result), not by
convention alone — mirroring MCC-AT-002 ATC-RESULT-003's treatment of `ok`
and `reason_code`.

**EBT-RESULT-003.** No failure path, no caller-supplied value, and no
partial-verification state may produce a non-`None` `evidence_digest`. A
digest MUST NOT be derivable from, or substitutable by, an unverified,
partially verified, expired, untrusted, mis-bound, or replayed attestation.
This is the direct consequence of EBT-RESULT-001/002 and is independently
structurally enforced (EBT-RESULT-002).

---

# 5. Decision Token Extension (EBT-TOKEN)

**EBT-TOKEN-001.** `DecisionEngine.issue_token()` MUST accept an optional
keyword parameter `evidence_digest: Optional[str] = None`. When non-`None`,
it MUST be included in the token's claim set under the key `evidence_digest`,
in the exact `sha256:<64 lowercase hex>` format (EBT-DIGEST-004), and MUST be
covered by the token's existing Ed25519 signature exactly as every other
claim already is — no separate signature, no second signing key, no
unsigned side-channel field.

**EBT-TOKEN-002.** `evidence_digest` MUST NOT be placed inside the
caller-controlled `auth_claims` dictionary. It MUST be a first-class,
engine-controlled claim, set only from `DecisionEngine.issue_token()`'s own
`evidence_digest` keyword argument — never smuggled in, overridden, or
removed via `auth_claims`. This prevents a caller from forging an evidence
binding by placing an arbitrary value under a similarly-named key in a
dictionary the engine otherwise trusts verbatim. This is a structural,
testable property.

**EBT-TOKEN-003.** For token issuance with no `evidence_digest` argument
(every pre-PR-3 call site, and every PR-3 call for an action with no
configured `AttestationRequirement`, i.e. MCC-AT-002's `NOT_REQUIRED` case),
the `evidence_digest` key MUST be entirely **absent** from the claim set —
not present with a `null`/`None` value. This is a deliberate, minimal
deviation from this token schema's general convention of including
possibly-`None` fields, chosen so that "no evidence binding" (key absent) is
structurally distinguishable from "evidence binding of an empty/null value"
(which this specification does not define and a conforming implementation
MUST NOT produce).

**EBT-TOKEN-004.** No component other than `DecisionEngine.issue_token()`,
invoked from `GovernanceService`'s two governed issuance methods (§7,
EBT-COMPAT-001), may set `evidence_digest` into a token. Any tampering with
an already-issued token's `evidence_digest` claim MUST cause the token's
existing Ed25519 signature verification (`ExecutionGate`'s first check) to
fail, exactly as tampering with any other claim already does — this
specification defines no new tamper-detection mechanism, relying entirely on
the existing whole-token signature.

---

# 6. Execution Gate Enforcement (EBT-GATE)

**EBT-GATE-001.** `ExecutionGate.verify()` / `._verify()` MUST accept an
optional keyword parameter `evidence: Optional[Dict[str, Any]] = None`,
representing the raw evidence artifact presented at actuation time.

**EBT-GATE-002.** Evidence-binding enforcement MUST NOT be folded into the
existing generic `binding` comparison (MCC-Core's pre-existing operation
binding, which tolerates a legacy token simply not carrying a compared
field). Evidence binding is directionally stricter: when the **token**
asserts an `evidence_digest`, presenting a matching evidence artifact becomes
**mandatory**, not merely checked-if-both-present. The two mechanisms MUST
remain structurally distinct in the implementation, even though both execute
before nonce consumption.

**EBT-GATE-003.** The Gate MUST evaluate exactly the following rule, after
every pre-existing static check (signature, key trust, audience, time
window, verdict, policy hash, action hash, payload hash, generic operation
binding) and before nonce consumption (§8):

- **(A)** If the token carries no `evidence_digest` claim (absent, per
  EBT-TOKEN-003): evidence binding introduces **no new requirement**. Legacy
  behavior is preserved exactly, regardless of whether an `evidence` argument
  was supplied. This is the backward-compatibility invariant (§10).
- **(B)** If the token carries an `evidence_digest` claim:
  1. If `evidence` is `None` (not supplied): fail closed with a stable,
     distinguishable reason (reference implementation:
     `EVIDENCE_REQUIRED`). The nonce MUST NOT be consumed.
  2. Otherwise, compute `hash_document(evidence)` using the identical
     trusted primitive Control used to produce the token's
     `evidence_digest` (EBT-DIGEST-001/002 — the same function, not a
     re-implementation). If canonicalization itself fails (the presented
     evidence is not a well-formed document), fail closed with a stable,
     distinguishable reason (reference implementation: `EVIDENCE_INVALID`).
     The nonce MUST NOT be consumed.
  3. If the computed digest does not exactly equal the token's
     `evidence_digest` claim, fail closed with a stable, distinguishable
     reason (reference implementation: `EVIDENCE_DIGEST_MISMATCH`). The
     nonce MUST NOT be consumed. This is the sole enforcement mechanism for
     evidence substitution (a different, independently well-formed and
     independently valid attestation for the same action/payload MUST still
     be rejected, since it is not byte-identical under canonicalization to
     the artifact the token was issued against) and for evidence mutation
     (any change to the presented artifact relative to the one Control
     verified MUST be rejected, for the same reason).
  4. Only if the computed digest exactly equals the token's claim does
     evaluation proceed to nonce consumption.

**EBT-GATE-004.** `ExecutionGate`'s evidence-binding check MUST perform only
a deterministic canonical-document hash comparison. It MUST NOT import,
invoke, or duplicate `mcc_attestation`'s semantic verification (trust
resolution, signature check, evidence-type authorization, claim policy, or
any risk interpretation). It MUST NOT decide whether a claim value (e.g.
`risk_class="low"`) is semantically correct or acceptable — that
determination was made exactly once, by `PreExecutionControl`, before the
token was ever issued (MCC-AT-002 §5). This is a structural, testable
property (`tests/test_evidence_bound_execution_ticket_architecture_guards.py`).

---

# 7. Ordering and Replay Interaction (EBT-ORDER)

**EBT-ORDER-001.** Within `ExecutionGate._verify()`, the evidence-binding
check (§6) MUST execute strictly before the token's nonce is consumed. A
missing, invalid, mismatched, or unparseable evidence artifact MUST NOT
consume the token's nonce. This is a structural, testable property, verified
both by source-order inspection and behaviorally: presenting wrong or
missing evidence against an evidence-bound token MUST fail closed while
leaving the token's nonce unconsumed, such that a subsequent presentation of
the *exact* correct evidence against the *same* token MUST then succeed.

**EBT-ORDER-002.** Within `EnforcementCoordinator.enforce()`, evidence
binding (performed inside `ExecutionGate.verify()`, the coordinator's first
step) MUST occur before any idempotency reservation, velocity reservation,
audit-before-actuation record write, revocation check, approval-mandate
consumption, consensus/challenge re-verification, or external side effect.
Because `enforce()`'s existing a-h ordering already calls `gate.verify()`
first, and the evidence-binding check is internal to that single call and
itself precedes nonce consumption (EBT-ORDER-001), this ordering requirement
holds by construction and requires no additional sequencing logic in the
coordinator.

**EBT-ORDER-003.** This specification defines no new replay-protection
mechanism for evidence artifacts at actuation time. Replay protection for
the *attestation itself* remains exclusively MCC-AT-002 §8's
`PreExecutionControl` nonce consumption, performed once, before issuance.
Presenting the same valid evidence artifact against the same still-valid,
not-yet-actuated token more than once is not "replay" in the MCC-AT-002
sense — it is simply re-checking a comparison that will keep succeeding
until the token's own (pre-existing, unchanged) one-time nonce is consumed
by a successful `ExecutionGate.verify()` call.

---

# 8. Enforcement Coordinator Plumbing (EBT-COORD)

**EBT-COORD-001.** `EnforcementCoordinator.enforce()` MUST accept an optional
keyword parameter `evidence: Optional[Dict[str, Any]] = None` and MUST pass
it through, unmodified, to `ExecutionGate.verify()` as that call's `evidence`
argument.

**EBT-COORD-002.** `EnforcementCoordinator` MUST NOT introduce a second
evidence-binding check anywhere else in its a-h enforcement sequence. Exactly
one boundary (`ExecutionGate`, §6) performs evidence-binding enforcement.

**EBT-COORD-003.** For an evidence-bound successful execution, the durable
`pre_actuation` audit record MUST include the signed token's `evidence_digest`
value. This establishes the auditable chain: signed attestation →
`evidence_digest` → signed execution authority (the token) → `pre_actuation`
audit record → side effect. The audit record MUST NOT copy the complete
attestation document or its semantic `claims` into the append-only chain
unless an existing, independent audit contract specifically requires it — the
digest alone is sufficient to prove which exact artifact gated execution,
without duplicating potentially sensitive claim content into an append-only
log (a concern this specification shares in spirit with the CLAUDE.md
Real-Clinic/PHI compliance gate's "audit stores hash/token/redacted fields,
not raw sensitive payloads" principle, applied here to evidence claims
generally, not only PHI).

---

# 9. Service Wiring (EBT-COMPAT)

**EBT-COMPAT-001.** Every governed runtime issuance path capable of calling
`DecisionEngine.issue_token()` for an action that MAY be governed by an
`AttestationRequirement` MUST propagate the `evidence_digest` produced by the
same `PreExecutionControl.evaluate()` call that gated issuance (MCC-AT-002
ATC-COMPAT-001) into that `issue_token()` call, and MUST propagate the exact
raw evidence artifact down the same governed execution path to
`ExecutionGate` (§6). As of this specification's reference implementation,
this is `GovernanceService.execute_with_mandate` and
`GovernanceService.execute_with_consensus`; `execute_with_approval` continues
to delegate to `execute_with_mandate` (MCC-AT-002 ATC-COMPAT-001) and
inherits evidence binding through that delegation rather than issuing a
token or deriving a digest a third time. This is a structural, testable
property
(`tests/test_evidence_bound_execution_ticket_architecture_guards.py`).

**EBT-COMPAT-002.** `PreExecutionControl.evaluate()` MUST be invoked exactly
once per issuance attempt (MCC-AT-002 unchanged; EBT-MODEL-002). A
conforming implementation MUST NOT invoke attestation verification a second
time merely to obtain `evidence_digest` for the token.

**EBT-COMPAT-003.** No HTTP execute request schema (mandate, approval,
consensus) may carry a caller-supplied `evidence_digest`, or any field by
which a caller could substitute a value for Control's own derivation
(EBT-RESULT-001). The transport-level `attestation` field (MCC-AT-002
ATC-COMPAT-002) remains the only caller-supplied evidence-related input, and
it carries the raw, untrusted attestation document — never a digest, and
never a "verified" assertion (MCC-AT-002 ATC-COMPAT-003, which continues to
apply unchanged). This is a structural, testable property.

**EBT-COMPAT-004.** `GovernanceService.execute_with_mandate` and
`execute_with_consensus`'s public signatures MUST NOT accept an
`evidence_digest` parameter. They accept only `attestation` (the raw
document); `evidence_digest` exists solely as an internal value derived by
`PreExecutionControl` and consumed by `DecisionEngine.issue_token()`. This is
a structural, testable property.

---

# 10. Backward Compatibility (EBT-BC)

**EBT-BC-001.** For any action with no configured `AttestationRequirement`,
or in any deployment with no `PreExecutionControl` configured at all,
behavior MUST be identical, in every observable respect, to behavior before
this specification's reference implementation (PR-3): `evidence_digest` is
never produced, never appears in issued tokens, and `ExecutionGate`'s
evidence-binding check (§6, case A) never activates.

**EBT-BC-002.** Every decision token issued before this specification's
reference implementation, and every token issued after it for an action with
no evidence binding, MUST continue to be accepted by `ExecutionGate` under
exactly its pre-existing verification semantics (signature, audience, time
window, verdict, policy/action/payload hashes, generic operation binding,
nonce consumption) — unmodified by this specification, and unaffected by
whether an `evidence` argument happens to be supplied alongside such a
token.

**EBT-BC-003.** This specification does not globally require
`evidence_digest`, does not change the meaning of `payload_hash`,
`action_hash`, `policy_hash`, `mandate_id`, `auth_claims`, or `nonce`, and
does not alter `MandateAuthority`, `ConsensusVerifier`, the ESCALATE approval
loop, idempotency, velocity limits, revocation, or the consensus challenge
flow.

---

# 11. Known Limitations (Informative)

*(Non-normative. Recorded here so the intermediate state after PR-3 is
documented explicitly, not discovered by omission.)*

- `evidence_digest` proves artifact identity, not semantic correctness. A
  trusted Attester that signed an incorrect assessment, accepted by Control's
  deterministic claim policy, still produces a token that binds correctly to
  that (incorrect) attestation. This is unchanged from MCC-AT-002's
  Abstract framing and is not a defect this specification addresses.
- `ExecutionGate` does not re-check Attester trust or Attester revocation at
  actuation time (MCC-AT-002 §11, unchanged). A trust anchor revoked *after*
  a token was validly issued does not retroactively invalidate that
  already-issued token's evidence binding.
- The evidence artifact travels alongside the token down the existing
  governed execution path as an additional in-process argument
  (`GovernanceService._run` → `EnforcementCoordinator.enforce` →
  `ExecutionGate.verify`). This specification does not define a wire-level
  transport encoding for the evidence artifact between an external caller
  and the gateway process beyond what already carries the `attestation`
  field (MCC-AT-002 ATC-COMPAT-002); that transport is unchanged by PR-3.
- This specification does not define multi-attester threshold evidence
  binding, evidence expiry independent of the attestation's own
  `expires_at`, or any mechanism for binding more than one evidence artifact
  into a single token. A single `evidence_digest` claim identifies exactly
  one complete signed attestation.

---

# 12. Relationship to Existing MCC-Core Artifacts (EBT-REL)

**EBT-REL-001.** This specification does not alter `mcc_core.authority`,
`mcc_core.mandate`, `mcc_core.consensus`, `mcc_core.challenge`,
`mcc_core.nonce`, `mcc_core.idempotency`, `mcc_core.velocity`, or
`mcc_core.audit`'s existing interfaces or semantics.

**EBT-REL-002.** This specification does not alter MCC-AT-001 or MCC-AT-002.
Every MCC-AT-001 and MCC-AT-002 requirement continues to apply unchanged.
`mcc_attestation.verify_attestation()` is invoked exactly as MCC-AT-002
specifies, exactly once, before this specification's `evidence_digest`
derivation — never modified, never re-invoked by `ExecutionGate`.

**EBT-REL-003.** This specification closes MCC-AT-002 §9's explicit
reservation (ATC-BOUNDARY-001/002). `docs/ATTESTATION_CONTROL_INTEGRATION.md`
and `docs/ATTESTATION_ARCHITECTURE.md` are updated to reference this document
for the evidence-binding mechanism they previously described as deferred.

---

# 13. Conformance

**EBT-CONF-001.** An implementation conforms to this specification's PR-3
scope if it satisfies EBT-DOC-001 through EBT-DOC-003, EBT-MODEL-001 through
EBT-MODEL-003, EBT-DIGEST-001 through EBT-DIGEST-006, EBT-RESULT-001 through
EBT-RESULT-003, EBT-TOKEN-001 through EBT-TOKEN-004, EBT-GATE-001 through
EBT-GATE-004, EBT-ORDER-001 through EBT-ORDER-003, EBT-COORD-001 through
EBT-COORD-003, EBT-COMPAT-001 through EBT-COMPAT-004, EBT-BC-001 through
EBT-BC-003, and EBT-REL-001 through EBT-REL-003.

**EBT-CONF-002.** `src/mcc_core/signing.py` (`hash_document`),
`gateway/pre_execution_control.py`, `src/mcc_core/core.py`
(`DecisionEngine.issue_token`), `src/mcc_core/gate.py` (`ExecutionGate`),
`src/mcc_core/coordinator.py` (`EnforcementCoordinator`), and
`gateway/governance_service.py`, together, are the reference implementation
of this Draft specification as of PR-3 (version 0.1 of this document). See
`tests/test_evidence_bound_execution_ticket.py`,
`tests/test_governance_service_attestation.py`, and
`tests/test_evidence_bound_execution_ticket_architecture_guards.py` for the
executable conformance evidence.

---

# 14. Future Work (Informative)

The following are explicitly out of scope for this Draft and for PR-3, and
are noted here only to record intended direction, not as normative
requirements:

- A remote, network-transported Attester service or independent Attester
  protocol.
- Multi-attester threshold evidence binding (more than one signed
  attestation contributing to a single token's authority).
- Certificate-chain-based Attester trust (as opposed to MCC-AT-001's direct
  trust-store model).
- New risk models, a general-purpose claim-policy expression language
  (explicitly excluded already by MCC-AT-002 ATC-REQ-003), or payment- or
  domain-specific evidence fields.
- `ExecutionGate` independently re-checking Attester trust or evidence
  validity windows at actuation time, beyond the exact-digest match this
  specification defines.
- Promotion of this document from Draft to Normative via the repository's
  Final Acceptance Review process.
