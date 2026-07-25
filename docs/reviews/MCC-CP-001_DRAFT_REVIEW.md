# MCC-CP-001 — Draft Architectural Review

Reviewed Document: `specs/MCC-CP-001.md`

Reviewed State: First complete draft (Sections 1–21, Appendices A–F)

Review Type: Read-only architectural review

Status: Informative — this document is not normative and does not modify `specs/MCC-CP-001.md`

---

## 1. Internal Inconsistencies

- **Version identifier mismatch.** The front matter (lines 5–9) declares `Document ID: MCC-CP-001`, `Version: Draft v0.1`, `Status: Draft`. Appendix D.2 ("Initial Release", line 1799–1803) declares `Version: Draft v1`, `Status: Initial Public Draft`. The document carries two different version strings and two different status labels for what appears to be the same release.

- **Document Roadmap placement.** The "Document Roadmap" section (lines 582–648) is inserted between Section 9 (Certification Pipeline) and Section 10 (Conformance Model), rather than near the front matter/Abstract or as a trailing appendix. This breaks the numbered-section reading order and makes the roadmap easy to miss.

- **Requirement Classification defined twice, in two places, at two different depths.** Section 10.3 "Requirement Classification" (lines 680–692, embedded within the Conformance Model) already defines REQUIRED / OPTIONAL / CONDITIONAL with normative rules. Section 13 "Requirement Classification" (lines 959–1037) re-defines the same three categories as a full standalone section with its own invariant block (CLASS-001..007). The two are consistent in substance but the duplication of both the concept and its title across two section numbers is a structural inconsistency.

- **Revalidation defined twice.** Section 8.9 "Revalidation" (lines 419–425) and Section 17.4 "Certification Revalidation" (lines 1336–1342) both state that certification may be repeated, that revalidation references the specification version, and that it produces a new result. The two sections do not contradict each other but cover the same ground under different numbers without cross-reference.

- **Scope item without corresponding content.** Section 1 (line 52) lists "certification governance" as within scope, but no section or appendix defines certification governance (e.g., how the Certification Authority itself is governed, appeals, oversight). Section 7.1 defines the Authority's responsibilities but not its own governance.

---

## 2. Duplicate Requirement Identifiers

- **`CONF-001` through `CONF-007` are defined twice with different normative text:**
  - Section 10.6 "Conformance Invariants" (lines 720–746) — e.g. `CONF-001`: "Conformance evaluates requirements."
  - Section 20.3 "Conformance Invariants" (lines 1514–1540) — e.g. `CONF-001`: "Conformance SHALL be evidence-based."

  Every identifier in the range CONF-001–CONF-007 collides between these two sections, each with distinct wording. Per Appendix C.4 (RID-001), "Requirement identifiers SHALL be globally unique" — this is a direct violation of the document's own registry invariant, using identifiers minted before Appendix C existed.

- No other identifier prefix (CI-, CP-PIPE-, CAP-, REQ-, CLASS-, EVID-, MAN-, CERT-, VER-, SEC-, REG-, REF-, STATE-, DEC-, RID-, REV-, EX-, EXT-) was found reused elsewhere in the document.

---

## 3. Cross-Section Contradictions

- **Certification decision outcomes are modeled two different ways.**
  - Section 8.6 (lines 383–392) and Section 9.6 (lines 511–520) both state certification produces exactly one of two outcomes: `CERTIFIED` / `NOT CERTIFIED`.
  - Appendix B.2 (lines 1678–1687) states the certification authority "MAY produce only one of the following outcomes": `Certified`, `Certified with Conditions`, `Rejected`, `Revoked` — four outcomes, different casing, and two labels (`Certified with Conditions`, `Revoked`) that do not appear anywhere in Sections 8 or 9.

  These are not reconcilable as written: the main-body lifecycle and pipeline sections describe a binary decision, while the appendix decision matrix describes a four-way decision. It is not specified which model is authoritative.

- **`Revoked` / revocation is used before it is defined.**
  - Appendix A.2 (line 1625) lists `Revoked` as a certification state, and A.4 STATE-005 (line 1656–1658) requires revoked certifications to preserve historical evidence.
  - Appendix B.2 lists `Revoked` as a decision outcome.
  - No section in the normative body (1–21) defines what revocation is, who may invoke it, on what grounds, or how it relates to the Section 8/9 CERTIFIED/NOT CERTIFIED model. Section 4 Terminology does not define "Revocation" or "Revoked."

