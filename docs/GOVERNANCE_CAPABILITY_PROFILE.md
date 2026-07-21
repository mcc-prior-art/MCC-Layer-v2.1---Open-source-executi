# MCC-Core Governance Capability Profile

**Status: Normative.** Profile format version **1** (`profile_version: "1"`).
Schema id `mcc-governance-capability-profile/1`.

A Governance Capability Profile is a **declarative**, framework-neutral,
machine-readable, versioned statement of which MCC-Core governance capabilities an
adapter supports. It is part of the Integration Contract ecosystem and changes
**no** runtime governance semantics.

> **A Governance Capability Profile is a declarative statement of adapter
> capabilities. It does not grant execution authority, replace runtime
> authorization, or weaken fail-closed enforcement.**

## Purpose & scope

Adapters differ in which optional governance features they exercise (human
escalation, constraint enforcement, portable audit evidence). The profile lets any
adapter declare — deterministically and verifiably — its supported, optional, and
explicitly-unsupported capabilities, so the Compliance Suite can validate the
declaration and the Certified Adapter Program can record the *validated* profile.

In scope: the declaration format, its schema, validation, canonicalization, and
digest. **Out of scope:** any new authorization protocol, policy engine, gateway,
transport, signing format, adapter SDK, dynamic plugin loading, remote negotiation,
or marketplace. This document adds no runtime behavior.

## Terminology — four terms that are NOT synonyms

| Term | Meaning | Produced by |
|------|---------|-------------|
| **declared** | the adapter says so in a profile | the adapter (untrusted) |
| **validated** | the profile passed schema + semantic validation | `validate_profile` |
| **certified** | the Certified Adapter Program recorded real compliance evidence | `mcc_compliance.program` |
| **authorized** | the runtime Gate permitted a specific action | the Gate (per action, fail-closed) |

A capability declaration never implies the next column. **Capability support is not
execution permission.**

## Relationship to the rest of the ecosystem

- **Integration Contract** (`docs/INTEGRATION_CONTRACT.md`) is normative; the profile
  references a contract version and its capability vocabulary is single-sourced from
  the contract's `REQUIRED_SECURITY_INVARIANTS`.
- **Compliance Suite** validates the declaration (schema + semantics).
- **Certified Adapter Program** links a *validated* profile to a certification via
  `link_capability_profile` (in the certification report, not the committed
  manifest — existing artifacts stay backward compatible).
- **Runtime authorization** remains entirely separate and fail-closed: every action
  is still independently decided by the Gate regardless of any profile.

## Canonical model & serialization

Implemented in `mcc_compliance.capability_profile`. A profile is a JSON object:

| Field | Req | Meaning |
|-------|-----|---------|
| `profile_version` | ✔ | profile format version (`"1"`) |
| `adapter` | ✔ | `{name, version, implementation_id, framework?}` — `framework` is descriptive metadata only |
| `integration_contract` | ✔ | `{version}` — canonical `MAJOR.MINOR`, no free-form claims |
| `compliance` | — | `{suite_version?, vector_set_version?}` |
| `certification` | — | `{claimed_status, evidence_digest?}` — a raw profile may only `SELF_DECLARED` |
| `runtime_capabilities` | ✔ | supported baseline + optional capabilities |
| `optional_capabilities` | — | supported optional capabilities |
| `unsupported_capabilities` | — | explicitly unsupported optional capabilities |
| `constraints` | — | structured per-capability constraints (keys must be supported) |
| `metadata` | — | open forward-compatibility namespace (non-normative) |

**Canonicalization** (`canonicalize_profile`) sorts and de-duplicates capability
lists and normalizes structure, so the same semantic profile always canonicalizes
identically regardless of input key/list ordering or whitespace. **Digest**
(`profile_digest`) is `sha256` over the canonical form, reusing
`mcc_core.signing.canonical_bytes` — an integrity fingerprint, **not** a signature
or trust scheme.

## Capability registry (single-sourced, evidence-backed)

**Baseline (mandatory)** — the exact Gate-enforced invariants
(`REQUIRED_SECURITY_INVARIANTS`): `signature_verified`, `decision_authority_valid`,
`verdict_authorizes`, `scope_matches`, `actor_matches`, `resource_matches`,
`action_hash_matches`, `nonce_matches`, `nonce_not_replayed`,
`within_validity_window`, `not_revoked`, `policy_hash_matches`,
`durably_recorded_before_enforce`. Because a conforming adapter passes through the
Gate, **all** baseline capabilities MUST be declared supported.

**Optional (closed set)** — each backed by a real repository feature:
`human_in_the_loop_escalation` (ESCALATE + single-use approval loop),
`constraint_enforcement` (CONSTRAIN verdict), `tamper_evident_audit_evidence`
(portable Governance Evidence Bundle, PR #42).

No capability outside this registry is accepted; there is no unbounded free-form
capability namespace.

## Validation behavior

`validate_profile(profile) -> ProfileValidation` performs schema-shape checks and
semantic checks and returns structured, deterministically-ordered errors with stable
`ProfileErrorCode` values. Semantic invariants:

- supported (`runtime` ∪ `optional`) and `unsupported` sets are disjoint;
- every baseline capability is supported; none is declared unsupported;
- all capability names are in the canonical registry; no duplicates;
- `profile_version` is supported; `integration_contract.version` is compatible;
- a present `compliance.suite_version` is recognized;
- adapter identity fields are non-empty strings;
- constraints reference only supported, known capabilities and are structured objects;
- a raw profile's `certification.claimed_status` must be `SELF_DECLARED` — claiming
  `VALIDATED`/`CERTIFIED` is a `FALSE_CERTIFICATION_CLAIM` (fail-closed).

### Failure behavior

Fail-closed: any error yields `valid=False`, no digest, and stable error codes. The
CLI prints no stack trace for a normal validation failure.

## Versioning, backward & forward compatibility

- The profile version is independent of the contract, compliance-suite, and package
  versions. Unsupported `profile_version` fails closed.
- **Forward compatibility:** unknown top-level or `adapter` fields are **rejected**
  (strict), except the `metadata` object, which is the explicit open namespace for
  non-normative additions. This matches the repository's strict-schema posture while
  still giving adapters a forward-compatible slot.
- **Backward compatibility:** the profile is **optional**. Legacy adapters and
  existing certification artifacts continue to work unchanged; a missing profile is
  represented explicitly as *no capability profile declared* and is **never**
  fabricated as fully capable. The committed certification manifest is unchanged.

## Certification linkage

`link_capability_profile(certification_result, profile)` (in
`mcc_compliance.program`) validates the profile, checks its adapter identity matches
the certification, and returns a linkage record carrying `self_declared: false`, the
`profile_digest`, and a `validation_status` of `CERTIFIED` / `VALIDATED` /
`REJECTED`. A self-declared profile can therefore **never** appear equivalent to
independently generated certification evidence.

## Security considerations

- Fail closed on malformed profiles.
- Never infer authority from a capability declaration.
- Never infer certification from adapter self-declaration.
- Never infer runtime authorization from certification.
- Reject contradictory supported/unsupported declarations and unknown/missing
  required capabilities.
- Reuse trusted canonicalization/hashing; introduce no new trust model.

## Non-authority statement

A Governance Capability Profile is descriptive metadata about an adapter. It confers
no authority. MCC-Core remains the decision authority; the Gate independently and
fail-closed authorizes or denies each action regardless of any declared, validated,
or certified capability profile.

## Positioning

MCC-Core is a framework-neutral execution-governance architecture and an emerging
governance contract / certification ecosystem — a protocol candidate, not a claimed
adopted industry standard.
