# MCC-TC-001

# Technical Certificate Specification

Document ID: MCC-TC-001

Version: Draft v0.1

Status: Draft

Category: Normative Specification

Applies To: MCC Technical Certificates

Language: English (Normative)

---

# Status of This Specification

This document is normative.

The key words MUST, MUST NOT, REQUIRED, SHALL, SHALL NOT, SHOULD, SHOULD NOT, RECOMMENDED, MAY and OPTIONAL in this specification are to be interpreted as described in RFC 2119 and RFC 8174.

This specification defines the normative Certificate model, schema, cryptographic integrity, signature, verification, trust, revocation, and conformance requirements for MCC Technical Certificates, as referenced by MCC-CP-001.

Reference implementations are informative unless explicitly stated otherwise.

---

# Abstract

A Technical Certificate is the authoritative, signed record of a successful MCC certification outcome for a Certification Subject.

This specification defines the normative Certificate model, its schema and required content, how it identifies its subject and issuer, its validity and revocation model, its cryptographic integrity and signature requirements, its verification procedure, its trust model, and its conformance requirements.

A Technical Certificate SHALL remain framework-neutral and implementation-independent, and SHALL be independently verifiable by a party holding only the Certificate, a recognized Trust Anchor, and this specification.

A Technical Certificate is a certification-program artifact. It is not, and SHALL NOT be interpreted as, a runtime execution authorization. Runtime governance behavior (ALLOW, DENY, ESCALATE, CONSTRAIN) belongs exclusively to MCC-Core runtime governance and is out of scope for this specification.

---

# 1. Purpose

The purpose of this specification is to define a single normative Technical Certificate format that satisfies the requirements defined by MCC-CP-001, Section 16 (Technical Certificate Requirements).

This specification exists so that:

- a successful certification outcome can be expressed as a single authoritative, cryptographically verifiable record, independent of any certification tooling implementation;
- a third party can verify a Technical Certificate's authenticity, integrity, and current validity without trusting the environment that produced it;
- a Technical Certificate can be reliably traced to the Certification Subject, specification version, Certification Manifest, and Evidence Bundle that substantiate it.

This specification defines the concrete artifact referenced by the term "Technical Certificate" in MCC-CP-001, Section 4 (Terminology).

Goals of this specification are:

- **Framework Neutrality.** The Certificate format MUST remain independent of any particular framework, programming language, or certification tooling implementation.
- **Authoritative Representation.** A Technical Certificate MUST represent the authoritative outcome of a successful certification, and MUST NOT be issuable for an unsuccessful certification.
- **Independent Verifiability.** A third party MUST be able to verify a Certificate's authenticity, integrity, and current validity using only the Certificate, a recognized Trust Anchor, and this specification.
- **Traceability.** A Technical Certificate MUST remain traceable to the Certification Subject, the specification version, the Certification Manifest, and the Evidence Bundle that substantiate it.
- **Long-Term Stability.** The Certificate format SHOULD evolve through versioned revisions of this specification while preserving compatibility whenever practical.

---

# 2. Scope

This specification defines:

- the Technical Certificate model and its role in certification;
- the normative Certificate Schema;
- Certificate Identity;
- Required Fields and Optional Fields;
- Subject Identification;
- Certification Result Representation;
- Issuer Information;
- Validity Period;
- the Revocation Model;
- Cryptographic Integrity;
- Signature Requirements;
- the Verification Procedure;
- the Trust Model;
- Compatibility and Versioning rules;
- security considerations applicable to Technical Certificates;
- the extension model for future Certificate content;
- conformance requirements for Certificate issuers and verifiers.

This specification does NOT define:

- the certification model, lifecycle, or pipeline (defined by MCC-CP-001);
- the Evidence Bundle structure or integrity model (defined by MCC-EB-001);
- the Certification Manifest schema (defined by MCC-CM-001);
- adapter, gateway, or SDK implementations;
- storage, transport, or distribution mechanisms for Certificates;
- a specific trust anchor distribution or key management mechanism;
- runtime execution semantics or runtime governance behavior (ALLOW, DENY, ESCALATE, CONSTRAIN), which belong exclusively to MCC-Core runtime governance;
- business-specific or domain-specific certificate content.

---

# 3. Certificate Model

## 3.1 Terminology

