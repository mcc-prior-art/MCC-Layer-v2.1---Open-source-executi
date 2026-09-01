# MCC-AT-004

# Independent Attester Service Boundary Specification

Document ID: MCC-AT-004

Version: 0.1

Status: Draft

Category: Normative Specification (Draft)

Applies To: MCC-Core Independent Attester Service Boundary (PR-4)

Language: English (Normative)

---

# Status of This Specification

This document is a **Draft**. It defines the normative trust-boundary and
service contract for the Independent Attester Service, implemented by
`src/mcc_attester_service/` in PR-4. It has not undergone the Final
Acceptance Review process used elsewhere in this repository's Specification
Program (see `docs/MCC_SPECIFICATION_PROGRAM_NORMATIVE_V1_0.md`) and does not
carry Normative status.

This specification does not amend, weaken, or restate MCC-AT-001, MCC-AT-002,
or MCC-AT-003. MCC-AT-001 governs the `EvidenceAttestation` artifact itself.
MCC-AT-002 governs whether Control requires and verifies an attestation
before token issuance. MCC-AT-003 governs the cryptographic binding of a
verified attestation into the signed decision token and its enforcement at
`ExecutionGate`. This document governs a distinct, earlier-in-time concern:
**where and how the signed `EvidenceAttestation` document is produced in the
first place**, and specifically, the trust boundary between whatever proposes
an action (an intelligence/agent) and the process that is cryptographically
attributed as having attested to it. Where the two overlap (the
`EvidenceAttestation` schema, its verification order), this document
cross-references MCC-AT-001 by requirement ID rather than duplicating it.

The key words MUST, MUST NOT, REQUIRED, SHALL, SHALL NOT, SHOULD, SHOULD NOT,
RECOMMENDED, MAY and OPTIONAL in this specification are to be interpreted as
described in RFC 2119 and RFC 8174.

Reference implementations are informative unless explicitly stated
otherwise.

---

# Abstract

MCC-AT-001 through MCC-AT-003 built a complete, verifiable, cryptographically
bound evidence chain — but left one question unanswered: **who runs the code
that signs an `EvidenceAttestation`, and where does its private key live?**
Until this specification, the reference `LocalAttester` (MCC-AT-001) was
simply instantiated wherever a caller happened to hold a `SigningKey` — which,
in an unconstrained deployment, could be the very same process (and the very
same trust domain) as the model or agent whose action is being assessed. If
that process also holds the Attester's private key, the "attribution"
guarantee MCC-AT-001's signature is supposed to provide is empty: the party
being assessed could sign its own assessment.

This specification closes that gap by defining the **Independent Attester
Service**: a separately runnable process, in its own trust domain, that owns
the Attester's Ed25519 private signing key and exposes exactly one
capability — producing a signed `EvidenceAttestation` for a described
operation, from a configured, non-caller-controlled assessment source. The
model/agent proposing the action can reach this service only as an
authenticated HTTP client; it can describe *what* to assess, never dictate
*what the Attester asserts*.

Core doctrine, unchanged from MCC-AT-001 through MCC-AT-003 and preserved
verbatim:

```
Intelligence assesses.
Attestation makes the assessment attributable.
Control verifies.
Execution acts.
```

**The signature does not make the assessment true.** Nothing in this
specification changes what an Ed25519 signature over an `EvidenceAttestation`
proves: attribution and integrity, never semantic correctness. Isolating the
private key from the model/agent closes a *different* gap — it makes the
attribution the signature provides meaningful, by ensuring the party
attesting and the party proposing cannot be made to collude.

**Attestation does not grant execution authority.** This specification
introduces no new authority mechanism. The Independent Attester Service never
issues MCC decision tokens, mandates, approvals, or consensus authority, and
never calls `ExecutionGate` or `EnforcementCoordinator`. Its output is
evidence, consumed exactly as MCC-AT-002 already consumes it — independently
verified, and never sufficient on its own to authorize execution.

---

# 1. Trust-Boundary Purpose and Threat Model (AIS-THREAT)

