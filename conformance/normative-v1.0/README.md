# MCC Normative v1.0 — Implementation Conformance Baseline

This directory is a **traceability and assessment milestone**, not a
certification. It is generated and validated by `src/mcc_conformance`
(`python -m mcc_conformance generate|validate`).

## What this baseline proves

- Every normatively-binding requirement (MUST, MUST NOT, SHALL, SHALL NOT,
  REQUIRED, or an explicitly declared normative invariant) in
  `specs/MCC-CP-001.md`, `specs/MCC-EB-001.md`, `specs/MCC-CM-001.md`, and
  `specs/MCC-TC-001.md`, as of the reviewed baseline commit, has been
  discovered with a stable identifier — 361 requirements already carry a
  canonical identifier defined by the specifications' own Requirement
  Identifier Registry sections; 68 additional requirements, expressed as
  binding prose without a canonical ID, were discovered and given a
  deterministic derived identifier.
- Every one of those 429 requirements has exactly one explicit conformance
  status (`requirements.json`, `traceability_matrix.md`).
- For every requirement not marked CONFORMANT, `gap_report.md` states what
  exists, what is missing, and a recommended remediation scope.
- The assessment is grounded in an actual, disclosed investigation of this
  repository's existing implementation surface (`src/`, `tests/`,
  `certifications/`, `evidence/`, `schemas/`, CI workflows) — not merely a
  grep for each specification's exact vocabulary. See "Methodology" below.
- The baseline's own tooling and generated artifacts are deterministic and
  schema-validated (`python -m mcc_conformance validate`, run in CI).

## What this baseline does NOT prove

- **It does not certify MCC-Core.** No requirement in this baseline is
  marked CONFORMANT (see Methodology). Certification requires an actual
  Evidence Bundle / Certification Manifest / Technical Certificate
  implementation, built and tested against these four specifications
  specifically, and a normative Conformance Suite execution — none of
  which exist yet.
- **It does not certify any adapter.** The pre-existing
  `src/mcc_compliance/` Compliance & Certification Suite certifies adapters
  against the *Integration Contract* (a different, older normative
  document), not against MCC-CP-001/EB-001/CM-001/TC-001.
- It does not execute, generate, or validate an actual Evidence Bundle,
  Certification Manifest, or Technical Certificate, because none exist to
  generate. It is a static, source-level trace.
- A PARTIAL status means a real, tested, semantically-related mechanism
  exists under a different name/scope — it does not mean the requirement,
  as this specification states it, is implemented.

## Specification release vs. implementation conformance vs. ecosystem certification

These are three distinct, sequential milestones. This baseline is the
**second** one, and even that is not yet complete:

1. **Specification release** (done) — MCC-CP-001/EB-001/CM-001/TC-001 are
   published as `Version: 1.0` / `Status: Normative`
   (`docs/MCC_SPECIFICATION_PROGRAM_NORMATIVE_V1_0.md`, tag
   `mcc-spec-v1.0.0`). This defines *what* is required. It says nothing
   about whether any implementation satisfies it.
2. **Implementation conformance** (this directory, in progress) — tracing
   every requirement to real code, real tests, and real evidence, honestly
   reporting gaps. A specification release does not imply conformance, and
   this baseline currently reports zero CONFORMANT requirements.
3. **Ecosystem / adapter certification** (not started) — certifying that a
   *specific implementation or adapter* satisfies the specifications, via
   execution of a normative Conformance Suite against real artifacts. This
   requires (2) to reach CONFORMANT on the applicable requirements first.
   **This PR does not perform, claim, or approximate step 3.**

## Methodology (and its limitations)

Assessment was performed at **requirement-category** granularity (grouped
by specification section / theme), not as an independently bespoke code
review of all 429 individual requirements. Requirements sharing a section
and normative theme share a status and rationale unless repository
evidence specifically distinguished them. This is disclosed, not hidden,
and is itself a limitation: a category-level PARTIAL does not guarantee
every individual requirement in that category has equally strong evidence.

Before any GAP classification, the following existing subsystems were read
and semantically compared against the relevant specification section —
absence of a specification's exact vocabulary (e.g. no literal string
"Bundle Descriptor") was treated only as an investigation *signal*, never
as final evidence of non-conformance:

- `src/mcc_evidence/` — a real, tested "Governance Evidence Bundle" system
  (directory/`.tar.gz` forms, SHA-256 digest recomputation and tamper
  detection, schema-version rejection, fail-closed verification, Ed25519
  signature verification).
