# MCC-EB-001

# Evidence Bundle Specification

Document ID: MCC-EB-001

Version: 1.0

Status: Normative

Category: Normative Specification

Applies To: MCC Certification Evidence Bundles

Language: English (Normative)

---

# 1. Status

This document is normative.

The key words MUST, MUST NOT, REQUIRED, SHALL, SHALL NOT, SHOULD, SHOULD NOT, RECOMMENDED, MAY and OPTIONAL in this specification are to be interpreted as described in RFC 2119 and RFC 8174.

This specification defines the normative structure, integrity model, validation rules, and reproducibility requirements for MCC Certification Evidence Bundles, as referenced by MCC-CP-001.

Reference implementations are informative unless explicitly stated otherwise.

---

# 2. Abstract

An Evidence Bundle is the reproducible, verifiable artifact produced during MCC certification that substantiates a certification decision.

This specification defines the normative directory structure, required files, required metadata, integrity model, provenance requirements, reproducibility requirements, validation rules, and versioning rules for Evidence Bundles.

Evidence Bundles SHALL remain framework-neutral and implementation-independent, and SHALL be independently verifiable without trusting the environment that produced them.

---

# 3. Purpose

The purpose of this specification is to define a single normative Evidence Bundle format that satisfies the evidence properties required by MCC-CP-001, Section 14 (Evidence Requirements).

This specification exists so that:

- certification evidence can be produced, exchanged, and verified independently of any certification tooling implementation;
- a third party can validate certification evidence without access to the original certification environment;
- Evidence Bundles remain stable, comparable, and reproducible across certification runs and across time.

This specification defines the concrete artifact referenced by the term "Evidence Bundle" in MCC-CP-001, Section 4 (Terminology).

---

# 4. Scope

This specification defines:

- the Evidence Bundle concept and its role in certification;
- the normative Bundle Directory Structure;
- required files within a Bundle;
- required metadata fields;
- the hash and integrity model;
- provenance requirements;
- reproducibility requirements;
- validation rules;
- versioning rules;
- compatibility requirements;
- security considerations applicable to Evidence Bundles;
- the extension model for future Bundle content;
- conformance requirements for Bundle producers and validators.

This specification does NOT define:

- the certification model, lifecycle, or pipeline (defined by MCC-CP-001);
- the Certification Manifest structure (defined by MCC-CM-001);
- the Technical Certificate structure (defined by MCC-TC-001);
- adapter, gateway, or SDK implementations;
- storage, transport, or distribution mechanisms for Bundles;
- runtime execution semantics;
- business logic.

---

# 5. Goals

## EB-G1. Framework Neutrality

The Evidence Bundle format MUST remain independent of any particular framework, programming language, or certification tooling implementation.

## EB-G2. Reproducibility

An Evidence Bundle MUST be reproducible: regenerating a Bundle from the same certification inputs MUST yield a Bundle that is verifiably equivalent under this specification's integrity model.

## EB-G3. Independent Verifiability

A third party MUST be able to validate an Evidence Bundle using only the Bundle itself and this specification, without trusting the environment that produced it.

## EB-G4. Structural Determinism

The Bundle Directory Structure and Required Files MUST be deterministic given the same certification inputs and the same specification version.

## EB-G5. Long-Term Stability

The Evidence Bundle format SHOULD evolve through versioned revisions of this specification while preserving compatibility whenever practical.

---

# 6. Non-Goals

This specification SHALL NOT:

- define how certification decisions are reached (defined by MCC-CP-001);
- define the Certification Manifest or Technical Certificate formats;
- mandate a specific programming language, library, or SDK for producing or validating Bundles;
- mandate a specific storage backend, transport protocol, or distribution channel;
- define business-specific or domain-specific evidence content;
- define runtime governance behavior (ALLOW, DENY, ESCALATE, CONSTRAIN), which belongs exclusively to MCC-Core runtime governance.

---

# 7. Terminology

Evidence Bundle
: The reproducible, verifiable artifact defined by this specification that substantiates a certification decision, as referenced by MCC-CP-001, Section 4.

Bundle Root
: The single top-level directory or archive that contains all contents of an Evidence Bundle.

Evidence Item
: A single discrete unit of evidence contained within an Evidence Bundle, corresponding to one or more evaluated Certification Requirements.

Bundle Descriptor
: The required file identifying an Evidence Bundle, its schema version, and its top-level metadata.

Integrity Record
: The required file or set of fields recording digests used to verify the integrity of Bundle contents.

