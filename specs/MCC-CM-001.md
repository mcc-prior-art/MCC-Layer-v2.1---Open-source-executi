# MCC-CM-001

# Certification Manifest Specification

Document ID: MCC-CM-001

Version: Draft v0.1

Status: Draft

Category: Normative Specification

Applies To: MCC Certification Manifests

Language: English (Normative)

---

# 1. Status

This document is normative.

The key words MUST, MUST NOT, REQUIRED, SHALL, SHALL NOT, SHOULD, SHOULD NOT, RECOMMENDED, MAY and OPTIONAL in this specification are to be interpreted as described in RFC 2119 and RFC 8174.

This specification defines the normative schema, required and optional fields, hash and Evidence Bundle referencing rules, versioning, compatibility, validation, and security requirements for MCC Certification Manifests, as referenced by MCC-CP-001.

Reference implementations are informative unless explicitly stated otherwise.

---

# 2. Abstract

A Certification Manifest is the structured, machine-readable artifact produced during MCC certification that describes a certification result: what was evaluated, against which specification, with what outcome, and by reference to which supporting Evidence Bundles.

This specification defines the normative Manifest Schema, its required and optional fields, how it references Evidence Bundles and their Digests, its versioning and compatibility rules, its validation rules, and its security considerations.

A Certification Manifest SHALL remain framework-neutral and implementation-independent, and SHALL be independently verifiable without trusting the environment that produced it.

---

# 3. Purpose

The purpose of this specification is to define a single normative Certification Manifest format that satisfies the requirements defined by MCC-CP-001, Section 15 (Certification Manifest Requirements).

This specification exists so that:

- certification results can be expressed in a structured, machine-readable form independent of any certification tooling implementation;
- a third party can interpret and validate a Certification Manifest without access to the original certification environment;
- a Certification Manifest can be reliably linked to the Evidence Bundle(s) and specification versions that substantiate it.

This specification defines the concrete artifact referenced by the term "Certification Manifest" in MCC-CP-001, Section 4 (Terminology).

---

# 4. Scope

This specification defines:

- the Certification Manifest concept and its role in certification;
- the normative Manifest Schema;
- Required Fields and Optional Fields;
- Hash References within a Manifest;
- Evidence Bundle References within a Manifest;
- Certification Metadata carried by a Manifest;
- Versioning Rules for the Manifest Schema;
- Compatibility Rules between Manifest Schema Versions;
- Validation Rules for Manifests;
- security considerations applicable to Manifests;
- the extension model for future Manifest content;
- conformance requirements for Manifest producers and validators.

This specification does NOT define:

- the certification model, lifecycle, or pipeline (defined by MCC-CP-001);
- the Evidence Bundle structure or integrity model (defined by MCC-EB-001);
- the Technical Certificate structure (defined by MCC-TC-001);
- adapter, gateway, or SDK implementations;
- storage, transport, or distribution mechanisms for Manifests;
- runtime execution semantics;
- business logic.

---

# 5. Goals

## CM-G1. Framework Neutrality

The Certification Manifest format MUST remain independent of any particular framework, programming language, or certification tooling implementation.

## CM-G2. Machine Readability

A Certification Manifest MUST be structured and machine-readable, without requiring interpretation beyond this specification and its declared Schema Version.

## CM-G3. Independent Verifiability

A third party MUST be able to interpret and validate a Certification Manifest, and confirm its relationship to the Evidence Bundle(s) it references, without trusting the environment that produced it.

## CM-G4. Traceability

A Certification Manifest MUST remain traceable to the Certification Subject, the specification version, and the Evidence Bundle(s) that substantiate it.

## CM-G5. Long-Term Stability

The Manifest format SHOULD evolve through versioned revisions of this specification while preserving compatibility whenever practical.

---

# 6. Non-Goals

This specification SHALL NOT:

