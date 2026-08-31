# MCC Attestation — Architecture (PR-1: Pre-Execution Attestation Foundation)

**Status:** Foundation only. This document describes `src/mcc_attestation/`
as it exists after PR-1 — a standalone, independent package. It does **not**
integrate into MCC-Control, `AuthorityModel`, decision-token issuance,
`ExecutionGate`, or the Gateway API. Runtime integration is explicitly
deferred to PR-2 and PR-3.

## 1. Target architecture

```
INTELLIGENCE → ATTESTER → CONTROL → EXECUTION
```

PR-1 implements only the **ATTESTER** boundary: a versioned
`EvidenceAttestation` contract, deterministic canonical representation,
Ed25519 signing, an attester trust model, and deterministic verification.

## 2. Core doctrine

Preserve this wording verbatim wherever this package is described:

```
Intelligence assesses.
Attestation makes the assessment attributable.
Control verifies.
Execution acts.
```

**A signature does NOT make an assessment true.** A signature proves
attribution and integrity: who asserted what, about which bound action,
under which version/context, and during which validity interval. **The
Attester may be wrong about the world.**

The verifier in this package **MUST NOT** determine whether the semantic
assessment is correct. It determines whether the assertion is:

- authentic
- trusted
- current
- integrity-protected
- correctly bound

