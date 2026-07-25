# MCC Specification Program — Final Normative Acceptance Review

Review Type: Final Normative Acceptance Review (read-only)

Reviewed Commit: `7a2c69f6c9f0a87a59c53a0dbd970ba5a7cab31f` (`origin/main`)

Files Reviewed:

- `specs/MCC-CP-001.md` — Official Certification Program Specification
- `specs/MCC-EB-001.md` — Evidence Bundle Specification
- `specs/MCC-CM-001.md` — Certification Manifest Specification
- `specs/MCC-TC-001.md` — Technical Certificate Specification

Reference Records Inspected:

- `docs/reviews/MCC-CP-001_DRAFT_REVIEW.md`
- `docs/reviews/MCC-CP-001_REVIEW_DISPOSITION.md`

Status: This document is a review record. It does not modify, and is not itself, a normative specification.

---

## Final Disposition

> **APPROVE FOR NORMATIVE v1.0**

The single BLOCKING finding carried by every prior review in this program — the mandatory, wholly undefined "Certification Report" output in `MCC-CP-001` §7.4/§9.7 — has been closed by the addition of Appendix G (Conformance Result Requirements) and Appendix H (Certification Report Requirements), merged to `main` in PR #57. No BLOCKING findings remain across the four-document package as of the reviewed commit.

---

## 1. Normative Completeness

Every artifact, process, state transition, verification procedure, conformance obligation, and certification output named across the four documents is now either normatively defined in the package or explicitly and unambiguously scoped away.

| Item | Status | Where defined |
|---|---|---|
| Certification Process (model, lifecycle, pipeline) | Defined | CP-001 §7, §8, §9 |
| Evidence Bundle | Defined | EB-001 (full document) |
| Certification Manifest | Defined | CM-001 (full document) |
| Technical Certificate | Defined | TC-001 (full document) |
| Conformance Result | Defined | CP-001 Appendix G — defined as content carried by the Certification Manifest (not a separate artifact), consistent with CP-001 §15.2 and CM-001 |
| Certification Report | Defined | CP-001 Appendix H — required minimum content, human-readability requirement, explicit non-authoritative status, applicability limited to successful certification; serialization format explicitly and appropriately left open pending a future specification |
| Certification lifecycle / state transitions | Defined | CP-001 §8 (Lifecycle), §9 (Pipeline), Appendix A (State Machine) |
| Revocation | Defined | TC-001 §12 (certificate-level: immutable content, external Revocation Record, mandatory verifier check); CP-001 Appendix A names the "Revoked" state that TC-001 operationalizes |
| Compatibility | Defined | EB-001 §18, CM-001 §17, TC-001 §17 — independently versioned with an explicit TC→CM→EB compatibility chain |
| Issuance obligations | Defined | TC-001 §21.2 (issuer), including the Evidence Bundle/Manifest consistency obligation added in the prior corrective revision |
| Verification obligations | Defined | TC-001 §15, §21.3 — fail-closed, covers structure, signature, manifest reference, evidence bundle consistency, subject/result consistency, validity, revocation |

**All five outputs named in CP-001 §7.4 ("Every successful certification SHALL produce: ...") now have a normative home.** This closes the completeness gap identified in every prior review of this program.

Residual, non-blocking completeness observations (see §7 below for full disposition):

- "Normative test vectors," named repeatedly in CP-001 (§7.3, §8.2, §9.2) as a certification *input*, remain undefined. This is a disjunctive, optional-among-several input category (not an unconditional mandatory output like Conformance Result/Certification Report were), and it affects only CP-001's own future Certification Suite tooling — not the implementability of Evidence Bundle, Manifest, or Certificate generators/verifiers.
- CP-001's Lifecycle (§8), Pipeline (§9), and State Machine (Appendix A) remain three parallel, not formally cross-mapped, descriptions of "what happens during certification." In practice this does not block implementation: all three downstream specs consistently anchor their normative cross-references to the Pipeline (§9) alone.

---

## 2. Normative Language

RFC 2119 / RFC 8174 usage (MUST, MUST NOT, SHALL, SHALL NOT, SHOULD, SHOULD NOT, MAY, RECOMMENDED) was reviewed across all four documents, including the newly added Appendix G/H.