- `src/mcc_compliance/` + `certifications/manifest.json` — a real, tested,
  deterministic certification system (golden requirement-like vectors with
  a `mandatory` flag, a compliance runner, a versioned certification
  manifest with digest-bound evidence and a CERTIFIED/NOT_CERTIFIED-style
  status, JSON + human-readable Markdown reports).
- `gateway/trust.py` — a real, tested multi-issuer trust set (per-issuer
  Ed25519 keys, rotation, per-key expiry, explicit revocation status,
  fail-closed unresolved-key handling).
- `src/mcc_compliance/capability_profile.py` — a real, tested, versioned,
  fail-closed Governance Capability Profile validator.

PARTIAL is used wherever a section's *behavior* has a real, tested analog
under a different name or scope, even with zero lexical overlap with the
specification's vocabulary. GAP is reserved for sections where, after this
investigation, no equivalent implementation behavior, test, or evidence
mechanism was found anywhere in the repository — principally: the exact
three-file Bundle structure (MCC-EB-001), structured Hash Reference /
Evidence Bundle Reference / Manifest Reference sub-objects as these
specifications define their required composition, the Revocation Record
model applied to an actual Technical Certificate, and every
specification's Extension Model.

**No requirement is marked CONFORMANT in this baseline.** That status
requires both an implementation reference and a meaningful automated test
tied to the *specific requirement as this specification states it* — not
to a semantically-adjacent requirement in a differently-scoped system. The
PARTIAL findings above are exactly the candidates for CONFORMANT once that
specific wiring is built; see `gap_report.md` for each one's recommended
remediation scope.

The full rule table, with its citations, is in
`src/mcc_conformance/assess.py` (see its module docstring for the complete
methodology statement).

## Regenerating and validating

```
python -m mcc_conformance generate   # recompute all artifacts from the specs
python -m mcc_conformance validate   # fail-closed structural + schema + drift check
pytest tests/test_conformance_baseline.py -v
```

`generate` is fully deterministic: given the same specification files and
the same assessment rules in `assess.py`, it always produces byte-identical
output (no wall-clock timestamps, random IDs, or unordered collections
anywhere in the generated artifacts). CI runs `generate` and diffs it
against the committed files — a stale, uncommitted regeneration fails the
build.

## How future specification versions must be handled

- A future MCC-CP-001/EB-001/CM-001/TC-001 revision that changes `Version:`
  MUST be re-extracted: run `python -m mcc_conformance generate` and commit
  the result. `validate_baseline_provenance` (in `src/mcc_conformance/
  validate.py`) enforces that every specification listed in `baseline.json`
  declares `version: "1.0"` — a version bump requires a corresponding
  update to `baseline.json`'s `BASELINE` constant in
  `src/mcc_conformance/generate.py`, not a silent drift.
- A breaking specification revision that removes or renumbers a canonical
  requirement identifier will change `requirements.json`'s content
  deterministically on regeneration; the previous baseline's file remains
  available via git history for historical comparison.
- The reviewed baseline commit (`a65b2f375408dfbe8df86fbfc09724c5c45d3ba4`)
  and tag (`mcc-spec-v1.0.0`) in `baseline.json` are fixed to this v1.0
  declaration and are not automatically updated by regeneration; a future
  Normative v1.1/v2.0 declaration should introduce its own
  `conformance/normative-v<X>.<Y>/` directory rather than overwrite this
  one, preserving this baseline as a historical record.

## How future implementation changes must update traceability

- Adding, moving, or renaming a file cited in `implementation_references`
  or `test_references` for any requirement requires updating
  `src/mcc_conformance/assess.py` and regenerating; `python -m
  mcc_conformance validate` fails closed if a cited path no longer exists.
- Upgrading a requirement from PARTIAL to CONFORMANT requires adding both a
  genuine implementation reference *for that specific requirement* and a
  genuine automated test reference for it in `assess.py`, then
  regenerating — `validate_requirements` (in `src/mcc_conformance/
  validate.py`) fails closed on a CONFORMANT requirement missing either.
- This baseline does not need to be regenerated for changes that do not
  touch the four specification files, the `src/mcc_conformance/assess.py`
  rule table, or the cited implementation/test paths' existence.

## Explicit statements

- **This PR does not certify MCC-Core.**
- **This PR does not certify any adapter.**
- **Certification will occur only after gap remediation and successful
  execution of the normative Conformance Suite** — a Suite that does not
  yet exist and is not created by this PR (see `gap_report.md` for the
  remediation items that would need to precede it).