**AIS-THREAT-001.** The threat this specification defends against: **a model
or agent that can influence, or fully control, both the proposal of an action
and the attestation of that action's evidence.** If the same trust domain
controls both, a signed `EvidenceAttestation` records only that the domain
signed something about itself — it carries no independent attribution, no
matter how cryptographically well-formed the signature is (MCC-AT-001's
"signature does not make the assessment true" already establishes the
semantic half of this; this specification establishes the *structural* half:
who is even permitted to produce the signature).

**AIS-THREAT-002.** Concretely, an implementation MUST prevent:

- a model/agent process directly holding the Attester's Ed25519 private key;
- a model/agent process directly instantiating `LocalAttester` with that key
  in-process;
- a model/agent process choosing, overriding, or influencing the trusted
  claims (`evidence_type`, `claims`, `provenance`) an Attester signs, beyond
  describing the operation to be assessed;
- a caller submitting a pre-computed `action_hash`/`payload_hash`/`scope`/
  `nonce`/timestamps/`evidence_digest`/`verified` flag as a substitute for the
  Attester service's own derivation of those values.

**AIS-THREAT-003.** Out of scope for this threat model (see §12, Known
Limitations): compromise of the Attester process itself (if an attacker
gains code execution inside the Attester service, this specification's
isolation guarantee no longer holds — that is a deployment/operational
security concern, not something a request-level trust boundary can prevent);
network-layer confidentiality/integrity (TLS termination, mTLS) is a
deployment concern this specification does not mandate a specific mechanism
for.

---

# 2. Conceptual Model (AIS-MODEL)

**AIS-MODEL-001.** This specification's target architecture:

```
INTELLIGENCE / AGENT
        |
        |  proposal / assessment input (action, resource, payload)
        v
INDEPENDENT ATTESTER SERVICE            <-- THIS SPECIFICATION
        |  AssessmentProvider supplies evidence_type/claims/provenance
        |  the SERVICE derives action_hash/payload_hash/scope itself
        |  the SERVICE generates attestation_id/nonce/validity window itself
        |  the SERVICE signs via mcc_attestation.attester.LocalAttester
        |      (PR-1, unmodified -- no second signing implementation)
        v
raw signed EvidenceAttestation (crosses the process boundary as JSON data)
        |
        v
PRE-EXECUTION CONTROL                   (MCC-AT-002, unmodified)
        |  verifies independently; never trusts the service's HTTP 200
        |  as "already verified"
        v
evidence_digest -> SIGNED DECISION TOKEN -> EXECUTION GATE   (MCC-AT-003, unmodified)
        |
        v
EXECUTION
```

**AIS-MODEL-002.** The Independent Attester Service and `PreExecutionControl`
MUST remain distinct components, in distinct processes, communicating only
through the raw, untrusted-until-verified signed `EvidenceAttestation`
document. A conforming implementation MUST NOT collapse the two into one
object or one process, and MUST NOT let the Attester service's own success
response (e.g. an HTTP 200) be interpreted anywhere in `GovernanceService` or
`PreExecutionControl` as "already verified" (see MCC-AT-002 ATC-VERIFY-001,
unchanged and still fully in force: Control invokes
`mcc_attestation.verify_attestation()` itself, on the raw document, every
time).

**AIS-MODEL-003.** This specification is a deployment/trust-boundary
extension, not a replacement protocol. A conforming implementation MUST reuse
the existing MCC-AT-001 `EvidenceAttestation` schema, canonicalization,
Ed25519 signing semantics (`mcc_core.signing`), and verification contract
unchanged. It MUST NOT introduce a second attestation format, a second
signing algorithm, or a second canonicalization scheme.

---

# 3. Service / Request / Response Contract (AIS-CONTRACT)

**AIS-CONTRACT-001.** The Independent Attester Service MUST expose, at
minimum, one authenticated endpoint that accepts a description of an
operation to assess and returns either a complete signed
`EvidenceAttestation` (as its `to_dict()` form) or a fail-closed rejection —
never a partial or unsigned artifact as a success response (§8).

