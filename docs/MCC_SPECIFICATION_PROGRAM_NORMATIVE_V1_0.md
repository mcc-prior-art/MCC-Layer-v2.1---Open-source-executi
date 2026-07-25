# MCC Specification Program — Normative v1.0 Declaration

Status: **Normative v1.0**

Document Type: Program Declaration Record

Applies To: The complete MCC Specification Program baseline

---

## 1. Declaration

This document formally declares the MCC Specification Program baseline described below as:

> **MCC Specification Program — Normative v1.0**

This is the first version of the MCC Specification Program to carry Normative status. All four constituent specifications are promoted from Draft to Normative as of this declaration.

---

## 2. Basis of Approval

This declaration is issued on the basis of the Final Normative Acceptance Review recorded at:

- `docs/reviews/MCC_SPECIFICATION_PROGRAM_NORMATIVE_V1_REVIEW.md`

Reviewed Baseline Commit:

- `7a2c69f6c9f0a87a59c53a0dbd970ba5a7cab31f`

Approval Disposition (as recorded in the review):

> **APPROVE FOR NORMATIVE v1.0**

The review found no BLOCKING findings across the four-specification package as of the reviewed commit. Its recorded NON-BLOCKING and EDITORIAL findings remain open as future-revision items and do not affect the validity of this declaration; they are enumerated in full in the review record referenced above, not restated here.

---

## 3. Specifications Covered

This declaration applies to exactly the following four specifications, each now carrying `Version: 1.0` and `Status: Normative` in its own document metadata:

| Document ID | Title | File |
|---|---|---|
| MCC-CP-001 | Official Certification Program Specification | `specs/MCC-CP-001.md` |
| MCC-EB-001 | Evidence Bundle Specification | `specs/MCC-EB-001.md` |
| MCC-CM-001 | Certification Manifest Specification | `specs/MCC-CM-001.md` |
| MCC-TC-001 | Technical Certificate Specification | `specs/MCC-TC-001.md` |

No other document is covered by this declaration. In particular, `docs/reviews/*` review records and this declaration itself are program governance artifacts, not normative specifications.

---

## 4. Scope and Compatibility Statement

- This declaration governs the specification text as it exists at the reviewed baseline commit plus the metadata-only changes (Version and Status fields) applied to promote the four documents to Normative v1.0. No normative requirement text, requirement identifier, or cross-specification reference was altered by this declaration.
- The four specifications' independent versioning model is unchanged by this declaration: the MCC-CP-001 specification version, the Evidence Bundle Schema Version (MCC-EB-001), the Manifest Schema Version (MCC-CM-001), and the Certificate Schema Version (MCC-TC-001) remain distinct, independently tracked identifiers, as defined within each respective document. Promotion to Normative v1.0 does not merge or conflate these version axes.
- Future revisions to any of the four specifications SHALL follow the versioning, compatibility, and breaking-change rules already defined within each specification (MCC-CP-001 §17; MCC-EB-001 §17–§18; MCC-CM-001 §16–§17; MCC-TC-001 §18, §17). A future breaking revision to any one document requires a new Schema Version (or specification version) under those existing rules; it does not by itself revoke this Normative v1.0 declaration for the other three documents.
- This declaration does not itself introduce, alter, or authorize any runtime governance behavior. The MCC Specification Program governs certification-program artifacts (Evidence Bundle, Certification Manifest, Technical Certificate) exclusively; it remains fully separate from MCC-Core runtime governance (ALLOW, DENY, ESCALATE, CONSTRAIN), consistent with the boundary defined throughout the four specifications.
- Known NON-BLOCKING and EDITORIAL findings recorded in the Final Normative Acceptance Review remain candidates for a future non-breaking revision and do not constitute open normative ambiguity within the v1.0 baseline.

---

## 5. Record

| Field | Value |
|---|---|
| Declared status | Normative v1.0 |
| Approval review | `docs/reviews/MCC_SPECIFICATION_PROGRAM_NORMATIVE_V1_REVIEW.md` |
| Reviewed baseline commit | `7a2c69f6c9f0a87a59c53a0dbd970ba5a7cab31f` |
| Approval disposition | APPROVE FOR NORMATIVE v1.0 |
| Specifications declared Normative v1.0 | MCC-CP-001, MCC-EB-001, MCC-CM-001, MCC-TC-001 |