- **`Certified with Conditions` has no defined relationship to CONDITIONAL requirements.** Sections 10.3/13 define a `CONDITIONAL` requirement classification, and Appendix B.2 introduces a `Certified with Conditions` outcome. The document never states whether these are related concepts (e.g., a certificate is "with conditions" when CONDITIONAL requirements evaluate a certain way) or are independent, coincidentally similarly-named ideas.

- **Section 21.2 treats Evidence Bundle, Certification Manifest, and Technical Certificate as governed by separate external specifications** (`MCC-EB-001`, `MCC-CM-001`, `MCC-TC-001`), while Sections 14, 15, and 16 of this same document already define normative requirements for exactly those three artifacts. The document does not state whether Sections 14–16 are the authoritative source (making the external references informative pointers) or temporary placeholders pending extraction (making Sections 14–16 provisional). See Section 4 below.

---

## 4. Sections That Should Potentially Move

- **Section 14 (Evidence Requirements) → candidate for `MCC-EB-001`.** Section 4 already defines "Evidence Bundle" as a distinct term, and Section 21.2 already lists `MCC-EB-001` as a normative reference, implying a dedicated Evidence Bundle specification is expected to exist.

- **Section 15 (Certification Manifest Requirements) → candidate for `MCC-CM-001`**, for the same reason (Section 21.2 already names `MCC-CM-001`).

- **Section 16 (Technical Certificate Requirements) → candidate for `MCC-TC-001`**, for the same reason (Section 21.2 already names `MCC-TC-001`).

- **Appendix C (Requirement Identifier Registry)** is a cross-cutting identifier-namespace concern rather than something specific to certification requirements alone (it would also need to cover Evidence, Manifest, and Certificate identifiers once those move out). It may belong alongside Section 19 (Registry Considerations) or in a shared cross-specification registry document rather than as a certification-program-specific appendix.

- **Appendix D (Revision History)** is document-control metadata rather than a normative technical appendix. Depending on the documentation program's conventions, this is sometimes kept out of the numbered Appendix sequence (e.g., as unnumbered front/back matter) rather than alongside technical appendices like the State Machine or Decision Matrix.

---

## 5. Missing Normative References

- **RFC 2119 / RFC 8174 are not listed in Section 21.2 Normative References**, despite being invoked as the interpretive authority for all normative keywords in the "Status of This Specification" section (line 23) and Section 5 (line 140). Every other document this specification depends on for meaning should logically appear in the references list.

- **`MCC-EB-001`, `MCC-CM-001`, `MCC-TC-001` are listed but never described.** Section 21.2 gives no titles, scope, or version for these three referenced specifications — only their identifiers. A reader cannot tell what these documents cover without inferring it from Sections 14–16 of this document.

- **No reference to a Capability Profile specification.** Section 11 defines Capability Profiles at length, but unlike Evidence/Manifest/Certificate, no corresponding `MCC-xx-001`-style normative reference exists for capability profiles, despite the parallel structure (Section 11 vs. Sections 14–16) suggesting one might eventually be needed.

- **No reference addressing "certification governance"** (named in-scope in Section 1) — no governance specification is cited, and none is defined in this document either.

---

## 6. Suggested Editorial Improvements

*(Non-normative suggestions only — no changes have been made to the specification.)*

- Reconcile the two version identifiers (front matter `Draft v0.1` vs. Appendix D.2 `Draft v1`) to a single value.
- Relocate "Document Roadmap" to immediately follow the Abstract, or move it to a trailing appendix, so the numbered-section sequence (1 → 21) reads without interruption.
- Merge or explicitly cross-reference Section 10.3 and Section 13 (both titled around "Requirement Classification") to avoid defining the same taxonomy twice.
- Merge or explicitly cross-reference Section 8.9 and Section 17.4 (both covering revalidation).
- Resolve the CONF-001–007 identifier collision between Section 10.6 and Section 20.3 by renumbering one set (e.g., retitle Section 20's block under a distinct prefix such as `CSTMT-`).
- Reconcile the certification-decision model: pick either the binary CERTIFIED/NOT CERTIFIED model (Sections 8, 9) or the four-outcome model (Appendix B), and update the other to match — including standardizing casing (`CERTIFIED` vs. `Certified`).
- Add "Revocation," "Revoked," and "Certified with Conditions" as defined terms in Section 4 Terminology, since they are used substantively in the appendices without being introduced in the main body.
- Add titles/short descriptions for `MCC-EB-001`, `MCC-CM-001`, and `MCC-TC-001` in Section 21.2, and state explicitly whether Sections 14–16 are authoritative-in-place or provisional pending extraction.
- Consider a stated identifier-namespace convention in Appendix C (e.g., "no two sections may reuse a requirement-ID prefix") to prevent future collisions like the CONF- duplication.