**AIS-CONTRACT-002.** The request schema MUST be strict (unknown fields
rejected) and MUST contain only a description of the operation: at minimum an
`action` identifier, an optional `resource` identifier, and an optional
structured `payload`. The reference implementation's `AttestRequest`
(`src/mcc_attester_service/app.py`) satisfies this with exactly three fields.

**AIS-CONTRACT-003.** The response, on success, MUST be the complete signed
`EvidenceAttestation` document (`schema_version`, `attestation_id`,
`attester_id`, `evidence_type`, `claims`, `action_hash`, `scope`,
`provenance`, `issued_at`, `not_before`, `expires_at`, `nonce`,
`payload_hash` when applicable, `policy_hash`/`policy_version` when
configured, `kid`, `sig`) — the same closed field set MCC-AT-001
(`_ALL_ALLOWED_FIELDS`) already defines. This specification adds no field to
that schema and removes none.

---

# 4. Private-Key Isolation (AIS-KEY)

**AIS-KEY-001.** The Attester's Ed25519 PRIVATE signing key MUST be loaded,
held, and used exclusively within the Independent Attester Service process
boundary. A conforming implementation MUST NOT require, load, import, or make
available that private key material in: the governed MCC gateway/runtime
(`gateway/*`), `src/mcc_core/*`, `ExecutionGate`, `EnforcementCoordinator`, or
the governed execution process generally. This is a structural, testable
property (`tests/test_attester_service_architecture_guards.py`).

