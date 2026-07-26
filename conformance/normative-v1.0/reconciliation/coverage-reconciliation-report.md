# MCC Normative v1.0 — Coverage Reconciliation Report

PR #66. Machine-readable backing: the existing
`conformance/normative-v1.0/requirements.json` (unchanged in content by this
PR — see the Status Reconciliation Report for why zero requirement statuses
moved) plus the new audit assertions in
`tests/test_normative_coverage_reconciliation.py`.

## Objective

Independently audit the completeness, identity integrity, and evidence
integrity of the existing four-specification conformance registry — without
assuming the prior total (810) is correct, and without building a second,
parallel extraction/registry tool. This report documents the methodology
used, every check performed, and every genuine finding, whether or not it
required a code change.

## Starting baseline (post-PR #65)

- 91 CONFORMANT, 527 PARTIAL, 102 GAP, 90 NOT_APPLICABLE, 810 total.
- 1466 passed, 0 failed, 18 skipped (pre-existing, unrelated).

## Methodology

### Why this is an audit of the existing extractor, not a second one

`src/mcc_conformance/extract.py` is already a real, two-pass, deterministic
extractor with its own internal duplicate-detection and coverage-audit
machinery (`coverage_audit.py`, `extraction_coverage_audit.json`) built
specifically to catch the class of defect this PR is commissioned to rule
out (391 silently-orphaned MUST/SHALL lines, found and fixed in PR #62).
Building a second, independent extractor to "re-derive the inventory from
scratch" would itself become exactly the kind of duplicated verification
stack the task explicitly forbids, and would not be more trustworthy than
auditing the existing one rigorously — two parsers making the same design
decisions independently is not independent verification.

Instead, this audit:

1. Read the complete current text of all four specifications directly
   (not from memory / prior session context — freshly re-read in this PR).
2. Performed **independent, from-scratch, non-extractor-reusing** checks
   against the raw specification text (raw `grep`-based RFC 2119 keyword
   counts per file, and a from-scratch per-H1-section "does this section
   contain a binding keyword, and if so does the registry have at least one
   requirement for it" pass, written independently of `extract.py`'s own
   line-index bookkeeping — see
   `tests/test_normative_coverage_reconciliation.py::test_every_h1_section_with_a_binding_keyword_yields_at_least_one_requirement`).
3. Audited the registry's own internal identity and evidence integrity
   (duplicate IDs, cross-specification ID collisions, orphaned evidence,
   evidence-to-requirement bidirectional linkage, test-node existence).
4. Added four new intentional fixtures (missing requirement, duplicate
   requirement, non-normative example, cross-spec ID collision) reproducing
   the exact defect classes Part B/C of the task asks for, on isolated
   `tmp_path` specs — not the real corpus — so each fixture is unambiguous.

### Normative / non-normative boundary (unchanged, re-verified)

The boundary rule already in force (`extract.py`'s `_has_binding` /
`_is_structural`, `assess.py`'s `_META` regex) is:

- Only uppercase MUST, MUST NOT, SHALL, SHALL NOT, and (except inside the
  three-way REQUIRED/OPTIONAL/CONDITIONAL classification-enum idiom)
  REQUIRED are binding. SHOULD/RECOMMENDED/MAY are recorded as
  `normative_keyword` metadata where dominant but are not what makes a line
  a *candidate* for extraction as an obligation.
- Structural lines (headings, `---`, canonical ID lines, blank lines) are
  never candidates.
- A candidate whose normalized text exactly matches a canonical requirement
  already in the same H1 section is a duplicate of that canonical ID, not a
  new requirement — this is Pass 2's own dedup, not a post-hoc filter.
- Meta/bibliographic/illustrative sections ("Status of This Specification",
  "Abstract", "Normative References", the Requirement Identifier Registry
  section, Appendix D Revision History, Appendix E Example Certification
  Flow, Appendix F Future Extensions) are **extracted** (their MUST/SHALL
  prose is not silently dropped) but **assessed** `NOT_APPLICABLE` by
  `assess.py`'s `_META` regex — verified directly by
  `test_fixture_non_normative_example_section_is_assessed_not_applicable`,
  which confirms every real Appendix E / Appendix F requirement is
  `NOT_APPLICABLE`, never `CONFORMANT`/`PARTIAL`/`GAP`.

This is an intentional, disclosed design: extraction answers "is this
lexically/structurally a candidate obligation," assessment answers "is this
requirement in scope for a certification subject." Conflating the two
layers was not found to be a defect.

## Requirements found per specification (unchanged from the current registry)

| Specification | Canonical | Derived | Total |
|---|---|---|---|
| MCC-CP-001 | 155 | 185 | 340 |
| MCC-EB-001 | 62 | 82 | 144 |
| MCC-CM-001 | 60 | 70 | 130 |
| MCC-TC-001 | 84 | 112 | 196 |
| **Total** | **361** | **449** | **810** |

### Independent raw-keyword cross-check

Raw, `extract.py`-independent `grep -oE` word-boundary counts of MUST /
MUST NOT / SHALL / SHALL NOT / REQUIRED per specification file (a coarser
signal than requirement count, since one requirement's text can and does
contain more than one keyword, and canonical restatement inflates the raw
count relative to the deduplicated one):

| Specification | MUST | MUST NOT | SHALL | SHALL NOT | REQUIRED |
|---|---|---|---|---|---|
| MCC-CP-001 | 9 | 3 | 337 | 40 | 12 |
| MCC-EB-001 | 121 | 25 | 34 | 7 | 2 |
| MCC-CM-001 | 119 | 26 | 17 | 5 | 2 |
| MCC-TC-001 | 190 | 52 | 15 | 5 | 1 |

No specification showed a raw keyword count materially inconsistent with
its extracted requirement count (e.g. an order-of-magnitude mismatch that
would suggest mass omission or mass duplication). MCC-CP-001's very high
raw SHALL count (337) against 340 extracted requirements is consistent with
that specification's own writing style (heavy per-clause SHALL repetition
in Requirement Classification / Certification Result / State Machine
sections) rather than evidence of under- or over-extraction.

### From-scratch per-section completeness check (the actual Wave-1-class regression guard)

`test_every_h1_section_with_a_binding_keyword_yields_at_least_one_requirement`
independently re-walks all four raw specification files line by line (not
calling into `extract.py`'s own captured-line bookkeeping) and asserts:
for every H1 section containing at least one MUST/MUST NOT/SHALL/SHALL
NOT/REQUIRED-bearing, non-structural line, the registry contains at least
one requirement whose `(specification_id, requirement_category)` matches
that section.

**Result: zero sections failed this check.** Every section with a binding
obligation is represented in the registry.

## Genuine findings

Four real, concrete issues were found and corrected; nothing else required
a code or data change.

### 1. Wave C evidence generator used bare test names, not pytest node ids (fixed)

`conformance/normative-v1.0/remediation/generate_wave_c_evidence.py`'s
`META` dict listed `proving_tests` as bare function names (e.g.
`"test_tc_model_001_certificate_represents_exactly_one_pass_outcome"`),
unlike Wave A's and Wave B's own evidence generators, which use
fully-qualified `path/to/test_file.py::test_name` pytest node ids. This
meant `wave-c-evidence.json`'s 92 `proving_tests` entries could not be
mechanically resolved to a real test function — exactly the "test nodes
exist" check Part C of this audit asks for. Fixed by qualifying every
entry with its file path at generation time; `wave-c-evidence.json`
regenerated (byte-identical output confirmed reproducible). See
`src/mcc_conformance/validate.py:validate_evidence_test_nodes` (new) and
`tests/test_normative_coverage_reconciliation.py::test_validate_evidence_test_nodes_passes_on_the_real_committed_evidence`.

### 2. `traceability_matrix.md`'s "Limitations of This Assessment" section contained stale, now-false prose (fixed)

`generate.py`'s `_matrix_md` hardcoded, from the Wave-0-era baseline before
any remediation wave existed: *"No requirement is marked CONFORMANT in this
baseline... no code in this repository implements the Evidence Bundle,
Certification Manifest, Technical Certificate, or Certification Program
process"* and *"This assessment does not execute or validate any generated
Evidence Bundle, Manifest, or Certificate, because none exist to
generate."* Both claims are now demonstrably false: 91 requirements are
CONFORMANT, and their tests build, sign, and verify real Evidence Bundles,
Certification Manifests, and Technical Certificates end to end (Waves
A/B/C). Fixed: the CONFORMANT-count bullet and the "does not execute"
bullet are now generated dynamically from the actual current status counts
and correctly describe what the referenced tests do, instead of a
hand-written sentence frozen at Wave-0.

### 3. `src/mcc_conformance/validate.py` did not require `evidence_references` for CONFORMANT (fixed)

The structural validator required `implementation_references` and
`test_references` for a `CONFORMANT` requirement, but not
`evidence_references` — even though every requirement Waves A/B/C actually
promoted already carries one via `assess.py`'s `ID_OVERRIDES` mechanism (a
4-tuple that always includes an evidence-file list). This was a latent gap:
nothing would have stopped a future promotion from omitting a deterministic
evidence record while still passing validation. Verified before tightening
that all 91 real CONFORMANT requirements already have a non-empty
`evidence_references` (zero regressions from the stricter check); fixed the
validator and updated the one pre-existing fixture test that exercised the
old, looser contract
(`tests/test_conformance_baseline.py::test_conformant_with_both_references_passes`
→ split into `test_conformant_without_evidence_reference_is_rejected` +
`test_conformant_with_all_three_references_passes`).

### 4. A dead, vestigial variable in `extract.py`'s Pass 2 (cleaned, no functional effect)

`covered_h1 = {h1 for (_, _, h1, _) in canonical}` was computed but never
read anywhere in the function — a leftover from (most plausibly) the
pre-PR#62 version of this code, where an equivalent set was presumably used
to *skip* Pass 2 for canonical-ID-bearing sections (the exact defect PR #62
fixed). Its presence, unused, was a landmine: a future refactor could
plausibly wire it back in without realizing Pass 2 already correctly runs
unconditionally over every H1 section. Removed the dead line and replaced
it with an explicit comment stating the invariant it must never violate.
This is a pure readability/maintenance fix; `extract_all()`'s output is
byte-identical before and after (confirmed by re-running the full
determinism/regression suite).

## Requirements found: missing / duplicate / orphaned — final tally

| Check | Result |
|---|---|
| Missing normative requirements (H1 sections with a binding obligation and zero registry requirements) | **0** |
| Duplicate `requirement_id` values (global, across all 4 specs) | **0** |
| Duplicate normalized requirement text within the same `(specification_id, requirement_category)` | **0** |
| Orphaned registry entries (registered requirement with no real source line / file) | **0** |
| Canonical-ID short-prefix collisions across specifications (e.g. `CM-` claimed by two specs) | **0** |
| Derived requirement IDs not prefixed by their own `specification_id` | **0** |
| Wave evidence records citing a `requirement_id` absent from the registry | **0** |
| CONFORMANT requirements whose cited evidence file has no matching record | **0** |
| Requirement-ID migrations needed | **0 — no migration map produced; none was required** |

No normative requirement was found missing, duplicated, or orphaned in the
real corpus. No requirement ID needed to change.

## Cross-specification traceability

- `assess.py`'s rule table (`RULES`) is scoped per-entry to either an exact
  `specification_id` or the explicit cross-cutting `"*"` sentinel (used only
  for the Extension Model rule, which is intentionally identical across all
  four specifications) — verified directly
  (`test_category_names_shared_across_specifications_do_not_cause_rule_collisions`).
  Several category *names* are legitimately shared across specifications
  (e.g. "6. Required Fields" exists in MCC-EB-001, MCC-CM-001, and
  MCC-TC-001 alike, each with its own distinct normative content) — this
  was already handled correctly by construction (matching is `(spec_id,
  category)`, never bare `category`), so no cross-spec category collision
  was found or needed fixing.
- Every promoted `ID_OVERRIDES` entry is keyed by the exact, globally-unique
  `requirement_id` string, never a category — so Technical Certificate
  evidence can never be silently reused as Certification Manifest evidence
  or vice versa; verified by the bidirectional evidence-linkage checks
  above (finding: 0 mismatches, 0 orphans).
- No circular or dangling `dependencies` field was found in any wave scope
  manifest (Waves A/B/C's own `dependencies` arrays reference only
  requirement IDs that exist and were resolved before the dependent
  requirement, matching the documented wave order A → B → C).

## Unresolved ambiguities

None found that required stopping. The normative/non-normative boundary,
while a documented and disclosed methodology choice (category-level
assessment granularity, per `assess.py`'s own docstring since its original
authoring), was re-verified against the actual current specification text
in this PR and found internally consistent — no case was found where the
boundary rule produced a result this audit considered indefensible.

## Reproduction

```bash
PYTHONPATH=src python3 -m mcc_conformance generate
PYTHONPATH=src python3 -m mcc_conformance validate
PYTHONPATH=src python3 -m pytest tests/test_normative_coverage_reconciliation.py tests/test_conformance_baseline.py tests/test_conformance_extraction_correction.py -v
PYTHONPATH=src python3 -m pytest tests/ -q
```
