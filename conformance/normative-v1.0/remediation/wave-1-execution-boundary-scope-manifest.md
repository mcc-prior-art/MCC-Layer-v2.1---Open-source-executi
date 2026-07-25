# MCC Normative v1.0 Conformance Remediation — Wave 1: Execution Boundary

**Status: BLOCKED — verified methodological defect. No requirements selected.
No remediation performed. `CONFORMANT` remains 0.**

This document is the required first-step deliverable for Wave 1 (per-wave
scope manifest). It reports why Wave 1, as scoped, has zero eligible
requirements against the Normative v1.0 baseline, rather than fabricating a
selection or forcing a `CONFORMANT` increase. The machine-readable form of
this finding is
[`wave-1-execution-boundary-scope-manifest.json`](./wave-1-execution-boundary-scope-manifest.json).

## Objective (as given)

Select a bounded subset of existing `GAP`/`PARTIAL` findings from the
Normative v1.0 baseline (`conformance/normative-v1.0/requirements.json`, 429
requirements) tied to the mandatory execution-control boundary: Decision
Token signature verification, action-hash binding, audience binding,
policy-hash binding, nonce/replay rejection, `nbf`/expiry, DENY blocking
actuation, audit-before-actuation, and bypass prevention — then implement the
minimal corrections needed to move those specific requirements to
`CONFORMANT`, with direct tests and evidence.

## Source of truth

- `conformance/normative-v1.0/requirements.json` (429 requirements, generated
  from `specs/MCC-CP-001.md`, `specs/MCC-EB-001.md`, `specs/MCC-CM-001.md`,
  `specs/MCC-TC-001.md`)
- Baseline commit: `ef95b13ad449166965e6ae901c2e483ceb95e6da` (`origin/main`,
  merge of PR #60), which contains the reviewed Normative v1.0 declaration
  commit `a65b2f375408dfbe8df86fbfc09724c5c45d3ba4` unchanged.

## Verification performed

1. Searched every requirement's `requirement_text`, `requirement_category`,
   and `section` in the committed `requirements.json` for the Wave 1
   vocabulary: `nonce`, `audience`, `action-hash`, `action_hash`,
   `policy-hash`, `policy_hash`, `nbf`, `decision token`, `execution gate`,
   `replay`, `actuation`, `fail-closed`, `ALLOW`, `DENY`, `ESCALATE`,
   `CONSTRAIN`.
2. `nonce`, `audience`, `action-hash`/`action_hash`, `policy-hash`/
   `policy_hash`, `nbf`, `decision token`, `execution gate`, `replay`, and
   `actuation` produced **zero matches** anywhere in the 429-requirement
   corpus.
3. `ALLOW`/`DENY`/`ESCALATE`/`CONSTRAIN` produced exactly three matches, all
   of them explicit scope-exclusion statements:
   - `MCC-CM-001-6-NON-GOALS-D01` (MCC-CM-001 §6, Non-Goals): *"This
     specification SHALL NOT: ... define runtime governance behavior (ALLOW,
     DENY, ESCALATE, CONSTRAIN), which belongs exclusively to MCC-Core
     runtime governance."*
   - `MCC-EB-001-6-NON-GOALS-D01` (MCC-EB-001 §6, Non-Goals): the identical
     exclusion clause.
   - `MCC-TC-001-ABSTRACT-D02` (MCC-TC-001, Abstract): *"A Technical
     Certificate is a certification-program artifact. It is not, and SHALL
     NOT be interpreted as, a runtime execution authorization. Runtime
     governance behavior (ALLOW, DENY, ESCALATE, CONSTRAIN) belongs
     exclusively to MCC-Core runtime governance and is out of scope for this
     specification."*
4. `fail-closed` produced six matches, none of which concern the Execution
   Gate: `CM-CONF-003`/`CM-VAL-001`, `EB-CONF-003`/`EB-VAL-001`, and
   `TC-CONF-003`/`TC-VERIFY-001` require that a **Manifest validator**,
   **Evidence Bundle validator**, and **Technical Certificate verifier**
   (certification-program tooling that does not yet exist) be fail-closed —
   not that the runtime Execution Gate be fail-closed. These six are already
   tracked in the baseline (as `GAP`/`PARTIAL`) for reasons unconnected to
   Wave 1's execution-boundary vocabulary, and moving them to `CONFORMANT`
   requires building the certification-program validators/verifiers
   themselves (MCC-EB-001/MCC-CM-001/MCC-TC-001 conformance suites), not
   anything about Decision Tokens, nonces, or the Execution Gate.
5. Independently re-confirmed this against the specification source files
   directly (`specs/MCC-CP-001.md`, `specs/MCC-EB-001.md`,
   `specs/MCC-CM-001.md`, `specs/MCC-TC-001.md`): every occurrence of
   `execution`, `ALLOW`, `DENY`, `ESCALATE`, or `CONSTRAIN` in all four files
   is part of an explicit statement that runtime execution/governance
   semantics are out of scope.

## Finding

**Zero of the 429 Normative v1.0 requirements impose an obligation on the
Wave 1 execution-boundary vocabulary.** All four specifications —
MCC-CP-001 (Certification Program), MCC-EB-001 (Evidence Bundle),
MCC-CM-001 (Certification Manifest), MCC-TC-001 (Technical Certificate) —
govern the **certification program's own artifacts** (how an Evidence
Bundle, Certification Manifest, and Technical Certificate are structured,
issued, and verified), and each one explicitly, repeatedly disclaims any
authority over MCC-Core's **runtime governance** behavior (Decision Tokens,
the Execution Gate, ALLOW/DENY/ESCALATE/CONSTRAIN verdicts, nonce/replay
protection, action-hash/audience/policy-hash binding). That vocabulary
belongs exclusively to `src/mcc_core/` (`gate.py`, `signing.py`, `nonce.py`,
`coordinator.py`, `authority.py`) and is tested by `tests/test_mcc_core.py`,
`tests/test_nonce.py`, `tests/test_coordinator.py`, etc. — a real,
well-tested system, but one this Normative v1.0 spec program was scoped, by
its own authors, to exclude.