- define how certification decisions are reached (defined by MCC-CP-001);
- define the Evidence Bundle or Technical Certificate formats;
- mandate a specific programming language, library, or SDK for producing or validating Manifests;
- mandate a specific storage backend, transport protocol, or distribution channel;
- define business-specific or domain-specific manifest content;
- define runtime governance behavior (ALLOW, DENY, ESCALATE, CONSTRAIN), which belongs exclusively to MCC-Core runtime governance.

---

# 7. Terminology

Certification Manifest
: The structured, machine-readable artifact defined by this specification that describes a certification result, as referenced by MCC-CP-001, Section 4 and Section 15.

Manifest Field
: A single named element of data within a Certification Manifest, as defined by the Manifest Schema.

Hash Reference
: A structured Manifest Field that identifies a Digest, the hash algorithm used to produce it, and the artifact or content the Digest corresponds to.

Evidence Bundle Reference
: A structured Manifest Field that identifies an Evidence Bundle, as defined by MCC-EB-001, that substantiates the certification result described by the Manifest.

Certification Metadata
: The set of Manifest Fields describing the certification run itself: the Certification Subject, the specification version, the requirements evaluated, and the certification result.

Requirement Result
: A structured Manifest Field recording the outcome (PASS, FAIL, or NOT APPLICABLE) of a single evaluated Certification Requirement, as defined by MCC-CP-001, Section 12.

Manifest Schema Version
: The version identifier of the Certification Manifest format itself, distinct from the version of MCC-CP-001 and from the Evidence Bundle Schema Version defined by MCC-EB-001.

Note: A Certification Manifest is a single structured document describing a certification result as a whole; it is distinct from an Evidence Bundle, which is a directory or archive of substantiating artifacts as defined by MCC-EB-001, and from a Technical Certificate, which is the authoritative certification outcome record as defined by MCC-TC-001.

---

# 8. Normative References

- RFC 2119, "Key words for use in RFCs to Indicate Requirement Levels"
- RFC 8174, "Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words"
- MCC-CP-001, "Official Certification Program Specification"
- MCC-EB-001, "Evidence Bundle Specification"

The complete normative and informative reference list is given in Section 24.

---

# 9. Certification Manifest Overview

## 9.1 Role in Certification

A Certification Manifest is produced during the Artifact Generation stage of the Certification Pipeline defined in MCC-CP-001, Section 9.7, and SHALL satisfy the requirements defined in MCC-CP-001, Section 15.

A Certification Manifest describes a certification result; it does not itself decide, execute, or authorize certification. The certification decision it describes is produced under MCC-CP-001, Sections 8.6 and 9.6.

## 9.2 Manifest Form

A Certification Manifest SHALL be a single structured, machine-readable document.

A Certification Manifest SHALL NOT be a directory or multi-file archive; where multiple substantiating files exist, they SHALL be organized as an Evidence Bundle under MCC-EB-001 and referenced from the Manifest by Evidence Bundle Reference.

## 9.3 Relationship to Other Certification Artifacts

A Certification Manifest MUST reference at least one Evidence Bundle, per Section 14.

A Certification Manifest MAY be referenced, by Hash Reference, from a Technical Certificate as defined by MCC-TC-001. Defining that reference is the responsibility of MCC-TC-001, not of this specification.

---

# 10. Manifest Schema

## 10.1 Purpose

The Manifest Schema defines the normative top-level structure of a Certification Manifest: the set of Manifest Fields it is composed of and how those fields are grouped.

## 10.2 Top-Level Structure

A Certification Manifest SHALL be composed of the following field groups:

- Identification fields, per Section 11.2;
- Certification Metadata fields, per Section 15;
- Requirement Results, per Section 15.4;
- Evidence Bundle References, per Section 14;
- Hash References, per Section 13;
- Optional Fields, per Section 12;
- Extension fields, per Section 20, where present.

## 10.3 Field Typing

Every Manifest Field MUST have a defined type consistent with this specification: identifier, string, timestamp, enumerated value, Hash Reference, Evidence Bundle Reference, Requirement Result, or a list thereof.

Manifest Fields MUST NOT be ambiguous as to type.

## 10.4 Canonical Form

