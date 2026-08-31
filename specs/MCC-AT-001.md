# MCC-AT-001

# Pre-Execution Attestation Specification

Document ID: MCC-AT-001

Version: 0.2

Status: Draft

Category: Normative Specification (Draft)

Applies To: MCC-Core Pre-Execution Attestation Foundation (PR-1)

Language: English (Normative)

---

# Status of This Specification

This document is a **Draft**. It defines the normative EvidenceAttestation
model, schema, cryptographic integrity, signature, immutability, trust, and
verification requirements implemented by `src/mcc_attestation/` in PR-1. It
has not yet undergone the Final Acceptance Review process used elsewhere in
this repository's Specification Program (see
`docs/MCC_SPECIFICATION_PROGRAM_NORMATIVE_V1_0.md` for that process as
applied to MCC-CP-001/EB-001/CM-001/TC-001) and does not carry Normative
status yet.

Version 0.2 is an architecture-review correction pass over 0.1: it hardens
the temporal invariant (§3), makes immutability a normative, testable
requirement rather than an implementation detail (§4), makes the two
optional binding checks report a distinguishable NOT-CHECKED state instead
of a bare `True` (§7), and adds digest-format and canonical-structure
requirements for the fields that carry them (§3). No requirement from
version 0.1 was weakened; every 0.1 requirement ID that survives unchanged
keeps its number, and new/changed requirements are called out explicitly
below.

The key words MUST, MUST NOT, REQUIRED, SHALL, SHALL NOT, SHOULD, SHOULD NOT,
RECOMMENDED, MAY and OPTIONAL in this specification are to be interpreted as
described in RFC 2119 and RFC 8174.

Reference implementations are informative unless explicitly stated
otherwise.

---

# Abstract

An EvidenceAttestation is a cryptographically attributable, PRE-EXECUTION
assertion about an assessment, bound to a specific proposed action and
scope, valid for a specific window of time, and signed by a specific
Attester.

This specification defines the normative EvidenceAttestation model, its
schema and required content, its immutability requirement, its
cryptographic integrity and signature requirements, its Attester trust
model, its deterministic verification procedure, and its explicit
non-authority boundary.

**An EvidenceAttestation is a pre-execution evidence artifact. It is not,
and SHALL NOT be interpreted as, execution authority or a runtime execution
authorization.** Runtime governance behavior (ALLOW, DENY, ESCALATE,
CONSTRAIN) belongs exclusively to MCC-Core runtime governance
(`mcc_core.gate`, `mcc_core.authority`) and is out of scope for this
specification and for PR-1.

---

# 1. Core Doctrine (AT-DOC)

**AT-DOC-001.** The following formula is the normative doctrine of this
specification and MUST be preserved verbatim in any description of this
system:

```
Intelligence assesses.
Attestation makes the assessment attributable.
Control verifies.
Execution acts.
```

**AT-DOC-002.** A signature over an EvidenceAttestation MUST NOT be
interpreted as evidence that the assessment it attributes is true. A
signature SHALL be interpreted only as proof of attribution and integrity:
who asserted what, about which bound action, under which version/context,
and during which validity interval.

**AT-DOC-003.** An Attester MAY be wrong about the world. This
specification places no requirement on, and makes no claim about, the
correctness of an Attester's semantic judgment.

**AT-DOC-004.** A verifier conforming to this specification MUST NOT
determine whether an attestation's semantic assessment is correct. A
conforming verifier determines only whether the assertion is authentic,
trusted, current, integrity-protected, and correctly bound (§7).

---

# 2. Conceptual Model (AT-MODEL)

**AT-MODEL-001.** Four concepts are structurally distinct under this
specification and MUST NOT be conflated:

- **Assessment** — a probabilistic semantic judgment, produced entirely
  outside the scope of this specification.