This is precisely the situation the task instructions anticipated: *"The
global result must show a real increase above `CONFORMANT: 0` unless a
verified methodological defect prevents it. If so, stop and report the
defect rather than manufacturing conformance."* No selection was made, no
test was added, and no conformance artifact was regenerated, because there
is no legitimate requirement subset for Wave 1 to remediate as scoped.

## Follow-up review: two additional findings

A subsequent read-only architectural review (requested separately, before this
PR was merged) re-verified the finding above and surfaced two further facts.
Both are documented here, in the same PR, because they change how the "paths
forward" below should be read. Neither changes the Wave 1 conclusion itself.

### Finding 1 — PR #60's requirement extraction is independently incomplete

`src/mcc_conformance/extract.py` disables its derived-requirement fallback for
an *entire* H1 section the moment that section contains a canonical
requirement ID anywhere within it (the `covered_h1` check, around lines
152-155). Canonical extraction itself only captures the paragraph immediately
following an ID line. Any other `MUST`/`SHALL`/`SHALL NOT`/`MUST NOT`/
`REQUIRED` sentence in that same section, not restated verbatim under a
canonical ID, is silently dropped — never extracted, canonical or derived,
and therefore absent from `requirements.json`, `traceability_matrix.*`, and
`gap_report.md`.

Measured directly against the four specification files:

| Spec | Orphaned MUST/SHALL-class lines never extracted |
|---|---|
| MCC-CP-001 | 155 |
| MCC-TC-001 | 102 |
| MCC-EB-001 | 73 |
| MCC-CM-001 | 61 |
| **Total** | **391** (vs. 429 requirements currently in the baseline) |