For any purpose requiring a Digest of a Certification Manifest, or a Digest of a subset of its fields, the data digested MUST first be reduced to a Canonical Form, consistent with the Canonical Form requirement of MCC-EB-001, Section 13.2.

## 10.5 Manifest Schema Invariants

CM-SCHEMA-001

A Certification Manifest MUST be a single structured, machine-readable document.

CM-SCHEMA-002

Every Manifest Field MUST have an unambiguous, defined type.

CM-SCHEMA-003

The top-level field groups defined in Section 10.2 MUST all be present, except where explicitly marked optional.

CM-SCHEMA-004

Digest computation over Manifest content MUST use a deterministic Canonical Form.

CM-SCHEMA-005

The Manifest Schema MUST remain independent of any specific serialization technology.

---

# 11. Required Fields

## 11.1 Purpose

Required Fields are the Manifest Fields that MUST be present in every conforming Certification Manifest.

## 11.2 Identification Fields

Every Certification Manifest MUST include:

- a manifest identifier, unique to the certification run it describes;
- the Manifest Schema Version;
- the MCC-CP-001 specification version under which certification was performed;
- the Certification Subject identifier, as defined by MCC-CP-001, Section 7.2.

## 11.3 Baseline Required Fields

Consistent with MCC-CP-001, Section 15.2, every Certification Manifest MUST include:

- manifest identifier;
- specification version;
- Certification Subject identifier;
- capability profiles;
- certification requirements evaluated;
- certification result;
- evidence references;
- generation timestamp.

## 11.4 Field Presence Rule

A Certification Manifest MUST NOT omit a Required Field regardless of certification outcome, including where the certification result is FAIL.

## 11.5 Required Fields Invariants

CM-RFLD-001

A manifest identifier MUST be present and unique to the certification run.

CM-RFLD-002

The Manifest Schema Version MUST be present.

CM-RFLD-003

The MCC-CP-001 specification version MUST be present.

CM-RFLD-004

The Certification Subject identifier MUST be present.

CM-RFLD-005

Certification requirements evaluated, certification result, evidence references, and generation timestamp MUST all be present.

CM-RFLD-006

Required Fields MUST be present regardless of certification outcome.

---

# 12. Optional Fields

## 12.1 Purpose

Optional Fields are Manifest Fields that MAY be present to provide additional, non-mandatory information.

## 12.2 Defined Optional Fields

A Certification Manifest MAY include:

- a human-readable summary of the certification result;
- references to prior Certification Manifests for the same Certification Subject, for historical traceability;
- capability claims that were declared but not evaluated, distinct from capability profiles that were evaluated;
- free-form annotations, subject to Section 19.4 (Sensitive Data).

## 12.3 Optional Field Constraints

An Optional Field, where present, MUST conform to the type rules of Section 10.3.

The absence of an Optional Field MUST NOT be treated as a validation failure.

An Optional Field MUST NOT be used to satisfy a Required Field obligation defined in Section 11.

## 12.4 Optional Fields Invariants

CM-OPTF-001

Optional Fields MAY be omitted without affecting Manifest validity.

CM-OPTF-002

Optional Fields, where present, MUST conform to defined type rules.

CM-OPTF-003

Optional Fields MUST NOT substitute for Required Fields.

CM-OPTF-004

Undefined, unrecognized fields MUST be treated as extensions under Section 20, not as ad hoc Optional Fields.

---

# 13. Hash References

## 13.1 Purpose

Hash References are the mechanism by which a Certification Manifest cryptographically binds itself to external content, most notably the Evidence Bundle(s) it references.

## 13.2 Hash Reference Structure

A Hash Reference MUST identify:

- the Digest value;
- the hash algorithm used to produce the Digest;
- the artifact or content the Digest corresponds to (for example, an Evidence Bundle identifier).

## 13.3 Hash Algorithm Requirements

The hash algorithm identified by a Hash Reference MUST be a collision-resistant cryptographic hash function, consistent with MCC-EB-001, Section 13.3.

A Certification Manifest MUST NOT be considered valid if any Hash Reference identifies a hash algorithm that is not collision-resistant.

