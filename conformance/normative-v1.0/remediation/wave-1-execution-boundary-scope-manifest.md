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

## Recommended paths forward

1. **Re-scope the next remediation wave** to a real Normative v1.0
   `GAP`/`PARTIAL` cluster that these four specifications actually govern —
   for example the Evidence Bundle three-file structure (`MCC-EB-001`), the
   Hash Reference / Evidence Bundle Reference / Manifest Reference
   sub-object composition (`MCC-CM-001`/`MCC-TC-001`), or wiring the
   existing Ed25519 canonical-serialization/signing primitives specifically
   to a Technical Certificate object. `conformance/normative-v1.0/gap_report.md`
   lists each candidate with a stated remediation scope (`SMALL` for the two
   PARTIAL-status primitives already reused from the runtime signing code;
   `LARGE` for the rest).
2. **If execution-boundary conformance is actually wanted**, it requires
   first bringing MCC-Core runtime-governance behavior into a specification's
   normative scope — either by amending MCC-CP-001/EB-001/CM-001/TC-001 or by
   authoring a new specification — through the same spec-first,
   architecture-author-approved process already used for this program, with
   its own requirement IDs. Only after that extraction step would Decision
   Token/Execution Gate requirements exist in a conformance baseline for a
   remediation wave to select.

No pull request scope beyond this manifest and report is proposed here; per
the task's own architecture constraints, this PR does not merge, does not
implement unrelated changes, and does not claim any conformance status
change.