Concrete example: `specs/MCC-CP-001.md` §7.4 "Certification Outputs" states
*"Every successful certification SHALL produce: Evidence Bundle;
Certification Manifest; Technical Certificate; Conformance Result;
Certification Report. These outputs SHALL be reproducible."* — the exact
requirement Appendix G and Appendix H (PR #57) exist to satisfy — and it has
**no requirement ID of its own** anywhere in `requirements.json`, because the
neighboring §7.5 Certification Invariants block (`CI-001`..`CI-010`) does not
restate it verbatim.

**This does not change the Wave 1 conclusion.** The vocabulary search in this
document's "Verification performed" section was run against the full
specification source text directly, not against `requirements.json`, so it
already covers these 391 orphaned lines — none of them contain
execution-boundary vocabulary either. It is reported because it independently
invalidates the completeness claim in `conformance/normative-v1.0/README.md`
("Every normatively-binding requirement ... has been discovered"), which is
not accurate as the baseline is currently generated.

**Status: documented only. `src/mcc_conformance/extract.py` is not modified
by this PR.**

### Finding 2 — runtime execution-boundary behavior already has real normative coverage; it is only disconnected from this program

Runtime governance is out of scope for MCC-CP-001/EB-001/CM-001/TC-001 (see
"Finding" above) — but that does **not** mean it is unspecified anywhere in
this repository. `docs/INTEGRATION_CONTRACT.md` is itself already
`Status: Normative`, contract version `1.0`
(`mcc_client.contract.CONTRACT_VERSION`), and contains explicit `MUST`-level
normative prose covering every item in the Wave 1 vocabulary:

| Concept | Citation in `docs/INTEGRATION_CONTRACT.md` |
|---|---|
| Decision Tokens | lines ~40, ~274 |
| Execution Gate | lines ~88, ~114, ~131, ~329 |
| authority/action/scope/audience/policy binding | line ~393 ("authority/scope/identity/policy binding at the Gate") |
| nonce and replay protection | lines ~276, ~297-298, ~349 |
| validity windows | line ~299 (`within_validity_window`) |
| fail-closed execution | lines ~187, ~200-201, ~219, ~222, ~227, ~336, ~393 |
| audit-before-actuation | lines ~136, ~228, ~302, ~393 |
| bypass prevention | lines ~329, ~395 ("cannot bypass the gate") |

It also already has real, tested, CI'd conformance evidence behind it:

- `src/mcc_compliance/vectors/v1/manifest.json` — golden vectors (`IC-V1-*`).
- `certifications/manifest.json` — two real `CERTIFIED` entries
  (`reference-governed-agent`, `voltagent`), each with `covered_invariants`
  including `action_hash_matches`, `nonce_not_replayed`,
  `policy_hash_matches`, `within_validity_window`, `verdict_authorizes`,
  `not_revoked`, `durably_recorded_before_enforce`, `signature_verified`,
  `actor_matches`, `resource_matches`.
- `tests/test_compliance_suite.py`, `tests/test_certified_adapter_program.py`.
- `sdk/python/src/mcc_client/contract.py` — the canonical wire models
  (`CONTRACT_VERSION`, `ContractErrorCode`, `conformance_manifest()`).

**The disconnection is structural, not substantive:**

- `grep -rn "Integration Contract" specs/*.md` returns **zero** results —
  none of the four Normative v1.0 specifications reference
  `docs/INTEGRATION_CONTRACT.md`.
- `docs/INTEGRATION_CONTRACT.md` has **no canonical `XX-000`-style
  Requirement Identifier Registry** (verified: zero lines match
  `^[A-Z][A-Z-]{1,20}-[0-9]{3}$`); it expresses its normative content as
  prose plus named tables ("Traceability matrix", "Invariant ownership
  matrix"), which `src/mcc_conformance/extract.py`'s canonical-ID-line
  extraction cannot parse.
- It is not listed in `extract.py`'s `SPEC_FILES` and has no presence in
  `conformance/normative-v1.0/requirements.json`.

**Correction to this document's original framing:** the original "recommended
paths forward" below implied that execution-boundary conformance would need
to be specified and implemented from scratch. That is corrected here: the
behavior is already specified and already has real conformance evidence. The
open question is registration/reconciliation, not specification or
implementation from scratch.

### Unresolved design decision (not made by this PR)

How should `docs/INTEGRATION_CONTRACT.md`'s existing coverage become
selectable by `conformance/normative-v1.0/` tooling and future waves?

1. **Register/reconcile it under a dedicated normative identifier**, e.g.
   `MCC-RG-001` — a thin specification that canonically adopts
   `docs/INTEGRATION_CONTRACT.md` and `mcc_client.contract` as its normative
   source (not a rewrite), with an `RG-###` Requirement Identifier Registry
   compatible with the existing extractor convention, parallel to (not
   subordinate to) CP-001/EB-001/CM-001/TC-001.
2. **Extend the conformance extractor** to ingest
   `docs/INTEGRATION_CONTRACT.md`'s table-based normative sections directly,
   without requiring the source document to adopt a canonical `XX-000` ID
   convention.

This PR does not decide between them and implements neither.
**`src/mcc_conformance/extract.py` is not modified. `MCC-RG-001` is not
created.**

### Future remediation candidates identified during this review (not implemented here)

These are dependency-ordered candidate waves for genuinely in-scope
MCC-EB-001/MCC-CM-001/MCC-TC-001 `GAP`/`PARTIAL` requirements, recorded so a
future implementation PR has a concrete starting point. **None of them are
implemented, tested, or evidence-generated by this PR.**

**Wave A — Evidence Bundle Structure and Hash Reference alignment** (small–medium)
- `CM-HASH-001..004` (PARTIAL) + `EB-STR-001..005` (PARTIAL) +
  `EB-FILE-001..005` (PARTIAL) — 14 requirements.
- Reuses `src/mcc_evidence/export.py`, `schema.py`, `verify.py`,
  `src/mcc_core/signing.py` — extends the existing bundle system in place
  (the exact Bundle Descriptor / Integrity Record / Provenance Record
  three-file split, plus a structured Hash Reference object) rather than
  creating a parallel one.
- No dependencies — leaf-level.

**Wave B — Evidence Bundle Reference in the Certification Manifest** (small)
- `CM-EBREF-001..004` (currently GAP) — 4 requirements.
- Depends on Wave A (needs a real EB-001-conformant Bundle and Hash
  Reference object to point at).

**Wave C — Technical Certificate required fields and model** (medium–large)
- `TC-RFLD-001..006` + `TC-MODEL-001..004` (PARTIAL) — 10 requirements.
- Reuses `gateway/trust.py`, `src/mcc_core/signing.py`.
- Depends on Wave A and Wave B (a Certificate references a Manifest which
  references a Bundle).

## What was deliberately NOT done

- No requirement was reclassified, and no `GAP`/`PARTIAL` finding was
  suppressed, deleted, or reworded to manufacture eligibility.
- No code was added to `src/mcc_core` or elsewhere purporting to "implement"
  an execution-boundary requirement that no Normative v1.0 specification
  states.
- No test was added asserting conformance to a nonexistent requirement.
- `conformance/normative-v1.0/requirements.json`,
  `traceability_matrix.{json,md}`, and `gap_report.md` were **not**
  regenerated, because nothing that feeds their generation (`specs/*.md`,
  `src/mcc_conformance/assess.py`) changed. Regeneration would be a no-op;
  running it was unnecessary and is left to CI's existing drift check.
- `src/mcc_conformance/extract.py` was **not** modified, despite Finding 1
  above — the extraction coverage gap is documented, not corrected, here.
- `MCC-RG-001` was **not** created, and no design decision between the two
  options above was made — both remain open, owner: AX.
- Waves A, B, and C above are **not** implemented — no production code, no
  tests, no evidence was generated for any of their requirement IDs. This
  remains a documentation-only PR.
- No `CONFORMANT` transition was manufactured anywhere in this PR; the
  baseline counts are unchanged (see "Before / after conformance delta" in
  the PR description).

## Recommended paths forward

1. **Decide the unresolved design decision** above (register/reconcile the
   Integration Contract under `MCC-RG-001`, vs. extend the extractor to
   ingest it directly) before any execution-boundary remediation wave can
   select real requirement IDs. This PR does not make that decision.
2. **Independently of that decision, start with Wave A** (Evidence Bundle
   Structure and Hash Reference alignment) as the correctly-scoped,
   dependency-ordered first remediation wave for genuinely in-scope
   MCC-EB-001/MCC-CM-001 findings — see "Future remediation candidates"
   above and `conformance/normative-v1.0/gap_report.md`.
3. **Correct the extraction coverage gap** (Finding 1) in
   `src/mcc_conformance/extract.py` in a dedicated methodology-correction
   PR before relying on `requirements.json` as a complete inventory for any
   future wave selection.

No pull request scope beyond this manifest and report is proposed here; per
the task's own architecture constraints, this PR does not merge, does not
implement unrelated changes, and does not claim any conformance status
change.