The goal is not to remove probability from AI. It is to remove probability
from the final authorization boundary — and PR-1 does not itself sit at that
boundary yet (that is PR-2/PR-3's job); it builds the primitive that later
work will use there.

## 3. Four concepts, kept structurally distinct

| Concept | Meaning | Where it lives |
|---|---|---|
| **Assessment** | Probabilistic semantic judgment (e.g. "this looks like a low-risk refund") | Outside this package entirely — produced by whatever model, rule engine, or human review process the deployment uses |
| **Attestation** | A signed, attributable assertion *about* that assessment | `mcc_attestation` (this package) |
| **Authority** | Permission derived independently from trusted policy / mandates | `mcc_core.authority`, `mcc_core.mandate` — **unchanged by this PR** |
| **Execution** | Actuation allowed only through the governed execution path | `mcc_core.gate`, `gateway/` — **unchanged by this PR** |

An attestation being `VERIFIED` is a statement about the first pair
(Assessment → Attestation): it establishes attribution and integrity. It
says nothing about, and does not itself grant, the second pair (Authority →
Execution). **An `EvidenceAttestation` does not itself grant execution
authority.**

## 4. Why this is not `mcc_evidence`

`mcc_evidence` (existing) is **observational** governance/assurance
evidence: it describes an already-completed governance path (a decision was
made, the gate enforced it, an outcome occurred) and carries no execution
authority. It looks **backward** in time.

`mcc_attestation` (new, this PR) is **pre-execution** evidence: a
cryptographically attributable assertion supplied to Control **before**
authorization is evaluated. It looks **forward** in time.

|  | `mcc_evidence` | `mcc_attestation` |
|---|---|---|
| Temporal relationship to a decision | After (describes what happened) | Before (feeds what may happen) |
| Carries execution authority | No | No |
| Is an authority source for the other | — | No — this package does not import `mcc_evidence`, and `mcc_evidence` is not treated as authoritative input to attestation verification |
| Signing primitive | `mcc_core.signing` (Ed25519) | `mcc_core.signing` (Ed25519) — same primitive, reused, not duplicated |

These concepts must remain separate. This package does not repurpose or
redefine `mcc_evidence`, and does not import it (see
`tests/test_mcc_attestation_architecture_guards.py`, which enforces this
statically).

## 5. EvidenceAttestation contract (schema `mcc-attestation/1`)

A closed, versioned field set (see `src/mcc_attestation/schema.py`):

| Field | Required | Type | Meaning |
|---|---|---|---|
| `schema_version` | yes | string | `"mcc-attestation/1"` |
| `attestation_id` | yes | string | Unique identifier for this attestation |
| `attester_id` | yes | string | Declared identity of the issuing Attester |
| `evidence_type` | yes | string | Free-form label for the kind of assertion (e.g. `"risk_assessment"`) — no hard-coded vocabulary |
| `claims` | yes | object | Structured, deterministic (canonically serializable) assessment data — semantics interpreted by policy/Control, never by this package |
| `action_hash` | yes | string | Binds this attestation to a specific proposed action — MUST match `sha256:<64 lowercase hex characters>` |
| `payload_hash` | no | string | Optional binding to a specific payload — MUST match `sha256:<64 lowercase hex characters>` when present |
| `scope` | yes | string | The scope this attestation applies to (e.g. `"payment:vendor_invoice"`) |
| `policy_hash` | no | string | Optional deterministic policy binding (content-digest form) — MUST match `sha256:<64 lowercase hex characters>` when present |
| `policy_version` | no | string | Optional deterministic policy binding (free-form version label — not a digest, no format constraint) |
| `provenance` | yes | object | Free-form structured provenance (e.g. `{"model": "...", "input_ref": "..."}`) |
| `issued_at` | yes | integer | Unix seconds — MUST NOT be after `not_before` |
| `not_before` | yes | integer | Unix seconds — validity window start |
| `expires_at` | yes | integer | Unix seconds — validity window end (must be strictly after `not_before`) |
| `nonce` | yes | string | Carried for future replay protection (see §8) |
| `kid` | yes | string | Signing key identifier |
| `sig` | yes | string | Detached Ed25519 signature (base64) |

Both `policy_hash` and `policy_version` are supported explicitly (the task
allows either or both) since different deployments may want a content
digest, a human-readable version label, or both.

No payment, fraud, phishing, or risk-class vocabulary is hard-coded into the
schema or the verifier. `claims` is opaque structured data as far as this
package is concerned — but it must be *canonically serializable*: recursively
composed only of `None`, `bool`, `str`, finite `int`/`float`, and
`dict`/`list` with string-only object keys (see §5a). A `set`, a custom
object, a non-string dict key, or a non-finite float (`NaN`/`Infinity`) is
rejected at construction, not silently coerced or dropped.

### 5a. Temporal invariant

```
issued_at <= not_before < expires_at
```

Both legs are enforced structurally (in `EvidenceAttestation.__post_init__`,
so identically whether an attestation is built via `from_dict` or
constructed directly, e.g. by `LocalAttester`) — an attestation violating
either ordering is malformed and is rejected before signature verification
is ever attempted, exactly like any other structural defect.

### 5b. Digest field format

`action_hash`, and `payload_hash`/`policy_hash` when present, MUST match
`sha256:<64 lowercase hex characters>` — the exact format
`mcc_core.signing.sha256_hex` produces. This is enforced structurally, at
the same point as the temporal invariant above. `policy_version` is a
free-form label, not a digest, and carries no format constraint.

### 5c. Immutability

`EvidenceAttestation` is a **frozen dataclass**. `claims` and `provenance`
are additionally **deep-frozen** at construction — recursively converted
into `types.MappingProxyType` (for objects) and `tuple` (for arrays),
independent of whatever mutable `dict`/`list` the caller originally passed
in. Two consequences, both structurally guaranteed (not merely documented,
and not achieved by relying on signature verification as a substitute):

- Assigning to any field on a constructed `EvidenceAttestation`
  (`att.attestation_id = "..."`) raises `dataclasses.FrozenInstanceError`.
- Mutating `att.claims[...]`/`att.provenance[...]` directly raises
  `TypeError` (a `MappingProxyType` has no item-assignment); mutating the
  caller's *original* dict *after* construction has zero effect on the
  attestation's content, because `_freeze` builds new container objects
  rather than wrapping the caller's originals.

`unsigned_dict()`/`to_dict()` still return plain, JSON-serializable
`dict`/`list` values (thawed on the way out) so canonical signing and
verification are unaffected — the frozen representation is purely a
structural-integrity guarantee on the live Python object, not a change to
the wire format.

## 6. Canonicalization and signing

Reused, unchanged, from `mcc_core.signing`:

- `canonical_bytes` — deterministic JSON (`sort_keys=True`,
  `separators=(",", ":")`, `ensure_ascii=True`).
- `SigningKey.sign_token` — signs `unsigned_dict() + kid` as one unit and
  returns the claims with `kid` and `sig` attached. `kid` is therefore
  covered by the signature, not appended afterward.
- `verify_token` — strips only the `sig` field and recomputes the signature
  over everything else (including `kid`).

No second canonicalization scheme and no symmetric-key/shared-secret
signature scheme are introduced. Mutating any
signed field after issuance (`claims`, `action_hash`, `scope`, `evidence_type`,
`provenance`, timestamps, `nonce`, `attester_id`, `kid`) invalidates the
signature — proven in `tests/test_mcc_attestation.py` (tests 4, 5, 6).

The Attester signing key is a **trust boundary**. A model with access to
this private key could sign attestations about itself, destroying the
attribution guarantee this package exists to provide. Nothing in
`mcc_attestation` exposes, logs, or serializes a private key —
`mcc_core.signing.SigningKey` already refuses to; `LocalAttester` (the local
reference Attester) receives an already-computed assessment as data, never
calls an LLM, and never performs autonomous semantic reasoning — it only
binds and signs.

## 7. Attester trust model

`AttesterTrustStore` resolves the pair **`(attester_id, kid)`** to a trusted
Ed25519 public key plus a closed set of permitted `evidence_type` values.
This is a deliberate design choice: a public key registered under one
`attester_id` simply does not exist under any other `attester_id`. An
attestation that declares one attester's identity while carrying a `kid`
that was only ever registered to a *different* attester fails closed at
resolution — **trust is never inferred from an attestation's self-declared
`attester_id` alone.**

```
attester.payment-risk.v1
    kid: payment-risk-key-01
    evidence_types:
        - risk_assessment
```

Verification fails closed for:

- unknown attester
- unknown kid
- revoked/untrusted key
- attester/key mismatch (a kid registered to a different attester)
- `evidence_type` not permitted for that attester

`AttesterTrustAnchor` requires at least one permitted `evidence_type` at
construction — an attester is never trusted for an unbounded set. `revoke()`
stops future resolution of a `(attester_id, kid)` pair without erasing it
from the registry or altering any previously-issued attestation.

This is a minimal, in-memory implementation. A distributed/persistent
backend and a richer key-rotation workflow are legitimate future extensions,
not built here — PR-1 does not build a full PKI or remote key-distribution
service.

## 8. Deterministic verifier

`verify_attestation()` returns a structured `AttestationVerificationResult`
— never a bare boolean:

```
overall_status            # VERIFIED | INVALID | UNSUPPORTED_SCHEMA
schema_supported
structure_valid
signer_verified
signer_trusted
evidence_type_allowed
time_valid
action_binding_valid
payload_binding_valid     # Optional[bool] -- see below
scope_valid
policy_binding_valid      # Optional[bool] -- see below
checks       # ordered list of {name, status, detail}; status ∈ PASS|FAIL|NA
warnings
failures
attestation_id
attester_id
```

**`VERIFIED` means only that the attestation is cryptographically and
structurally valid under the supplied trust and expected bindings.** It does
**not** mean "the risk assessment is objectively correct," and it does
**not** itself authorize execution.

**`payload_binding_valid` and `policy_binding_valid` are `Optional[bool]`**,
distinctly from every other field above, because those two bindings are
themselves optional (the caller may or may not supply an expected value to
check against):

| Value | Meaning |
|---|---|
| `None` | **NOT CHECKED / NOT APPLICABLE.** The caller supplied no expected value, or verification did not reach this step. A caller MUST NOT read `None` as "proven." |
| `True` | The caller supplied an expected value and the attestation matched it. |
| `False` | The caller supplied an expected value and it did **not** match (the overall result is already `INVALID` in this case). |

The corresponding `checks` entry uses `CheckStatus.NA` (not `PASS`) whenever
the binding was not exercised — a result MUST distinguish an actually
verified binding from one that was simply never asked about. Before this
correction, both cases collapsed to `True`/`PASS`, which a future Control
integration could have misread as proof. This is now a structural
distinction (`Optional[bool]` + `NA`), not a documentation-only promise.

### Verification order (fixed, deterministic)

1. input/type validation
2. schema version
3. required fields / structural validation — includes the temporal
   invariant (§5a), digest-format checks (§5b), and canonical-structure
   checks on `claims`/`provenance` (§5)
4. attester identity (part of structural validation — one of the required
   string fields)
5. key lookup/trust — `(attester_id, kid) → AttesterTrustAnchor`
6. signature verification (Ed25519, via `mcc_core.signing.verify_token`)
7. `evidence_type` authorization against the resolved anchor
8. current-time validity window: `not_before <= now < expires_at`
9. `action_hash` binding against the caller's expected action
10. optional `payload_hash` binding, if the caller supplied an expected value
    (`NA` otherwise — see above)
11. expected `scope` binding
12. optional expected `policy_hash` / `policy_version` binding (`NA`
    otherwise)
13. success → `VERIFIED`

Any failing step returns a fail-closed result immediately (later steps would
be moot — the overall result is already `INVALID`). Structured boolean
fields not yet reached when a failure occurs remain `False` (or `None` for
the two optional bindings), so a caller can see exactly how far verification
got.

### Fail-closed guarantee

Malformed, unsigned, expired, not-yet-valid, forged, unsupported, untrusted,
wrongly bound, or otherwise invalid attestations **never** return `VERIFIED`.
Any unexpected exception anywhere in the verifier is caught and resolves to
`INVALID` — **no exception path can produce a `VERIFIED` result.** This is
proven directly by `tests/test_mcc_attestation.py::test_21_*`.

### Replay is deferred to Control (PR-2)

`nonce` is a required field, structurally validated (present, non-empty),
but **not consumed** by this package — no nonce registry is created, checked,
or claimed here. Consuming the nonce against a replay-detection registry
(exactly-once enforcement) is a Control/runtime responsibility, deferred to
PR-2's integration work. This package does not create a second, competing
nonce registry alongside `mcc_core.nonce`.

## 9. What PR-1 explicitly does not do

- Does not modify `src/mcc_core/gate.py`, `src/mcc_core/authority.py`,
  existing decision-token issuance, the Gateway API, public `/evaluate`
  endpoints, existing execution flow, or existing nonce/replay behavior.
- Does not modify `mcc_evidence` semantics.
- Does not bind attestations into decision tokens.
- Does not add execution-ticket semantics.
- Does not add an Attester network service, a queue, a Redis dependency, or
  a background worker.
- Does not add an ML model or a risk-class policy.
- Does not change `ALLOW` / `DENY` / `ESCALATE` / `CONSTRAIN` behavior.
- Does not consume replay state.

All of the above are explicitly deferred to PR-2 / PR-3.

## 10. Accurate claim language

Preferred:

- "cryptographically attributable assertion"
- "trusted signed attestation"
- "deterministic verification"
- "action-bound evidence"
- "pre-execution evidence"

Avoid:

- "cryptographic fact"
- "the attestation proves the risk is low"
- "the verifier proves the model is correct"
- "Control can never be wrong"

## 11. Reference implementation

- `src/mcc_attestation/schema.py` — `EvidenceAttestation`,
  `AttestationVerificationResult`, `AttestationStatus`, errors.
- `src/mcc_attestation/trust.py` — `AttesterTrustAnchor`,
  `AttesterTrustStore`.
- `src/mcc_attestation/attester.py` — `LocalAttester`, `sign_attestation`.
- `src/mcc_attestation/verifier.py` — `verify_attestation`.
- `tests/test_mcc_attestation.py` — the 23 mandatory security/behavior
  tests plus additional structural/trust-model coverage.
- `tests/test_mcc_attestation_architecture_guards.py` — static AST guards
  proving no LLM/agent-framework/execution/`mcc_evidence`-as-authority/
  `ExecutionGate` dependency.

See `specs/MCC-AT-001.md` for the normative specification.