Technical Certificate
: The authoritative, signed record of a successful certification outcome, as defined by this specification and referenced by MCC-CP-001, Section 4 and Section 16.

Certificate Identity
: The set of fields that uniquely identify a Technical Certificate, independent of its content.

Issuer
: The Certification Authority, as defined by MCC-CP-001, Section 7.1, that signs and issues a Technical Certificate.

Subject
: The Certification Subject, as defined by MCC-CP-001, Section 7.2, to which a Technical Certificate applies.

Validity Period
: The interval, beginning at issuance, during which a Technical Certificate is considered current absent revocation.

Trust Anchor
: A verification key, associated with an Issuer, that a verifier relies upon to authenticate a Technical Certificate's signature.

Revocation
: The act, subsequent to issuance, of declaring a previously valid Technical Certificate no longer current.

Certificate Schema Version
: The version identifier of the Technical Certificate format itself, distinct from the version of MCC-CP-001, the Evidence Bundle Schema Version, and the Manifest Schema Version.

## 3.2 Role in Certification

A Technical Certificate is issued during the Technical Certificate Issuance step of the Certification Lifecycle defined in MCC-CP-001, Section 8.7, only after the Certification Decision defined in MCC-CP-001, Sections 8.6 and 9.6, is PASS.

A Technical Certificate SHALL NOT be issued where the Certification Decision is FAIL.

## 3.3 Relationship to Other Certification Artifacts

A Technical Certificate MUST reference exactly one Certification Manifest, as defined by MCC-CM-001.

A Technical Certificate is traceable to the Evidence Bundle that substantiates its Certification Manifest transitively, through that Manifest's Evidence Bundle Reference as defined by MCC-CM-001, Section 14. This transitive path satisfies the traceability requirement of MCC-CP-001, Section 16.5.

## 3.4 Distinction from Runtime Governance Artifacts

A Technical Certificate is a certification-program artifact that attests to conformance with MCC specifications. It is not an execution authorization, decision token, or gate-signal within MCC-Core runtime governance.

The verdicts ALLOW, DENY, ESCALATE, and CONSTRAIN, and the runtime Decision Token signing and gate enforcement mechanisms that produce and consume them, are entirely out of scope for this specification and remain exclusive to MCC-Core runtime governance.

## 3.5 Certificate Model Invariants

TC-MODEL-001

A Technical Certificate MUST represent exactly one successful (PASS) certification outcome.

TC-MODEL-002

A Technical Certificate MUST reference exactly one Certification Manifest.

TC-MODEL-003

A Technical Certificate MUST NOT be interpreted or used as a runtime execution authorization.

TC-MODEL-004

A Technical Certificate MUST remain traceable, directly or transitively, to the Certification Subject, specification version, Certification Manifest, and Evidence Bundle.

---

# 4. Certificate Schema

## 4.1 Purpose

The Certificate Schema defines the normative top-level structure of a Technical Certificate: the set of fields it is composed of and how those fields are grouped.

## 4.2 Top-Level Structure

A Technical Certificate SHALL be a single structured, machine-readable document composed of the following field groups:

- Certificate Identity, per Section 5;
- Subject Identification, per Section 8;
- Certification Result Representation, per Section 9;
- Issuer Information, per Section 10;
- Validity Period, per Section 11;
- Manifest Reference, per Section 6;
- Signature, per Section 14;
- Optional Fields, per Section 7;
- Extension fields, per Section 20, where present.

## 4.3 Field Typing

Every Certificate field MUST have a defined type consistent with this specification: identifier, string, timestamp, enumerated value, Hash Reference, or signature value.

Certificate fields MUST NOT be ambiguous as to type.

## 4.4 Canonical Form

For any purpose requiring a Digest or signature over a Technical Certificate, the data covered MUST first be reduced to a deterministic Canonical Form, consistent with the Canonical Form requirement of MCC-EB-001, Section 13.2 and MCC-CM-001, Section 10.4.

The Canonical Form used for signing MUST exclude the Signature field itself.

## 4.5 Certificate Schema Invariants

TC-SCHEMA-001

A Technical Certificate MUST be a single structured, machine-readable document.

TC-SCHEMA-002

Every Certificate field MUST have an unambiguous, defined type.

TC-SCHEMA-003

The top-level field groups defined in Section 4.2 MUST all be present, except where explicitly marked optional.

TC-SCHEMA-004

Signature computation MUST use a deterministic Canonical Form that excludes the Signature field.

