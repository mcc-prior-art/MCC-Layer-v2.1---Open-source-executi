# MCC Normative v1.0 — Gap Report

Auto-generated. Do not hand-edit — regenerate with:

```
python -m mcc_conformance generate
```

Total non-CONFORMANT requirements: 429 of 429.

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

## MCC-EB-001-9-EVIDENCE-BUNDLE-OVERVIEW-D05

- Specification / section: MCC-EB-001 / 9. Evidence Bundle Overview / 9.3 Relationship to Certification Requirements
- Status: PARTIAL
- Requirement: An Evidence Bundle MAY contain Evidence Items for REQUIRED, OPTIONAL, and CONDITIONAL requirements alike, subject to the Required Files and Required Metadata rules in Sections 11 and 12.
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
- Requirement: A Technical Certificate is a certification-program artifact. It is not, and SHALL NOT be interpreted as, a runtime execution authorization. Runtime governance behavior (ALLOW, DENY, ESCALATE, CONSTRAIN) belongs exclusively to MCC-Core runtime governance and is out of scope for this specification.
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