## 13.4 Hash Reference Usage

Every Evidence Bundle Reference, per Section 14, MUST include at least one Hash Reference binding it to the referenced Evidence Bundle's Integrity Record, as defined by MCC-EB-001, Section 13.

A Certification Manifest MAY include additional Hash References for auxiliary content, subject to Section 20 (Extension Model).

## 13.5 Hash Reference Invariants

CM-HASH-001

A Hash Reference MUST identify a Digest, a hash algorithm, and the content it corresponds to.

CM-HASH-002

Hash Reference algorithms MUST be collision-resistant.

CM-HASH-003

Every Evidence Bundle Reference MUST include at least one Hash Reference.

CM-HASH-004

Hash References MUST be independently recomputable and verifiable by a validator.

---

# 14. Evidence Bundle References

## 14.1 Purpose

Evidence Bundle References define how a Certification Manifest identifies and binds to the Evidence Bundle(s), as defined by MCC-EB-001, that substantiate its certification result.

## 14.2 Primary Evidence Bundle Reference

A Certification Manifest MUST reference exactly one primary Evidence Bundle corresponding to the certification run described by the Manifest.

The primary Evidence Bundle Reference MUST include:

- the Evidence Bundle identifier, as defined by MCC-EB-001, Section 12.1;
- the Evidence Bundle Schema Version, as defined by MCC-EB-001, Section 17.2;
- a Hash Reference binding the Manifest to that Evidence Bundle's Integrity Record.

## 14.3 Supplementary Evidence Bundle References

A Certification Manifest MAY reference additional Evidence Bundles from prior certification runs of the same Certification Subject, for revalidation traceability consistent with MCC-CP-001, Section 8.9 and Section 17.4.

A supplementary Evidence Bundle Reference MUST be distinguishable from the primary Evidence Bundle Reference defined in Section 14.2.

## 14.4 Reference Integrity

An Evidence Bundle Reference MUST NOT be considered satisfied unless the Hash Reference it carries is independently verified against the referenced Evidence Bundle's Integrity Record.

A Certification Manifest whose primary Evidence Bundle Reference cannot be verified MUST NOT be treated as valid.

## 14.5 Evidence Bundle Reference Invariants

CM-EBREF-001

A Certification Manifest MUST reference exactly one primary Evidence Bundle.

CM-EBREF-002

The primary Evidence Bundle Reference MUST include the Evidence Bundle identifier, Schema Version, and a Hash Reference.

CM-EBREF-003

Supplementary Evidence Bundle References MUST be distinguishable from the primary reference.

CM-EBREF-004

An unverifiable primary Evidence Bundle Reference invalidates the Manifest.

---

# 15. Certification Metadata

## 15.1 Purpose

Certification Metadata is the set of Manifest Fields describing the certification run itself, consistent with MCC-CP-001, Sections 7 through 13.

## 15.2 Subject and Scope Metadata

Certification Metadata MUST identify:

- the Certification Subject, as defined by MCC-CP-001, Section 7.2;
- the capability profiles claimed and the capability profiles verified, as defined by MCC-CP-001, Section 11;
- the specification version of MCC-CP-001 under which certification was performed.

## 15.3 Certification Result

Certification Metadata MUST record the overall certification result as one of the outcomes defined by MCC-CP-001, Sections 8.6 and 9.6:

- PASS
- FAIL

A Certification Manifest MUST NOT record a certification result other than PASS or FAIL.

## 15.4 Requirement Results

Certification Metadata MUST include a Requirement Result for every Certification Requirement evaluated during certification.

Each Requirement Result MUST identify:

- the Certification Requirement identifier, as defined by MCC-CP-001, Section 12.2;
- its classification (REQUIRED, OPTIONAL, or CONDITIONAL), as defined by MCC-CP-001, Sections 10.3 and 13.2;
- its outcome (PASS, FAIL, or NOT APPLICABLE), consistent with MCC-CP-001, Sections 8.5, 9.5, and 10.4.

