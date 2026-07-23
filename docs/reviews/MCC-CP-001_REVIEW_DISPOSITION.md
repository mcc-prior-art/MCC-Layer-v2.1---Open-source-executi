# MCC-CP-001 — Review Disposition

Source Review: `docs/reviews/MCC-CP-001_DRAFT_REVIEW.md`

Reviewed Document: `specs/MCC-CP-001.md`

Disposition Type: Read-only analysis. No specification file was modified to produce this document.

Classification Legend:

- **Accepted** — the finding is valid and describes a defect that should be corrected in a future editorial revision of `specs/MCC-CP-001.md`. Low-judgment, mechanical, or additive fixes.
- **Rejected** — the finding does not describe a defect; the current text is intentional, consistent, or a legitimate specification pattern, and no change is warranted.
- **Future work** — the finding is valid but requires an architectural decision beyond editorial correction (author judgment, not implementation-editor judgment), and/or is properly scoped to a specification that has not yet been written (`MCC-EB-001`, `MCC-CM-001`, `MCC-TC-001`, or a later MCC-CP-001 revision).

---

## 1. Internal Inconsistencies

### 1.1 Version identifier mismatch (front matter `Draft v0.1` vs. Appendix D.2 `Draft v1`)

**Classification: Accepted**

Rationale: A single document cannot carry two version identifiers for what is presented as one release. This is a factual, mechanical defect with one correct fix (pick one version string and status label and apply it in both places). It requires no architectural judgment, only confirmation of which value is intended.

### 1.2 Document Roadmap placement (between Section 9 and Section 10)

**Classification: Accepted**

Rationale: The roadmap's position mid-document is a pure organizational/formatting issue. It does not alter normative meaning, and relocating it (to follow the Abstract, or to a trailing appendix) is a safe, non-substantive fix. Accepted as a housekeeping item, not a blocking one.

### 1.3 Requirement Classification defined in two places (Section 10.3 and Section 13)

**Classification: Rejected**

Rationale: Comparing the two sections directly, they are not duplicates — Section 10.3 introduces REQUIRED/OPTIONAL/CONDITIONAL as part of the Conformance Model overview, while Section 13 gives each category its own subsection with additional normative detail not present in 10.3 (e.g., 13.2's "multiple classifications SHALL NOT be permitted," 13.3's explicit certification-blocking consequence, 13.5's NOT APPLICABLE outcome rule). This is a legitimate specification pattern — introduce a concept where first needed, then give it a full normative treatment in a dedicated section — and the two sections are consistent with each other. No contradiction exists. Rejected as a defect; a cross-reference between the two (e.g., "see Section 13 for full classification rules") would be a reasonable optional polish but is not required.

### 1.4 Revalidation defined in two places (Section 8.9 and Section 17.4)

**Classification: Rejected**

Rationale: Section 8.9 addresses revalidation as a lifecycle step (procedural: certification may be repeated). Section 17.4 addresses it as a versioning concern (policy: revalidation against newer specification versions, preservation of prior results). These are two different normative angles on the same activity, not a restatement of identical content, and they do not conflict. This is consistent with the document's own structure, which separates Lifecycle (Section 8) from Versioning (Section 17) as distinct concerns. No change required.

### 1.5 "Certification governance" named in Scope (Section 1) with no corresponding section

**Classification: Future work**

Rationale: This is a real content gap, but closing it requires deciding what "certification governance" normatively means for this program (oversight of the Certification Authority, appeals process, conflict of interest rules, etc.) — that is an architectural decision, not an editorial one. Deferred pending AX's decision on whether to add a dedicated Governance section in a future revision or narrow the Section 1 scope bullet to match what is actually specified today.

---

## 2. Duplicate Requirement Identifiers

### 2.1 `CONF-001`–`CONF-007` defined twice with different text (Section 10.6 vs. Section 20.3)

**Classification: Accepted — blocking**

Rationale: This is not a matter of interpretation. Appendix C.4 (`RID-001`) states requirement identifiers "SHALL be globally unique," and the document violates its own invariant with two fully-populated, differently-worded `CONF-` blocks. This is a mechanical, unambiguous defect (not an architecture question) — the fix is to rename one block's prefix (the reviewer's suggestion of `CSTMT-` for Section 20 is reasonable) — but it must be corrected before the document can claim internal consistency. This finding blocks unconditional baseline sign-off (see Section 4 of this disposition).