Provenance Record
: The required file or set of fields recording the origin of an Evidence Bundle, including the certification run and specification version that produced it.

Canonical Form
: A deterministic, unambiguous serialization of data used as input to a hash function, such that identical logical content always produces an identical Canonical Form.

Digest
: The output of a cryptographic hash function applied to data in Canonical Form.

Schema Version
: The version identifier of the Evidence Bundle format itself, distinct from the version of MCC-CP-001 or of any individual certification.

Note: A Bundle Descriptor is distinct from a Certification Manifest as defined by MCC-CP-001, Section 15 and MCC-CM-001. A Bundle Descriptor describes the Evidence Bundle artifact; a Certification Manifest describes the certification result as a whole and MAY reference one or more Evidence Bundles.

---

# 8. Normative References

- RFC 2119, "Key words for use in RFCs to Indicate Requirement Levels"
- RFC 8174, "Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words"
- MCC-CP-001, "Official Certification Program Specification"

The complete normative and informative reference list is given in Section 24.

---

# 9. Evidence Bundle Overview

## 9.1 Role in Certification

An Evidence Bundle is produced during the Evidence Generation stage of the Certification Pipeline defined in MCC-CP-001, Section 9.4, and SHALL satisfy the evidence properties defined in MCC-CP-001, Section 14.3 (reproducible, traceable, verifiable, immutable after generation, attributable to a certification run).

An Evidence Bundle is not itself a certification decision, a Certification Manifest, or a Technical Certificate. It is the substantiating artifact those outputs reference.

## 9.2 Bundle Forms

An Evidence Bundle SHALL take one of the following forms:

- a directory tree rooted at a single Bundle Root; or
- a single deterministic archive of that directory tree.

Both forms SHALL be structurally equivalent: converting between them SHALL NOT alter the Bundle's content or digests.

## 9.3 Relationship to Certification Requirements

Every Evidence Item within a Bundle SHALL correspond to one or more Certification Requirements evaluated under MCC-CP-001, Section 12.

An Evidence Bundle MAY contain Evidence Items for REQUIRED, OPTIONAL, and CONDITIONAL requirements alike, subject to the Required Files and Required Metadata rules in Sections 11 and 12.

---

# 10. Bundle Directory Structure

## 10.1 Bundle Root

Every Evidence Bundle SHALL have exactly one Bundle Root.

All Bundle contents SHALL be located within the Bundle Root.

The Bundle Root SHALL NOT contain content that is not part of the Evidence Bundle.

## 10.2 Top-Level Layout

The Bundle Root SHALL contain, directly at its top level:

- exactly one Bundle Descriptor;
- exactly one Integrity Record;
- exactly one Provenance Record;
- exactly one Evidence Directory containing zero or more Evidence Items.

The Bundle Root MAY contain additional top-level entries only as permitted by the Extension Model defined in Section 20.

## 10.3 Evidence Directory

The Evidence Directory SHALL contain one entry per Evidence Item.

Each Evidence Item entry SHALL be uniquely named within the Evidence Directory.

The internal structure of an individual Evidence Item MAY vary by requirement type but MUST remain within its own entry in the Evidence Directory.

## 10.4 Path Rules

All paths within a Bundle SHALL be relative to the Bundle Root.

Path names within a Bundle SHALL NOT encode information that is not also present in the Bundle Descriptor, Integrity Record, or Provenance Record.

Path names SHALL be stable across regeneration of an equivalent Bundle, in support of EB-G2 (Reproducibility).

## 10.5 Structure Invariants

EB-STR-001

Every Evidence Bundle SHALL have exactly one Bundle Root.

EB-STR-002

The Bundle Root SHALL contain exactly one Bundle Descriptor, one Integrity Record, one Provenance Record, and one Evidence Directory.

EB-STR-003

Bundle directory structure SHALL be deterministic for equivalent certification inputs.

EB-STR-004

Directory and file naming SHALL remain stable across regeneration of an equivalent Bundle.

EB-STR-005

The directory form and archive form of a Bundle SHALL be structurally equivalent.

---

# 11. Required Files

## 11.1 Bundle Descriptor

The Bundle Descriptor MUST be present at the Bundle Root.

The Bundle Descriptor MUST declare:

- the Evidence Bundle Schema Version;
- a Bundle identifier unique to the certification run that produced it;
- the specification version of MCC-CP-001 under which certification was performed.

## 11.2 Integrity Record

The Integrity Record MUST be present at the Bundle Root.