## 15.5 Generation Metadata

Certification Metadata MUST include a generation timestamp identifying when the Manifest was produced.

## 15.6 Certification Metadata Invariants

CM-META-001

Certification Metadata MUST identify the Certification Subject and specification version.

CM-META-002

Certification Metadata MUST identify claimed and verified capability profiles.

CM-META-003

The certification result MUST be exactly one of PASS or FAIL.

CM-META-004

Every evaluated Certification Requirement MUST have a corresponding Requirement Result.

CM-META-005

Certification Metadata MUST include a generation timestamp.

---

# 16. Versioning Rules

## 16.1 Purpose

Versioning Rules define how the Manifest Schema Version is declared, interpreted, and evolved, independently of the versioning of MCC-CP-001 and MCC-EB-001.

## 16.2 Schema Version Declaration

Every Certification Manifest MUST declare its Manifest Schema Version among its Identification Fields.

The Manifest Schema Version MUST be immutable once assigned to a published revision of this specification.

## 16.3 Schema Version Scope

The Manifest Schema Version governs the Manifest Schema, Required Fields, Optional Fields, Hash References, and Evidence Bundle Reference rules defined by this specification.

The Manifest Schema Version is distinct from, and SHALL NOT be conflated with, the MCC-CP-001 specification version or the Evidence Bundle Schema Version referenced by a Manifest.

## 16.4 Version Evolution

A future revision of this specification MAY introduce a new Manifest Schema Version.

A validator MUST reject a Certification Manifest declaring a Schema Version it does not recognize, consistent with Section 18.6.

## 16.5 Versioning Invariants

CM-VSN-001

Every Certification Manifest MUST declare a Manifest Schema Version.

CM-VSN-002

Manifest Schema Versions MUST be immutable once published.

CM-VSN-003

Manifest Schema Version, MCC-CP-001 specification version, and Evidence Bundle Schema Version MUST be tracked independently.

CM-VSN-004

An unrecognized Manifest Schema Version MUST cause validation to fail.

---

# 17. Compatibility Rules

## 17.1 Purpose

Compatibility Rules define how Manifest producers and validators built against different revisions of this specification are expected to interoperate.

## 17.2 Backward Compatibility

A validator supporting a given Manifest Schema Version SHOULD also support validating Manifests declaring earlier Schema Versions where this specification's revision history states that compatibility is preserved.

## 17.3 Forward Compatibility

A validator MUST NOT assume forward compatibility with a Manifest Schema Version it does not recognize.

An unrecognized Manifest Schema Version MUST be treated per Section 16.4 and Section 18.6, not silently accepted.

## 17.4 Breaking Changes

A revision of this specification that alters the Manifest Schema, Required Fields, Hash Reference structure, or Evidence Bundle Reference rules in a way that invalidates previously valid Manifests MUST introduce a new Manifest Schema Version and MUST document the change as breaking.

## 17.5 Cross-Specification Compatibility

A Certification Manifest MUST NOT be considered valid if it references an Evidence Bundle Schema Version that MCC-EB-001, as currently published, does not recognize.

## 17.6 Compatibility Invariants

CM-COMPAT-001

Compatibility claims between Manifest Schema Versions MUST be explicit, not assumed.

CM-COMPAT-002

Unrecognized Manifest Schema Versions MUST NOT be silently accepted.

CM-COMPAT-003

Breaking changes MUST introduce a new Manifest Schema Version.

CM-COMPAT-004

Manifest validity MUST account for the compatibility of any referenced Evidence Bundle Schema Version.

---

# 18. Validation Rules

## 18.1 Purpose

Validation Rules define the normative procedure and criteria a validator MUST apply to determine whether a Certification Manifest is valid.

## 18.2 Structural Validation

A validator MUST verify that the Manifest conforms to the Manifest Schema defined in Section 10 and contains all Required Fields defined in Section 11.

A Manifest that fails structural validation MUST be rejected without further processing.

## 18.3 Hash Reference Validation

A validator MUST independently recompute and verify every Hash Reference contained in the Manifest, consistent with Section 13.5.