TC-SCHEMA-005

The Certificate Schema MUST remain independent of any specific serialization technology.

---

# 5. Certificate Identity

## 5.1 Purpose

Certificate Identity is the set of fields that uniquely identify a Technical Certificate, independent of its content or subject.

## 5.2 Identity Fields

Every Technical Certificate MUST include:

- a certificate identifier, globally unique among Technical Certificates issued by the same Issuer;
- the Certificate Schema Version;
- the MCC-CP-001 specification version under which the underlying certification was performed.

## 5.3 Identifier Stability

A certificate identifier, once assigned, MUST NOT be reused for a different Technical Certificate, including after revocation of the original.

A revalidation that produces a new certification result MUST be issued as a new Technical Certificate with a new certificate identifier, consistent with MCC-CP-001, Sections 8.9 and 17.4.

## 5.4 Certificate Identity Invariants

TC-ID-001

Every Technical Certificate MUST have a globally unique certificate identifier.

TC-ID-002

Certificate identifiers MUST NOT be reused, including after revocation.

TC-ID-003

A revalidation MUST produce a new Technical Certificate with a new certificate identifier.

---

# 6. Required Fields

## 6.1 Purpose

Required Fields are the fields that MUST be present in every conforming Technical Certificate.

## 6.2 Baseline Required Fields

Consistent with MCC-CP-001, Section 16.2, every Technical Certificate MUST include:

- certificate identifier;
- Certification Subject identifier;
- specification version;
- certification result;
- certified capability profiles;
- Certification Manifest reference;
- Evidence Bundle reference (satisfied transitively per Section 3.3);
- issuance timestamp.

## 6.3 Additional Required Fields

In addition to Section 6.2, every Technical Certificate MUST include:

- Issuer identity, per Section 10;
- Validity Period fields, per Section 11;
- a Signature, per Section 14.

## 6.4 Field Presence Rule

A Technical Certificate MUST NOT omit a Required Field. A Certificate that omits any Required Field MUST be rejected under Section 15.

## 6.5 Required Fields Invariants

TC-RFLD-001

All fields listed in Section 6.2 MUST be present.

TC-RFLD-002

Issuer identity, Validity Period fields, and a Signature MUST be present.

TC-RFLD-003

A Certificate omitting any Required Field MUST be rejected.

---

# 7. Optional Fields

## 7.1 Purpose

Optional Fields are fields that MAY be present to provide additional, non-mandatory information.

## 7.2 Defined Optional Fields

A Technical Certificate MAY include:

- a human-readable label or description;
- references to superseded Technical Certificates from prior certification runs of the same Certification Subject;
- free-form annotations, subject to Section 19.4 (Sensitive Data).

## 7.3 Optional Field Constraints

An Optional Field, where present, MUST conform to the type rules of Section 4.3.

The absence of an Optional Field MUST NOT be treated as a validation failure.

An Optional Field MUST NOT be used to satisfy a Required Field obligation defined in Section 6.

## 7.4 Optional Fields Invariants

TC-OPTF-001

Optional Fields MAY be omitted without affecting Certificate validity.

TC-OPTF-002

Optional Fields, where present, MUST conform to defined type rules.

TC-OPTF-003

Optional Fields MUST NOT substitute for Required Fields.

---

# 8. Subject Identification

## 8.1 Purpose

Subject Identification defines how a Technical Certificate unambiguously identifies the Certification Subject to which it applies.

## 8.2 Subject Field

A Technical Certificate MUST identify exactly one Certification Subject, using the Certification Subject identifier defined by MCC-CP-001, Section 7.2.

A Technical Certificate MUST NOT apply to more than one Certification Subject.

## 8.3 Subject Consistency

The Certification Subject identified by a Technical Certificate MUST match the Certification Subject identified by the Certification Manifest it references.

A mismatch MUST cause verification to fail under Section 15.

## 8.4 Subject Identification Invariants

TC-SUBJ-001

A Technical Certificate MUST identify exactly one Certification Subject.

TC-SUBJ-002

The Certificate's Subject MUST match its referenced Manifest's Subject.

TC-SUBJ-003

A Subject mismatch MUST cause verification failure.

---

# 9. Certification Result Representation

## 9.1 Purpose

Certification Result Representation defines how a Technical Certificate records the certification outcome it attests to.

## 9.2 Result Value