- **Attestation** — a signed, attributable assertion *about* an Assessment
  (this specification's subject matter).
- **Authority** — permission derived independently from trusted policy or
  mandates, defined by MCC-Core runtime governance, out of scope here.
- **Execution** — actuation allowed only through the governed execution
  path, defined by MCC-Core runtime governance, out of scope here.

**AT-MODEL-002.** An EvidenceAttestation SHALL NOT itself constitute or
grant Authority, and SHALL NOT itself authorize Execution.

**AT-MODEL-003.** This specification is architecturally distinct from, and
MUST NOT be conflated with, the Governance Evidence Bundle (observational,
post-governance evidence; see `docs/GOVERNANCE_EVIDENCE_BUNDLE.md`) or the
MCC-EB-001 / MCC-CM-001 / MCC-TC-001 certification-program artifacts
(§ MCC-CP-001). Those describe an already-completed governance or
certification outcome. An EvidenceAttestation is supplied *before*
authorization is evaluated.

---

# 3. EvidenceAttestation Schema (AT-SCHEMA)

**AT-SCHEMA-001.** The Attestation Schema Version defined by this
specification is `mcc-attestation/1`.

**AT-SCHEMA-002.** An EvidenceAttestation is a single, structured,
machine-readable JSON document with the closed field set defined in the
table below. A conforming implementation MUST reject any document
containing a field outside this set (AT-VERIFY-003), and MUST reject any
document missing a Required field.

| Field | Required | Type | Description |
|---|---|---|---|
| `schema_version` | REQUIRED | string | MUST equal `"mcc-attestation/1"` for this version of the specification |
| `attestation_id` | REQUIRED | string, non-empty | Unique identifier for this attestation |
| `attester_id` | REQUIRED | string, non-empty | Declared identity of the issuing Attester |
| `evidence_type` | REQUIRED | string, non-empty | Label for the kind of assertion; this specification defines no fixed vocabulary |
| `claims` | REQUIRED | object | Structured, deterministic (canonically serializable — AT-SCHEMA-007) assessment data; semantics are interpreted by policy/Control, never by a conforming verifier |
| `action_hash` | REQUIRED | string, digest (AT-SCHEMA-006) | Binds the attestation to a specific proposed action |
| `payload_hash` | OPTIONAL | string, digest (AT-SCHEMA-006) when present | Binds the attestation to a specific payload |
| `scope` | REQUIRED | string, non-empty | The scope this attestation applies to |
| `policy_hash` | OPTIONAL | string, digest (AT-SCHEMA-006) when present | Deterministic policy binding (content-hash form) |
| `policy_version` | OPTIONAL | string, non-empty | Deterministic policy binding (version-label form; not digest-shaped — AT-SCHEMA-006 does not apply) |
| `provenance` | REQUIRED | object | Free-form structured provenance (e.g. model identity, input reference); canonically serializable (AT-SCHEMA-007) |
| `issued_at` | REQUIRED | integer | Unix seconds; ordering constrained by AT-SCHEMA-004 |
| `not_before` | REQUIRED | integer | Unix seconds; validity window start; ordering constrained by AT-SCHEMA-004 |
| `expires_at` | REQUIRED | integer | Unix seconds; validity window end; ordering constrained by AT-SCHEMA-004 |
| `nonce` | REQUIRED | string, non-empty | Carried for future replay protection (§9) |
| `kid` | REQUIRED | string, non-empty | Signing key identifier |
| `sig` | REQUIRED | string, non-empty | Detached signature over the Canonical Form (§5) |

**AT-SCHEMA-003.** `policy_hash` and `policy_version` are independent,
optional bindings. A conforming implementation MAY populate neither, either,
or both.

**AT-SCHEMA-004.** The following temporal invariant is REQUIRED:

```
issued_at <= not_before < expires_at
```

Both legs MUST be enforced. A document violating either leg is malformed
and MUST be rejected during structural verification (AT-VERIFY-002), not
merely at time-validity checking (AT-VERIFY-008). *(Version 0.2: the
`issued_at <= not_before` leg is new; 0.1 enforced only
`not_before < expires_at`. A conforming implementation MUST enforce this
invariant identically regardless of whether an EvidenceAttestation is
constructed from a serialized document or built directly by an Attester —
see AT-IMMUT-004.)*

**AT-SCHEMA-005.** This specification defines no hard-coded evidence-type
vocabulary (e.g. no built-in notion of `payment`, `fraud`, or `phishing`
semantics) and no hard-coded interpretation of `claims`. A conforming
cryptographic verifier MUST NOT branch on the *content* of `claims` or
`evidence_type` for any purpose other than the evidence-type authorization
check in §8.

**AT-SCHEMA-006.** *(New in version 0.2.)* `action_hash`, and
`payload_hash`/`policy_hash` when present, MUST match the pattern
`sha256:<64 lowercase hex characters>` (the format
`mcc_core.signing.sha256_hex` produces). A document with a digest field
that does not match this pattern is malformed and MUST be rejected during
structural verification. `policy_version` is a free-form label, not a
digest, and is exempt from this requirement.

**AT-SCHEMA-007.** *(New in version 0.2.)* `claims` and `provenance` MUST
contain only values that are canonically serializable: recursively composed
of `null`, `bool`, `str`, finite `int`/`float`, and `object`/`array` with
string-only object keys. A document whose `claims` or `provenance` contains
a value outside this set (e.g. a non-finite float, a non-string object key,
or any value with no canonical JSON representation) is malformed and MUST
be rejected during structural verification, so that a conforming
implementation never signs or accepts a Canonical Form (§5) built from an
ambiguous or non-reproducible serialization.

---

# 4. Immutability (AT-IMMUT)

*(New section in version 0.2. Immutability was described informally in
version 0.1's abstract; it is now a normative, independently testable
requirement.)*

**AT-IMMUT-001.** A constructed EvidenceAttestation instance MUST be
immutable: a conforming implementation MUST NOT provide any supported way
to change a field's value on an already-constructed instance. Attempting to
do so MUST raise an error rather than silently succeeding or silently being
ignored.

**AT-IMMUT-002.** `claims` and `provenance` MUST be immutable on the
constructed instance, independent of the mutability of whatever object the
caller supplied when building the attestation. Specifically: mutating the
caller's original `claims`/`provenance` object *after* the attestation was
constructed MUST have no effect on the constructed attestation's content or
its signature. A conforming implementation satisfies this by deep-copying
into an immutable structure at construction time (e.g. recursively into
read-only mapping/sequence types), not by documentation convention alone.

**AT-IMMUT-003.** Signature verification (§5) MUST NOT be relied upon as a
substitute for AT-IMMUT-001/002. Immutability is a structural property of
the constructed object, independently of whether a caller ever re-serializes
and re-verifies it. (Rationale: an in-process caller holding a live
reference to an attestation object — as opposed to a re-parsed wire
document — never exercises signature verification against its own direct
field/container mutations, so signature verification alone would not catch
a violation of this kind.)

**AT-IMMUT-004.** Every structural invariant this specification defines for
an EvidenceAttestation (AT-SCHEMA-004, AT-SCHEMA-006, AT-SCHEMA-007) MUST be
enforced identically at construction time, regardless of whether the
instance is built from a parsed/untrusted document or constructed directly
by trusted first-party code (e.g. an Attester). A conforming implementation
MUST NOT expose a direct-construction path that bypasses these checks.

**AT-IMMUT-005.** AT-IMMUT-001/002 apply to the constructed
EvidenceAttestation instance's fields. They do not, by themselves, mandate
immutability of the plain, JSON-serializable representation a conforming
implementation returns when serializing an attestation for signing,
transport, or storage (its "Canonical Form" per §5, or an equivalent
serialized document) — ordinary mutable JSON container types are expected
and sufficient there, since that representation is not the object AT-IMMUT
protects.

---

# 5. Canonical Form and Signature (AT-SIG)

**AT-SIG-001.** The signed representation ("Canonical Form") of an
EvidenceAttestation is the deterministic JSON serialization of every field
in AT-SCHEMA-002 except `sig`, with keys sorted and compact separators — the
same canonicalization convention used by every other signed artifact in the
MCC-Core reference implementation (`mcc_core.signing.canonical_bytes`). A
conforming implementation MUST NOT introduce a second, incompatible
canonicalization scheme.

**AT-SIG-002.** The signature algorithm is Ed25519. This specification does
not define, and a conforming implementation MUST NOT accept, a
symmetric-key or shared-secret signature scheme over an EvidenceAttestation.

**AT-SIG-003.** The signature MUST cover every field in the Canonical Form,
including `kid`. Mutating any field covered by the Canonical Form after
issuance MUST invalidate signature verification.

**AT-SIG-004.** A conforming Attester implementation MUST NOT expose,
serialize into an attestation, or log the private signing key. A conforming
implementation MUST NOT allow model-controlled input to substitute a
signing key.

**AT-SIG-005.** A reference (local, in-process) Attester MAY receive an
already-computed assessment as data. It MUST NOT call a language model, and
MUST NOT perform autonomous semantic reasoning about the assessment's
correctness. It only constructs and signs a defined EvidenceAttestation.

---

# 6. Attester Trust Model (AT-TRUST)

**AT-TRUST-001.** A conforming verifier MUST resolve trust by the ordered
pair `(attester_id, kid)`, not by `kid` alone and not by `attester_id`
alone. Trust MUST NOT be inferred from an attestation's self-declared
`attester_id` field without independently confirming, via trust-anchor
resolution, that the resolved anchor's `attester_id` and the declared one
correspond to the same registered anchor.

**AT-TRUST-002.** Each trust anchor MUST declare a closed, non-empty set of
`evidence_type` values the corresponding Attester is permitted to assert.
An Attester with no permitted `evidence_type` set is not a valid trust
anchor.

**AT-TRUST-003.** Verification MUST fail closed (resolve to no trust
anchor) for:

- an unknown `attester_id`;
- an unknown `kid`;
- a `kid` known only under a *different* `attester_id` than the one
  declared in the attestation;
- a revoked trust anchor;
- an `evidence_type` not present in the resolved anchor's permitted set
  (this specific failure is reported as a distinct verification step, §8).

**AT-TRUST-004.** Revoking a trust anchor MUST NOT alter or erase any
previously-issued attestation's content. Revocation affects only future
trust resolution.

**AT-TRUST-005.** This specification does not mandate a specific trust-anchor
persistence, distribution, or rotation technology (analogous to
MCC-TC-001 §12.6/§16 for Revocation Records and Trust Anchors). A minimal
in-memory implementation satisfying AT-TRUST-001 through AT-TRUST-004 is
sufficient to conform for PR-1's scope.

---

# 7. Verification Order (AT-VERIFY)

**AT-VERIFY-001.** Verification of a raw (untrusted) attestation document
MUST proceed in the following fixed order. A conforming verifier MUST NOT
skip a step because a caller already believes an earlier step's outcome.

1. Input/type validation (AT-VERIFY-002)
2. Schema version support (AT-VERIFY-002)
3. Required-field / structural validation (AT-VERIFY-002, AT-VERIFY-003,
   AT-SCHEMA-004, AT-SCHEMA-006, AT-SCHEMA-007)
4. Attester identity (structural — part of step 3)
5. Key lookup / trust resolution (AT-TRUST-001–004)
6. Signature verification (AT-SIG-001–003)
7. `evidence_type` authorization (AT-TRUST-002)
8. Validity window check: `not_before` / `expires_at` against the current
   time (AT-VERIFY-008)
9. `action_hash` binding against the caller's expected action
   (AT-VERIFY-009)
10. Optional `payload_hash` binding, if the caller supplies an expected
    value (AT-VERIFY-009, AT-VERIFY-011)
11. Expected `scope` binding (AT-VERIFY-009)
12. Optional expected `policy_hash` / `policy_version` binding
    (AT-VERIFY-009, AT-VERIFY-011)
13. Success

**AT-VERIFY-002.** Structural verification MUST precede every other check.
A document with an unsupported or missing `schema_version` MUST resolve to
`UNSUPPORTED_SCHEMA` before any other field is validated. A document that is
not a JSON object, is missing a Required field, has a field of the wrong
type, violates AT-SCHEMA-004's timestamp ordering, violates AT-SCHEMA-006's
digest format, or violates AT-SCHEMA-007's canonical-structure requirement
MUST resolve to `INVALID`.

**AT-VERIFY-003.** A document containing a field outside the closed set
defined in AT-SCHEMA-002 MUST be rejected as structurally invalid. This
specifically prevents an attempted authority-grant field (e.g. an injected
`execution_allowed` or `verdict` key) from silently surviving into a
verified attestation (see §10, AT-AUTH-002).

**AT-VERIFY-004.** There is no partial-pass outcome. A single failing step
MUST cause the whole attestation to resolve to `INVALID` (or
`UNSUPPORTED_SCHEMA` for step 2 specifically) — never to a downgraded
"partially verified" status.

**AT-VERIFY-005.** Overall verification status is a closed enumeration:
`VERIFIED`, `INVALID`, `UNSUPPORTED_SCHEMA`. There is no `ALLOW`-shaped or
`AUTHORIZED`-shaped status.

**AT-VERIFY-006.** A conforming verifier MUST return a structured result
reporting, at minimum, the independent dimensions: `schema_supported`,
`structure_valid`, `signer_verified`, `signer_trusted`, `evidence_type_allowed`,
`time_valid`, `action_binding_valid`, `payload_binding_valid`, `scope_valid`,
`policy_binding_valid`, plus `failures` and `warnings`. A bare Boolean return
value does not conform.

**AT-VERIFY-007.** Any unexpected exception during verification MUST be
caught and MUST resolve to `INVALID`. No exception path may produce a
`VERIFIED` result.

**AT-VERIFY-008.** `now < not_before` and `now >= expires_at` MUST both be
treated as failing the validity-window check (the window is inclusive of
`not_before` and exclusive of `expires_at`).

**AT-VERIFY-009.** Binding checks (`action_hash`, `payload_hash`, `scope`,
`policy_hash`/`policy_version`) compare the attestation's declared value
against a value the *caller* supplies as "expected." `action_hash` and
`scope` bindings are always evaluated. `payload_hash`, `policy_hash`, and
`policy_version` bindings are evaluated only when the caller supplies a
corresponding expected value; when the caller supplies none, the check MUST
be reported per AT-VERIFY-011 and MUST NOT itself cause `INVALID`.

**AT-VERIFY-010.** `VERIFIED` means only that the attestation is
cryptographically and structurally valid under the supplied trust and
expected bindings (§10, AT-AUTH-001). It is never a statement that `claims`
is factually or objectively correct.

**AT-VERIFY-011.** *(New in version 0.2, replaces the 0.1 behavior of
reporting an unevaluated optional binding as passed.)* The
`payload_binding_valid` and `policy_binding_valid` fields of the structured
result (AT-VERIFY-006) MUST distinguish three states, not two:

| State | Meaning |
|---|---|
| NOT CHECKED / NOT APPLICABLE | The caller supplied no expected value for that binding (or verification did not reach that step). MUST NOT be represented using the same value a conforming implementation uses for "checked and matched." |
| Checked and matched | The caller supplied an expected value and the attestation's declared value equalled it. |
| Checked and did not match | The caller supplied an expected value and the attestation's declared value did not equal it. The overall result is already `INVALID` in this case (AT-VERIFY-004). |

A conforming implementation satisfies this with an optional/nullable
Boolean (`None`/`null` for NOT CHECKED, distinct from `True`/`False`) or an
equivalent three-valued representation; a plain Boolean field, or any
representation under which NOT CHECKED and "checked and matched" are
indistinguishable to a caller, does not conform. The corresponding entry in
the ordered `checks` list (AT-VERIFY-006) MUST likewise be distinguishable
(e.g. a distinct `NA` status), never reported identically to a passing
check.

---

# 8. Evidence-Type Authorization (AT-TYPE)

**AT-TYPE-001.** An attestation whose `evidence_type` is not in the
resolved trust anchor's permitted set MUST resolve to `INVALID`, reported
distinctly from a trust-resolution or signature failure (see the
`evidence_type_authorization` check, AT-VERIFY-006).

---

# 9. Replay (Deferred)

**AT-REPLAY-001.** This specification requires `nonce` to be present and
structurally valid (a non-empty string) on every EvidenceAttestation. It
does **not** require, and PR-1's reference verifier does **not** perform,
nonce consumption against a replay registry.

**AT-REPLAY-002.** Replay enforcement (exactly-once consumption of
`nonce`) is intentionally deferred to a future Control/runtime integration.
A conforming PR-1-scope verifier is not non-conformant for omitting replay
consumption. A future revision of this specification (or a companion
Control-integration specification) SHALL define the replay-registry
requirements when that integration lands.

**AT-REPLAY-003.** A conforming implementation MUST NOT introduce a second,
independent nonce registry that duplicates or competes with
`mcc_core.nonce`'s existing replay-protection registry when replay
enforcement is eventually added.

---

# 10. Non-Authority Boundary (AT-AUTH)

**AT-AUTH-001.** `VERIFIED` status SHALL NOT be interpreted, represented,
or documented as: "the risk is low," "the action is authorized," "the model
is correct," or any equivalent authority-granting statement. It SHALL be
interpreted only as: "this assertion is authentic, trusted, current,
integrity-protected, and correctly bound." A NOT-CHECKED optional binding
(AT-VERIFY-011) SHALL NOT be interpreted or represented as "proven."

**AT-AUTH-002.** The EvidenceAttestation schema (§3) and the
`AttestationVerificationResult` structure (§7) MUST NOT contain a field
whose name or semantics constitute an execution verdict or authority grant
(e.g. `verdict`, `decision`, `allow`, `deny`, `escalate`, `constrain`,
`authority`, `authorized`, `token_issued`, `execution_allowed`). This is a
structural, testable requirement (see
`tests/test_mcc_attestation.py::test_23*`).

**AT-AUTH-003.** Interpreting a `VERIFIED` EvidenceAttestation into an
authorization decision is exclusively a Control-layer responsibility,
architecturally and temporally outside this specification and outside
PR-1's implementation scope.

---

# 11. Relationship to Existing MCC-Core Artifacts (AT-REL)

**AT-REL-001.** This specification does not alter, and PR-1's
implementation does not modify, `src/mcc_core/gate.py`,
`src/mcc_core/authority.py`, existing decision-token issuance, the Gateway
API, or existing nonce/replay behavior.

**AT-REL-002.** `mcc_evidence` (the Governance Evidence Bundle and related
MCC-EB-001/CM-001/TC-001 certification-program artifacts) remains
observational and post-governance, as defined in its own specifications and
`docs/GOVERNANCE_EVIDENCE_BUNDLE.md`. This specification does not alter
`mcc_evidence`'s semantics, and a conforming `mcc_attestation` implementation
does not depend on `mcc_evidence` as an authority source (see
`tests/test_mcc_attestation_architecture_guards.py`).

**AT-REL-003.** Reuse of `mcc_core.signing` (Ed25519, canonical
serialization) by this specification's reference implementation is
intentional and MUST NOT be read as coupling this specification's authority
boundary to `mcc_core`'s runtime governance layer — `mcc_core.signing` is a
pure, stateless cryptographic primitive with no gate, authority, or executor
semantics of its own.

---

# 12. Conformance

**AT-CONF-001.** An implementation conforms to this specification's PR-1
scope if it satisfies AT-SCHEMA-001 through AT-SCHEMA-007, AT-IMMUT-001
through AT-IMMUT-005, AT-SIG-001 through AT-SIG-005, AT-TRUST-001 through
AT-TRUST-005, AT-VERIFY-001 through AT-VERIFY-011, AT-TYPE-001,
AT-REPLAY-001 through AT-REPLAY-003, AT-AUTH-001 through AT-AUTH-003, and
AT-REL-001 through AT-REL-003.

**AT-CONF-002.** `src/mcc_attestation/` is the reference implementation of
this Draft specification as of PR-1 (version 0.2 of this document). See
`docs/ATTESTATION_ARCHITECTURE.md` for an informative architectural
narrative and `tests/test_mcc_attestation.py` /
`tests/test_mcc_attestation_architecture_guards.py` for the executable
conformance evidence.

---

# 13. Future Work (Informative)

The following are explicitly out of scope for this Draft and for PR-1, and
are noted here only to record intended direction, not as normative
requirements:

- Binding a `VERIFIED` attestation into decision-token issuance or the
  Execution Gate's evaluation path (PR-2/PR-3).
- Nonce/replay consumption against a registry (§9).
- A distributed or persistent Attester Trust Store backend.
- A remote Attester network service, queue, or background worker.
- Promotion of this document from Draft to Normative via the repository's
  Final Acceptance Review process.