The Integrity Record MUST enumerate a Digest for every file within the Bundle other than the Integrity Record itself.

The Integrity Record MUST declare the hash algorithm used, as governed by Section 13.

## 11.3 Provenance Record

The Provenance Record MUST be present at the Bundle Root.

The Provenance Record MUST satisfy the Provenance Requirements defined in Section 14.

## 11.4 Evidence Items

The Evidence Directory MAY be empty only if no Certification Requirements were applicable to the associated certification run.

Where Evidence Items are present, each MUST be referenced by at least one entry in the Integrity Record.

## 11.5 Required Files Invariants

EB-FILE-001

A Bundle Descriptor MUST be present at the Bundle Root.

EB-FILE-002

An Integrity Record MUST be present at the Bundle Root.

EB-FILE-003

A Provenance Record MUST be present at the Bundle Root.

EB-FILE-004

Every file in the Bundle other than the Integrity Record MUST be enumerated by the Integrity Record.

EB-FILE-005

Required files MUST NOT be omitted regardless of certification outcome.

---

# 12. Required Metadata

## 12.1 Bundle-Level Metadata

The Bundle Descriptor MUST include:

- Bundle identifier;
- Evidence Bundle Schema Version;
- MCC-CP-001 specification version referenced;
- generation timestamp;
- reference to the associated Certification Subject identifier, as defined by MCC-CP-001, Section 7.2.

## 12.2 Evidence Item Metadata

Each Evidence Item MUST be associated with metadata identifying:

- the Certification Requirement identifier it corresponds to, as defined by MCC-CP-001, Section 12.2;
- the verification method applied, as defined by MCC-CP-001, Section 12.4;
- the outcome produced (PASS, FAIL, or NOT APPLICABLE), consistent with MCC-CP-001, Section 10.4.

## 12.3 Metadata Integrity

Required metadata fields MUST be included in the data covered by the Integrity Record.

Metadata fields MUST NOT be modified after Bundle generation without invalidating the Bundle's integrity under Section 13.

## 12.4 Required Metadata Invariants

EB-META-001

Bundle-level metadata MUST identify the Bundle, its schema version, and the specification version it was produced under.

EB-META-002

Every Evidence Item MUST be associated with the Certification Requirement it corresponds to.

EB-META-003

Every Evidence Item MUST record its verification outcome.

EB-META-004

Required metadata MUST be covered by the Integrity Record.

EB-META-005

Metadata SHALL remain immutable after Bundle generation.

---

# 13. Hash and Integrity Model

## 13.1 Purpose

The Hash and Integrity Model defines how Evidence Bundle contents are protected against undetected modification and how integrity is independently verified.

## 13.2 Canonical Form

Data covered by a Digest MUST first be reduced to a Canonical Form.

Canonical Form MUST be deterministic: identical logical content MUST always produce an identical Canonical Form, regardless of the environment or tooling that produced it.

## 13.3 Hash Algorithm

The Integrity Record MUST declare the cryptographic hash algorithm used to compute its Digests.

The declared hash algorithm MUST be a collision-resistant cryptographic hash function.

A Bundle MUST NOT be considered valid if it declares a hash algorithm that is not collision-resistant.

## 13.4 Digest Coverage

Every file within the Bundle Root, other than the Integrity Record itself, MUST have a corresponding Digest entry in the Integrity Record.

A Digest MUST cover the complete Canonical Form of the file it corresponds to.

## 13.5 Integrity Verification

A validator MUST recompute the Digest of every file covered by the Integrity Record and compare it against the declared value.

A Bundle SHALL be considered tampered if any recomputed Digest does not match its declared value.

A tampered Bundle MUST NOT be treated as valid evidence.

## 13.6 Hash and Integrity Invariants

EB-HASH-001

All Digest-covered data MUST first be reduced to a deterministic Canonical Form.

EB-HASH-002

The Integrity Record MUST declare a collision-resistant hash algorithm.

EB-HASH-003

Every non-Integrity-Record file MUST have a corresponding Digest entry.

EB-HASH-004

Digest verification MUST be performed by independent recomputation, not by trusting a prior verification result.

EB-HASH-005

A Bundle with any mismatched Digest MUST be rejected as tampered.

---

# 14. Provenance Requirements

## 14.1 Purpose

Provenance Requirements define what an Evidence Bundle MUST record about its own origin, so that a validator can determine where a Bundle came from without relying on unverifiable external claims.

## 14.2 Required Provenance Fields

The Provenance Record MUST identify:

- the certification run that produced the Bundle;
- the Certification Pipeline stage, as defined by MCC-CP-001, Section 9, that generated the Bundle;
- the specification version of MCC-CP-001 in effect at generation time;
- the Evidence Bundle Schema Version in effect at generation time.

## 14.3 Chain of Custody

Where an Evidence Bundle is derived from, or supersedes, a prior Bundle, the Provenance Record MUST reference the prior Bundle's identifier.

Provenance references MUST NOT be circular.

## 14.4 Non-Repudiation Scope

This specification does NOT require a specific signing mechanism for provenance data. Where a certification implementation applies a signature to a Bundle or its Provenance Record, verification of that signature is outside the scope of this specification and is addressed by the implementation's own trust model.

## 14.5 Provenance Invariants

EB-PROV-001

Every Bundle MUST record the certification run that produced it.

EB-PROV-002

Every Bundle MUST record the specification versions in effect at generation time.

EB-PROV-003

Provenance references between Bundles MUST NOT be circular.

EB-PROV-004

Provenance data MUST be covered by the Integrity Record.

EB-PROV-005

Provenance data MUST remain immutable after Bundle generation.

---

# 15. Reproducibility Requirements

## 15.1 Purpose

Reproducibility Requirements define what it means for an Evidence Bundle to be independently regenerable and comparable, in support of EB-G2.

## 15.2 Deterministic Generation

Given identical certification inputs and an identical specification version, Bundle generation MUST produce a Bundle whose Digests are identical to a previously generated Bundle for the same certification run.

## 15.3 Prohibited Non-Determinism

Canonical Form and Digest computation MUST NOT depend on:

- wall-clock time, other than an explicitly declared generation timestamp field that is itself excluded from, or deterministically normalized within, the Canonical Form used for reproducibility comparison;
- random or non-deterministic identifiers not derived from the certification run itself;
- the order in which Evidence Items were internally processed, where that order is not otherwise normatively significant.

## 15.4 Regeneration Equivalence

Two Bundles produced from identical certification inputs and an identical specification version SHALL be considered equivalent if their Integrity Records match after excluding fields explicitly permitted to vary under Section 15.3.

## 15.5 Reproducibility Invariants

EB-REPRO-001

Bundle generation MUST be deterministic given identical certification inputs and specification version.

EB-REPRO-002

Non-deterministic values MUST NOT influence Canonical Form or Digest computation, except as explicitly permitted.

EB-REPRO-003

Equivalent certification inputs MUST produce Bundles with matching Integrity Records under Section 15.4.

EB-REPRO-004

Reproducibility MUST be verifiable without access to the original generation environment.

---

# 16. Validation Rules

## 16.1 Purpose

Validation Rules define the normative procedure and criteria a validator MUST apply to determine whether an Evidence Bundle is valid.

## 16.2 Structural Validation

A validator MUST verify that the Bundle conforms to the Bundle Directory Structure defined in Section 10 and contains all Required Files defined in Section 11.

A Bundle that fails structural validation MUST be rejected without further processing.

## 16.3 Metadata Validation

A validator MUST verify that all Required Metadata defined in Section 12 is present and internally consistent (for example, that referenced Certification Requirement identifiers are well-formed).

## 16.4 Integrity Validation

A validator MUST perform Integrity Verification as defined in Section 13.5.

A Bundle that fails integrity validation MUST be rejected.

## 16.5 Provenance Validation

A validator MUST verify that Provenance Requirements defined in Section 14 are satisfied, including the absence of circular references.

## 16.6 Fail-Closed Validation

Validation SHALL be fail-closed: a Bundle MUST be treated as invalid unless every applicable validation step in this section succeeds.

Partial or inconclusive validation results MUST NOT be treated as valid.

## 16.7 Validation Invariants

EB-VAL-001

Validation MUST be fail-closed.

EB-VAL-002

Structural validation MUST precede metadata, integrity, and provenance validation.

EB-VAL-003

A Bundle failing any validation step MUST be rejected in its entirety.

EB-VAL-004

Validation MUST be reproducible: the same Bundle MUST produce the same validation result under the same specification version.

EB-VAL-005

Validation MUST NOT depend on trusting the environment that produced the Bundle.

---

# 17. Versioning Rules

## 17.1 Purpose

Versioning Rules define how the Evidence Bundle Schema Version is declared, interpreted, and evolved, independently of the versioning of MCC-CP-001 itself.

## 17.2 Schema Version Declaration