A Technical Certificate MUST record its certification result as exactly PASS, consistent with MCC-CP-001, Sections 8.6 and 9.6, and Section 3.2 of this specification.

A Technical Certificate MUST NOT record a certification result of FAIL. No Certificate model exists for a FAIL outcome, since Certificates are never issued for a FAIL certification result.

## 9.3 Result Consistency

The certification result recorded by a Technical Certificate MUST match the certification result recorded by the Certification Manifest it references.

A mismatch MUST cause verification to fail under Section 15.

## 9.4 Certified Capability Profiles

A Technical Certificate MUST record the capability profiles verified during certification, consistent with MCC-CP-001, Section 11.6.

A capability profile MUST NOT appear as certified on a Technical Certificate unless it was verified during the certification the Certificate attests to.

## 9.5 Certification Result Representation Invariants

TC-RES-001

The certification result field MUST be present and MUST be PASS.

TC-RES-002

The Certificate's result MUST match its referenced Manifest's result.

TC-RES-003

Certified capability profiles MUST be limited to those actually verified.

---

# 10. Issuer Information

## 10.1 Purpose

Issuer Information identifies the Certification Authority, as defined by MCC-CP-001, Section 7.1, that issued a Technical Certificate.

## 10.2 Issuer Fields

A Technical Certificate MUST identify its Issuer by a stable Issuer identifier associated with a Trust Anchor, as defined by Section 16.

## 10.3 Issuer Authority

A Technical Certificate MUST NOT be considered validly issued unless its Issuer is recognized as the Certification Authority under MCC-CP-001, Section 7.1, at the time of verification.

## 10.4 Issuer Information Invariants

TC-ISS-001

A Technical Certificate MUST identify its Issuer.

TC-ISS-002

The Issuer identifier MUST be associated with a resolvable Trust Anchor.

TC-ISS-003

An unrecognized Issuer MUST cause verification to fail.

---

# 11. Validity Period

## 11.1 Purpose

The Validity Period defines the interval during which a Technical Certificate is considered current, absent revocation.

## 11.2 Issuance Timestamp

Every Technical Certificate MUST record an issuance timestamp.

A Technical Certificate MUST NOT be considered valid before its issuance timestamp.

## 11.3 Expiration

A Technical Certificate MAY declare an explicit expiration timestamp.

Where no expiration timestamp is declared, a Technical Certificate SHALL remain valid indefinitely, subject only to revocation under Section 12.

Where an expiration timestamp is declared, a Technical Certificate MUST NOT be considered valid after that timestamp.

## 11.4 Validity Period Invariants

TC-VALID-001

Every Technical Certificate MUST record an issuance timestamp.

TC-VALID-002

A Certificate MUST NOT be valid before its issuance timestamp.

TC-VALID-003

An expired Certificate, where an expiration timestamp is declared and passed, MUST NOT be treated as valid.

TC-VALID-004

Absence of an expiration timestamp MUST NOT be treated as a validation failure.

---

# 12. Revocation Model

## 12.1 Purpose

The Revocation Model defines how a previously valid Technical Certificate is declared no longer current, consistent with the Revoked state defined by MCC-CP-001, Appendix A.

## 12.2 Immutability and Revocation

A Technical Certificate MUST remain immutable after issuance, consistent with MCC-CP-001, Section 16.4.

Revocation SHALL NOT be represented by modifying a Technical Certificate's own content. Revocation SHALL be represented by an external Revocation Record.

## 12.3 Revocation Record

A Revocation Record MUST identify:

- the certificate identifier of the revoked Technical Certificate;
- the revocation timestamp;
- the Issuer that authorized the revocation.

A Revocation Record MAY include a revocation reason.

## 12.4 Revocation Authority

A Technical Certificate MUST NOT be revoked by any party other than the Issuer that issued it, or an entity the Issuer has designated in accordance with the Trust Model defined in Section 16.

## 12.5 Revocation Effect

Once a valid Revocation Record exists for a Technical Certificate, that Certificate MUST NOT be treated as currently valid regardless of its Validity Period under Section 11.

A revoked Technical Certificate's content, and the historical fact that it was issued, MUST remain available for audit and traceability, consistent with MCC-CP-001, Appendix A, STATE-005.

## 12.6 Revocation Check Requirement

A verifier MUST check for the existence of a valid Revocation Record for a Technical Certificate before treating that Certificate as currently valid.