**AIS-KEY-002.** The governed MCC gateway/runtime MUST require only the
Attester's PUBLIC key, through the existing trust-store mechanisms
(`mcc_attestation.trust.AttesterTrustAnchor`/`AttesterTrustStore`, loaded by
`gateway.governance_api._build_pre_execution_control` from
`MCC_ATTESTATION_TRUST_CONFIG`). This mechanism already accepted only
`public_key_b64` before PR-4 (MCC-AT-002's reference implementation); PR-4
introduces no change to it — the Independent Attester Service is simply a new
kind of *producer* of the attestations that trust configuration verifies.

**AIS-KEY-003.** The service-to-service authentication secret (§7) MUST be a
value entirely distinct from the Attester's private signing key. Compromising
one MUST NOT compromise the other. A conforming implementation MUST refuse
to start if the two are configured to the same value or if the auth secret
falls below a minimum length floor (reference implementation: 16 characters;
see `config.MIN_AUTH_SECRET_LENGTH`).

**AIS-KEY-004.** The service MUST NOT silently generate a signing key when
none is configured. Missing or malformed key configuration MUST cause the
service to refuse to start (§8), never to fall back to an ephemeral or
default key.

---

# 5. AssessmentProvider Responsibility (AIS-PROVIDER)

**AIS-PROVIDER-001.** The component that supplies the Attester's assessment
content (`evidence_type`, `claims`, `provenance`) MUST be a narrow, explicit
interface (`AssessmentProvider`) distinct from the Attester service's own
cryptographic/binding/identity responsibilities. A conforming implementation
MUST NOT let the provider set, override, or influence `attester_id`, `kid`,
`attestation_id`, `nonce`, the validity window, or the action/payload/scope
binding — those remain the Attester service's own responsibility (§6, §7 of
MCC-AT-001's analogous separation, applied here one layer earlier).

**AIS-PROVIDER-002.** This specification does not integrate, and a
conforming PR-4 implementation MUST NOT ship as a production default, an LLM,
an ML risk engine, a payment-specific model, or a general policy language. A
deterministic, explicitly test-only reference provider MAY be shipped
(reference implementation: `DeterministicTestProvider`), but it MUST document
itself as non-production and MUST fail closed (raise) for any action it has
no configured entry for — it MUST NOT fabricate an "always low risk" or any
other default assessment.

**AIS-PROVIDER-003.** The Attester service MUST treat any exception raised
by the configured `AssessmentProvider` — of any type — as a fail-closed
provider failure (§8), and MUST validate that the provider's return value is
a well-formed assessment result before using it. A provider that is
unavailable, raises, times out, or returns malformed content MUST NOT result
in a signed artifact.

---

# 6. Caller-Controlled vs. Attester-Controlled Fields (AIS-FIELDS)

**AIS-FIELDS-001.** A caller of the Independent Attester Service MAY supply
only a description of the operation to be assessed: `action`, `resource`,
`payload` (AIS-CONTRACT-002). A caller MUST NOT be able to supply, override,
or influence any of the following, which are exclusively Attester-controlled:

`sig`, `kid`, `attester_id`, `attestation_id`, `nonce`, `issued_at`,
`not_before`, `expires_at`, `action_hash`, `payload_hash`, `evidence_digest`,
any `verified`/verification-result field, trusted provenance metadata,
`evidence_type`, `claims`.

**AIS-FIELDS-002.** The request schema MUST enforce AIS-FIELDS-001
structurally — rejecting unknown/unmodeled fields outright (`extra="forbid"`
or equivalent), not merely by omitting these fields from documentation. This
is a structural, testable property (`tests/test_attester_service.py`'s
per-field bypass-rejection parametrization).

**AIS-FIELDS-003.** `evidence_type`, `claims`, and `provenance` in the signed
artifact MUST originate solely from the configured `AssessmentProvider`'s
returned result (§5) — never from any caller-supplied field, since no such
field exists on the request schema at all (AIS-FIELDS-001/002 make this true
by construction, not merely by convention).

---

# 7. Caller-Authentication Boundary (AIS-AUTH)

**AIS-AUTH-001.** The Independent Attester Service MUST NOT be an
unauthenticated public signing oracle. It MUST implement a
service-to-service authentication boundary, and authentication failure MUST
occur, and MUST be enforced, strictly before any assessment or signing is
attempted (§8's ordering).

**AIS-AUTH-002.** The reference implementation's authentication mechanism is
a static shared secret, compared via a constant-time comparison
(`secrets.compare_digest`), presented as a request header
(`X-Attester-Auth`). This mirrors the existing `X-API-Key`/`X-Operator-Key`
convention `gateway.governance_api._auth_deps` already establishes for the
governed gateway's own HTTP boundary, applied here to a second, independent
service.

**AIS-AUTH-003.** What this authentication mechanism PROVES: that the caller
possesses the configured shared secret. What it does NOT prove, and a
conforming implementation MUST NOT claim it proves: the caller's individual
identity beyond that (every holder of the secret is indistinguishable to this
check); that the request's *content* is trustworthy beyond what the strict
schema (§6) already constrains; anything about network-layer transport
security. TLS/mTLS termination, if used, is a deployment concern layered
underneath this boundary, not a replacement for it, and is out of scope for
this specification (§13).

**AIS-AUTH-004.** This specification does not define, and a conforming
implementation MUST NOT introduce, a general-purpose identity platform,
OAuth/OIDC integration, or certificate-based mutual authentication as a
REQUIREMENT — the smallest deterministic boundary appropriate to close
AIS-AUTH-001 is sufficient; a deployment MAY layer a stronger mechanism
underneath or in front of it without contradicting this specification.

---

# 8. Fail-Closed Behavior (AIS-FAIL-CLOSED)

**AIS-FAIL-CLOSED-001.** The Independent Attester Service MUST return no
signed attestation — not a partial one, not an unsigned one, not one carrying
a placeholder or default value — if any of the following holds:

1. caller authentication fails;
2. the request schema is invalid;
3. the configured `AssessmentProvider` is unavailable, raises, or returns a
   malformed result;
4. the action/payload/scope binding cannot be derived;
5. the service's own configuration (signing key, validity window, scope
   template, policy binding) is invalid;
6. the signing key is unavailable or malformed;
7. signing itself fails for any other reason.

**AIS-FAIL-CLOSED-002.** Authentication (item 1) MUST be checked before
assessment or signing is attempted (AIS-AUTH-001). Configuration validity
(item 5) and signing-key validity (item 6) MUST be checked at service
start-up wherever structurally possible, so that a misconfigured service
never reaches a state where it could attempt to sign at all — refusing to
start is preferred over failing per-request for a condition that is already
known at start-up.

**AIS-FAIL-CLOSED-003.** A conforming implementation MUST NOT collapse
distinct failure reasons into a response shape indistinguishable from
success, and MUST NOT include any attestation-shaped fields (e.g. `sig`,
`kid`, `claims`) in a failure response.

---

# 9. Action/Payload/Scope/Policy Binding Ownership (AIS-BINDING)

**AIS-BINDING-001.** The Attester service MUST derive `action_hash` and, when
applicable, `payload_hash` itself, from the actual submitted `action` and
`payload`, using the SAME canonical hashing primitives
`gateway.pre_execution_control` and `mcc_core.core.DecisionEngine` already
use (`mcc_core.signing.hash_action`/`hash_payload`) — never a caller-supplied
hash (which the schema does not accept in the first place, AIS-FIELDS-001).

**AIS-BINDING-002.** `scope` MUST be derived by the service from a trusted,
server-side scope template (the SAME `str.format(action=..., resource=...)`
convention `gateway.pre_execution_control.AttestationRequirement.
resolve_scope` already uses) combined with the caller-supplied `resource`
identifier — the caller supplies which resource the operation concerns, never
the resulting scope string itself, and never the template.

**AIS-BINDING-003.** When the Attester service is configured with a trusted
`policy_hash`/`policy_version` (matching what `PreExecutionControl` expects
to bind against for a given deployment), it MUST include them in the signed
artifact from that trusted server-side configuration, never from a caller
field (none exists on the request schema).

---

# 10. Nonce and Validity-Window Ownership (AIS-NONCE)

**AIS-NONCE-001.** The Attester service MUST generate `attestation_id` and
`nonce` itself, using cryptographically appropriate randomness consistent
with existing repository convention (`secrets.token_urlsafe`, the same
primitive `mcc_core.challenge` already uses for its own nonce generation) —
never accept either from the caller (AIS-FIELDS-001).

**AIS-NONCE-002.** `issued_at`, `not_before`, and `expires_at` MUST be
generated by the service itself from its own clock and a trusted,
deterministically configured validity duration, bounded to a sane range
(reference implementation: `[MIN_VALIDITY_SECONDS, MAX_VALIDITY_SECONDS]` =
`[1, 3600]`). A conforming implementation MUST NOT accept a caller-supplied
validity window.

**AIS-NONCE-003.** This specification does not alter MCC-AT-002's replay
protection (`PreExecutionControl` consuming the attestation's `nonce` against
`mcc_core.nonce`, domain-separated by key). The Independent Attester Service
generates a fresh, unpredictable nonce per issued attestation; it does not
itself track or consume nonces — that remains exclusively
`PreExecutionControl`'s responsibility, unchanged.

---

# 11. Relationship to MCC-AT-001 / 002 / 003 (AIS-REL)

**AIS-REL-001.** This specification does not alter `src/mcc_attestation/*`.
`mcc_attestation.attester.LocalAttester` and
`mcc_attestation.verifier.verify_attestation` are reused unmodified — the
Attester service is a new, isolated CALLER of `LocalAttester`, not a
replacement for it.

**AIS-REL-002.** This specification does not alter
`gateway/pre_execution_control.py`'s decision logic (MCC-AT-002) or
`src/mcc_core/gate.py`'s evidence-binding enforcement (MCC-AT-003). Every
requirement in MCC-AT-002 (§5's required evaluation order, the exact-payload
rule, replay protection) and MCC-AT-003 (the digest algorithm, the token
claim, the Gate's enforcement order, fail-closed missing/mismatch semantics)
continues to apply unchanged to an artifact produced by the Independent
Attester Service, exactly as it applies to any other `EvidenceAttestation`.
`PreExecutionControl` cannot distinguish, and MUST NOT be made to
distinguish, an artifact's *origin* (in-process `LocalAttester` call vs. the
Independent Attester Service) — only its cryptographic and structural
validity.

**AIS-REL-003.** This specification closes the informal deployment gap
`docs/ATTESTATION_ARCHITECTURE.md` and `docs/ATTESTATION_CONTROL_INTEGRATION.md`
previously described as a future extension: a remote/independent Attester
process is no longer merely anticipated, it has a reference implementation.

---

# 12. Known Limitations (Informative)

*(Non-normative. Recorded here so the state after PR-4 is documented
explicitly, not discovered by omission.)*

- **Attester process compromise is out of scope.** If an attacker gains code
  execution inside the Attester service itself, this specification's
  isolation guarantee (§1, AIS-THREAT) no longer holds. Process isolation
  defends against a model/agent that does not control the Attester process,
  not against an Attester process that has itself been compromised.
- **No multi-attester threshold scheme.** A single Attester service instance
  signs alone; there is no N-of-M independent-Attester quorum analogous to
  `mcc_core.consensus`'s evaluator quorum. This is explicitly out of scope
  for PR-4 (see the task's Architectural Non-Goals) and may be a legitimate
  future extension.
- **No certificate-chain/PKI hierarchy.** Trust is a flat, directly
  configured `(attester_id, kid) -> public key` mapping (MCC-AT-001's
  existing model), not a certificate chain rooted in a CA.
- **No HSM/KMS integration.** The reference implementation loads the private
  key from a PEM file (`SigningKey.from_pem_file`, the existing repository
  convention). Hardware-backed or remote key custody is a legitimate future
  extension, not implemented here.
- **No Attester revocation re-check at actuation time.** Unchanged from
  MCC-AT-002/003: `ExecutionGate` does not re-verify Attester trust or
  revocation at actuation time; a trust anchor revoked after a token was
  validly issued does not retroactively invalidate that token.
- **Authentication proves possession of a shared secret, not deep identity.**
  See AIS-AUTH-003. A deployment requiring stronger caller identity
  (mTLS client certificates, per-caller credentials) MAY layer that on top;
  this specification does not mandate it.
- **The reference `python -m mcc_attester_service` entrypoint wires the
  DETERMINISTIC TEST PROVIDER only.** It exists to make the process-isolation
  claim concretely testable and runnable, not as a production deployment
  artifact. A real deployment supplies its own `AssessmentProvider` and,
  typically, its own process entrypoint.

---

# 13. Conformance

**AIS-CONF-001.** An implementation conforms to this specification's PR-4
scope if it satisfies AIS-THREAT-001 through AIS-THREAT-003, AIS-MODEL-001
through AIS-MODEL-003, AIS-CONTRACT-001 through AIS-CONTRACT-003, AIS-KEY-001
through AIS-KEY-004, AIS-PROVIDER-001 through AIS-PROVIDER-003, AIS-FIELDS-001
through AIS-FIELDS-003, AIS-AUTH-001 through AIS-AUTH-004,
AIS-FAIL-CLOSED-001 through AIS-FAIL-CLOSED-003, AIS-BINDING-001 through
AIS-BINDING-003, AIS-NONCE-001 through AIS-NONCE-003, and AIS-REL-001 through
AIS-REL-003.

**AIS-CONF-002.** `src/mcc_attester_service/` (`provider.py`, `config.py`,
`service.py`, `app.py`, `__main__.py`) is the reference implementation of
this Draft specification as of PR-4 (version 0.1 of this document). See
`tests/test_attester_service.py`, `tests/test_attester_service_e2e.py`,
`tests/test_attester_service_architecture_guards.py`, and
`tests/test_attester_service_process_isolation.py` for the executable
conformance evidence, including the required cross-process proof.

---

# 14. Future Work (Informative)

The following are explicitly out of scope for this Draft and for PR-4, and
are noted here only to record intended direction, not as normative
requirements:

- Multi-attester threshold schemes (N-of-M independent Attester processes).
- Certificate-chain / PKI-based Attester trust.
- Remote HSM/KMS-backed key custody for the Attester's signing key.
- A real (non-test, non-deterministic) `AssessmentProvider` implementation —
  an ML risk model, an LLM-based assessor, a human-review-backed provider, or
  any payment-specific logic.
- A generalized claim-policy DSL (explicitly excluded already by MCC-AT-002
  ATC-REQ-003, and unaffected by this specification).
- Attester revocation re-check at actuation time.
- A production cloud deployment topology (this specification defines the
  service's own boundary and contract, not its hosting environment).
- Promotion of this document from Draft to Normative via the repository's
  Final Acceptance Review process.