---

## 3. Cross-Section Contradictions

### 3.1 Certification decision outcomes: binary (Sections 8, 9) vs. four-outcome (Appendix B)

**Classification: Future work — blocking**

Rationale: This is the most significant finding in the review. It is not an editorial slip — it is two incompatible normative models for what a certification decision *is*. Sections 8.6 and 9.6 define exactly two outcomes (`CERTIFIED` / `NOT CERTIFIED`); Appendix B.2 defines four (`Certified`, `Certified with Conditions`, `Rejected`, `Revoked`), with different casing and two labels absent from the main body. Choosing between these models — or defining how they relate — is an architectural decision that determines core certification semantics (notably, whether "Certified with Conditions" is a real outcome tied to CONDITIONAL requirements, and whether revocation is part of the decision model or a separate post-issuance lifecycle event). This is squarely outside implementation-editor authority and must be resolved by AX before the decision model can be considered normative. This finding blocks unconditional baseline sign-off.

### 3.2 `Revoked` / revocation used before being defined

**Classification: Future work**

Rationale: Directly dependent on 3.1 — revocation cannot be properly defined (grounds, authority, procedure) until the decision-outcome model itself is settled. A minimal fix (adding "Revocation" as a defined term in Section 4) could be done independently, but the substantive procedure likely belongs with whichever artifact is actually revoked in practice — most plausibly the Technical Certificate, i.e., `MCC-TC-001` — rather than in MCC-CP-001's core lifecycle. Deferred pending 3.1's resolution and the eventual authoring of `MCC-TC-001`.

### 3.3 `Certified with Conditions` has no defined relationship to CONDITIONAL requirements

**Classification: Future work**

Rationale: Same family as 3.1/3.2. Whether this outcome is mechanically derived from CONDITIONAL requirement results, or is an independent concept that happens to share vocabulary, is an architectural question to be settled alongside 3.1.

### 3.4 Section 21.2 references external specs (`MCC-EB-001`, `MCC-CM-001`, `MCC-TC-001`) while Sections 14–16 already define that content internally

**Classification: Future work**

Rationale: This is not a defect to be fixed by editing MCC-CP-001 today — it is the expected, transitional state of a specification-first process where MCC-CP-001 was drafted first and the referenced companion specifications do not yet exist. Sections 14–16 are read as the authoritative source for Evidence, Manifest, and Certificate requirements *for as long as* `MCC-EB-001`/`MCC-CM-001`/`MCC-TC-001` remain unwritten. Once each companion specification is authored, a subsequent MCC-CP-001 revision should extract the corresponding section(s) and convert Section 21.2's references from aspirational to substantive. No action against MCC-CP-001 is needed until that point.

---

## 4. Sections That Should Potentially Move

### 4.1–4.3 Sections 14, 15, 16 → `MCC-EB-001`, `MCC-CM-001`, `MCC-TC-001` respectively

**Classification: Future work**

Rationale: Same reasoning as 3.4. These extractions are the natural, expected work of the *next* specifications in the roadmap, not a correction owed to MCC-CP-001 itself. Extraction is deferred until each companion specification begins.

### 4.4 Appendix C (Requirement Identifier Registry) → possible shared cross-specification registry document

**Classification: Future work**

Rationale: A shared registry only becomes necessary once more than one specification exists and needs a common identifier namespace. With only MCC-CP-001 currently drafted, relocating Appendix C now would be premature. Revisit once `MCC-EB-001`, `MCC-CM-001`, and `MCC-TC-001` exist and their identifier prefixes need to be reconciled against MCC-CP-001's (this is also the natural place to close out the 2.1 collision permanently, via a documented namespace-allocation convention).

### 4.5 Appendix D (Revision History) → possible unnumbered front/back matter

**Classification: Rejected**