This specification does NOT define a specific revocation registry technology or distribution mechanism; it defines only the normative content and effect of a Revocation Record.

## 12.7 Revocation Model Invariants

TC-REV-001

A Technical Certificate MUST NOT be mutated to represent revocation.

TC-REV-002

Revocation MUST be represented by an external Revocation Record.

TC-REV-003

A Revocation Record MUST identify the certificate identifier, revocation timestamp, and authorizing Issuer.

TC-REV-004

Only the Issuer, or its designated authority under the Trust Model, MUST be able to produce a valid Revocation Record.

TC-REV-005

A verifier MUST check for revocation before treating a Certificate as valid.

TC-REV-006

Revoked Certificates MUST remain available for audit and traceability.

---

# 13. Cryptographic Integrity

## 13.1 Purpose

Cryptographic Integrity defines how the contents of a Technical Certificate are protected against undetected modification, independent of the Signature Requirements defined in Section 14.

## 13.2 Digest Requirements

Where a Technical Certificate includes a Hash Reference to its Certification Manifest, that Hash Reference MUST use a collision-resistant cryptographic hash function, consistent with MCC-EB-001, Section 13.3 and MCC-CM-001, Section 13.3.

## 13.3 Integrity Scope

Cryptographic Integrity, in this specification, refers to the binding between a Technical Certificate and the Certification Manifest it references.

The integrity of the Technical Certificate's own content as a whole is provided by the Signature Requirements defined in Section 14, not by a separate self-digest.

## 13.4 Cryptographic Integrity Invariants

TC-HASH-001

A Hash Reference to the Certification Manifest MUST use a collision-resistant hash algorithm.

TC-HASH-002

Manifest binding MUST be independently recomputable and verifiable.

TC-HASH-003

Whole-Certificate integrity MUST be provided by its Signature, not by a separate mechanism.

---

# 14. Signature Requirements

## 14.1 Purpose

Signature Requirements define how a Technical Certificate is cryptographically signed by its Issuer, providing authenticity and integrity for the Certificate as a whole.

## 14.2 Signature Algorithm

The signature algorithm used to sign a Technical Certificate MUST be an asymmetric (public-key) digital signature scheme.

The signature algorithm MUST NOT be a symmetric-key or shared-secret authentication mechanism, including HMAC.

Ed25519, as defined by RFC 8032, is RECOMMENDED as the reference signature algorithm. This specification does not preclude other collision-resistant asymmetric signature schemes.

## 14.3 Signature Coverage

A Technical Certificate's Signature MUST cover the complete Canonical Form of the Certificate, excluding the Signature field itself, as defined by Section 4.4.

A Signature MUST become invalid if any covered field is modified after signing.

## 14.4 Signature Declaration

A Technical Certificate MUST declare the signature algorithm used and the Issuer identity associated with the signing key.

## 14.5 Signature Requirements Invariants

TC-SIG-001

Every Technical Certificate MUST be signed using an asymmetric digital signature scheme.

TC-SIG-002

HMAC and other symmetric-key authentication mechanisms MUST NOT be used to sign a Technical Certificate.

TC-SIG-003

A Signature MUST cover the complete Canonical Form of the Certificate excluding the Signature field.

TC-SIG-004

A Certificate MUST declare its signature algorithm and Issuer identity.

TC-SIG-005

Modification of any signed field MUST invalidate the Signature.

---

# 15. Verification Procedure

## 15.1 Purpose

This section defines the normative procedure and criteria a verifier MUST apply to determine whether a Technical Certificate is currently valid.

## 15.2 Structural Verification

A verifier MUST verify that the Certificate conforms to the Certificate Schema defined in Section 4 and contains all Required Fields defined in Section 6.

A Certificate that fails structural verification MUST be rejected without further processing.

## 15.3 Signature Verification

A verifier MUST verify the Certificate's Signature against a Trust Anchor associated with the declared Issuer, consistent with Section 16.

A Certificate with an invalid or unverifiable Signature MUST be rejected.

## 15.4 Manifest Reference Verification

A verifier MUST verify the Manifest Reference, including its Hash Reference, against the referenced Certification Manifest, consistent with MCC-CM-001, Section 18.

A Certificate whose Manifest Reference cannot be verified MUST be rejected.

## 15.5 Subject and Result Consistency Verification