- **No stray lowercase normative keywords** were found anywhere in the four-document corpus (verified by full-text scan).
- The large majority of MUST/SHALL statements name a responsible actor (issuer, verifier, validator, or the artifact itself as the subject of a structural constraint) and a testable consequence.
- Appendix G/H follow the same pattern as the rest of CP-001: producer identity is stated through prohibition/context rather than an affirmative "the certification implementation SHALL produce..." sentence (e.g. Appendix G.3: *"A certification implementation MUST NOT produce a Conformance Result as a document distinct from the Certification Manifest"*). This is consistent with CP-001's pre-existing style for Evidence Bundle (§14), Certification Manifest (§15), and Technical Certificate (§16) requirements, none of which name an affirmative producer either — so this is a house-style characteristic of CP-001, not a defect introduced by, or unique to, the new appendices.
- Certification Report (Appendix H) states producer-side content and consistency obligations (H.2, H.3, CREP-005) but does not state an explicit consumer-side rejection rule (no "MUST be rejected" / "MUST NOT be treated as valid" for a non-conforming Report), unlike the dedicated Validation Rules (EB-001 §16), Validation Rules (CM-001 §18), and Verification Procedure (TC-001 §15) sections for the other three artifacts. This is judged non-blocking: the Report is explicitly declared non-authoritative (H.3, CREP-004) and its serialization format is explicitly deferred to a future specification (H.4), so no downstream verification procedure currently depends on rejecting a malformed Report the way certification validity depends on rejecting a malformed Bundle, Manifest, or Certificate.
- No internally contradictory requirements were found in this pass.

---

## 3. Implementability

An independent implementation team can build, from the current four-document package alone and without undocumented architectural decisions:

- a conforming **Evidence Bundle generator** (EB-001 §10–§18);
- a conforming **Certification Manifest generator** (CM-001 §10–§18);
- a conforming **Technical Certificate issuer** (TC-001 §4–§14, §21.2), including the direct Evidence Bundle Reference and issuer-side consistency check added in the prior corrective revision;
- an independent **offline verifier** (TC-001 §15, cross-calling CM-001 §18 and EB-001 §16 as specified);
- a **Certification Report producer**, satisfying Appendix H's minimum content and consistency rules, in a serialization format of the implementer's choosing (explicitly permitted pending a future format specification).

A full **Certification Suite** implementing CP-001 §9's Pipeline end-to-end is implementable for Stages 1–6 and for the Manifest/Certificate/Report artifact-generation obligations of Stage 7. It remains **not fully implementable** with respect to the "normative test vectors" referenced as a certification input in §7.3/§8.2/§9.2 (still undefined) — an implementer building the meta-level suite that certifies *other implementations* against these specifications would need to define that input category itself, absent further specification. This does not affect the implementability of the four core artifact types themselves.

---

## 4. Conformance and Testability

Artifact-level requirements across EB-001, CM-001, and TC-001 map cleanly to reproducible, observable pass/fail conformance tests, including negative-test obligations (tamper, mismatch, expiry, revocation, unrecognized schema version, missing required field) and fail-closed behavior, each stated explicitly in the respective Validation Rules / Verification Procedure sections.

Program-level testability (CP-001) is now materially improved by Appendix G/H:

- **Conformance Result** is fully testable — it reduces to validating the existing, already-testable Certification Manifest fields (CM-001 §11.3, §18), so no new test surface was introduced; the ambiguity is closed by definition rather than by new machinery.
- **Certification Report** has an observable minimum-content check (H.2's six required items) and an observable consistency check (H.3/CREP-005, testable by comparing Report claims against the referenced Manifest) but no independently defined validation/rejection procedure of its own. This is a testability gap smaller in scope than the pre-PR-57 state (where the artifact had zero observable criteria at all) but not fully closed to the standard set by the other three artifacts.

Neither of these is judged to block Normative v1.0, for the reasons given in §2 and §3 above.

---

## 5. Cross-Specification Integrity

Reconfirmed in full against the current `main` tip:

- **TC → CM → EB traceability**: TC-001 §3.3, §6.5–§6.6 require both a direct Manifest Reference and a direct Evidence Bundle Reference; TC-001 §15.5 implements the mandatory consistency check between the Certificate's direct Evidence Bundle Reference and the Manifest's own Evidence Bundle Reference, with explicit rejection on mismatch (TC-VERIFY-006). Confirmed present and unchanged since the prior corrective revision.
- **Independent schema versioning**: Evidence Bundle Schema Version (EB-001), Manifest Schema Version (CM-001), Certificate Schema Version (TC-001), and the MCC-CP-001 specification version are each independently declared and explicitly stated to be non-conflatable, in all three downstream documents.
- **Compatibility chain**: CM-001 §17.5 checks against EB-001; TC-001 §17.4 checks against both CM-001 and (added in the prior corrective revision) EB-001 directly, for the new direct Evidence Bundle Reference. Chain confirmed intact.
- **Identifier uniqueness**: full-text scan across all four documents, using the standalone-line definition pattern consistently used throughout the program, finds **361 total defined normative requirement identifiers (CP-001: 155, EB-001: 62, CM-001: 60, TC-001: 84) with zero duplicates.** The new `CRES-` and `CREP-` prefixes introduced by Appendix G/H do not collide with any prefix registered by CP-001 itself or by EB-001/CM-001/TC-001's respective namespace registries.
- **State and PASS/FAIL vocabulary**: CP-001 §8.6/§9.6/Appendix B.2 (binary PASS/FAIL, ALLOW/DENY/ESCALATE/CONSTRAIN explicitly excluded) confirmed byte-identical to the prior review; CM-001 §15.3 and TC-001 §9.2 correctly consume the same binary vocabulary; the new Appendix G/H also correctly reuse PASS/FAIL without introducing a competing vocabulary.
- **Runtime governance artifact separation**: confirmed clean across all four documents; strongest in TC-001 (§3.4, §19.5, TC-MODEL-003, TC-SEC-005). Appendix G/H do not touch this boundary.
- **Signature and trust concentration in MCC-TC-001**: confirmed unchanged — TC-001 §14 (Signature) and §16 (Trust Model) are untouched by any change since the last full review; EB-001/CM-001 continue to correctly defer to TC-001 for whole-artifact trust.
- **No HMAC introduction**: confirmed by full-text scan — the only occurrences of "HMAC" across the four documents are TC-001's explicit exclusions (§14.2, TC-SIG-002).

---

## 6. Security and Trust Model

Unchanged from, and reconfirmed against, the prior full review — Appendix G/H introduce no new artifacts requiring their own trust boundary (Conformance Result rides on the Manifest's existing integrity guarantees; Certification Report is explicitly non-authoritative and outside the cryptographic trust chain by design).

- **Signing authority**: TC-001 Issuer (§3.1, §10), tied to CP-001's Certification Authority (§7.1).
- **Certificate issuer obligations**: TC-001 §21.2, including the Evidence Bundle/Manifest consistency obligation.
- **Verification authority**: TC-001 §16 (Trust Anchors), explicitly requiring recognition to be established outside self-declaration.
- **Integrity boundaries**: EB-001 §13 (Bundle), CM-001 §13 (Manifest Hash References), TC-001 §13–§14 (Manifest/Bundle binding via Hash Reference, whole-Certificate integrity via Signature only).
- **Canonicalization**: consistently defined and cross-referenced (EB-001 §13.2, CM-001 §10.4, TC-001 §4.4).
- **Digest and Hash Reference semantics**: single source of truth in EB-001 §7/§13 and CM-001 §7/§13, correctly reused (not redefined) by TC-001 §3.1.
- **Revocation semantics**: TC-001 §12 — immutable Certificate content, external Revocation Record, mandatory verifier check, audit trail preserved (STATE-005 cross-reference to CP-001 Appendix A).
- **Failure handling**: fail-closed throughout EB-001 §16, CM-001 §18, TC-001 §15; each states rejection as the default for any unmet condition.
- **Substitution / mismatch protection**: TC-001 §8.3 (Subject), §9.3 (Result), §15.5 (Evidence Bundle vs. Manifest's Evidence Bundle Reference) — all three identity/content dimensions are cross-checked.
- **Partial verification**: explicitly barred (TC-001 §15.8 Fail-Closed Verification: "Partial or inconclusive verification results MUST NOT be treated as valid").
- **Replay**: not a meaningful threat under this artifact model — a still-valid, non-expired, non-revoked Certificate being re-presented is the intended normal use, not an attack; this was confirmed by design intent (CP-001 VER-005/VER-006 explicitly preserve historical, potentially-coexisting certification records) rather than assumed.

This remains the strongest area of the specification package.

---

## 7. Re-Evaluation of Previously Reported Residual Findings

| Finding | Prior classification | Re-evaluated status | Rationale |
|---|---|---|---|
| CP-001 Appendix A state labels ("Certified"/"Rejected") vs. PASS/FAIL vocabulary | NON-BLOCKING | **NON-BLOCKING (unchanged)** | Confirmed still present, still confined to narrative Appendix text. No field anywhere is normatively required to emit the literal values "Certified"/"Rejected"; the one operationally load-bearing citation (the "Revoked" state / STATE-005) remains accurate and is correctly used by TC-001 §12. |
| CP-001 §7.4 Conformance Result / Certification Report | **BLOCKING** | **RESOLVED — closed by Appendix G/H (PR #57, merged)** | Both outputs now have full normative definitions, as detailed in §1 and §4 above. This was the sole finding preventing APPROVE FOR NORMATIVE v1.0 in every prior review of this program. |
| CP-001 Document Roadmap still lists Sections 12–21 and Appendices A–H as "Planned" though fully written | NON-BLOCKING | **NON-BLOCKING (unchanged, and now also covers G/H)** | The newly added Appendix G/H entries were appended to the same already-stale "Planned Normative Sections" list, consistent with (not worsening) the pre-existing issue. Purely self-referential; does not affect the validity of the actual normative content. |
| Stale "(planned)" labels for MCC-CM-001/MCC-TC-001 in EB-001 §24.2 and CM-001 §24.2 | EDITORIAL | **EDITORIAL (unchanged)** | Both sibling specs are now published; only the status annotation is stale. Informative-reference classification remains correct. |
| Registered-prefix completeness (EB-001 §23.3, CM-001 §23.3, TC-001 §22.3 each omit their own `-RID-`/`-REF-` prefix from their own listing) | EDITORIAL | **EDITORIAL (unchanged)** | Zero collision risk, independently reconfirmed by the full-corpus uniqueness scan in §5 above. |
| Terminology-family consistency (Validate/Validator in EB-001/CM-001 vs. Verify/Verifier in TC-001) | EDITORIAL | **EDITORIAL (unchanged)** | Defensible per PKI convention; no functional ambiguity in either document. |

**No previously non-blocking or editorial finding is upgraded to BLOCKING in this review.** The only finding that was ever BLOCKING has been resolved.

---

## 8. Findings Summary

### BLOCKING
None.

### NON-BLOCKING
- CP-001 "normative test vectors" (§7.3/§8.2/§9.2) remain undefined — affects only the future Certification Suite, not artifact-level implementability.
- CP-001 Lifecycle/Pipeline/State-Machine (§8/§9/Appendix A) remain three non-formally-reconciled process descriptions; not blocking since all downstream specs anchor to the Pipeline.
- Certification Report (Appendix H) lacks an explicit consumer-side rejection rule, unlike the other three artifacts' dedicated validation sections; judged acceptable given its explicit non-authoritative status and deliberately deferred format.
- Appendix G/H producer identity is stated implicitly/via prohibition rather than affirmatively — consistent with CP-001's pre-existing house style, not a new defect.
- CP-001 Appendix A state-label vocabulary drift from PASS/FAIL (pre-existing, confined to narrative text).
- CP-001 Document Roadmap staleness (pre-existing, now also covers G/H).

### EDITORIAL
- Stale "(planned)" informative-reference labels in EB-001 §24.2 / CM-001 §24.2.
- Registered-prefix self-listing completeness in EB-001 §23.3 / CM-001 §23.3 / TC-001 §22.3.
- Validate/Validator vs. Verify/Verifier terminology-family difference between EB-001/CM-001 and TC-001.
- Minor "Section 10.4/10.5" slash-shorthand citation style in Appendix G, inconsistent with the document's usual "Sections X and Y" phrasing.

### NO ISSUE (reconfirmed)
- Requirement-identifier uniqueness across the full four-document corpus (361 identifiers, zero duplicates).
- Runtime governance artifact separation (ALLOW/DENY/ESCALATE/CONSTRAIN exclusion).
- No HMAC introduced anywhere; Ed25519 remains RECOMMENDED, not mandatory.
- Independent schema versioning and the TC→CM→EB compatibility chain.
- Signature/trust concentration exclusively in MCC-TC-001.
- Direct Technical Certificate Evidence Bundle Reference and its mandatory consistency check against the Manifest's Evidence Bundle Reference.
- Fail-closed behavior and negative-test coverage across all validation/verification procedures.

---

## 9. Final Decision

> **APPROVE FOR NORMATIVE v1.0**
