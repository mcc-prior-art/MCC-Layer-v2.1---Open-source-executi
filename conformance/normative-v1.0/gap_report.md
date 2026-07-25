# MCC Normative v1.0 — Gap Report

Auto-generated. Do not hand-edit — regenerate with:

```
python -m mcc_conformance generate
```

Total non-CONFORMANT requirements: 810 of 810.

## CM-COMPAT-001

- Specification / section: MCC-CM-001 / 17. Compatibility Rules / 17.6 Compatibility Invariants
- Status: PARTIAL
- Requirement: Compatibility claims between Manifest Schema Versions MUST be explicit, not assumed.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: MANIFEST_SCHEMA_VERSION is tracked independently of contract_version and compliance_suite_version, the same independent-versioning model this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## CM-COMPAT-002

- Specification / section: MCC-CM-001 / 17. Compatibility Rules / 17.6 Compatibility Invariants
- Status: PARTIAL
- Requirement: Unrecognized Manifest Schema Versions MUST NOT be silently accepted.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: MANIFEST_SCHEMA_VERSION is tracked independently of contract_version and compliance_suite_version, the same independent-versioning model this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## CM-COMPAT-003

- Specification / section: MCC-CM-001 / 17. Compatibility Rules / 17.6 Compatibility Invariants
- Status: PARTIAL
- Requirement: Breaking changes MUST introduce a new Manifest Schema Version.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: MANIFEST_SCHEMA_VERSION is tracked independently of contract_version and compliance_suite_version, the same independent-versioning model this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## CM-COMPAT-004

- Specification / section: MCC-CM-001 / 17. Compatibility Rules / 17.6 Compatibility Invariants
- Status: PARTIAL
- Requirement: Manifest validity MUST account for the compatibility of any referenced Evidence Bundle Schema Version.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: MANIFEST_SCHEMA_VERSION is tracked independently of contract_version and compliance_suite_version, the same independent-versioning model this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## CM-CONF-001

- Specification / section: MCC-CM-001 / 22. Conformance Requirements / 22.5 Conformance Invariants
- Status: GAP
- Requirement: Conformance is defined separately for Manifest producers and Manifest validators.
- Existing implementation: None
- Missing implementation behavior: Full requirement not implemented.
- Missing test coverage: No test exists for this requirement.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: No producer/validator conformance-declaration mechanism specific to this specification's Manifest Schema Version was found.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## CM-CONF-002

- Specification / section: MCC-CM-001 / 22. Conformance Requirements / 22.5 Conformance Invariants
- Status: GAP
- Requirement: A conforming producer MUST NOT emit Manifests that fail their own declared Schema Version's validation rules.
- Existing implementation: None
- Missing implementation behavior: Full requirement not implemented.
- Missing test coverage: No test exists for this requirement.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: No producer/validator conformance-declaration mechanism specific to this specification's Manifest Schema Version was found.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## CM-CONF-003

- Specification / section: MCC-CM-001 / 22. Conformance Requirements / 22.5 Conformance Invariants
- Status: GAP
- Requirement: A conforming validator MUST implement fail-closed validation in full.
- Existing implementation: None
- Missing implementation behavior: Full requirement not implemented.
- Missing test coverage: No test exists for this requirement.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: No producer/validator conformance-declaration mechanism specific to this specification's Manifest Schema Version was found.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## CM-CONF-004

- Specification / section: MCC-CM-001 / 22. Conformance Requirements / 22.5 Conformance Invariants
- Status: GAP
- Requirement: Conformance MUST remain framework-neutral and implementation-independent.
- Existing implementation: None
- Missing implementation behavior: Full requirement not implemented.
- Missing test coverage: No test exists for this requirement.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: No producer/validator conformance-declaration mechanism specific to this specification's Manifest Schema Version was found.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## CM-EBREF-001

- Specification / section: MCC-CM-001 / 14. Evidence Bundle References / 14.5 Evidence Bundle Reference Invariants
- Status: GAP
- Requirement: A Certification Manifest MUST reference exactly one primary Evidence Bundle.
- Existing implementation: None
- Missing implementation behavior: Full requirement not implemented.
- Missing test coverage: No test exists for this requirement.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: certifications/manifest.json references compliance vectors and adapters, not an Evidence Bundle as MCC-EB-001 defines it; no Evidence-Bundle-Reference-shaped field exists.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## CM-EBREF-002

- Specification / section: MCC-CM-001 / 14. Evidence Bundle References / 14.5 Evidence Bundle Reference Invariants
- Status: GAP
- Requirement: The primary Evidence Bundle Reference MUST include the Evidence Bundle identifier, Schema Version, and a Hash Reference.
- Existing implementation: None
- Missing implementation behavior: Full requirement not implemented.
- Missing test coverage: No test exists for this requirement.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: certifications/manifest.json references compliance vectors and adapters, not an Evidence Bundle as MCC-EB-001 defines it; no Evidence-Bundle-Reference-shaped field exists.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## CM-EBREF-003

- Specification / section: MCC-CM-001 / 14. Evidence Bundle References / 14.5 Evidence Bundle Reference Invariants
- Status: GAP
- Requirement: Supplementary Evidence Bundle References MUST be distinguishable from the primary reference.
- Existing implementation: None
- Missing implementation behavior: Full requirement not implemented.
- Missing test coverage: No test exists for this requirement.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: certifications/manifest.json references compliance vectors and adapters, not an Evidence Bundle as MCC-EB-001 defines it; no Evidence-Bundle-Reference-shaped field exists.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## CM-EBREF-004

- Specification / section: MCC-CM-001 / 14. Evidence Bundle References / 14.5 Evidence Bundle Reference Invariants
- Status: GAP
- Requirement: An unverifiable primary Evidence Bundle Reference invalidates the Manifest.
- Existing implementation: None
- Missing implementation behavior: Full requirement not implemented.
- Missing test coverage: No test exists for this requirement.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: certifications/manifest.json references compliance vectors and adapters, not an Evidence Bundle as MCC-EB-001 defines it; no Evidence-Bundle-Reference-shaped field exists.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## CM-EXT-001

- Specification / section: MCC-CM-001 / 20. Extension Model / 20.4 Extension Model Invariants
- Status: GAP
- Requirement: Extensions MUST be explicitly declared within the Manifest.
- Existing implementation: None
- Missing implementation behavior: Full requirement not implemented.
- Missing test coverage: No test exists for this requirement.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: No extension-declaration mechanism (a way to mark additional fields as explicit, non-breaking extensions to a committed schema) was found anywhere in this repository for any artifact.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## CM-EXT-002

- Specification / section: MCC-CM-001 / 20. Extension Model / 20.4 Extension Model Invariants
- Status: GAP
- Requirement: Extensions MUST NOT redefine the meaning of Required Fields, Hash References, or Evidence Bundle References.
- Existing implementation: None
- Missing implementation behavior: Full requirement not implemented.
- Missing test coverage: No test exists for this requirement.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: No extension-declaration mechanism (a way to mark additional fields as explicit, non-breaking extensions to a committed schema) was found anywhere in this repository for any artifact.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## CM-EXT-003

- Specification / section: MCC-CM-001 / 20. Extension Model / 20.4 Extension Model Invariants
- Status: GAP
- Requirement: Unrecognized extensions MUST be ignored, not treated as validation failures.
- Existing implementation: None
- Missing implementation behavior: Full requirement not implemented.
- Missing test coverage: No test exists for this requirement.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: No extension-declaration mechanism (a way to mark additional fields as explicit, non-breaking extensions to a committed schema) was found anywhere in this repository for any artifact.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## CM-HASH-001

- Specification / section: MCC-CM-001 / 13. Hash References / 13.5 Hash Reference Invariants
- Status: PARTIAL
- Requirement: A Hash Reference MUST identify a Digest, a hash algorithm, and the content it corresponds to.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: certifications/manifest.json binds evidence_digest / vector_manifest_digest (sha256, DIGEST_ALGORITHM) to the certification record, the same binding concept, but as bare digest strings rather than this section's required identifier+algorithm+content-pointer structured Hash Reference object.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## CM-HASH-002

- Specification / section: MCC-CM-001 / 13. Hash References / 13.5 Hash Reference Invariants
- Status: PARTIAL
- Requirement: Hash Reference algorithms MUST be collision-resistant.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: certifications/manifest.json binds evidence_digest / vector_manifest_digest (sha256, DIGEST_ALGORITHM) to the certification record, the same binding concept, but as bare digest strings rather than this section's required identifier+algorithm+content-pointer structured Hash Reference object.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## CM-HASH-003

- Specification / section: MCC-CM-001 / 13. Hash References / 13.5 Hash Reference Invariants
- Status: PARTIAL
- Requirement: Every Evidence Bundle Reference MUST include at least one Hash Reference.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: certifications/manifest.json binds evidence_digest / vector_manifest_digest (sha256, DIGEST_ALGORITHM) to the certification record, the same binding concept, but as bare digest strings rather than this section's required identifier+algorithm+content-pointer structured Hash Reference object.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## CM-HASH-004

- Specification / section: MCC-CM-001 / 13. Hash References / 13.5 Hash Reference Invariants
- Status: PARTIAL
- Requirement: Hash References MUST be independently recomputable and verifiable by a validator.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: certifications/manifest.json binds evidence_digest / vector_manifest_digest (sha256, DIGEST_ALGORITHM) to the certification record, the same binding concept, but as bare digest strings rather than this section's required identifier+algorithm+content-pointer structured Hash Reference object.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## CM-META-001

- Specification / section: MCC-CM-001 / 15. Certification Metadata / 15.6 Certification Metadata Invariants
- Status: PARTIAL
- Requirement: Certification Metadata MUST identify the Certification Subject and specification version.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: certifications/manifest.json records subject (adapter/adapter_key), specification version (contract_version), a Requirement-Result-like list (covered_invariants), and an overall status — the same metadata categories this section requires, under different names.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## CM-META-002

- Specification / section: MCC-CM-001 / 15. Certification Metadata / 15.6 Certification Metadata Invariants
- Status: PARTIAL
- Requirement: Certification Metadata MUST identify claimed and verified capability profiles.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: certifications/manifest.json records subject (adapter/adapter_key), specification version (contract_version), a Requirement-Result-like list (covered_invariants), and an overall status — the same metadata categories this section requires, under different names.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## CM-META-003

- Specification / section: MCC-CM-001 / 15. Certification Metadata / 15.6 Certification Metadata Invariants
- Status: PARTIAL
- Requirement: The certification result MUST be exactly one of PASS or FAIL.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: certifications/manifest.json records subject (adapter/adapter_key), specification version (contract_version), a Requirement-Result-like list (covered_invariants), and an overall status — the same metadata categories this section requires, under different names.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## CM-META-004

- Specification / section: MCC-CM-001 / 15. Certification Metadata / 15.6 Certification Metadata Invariants
- Status: PARTIAL
- Requirement: Every evaluated Certification Requirement MUST have a corresponding Requirement Result.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: certifications/manifest.json records subject (adapter/adapter_key), specification version (contract_version), a Requirement-Result-like list (covered_invariants), and an overall status — the same metadata categories this section requires, under different names.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## CM-META-005

- Specification / section: MCC-CM-001 / 15. Certification Metadata / 15.6 Certification Metadata Invariants
- Status: PARTIAL
- Requirement: Certification Metadata MUST include a generation timestamp.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: certifications/manifest.json records subject (adapter/adapter_key), specification version (contract_version), a Requirement-Result-like list (covered_invariants), and an overall status — the same metadata categories this section requires, under different names.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## CM-OPTF-001

- Specification / section: MCC-CM-001 / 12. Optional Fields / 12.4 Optional Fields Invariants
- Status: PARTIAL
- Requirement: Optional Fields MAY be omitted without affecting Manifest validity.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: certifications/manifest.json is a real, versioned (MANIFEST_SCHEMA_VERSION), digest-bound, structured certification record (subject/adapter, contract_version, status, evidence_digest, report_id) — the same kind of artifact this section describes, but with different field names/shape and scoped to adapters certified against the Integration Contract, not this specification's Manifest Schema.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## CM-OPTF-002

- Specification / section: MCC-CM-001 / 12. Optional Fields / 12.4 Optional Fields Invariants
- Status: PARTIAL
- Requirement: Optional Fields, where present, MUST conform to defined type rules.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: certifications/manifest.json is a real, versioned (MANIFEST_SCHEMA_VERSION), digest-bound, structured certification record (subject/adapter, contract_version, status, evidence_digest, report_id) — the same kind of artifact this section describes, but with different field names/shape and scoped to adapters certified against the Integration Contract, not this specification's Manifest Schema.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## CM-OPTF-003

- Specification / section: MCC-CM-001 / 12. Optional Fields / 12.4 Optional Fields Invariants
- Status: PARTIAL
- Requirement: Optional Fields MUST NOT substitute for Required Fields.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: certifications/manifest.json is a real, versioned (MANIFEST_SCHEMA_VERSION), digest-bound, structured certification record (subject/adapter, contract_version, status, evidence_digest, report_id) — the same kind of artifact this section describes, but with different field names/shape and scoped to adapters certified against the Integration Contract, not this specification's Manifest Schema.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## CM-OPTF-004

- Specification / section: MCC-CM-001 / 12. Optional Fields / 12.4 Optional Fields Invariants
- Status: PARTIAL
- Requirement: Undefined, unrecognized fields MUST be treated as extensions under Section 20, not as ad hoc Optional Fields.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: certifications/manifest.json is a real, versioned (MANIFEST_SCHEMA_VERSION), digest-bound, structured certification record (subject/adapter, contract_version, status, evidence_digest, report_id) — the same kind of artifact this section describes, but with different field names/shape and scoped to adapters certified against the Integration Contract, not this specification's Manifest Schema.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## CM-REF-001

- Specification / section: MCC-CM-001 / 24. References / 24.3 Reference Invariants
- Status: NOT_APPLICABLE
- Requirement: Normative references SHALL identify only documents required to interpret this specification's normative requirements.
- Existing implementation: None
- Missing implementation behavior: N/A (not an implementable requirement).
- Missing test coverage: No test exists for this requirement.
- Missing evidence: N/A
- Rationale: Interpretive, bibliographic, non-normative-by-design (explicitly marked informative/example), or document-self-referential statement. It does not describe a discrete, independently implementable system behavior.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: N/A

## CM-REF-002

- Specification / section: MCC-CM-001 / 24. References / 24.3 Reference Invariants
- Status: NOT_APPLICABLE
- Requirement: Informative references SHALL NOT define normative behavior.
- Existing implementation: None
- Missing implementation behavior: N/A (not an implementable requirement).
- Missing test coverage: No test exists for this requirement.
- Missing evidence: N/A
- Rationale: Interpretive, bibliographic, non-normative-by-design (explicitly marked informative/example), or document-self-referential statement. It does not describe a discrete, independently implementable system behavior.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: N/A

## CM-REF-003

- Specification / section: MCC-CM-001 / 24. References / 24.3 Reference Invariants
- Status: NOT_APPLICABLE
- Requirement: References to planned specifications MUST be clearly marked as informative until those specifications are published.
- Existing implementation: None
- Missing implementation behavior: N/A (not an implementable requirement).
- Missing test coverage: No test exists for this requirement.
- Missing evidence: N/A
- Rationale: Interpretive, bibliographic, non-normative-by-design (explicitly marked informative/example), or document-self-referential statement. It does not describe a discrete, independently implementable system behavior.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: N/A

## CM-RFLD-001

- Specification / section: MCC-CM-001 / 11. Required Fields / 11.5 Required Fields Invariants
- Status: PARTIAL
- Requirement: A manifest identifier MUST be present and unique to the certification run.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: certifications/manifest.json is a real, versioned (MANIFEST_SCHEMA_VERSION), digest-bound, structured certification record (subject/adapter, contract_version, status, evidence_digest, report_id) — the same kind of artifact this section describes, but with different field names/shape and scoped to adapters certified against the Integration Contract, not this specification's Manifest Schema.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## CM-RFLD-002

- Specification / section: MCC-CM-001 / 11. Required Fields / 11.5 Required Fields Invariants
- Status: PARTIAL
- Requirement: The Manifest Schema Version MUST be present.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: certifications/manifest.json is a real, versioned (MANIFEST_SCHEMA_VERSION), digest-bound, structured certification record (subject/adapter, contract_version, status, evidence_digest, report_id) — the same kind of artifact this section describes, but with different field names/shape and scoped to adapters certified against the Integration Contract, not this specification's Manifest Schema.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## CM-RFLD-003

- Specification / section: MCC-CM-001 / 11. Required Fields / 11.5 Required Fields Invariants
- Status: PARTIAL
- Requirement: The MCC-CP-001 specification version MUST be present.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: certifications/manifest.json is a real, versioned (MANIFEST_SCHEMA_VERSION), digest-bound, structured certification record (subject/adapter, contract_version, status, evidence_digest, report_id) — the same kind of artifact this section describes, but with different field names/shape and scoped to adapters certified against the Integration Contract, not this specification's Manifest Schema.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## CM-RFLD-004

- Specification / section: MCC-CM-001 / 11. Required Fields / 11.5 Required Fields Invariants
- Status: PARTIAL
- Requirement: The Certification Subject identifier MUST be present.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: certifications/manifest.json is a real, versioned (MANIFEST_SCHEMA_VERSION), digest-bound, structured certification record (subject/adapter, contract_version, status, evidence_digest, report_id) — the same kind of artifact this section describes, but with different field names/shape and scoped to adapters certified against the Integration Contract, not this specification's Manifest Schema.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## CM-RFLD-005

- Specification / section: MCC-CM-001 / 11. Required Fields / 11.5 Required Fields Invariants
- Status: PARTIAL
- Requirement: Certification requirements evaluated, certification result, evidence references, and generation timestamp MUST all be present.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: certifications/manifest.json is a real, versioned (MANIFEST_SCHEMA_VERSION), digest-bound, structured certification record (subject/adapter, contract_version, status, evidence_digest, report_id) — the same kind of artifact this section describes, but with different field names/shape and scoped to adapters certified against the Integration Contract, not this specification's Manifest Schema.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## CM-RFLD-006

- Specification / section: MCC-CM-001 / 11. Required Fields / 11.5 Required Fields Invariants
- Status: PARTIAL
- Requirement: Required Fields MUST be present regardless of certification outcome.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: certifications/manifest.json is a real, versioned (MANIFEST_SCHEMA_VERSION), digest-bound, structured certification record (subject/adapter, contract_version, status, evidence_digest, report_id) — the same kind of artifact this section describes, but with different field names/shape and scoped to adapters certified against the Integration Contract, not this specification's Manifest Schema.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## CM-RID-001

- Specification / section: MCC-CM-001 / 23. Requirement Identifier Registry / 23.5 Registry Invariants
- Status: NOT_APPLICABLE
- Requirement: All identifiers defined by this specification MUST use the `CM-` namespace prefix.
- Existing implementation: None
- Missing implementation behavior: N/A (not an implementable requirement).
- Missing test coverage: No test exists for this requirement.
- Missing evidence: N/A
- Rationale: Interpretive, bibliographic, non-normative-by-design (explicitly marked informative/example), or document-self-referential statement. It does not describe a discrete, independently implementable system behavior.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: N/A

## CM-RID-002

- Specification / section: MCC-CM-001 / 23. Requirement Identifier Registry / 23.5 Registry Invariants
- Status: NOT_APPLICABLE
- Requirement: Identifiers within the `CM-` namespace MUST be globally unique.
- Existing implementation: None
- Missing implementation behavior: N/A (not an implementable requirement).
- Missing test coverage: No test exists for this requirement.
- Missing evidence: N/A
- Rationale: Interpretive, bibliographic, non-normative-by-design (explicitly marked informative/example), or document-self-referential statement. It does not describe a discrete, independently implementable system behavior.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: N/A

## CM-RID-003

- Specification / section: MCC-CM-001 / 23. Requirement Identifier Registry / 23.5 Registry Invariants
- Status: NOT_APPLICABLE
- Requirement: Retired identifiers MUST NOT be reassigned to a different requirement.
- Existing implementation: None
- Missing implementation behavior: N/A (not an implementable requirement).
- Missing test coverage: No test exists for this requirement.
- Missing evidence: N/A
- Rationale: Interpretive, bibliographic, non-normative-by-design (explicitly marked informative/example), or document-self-referential statement. It does not describe a discrete, independently implementable system behavior.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: N/A

## CM-RID-004

- Specification / section: MCC-CM-001 / 23. Requirement Identifier Registry / 23.5 Registry Invariants
- Status: NOT_APPLICABLE
- Requirement: New category tags MUST NOT collide with prefixes already registered by another MCC specification.
- Existing implementation: None
- Missing implementation behavior: N/A (not an implementable requirement).
- Missing test coverage: No test exists for this requirement.
- Missing evidence: N/A
- Rationale: Interpretive, bibliographic, non-normative-by-design (explicitly marked informative/example), or document-self-referential statement. It does not describe a discrete, independently implementable system behavior.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: N/A

## CM-SCHEMA-001

- Specification / section: MCC-CM-001 / 10. Manifest Schema / 10.5 Manifest Schema Invariants
- Status: PARTIAL
- Requirement: A Certification Manifest MUST be a single structured, machine-readable document.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: certifications/manifest.json is a real, versioned (MANIFEST_SCHEMA_VERSION), digest-bound, structured certification record (subject/adapter, contract_version, status, evidence_digest, report_id) — the same kind of artifact this section describes, but with different field names/shape and scoped to adapters certified against the Integration Contract, not this specification's Manifest Schema.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## CM-SCHEMA-002

- Specification / section: MCC-CM-001 / 10. Manifest Schema / 10.5 Manifest Schema Invariants
- Status: PARTIAL
- Requirement: Every Manifest Field MUST have an unambiguous, defined type.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: certifications/manifest.json is a real, versioned (MANIFEST_SCHEMA_VERSION), digest-bound, structured certification record (subject/adapter, contract_version, status, evidence_digest, report_id) — the same kind of artifact this section describes, but with different field names/shape and scoped to adapters certified against the Integration Contract, not this specification's Manifest Schema.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## CM-SCHEMA-003

- Specification / section: MCC-CM-001 / 10. Manifest Schema / 10.5 Manifest Schema Invariants
- Status: PARTIAL
- Requirement: The top-level field groups defined in Section 10.2 MUST all be present, except where explicitly marked optional.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: certifications/manifest.json is a real, versioned (MANIFEST_SCHEMA_VERSION), digest-bound, structured certification record (subject/adapter, contract_version, status, evidence_digest, report_id) — the same kind of artifact this section describes, but with different field names/shape and scoped to adapters certified against the Integration Contract, not this specification's Manifest Schema.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## CM-SCHEMA-004

- Specification / section: MCC-CM-001 / 10. Manifest Schema / 10.5 Manifest Schema Invariants
- Status: PARTIAL
- Requirement: Digest computation over Manifest content MUST use a deterministic Canonical Form.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: certifications/manifest.json is a real, versioned (MANIFEST_SCHEMA_VERSION), digest-bound, structured certification record (subject/adapter, contract_version, status, evidence_digest, report_id) — the same kind of artifact this section describes, but with different field names/shape and scoped to adapters certified against the Integration Contract, not this specification's Manifest Schema.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## CM-SCHEMA-005

- Specification / section: MCC-CM-001 / 10. Manifest Schema / 10.5 Manifest Schema Invariants
- Status: PARTIAL
- Requirement: The Manifest Schema MUST remain independent of any specific serialization technology.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: certifications/manifest.json is a real, versioned (MANIFEST_SCHEMA_VERSION), digest-bound, structured certification record (subject/adapter, contract_version, status, evidence_digest, report_id) — the same kind of artifact this section describes, but with different field names/shape and scoped to adapters certified against the Integration Contract, not this specification's Manifest Schema.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## CM-SEC-001

- Specification / section: MCC-CM-001 / 19. Security Considerations / 19.5 Security Invariants
- Status: PARTIAL
- Requirement: Manifest validation MUST assume an untrusted source.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: The certification manifest is digest-bound and contains no secrets/paths by design (see reporting.py docstring), consistent with this section's requirements.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## CM-SEC-002

- Specification / section: MCC-CM-001 / 19. Security Considerations / 19.5 Security Invariants
- Status: PARTIAL
- Requirement: Tamper detection for referenced content MUST rely on independently recomputed Hash References.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: The certification manifest is digest-bound and contains no secrets/paths by design (see reporting.py docstring), consistent with this section's requirements.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## CM-SEC-003

- Specification / section: MCC-CM-001 / 19. Security Considerations / 19.5 Security Invariants
- Status: PARTIAL
- Requirement: Manifests MUST NOT contain secrets or credentials.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: The certification manifest is digest-bound and contains no secrets/paths by design (see reporting.py docstring), consistent with this section's requirements.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## CM-SEC-004

- Specification / section: MCC-CM-001 / 19. Security Considerations / 19.5 Security Invariants
- Status: PARTIAL
- Requirement: Sensitive underlying data MUST be redacted or hashed before inclusion in a Manifest Field.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: The certification manifest is digest-bound and contains no secrets/paths by design (see reporting.py docstring), consistent with this section's requirements.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## CM-SEC-005

- Specification / section: MCC-CM-001 / 19. Security Considerations / 19.5 Security Invariants
- Status: PARTIAL
- Requirement: Security properties of a Manifest MUST be verifiable without trusting its origin.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: The certification manifest is digest-bound and contains no secrets/paths by design (see reporting.py docstring), consistent with this section's requirements.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## CM-VAL-001

- Specification / section: MCC-CM-001 / 18. Validation Rules / 18.7 Validation Invariants
- Status: PARTIAL
- Requirement: Validation MUST be fail-closed.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: program.py's manifest build/verify path regenerates the manifest and canonically compares it, detecting tamper/staleness/regression — a real, tested, fail-closed validation mechanism for this artifact class.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## CM-VAL-002

- Specification / section: MCC-CM-001 / 18. Validation Rules / 18.7 Validation Invariants
- Status: PARTIAL
- Requirement: Structural validation MUST precede Hash Reference, Evidence Bundle Reference, and metadata consistency validation.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: program.py's manifest build/verify path regenerates the manifest and canonically compares it, detecting tamper/staleness/regression — a real, tested, fail-closed validation mechanism for this artifact class.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## CM-VAL-003

- Specification / section: MCC-CM-001 / 18. Validation Rules / 18.7 Validation Invariants
- Status: PARTIAL
- Requirement: A Manifest failing any validation step MUST be rejected in its entirety.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: program.py's manifest build/verify path regenerates the manifest and canonically compares it, detecting tamper/staleness/regression — a real, tested, fail-closed validation mechanism for this artifact class.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## CM-VAL-004

- Specification / section: MCC-CM-001 / 18. Validation Rules / 18.7 Validation Invariants
- Status: PARTIAL
- Requirement: Validation MUST be reproducible: the same Manifest MUST produce the same validation result under the same Schema Version.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: program.py's manifest build/verify path regenerates the manifest and canonically compares it, detecting tamper/staleness/regression — a real, tested, fail-closed validation mechanism for this artifact class.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## CM-VAL-005

- Specification / section: MCC-CM-001 / 18. Validation Rules / 18.7 Validation Invariants
- Status: PARTIAL
- Requirement: Validation MUST NOT depend on trusting the environment that produced the Manifest.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: program.py's manifest build/verify path regenerates the manifest and canonically compares it, detecting tamper/staleness/regression — a real, tested, fail-closed validation mechanism for this artifact class.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## CM-VSN-001

- Specification / section: MCC-CM-001 / 16. Versioning Rules / 16.5 Versioning Invariants
- Status: PARTIAL
- Requirement: Every Certification Manifest MUST declare a Manifest Schema Version.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: MANIFEST_SCHEMA_VERSION is tracked independently of contract_version and compliance_suite_version, the same independent-versioning model this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## CM-VSN-002

- Specification / section: MCC-CM-001 / 16. Versioning Rules / 16.5 Versioning Invariants
- Status: PARTIAL
- Requirement: Manifest Schema Versions MUST be immutable once published.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: MANIFEST_SCHEMA_VERSION is tracked independently of contract_version and compliance_suite_version, the same independent-versioning model this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## CM-VSN-003

- Specification / section: MCC-CM-001 / 16. Versioning Rules / 16.5 Versioning Invariants
- Status: PARTIAL
- Requirement: Manifest Schema Version, MCC-CP-001 specification version, and Evidence Bundle Schema Version MUST be tracked independently.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: MANIFEST_SCHEMA_VERSION is tracked independently of contract_version and compliance_suite_version, the same independent-versioning model this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## CM-VSN-004

- Specification / section: MCC-CM-001 / 16. Versioning Rules / 16.5 Versioning Invariants
- Status: PARTIAL
- Requirement: An unrecognized Manifest Schema Version MUST cause validation to fail.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: MANIFEST_SCHEMA_VERSION is tracked independently of contract_version and compliance_suite_version, the same independent-versioning model this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CM-001-1-STATUS-D01

- Specification / section: MCC-CM-001 / 1. Status
- Status: NOT_APPLICABLE
- Requirement: The key words MUST, MUST NOT, REQUIRED, SHALL, SHALL NOT, SHOULD, SHOULD NOT, RECOMMENDED, MAY and OPTIONAL in this specification are to be interpreted as described in RFC 2119 and RFC 8174.
- Existing implementation: None
- Missing implementation behavior: N/A (not an implementable requirement).
- Missing test coverage: No test exists for this requirement.
- Missing evidence: N/A
- Rationale: Interpretive, bibliographic, non-normative-by-design (explicitly marked informative/example), or document-self-referential statement. It does not describe a discrete, independently implementable system behavior.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: N/A

## MCC-CM-001-10-MANIFEST-SCHEMA-D01

- Specification / section: MCC-CM-001 / 10. Manifest Schema / 10.2 Top-Level Structure
- Status: PARTIAL
- Requirement: A Certification Manifest SHALL be composed of the following field groups: - Identification fields, per Section 11.2; - Certification Metadata fields, per Section 15; - Requirement Results, per Section 15.4; - Evidence Bundle References, per Section 14; - Hash References, per Section 13; - Optional Fields, per Section 12; - Extension fields, per Section 20, where present.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: certifications/manifest.json is a real, versioned (MANIFEST_SCHEMA_VERSION), digest-bound, structured certification record (subject/adapter, contract_version, status, evidence_digest, report_id) — the same kind of artifact this section describes, but with different field names/shape and scoped to adapters certified against the Integration Contract, not this specification's Manifest Schema.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CM-001-10-MANIFEST-SCHEMA-D02

- Specification / section: MCC-CM-001 / 10. Manifest Schema / 10.3 Field Typing
- Status: PARTIAL
- Requirement: Every Manifest Field MUST have a defined type consistent with this specification: identifier, string, timestamp, enumerated value, Hash Reference, Evidence Bundle Reference, Requirement Result, or a list thereof.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: certifications/manifest.json is a real, versioned (MANIFEST_SCHEMA_VERSION), digest-bound, structured certification record (subject/adapter, contract_version, status, evidence_digest, report_id) — the same kind of artifact this section describes, but with different field names/shape and scoped to adapters certified against the Integration Contract, not this specification's Manifest Schema.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CM-001-10-MANIFEST-SCHEMA-D03

- Specification / section: MCC-CM-001 / 10. Manifest Schema / 10.3 Field Typing
- Status: PARTIAL
- Requirement: Manifest Fields MUST NOT be ambiguous as to type.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: certifications/manifest.json is a real, versioned (MANIFEST_SCHEMA_VERSION), digest-bound, structured certification record (subject/adapter, contract_version, status, evidence_digest, report_id) — the same kind of artifact this section describes, but with different field names/shape and scoped to adapters certified against the Integration Contract, not this specification's Manifest Schema.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CM-001-10-MANIFEST-SCHEMA-D04

- Specification / section: MCC-CM-001 / 10. Manifest Schema / 10.4 Canonical Form
- Status: PARTIAL
- Requirement: For any purpose requiring a Digest of a Certification Manifest, or a Digest of a subset of its fields, the data digested MUST first be reduced to a Canonical Form, consistent with the Canonical Form requirement of MCC-EB-001, Section 13.2.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: certifications/manifest.json is a real, versioned (MANIFEST_SCHEMA_VERSION), digest-bound, structured certification record (subject/adapter, contract_version, status, evidence_digest, report_id) — the same kind of artifact this section describes, but with different field names/shape and scoped to adapters certified against the Integration Contract, not this specification's Manifest Schema.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CM-001-11-REQUIRED-FIELDS-D01

- Specification / section: MCC-CM-001 / 11. Required Fields / 11.1 Purpose
- Status: PARTIAL
- Requirement: Required Fields are the Manifest Fields that MUST be present in every conforming Certification Manifest.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: certifications/manifest.json is a real, versioned (MANIFEST_SCHEMA_VERSION), digest-bound, structured certification record (subject/adapter, contract_version, status, evidence_digest, report_id) — the same kind of artifact this section describes, but with different field names/shape and scoped to adapters certified against the Integration Contract, not this specification's Manifest Schema.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CM-001-11-REQUIRED-FIELDS-D02

- Specification / section: MCC-CM-001 / 11. Required Fields / 11.2 Identification Fields
- Status: PARTIAL
- Requirement: Every Certification Manifest MUST include: - a manifest identifier, unique to the certification run it describes; - the Manifest Schema Version; - the MCC-CP-001 specification version under which certification was performed; - the Certification Subject identifier, as defined by MCC-CP-001, Section 7.2.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: certifications/manifest.json is a real, versioned (MANIFEST_SCHEMA_VERSION), digest-bound, structured certification record (subject/adapter, contract_version, status, evidence_digest, report_id) — the same kind of artifact this section describes, but with different field names/shape and scoped to adapters certified against the Integration Contract, not this specification's Manifest Schema.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CM-001-11-REQUIRED-FIELDS-D03

- Specification / section: MCC-CM-001 / 11. Required Fields / 11.3 Baseline Required Fields
- Status: PARTIAL
- Requirement: Consistent with MCC-CP-001, Section 15.2, every Certification Manifest MUST include: - manifest identifier; - specification version; - Certification Subject identifier; - capability profiles; - certification requirements evaluated; - certification result; - evidence references; - generation timestamp.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: certifications/manifest.json is a real, versioned (MANIFEST_SCHEMA_VERSION), digest-bound, structured certification record (subject/adapter, contract_version, status, evidence_digest, report_id) — the same kind of artifact this section describes, but with different field names/shape and scoped to adapters certified against the Integration Contract, not this specification's Manifest Schema.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CM-001-11-REQUIRED-FIELDS-D04

- Specification / section: MCC-CM-001 / 11. Required Fields / 11.4 Field Presence Rule
- Status: PARTIAL
- Requirement: A Certification Manifest MUST NOT omit a Required Field regardless of certification outcome, including where the certification result is FAIL.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: certifications/manifest.json is a real, versioned (MANIFEST_SCHEMA_VERSION), digest-bound, structured certification record (subject/adapter, contract_version, status, evidence_digest, report_id) — the same kind of artifact this section describes, but with different field names/shape and scoped to adapters certified against the Integration Contract, not this specification's Manifest Schema.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CM-001-12-OPTIONAL-FIELDS-D01

- Specification / section: MCC-CM-001 / 12. Optional Fields / 12.3 Optional Field Constraints
- Status: PARTIAL
- Requirement: An Optional Field, where present, MUST conform to the type rules of Section 10.3.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: certifications/manifest.json is a real, versioned (MANIFEST_SCHEMA_VERSION), digest-bound, structured certification record (subject/adapter, contract_version, status, evidence_digest, report_id) — the same kind of artifact this section describes, but with different field names/shape and scoped to adapters certified against the Integration Contract, not this specification's Manifest Schema.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CM-001-12-OPTIONAL-FIELDS-D02

- Specification / section: MCC-CM-001 / 12. Optional Fields / 12.3 Optional Field Constraints
- Status: PARTIAL
- Requirement: The absence of an Optional Field MUST NOT be treated as a validation failure.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: certifications/manifest.json is a real, versioned (MANIFEST_SCHEMA_VERSION), digest-bound, structured certification record (subject/adapter, contract_version, status, evidence_digest, report_id) — the same kind of artifact this section describes, but with different field names/shape and scoped to adapters certified against the Integration Contract, not this specification's Manifest Schema.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CM-001-12-OPTIONAL-FIELDS-D03

- Specification / section: MCC-CM-001 / 12. Optional Fields / 12.3 Optional Field Constraints
- Status: PARTIAL
- Requirement: An Optional Field MUST NOT be used to satisfy a Required Field obligation defined in Section 11.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: certifications/manifest.json is a real, versioned (MANIFEST_SCHEMA_VERSION), digest-bound, structured certification record (subject/adapter, contract_version, status, evidence_digest, report_id) — the same kind of artifact this section describes, but with different field names/shape and scoped to adapters certified against the Integration Contract, not this specification's Manifest Schema.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CM-001-13-HASH-REFERENCES-D01

- Specification / section: MCC-CM-001 / 13. Hash References / 13.2 Hash Reference Structure
- Status: PARTIAL
- Requirement: A Hash Reference MUST identify: - the Digest value; - the hash algorithm used to produce the Digest; - the artifact or content the Digest corresponds to (for example, an Evidence Bundle identifier).
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: certifications/manifest.json binds evidence_digest / vector_manifest_digest (sha256, DIGEST_ALGORITHM) to the certification record, the same binding concept, but as bare digest strings rather than this section's required identifier+algorithm+content-pointer structured Hash Reference object.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CM-001-13-HASH-REFERENCES-D02

- Specification / section: MCC-CM-001 / 13. Hash References / 13.3 Hash Algorithm Requirements
- Status: PARTIAL
- Requirement: The hash algorithm identified by a Hash Reference MUST be a collision-resistant cryptographic hash function, consistent with MCC-EB-001, Section 13.3.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: certifications/manifest.json binds evidence_digest / vector_manifest_digest (sha256, DIGEST_ALGORITHM) to the certification record, the same binding concept, but as bare digest strings rather than this section's required identifier+algorithm+content-pointer structured Hash Reference object.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CM-001-13-HASH-REFERENCES-D03

- Specification / section: MCC-CM-001 / 13. Hash References / 13.3 Hash Algorithm Requirements
- Status: PARTIAL
- Requirement: A Certification Manifest MUST NOT be considered valid if any Hash Reference identifies a hash algorithm that is not collision-resistant.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: certifications/manifest.json binds evidence_digest / vector_manifest_digest (sha256, DIGEST_ALGORITHM) to the certification record, the same binding concept, but as bare digest strings rather than this section's required identifier+algorithm+content-pointer structured Hash Reference object.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CM-001-13-HASH-REFERENCES-D04

- Specification / section: MCC-CM-001 / 13. Hash References / 13.4 Hash Reference Usage
- Status: PARTIAL
- Requirement: Every Evidence Bundle Reference, per Section 14, MUST include at least one Hash Reference binding it to the referenced Evidence Bundle's Integrity Record, as defined by MCC-EB-001, Section 13.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: certifications/manifest.json binds evidence_digest / vector_manifest_digest (sha256, DIGEST_ALGORITHM) to the certification record, the same binding concept, but as bare digest strings rather than this section's required identifier+algorithm+content-pointer structured Hash Reference object.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CM-001-14-EVIDENCE-BUNDLE-REFERENCES-D01

- Specification / section: MCC-CM-001 / 14. Evidence Bundle References / 14.2 Primary Evidence Bundle Reference
- Status: GAP
- Requirement: A Certification Manifest MUST reference exactly one primary Evidence Bundle corresponding to the certification run described by the Manifest.
- Existing implementation: None
- Missing implementation behavior: Full requirement not implemented.
- Missing test coverage: No test exists for this requirement.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: certifications/manifest.json references compliance vectors and adapters, not an Evidence Bundle as MCC-EB-001 defines it; no Evidence-Bundle-Reference-shaped field exists.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CM-001-14-EVIDENCE-BUNDLE-REFERENCES-D02

- Specification / section: MCC-CM-001 / 14. Evidence Bundle References / 14.2 Primary Evidence Bundle Reference
- Status: GAP
- Requirement: The primary Evidence Bundle Reference MUST include: - the Evidence Bundle identifier, as defined by MCC-EB-001, Section 12.1; - the Evidence Bundle Schema Version, as defined by MCC-EB-001, Section 17.2; - a Hash Reference binding the Manifest to that Evidence Bundle's Integrity Record.
- Existing implementation: None
- Missing implementation behavior: Full requirement not implemented.
- Missing test coverage: No test exists for this requirement.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: certifications/manifest.json references compliance vectors and adapters, not an Evidence Bundle as MCC-EB-001 defines it; no Evidence-Bundle-Reference-shaped field exists.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CM-001-14-EVIDENCE-BUNDLE-REFERENCES-D03

- Specification / section: MCC-CM-001 / 14. Evidence Bundle References / 14.3 Supplementary Evidence Bundle References
- Status: GAP
- Requirement: A supplementary Evidence Bundle Reference MUST be distinguishable from the primary Evidence Bundle Reference defined in Section 14.2.
- Existing implementation: None
- Missing implementation behavior: Full requirement not implemented.
- Missing test coverage: No test exists for this requirement.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: certifications/manifest.json references compliance vectors and adapters, not an Evidence Bundle as MCC-EB-001 defines it; no Evidence-Bundle-Reference-shaped field exists.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CM-001-14-EVIDENCE-BUNDLE-REFERENCES-D04

- Specification / section: MCC-CM-001 / 14. Evidence Bundle References / 14.4 Reference Integrity
- Status: GAP
- Requirement: An Evidence Bundle Reference MUST NOT be considered satisfied unless the Hash Reference it carries is independently verified against the referenced Evidence Bundle's Integrity Record.
- Existing implementation: None
- Missing implementation behavior: Full requirement not implemented.
- Missing test coverage: No test exists for this requirement.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: certifications/manifest.json references compliance vectors and adapters, not an Evidence Bundle as MCC-EB-001 defines it; no Evidence-Bundle-Reference-shaped field exists.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CM-001-14-EVIDENCE-BUNDLE-REFERENCES-D05

- Specification / section: MCC-CM-001 / 14. Evidence Bundle References / 14.4 Reference Integrity
- Status: GAP
- Requirement: A Certification Manifest whose primary Evidence Bundle Reference cannot be verified MUST NOT be treated as valid.
- Existing implementation: None
- Missing implementation behavior: Full requirement not implemented.
- Missing test coverage: No test exists for this requirement.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: certifications/manifest.json references compliance vectors and adapters, not an Evidence Bundle as MCC-EB-001 defines it; no Evidence-Bundle-Reference-shaped field exists.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CM-001-15-CERTIFICATION-METADATA-D01

- Specification / section: MCC-CM-001 / 15. Certification Metadata / 15.2 Subject and Scope Metadata
- Status: PARTIAL
- Requirement: Certification Metadata MUST identify: - the Certification Subject, as defined by MCC-CP-001, Section 7.2; - the capability profiles claimed and the capability profiles verified, as defined by MCC-CP-001, Section 11; - the specification version of MCC-CP-001 under which certification was performed.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: certifications/manifest.json records subject (adapter/adapter_key), specification version (contract_version), a Requirement-Result-like list (covered_invariants), and an overall status — the same metadata categories this section requires, under different names.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CM-001-15-CERTIFICATION-METADATA-D02

- Specification / section: MCC-CM-001 / 15. Certification Metadata / 15.3 Certification Result
- Status: PARTIAL
- Requirement: Certification Metadata MUST record the overall certification result as one of the outcomes defined by MCC-CP-001, Sections 8.6 and 9.6: - PASS - FAIL
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: certifications/manifest.json records subject (adapter/adapter_key), specification version (contract_version), a Requirement-Result-like list (covered_invariants), and an overall status — the same metadata categories this section requires, under different names.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CM-001-15-CERTIFICATION-METADATA-D03

- Specification / section: MCC-CM-001 / 15. Certification Metadata / 15.3 Certification Result
- Status: PARTIAL
- Requirement: A Certification Manifest MUST NOT record a certification result other than PASS or FAIL.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: certifications/manifest.json records subject (adapter/adapter_key), specification version (contract_version), a Requirement-Result-like list (covered_invariants), and an overall status — the same metadata categories this section requires, under different names.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CM-001-15-CERTIFICATION-METADATA-D04

- Specification / section: MCC-CM-001 / 15. Certification Metadata / 15.4 Requirement Results
- Status: PARTIAL
- Requirement: Certification Metadata MUST include a Requirement Result for every Certification Requirement evaluated during certification.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: certifications/manifest.json records subject (adapter/adapter_key), specification version (contract_version), a Requirement-Result-like list (covered_invariants), and an overall status — the same metadata categories this section requires, under different names.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CM-001-15-CERTIFICATION-METADATA-D05

- Specification / section: MCC-CM-001 / 15. Certification Metadata / 15.4 Requirement Results
- Status: PARTIAL
- Requirement: Each Requirement Result MUST identify: - the Certification Requirement identifier, as defined by MCC-CP-001, Section 12.2; - its classification (REQUIRED, OPTIONAL, or CONDITIONAL), as defined by MCC-CP-001, Sections 10.3 and 13.2; - its outcome (PASS, FAIL, or NOT APPLICABLE), consistent with MCC-CP-001, Sections 8.5, 9.5, and 10.4.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: certifications/manifest.json records subject (adapter/adapter_key), specification version (contract_version), a Requirement-Result-like list (covered_invariants), and an overall status — the same metadata categories this section requires, under different names.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CM-001-15-CERTIFICATION-METADATA-D06

- Specification / section: MCC-CM-001 / 15. Certification Metadata / 15.5 Generation Metadata
- Status: PARTIAL
- Requirement: Certification Metadata MUST include a generation timestamp identifying when the Manifest was produced.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: certifications/manifest.json records subject (adapter/adapter_key), specification version (contract_version), a Requirement-Result-like list (covered_invariants), and an overall status — the same metadata categories this section requires, under different names.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CM-001-16-VERSIONING-RULES-D01

- Specification / section: MCC-CM-001 / 16. Versioning Rules / 16.2 Schema Version Declaration
- Status: PARTIAL
- Requirement: Every Certification Manifest MUST declare its Manifest Schema Version among its Identification Fields.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: MANIFEST_SCHEMA_VERSION is tracked independently of contract_version and compliance_suite_version, the same independent-versioning model this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CM-001-16-VERSIONING-RULES-D02

- Specification / section: MCC-CM-001 / 16. Versioning Rules / 16.2 Schema Version Declaration
- Status: PARTIAL
- Requirement: The Manifest Schema Version MUST be immutable once assigned to a published revision of this specification.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: MANIFEST_SCHEMA_VERSION is tracked independently of contract_version and compliance_suite_version, the same independent-versioning model this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CM-001-16-VERSIONING-RULES-D03

- Specification / section: MCC-CM-001 / 16. Versioning Rules / 16.3 Schema Version Scope
- Status: PARTIAL
- Requirement: The Manifest Schema Version is distinct from, and SHALL NOT be conflated with, the MCC-CP-001 specification version or the Evidence Bundle Schema Version referenced by a Manifest.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: MANIFEST_SCHEMA_VERSION is tracked independently of contract_version and compliance_suite_version, the same independent-versioning model this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CM-001-16-VERSIONING-RULES-D04

- Specification / section: MCC-CM-001 / 16. Versioning Rules / 16.4 Version Evolution
- Status: PARTIAL
- Requirement: A validator MUST reject a Certification Manifest declaring a Schema Version it does not recognize, consistent with Section 18.6.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: MANIFEST_SCHEMA_VERSION is tracked independently of contract_version and compliance_suite_version, the same independent-versioning model this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CM-001-17-COMPATIBILITY-RULES-D01

- Specification / section: MCC-CM-001 / 17. Compatibility Rules / 17.3 Forward Compatibility
- Status: PARTIAL
- Requirement: A validator MUST NOT assume forward compatibility with a Manifest Schema Version it does not recognize.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: MANIFEST_SCHEMA_VERSION is tracked independently of contract_version and compliance_suite_version, the same independent-versioning model this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CM-001-17-COMPATIBILITY-RULES-D02

- Specification / section: MCC-CM-001 / 17. Compatibility Rules / 17.3 Forward Compatibility
- Status: PARTIAL
- Requirement: An unrecognized Manifest Schema Version MUST be treated per Section 16.4 and Section 18.6, not silently accepted.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: MANIFEST_SCHEMA_VERSION is tracked independently of contract_version and compliance_suite_version, the same independent-versioning model this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CM-001-17-COMPATIBILITY-RULES-D03

- Specification / section: MCC-CM-001 / 17. Compatibility Rules / 17.4 Breaking Changes
- Status: PARTIAL
- Requirement: A revision of this specification that alters the Manifest Schema, Required Fields, Hash Reference structure, or Evidence Bundle Reference rules in a way that invalidates previously valid Manifests MUST introduce a new Manifest Schema Version and MUST document the change as breaking.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: MANIFEST_SCHEMA_VERSION is tracked independently of contract_version and compliance_suite_version, the same independent-versioning model this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CM-001-17-COMPATIBILITY-RULES-D04

- Specification / section: MCC-CM-001 / 17. Compatibility Rules / 17.5 Cross-Specification Compatibility
- Status: PARTIAL
- Requirement: A Certification Manifest MUST NOT be considered valid if it references an Evidence Bundle Schema Version that MCC-EB-001, as currently published, does not recognize.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: MANIFEST_SCHEMA_VERSION is tracked independently of contract_version and compliance_suite_version, the same independent-versioning model this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CM-001-18-VALIDATION-RULES-D01

- Specification / section: MCC-CM-001 / 18. Validation Rules / 18.1 Purpose
- Status: PARTIAL
- Requirement: Validation Rules define the normative procedure and criteria a validator MUST apply to determine whether a Certification Manifest is valid.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: program.py's manifest build/verify path regenerates the manifest and canonically compares it, detecting tamper/staleness/regression — a real, tested, fail-closed validation mechanism for this artifact class.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CM-001-18-VALIDATION-RULES-D02

- Specification / section: MCC-CM-001 / 18. Validation Rules / 18.2 Structural Validation
- Status: PARTIAL
- Requirement: A validator MUST verify that the Manifest conforms to the Manifest Schema defined in Section 10 and contains all Required Fields defined in Section 11.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: program.py's manifest build/verify path regenerates the manifest and canonically compares it, detecting tamper/staleness/regression — a real, tested, fail-closed validation mechanism for this artifact class.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CM-001-18-VALIDATION-RULES-D03

- Specification / section: MCC-CM-001 / 18. Validation Rules / 18.2 Structural Validation
- Status: PARTIAL
- Requirement: A Manifest that fails structural validation MUST be rejected without further processing.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: program.py's manifest build/verify path regenerates the manifest and canonically compares it, detecting tamper/staleness/regression — a real, tested, fail-closed validation mechanism for this artifact class.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CM-001-18-VALIDATION-RULES-D04

- Specification / section: MCC-CM-001 / 18. Validation Rules / 18.3 Hash Reference Validation
- Status: PARTIAL
- Requirement: A validator MUST independently recompute and verify every Hash Reference contained in the Manifest, consistent with Section 13.5.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: program.py's manifest build/verify path regenerates the manifest and canonically compares it, detecting tamper/staleness/regression — a real, tested, fail-closed validation mechanism for this artifact class.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CM-001-18-VALIDATION-RULES-D05

- Specification / section: MCC-CM-001 / 18. Validation Rules / 18.3 Hash Reference Validation
- Status: PARTIAL
- Requirement: A Manifest containing any unverifiable Hash Reference MUST be rejected.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: program.py's manifest build/verify path regenerates the manifest and canonically compares it, detecting tamper/staleness/regression — a real, tested, fail-closed validation mechanism for this artifact class.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CM-001-18-VALIDATION-RULES-D06

- Specification / section: MCC-CM-001 / 18. Validation Rules / 18.4 Evidence Bundle Reference Validation
- Status: PARTIAL
- Requirement: A validator MUST verify the primary Evidence Bundle Reference defined in Section 14.2 against the referenced Evidence Bundle's Integrity Record, as defined by MCC-EB-001, Section 16.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: program.py's manifest build/verify path regenerates the manifest and canonically compares it, detecting tamper/staleness/regression — a real, tested, fail-closed validation mechanism for this artifact class.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CM-001-18-VALIDATION-RULES-D07

- Specification / section: MCC-CM-001 / 18. Validation Rules / 18.4 Evidence Bundle Reference Validation
- Status: PARTIAL
- Requirement: A Manifest whose primary Evidence Bundle Reference cannot be verified MUST be rejected.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: program.py's manifest build/verify path regenerates the manifest and canonically compares it, detecting tamper/staleness/regression — a real, tested, fail-closed validation mechanism for this artifact class.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CM-001-18-VALIDATION-RULES-D08

- Specification / section: MCC-CM-001 / 18. Validation Rules / 18.5 Metadata Consistency Validation
- Status: PARTIAL
- Requirement: A validator MUST verify that Certification Metadata is internally consistent: that the certification result recorded under Section 15.3 is consistent with the Requirement Results recorded under Section 15.4, per MCC-CP-001, Section 10.5.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: program.py's manifest build/verify path regenerates the manifest and canonically compares it, detecting tamper/staleness/regression — a real, tested, fail-closed validation mechanism for this artifact class.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CM-001-18-VALIDATION-RULES-D09

- Specification / section: MCC-CM-001 / 18. Validation Rules / 18.6 Fail-Closed Validation
- Status: PARTIAL
- Requirement: Validation SHALL be fail-closed: a Certification Manifest MUST be treated as invalid unless every applicable validation step in this section succeeds.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: program.py's manifest build/verify path regenerates the manifest and canonically compares it, detecting tamper/staleness/regression — a real, tested, fail-closed validation mechanism for this artifact class.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CM-001-18-VALIDATION-RULES-D10

- Specification / section: MCC-CM-001 / 18. Validation Rules / 18.6 Fail-Closed Validation
- Status: PARTIAL
- Requirement: Partial or inconclusive validation results MUST NOT be treated as valid.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: program.py's manifest build/verify path regenerates the manifest and canonically compares it, detecting tamper/staleness/regression — a real, tested, fail-closed validation mechanism for this artifact class.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CM-001-19-SECURITY-CONSIDERATIONS-D01

- Specification / section: MCC-CM-001 / 19. Security Considerations / 19.2 Threat Model
- Status: PARTIAL
- Requirement: Validation of a Certification Manifest MUST assume: - the Manifest MAY originate from an untrusted or compromised source; - the Manifest MAY have been partially or fully tampered with; - the environment that produced the Manifest MUST NOT be trusted implicitly.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: The certification manifest is digest-bound and contains no secrets/paths by design (see reporting.py docstring), consistent with this section's requirements.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CM-001-19-SECURITY-CONSIDERATIONS-D02

- Specification / section: MCC-CM-001 / 19. Security Considerations / 19.4 Sensitive Data
- Status: PARTIAL
- Requirement: A Certification Manifest MUST NOT include secrets, credentials, or other sensitive material not required to describe the certification result.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: The certification manifest is digest-bound and contains no secrets/paths by design (see reporting.py docstring), consistent with this section's requirements.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CM-001-19-SECURITY-CONSIDERATIONS-D03

- Specification / section: MCC-CM-001 / 19. Security Considerations / 19.4 Sensitive Data
- Status: PARTIAL
- Requirement: Where underlying certification inputs contain sensitive material, Manifest Fields MUST reference redacted or hashed representations rather than raw sensitive values, consistent with MCC-EB-001, Section 19.4.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: The certification manifest is digest-bound and contains no secrets/paths by design (see reporting.py docstring), consistent with this section's requirements.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CM-001-2-ABSTRACT-D01

- Specification / section: MCC-CM-001 / 2. Abstract
- Status: NOT_APPLICABLE
- Requirement: A Certification Manifest SHALL remain framework-neutral and implementation-independent, and SHALL be independently verifiable without trusting the environment that produced it.
- Existing implementation: None
- Missing implementation behavior: N/A (not an implementable requirement).
- Missing test coverage: No test exists for this requirement.
- Missing evidence: N/A
- Rationale: Interpretive, bibliographic, non-normative-by-design (explicitly marked informative/example), or document-self-referential statement. It does not describe a discrete, independently implementable system behavior.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: N/A

## MCC-CM-001-20-EXTENSION-MODEL-D01

- Specification / section: MCC-CM-001 / 20. Extension Model / 20.2 Extension Points
- Status: GAP
- Requirement: Extensions MUST be declared and identified as such within the Manifest.
- Existing implementation: None
- Missing implementation behavior: Full requirement not implemented.
- Missing test coverage: No test exists for this requirement.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: No extension-declaration mechanism (a way to mark additional fields as explicit, non-breaking extensions to a committed schema) was found anywhere in this repository for any artifact.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CM-001-20-EXTENSION-MODEL-D02

- Specification / section: MCC-CM-001 / 20. Extension Model / 20.3 Extension Constraints
- Status: GAP
- Requirement: An extension MUST NOT alter the meaning of any Required Field, Hash Reference, or Evidence Bundle Reference defined by this specification.
- Existing implementation: None
- Missing implementation behavior: Full requirement not implemented.
- Missing test coverage: No test exists for this requirement.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: No extension-declaration mechanism (a way to mark additional fields as explicit, non-breaking extensions to a committed schema) was found anywhere in this repository for any artifact.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CM-001-20-EXTENSION-MODEL-D03

- Specification / section: MCC-CM-001 / 20. Extension Model / 20.3 Extension Constraints
- Status: GAP
- Requirement: A validator that does not recognize a declared extension MUST ignore that extension's content without failing validation, provided all other validation rules in Section 18 are satisfied.
- Existing implementation: None
- Missing implementation behavior: Full requirement not implemented.
- Missing test coverage: No test exists for this requirement.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: No extension-declaration mechanism (a way to mark additional fields as explicit, non-breaking extensions to a committed schema) was found anywhere in this repository for any artifact.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CM-001-22-CONFORMANCE-REQUIREMENTS-D01

- Specification / section: MCC-CM-001 / 22. Conformance Requirements / 22.2 Conforming Manifest Producer
- Status: GAP
- Requirement: A conforming Manifest producer MUST generate Manifests satisfying Sections 10 through 15 of this specification for the Manifest Schema Version it declares.
- Existing implementation: None
- Missing implementation behavior: Full requirement not implemented.
- Missing test coverage: No test exists for this requirement.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: No producer/validator conformance-declaration mechanism specific to this specification's Manifest Schema Version was found.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CM-001-22-CONFORMANCE-REQUIREMENTS-D02

- Specification / section: MCC-CM-001 / 22. Conformance Requirements / 22.2 Conforming Manifest Producer
- Status: GAP
- Requirement: A conforming Manifest producer MUST NOT emit a Manifest that fails validation under Section 18 against its own declared Schema Version.
- Existing implementation: None
- Missing implementation behavior: Full requirement not implemented.
- Missing test coverage: No test exists for this requirement.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: No producer/validator conformance-declaration mechanism specific to this specification's Manifest Schema Version was found.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CM-001-22-CONFORMANCE-REQUIREMENTS-D03

- Specification / section: MCC-CM-001 / 22. Conformance Requirements / 22.3 Conforming Manifest Validator
- Status: GAP
- Requirement: A conforming Manifest validator MUST implement the validation procedure defined in Section 18 in full, without omitting any applicable step.
- Existing implementation: None
- Missing implementation behavior: Full requirement not implemented.
- Missing test coverage: No test exists for this requirement.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: No producer/validator conformance-declaration mechanism specific to this specification's Manifest Schema Version was found.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CM-001-22-CONFORMANCE-REQUIREMENTS-D04

- Specification / section: MCC-CM-001 / 22. Conformance Requirements / 22.3 Conforming Manifest Validator
- Status: GAP
- Requirement: A conforming Manifest validator MUST reject a Manifest whenever any applicable validation step fails.
- Existing implementation: None
- Missing implementation behavior: Full requirement not implemented.
- Missing test coverage: No test exists for this requirement.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: No producer/validator conformance-declaration mechanism specific to this specification's Manifest Schema Version was found.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CM-001-22-CONFORMANCE-REQUIREMENTS-D05

- Specification / section: MCC-CM-001 / 22. Conformance Requirements / 22.4 Conformance Independence
- Status: GAP
- Requirement: Conformance to this specification SHALL be evaluated independently of any specific programming language, framework, or certification tooling implementation.
- Existing implementation: None
- Missing implementation behavior: Full requirement not implemented.
- Missing test coverage: No test exists for this requirement.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: No producer/validator conformance-declaration mechanism specific to this specification's Manifest Schema Version was found.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CM-001-23-REQUIREMENT-IDENTIFIER-REGISTRY-D01

- Specification / section: MCC-CM-001 / 23. Requirement Identifier Registry / 23.2 Namespace Convention
- Status: NOT_APPLICABLE
- Requirement: Every normative requirement identifier defined by this specification SHALL be prefixed with `CM-`, followed by a section-scoped category tag, followed by a three-digit sequence number.
- Existing implementation: None
- Missing implementation behavior: N/A (not an implementable requirement).
- Missing test coverage: No test exists for this requirement.
- Missing evidence: N/A
- Rationale: Interpretive, bibliographic, non-normative-by-design (explicitly marked informative/example), or document-self-referential statement. It does not describe a discrete, independently implementable system behavior.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: N/A

## MCC-CM-001-23-REQUIREMENT-IDENTIFIER-REGISTRY-D02

- Specification / section: MCC-CM-001 / 23. Requirement Identifier Registry / 23.4 Registry Requirements
- Status: NOT_APPLICABLE
- Requirement: Requirement identifiers under this specification's `CM-` namespace SHALL be globally unique.
- Existing implementation: None
- Missing implementation behavior: N/A (not an implementable requirement).
- Missing test coverage: No test exists for this requirement.
- Missing evidence: N/A
- Rationale: Interpretive, bibliographic, non-normative-by-design (explicitly marked informative/example), or document-self-referential statement. It does not describe a discrete, independently implementable system behavior.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: N/A

## MCC-CM-001-23-REQUIREMENT-IDENTIFIER-REGISTRY-D03

- Specification / section: MCC-CM-001 / 23. Requirement Identifier Registry / 23.4 Registry Requirements
- Status: NOT_APPLICABLE
- Requirement: A future revision of this specification MUST NOT reuse a retired identifier for a different requirement.
- Existing implementation: None
- Missing implementation behavior: N/A (not an implementable requirement).
- Missing test coverage: No test exists for this requirement.
- Missing evidence: N/A
- Rationale: Interpretive, bibliographic, non-normative-by-design (explicitly marked informative/example), or document-self-referential statement. It does not describe a discrete, independently implementable system behavior.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: N/A

## MCC-CM-001-23-REQUIREMENT-IDENTIFIER-REGISTRY-D04

- Specification / section: MCC-CM-001 / 23. Requirement Identifier Registry / 23.4 Registry Requirements
- Status: NOT_APPLICABLE
- Requirement: A future revision of this specification MUST NOT introduce a new category tag that collides with a prefix already registered by MCC-CP-001 or MCC-EB-001.
- Existing implementation: None
- Missing implementation behavior: N/A (not an implementable requirement).
- Missing test coverage: No test exists for this requirement.
- Missing evidence: N/A
- Rationale: Interpretive, bibliographic, non-normative-by-design (explicitly marked informative/example), or document-self-referential statement. It does not describe a discrete, independently implementable system behavior.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: N/A

## MCC-CM-001-5-GOALS-D01

- Specification / section: MCC-CM-001 / 5. Goals / CM-G1. Framework Neutrality
- Status: GAP
- Requirement: The Certification Manifest format MUST remain independent of any particular framework, programming language, or certification tooling implementation.
- Existing implementation: None
- Missing implementation behavior: Full requirement not implemented.
- Missing test coverage: No test exists for this requirement.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: No implementation behavior, automated test, or evidence mechanism semantically equivalent to this requirement (category: '5. Goals') was found anywhere under src/, tests/, certifications/, evidence/, schemas/, docs/, or CI workflows, after the broader semantic-mapping investigation described in this module's docstring — not merely a lexical search for this specification's exact terminology.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CM-001-5-GOALS-D02

- Specification / section: MCC-CM-001 / 5. Goals / CM-G2. Machine Readability
- Status: GAP
- Requirement: A Certification Manifest MUST be structured and machine-readable, without requiring interpretation beyond this specification and its declared Schema Version.
- Existing implementation: None
- Missing implementation behavior: Full requirement not implemented.
- Missing test coverage: No test exists for this requirement.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: No implementation behavior, automated test, or evidence mechanism semantically equivalent to this requirement (category: '5. Goals') was found anywhere under src/, tests/, certifications/, evidence/, schemas/, docs/, or CI workflows, after the broader semantic-mapping investigation described in this module's docstring — not merely a lexical search for this specification's exact terminology.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CM-001-5-GOALS-D03

- Specification / section: MCC-CM-001 / 5. Goals / CM-G3. Independent Verifiability
- Status: GAP
- Requirement: A third party MUST be able to interpret and validate a Certification Manifest, and confirm its relationship to the Evidence Bundle(s) it references, without trusting the environment that produced it.
- Existing implementation: None
- Missing implementation behavior: Full requirement not implemented.
- Missing test coverage: No test exists for this requirement.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: No implementation behavior, automated test, or evidence mechanism semantically equivalent to this requirement (category: '5. Goals') was found anywhere under src/, tests/, certifications/, evidence/, schemas/, docs/, or CI workflows, after the broader semantic-mapping investigation described in this module's docstring — not merely a lexical search for this specification's exact terminology.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CM-001-5-GOALS-D04

- Specification / section: MCC-CM-001 / 5. Goals / CM-G4. Traceability
- Status: GAP
- Requirement: A Certification Manifest MUST remain traceable to the Certification Subject, the specification version, and the Evidence Bundle(s) that substantiate it.
- Existing implementation: None
- Missing implementation behavior: Full requirement not implemented.
- Missing test coverage: No test exists for this requirement.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: No implementation behavior, automated test, or evidence mechanism semantically equivalent to this requirement (category: '5. Goals') was found anywhere under src/, tests/, certifications/, evidence/, schemas/, docs/, or CI workflows, after the broader semantic-mapping investigation described in this module's docstring — not merely a lexical search for this specification's exact terminology.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CM-001-6-NON-GOALS-D01

- Specification / section: MCC-CM-001 / 6. Non-Goals
- Status: GAP
- Requirement: This specification SHALL NOT: - define how certification decisions are reached (defined by MCC-CP-001); - define the Evidence Bundle or Technical Certificate formats; - mandate a specific programming language, library, or SDK for producing or validating Manifests; - mandate a specific storage backend, transport protocol, or distribution channel; - define business-specific or domain-specific manifest content; - define runtime governance behavior (ALLOW, DENY, ESCALATE, CONSTRAIN), which belongs exclusively to MCC-Core runtime governance.
- Existing implementation: None
- Missing implementation behavior: Full requirement not implemented.
- Missing test coverage: No test exists for this requirement.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: No implementation behavior, automated test, or evidence mechanism semantically equivalent to this requirement (category: '6. Non-Goals') was found anywhere under src/, tests/, certifications/, evidence/, schemas/, docs/, or CI workflows, after the broader semantic-mapping investigation described in this module's docstring — not merely a lexical search for this specification's exact terminology.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CM-001-9-CERTIFICATION-MANIFEST-OVERVIEW-D01

- Specification / section: MCC-CM-001 / 9. Certification Manifest Overview / 9.1 Role in Certification
- Status: PARTIAL
- Requirement: A Certification Manifest is produced during the Artifact Generation stage of the Certification Pipeline defined in MCC-CP-001, Section 9.7, and SHALL satisfy the requirements defined in MCC-CP-001, Section 15.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: certifications/manifest.json is a real, versioned (MANIFEST_SCHEMA_VERSION), digest-bound, structured certification record (subject/adapter, contract_version, status, evidence_digest, report_id) — the same kind of artifact this section describes, but with different field names/shape and scoped to adapters certified against the Integration Contract, not this specification's Manifest Schema.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CM-001-9-CERTIFICATION-MANIFEST-OVERVIEW-D02

- Specification / section: MCC-CM-001 / 9. Certification Manifest Overview / 9.2 Manifest Form
- Status: PARTIAL
- Requirement: A Certification Manifest SHALL be a single structured, machine-readable document.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: certifications/manifest.json is a real, versioned (MANIFEST_SCHEMA_VERSION), digest-bound, structured certification record (subject/adapter, contract_version, status, evidence_digest, report_id) — the same kind of artifact this section describes, but with different field names/shape and scoped to adapters certified against the Integration Contract, not this specification's Manifest Schema.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CM-001-9-CERTIFICATION-MANIFEST-OVERVIEW-D03

- Specification / section: MCC-CM-001 / 9. Certification Manifest Overview / 9.2 Manifest Form
- Status: PARTIAL
- Requirement: A Certification Manifest SHALL NOT be a directory or multi-file archive; where multiple substantiating files exist, they SHALL be organized as an Evidence Bundle under MCC-EB-001 and referenced from the Manifest by Evidence Bundle Reference.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: certifications/manifest.json is a real, versioned (MANIFEST_SCHEMA_VERSION), digest-bound, structured certification record (subject/adapter, contract_version, status, evidence_digest, report_id) — the same kind of artifact this section describes, but with different field names/shape and scoped to adapters certified against the Integration Contract, not this specification's Manifest Schema.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CM-001-9-CERTIFICATION-MANIFEST-OVERVIEW-D04

- Specification / section: MCC-CM-001 / 9. Certification Manifest Overview / 9.3 Relationship to Other Certification Artifacts
- Status: PARTIAL
- Requirement: A Certification Manifest MUST reference at least one Evidence Bundle, per Section 14.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: certifications/manifest.json is a real, versioned (MANIFEST_SCHEMA_VERSION), digest-bound, structured certification record (subject/adapter, contract_version, status, evidence_digest, report_id) — the same kind of artifact this section describes, but with different field names/shape and scoped to adapters certified against the Integration Contract, not this specification's Manifest Schema.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## CAP-001

- Specification / section: MCC-CP-001 / 11. Capability Profiles / 11.7 Capability Profile Invariants
- Status: PARTIAL
- Requirement: Capability Profiles SHALL remain framework-neutral.
- Existing implementation: src/mcc_compliance/capability_profile.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_compliance/capability_profile.py is a real, tested, versioned, fail-closed capability-profile validator (declared/validated/certified/authorized trust ladder) — a close analog to this section.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## CAP-002

- Specification / section: MCC-CP-001 / 11. Capability Profiles / 11.7 Capability Profile Invariants
- Status: PARTIAL
- Requirement: Capability evaluation SHALL remain implementation-independent.
- Existing implementation: src/mcc_compliance/capability_profile.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_compliance/capability_profile.py is a real, tested, versioned, fail-closed capability-profile validator (declared/validated/certified/authorized trust ladder) — a close analog to this section.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## CAP-003

- Specification / section: MCC-CP-001 / 11. Capability Profiles / 11.7 Capability Profile Invariants
- Status: PARTIAL
- Requirement: Capability claims SHALL be reproducible.
- Existing implementation: src/mcc_compliance/capability_profile.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_compliance/capability_profile.py is a real, tested, versioned, fail-closed capability-profile validator (declared/validated/certified/authorized trust ladder) — a close analog to this section.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## CAP-004

- Specification / section: MCC-CP-001 / 11. Capability Profiles / 11.7 Capability Profile Invariants
- Status: PARTIAL
- Requirement: Capability claims SHALL be independently verifiable.
- Existing implementation: src/mcc_compliance/capability_profile.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_compliance/capability_profile.py is a real, tested, versioned, fail-closed capability-profile validator (declared/validated/certified/authorized trust ladder) — a close analog to this section.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## CAP-005

- Specification / section: MCC-CP-001 / 11. Capability Profiles / 11.7 Capability Profile Invariants
- Status: PARTIAL
- Requirement: Capability identifiers SHALL be versioned.
- Existing implementation: src/mcc_compliance/capability_profile.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_compliance/capability_profile.py is a real, tested, versioned, fail-closed capability-profile validator (declared/validated/certified/authorized trust ladder) — a close analog to this section.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## CAP-006

- Specification / section: MCC-CP-001 / 11. Capability Profiles / 11.7 Capability Profile Invariants
- Status: PARTIAL
- Requirement: Capabilities SHALL reference normative requirements only.
- Existing implementation: src/mcc_compliance/capability_profile.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_compliance/capability_profile.py is a real, tested, versioned, fail-closed capability-profile validator (declared/validated/certified/authorized trust ladder) — a close analog to this section.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## CAP-007

- Specification / section: MCC-CP-001 / 11. Capability Profiles / 11.7 Capability Profile Invariants
- Status: PARTIAL
- Requirement: Capability dependencies SHALL be acyclic.
- Existing implementation: src/mcc_compliance/capability_profile.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_compliance/capability_profile.py is a real, tested, versioned, fail-closed capability-profile validator (declared/validated/certified/authorized trust ladder) — a close analog to this section.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## CAP-008

- Specification / section: MCC-CP-001 / 11. Capability Profiles / 11.7 Capability Profile Invariants
- Status: PARTIAL
- Requirement: Only verified capabilities MAY be certified.
- Existing implementation: src/mcc_compliance/capability_profile.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_compliance/capability_profile.py is a real, tested, versioned, fail-closed capability-profile validator (declared/validated/certified/authorized trust ladder) — a close analog to this section.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## CERT-001

- Specification / section: MCC-CP-001 / 16. Technical Certificate Requirements / 16.6 Certificate Invariants
- Status: PARTIAL
- Requirement: Technical Certificates SHALL be authoritative.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: certifications/manifest.json's CERTIFIED entries are the closest analog to this section's authoritative certified-outcome record found in the repository.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## CERT-002

- Specification / section: MCC-CP-001 / 16. Technical Certificate Requirements / 16.6 Certificate Invariants
- Status: PARTIAL
- Requirement: Technical Certificates SHALL remain framework-neutral.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: certifications/manifest.json's CERTIFIED entries are the closest analog to this section's authoritative certified-outcome record found in the repository.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## CERT-003

- Specification / section: MCC-CP-001 / 16. Technical Certificate Requirements / 16.6 Certificate Invariants
- Status: PARTIAL
- Requirement: Technical Certificates SHALL remain implementation-independent.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: certifications/manifest.json's CERTIFIED entries are the closest analog to this section's authoritative certified-outcome record found in the repository.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## CERT-004

- Specification / section: MCC-CP-001 / 16. Technical Certificate Requirements / 16.6 Certificate Invariants
- Status: PARTIAL
- Requirement: Technical Certificates SHALL reference Certification Manifests.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: certifications/manifest.json's CERTIFIED entries are the closest analog to this section's authoritative certified-outcome record found in the repository.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## CERT-005

- Specification / section: MCC-CP-001 / 16. Technical Certificate Requirements / 16.6 Certificate Invariants
- Status: PARTIAL
- Requirement: Technical Certificates SHALL reference Evidence Bundles.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: certifications/manifest.json's CERTIFIED entries are the closest analog to this section's authoritative certified-outcome record found in the repository.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## CERT-006

- Specification / section: MCC-CP-001 / 16. Technical Certificate Requirements / 16.6 Certificate Invariants
- Status: PARTIAL
- Requirement: Technical Certificates SHALL declare specification versions.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: certifications/manifest.json's CERTIFIED entries are the closest analog to this section's authoritative certified-outcome record found in the repository.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## CERT-007

- Specification / section: MCC-CP-001 / 16. Technical Certificate Requirements / 16.6 Certificate Invariants
- Status: PARTIAL
- Requirement: Technical Certificates SHALL remain immutable after issuance.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: certifications/manifest.json's CERTIFIED entries are the closest analog to this section's authoritative certified-outcome record found in the repository.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## CI-001

- Specification / section: MCC-CP-001 / 7. Certification Model / 7.5 Certification Invariants
- Status: PARTIAL
- Requirement: Certification evaluates specifications. Never implementations.
- Existing implementation: src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_compliance implements a real, tested certification model (evaluate an adapter's behavior against versioned requirements, produce a deterministic result) — the same model this section describes, scoped to adapters vs. the Integration Contract rather than implementations vs. these four specifications.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## CI-002

- Specification / section: MCC-CP-001 / 7. Certification Model / 7.5 Certification Invariants
- Status: PARTIAL
- Requirement: Evidence precedes certification.
- Existing implementation: src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_compliance implements a real, tested certification model (evaluate an adapter's behavior against versioned requirements, produce a deterministic result) — the same model this section describes, scoped to adapters vs. the Integration Contract rather than implementations vs. these four specifications.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## CI-003

- Specification / section: MCC-CP-001 / 7. Certification Model / 7.5 Certification Invariants
- Status: PARTIAL
- Requirement: Certification precedes Technical Certificate issuance.
- Existing implementation: src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_compliance implements a real, tested certification model (evaluate an adapter's behavior against versioned requirements, produce a deterministic result) — the same model this section describes, scoped to adapters vs. the Integration Contract rather than implementations vs. these four specifications.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## CI-004

- Specification / section: MCC-CP-001 / 7. Certification Model / 7.5 Certification Invariants
- Status: PARTIAL
- Requirement: Certification results SHALL be reproducible.
- Existing implementation: src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_compliance implements a real, tested certification model (evaluate an adapter's behavior against versioned requirements, produce a deterministic result) — the same model this section describes, scoped to adapters vs. the Integration Contract rather than implementations vs. these four specifications.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## CI-005

- Specification / section: MCC-CP-001 / 7. Certification Model / 7.5 Certification Invariants
- Status: PARTIAL
- Requirement: Certification SHALL remain framework-neutral.
- Existing implementation: src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_compliance implements a real, tested certification model (evaluate an adapter's behavior against versioned requirements, produce a deterministic result) — the same model this section describes, scoped to adapters vs. the Integration Contract rather than implementations vs. these four specifications.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## CI-006

- Specification / section: MCC-CP-001 / 7. Certification Model / 7.5 Certification Invariants
- Status: PARTIAL
- Requirement: No implementation SHALL become normative.
- Existing implementation: src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_compliance implements a real, tested certification model (evaluate an adapter's behavior against versioned requirements, produce a deterministic result) — the same model this section describes, scoped to adapters vs. the Integration Contract rather than implementations vs. these four specifications.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## CI-007

- Specification / section: MCC-CP-001 / 7. Certification Model / 7.5 Certification Invariants
- Status: PARTIAL
- Requirement: Reference implementations remain informative.
- Existing implementation: src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_compliance implements a real, tested certification model (evaluate an adapter's behavior against versioned requirements, produce a deterministic result) — the same model this section describes, scoped to adapters vs. the Integration Contract rather than implementations vs. these four specifications.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## CI-008

- Specification / section: MCC-CP-001 / 7. Certification Model / 7.5 Certification Invariants
- Status: PARTIAL
- Requirement: Certification SHALL be independently verifiable.
- Existing implementation: src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_compliance implements a real, tested certification model (evaluate an adapter's behavior against versioned requirements, produce a deterministic result) — the same model this section describes, scoped to adapters vs. the Integration Contract rather than implementations vs. these four specifications.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## CI-009

- Specification / section: MCC-CP-001 / 7. Certification Model / 7.5 Certification Invariants
- Status: PARTIAL
- Requirement: Normative requirements SHALL be versioned.
- Existing implementation: src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_compliance implements a real, tested certification model (evaluate an adapter's behavior against versioned requirements, produce a deterministic result) — the same model this section describes, scoped to adapters vs. the Integration Contract rather than implementations vs. these four specifications.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## CI-010

- Specification / section: MCC-CP-001 / 7. Certification Model / 7.5 Certification Invariants
- Status: PARTIAL
- Requirement: Certification SHALL remain implementation-independent.
- Existing implementation: src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_compliance implements a real, tested certification model (evaluate an adapter's behavior against versioned requirements, produce a deterministic result) — the same model this section describes, scoped to adapters vs. the Integration Contract rather than implementations vs. these four specifications.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## CLASS-001

- Specification / section: MCC-CP-001 / 13. Requirement Classification / 13.6 Requirement Classification Invariants
- Status: PARTIAL
- Requirement: Every Certification Requirement SHALL have exactly one classification.
- Existing implementation: src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: Each compliance vector carries an explicit boolean `mandatory` flag (src/mcc_compliance/vectors/v1/manifest.json), the same required-vs-optional classification concept this section requires, though only a two-way (not three-way REQUIRED/OPTIONAL/CONDITIONAL) split was found.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## CLASS-002

- Specification / section: MCC-CP-001 / 13. Requirement Classification / 13.6 Requirement Classification Invariants
- Status: PARTIAL
- Requirement: Classification SHALL remain implementation-independent.
- Existing implementation: src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: Each compliance vector carries an explicit boolean `mandatory` flag (src/mcc_compliance/vectors/v1/manifest.json), the same required-vs-optional classification concept this section requires, though only a two-way (not three-way REQUIRED/OPTIONAL/CONDITIONAL) split was found.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## CLASS-003

- Specification / section: MCC-CP-001 / 13. Requirement Classification / 13.6 Requirement Classification Invariants
- Status: PARTIAL
- Requirement: Classification SHALL remain framework-neutral.
- Existing implementation: src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: Each compliance vector carries an explicit boolean `mandatory` flag (src/mcc_compliance/vectors/v1/manifest.json), the same required-vs-optional classification concept this section requires, though only a two-way (not three-way REQUIRED/OPTIONAL/CONDITIONAL) split was found.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## CLASS-004

- Specification / section: MCC-CP-001 / 13. Requirement Classification / 13.6 Requirement Classification Invariants
- Status: PARTIAL
- Requirement: REQUIRED requirements SHALL always participate in certification.
- Existing implementation: src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: Each compliance vector carries an explicit boolean `mandatory` flag (src/mcc_compliance/vectors/v1/manifest.json), the same required-vs-optional classification concept this section requires, though only a two-way (not three-way REQUIRED/OPTIONAL/CONDITIONAL) split was found.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## CLASS-005

- Specification / section: MCC-CP-001 / 13. Requirement Classification / 13.6 Requirement Classification Invariants
- Status: PARTIAL
- Requirement: OPTIONAL requirements SHALL NOT determine certification status.
- Existing implementation: src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: Each compliance vector carries an explicit boolean `mandatory` flag (src/mcc_compliance/vectors/v1/manifest.json), the same required-vs-optional classification concept this section requires, though only a two-way (not three-way REQUIRED/OPTIONAL/CONDITIONAL) split was found.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## CLASS-006

- Specification / section: MCC-CP-001 / 13. Requirement Classification / 13.6 Requirement Classification Invariants
- Status: PARTIAL
- Requirement: CONDITIONAL requirements SHALL define explicit applicability conditions.
- Existing implementation: src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: Each compliance vector carries an explicit boolean `mandatory` flag (src/mcc_compliance/vectors/v1/manifest.json), the same required-vs-optional classification concept this section requires, though only a two-way (not three-way REQUIRED/OPTIONAL/CONDITIONAL) split was found.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## CLASS-007

- Specification / section: MCC-CP-001 / 13. Requirement Classification / 13.6 Requirement Classification Invariants
- Status: PARTIAL
- Requirement: Requirement classifications SHALL be versioned.
- Existing implementation: src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: Each compliance vector carries an explicit boolean `mandatory` flag (src/mcc_compliance/vectors/v1/manifest.json), the same required-vs-optional classification concept this section requires, though only a two-way (not three-way REQUIRED/OPTIONAL/CONDITIONAL) split was found.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## CONF-001

- Specification / section: MCC-CP-001 / 10. Conformance Model / 10.6 Conformance Invariants
- Status: PARTIAL
- Requirement: Conformance evaluates requirements.
- Existing implementation: src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: Each compliance vector produces a real pass/fail-style CaseResult, aggregated into scenarios_passed / scenarios_failed / scenarios_total, the same evaluated-outcome model this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## CONF-002

- Specification / section: MCC-CP-001 / 10. Conformance Model / 10.6 Conformance Invariants
- Status: PARTIAL
- Requirement: Conformance SHALL remain implementation-independent.
- Existing implementation: src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: Each compliance vector produces a real pass/fail-style CaseResult, aggregated into scenarios_passed / scenarios_failed / scenarios_total, the same evaluated-outcome model this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## CONF-003

- Specification / section: MCC-CP-001 / 10. Conformance Model / 10.6 Conformance Invariants
- Status: PARTIAL
- Requirement: Conformance SHALL remain framework-neutral.
- Existing implementation: src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: Each compliance vector produces a real pass/fail-style CaseResult, aggregated into scenarios_passed / scenarios_failed / scenarios_total, the same evaluated-outcome model this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## CONF-004

- Specification / section: MCC-CP-001 / 10. Conformance Model / 10.6 Conformance Invariants
- Status: PARTIAL
- Requirement: Conformance SHALL be reproducible.
- Existing implementation: src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: Each compliance vector produces a real pass/fail-style CaseResult, aggregated into scenarios_passed / scenarios_failed / scenarios_total, the same evaluated-outcome model this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## CONF-005

- Specification / section: MCC-CP-001 / 10. Conformance Model / 10.6 Conformance Invariants
- Status: PARTIAL
- Requirement: Conformance SHALL be independently verifiable.
- Existing implementation: src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: Each compliance vector produces a real pass/fail-style CaseResult, aggregated into scenarios_passed / scenarios_failed / scenarios_total, the same evaluated-outcome model this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## CONF-006

- Specification / section: MCC-CP-001 / 10. Conformance Model / 10.6 Conformance Invariants
- Status: PARTIAL
- Requirement: Normative requirements SHALL be versioned.
- Existing implementation: src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: Each compliance vector produces a real pass/fail-style CaseResult, aggregated into scenarios_passed / scenarios_failed / scenarios_total, the same evaluated-outcome model this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## CONF-007

- Specification / section: MCC-CP-001 / 10. Conformance Model / 10.6 Conformance Invariants
- Status: PARTIAL
- Requirement: Certification decisions SHALL be derived only from evaluated normative requirements.
- Existing implementation: src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: Each compliance vector produces a real pass/fail-style CaseResult, aggregated into scenarios_passed / scenarios_failed / scenarios_total, the same evaluated-outcome model this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## CP-PIPE-001

- Specification / section: MCC-CP-001 / 9. Certification Pipeline / 9.9 Pipeline Invariants
- Status: PARTIAL
- Requirement: Pipeline stages execute sequentially.
- Existing implementation: src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: run_compliance executes an ordered, deterministic sequence of stages (structural checks, scenario execution, evidence generation, assessment, artifact generation) analogous to this section's Pipeline.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## CP-PIPE-002

- Specification / section: MCC-CP-001 / 9. Certification Pipeline / 9.9 Pipeline Invariants
- Status: PARTIAL
- Requirement: Mandatory stages SHALL NOT be skipped.
- Existing implementation: src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: run_compliance executes an ordered, deterministic sequence of stages (structural checks, scenario execution, evidence generation, assessment, artifact generation) analogous to this section's Pipeline.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## CP-PIPE-003

- Specification / section: MCC-CP-001 / 9. Certification Pipeline / 9.9 Pipeline Invariants
- Status: PARTIAL
- Requirement: Evidence SHALL precede certification.
- Existing implementation: src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: run_compliance executes an ordered, deterministic sequence of stages (structural checks, scenario execution, evidence generation, assessment, artifact generation) analogous to this section's Pipeline.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## CP-PIPE-004

- Specification / section: MCC-CP-001 / 9. Certification Pipeline / 9.9 Pipeline Invariants
- Status: PARTIAL
- Requirement: Certification SHALL precede certificate issuance.
- Existing implementation: src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: run_compliance executes an ordered, deterministic sequence of stages (structural checks, scenario execution, evidence generation, assessment, artifact generation) analogous to this section's Pipeline.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## CP-PIPE-005

- Specification / section: MCC-CP-001 / 9. Certification Pipeline / 9.9 Pipeline Invariants
- Status: PARTIAL
- Requirement: Artifacts SHALL remain reproducible.
- Existing implementation: src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: run_compliance executes an ordered, deterministic sequence of stages (structural checks, scenario execution, evidence generation, assessment, artifact generation) analogous to this section's Pipeline.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## CP-PIPE-006

- Specification / section: MCC-CP-001 / 9. Certification Pipeline / 9.9 Pipeline Invariants
- Status: PARTIAL
- Requirement: Pipeline SHALL remain framework-neutral.
- Existing implementation: src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: run_compliance executes an ordered, deterministic sequence of stages (structural checks, scenario execution, evidence generation, assessment, artifact generation) analogous to this section's Pipeline.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## CP-PIPE-007

- Specification / section: MCC-CP-001 / 9. Certification Pipeline / 9.9 Pipeline Invariants
- Status: PARTIAL
- Requirement: Pipeline SHALL remain implementation-independent.
- Existing implementation: src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: run_compliance executes an ordered, deterministic sequence of stages (structural checks, scenario execution, evidence generation, assessment, artifact generation) analogous to this section's Pipeline.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## CREP-001

- Specification / section: MCC-CP-001 / Appendix H — Certification Report Requirements / H.6 Certification Report Invariants
- Status: PARTIAL
- Requirement: A Certification Report SHALL be produced for every successful certification.
- Existing implementation: src/mcc_compliance/reporting.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_compliance/reporting.py generates a real, deterministic, human-readable Markdown report (secret-free, non-authoritative relative to the manifest, with an explicit certification-scope disclaimer) — closely matching this appendix's required content and properties.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## CREP-002

- Specification / section: MCC-CP-001 / Appendix H — Certification Report Requirements / H.6 Certification Report Invariants
- Status: PARTIAL
- Requirement: The Certification Report SHALL be human-readable.
- Existing implementation: src/mcc_compliance/reporting.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_compliance/reporting.py generates a real, deterministic, human-readable Markdown report (secret-free, non-authoritative relative to the manifest, with an explicit certification-scope disclaimer) — closely matching this appendix's required content and properties.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## CREP-003

- Specification / section: MCC-CP-001 / Appendix H — Certification Report Requirements / H.6 Certification Report Invariants
- Status: PARTIAL
- Requirement: The Certification Report SHALL identify the Certification Subject, the specification version, and the overall certification outcome.
- Existing implementation: src/mcc_compliance/reporting.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_compliance/reporting.py generates a real, deterministic, human-readable Markdown report (secret-free, non-authoritative relative to the manifest, with an explicit certification-scope disclaimer) — closely matching this appendix's required content and properties.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## CREP-004

- Specification / section: MCC-CP-001 / Appendix H — Certification Report Requirements / H.6 Certification Report Invariants
- Status: PARTIAL
- Requirement: The Certification Report SHALL NOT be treated as authoritative in place of the Certification Manifest or Technical Certificate.
- Existing implementation: src/mcc_compliance/reporting.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_compliance/reporting.py generates a real, deterministic, human-readable Markdown report (secret-free, non-authoritative relative to the manifest, with an explicit certification-scope disclaimer) — closely matching this appendix's required content and properties.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## CREP-005

- Specification / section: MCC-CP-001 / Appendix H — Certification Report Requirements / H.6 Certification Report Invariants
- Status: PARTIAL
- Requirement: The Certification Report SHALL NOT contain claims inconsistent with its referenced Certification Manifest.
- Existing implementation: src/mcc_compliance/reporting.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_compliance/reporting.py generates a real, deterministic, human-readable Markdown report (secret-free, non-authoritative relative to the manifest, with an explicit certification-scope disclaimer) — closely matching this appendix's required content and properties.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## CREP-006

- Specification / section: MCC-CP-001 / Appendix H — Certification Report Requirements / H.6 Certification Report Invariants
- Status: PARTIAL
- Requirement: The Certification Report format SHALL remain implementation-independent absent a future normative format specification.
- Existing implementation: src/mcc_compliance/reporting.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_compliance/reporting.py generates a real, deterministic, human-readable Markdown report (secret-free, non-authoritative relative to the manifest, with an explicit certification-scope disclaimer) — closely matching this appendix's required content and properties.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## CRES-001

- Specification / section: MCC-CP-001 / Appendix G — Conformance Result Requirements / G.4 Conformance Result Invariants
- Status: PARTIAL
- Requirement: The Conformance Result SHALL be carried by the Certification Manifest and SHALL NOT be produced as a separate artifact.
- Existing implementation: src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: scenarios_passed / scenarios_failed / scenarios_total in certifications/manifest.json is a real, reproducible Conformance-Result-equivalent, carried within the certification manifest rather than as a separate artifact, matching this appendix's own "not a separate artifact" model.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## CRES-002

- Specification / section: MCC-CP-001 / Appendix G — Conformance Result Requirements / G.4 Conformance Result Invariants
- Status: PARTIAL
- Requirement: The Conformance Result SHALL identify the Certification Subject, the specification version, and the overall outcome.
- Existing implementation: src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: scenarios_passed / scenarios_failed / scenarios_total in certifications/manifest.json is a real, reproducible Conformance-Result-equivalent, carried within the certification manifest rather than as a separate artifact, matching this appendix's own "not a separate artifact" model.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## CRES-003

- Specification / section: MCC-CP-001 / Appendix G — Conformance Result Requirements / G.4 Conformance Result Invariants
- Status: PARTIAL
- Requirement: The Conformance Result SHALL include a Requirement Result for every evaluated Certification Requirement.
- Existing implementation: src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: scenarios_passed / scenarios_failed / scenarios_total in certifications/manifest.json is a real, reproducible Conformance-Result-equivalent, carried within the certification manifest rather than as a separate artifact, matching this appendix's own "not a separate artifact" model.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## CRES-004

- Specification / section: MCC-CP-001 / Appendix G — Conformance Result Requirements / G.4 Conformance Result Invariants
- Status: PARTIAL
- Requirement: The Conformance Result SHALL be reproducible.
- Existing implementation: src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: scenarios_passed / scenarios_failed / scenarios_total in certifications/manifest.json is a real, reproducible Conformance-Result-equivalent, carried within the certification manifest rather than as a separate artifact, matching this appendix's own "not a separate artifact" model.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## CRES-005

- Specification / section: MCC-CP-001 / Appendix G — Conformance Result Requirements / G.4 Conformance Result Invariants
- Status: PARTIAL
- Requirement: The Conformance Result SHALL remain consistent with the Certification Manifest requirements defined by MCC-CM-001.
- Existing implementation: src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: scenarios_passed / scenarios_failed / scenarios_total in certifications/manifest.json is a real, reproducible Conformance-Result-equivalent, carried within the certification manifest rather than as a separate artifact, matching this appendix's own "not a separate artifact" model.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## CSTMT-001

- Specification / section: MCC-CP-001 / 20. Conformance Statement / 20.3 Conformance Invariants
- Status: GAP
- Requirement: Conformance SHALL be evidence-based.
- Existing implementation: None
- Missing implementation behavior: Full requirement not implemented.
- Missing test coverage: No test exists for this requirement.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: No mechanism for an implementation to claim conformance specifically to MCC-CP-001 (as opposed to the Integration Contract) was found.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## CSTMT-002

- Specification / section: MCC-CP-001 / 20. Conformance Statement / 20.3 Conformance Invariants
- Status: GAP
- Requirement: Conformance SHALL remain reproducible.
- Existing implementation: None
- Missing implementation behavior: Full requirement not implemented.
- Missing test coverage: No test exists for this requirement.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: No mechanism for an implementation to claim conformance specifically to MCC-CP-001 (as opposed to the Integration Contract) was found.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## CSTMT-003

- Specification / section: MCC-CP-001 / 20. Conformance Statement / 20.3 Conformance Invariants
- Status: GAP
- Requirement: Conformance SHALL remain independently verifiable.
- Existing implementation: None
- Missing implementation behavior: Full requirement not implemented.
- Missing test coverage: No test exists for this requirement.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: No mechanism for an implementation to claim conformance specifically to MCC-CP-001 (as opposed to the Integration Contract) was found.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## CSTMT-004

- Specification / section: MCC-CP-001 / 20. Conformance Statement / 20.3 Conformance Invariants
- Status: GAP
- Requirement: Conformance SHALL remain implementation-independent.
- Existing implementation: None
- Missing implementation behavior: Full requirement not implemented.
- Missing test coverage: No test exists for this requirement.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: No mechanism for an implementation to claim conformance specifically to MCC-CP-001 (as opposed to the Integration Contract) was found.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## CSTMT-005

- Specification / section: MCC-CP-001 / 20. Conformance Statement / 20.3 Conformance Invariants
- Status: GAP
- Requirement: Conformance SHALL remain framework-neutral.
- Existing implementation: None
- Missing implementation behavior: Full requirement not implemented.
- Missing test coverage: No test exists for this requirement.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: No mechanism for an implementation to claim conformance specifically to MCC-CP-001 (as opposed to the Integration Contract) was found.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## CSTMT-006

- Specification / section: MCC-CP-001 / 20. Conformance Statement / 20.3 Conformance Invariants
- Status: GAP
- Requirement: Conformance SHALL reference normative specification versions.
- Existing implementation: None
- Missing implementation behavior: Full requirement not implemented.
- Missing test coverage: No test exists for this requirement.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: No mechanism for an implementation to claim conformance specifically to MCC-CP-001 (as opposed to the Integration Contract) was found.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## CSTMT-007

- Specification / section: MCC-CP-001 / 20. Conformance Statement / 20.3 Conformance Invariants
- Status: GAP
- Requirement: Conformance claims SHALL remain traceable.
- Existing implementation: None
- Missing implementation behavior: Full requirement not implemented.
- Missing test coverage: No test exists for this requirement.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: No mechanism for an implementation to claim conformance specifically to MCC-CP-001 (as opposed to the Integration Contract) was found.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## DEC-001

- Specification / section: MCC-CP-001 / Appendix B — Certification Decision Matrix / B.4 Decision Invariants
- Status: PARTIAL
- Requirement: Certification decisions SHALL be evidence-based.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: status=CERTIFIED / NOT_CERTIFIED (models.py CertificationStatus) is a real, binary, evidence-derived decision outcome, the same decision-matrix concept this appendix requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## DEC-002

- Specification / section: MCC-CP-001 / Appendix B — Certification Decision Matrix / B.4 Decision Invariants
- Status: PARTIAL
- Requirement: Certification decisions SHALL remain reproducible.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: status=CERTIFIED / NOT_CERTIFIED (models.py CertificationStatus) is a real, binary, evidence-derived decision outcome, the same decision-matrix concept this appendix requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## DEC-003

- Specification / section: MCC-CP-001 / Appendix B — Certification Decision Matrix / B.4 Decision Invariants
- Status: PARTIAL
- Requirement: Certification decisions SHALL remain independently verifiable.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: status=CERTIFIED / NOT_CERTIFIED (models.py CertificationStatus) is a real, binary, evidence-derived decision outcome, the same decision-matrix concept this appendix requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## DEC-004

- Specification / section: MCC-CP-001 / Appendix B — Certification Decision Matrix / B.4 Decision Invariants
- Status: PARTIAL
- Requirement: Certification decisions SHALL reference the applicable specification version.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: status=CERTIFIED / NOT_CERTIFIED (models.py CertificationStatus) is a real, binary, evidence-derived decision outcome, the same decision-matrix concept this appendix requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## DEC-005

- Specification / section: MCC-CP-001 / Appendix B — Certification Decision Matrix / B.4 Decision Invariants
- Status: PARTIAL
- Requirement: Certification decisions SHALL reference the Certification Manifest.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: status=CERTIFIED / NOT_CERTIFIED (models.py CertificationStatus) is a real, binary, evidence-derived decision outcome, the same decision-matrix concept this appendix requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## DEC-006

- Specification / section: MCC-CP-001 / Appendix B — Certification Decision Matrix / B.4 Decision Invariants
- Status: PARTIAL
- Requirement: Certification decisions SHALL reference the Evidence Bundle.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: status=CERTIFIED / NOT_CERTIFIED (models.py CertificationStatus) is a real, binary, evidence-derived decision outcome, the same decision-matrix concept this appendix requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## DEC-007

- Specification / section: MCC-CP-001 / Appendix B — Certification Decision Matrix / B.4 Decision Invariants
- Status: PARTIAL
- Requirement: Certification decisions SHALL reference the Technical Certificate when certification is granted.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: status=CERTIFIED / NOT_CERTIFIED (models.py CertificationStatus) is a real, binary, evidence-derived decision outcome, the same decision-matrix concept this appendix requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## EVID-001

- Specification / section: MCC-CP-001 / 14. Evidence Requirements / 14.6 Evidence Invariants
- Status: PARTIAL
- Requirement: Evidence SHALL be reproducible.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_evidence implements reproducible, traceable, verifiable, immutable-after-generation evidence for a governance run, the same evidence-property model this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## EVID-002

- Specification / section: MCC-CP-001 / 14. Evidence Requirements / 14.6 Evidence Invariants
- Status: PARTIAL
- Requirement: Evidence SHALL remain framework-neutral.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_evidence implements reproducible, traceable, verifiable, immutable-after-generation evidence for a governance run, the same evidence-property model this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## EVID-003

- Specification / section: MCC-CP-001 / 14. Evidence Requirements / 14.6 Evidence Invariants
- Status: PARTIAL
- Requirement: Evidence SHALL remain implementation-independent.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_evidence implements reproducible, traceable, verifiable, immutable-after-generation evidence for a governance run, the same evidence-property model this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## EVID-004

- Specification / section: MCC-CP-001 / 14. Evidence Requirements / 14.6 Evidence Invariants
- Status: PARTIAL
- Requirement: Evidence SHALL remain traceable.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_evidence implements reproducible, traceable, verifiable, immutable-after-generation evidence for a governance run, the same evidence-property model this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## EVID-005

- Specification / section: MCC-CP-001 / 14. Evidence Requirements / 14.6 Evidence Invariants
- Status: PARTIAL
- Requirement: Evidence SHALL support independent verification.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_evidence implements reproducible, traceable, verifiable, immutable-after-generation evidence for a governance run, the same evidence-property model this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## EVID-006

- Specification / section: MCC-CP-001 / 14. Evidence Requirements / 14.6 Evidence Invariants
- Status: PARTIAL
- Requirement: Evidence SHALL reference specification versions.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_evidence implements reproducible, traceable, verifiable, immutable-after-generation evidence for a governance run, the same evidence-property model this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## EVID-007

- Specification / section: MCC-CP-001 / 14. Evidence Requirements / 14.6 Evidence Invariants
- Status: PARTIAL
- Requirement: Evidence SHALL remain immutable after certification.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_evidence implements reproducible, traceable, verifiable, immutable-after-generation evidence for a governance run, the same evidence-property model this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## EX-001

- Specification / section: MCC-CP-001 / Appendix E — Example Certification Flow / E.3 Example Invariants
- Status: NOT_APPLICABLE
- Requirement: Examples SHALL remain non-normative.
- Existing implementation: None
- Missing implementation behavior: N/A (not an implementable requirement).
- Missing test coverage: No test exists for this requirement.
- Missing evidence: N/A
- Rationale: Interpretive, bibliographic, non-normative-by-design (explicitly marked informative/example), or document-self-referential statement. It does not describe a discrete, independently implementable system behavior.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: N/A

## EX-002

- Specification / section: MCC-CP-001 / Appendix E — Example Certification Flow / E.3 Example Invariants
- Status: NOT_APPLICABLE
- Requirement: Examples SHALL remain consistent with normative requirements.
- Existing implementation: None
- Missing implementation behavior: N/A (not an implementable requirement).
- Missing test coverage: No test exists for this requirement.
- Missing evidence: N/A
- Rationale: Interpretive, bibliographic, non-normative-by-design (explicitly marked informative/example), or document-self-referential statement. It does not describe a discrete, independently implementable system behavior.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: N/A

## EX-003

- Specification / section: MCC-CP-001 / Appendix E — Example Certification Flow / E.3 Example Invariants
- Status: NOT_APPLICABLE
- Requirement: Examples SHALL remain reproducible.
- Existing implementation: None
- Missing implementation behavior: N/A (not an implementable requirement).
- Missing test coverage: No test exists for this requirement.
- Missing evidence: N/A
- Rationale: Interpretive, bibliographic, non-normative-by-design (explicitly marked informative/example), or document-self-referential statement. It does not describe a discrete, independently implementable system behavior.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: N/A

## EX-004

- Specification / section: MCC-CP-001 / Appendix E — Example Certification Flow / E.3 Example Invariants
- Status: NOT_APPLICABLE
- Requirement: Examples SHALL remain implementation-independent.
- Existing implementation: None
- Missing implementation behavior: N/A (not an implementable requirement).
- Missing test coverage: No test exists for this requirement.
- Missing evidence: N/A
- Rationale: Interpretive, bibliographic, non-normative-by-design (explicitly marked informative/example), or document-self-referential statement. It does not describe a discrete, independently implementable system behavior.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: N/A

## EX-005

- Specification / section: MCC-CP-001 / Appendix E — Example Certification Flow / E.3 Example Invariants
- Status: NOT_APPLICABLE
- Requirement: Examples SHALL remain framework-neutral.
- Existing implementation: None
- Missing implementation behavior: N/A (not an implementable requirement).
- Missing test coverage: No test exists for this requirement.
- Missing evidence: N/A
- Rationale: Interpretive, bibliographic, non-normative-by-design (explicitly marked informative/example), or document-self-referential statement. It does not describe a discrete, independently implementable system behavior.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: N/A

## EX-006

- Specification / section: MCC-CP-001 / Appendix E — Example Certification Flow / E.3 Example Invariants
- Status: NOT_APPLICABLE
- Requirement: Examples SHALL NOT introduce additional requirements.
- Existing implementation: None
- Missing implementation behavior: N/A (not an implementable requirement).
- Missing test coverage: No test exists for this requirement.
- Missing evidence: N/A
- Rationale: Interpretive, bibliographic, non-normative-by-design (explicitly marked informative/example), or document-self-referential statement. It does not describe a discrete, independently implementable system behavior.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: N/A

## EX-007

- Specification / section: MCC-CP-001 / Appendix E — Example Certification Flow / E.3 Example Invariants
- Status: NOT_APPLICABLE
- Requirement: Examples SHALL support understanding of the certification process.
- Existing implementation: None
- Missing implementation behavior: N/A (not an implementable requirement).
- Missing test coverage: No test exists for this requirement.
- Missing evidence: N/A
- Rationale: Interpretive, bibliographic, non-normative-by-design (explicitly marked informative/example), or document-self-referential statement. It does not describe a discrete, independently implementable system behavior.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: N/A

## EXT-001

- Specification / section: MCC-CP-001 / Appendix F — Future Extensions / F.3 Extension Invariants
- Status: NOT_APPLICABLE
- Requirement: Future extensions SHALL preserve the normative architecture.
- Existing implementation: None
- Missing implementation behavior: N/A (not an implementable requirement).
- Missing test coverage: No test exists for this requirement.
- Missing evidence: N/A
- Rationale: Interpretive, bibliographic, non-normative-by-design (explicitly marked informative/example), or document-self-referential statement. It does not describe a discrete, independently implementable system behavior.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: N/A

## EXT-002

- Specification / section: MCC-CP-001 / Appendix F — Future Extensions / F.3 Extension Invariants
- Status: NOT_APPLICABLE
- Requirement: Future extensions SHALL remain framework-neutral.
- Existing implementation: None
- Missing implementation behavior: N/A (not an implementable requirement).
- Missing test coverage: No test exists for this requirement.
- Missing evidence: N/A
- Rationale: Interpretive, bibliographic, non-normative-by-design (explicitly marked informative/example), or document-self-referential statement. It does not describe a discrete, independently implementable system behavior.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: N/A

## EXT-003

- Specification / section: MCC-CP-001 / Appendix F — Future Extensions / F.3 Extension Invariants
- Status: NOT_APPLICABLE
- Requirement: Future extensions SHALL remain implementation-independent.
- Existing implementation: None
- Missing implementation behavior: N/A (not an implementable requirement).
- Missing test coverage: No test exists for this requirement.
- Missing evidence: N/A
- Rationale: Interpretive, bibliographic, non-normative-by-design (explicitly marked informative/example), or document-self-referential statement. It does not describe a discrete, independently implementable system behavior.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: N/A

## EXT-004

- Specification / section: MCC-CP-001 / Appendix F — Future Extensions / F.3 Extension Invariants
- Status: NOT_APPLICABLE
- Requirement: Future extensions SHALL preserve reproducibility.
- Existing implementation: None
- Missing implementation behavior: N/A (not an implementable requirement).
- Missing test coverage: No test exists for this requirement.
- Missing evidence: N/A
- Rationale: Interpretive, bibliographic, non-normative-by-design (explicitly marked informative/example), or document-self-referential statement. It does not describe a discrete, independently implementable system behavior.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: N/A

## EXT-005

- Specification / section: MCC-CP-001 / Appendix F — Future Extensions / F.3 Extension Invariants
- Status: NOT_APPLICABLE
- Requirement: Future extensions SHALL preserve independent verification.
- Existing implementation: None
- Missing implementation behavior: N/A (not an implementable requirement).
- Missing test coverage: No test exists for this requirement.
- Missing evidence: N/A
- Rationale: Interpretive, bibliographic, non-normative-by-design (explicitly marked informative/example), or document-self-referential statement. It does not describe a discrete, independently implementable system behavior.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: N/A

## EXT-006

- Specification / section: MCC-CP-001 / Appendix F — Future Extensions / F.3 Extension Invariants
- Status: NOT_APPLICABLE
- Requirement: Future extensions SHALL preserve traceability.
- Existing implementation: None
- Missing implementation behavior: N/A (not an implementable requirement).
- Missing test coverage: No test exists for this requirement.
- Missing evidence: N/A
- Rationale: Interpretive, bibliographic, non-normative-by-design (explicitly marked informative/example), or document-self-referential statement. It does not describe a discrete, independently implementable system behavior.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: N/A

## EXT-007

- Specification / section: MCC-CP-001 / Appendix F — Future Extensions / F.3 Extension Invariants
- Status: NOT_APPLICABLE
- Requirement: Future extensions SHALL preserve compatibility with published specification versions unless explicitly documented otherwise.
- Existing implementation: None
- Missing implementation behavior: N/A (not an implementable requirement).
- Missing test coverage: No test exists for this requirement.
- Missing evidence: N/A
- Rationale: Interpretive, bibliographic, non-normative-by-design (explicitly marked informative/example), or document-self-referential statement. It does not describe a discrete, independently implementable system behavior.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: N/A

## MAN-001

- Specification / section: MCC-CP-001 / 15. Certification Manifest Requirements / 15.6 Manifest Invariants
- Status: PARTIAL
- Requirement: Certification Manifests SHALL be machine-readable.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: certifications/manifest.json is a real, structured, machine-readable certification-result record, the same artifact class this section requires, under different field names and scope.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MAN-002

- Specification / section: MCC-CP-001 / 15. Certification Manifest Requirements / 15.6 Manifest Invariants
- Status: PARTIAL
- Requirement: Certification Manifests SHALL remain framework-neutral.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: certifications/manifest.json is a real, structured, machine-readable certification-result record, the same artifact class this section requires, under different field names and scope.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MAN-003

- Specification / section: MCC-CP-001 / 15. Certification Manifest Requirements / 15.6 Manifest Invariants
- Status: PARTIAL
- Requirement: Certification Manifests SHALL remain implementation-independent.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: certifications/manifest.json is a real, structured, machine-readable certification-result record, the same artifact class this section requires, under different field names and scope.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MAN-004

- Specification / section: MCC-CP-001 / 15. Certification Manifest Requirements / 15.6 Manifest Invariants
- Status: PARTIAL
- Requirement: Certification Manifests SHALL reference certification evidence.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: certifications/manifest.json is a real, structured, machine-readable certification-result record, the same artifact class this section requires, under different field names and scope.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MAN-005

- Specification / section: MCC-CP-001 / 15. Certification Manifest Requirements / 15.6 Manifest Invariants
- Status: PARTIAL
- Requirement: Certification Manifests SHALL remain traceable.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: certifications/manifest.json is a real, structured, machine-readable certification-result record, the same artifact class this section requires, under different field names and scope.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MAN-006

- Specification / section: MCC-CP-001 / 15. Certification Manifest Requirements / 15.6 Manifest Invariants
- Status: PARTIAL
- Requirement: Certification Manifests SHALL declare specification versions.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: certifications/manifest.json is a real, structured, machine-readable certification-result record, the same artifact class this section requires, under different field names and scope.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MAN-007

- Specification / section: MCC-CP-001 / 15. Certification Manifest Requirements / 15.6 Manifest Invariants
- Status: PARTIAL
- Requirement: Certification Manifests SHALL remain immutable after publication.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: certifications/manifest.json is a real, structured, machine-readable certification-result record, the same artifact class this section requires, under different field names and scope.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-10-CONFORMANCE-MODEL-D01

- Specification / section: MCC-CP-001 / 10. Conformance Model / 10.1 Purpose
- Status: PARTIAL
- Requirement: Conformance SHALL be evaluated only against normative requirements defined by MCC specifications.
- Existing implementation: src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: Each compliance vector produces a real pass/fail-style CaseResult, aggregated into scenarios_passed / scenarios_failed / scenarios_total, the same evaluated-outcome model this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-10-CONFORMANCE-MODEL-D02

- Specification / section: MCC-CP-001 / 10. Conformance Model / 10.1 Purpose
- Status: PARTIAL
- Requirement: No implementation-specific behavior SHALL influence conformance results.
- Existing implementation: src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: Each compliance vector produces a real pass/fail-style CaseResult, aggregated into scenarios_passed / scenarios_failed / scenarios_total, the same evaluated-outcome model this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-10-CONFORMANCE-MODEL-D03

- Specification / section: MCC-CP-001 / 10. Conformance Model / 10.2 Normative Requirements
- Status: PARTIAL
- Requirement: Each normative requirement SHALL have a unique identifier.
- Existing implementation: src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: Each compliance vector produces a real pass/fail-style CaseResult, aggregated into scenarios_passed / scenarios_failed / scenarios_total, the same evaluated-outcome model this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-10-CONFORMANCE-MODEL-D04

- Specification / section: MCC-CP-001 / 10. Conformance Model / 10.2 Normative Requirements
- Status: PARTIAL
- Requirement: Each requirement SHALL define: - identifier; - requirement statement; - applicability; - verification method; - expected outcome.
- Existing implementation: src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: Each compliance vector produces a real pass/fail-style CaseResult, aggregated into scenarios_passed / scenarios_failed / scenarios_total, the same evaluated-outcome model this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-10-CONFORMANCE-MODEL-D05

- Specification / section: MCC-CP-001 / 10. Conformance Model / 10.2 Normative Requirements
- Status: PARTIAL
- Requirement: Requirements SHALL remain stable within a published specification version.
- Existing implementation: src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: Each compliance vector produces a real pass/fail-style CaseResult, aggregated into scenarios_passed / scenarios_failed / scenarios_total, the same evaluated-outcome model this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-10-CONFORMANCE-MODEL-D06

- Specification / section: MCC-CP-001 / 10. Conformance Model / 10.3 Requirement Classification
- Status: PARTIAL
- Requirement: Normative requirements SHALL be classified as one of: - REQUIRED - OPTIONAL - CONDITIONAL
- Existing implementation: src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: Each compliance vector produces a real pass/fail-style CaseResult, aggregated into scenarios_passed / scenarios_failed / scenarios_total, the same evaluated-outcome model this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-10-CONFORMANCE-MODEL-D07

- Specification / section: MCC-CP-001 / 10. Conformance Model / 10.3 Requirement Classification
- Status: PARTIAL
- Requirement: REQUIRED requirements SHALL always be evaluated.
- Existing implementation: src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: Each compliance vector produces a real pass/fail-style CaseResult, aggregated into scenarios_passed / scenarios_failed / scenarios_total, the same evaluated-outcome model this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-10-CONFORMANCE-MODEL-D08

- Specification / section: MCC-CP-001 / 10. Conformance Model / 10.3 Requirement Classification
- Status: PARTIAL
- Requirement: OPTIONAL requirements SHALL NOT affect mandatory certification.
- Existing implementation: src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: Each compliance vector produces a real pass/fail-style CaseResult, aggregated into scenarios_passed / scenarios_failed / scenarios_total, the same evaluated-outcome model this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-10-CONFORMANCE-MODEL-D09

- Specification / section: MCC-CP-001 / 10. Conformance Model / 10.3 Requirement Classification
- Status: PARTIAL
- Requirement: CONDITIONAL requirements SHALL apply only when their stated conditions are satisfied.
- Existing implementation: src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: Each compliance vector produces a real pass/fail-style CaseResult, aggregated into scenarios_passed / scenarios_failed / scenarios_total, the same evaluated-outcome model this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-10-CONFORMANCE-MODEL-D10

- Specification / section: MCC-CP-001 / 10. Conformance Model / 10.4 Conformance Evaluation
- Status: PARTIAL
- Requirement: Each evaluated requirement SHALL produce exactly one outcome: - PASS - FAIL - NOT APPLICABLE
- Existing implementation: src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: Each compliance vector produces a real pass/fail-style CaseResult, aggregated into scenarios_passed / scenarios_failed / scenarios_total, the same evaluated-outcome model this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-10-CONFORMANCE-MODEL-D11

- Specification / section: MCC-CP-001 / 10. Conformance Model / 10.5 Overall Conformance
- Status: PARTIAL
- Requirement: Overall conformance SHALL be determined only after all REQUIRED and applicable CONDITIONAL requirements have been evaluated.
- Existing implementation: src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: Each compliance vector produces a real pass/fail-style CaseResult, aggregated into scenarios_passed / scenarios_failed / scenarios_total, the same evaluated-outcome model this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-10-CONFORMANCE-MODEL-D12

- Specification / section: MCC-CP-001 / 10. Conformance Model / 10.5 Overall Conformance
- Status: PARTIAL
- Requirement: Certification SHALL NOT be issued if any REQUIRED requirement fails.
- Existing implementation: src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: Each compliance vector produces a real pass/fail-style CaseResult, aggregated into scenarios_passed / scenarios_failed / scenarios_total, the same evaluated-outcome model this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-10-CONFORMANCE-MODEL-D13

- Specification / section: MCC-CP-001 / 10. Conformance Model / 10.5 Overall Conformance
- Status: PARTIAL
- Requirement: OPTIONAL requirements SHALL NOT prevent certification.
- Existing implementation: src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: Each compliance vector produces a real pass/fail-style CaseResult, aggregated into scenarios_passed / scenarios_failed / scenarios_total, the same evaluated-outcome model this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-11-CAPABILITY-PROFILES-D01

- Specification / section: MCC-CP-001 / 11. Capability Profiles / 11.2 Capability Profile Identifier
- Status: PARTIAL
- Requirement: Each Capability Profile SHALL have a globally unique identifier.
- Existing implementation: src/mcc_compliance/capability_profile.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_compliance/capability_profile.py is a real, tested, versioned, fail-closed capability-profile validator (declared/validated/certified/authorized trust ladder) — a close analog to this section.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-11-CAPABILITY-PROFILES-D02

- Specification / section: MCC-CP-001 / 11. Capability Profiles / 11.2 Capability Profile Identifier
- Status: PARTIAL
- Requirement: Each profile SHALL define: - profile identifier; - profile name; - specification version; - capability set; - applicability conditions.
- Existing implementation: src/mcc_compliance/capability_profile.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_compliance/capability_profile.py is a real, tested, versioned, fail-closed capability-profile validator (declared/validated/certified/authorized trust ladder) — a close analog to this section.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-11-CAPABILITY-PROFILES-D03

- Specification / section: MCC-CP-001 / 11. Capability Profiles / 11.2 Capability Profile Identifier
- Status: PARTIAL
- Requirement: Capability Profile identifiers SHALL remain stable within a published specification version.
- Existing implementation: src/mcc_compliance/capability_profile.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_compliance/capability_profile.py is a real, tested, versioned, fail-closed capability-profile validator (declared/validated/certified/authorized trust ladder) — a close analog to this section.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-11-CAPABILITY-PROFILES-D04

- Specification / section: MCC-CP-001 / 11. Capability Profiles / 11.3 Capability Definition
- Status: PARTIAL
- Requirement: Each capability SHALL define: - capability identifier; - capability description; - normative requirements; - verification method; - expected outcome.
- Existing implementation: src/mcc_compliance/capability_profile.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_compliance/capability_profile.py is a real, tested, versioned, fail-closed capability-profile validator (declared/validated/certified/authorized trust ladder) — a close analog to this section.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-11-CAPABILITY-PROFILES-D05

- Specification / section: MCC-CP-001 / 11. Capability Profiles / 11.3 Capability Definition
- Status: PARTIAL
- Requirement: Capabilities SHALL reference only normative MCC requirements.
- Existing implementation: src/mcc_compliance/capability_profile.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_compliance/capability_profile.py is a real, tested, versioned, fail-closed capability-profile validator (declared/validated/certified/authorized trust ladder) — a close analog to this section.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-11-CAPABILITY-PROFILES-D06

- Specification / section: MCC-CP-001 / 11. Capability Profiles / 11.4 Capability Evaluation
- Status: PARTIAL
- Requirement: Each declared capability SHALL be evaluated independently.
- Existing implementation: src/mcc_compliance/capability_profile.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_compliance/capability_profile.py is a real, tested, versioned, fail-closed capability-profile validator (declared/validated/certified/authorized trust ladder) — a close analog to this section.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-11-CAPABILITY-PROFILES-D07

- Specification / section: MCC-CP-001 / 11. Capability Profiles / 11.4 Capability Evaluation
- Status: PARTIAL
- Requirement: Capability evaluation SHALL produce one of the following outcomes: - PASS - FAIL - NOT APPLICABLE
- Existing implementation: src/mcc_compliance/capability_profile.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_compliance/capability_profile.py is a real, tested, versioned, fail-closed capability-profile validator (declared/validated/certified/authorized trust ladder) — a close analog to this section.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-11-CAPABILITY-PROFILES-D08

- Specification / section: MCC-CP-001 / 11. Capability Profiles / 11.4 Capability Evaluation
- Status: PARTIAL
- Requirement: Capability evaluation SHALL be reproducible.
- Existing implementation: src/mcc_compliance/capability_profile.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_compliance/capability_profile.py is a real, tested, versioned, fail-closed capability-profile validator (declared/validated/certified/authorized trust ladder) — a close analog to this section.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-11-CAPABILITY-PROFILES-D09

- Specification / section: MCC-CP-001 / 11. Capability Profiles / 11.5 Capability Dependencies
- Status: PARTIAL
- Requirement: Dependent capabilities SHALL be evaluated before the capability that references them.
- Existing implementation: src/mcc_compliance/capability_profile.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_compliance/capability_profile.py is a real, tested, versioned, fail-closed capability-profile validator (declared/validated/certified/authorized trust ladder) — a close analog to this section.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-11-CAPABILITY-PROFILES-D10

- Specification / section: MCC-CP-001 / 11. Capability Profiles / 11.5 Capability Dependencies
- Status: PARTIAL
- Requirement: Circular capability dependencies SHALL NOT be permitted.
- Existing implementation: src/mcc_compliance/capability_profile.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_compliance/capability_profile.py is a real, tested, versioned, fail-closed capability-profile validator (declared/validated/certified/authorized trust ladder) — a close analog to this section.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-11-CAPABILITY-PROFILES-D11

- Specification / section: MCC-CP-001 / 11. Capability Profiles / 11.6 Capability Claims
- Status: PARTIAL
- Requirement: Capability claims SHALL be verified during certification.
- Existing implementation: src/mcc_compliance/capability_profile.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_compliance/capability_profile.py is a real, tested, versioned, fail-closed capability-profile validator (declared/validated/certified/authorized trust ladder) — a close analog to this section.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-11-CAPABILITY-PROFILES-D12

- Specification / section: MCC-CP-001 / 11. Capability Profiles / 11.6 Capability Claims
- Status: PARTIAL
- Requirement: Unverified capability claims SHALL NOT appear within Certification Manifests or Technical Certificates.
- Existing implementation: src/mcc_compliance/capability_profile.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_compliance/capability_profile.py is a real, tested, versioned, fail-closed capability-profile validator (declared/validated/certified/authorized trust ladder) — a close analog to this section.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-12-CERTIFICATION-REQUIREMENTS-D01

- Specification / section: MCC-CP-001 / 12. Certification Requirements / 12.1 Purpose
- Status: PARTIAL
- Requirement: Certification Requirements define the normative requirements that SHALL be evaluated during certification.
- Existing implementation: src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: The compliance vector manifest (src/mcc_compliance/vectors/v1/manifest.json) gives each requirement-like vector a stable id, an associated invariant/requirement name, and a verification scenario — the same requirement-identity model this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-12-CERTIFICATION-REQUIREMENTS-D02

- Specification / section: MCC-CP-001 / 12. Certification Requirements / 12.1 Purpose
- Status: PARTIAL
- Requirement: Certification Requirements SHALL be technology-independent and framework-neutral.
- Existing implementation: src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: The compliance vector manifest (src/mcc_compliance/vectors/v1/manifest.json) gives each requirement-like vector a stable id, an associated invariant/requirement name, and a verification scenario — the same requirement-identity model this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-12-CERTIFICATION-REQUIREMENTS-D03

- Specification / section: MCC-CP-001 / 12. Certification Requirements / 12.1 Purpose
- Status: PARTIAL
- Requirement: Certification SHALL evaluate only published normative requirements.
- Existing implementation: src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: The compliance vector manifest (src/mcc_compliance/vectors/v1/manifest.json) gives each requirement-like vector a stable id, an associated invariant/requirement name, and a verification scenario — the same requirement-identity model this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-12-CERTIFICATION-REQUIREMENTS-D04

- Specification / section: MCC-CP-001 / 12. Certification Requirements / 12.2 Requirement Identifier
- Status: PARTIAL
- Requirement: Each Certification Requirement SHALL define: - requirement identifier; - requirement title; - normative statement; - applicability; - verification method; - expected outcome.
- Existing implementation: src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: The compliance vector manifest (src/mcc_compliance/vectors/v1/manifest.json) gives each requirement-like vector a stable id, an associated invariant/requirement name, and a verification scenario — the same requirement-identity model this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-12-CERTIFICATION-REQUIREMENTS-D05

- Specification / section: MCC-CP-001 / 12. Certification Requirements / 12.2 Requirement Identifier
- Status: PARTIAL
- Requirement: Requirement identifiers SHALL be globally unique within a specification version.
- Existing implementation: src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: The compliance vector manifest (src/mcc_compliance/vectors/v1/manifest.json) gives each requirement-like vector a stable id, an associated invariant/requirement name, and a verification scenario — the same requirement-identity model this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-12-CERTIFICATION-REQUIREMENTS-D06

- Specification / section: MCC-CP-001 / 12. Certification Requirements / 12.3 Requirement Applicability
- Status: PARTIAL
- Requirement: Each requirement SHALL specify its applicability.
- Existing implementation: src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: The compliance vector manifest (src/mcc_compliance/vectors/v1/manifest.json) gives each requirement-like vector a stable id, an associated invariant/requirement name, and a verification scenario — the same requirement-identity model this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-12-CERTIFICATION-REQUIREMENTS-D07

- Specification / section: MCC-CP-001 / 12. Certification Requirements / 12.3 Requirement Applicability
- Status: PARTIAL
- Requirement: Requirements SHALL NOT be evaluated outside their stated applicability.
- Existing implementation: src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: The compliance vector manifest (src/mcc_compliance/vectors/v1/manifest.json) gives each requirement-like vector a stable id, an associated invariant/requirement name, and a verification scenario — the same requirement-identity model this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-12-CERTIFICATION-REQUIREMENTS-D08

- Specification / section: MCC-CP-001 / 12. Certification Requirements / 12.4 Requirement Verification
- Status: PARTIAL
- Requirement: Each requirement SHALL define at least one normative verification method.
- Existing implementation: src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: The compliance vector manifest (src/mcc_compliance/vectors/v1/manifest.json) gives each requirement-like vector a stable id, an associated invariant/requirement name, and a verification scenario — the same requirement-identity model this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-12-CERTIFICATION-REQUIREMENTS-D09

- Specification / section: MCC-CP-001 / 12. Certification Requirements / 12.4 Requirement Verification
- Status: PARTIAL
- Requirement: Verification methods SHALL produce reproducible results.
- Existing implementation: src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: The compliance vector manifest (src/mcc_compliance/vectors/v1/manifest.json) gives each requirement-like vector a stable id, an associated invariant/requirement name, and a verification scenario — the same requirement-identity model this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-12-CERTIFICATION-REQUIREMENTS-D10

- Specification / section: MCC-CP-001 / 12. Certification Requirements / 12.4 Requirement Verification
- Status: PARTIAL
- Requirement: Verification SHALL remain implementation-independent.
- Existing implementation: src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: The compliance vector manifest (src/mcc_compliance/vectors/v1/manifest.json) gives each requirement-like vector a stable id, an associated invariant/requirement name, and a verification scenario — the same requirement-identity model this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-12-CERTIFICATION-REQUIREMENTS-D11

- Specification / section: MCC-CP-001 / 12. Certification Requirements / 12.5 Requirement Traceability
- Status: PARTIAL
- Requirement: Every Certification Requirement SHALL be traceable to: - the governing specification; - the evaluated capability profile, if applicable; - the verification result; - the generated Evidence Bundle.
- Existing implementation: src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: The compliance vector manifest (src/mcc_compliance/vectors/v1/manifest.json) gives each requirement-like vector a stable id, an associated invariant/requirement name, and a verification scenario — the same requirement-identity model this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-12-CERTIFICATION-REQUIREMENTS-D12

- Specification / section: MCC-CP-001 / 12. Certification Requirements / 12.5 Requirement Traceability
- Status: PARTIAL
- Requirement: Traceability SHALL be preserved throughout certification.
- Existing implementation: src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: The compliance vector manifest (src/mcc_compliance/vectors/v1/manifest.json) gives each requirement-like vector a stable id, an associated invariant/requirement name, and a verification scenario — the same requirement-identity model this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-13-REQUIREMENT-CLASSIFICATION-D01

- Specification / section: MCC-CP-001 / 13. Requirement Classification / 13.1 Purpose
- Status: PARTIAL
- Requirement: Classification SHALL determine how requirements participate in certification.
- Existing implementation: src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: Each compliance vector carries an explicit boolean `mandatory` flag (src/mcc_compliance/vectors/v1/manifest.json), the same required-vs-optional classification concept this section requires, though only a two-way (not three-way REQUIRED/OPTIONAL/CONDITIONAL) split was found.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-13-REQUIREMENT-CLASSIFICATION-D02

- Specification / section: MCC-CP-001 / 13. Requirement Classification / 13.1 Purpose
- Status: PARTIAL
- Requirement: Requirement Classification SHALL remain framework-neutral.
- Existing implementation: src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: Each compliance vector carries an explicit boolean `mandatory` flag (src/mcc_compliance/vectors/v1/manifest.json), the same required-vs-optional classification concept this section requires, though only a two-way (not three-way REQUIRED/OPTIONAL/CONDITIONAL) split was found.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-13-REQUIREMENT-CLASSIFICATION-D03

- Specification / section: MCC-CP-001 / 13. Requirement Classification / 13.2 Classification Categories
- Status: PARTIAL
- Requirement: Each Certification Requirement SHALL be classified as exactly one of: - REQUIRED - OPTIONAL - CONDITIONAL
- Existing implementation: src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: Each compliance vector carries an explicit boolean `mandatory` flag (src/mcc_compliance/vectors/v1/manifest.json), the same required-vs-optional classification concept this section requires, though only a two-way (not three-way REQUIRED/OPTIONAL/CONDITIONAL) split was found.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-13-REQUIREMENT-CLASSIFICATION-D04

- Specification / section: MCC-CP-001 / 13. Requirement Classification / 13.2 Classification Categories
- Status: PARTIAL
- Requirement: Multiple classifications for the same requirement SHALL NOT be permitted.
- Existing implementation: src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: Each compliance vector carries an explicit boolean `mandatory` flag (src/mcc_compliance/vectors/v1/manifest.json), the same required-vs-optional classification concept this section requires, though only a two-way (not three-way REQUIRED/OPTIONAL/CONDITIONAL) split was found.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-13-REQUIREMENT-CLASSIFICATION-D05

- Specification / section: MCC-CP-001 / 13. Requirement Classification / 13.3 REQUIRED Requirements
- Status: PARTIAL
- Requirement: REQUIRED requirements SHALL always be evaluated.
- Existing implementation: src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: Each compliance vector carries an explicit boolean `mandatory` flag (src/mcc_compliance/vectors/v1/manifest.json), the same required-vs-optional classification concept this section requires, though only a two-way (not three-way REQUIRED/OPTIONAL/CONDITIONAL) split was found.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-13-REQUIREMENT-CLASSIFICATION-D06

- Specification / section: MCC-CP-001 / 13. Requirement Classification / 13.3 REQUIRED Requirements
- Status: PARTIAL
- Requirement: Failure of a REQUIRED requirement SHALL prevent certification.
- Existing implementation: src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: Each compliance vector carries an explicit boolean `mandatory` flag (src/mcc_compliance/vectors/v1/manifest.json), the same required-vs-optional classification concept this section requires, though only a two-way (not three-way REQUIRED/OPTIONAL/CONDITIONAL) split was found.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-13-REQUIREMENT-CLASSIFICATION-D07

- Specification / section: MCC-CP-001 / 13. Requirement Classification / 13.4 OPTIONAL Requirements
- Status: PARTIAL
- Requirement: Failure of OPTIONAL requirements SHALL NOT prevent certification.
- Existing implementation: src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: Each compliance vector carries an explicit boolean `mandatory` flag (src/mcc_compliance/vectors/v1/manifest.json), the same required-vs-optional classification concept this section requires, though only a two-way (not three-way REQUIRED/OPTIONAL/CONDITIONAL) split was found.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-13-REQUIREMENT-CLASSIFICATION-D08

- Specification / section: MCC-CP-001 / 13. Requirement Classification / 13.5 CONDITIONAL Requirements
- Status: PARTIAL
- Requirement: CONDITIONAL requirements SHALL apply only when their stated applicability conditions are satisfied.
- Existing implementation: src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: Each compliance vector carries an explicit boolean `mandatory` flag (src/mcc_compliance/vectors/v1/manifest.json), the same required-vs-optional classification concept this section requires, though only a two-way (not three-way REQUIRED/OPTIONAL/CONDITIONAL) split was found.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-13-REQUIREMENT-CLASSIFICATION-D09

- Specification / section: MCC-CP-001 / 13. Requirement Classification / 13.5 CONDITIONAL Requirements
- Status: PARTIAL
- Requirement: When applicability conditions are not satisfied, the requirement SHALL produce the result NOT APPLICABLE.
- Existing implementation: src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: Each compliance vector carries an explicit boolean `mandatory` flag (src/mcc_compliance/vectors/v1/manifest.json), the same required-vs-optional classification concept this section requires, though only a two-way (not three-way REQUIRED/OPTIONAL/CONDITIONAL) split was found.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-14-EVIDENCE-REQUIREMENTS-D01

- Specification / section: MCC-CP-001 / 14. Evidence Requirements / 14.1 Purpose
- Status: PARTIAL
- Requirement: Certification evidence SHALL support independent verification of certification results.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_evidence implements reproducible, traceable, verifiable, immutable-after-generation evidence for a governance run, the same evidence-property model this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-14-EVIDENCE-REQUIREMENTS-D02

- Specification / section: MCC-CP-001 / 14. Evidence Requirements / 14.1 Purpose
- Status: PARTIAL
- Requirement: Evidence SHALL remain implementation-independent and framework-neutral.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_evidence implements reproducible, traceable, verifiable, immutable-after-generation evidence for a governance run, the same evidence-property model this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-14-EVIDENCE-REQUIREMENTS-D03

- Specification / section: MCC-CP-001 / 14. Evidence Requirements / 14.2 Evidence Sources
- Status: PARTIAL
- Requirement: Evidence sources SHALL be explicitly identified.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_evidence implements reproducible, traceable, verifiable, immutable-after-generation evidence for a governance run, the same evidence-property model this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-14-EVIDENCE-REQUIREMENTS-D04

- Specification / section: MCC-CP-001 / 14. Evidence Requirements / 14.3 Evidence Properties
- Status: PARTIAL
- Requirement: Certification evidence SHALL be: - reproducible; - traceable; - verifiable; - immutable after generation; - attributable to a certification run.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_evidence implements reproducible, traceable, verifiable, immutable-after-generation evidence for a governance run, the same evidence-property model this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-14-EVIDENCE-REQUIREMENTS-D05

- Specification / section: MCC-CP-001 / 14. Evidence Requirements / 14.3 Evidence Properties
- Status: PARTIAL
- Requirement: Evidence SHALL reference the applicable specification version.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_evidence implements reproducible, traceable, verifiable, immutable-after-generation evidence for a governance run, the same evidence-property model this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-14-EVIDENCE-REQUIREMENTS-D06

- Specification / section: MCC-CP-001 / 14. Evidence Requirements / 14.4 Evidence Traceability
- Status: PARTIAL
- Requirement: Every evidence item SHALL be traceable to: - the Certification Subject; - the evaluated requirement; - the verification result; - the certification decision.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_evidence implements reproducible, traceable, verifiable, immutable-after-generation evidence for a governance run, the same evidence-property model this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-14-EVIDENCE-REQUIREMENTS-D07

- Specification / section: MCC-CP-001 / 14. Evidence Requirements / 14.4 Evidence Traceability
- Status: PARTIAL
- Requirement: Evidence traceability SHALL be preserved throughout certification.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_evidence implements reproducible, traceable, verifiable, immutable-after-generation evidence for a governance run, the same evidence-property model this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-14-EVIDENCE-REQUIREMENTS-D08

- Specification / section: MCC-CP-001 / 14. Evidence Requirements / 14.5 Evidence Retention
- Status: PARTIAL
- Requirement: Evidence SHALL remain available for independent verification.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_evidence implements reproducible, traceable, verifiable, immutable-after-generation evidence for a governance run, the same evidence-property model this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-14-EVIDENCE-REQUIREMENTS-D09

- Specification / section: MCC-CP-001 / 14. Evidence Requirements / 14.5 Evidence Retention
- Status: PARTIAL
- Requirement: Evidence SHALL NOT be modified after certification.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_evidence implements reproducible, traceable, verifiable, immutable-after-generation evidence for a governance run, the same evidence-property model this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-15-CERTIFICATION-MANIFEST-REQUIREMENTS-D01

- Specification / section: MCC-CP-001 / 15. Certification Manifest Requirements / 15.1 Purpose
- Status: PARTIAL
- Requirement: A Certification Manifest SHALL describe the certification results in a structured, machine-readable form.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: certifications/manifest.json is a real, structured, machine-readable certification-result record, the same artifact class this section requires, under different field names and scope.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-15-CERTIFICATION-MANIFEST-REQUIREMENTS-D02

- Specification / section: MCC-CP-001 / 15. Certification Manifest Requirements / 15.2 Manifest Contents
- Status: PARTIAL
- Requirement: Every Certification Manifest SHALL include: - manifest identifier; - specification version; - Certification Subject identifier; - capability profiles; - certification requirements evaluated; - certification result; - evidence references; - generation timestamp.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: certifications/manifest.json is a real, structured, machine-readable certification-result record, the same artifact class this section requires, under different field names and scope.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-15-CERTIFICATION-MANIFEST-REQUIREMENTS-D03

- Specification / section: MCC-CP-001 / 15. Certification Manifest Requirements / 15.3 Manifest Integrity
- Status: PARTIAL
- Requirement: Certification Manifests SHALL accurately represent the certification results.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: certifications/manifest.json is a real, structured, machine-readable certification-result record, the same artifact class this section requires, under different field names and scope.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-15-CERTIFICATION-MANIFEST-REQUIREMENTS-D04

- Specification / section: MCC-CP-001 / 15. Certification Manifest Requirements / 15.3 Manifest Integrity
- Status: PARTIAL
- Requirement: A Certification Manifest SHALL NOT contain unverifiable claims.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: certifications/manifest.json is a real, structured, machine-readable certification-result record, the same artifact class this section requires, under different field names and scope.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-15-CERTIFICATION-MANIFEST-REQUIREMENTS-D05

- Specification / section: MCC-CP-001 / 15. Certification Manifest Requirements / 15.3 Manifest Integrity
- Status: PARTIAL
- Requirement: Manifest integrity SHALL be preserved after generation.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: certifications/manifest.json is a real, structured, machine-readable certification-result record, the same artifact class this section requires, under different field names and scope.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-15-CERTIFICATION-MANIFEST-REQUIREMENTS-D06

- Specification / section: MCC-CP-001 / 15. Certification Manifest Requirements / 15.4 Manifest Traceability
- Status: PARTIAL
- Requirement: Every Certification Manifest SHALL be traceable to: - the Certification Subject; - the applicable specification version; - the Evidence Bundle; - the Technical Certificate, if issued.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: certifications/manifest.json is a real, structured, machine-readable certification-result record, the same artifact class this section requires, under different field names and scope.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-15-CERTIFICATION-MANIFEST-REQUIREMENTS-D07

- Specification / section: MCC-CP-001 / 15. Certification Manifest Requirements / 15.5 Manifest Versioning
- Status: PARTIAL
- Requirement: Certification Manifests SHALL declare the specification version against which certification was performed.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: certifications/manifest.json is a real, structured, machine-readable certification-result record, the same artifact class this section requires, under different field names and scope.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-15-CERTIFICATION-MANIFEST-REQUIREMENTS-D08

- Specification / section: MCC-CP-001 / 15. Certification Manifest Requirements / 15.5 Manifest Versioning
- Status: PARTIAL
- Requirement: Manifest versions SHALL remain immutable after publication.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: certifications/manifest.json is a real, structured, machine-readable certification-result record, the same artifact class this section requires, under different field names and scope.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-16-TECHNICAL-CERTIFICATE-REQUIREMENTS-D01

- Specification / section: MCC-CP-001 / 16. Technical Certificate Requirements / 16.1 Purpose
- Status: PARTIAL
- Requirement: A Technical Certificate SHALL represent the authoritative certification outcome for a Certification Subject.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: certifications/manifest.json's CERTIFIED entries are the closest analog to this section's authoritative certified-outcome record found in the repository.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-16-TECHNICAL-CERTIFICATE-REQUIREMENTS-D02

- Specification / section: MCC-CP-001 / 16. Technical Certificate Requirements / 16.1 Purpose
- Status: PARTIAL
- Requirement: Technical Certificates SHALL be derived only from successful certification.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: certifications/manifest.json's CERTIFIED entries are the closest analog to this section's authoritative certified-outcome record found in the repository.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-16-TECHNICAL-CERTIFICATE-REQUIREMENTS-D03

- Specification / section: MCC-CP-001 / 16. Technical Certificate Requirements / 16.2 Certificate Contents
- Status: PARTIAL
- Requirement: Every Technical Certificate SHALL include: - certificate identifier; - Certification Subject identifier; - specification version; - certification result; - certified capability profiles; - Certification Manifest reference; - Evidence Bundle reference; - issuance timestamp.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: certifications/manifest.json's CERTIFIED entries are the closest analog to this section's authoritative certified-outcome record found in the repository.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-16-TECHNICAL-CERTIFICATE-REQUIREMENTS-D04

- Specification / section: MCC-CP-001 / 16. Technical Certificate Requirements / 16.3 Certificate Issuance
- Status: PARTIAL
- Requirement: Technical Certificates SHALL be issued only after successful completion of certification.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: certifications/manifest.json's CERTIFIED entries are the closest analog to this section's authoritative certified-outcome record found in the repository.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-16-TECHNICAL-CERTIFICATE-REQUIREMENTS-D05

- Specification / section: MCC-CP-001 / 16. Technical Certificate Requirements / 16.3 Certificate Issuance
- Status: PARTIAL
- Requirement: Certificates SHALL NOT be issued for unsuccessful certification.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: certifications/manifest.json's CERTIFIED entries are the closest analog to this section's authoritative certified-outcome record found in the repository.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-16-TECHNICAL-CERTIFICATE-REQUIREMENTS-D06

- Specification / section: MCC-CP-001 / 16. Technical Certificate Requirements / 16.4 Certificate Integrity
- Status: PARTIAL
- Requirement: Technical Certificates SHALL accurately represent certification results.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: certifications/manifest.json's CERTIFIED entries are the closest analog to this section's authoritative certified-outcome record found in the repository.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-16-TECHNICAL-CERTIFICATE-REQUIREMENTS-D07

- Specification / section: MCC-CP-001 / 16. Technical Certificate Requirements / 16.4 Certificate Integrity
- Status: PARTIAL
- Requirement: Certificates SHALL NOT contain unverifiable claims.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: certifications/manifest.json's CERTIFIED entries are the closest analog to this section's authoritative certified-outcome record found in the repository.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-16-TECHNICAL-CERTIFICATE-REQUIREMENTS-D08

- Specification / section: MCC-CP-001 / 16. Technical Certificate Requirements / 16.4 Certificate Integrity
- Status: PARTIAL
- Requirement: Certificate integrity SHALL be preserved after issuance.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: certifications/manifest.json's CERTIFIED entries are the closest analog to this section's authoritative certified-outcome record found in the repository.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-16-TECHNICAL-CERTIFICATE-REQUIREMENTS-D09

- Specification / section: MCC-CP-001 / 16. Technical Certificate Requirements / 16.5 Certificate Traceability
- Status: PARTIAL
- Requirement: Every Technical Certificate SHALL be traceable to: - the Certification Subject; - the applicable specification version; - the Certification Manifest; - the Evidence Bundle.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: certifications/manifest.json's CERTIFIED entries are the closest analog to this section's authoritative certified-outcome record found in the repository.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-17-VERSIONING-D01

- Specification / section: MCC-CP-001 / 17. Versioning / 17.1 Purpose
- Status: PARTIAL
- Requirement: Versioning SHALL support reproducible certification.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: contract_version / compliance_suite_version / MANIFEST_SCHEMA_VERSION are independently tracked, immutable-once-published identifiers, the same versioning model this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-17-VERSIONING-D02

- Specification / section: MCC-CP-001 / 17. Versioning / 17.1 Purpose
- Status: PARTIAL
- Requirement: Versioning SHALL support long-term compatibility.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: contract_version / compliance_suite_version / MANIFEST_SCHEMA_VERSION are independently tracked, immutable-once-published identifiers, the same versioning model this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-17-VERSIONING-D03

- Specification / section: MCC-CP-001 / 17. Versioning / 17.2 Specification Versions
- Status: PARTIAL
- Requirement: Each certification SHALL reference an explicit specification version.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: contract_version / compliance_suite_version / MANIFEST_SCHEMA_VERSION are independently tracked, immutable-once-published identifiers, the same versioning model this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-17-VERSIONING-D04

- Specification / section: MCC-CP-001 / 17. Versioning / 17.2 Specification Versions
- Status: PARTIAL
- Requirement: Specification versions SHALL uniquely identify the normative document used during certification.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: contract_version / compliance_suite_version / MANIFEST_SCHEMA_VERSION are independently tracked, immutable-once-published identifiers, the same versioning model this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-17-VERSIONING-D05

- Specification / section: MCC-CP-001 / 17. Versioning / 17.2 Specification Versions
- Status: PARTIAL
- Requirement: Version identifiers SHALL remain immutable.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: contract_version / compliance_suite_version / MANIFEST_SCHEMA_VERSION are independently tracked, immutable-once-published identifiers, the same versioning model this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-17-VERSIONING-D06

- Specification / section: MCC-CP-001 / 17. Versioning / 17.3 Version Compatibility
- Status: PARTIAL
- Requirement: Certification SHALL be evaluated only against the referenced specification version.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: contract_version / compliance_suite_version / MANIFEST_SCHEMA_VERSION are independently tracked, immutable-once-published identifiers, the same versioning model this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-17-VERSIONING-D07

- Specification / section: MCC-CP-001 / 17. Versioning / 17.3 Version Compatibility
- Status: PARTIAL
- Requirement: Different specification versions SHALL NOT be considered equivalent unless explicitly declared.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: contract_version / compliance_suite_version / MANIFEST_SCHEMA_VERSION are independently tracked, immutable-once-published identifiers, the same versioning model this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-17-VERSIONING-D08

- Specification / section: MCC-CP-001 / 17. Versioning / 17.3 Version Compatibility
- Status: PARTIAL
- Requirement: Compatibility rules SHALL be documented.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: contract_version / compliance_suite_version / MANIFEST_SCHEMA_VERSION are independently tracked, immutable-once-published identifiers, the same versioning model this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-17-VERSIONING-D09

- Specification / section: MCC-CP-001 / 17. Versioning / 17.4 Certification Revalidation
- Status: PARTIAL
- Requirement: Each revalidation SHALL produce a new certification result.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: contract_version / compliance_suite_version / MANIFEST_SCHEMA_VERSION are independently tracked, immutable-once-published identifiers, the same versioning model this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-17-VERSIONING-D10

- Specification / section: MCC-CP-001 / 17. Versioning / 17.4 Certification Revalidation
- Status: PARTIAL
- Requirement: Previous certification results SHALL remain preserved.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: contract_version / compliance_suite_version / MANIFEST_SCHEMA_VERSION are independently tracked, immutable-once-published identifiers, the same versioning model this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-18-SECURITY-CONSIDERATIONS-D01

- Specification / section: MCC-CP-001 / 18. Security Considerations / 18.1 Purpose
- Status: PARTIAL
- Requirement: Security requirements SHALL protect certification integrity.
- Existing implementation: src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: The compliance suite is evidence-based, reproducible, and fail-closed (every mandatory vector must pass), the same security posture this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-18-SECURITY-CONSIDERATIONS-D02

- Specification / section: MCC-CP-001 / 18. Security Considerations / 18.1 Purpose
- Status: PARTIAL
- Requirement: Security requirements SHALL remain implementation-independent.
- Existing implementation: src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: The compliance suite is evidence-based, reproducible, and fail-closed (every mandatory vector must pass), the same security posture this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-18-SECURITY-CONSIDERATIONS-D03

- Specification / section: MCC-CP-001 / 18. Security Considerations / 18.2 Security Objectives
- Status: PARTIAL
- Requirement: Certification SHALL resist unauthorized modification.
- Existing implementation: src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: The compliance suite is evidence-based, reproducible, and fail-closed (every mandatory vector must pass), the same security posture this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-18-SECURITY-CONSIDERATIONS-D04

- Specification / section: MCC-CP-001 / 18. Security Considerations / 18.2 Security Objectives
- Status: PARTIAL
- Requirement: Certification SHALL support independent verification.
- Existing implementation: src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: The compliance suite is evidence-based, reproducible, and fail-closed (every mandatory vector must pass), the same security posture this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-18-SECURITY-CONSIDERATIONS-D05

- Specification / section: MCC-CP-001 / 18. Security Considerations / 18.3 Threat Model
- Status: PARTIAL
- Requirement: Certification SHALL assume untrusted implementations.
- Existing implementation: src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: The compliance suite is evidence-based, reproducible, and fail-closed (every mandatory vector must pass), the same security posture this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-18-SECURITY-CONSIDERATIONS-D06

- Specification / section: MCC-CP-001 / 18. Security Considerations / 18.3 Threat Model
- Status: PARTIAL
- Requirement: Certification SHALL assume potentially malicious inputs.
- Existing implementation: src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: The compliance suite is evidence-based, reproducible, and fail-closed (every mandatory vector must pass), the same security posture this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-18-SECURITY-CONSIDERATIONS-D07

- Specification / section: MCC-CP-001 / 18. Security Considerations / 18.3 Threat Model
- Status: PARTIAL
- Requirement: Certification SHALL rely only on evaluated evidence.
- Existing implementation: src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: The compliance suite is evidence-based, reproducible, and fail-closed (every mandatory vector must pass), the same security posture this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-18-SECURITY-CONSIDERATIONS-D08

- Specification / section: MCC-CP-001 / 18. Security Considerations / 18.3 Threat Model
- Status: PARTIAL
- Requirement: Certification SHALL remain independent of implementation identity.
- Existing implementation: src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: The compliance suite is evidence-based, reproducible, and fail-closed (every mandatory vector must pass), the same security posture this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-19-REGISTRY-CONSIDERATIONS-D01

- Specification / section: MCC-CP-001 / 19. Registry Considerations / 19.1 Purpose
- Status: PARTIAL
- Requirement: Registries SHALL support reproducibility, traceability, and long-term interoperability.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: certifications/manifest.json is itself a real, version-controlled, CI-verified registry of certification records, the same registry concept this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-19-REGISTRY-CONSIDERATIONS-D02

- Specification / section: MCC-CP-001 / 19. Registry Considerations / 19.2 Registry Scope
- Status: PARTIAL
- Requirement: Registry contents SHALL remain implementation-independent.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: certifications/manifest.json is itself a real, version-controlled, CI-verified registry of certification records, the same registry concept this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-19-REGISTRY-CONSIDERATIONS-D03

- Specification / section: MCC-CP-001 / 19. Registry Considerations / 19.3 Registry Requirements
- Status: PARTIAL
- Requirement: Registry entries SHALL be uniquely identifiable.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: certifications/manifest.json is itself a real, version-controlled, CI-verified registry of certification records, the same registry concept this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-19-REGISTRY-CONSIDERATIONS-D04

- Specification / section: MCC-CP-001 / 19. Registry Considerations / 19.3 Registry Requirements
- Status: PARTIAL
- Requirement: Registry entries SHALL be immutable after publication.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: certifications/manifest.json is itself a real, version-controlled, CI-verified registry of certification records, the same registry concept this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-19-REGISTRY-CONSIDERATIONS-D05

- Specification / section: MCC-CP-001 / 19. Registry Considerations / 19.3 Registry Requirements
- Status: PARTIAL
- Requirement: Registry entries SHALL remain traceable.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: certifications/manifest.json is itself a real, version-controlled, CI-verified registry of certification records, the same registry concept this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-19-REGISTRY-CONSIDERATIONS-D06

- Specification / section: MCC-CP-001 / 19. Registry Considerations / 19.3 Registry Requirements
- Status: PARTIAL
- Requirement: Registry entries SHALL reference applicable specification versions.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: certifications/manifest.json is itself a real, version-controlled, CI-verified registry of certification records, the same registry concept this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-2-GOALS-D01

- Specification / section: MCC-CP-001 / 2. Goals / G1. Framework Neutrality
- Status: GAP
- Requirement: Certification MUST remain independent of any particular framework.
- Existing implementation: None
- Missing implementation behavior: Full requirement not implemented.
- Missing test coverage: No test exists for this requirement.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: No implementation behavior, automated test, or evidence mechanism semantically equivalent to this requirement (category: '2. Goals') was found anywhere under src/, tests/, certifications/, evidence/, schemas/, docs/, or CI workflows, after the broader semantic-mapping investigation described in this module's docstring — not merely a lexical search for this specification's exact terminology.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-2-GOALS-D02

- Specification / section: MCC-CP-001 / 2. Goals / G1. Framework Neutrality
- Status: GAP
- Requirement: No framework SHALL become normative through implementation popularity.
- Existing implementation: None
- Missing implementation behavior: Full requirement not implemented.
- Missing test coverage: No test exists for this requirement.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: No implementation behavior, automated test, or evidence mechanism semantically equivalent to this requirement (category: '2. Goals') was found anywhere under src/, tests/, certifications/, evidence/, schemas/, docs/, or CI workflows, after the broader semantic-mapping investigation described in this module's docstring — not merely a lexical search for this specification's exact terminology.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-2-GOALS-D03

- Specification / section: MCC-CP-001 / 2. Goals / G2. Reproducibility
- Status: GAP
- Requirement: Certification results MUST be reproducible using the published certification artifacts.
- Existing implementation: None
- Missing implementation behavior: Full requirement not implemented.
- Missing test coverage: No test exists for this requirement.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: No implementation behavior, automated test, or evidence mechanism semantically equivalent to this requirement (category: '2. Goals') was found anywhere under src/, tests/, certifications/, evidence/, schemas/, docs/, or CI workflows, after the broader semantic-mapping investigation described in this module's docstring — not merely a lexical search for this specification's exact terminology.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-2-GOALS-D04

- Specification / section: MCC-CP-001 / 2. Goals / G3. Independent Verification
- Status: GAP
- Requirement: A third party MUST be able to verify certification without trusting the original certification environment.
- Existing implementation: None
- Missing implementation behavior: Full requirement not implemented.
- Missing test coverage: No test exists for this requirement.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: No implementation behavior, automated test, or evidence mechanism semantically equivalent to this requirement (category: '2. Goals') was found anywhere under src/, tests/, certifications/, evidence/, schemas/, docs/, or CI workflows, after the broader semantic-mapping investigation described in this module's docstring — not merely a lexical search for this specification's exact terminology.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-2-GOALS-D05

- Specification / section: MCC-CP-001 / 2. Goals / G4. Conformance
- Status: GAP
- Requirement: Certification SHALL measure conformance to MCC specifications.
- Existing implementation: None
- Missing implementation behavior: Full requirement not implemented.
- Missing test coverage: No test exists for this requirement.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: No implementation behavior, automated test, or evidence mechanism semantically equivalent to this requirement (category: '2. Goals') was found anywhere under src/, tests/, certifications/, evidence/, schemas/, docs/, or CI workflows, after the broader semantic-mapping investigation described in this module's docstring — not merely a lexical search for this specification's exact terminology.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-2-GOALS-D06

- Specification / section: MCC-CP-001 / 2. Goals / G4. Conformance
- Status: GAP
- Requirement: Certification SHALL NOT measure implementation similarity.
- Existing implementation: None
- Missing implementation behavior: Full requirement not implemented.
- Missing test coverage: No test exists for this requirement.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: No implementation behavior, automated test, or evidence mechanism semantically equivalent to this requirement (category: '2. Goals') was found anywhere under src/, tests/, certifications/, evidence/, schemas/, docs/, or CI workflows, after the broader semantic-mapping investigation described in this module's docstring — not merely a lexical search for this specification's exact terminology.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-20-CONFORMANCE-STATEMENT-D01

- Specification / section: MCC-CP-001 / 20. Conformance Statement / 20.1 Purpose
- Status: GAP
- Requirement: Conformance SHALL be evaluated solely against normative requirements defined by this specification.
- Existing implementation: None
- Missing implementation behavior: Full requirement not implemented.
- Missing test coverage: No test exists for this requirement.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: No mechanism for an implementation to claim conformance specifically to MCC-CP-001 (as opposed to the Integration Contract) was found.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-20-CONFORMANCE-STATEMENT-D02

- Specification / section: MCC-CP-001 / 20. Conformance Statement / 20.2 Conformance Claims
- Status: GAP
- Requirement: Conformance claims SHALL reference the applicable specification version.
- Existing implementation: None
- Missing implementation behavior: Full requirement not implemented.
- Missing test coverage: No test exists for this requirement.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: No mechanism for an implementation to claim conformance specifically to MCC-CP-001 (as opposed to the Integration Contract) was found.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-20-CONFORMANCE-STATEMENT-D03

- Specification / section: MCC-CP-001 / 20. Conformance Statement / 20.2 Conformance Claims
- Status: GAP
- Requirement: Conformance claims SHALL reference the associated Certification Manifest.
- Existing implementation: None
- Missing implementation behavior: Full requirement not implemented.
- Missing test coverage: No test exists for this requirement.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: No mechanism for an implementation to claim conformance specifically to MCC-CP-001 (as opposed to the Integration Contract) was found.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-20-CONFORMANCE-STATEMENT-D04

- Specification / section: MCC-CP-001 / 20. Conformance Statement / 20.2 Conformance Claims
- Status: GAP
- Requirement: Conformance claims SHALL reference the associated Technical Certificate.
- Existing implementation: None
- Missing implementation behavior: Full requirement not implemented.
- Missing test coverage: No test exists for this requirement.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: No mechanism for an implementation to claim conformance specifically to MCC-CP-001 (as opposed to the Integration Contract) was found.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-21-REFERENCES-D01

- Specification / section: MCC-CP-001 / 21. References / 21.2 Normative References
- Status: NOT_APPLICABLE
- Requirement: The following specifications SHALL be considered normative when referenced by this document: - MCC-CP-001 - MCC-EB-001 - MCC-CM-001 - MCC-TC-001
- Existing implementation: None
- Missing implementation behavior: N/A (not an implementable requirement).
- Missing test coverage: No test exists for this requirement.
- Missing evidence: N/A
- Rationale: Interpretive, bibliographic, non-normative-by-design (explicitly marked informative/example), or document-self-referential statement. It does not describe a discrete, independently implementable system behavior.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: N/A

## MCC-CP-001-21-REFERENCES-D02

- Specification / section: MCC-CP-001 / 21. References / 21.3 Informative References
- Status: NOT_APPLICABLE
- Requirement: Informative material SHALL NOT introduce normative requirements.
- Existing implementation: None
- Missing implementation behavior: N/A (not an implementable requirement).
- Missing test coverage: No test exists for this requirement.
- Missing evidence: N/A
- Rationale: Interpretive, bibliographic, non-normative-by-design (explicitly marked informative/example), or document-self-referential statement. It does not describe a discrete, independently implementable system behavior.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: N/A

## MCC-CP-001-3-NON-GOALS-D01

- Specification / section: MCC-CP-001 / 3. Non-Goals
- Status: GAP
- Requirement: The Certification Program SHALL NOT: - define framework architectures; - define adapter SDK implementations; - authorize runtime actions; - replace governance decisions; - replace execution policy; - define transport protocols; - define business-specific behavior.
- Existing implementation: None
- Missing implementation behavior: Full requirement not implemented.
- Missing test coverage: No test exists for this requirement.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: No implementation behavior, automated test, or evidence mechanism semantically equivalent to this requirement (category: '3. Non-Goals') was found anywhere under src/, tests/, certifications/, evidence/, schemas/, docs/, or CI workflows, after the broader semantic-mapping investigation described in this module's docstring — not merely a lexical search for this specification's exact terminology.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-5-NORMATIVE-LANGUAGE-D01

- Specification / section: MCC-CP-001 / 5. Normative Language
- Status: NOT_APPLICABLE
- Requirement: The key words MUST, MUST NOT, REQUIRED, SHALL, SHALL NOT, SHOULD, SHOULD NOT, RECOMMENDED, MAY and OPTIONAL in this specification are to be interpreted as described in RFC 2119 and RFC 8174.
- Existing implementation: None
- Missing implementation behavior: N/A (not an implementable requirement).
- Missing test coverage: No test exists for this requirement.
- Missing evidence: N/A
- Rationale: Interpretive, bibliographic, non-normative-by-design (explicitly marked informative/example), or document-self-referential statement. It does not describe a discrete, independently implementable system behavior.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: N/A

## MCC-CP-001-6-ARCHITECTURAL-PRINCIPLES-D01

- Specification / section: MCC-CP-001 / 6. Architectural Principles
- Status: GAP
- Requirement: Certification SHALL remain independent of implementation technologies.
- Existing implementation: None
- Missing implementation behavior: Full requirement not implemented.
- Missing test coverage: No test exists for this requirement.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: No implementation behavior, automated test, or evidence mechanism semantically equivalent to this requirement (category: '6. Architectural Principles') was found anywhere under src/, tests/, certifications/, evidence/, schemas/, docs/, or CI workflows, after the broader semantic-mapping investigation described in this module's docstring — not merely a lexical search for this specification's exact terminology.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-6-ARCHITECTURAL-PRINCIPLES-D02

- Specification / section: MCC-CP-001 / 6. Architectural Principles
- Status: GAP
- Requirement: Certification claims MUST be supported by reproducible evidence.
- Existing implementation: None
- Missing implementation behavior: Full requirement not implemented.
- Missing test coverage: No test exists for this requirement.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: No implementation behavior, automated test, or evidence mechanism semantically equivalent to this requirement (category: '6. Architectural Principles') was found anywhere under src/, tests/, certifications/, evidence/, schemas/, docs/, or CI workflows, after the broader semantic-mapping investigation described in this module's docstring — not merely a lexical search for this specification's exact terminology.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-6-ARCHITECTURAL-PRINCIPLES-D03

- Specification / section: MCC-CP-001 / 6. Architectural Principles
- Status: GAP
- Requirement: Certification SHALL be independently verifiable.
- Existing implementation: None
- Missing implementation behavior: Full requirement not implemented.
- Missing test coverage: No test exists for this requirement.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: No implementation behavior, automated test, or evidence mechanism semantically equivalent to this requirement (category: '6. Architectural Principles') was found anywhere under src/, tests/, certifications/, evidence/, schemas/, docs/, or CI workflows, after the broader semantic-mapping investigation described in this module's docstring — not merely a lexical search for this specification's exact terminology.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-7-CERTIFICATION-MODEL-D01

- Specification / section: MCC-CP-001 / 7. Certification Model
- Status: PARTIAL
- Requirement: All certifications SHALL be performed according to this model.
- Existing implementation: src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_compliance implements a real, tested certification model (evaluate an adapter's behavior against versioned requirements, produce a deterministic result) — the same model this section describes, scoped to adapters vs. the Integration Contract rather than implementations vs. these four specifications.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-7-CERTIFICATION-MODEL-D02

- Specification / section: MCC-CP-001 / 7. Certification Model
- Status: PARTIAL
- Requirement: Certification SHALL always evaluate normative requirements.
- Existing implementation: src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_compliance implements a real, tested certification model (evaluate an adapter's behavior against versioned requirements, produce a deterministic result) — the same model this section describes, scoped to adapters vs. the Integration Contract rather than implementations vs. these four specifications.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-7-CERTIFICATION-MODEL-D03

- Specification / section: MCC-CP-001 / 7. Certification Model
- Status: PARTIAL
- Requirement: Certification SHALL NOT evaluate implementation popularity, project ownership, programming language, framework ecosystem, deployment topology, commercial status or organizational affiliation.
- Existing implementation: src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_compliance implements a real, tested certification model (evaluate an adapter's behavior against versioned requirements, produce a deterministic result) — the same model this section describes, scoped to adapters vs. the Integration Contract rather than implementations vs. these four specifications.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-7-CERTIFICATION-MODEL-D04

- Specification / section: MCC-CP-001 / 7. Certification Model
- Status: PARTIAL
- Requirement: Every successful certification SHALL produce reproducible certification artifacts.
- Existing implementation: src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_compliance implements a real, tested certification model (evaluate an adapter's behavior against versioned requirements, produce a deterministic result) — the same model this section describes, scoped to adapters vs. the Integration Contract rather than implementations vs. these four specifications.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-7-CERTIFICATION-MODEL-D05

- Specification / section: MCC-CP-001 / 7. Certification Model
- Status: PARTIAL
- Requirement: Those artifacts SHALL be sufficient for independent verification.
- Existing implementation: src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_compliance implements a real, tested certification model (evaluate an adapter's behavior against versioned requirements, produce a deterministic result) — the same model this section describes, scoped to adapters vs. the Integration Contract rather than implementations vs. these four specifications.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-7-CERTIFICATION-MODEL-D06

- Specification / section: MCC-CP-001 / 7. Certification Model / 7.1 Certification Authority
- Status: PARTIAL
- Requirement: Implementations SHALL NOT redefine certification requirements.
- Existing implementation: src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_compliance implements a real, tested certification model (evaluate an adapter's behavior against versioned requirements, produce a deterministic result) — the same model this section describes, scoped to adapters vs. the Integration Contract rather than implementations vs. these four specifications.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-7-CERTIFICATION-MODEL-D07

- Specification / section: MCC-CP-001 / 7. Certification Model / 7.2 Certification Subject
- Status: PARTIAL
- Requirement: Certification SHALL evaluate behavior rather than implementation origin.
- Existing implementation: src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_compliance implements a real, tested certification model (evaluate an adapter's behavior against versioned requirements, produce a deterministic result) — the same model this section describes, scoped to adapters vs. the Integration Contract rather than implementations vs. these four specifications.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-7-CERTIFICATION-MODEL-D08

- Specification / section: MCC-CP-001 / 7. Certification Model / 7.3 Certification Inputs
- Status: PARTIAL
- Requirement: Certification SHALL consume one or more of the following inputs: - implementation under evaluation; - specification version; - conformance profile; - capability profile; - certification configuration; - normative test vectors.
- Existing implementation: src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_compliance implements a real, tested certification model (evaluate an adapter's behavior against versioned requirements, produce a deterministic result) — the same model this section describes, scoped to adapters vs. the Integration Contract rather than implementations vs. these four specifications.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-7-CERTIFICATION-MODEL-D09

- Specification / section: MCC-CP-001 / 7. Certification Model / 7.3 Certification Inputs
- Status: PARTIAL
- Requirement: Certification inputs SHALL be versioned.
- Existing implementation: src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_compliance implements a real, tested certification model (evaluate an adapter's behavior against versioned requirements, produce a deterministic result) — the same model this section describes, scoped to adapters vs. the Integration Contract rather than implementations vs. these four specifications.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-7-CERTIFICATION-MODEL-D10

- Specification / section: MCC-CP-001 / 7. Certification Model / 7.4 Certification Outputs
- Status: PARTIAL
- Requirement: Every successful certification SHALL produce: - Evidence Bundle; - Certification Manifest; - Technical Certificate; - Conformance Result; - Certification Report.
- Existing implementation: src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_compliance implements a real, tested certification model (evaluate an adapter's behavior against versioned requirements, produce a deterministic result) — the same model this section describes, scoped to adapters vs. the Integration Contract rather than implementations vs. these four specifications.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-7-CERTIFICATION-MODEL-D11

- Specification / section: MCC-CP-001 / 7. Certification Model / 7.4 Certification Outputs
- Status: PARTIAL
- Requirement: These outputs SHALL be reproducible.
- Existing implementation: src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_compliance implements a real, tested certification model (evaluate an adapter's behavior against versioned requirements, produce a deterministic result) — the same model this section describes, scoped to adapters vs. the Integration Contract rather than implementations vs. these four specifications.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-7-CERTIFICATION-MODEL-D12

- Specification / section: MCC-CP-001 / 7. Certification Model / 7.5 Certification Invariants
- Status: PARTIAL
- Requirement: The following invariants SHALL always hold.
- Existing implementation: src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_compliance implements a real, tested certification model (evaluate an adapter's behavior against versioned requirements, produce a deterministic result) — the same model this section describes, scoped to adapters vs. the Integration Contract rather than implementations vs. these four specifications.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-8-CERTIFICATION-LIFECYCLE-D01

- Specification / section: MCC-CP-001 / 8. Certification Lifecycle
- Status: PARTIAL
- Requirement: Every certification SHALL progress through the following lifecycle.
- Existing implementation: src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: run_compliance's registration -> scenario execution -> assessment -> report/manifest generation flow is procedurally analogous to this section's lifecycle steps, for a differently-scoped certification target.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-8-CERTIFICATION-LIFECYCLE-D02

- Specification / section: MCC-CP-001 / 8. Certification Lifecycle / 8.1 Registration
- Status: PARTIAL
- Requirement: The Certification Subject SHALL be registered for evaluation.
- Existing implementation: src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: run_compliance's registration -> scenario execution -> assessment -> report/manifest generation flow is procedurally analogous to this section's lifecycle steps, for a differently-scoped certification target.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-8-CERTIFICATION-LIFECYCLE-D03

- Specification / section: MCC-CP-001 / 8. Certification Lifecycle / 8.1 Registration
- Status: PARTIAL
- Requirement: Registration SHALL record: - implementation identifier; - specification version; - certification profile; - capability profile; - certification configuration.
- Existing implementation: src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: run_compliance's registration -> scenario execution -> assessment -> report/manifest generation flow is procedurally analogous to this section's lifecycle steps, for a differently-scoped certification target.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-8-CERTIFICATION-LIFECYCLE-D04

- Specification / section: MCC-CP-001 / 8. Certification Lifecycle / 8.2 Preparation
- Status: PARTIAL
- Requirement: The certification environment SHALL be prepared.
- Existing implementation: src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: run_compliance's registration -> scenario execution -> assessment -> report/manifest generation flow is procedurally analogous to this section's lifecycle steps, for a differently-scoped certification target.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-8-CERTIFICATION-LIFECYCLE-D05

- Specification / section: MCC-CP-001 / 8. Certification Lifecycle / 8.2 Preparation
- Status: PARTIAL
- Requirement: Preparation SHALL verify: - specification version compatibility; - required certification artifacts; - required tooling; - normative test vectors; - environment integrity.
- Existing implementation: src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: run_compliance's registration -> scenario execution -> assessment -> report/manifest generation flow is procedurally analogous to this section's lifecycle steps, for a differently-scoped certification target.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-8-CERTIFICATION-LIFECYCLE-D06

- Specification / section: MCC-CP-001 / 8. Certification Lifecycle / 8.2 Preparation
- Status: PARTIAL
- Requirement: Certification SHALL NOT continue if preparation fails.
- Existing implementation: src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: run_compliance's registration -> scenario execution -> assessment -> report/manifest generation flow is procedurally analogous to this section's lifecycle steps, for a differently-scoped certification target.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-8-CERTIFICATION-LIFECYCLE-D07

- Specification / section: MCC-CP-001 / 8. Certification Lifecycle / 8.3 Evaluation
- Status: PARTIAL
- Requirement: The Certification Subject SHALL be evaluated against the applicable MCC specifications.
- Existing implementation: src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: run_compliance's registration -> scenario execution -> assessment -> report/manifest generation flow is procedurally analogous to this section's lifecycle steps, for a differently-scoped certification target.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-8-CERTIFICATION-LIFECYCLE-D08

- Specification / section: MCC-CP-001 / 8. Certification Lifecycle / 8.3 Evaluation
- Status: PARTIAL
- Requirement: Evaluation SHALL execute all mandatory certification requirements.
- Existing implementation: src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: run_compliance's registration -> scenario execution -> assessment -> report/manifest generation flow is procedurally analogous to this section's lifecycle steps, for a differently-scoped certification target.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-8-CERTIFICATION-LIFECYCLE-D09

- Specification / section: MCC-CP-001 / 8. Certification Lifecycle / 8.3 Evaluation
- Status: PARTIAL
- Requirement: Optional requirements SHALL NOT affect mandatory conformance.
- Existing implementation: src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: run_compliance's registration -> scenario execution -> assessment -> report/manifest generation flow is procedurally analogous to this section's lifecycle steps, for a differently-scoped certification target.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-8-CERTIFICATION-LIFECYCLE-D10

- Specification / section: MCC-CP-001 / 8. Certification Lifecycle / 8.4 Evidence Collection
- Status: PARTIAL
- Requirement: Certification SHALL collect all required evidence.
- Existing implementation: src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: run_compliance's registration -> scenario execution -> assessment -> report/manifest generation flow is procedurally analogous to this section's lifecycle steps, for a differently-scoped certification target.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-8-CERTIFICATION-LIFECYCLE-D11

- Specification / section: MCC-CP-001 / 8. Certification Lifecycle / 8.4 Evidence Collection
- Status: PARTIAL
- Requirement: Evidence SHALL be reproducible.
- Existing implementation: src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: run_compliance's registration -> scenario execution -> assessment -> report/manifest generation flow is procedurally analogous to this section's lifecycle steps, for a differently-scoped certification target.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-8-CERTIFICATION-LIFECYCLE-D12

- Specification / section: MCC-CP-001 / 8. Certification Lifecycle / 8.4 Evidence Collection
- Status: PARTIAL
- Requirement: Evidence SHALL be associated with the evaluated specification version.
- Existing implementation: src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: run_compliance's registration -> scenario execution -> assessment -> report/manifest generation flow is procedurally analogous to this section's lifecycle steps, for a differently-scoped certification target.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-8-CERTIFICATION-LIFECYCLE-D13

- Specification / section: MCC-CP-001 / 8. Certification Lifecycle / 8.5 Conformance Assessment
- Status: PARTIAL
- Requirement: Collected evidence SHALL be evaluated against normative requirements.
- Existing implementation: src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: run_compliance's registration -> scenario execution -> assessment -> report/manifest generation flow is procedurally analogous to this section's lifecycle steps, for a differently-scoped certification target.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-8-CERTIFICATION-LIFECYCLE-D14

- Specification / section: MCC-CP-001 / 8. Certification Lifecycle / 8.5 Conformance Assessment
- Status: PARTIAL
- Requirement: Each requirement SHALL produce one of the following outcomes: - PASS - FAIL - NOT APPLICABLE
- Existing implementation: src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: run_compliance's registration -> scenario execution -> assessment -> report/manifest generation flow is procedurally analogous to this section's lifecycle steps, for a differently-scoped certification target.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-8-CERTIFICATION-LIFECYCLE-D15

- Specification / section: MCC-CP-001 / 8. Certification Lifecycle / 8.5 Conformance Assessment
- Status: PARTIAL
- Requirement: Conformance SHALL be determined only from normative requirements.
- Existing implementation: src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: run_compliance's registration -> scenario execution -> assessment -> report/manifest generation flow is procedurally analogous to this section's lifecycle steps, for a differently-scoped certification target.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-8-CERTIFICATION-LIFECYCLE-D16

- Specification / section: MCC-CP-001 / 8. Certification Lifecycle / 8.6 Certification Decision
- Status: PARTIAL
- Requirement: Certification SHALL issue exactly one certification decision.
- Existing implementation: src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: run_compliance's registration -> scenario execution -> assessment -> report/manifest generation flow is procedurally analogous to this section's lifecycle steps, for a differently-scoped certification target.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-8-CERTIFICATION-LIFECYCLE-D17

- Specification / section: MCC-CP-001 / 8. Certification Lifecycle / 8.6 Certification Decision
- Status: PARTIAL
- Requirement: Certification decisions SHALL be reproducible.
- Existing implementation: src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: run_compliance's registration -> scenario execution -> assessment -> report/manifest generation flow is procedurally analogous to this section's lifecycle steps, for a differently-scoped certification target.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-8-CERTIFICATION-LIFECYCLE-D18

- Specification / section: MCC-CP-001 / 8. Certification Lifecycle / 8.7 Technical Certificate Issuance
- Status: PARTIAL
- Requirement: A Technical Certificate SHALL only be issued after successful certification.
- Existing implementation: src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: run_compliance's registration -> scenario execution -> assessment -> report/manifest generation flow is procedurally analogous to this section's lifecycle steps, for a differently-scoped certification target.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-8-CERTIFICATION-LIFECYCLE-D19

- Specification / section: MCC-CP-001 / 8. Certification Lifecycle / 8.7 Technical Certificate Issuance
- Status: PARTIAL
- Requirement: Technical Certificates SHALL reference: - specification version; - Certification Manifest; - Evidence Bundle; - certification result.
- Existing implementation: src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: run_compliance's registration -> scenario execution -> assessment -> report/manifest generation flow is procedurally analogous to this section's lifecycle steps, for a differently-scoped certification target.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-8-CERTIFICATION-LIFECYCLE-D20

- Specification / section: MCC-CP-001 / 8. Certification Lifecycle / 8.8 Publication
- Status: PARTIAL
- Requirement: Publication SHALL NOT modify certification results.
- Existing implementation: src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: run_compliance's registration -> scenario execution -> assessment -> report/manifest generation flow is procedurally analogous to this section's lifecycle steps, for a differently-scoped certification target.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-8-CERTIFICATION-LIFECYCLE-D21

- Specification / section: MCC-CP-001 / 8. Certification Lifecycle / 8.8 Publication
- Status: PARTIAL
- Requirement: Published artifacts SHALL remain reproducible.
- Existing implementation: src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: run_compliance's registration -> scenario execution -> assessment -> report/manifest generation flow is procedurally analogous to this section's lifecycle steps, for a differently-scoped certification target.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-8-CERTIFICATION-LIFECYCLE-D22

- Specification / section: MCC-CP-001 / 8. Certification Lifecycle / 8.9 Revalidation
- Status: PARTIAL
- Requirement: Every revalidation SHALL reference the applicable specification version.
- Existing implementation: src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: run_compliance's registration -> scenario execution -> assessment -> report/manifest generation flow is procedurally analogous to this section's lifecycle steps, for a differently-scoped certification target.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-8-CERTIFICATION-LIFECYCLE-D23

- Specification / section: MCC-CP-001 / 8. Certification Lifecycle / 8.9 Revalidation
- Status: PARTIAL
- Requirement: Revalidation SHALL produce a new certification result.
- Existing implementation: src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: run_compliance's registration -> scenario execution -> assessment -> report/manifest generation flow is procedurally analogous to this section's lifecycle steps, for a differently-scoped certification target.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-9-CERTIFICATION-PIPELINE-D01

- Specification / section: MCC-CP-001 / 9. Certification Pipeline
- Status: PARTIAL
- Requirement: Every certification SHALL execute every mandatory stage in the order defined below.
- Existing implementation: src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: run_compliance executes an ordered, deterministic sequence of stages (structural checks, scenario execution, evidence generation, assessment, artifact generation) analogous to this section's Pipeline.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-9-CERTIFICATION-PIPELINE-D02

- Specification / section: MCC-CP-001 / 9. Certification Pipeline
- Status: PARTIAL
- Requirement: A failed mandatory stage SHALL terminate certification.
- Existing implementation: src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: run_compliance executes an ordered, deterministic sequence of stages (structural checks, scenario execution, evidence generation, assessment, artifact generation) analogous to this section's Pipeline.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-9-CERTIFICATION-PIPELINE-D03

- Specification / section: MCC-CP-001 / 9. Certification Pipeline / 9.2 Stage 2 — Environment Validation
- Status: PARTIAL
- Requirement: Validation SHALL include: - specification version; - required tooling; - capability profile; - normative test vectors; - environment integrity.
- Existing implementation: src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: run_compliance executes an ordered, deterministic sequence of stages (structural checks, scenario execution, evidence generation, assessment, artifact generation) analogous to this section's Pipeline.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-9-CERTIFICATION-PIPELINE-D04

- Specification / section: MCC-CP-001 / 9. Certification Pipeline / 9.8 Stage 8 — Publication
- Status: PARTIAL
- Requirement: Publication SHALL preserve reproducibility.
- Existing implementation: src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: run_compliance executes an ordered, deterministic sequence of stages (structural checks, scenario execution, evidence generation, assessment, artifact generation) analogous to this section's Pipeline.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-9-CERTIFICATION-PIPELINE-D05

- Specification / section: MCC-CP-001 / 9. Certification Pipeline / 9.9 Pipeline Invariants
- Status: PARTIAL
- Requirement: The Certification Pipeline SHALL satisfy the following invariants.
- Existing implementation: src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: run_compliance executes an ordered, deterministic sequence of stages (structural checks, scenario execution, evidence generation, assessment, artifact generation) analogous to this section's Pipeline.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-ABSTRACT-D01

- Specification / section: MCC-CP-001 / Abstract
- Status: NOT_APPLICABLE
- Requirement: Certification SHALL evaluate conformance to MCC specifications rather than implementation identity.
- Existing implementation: None
- Missing implementation behavior: N/A (not an implementable requirement).
- Missing test coverage: No test exists for this requirement.
- Missing evidence: N/A
- Rationale: Interpretive, bibliographic, non-normative-by-design (explicitly marked informative/example), or document-self-referential statement. It does not describe a discrete, independently implementable system behavior.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: N/A

## MCC-CP-001-APPENDIX-A-CERTIFICATION-STATE-MACHINE-D01

- Specification / section: MCC-CP-001 / Appendix A — Certification State Machine / A.2 States
- Status: GAP
- Requirement: The certification process SHALL consist of the following states: - Draft - Submitted - Under Evaluation - Evidence Collection - Validation - Decision - Certified - Rejected - Revoked - Archived
- Existing implementation: None
- Missing implementation behavior: Full requirement not implemented.
- Missing test coverage: No test exists for this requirement.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: No explicit certification-process state machine (Draft/Submitted/Under Evaluation/.../Archived) implementation was found; the compliance runner is a single synchronous pass, not a persisted multi-state record.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-APPENDIX-A-CERTIFICATION-STATE-MACHINE-D02

- Specification / section: MCC-CP-001 / Appendix A — Certification State Machine / A.3 State Transitions
- Status: GAP
- Requirement: State transitions SHALL occur only through defined certification procedures.
- Existing implementation: None
- Missing implementation behavior: Full requirement not implemented.
- Missing test coverage: No test exists for this requirement.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: No explicit certification-process state machine (Draft/Submitted/Under Evaluation/.../Archived) implementation was found; the compliance runner is a single synchronous pass, not a persisted multi-state record.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-APPENDIX-A-CERTIFICATION-STATE-MACHINE-D03

- Specification / section: MCC-CP-001 / Appendix A — Certification State Machine / A.3 State Transitions
- Status: GAP
- Requirement: Undefined transitions SHALL NOT occur.
- Existing implementation: None
- Missing implementation behavior: Full requirement not implemented.
- Missing test coverage: No test exists for this requirement.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: No explicit certification-process state machine (Draft/Submitted/Under Evaluation/.../Archived) implementation was found; the compliance runner is a single synchronous pass, not a persisted multi-state record.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-APPENDIX-A-CERTIFICATION-STATE-MACHINE-D04

- Specification / section: MCC-CP-001 / Appendix A — Certification State Machine / A.3 State Transitions
- Status: GAP
- Requirement: Revocation SHALL NOT modify historical certification evidence.
- Existing implementation: None
- Missing implementation behavior: Full requirement not implemented.
- Missing test coverage: No test exists for this requirement.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: No explicit certification-process state machine (Draft/Submitted/Under Evaluation/.../Archived) implementation was found; the compliance runner is a single synchronous pass, not a persisted multi-state record.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-APPENDIX-A-CERTIFICATION-STATE-MACHINE-D05

- Specification / section: MCC-CP-001 / Appendix A — Certification State Machine / A.3 State Transitions
- Status: GAP
- Requirement: Archival SHALL preserve certification history.
- Existing implementation: None
- Missing implementation behavior: Full requirement not implemented.
- Missing test coverage: No test exists for this requirement.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: No explicit certification-process state machine (Draft/Submitted/Under Evaluation/.../Archived) implementation was found; the compliance runner is a single synchronous pass, not a persisted multi-state record.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-APPENDIX-B-CERTIFICATION-DECISION-MATRIX-D01

- Specification / section: MCC-CP-001 / Appendix B — Certification Decision Matrix / B.1 Overview
- Status: PARTIAL
- Requirement: Certification decisions SHALL be derived exclusively from evaluated normative requirements.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: status=CERTIFIED / NOT_CERTIFIED (models.py CertificationStatus) is a real, binary, evidence-derived decision outcome, the same decision-matrix concept this appendix requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-APPENDIX-B-CERTIFICATION-DECISION-MATRIX-D02

- Specification / section: MCC-CP-001 / Appendix B — Certification Decision Matrix / B.2 Decision Outcomes
- Status: PARTIAL
- Requirement: No additional certification outcomes SHALL be defined unless introduced by a future specification revision.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: status=CERTIFIED / NOT_CERTIFIED (models.py CertificationStatus) is a real, binary, evidence-derived decision outcome, the same decision-matrix concept this appendix requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-APPENDIX-B-CERTIFICATION-DECISION-MATRIX-D03

- Specification / section: MCC-CP-001 / Appendix B — Certification Decision Matrix / B.2 Decision Outcomes
- Status: PARTIAL
- Requirement: The governance runtime outcomes ALLOW, DENY, ESCALATE, and CONSTRAIN belong exclusively to MCC-Core runtime governance and SHALL NOT be used as certification outcomes.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: status=CERTIFIED / NOT_CERTIFIED (models.py CertificationStatus) is a real, binary, evidence-derived decision outcome, the same decision-matrix concept this appendix requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-APPENDIX-B-CERTIFICATION-DECISION-MATRIX-D04

- Specification / section: MCC-CP-001 / Appendix B — Certification Decision Matrix / B.3 Decision Rules
- Status: PARTIAL
- Requirement: Certification SHALL be granted only when all REQUIRED normative requirements have been satisfied.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: status=CERTIFIED / NOT_CERTIFIED (models.py CertificationStatus) is a real, binary, evidence-derived decision outcome, the same decision-matrix concept this appendix requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-APPENDIX-B-CERTIFICATION-DECISION-MATRIX-D05

- Specification / section: MCC-CP-001 / Appendix B — Certification Decision Matrix / B.3 Decision Rules
- Status: PARTIAL
- Requirement: OPTIONAL requirements SHALL NOT determine certification status.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: status=CERTIFIED / NOT_CERTIFIED (models.py CertificationStatus) is a real, binary, evidence-derived decision outcome, the same decision-matrix concept this appendix requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-APPENDIX-B-CERTIFICATION-DECISION-MATRIX-D06

- Specification / section: MCC-CP-001 / Appendix B — Certification Decision Matrix / B.3 Decision Rules
- Status: PARTIAL
- Requirement: CONDITIONAL requirements SHALL be evaluated only when their applicability conditions are satisfied.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: status=CERTIFIED / NOT_CERTIFIED (models.py CertificationStatus) is a real, binary, evidence-derived decision outcome, the same decision-matrix concept this appendix requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-APPENDIX-C-REQUIREMENT-IDENTIFIER-REGIST-D01

- Specification / section: MCC-CP-001 / Appendix C — Requirement Identifier Registry / C.1 Purpose
- Status: NOT_APPLICABLE
- Requirement: Requirement identifiers SHALL remain globally unique within a published specification version.
- Existing implementation: None
- Missing implementation behavior: N/A (not an implementable requirement).
- Missing test coverage: No test exists for this requirement.
- Missing evidence: N/A
- Rationale: Interpretive, bibliographic, non-normative-by-design (explicitly marked informative/example), or document-self-referential statement. It does not describe a discrete, independently implementable system behavior.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: N/A

## MCC-CP-001-APPENDIX-C-REQUIREMENT-IDENTIFIER-REGIST-D02

- Specification / section: MCC-CP-001 / Appendix C — Requirement Identifier Registry / C.2 Identifier Structure
- Status: NOT_APPLICABLE
- Requirement: Identifier formats SHALL remain stable across specification revisions.
- Existing implementation: None
- Missing implementation behavior: N/A (not an implementable requirement).
- Missing test coverage: No test exists for this requirement.
- Missing evidence: N/A
- Rationale: Interpretive, bibliographic, non-normative-by-design (explicitly marked informative/example), or document-self-referential statement. It does not describe a discrete, independently implementable system behavior.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: N/A

## MCC-CP-001-APPENDIX-C-REQUIREMENT-IDENTIFIER-REGIST-D03

- Specification / section: MCC-CP-001 / Appendix C — Requirement Identifier Registry / C.3 Registry Requirements
- Status: NOT_APPLICABLE
- Requirement: The registry SHALL maintain: - identifier; - requirement title; - specification version; - status; - applicable section.
- Existing implementation: None
- Missing implementation behavior: N/A (not an implementable requirement).
- Missing test coverage: No test exists for this requirement.
- Missing evidence: N/A
- Rationale: Interpretive, bibliographic, non-normative-by-design (explicitly marked informative/example), or document-self-referential statement. It does not describe a discrete, independently implementable system behavior.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: N/A

## MCC-CP-001-APPENDIX-C-REQUIREMENT-IDENTIFIER-REGIST-D04

- Specification / section: MCC-CP-001 / Appendix C — Requirement Identifier Registry / C.3 Registry Requirements
- Status: NOT_APPLICABLE
- Requirement: Registry entries SHALL remain immutable after publication.
- Existing implementation: None
- Missing implementation behavior: N/A (not an implementable requirement).
- Missing test coverage: No test exists for this requirement.
- Missing evidence: N/A
- Rationale: Interpretive, bibliographic, non-normative-by-design (explicitly marked informative/example), or document-self-referential statement. It does not describe a discrete, independently implementable system behavior.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: N/A

## MCC-CP-001-APPENDIX-D-REVISION-HISTORY-D01

- Specification / section: MCC-CP-001 / Appendix D — Revision History / D.1 Purpose
- Status: NOT_APPLICABLE
- Requirement: Revision history SHALL provide a complete and traceable record of specification evolution.
- Existing implementation: None
- Missing implementation behavior: N/A (not an implementable requirement).
- Missing test coverage: No test exists for this requirement.
- Missing evidence: N/A
- Rationale: Interpretive, bibliographic, non-normative-by-design (explicitly marked informative/example), or document-self-referential statement. It does not describe a discrete, independently implementable system behavior.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: N/A

## MCC-CP-001-APPENDIX-D-REVISION-HISTORY-D02

- Specification / section: MCC-CP-001 / Appendix D — Revision History / D.3 Future Revisions
- Status: NOT_APPLICABLE
- Requirement: Future revisions SHALL preserve backward traceability.
- Existing implementation: None
- Missing implementation behavior: N/A (not an implementable requirement).
- Missing test coverage: No test exists for this requirement.
- Missing evidence: N/A
- Rationale: Interpretive, bibliographic, non-normative-by-design (explicitly marked informative/example), or document-self-referential statement. It does not describe a discrete, independently implementable system behavior.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: N/A

## MCC-CP-001-APPENDIX-D-REVISION-HISTORY-D03

- Specification / section: MCC-CP-001 / Appendix D — Revision History / D.3 Future Revisions
- Status: NOT_APPLICABLE
- Requirement: Deprecated requirements SHALL remain documented.
- Existing implementation: None
- Missing implementation behavior: N/A (not an implementable requirement).
- Missing test coverage: No test exists for this requirement.
- Missing evidence: N/A
- Rationale: Interpretive, bibliographic, non-normative-by-design (explicitly marked informative/example), or document-self-referential statement. It does not describe a discrete, independently implementable system behavior.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: N/A

## MCC-CP-001-APPENDIX-D-REVISION-HISTORY-D04

- Specification / section: MCC-CP-001 / Appendix D — Revision History / D.3 Future Revisions
- Status: NOT_APPLICABLE
- Requirement: Superseded requirements SHALL reference their replacements where applicable.
- Existing implementation: None
- Missing implementation behavior: N/A (not an implementable requirement).
- Missing test coverage: No test exists for this requirement.
- Missing evidence: N/A
- Rationale: Interpretive, bibliographic, non-normative-by-design (explicitly marked informative/example), or document-self-referential statement. It does not describe a discrete, independently implementable system behavior.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: N/A

## MCC-CP-001-APPENDIX-E-EXAMPLE-CERTIFICATION-FLOW-D01

- Specification / section: MCC-CP-001 / Appendix E — Example Certification Flow / E.1 Purpose
- Status: NOT_APPLICABLE
- Requirement: The example is provided for illustration only and SHALL NOT introduce additional normative requirements.
- Existing implementation: None
- Missing implementation behavior: N/A (not an implementable requirement).
- Missing test coverage: No test exists for this requirement.
- Missing evidence: N/A
- Rationale: Interpretive, bibliographic, non-normative-by-design (explicitly marked informative/example), or document-self-referential statement. It does not describe a discrete, independently implementable system behavior.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: N/A

## MCC-CP-001-APPENDIX-F-FUTURE-EXTENSIONS-D01

- Specification / section: MCC-CP-001 / Appendix F — Future Extensions / F.1 Purpose
- Status: NOT_APPLICABLE
- Requirement: The items described in this appendix are informative only and SHALL NOT introduce normative requirements.
- Existing implementation: None
- Missing implementation behavior: N/A (not an implementable requirement).
- Missing test coverage: No test exists for this requirement.
- Missing evidence: N/A
- Rationale: Interpretive, bibliographic, non-normative-by-design (explicitly marked informative/example), or document-self-referential statement. It does not describe a discrete, independently implementable system behavior.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: N/A

## MCC-CP-001-APPENDIX-F-FUTURE-EXTENSIONS-D02

- Specification / section: MCC-CP-001 / Appendix F — Future Extensions / F.2 Potential Extensions
- Status: NOT_APPLICABLE
- Requirement: Future extensions SHALL preserve backward traceability unless an explicitly documented breaking revision is published.
- Existing implementation: None
- Missing implementation behavior: N/A (not an implementable requirement).
- Missing test coverage: No test exists for this requirement.
- Missing evidence: N/A
- Rationale: Interpretive, bibliographic, non-normative-by-design (explicitly marked informative/example), or document-self-referential statement. It does not describe a discrete, independently implementable system behavior.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: N/A

## MCC-CP-001-APPENDIX-G-CONFORMANCE-RESULT-REQUIREMEN-D01

- Specification / section: MCC-CP-001 / Appendix G — Conformance Result Requirements / G.2 Conformance Result Content
- Status: PARTIAL
- Requirement: The Conformance Result SHALL identify: - the Certification Subject identifier, as defined in Section 7.2; - the specification version under which certification was performed; - the overall certification outcome, exactly one of PASS or FAIL, consistent with Section 8.6 and Section 9.6; - the Requirement Result (PASS, FAIL, or NOT APPLICABLE) for every evaluated Certification Requirement, consistent with Section 10.4; - the generation timestamp.
- Existing implementation: src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: scenarios_passed / scenarios_failed / scenarios_total in certifications/manifest.json is a real, reproducible Conformance-Result-equivalent, carried within the certification manifest rather than as a separate artifact, matching this appendix's own "not a separate artifact" model.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-APPENDIX-G-CONFORMANCE-RESULT-REQUIREMEN-D02

- Specification / section: MCC-CP-001 / Appendix G — Conformance Result Requirements / G.3 Relationship to the Certification Manifest
- Status: PARTIAL
- Requirement: It SHALL be carried by the Manifest Fields required under Section 15.2 ("certification requirements evaluated" and "certification result"), as further specified by MCC-CM-001.
- Existing implementation: src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: scenarios_passed / scenarios_failed / scenarios_total in certifications/manifest.json is a real, reproducible Conformance-Result-equivalent, carried within the certification manifest rather than as a separate artifact, matching this appendix's own "not a separate artifact" model.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-APPENDIX-G-CONFORMANCE-RESULT-REQUIREMEN-D03

- Specification / section: MCC-CP-001 / Appendix G — Conformance Result Requirements / G.3 Relationship to the Certification Manifest
- Status: PARTIAL
- Requirement: A certification implementation MUST NOT produce a Conformance Result as a document distinct from the Certification Manifest.
- Existing implementation: src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: scenarios_passed / scenarios_failed / scenarios_total in certifications/manifest.json is a real, reproducible Conformance-Result-equivalent, carried within the certification manifest rather than as a separate artifact, matching this appendix's own "not a separate artifact" model.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-APPENDIX-H-CERTIFICATION-REPORT-REQUIREM-D01

- Specification / section: MCC-CP-001 / Appendix H — Certification Report Requirements / H.2 Certification Report Content
- Status: PARTIAL
- Requirement: Every Certification Report SHALL include: - the Certification Subject identifier; - the specification version under which certification was performed; - the overall certification outcome (PASS or FAIL); - a human-readable summary of Requirement Results; - a reference to the associated Certification Manifest; - the generation timestamp.
- Existing implementation: src/mcc_compliance/reporting.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_compliance/reporting.py generates a real, deterministic, human-readable Markdown report (secret-free, non-authoritative relative to the manifest, with an explicit certification-scope disclaimer) — closely matching this appendix's required content and properties.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-APPENDIX-H-CERTIFICATION-REPORT-REQUIREM-D02

- Specification / section: MCC-CP-001 / Appendix H — Certification Report Requirements / H.3 Certification Report Properties
- Status: PARTIAL
- Requirement: The Certification Report SHALL NOT be treated as the authoritative record of a certification outcome.
- Existing implementation: src/mcc_compliance/reporting.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_compliance/reporting.py generates a real, deterministic, human-readable Markdown report (secret-free, non-authoritative relative to the manifest, with an explicit certification-scope disclaimer) — closely matching this appendix's required content and properties.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-APPENDIX-H-CERTIFICATION-REPORT-REQUIREM-D03

- Specification / section: MCC-CP-001 / Appendix H — Certification Report Requirements / H.5 Certification Report Applicability
- Status: PARTIAL
- Requirement: A Certification Report SHALL be produced for every successful certification, consistent with Section 7.4.
- Existing implementation: src/mcc_compliance/reporting.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_compliance/reporting.py generates a real, deterministic, human-readable Markdown report (secret-free, non-authoritative relative to the manifest, with an explicit certification-scope disclaimer) — closely matching this appendix's required content and properties.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-CP-001-DOCUMENT-ROADMAP-D01

- Specification / section: MCC-CP-001 / Document Roadmap
- Status: NOT_APPLICABLE
- Requirement: Future revisions MAY extend this structure but SHALL preserve numbering compatibility whenever practical.
- Existing implementation: None
- Missing implementation behavior: N/A (not an implementable requirement).
- Missing test coverage: No test exists for this requirement.
- Missing evidence: N/A
- Rationale: Interpretive, bibliographic, non-normative-by-design (explicitly marked informative/example), or document-self-referential statement. It does not describe a discrete, independently implementable system behavior.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: N/A

## MCC-CP-001-DOCUMENT-ROADMAP-D02

- Specification / section: MCC-CP-001 / Document Roadmap
- Status: NOT_APPLICABLE
- Requirement: The remaining sections SHALL be developed according to this roadmap unless superseded by a later approved specification revision.
- Existing implementation: None
- Missing implementation behavior: N/A (not an implementable requirement).
- Missing test coverage: No test exists for this requirement.
- Missing evidence: N/A
- Rationale: Interpretive, bibliographic, non-normative-by-design (explicitly marked informative/example), or document-self-referential statement. It does not describe a discrete, independently implementable system behavior.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: N/A

## MCC-CP-001-STATUS-OF-THIS-SPECIFICATION-D01

- Specification / section: MCC-CP-001 / Status of This Specification
- Status: NOT_APPLICABLE
- Requirement: Normative keywords such as MUST, MUST NOT, REQUIRED, SHALL, SHALL NOT, SHOULD, SHOULD NOT, RECOMMENDED, MAY and OPTIONAL are to be interpreted as described in RFC 2119 and RFC 8174.
- Existing implementation: None
- Missing implementation behavior: N/A (not an implementable requirement).
- Missing test coverage: No test exists for this requirement.
- Missing evidence: N/A
- Rationale: Interpretive, bibliographic, non-normative-by-design (explicitly marked informative/example), or document-self-referential statement. It does not describe a discrete, independently implementable system behavior.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: N/A

## REF-001

- Specification / section: MCC-CP-001 / 21. References / 21.4 Reference Invariants
- Status: NOT_APPLICABLE
- Requirement: Normative references SHALL identify normative specifications.
- Existing implementation: None
- Missing implementation behavior: N/A (not an implementable requirement).
- Missing test coverage: No test exists for this requirement.
- Missing evidence: N/A
- Rationale: Interpretive, bibliographic, non-normative-by-design (explicitly marked informative/example), or document-self-referential statement. It does not describe a discrete, independently implementable system behavior.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: N/A

## REF-002

- Specification / section: MCC-CP-001 / 21. References / 21.4 Reference Invariants
- Status: NOT_APPLICABLE
- Requirement: Informative references SHALL NOT define normative behavior.
- Existing implementation: None
- Missing implementation behavior: N/A (not an implementable requirement).
- Missing test coverage: No test exists for this requirement.
- Missing evidence: N/A
- Rationale: Interpretive, bibliographic, non-normative-by-design (explicitly marked informative/example), or document-self-referential statement. It does not describe a discrete, independently implementable system behavior.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: N/A

## REF-003

- Specification / section: MCC-CP-001 / 21. References / 21.4 Reference Invariants
- Status: NOT_APPLICABLE
- Requirement: References SHALL remain versioned.
- Existing implementation: None
- Missing implementation behavior: N/A (not an implementable requirement).
- Missing test coverage: No test exists for this requirement.
- Missing evidence: N/A
- Rationale: Interpretive, bibliographic, non-normative-by-design (explicitly marked informative/example), or document-self-referential statement. It does not describe a discrete, independently implementable system behavior.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: N/A

## REF-004

- Specification / section: MCC-CP-001 / 21. References / 21.4 Reference Invariants
- Status: NOT_APPLICABLE
- Requirement: References SHALL remain traceable.
- Existing implementation: None
- Missing implementation behavior: N/A (not an implementable requirement).
- Missing test coverage: No test exists for this requirement.
- Missing evidence: N/A
- Rationale: Interpretive, bibliographic, non-normative-by-design (explicitly marked informative/example), or document-self-referential statement. It does not describe a discrete, independently implementable system behavior.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: N/A

## REF-005

- Specification / section: MCC-CP-001 / 21. References / 21.4 Reference Invariants
- Status: NOT_APPLICABLE
- Requirement: References SHALL remain implementation-independent.
- Existing implementation: None
- Missing implementation behavior: N/A (not an implementable requirement).
- Missing test coverage: No test exists for this requirement.
- Missing evidence: N/A
- Rationale: Interpretive, bibliographic, non-normative-by-design (explicitly marked informative/example), or document-self-referential statement. It does not describe a discrete, independently implementable system behavior.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: N/A

## REF-006

- Specification / section: MCC-CP-001 / 21. References / 21.4 Reference Invariants
- Status: NOT_APPLICABLE
- Requirement: References SHALL remain framework-neutral.
- Existing implementation: None
- Missing implementation behavior: N/A (not an implementable requirement).
- Missing test coverage: No test exists for this requirement.
- Missing evidence: N/A
- Rationale: Interpretive, bibliographic, non-normative-by-design (explicitly marked informative/example), or document-self-referential statement. It does not describe a discrete, independently implementable system behavior.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: N/A

## REF-007

- Specification / section: MCC-CP-001 / 21. References / 21.4 Reference Invariants
- Status: NOT_APPLICABLE
- Requirement: References SHALL support reproducible certification.
- Existing implementation: None
- Missing implementation behavior: N/A (not an implementable requirement).
- Missing test coverage: No test exists for this requirement.
- Missing evidence: N/A
- Rationale: Interpretive, bibliographic, non-normative-by-design (explicitly marked informative/example), or document-self-referential statement. It does not describe a discrete, independently implementable system behavior.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: N/A

## REG-001

- Specification / section: MCC-CP-001 / 19. Registry Considerations / 19.4 Registry Invariants
- Status: PARTIAL
- Requirement: Registry identifiers SHALL be globally unique.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: certifications/manifest.json is itself a real, version-controlled, CI-verified registry of certification records, the same registry concept this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## REG-002

- Specification / section: MCC-CP-001 / 19. Registry Considerations / 19.4 Registry Invariants
- Status: PARTIAL
- Requirement: Registry entries SHALL remain immutable.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: certifications/manifest.json is itself a real, version-controlled, CI-verified registry of certification records, the same registry concept this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## REG-003

- Specification / section: MCC-CP-001 / 19. Registry Considerations / 19.4 Registry Invariants
- Status: PARTIAL
- Requirement: Registry entries SHALL remain framework-neutral.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: certifications/manifest.json is itself a real, version-controlled, CI-verified registry of certification records, the same registry concept this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## REG-004

- Specification / section: MCC-CP-001 / 19. Registry Considerations / 19.4 Registry Invariants
- Status: PARTIAL
- Requirement: Registry entries SHALL remain implementation-independent.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: certifications/manifest.json is itself a real, version-controlled, CI-verified registry of certification records, the same registry concept this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## REG-005

- Specification / section: MCC-CP-001 / 19. Registry Considerations / 19.4 Registry Invariants
- Status: PARTIAL
- Requirement: Registry entries SHALL support independent verification.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: certifications/manifest.json is itself a real, version-controlled, CI-verified registry of certification records, the same registry concept this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## REG-006

- Specification / section: MCC-CP-001 / 19. Registry Considerations / 19.4 Registry Invariants
- Status: PARTIAL
- Requirement: Registry entries SHALL preserve version traceability.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: certifications/manifest.json is itself a real, version-controlled, CI-verified registry of certification records, the same registry concept this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## REG-007

- Specification / section: MCC-CP-001 / 19. Registry Considerations / 19.4 Registry Invariants
- Status: PARTIAL
- Requirement: Registry entries SHALL remain reproducible.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: certifications/manifest.json is itself a real, version-controlled, CI-verified registry of certification records, the same registry concept this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## REQ-001

- Specification / section: MCC-CP-001 / 12. Certification Requirements / 12.6 Requirement Invariants
- Status: PARTIAL
- Requirement: Requirements SHALL be normative.
- Existing implementation: src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: The compliance vector manifest (src/mcc_compliance/vectors/v1/manifest.json) gives each requirement-like vector a stable id, an associated invariant/requirement name, and a verification scenario — the same requirement-identity model this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## REQ-002

- Specification / section: MCC-CP-001 / 12. Certification Requirements / 12.6 Requirement Invariants
- Status: PARTIAL
- Requirement: Requirements SHALL be uniquely identified.
- Existing implementation: src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: The compliance vector manifest (src/mcc_compliance/vectors/v1/manifest.json) gives each requirement-like vector a stable id, an associated invariant/requirement name, and a verification scenario — the same requirement-identity model this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## REQ-003

- Specification / section: MCC-CP-001 / 12. Certification Requirements / 12.6 Requirement Invariants
- Status: PARTIAL
- Requirement: Requirements SHALL be reproducible.
- Existing implementation: src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: The compliance vector manifest (src/mcc_compliance/vectors/v1/manifest.json) gives each requirement-like vector a stable id, an associated invariant/requirement name, and a verification scenario — the same requirement-identity model this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## REQ-004

- Specification / section: MCC-CP-001 / 12. Certification Requirements / 12.6 Requirement Invariants
- Status: PARTIAL
- Requirement: Requirements SHALL remain framework-neutral.
- Existing implementation: src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: The compliance vector manifest (src/mcc_compliance/vectors/v1/manifest.json) gives each requirement-like vector a stable id, an associated invariant/requirement name, and a verification scenario — the same requirement-identity model this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## REQ-005

- Specification / section: MCC-CP-001 / 12. Certification Requirements / 12.6 Requirement Invariants
- Status: PARTIAL
- Requirement: Requirements SHALL remain implementation-independent.
- Existing implementation: src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: The compliance vector manifest (src/mcc_compliance/vectors/v1/manifest.json) gives each requirement-like vector a stable id, an associated invariant/requirement name, and a verification scenario — the same requirement-identity model this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## REQ-006

- Specification / section: MCC-CP-001 / 12. Certification Requirements / 12.6 Requirement Invariants
- Status: PARTIAL
- Requirement: Requirements SHALL define verification methods.
- Existing implementation: src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: The compliance vector manifest (src/mcc_compliance/vectors/v1/manifest.json) gives each requirement-like vector a stable id, an associated invariant/requirement name, and a verification scenario — the same requirement-identity model this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## REQ-007

- Specification / section: MCC-CP-001 / 12. Certification Requirements / 12.6 Requirement Invariants
- Status: PARTIAL
- Requirement: Requirements SHALL remain fully traceable.
- Existing implementation: src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: The compliance vector manifest (src/mcc_compliance/vectors/v1/manifest.json) gives each requirement-like vector a stable id, an associated invariant/requirement name, and a verification scenario — the same requirement-identity model this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## REV-001

- Specification / section: MCC-CP-001 / Appendix D — Revision History / D.4 Revision Invariants
- Status: NOT_APPLICABLE
- Requirement: Every published revision SHALL have a unique version identifier.
- Existing implementation: None
- Missing implementation behavior: N/A (not an implementable requirement).
- Missing test coverage: No test exists for this requirement.
- Missing evidence: N/A
- Rationale: Interpretive, bibliographic, non-normative-by-design (explicitly marked informative/example), or document-self-referential statement. It does not describe a discrete, independently implementable system behavior.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: N/A

## REV-002

- Specification / section: MCC-CP-001 / Appendix D — Revision History / D.4 Revision Invariants
- Status: NOT_APPLICABLE
- Requirement: Every revision SHALL include a change summary.
- Existing implementation: None
- Missing implementation behavior: N/A (not an implementable requirement).
- Missing test coverage: No test exists for this requirement.
- Missing evidence: N/A
- Rationale: Interpretive, bibliographic, non-normative-by-design (explicitly marked informative/example), or document-self-referential statement. It does not describe a discrete, independently implementable system behavior.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: N/A

## REV-003

- Specification / section: MCC-CP-001 / Appendix D — Revision History / D.4 Revision Invariants
- Status: NOT_APPLICABLE
- Requirement: Breaking changes SHALL be explicitly identified.
- Existing implementation: None
- Missing implementation behavior: N/A (not an implementable requirement).
- Missing test coverage: No test exists for this requirement.
- Missing evidence: N/A
- Rationale: Interpretive, bibliographic, non-normative-by-design (explicitly marked informative/example), or document-self-referential statement. It does not describe a discrete, independently implementable system behavior.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: N/A

## REV-004

- Specification / section: MCC-CP-001 / Appendix D — Revision History / D.4 Revision Invariants
- Status: NOT_APPLICABLE
- Requirement: Revision history SHALL remain immutable after publication.
- Existing implementation: None
- Missing implementation behavior: N/A (not an implementable requirement).
- Missing test coverage: No test exists for this requirement.
- Missing evidence: N/A
- Rationale: Interpretive, bibliographic, non-normative-by-design (explicitly marked informative/example), or document-self-referential statement. It does not describe a discrete, independently implementable system behavior.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: N/A

## REV-005

- Specification / section: MCC-CP-001 / Appendix D — Revision History / D.4 Revision Invariants
- Status: NOT_APPLICABLE
- Requirement: Revision history SHALL remain traceable.
- Existing implementation: None
- Missing implementation behavior: N/A (not an implementable requirement).
- Missing test coverage: No test exists for this requirement.
- Missing evidence: N/A
- Rationale: Interpretive, bibliographic, non-normative-by-design (explicitly marked informative/example), or document-self-referential statement. It does not describe a discrete, independently implementable system behavior.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: N/A

## REV-006

- Specification / section: MCC-CP-001 / Appendix D — Revision History / D.4 Revision Invariants
- Status: NOT_APPLICABLE
- Requirement: Revision history SHALL remain versioned.
- Existing implementation: None
- Missing implementation behavior: N/A (not an implementable requirement).
- Missing test coverage: No test exists for this requirement.
- Missing evidence: N/A
- Rationale: Interpretive, bibliographic, non-normative-by-design (explicitly marked informative/example), or document-self-referential statement. It does not describe a discrete, independently implementable system behavior.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: N/A

## REV-007

- Specification / section: MCC-CP-001 / Appendix D — Revision History / D.4 Revision Invariants
- Status: NOT_APPLICABLE
- Requirement: Revision history SHALL support independent verification of specification evolution.
- Existing implementation: None
- Missing implementation behavior: N/A (not an implementable requirement).
- Missing test coverage: No test exists for this requirement.
- Missing evidence: N/A
- Rationale: Interpretive, bibliographic, non-normative-by-design (explicitly marked informative/example), or document-self-referential statement. It does not describe a discrete, independently implementable system behavior.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: N/A

## RID-001

- Specification / section: MCC-CP-001 / Appendix C — Requirement Identifier Registry / C.4 Registry Invariants
- Status: NOT_APPLICABLE
- Requirement: Requirement identifiers SHALL be globally unique.
- Existing implementation: None
- Missing implementation behavior: N/A (not an implementable requirement).
- Missing test coverage: No test exists for this requirement.
- Missing evidence: N/A
- Rationale: Interpretive, bibliographic, non-normative-by-design (explicitly marked informative/example), or document-self-referential statement. It does not describe a discrete, independently implementable system behavior.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: N/A

## RID-002

- Specification / section: MCC-CP-001 / Appendix C — Requirement Identifier Registry / C.4 Registry Invariants
- Status: NOT_APPLICABLE
- Requirement: Requirement identifiers SHALL remain versioned.
- Existing implementation: None
- Missing implementation behavior: N/A (not an implementable requirement).
- Missing test coverage: No test exists for this requirement.
- Missing evidence: N/A
- Rationale: Interpretive, bibliographic, non-normative-by-design (explicitly marked informative/example), or document-self-referential statement. It does not describe a discrete, independently implementable system behavior.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: N/A

## RID-003

- Specification / section: MCC-CP-001 / Appendix C — Requirement Identifier Registry / C.4 Registry Invariants
- Status: NOT_APPLICABLE
- Requirement: Requirement identifiers SHALL remain traceable.
- Existing implementation: None
- Missing implementation behavior: N/A (not an implementable requirement).
- Missing test coverage: No test exists for this requirement.
- Missing evidence: N/A
- Rationale: Interpretive, bibliographic, non-normative-by-design (explicitly marked informative/example), or document-self-referential statement. It does not describe a discrete, independently implementable system behavior.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: N/A

## RID-004

- Specification / section: MCC-CP-001 / Appendix C — Requirement Identifier Registry / C.4 Registry Invariants
- Status: NOT_APPLICABLE
- Requirement: Registry entries SHALL remain immutable.
- Existing implementation: None
- Missing implementation behavior: N/A (not an implementable requirement).
- Missing test coverage: No test exists for this requirement.
- Missing evidence: N/A
- Rationale: Interpretive, bibliographic, non-normative-by-design (explicitly marked informative/example), or document-self-referential statement. It does not describe a discrete, independently implementable system behavior.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: N/A

## RID-005

- Specification / section: MCC-CP-001 / Appendix C — Requirement Identifier Registry / C.4 Registry Invariants
- Status: NOT_APPLICABLE
- Requirement: Registry entries SHALL support reproducible certification.
- Existing implementation: None
- Missing implementation behavior: N/A (not an implementable requirement).
- Missing test coverage: No test exists for this requirement.
- Missing evidence: N/A
- Rationale: Interpretive, bibliographic, non-normative-by-design (explicitly marked informative/example), or document-self-referential statement. It does not describe a discrete, independently implementable system behavior.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: N/A

## RID-006

- Specification / section: MCC-CP-001 / Appendix C — Requirement Identifier Registry / C.4 Registry Invariants
- Status: NOT_APPLICABLE
- Requirement: Registry entries SHALL remain implementation-independent.
- Existing implementation: None
- Missing implementation behavior: N/A (not an implementable requirement).
- Missing test coverage: No test exists for this requirement.
- Missing evidence: N/A
- Rationale: Interpretive, bibliographic, non-normative-by-design (explicitly marked informative/example), or document-self-referential statement. It does not describe a discrete, independently implementable system behavior.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: N/A

## RID-007

- Specification / section: MCC-CP-001 / Appendix C — Requirement Identifier Registry / C.4 Registry Invariants
- Status: NOT_APPLICABLE
- Requirement: Registry entries SHALL remain framework-neutral.
- Existing implementation: None
- Missing implementation behavior: N/A (not an implementable requirement).
- Missing test coverage: No test exists for this requirement.
- Missing evidence: N/A
- Rationale: Interpretive, bibliographic, non-normative-by-design (explicitly marked informative/example), or document-self-referential statement. It does not describe a discrete, independently implementable system behavior.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: N/A

## SEC-001

- Specification / section: MCC-CP-001 / 18. Security Considerations / 18.4 Security Invariants
- Status: PARTIAL
- Requirement: Certification SHALL be evidence-based.
- Existing implementation: src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: The compliance suite is evidence-based, reproducible, and fail-closed (every mandatory vector must pass), the same security posture this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## SEC-002

- Specification / section: MCC-CP-001 / 18. Security Considerations / 18.4 Security Invariants
- Status: PARTIAL
- Requirement: Certification SHALL remain reproducible.
- Existing implementation: src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: The compliance suite is evidence-based, reproducible, and fail-closed (every mandatory vector must pass), the same security posture this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## SEC-003

- Specification / section: MCC-CP-001 / 18. Security Considerations / 18.4 Security Invariants
- Status: PARTIAL
- Requirement: Certification SHALL remain independently verifiable.
- Existing implementation: src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: The compliance suite is evidence-based, reproducible, and fail-closed (every mandatory vector must pass), the same security posture this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## SEC-004

- Specification / section: MCC-CP-001 / 18. Security Considerations / 18.4 Security Invariants
- Status: PARTIAL
- Requirement: Certification SHALL preserve evidence integrity.
- Existing implementation: src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: The compliance suite is evidence-based, reproducible, and fail-closed (every mandatory vector must pass), the same security posture this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## SEC-005

- Specification / section: MCC-CP-001 / 18. Security Considerations / 18.4 Security Invariants
- Status: PARTIAL
- Requirement: Certification SHALL preserve manifest integrity.
- Existing implementation: src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: The compliance suite is evidence-based, reproducible, and fail-closed (every mandatory vector must pass), the same security posture this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## SEC-006

- Specification / section: MCC-CP-001 / 18. Security Considerations / 18.4 Security Invariants
- Status: PARTIAL
- Requirement: Certification SHALL preserve certificate integrity.
- Existing implementation: src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: The compliance suite is evidence-based, reproducible, and fail-closed (every mandatory vector must pass), the same security posture this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## SEC-007

- Specification / section: MCC-CP-001 / 18. Security Considerations / 18.4 Security Invariants
- Status: PARTIAL
- Requirement: Certification SHALL preserve specification traceability.
- Existing implementation: src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: The compliance suite is evidence-based, reproducible, and fail-closed (every mandatory vector must pass), the same security posture this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## STATE-001

- Specification / section: MCC-CP-001 / Appendix A — Certification State Machine / A.4 State Invariants
- Status: GAP
- Requirement: Certification SHALL have exactly one active state.
- Existing implementation: None
- Missing implementation behavior: Full requirement not implemented.
- Missing test coverage: No test exists for this requirement.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: No explicit certification-process state machine (Draft/Submitted/Under Evaluation/.../Archived) implementation was found; the compliance runner is a single synchronous pass, not a persisted multi-state record.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## STATE-002

- Specification / section: MCC-CP-001 / Appendix A — Certification State Machine / A.4 State Invariants
- Status: GAP
- Requirement: State transitions SHALL be traceable.
- Existing implementation: None
- Missing implementation behavior: Full requirement not implemented.
- Missing test coverage: No test exists for this requirement.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: No explicit certification-process state machine (Draft/Submitted/Under Evaluation/.../Archived) implementation was found; the compliance runner is a single synchronous pass, not a persisted multi-state record.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## STATE-003

- Specification / section: MCC-CP-001 / Appendix A — Certification State Machine / A.4 State Invariants
- Status: GAP
- Requirement: State transitions SHALL be reproducible.
- Existing implementation: None
- Missing implementation behavior: Full requirement not implemented.
- Missing test coverage: No test exists for this requirement.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: No explicit certification-process state machine (Draft/Submitted/Under Evaluation/.../Archived) implementation was found; the compliance runner is a single synchronous pass, not a persisted multi-state record.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## STATE-004

- Specification / section: MCC-CP-001 / Appendix A — Certification State Machine / A.4 State Invariants
- Status: GAP
- Requirement: Archived certifications SHALL remain verifiable.
- Existing implementation: None
- Missing implementation behavior: Full requirement not implemented.
- Missing test coverage: No test exists for this requirement.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: No explicit certification-process state machine (Draft/Submitted/Under Evaluation/.../Archived) implementation was found; the compliance runner is a single synchronous pass, not a persisted multi-state record.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## STATE-005

- Specification / section: MCC-CP-001 / Appendix A — Certification State Machine / A.4 State Invariants
- Status: GAP
- Requirement: Revoked certifications SHALL preserve historical evidence.
- Existing implementation: None
- Missing implementation behavior: Full requirement not implemented.
- Missing test coverage: No test exists for this requirement.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: No explicit certification-process state machine (Draft/Submitted/Under Evaluation/.../Archived) implementation was found; the compliance runner is a single synchronous pass, not a persisted multi-state record.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## STATE-006

- Specification / section: MCC-CP-001 / Appendix A — Certification State Machine / A.4 State Invariants
- Status: GAP
- Requirement: Certification SHALL NOT skip mandatory states.
- Existing implementation: None
- Missing implementation behavior: Full requirement not implemented.
- Missing test coverage: No test exists for this requirement.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: No explicit certification-process state machine (Draft/Submitted/Under Evaluation/.../Archived) implementation was found; the compliance runner is a single synchronous pass, not a persisted multi-state record.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## STATE-007

- Specification / section: MCC-CP-001 / Appendix A — Certification State Machine / A.4 State Invariants
- Status: GAP
- Requirement: State history SHALL remain immutable.
- Existing implementation: None
- Missing implementation behavior: Full requirement not implemented.
- Missing test coverage: No test exists for this requirement.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: No explicit certification-process state machine (Draft/Submitted/Under Evaluation/.../Archived) implementation was found; the compliance runner is a single synchronous pass, not a persisted multi-state record.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## VER-001

- Specification / section: MCC-CP-001 / 17. Versioning / 17.5 Version Invariants
- Status: PARTIAL
- Requirement: Specification versions SHALL be immutable.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: contract_version / compliance_suite_version / MANIFEST_SCHEMA_VERSION are independently tracked, immutable-once-published identifiers, the same versioning model this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## VER-002

- Specification / section: MCC-CP-001 / 17. Versioning / 17.5 Version Invariants
- Status: PARTIAL
- Requirement: Certification SHALL reference exactly one specification version.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: contract_version / compliance_suite_version / MANIFEST_SCHEMA_VERSION are independently tracked, immutable-once-published identifiers, the same versioning model this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## VER-003

- Specification / section: MCC-CP-001 / 17. Versioning / 17.5 Version Invariants
- Status: PARTIAL
- Requirement: Version identifiers SHALL remain globally unique.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: contract_version / compliance_suite_version / MANIFEST_SCHEMA_VERSION are independently tracked, immutable-once-published identifiers, the same versioning model this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## VER-004

- Specification / section: MCC-CP-001 / 17. Versioning / 17.5 Version Invariants
- Status: PARTIAL
- Requirement: Version compatibility SHALL be explicitly documented.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: contract_version / compliance_suite_version / MANIFEST_SCHEMA_VERSION are independently tracked, immutable-once-published identifiers, the same versioning model this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## VER-005

- Specification / section: MCC-CP-001 / 17. Versioning / 17.5 Version Invariants
- Status: PARTIAL
- Requirement: Historical certification results SHALL remain reproducible.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: contract_version / compliance_suite_version / MANIFEST_SCHEMA_VERSION are independently tracked, immutable-once-published identifiers, the same versioning model this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## VER-006

- Specification / section: MCC-CP-001 / 17. Versioning / 17.5 Version Invariants
- Status: PARTIAL
- Requirement: Revalidation SHALL NOT overwrite previous certification records.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: contract_version / compliance_suite_version / MANIFEST_SCHEMA_VERSION are independently tracked, immutable-once-published identifiers, the same versioning model this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## VER-007

- Specification / section: MCC-CP-001 / 17. Versioning / 17.5 Version Invariants
- Status: PARTIAL
- Requirement: Version history SHALL remain traceable.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: contract_version / compliance_suite_version / MANIFEST_SCHEMA_VERSION are independently tracked, immutable-once-published identifiers, the same versioning model this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## EB-COMPAT-001

- Specification / section: MCC-EB-001 / 18. Compatibility Requirements / 18.5 Compatibility Invariants
- Status: PARTIAL
- Requirement: Compatibility claims between Schema Versions MUST be explicit, not assumed.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: BUNDLE_SCHEMA_VERSION / SUPPORTED_SCHEMA_VERSIONS and the UNSUPPORTED_SCHEMA verification outcome implement the same reject-unrecognized-schema-version model this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## EB-COMPAT-002

- Specification / section: MCC-EB-001 / 18. Compatibility Requirements / 18.5 Compatibility Invariants
- Status: PARTIAL
- Requirement: Unrecognized Schema Versions MUST NOT be silently accepted.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: BUNDLE_SCHEMA_VERSION / SUPPORTED_SCHEMA_VERSIONS and the UNSUPPORTED_SCHEMA verification outcome implement the same reject-unrecognized-schema-version model this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## EB-COMPAT-003

- Specification / section: MCC-EB-001 / 18. Compatibility Requirements / 18.5 Compatibility Invariants
- Status: PARTIAL
- Requirement: Breaking changes MUST introduce a new Schema Version.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: BUNDLE_SCHEMA_VERSION / SUPPORTED_SCHEMA_VERSIONS and the UNSUPPORTED_SCHEMA verification outcome implement the same reject-unrecognized-schema-version model this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## EB-COMPAT-004

- Specification / section: MCC-EB-001 / 18. Compatibility Requirements / 18.5 Compatibility Invariants
- Status: PARTIAL
- Requirement: Compatibility MUST remain independent of implementation or tooling.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: BUNDLE_SCHEMA_VERSION / SUPPORTED_SCHEMA_VERSIONS and the UNSUPPORTED_SCHEMA verification outcome implement the same reject-unrecognized-schema-version model this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## EB-CONF-001

- Specification / section: MCC-EB-001 / 22. Conformance Requirements / 22.5 Conformance Invariants
- Status: GAP
- Requirement: Conformance is defined separately for Bundle producers and Bundle validators.
- Existing implementation: None
- Missing implementation behavior: Full requirement not implemented.
- Missing test coverage: No test exists for this requirement.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: No producer/validator conformance-declaration mechanism specific to this specification's Bundle Schema Version was found.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## EB-CONF-002

- Specification / section: MCC-EB-001 / 22. Conformance Requirements / 22.5 Conformance Invariants
- Status: GAP
- Requirement: A conforming producer MUST NOT emit Bundles that fail their own declared Schema Version's validation rules.
- Existing implementation: None
- Missing implementation behavior: Full requirement not implemented.
- Missing test coverage: No test exists for this requirement.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: No producer/validator conformance-declaration mechanism specific to this specification's Bundle Schema Version was found.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## EB-CONF-003

- Specification / section: MCC-EB-001 / 22. Conformance Requirements / 22.5 Conformance Invariants
- Status: GAP
- Requirement: A conforming validator MUST implement fail-closed validation in full.
- Existing implementation: None
- Missing implementation behavior: Full requirement not implemented.
- Missing test coverage: No test exists for this requirement.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: No producer/validator conformance-declaration mechanism specific to this specification's Bundle Schema Version was found.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## EB-CONF-004

- Specification / section: MCC-EB-001 / 22. Conformance Requirements / 22.5 Conformance Invariants
- Status: GAP
- Requirement: Conformance MUST remain framework-neutral and implementation-independent.
- Existing implementation: None
- Missing implementation behavior: Full requirement not implemented.
- Missing test coverage: No test exists for this requirement.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: No producer/validator conformance-declaration mechanism specific to this specification's Bundle Schema Version was found.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## EB-EXT-001

- Specification / section: MCC-EB-001 / 20. Extension Model / 20.4 Extension Model Invariants
- Status: GAP
- Requirement: Extensions MUST be explicitly declared in the Bundle Descriptor.
- Existing implementation: None
- Missing implementation behavior: Full requirement not implemented.
- Missing test coverage: No test exists for this requirement.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: No extension-declaration mechanism (a way to mark additional fields as explicit, non-breaking extensions to a committed schema) was found anywhere in this repository for any artifact.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## EB-EXT-002

- Specification / section: MCC-EB-001 / 20. Extension Model / 20.4 Extension Model Invariants
- Status: GAP
- Requirement: Extensions MUST NOT redefine the meaning of Required Files or Required Metadata.
- Existing implementation: None
- Missing implementation behavior: Full requirement not implemented.
- Missing test coverage: No test exists for this requirement.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: No extension-declaration mechanism (a way to mark additional fields as explicit, non-breaking extensions to a committed schema) was found anywhere in this repository for any artifact.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## EB-EXT-003

- Specification / section: MCC-EB-001 / 20. Extension Model / 20.4 Extension Model Invariants
- Status: GAP
- Requirement: Unrecognized extensions MUST be ignored, not treated as validation failures.
- Existing implementation: None
- Missing implementation behavior: Full requirement not implemented.
- Missing test coverage: No test exists for this requirement.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: No extension-declaration mechanism (a way to mark additional fields as explicit, non-breaking extensions to a committed schema) was found anywhere in this repository for any artifact.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## EB-EXT-004

- Specification / section: MCC-EB-001 / 20. Extension Model / 20.4 Extension Model Invariants
- Status: GAP
- Requirement: Extension content MUST be covered by the Integrity Record.
- Existing implementation: None
- Missing implementation behavior: Full requirement not implemented.
- Missing test coverage: No test exists for this requirement.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: No extension-declaration mechanism (a way to mark additional fields as explicit, non-breaking extensions to a committed schema) was found anywhere in this repository for any artifact.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## EB-FILE-001

- Specification / section: MCC-EB-001 / 11. Required Files / 11.5 Required Files Invariants
- Status: PARTIAL
- Requirement: A Bundle Descriptor MUST be present at the Bundle Root.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_evidence exports/verifies bundles in directory and .tar.gz form with bundle-level metadata (bundle_id, created_at), semantically close to this section, but uses one manifest.json plus named artifact paths rather than this specification's separate Bundle Descriptor / Integrity Record / Provenance Record files, so the exact structural requirement is not met.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## EB-FILE-002

- Specification / section: MCC-EB-001 / 11. Required Files / 11.5 Required Files Invariants
- Status: PARTIAL
- Requirement: An Integrity Record MUST be present at the Bundle Root.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_evidence exports/verifies bundles in directory and .tar.gz form with bundle-level metadata (bundle_id, created_at), semantically close to this section, but uses one manifest.json plus named artifact paths rather than this specification's separate Bundle Descriptor / Integrity Record / Provenance Record files, so the exact structural requirement is not met.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## EB-FILE-003

- Specification / section: MCC-EB-001 / 11. Required Files / 11.5 Required Files Invariants
- Status: PARTIAL
- Requirement: A Provenance Record MUST be present at the Bundle Root.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_evidence exports/verifies bundles in directory and .tar.gz form with bundle-level metadata (bundle_id, created_at), semantically close to this section, but uses one manifest.json plus named artifact paths rather than this specification's separate Bundle Descriptor / Integrity Record / Provenance Record files, so the exact structural requirement is not met.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## EB-FILE-004

- Specification / section: MCC-EB-001 / 11. Required Files / 11.5 Required Files Invariants
- Status: PARTIAL
- Requirement: Every file in the Bundle other than the Integrity Record MUST be enumerated by the Integrity Record.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_evidence exports/verifies bundles in directory and .tar.gz form with bundle-level metadata (bundle_id, created_at), semantically close to this section, but uses one manifest.json plus named artifact paths rather than this specification's separate Bundle Descriptor / Integrity Record / Provenance Record files, so the exact structural requirement is not met.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## EB-FILE-005

- Specification / section: MCC-EB-001 / 11. Required Files / 11.5 Required Files Invariants
- Status: PARTIAL
- Requirement: Required files MUST NOT be omitted regardless of certification outcome.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_evidence exports/verifies bundles in directory and .tar.gz form with bundle-level metadata (bundle_id, created_at), semantically close to this section, but uses one manifest.json plus named artifact paths rather than this specification's separate Bundle Descriptor / Integrity Record / Provenance Record files, so the exact structural requirement is not met.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## EB-HASH-001

- Specification / section: MCC-EB-001 / 13. Hash and Integrity Model / 13.6 Hash and Integrity Invariants
- Status: PARTIAL
- Requirement: All Digest-covered data MUST first be reduced to a deterministic Canonical Form.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_evidence/verify.py recomputes SHA-256 digests over canonical form and rejects any bundle with a mismatched digest as tampered, with dedicated tamper tests — behaviorally equivalent to this requirement, though bound to the mcc-evidence/1 schema rather than this specification's Bundle.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## EB-HASH-002

- Specification / section: MCC-EB-001 / 13. Hash and Integrity Model / 13.6 Hash and Integrity Invariants
- Status: PARTIAL
- Requirement: The Integrity Record MUST declare a collision-resistant hash algorithm.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_evidence/verify.py recomputes SHA-256 digests over canonical form and rejects any bundle with a mismatched digest as tampered, with dedicated tamper tests — behaviorally equivalent to this requirement, though bound to the mcc-evidence/1 schema rather than this specification's Bundle.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## EB-HASH-003

- Specification / section: MCC-EB-001 / 13. Hash and Integrity Model / 13.6 Hash and Integrity Invariants
- Status: PARTIAL
- Requirement: Every non-Integrity-Record file MUST have a corresponding Digest entry.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_evidence/verify.py recomputes SHA-256 digests over canonical form and rejects any bundle with a mismatched digest as tampered, with dedicated tamper tests — behaviorally equivalent to this requirement, though bound to the mcc-evidence/1 schema rather than this specification's Bundle.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## EB-HASH-004

- Specification / section: MCC-EB-001 / 13. Hash and Integrity Model / 13.6 Hash and Integrity Invariants
- Status: PARTIAL
- Requirement: Digest verification MUST be performed by independent recomputation, not by trusting a prior verification result.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_evidence/verify.py recomputes SHA-256 digests over canonical form and rejects any bundle with a mismatched digest as tampered, with dedicated tamper tests — behaviorally equivalent to this requirement, though bound to the mcc-evidence/1 schema rather than this specification's Bundle.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## EB-HASH-005

- Specification / section: MCC-EB-001 / 13. Hash and Integrity Model / 13.6 Hash and Integrity Invariants
- Status: PARTIAL
- Requirement: A Bundle with any mismatched Digest MUST be rejected as tampered.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_evidence/verify.py recomputes SHA-256 digests over canonical form and rejects any bundle with a mismatched digest as tampered, with dedicated tamper tests — behaviorally equivalent to this requirement, though bound to the mcc-evidence/1 schema rather than this specification's Bundle.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## EB-META-001

- Specification / section: MCC-EB-001 / 12. Required Metadata / 12.4 Required Metadata Invariants
- Status: PARTIAL
- Requirement: Bundle-level metadata MUST identify the Bundle, its schema version, and the specification version it was produced under.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_evidence exports/verifies bundles in directory and .tar.gz form with bundle-level metadata (bundle_id, created_at), semantically close to this section, but uses one manifest.json plus named artifact paths rather than this specification's separate Bundle Descriptor / Integrity Record / Provenance Record files, so the exact structural requirement is not met.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## EB-META-002

- Specification / section: MCC-EB-001 / 12. Required Metadata / 12.4 Required Metadata Invariants
- Status: PARTIAL
- Requirement: Every Evidence Item MUST be associated with the Certification Requirement it corresponds to.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_evidence exports/verifies bundles in directory and .tar.gz form with bundle-level metadata (bundle_id, created_at), semantically close to this section, but uses one manifest.json plus named artifact paths rather than this specification's separate Bundle Descriptor / Integrity Record / Provenance Record files, so the exact structural requirement is not met.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## EB-META-003

- Specification / section: MCC-EB-001 / 12. Required Metadata / 12.4 Required Metadata Invariants
- Status: PARTIAL
- Requirement: Every Evidence Item MUST record its verification outcome.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_evidence exports/verifies bundles in directory and .tar.gz form with bundle-level metadata (bundle_id, created_at), semantically close to this section, but uses one manifest.json plus named artifact paths rather than this specification's separate Bundle Descriptor / Integrity Record / Provenance Record files, so the exact structural requirement is not met.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## EB-META-004

- Specification / section: MCC-EB-001 / 12. Required Metadata / 12.4 Required Metadata Invariants
- Status: PARTIAL
- Requirement: Required metadata MUST be covered by the Integrity Record.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_evidence exports/verifies bundles in directory and .tar.gz form with bundle-level metadata (bundle_id, created_at), semantically close to this section, but uses one manifest.json plus named artifact paths rather than this specification's separate Bundle Descriptor / Integrity Record / Provenance Record files, so the exact structural requirement is not met.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## EB-META-005

- Specification / section: MCC-EB-001 / 12. Required Metadata / 12.4 Required Metadata Invariants
- Status: PARTIAL
- Requirement: Metadata SHALL remain immutable after Bundle generation.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_evidence exports/verifies bundles in directory and .tar.gz form with bundle-level metadata (bundle_id, created_at), semantically close to this section, but uses one manifest.json plus named artifact paths rather than this specification's separate Bundle Descriptor / Integrity Record / Provenance Record files, so the exact structural requirement is not met.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## EB-PROV-001

- Specification / section: MCC-EB-001 / 14. Provenance Requirements / 14.5 Provenance Invariants
- Status: PARTIAL
- Requirement: Every Bundle MUST record the certification run that produced it.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: EvidenceInput (export.py) records the originating governance run and correlation id, a narrower provenance model than this section's full requirement set (no explicit prior-bundle chain-of-custody reference field).
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## EB-PROV-002

- Specification / section: MCC-EB-001 / 14. Provenance Requirements / 14.5 Provenance Invariants
- Status: PARTIAL
- Requirement: Every Bundle MUST record the specification versions in effect at generation time.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: EvidenceInput (export.py) records the originating governance run and correlation id, a narrower provenance model than this section's full requirement set (no explicit prior-bundle chain-of-custody reference field).
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## EB-PROV-003

- Specification / section: MCC-EB-001 / 14. Provenance Requirements / 14.5 Provenance Invariants
- Status: PARTIAL
- Requirement: Provenance references between Bundles MUST NOT be circular.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: EvidenceInput (export.py) records the originating governance run and correlation id, a narrower provenance model than this section's full requirement set (no explicit prior-bundle chain-of-custody reference field).
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## EB-PROV-004

- Specification / section: MCC-EB-001 / 14. Provenance Requirements / 14.5 Provenance Invariants
- Status: PARTIAL
- Requirement: Provenance data MUST be covered by the Integrity Record.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: EvidenceInput (export.py) records the originating governance run and correlation id, a narrower provenance model than this section's full requirement set (no explicit prior-bundle chain-of-custody reference field).
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## EB-PROV-005

- Specification / section: MCC-EB-001 / 14. Provenance Requirements / 14.5 Provenance Invariants
- Status: PARTIAL
- Requirement: Provenance data MUST remain immutable after Bundle generation.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: EvidenceInput (export.py) records the originating governance run and correlation id, a narrower provenance model than this section's full requirement set (no explicit prior-bundle chain-of-custody reference field).
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## EB-REF-001

- Specification / section: MCC-EB-001 / 24. References / 24.3 Reference Invariants
- Status: NOT_APPLICABLE
- Requirement: Normative references SHALL identify only documents required to interpret this specification's normative requirements.
- Existing implementation: None
- Missing implementation behavior: N/A (not an implementable requirement).
- Missing test coverage: No test exists for this requirement.
- Missing evidence: N/A
- Rationale: Interpretive, bibliographic, non-normative-by-design (explicitly marked informative/example), or document-self-referential statement. It does not describe a discrete, independently implementable system behavior.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: N/A

## EB-REF-002

- Specification / section: MCC-EB-001 / 24. References / 24.3 Reference Invariants
- Status: NOT_APPLICABLE
- Requirement: Informative references SHALL NOT define normative behavior.
- Existing implementation: None
- Missing implementation behavior: N/A (not an implementable requirement).
- Missing test coverage: No test exists for this requirement.
- Missing evidence: N/A
- Rationale: Interpretive, bibliographic, non-normative-by-design (explicitly marked informative/example), or document-self-referential statement. It does not describe a discrete, independently implementable system behavior.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: N/A

## EB-REF-003

- Specification / section: MCC-EB-001 / 24. References / 24.3 Reference Invariants
- Status: NOT_APPLICABLE
- Requirement: References to planned specifications MUST be clearly marked as informative until those specifications are published.
- Existing implementation: None
- Missing implementation behavior: N/A (not an implementable requirement).
- Missing test coverage: No test exists for this requirement.
- Missing evidence: N/A
- Rationale: Interpretive, bibliographic, non-normative-by-design (explicitly marked informative/example), or document-self-referential statement. It does not describe a discrete, independently implementable system behavior.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: N/A

## EB-REPRO-001

- Specification / section: MCC-EB-001 / 15. Reproducibility Requirements / 15.5 Reproducibility Invariants
- Status: PARTIAL
- Requirement: Bundle generation MUST be deterministic given identical certification inputs and specification version.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: schema.py explicitly documents and excludes non-deterministic fields (created_at, bundle_id) from equivalence comparison — the same determinism-with-declared-exceptions model this section requires — but for the mcc-evidence/1 schema, not this specification's Bundle.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## EB-REPRO-002

- Specification / section: MCC-EB-001 / 15. Reproducibility Requirements / 15.5 Reproducibility Invariants
- Status: PARTIAL
- Requirement: Non-deterministic values MUST NOT influence Canonical Form or Digest computation, except as explicitly permitted.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: schema.py explicitly documents and excludes non-deterministic fields (created_at, bundle_id) from equivalence comparison — the same determinism-with-declared-exceptions model this section requires — but for the mcc-evidence/1 schema, not this specification's Bundle.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## EB-REPRO-003

- Specification / section: MCC-EB-001 / 15. Reproducibility Requirements / 15.5 Reproducibility Invariants
- Status: PARTIAL
- Requirement: Equivalent certification inputs MUST produce Bundles with matching Integrity Records under Section 15.4.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: schema.py explicitly documents and excludes non-deterministic fields (created_at, bundle_id) from equivalence comparison — the same determinism-with-declared-exceptions model this section requires — but for the mcc-evidence/1 schema, not this specification's Bundle.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## EB-REPRO-004

- Specification / section: MCC-EB-001 / 15. Reproducibility Requirements / 15.5 Reproducibility Invariants
- Status: PARTIAL
- Requirement: Reproducibility MUST be verifiable without access to the original generation environment.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: schema.py explicitly documents and excludes non-deterministic fields (created_at, bundle_id) from equivalence comparison — the same determinism-with-declared-exceptions model this section requires — but for the mcc-evidence/1 schema, not this specification's Bundle.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## EB-RID-001

- Specification / section: MCC-EB-001 / 23. Requirement Identifier Registry / 23.5 Registry Invariants
- Status: NOT_APPLICABLE
- Requirement: All identifiers defined by this specification MUST use the `EB-` namespace prefix.
- Existing implementation: None
- Missing implementation behavior: N/A (not an implementable requirement).
- Missing test coverage: No test exists for this requirement.
- Missing evidence: N/A
- Rationale: Interpretive, bibliographic, non-normative-by-design (explicitly marked informative/example), or document-self-referential statement. It does not describe a discrete, independently implementable system behavior.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: N/A

## EB-RID-002

- Specification / section: MCC-EB-001 / 23. Requirement Identifier Registry / 23.5 Registry Invariants
- Status: NOT_APPLICABLE
- Requirement: Identifiers within the `EB-` namespace MUST be globally unique.
- Existing implementation: None
- Missing implementation behavior: N/A (not an implementable requirement).
- Missing test coverage: No test exists for this requirement.
- Missing evidence: N/A
- Rationale: Interpretive, bibliographic, non-normative-by-design (explicitly marked informative/example), or document-self-referential statement. It does not describe a discrete, independently implementable system behavior.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: N/A

## EB-RID-003

- Specification / section: MCC-EB-001 / 23. Requirement Identifier Registry / 23.5 Registry Invariants
- Status: NOT_APPLICABLE
- Requirement: Retired identifiers MUST NOT be reassigned to a different requirement.
- Existing implementation: None
- Missing implementation behavior: N/A (not an implementable requirement).
- Missing test coverage: No test exists for this requirement.
- Missing evidence: N/A
- Rationale: Interpretive, bibliographic, non-normative-by-design (explicitly marked informative/example), or document-self-referential statement. It does not describe a discrete, independently implementable system behavior.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: N/A

## EB-RID-004

- Specification / section: MCC-EB-001 / 23. Requirement Identifier Registry / 23.5 Registry Invariants
- Status: NOT_APPLICABLE
- Requirement: New category tags MUST NOT collide with prefixes already registered by another MCC specification.
- Existing implementation: None
- Missing implementation behavior: N/A (not an implementable requirement).
- Missing test coverage: No test exists for this requirement.
- Missing evidence: N/A
- Rationale: Interpretive, bibliographic, non-normative-by-design (explicitly marked informative/example), or document-self-referential statement. It does not describe a discrete, independently implementable system behavior.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: N/A

## EB-SEC-001

- Specification / section: MCC-EB-001 / 19. Security Considerations / 19.5 Security Invariants
- Status: PARTIAL
- Requirement: Bundle validation MUST assume an untrusted source.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: verify_bundle assumes an untrusted source, never treats content as authoritative before integrity verification, and verifies Ed25519 signatures against supplied trusted keys — the same threat model.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## EB-SEC-002

- Specification / section: MCC-EB-001 / 19. Security Considerations / 19.5 Security Invariants
- Status: PARTIAL
- Requirement: Tamper detection MUST rely solely on independently recomputed Digests.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: verify_bundle assumes an untrusted source, never treats content as authoritative before integrity verification, and verifies Ed25519 signatures against supplied trusted keys — the same threat model.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## EB-SEC-003

- Specification / section: MCC-EB-001 / 19. Security Considerations / 19.5 Security Invariants
- Status: PARTIAL
- Requirement: Bundles MUST NOT contain secrets or credentials.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: verify_bundle assumes an untrusted source, never treats content as authoritative before integrity verification, and verifies Ed25519 signatures against supplied trusted keys — the same threat model.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## EB-SEC-004

- Specification / section: MCC-EB-001 / 19. Security Considerations / 19.5 Security Invariants
- Status: PARTIAL
- Requirement: Sensitive underlying data MUST be redacted or hashed before inclusion as an Evidence Item.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: verify_bundle assumes an untrusted source, never treats content as authoritative before integrity verification, and verifies Ed25519 signatures against supplied trusted keys — the same threat model.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## EB-SEC-005

- Specification / section: MCC-EB-001 / 19. Security Considerations / 19.5 Security Invariants
- Status: PARTIAL
- Requirement: Security properties of a Bundle MUST be verifiable without trusting its origin.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: verify_bundle assumes an untrusted source, never treats content as authoritative before integrity verification, and verifies Ed25519 signatures against supplied trusted keys — the same threat model.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## EB-STR-001

- Specification / section: MCC-EB-001 / 10. Bundle Directory Structure / 10.5 Structure Invariants
- Status: PARTIAL
- Requirement: Every Evidence Bundle SHALL have exactly one Bundle Root.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_evidence exports/verifies bundles in directory and .tar.gz form with bundle-level metadata (bundle_id, created_at), semantically close to this section, but uses one manifest.json plus named artifact paths rather than this specification's separate Bundle Descriptor / Integrity Record / Provenance Record files, so the exact structural requirement is not met.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## EB-STR-002

- Specification / section: MCC-EB-001 / 10. Bundle Directory Structure / 10.5 Structure Invariants
- Status: PARTIAL
- Requirement: The Bundle Root SHALL contain exactly one Bundle Descriptor, one Integrity Record, one Provenance Record, and one Evidence Directory.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_evidence exports/verifies bundles in directory and .tar.gz form with bundle-level metadata (bundle_id, created_at), semantically close to this section, but uses one manifest.json plus named artifact paths rather than this specification's separate Bundle Descriptor / Integrity Record / Provenance Record files, so the exact structural requirement is not met.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## EB-STR-003

- Specification / section: MCC-EB-001 / 10. Bundle Directory Structure / 10.5 Structure Invariants
- Status: PARTIAL
- Requirement: Bundle directory structure SHALL be deterministic for equivalent certification inputs.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_evidence exports/verifies bundles in directory and .tar.gz form with bundle-level metadata (bundle_id, created_at), semantically close to this section, but uses one manifest.json plus named artifact paths rather than this specification's separate Bundle Descriptor / Integrity Record / Provenance Record files, so the exact structural requirement is not met.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## EB-STR-004

- Specification / section: MCC-EB-001 / 10. Bundle Directory Structure / 10.5 Structure Invariants
- Status: PARTIAL
- Requirement: Directory and file naming SHALL remain stable across regeneration of an equivalent Bundle.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_evidence exports/verifies bundles in directory and .tar.gz form with bundle-level metadata (bundle_id, created_at), semantically close to this section, but uses one manifest.json plus named artifact paths rather than this specification's separate Bundle Descriptor / Integrity Record / Provenance Record files, so the exact structural requirement is not met.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## EB-STR-005

- Specification / section: MCC-EB-001 / 10. Bundle Directory Structure / 10.5 Structure Invariants
- Status: PARTIAL
- Requirement: The directory form and archive form of a Bundle SHALL be structurally equivalent.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_evidence exports/verifies bundles in directory and .tar.gz form with bundle-level metadata (bundle_id, created_at), semantically close to this section, but uses one manifest.json plus named artifact paths rather than this specification's separate Bundle Descriptor / Integrity Record / Provenance Record files, so the exact structural requirement is not met.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## EB-VAL-001

- Specification / section: MCC-EB-001 / 16. Validation Rules / 16.7 Validation Invariants
- Status: PARTIAL
- Requirement: Validation MUST be fail-closed.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: verify_bundle implements fail-closed, ordered validation (structure, integrity, schema, signature) and never treats a partial result as valid, directly analogous to this section's requirements.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## EB-VAL-002

- Specification / section: MCC-EB-001 / 16. Validation Rules / 16.7 Validation Invariants
- Status: PARTIAL
- Requirement: Structural validation MUST precede metadata, integrity, and provenance validation.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: verify_bundle implements fail-closed, ordered validation (structure, integrity, schema, signature) and never treats a partial result as valid, directly analogous to this section's requirements.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## EB-VAL-003

- Specification / section: MCC-EB-001 / 16. Validation Rules / 16.7 Validation Invariants
- Status: PARTIAL
- Requirement: A Bundle failing any validation step MUST be rejected in its entirety.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: verify_bundle implements fail-closed, ordered validation (structure, integrity, schema, signature) and never treats a partial result as valid, directly analogous to this section's requirements.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## EB-VAL-004

- Specification / section: MCC-EB-001 / 16. Validation Rules / 16.7 Validation Invariants
- Status: PARTIAL
- Requirement: Validation MUST be reproducible: the same Bundle MUST produce the same validation result under the same specification version.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: verify_bundle implements fail-closed, ordered validation (structure, integrity, schema, signature) and never treats a partial result as valid, directly analogous to this section's requirements.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## EB-VAL-005

- Specification / section: MCC-EB-001 / 16. Validation Rules / 16.7 Validation Invariants
- Status: PARTIAL
- Requirement: Validation MUST NOT depend on trusting the environment that produced the Bundle.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: verify_bundle implements fail-closed, ordered validation (structure, integrity, schema, signature) and never treats a partial result as valid, directly analogous to this section's requirements.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## EB-VSN-001

- Specification / section: MCC-EB-001 / 17. Versioning Rules / 17.5 Versioning Invariants
- Status: PARTIAL
- Requirement: Every Bundle MUST declare an Evidence Bundle Schema Version.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: BUNDLE_SCHEMA_VERSION / SUPPORTED_SCHEMA_VERSIONS and the UNSUPPORTED_SCHEMA verification outcome implement the same reject-unrecognized-schema-version model this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## EB-VSN-002

- Specification / section: MCC-EB-001 / 17. Versioning Rules / 17.5 Versioning Invariants
- Status: PARTIAL
- Requirement: Schema Versions MUST be immutable once published.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: BUNDLE_SCHEMA_VERSION / SUPPORTED_SCHEMA_VERSIONS and the UNSUPPORTED_SCHEMA verification outcome implement the same reject-unrecognized-schema-version model this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## EB-VSN-003

- Specification / section: MCC-EB-001 / 17. Versioning Rules / 17.5 Versioning Invariants
- Status: PARTIAL
- Requirement: Schema Version and MCC-CP-001 specification version MUST be tracked independently.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: BUNDLE_SCHEMA_VERSION / SUPPORTED_SCHEMA_VERSIONS and the UNSUPPORTED_SCHEMA verification outcome implement the same reject-unrecognized-schema-version model this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## EB-VSN-004

- Specification / section: MCC-EB-001 / 17. Versioning Rules / 17.5 Versioning Invariants
- Status: PARTIAL
- Requirement: An unrecognized Schema Version MUST cause validation to fail.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: BUNDLE_SCHEMA_VERSION / SUPPORTED_SCHEMA_VERSIONS and the UNSUPPORTED_SCHEMA verification outcome implement the same reject-unrecognized-schema-version model this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-EB-001-1-STATUS-D01

- Specification / section: MCC-EB-001 / 1. Status
- Status: NOT_APPLICABLE
- Requirement: The key words MUST, MUST NOT, REQUIRED, SHALL, SHALL NOT, SHOULD, SHOULD NOT, RECOMMENDED, MAY and OPTIONAL in this specification are to be interpreted as described in RFC 2119 and RFC 8174.
- Existing implementation: None
- Missing implementation behavior: N/A (not an implementable requirement).
- Missing test coverage: No test exists for this requirement.
- Missing evidence: N/A
- Rationale: Interpretive, bibliographic, non-normative-by-design (explicitly marked informative/example), or document-self-referential statement. It does not describe a discrete, independently implementable system behavior.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: N/A

## MCC-EB-001-10-BUNDLE-DIRECTORY-STRUCTURE-D01

- Specification / section: MCC-EB-001 / 10. Bundle Directory Structure / 10.1 Bundle Root
- Status: PARTIAL
- Requirement: All Bundle contents SHALL be located within the Bundle Root.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_evidence exports/verifies bundles in directory and .tar.gz form with bundle-level metadata (bundle_id, created_at), semantically close to this section, but uses one manifest.json plus named artifact paths rather than this specification's separate Bundle Descriptor / Integrity Record / Provenance Record files, so the exact structural requirement is not met.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-EB-001-10-BUNDLE-DIRECTORY-STRUCTURE-D02

- Specification / section: MCC-EB-001 / 10. Bundle Directory Structure / 10.1 Bundle Root
- Status: PARTIAL
- Requirement: The Bundle Root SHALL NOT contain content that is not part of the Evidence Bundle.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_evidence exports/verifies bundles in directory and .tar.gz form with bundle-level metadata (bundle_id, created_at), semantically close to this section, but uses one manifest.json plus named artifact paths rather than this specification's separate Bundle Descriptor / Integrity Record / Provenance Record files, so the exact structural requirement is not met.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-EB-001-10-BUNDLE-DIRECTORY-STRUCTURE-D03

- Specification / section: MCC-EB-001 / 10. Bundle Directory Structure / 10.2 Top-Level Layout
- Status: PARTIAL
- Requirement: The Bundle Root SHALL contain, directly at its top level: - exactly one Bundle Descriptor; - exactly one Integrity Record; - exactly one Provenance Record; - exactly one Evidence Directory containing zero or more Evidence Items.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_evidence exports/verifies bundles in directory and .tar.gz form with bundle-level metadata (bundle_id, created_at), semantically close to this section, but uses one manifest.json plus named artifact paths rather than this specification's separate Bundle Descriptor / Integrity Record / Provenance Record files, so the exact structural requirement is not met.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-EB-001-10-BUNDLE-DIRECTORY-STRUCTURE-D04

- Specification / section: MCC-EB-001 / 10. Bundle Directory Structure / 10.3 Evidence Directory
- Status: PARTIAL
- Requirement: The Evidence Directory SHALL contain one entry per Evidence Item.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_evidence exports/verifies bundles in directory and .tar.gz form with bundle-level metadata (bundle_id, created_at), semantically close to this section, but uses one manifest.json plus named artifact paths rather than this specification's separate Bundle Descriptor / Integrity Record / Provenance Record files, so the exact structural requirement is not met.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-EB-001-10-BUNDLE-DIRECTORY-STRUCTURE-D05

- Specification / section: MCC-EB-001 / 10. Bundle Directory Structure / 10.3 Evidence Directory
- Status: PARTIAL
- Requirement: Each Evidence Item entry SHALL be uniquely named within the Evidence Directory.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_evidence exports/verifies bundles in directory and .tar.gz form with bundle-level metadata (bundle_id, created_at), semantically close to this section, but uses one manifest.json plus named artifact paths rather than this specification's separate Bundle Descriptor / Integrity Record / Provenance Record files, so the exact structural requirement is not met.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-EB-001-10-BUNDLE-DIRECTORY-STRUCTURE-D06

- Specification / section: MCC-EB-001 / 10. Bundle Directory Structure / 10.3 Evidence Directory
- Status: PARTIAL
- Requirement: The internal structure of an individual Evidence Item MAY vary by requirement type but MUST remain within its own entry in the Evidence Directory.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_evidence exports/verifies bundles in directory and .tar.gz form with bundle-level metadata (bundle_id, created_at), semantically close to this section, but uses one manifest.json plus named artifact paths rather than this specification's separate Bundle Descriptor / Integrity Record / Provenance Record files, so the exact structural requirement is not met.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-EB-001-10-BUNDLE-DIRECTORY-STRUCTURE-D07

- Specification / section: MCC-EB-001 / 10. Bundle Directory Structure / 10.4 Path Rules
- Status: PARTIAL
- Requirement: All paths within a Bundle SHALL be relative to the Bundle Root.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_evidence exports/verifies bundles in directory and .tar.gz form with bundle-level metadata (bundle_id, created_at), semantically close to this section, but uses one manifest.json plus named artifact paths rather than this specification's separate Bundle Descriptor / Integrity Record / Provenance Record files, so the exact structural requirement is not met.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-EB-001-10-BUNDLE-DIRECTORY-STRUCTURE-D08

- Specification / section: MCC-EB-001 / 10. Bundle Directory Structure / 10.4 Path Rules
- Status: PARTIAL
- Requirement: Path names within a Bundle SHALL NOT encode information that is not also present in the Bundle Descriptor, Integrity Record, or Provenance Record.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_evidence exports/verifies bundles in directory and .tar.gz form with bundle-level metadata (bundle_id, created_at), semantically close to this section, but uses one manifest.json plus named artifact paths rather than this specification's separate Bundle Descriptor / Integrity Record / Provenance Record files, so the exact structural requirement is not met.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-EB-001-10-BUNDLE-DIRECTORY-STRUCTURE-D09

- Specification / section: MCC-EB-001 / 10. Bundle Directory Structure / 10.4 Path Rules
- Status: PARTIAL
- Requirement: Path names SHALL be stable across regeneration of an equivalent Bundle, in support of EB-G2 (Reproducibility).
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_evidence exports/verifies bundles in directory and .tar.gz form with bundle-level metadata (bundle_id, created_at), semantically close to this section, but uses one manifest.json plus named artifact paths rather than this specification's separate Bundle Descriptor / Integrity Record / Provenance Record files, so the exact structural requirement is not met.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-EB-001-11-REQUIRED-FILES-D01

- Specification / section: MCC-EB-001 / 11. Required Files / 11.1 Bundle Descriptor
- Status: PARTIAL
- Requirement: The Bundle Descriptor MUST be present at the Bundle Root.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_evidence exports/verifies bundles in directory and .tar.gz form with bundle-level metadata (bundle_id, created_at), semantically close to this section, but uses one manifest.json plus named artifact paths rather than this specification's separate Bundle Descriptor / Integrity Record / Provenance Record files, so the exact structural requirement is not met.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-EB-001-11-REQUIRED-FILES-D02

- Specification / section: MCC-EB-001 / 11. Required Files / 11.1 Bundle Descriptor
- Status: PARTIAL
- Requirement: The Bundle Descriptor MUST declare: - the Evidence Bundle Schema Version; - a Bundle identifier unique to the certification run that produced it; - the specification version of MCC-CP-001 under which certification was performed.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_evidence exports/verifies bundles in directory and .tar.gz form with bundle-level metadata (bundle_id, created_at), semantically close to this section, but uses one manifest.json plus named artifact paths rather than this specification's separate Bundle Descriptor / Integrity Record / Provenance Record files, so the exact structural requirement is not met.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-EB-001-11-REQUIRED-FILES-D03

- Specification / section: MCC-EB-001 / 11. Required Files / 11.2 Integrity Record
- Status: PARTIAL
- Requirement: The Integrity Record MUST be present at the Bundle Root.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_evidence exports/verifies bundles in directory and .tar.gz form with bundle-level metadata (bundle_id, created_at), semantically close to this section, but uses one manifest.json plus named artifact paths rather than this specification's separate Bundle Descriptor / Integrity Record / Provenance Record files, so the exact structural requirement is not met.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-EB-001-11-REQUIRED-FILES-D04

- Specification / section: MCC-EB-001 / 11. Required Files / 11.2 Integrity Record
- Status: PARTIAL
- Requirement: The Integrity Record MUST enumerate a Digest for every file within the Bundle other than the Integrity Record itself.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_evidence exports/verifies bundles in directory and .tar.gz form with bundle-level metadata (bundle_id, created_at), semantically close to this section, but uses one manifest.json plus named artifact paths rather than this specification's separate Bundle Descriptor / Integrity Record / Provenance Record files, so the exact structural requirement is not met.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-EB-001-11-REQUIRED-FILES-D05

- Specification / section: MCC-EB-001 / 11. Required Files / 11.2 Integrity Record
- Status: PARTIAL
- Requirement: The Integrity Record MUST declare the hash algorithm used, as governed by Section 13.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_evidence exports/verifies bundles in directory and .tar.gz form with bundle-level metadata (bundle_id, created_at), semantically close to this section, but uses one manifest.json plus named artifact paths rather than this specification's separate Bundle Descriptor / Integrity Record / Provenance Record files, so the exact structural requirement is not met.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-EB-001-11-REQUIRED-FILES-D06

- Specification / section: MCC-EB-001 / 11. Required Files / 11.3 Provenance Record
- Status: PARTIAL
- Requirement: The Provenance Record MUST be present at the Bundle Root.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_evidence exports/verifies bundles in directory and .tar.gz form with bundle-level metadata (bundle_id, created_at), semantically close to this section, but uses one manifest.json plus named artifact paths rather than this specification's separate Bundle Descriptor / Integrity Record / Provenance Record files, so the exact structural requirement is not met.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-EB-001-11-REQUIRED-FILES-D07

- Specification / section: MCC-EB-001 / 11. Required Files / 11.3 Provenance Record
- Status: PARTIAL
- Requirement: The Provenance Record MUST satisfy the Provenance Requirements defined in Section 14.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_evidence exports/verifies bundles in directory and .tar.gz form with bundle-level metadata (bundle_id, created_at), semantically close to this section, but uses one manifest.json plus named artifact paths rather than this specification's separate Bundle Descriptor / Integrity Record / Provenance Record files, so the exact structural requirement is not met.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-EB-001-11-REQUIRED-FILES-D08

- Specification / section: MCC-EB-001 / 11. Required Files / 11.4 Evidence Items
- Status: PARTIAL
- Requirement: Where Evidence Items are present, each MUST be referenced by at least one entry in the Integrity Record.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_evidence exports/verifies bundles in directory and .tar.gz form with bundle-level metadata (bundle_id, created_at), semantically close to this section, but uses one manifest.json plus named artifact paths rather than this specification's separate Bundle Descriptor / Integrity Record / Provenance Record files, so the exact structural requirement is not met.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-EB-001-12-REQUIRED-METADATA-D01

- Specification / section: MCC-EB-001 / 12. Required Metadata / 12.1 Bundle-Level Metadata
- Status: PARTIAL
- Requirement: The Bundle Descriptor MUST include: - Bundle identifier; - Evidence Bundle Schema Version; - MCC-CP-001 specification version referenced; - generation timestamp; - reference to the associated Certification Subject identifier, as defined by MCC-CP-001, Section 7.2.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_evidence exports/verifies bundles in directory and .tar.gz form with bundle-level metadata (bundle_id, created_at), semantically close to this section, but uses one manifest.json plus named artifact paths rather than this specification's separate Bundle Descriptor / Integrity Record / Provenance Record files, so the exact structural requirement is not met.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-EB-001-12-REQUIRED-METADATA-D02

- Specification / section: MCC-EB-001 / 12. Required Metadata / 12.2 Evidence Item Metadata
- Status: PARTIAL
- Requirement: Each Evidence Item MUST be associated with metadata identifying: - the Certification Requirement identifier it corresponds to, as defined by MCC-CP-001, Section 12.2; - the verification method applied, as defined by MCC-CP-001, Section 12.4; - the outcome produced (PASS, FAIL, or NOT APPLICABLE), consistent with MCC-CP-001, Section 10.4.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_evidence exports/verifies bundles in directory and .tar.gz form with bundle-level metadata (bundle_id, created_at), semantically close to this section, but uses one manifest.json plus named artifact paths rather than this specification's separate Bundle Descriptor / Integrity Record / Provenance Record files, so the exact structural requirement is not met.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-EB-001-12-REQUIRED-METADATA-D03

- Specification / section: MCC-EB-001 / 12. Required Metadata / 12.3 Metadata Integrity
- Status: PARTIAL
- Requirement: Required metadata fields MUST be included in the data covered by the Integrity Record.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_evidence exports/verifies bundles in directory and .tar.gz form with bundle-level metadata (bundle_id, created_at), semantically close to this section, but uses one manifest.json plus named artifact paths rather than this specification's separate Bundle Descriptor / Integrity Record / Provenance Record files, so the exact structural requirement is not met.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-EB-001-12-REQUIRED-METADATA-D04

- Specification / section: MCC-EB-001 / 12. Required Metadata / 12.3 Metadata Integrity
- Status: PARTIAL
- Requirement: Metadata fields MUST NOT be modified after Bundle generation without invalidating the Bundle's integrity under Section 13.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_evidence exports/verifies bundles in directory and .tar.gz form with bundle-level metadata (bundle_id, created_at), semantically close to this section, but uses one manifest.json plus named artifact paths rather than this specification's separate Bundle Descriptor / Integrity Record / Provenance Record files, so the exact structural requirement is not met.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-EB-001-13-HASH-AND-INTEGRITY-MODEL-D01

- Specification / section: MCC-EB-001 / 13. Hash and Integrity Model / 13.2 Canonical Form
- Status: PARTIAL
- Requirement: Data covered by a Digest MUST first be reduced to a Canonical Form.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_evidence/verify.py recomputes SHA-256 digests over canonical form and rejects any bundle with a mismatched digest as tampered, with dedicated tamper tests — behaviorally equivalent to this requirement, though bound to the mcc-evidence/1 schema rather than this specification's Bundle.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-EB-001-13-HASH-AND-INTEGRITY-MODEL-D02

- Specification / section: MCC-EB-001 / 13. Hash and Integrity Model / 13.2 Canonical Form
- Status: PARTIAL
- Requirement: Canonical Form MUST be deterministic: identical logical content MUST always produce an identical Canonical Form, regardless of the environment or tooling that produced it.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_evidence/verify.py recomputes SHA-256 digests over canonical form and rejects any bundle with a mismatched digest as tampered, with dedicated tamper tests — behaviorally equivalent to this requirement, though bound to the mcc-evidence/1 schema rather than this specification's Bundle.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-EB-001-13-HASH-AND-INTEGRITY-MODEL-D03

- Specification / section: MCC-EB-001 / 13. Hash and Integrity Model / 13.3 Hash Algorithm
- Status: PARTIAL
- Requirement: The Integrity Record MUST declare the cryptographic hash algorithm used to compute its Digests.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_evidence/verify.py recomputes SHA-256 digests over canonical form and rejects any bundle with a mismatched digest as tampered, with dedicated tamper tests — behaviorally equivalent to this requirement, though bound to the mcc-evidence/1 schema rather than this specification's Bundle.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-EB-001-13-HASH-AND-INTEGRITY-MODEL-D04

- Specification / section: MCC-EB-001 / 13. Hash and Integrity Model / 13.3 Hash Algorithm
- Status: PARTIAL
- Requirement: The declared hash algorithm MUST be a collision-resistant cryptographic hash function.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_evidence/verify.py recomputes SHA-256 digests over canonical form and rejects any bundle with a mismatched digest as tampered, with dedicated tamper tests — behaviorally equivalent to this requirement, though bound to the mcc-evidence/1 schema rather than this specification's Bundle.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-EB-001-13-HASH-AND-INTEGRITY-MODEL-D05

- Specification / section: MCC-EB-001 / 13. Hash and Integrity Model / 13.3 Hash Algorithm
- Status: PARTIAL
- Requirement: A Bundle MUST NOT be considered valid if it declares a hash algorithm that is not collision-resistant.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_evidence/verify.py recomputes SHA-256 digests over canonical form and rejects any bundle with a mismatched digest as tampered, with dedicated tamper tests — behaviorally equivalent to this requirement, though bound to the mcc-evidence/1 schema rather than this specification's Bundle.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-EB-001-13-HASH-AND-INTEGRITY-MODEL-D06

- Specification / section: MCC-EB-001 / 13. Hash and Integrity Model / 13.4 Digest Coverage
- Status: PARTIAL
- Requirement: Every file within the Bundle Root, other than the Integrity Record itself, MUST have a corresponding Digest entry in the Integrity Record.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_evidence/verify.py recomputes SHA-256 digests over canonical form and rejects any bundle with a mismatched digest as tampered, with dedicated tamper tests — behaviorally equivalent to this requirement, though bound to the mcc-evidence/1 schema rather than this specification's Bundle.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-EB-001-13-HASH-AND-INTEGRITY-MODEL-D07

- Specification / section: MCC-EB-001 / 13. Hash and Integrity Model / 13.4 Digest Coverage
- Status: PARTIAL
- Requirement: A Digest MUST cover the complete Canonical Form of the file it corresponds to.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_evidence/verify.py recomputes SHA-256 digests over canonical form and rejects any bundle with a mismatched digest as tampered, with dedicated tamper tests — behaviorally equivalent to this requirement, though bound to the mcc-evidence/1 schema rather than this specification's Bundle.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-EB-001-13-HASH-AND-INTEGRITY-MODEL-D08

- Specification / section: MCC-EB-001 / 13. Hash and Integrity Model / 13.5 Integrity Verification
- Status: PARTIAL
- Requirement: A validator MUST recompute the Digest of every file covered by the Integrity Record and compare it against the declared value.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_evidence/verify.py recomputes SHA-256 digests over canonical form and rejects any bundle with a mismatched digest as tampered, with dedicated tamper tests — behaviorally equivalent to this requirement, though bound to the mcc-evidence/1 schema rather than this specification's Bundle.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-EB-001-13-HASH-AND-INTEGRITY-MODEL-D09

- Specification / section: MCC-EB-001 / 13. Hash and Integrity Model / 13.5 Integrity Verification
- Status: PARTIAL
- Requirement: A Bundle SHALL be considered tampered if any recomputed Digest does not match its declared value.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_evidence/verify.py recomputes SHA-256 digests over canonical form and rejects any bundle with a mismatched digest as tampered, with dedicated tamper tests — behaviorally equivalent to this requirement, though bound to the mcc-evidence/1 schema rather than this specification's Bundle.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-EB-001-13-HASH-AND-INTEGRITY-MODEL-D10

- Specification / section: MCC-EB-001 / 13. Hash and Integrity Model / 13.5 Integrity Verification
- Status: PARTIAL
- Requirement: A tampered Bundle MUST NOT be treated as valid evidence.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_evidence/verify.py recomputes SHA-256 digests over canonical form and rejects any bundle with a mismatched digest as tampered, with dedicated tamper tests — behaviorally equivalent to this requirement, though bound to the mcc-evidence/1 schema rather than this specification's Bundle.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-EB-001-14-PROVENANCE-REQUIREMENTS-D01

- Specification / section: MCC-EB-001 / 14. Provenance Requirements / 14.1 Purpose
- Status: PARTIAL
- Requirement: Provenance Requirements define what an Evidence Bundle MUST record about its own origin, so that a validator can determine where a Bundle came from without relying on unverifiable external claims.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: EvidenceInput (export.py) records the originating governance run and correlation id, a narrower provenance model than this section's full requirement set (no explicit prior-bundle chain-of-custody reference field).
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-EB-001-14-PROVENANCE-REQUIREMENTS-D02

- Specification / section: MCC-EB-001 / 14. Provenance Requirements / 14.2 Required Provenance Fields
- Status: PARTIAL
- Requirement: The Provenance Record MUST identify: - the certification run that produced the Bundle; - the Certification Pipeline stage, as defined by MCC-CP-001, Section 9, that generated the Bundle; - the specification version of MCC-CP-001 in effect at generation time; - the Evidence Bundle Schema Version in effect at generation time.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: EvidenceInput (export.py) records the originating governance run and correlation id, a narrower provenance model than this section's full requirement set (no explicit prior-bundle chain-of-custody reference field).
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-EB-001-14-PROVENANCE-REQUIREMENTS-D03

- Specification / section: MCC-EB-001 / 14. Provenance Requirements / 14.3 Chain of Custody
- Status: PARTIAL
- Requirement: Where an Evidence Bundle is derived from, or supersedes, a prior Bundle, the Provenance Record MUST reference the prior Bundle's identifier.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: EvidenceInput (export.py) records the originating governance run and correlation id, a narrower provenance model than this section's full requirement set (no explicit prior-bundle chain-of-custody reference field).
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-EB-001-14-PROVENANCE-REQUIREMENTS-D04

- Specification / section: MCC-EB-001 / 14. Provenance Requirements / 14.3 Chain of Custody
- Status: PARTIAL
- Requirement: Provenance references MUST NOT be circular.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: EvidenceInput (export.py) records the originating governance run and correlation id, a narrower provenance model than this section's full requirement set (no explicit prior-bundle chain-of-custody reference field).
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-EB-001-15-REPRODUCIBILITY-REQUIREMENTS-D01

- Specification / section: MCC-EB-001 / 15. Reproducibility Requirements / 15.2 Deterministic Generation
- Status: PARTIAL
- Requirement: Given identical certification inputs and an identical specification version, Bundle generation MUST produce a Bundle whose Digests are identical to a previously generated Bundle for the same certification run.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: schema.py explicitly documents and excludes non-deterministic fields (created_at, bundle_id) from equivalence comparison — the same determinism-with-declared-exceptions model this section requires — but for the mcc-evidence/1 schema, not this specification's Bundle.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-EB-001-15-REPRODUCIBILITY-REQUIREMENTS-D02

- Specification / section: MCC-EB-001 / 15. Reproducibility Requirements / 15.3 Prohibited Non-Determinism
- Status: PARTIAL
- Requirement: Canonical Form and Digest computation MUST NOT depend on: - wall-clock time, other than an explicitly declared generation timestamp field that is itself excluded from, or deterministically normalized within, the Canonical Form used for reproducibility comparison; - random or non-deterministic identifiers not derived from the certification run itself; - the order in which Evidence Items were internally processed, where that order is not otherwise normatively significant.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: schema.py explicitly documents and excludes non-deterministic fields (created_at, bundle_id) from equivalence comparison — the same determinism-with-declared-exceptions model this section requires — but for the mcc-evidence/1 schema, not this specification's Bundle.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-EB-001-15-REPRODUCIBILITY-REQUIREMENTS-D03

- Specification / section: MCC-EB-001 / 15. Reproducibility Requirements / 15.4 Regeneration Equivalence
- Status: PARTIAL
- Requirement: Two Bundles produced from identical certification inputs and an identical specification version SHALL be considered equivalent if their Integrity Records match after excluding fields explicitly permitted to vary under Section 15.3.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: schema.py explicitly documents and excludes non-deterministic fields (created_at, bundle_id) from equivalence comparison — the same determinism-with-declared-exceptions model this section requires — but for the mcc-evidence/1 schema, not this specification's Bundle.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-EB-001-16-VALIDATION-RULES-D01

- Specification / section: MCC-EB-001 / 16. Validation Rules / 16.1 Purpose
- Status: PARTIAL
- Requirement: Validation Rules define the normative procedure and criteria a validator MUST apply to determine whether an Evidence Bundle is valid.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: verify_bundle implements fail-closed, ordered validation (structure, integrity, schema, signature) and never treats a partial result as valid, directly analogous to this section's requirements.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-EB-001-16-VALIDATION-RULES-D02

- Specification / section: MCC-EB-001 / 16. Validation Rules / 16.2 Structural Validation
- Status: PARTIAL
- Requirement: A validator MUST verify that the Bundle conforms to the Bundle Directory Structure defined in Section 10 and contains all Required Files defined in Section 11.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: verify_bundle implements fail-closed, ordered validation (structure, integrity, schema, signature) and never treats a partial result as valid, directly analogous to this section's requirements.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-EB-001-16-VALIDATION-RULES-D03

- Specification / section: MCC-EB-001 / 16. Validation Rules / 16.2 Structural Validation
- Status: PARTIAL
- Requirement: A Bundle that fails structural validation MUST be rejected without further processing.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: verify_bundle implements fail-closed, ordered validation (structure, integrity, schema, signature) and never treats a partial result as valid, directly analogous to this section's requirements.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-EB-001-16-VALIDATION-RULES-D04

- Specification / section: MCC-EB-001 / 16. Validation Rules / 16.3 Metadata Validation
- Status: PARTIAL
- Requirement: A validator MUST verify that all Required Metadata defined in Section 12 is present and internally consistent (for example, that referenced Certification Requirement identifiers are well-formed).
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: verify_bundle implements fail-closed, ordered validation (structure, integrity, schema, signature) and never treats a partial result as valid, directly analogous to this section's requirements.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-EB-001-16-VALIDATION-RULES-D05

- Specification / section: MCC-EB-001 / 16. Validation Rules / 16.4 Integrity Validation
- Status: PARTIAL
- Requirement: A validator MUST perform Integrity Verification as defined in Section 13.5.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: verify_bundle implements fail-closed, ordered validation (structure, integrity, schema, signature) and never treats a partial result as valid, directly analogous to this section's requirements.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-EB-001-16-VALIDATION-RULES-D06

- Specification / section: MCC-EB-001 / 16. Validation Rules / 16.4 Integrity Validation
- Status: PARTIAL
- Requirement: A Bundle that fails integrity validation MUST be rejected.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: verify_bundle implements fail-closed, ordered validation (structure, integrity, schema, signature) and never treats a partial result as valid, directly analogous to this section's requirements.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-EB-001-16-VALIDATION-RULES-D07

- Specification / section: MCC-EB-001 / 16. Validation Rules / 16.5 Provenance Validation
- Status: PARTIAL
- Requirement: A validator MUST verify that Provenance Requirements defined in Section 14 are satisfied, including the absence of circular references.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: verify_bundle implements fail-closed, ordered validation (structure, integrity, schema, signature) and never treats a partial result as valid, directly analogous to this section's requirements.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-EB-001-16-VALIDATION-RULES-D08

- Specification / section: MCC-EB-001 / 16. Validation Rules / 16.6 Fail-Closed Validation
- Status: PARTIAL
- Requirement: Validation SHALL be fail-closed: a Bundle MUST be treated as invalid unless every applicable validation step in this section succeeds.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: verify_bundle implements fail-closed, ordered validation (structure, integrity, schema, signature) and never treats a partial result as valid, directly analogous to this section's requirements.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-EB-001-16-VALIDATION-RULES-D09

- Specification / section: MCC-EB-001 / 16. Validation Rules / 16.6 Fail-Closed Validation
- Status: PARTIAL
- Requirement: Partial or inconclusive validation results MUST NOT be treated as valid.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: verify_bundle implements fail-closed, ordered validation (structure, integrity, schema, signature) and never treats a partial result as valid, directly analogous to this section's requirements.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-EB-001-17-VERSIONING-RULES-D01

- Specification / section: MCC-EB-001 / 17. Versioning Rules / 17.2 Schema Version Declaration
- Status: PARTIAL
- Requirement: Every Bundle MUST declare its Evidence Bundle Schema Version in the Bundle Descriptor.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: BUNDLE_SCHEMA_VERSION / SUPPORTED_SCHEMA_VERSIONS and the UNSUPPORTED_SCHEMA verification outcome implement the same reject-unrecognized-schema-version model this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-EB-001-17-VERSIONING-RULES-D02

- Specification / section: MCC-EB-001 / 17. Versioning Rules / 17.2 Schema Version Declaration
- Status: PARTIAL
- Requirement: The Schema Version MUST be immutable once assigned to a published revision of this specification.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: BUNDLE_SCHEMA_VERSION / SUPPORTED_SCHEMA_VERSIONS and the UNSUPPORTED_SCHEMA verification outcome implement the same reject-unrecognized-schema-version model this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-EB-001-17-VERSIONING-RULES-D03

- Specification / section: MCC-EB-001 / 17. Versioning Rules / 17.3 Schema Version Scope
- Status: PARTIAL
- Requirement: The Evidence Bundle Schema Version is distinct from, and SHALL NOT be conflated with, the MCC-CP-001 specification version referenced by a Bundle's Provenance Record.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: BUNDLE_SCHEMA_VERSION / SUPPORTED_SCHEMA_VERSIONS and the UNSUPPORTED_SCHEMA verification outcome implement the same reject-unrecognized-schema-version model this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-EB-001-17-VERSIONING-RULES-D04

- Specification / section: MCC-EB-001 / 17. Versioning Rules / 17.4 Version Evolution
- Status: PARTIAL
- Requirement: A validator MUST reject a Bundle declaring a Schema Version it does not recognize, consistent with Section 16.6.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: BUNDLE_SCHEMA_VERSION / SUPPORTED_SCHEMA_VERSIONS and the UNSUPPORTED_SCHEMA verification outcome implement the same reject-unrecognized-schema-version model this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-EB-001-18-COMPATIBILITY-REQUIREMENTS-D01

- Specification / section: MCC-EB-001 / 18. Compatibility Requirements / 18.3 Forward Compatibility
- Status: PARTIAL
- Requirement: A validator MUST NOT assume forward compatibility with a Schema Version it does not recognize.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: BUNDLE_SCHEMA_VERSION / SUPPORTED_SCHEMA_VERSIONS and the UNSUPPORTED_SCHEMA verification outcome implement the same reject-unrecognized-schema-version model this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-EB-001-18-COMPATIBILITY-REQUIREMENTS-D02

- Specification / section: MCC-EB-001 / 18. Compatibility Requirements / 18.3 Forward Compatibility
- Status: PARTIAL
- Requirement: An unrecognized Schema Version MUST be treated per Section 17.4 and Section 16.6, not silently accepted.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: BUNDLE_SCHEMA_VERSION / SUPPORTED_SCHEMA_VERSIONS and the UNSUPPORTED_SCHEMA verification outcome implement the same reject-unrecognized-schema-version model this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-EB-001-18-COMPATIBILITY-REQUIREMENTS-D03

- Specification / section: MCC-EB-001 / 18. Compatibility Requirements / 18.4 Breaking Changes
- Status: PARTIAL
- Requirement: A revision of this specification that alters the Bundle Directory Structure, Required Files, Required Metadata, or Hash and Integrity Model in a way that invalidates previously valid Bundles MUST introduce a new Schema Version and MUST document the change as breaking.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: BUNDLE_SCHEMA_VERSION / SUPPORTED_SCHEMA_VERSIONS and the UNSUPPORTED_SCHEMA verification outcome implement the same reject-unrecognized-schema-version model this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-EB-001-19-SECURITY-CONSIDERATIONS-D01

- Specification / section: MCC-EB-001 / 19. Security Considerations / 19.2 Threat Model
- Status: PARTIAL
- Requirement: Validation of an Evidence Bundle MUST assume: - the Bundle MAY originate from an untrusted or compromised source; - the Bundle MAY have been partially or fully tampered with; - the environment that produced the Bundle MUST NOT be trusted implicitly.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: verify_bundle assumes an untrusted source, never treats content as authoritative before integrity verification, and verifies Ed25519 signatures against supplied trusted keys — the same threat model.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-EB-001-19-SECURITY-CONSIDERATIONS-D02

- Specification / section: MCC-EB-001 / 19. Security Considerations / 19.3 Tamper Detection
- Status: PARTIAL
- Requirement: A validator MUST NOT treat any Bundle content as authoritative prior to successful Integrity Verification.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: verify_bundle assumes an untrusted source, never treats content as authoritative before integrity verification, and verifies Ed25519 signatures against supplied trusted keys — the same threat model.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-EB-001-19-SECURITY-CONSIDERATIONS-D03

- Specification / section: MCC-EB-001 / 19. Security Considerations / 19.4 Sensitive Data
- Status: PARTIAL
- Requirement: An Evidence Bundle MUST NOT include secrets, credentials, or other sensitive material not required to demonstrate conformance to a Certification Requirement.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: verify_bundle assumes an untrusted source, never treats content as authoritative before integrity verification, and verifies Ed25519 signatures against supplied trusted keys — the same threat model.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-EB-001-19-SECURITY-CONSIDERATIONS-D04

- Specification / section: MCC-EB-001 / 19. Security Considerations / 19.4 Sensitive Data
- Status: PARTIAL
- Requirement: Where underlying certification inputs contain sensitive material, Evidence Items MUST reference redacted or hashed representations rather than raw sensitive values.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: verify_bundle assumes an untrusted source, never treats content as authoritative before integrity verification, and verifies Ed25519 signatures against supplied trusted keys — the same threat model.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-EB-001-2-ABSTRACT-D01

- Specification / section: MCC-EB-001 / 2. Abstract
- Status: NOT_APPLICABLE
- Requirement: Evidence Bundles SHALL remain framework-neutral and implementation-independent, and SHALL be independently verifiable without trusting the environment that produced them.
- Existing implementation: None
- Missing implementation behavior: N/A (not an implementable requirement).
- Missing test coverage: No test exists for this requirement.
- Missing evidence: N/A
- Rationale: Interpretive, bibliographic, non-normative-by-design (explicitly marked informative/example), or document-self-referential statement. It does not describe a discrete, independently implementable system behavior.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: N/A

## MCC-EB-001-20-EXTENSION-MODEL-D01

- Specification / section: MCC-EB-001 / 20. Extension Model / 20.2 Extension Points
- Status: GAP
- Requirement: Extensions MUST be declared in the Bundle Descriptor.
- Existing implementation: None
- Missing implementation behavior: Full requirement not implemented.
- Missing test coverage: No test exists for this requirement.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: No extension-declaration mechanism (a way to mark additional fields as explicit, non-breaking extensions to a committed schema) was found anywhere in this repository for any artifact.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-EB-001-20-EXTENSION-MODEL-D02

- Specification / section: MCC-EB-001 / 20. Extension Model / 20.3 Extension Constraints
- Status: GAP
- Requirement: An extension MUST NOT alter the meaning of any Required File or Required Metadata defined by this specification.
- Existing implementation: None
- Missing implementation behavior: Full requirement not implemented.
- Missing test coverage: No test exists for this requirement.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: No extension-declaration mechanism (a way to mark additional fields as explicit, non-breaking extensions to a committed schema) was found anywhere in this repository for any artifact.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-EB-001-20-EXTENSION-MODEL-D03

- Specification / section: MCC-EB-001 / 20. Extension Model / 20.3 Extension Constraints
- Status: GAP
- Requirement: A validator that does not recognize a declared extension MUST ignore that extension's content without failing validation, provided all other validation rules in Section 16 are satisfied.
- Existing implementation: None
- Missing implementation behavior: Full requirement not implemented.
- Missing test coverage: No test exists for this requirement.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: No extension-declaration mechanism (a way to mark additional fields as explicit, non-breaking extensions to a committed schema) was found anywhere in this repository for any artifact.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-EB-001-20-EXTENSION-MODEL-D04

- Specification / section: MCC-EB-001 / 20. Extension Model / 20.3 Extension Constraints
- Status: GAP
- Requirement: An extension MUST be covered by the Integrity Record like any other Bundle content.
- Existing implementation: None
- Missing implementation behavior: Full requirement not implemented.
- Missing test coverage: No test exists for this requirement.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: No extension-declaration mechanism (a way to mark additional fields as explicit, non-breaking extensions to a committed schema) was found anywhere in this repository for any artifact.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-EB-001-22-CONFORMANCE-REQUIREMENTS-D01

- Specification / section: MCC-EB-001 / 22. Conformance Requirements / 22.2 Conforming Bundle Producer
- Status: GAP
- Requirement: A conforming Bundle producer MUST generate Bundles satisfying Sections 10 through 15 of this specification for the Schema Version it declares.
- Existing implementation: None
- Missing implementation behavior: Full requirement not implemented.
- Missing test coverage: No test exists for this requirement.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: No producer/validator conformance-declaration mechanism specific to this specification's Bundle Schema Version was found.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-EB-001-22-CONFORMANCE-REQUIREMENTS-D02

- Specification / section: MCC-EB-001 / 22. Conformance Requirements / 22.2 Conforming Bundle Producer
- Status: GAP
- Requirement: A conforming Bundle producer MUST NOT emit a Bundle that fails validation under Section 16 against its own declared Schema Version.
- Existing implementation: None
- Missing implementation behavior: Full requirement not implemented.
- Missing test coverage: No test exists for this requirement.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: No producer/validator conformance-declaration mechanism specific to this specification's Bundle Schema Version was found.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-EB-001-22-CONFORMANCE-REQUIREMENTS-D03

- Specification / section: MCC-EB-001 / 22. Conformance Requirements / 22.3 Conforming Bundle Validator
- Status: GAP
- Requirement: A conforming Bundle validator MUST implement the validation procedure defined in Section 16 in full, without omitting any applicable step.
- Existing implementation: None
- Missing implementation behavior: Full requirement not implemented.
- Missing test coverage: No test exists for this requirement.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: No producer/validator conformance-declaration mechanism specific to this specification's Bundle Schema Version was found.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-EB-001-22-CONFORMANCE-REQUIREMENTS-D04

- Specification / section: MCC-EB-001 / 22. Conformance Requirements / 22.3 Conforming Bundle Validator
- Status: GAP
- Requirement: A conforming Bundle validator MUST reject a Bundle whenever any applicable validation step fails.
- Existing implementation: None
- Missing implementation behavior: Full requirement not implemented.
- Missing test coverage: No test exists for this requirement.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: No producer/validator conformance-declaration mechanism specific to this specification's Bundle Schema Version was found.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-EB-001-22-CONFORMANCE-REQUIREMENTS-D05

- Specification / section: MCC-EB-001 / 22. Conformance Requirements / 22.4 Conformance Independence
- Status: GAP
- Requirement: Conformance to this specification SHALL be evaluated independently of any specific programming language, framework, or certification tooling implementation.
- Existing implementation: None
- Missing implementation behavior: Full requirement not implemented.
- Missing test coverage: No test exists for this requirement.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: No producer/validator conformance-declaration mechanism specific to this specification's Bundle Schema Version was found.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-EB-001-23-REQUIREMENT-IDENTIFIER-REGISTRY-D01

- Specification / section: MCC-EB-001 / 23. Requirement Identifier Registry / 23.2 Namespace Convention
- Status: NOT_APPLICABLE
- Requirement: Every normative requirement identifier defined by this specification SHALL be prefixed with `EB-`, followed by a section-scoped category tag, followed by a three-digit sequence number.
- Existing implementation: None
- Missing implementation behavior: N/A (not an implementable requirement).
- Missing test coverage: No test exists for this requirement.
- Missing evidence: N/A
- Rationale: Interpretive, bibliographic, non-normative-by-design (explicitly marked informative/example), or document-self-referential statement. It does not describe a discrete, independently implementable system behavior.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: N/A

## MCC-EB-001-23-REQUIREMENT-IDENTIFIER-REGISTRY-D02

- Specification / section: MCC-EB-001 / 23. Requirement Identifier Registry / 23.4 Registry Requirements
- Status: NOT_APPLICABLE
- Requirement: Requirement identifiers under this specification's `EB-` namespace SHALL be globally unique.
- Existing implementation: None
- Missing implementation behavior: N/A (not an implementable requirement).
- Missing test coverage: No test exists for this requirement.
- Missing evidence: N/A
- Rationale: Interpretive, bibliographic, non-normative-by-design (explicitly marked informative/example), or document-self-referential statement. It does not describe a discrete, independently implementable system behavior.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: N/A

## MCC-EB-001-23-REQUIREMENT-IDENTIFIER-REGISTRY-D03

- Specification / section: MCC-EB-001 / 23. Requirement Identifier Registry / 23.4 Registry Requirements
- Status: NOT_APPLICABLE
- Requirement: A future revision of this specification MUST NOT reuse a retired identifier for a different requirement.
- Existing implementation: None
- Missing implementation behavior: N/A (not an implementable requirement).
- Missing test coverage: No test exists for this requirement.
- Missing evidence: N/A
- Rationale: Interpretive, bibliographic, non-normative-by-design (explicitly marked informative/example), or document-self-referential statement. It does not describe a discrete, independently implementable system behavior.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: N/A

## MCC-EB-001-23-REQUIREMENT-IDENTIFIER-REGISTRY-D04

- Specification / section: MCC-EB-001 / 23. Requirement Identifier Registry / 23.4 Registry Requirements
- Status: NOT_APPLICABLE
- Requirement: A future revision of this specification MUST NOT introduce a new category tag that collides with a prefix already registered by MCC-CP-001 or by this specification.
- Existing implementation: None
- Missing implementation behavior: N/A (not an implementable requirement).
- Missing test coverage: No test exists for this requirement.
- Missing evidence: N/A
- Rationale: Interpretive, bibliographic, non-normative-by-design (explicitly marked informative/example), or document-self-referential statement. It does not describe a discrete, independently implementable system behavior.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: N/A

## MCC-EB-001-5-GOALS-D01

- Specification / section: MCC-EB-001 / 5. Goals / EB-G1. Framework Neutrality
- Status: GAP
- Requirement: The Evidence Bundle format MUST remain independent of any particular framework, programming language, or certification tooling implementation.
- Existing implementation: None
- Missing implementation behavior: Full requirement not implemented.
- Missing test coverage: No test exists for this requirement.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: No implementation behavior, automated test, or evidence mechanism semantically equivalent to this requirement (category: '5. Goals') was found anywhere under src/, tests/, certifications/, evidence/, schemas/, docs/, or CI workflows, after the broader semantic-mapping investigation described in this module's docstring — not merely a lexical search for this specification's exact terminology.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-EB-001-5-GOALS-D02

- Specification / section: MCC-EB-001 / 5. Goals / EB-G2. Reproducibility
- Status: GAP
- Requirement: An Evidence Bundle MUST be reproducible: regenerating a Bundle from the same certification inputs MUST yield a Bundle that is verifiably equivalent under this specification's integrity model.
- Existing implementation: None
- Missing implementation behavior: Full requirement not implemented.
- Missing test coverage: No test exists for this requirement.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: No implementation behavior, automated test, or evidence mechanism semantically equivalent to this requirement (category: '5. Goals') was found anywhere under src/, tests/, certifications/, evidence/, schemas/, docs/, or CI workflows, after the broader semantic-mapping investigation described in this module's docstring — not merely a lexical search for this specification's exact terminology.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-EB-001-5-GOALS-D03

- Specification / section: MCC-EB-001 / 5. Goals / EB-G3. Independent Verifiability
- Status: GAP
- Requirement: A third party MUST be able to validate an Evidence Bundle using only the Bundle itself and this specification, without trusting the environment that produced it.
- Existing implementation: None
- Missing implementation behavior: Full requirement not implemented.
- Missing test coverage: No test exists for this requirement.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: No implementation behavior, automated test, or evidence mechanism semantically equivalent to this requirement (category: '5. Goals') was found anywhere under src/, tests/, certifications/, evidence/, schemas/, docs/, or CI workflows, after the broader semantic-mapping investigation described in this module's docstring — not merely a lexical search for this specification's exact terminology.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-EB-001-5-GOALS-D04

- Specification / section: MCC-EB-001 / 5. Goals / EB-G4. Structural Determinism
- Status: GAP
- Requirement: The Bundle Directory Structure and Required Files MUST be deterministic given the same certification inputs and the same specification version.
- Existing implementation: None
- Missing implementation behavior: Full requirement not implemented.
- Missing test coverage: No test exists for this requirement.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: No implementation behavior, automated test, or evidence mechanism semantically equivalent to this requirement (category: '5. Goals') was found anywhere under src/, tests/, certifications/, evidence/, schemas/, docs/, or CI workflows, after the broader semantic-mapping investigation described in this module's docstring — not merely a lexical search for this specification's exact terminology.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-EB-001-6-NON-GOALS-D01

- Specification / section: MCC-EB-001 / 6. Non-Goals
- Status: GAP
- Requirement: This specification SHALL NOT: - define how certification decisions are reached (defined by MCC-CP-001); - define the Certification Manifest or Technical Certificate formats; - mandate a specific programming language, library, or SDK for producing or validating Bundles; - mandate a specific storage backend, transport protocol, or distribution channel; - define business-specific or domain-specific evidence content; - define runtime governance behavior (ALLOW, DENY, ESCALATE, CONSTRAIN), which belongs exclusively to MCC-Core runtime governance.
- Existing implementation: None
- Missing implementation behavior: Full requirement not implemented.
- Missing test coverage: No test exists for this requirement.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: No implementation behavior, automated test, or evidence mechanism semantically equivalent to this requirement (category: '6. Non-Goals') was found anywhere under src/, tests/, certifications/, evidence/, schemas/, docs/, or CI workflows, after the broader semantic-mapping investigation described in this module's docstring — not merely a lexical search for this specification's exact terminology.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-EB-001-9-EVIDENCE-BUNDLE-OVERVIEW-D01

- Specification / section: MCC-EB-001 / 9. Evidence Bundle Overview / 9.1 Role in Certification
- Status: PARTIAL
- Requirement: An Evidence Bundle is produced during the Evidence Generation stage of the Certification Pipeline defined in MCC-CP-001, Section 9.4, and SHALL satisfy the evidence properties defined in MCC-CP-001, Section 14.3 (reproducible, traceable, verifiable, immutable after generation, attributable to a certification run).
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_evidence exports/verifies bundles in directory and .tar.gz form with bundle-level metadata (bundle_id, created_at), semantically close to this section, but uses one manifest.json plus named artifact paths rather than this specification's separate Bundle Descriptor / Integrity Record / Provenance Record files, so the exact structural requirement is not met.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-EB-001-9-EVIDENCE-BUNDLE-OVERVIEW-D02

- Specification / section: MCC-EB-001 / 9. Evidence Bundle Overview / 9.2 Bundle Forms
- Status: PARTIAL
- Requirement: An Evidence Bundle SHALL take one of the following forms: - a directory tree rooted at a single Bundle Root; or - a single deterministic archive of that directory tree.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_evidence exports/verifies bundles in directory and .tar.gz form with bundle-level metadata (bundle_id, created_at), semantically close to this section, but uses one manifest.json plus named artifact paths rather than this specification's separate Bundle Descriptor / Integrity Record / Provenance Record files, so the exact structural requirement is not met.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-EB-001-9-EVIDENCE-BUNDLE-OVERVIEW-D03

- Specification / section: MCC-EB-001 / 9. Evidence Bundle Overview / 9.2 Bundle Forms
- Status: PARTIAL
- Requirement: Both forms SHALL be structurally equivalent: converting between them SHALL NOT alter the Bundle's content or digests.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_evidence exports/verifies bundles in directory and .tar.gz form with bundle-level metadata (bundle_id, created_at), semantically close to this section, but uses one manifest.json plus named artifact paths rather than this specification's separate Bundle Descriptor / Integrity Record / Provenance Record files, so the exact structural requirement is not met.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-EB-001-9-EVIDENCE-BUNDLE-OVERVIEW-D04

- Specification / section: MCC-EB-001 / 9. Evidence Bundle Overview / 9.3 Relationship to Certification Requirements
- Status: PARTIAL
- Requirement: Every Evidence Item within a Bundle SHALL correspond to one or more Certification Requirements evaluated under MCC-CP-001, Section 12.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_evidence exports/verifies bundles in directory and .tar.gz form with bundle-level metadata (bundle_id, created_at), semantically close to this section, but uses one manifest.json plus named artifact paths rather than this specification's separate Bundle Descriptor / Integrity Record / Provenance Record files, so the exact structural requirement is not met.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-TC-001-1-PURPOSE-D01

- Specification / section: MCC-TC-001 / 1. Purpose
- Status: GAP
- Requirement: - **Framework Neutrality.** The Certificate format MUST remain independent of any particular framework, programming language, or certification tooling implementation.
- Existing implementation: None
- Missing implementation behavior: Full requirement not implemented.
- Missing test coverage: No test exists for this requirement.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: No implementation behavior, automated test, or evidence mechanism semantically equivalent to this requirement (category: '1. Purpose') was found anywhere under src/, tests/, certifications/, evidence/, schemas/, docs/, or CI workflows, after the broader semantic-mapping investigation described in this module's docstring — not merely a lexical search for this specification's exact terminology.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-TC-001-1-PURPOSE-D02

- Specification / section: MCC-TC-001 / 1. Purpose
- Status: GAP
- Requirement: - **Authoritative Representation.** A Technical Certificate MUST represent the authoritative outcome of a successful certification, and MUST NOT be issuable for an unsuccessful certification.
- Existing implementation: None
- Missing implementation behavior: Full requirement not implemented.
- Missing test coverage: No test exists for this requirement.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: No implementation behavior, automated test, or evidence mechanism semantically equivalent to this requirement (category: '1. Purpose') was found anywhere under src/, tests/, certifications/, evidence/, schemas/, docs/, or CI workflows, after the broader semantic-mapping investigation described in this module's docstring — not merely a lexical search for this specification's exact terminology.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-TC-001-1-PURPOSE-D03

- Specification / section: MCC-TC-001 / 1. Purpose
- Status: GAP
- Requirement: - **Independent Verifiability.** A third party MUST be able to verify a Certificate's authenticity, integrity, and current validity using only the Certificate, a recognized Trust Anchor, and this specification.
- Existing implementation: None
- Missing implementation behavior: Full requirement not implemented.
- Missing test coverage: No test exists for this requirement.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: No implementation behavior, automated test, or evidence mechanism semantically equivalent to this requirement (category: '1. Purpose') was found anywhere under src/, tests/, certifications/, evidence/, schemas/, docs/, or CI workflows, after the broader semantic-mapping investigation described in this module's docstring — not merely a lexical search for this specification's exact terminology.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-TC-001-1-PURPOSE-D04

- Specification / section: MCC-TC-001 / 1. Purpose
- Status: GAP
- Requirement: - **Traceability.** A Technical Certificate MUST remain traceable to the Certification Subject, the specification version, the Certification Manifest, and the Evidence Bundle that substantiate it.
- Existing implementation: None
- Missing implementation behavior: Full requirement not implemented.
- Missing test coverage: No test exists for this requirement.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: No implementation behavior, automated test, or evidence mechanism semantically equivalent to this requirement (category: '1. Purpose') was found anywhere under src/, tests/, certifications/, evidence/, schemas/, docs/, or CI workflows, after the broader semantic-mapping investigation described in this module's docstring — not merely a lexical search for this specification's exact terminology.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-TC-001-10-ISSUER-INFORMATION-D01

- Specification / section: MCC-TC-001 / 10. Issuer Information / 10.2 Issuer Fields
- Status: PARTIAL
- Requirement: A Technical Certificate MUST identify its Issuer by a stable Issuer identifier associated with a Trust Anchor, as defined by Section 16.
- Existing implementation: gateway/trust.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: gateway/trust.py implements a real, tested per-issuer Ed25519 key model (the Issuer/Trust Anchor concept this section requires), but it is not wired to certifications/manifest.json entries, which instead carry only an informal issuer statement (CERTIFICATION_NOTE).
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-TC-001-10-ISSUER-INFORMATION-D02

- Specification / section: MCC-TC-001 / 10. Issuer Information / 10.3 Issuer Authority
- Status: PARTIAL
- Requirement: A Technical Certificate MUST NOT be considered validly issued unless its Issuer is recognized as the Certification Authority under MCC-CP-001, Section 7.1, at the time of verification.
- Existing implementation: gateway/trust.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: gateway/trust.py implements a real, tested per-issuer Ed25519 key model (the Issuer/Trust Anchor concept this section requires), but it is not wired to certifications/manifest.json entries, which instead carry only an informal issuer statement (CERTIFICATION_NOTE).
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-TC-001-11-VALIDITY-PERIOD-D01

- Specification / section: MCC-TC-001 / 11. Validity Period / 11.2 Issuance Timestamp
- Status: PARTIAL
- Requirement: A Technical Certificate MUST NOT be considered valid before its issuance timestamp.
- Existing implementation: gateway/trust.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: gateway/trust.py's per-key not_after expiry implements the same validity-period-with-optional-expiration model this section requires, though for trust/mandate keys, not for a Technical Certificate.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-TC-001-11-VALIDITY-PERIOD-D02

- Specification / section: MCC-TC-001 / 11. Validity Period / 11.3 Expiration
- Status: PARTIAL
- Requirement: Where no expiration timestamp is declared, a Technical Certificate SHALL remain valid indefinitely, subject only to revocation under Section 12.
- Existing implementation: gateway/trust.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: gateway/trust.py's per-key not_after expiry implements the same validity-period-with-optional-expiration model this section requires, though for trust/mandate keys, not for a Technical Certificate.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-TC-001-11-VALIDITY-PERIOD-D03

- Specification / section: MCC-TC-001 / 11. Validity Period / 11.3 Expiration
- Status: PARTIAL
- Requirement: Where an expiration timestamp is declared, a Technical Certificate MUST NOT be considered valid after that timestamp.
- Existing implementation: gateway/trust.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: gateway/trust.py's per-key not_after expiry implements the same validity-period-with-optional-expiration model this section requires, though for trust/mandate keys, not for a Technical Certificate.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-TC-001-12-REVOCATION-MODEL-D01

- Specification / section: MCC-TC-001 / 12. Revocation Model / 12.2 Immutability and Revocation
- Status: PARTIAL
- Requirement: A Technical Certificate MUST remain immutable after issuance, consistent with MCC-CP-001, Section 16.6, CERT-007.
- Existing implementation: gateway/trust.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: gateway/trust.py implements a real, tested REVOKED_KEY status and fail-closed unresolved/revoked-key handling — the same external-revocation-record, verifier-must-check model this section requires, scoped to trust/mandate keys rather than a Technical Certificate's own Revocation Record.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-TC-001-12-REVOCATION-MODEL-D02

- Specification / section: MCC-TC-001 / 12. Revocation Model / 12.2 Immutability and Revocation
- Status: PARTIAL
- Requirement: Revocation SHALL NOT be represented by modifying a Technical Certificate's own content.
- Existing implementation: gateway/trust.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: gateway/trust.py implements a real, tested REVOKED_KEY status and fail-closed unresolved/revoked-key handling — the same external-revocation-record, verifier-must-check model this section requires, scoped to trust/mandate keys rather than a Technical Certificate's own Revocation Record.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-TC-001-12-REVOCATION-MODEL-D03

- Specification / section: MCC-TC-001 / 12. Revocation Model / 12.2 Immutability and Revocation
- Status: PARTIAL
- Requirement: Revocation SHALL be represented by an external Revocation Record.
- Existing implementation: gateway/trust.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: gateway/trust.py implements a real, tested REVOKED_KEY status and fail-closed unresolved/revoked-key handling — the same external-revocation-record, verifier-must-check model this section requires, scoped to trust/mandate keys rather than a Technical Certificate's own Revocation Record.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-TC-001-12-REVOCATION-MODEL-D04

- Specification / section: MCC-TC-001 / 12. Revocation Model / 12.3 Revocation Record
- Status: PARTIAL
- Requirement: A Revocation Record MUST identify: - the certificate identifier of the revoked Technical Certificate; - the revocation timestamp; - the Issuer that authorized the revocation.
- Existing implementation: gateway/trust.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: gateway/trust.py implements a real, tested REVOKED_KEY status and fail-closed unresolved/revoked-key handling — the same external-revocation-record, verifier-must-check model this section requires, scoped to trust/mandate keys rather than a Technical Certificate's own Revocation Record.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-TC-001-12-REVOCATION-MODEL-D05

- Specification / section: MCC-TC-001 / 12. Revocation Model / 12.4 Revocation Authority
- Status: PARTIAL
- Requirement: A Technical Certificate MUST NOT be revoked by any party other than the Issuer that issued it, or an entity the Issuer has designated in accordance with the Trust Model defined in Section 16.
- Existing implementation: gateway/trust.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: gateway/trust.py implements a real, tested REVOKED_KEY status and fail-closed unresolved/revoked-key handling — the same external-revocation-record, verifier-must-check model this section requires, scoped to trust/mandate keys rather than a Technical Certificate's own Revocation Record.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-TC-001-12-REVOCATION-MODEL-D06

- Specification / section: MCC-TC-001 / 12. Revocation Model / 12.5 Revocation Effect
- Status: PARTIAL
- Requirement: Once a valid Revocation Record exists for a Technical Certificate, that Certificate MUST NOT be treated as currently valid regardless of its Validity Period under Section 11.
- Existing implementation: gateway/trust.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: gateway/trust.py implements a real, tested REVOKED_KEY status and fail-closed unresolved/revoked-key handling — the same external-revocation-record, verifier-must-check model this section requires, scoped to trust/mandate keys rather than a Technical Certificate's own Revocation Record.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-TC-001-12-REVOCATION-MODEL-D07

- Specification / section: MCC-TC-001 / 12. Revocation Model / 12.5 Revocation Effect
- Status: PARTIAL
- Requirement: A revoked Technical Certificate's content, and the historical fact that it was issued, MUST remain available for audit and traceability, consistent with MCC-CP-001, Appendix A, STATE-005.
- Existing implementation: gateway/trust.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: gateway/trust.py implements a real, tested REVOKED_KEY status and fail-closed unresolved/revoked-key handling — the same external-revocation-record, verifier-must-check model this section requires, scoped to trust/mandate keys rather than a Technical Certificate's own Revocation Record.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-TC-001-12-REVOCATION-MODEL-D08

- Specification / section: MCC-TC-001 / 12. Revocation Model / 12.6 Revocation Check Requirement
- Status: PARTIAL
- Requirement: A verifier MUST check for the existence of a valid Revocation Record for a Technical Certificate before treating that Certificate as currently valid.
- Existing implementation: gateway/trust.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: gateway/trust.py implements a real, tested REVOKED_KEY status and fail-closed unresolved/revoked-key handling — the same external-revocation-record, verifier-must-check model this section requires, scoped to trust/mandate keys rather than a Technical Certificate's own Revocation Record.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-TC-001-13-CRYPTOGRAPHIC-INTEGRITY-D01

- Specification / section: MCC-TC-001 / 13. Cryptographic Integrity / 13.2 Digest Requirements
- Status: PARTIAL
- Requirement: Where a Technical Certificate includes a Hash Reference to its Certification Manifest or to its Evidence Bundle, that Hash Reference MUST use a collision-resistant cryptographic hash function, consistent with MCC-EB-001, Section 13.3 and MCC-CM-001, Section 13.3.
- Existing implementation: src/mcc_core/signing.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_core/signing.py provides the collision-resistant digest primitive this section requires; src/mcc_evidence/verify.py demonstrates it applied to binding a signed artifact to referenced content, though not to a Technical Certificate specifically.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-TC-001-14-SIGNATURE-REQUIREMENTS-D01

- Specification / section: MCC-TC-001 / 14. Signature Requirements / 14.2 Signature Algorithm
- Status: PARTIAL
- Requirement: The signature algorithm used to sign a Technical Certificate MUST be an asymmetric (public-key) digital signature scheme.
- Existing implementation: src/mcc_core/signing.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: The runtime signs its own authority-bearing artifact (the Decision Token, a different artifact per Section 3.4) exclusively with Ed25519, with a dedicated repository-wide test confirming no symmetric-key or shared-secret mechanism is used anywhere in that signing path.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-TC-001-14-SIGNATURE-REQUIREMENTS-D02

- Specification / section: MCC-TC-001 / 14. Signature Requirements / 14.2 Signature Algorithm
- Status: PARTIAL
- Requirement: The signature algorithm MUST NOT be a symmetric-key or shared-secret authentication mechanism, including HMAC.
- Existing implementation: src/mcc_core/signing.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: The runtime signs its own authority-bearing artifact (the Decision Token, a different artifact per Section 3.4) exclusively with Ed25519, with a dedicated repository-wide test confirming no symmetric-key or shared-secret mechanism is used anywhere in that signing path.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-TC-001-14-SIGNATURE-REQUIREMENTS-D03

- Specification / section: MCC-TC-001 / 14. Signature Requirements / 14.3 Signature Coverage
- Status: PARTIAL
- Requirement: A Technical Certificate's Signature MUST cover the complete Canonical Form of the Certificate, excluding the Signature field itself, as defined by Section 4.4.
- Existing implementation: src/mcc_core/signing.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: The runtime signs its own authority-bearing artifact (the Decision Token, a different artifact per Section 3.4) exclusively with Ed25519, with a dedicated repository-wide test confirming no symmetric-key or shared-secret mechanism is used anywhere in that signing path.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-TC-001-14-SIGNATURE-REQUIREMENTS-D04

- Specification / section: MCC-TC-001 / 14. Signature Requirements / 14.3 Signature Coverage
- Status: PARTIAL
- Requirement: A Signature MUST become invalid if any covered field is modified after signing.
- Existing implementation: src/mcc_core/signing.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: The runtime signs its own authority-bearing artifact (the Decision Token, a different artifact per Section 3.4) exclusively with Ed25519, with a dedicated repository-wide test confirming no symmetric-key or shared-secret mechanism is used anywhere in that signing path.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-TC-001-14-SIGNATURE-REQUIREMENTS-D05

- Specification / section: MCC-TC-001 / 14. Signature Requirements / 14.4 Signature Declaration
- Status: PARTIAL
- Requirement: A Technical Certificate MUST declare the signature algorithm used and the Issuer identity associated with the signing key.
- Existing implementation: src/mcc_core/signing.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: The runtime signs its own authority-bearing artifact (the Decision Token, a different artifact per Section 3.4) exclusively with Ed25519, with a dedicated repository-wide test confirming no symmetric-key or shared-secret mechanism is used anywhere in that signing path.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-TC-001-15-VERIFICATION-PROCEDURE-D01

- Specification / section: MCC-TC-001 / 15. Verification Procedure / 15.1 Purpose
- Status: PARTIAL
- Requirement: This section defines the normative procedure and criteria a verifier MUST apply to determine whether a Technical Certificate is currently valid.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_evidence/verify.py implements an ordered, fail-closed, multi-step verification procedure (structure, then integrity, then signature, then consistency) procedurally analogous to this section, for the Governance Evidence Bundle rather than a Technical Certificate.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-TC-001-15-VERIFICATION-PROCEDURE-D02

- Specification / section: MCC-TC-001 / 15. Verification Procedure / 15.2 Structural Verification
- Status: PARTIAL
- Requirement: A verifier MUST verify that the Certificate conforms to the Certificate Schema defined in Section 4 and contains all Required Fields defined in Section 6.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_evidence/verify.py implements an ordered, fail-closed, multi-step verification procedure (structure, then integrity, then signature, then consistency) procedurally analogous to this section, for the Governance Evidence Bundle rather than a Technical Certificate.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-TC-001-15-VERIFICATION-PROCEDURE-D03

- Specification / section: MCC-TC-001 / 15. Verification Procedure / 15.2 Structural Verification
- Status: PARTIAL
- Requirement: A Certificate that fails structural verification MUST be rejected without further processing.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_evidence/verify.py implements an ordered, fail-closed, multi-step verification procedure (structure, then integrity, then signature, then consistency) procedurally analogous to this section, for the Governance Evidence Bundle rather than a Technical Certificate.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-TC-001-15-VERIFICATION-PROCEDURE-D04

- Specification / section: MCC-TC-001 / 15. Verification Procedure / 15.3 Signature Verification
- Status: PARTIAL
- Requirement: A verifier MUST verify the Certificate's Signature against a Trust Anchor associated with the declared Issuer, consistent with Section 16.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_evidence/verify.py implements an ordered, fail-closed, multi-step verification procedure (structure, then integrity, then signature, then consistency) procedurally analogous to this section, for the Governance Evidence Bundle rather than a Technical Certificate.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-TC-001-15-VERIFICATION-PROCEDURE-D05

- Specification / section: MCC-TC-001 / 15. Verification Procedure / 15.3 Signature Verification
- Status: PARTIAL
- Requirement: A Certificate with an invalid or unverifiable Signature MUST be rejected.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_evidence/verify.py implements an ordered, fail-closed, multi-step verification procedure (structure, then integrity, then signature, then consistency) procedurally analogous to this section, for the Governance Evidence Bundle rather than a Technical Certificate.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-TC-001-15-VERIFICATION-PROCEDURE-D06

- Specification / section: MCC-TC-001 / 15. Verification Procedure / 15.4 Manifest Reference Verification
- Status: PARTIAL
- Requirement: A verifier MUST verify the Manifest Reference, including its Hash Reference, against the referenced Certification Manifest, consistent with MCC-CM-001, Section 18.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_evidence/verify.py implements an ordered, fail-closed, multi-step verification procedure (structure, then integrity, then signature, then consistency) procedurally analogous to this section, for the Governance Evidence Bundle rather than a Technical Certificate.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-TC-001-15-VERIFICATION-PROCEDURE-D07

- Specification / section: MCC-TC-001 / 15. Verification Procedure / 15.4 Manifest Reference Verification
- Status: PARTIAL
- Requirement: A Certificate whose Manifest Reference cannot be verified MUST be rejected.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_evidence/verify.py implements an ordered, fail-closed, multi-step verification procedure (structure, then integrity, then signature, then consistency) procedurally analogous to this section, for the Governance Evidence Bundle rather than a Technical Certificate.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-TC-001-15-VERIFICATION-PROCEDURE-D08

- Specification / section: MCC-TC-001 / 15. Verification Procedure / 15.5 Evidence Bundle Reference Consistency Verification
- Status: PARTIAL
- Requirement: A verifier MUST perform the following steps, in order, to verify the Certificate's Evidence Bundle Reference:
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_evidence/verify.py implements an ordered, fail-closed, multi-step verification procedure (structure, then integrity, then signature, then consistency) procedurally analogous to this section, for the Governance Evidence Bundle rather than a Technical Certificate.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-TC-001-15-VERIFICATION-PROCEDURE-D09

- Specification / section: MCC-TC-001 / 15. Verification Procedure / 15.5 Evidence Bundle Reference Consistency Verification
- Status: PARTIAL
- Requirement: Both Evidence Bundle References MUST identify the exact same Evidence Bundle.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_evidence/verify.py implements an ordered, fail-closed, multi-step verification procedure (structure, then integrity, then signature, then consistency) procedurally analogous to this section, for the Governance Evidence Bundle rather than a Technical Certificate.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-TC-001-15-VERIFICATION-PROCEDURE-D10

- Specification / section: MCC-TC-001 / 15. Verification Procedure / 15.5 Evidence Bundle Reference Consistency Verification
- Status: PARTIAL
- Requirement: A verifier MUST return verification failure if the two Evidence Bundle References identify different Evidence Bundles.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_evidence/verify.py implements an ordered, fail-closed, multi-step verification procedure (structure, then integrity, then signature, then consistency) procedurally analogous to this section, for the Governance Evidence Bundle rather than a Technical Certificate.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-TC-001-15-VERIFICATION-PROCEDURE-D11

- Specification / section: MCC-TC-001 / 15. Verification Procedure / 15.5 Evidence Bundle Reference Consistency Verification
- Status: PARTIAL
- Requirement: A Certificate whose direct Evidence Bundle Reference cannot itself be verified against the referenced Evidence Bundle's Integrity Record, consistent with MCC-EB-001, Section 16, MUST also be rejected.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_evidence/verify.py implements an ordered, fail-closed, multi-step verification procedure (structure, then integrity, then signature, then consistency) procedurally analogous to this section, for the Governance Evidence Bundle rather than a Technical Certificate.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-TC-001-15-VERIFICATION-PROCEDURE-D12

- Specification / section: MCC-TC-001 / 15. Verification Procedure / 15.6 Subject and Result Consistency Verification
- Status: PARTIAL
- Requirement: A verifier MUST verify Subject consistency per Section 8.3 and Certification Result consistency per Section 9.3.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_evidence/verify.py implements an ordered, fail-closed, multi-step verification procedure (structure, then integrity, then signature, then consistency) procedurally analogous to this section, for the Governance Evidence Bundle rather than a Technical Certificate.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-TC-001-15-VERIFICATION-PROCEDURE-D13

- Specification / section: MCC-TC-001 / 15. Verification Procedure / 15.7 Validity and Revocation Verification
- Status: PARTIAL
- Requirement: A verifier MUST verify that the Certificate is within its Validity Period per Section 11 and MUST check for a Revocation Record per Section 12.6.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_evidence/verify.py implements an ordered, fail-closed, multi-step verification procedure (structure, then integrity, then signature, then consistency) procedurally analogous to this section, for the Governance Evidence Bundle rather than a Technical Certificate.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-TC-001-15-VERIFICATION-PROCEDURE-D14

- Specification / section: MCC-TC-001 / 15. Verification Procedure / 15.7 Validity and Revocation Verification
- Status: PARTIAL
- Requirement: A Certificate that is expired or revoked MUST NOT be treated as currently valid, even if all other verification steps succeed.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_evidence/verify.py implements an ordered, fail-closed, multi-step verification procedure (structure, then integrity, then signature, then consistency) procedurally analogous to this section, for the Governance Evidence Bundle rather than a Technical Certificate.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-TC-001-15-VERIFICATION-PROCEDURE-D15

- Specification / section: MCC-TC-001 / 15. Verification Procedure / 15.8 Fail-Closed Verification
- Status: PARTIAL
- Requirement: Verification SHALL be fail-closed: a Technical Certificate MUST be treated as invalid unless every applicable verification step in this section succeeds.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_evidence/verify.py implements an ordered, fail-closed, multi-step verification procedure (structure, then integrity, then signature, then consistency) procedurally analogous to this section, for the Governance Evidence Bundle rather than a Technical Certificate.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-TC-001-15-VERIFICATION-PROCEDURE-D16

- Specification / section: MCC-TC-001 / 15. Verification Procedure / 15.8 Fail-Closed Verification
- Status: PARTIAL
- Requirement: Partial or inconclusive verification results MUST NOT be treated as valid.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_evidence/verify.py implements an ordered, fail-closed, multi-step verification procedure (structure, then integrity, then signature, then consistency) procedurally analogous to this section, for the Governance Evidence Bundle rather than a Technical Certificate.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-TC-001-16-TRUST-MODEL-D01

- Specification / section: MCC-TC-001 / 16. Trust Model / 16.2 Trust Anchors
- Status: PARTIAL
- Requirement: A verifier MUST possess or obtain a set of Trust Anchors it recognizes through a mechanism outside the scope of this specification.
- Existing implementation: gateway/trust.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: gateway/trust.py is a real, tested multi-issuer trust set (per-issuer keys, rotation, expiry, revocation, fail-closed unresolved-key handling) — the closest and strongest analog to this section found in the repository, though scoped to mandate/approval trust, not Technical Certificate trust.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-TC-001-16-TRUST-MODEL-D02

- Specification / section: MCC-TC-001 / 16. Trust Model / 16.3 Trust Anchor Recognition
- Status: PARTIAL
- Requirement: A Technical Certificate signed by a key that does not correspond to a Trust Anchor recognized by the verifier MUST NOT be treated as valid.
- Existing implementation: gateway/trust.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: gateway/trust.py is a real, tested multi-issuer trust set (per-issuer keys, rotation, expiry, revocation, fail-closed unresolved-key handling) — the closest and strongest analog to this section found in the repository, though scoped to mandate/approval trust, not Technical Certificate trust.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-TC-001-16-TRUST-MODEL-D03

- Specification / section: MCC-TC-001 / 16. Trust Model / 16.3 Trust Anchor Recognition
- Status: PARTIAL
- Requirement: Recognition of a Trust Anchor MUST NOT be inferred from the Certificate itself; a Certificate MUST NOT be trusted merely because it declares an Issuer identity.
- Existing implementation: gateway/trust.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: gateway/trust.py is a real, tested multi-issuer trust set (per-issuer keys, rotation, expiry, revocation, fail-closed unresolved-key handling) — the closest and strongest analog to this section found in the repository, though scoped to mandate/approval trust, not Technical Certificate trust.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-TC-001-16-TRUST-MODEL-D04

- Specification / section: MCC-TC-001 / 16. Trust Model / 16.4 Trust Anchor Rotation and Revocation
- Status: PARTIAL
- Requirement: Where an Issuer's signing key is rotated or revoked, a verifier MUST cease treating Technical Certificates signed with the superseded key as currently trusted for new verification, without invalidating the historical fact that they were issued.
- Existing implementation: gateway/trust.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: gateway/trust.py is a real, tested multi-issuer trust set (per-issuer keys, rotation, expiry, revocation, fail-closed unresolved-key handling) — the closest and strongest analog to this section found in the repository, though scoped to mandate/approval trust, not Technical Certificate trust.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-TC-001-16-TRUST-MODEL-D05

- Specification / section: MCC-TC-001 / 16. Trust Model / 16.5 Multiple Trust Domains
- Status: PARTIAL
- Requirement: A verifier MUST NOT treat a Technical Certificate as valid solely because it was signed by a key not among the verifier's recognized Trust Anchors, regardless of any other party's trust in that key.
- Existing implementation: gateway/trust.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: gateway/trust.py is a real, tested multi-issuer trust set (per-issuer keys, rotation, expiry, revocation, fail-closed unresolved-key handling) — the closest and strongest analog to this section found in the repository, though scoped to mandate/approval trust, not Technical Certificate trust.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-TC-001-17-COMPATIBILITY-D01

- Specification / section: MCC-TC-001 / 17. Compatibility / 17.3 Forward Compatibility
- Status: PARTIAL
- Requirement: A verifier MUST NOT assume forward compatibility with a Certificate Schema Version it does not recognize.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: Independent schema/contract versioning exists for the compliance-manifest artifact family (compliance_suite_version, contract_version, MANIFEST_SCHEMA_VERSION), the same independent-tracking model this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-TC-001-17-COMPATIBILITY-D02

- Specification / section: MCC-TC-001 / 17. Compatibility / 17.3 Forward Compatibility
- Status: PARTIAL
- Requirement: An unrecognized Certificate Schema Version MUST be treated per Section 18.4 and Section 15.8, not silently accepted.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: Independent schema/contract versioning exists for the compliance-manifest artifact family (compliance_suite_version, contract_version, MANIFEST_SCHEMA_VERSION), the same independent-tracking model this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-TC-001-17-COMPATIBILITY-D03

- Specification / section: MCC-TC-001 / 17. Compatibility / 17.4 Cross-Specification Compatibility
- Status: PARTIAL
- Requirement: A Technical Certificate MUST NOT be considered valid if it references a Manifest Schema Version that MCC-CM-001, as currently published, does not recognize.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: Independent schema/contract versioning exists for the compliance-manifest artifact family (compliance_suite_version, contract_version, MANIFEST_SCHEMA_VERSION), the same independent-tracking model this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-TC-001-17-COMPATIBILITY-D04

- Specification / section: MCC-TC-001 / 17. Compatibility / 17.4 Cross-Specification Compatibility
- Status: PARTIAL
- Requirement: A Technical Certificate MUST NOT be considered valid if its direct Evidence Bundle Reference identifies an Evidence Bundle Schema Version that MCC-EB-001, as currently published, does not recognize.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: Independent schema/contract versioning exists for the compliance-manifest artifact family (compliance_suite_version, contract_version, MANIFEST_SCHEMA_VERSION), the same independent-tracking model this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-TC-001-18-VERSIONING-D01

- Specification / section: MCC-TC-001 / 18. Versioning / 18.2 Schema Version Declaration
- Status: PARTIAL
- Requirement: Every Technical Certificate MUST declare its Certificate Schema Version among its Identity fields.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: Independent schema/contract versioning exists for the compliance-manifest artifact family (compliance_suite_version, contract_version, MANIFEST_SCHEMA_VERSION), the same independent-tracking model this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-TC-001-18-VERSIONING-D02

- Specification / section: MCC-TC-001 / 18. Versioning / 18.2 Schema Version Declaration
- Status: PARTIAL
- Requirement: The Certificate Schema Version MUST be immutable once assigned to a published revision of this specification.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: Independent schema/contract versioning exists for the compliance-manifest artifact family (compliance_suite_version, contract_version, MANIFEST_SCHEMA_VERSION), the same independent-tracking model this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-TC-001-18-VERSIONING-D03

- Specification / section: MCC-TC-001 / 18. Versioning / 18.3 Schema Version Scope
- Status: PARTIAL
- Requirement: The Certificate Schema Version is distinct from, and SHALL NOT be conflated with, the MCC-CP-001 specification version, the Evidence Bundle Schema Version, or the Manifest Schema Version referenced by a Certificate.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: Independent schema/contract versioning exists for the compliance-manifest artifact family (compliance_suite_version, contract_version, MANIFEST_SCHEMA_VERSION), the same independent-tracking model this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-TC-001-18-VERSIONING-D04

- Specification / section: MCC-TC-001 / 18. Versioning / 18.4 Version Evolution
- Status: PARTIAL
- Requirement: A verifier MUST reject a Technical Certificate declaring a Schema Version it does not recognize.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: Independent schema/contract versioning exists for the compliance-manifest artifact family (compliance_suite_version, contract_version, MANIFEST_SCHEMA_VERSION), the same independent-tracking model this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-TC-001-19-SECURITY-CONSIDERATIONS-D01

- Specification / section: MCC-TC-001 / 19. Security Considerations / 19.2 Threat Model
- Status: PARTIAL
- Requirement: Verification of a Technical Certificate MUST assume: - the Certificate MAY originate from an untrusted or compromised source; - the Certificate MAY have been forged, tampered with, expired, or revoked; - the environment that produced or transmitted the Certificate MUST NOT be trusted implicitly.
- Existing implementation: gateway/trust.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: gateway/trust.py assumes an untrusted/unresolved key yields no trust (fail-closed), the same threat model this section requires for Certificate forgery/tamper resistance.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-TC-001-19-SECURITY-CONSIDERATIONS-D02

- Specification / section: MCC-TC-001 / 19. Security Considerations / 19.3 Forgery and Tamper Resistance
- Status: PARTIAL
- Requirement: A verifier MUST NOT treat any Certificate content as authoritative prior to successful Signature Verification.
- Existing implementation: gateway/trust.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: gateway/trust.py assumes an untrusted/unresolved key yields no trust (fail-closed), the same threat model this section requires for Certificate forgery/tamper resistance.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-TC-001-19-SECURITY-CONSIDERATIONS-D03

- Specification / section: MCC-TC-001 / 19. Security Considerations / 19.4 Sensitive Data
- Status: PARTIAL
- Requirement: A Technical Certificate MUST NOT include secrets, credentials, or other sensitive material not required to represent the certification outcome.
- Existing implementation: gateway/trust.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: gateway/trust.py assumes an untrusted/unresolved key yields no trust (fail-closed), the same threat model this section requires for Certificate forgery/tamper resistance.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-TC-001-19-SECURITY-CONSIDERATIONS-D04

- Specification / section: MCC-TC-001 / 19. Security Considerations / 19.4 Sensitive Data
- Status: PARTIAL
- Requirement: Where underlying certification inputs contain sensitive material, Certificate fields MUST reference redacted or hashed representations rather than raw sensitive values, consistent with MCC-EB-001, Section 19.4 and MCC-CM-001, Section 19.4.
- Existing implementation: gateway/trust.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: gateway/trust.py assumes an untrusted/unresolved key yields no trust (fail-closed), the same threat model this section requires for Certificate forgery/tamper resistance.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-TC-001-19-SECURITY-CONSIDERATIONS-D05

- Specification / section: MCC-TC-001 / 19. Security Considerations / 19.5 Runtime Governance Boundary
- Status: PARTIAL
- Requirement: A Technical Certificate MUST NOT be used, by any implementation, as a substitute for a runtime governance decision.
- Existing implementation: gateway/trust.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: gateway/trust.py assumes an untrusted/unresolved key yields no trust (fail-closed), the same threat model this section requires for Certificate forgery/tamper resistance.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-TC-001-19-SECURITY-CONSIDERATIONS-D06

- Specification / section: MCC-TC-001 / 19. Security Considerations / 19.5 Runtime Governance Boundary
- Status: PARTIAL
- Requirement: Possession of a valid Technical Certificate for a Certification Subject MUST NOT be treated as authorization to execute any runtime action governed by MCC-Core.
- Existing implementation: gateway/trust.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: gateway/trust.py assumes an untrusted/unresolved key yields no trust (fail-closed), the same threat model this section requires for Certificate forgery/tamper resistance.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-TC-001-20-EXTENSION-MODEL-D01

- Specification / section: MCC-TC-001 / 20. Extension Model / 20.2 Extension Points
- Status: GAP
- Requirement: Extensions MUST be declared and identified as such within the Certificate.
- Existing implementation: None
- Missing implementation behavior: Full requirement not implemented.
- Missing test coverage: No test exists for this requirement.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: No extension-declaration mechanism (a way to mark additional fields as explicit, non-breaking extensions to a committed schema) was found anywhere in this repository for any artifact.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-TC-001-20-EXTENSION-MODEL-D02

- Specification / section: MCC-TC-001 / 20. Extension Model / 20.3 Extension Constraints
- Status: GAP
- Requirement: An extension MUST NOT alter the meaning of any Required Field, the Signature, the Manifest Reference, or the Evidence Bundle Reference defined by this specification.
- Existing implementation: None
- Missing implementation behavior: Full requirement not implemented.
- Missing test coverage: No test exists for this requirement.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: No extension-declaration mechanism (a way to mark additional fields as explicit, non-breaking extensions to a committed schema) was found anywhere in this repository for any artifact.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-TC-001-20-EXTENSION-MODEL-D03

- Specification / section: MCC-TC-001 / 20. Extension Model / 20.3 Extension Constraints
- Status: GAP
- Requirement: An extension MUST be covered by the Certificate's Signature like any other Certificate content.
- Existing implementation: None
- Missing implementation behavior: Full requirement not implemented.
- Missing test coverage: No test exists for this requirement.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: No extension-declaration mechanism (a way to mark additional fields as explicit, non-breaking extensions to a committed schema) was found anywhere in this repository for any artifact.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-TC-001-20-EXTENSION-MODEL-D04

- Specification / section: MCC-TC-001 / 20. Extension Model / 20.3 Extension Constraints
- Status: GAP
- Requirement: A verifier that does not recognize a declared extension MUST ignore that extension's content without failing verification, provided all other verification steps in Section 15 are satisfied.
- Existing implementation: None
- Missing implementation behavior: Full requirement not implemented.
- Missing test coverage: No test exists for this requirement.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: No extension-declaration mechanism (a way to mark additional fields as explicit, non-breaking extensions to a committed schema) was found anywhere in this repository for any artifact.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-TC-001-21-CONFORMANCE-REQUIREMENTS-D01

- Specification / section: MCC-TC-001 / 21. Conformance Requirements / 21.2 Conforming Certificate Issuer
- Status: GAP
- Requirement: A conforming Certificate issuer MUST issue Technical Certificates satisfying Sections 4 through 14 of this specification for the Certificate Schema Version it declares.
- Existing implementation: None
- Missing implementation behavior: Full requirement not implemented.
- Missing test coverage: No test exists for this requirement.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: No issuer/verifier conformance-declaration mechanism specific to this specification's Certificate Schema Version was found.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-TC-001-21-CONFORMANCE-REQUIREMENTS-D02

- Specification / section: MCC-TC-001 / 21. Conformance Requirements / 21.2 Conforming Certificate Issuer
- Status: GAP
- Requirement: A conforming Certificate issuer MUST NOT issue a Technical Certificate for a certification result other than PASS.
- Existing implementation: None
- Missing implementation behavior: Full requirement not implemented.
- Missing test coverage: No test exists for this requirement.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: No issuer/verifier conformance-declaration mechanism specific to this specification's Certificate Schema Version was found.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-TC-001-21-CONFORMANCE-REQUIREMENTS-D03

- Specification / section: MCC-TC-001 / 21. Conformance Requirements / 21.2 Conforming Certificate Issuer
- Status: GAP
- Requirement: A conforming Certificate issuer MUST NOT issue a Technical Certificate that fails verification under Section 15 against its own declared Schema Version.
- Existing implementation: None
- Missing implementation behavior: Full requirement not implemented.
- Missing test coverage: No test exists for this requirement.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: No issuer/verifier conformance-declaration mechanism specific to this specification's Certificate Schema Version was found.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-TC-001-21-CONFORMANCE-REQUIREMENTS-D04

- Specification / section: MCC-TC-001 / 21. Conformance Requirements / 21.2 Conforming Certificate Issuer
- Status: GAP
- Requirement: A conforming Certificate issuer MUST ensure that the Certificate's direct Evidence Bundle Reference and the Evidence Bundle Reference contained in the referenced Certification Manifest identify the same Evidence Bundle before issuance.
- Existing implementation: None
- Missing implementation behavior: Full requirement not implemented.
- Missing test coverage: No test exists for this requirement.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: No issuer/verifier conformance-declaration mechanism specific to this specification's Certificate Schema Version was found.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-TC-001-21-CONFORMANCE-REQUIREMENTS-D05

- Specification / section: MCC-TC-001 / 21. Conformance Requirements / 21.3 Conforming Certificate Verifier
- Status: GAP
- Requirement: A conforming Certificate verifier MUST implement the verification procedure defined in Section 15 in full, without omitting any applicable step, including the Revocation Check Requirement of Section 12.6.
- Existing implementation: None
- Missing implementation behavior: Full requirement not implemented.
- Missing test coverage: No test exists for this requirement.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: No issuer/verifier conformance-declaration mechanism specific to this specification's Certificate Schema Version was found.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-TC-001-21-CONFORMANCE-REQUIREMENTS-D06

- Specification / section: MCC-TC-001 / 21. Conformance Requirements / 21.3 Conforming Certificate Verifier
- Status: GAP
- Requirement: A conforming Certificate verifier MUST reject a Technical Certificate whenever any applicable verification step fails.
- Existing implementation: None
- Missing implementation behavior: Full requirement not implemented.
- Missing test coverage: No test exists for this requirement.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: No issuer/verifier conformance-declaration mechanism specific to this specification's Certificate Schema Version was found.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-TC-001-21-CONFORMANCE-REQUIREMENTS-D07

- Specification / section: MCC-TC-001 / 21. Conformance Requirements / 21.4 Conformance Independence
- Status: GAP
- Requirement: Conformance to this specification SHALL be evaluated independently of any specific programming language, framework, or certification tooling implementation.
- Existing implementation: None
- Missing implementation behavior: Full requirement not implemented.
- Missing test coverage: No test exists for this requirement.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: No issuer/verifier conformance-declaration mechanism specific to this specification's Certificate Schema Version was found.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-TC-001-22-REQUIREMENT-IDENTIFIER-REGISTRY-D01

- Specification / section: MCC-TC-001 / 22. Requirement Identifier Registry / 22.2 Namespace Convention
- Status: NOT_APPLICABLE
- Requirement: Every normative requirement identifier defined by this specification SHALL be prefixed with `TC-`, followed by a section-scoped category tag, followed by a three-digit sequence number.
- Existing implementation: None
- Missing implementation behavior: N/A (not an implementable requirement).
- Missing test coverage: No test exists for this requirement.
- Missing evidence: N/A
- Rationale: Interpretive, bibliographic, non-normative-by-design (explicitly marked informative/example), or document-self-referential statement. It does not describe a discrete, independently implementable system behavior.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: N/A

## MCC-TC-001-22-REQUIREMENT-IDENTIFIER-REGISTRY-D02

- Specification / section: MCC-TC-001 / 22. Requirement Identifier Registry / 22.4 Registry Requirements
- Status: NOT_APPLICABLE
- Requirement: Requirement identifiers under this specification's `TC-` namespace SHALL be globally unique.
- Existing implementation: None
- Missing implementation behavior: N/A (not an implementable requirement).
- Missing test coverage: No test exists for this requirement.
- Missing evidence: N/A
- Rationale: Interpretive, bibliographic, non-normative-by-design (explicitly marked informative/example), or document-self-referential statement. It does not describe a discrete, independently implementable system behavior.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: N/A

## MCC-TC-001-22-REQUIREMENT-IDENTIFIER-REGISTRY-D03

- Specification / section: MCC-TC-001 / 22. Requirement Identifier Registry / 22.4 Registry Requirements
- Status: NOT_APPLICABLE
- Requirement: A future revision of this specification MUST NOT reuse a retired identifier for a different requirement.
- Existing implementation: None
- Missing implementation behavior: N/A (not an implementable requirement).
- Missing test coverage: No test exists for this requirement.
- Missing evidence: N/A
- Rationale: Interpretive, bibliographic, non-normative-by-design (explicitly marked informative/example), or document-self-referential statement. It does not describe a discrete, independently implementable system behavior.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: N/A

## MCC-TC-001-22-REQUIREMENT-IDENTIFIER-REGISTRY-D04

- Specification / section: MCC-TC-001 / 22. Requirement Identifier Registry / 22.4 Registry Requirements
- Status: NOT_APPLICABLE
- Requirement: A future revision of this specification MUST NOT introduce a new category tag that collides with a prefix already registered by MCC-CP-001, MCC-EB-001, or MCC-CM-001.
- Existing implementation: None
- Missing implementation behavior: N/A (not an implementable requirement).
- Missing test coverage: No test exists for this requirement.
- Missing evidence: N/A
- Rationale: Interpretive, bibliographic, non-normative-by-design (explicitly marked informative/example), or document-self-referential statement. It does not describe a discrete, independently implementable system behavior.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: N/A

## MCC-TC-001-3-CERTIFICATE-MODEL-D01

- Specification / section: MCC-TC-001 / 3. Certificate Model / 3.2 Role in Certification
- Status: PARTIAL
- Requirement: A Technical Certificate SHALL NOT be issued where the Certification Decision is FAIL.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: certifications/manifest.json's CERTIFIED entries are a real, digest-identified (report_id), versioned, authoritative record of a successful certification outcome — the same concept this section describes, under a different name and without this specification's specific field structure.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-TC-001-3-CERTIFICATE-MODEL-D02

- Specification / section: MCC-TC-001 / 3. Certificate Model / 3.3 Relationship to Other Certification Artifacts
- Status: PARTIAL
- Requirement: A Technical Certificate MUST reference exactly one Certification Manifest, as defined by MCC-CM-001, by a direct Manifest Reference, per Section 6.5.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: certifications/manifest.json's CERTIFIED entries are a real, digest-identified (report_id), versioned, authoritative record of a successful certification outcome — the same concept this section describes, under a different name and without this specification's specific field structure.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-TC-001-3-CERTIFICATE-MODEL-D03

- Specification / section: MCC-TC-001 / 3. Certificate Model / 3.3 Relationship to Other Certification Artifacts
- Status: PARTIAL
- Requirement: A Technical Certificate MUST also reference, by a direct Evidence Bundle Reference per Section 6.6, the Evidence Bundle that substantiates its Certification Manifest.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: certifications/manifest.json's CERTIFIED entries are a real, digest-identified (report_id), versioned, authoritative record of a successful certification outcome — the same concept this section describes, under a different name and without this specification's specific field structure.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-TC-001-3-CERTIFICATE-MODEL-D04

- Specification / section: MCC-TC-001 / 3. Certificate Model / 3.3 Relationship to Other Certification Artifacts
- Status: PARTIAL
- Requirement: The Evidence Bundle identified by the Certificate's direct Evidence Bundle Reference MUST be the same Evidence Bundle identified by the Evidence Bundle Reference contained within the referenced Certification Manifest, as defined by MCC-CM-001, Section 14.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: certifications/manifest.json's CERTIFIED entries are a real, digest-identified (report_id), versioned, authoritative record of a successful certification outcome — the same concept this section describes, under a different name and without this specification's specific field structure.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-TC-001-3-CERTIFICATE-MODEL-D05

- Specification / section: MCC-TC-001 / 3. Certificate Model / 3.3 Relationship to Other Certification Artifacts
- Status: PARTIAL
- Requirement: A verifier MUST check this consistency, per Section 15.5.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: certifications/manifest.json's CERTIFIED entries are a real, digest-identified (report_id), versioned, authoritative record of a successful certification outcome — the same concept this section describes, under a different name and without this specification's specific field structure.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-TC-001-4-CERTIFICATE-SCHEMA-D01

- Specification / section: MCC-TC-001 / 4. Certificate Schema / 4.2 Top-Level Structure
- Status: PARTIAL
- Requirement: A Technical Certificate SHALL be a single structured, machine-readable document composed of the following field groups: - Certificate Identity, per Section 5; - Subject Identification, per Section 8; - Certification Result Representation, per Section 9; - Issuer Information, per Section 10; - Validity Period, per Section 11; - Manifest Reference, per Section 6.5; - Evidence Bundle Reference, per Section 6.6; - Signature, per Section 14; - Optional Fields, per Section 7; - Extension fields, per Section 20, where present.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: certifications/manifest.json's CERTIFIED entries are a real, digest-identified (report_id), versioned, authoritative record of a successful certification outcome — the same concept this section describes, under a different name and without this specification's specific field structure.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-TC-001-4-CERTIFICATE-SCHEMA-D02

- Specification / section: MCC-TC-001 / 4. Certificate Schema / 4.3 Field Typing
- Status: PARTIAL
- Requirement: Every Certificate field MUST have a defined type consistent with this specification: identifier, string, timestamp, enumerated value, Hash Reference, or signature value.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: certifications/manifest.json's CERTIFIED entries are a real, digest-identified (report_id), versioned, authoritative record of a successful certification outcome — the same concept this section describes, under a different name and without this specification's specific field structure.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-TC-001-4-CERTIFICATE-SCHEMA-D03

- Specification / section: MCC-TC-001 / 4. Certificate Schema / 4.3 Field Typing
- Status: PARTIAL
- Requirement: Certificate fields MUST NOT be ambiguous as to type.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: certifications/manifest.json's CERTIFIED entries are a real, digest-identified (report_id), versioned, authoritative record of a successful certification outcome — the same concept this section describes, under a different name and without this specification's specific field structure.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-TC-001-4-CERTIFICATE-SCHEMA-D04

- Specification / section: MCC-TC-001 / 4. Certificate Schema / 4.4 Canonical Form
- Status: PARTIAL
- Requirement: For any purpose requiring a Digest or signature over a Technical Certificate, the data covered MUST first be reduced to a deterministic Canonical Form, consistent with the Canonical Form requirement of MCC-EB-001, Section 13.2 and MCC-CM-001, Section 10.4.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: certifications/manifest.json's CERTIFIED entries are a real, digest-identified (report_id), versioned, authoritative record of a successful certification outcome — the same concept this section describes, under a different name and without this specification's specific field structure.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-TC-001-4-CERTIFICATE-SCHEMA-D05

- Specification / section: MCC-TC-001 / 4. Certificate Schema / 4.4 Canonical Form
- Status: PARTIAL
- Requirement: The Canonical Form used for signing MUST exclude the Signature field itself.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: certifications/manifest.json's CERTIFIED entries are a real, digest-identified (report_id), versioned, authoritative record of a successful certification outcome — the same concept this section describes, under a different name and without this specification's specific field structure.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-TC-001-5-CERTIFICATE-IDENTITY-D01

- Specification / section: MCC-TC-001 / 5. Certificate Identity / 5.2 Identity Fields
- Status: PARTIAL
- Requirement: Every Technical Certificate MUST include: - a certificate identifier, globally unique among Technical Certificates issued by the same Issuer; - the Certificate Schema Version; - the MCC-CP-001 specification version under which the underlying certification was performed.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: certifications/manifest.json's CERTIFIED entries are a real, digest-identified (report_id), versioned, authoritative record of a successful certification outcome — the same concept this section describes, under a different name and without this specification's specific field structure.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-TC-001-5-CERTIFICATE-IDENTITY-D02

- Specification / section: MCC-TC-001 / 5. Certificate Identity / 5.3 Identifier Stability
- Status: PARTIAL
- Requirement: A certificate identifier, once assigned, MUST NOT be reused for a different Technical Certificate, including after revocation of the original.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: certifications/manifest.json's CERTIFIED entries are a real, digest-identified (report_id), versioned, authoritative record of a successful certification outcome — the same concept this section describes, under a different name and without this specification's specific field structure.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-TC-001-5-CERTIFICATE-IDENTITY-D03

- Specification / section: MCC-TC-001 / 5. Certificate Identity / 5.3 Identifier Stability
- Status: PARTIAL
- Requirement: A revalidation that produces a new certification result MUST be issued as a new Technical Certificate with a new certificate identifier, consistent with MCC-CP-001, Sections 8.9 and 17.4.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: certifications/manifest.json's CERTIFIED entries are a real, digest-identified (report_id), versioned, authoritative record of a successful certification outcome — the same concept this section describes, under a different name and without this specification's specific field structure.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-TC-001-6-REQUIRED-FIELDS-D01

- Specification / section: MCC-TC-001 / 6. Required Fields / 6.1 Purpose
- Status: PARTIAL
- Requirement: Required Fields are the fields that MUST be present in every conforming Technical Certificate.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: Baseline fields (subject/adapter identity, specification/contract version, certification result, generation timestamp-equivalent) have real analogs in certifications/manifest.json; the Manifest Reference and Evidence Bundle Reference structured sub-objects this section also requires do not (see Section 6.5/6.6 rows in this matrix).
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-TC-001-6-REQUIRED-FIELDS-D02

- Specification / section: MCC-TC-001 / 6. Required Fields / 6.2 Baseline Required Fields
- Status: PARTIAL
- Requirement: Consistent with MCC-CP-001, Section 16.2, every Technical Certificate MUST include: - certificate identifier; - Certification Subject identifier; - specification version; - certification result; - certified capability profiles; - Certification Manifest reference, per Section 6.5; - Evidence Bundle reference, per Section 6.6; - issuance timestamp.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: Baseline fields (subject/adapter identity, specification/contract version, certification result, generation timestamp-equivalent) have real analogs in certifications/manifest.json; the Manifest Reference and Evidence Bundle Reference structured sub-objects this section also requires do not (see Section 6.5/6.6 rows in this matrix).
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-TC-001-6-REQUIRED-FIELDS-D03

- Specification / section: MCC-TC-001 / 6. Required Fields / 6.3 Additional Required Fields
- Status: PARTIAL
- Requirement: In addition to Section 6.2, every Technical Certificate MUST include: - Issuer identity, per Section 10; - Validity Period fields, per Section 11; - a Signature, per Section 14.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: Baseline fields (subject/adapter identity, specification/contract version, certification result, generation timestamp-equivalent) have real analogs in certifications/manifest.json; the Manifest Reference and Evidence Bundle Reference structured sub-objects this section also requires do not (see Section 6.5/6.6 rows in this matrix).
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-TC-001-6-REQUIRED-FIELDS-D04

- Specification / section: MCC-TC-001 / 6. Required Fields / 6.4 Field Presence Rule
- Status: PARTIAL
- Requirement: A Technical Certificate MUST NOT omit a Required Field.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: Baseline fields (subject/adapter identity, specification/contract version, certification result, generation timestamp-equivalent) have real analogs in certifications/manifest.json; the Manifest Reference and Evidence Bundle Reference structured sub-objects this section also requires do not (see Section 6.5/6.6 rows in this matrix).
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-TC-001-6-REQUIRED-FIELDS-D05

- Specification / section: MCC-TC-001 / 6. Required Fields / 6.4 Field Presence Rule
- Status: PARTIAL
- Requirement: A Certificate that omits any Required Field MUST be rejected under Section 15.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: Baseline fields (subject/adapter identity, specification/contract version, certification result, generation timestamp-equivalent) have real analogs in certifications/manifest.json; the Manifest Reference and Evidence Bundle Reference structured sub-objects this section also requires do not (see Section 6.5/6.6 rows in this matrix).
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-TC-001-6-REQUIRED-FIELDS-D06

- Specification / section: MCC-TC-001 / 6. Required Fields / 6.5 Manifest Reference Structure
- Status: PARTIAL
- Requirement: The Manifest Reference MUST include: - the Certification Manifest identifier; - the Manifest Schema Version, as defined by MCC-CM-001, Section 16.2; - a Hash Reference binding the Certificate to that Certification Manifest, using the Hash Reference model defined by MCC-CM-001, Section 13.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: Baseline fields (subject/adapter identity, specification/contract version, certification result, generation timestamp-equivalent) have real analogs in certifications/manifest.json; the Manifest Reference and Evidence Bundle Reference structured sub-objects this section also requires do not (see Section 6.5/6.6 rows in this matrix).
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-TC-001-6-REQUIRED-FIELDS-D07

- Specification / section: MCC-TC-001 / 6. Required Fields / 6.6 Evidence Bundle Reference Structure
- Status: PARTIAL
- Requirement: The Evidence Bundle Reference MUST be present as direct Certificate content.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: Baseline fields (subject/adapter identity, specification/contract version, certification result, generation timestamp-equivalent) have real analogs in certifications/manifest.json; the Manifest Reference and Evidence Bundle Reference structured sub-objects this section also requires do not (see Section 6.5/6.6 rows in this matrix).
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-TC-001-6-REQUIRED-FIELDS-D08

- Specification / section: MCC-TC-001 / 6. Required Fields / 6.6 Evidence Bundle Reference Structure
- Status: PARTIAL
- Requirement: It MUST NOT be satisfied only by transitive resolution through the Certification Manifest.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: Baseline fields (subject/adapter identity, specification/contract version, certification result, generation timestamp-equivalent) have real analogs in certifications/manifest.json; the Manifest Reference and Evidence Bundle Reference structured sub-objects this section also requires do not (see Section 6.5/6.6 rows in this matrix).
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-TC-001-6-REQUIRED-FIELDS-D09

- Specification / section: MCC-TC-001 / 6. Required Fields / 6.6 Evidence Bundle Reference Structure
- Status: PARTIAL
- Requirement: The Evidence Bundle Reference MUST include: - the Evidence Bundle identifier, as defined by MCC-EB-001, Section 12.1; - the Evidence Bundle Schema Version, as defined by MCC-EB-001, Section 17.2; - a Hash Reference binding the Certificate to that Evidence Bundle's Integrity Record, using the same normative Hash Reference model defined by MCC-EB-001, Section 13, and used by MCC-CM-001, Section 13, for the equivalent binding within a Certification Manifest.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: Baseline fields (subject/adapter identity, specification/contract version, certification result, generation timestamp-equivalent) have real analogs in certifications/manifest.json; the Manifest Reference and Evidence Bundle Reference structured sub-objects this section also requires do not (see Section 6.5/6.6 rows in this matrix).
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-TC-001-6-REQUIRED-FIELDS-D10

- Specification / section: MCC-TC-001 / 6. Required Fields / 6.6 Evidence Bundle Reference Structure
- Status: PARTIAL
- Requirement: The Evidence Bundle identified by this Hash Reference MUST be the same Evidence Bundle identified by the Evidence Bundle Reference contained within the Certificate's referenced Certification Manifest, consistent with Section 3.3 and Section 15.5.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: Baseline fields (subject/adapter identity, specification/contract version, certification result, generation timestamp-equivalent) have real analogs in certifications/manifest.json; the Manifest Reference and Evidence Bundle Reference structured sub-objects this section also requires do not (see Section 6.5/6.6 rows in this matrix).
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-TC-001-7-OPTIONAL-FIELDS-D01

- Specification / section: MCC-TC-001 / 7. Optional Fields / 7.3 Optional Field Constraints
- Status: GAP
- Requirement: An Optional Field, where present, MUST conform to the type rules of Section 4.3.
- Existing implementation: None
- Missing implementation behavior: Full requirement not implemented.
- Missing test coverage: No test exists for this requirement.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: No optional-field mechanism for a certification record was found.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-TC-001-7-OPTIONAL-FIELDS-D02

- Specification / section: MCC-TC-001 / 7. Optional Fields / 7.3 Optional Field Constraints
- Status: GAP
- Requirement: The absence of an Optional Field MUST NOT be treated as a validation failure.
- Existing implementation: None
- Missing implementation behavior: Full requirement not implemented.
- Missing test coverage: No test exists for this requirement.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: No optional-field mechanism for a certification record was found.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-TC-001-7-OPTIONAL-FIELDS-D03

- Specification / section: MCC-TC-001 / 7. Optional Fields / 7.3 Optional Field Constraints
- Status: GAP
- Requirement: An Optional Field MUST NOT be used to satisfy a Required Field obligation defined in Section 6.
- Existing implementation: None
- Missing implementation behavior: Full requirement not implemented.
- Missing test coverage: No test exists for this requirement.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: No optional-field mechanism for a certification record was found.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-TC-001-8-SUBJECT-IDENTIFICATION-D01

- Specification / section: MCC-TC-001 / 8. Subject Identification / 8.2 Subject Field
- Status: PARTIAL
- Requirement: A Technical Certificate MUST identify exactly one Certification Subject, using the Certification Subject identifier defined by MCC-CP-001, Section 7.2.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: adapter_key / implementation_id in certifications/manifest.json identify exactly one subject per record, the same one-subject-per-record model this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-TC-001-8-SUBJECT-IDENTIFICATION-D02

- Specification / section: MCC-TC-001 / 8. Subject Identification / 8.2 Subject Field
- Status: PARTIAL
- Requirement: A Technical Certificate MUST NOT apply to more than one Certification Subject.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: adapter_key / implementation_id in certifications/manifest.json identify exactly one subject per record, the same one-subject-per-record model this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-TC-001-8-SUBJECT-IDENTIFICATION-D03

- Specification / section: MCC-TC-001 / 8. Subject Identification / 8.3 Subject Consistency
- Status: PARTIAL
- Requirement: The Certification Subject identified by a Technical Certificate MUST match the Certification Subject identified by the Certification Manifest it references.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: adapter_key / implementation_id in certifications/manifest.json identify exactly one subject per record, the same one-subject-per-record model this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-TC-001-8-SUBJECT-IDENTIFICATION-D04

- Specification / section: MCC-TC-001 / 8. Subject Identification / 8.3 Subject Consistency
- Status: PARTIAL
- Requirement: A mismatch MUST cause verification to fail under Section 15.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: adapter_key / implementation_id in certifications/manifest.json identify exactly one subject per record, the same one-subject-per-record model this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-TC-001-9-CERTIFICATION-RESULT-REPRESENTATION-D01

- Specification / section: MCC-TC-001 / 9. Certification Result Representation / 9.2 Result Value
- Status: PARTIAL
- Requirement: A Technical Certificate MUST record its certification result as exactly PASS, consistent with MCC-CP-001, Sections 8.6 and 9.6, and Section 3.2 of this specification.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: status=CERTIFIED is issued only for a fully-passing compliance run (fail-closed: every mandatory vector must pass, per reporting.py), the same PASS-only issuance model this section requires, though the verdict vocabulary (CERTIFIED vs. PASS) differs.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-TC-001-9-CERTIFICATION-RESULT-REPRESENTATION-D02

- Specification / section: MCC-TC-001 / 9. Certification Result Representation / 9.2 Result Value
- Status: PARTIAL
- Requirement: A Technical Certificate MUST NOT record a certification result of FAIL. No Certificate model exists for a FAIL outcome, since Certificates are never issued for a FAIL certification result.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: status=CERTIFIED is issued only for a fully-passing compliance run (fail-closed: every mandatory vector must pass, per reporting.py), the same PASS-only issuance model this section requires, though the verdict vocabulary (CERTIFIED vs. PASS) differs.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-TC-001-9-CERTIFICATION-RESULT-REPRESENTATION-D03

- Specification / section: MCC-TC-001 / 9. Certification Result Representation / 9.3 Result Consistency
- Status: PARTIAL
- Requirement: The certification result recorded by a Technical Certificate MUST match the certification result recorded by the Certification Manifest it references.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: status=CERTIFIED is issued only for a fully-passing compliance run (fail-closed: every mandatory vector must pass, per reporting.py), the same PASS-only issuance model this section requires, though the verdict vocabulary (CERTIFIED vs. PASS) differs.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-TC-001-9-CERTIFICATION-RESULT-REPRESENTATION-D04

- Specification / section: MCC-TC-001 / 9. Certification Result Representation / 9.3 Result Consistency
- Status: PARTIAL
- Requirement: A mismatch MUST cause verification to fail under Section 15.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: status=CERTIFIED is issued only for a fully-passing compliance run (fail-closed: every mandatory vector must pass, per reporting.py), the same PASS-only issuance model this section requires, though the verdict vocabulary (CERTIFIED vs. PASS) differs.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-TC-001-9-CERTIFICATION-RESULT-REPRESENTATION-D05

- Specification / section: MCC-TC-001 / 9. Certification Result Representation / 9.4 Certified Capability Profiles
- Status: PARTIAL
- Requirement: A Technical Certificate MUST record the capability profiles verified during certification, consistent with MCC-CP-001, Section 11.6.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: status=CERTIFIED is issued only for a fully-passing compliance run (fail-closed: every mandatory vector must pass, per reporting.py), the same PASS-only issuance model this section requires, though the verdict vocabulary (CERTIFIED vs. PASS) differs.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-TC-001-9-CERTIFICATION-RESULT-REPRESENTATION-D06

- Specification / section: MCC-TC-001 / 9. Certification Result Representation / 9.4 Certified Capability Profiles
- Status: PARTIAL
- Requirement: A capability profile MUST NOT appear as certified on a Technical Certificate unless it was verified during the certification the Certificate attests to.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: status=CERTIFIED is issued only for a fully-passing compliance run (fail-closed: every mandatory vector must pass, per reporting.py), the same PASS-only issuance model this section requires, though the verdict vocabulary (CERTIFIED vs. PASS) differs.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## MCC-TC-001-ABSTRACT-D01

- Specification / section: MCC-TC-001 / Abstract
- Status: NOT_APPLICABLE
- Requirement: A Technical Certificate SHALL remain framework-neutral and implementation-independent, and SHALL be independently verifiable by a party holding only the Certificate, a recognized Trust Anchor, and this specification.
- Existing implementation: None
- Missing implementation behavior: N/A (not an implementable requirement).
- Missing test coverage: No test exists for this requirement.
- Missing evidence: N/A
- Rationale: Interpretive, bibliographic, non-normative-by-design (explicitly marked informative/example), or document-self-referential statement. It does not describe a discrete, independently implementable system behavior.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: N/A

## MCC-TC-001-ABSTRACT-D02

- Specification / section: MCC-TC-001 / Abstract
- Status: NOT_APPLICABLE
- Requirement: It is not, and SHALL NOT be interpreted as, a runtime execution authorization.
- Existing implementation: None
- Missing implementation behavior: N/A (not an implementable requirement).
- Missing test coverage: No test exists for this requirement.
- Missing evidence: N/A
- Rationale: Interpretive, bibliographic, non-normative-by-design (explicitly marked informative/example), or document-self-referential statement. It does not describe a discrete, independently implementable system behavior.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: N/A

## MCC-TC-001-STATUS-OF-THIS-SPECIFICATION-D01

- Specification / section: MCC-TC-001 / Status of This Specification
- Status: NOT_APPLICABLE
- Requirement: The key words MUST, MUST NOT, REQUIRED, SHALL, SHALL NOT, SHOULD, SHOULD NOT, RECOMMENDED, MAY and OPTIONAL in this specification are to be interpreted as described in RFC 2119 and RFC 8174.
- Existing implementation: None
- Missing implementation behavior: N/A (not an implementable requirement).
- Missing test coverage: No test exists for this requirement.
- Missing evidence: N/A
- Rationale: Interpretive, bibliographic, non-normative-by-design (explicitly marked informative/example), or document-self-referential statement. It does not describe a discrete, independently implementable system behavior.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: N/A

## TC-COMPAT-001

- Specification / section: MCC-TC-001 / 17. Compatibility / 17.5 Compatibility Invariants
- Status: PARTIAL
- Requirement: Compatibility claims between Certificate Schema Versions MUST be explicit, not assumed.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: Independent schema/contract versioning exists for the compliance-manifest artifact family (compliance_suite_version, contract_version, MANIFEST_SCHEMA_VERSION), the same independent-tracking model this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## TC-COMPAT-002

- Specification / section: MCC-TC-001 / 17. Compatibility / 17.5 Compatibility Invariants
- Status: PARTIAL
- Requirement: Unrecognized Certificate Schema Versions MUST NOT be silently accepted.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: Independent schema/contract versioning exists for the compliance-manifest artifact family (compliance_suite_version, contract_version, MANIFEST_SCHEMA_VERSION), the same independent-tracking model this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## TC-COMPAT-003

- Specification / section: MCC-TC-001 / 17. Compatibility / 17.5 Compatibility Invariants
- Status: PARTIAL
- Requirement: Certificate validity MUST account for the compatibility of any referenced Manifest Schema Version.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: Independent schema/contract versioning exists for the compliance-manifest artifact family (compliance_suite_version, contract_version, MANIFEST_SCHEMA_VERSION), the same independent-tracking model this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## TC-COMPAT-004

- Specification / section: MCC-TC-001 / 17. Compatibility / 17.5 Compatibility Invariants
- Status: PARTIAL
- Requirement: Certificate validity MUST account for the compatibility of the Evidence Bundle Schema Version identified by the direct Evidence Bundle Reference.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: Independent schema/contract versioning exists for the compliance-manifest artifact family (compliance_suite_version, contract_version, MANIFEST_SCHEMA_VERSION), the same independent-tracking model this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## TC-CONF-001

- Specification / section: MCC-TC-001 / 21. Conformance Requirements / 21.5 Conformance Invariants
- Status: GAP
- Requirement: Conformance is defined separately for Certificate issuers and Certificate verifiers.
- Existing implementation: None
- Missing implementation behavior: Full requirement not implemented.
- Missing test coverage: No test exists for this requirement.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: No issuer/verifier conformance-declaration mechanism specific to this specification's Certificate Schema Version was found.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## TC-CONF-002

- Specification / section: MCC-TC-001 / 21. Conformance Requirements / 21.5 Conformance Invariants
- Status: GAP
- Requirement: A conforming issuer MUST NOT issue Certificates for a non-PASS result.
- Existing implementation: None
- Missing implementation behavior: Full requirement not implemented.
- Missing test coverage: No test exists for this requirement.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: No issuer/verifier conformance-declaration mechanism specific to this specification's Certificate Schema Version was found.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## TC-CONF-003

- Specification / section: MCC-TC-001 / 21. Conformance Requirements / 21.5 Conformance Invariants
- Status: GAP
- Requirement: A conforming verifier MUST implement fail-closed verification in full, including revocation checking.
- Existing implementation: None
- Missing implementation behavior: Full requirement not implemented.
- Missing test coverage: No test exists for this requirement.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: No issuer/verifier conformance-declaration mechanism specific to this specification's Certificate Schema Version was found.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## TC-CONF-004

- Specification / section: MCC-TC-001 / 21. Conformance Requirements / 21.5 Conformance Invariants
- Status: GAP
- Requirement: Conformance MUST remain framework-neutral and implementation-independent.
- Existing implementation: None
- Missing implementation behavior: Full requirement not implemented.
- Missing test coverage: No test exists for this requirement.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: No issuer/verifier conformance-declaration mechanism specific to this specification's Certificate Schema Version was found.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## TC-CONF-005

- Specification / section: MCC-TC-001 / 21. Conformance Requirements / 21.5 Conformance Invariants
- Status: GAP
- Requirement: A conforming issuer MUST ensure its direct Evidence Bundle Reference and its Certification Manifest's Evidence Bundle Reference identify the same Evidence Bundle before issuance.
- Existing implementation: None
- Missing implementation behavior: Full requirement not implemented.
- Missing test coverage: No test exists for this requirement.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: No issuer/verifier conformance-declaration mechanism specific to this specification's Certificate Schema Version was found.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## TC-EXT-001

- Specification / section: MCC-TC-001 / 20. Extension Model / 20.4 Extension Model Invariants
- Status: GAP
- Requirement: Extensions MUST be explicitly declared within the Certificate.
- Existing implementation: None
- Missing implementation behavior: Full requirement not implemented.
- Missing test coverage: No test exists for this requirement.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: No extension-declaration mechanism (a way to mark additional fields as explicit, non-breaking extensions to a committed schema) was found anywhere in this repository for any artifact.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## TC-EXT-002

- Specification / section: MCC-TC-001 / 20. Extension Model / 20.4 Extension Model Invariants
- Status: GAP
- Requirement: Extensions MUST NOT redefine the meaning of Required Fields, the Signature, the Manifest Reference, or the Evidence Bundle Reference.
- Existing implementation: None
- Missing implementation behavior: Full requirement not implemented.
- Missing test coverage: No test exists for this requirement.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: No extension-declaration mechanism (a way to mark additional fields as explicit, non-breaking extensions to a committed schema) was found anywhere in this repository for any artifact.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## TC-EXT-003

- Specification / section: MCC-TC-001 / 20. Extension Model / 20.4 Extension Model Invariants
- Status: GAP
- Requirement: Extension content MUST be covered by the Certificate's Signature.
- Existing implementation: None
- Missing implementation behavior: Full requirement not implemented.
- Missing test coverage: No test exists for this requirement.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: No extension-declaration mechanism (a way to mark additional fields as explicit, non-breaking extensions to a committed schema) was found anywhere in this repository for any artifact.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## TC-EXT-004

- Specification / section: MCC-TC-001 / 20. Extension Model / 20.4 Extension Model Invariants
- Status: GAP
- Requirement: Unrecognized extensions MUST be ignored, not treated as verification failures.
- Existing implementation: None
- Missing implementation behavior: Full requirement not implemented.
- Missing test coverage: No test exists for this requirement.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: No extension-declaration mechanism (a way to mark additional fields as explicit, non-breaking extensions to a committed schema) was found anywhere in this repository for any artifact.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## TC-HASH-001

- Specification / section: MCC-TC-001 / 13. Cryptographic Integrity / 13.4 Cryptographic Integrity Invariants
- Status: PARTIAL
- Requirement: A Hash Reference to the Certification Manifest or to the Evidence Bundle MUST use a collision-resistant hash algorithm.
- Existing implementation: src/mcc_core/signing.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_core/signing.py provides the collision-resistant digest primitive this section requires; src/mcc_evidence/verify.py demonstrates it applied to binding a signed artifact to referenced content, though not to a Technical Certificate specifically.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## TC-HASH-002

- Specification / section: MCC-TC-001 / 13. Cryptographic Integrity / 13.4 Cryptographic Integrity Invariants
- Status: PARTIAL
- Requirement: Manifest and Evidence Bundle binding MUST each be independently recomputable and verifiable.
- Existing implementation: src/mcc_core/signing.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_core/signing.py provides the collision-resistant digest primitive this section requires; src/mcc_evidence/verify.py demonstrates it applied to binding a signed artifact to referenced content, though not to a Technical Certificate specifically.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## TC-HASH-003

- Specification / section: MCC-TC-001 / 13. Cryptographic Integrity / 13.4 Cryptographic Integrity Invariants
- Status: PARTIAL
- Requirement: Whole-Certificate integrity MUST be provided by its Signature, not by a separate mechanism.
- Existing implementation: src/mcc_core/signing.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_core/signing.py provides the collision-resistant digest primitive this section requires; src/mcc_evidence/verify.py demonstrates it applied to binding a signed artifact to referenced content, though not to a Technical Certificate specifically.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## TC-ID-001

- Specification / section: MCC-TC-001 / 5. Certificate Identity / 5.4 Certificate Identity Invariants
- Status: PARTIAL
- Requirement: Every Technical Certificate MUST have a globally unique certificate identifier.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: certifications/manifest.json's CERTIFIED entries are a real, digest-identified (report_id), versioned, authoritative record of a successful certification outcome — the same concept this section describes, under a different name and without this specification's specific field structure.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## TC-ID-002

- Specification / section: MCC-TC-001 / 5. Certificate Identity / 5.4 Certificate Identity Invariants
- Status: PARTIAL
- Requirement: Certificate identifiers MUST NOT be reused, including after revocation.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: certifications/manifest.json's CERTIFIED entries are a real, digest-identified (report_id), versioned, authoritative record of a successful certification outcome — the same concept this section describes, under a different name and without this specification's specific field structure.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## TC-ID-003

- Specification / section: MCC-TC-001 / 5. Certificate Identity / 5.4 Certificate Identity Invariants
- Status: PARTIAL
- Requirement: A revalidation MUST produce a new Technical Certificate with a new certificate identifier.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: certifications/manifest.json's CERTIFIED entries are a real, digest-identified (report_id), versioned, authoritative record of a successful certification outcome — the same concept this section describes, under a different name and without this specification's specific field structure.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## TC-ISS-001

- Specification / section: MCC-TC-001 / 10. Issuer Information / 10.4 Issuer Information Invariants
- Status: PARTIAL
- Requirement: A Technical Certificate MUST identify its Issuer.
- Existing implementation: gateway/trust.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: gateway/trust.py implements a real, tested per-issuer Ed25519 key model (the Issuer/Trust Anchor concept this section requires), but it is not wired to certifications/manifest.json entries, which instead carry only an informal issuer statement (CERTIFICATION_NOTE).
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## TC-ISS-002

- Specification / section: MCC-TC-001 / 10. Issuer Information / 10.4 Issuer Information Invariants
- Status: PARTIAL
- Requirement: The Issuer identifier MUST be associated with a resolvable Trust Anchor.
- Existing implementation: gateway/trust.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: gateway/trust.py implements a real, tested per-issuer Ed25519 key model (the Issuer/Trust Anchor concept this section requires), but it is not wired to certifications/manifest.json entries, which instead carry only an informal issuer statement (CERTIFICATION_NOTE).
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## TC-ISS-003

- Specification / section: MCC-TC-001 / 10. Issuer Information / 10.4 Issuer Information Invariants
- Status: PARTIAL
- Requirement: An unrecognized Issuer MUST cause verification to fail.
- Existing implementation: gateway/trust.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: gateway/trust.py implements a real, tested per-issuer Ed25519 key model (the Issuer/Trust Anchor concept this section requires), but it is not wired to certifications/manifest.json entries, which instead carry only an informal issuer statement (CERTIFICATION_NOTE).
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## TC-MODEL-001

- Specification / section: MCC-TC-001 / 3. Certificate Model / 3.5 Certificate Model Invariants
- Status: PARTIAL
- Requirement: A Technical Certificate MUST represent exactly one successful (PASS) certification outcome.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: certifications/manifest.json's CERTIFIED entries are a real, digest-identified (report_id), versioned, authoritative record of a successful certification outcome — the same concept this section describes, under a different name and without this specification's specific field structure.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## TC-MODEL-002

- Specification / section: MCC-TC-001 / 3. Certificate Model / 3.5 Certificate Model Invariants
- Status: PARTIAL
- Requirement: A Technical Certificate MUST reference exactly one Certification Manifest.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: certifications/manifest.json's CERTIFIED entries are a real, digest-identified (report_id), versioned, authoritative record of a successful certification outcome — the same concept this section describes, under a different name and without this specification's specific field structure.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## TC-MODEL-003

- Specification / section: MCC-TC-001 / 3. Certificate Model / 3.5 Certificate Model Invariants
- Status: PARTIAL
- Requirement: A Technical Certificate MUST NOT be interpreted or used as a runtime execution authorization.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: certifications/manifest.json's CERTIFIED entries are a real, digest-identified (report_id), versioned, authoritative record of a successful certification outcome — the same concept this section describes, under a different name and without this specification's specific field structure.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## TC-MODEL-004

- Specification / section: MCC-TC-001 / 3. Certificate Model / 3.5 Certificate Model Invariants
- Status: PARTIAL
- Requirement: A Technical Certificate MUST remain traceable to the Certification Subject, specification version, Certification Manifest, and Evidence Bundle, by direct reference in every case.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: certifications/manifest.json's CERTIFIED entries are a real, digest-identified (report_id), versioned, authoritative record of a successful certification outcome — the same concept this section describes, under a different name and without this specification's specific field structure.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## TC-OPTF-001

- Specification / section: MCC-TC-001 / 7. Optional Fields / 7.4 Optional Fields Invariants
- Status: GAP
- Requirement: Optional Fields MAY be omitted without affecting Certificate validity.
- Existing implementation: None
- Missing implementation behavior: Full requirement not implemented.
- Missing test coverage: No test exists for this requirement.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: No optional-field mechanism for a certification record was found.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## TC-OPTF-002

- Specification / section: MCC-TC-001 / 7. Optional Fields / 7.4 Optional Fields Invariants
- Status: GAP
- Requirement: Optional Fields, where present, MUST conform to defined type rules.
- Existing implementation: None
- Missing implementation behavior: Full requirement not implemented.
- Missing test coverage: No test exists for this requirement.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: No optional-field mechanism for a certification record was found.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## TC-OPTF-003

- Specification / section: MCC-TC-001 / 7. Optional Fields / 7.4 Optional Fields Invariants
- Status: GAP
- Requirement: Optional Fields MUST NOT substitute for Required Fields.
- Existing implementation: None
- Missing implementation behavior: Full requirement not implemented.
- Missing test coverage: No test exists for this requirement.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: No optional-field mechanism for a certification record was found.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## TC-RES-001

- Specification / section: MCC-TC-001 / 9. Certification Result Representation / 9.5 Certification Result Representation Invariants
- Status: PARTIAL
- Requirement: The certification result field MUST be present and MUST be PASS.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: status=CERTIFIED is issued only for a fully-passing compliance run (fail-closed: every mandatory vector must pass, per reporting.py), the same PASS-only issuance model this section requires, though the verdict vocabulary (CERTIFIED vs. PASS) differs.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## TC-RES-002

- Specification / section: MCC-TC-001 / 9. Certification Result Representation / 9.5 Certification Result Representation Invariants
- Status: PARTIAL
- Requirement: The Certificate's result MUST match its referenced Manifest's result.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: status=CERTIFIED is issued only for a fully-passing compliance run (fail-closed: every mandatory vector must pass, per reporting.py), the same PASS-only issuance model this section requires, though the verdict vocabulary (CERTIFIED vs. PASS) differs.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## TC-RES-003

- Specification / section: MCC-TC-001 / 9. Certification Result Representation / 9.5 Certification Result Representation Invariants
- Status: PARTIAL
- Requirement: Certified capability profiles MUST be limited to those actually verified.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: status=CERTIFIED is issued only for a fully-passing compliance run (fail-closed: every mandatory vector must pass, per reporting.py), the same PASS-only issuance model this section requires, though the verdict vocabulary (CERTIFIED vs. PASS) differs.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## TC-REV-001

- Specification / section: MCC-TC-001 / 12. Revocation Model / 12.7 Revocation Model Invariants
- Status: PARTIAL
- Requirement: A Technical Certificate MUST NOT be mutated to represent revocation.
- Existing implementation: gateway/trust.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: gateway/trust.py implements a real, tested REVOKED_KEY status and fail-closed unresolved/revoked-key handling — the same external-revocation-record, verifier-must-check model this section requires, scoped to trust/mandate keys rather than a Technical Certificate's own Revocation Record.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## TC-REV-002

- Specification / section: MCC-TC-001 / 12. Revocation Model / 12.7 Revocation Model Invariants
- Status: PARTIAL
- Requirement: Revocation MUST be represented by an external Revocation Record.
- Existing implementation: gateway/trust.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: gateway/trust.py implements a real, tested REVOKED_KEY status and fail-closed unresolved/revoked-key handling — the same external-revocation-record, verifier-must-check model this section requires, scoped to trust/mandate keys rather than a Technical Certificate's own Revocation Record.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## TC-REV-003

- Specification / section: MCC-TC-001 / 12. Revocation Model / 12.7 Revocation Model Invariants
- Status: PARTIAL
- Requirement: A Revocation Record MUST identify the certificate identifier, revocation timestamp, and authorizing Issuer.
- Existing implementation: gateway/trust.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: gateway/trust.py implements a real, tested REVOKED_KEY status and fail-closed unresolved/revoked-key handling — the same external-revocation-record, verifier-must-check model this section requires, scoped to trust/mandate keys rather than a Technical Certificate's own Revocation Record.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## TC-REV-004

- Specification / section: MCC-TC-001 / 12. Revocation Model / 12.7 Revocation Model Invariants
- Status: PARTIAL
- Requirement: Only the Issuer, or its designated authority under the Trust Model, MUST be able to produce a valid Revocation Record.
- Existing implementation: gateway/trust.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: gateway/trust.py implements a real, tested REVOKED_KEY status and fail-closed unresolved/revoked-key handling — the same external-revocation-record, verifier-must-check model this section requires, scoped to trust/mandate keys rather than a Technical Certificate's own Revocation Record.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## TC-REV-005

- Specification / section: MCC-TC-001 / 12. Revocation Model / 12.7 Revocation Model Invariants
- Status: PARTIAL
- Requirement: A verifier MUST check for revocation before treating a Certificate as valid.
- Existing implementation: gateway/trust.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: gateway/trust.py implements a real, tested REVOKED_KEY status and fail-closed unresolved/revoked-key handling — the same external-revocation-record, verifier-must-check model this section requires, scoped to trust/mandate keys rather than a Technical Certificate's own Revocation Record.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## TC-REV-006

- Specification / section: MCC-TC-001 / 12. Revocation Model / 12.7 Revocation Model Invariants
- Status: PARTIAL
- Requirement: Revoked Certificates MUST remain available for audit and traceability.
- Existing implementation: gateway/trust.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: gateway/trust.py implements a real, tested REVOKED_KEY status and fail-closed unresolved/revoked-key handling — the same external-revocation-record, verifier-must-check model this section requires, scoped to trust/mandate keys rather than a Technical Certificate's own Revocation Record.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## TC-RFLD-001

- Specification / section: MCC-TC-001 / 6. Required Fields / 6.7 Required Fields Invariants
- Status: PARTIAL
- Requirement: All fields listed in Section 6.2 MUST be present.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: Baseline fields (subject/adapter identity, specification/contract version, certification result, generation timestamp-equivalent) have real analogs in certifications/manifest.json; the Manifest Reference and Evidence Bundle Reference structured sub-objects this section also requires do not (see Section 6.5/6.6 rows in this matrix).
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## TC-RFLD-002

- Specification / section: MCC-TC-001 / 6. Required Fields / 6.7 Required Fields Invariants
- Status: PARTIAL
- Requirement: Issuer identity, Validity Period fields, and a Signature MUST be present.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: Baseline fields (subject/adapter identity, specification/contract version, certification result, generation timestamp-equivalent) have real analogs in certifications/manifest.json; the Manifest Reference and Evidence Bundle Reference structured sub-objects this section also requires do not (see Section 6.5/6.6 rows in this matrix).
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## TC-RFLD-003

- Specification / section: MCC-TC-001 / 6. Required Fields / 6.7 Required Fields Invariants
- Status: PARTIAL
- Requirement: A Certificate omitting any Required Field MUST be rejected.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: Baseline fields (subject/adapter identity, specification/contract version, certification result, generation timestamp-equivalent) have real analogs in certifications/manifest.json; the Manifest Reference and Evidence Bundle Reference structured sub-objects this section also requires do not (see Section 6.5/6.6 rows in this matrix).
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## TC-RFLD-004

- Specification / section: MCC-TC-001 / 6. Required Fields / 6.7 Required Fields Invariants
- Status: PARTIAL
- Requirement: The Manifest Reference MUST include the Manifest identifier, the Manifest Schema Version, and a Hash Reference to the Certification Manifest.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: Baseline fields (subject/adapter identity, specification/contract version, certification result, generation timestamp-equivalent) have real analogs in certifications/manifest.json; the Manifest Reference and Evidence Bundle Reference structured sub-objects this section also requires do not (see Section 6.5/6.6 rows in this matrix).
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## TC-RFLD-005

- Specification / section: MCC-TC-001 / 6. Required Fields / 6.7 Required Fields Invariants
- Status: PARTIAL
- Requirement: The Evidence Bundle Reference MUST include the Evidence Bundle identifier, the Evidence Bundle Schema Version, and a Hash Reference to the Evidence Bundle.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: Baseline fields (subject/adapter identity, specification/contract version, certification result, generation timestamp-equivalent) have real analogs in certifications/manifest.json; the Manifest Reference and Evidence Bundle Reference structured sub-objects this section also requires do not (see Section 6.5/6.6 rows in this matrix).
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## TC-RFLD-006

- Specification / section: MCC-TC-001 / 6. Required Fields / 6.7 Required Fields Invariants
- Status: PARTIAL
- Requirement: The Evidence Bundle Reference MUST be direct Certificate content and MUST NOT be satisfied only by transitive resolution through the Certification Manifest.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: Baseline fields (subject/adapter identity, specification/contract version, certification result, generation timestamp-equivalent) have real analogs in certifications/manifest.json; the Manifest Reference and Evidence Bundle Reference structured sub-objects this section also requires do not (see Section 6.5/6.6 rows in this matrix).
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## TC-RID-001

- Specification / section: MCC-TC-001 / 22. Requirement Identifier Registry / 22.5 Registry Invariants
- Status: NOT_APPLICABLE
- Requirement: All identifiers defined by this specification MUST use the `TC-` namespace prefix.
- Existing implementation: None
- Missing implementation behavior: N/A (not an implementable requirement).
- Missing test coverage: No test exists for this requirement.
- Missing evidence: N/A
- Rationale: Interpretive, bibliographic, non-normative-by-design (explicitly marked informative/example), or document-self-referential statement. It does not describe a discrete, independently implementable system behavior.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: N/A

## TC-RID-002

- Specification / section: MCC-TC-001 / 22. Requirement Identifier Registry / 22.5 Registry Invariants
- Status: NOT_APPLICABLE
- Requirement: Identifiers within the `TC-` namespace MUST be globally unique.
- Existing implementation: None
- Missing implementation behavior: N/A (not an implementable requirement).
- Missing test coverage: No test exists for this requirement.
- Missing evidence: N/A
- Rationale: Interpretive, bibliographic, non-normative-by-design (explicitly marked informative/example), or document-self-referential statement. It does not describe a discrete, independently implementable system behavior.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: N/A

## TC-RID-003

- Specification / section: MCC-TC-001 / 22. Requirement Identifier Registry / 22.5 Registry Invariants
- Status: NOT_APPLICABLE
- Requirement: Retired identifiers MUST NOT be reassigned to a different requirement.
- Existing implementation: None
- Missing implementation behavior: N/A (not an implementable requirement).
- Missing test coverage: No test exists for this requirement.
- Missing evidence: N/A
- Rationale: Interpretive, bibliographic, non-normative-by-design (explicitly marked informative/example), or document-self-referential statement. It does not describe a discrete, independently implementable system behavior.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: N/A

## TC-RID-004

- Specification / section: MCC-TC-001 / 22. Requirement Identifier Registry / 22.5 Registry Invariants
- Status: NOT_APPLICABLE
- Requirement: New category tags MUST NOT collide with prefixes already registered by another MCC specification.
- Existing implementation: None
- Missing implementation behavior: N/A (not an implementable requirement).
- Missing test coverage: No test exists for this requirement.
- Missing evidence: N/A
- Rationale: Interpretive, bibliographic, non-normative-by-design (explicitly marked informative/example), or document-self-referential statement. It does not describe a discrete, independently implementable system behavior.
- Recommended remediation scope: LARGE
- May affect public interfaces / governance semantics: N/A

## TC-SCHEMA-001

- Specification / section: MCC-TC-001 / 4. Certificate Schema / 4.5 Certificate Schema Invariants
- Status: PARTIAL
- Requirement: A Technical Certificate MUST be a single structured, machine-readable document.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: certifications/manifest.json's CERTIFIED entries are a real, digest-identified (report_id), versioned, authoritative record of a successful certification outcome — the same concept this section describes, under a different name and without this specification's specific field structure.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## TC-SCHEMA-002

- Specification / section: MCC-TC-001 / 4. Certificate Schema / 4.5 Certificate Schema Invariants
- Status: PARTIAL
- Requirement: Every Certificate field MUST have an unambiguous, defined type.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: certifications/manifest.json's CERTIFIED entries are a real, digest-identified (report_id), versioned, authoritative record of a successful certification outcome — the same concept this section describes, under a different name and without this specification's specific field structure.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## TC-SCHEMA-003

- Specification / section: MCC-TC-001 / 4. Certificate Schema / 4.5 Certificate Schema Invariants
- Status: PARTIAL
- Requirement: The top-level field groups defined in Section 4.2 MUST all be present, except where explicitly marked optional.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: certifications/manifest.json's CERTIFIED entries are a real, digest-identified (report_id), versioned, authoritative record of a successful certification outcome — the same concept this section describes, under a different name and without this specification's specific field structure.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## TC-SCHEMA-004

- Specification / section: MCC-TC-001 / 4. Certificate Schema / 4.5 Certificate Schema Invariants
- Status: PARTIAL
- Requirement: Signature computation MUST use a deterministic Canonical Form that excludes the Signature field.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: certifications/manifest.json's CERTIFIED entries are a real, digest-identified (report_id), versioned, authoritative record of a successful certification outcome — the same concept this section describes, under a different name and without this specification's specific field structure.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## TC-SCHEMA-005

- Specification / section: MCC-TC-001 / 4. Certificate Schema / 4.5 Certificate Schema Invariants
- Status: PARTIAL
- Requirement: The Certificate Schema MUST remain independent of any specific serialization technology.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: certifications/manifest.json's CERTIFIED entries are a real, digest-identified (report_id), versioned, authoritative record of a successful certification outcome — the same concept this section describes, under a different name and without this specification's specific field structure.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## TC-SEC-001

- Specification / section: MCC-TC-001 / 19. Security Considerations / 19.6 Security Invariants
- Status: PARTIAL
- Requirement: Certificate verification MUST assume an untrusted source.
- Existing implementation: gateway/trust.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: gateway/trust.py assumes an untrusted/unresolved key yields no trust (fail-closed), the same threat model this section requires for Certificate forgery/tamper resistance.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## TC-SEC-002

- Specification / section: MCC-TC-001 / 19. Security Considerations / 19.6 Security Invariants
- Status: PARTIAL
- Requirement: Forgery and tamper detection MUST rely on Signature Verification against a recognized Trust Anchor.
- Existing implementation: gateway/trust.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: gateway/trust.py assumes an untrusted/unresolved key yields no trust (fail-closed), the same threat model this section requires for Certificate forgery/tamper resistance.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## TC-SEC-003

- Specification / section: MCC-TC-001 / 19. Security Considerations / 19.6 Security Invariants
- Status: PARTIAL
- Requirement: Certificates MUST NOT contain secrets or credentials.
- Existing implementation: gateway/trust.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: gateway/trust.py assumes an untrusted/unresolved key yields no trust (fail-closed), the same threat model this section requires for Certificate forgery/tamper resistance.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## TC-SEC-004

- Specification / section: MCC-TC-001 / 19. Security Considerations / 19.6 Security Invariants
- Status: PARTIAL
- Requirement: Sensitive underlying data MUST be redacted or hashed before inclusion in a Certificate field.
- Existing implementation: gateway/trust.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: gateway/trust.py assumes an untrusted/unresolved key yields no trust (fail-closed), the same threat model this section requires for Certificate forgery/tamper resistance.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## TC-SEC-005

- Specification / section: MCC-TC-001 / 19. Security Considerations / 19.6 Security Invariants
- Status: PARTIAL
- Requirement: A valid Technical Certificate MUST NOT be treated as a runtime execution authorization.
- Existing implementation: gateway/trust.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: gateway/trust.py assumes an untrusted/unresolved key yields no trust (fail-closed), the same threat model this section requires for Certificate forgery/tamper resistance.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## TC-SIG-001

- Specification / section: MCC-TC-001 / 14. Signature Requirements / 14.5 Signature Requirements Invariants
- Status: PARTIAL
- Requirement: Every Technical Certificate MUST be signed using an asymmetric digital signature scheme.
- Existing implementation: src/mcc_core/signing.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: The runtime signs its own authority-bearing artifact (the Decision Token, a different artifact per Section 3.4) exclusively with Ed25519, with a dedicated repository-wide test confirming no symmetric-key or shared-secret mechanism is used anywhere in that signing path.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## TC-SIG-002

- Specification / section: MCC-TC-001 / 14. Signature Requirements / 14.5 Signature Requirements Invariants
- Status: PARTIAL
- Requirement: HMAC and other symmetric-key authentication mechanisms MUST NOT be used to sign a Technical Certificate.
- Existing implementation: src/mcc_core/signing.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: The runtime signs its own authority-bearing artifact (the Decision Token, a different artifact per Section 3.4) exclusively with Ed25519, with a dedicated repository-wide test confirming no symmetric-key or shared-secret mechanism is used anywhere in that signing path.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## TC-SIG-003

- Specification / section: MCC-TC-001 / 14. Signature Requirements / 14.5 Signature Requirements Invariants
- Status: PARTIAL
- Requirement: A Signature MUST cover the complete Canonical Form of the Certificate excluding the Signature field.
- Existing implementation: src/mcc_core/signing.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: The runtime signs its own authority-bearing artifact (the Decision Token, a different artifact per Section 3.4) exclusively with Ed25519, with a dedicated repository-wide test confirming no symmetric-key or shared-secret mechanism is used anywhere in that signing path.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## TC-SIG-004

- Specification / section: MCC-TC-001 / 14. Signature Requirements / 14.5 Signature Requirements Invariants
- Status: PARTIAL
- Requirement: A Certificate MUST declare its signature algorithm and Issuer identity.
- Existing implementation: src/mcc_core/signing.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: The runtime signs its own authority-bearing artifact (the Decision Token, a different artifact per Section 3.4) exclusively with Ed25519, with a dedicated repository-wide test confirming no symmetric-key or shared-secret mechanism is used anywhere in that signing path.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## TC-SIG-005

- Specification / section: MCC-TC-001 / 14. Signature Requirements / 14.5 Signature Requirements Invariants
- Status: PARTIAL
- Requirement: Modification of any signed field MUST invalidate the Signature.
- Existing implementation: src/mcc_core/signing.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: The runtime signs its own authority-bearing artifact (the Decision Token, a different artifact per Section 3.4) exclusively with Ed25519, with a dedicated repository-wide test confirming no symmetric-key or shared-secret mechanism is used anywhere in that signing path.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## TC-SUBJ-001

- Specification / section: MCC-TC-001 / 8. Subject Identification / 8.4 Subject Identification Invariants
- Status: PARTIAL
- Requirement: A Technical Certificate MUST identify exactly one Certification Subject.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: adapter_key / implementation_id in certifications/manifest.json identify exactly one subject per record, the same one-subject-per-record model this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## TC-SUBJ-002

- Specification / section: MCC-TC-001 / 8. Subject Identification / 8.4 Subject Identification Invariants
- Status: PARTIAL
- Requirement: The Certificate's Subject MUST match its referenced Manifest's Subject.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: adapter_key / implementation_id in certifications/manifest.json identify exactly one subject per record, the same one-subject-per-record model this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## TC-SUBJ-003

- Specification / section: MCC-TC-001 / 8. Subject Identification / 8.4 Subject Identification Invariants
- Status: PARTIAL
- Requirement: A Subject mismatch MUST cause verification failure.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: adapter_key / implementation_id in certifications/manifest.json identify exactly one subject per record, the same one-subject-per-record model this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## TC-TRUST-001

- Specification / section: MCC-TC-001 / 16. Trust Model / 16.6 Trust Model Invariants
- Status: PARTIAL
- Requirement: A verifier MUST rely only on Trust Anchors it recognizes.
- Existing implementation: gateway/trust.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: gateway/trust.py is a real, tested multi-issuer trust set (per-issuer keys, rotation, expiry, revocation, fail-closed unresolved-key handling) — the closest and strongest analog to this section found in the repository, though scoped to mandate/approval trust, not Technical Certificate trust.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## TC-TRUST-002

- Specification / section: MCC-TC-001 / 16. Trust Model / 16.6 Trust Model Invariants
- Status: PARTIAL
- Requirement: Trust MUST NOT be inferred from a Certificate's self-declared Issuer identity alone.
- Existing implementation: gateway/trust.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: gateway/trust.py is a real, tested multi-issuer trust set (per-issuer keys, rotation, expiry, revocation, fail-closed unresolved-key handling) — the closest and strongest analog to this section found in the repository, though scoped to mandate/approval trust, not Technical Certificate trust.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## TC-TRUST-003

- Specification / section: MCC-TC-001 / 16. Trust Model / 16.6 Trust Model Invariants
- Status: PARTIAL
- Requirement: Trust Anchor rotation or revocation MUST NOT retroactively invalidate the historical record of issuance.
- Existing implementation: gateway/trust.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: gateway/trust.py is a real, tested multi-issuer trust set (per-issuer keys, rotation, expiry, revocation, fail-closed unresolved-key handling) — the closest and strongest analog to this section found in the repository, though scoped to mandate/approval trust, not Technical Certificate trust.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## TC-TRUST-004

- Specification / section: MCC-TC-001 / 16. Trust Model / 16.6 Trust Model Invariants
- Status: PARTIAL
- Requirement: A verifier MAY recognize multiple Trust Anchors across multiple Issuers.
- Existing implementation: gateway/trust.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: gateway/trust.py is a real, tested multi-issuer trust set (per-issuer keys, rotation, expiry, revocation, fail-closed unresolved-key handling) — the closest and strongest analog to this section found in the repository, though scoped to mandate/approval trust, not Technical Certificate trust.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## TC-VALID-001

- Specification / section: MCC-TC-001 / 11. Validity Period / 11.4 Validity Period Invariants
- Status: PARTIAL
- Requirement: Every Technical Certificate MUST record an issuance timestamp.
- Existing implementation: gateway/trust.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: gateway/trust.py's per-key not_after expiry implements the same validity-period-with-optional-expiration model this section requires, though for trust/mandate keys, not for a Technical Certificate.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## TC-VALID-002

- Specification / section: MCC-TC-001 / 11. Validity Period / 11.4 Validity Period Invariants
- Status: PARTIAL
- Requirement: A Certificate MUST NOT be valid before its issuance timestamp.
- Existing implementation: gateway/trust.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: gateway/trust.py's per-key not_after expiry implements the same validity-period-with-optional-expiration model this section requires, though for trust/mandate keys, not for a Technical Certificate.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## TC-VALID-003

- Specification / section: MCC-TC-001 / 11. Validity Period / 11.4 Validity Period Invariants
- Status: PARTIAL
- Requirement: An expired Certificate, where an expiration timestamp is declared and passed, MUST NOT be treated as valid.
- Existing implementation: gateway/trust.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: gateway/trust.py's per-key not_after expiry implements the same validity-period-with-optional-expiration model this section requires, though for trust/mandate keys, not for a Technical Certificate.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## TC-VALID-004

- Specification / section: MCC-TC-001 / 11. Validity Period / 11.4 Validity Period Invariants
- Status: PARTIAL
- Requirement: Absence of an expiration timestamp MUST NOT be treated as a validation failure.
- Existing implementation: gateway/trust.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: gateway/trust.py's per-key not_after expiry implements the same validity-period-with-optional-expiration model this section requires, though for trust/mandate keys, not for a Technical Certificate.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## TC-VERIFY-001

- Specification / section: MCC-TC-001 / 15. Verification Procedure / 15.9 Verification Procedure Invariants
- Status: PARTIAL
- Requirement: Verification MUST be fail-closed.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_evidence/verify.py implements an ordered, fail-closed, multi-step verification procedure (structure, then integrity, then signature, then consistency) procedurally analogous to this section, for the Governance Evidence Bundle rather than a Technical Certificate.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## TC-VERIFY-002

- Specification / section: MCC-TC-001 / 15. Verification Procedure / 15.9 Verification Procedure Invariants
- Status: PARTIAL
- Requirement: Structural verification MUST precede signature, manifest reference, evidence bundle reference, and consistency verification.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_evidence/verify.py implements an ordered, fail-closed, multi-step verification procedure (structure, then integrity, then signature, then consistency) procedurally analogous to this section, for the Governance Evidence Bundle rather than a Technical Certificate.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## TC-VERIFY-003

- Specification / section: MCC-TC-001 / 15. Verification Procedure / 15.9 Verification Procedure Invariants
- Status: PARTIAL
- Requirement: Signature verification MUST use a Trust Anchor associated with the declared Issuer.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_evidence/verify.py implements an ordered, fail-closed, multi-step verification procedure (structure, then integrity, then signature, then consistency) procedurally analogous to this section, for the Governance Evidence Bundle rather than a Technical Certificate.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## TC-VERIFY-004

- Specification / section: MCC-TC-001 / 15. Verification Procedure / 15.9 Verification Procedure Invariants
- Status: PARTIAL
- Requirement: Validity and revocation MUST both be checked, independent of all other verification steps.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_evidence/verify.py implements an ordered, fail-closed, multi-step verification procedure (structure, then integrity, then signature, then consistency) procedurally analogous to this section, for the Governance Evidence Bundle rather than a Technical Certificate.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## TC-VERIFY-005

- Specification / section: MCC-TC-001 / 15. Verification Procedure / 15.9 Verification Procedure Invariants
- Status: PARTIAL
- Requirement: A Certificate failing any verification step MUST be rejected in its entirety.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_evidence/verify.py implements an ordered, fail-closed, multi-step verification procedure (structure, then integrity, then signature, then consistency) procedurally analogous to this section, for the Governance Evidence Bundle rather than a Technical Certificate.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## TC-VERIFY-006

- Specification / section: MCC-TC-001 / 15. Verification Procedure / 15.9 Verification Procedure Invariants
- Status: PARTIAL
- Requirement: A verifier MUST reject a Technical Certificate whose direct Evidence Bundle Reference identifies a different Evidence Bundle than the Evidence Bundle Reference contained in its referenced Certification Manifest.
- Existing implementation: src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: src/mcc_evidence/verify.py implements an ordered, fail-closed, multi-step verification procedure (structure, then integrity, then signature, then consistency) procedurally analogous to this section, for the Governance Evidence Bundle rather than a Technical Certificate.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## TC-VSN-001

- Specification / section: MCC-TC-001 / 18. Versioning / 18.5 Versioning Invariants
- Status: PARTIAL
- Requirement: Every Technical Certificate MUST declare a Certificate Schema Version.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: Independent schema/contract versioning exists for the compliance-manifest artifact family (compliance_suite_version, contract_version, MANIFEST_SCHEMA_VERSION), the same independent-tracking model this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## TC-VSN-002

- Specification / section: MCC-TC-001 / 18. Versioning / 18.5 Versioning Invariants
- Status: PARTIAL
- Requirement: Certificate Schema Versions MUST be immutable once published.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: Independent schema/contract versioning exists for the compliance-manifest artifact family (compliance_suite_version, contract_version, MANIFEST_SCHEMA_VERSION), the same independent-tracking model this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## TC-VSN-003

- Specification / section: MCC-TC-001 / 18. Versioning / 18.5 Versioning Invariants
- Status: PARTIAL
- Requirement: Certificate Schema Version MUST be tracked independently of MCC-CP-001, MCC-EB-001, and MCC-CM-001 versions.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: Independent schema/contract versioning exists for the compliance-manifest artifact family (compliance_suite_version, contract_version, MANIFEST_SCHEMA_VERSION), the same independent-tracking model this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

## TC-VSN-004

- Specification / section: MCC-TC-001 / 18. Versioning / 18.5 Versioning Invariants
- Status: PARTIAL
- Requirement: An unrecognized Certificate Schema Version MUST cause verification to fail.
- Existing implementation: src/mcc_compliance/program.py; certifications/manifest.json
- Missing implementation behavior: Not wired to the artifact this specification defines; see rationale.
- Missing test coverage: Existing tests cover the reused primitive only, not this requirement directly.
- Missing evidence: No generated evidence artifact exists for this requirement.
- Rationale: Independent schema/contract versioning exists for the compliance-manifest artifact family (compliance_suite_version, contract_version, MANIFEST_SCHEMA_VERSION), the same independent-tracking model this section requires.
- Recommended remediation scope: SMALL
- May affect public interfaces / governance semantics: Yes — requires new public artifact schemas/objects and, for MCC-CP-001, new certification-program tooling; no existing Decision Token, Execution Gate, or Policy Bundle semantics are affected.