Every Bundle MUST declare its Evidence Bundle Schema Version in the Bundle Descriptor.

The Schema Version MUST be immutable once assigned to a published revision of this specification.

## 17.3 Schema Version Scope

The Evidence Bundle Schema Version governs the Bundle Directory Structure, Required Files, Required Metadata, and Hash and Integrity Model defined by this specification.

The Evidence Bundle Schema Version is distinct from, and SHALL NOT be conflated with, the MCC-CP-001 specification version referenced by a Bundle's Provenance Record.

## 17.4 Version Evolution

A future revision of this specification MAY introduce a new Evidence Bundle Schema Version.

A validator MUST reject a Bundle declaring a Schema Version it does not recognize, consistent with Section 16.6.

## 17.5 Versioning Invariants

EB-VSN-001

Every Bundle MUST declare an Evidence Bundle Schema Version.

EB-VSN-002

Schema Versions MUST be immutable once published.

EB-VSN-003

Schema Version and MCC-CP-001 specification version MUST be tracked independently.

EB-VSN-004

An unrecognized Schema Version MUST cause validation to fail.

---

# 18. Compatibility Requirements

## 18.1 Purpose

Compatibility Requirements define how validators and Bundle producers built against different revisions of this specification are expected to interoperate.

## 18.2 Backward Compatibility

A validator supporting a given Schema Version SHOULD also support validating Bundles declaring earlier Schema Versions where this specification's revision history states that compatibility is preserved.

## 18.3 Forward Compatibility

A validator MUST NOT assume forward compatibility with a Schema Version it does not recognize.

An unrecognized Schema Version MUST be treated per Section 17.4 and Section 16.6, not silently accepted.

## 18.4 Breaking Changes

A revision of this specification that alters the Bundle Directory Structure, Required Files, Required Metadata, or Hash and Integrity Model in a way that invalidates previously valid Bundles MUST introduce a new Schema Version and MUST document the change as breaking.

## 18.5 Compatibility Invariants

EB-COMPAT-001

Compatibility claims between Schema Versions MUST be explicit, not assumed.

EB-COMPAT-002

Unrecognized Schema Versions MUST NOT be silently accepted.

EB-COMPAT-003

Breaking changes MUST introduce a new Schema Version.

EB-COMPAT-004

Compatibility MUST remain independent of implementation or tooling.

---

# 19. Security Considerations

## 19.1 Purpose

This section defines the threat model and security requirements applicable to Evidence Bundles.

## 19.2 Threat Model

Validation of an Evidence Bundle MUST assume:

- the Bundle MAY originate from an untrusted or compromised source;
- the Bundle MAY have been partially or fully tampered with;
- the environment that produced the Bundle MUST NOT be trusted implicitly.

## 19.3 Tamper Detection

Tamper detection is provided exclusively through the Hash and Integrity Model defined in Section 13.

A validator MUST NOT treat any Bundle content as authoritative prior to successful Integrity Verification.

## 19.4 Sensitive Data

An Evidence Bundle MUST NOT include secrets, credentials, or other sensitive material not required to demonstrate conformance to a Certification Requirement.

Where underlying certification inputs contain sensitive material, Evidence Items MUST reference redacted or hashed representations rather than raw sensitive values.

## 19.5 Security Invariants

EB-SEC-001

Bundle validation MUST assume an untrusted source.

EB-SEC-002

Tamper detection MUST rely solely on independently recomputed Digests.

EB-SEC-003

Bundles MUST NOT contain secrets or credentials.

EB-SEC-004

Sensitive underlying data MUST be redacted or hashed before inclusion as an Evidence Item.

EB-SEC-005

Security properties of a Bundle MUST be verifiable without trusting its origin.

---

# 20. Extension Model

## 20.1 Purpose

The Extension Model defines how future content MAY be added to an Evidence Bundle without breaking validators built against an earlier revision of this specification.

## 20.2 Extension Points

Additional top-level entries at the Bundle Root, beyond those required by Section 10.2, are permitted only as explicitly declared extensions.

Extensions MUST be declared in the Bundle Descriptor.

## 20.3 Extension Constraints

An extension MUST NOT alter the meaning of any Required File or Required Metadata defined by this specification.

A validator that does not recognize a declared extension MUST ignore that extension's content without failing validation, provided all other validation rules in Section 16 are satisfied.

An extension MUST be covered by the Integrity Record like any other Bundle content.

## 20.4 Extension Model Invariants

EB-EXT-001