A verifier MUST verify Subject consistency per Section 8.3 and Certification Result consistency per Section 9.3.

## 15.6 Validity and Revocation Verification

A verifier MUST verify that the Certificate is within its Validity Period per Section 11 and MUST check for a Revocation Record per Section 12.6.

A Certificate that is expired or revoked MUST NOT be treated as currently valid, even if all other verification steps succeed.

## 15.7 Fail-Closed Verification

Verification SHALL be fail-closed: a Technical Certificate MUST be treated as invalid unless every applicable verification step in this section succeeds.

Partial or inconclusive verification results MUST NOT be treated as valid.

## 15.8 Verification Procedure Invariants

TC-VERIFY-001

Verification MUST be fail-closed.

TC-VERIFY-002

Structural verification MUST precede signature, manifest reference, and consistency verification.

TC-VERIFY-003

Signature verification MUST use a Trust Anchor associated with the declared Issuer.

TC-VERIFY-004

Validity and revocation MUST both be checked, independent of all other verification steps.

TC-VERIFY-005

A Certificate failing any verification step MUST be rejected in its entirety.

---

# 16. Trust Model

## 16.1 Purpose

The Trust Model defines how a verifier establishes and applies trust in an Issuer's signing key when verifying a Technical Certificate.

## 16.2 Trust Anchors

A Trust Anchor is a verification key associated with an Issuer that a verifier relies upon to authenticate a Technical Certificate's Signature.

A verifier MUST possess or obtain a set of Trust Anchors it recognizes through a mechanism outside the scope of this specification.

## 16.3 Trust Anchor Recognition

A Technical Certificate signed by a key that does not correspond to a Trust Anchor recognized by the verifier MUST NOT be treated as valid.

Recognition of a Trust Anchor MUST NOT be inferred from the Certificate itself; a Certificate MUST NOT be trusted merely because it declares an Issuer identity.

## 16.4 Trust Anchor Rotation and Revocation

Where an Issuer's signing key is rotated or revoked, a verifier MUST cease treating Technical Certificates signed with the superseded key as currently trusted for new verification, without invalidating the historical fact that they were issued.

This specification does NOT define the mechanism by which Trust Anchor rotation or revocation is communicated to verifiers.

## 16.5 Multiple Trust Domains

This specification permits multiple Issuers, and therefore multiple Trust Anchors, to coexist. A verifier MAY recognize more than one Trust Anchor.

A verifier MUST NOT treat a Technical Certificate as valid solely because it was signed by a key not among the verifier's recognized Trust Anchors, regardless of any other party's trust in that key.

## 16.6 Trust Model Invariants

TC-TRUST-001

A verifier MUST rely only on Trust Anchors it recognizes.

TC-TRUST-002

Trust MUST NOT be inferred from a Certificate's self-declared Issuer identity alone.

TC-TRUST-003

Trust Anchor rotation or revocation MUST NOT retroactively invalidate the historical record of issuance.

TC-TRUST-004

A verifier MAY recognize multiple Trust Anchors across multiple Issuers.

---

# 17. Compatibility

## 17.1 Purpose

Compatibility rules define how Certificate issuers and verifiers built against different revisions of this specification are expected to interoperate.

## 17.2 Backward Compatibility

A verifier supporting a given Certificate Schema Version SHOULD also support verifying Certificates declaring earlier Schema Versions where this specification's revision history states that compatibility is preserved.

## 17.3 Forward Compatibility

A verifier MUST NOT assume forward compatibility with a Certificate Schema Version it does not recognize.

An unrecognized Certificate Schema Version MUST be treated per Section 18.4 and Section 15.7, not silently accepted.

## 17.4 Cross-Specification Compatibility

A Technical Certificate MUST NOT be considered valid if it references a Manifest Schema Version that MCC-CM-001, as currently published, does not recognize.

## 17.5 Compatibility Invariants

TC-COMPAT-001

Compatibility claims between Certificate Schema Versions MUST be explicit, not assumed.

TC-COMPAT-002

Unrecognized Certificate Schema Versions MUST NOT be silently accepted.

TC-COMPAT-003

Certificate validity MUST account for the compatibility of any referenced Manifest Schema Version.

---

# 18. Versioning

## 18.1 Purpose

Versioning rules define how the Certificate Schema Version is declared, interpreted, and evolved, independently of MCC-CP-001, MCC-EB-001, and MCC-CM-001 versioning.