A Manifest containing any unverifiable Hash Reference MUST be rejected.

## 18.4 Evidence Bundle Reference Validation

A validator MUST verify the primary Evidence Bundle Reference defined in Section 14.2 against the referenced Evidence Bundle's Integrity Record, as defined by MCC-EB-001, Section 16.

A Manifest whose primary Evidence Bundle Reference cannot be verified MUST be rejected.

## 18.5 Metadata Consistency Validation

A validator MUST verify that Certification Metadata is internally consistent: that the certification result recorded under Section 15.3 is consistent with the Requirement Results recorded under Section 15.4, per MCC-CP-001, Section 10.5.

## 18.6 Fail-Closed Validation

Validation SHALL be fail-closed: a Certification Manifest MUST be treated as invalid unless every applicable validation step in this section succeeds.

Partial or inconclusive validation results MUST NOT be treated as valid.

## 18.7 Validation Invariants

CM-VAL-001

Validation MUST be fail-closed.

CM-VAL-002

Structural validation MUST precede Hash Reference, Evidence Bundle Reference, and metadata consistency validation.

CM-VAL-003

A Manifest failing any validation step MUST be rejected in its entirety.

CM-VAL-004

Validation MUST be reproducible: the same Manifest MUST produce the same validation result under the same Schema Version.

CM-VAL-005

Validation MUST NOT depend on trusting the environment that produced the Manifest.

---

# 19. Security Considerations

## 19.1 Purpose

This section defines the threat model and security requirements applicable to Certification Manifests.

## 19.2 Threat Model

Validation of a Certification Manifest MUST assume:

- the Manifest MAY originate from an untrusted or compromised source;
- the Manifest MAY have been partially or fully tampered with;
- the environment that produced the Manifest MUST NOT be trusted implicitly.

## 19.3 Tamper Detection

Tamper detection for Manifest content that references external artifacts is provided through Hash Reference verification, per Section 13 and Section 18.3.

Where a Manifest's own integrity as a whole is protected (for example, by a signature applied by a Technical Certificate under MCC-TC-001), verification of that protection is outside the scope of this specification.

## 19.4 Sensitive Data

A Certification Manifest MUST NOT include secrets, credentials, or other sensitive material not required to describe the certification result.

Where underlying certification inputs contain sensitive material, Manifest Fields MUST reference redacted or hashed representations rather than raw sensitive values, consistent with MCC-EB-001, Section 19.4.

## 19.5 Security Invariants

CM-SEC-001

Manifest validation MUST assume an untrusted source.

CM-SEC-002

Tamper detection for referenced content MUST rely on independently recomputed Hash References.

CM-SEC-003

Manifests MUST NOT contain secrets or credentials.

CM-SEC-004

Sensitive underlying data MUST be redacted or hashed before inclusion in a Manifest Field.

CM-SEC-005

Security properties of a Manifest MUST be verifiable without trusting its origin.

---

# 20. Extension Model

## 20.1 Purpose

The Extension Model defines how future content MAY be added to a Certification Manifest without breaking validators built against an earlier revision of this specification.

## 20.2 Extension Points

Fields beyond those defined by Sections 10 through 15 are permitted only as explicitly declared extensions.

Extensions MUST be declared and identified as such within the Manifest.

## 20.3 Extension Constraints

An extension MUST NOT alter the meaning of any Required Field, Hash Reference, or Evidence Bundle Reference defined by this specification.

A validator that does not recognize a declared extension MUST ignore that extension's content without failing validation, provided all other validation rules in Section 18 are satisfied.

## 20.4 Extension Model Invariants

CM-EXT-001

Extensions MUST be explicitly declared within the Manifest.

CM-EXT-002

Extensions MUST NOT redefine the meaning of Required Fields, Hash References, or Evidence Bundle References.

CM-EXT-003

Unrecognized extensions MUST be ignored, not treated as validation failures.

---

# 21. IANA Considerations

This specification defines no protocol elements, media types, port numbers, or other identifiers subject to registration with the Internet Assigned Numbers Authority.