Rationale: Keeping revision history as a lettered, numbered appendix alongside other technical appendices is a common and acceptable specification convention (e.g., IETF/W3C-style documents routinely do this). It introduces no ambiguity, no normative conflict, and no reader confusion. This is a stylistic preference with no defect underlying it — no change warranted.

---

## 5. Missing Normative References

### 5.1 RFC 2119 / RFC 8174 not listed in Section 21.2

**Classification: Accepted**

Rationale: The document invokes RFC 2119/8174 by name as the interpretive authority for every normative keyword in the document (Status section, Section 5), so omitting them from the Normative References list is an internal completeness gap, not a judgment call. Purely additive fix — add both as normative references.

### 5.2 `MCC-EB-001`, `MCC-CM-001`, `MCC-TC-001` listed without titles/descriptions

**Classification: Accepted**

Rationale: Purely additive — add a one-line title/scope description for each referenced identifier. No architectural judgment required, and doing so does not commit the author to anything not already implied by Sections 14–16.

### 5.3 No normative reference for a Capability Profile specification

**Classification: Future work**

Rationale: Unlike Evidence/Manifest/Certificate, there is no existing signal (elsewhere in the document) that Capability Profiles are intended to be split into their own specification. Whether Section 11 remains permanently part of MCC-CP-001 or is eventually extracted into an `MCC-xx-001`-style document is an open architectural question for AX, not something to be decided or assumed here.

### 5.4 No reference addressing "certification governance"

**Classification: Future work**

Rationale: Directly tied to 1.5 — cannot cite a governance reference for a concept that is not yet defined anywhere in the MCC specification set. Deferred to the same future decision.

---

## 6. Suggested Editorial Improvements (Section 6 of the source review)

Each item in the source review's Section 6 restates a fix for a finding already classified above. No new findings are introduced by Section 6; dispositions are inherited from the corresponding item:

| Section 6 suggestion | Inherited from | Disposition |
|---|---|---|
| Reconcile version identifiers | 1.1 | Accepted |
| Relocate Document Roadmap | 1.2 | Accepted |
| Merge/cross-reference 10.3 and 13 | 1.3 | Rejected |
| Merge/cross-reference 8.9 and 17.4 | 1.4 | Rejected |
| Resolve CONF- identifier collision | 2.1 | Accepted — blocking |
| Reconcile decision-outcome model | 3.1 | Future work — blocking |
| Define Revocation/Revoked/Certified with Conditions | 3.2, 3.3 | Future work |
| Add titles for MCC-EB-001/CM-001/TC-001 | 5.2 | Accepted |
| State identifier-namespace convention in Appendix C | 4.4 | Future work |

---

## 7. Baseline Readiness Determination

**MCC-CP-001 Draft v1 is NOT YET ready to become the unconditional normative baseline.**

Two findings are classified above as **blocking**:

1. **Finding 2.1** — the `CONF-001`–`CONF-007` identifier collision, which violates the document's own uniqueness invariant (Appendix C, `RID-001`). This is a mechanical defect with a clear, low-risk fix, but it has not yet been made (per this task's instruction not to modify the specification).
2. **Finding 3.1** — the unresolved contradiction between the binary (`CERTIFIED`/`NOT CERTIFIED`) and four-outcome (`Certified`/`Certified with Conditions`/`Rejected`/`Revoked`) certification decision models. This is a substantive architectural question — not an editorial one — and it must be resolved by AX before the certification decision model can be considered singular and normative. Findings 3.2 and 3.3 are downstream of this same open question.

All other findings are either **Rejected** (no defect exists) or **Future work** properly scoped to later specifications (`MCC-EB-001`, `MCC-CM-001`, `MCC-TC-001`) or a later MCC-CP-001 revision, and do not block baseline status on their own.

**Conclusion:** Because mandatory normative changes remain outstanding (Findings 2.1 and 3.1 above), MCC-CP-001 is **not** being declared approved for completion at this time, and the next specification (`MCC-EB-001`) is **not** yet being opened. Recommended next step: obtain AX's decision on the certification-decision model (Finding 3.1), then perform a single corrective editorial revision to MCC-CP-001 addressing Findings 1.1, 1.2, 2.1, 3.1–3.3, 5.1, and 5.2 before requesting re-review for baseline sign-off.