Extensions MUST be explicitly declared in the Bundle Descriptor.

EB-EXT-002

Extensions MUST NOT redefine the meaning of Required Files or Required Metadata.

EB-EXT-003

Unrecognized extensions MUST be ignored, not treated as validation failures.

EB-EXT-004

Extension content MUST be covered by the Integrity Record.

---

# 21. IANA Considerations

This specification defines no protocol elements, media types, port numbers, or other identifiers subject to registration with the Internet Assigned Numbers Authority.

No IANA actions are required by this specification.

Identifier namespace management for this specification's own normative requirement identifiers is addressed in Section 23, not through IANA.

---

# 22. Conformance Requirements

## 22.1 Purpose

This section defines what it means for a Bundle producer or a Bundle validator to conform to this specification.

## 22.2 Conforming Bundle Producer

A conforming Bundle producer MUST generate Bundles satisfying Sections 10 through 15 of this specification for the Schema Version it declares.

A conforming Bundle producer MUST NOT emit a Bundle that fails validation under Section 16 against its own declared Schema Version.

## 22.3 Conforming Bundle Validator

A conforming Bundle validator MUST implement the validation procedure defined in Section 16 in full, without omitting any applicable step.

A conforming Bundle validator MUST reject a Bundle whenever any applicable validation step fails.

## 22.4 Conformance Independence

Conformance to this specification SHALL be evaluated independently of any specific programming language, framework, or certification tooling implementation.

## 22.5 Conformance Invariants

EB-CONF-001

Conformance is defined separately for Bundle producers and Bundle validators.

EB-CONF-002

A conforming producer MUST NOT emit Bundles that fail their own declared Schema Version's validation rules.

EB-CONF-003

A conforming validator MUST implement fail-closed validation in full.

EB-CONF-004

Conformance MUST remain framework-neutral and implementation-independent.

---

# 23. Requirement Identifier Registry

## 23.1 Purpose

This section documents the identifier namespace used by this specification's normative requirement identifiers, so that future specifications and future revisions of this specification can avoid identifier collisions such as the one identified and resolved in MCC-CP-001.

## 23.2 Namespace Convention

Every normative requirement identifier defined by this specification SHALL be prefixed with `EB-`, followed by a section-scoped category tag, followed by a three-digit sequence number.

## 23.3 Registered Prefixes

The following category tags are defined by this specification:

- `EB-STR-` — Bundle Directory Structure (Section 10)
- `EB-FILE-` — Required Files (Section 11)
- `EB-META-` — Required Metadata (Section 12)
- `EB-HASH-` — Hash and Integrity Model (Section 13)
- `EB-PROV-` — Provenance Requirements (Section 14)
- `EB-REPRO-` — Reproducibility Requirements (Section 15)
- `EB-VAL-` — Validation Rules (Section 16)
- `EB-VSN-` — Versioning Rules (Section 17)
- `EB-COMPAT-` — Compatibility Requirements (Section 18)
- `EB-SEC-` — Security Considerations (Section 19)
- `EB-EXT-` — Extension Model (Section 20)
- `EB-CONF-` — Conformance Requirements (Section 22)

## 23.4 Registry Requirements

Requirement identifiers under this specification's `EB-` namespace SHALL be globally unique.

A future revision of this specification MUST NOT reuse a retired identifier for a different requirement.

A future revision of this specification MUST NOT introduce a new category tag that collides with a prefix already registered by MCC-CP-001 or by this specification.

## 23.5 Registry Invariants

EB-RID-001

All identifiers defined by this specification MUST use the `EB-` namespace prefix.

EB-RID-002

Identifiers within the `EB-` namespace MUST be globally unique.

EB-RID-003

Retired identifiers MUST NOT be reassigned to a different requirement.

EB-RID-004

New category tags MUST NOT collide with prefixes already registered by another MCC specification.

---

# 24. References

## 24.1 Normative References

- RFC 2119, "Key words for use in RFCs to Indicate Requirement Levels"
- RFC 8174, "Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words"
- MCC-CP-001, "Official Certification Program Specification"

## 24.2 Informative References

- MCC-CM-001, "Certification Manifest Specification" (planned)
- MCC-TC-001, "Technical Certificate Specification" (planned)

## 24.3 Reference Invariants

EB-REF-001

Normative references SHALL identify only documents required to interpret this specification's normative requirements.

EB-REF-002

Informative references SHALL NOT define normative behavior.

EB-REF-003

References to planned specifications MUST be clearly marked as informative until those specifications are published.