No IANA actions are required by this specification.

Identifier namespace management for this specification's own normative requirement identifiers is addressed in Section 23, not through IANA.

---

# 22. Conformance Requirements

## 22.1 Purpose

This section defines what it means for a Manifest producer or a Manifest validator to conform to this specification.

## 22.2 Conforming Manifest Producer

A conforming Manifest producer MUST generate Manifests satisfying Sections 10 through 15 of this specification for the Manifest Schema Version it declares.

A conforming Manifest producer MUST NOT emit a Manifest that fails validation under Section 18 against its own declared Schema Version.

## 22.3 Conforming Manifest Validator

A conforming Manifest validator MUST implement the validation procedure defined in Section 18 in full, without omitting any applicable step.

A conforming Manifest validator MUST reject a Manifest whenever any applicable validation step fails.

## 22.4 Conformance Independence

Conformance to this specification SHALL be evaluated independently of any specific programming language, framework, or certification tooling implementation.

## 22.5 Conformance Invariants

CM-CONF-001

Conformance is defined separately for Manifest producers and Manifest validators.

CM-CONF-002

A conforming producer MUST NOT emit Manifests that fail their own declared Schema Version's validation rules.

CM-CONF-003

A conforming validator MUST implement fail-closed validation in full.

CM-CONF-004

Conformance MUST remain framework-neutral and implementation-independent.

---

# 23. Requirement Identifier Registry

## 23.1 Purpose

This section documents the identifier namespace used by this specification's normative requirement identifiers, consistent with the namespace convention established by MCC-EB-001, Section 23.

## 23.2 Namespace Convention

Every normative requirement identifier defined by this specification SHALL be prefixed with `CM-`, followed by a section-scoped category tag, followed by a three-digit sequence number.

## 23.3 Registered Prefixes

The following category tags are defined by this specification:

- `CM-SCHEMA-` — Manifest Schema (Section 10)
- `CM-RFLD-` — Required Fields (Section 11)
- `CM-OPTF-` — Optional Fields (Section 12)
- `CM-HASH-` — Hash References (Section 13)
- `CM-EBREF-` — Evidence Bundle References (Section 14)
- `CM-META-` — Certification Metadata (Section 15)
- `CM-VSN-` — Versioning Rules (Section 16)
- `CM-COMPAT-` — Compatibility Rules (Section 17)
- `CM-VAL-` — Validation Rules (Section 18)
- `CM-SEC-` — Security Considerations (Section 19)
- `CM-EXT-` — Extension Model (Section 20)
- `CM-CONF-` — Conformance Requirements (Section 22)

## 23.4 Registry Requirements

Requirement identifiers under this specification's `CM-` namespace SHALL be globally unique.

A future revision of this specification MUST NOT reuse a retired identifier for a different requirement.

A future revision of this specification MUST NOT introduce a new category tag that collides with a prefix already registered by MCC-CP-001 or MCC-EB-001.

## 23.5 Registry Invariants

CM-RID-001

All identifiers defined by this specification MUST use the `CM-` namespace prefix.

CM-RID-002

Identifiers within the `CM-` namespace MUST be globally unique.

CM-RID-003

Retired identifiers MUST NOT be reassigned to a different requirement.

CM-RID-004

New category tags MUST NOT collide with prefixes already registered by another MCC specification.

---

# 24. References

## 24.1 Normative References

- RFC 2119, "Key words for use in RFCs to Indicate Requirement Levels"
- RFC 8174, "Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words"
- MCC-CP-001, "Official Certification Program Specification"
- MCC-EB-001, "Evidence Bundle Specification"

## 24.2 Informative References

- MCC-TC-001, "Technical Certificate Specification" (planned)

## 24.3 Reference Invariants

CM-REF-001

Normative references SHALL identify only documents required to interpret this specification's normative requirements.

CM-REF-002

Informative references SHALL NOT define normative behavior.

CM-REF-003

References to planned specifications MUST be clearly marked as informative until those specifications are published.