## 18.2 Schema Version Declaration

Every Technical Certificate MUST declare its Certificate Schema Version among its Identity fields.

The Certificate Schema Version MUST be immutable once assigned to a published revision of this specification.

## 18.3 Schema Version Scope

The Certificate Schema Version governs the Certificate Schema, Required Fields, Signature Requirements, and Verification Procedure defined by this specification.

The Certificate Schema Version is distinct from, and SHALL NOT be conflated with, the MCC-CP-001 specification version, the Evidence Bundle Schema Version, or the Manifest Schema Version referenced by a Certificate.

## 18.4 Version Evolution

A future revision of this specification MAY introduce a new Certificate Schema Version.

A verifier MUST reject a Technical Certificate declaring a Schema Version it does not recognize.

## 18.5 Versioning Invariants

TC-VSN-001

Every Technical Certificate MUST declare a Certificate Schema Version.

TC-VSN-002

Certificate Schema Versions MUST be immutable once published.

TC-VSN-003

Certificate Schema Version MUST be tracked independently of MCC-CP-001, MCC-EB-001, and MCC-CM-001 versions.

TC-VSN-004

An unrecognized Certificate Schema Version MUST cause verification to fail.

---

# 19. Security Considerations

## 19.1 Purpose

This section defines the threat model and security requirements applicable to Technical Certificates.

## 19.2 Threat Model

Verification of a Technical Certificate MUST assume:

- the Certificate MAY originate from an untrusted or compromised source;
- the Certificate MAY have been forged, tampered with, expired, or revoked;
- the environment that produced or transmitted the Certificate MUST NOT be trusted implicitly.

## 19.3 Forgery and Tamper Resistance

Forgery and tamper resistance are provided exclusively through Signature Verification, per Section 15.3, against a recognized Trust Anchor, per Section 16.

A verifier MUST NOT treat any Certificate content as authoritative prior to successful Signature Verification.

## 19.4 Sensitive Data

A Technical Certificate MUST NOT include secrets, credentials, or other sensitive material not required to represent the certification outcome.

Where underlying certification inputs contain sensitive material, Certificate fields MUST reference redacted or hashed representations rather than raw sensitive values, consistent with MCC-EB-001, Section 19.4 and MCC-CM-001, Section 19.4.

## 19.5 Runtime Governance Boundary

A Technical Certificate MUST NOT be used, by any implementation, as a substitute for a runtime governance decision. Possession of a valid Technical Certificate for a Certification Subject MUST NOT be treated as authorization to execute any runtime action governed by MCC-Core.

## 19.6 Security Invariants

TC-SEC-001

Certificate verification MUST assume an untrusted source.

TC-SEC-002

Forgery and tamper detection MUST rely on Signature Verification against a recognized Trust Anchor.

TC-SEC-003

Certificates MUST NOT contain secrets or credentials.

TC-SEC-004

Sensitive underlying data MUST be redacted or hashed before inclusion in a Certificate field.

TC-SEC-005

A valid Technical Certificate MUST NOT be treated as a runtime execution authorization.

---

# 20. Extension Model

## 20.1 Purpose

The Extension Model defines how future content MAY be added to a Technical Certificate without breaking verifiers built against an earlier revision of this specification.

## 20.2 Extension Points

Fields beyond those defined by Sections 4 through 11 are permitted only as explicitly declared extensions.

Extensions MUST be declared and identified as such within the Certificate.

## 20.3 Extension Constraints

An extension MUST NOT alter the meaning of any Required Field, the Signature, or the Manifest Reference defined by this specification.

An extension MUST be covered by the Certificate's Signature like any other Certificate content.

A verifier that does not recognize a declared extension MUST ignore that extension's content without failing verification, provided all other verification steps in Section 15 are satisfied.

## 20.4 Extension Model Invariants

TC-EXT-001

Extensions MUST be explicitly declared within the Certificate.

TC-EXT-002

Extensions MUST NOT redefine the meaning of Required Fields, the Signature, or the Manifest Reference.

TC-EXT-003

Extension content MUST be covered by the Certificate's Signature.

TC-EXT-004

Unrecognized extensions MUST be ignored, not treated as verification failures.

---

# 21. Conformance Requirements

## 21.1 Purpose

This section defines what it means for a Certificate issuer or a Certificate verifier to conform to this specification.

## 21.2 Conforming Certificate Issuer

A conforming Certificate issuer MUST issue Technical Certificates satisfying Sections 4 through 14 of this specification for the Certificate Schema Version it declares.

A conforming Certificate issuer MUST NOT issue a Technical Certificate for a certification result other than PASS.

A conforming Certificate issuer MUST NOT issue a Technical Certificate that fails verification under Section 15 against its own declared Schema Version.

## 21.3 Conforming Certificate Verifier

A conforming Certificate verifier MUST implement the verification procedure defined in Section 15 in full, without omitting any applicable step, including the Revocation Check Requirement of Section 12.6.

A conforming Certificate verifier MUST reject a Technical Certificate whenever any applicable verification step fails.

## 21.4 Conformance Independence

Conformance to this specification SHALL be evaluated independently of any specific programming language, framework, or certification tooling implementation.

## 21.5 Conformance Invariants

TC-CONF-001

Conformance is defined separately for Certificate issuers and Certificate verifiers.

TC-CONF-002

A conforming issuer MUST NOT issue Certificates for a non-PASS result.

TC-CONF-003

A conforming verifier MUST implement fail-closed verification in full, including revocation checking.

TC-CONF-004

Conformance MUST remain framework-neutral and implementation-independent.

---

# 22. Requirement Identifier Registry

## 22.1 Purpose

This section documents the identifier namespace used by this specification's normative requirement identifiers, consistent with the namespace convention established by MCC-EB-001, Section 23 and MCC-CM-001, Section 23.

## 22.2 Namespace Convention

Every normative requirement identifier defined by this specification SHALL be prefixed with `TC-`, followed by a section-scoped category tag, followed by a three-digit sequence number.

## 22.3 Registered Prefixes

The following category tags are defined by this specification:

- `TC-MODEL-` — Certificate Model (Section 3)
- `TC-SCHEMA-` — Certificate Schema (Section 4)
- `TC-ID-` — Certificate Identity (Section 5)
- `TC-RFLD-` — Required Fields (Section 6)
- `TC-OPTF-` — Optional Fields (Section 7)
- `TC-SUBJ-` — Subject Identification (Section 8)
- `TC-RES-` — Certification Result Representation (Section 9)
- `TC-ISS-` — Issuer Information (Section 10)
- `TC-VALID-` — Validity Period (Section 11)
- `TC-REV-` — Revocation Model (Section 12)
- `TC-HASH-` — Cryptographic Integrity (Section 13)
- `TC-SIG-` — Signature Requirements (Section 14)
- `TC-VERIFY-` — Verification Procedure (Section 15)
- `TC-TRUST-` — Trust Model (Section 16)
- `TC-COMPAT-` — Compatibility (Section 17)
- `TC-VSN-` — Versioning (Section 18)
- `TC-SEC-` — Security Considerations (Section 19)
- `TC-EXT-` — Extension Model (Section 20)
- `TC-CONF-` — Conformance Requirements (Section 21)

## 22.4 Registry Requirements

Requirement identifiers under this specification's `TC-` namespace SHALL be globally unique.

A future revision of this specification MUST NOT reuse a retired identifier for a different requirement.

A future revision of this specification MUST NOT introduce a new category tag that collides with a prefix already registered by MCC-CP-001, MCC-EB-001, or MCC-CM-001.

## 22.5 Registry Invariants

TC-RID-001

All identifiers defined by this specification MUST use the `TC-` namespace prefix.

TC-RID-002

Identifiers within the `TC-` namespace MUST be globally unique.

TC-RID-003

Retired identifiers MUST NOT be reassigned to a different requirement.

TC-RID-004

New category tags MUST NOT collide with prefixes already registered by another MCC specification.

---

# 23. Normative References

- RFC 2119, "Key words for use in RFCs to Indicate Requirement Levels"
- RFC 8174, "Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words"
- RFC 8032, "Edwards-Curve Digital Signature Algorithm (EdDSA)"
- MCC-CP-001, "Official Certification Program Specification"
- MCC-EB-001, "Evidence Bundle Specification"
- MCC-CM-001, "Certification Manifest Specification"

---

# 24. Informative References

No informative references are defined at this time.

Deployment guidance, trust anchor distribution profiles, and revocation registry implementations that MAY accompany this specification are reference material and remain outside its normative scope.
