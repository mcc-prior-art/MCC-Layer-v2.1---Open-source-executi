# MCC Normative v1.0 — Implementation Traceability Matrix

Auto-generated. Do not hand-edit — regenerate with:

```
python -m mcc_conformance generate
```

## Baseline Provenance

- Release: MCC Specification Program — Normative v1.0
- Tag: `mcc-spec-v1.0.0`
- Baseline commit: `a65b2f375408dfbe8df86fbfc09724c5c45d3ba4`
- Declaration: docs/MCC_SPECIFICATION_PROGRAM_NORMATIVE_V1_0.md
- Review: docs/reviews/MCC_SPECIFICATION_PROGRAM_NORMATIVE_V1_REVIEW.md
- Final disposition: APPROVE FOR NORMATIVE v1.0

## Totals by Specification

| Specification | Requirements |
|---|---|
| MCC-CP-001 | 193 |
| MCC-EB-001 | 74 |
| MCC-CM-001 | 71 |
| MCC-TC-001 | 91 |
| **Total** | **429** |

## Totals by Conformance Status

| Status | Count | % of total |
|---|---|---|
| CONFORMANT | 0 | 0.0% |
| PARTIAL | 295 | 68.8% |
| GAP | 69 | 16.1% |
| NOT_APPLICABLE | 65 | 15.2% |
| NOT_ASSESSED | 0 | 0.0% |

**Conformance coverage (CONFORMANT / applicable requirements): 0.0% (0/364)**

## Full Traceability Matrix

| Requirement ID | Spec | Section | Status | Implementation | Tests |
|---|---|---|---|---|---|
| CM-COMPAT-001 | MCC-CM-001 | 17. Compatibility Rules / 17.6 Compatibility Invariants | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| CM-COMPAT-002 | MCC-CM-001 | 17. Compatibility Rules / 17.6 Compatibility Invariants | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| CM-COMPAT-003 | MCC-CM-001 | 17. Compatibility Rules / 17.6 Compatibility Invariants | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| CM-COMPAT-004 | MCC-CM-001 | 17. Compatibility Rules / 17.6 Compatibility Invariants | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| CM-CONF-001 | MCC-CM-001 | 22. Conformance Requirements / 22.5 Conformance Invariants | GAP | — | — |
| CM-CONF-002 | MCC-CM-001 | 22. Conformance Requirements / 22.5 Conformance Invariants | GAP | — | — |
| CM-CONF-003 | MCC-CM-001 | 22. Conformance Requirements / 22.5 Conformance Invariants | GAP | — | — |
| CM-CONF-004 | MCC-CM-001 | 22. Conformance Requirements / 22.5 Conformance Invariants | GAP | — | — |
| CM-EBREF-001 | MCC-CM-001 | 14. Evidence Bundle References / 14.5 Evidence Bundle Reference Invariants | GAP | — | — |
| CM-EBREF-002 | MCC-CM-001 | 14. Evidence Bundle References / 14.5 Evidence Bundle Reference Invariants | GAP | — | — |
| CM-EBREF-003 | MCC-CM-001 | 14. Evidence Bundle References / 14.5 Evidence Bundle Reference Invariants | GAP | — | — |
| CM-EBREF-004 | MCC-CM-001 | 14. Evidence Bundle References / 14.5 Evidence Bundle Reference Invariants | GAP | — | — |
| CM-EXT-001 | MCC-CM-001 | 20. Extension Model / 20.4 Extension Model Invariants | GAP | — | — |
| CM-EXT-002 | MCC-CM-001 | 20. Extension Model / 20.4 Extension Model Invariants | GAP | — | — |
| CM-EXT-003 | MCC-CM-001 | 20. Extension Model / 20.4 Extension Model Invariants | GAP | — | — |
| CM-HASH-001 | MCC-CM-001 | 13. Hash References / 13.5 Hash Reference Invariants | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| CM-HASH-002 | MCC-CM-001 | 13. Hash References / 13.5 Hash Reference Invariants | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| CM-HASH-003 | MCC-CM-001 | 13. Hash References / 13.5 Hash Reference Invariants | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| CM-HASH-004 | MCC-CM-001 | 13. Hash References / 13.5 Hash Reference Invariants | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| CM-META-001 | MCC-CM-001 | 15. Certification Metadata / 15.6 Certification Metadata Invariants | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| CM-META-002 | MCC-CM-001 | 15. Certification Metadata / 15.6 Certification Metadata Invariants | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| CM-META-003 | MCC-CM-001 | 15. Certification Metadata / 15.6 Certification Metadata Invariants | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| CM-META-004 | MCC-CM-001 | 15. Certification Metadata / 15.6 Certification Metadata Invariants | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| CM-META-005 | MCC-CM-001 | 15. Certification Metadata / 15.6 Certification Metadata Invariants | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| CM-OPTF-001 | MCC-CM-001 | 12. Optional Fields / 12.4 Optional Fields Invariants | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| CM-OPTF-002 | MCC-CM-001 | 12. Optional Fields / 12.4 Optional Fields Invariants | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| CM-OPTF-003 | MCC-CM-001 | 12. Optional Fields / 12.4 Optional Fields Invariants | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| CM-OPTF-004 | MCC-CM-001 | 12. Optional Fields / 12.4 Optional Fields Invariants | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| CM-REF-001 | MCC-CM-001 | 24. References / 24.3 Reference Invariants | NOT_APPLICABLE | — | — |
| CM-REF-002 | MCC-CM-001 | 24. References / 24.3 Reference Invariants | NOT_APPLICABLE | — | — |
| CM-REF-003 | MCC-CM-001 | 24. References / 24.3 Reference Invariants | NOT_APPLICABLE | — | — |
| CM-RFLD-001 | MCC-CM-001 | 11. Required Fields / 11.5 Required Fields Invariants | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| CM-RFLD-002 | MCC-CM-001 | 11. Required Fields / 11.5 Required Fields Invariants | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| CM-RFLD-003 | MCC-CM-001 | 11. Required Fields / 11.5 Required Fields Invariants | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| CM-RFLD-004 | MCC-CM-001 | 11. Required Fields / 11.5 Required Fields Invariants | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| CM-RFLD-005 | MCC-CM-001 | 11. Required Fields / 11.5 Required Fields Invariants | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| CM-RFLD-006 | MCC-CM-001 | 11. Required Fields / 11.5 Required Fields Invariants | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| CM-RID-001 | MCC-CM-001 | 23. Requirement Identifier Registry / 23.5 Registry Invariants | NOT_APPLICABLE | — | — |
| CM-RID-002 | MCC-CM-001 | 23. Requirement Identifier Registry / 23.5 Registry Invariants | NOT_APPLICABLE | — | — |
| CM-RID-003 | MCC-CM-001 | 23. Requirement Identifier Registry / 23.5 Registry Invariants | NOT_APPLICABLE | — | — |
| CM-RID-004 | MCC-CM-001 | 23. Requirement Identifier Registry / 23.5 Registry Invariants | NOT_APPLICABLE | — | — |
| CM-SCHEMA-001 | MCC-CM-001 | 10. Manifest Schema / 10.5 Manifest Schema Invariants | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| CM-SCHEMA-002 | MCC-CM-001 | 10. Manifest Schema / 10.5 Manifest Schema Invariants | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| CM-SCHEMA-003 | MCC-CM-001 | 10. Manifest Schema / 10.5 Manifest Schema Invariants | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| CM-SCHEMA-004 | MCC-CM-001 | 10. Manifest Schema / 10.5 Manifest Schema Invariants | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| CM-SCHEMA-005 | MCC-CM-001 | 10. Manifest Schema / 10.5 Manifest Schema Invariants | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| CM-SEC-001 | MCC-CM-001 | 19. Security Considerations / 19.5 Security Invariants | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| CM-SEC-002 | MCC-CM-001 | 19. Security Considerations / 19.5 Security Invariants | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| CM-SEC-003 | MCC-CM-001 | 19. Security Considerations / 19.5 Security Invariants | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| CM-SEC-004 | MCC-CM-001 | 19. Security Considerations / 19.5 Security Invariants | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| CM-SEC-005 | MCC-CM-001 | 19. Security Considerations / 19.5 Security Invariants | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| CM-VAL-001 | MCC-CM-001 | 18. Validation Rules / 18.7 Validation Invariants | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| CM-VAL-002 | MCC-CM-001 | 18. Validation Rules / 18.7 Validation Invariants | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| CM-VAL-003 | MCC-CM-001 | 18. Validation Rules / 18.7 Validation Invariants | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| CM-VAL-004 | MCC-CM-001 | 18. Validation Rules / 18.7 Validation Invariants | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| CM-VAL-005 | MCC-CM-001 | 18. Validation Rules / 18.7 Validation Invariants | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| CM-VSN-001 | MCC-CM-001 | 16. Versioning Rules / 16.5 Versioning Invariants | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| CM-VSN-002 | MCC-CM-001 | 16. Versioning Rules / 16.5 Versioning Invariants | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| CM-VSN-003 | MCC-CM-001 | 16. Versioning Rules / 16.5 Versioning Invariants | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| CM-VSN-004 | MCC-CM-001 | 16. Versioning Rules / 16.5 Versioning Invariants | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| MCC-CM-001-1-STATUS-D01 | MCC-CM-001 | 1. Status | NOT_APPLICABLE | — | — |
| MCC-CM-001-2-ABSTRACT-D01 | MCC-CM-001 | 2. Abstract | NOT_APPLICABLE | — | — |
| MCC-CM-001-5-GOALS-D01 | MCC-CM-001 | 5. Goals / CM-G1. Framework Neutrality | GAP | — | — |
| MCC-CM-001-5-GOALS-D02 | MCC-CM-001 | 5. Goals / CM-G2. Machine Readability | GAP | — | — |
| MCC-CM-001-5-GOALS-D03 | MCC-CM-001 | 5. Goals / CM-G3. Independent Verifiability | GAP | — | — |
| MCC-CM-001-5-GOALS-D04 | MCC-CM-001 | 5. Goals / CM-G4. Traceability | GAP | — | — |
| MCC-CM-001-6-NON-GOALS-D01 | MCC-CM-001 | 6. Non-Goals | GAP | — | — |
| MCC-CM-001-9-CERTIFICATION-MANIFEST-OVERVIEW-D01 | MCC-CM-001 | 9. Certification Manifest Overview / 9.1 Role in Certification | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| MCC-CM-001-9-CERTIFICATION-MANIFEST-OVERVIEW-D02 | MCC-CM-001 | 9. Certification Manifest Overview / 9.2 Manifest Form | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| MCC-CM-001-9-CERTIFICATION-MANIFEST-OVERVIEW-D03 | MCC-CM-001 | 9. Certification Manifest Overview / 9.2 Manifest Form | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| MCC-CM-001-9-CERTIFICATION-MANIFEST-OVERVIEW-D04 | MCC-CM-001 | 9. Certification Manifest Overview / 9.3 Relationship to Other Certification Artifacts | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| CAP-001 | MCC-CP-001 | 11. Capability Profiles / 11.7 Capability Profile Invariants | PARTIAL | src/mcc_compliance/capability_profile.py | tests/test_capability_profile.py |
| CAP-002 | MCC-CP-001 | 11. Capability Profiles / 11.7 Capability Profile Invariants | PARTIAL | src/mcc_compliance/capability_profile.py | tests/test_capability_profile.py |
| CAP-003 | MCC-CP-001 | 11. Capability Profiles / 11.7 Capability Profile Invariants | PARTIAL | src/mcc_compliance/capability_profile.py | tests/test_capability_profile.py |
| CAP-004 | MCC-CP-001 | 11. Capability Profiles / 11.7 Capability Profile Invariants | PARTIAL | src/mcc_compliance/capability_profile.py | tests/test_capability_profile.py |
| CAP-005 | MCC-CP-001 | 11. Capability Profiles / 11.7 Capability Profile Invariants | PARTIAL | src/mcc_compliance/capability_profile.py | tests/test_capability_profile.py |
| CAP-006 | MCC-CP-001 | 11. Capability Profiles / 11.7 Capability Profile Invariants | PARTIAL | src/mcc_compliance/capability_profile.py | tests/test_capability_profile.py |
| CAP-007 | MCC-CP-001 | 11. Capability Profiles / 11.7 Capability Profile Invariants | PARTIAL | src/mcc_compliance/capability_profile.py | tests/test_capability_profile.py |
| CAP-008 | MCC-CP-001 | 11. Capability Profiles / 11.7 Capability Profile Invariants | PARTIAL | src/mcc_compliance/capability_profile.py | tests/test_capability_profile.py |
| CERT-001 | MCC-CP-001 | 16. Technical Certificate Requirements / 16.6 Certificate Invariants | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| CERT-002 | MCC-CP-001 | 16. Technical Certificate Requirements / 16.6 Certificate Invariants | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| CERT-003 | MCC-CP-001 | 16. Technical Certificate Requirements / 16.6 Certificate Invariants | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| CERT-004 | MCC-CP-001 | 16. Technical Certificate Requirements / 16.6 Certificate Invariants | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| CERT-005 | MCC-CP-001 | 16. Technical Certificate Requirements / 16.6 Certificate Invariants | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| CERT-006 | MCC-CP-001 | 16. Technical Certificate Requirements / 16.6 Certificate Invariants | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| CERT-007 | MCC-CP-001 | 16. Technical Certificate Requirements / 16.6 Certificate Invariants | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| CI-001 | MCC-CP-001 | 7. Certification Model / 7.5 Certification Invariants | PARTIAL | src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json | tests/test_compliance_suite.py |
| CI-002 | MCC-CP-001 | 7. Certification Model / 7.5 Certification Invariants | PARTIAL | src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json | tests/test_compliance_suite.py |
| CI-003 | MCC-CP-001 | 7. Certification Model / 7.5 Certification Invariants | PARTIAL | src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json | tests/test_compliance_suite.py |
| CI-004 | MCC-CP-001 | 7. Certification Model / 7.5 Certification Invariants | PARTIAL | src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json | tests/test_compliance_suite.py |
| CI-005 | MCC-CP-001 | 7. Certification Model / 7.5 Certification Invariants | PARTIAL | src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json | tests/test_compliance_suite.py |
| CI-006 | MCC-CP-001 | 7. Certification Model / 7.5 Certification Invariants | PARTIAL | src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json | tests/test_compliance_suite.py |
| CI-007 | MCC-CP-001 | 7. Certification Model / 7.5 Certification Invariants | PARTIAL | src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json | tests/test_compliance_suite.py |
| CI-008 | MCC-CP-001 | 7. Certification Model / 7.5 Certification Invariants | PARTIAL | src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json | tests/test_compliance_suite.py |
| CI-009 | MCC-CP-001 | 7. Certification Model / 7.5 Certification Invariants | PARTIAL | src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json | tests/test_compliance_suite.py |
| CI-010 | MCC-CP-001 | 7. Certification Model / 7.5 Certification Invariants | PARTIAL | src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json | tests/test_compliance_suite.py |
| CLASS-001 | MCC-CP-001 | 13. Requirement Classification / 13.6 Requirement Classification Invariants | PARTIAL | src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json | tests/test_compliance_suite.py |
| CLASS-002 | MCC-CP-001 | 13. Requirement Classification / 13.6 Requirement Classification Invariants | PARTIAL | src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json | tests/test_compliance_suite.py |
| CLASS-003 | MCC-CP-001 | 13. Requirement Classification / 13.6 Requirement Classification Invariants | PARTIAL | src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json | tests/test_compliance_suite.py |
| CLASS-004 | MCC-CP-001 | 13. Requirement Classification / 13.6 Requirement Classification Invariants | PARTIAL | src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json | tests/test_compliance_suite.py |
| CLASS-005 | MCC-CP-001 | 13. Requirement Classification / 13.6 Requirement Classification Invariants | PARTIAL | src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json | tests/test_compliance_suite.py |
| CLASS-006 | MCC-CP-001 | 13. Requirement Classification / 13.6 Requirement Classification Invariants | PARTIAL | src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json | tests/test_compliance_suite.py |
| CLASS-007 | MCC-CP-001 | 13. Requirement Classification / 13.6 Requirement Classification Invariants | PARTIAL | src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json | tests/test_compliance_suite.py |
| CONF-001 | MCC-CP-001 | 10. Conformance Model / 10.6 Conformance Invariants | PARTIAL | src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json | tests/test_compliance_suite.py |
| CONF-002 | MCC-CP-001 | 10. Conformance Model / 10.6 Conformance Invariants | PARTIAL | src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json | tests/test_compliance_suite.py |
| CONF-003 | MCC-CP-001 | 10. Conformance Model / 10.6 Conformance Invariants | PARTIAL | src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json | tests/test_compliance_suite.py |
| CONF-004 | MCC-CP-001 | 10. Conformance Model / 10.6 Conformance Invariants | PARTIAL | src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json | tests/test_compliance_suite.py |
| CONF-005 | MCC-CP-001 | 10. Conformance Model / 10.6 Conformance Invariants | PARTIAL | src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json | tests/test_compliance_suite.py |
| CONF-006 | MCC-CP-001 | 10. Conformance Model / 10.6 Conformance Invariants | PARTIAL | src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json | tests/test_compliance_suite.py |
| CONF-007 | MCC-CP-001 | 10. Conformance Model / 10.6 Conformance Invariants | PARTIAL | src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json | tests/test_compliance_suite.py |
| CP-PIPE-001 | MCC-CP-001 | 9. Certification Pipeline / 9.9 Pipeline Invariants | PARTIAL | src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json | tests/test_compliance_suite.py |
| CP-PIPE-002 | MCC-CP-001 | 9. Certification Pipeline / 9.9 Pipeline Invariants | PARTIAL | src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json | tests/test_compliance_suite.py |
| CP-PIPE-003 | MCC-CP-001 | 9. Certification Pipeline / 9.9 Pipeline Invariants | PARTIAL | src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json | tests/test_compliance_suite.py |
| CP-PIPE-004 | MCC-CP-001 | 9. Certification Pipeline / 9.9 Pipeline Invariants | PARTIAL | src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json | tests/test_compliance_suite.py |
| CP-PIPE-005 | MCC-CP-001 | 9. Certification Pipeline / 9.9 Pipeline Invariants | PARTIAL | src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json | tests/test_compliance_suite.py |
| CP-PIPE-006 | MCC-CP-001 | 9. Certification Pipeline / 9.9 Pipeline Invariants | PARTIAL | src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json | tests/test_compliance_suite.py |
| CP-PIPE-007 | MCC-CP-001 | 9. Certification Pipeline / 9.9 Pipeline Invariants | PARTIAL | src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json | tests/test_compliance_suite.py |
| CREP-001 | MCC-CP-001 | Appendix H — Certification Report Requirements / H.6 Certification Report Invariants | PARTIAL | src/mcc_compliance/reporting.py | tests/test_compliance_suite.py; tests/test_sdk_certification.py |
| CREP-002 | MCC-CP-001 | Appendix H — Certification Report Requirements / H.6 Certification Report Invariants | PARTIAL | src/mcc_compliance/reporting.py | tests/test_compliance_suite.py; tests/test_sdk_certification.py |
| CREP-003 | MCC-CP-001 | Appendix H — Certification Report Requirements / H.6 Certification Report Invariants | PARTIAL | src/mcc_compliance/reporting.py | tests/test_compliance_suite.py; tests/test_sdk_certification.py |
| CREP-004 | MCC-CP-001 | Appendix H — Certification Report Requirements / H.6 Certification Report Invariants | PARTIAL | src/mcc_compliance/reporting.py | tests/test_compliance_suite.py; tests/test_sdk_certification.py |
| CREP-005 | MCC-CP-001 | Appendix H — Certification Report Requirements / H.6 Certification Report Invariants | PARTIAL | src/mcc_compliance/reporting.py | tests/test_compliance_suite.py; tests/test_sdk_certification.py |
| CREP-006 | MCC-CP-001 | Appendix H — Certification Report Requirements / H.6 Certification Report Invariants | PARTIAL | src/mcc_compliance/reporting.py | tests/test_compliance_suite.py; tests/test_sdk_certification.py |
| CRES-001 | MCC-CP-001 | Appendix G — Conformance Result Requirements / G.4 Conformance Result Invariants | PARTIAL | src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json | tests/test_compliance_suite.py |
| CRES-002 | MCC-CP-001 | Appendix G — Conformance Result Requirements / G.4 Conformance Result Invariants | PARTIAL | src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json | tests/test_compliance_suite.py |
| CRES-003 | MCC-CP-001 | Appendix G — Conformance Result Requirements / G.4 Conformance Result Invariants | PARTIAL | src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json | tests/test_compliance_suite.py |
| CRES-004 | MCC-CP-001 | Appendix G — Conformance Result Requirements / G.4 Conformance Result Invariants | PARTIAL | src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json | tests/test_compliance_suite.py |
| CRES-005 | MCC-CP-001 | Appendix G — Conformance Result Requirements / G.4 Conformance Result Invariants | PARTIAL | src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json | tests/test_compliance_suite.py |
| CSTMT-001 | MCC-CP-001 | 20. Conformance Statement / 20.3 Conformance Invariants | GAP | — | — |
| CSTMT-002 | MCC-CP-001 | 20. Conformance Statement / 20.3 Conformance Invariants | GAP | — | — |
| CSTMT-003 | MCC-CP-001 | 20. Conformance Statement / 20.3 Conformance Invariants | GAP | — | — |
| CSTMT-004 | MCC-CP-001 | 20. Conformance Statement / 20.3 Conformance Invariants | GAP | — | — |
| CSTMT-005 | MCC-CP-001 | 20. Conformance Statement / 20.3 Conformance Invariants | GAP | — | — |
| CSTMT-006 | MCC-CP-001 | 20. Conformance Statement / 20.3 Conformance Invariants | GAP | — | — |
| CSTMT-007 | MCC-CP-001 | 20. Conformance Statement / 20.3 Conformance Invariants | GAP | — | — |
| DEC-001 | MCC-CP-001 | Appendix B — Certification Decision Matrix / B.4 Decision Invariants | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| DEC-002 | MCC-CP-001 | Appendix B — Certification Decision Matrix / B.4 Decision Invariants | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| DEC-003 | MCC-CP-001 | Appendix B — Certification Decision Matrix / B.4 Decision Invariants | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| DEC-004 | MCC-CP-001 | Appendix B — Certification Decision Matrix / B.4 Decision Invariants | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| DEC-005 | MCC-CP-001 | Appendix B — Certification Decision Matrix / B.4 Decision Invariants | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| DEC-006 | MCC-CP-001 | Appendix B — Certification Decision Matrix / B.4 Decision Invariants | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| DEC-007 | MCC-CP-001 | Appendix B — Certification Decision Matrix / B.4 Decision Invariants | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| EVID-001 | MCC-CP-001 | 14. Evidence Requirements / 14.6 Evidence Invariants | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| EVID-002 | MCC-CP-001 | 14. Evidence Requirements / 14.6 Evidence Invariants | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| EVID-003 | MCC-CP-001 | 14. Evidence Requirements / 14.6 Evidence Invariants | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| EVID-004 | MCC-CP-001 | 14. Evidence Requirements / 14.6 Evidence Invariants | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| EVID-005 | MCC-CP-001 | 14. Evidence Requirements / 14.6 Evidence Invariants | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| EVID-006 | MCC-CP-001 | 14. Evidence Requirements / 14.6 Evidence Invariants | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| EVID-007 | MCC-CP-001 | 14. Evidence Requirements / 14.6 Evidence Invariants | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| EX-001 | MCC-CP-001 | Appendix E — Example Certification Flow / E.3 Example Invariants | NOT_APPLICABLE | — | — |
| EX-002 | MCC-CP-001 | Appendix E — Example Certification Flow / E.3 Example Invariants | NOT_APPLICABLE | — | — |
| EX-003 | MCC-CP-001 | Appendix E — Example Certification Flow / E.3 Example Invariants | NOT_APPLICABLE | — | — |
| EX-004 | MCC-CP-001 | Appendix E — Example Certification Flow / E.3 Example Invariants | NOT_APPLICABLE | — | — |
| EX-005 | MCC-CP-001 | Appendix E — Example Certification Flow / E.3 Example Invariants | NOT_APPLICABLE | — | — |
| EX-006 | MCC-CP-001 | Appendix E — Example Certification Flow / E.3 Example Invariants | NOT_APPLICABLE | — | — |
| EX-007 | MCC-CP-001 | Appendix E — Example Certification Flow / E.3 Example Invariants | NOT_APPLICABLE | — | — |
| EXT-001 | MCC-CP-001 | Appendix F — Future Extensions / F.3 Extension Invariants | NOT_APPLICABLE | — | — |
| EXT-002 | MCC-CP-001 | Appendix F — Future Extensions / F.3 Extension Invariants | NOT_APPLICABLE | — | — |
| EXT-003 | MCC-CP-001 | Appendix F — Future Extensions / F.3 Extension Invariants | NOT_APPLICABLE | — | — |
| EXT-004 | MCC-CP-001 | Appendix F — Future Extensions / F.3 Extension Invariants | NOT_APPLICABLE | — | — |
| EXT-005 | MCC-CP-001 | Appendix F — Future Extensions / F.3 Extension Invariants | NOT_APPLICABLE | — | — |
| EXT-006 | MCC-CP-001 | Appendix F — Future Extensions / F.3 Extension Invariants | NOT_APPLICABLE | — | — |
| EXT-007 | MCC-CP-001 | Appendix F — Future Extensions / F.3 Extension Invariants | NOT_APPLICABLE | — | — |
| MAN-001 | MCC-CP-001 | 15. Certification Manifest Requirements / 15.6 Manifest Invariants | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| MAN-002 | MCC-CP-001 | 15. Certification Manifest Requirements / 15.6 Manifest Invariants | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| MAN-003 | MCC-CP-001 | 15. Certification Manifest Requirements / 15.6 Manifest Invariants | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| MAN-004 | MCC-CP-001 | 15. Certification Manifest Requirements / 15.6 Manifest Invariants | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| MAN-005 | MCC-CP-001 | 15. Certification Manifest Requirements / 15.6 Manifest Invariants | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| MAN-006 | MCC-CP-001 | 15. Certification Manifest Requirements / 15.6 Manifest Invariants | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| MAN-007 | MCC-CP-001 | 15. Certification Manifest Requirements / 15.6 Manifest Invariants | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| MCC-CP-001-2-GOALS-D01 | MCC-CP-001 | 2. Goals / G1. Framework Neutrality | GAP | — | — |
| MCC-CP-001-2-GOALS-D02 | MCC-CP-001 | 2. Goals / G1. Framework Neutrality | GAP | — | — |
| MCC-CP-001-2-GOALS-D03 | MCC-CP-001 | 2. Goals / G2. Reproducibility | GAP | — | — |
| MCC-CP-001-2-GOALS-D04 | MCC-CP-001 | 2. Goals / G3. Independent Verification | GAP | — | — |
| MCC-CP-001-2-GOALS-D05 | MCC-CP-001 | 2. Goals / G4. Conformance | GAP | — | — |
| MCC-CP-001-2-GOALS-D06 | MCC-CP-001 | 2. Goals / G4. Conformance | GAP | — | — |
| MCC-CP-001-3-NON-GOALS-D01 | MCC-CP-001 | 3. Non-Goals | GAP | — | — |
| MCC-CP-001-5-NORMATIVE-LANGUAGE-D01 | MCC-CP-001 | 5. Normative Language | NOT_APPLICABLE | — | — |
| MCC-CP-001-6-ARCHITECTURAL-PRINCIPLES-D01 | MCC-CP-001 | 6. Architectural Principles | GAP | — | — |
| MCC-CP-001-6-ARCHITECTURAL-PRINCIPLES-D02 | MCC-CP-001 | 6. Architectural Principles | GAP | — | — |
| MCC-CP-001-6-ARCHITECTURAL-PRINCIPLES-D03 | MCC-CP-001 | 6. Architectural Principles | GAP | — | — |
| MCC-CP-001-8-CERTIFICATION-LIFECYCLE-D01 | MCC-CP-001 | 8. Certification Lifecycle | PARTIAL | src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json | tests/test_compliance_suite.py |
| MCC-CP-001-8-CERTIFICATION-LIFECYCLE-D02 | MCC-CP-001 | 8. Certification Lifecycle / 8.1 Registration | PARTIAL | src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json | tests/test_compliance_suite.py |
| MCC-CP-001-8-CERTIFICATION-LIFECYCLE-D03 | MCC-CP-001 | 8. Certification Lifecycle / 8.1 Registration | PARTIAL | src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json | tests/test_compliance_suite.py |
| MCC-CP-001-8-CERTIFICATION-LIFECYCLE-D04 | MCC-CP-001 | 8. Certification Lifecycle / 8.2 Preparation | PARTIAL | src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json | tests/test_compliance_suite.py |
| MCC-CP-001-8-CERTIFICATION-LIFECYCLE-D05 | MCC-CP-001 | 8. Certification Lifecycle / 8.2 Preparation | PARTIAL | src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json | tests/test_compliance_suite.py |
| MCC-CP-001-8-CERTIFICATION-LIFECYCLE-D06 | MCC-CP-001 | 8. Certification Lifecycle / 8.2 Preparation | PARTIAL | src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json | tests/test_compliance_suite.py |
| MCC-CP-001-8-CERTIFICATION-LIFECYCLE-D07 | MCC-CP-001 | 8. Certification Lifecycle / 8.3 Evaluation | PARTIAL | src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json | tests/test_compliance_suite.py |
| MCC-CP-001-8-CERTIFICATION-LIFECYCLE-D08 | MCC-CP-001 | 8. Certification Lifecycle / 8.3 Evaluation | PARTIAL | src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json | tests/test_compliance_suite.py |
| MCC-CP-001-8-CERTIFICATION-LIFECYCLE-D09 | MCC-CP-001 | 8. Certification Lifecycle / 8.3 Evaluation | PARTIAL | src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json | tests/test_compliance_suite.py |
| MCC-CP-001-8-CERTIFICATION-LIFECYCLE-D10 | MCC-CP-001 | 8. Certification Lifecycle / 8.4 Evidence Collection | PARTIAL | src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json | tests/test_compliance_suite.py |
| MCC-CP-001-8-CERTIFICATION-LIFECYCLE-D11 | MCC-CP-001 | 8. Certification Lifecycle / 8.4 Evidence Collection | PARTIAL | src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json | tests/test_compliance_suite.py |
| MCC-CP-001-8-CERTIFICATION-LIFECYCLE-D12 | MCC-CP-001 | 8. Certification Lifecycle / 8.4 Evidence Collection | PARTIAL | src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json | tests/test_compliance_suite.py |
| MCC-CP-001-8-CERTIFICATION-LIFECYCLE-D13 | MCC-CP-001 | 8. Certification Lifecycle / 8.5 Conformance Assessment | PARTIAL | src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json | tests/test_compliance_suite.py |
| MCC-CP-001-8-CERTIFICATION-LIFECYCLE-D14 | MCC-CP-001 | 8. Certification Lifecycle / 8.5 Conformance Assessment | PARTIAL | src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json | tests/test_compliance_suite.py |
| MCC-CP-001-8-CERTIFICATION-LIFECYCLE-D15 | MCC-CP-001 | 8. Certification Lifecycle / 8.5 Conformance Assessment | PARTIAL | src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json | tests/test_compliance_suite.py |
| MCC-CP-001-8-CERTIFICATION-LIFECYCLE-D16 | MCC-CP-001 | 8. Certification Lifecycle / 8.6 Certification Decision | PARTIAL | src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json | tests/test_compliance_suite.py |
| MCC-CP-001-8-CERTIFICATION-LIFECYCLE-D17 | MCC-CP-001 | 8. Certification Lifecycle / 8.6 Certification Decision | PARTIAL | src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json | tests/test_compliance_suite.py |
| MCC-CP-001-8-CERTIFICATION-LIFECYCLE-D18 | MCC-CP-001 | 8. Certification Lifecycle / 8.7 Technical Certificate Issuance | PARTIAL | src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json | tests/test_compliance_suite.py |
| MCC-CP-001-8-CERTIFICATION-LIFECYCLE-D19 | MCC-CP-001 | 8. Certification Lifecycle / 8.7 Technical Certificate Issuance | PARTIAL | src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json | tests/test_compliance_suite.py |
| MCC-CP-001-8-CERTIFICATION-LIFECYCLE-D20 | MCC-CP-001 | 8. Certification Lifecycle / 8.8 Publication | PARTIAL | src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json | tests/test_compliance_suite.py |
| MCC-CP-001-8-CERTIFICATION-LIFECYCLE-D21 | MCC-CP-001 | 8. Certification Lifecycle / 8.8 Publication | PARTIAL | src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json | tests/test_compliance_suite.py |
| MCC-CP-001-8-CERTIFICATION-LIFECYCLE-D22 | MCC-CP-001 | 8. Certification Lifecycle / 8.9 Revalidation | PARTIAL | src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json | tests/test_compliance_suite.py |
| MCC-CP-001-8-CERTIFICATION-LIFECYCLE-D23 | MCC-CP-001 | 8. Certification Lifecycle / 8.9 Revalidation | PARTIAL | src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json | tests/test_compliance_suite.py |
| MCC-CP-001-ABSTRACT-D01 | MCC-CP-001 | Abstract | NOT_APPLICABLE | — | — |
| MCC-CP-001-DOCUMENT-ROADMAP-D01 | MCC-CP-001 | Document Roadmap | NOT_APPLICABLE | — | — |
| MCC-CP-001-DOCUMENT-ROADMAP-D02 | MCC-CP-001 | Document Roadmap | NOT_APPLICABLE | — | — |
| MCC-CP-001-STATUS-OF-THIS-SPECIFICATION-D01 | MCC-CP-001 | Status of This Specification | NOT_APPLICABLE | — | — |
| REF-001 | MCC-CP-001 | 21. References / 21.4 Reference Invariants | NOT_APPLICABLE | — | — |
| REF-002 | MCC-CP-001 | 21. References / 21.4 Reference Invariants | NOT_APPLICABLE | — | — |
| REF-003 | MCC-CP-001 | 21. References / 21.4 Reference Invariants | NOT_APPLICABLE | — | — |
| REF-004 | MCC-CP-001 | 21. References / 21.4 Reference Invariants | NOT_APPLICABLE | — | — |
| REF-005 | MCC-CP-001 | 21. References / 21.4 Reference Invariants | NOT_APPLICABLE | — | — |
| REF-006 | MCC-CP-001 | 21. References / 21.4 Reference Invariants | NOT_APPLICABLE | — | — |
| REF-007 | MCC-CP-001 | 21. References / 21.4 Reference Invariants | NOT_APPLICABLE | — | — |
| REG-001 | MCC-CP-001 | 19. Registry Considerations / 19.4 Registry Invariants | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| REG-002 | MCC-CP-001 | 19. Registry Considerations / 19.4 Registry Invariants | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| REG-003 | MCC-CP-001 | 19. Registry Considerations / 19.4 Registry Invariants | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| REG-004 | MCC-CP-001 | 19. Registry Considerations / 19.4 Registry Invariants | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| REG-005 | MCC-CP-001 | 19. Registry Considerations / 19.4 Registry Invariants | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| REG-006 | MCC-CP-001 | 19. Registry Considerations / 19.4 Registry Invariants | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| REG-007 | MCC-CP-001 | 19. Registry Considerations / 19.4 Registry Invariants | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| REQ-001 | MCC-CP-001 | 12. Certification Requirements / 12.6 Requirement Invariants | PARTIAL | src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json | tests/test_compliance_suite.py |
| REQ-002 | MCC-CP-001 | 12. Certification Requirements / 12.6 Requirement Invariants | PARTIAL | src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json | tests/test_compliance_suite.py |
| REQ-003 | MCC-CP-001 | 12. Certification Requirements / 12.6 Requirement Invariants | PARTIAL | src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json | tests/test_compliance_suite.py |
| REQ-004 | MCC-CP-001 | 12. Certification Requirements / 12.6 Requirement Invariants | PARTIAL | src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json | tests/test_compliance_suite.py |
| REQ-005 | MCC-CP-001 | 12. Certification Requirements / 12.6 Requirement Invariants | PARTIAL | src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json | tests/test_compliance_suite.py |
| REQ-006 | MCC-CP-001 | 12. Certification Requirements / 12.6 Requirement Invariants | PARTIAL | src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json | tests/test_compliance_suite.py |
| REQ-007 | MCC-CP-001 | 12. Certification Requirements / 12.6 Requirement Invariants | PARTIAL | src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json | tests/test_compliance_suite.py |
| REV-001 | MCC-CP-001 | Appendix D — Revision History / D.4 Revision Invariants | NOT_APPLICABLE | — | — |
| REV-002 | MCC-CP-001 | Appendix D — Revision History / D.4 Revision Invariants | NOT_APPLICABLE | — | — |
| REV-003 | MCC-CP-001 | Appendix D — Revision History / D.4 Revision Invariants | NOT_APPLICABLE | — | — |
| REV-004 | MCC-CP-001 | Appendix D — Revision History / D.4 Revision Invariants | NOT_APPLICABLE | — | — |
| REV-005 | MCC-CP-001 | Appendix D — Revision History / D.4 Revision Invariants | NOT_APPLICABLE | — | — |
| REV-006 | MCC-CP-001 | Appendix D — Revision History / D.4 Revision Invariants | NOT_APPLICABLE | — | — |
| REV-007 | MCC-CP-001 | Appendix D — Revision History / D.4 Revision Invariants | NOT_APPLICABLE | — | — |
| RID-001 | MCC-CP-001 | Appendix C — Requirement Identifier Registry / C.4 Registry Invariants | NOT_APPLICABLE | — | — |
| RID-002 | MCC-CP-001 | Appendix C — Requirement Identifier Registry / C.4 Registry Invariants | NOT_APPLICABLE | — | — |
| RID-003 | MCC-CP-001 | Appendix C — Requirement Identifier Registry / C.4 Registry Invariants | NOT_APPLICABLE | — | — |
| RID-004 | MCC-CP-001 | Appendix C — Requirement Identifier Registry / C.4 Registry Invariants | NOT_APPLICABLE | — | — |
| RID-005 | MCC-CP-001 | Appendix C — Requirement Identifier Registry / C.4 Registry Invariants | NOT_APPLICABLE | — | — |
| RID-006 | MCC-CP-001 | Appendix C — Requirement Identifier Registry / C.4 Registry Invariants | NOT_APPLICABLE | — | — |
| RID-007 | MCC-CP-001 | Appendix C — Requirement Identifier Registry / C.4 Registry Invariants | NOT_APPLICABLE | — | — |
| SEC-001 | MCC-CP-001 | 18. Security Considerations / 18.4 Security Invariants | PARTIAL | src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json | tests/test_compliance_suite.py |
| SEC-002 | MCC-CP-001 | 18. Security Considerations / 18.4 Security Invariants | PARTIAL | src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json | tests/test_compliance_suite.py |
| SEC-003 | MCC-CP-001 | 18. Security Considerations / 18.4 Security Invariants | PARTIAL | src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json | tests/test_compliance_suite.py |
| SEC-004 | MCC-CP-001 | 18. Security Considerations / 18.4 Security Invariants | PARTIAL | src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json | tests/test_compliance_suite.py |
| SEC-005 | MCC-CP-001 | 18. Security Considerations / 18.4 Security Invariants | PARTIAL | src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json | tests/test_compliance_suite.py |
| SEC-006 | MCC-CP-001 | 18. Security Considerations / 18.4 Security Invariants | PARTIAL | src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json | tests/test_compliance_suite.py |
| SEC-007 | MCC-CP-001 | 18. Security Considerations / 18.4 Security Invariants | PARTIAL | src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json | tests/test_compliance_suite.py |
| STATE-001 | MCC-CP-001 | Appendix A — Certification State Machine / A.4 State Invariants | GAP | — | — |
| STATE-002 | MCC-CP-001 | Appendix A — Certification State Machine / A.4 State Invariants | GAP | — | — |
| STATE-003 | MCC-CP-001 | Appendix A — Certification State Machine / A.4 State Invariants | GAP | — | — |
| STATE-004 | MCC-CP-001 | Appendix A — Certification State Machine / A.4 State Invariants | GAP | — | — |
| STATE-005 | MCC-CP-001 | Appendix A — Certification State Machine / A.4 State Invariants | GAP | — | — |
| STATE-006 | MCC-CP-001 | Appendix A — Certification State Machine / A.4 State Invariants | GAP | — | — |
| STATE-007 | MCC-CP-001 | Appendix A — Certification State Machine / A.4 State Invariants | GAP | — | — |
| VER-001 | MCC-CP-001 | 17. Versioning / 17.5 Version Invariants | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| VER-002 | MCC-CP-001 | 17. Versioning / 17.5 Version Invariants | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| VER-003 | MCC-CP-001 | 17. Versioning / 17.5 Version Invariants | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| VER-004 | MCC-CP-001 | 17. Versioning / 17.5 Version Invariants | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| VER-005 | MCC-CP-001 | 17. Versioning / 17.5 Version Invariants | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| VER-006 | MCC-CP-001 | 17. Versioning / 17.5 Version Invariants | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| VER-007 | MCC-CP-001 | 17. Versioning / 17.5 Version Invariants | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| EB-COMPAT-001 | MCC-EB-001 | 18. Compatibility Requirements / 18.5 Compatibility Invariants | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| EB-COMPAT-002 | MCC-EB-001 | 18. Compatibility Requirements / 18.5 Compatibility Invariants | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| EB-COMPAT-003 | MCC-EB-001 | 18. Compatibility Requirements / 18.5 Compatibility Invariants | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| EB-COMPAT-004 | MCC-EB-001 | 18. Compatibility Requirements / 18.5 Compatibility Invariants | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| EB-CONF-001 | MCC-EB-001 | 22. Conformance Requirements / 22.5 Conformance Invariants | GAP | — | — |
| EB-CONF-002 | MCC-EB-001 | 22. Conformance Requirements / 22.5 Conformance Invariants | GAP | — | — |
| EB-CONF-003 | MCC-EB-001 | 22. Conformance Requirements / 22.5 Conformance Invariants | GAP | — | — |
| EB-CONF-004 | MCC-EB-001 | 22. Conformance Requirements / 22.5 Conformance Invariants | GAP | — | — |
| EB-EXT-001 | MCC-EB-001 | 20. Extension Model / 20.4 Extension Model Invariants | GAP | — | — |
| EB-EXT-002 | MCC-EB-001 | 20. Extension Model / 20.4 Extension Model Invariants | GAP | — | — |
| EB-EXT-003 | MCC-EB-001 | 20. Extension Model / 20.4 Extension Model Invariants | GAP | — | — |
| EB-EXT-004 | MCC-EB-001 | 20. Extension Model / 20.4 Extension Model Invariants | GAP | — | — |
| EB-FILE-001 | MCC-EB-001 | 11. Required Files / 11.5 Required Files Invariants | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| EB-FILE-002 | MCC-EB-001 | 11. Required Files / 11.5 Required Files Invariants | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| EB-FILE-003 | MCC-EB-001 | 11. Required Files / 11.5 Required Files Invariants | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| EB-FILE-004 | MCC-EB-001 | 11. Required Files / 11.5 Required Files Invariants | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| EB-FILE-005 | MCC-EB-001 | 11. Required Files / 11.5 Required Files Invariants | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| EB-HASH-001 | MCC-EB-001 | 13. Hash and Integrity Model / 13.6 Hash and Integrity Invariants | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| EB-HASH-002 | MCC-EB-001 | 13. Hash and Integrity Model / 13.6 Hash and Integrity Invariants | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| EB-HASH-003 | MCC-EB-001 | 13. Hash and Integrity Model / 13.6 Hash and Integrity Invariants | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| EB-HASH-004 | MCC-EB-001 | 13. Hash and Integrity Model / 13.6 Hash and Integrity Invariants | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| EB-HASH-005 | MCC-EB-001 | 13. Hash and Integrity Model / 13.6 Hash and Integrity Invariants | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| EB-META-001 | MCC-EB-001 | 12. Required Metadata / 12.4 Required Metadata Invariants | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| EB-META-002 | MCC-EB-001 | 12. Required Metadata / 12.4 Required Metadata Invariants | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| EB-META-003 | MCC-EB-001 | 12. Required Metadata / 12.4 Required Metadata Invariants | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| EB-META-004 | MCC-EB-001 | 12. Required Metadata / 12.4 Required Metadata Invariants | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| EB-META-005 | MCC-EB-001 | 12. Required Metadata / 12.4 Required Metadata Invariants | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| EB-PROV-001 | MCC-EB-001 | 14. Provenance Requirements / 14.5 Provenance Invariants | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| EB-PROV-002 | MCC-EB-001 | 14. Provenance Requirements / 14.5 Provenance Invariants | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| EB-PROV-003 | MCC-EB-001 | 14. Provenance Requirements / 14.5 Provenance Invariants | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| EB-PROV-004 | MCC-EB-001 | 14. Provenance Requirements / 14.5 Provenance Invariants | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| EB-PROV-005 | MCC-EB-001 | 14. Provenance Requirements / 14.5 Provenance Invariants | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| EB-REF-001 | MCC-EB-001 | 24. References / 24.3 Reference Invariants | NOT_APPLICABLE | — | — |
| EB-REF-002 | MCC-EB-001 | 24. References / 24.3 Reference Invariants | NOT_APPLICABLE | — | — |
| EB-REF-003 | MCC-EB-001 | 24. References / 24.3 Reference Invariants | NOT_APPLICABLE | — | — |
| EB-REPRO-001 | MCC-EB-001 | 15. Reproducibility Requirements / 15.5 Reproducibility Invariants | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| EB-REPRO-002 | MCC-EB-001 | 15. Reproducibility Requirements / 15.5 Reproducibility Invariants | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| EB-REPRO-003 | MCC-EB-001 | 15. Reproducibility Requirements / 15.5 Reproducibility Invariants | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| EB-REPRO-004 | MCC-EB-001 | 15. Reproducibility Requirements / 15.5 Reproducibility Invariants | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| EB-RID-001 | MCC-EB-001 | 23. Requirement Identifier Registry / 23.5 Registry Invariants | NOT_APPLICABLE | — | — |
| EB-RID-002 | MCC-EB-001 | 23. Requirement Identifier Registry / 23.5 Registry Invariants | NOT_APPLICABLE | — | — |
| EB-RID-003 | MCC-EB-001 | 23. Requirement Identifier Registry / 23.5 Registry Invariants | NOT_APPLICABLE | — | — |
| EB-RID-004 | MCC-EB-001 | 23. Requirement Identifier Registry / 23.5 Registry Invariants | NOT_APPLICABLE | — | — |
| EB-SEC-001 | MCC-EB-001 | 19. Security Considerations / 19.5 Security Invariants | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| EB-SEC-002 | MCC-EB-001 | 19. Security Considerations / 19.5 Security Invariants | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| EB-SEC-003 | MCC-EB-001 | 19. Security Considerations / 19.5 Security Invariants | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| EB-SEC-004 | MCC-EB-001 | 19. Security Considerations / 19.5 Security Invariants | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| EB-SEC-005 | MCC-EB-001 | 19. Security Considerations / 19.5 Security Invariants | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| EB-STR-001 | MCC-EB-001 | 10. Bundle Directory Structure / 10.5 Structure Invariants | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| EB-STR-002 | MCC-EB-001 | 10. Bundle Directory Structure / 10.5 Structure Invariants | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| EB-STR-003 | MCC-EB-001 | 10. Bundle Directory Structure / 10.5 Structure Invariants | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| EB-STR-004 | MCC-EB-001 | 10. Bundle Directory Structure / 10.5 Structure Invariants | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| EB-STR-005 | MCC-EB-001 | 10. Bundle Directory Structure / 10.5 Structure Invariants | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| EB-VAL-001 | MCC-EB-001 | 16. Validation Rules / 16.7 Validation Invariants | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| EB-VAL-002 | MCC-EB-001 | 16. Validation Rules / 16.7 Validation Invariants | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| EB-VAL-003 | MCC-EB-001 | 16. Validation Rules / 16.7 Validation Invariants | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| EB-VAL-004 | MCC-EB-001 | 16. Validation Rules / 16.7 Validation Invariants | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| EB-VAL-005 | MCC-EB-001 | 16. Validation Rules / 16.7 Validation Invariants | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| EB-VSN-001 | MCC-EB-001 | 17. Versioning Rules / 17.5 Versioning Invariants | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| EB-VSN-002 | MCC-EB-001 | 17. Versioning Rules / 17.5 Versioning Invariants | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| EB-VSN-003 | MCC-EB-001 | 17. Versioning Rules / 17.5 Versioning Invariants | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| EB-VSN-004 | MCC-EB-001 | 17. Versioning Rules / 17.5 Versioning Invariants | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| MCC-EB-001-1-STATUS-D01 | MCC-EB-001 | 1. Status | NOT_APPLICABLE | — | — |
| MCC-EB-001-2-ABSTRACT-D01 | MCC-EB-001 | 2. Abstract | NOT_APPLICABLE | — | — |
| MCC-EB-001-5-GOALS-D01 | MCC-EB-001 | 5. Goals / EB-G1. Framework Neutrality | GAP | — | — |
| MCC-EB-001-5-GOALS-D02 | MCC-EB-001 | 5. Goals / EB-G2. Reproducibility | GAP | — | — |
| MCC-EB-001-5-GOALS-D03 | MCC-EB-001 | 5. Goals / EB-G3. Independent Verifiability | GAP | — | — |
| MCC-EB-001-5-GOALS-D04 | MCC-EB-001 | 5. Goals / EB-G4. Structural Determinism | GAP | — | — |
| MCC-EB-001-6-NON-GOALS-D01 | MCC-EB-001 | 6. Non-Goals | GAP | — | — |
| MCC-EB-001-9-EVIDENCE-BUNDLE-OVERVIEW-D01 | MCC-EB-001 | 9. Evidence Bundle Overview / 9.1 Role in Certification | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| MCC-EB-001-9-EVIDENCE-BUNDLE-OVERVIEW-D02 | MCC-EB-001 | 9. Evidence Bundle Overview / 9.2 Bundle Forms | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| MCC-EB-001-9-EVIDENCE-BUNDLE-OVERVIEW-D03 | MCC-EB-001 | 9. Evidence Bundle Overview / 9.2 Bundle Forms | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| MCC-EB-001-9-EVIDENCE-BUNDLE-OVERVIEW-D04 | MCC-EB-001 | 9. Evidence Bundle Overview / 9.3 Relationship to Certification Requirements | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| MCC-EB-001-9-EVIDENCE-BUNDLE-OVERVIEW-D05 | MCC-EB-001 | 9. Evidence Bundle Overview / 9.3 Relationship to Certification Requirements | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| MCC-TC-001-1-PURPOSE-D01 | MCC-TC-001 | 1. Purpose | GAP | — | — |
| MCC-TC-001-1-PURPOSE-D02 | MCC-TC-001 | 1. Purpose | GAP | — | — |
| MCC-TC-001-1-PURPOSE-D03 | MCC-TC-001 | 1. Purpose | GAP | — | — |
| MCC-TC-001-1-PURPOSE-D04 | MCC-TC-001 | 1. Purpose | GAP | — | — |
| MCC-TC-001-ABSTRACT-D01 | MCC-TC-001 | Abstract | NOT_APPLICABLE | — | — |
| MCC-TC-001-ABSTRACT-D02 | MCC-TC-001 | Abstract | NOT_APPLICABLE | — | — |
| MCC-TC-001-STATUS-OF-THIS-SPECIFICATION-D01 | MCC-TC-001 | Status of This Specification | NOT_APPLICABLE | — | — |
| TC-COMPAT-001 | MCC-TC-001 | 17. Compatibility / 17.5 Compatibility Invariants | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| TC-COMPAT-002 | MCC-TC-001 | 17. Compatibility / 17.5 Compatibility Invariants | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| TC-COMPAT-003 | MCC-TC-001 | 17. Compatibility / 17.5 Compatibility Invariants | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| TC-COMPAT-004 | MCC-TC-001 | 17. Compatibility / 17.5 Compatibility Invariants | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| TC-CONF-001 | MCC-TC-001 | 21. Conformance Requirements / 21.5 Conformance Invariants | GAP | — | — |
| TC-CONF-002 | MCC-TC-001 | 21. Conformance Requirements / 21.5 Conformance Invariants | GAP | — | — |
| TC-CONF-003 | MCC-TC-001 | 21. Conformance Requirements / 21.5 Conformance Invariants | GAP | — | — |
| TC-CONF-004 | MCC-TC-001 | 21. Conformance Requirements / 21.5 Conformance Invariants | GAP | — | — |
| TC-CONF-005 | MCC-TC-001 | 21. Conformance Requirements / 21.5 Conformance Invariants | GAP | — | — |
| TC-EXT-001 | MCC-TC-001 | 20. Extension Model / 20.4 Extension Model Invariants | GAP | — | — |
| TC-EXT-002 | MCC-TC-001 | 20. Extension Model / 20.4 Extension Model Invariants | GAP | — | — |
| TC-EXT-003 | MCC-TC-001 | 20. Extension Model / 20.4 Extension Model Invariants | GAP | — | — |
| TC-EXT-004 | MCC-TC-001 | 20. Extension Model / 20.4 Extension Model Invariants | GAP | — | — |
| TC-HASH-001 | MCC-TC-001 | 13. Cryptographic Integrity / 13.4 Cryptographic Integrity Invariants | PARTIAL | src/mcc_core/signing.py | tests/test_mcc_core.py::test_sign_and_verify_roundtrip; tests/test_mcc_core.py::test_canonical_serialization_is_deterministic |
| TC-HASH-002 | MCC-TC-001 | 13. Cryptographic Integrity / 13.4 Cryptographic Integrity Invariants | PARTIAL | src/mcc_core/signing.py | tests/test_mcc_core.py::test_sign_and_verify_roundtrip; tests/test_mcc_core.py::test_canonical_serialization_is_deterministic |
| TC-HASH-003 | MCC-TC-001 | 13. Cryptographic Integrity / 13.4 Cryptographic Integrity Invariants | PARTIAL | src/mcc_core/signing.py | tests/test_mcc_core.py::test_sign_and_verify_roundtrip; tests/test_mcc_core.py::test_canonical_serialization_is_deterministic |
| TC-ID-001 | MCC-TC-001 | 5. Certificate Identity / 5.4 Certificate Identity Invariants | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| TC-ID-002 | MCC-TC-001 | 5. Certificate Identity / 5.4 Certificate Identity Invariants | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| TC-ID-003 | MCC-TC-001 | 5. Certificate Identity / 5.4 Certificate Identity Invariants | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| TC-ISS-001 | MCC-TC-001 | 10. Issuer Information / 10.4 Issuer Information Invariants | PARTIAL | gateway/trust.py | tests/test_trust.py |
| TC-ISS-002 | MCC-TC-001 | 10. Issuer Information / 10.4 Issuer Information Invariants | PARTIAL | gateway/trust.py | tests/test_trust.py |
| TC-ISS-003 | MCC-TC-001 | 10. Issuer Information / 10.4 Issuer Information Invariants | PARTIAL | gateway/trust.py | tests/test_trust.py |
| TC-MODEL-001 | MCC-TC-001 | 3. Certificate Model / 3.5 Certificate Model Invariants | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| TC-MODEL-002 | MCC-TC-001 | 3. Certificate Model / 3.5 Certificate Model Invariants | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| TC-MODEL-003 | MCC-TC-001 | 3. Certificate Model / 3.5 Certificate Model Invariants | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| TC-MODEL-004 | MCC-TC-001 | 3. Certificate Model / 3.5 Certificate Model Invariants | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| TC-OPTF-001 | MCC-TC-001 | 7. Optional Fields / 7.4 Optional Fields Invariants | GAP | — | — |
| TC-OPTF-002 | MCC-TC-001 | 7. Optional Fields / 7.4 Optional Fields Invariants | GAP | — | — |
| TC-OPTF-003 | MCC-TC-001 | 7. Optional Fields / 7.4 Optional Fields Invariants | GAP | — | — |
| TC-RES-001 | MCC-TC-001 | 9. Certification Result Representation / 9.5 Certification Result Representation Invariants | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| TC-RES-002 | MCC-TC-001 | 9. Certification Result Representation / 9.5 Certification Result Representation Invariants | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| TC-RES-003 | MCC-TC-001 | 9. Certification Result Representation / 9.5 Certification Result Representation Invariants | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| TC-REV-001 | MCC-TC-001 | 12. Revocation Model / 12.7 Revocation Model Invariants | PARTIAL | gateway/trust.py | tests/test_trust.py |
| TC-REV-002 | MCC-TC-001 | 12. Revocation Model / 12.7 Revocation Model Invariants | PARTIAL | gateway/trust.py | tests/test_trust.py |
| TC-REV-003 | MCC-TC-001 | 12. Revocation Model / 12.7 Revocation Model Invariants | PARTIAL | gateway/trust.py | tests/test_trust.py |
| TC-REV-004 | MCC-TC-001 | 12. Revocation Model / 12.7 Revocation Model Invariants | PARTIAL | gateway/trust.py | tests/test_trust.py |
| TC-REV-005 | MCC-TC-001 | 12. Revocation Model / 12.7 Revocation Model Invariants | PARTIAL | gateway/trust.py | tests/test_trust.py |
| TC-REV-006 | MCC-TC-001 | 12. Revocation Model / 12.7 Revocation Model Invariants | PARTIAL | gateway/trust.py | tests/test_trust.py |
| TC-RFLD-001 | MCC-TC-001 | 6. Required Fields / 6.7 Required Fields Invariants | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| TC-RFLD-002 | MCC-TC-001 | 6. Required Fields / 6.7 Required Fields Invariants | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| TC-RFLD-003 | MCC-TC-001 | 6. Required Fields / 6.7 Required Fields Invariants | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| TC-RFLD-004 | MCC-TC-001 | 6. Required Fields / 6.7 Required Fields Invariants | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| TC-RFLD-005 | MCC-TC-001 | 6. Required Fields / 6.7 Required Fields Invariants | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| TC-RFLD-006 | MCC-TC-001 | 6. Required Fields / 6.7 Required Fields Invariants | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| TC-RID-001 | MCC-TC-001 | 22. Requirement Identifier Registry / 22.5 Registry Invariants | NOT_APPLICABLE | — | — |
| TC-RID-002 | MCC-TC-001 | 22. Requirement Identifier Registry / 22.5 Registry Invariants | NOT_APPLICABLE | — | — |
| TC-RID-003 | MCC-TC-001 | 22. Requirement Identifier Registry / 22.5 Registry Invariants | NOT_APPLICABLE | — | — |
| TC-RID-004 | MCC-TC-001 | 22. Requirement Identifier Registry / 22.5 Registry Invariants | NOT_APPLICABLE | — | — |
| TC-SCHEMA-001 | MCC-TC-001 | 4. Certificate Schema / 4.5 Certificate Schema Invariants | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| TC-SCHEMA-002 | MCC-TC-001 | 4. Certificate Schema / 4.5 Certificate Schema Invariants | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| TC-SCHEMA-003 | MCC-TC-001 | 4. Certificate Schema / 4.5 Certificate Schema Invariants | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| TC-SCHEMA-004 | MCC-TC-001 | 4. Certificate Schema / 4.5 Certificate Schema Invariants | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| TC-SCHEMA-005 | MCC-TC-001 | 4. Certificate Schema / 4.5 Certificate Schema Invariants | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| TC-SEC-001 | MCC-TC-001 | 19. Security Considerations / 19.6 Security Invariants | PARTIAL | gateway/trust.py | tests/test_trust.py |
| TC-SEC-002 | MCC-TC-001 | 19. Security Considerations / 19.6 Security Invariants | PARTIAL | gateway/trust.py | tests/test_trust.py |
| TC-SEC-003 | MCC-TC-001 | 19. Security Considerations / 19.6 Security Invariants | PARTIAL | gateway/trust.py | tests/test_trust.py |
| TC-SEC-004 | MCC-TC-001 | 19. Security Considerations / 19.6 Security Invariants | PARTIAL | gateway/trust.py | tests/test_trust.py |
| TC-SEC-005 | MCC-TC-001 | 19. Security Considerations / 19.6 Security Invariants | PARTIAL | gateway/trust.py | tests/test_trust.py |
| TC-SIG-001 | MCC-TC-001 | 14. Signature Requirements / 14.5 Signature Requirements Invariants | PARTIAL | src/mcc_core/signing.py | tests/test_mcc_core.py::test_sign_and_verify_roundtrip; tests/test_mcc_core.py::test_canonical_serialization_is_deterministic |
| TC-SIG-002 | MCC-TC-001 | 14. Signature Requirements / 14.5 Signature Requirements Invariants | PARTIAL | src/mcc_core/signing.py | tests/test_mcc_core.py::test_sign_and_verify_roundtrip; tests/test_mcc_core.py::test_canonical_serialization_is_deterministic |
| TC-SIG-003 | MCC-TC-001 | 14. Signature Requirements / 14.5 Signature Requirements Invariants | PARTIAL | src/mcc_core/signing.py | tests/test_mcc_core.py::test_sign_and_verify_roundtrip; tests/test_mcc_core.py::test_canonical_serialization_is_deterministic |
| TC-SIG-004 | MCC-TC-001 | 14. Signature Requirements / 14.5 Signature Requirements Invariants | PARTIAL | src/mcc_core/signing.py | tests/test_mcc_core.py::test_sign_and_verify_roundtrip; tests/test_mcc_core.py::test_canonical_serialization_is_deterministic |
| TC-SIG-005 | MCC-TC-001 | 14. Signature Requirements / 14.5 Signature Requirements Invariants | PARTIAL | src/mcc_core/signing.py | tests/test_mcc_core.py::test_sign_and_verify_roundtrip; tests/test_mcc_core.py::test_canonical_serialization_is_deterministic |
| TC-SUBJ-001 | MCC-TC-001 | 8. Subject Identification / 8.4 Subject Identification Invariants | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| TC-SUBJ-002 | MCC-TC-001 | 8. Subject Identification / 8.4 Subject Identification Invariants | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| TC-SUBJ-003 | MCC-TC-001 | 8. Subject Identification / 8.4 Subject Identification Invariants | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| TC-TRUST-001 | MCC-TC-001 | 16. Trust Model / 16.6 Trust Model Invariants | PARTIAL | gateway/trust.py | tests/test_trust.py |
| TC-TRUST-002 | MCC-TC-001 | 16. Trust Model / 16.6 Trust Model Invariants | PARTIAL | gateway/trust.py | tests/test_trust.py |
| TC-TRUST-003 | MCC-TC-001 | 16. Trust Model / 16.6 Trust Model Invariants | PARTIAL | gateway/trust.py | tests/test_trust.py |
| TC-TRUST-004 | MCC-TC-001 | 16. Trust Model / 16.6 Trust Model Invariants | PARTIAL | gateway/trust.py | tests/test_trust.py |
| TC-VALID-001 | MCC-TC-001 | 11. Validity Period / 11.4 Validity Period Invariants | PARTIAL | gateway/trust.py | tests/test_trust.py |
| TC-VALID-002 | MCC-TC-001 | 11. Validity Period / 11.4 Validity Period Invariants | PARTIAL | gateway/trust.py | tests/test_trust.py |
| TC-VALID-003 | MCC-TC-001 | 11. Validity Period / 11.4 Validity Period Invariants | PARTIAL | gateway/trust.py | tests/test_trust.py |
| TC-VALID-004 | MCC-TC-001 | 11. Validity Period / 11.4 Validity Period Invariants | PARTIAL | gateway/trust.py | tests/test_trust.py |
| TC-VERIFY-001 | MCC-TC-001 | 15. Verification Procedure / 15.9 Verification Procedure Invariants | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| TC-VERIFY-002 | MCC-TC-001 | 15. Verification Procedure / 15.9 Verification Procedure Invariants | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| TC-VERIFY-003 | MCC-TC-001 | 15. Verification Procedure / 15.9 Verification Procedure Invariants | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| TC-VERIFY-004 | MCC-TC-001 | 15. Verification Procedure / 15.9 Verification Procedure Invariants | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| TC-VERIFY-005 | MCC-TC-001 | 15. Verification Procedure / 15.9 Verification Procedure Invariants | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| TC-VERIFY-006 | MCC-TC-001 | 15. Verification Procedure / 15.9 Verification Procedure Invariants | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| TC-VSN-001 | MCC-TC-001 | 18. Versioning / 18.5 Versioning Invariants | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| TC-VSN-002 | MCC-TC-001 | 18. Versioning / 18.5 Versioning Invariants | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| TC-VSN-003 | MCC-TC-001 | 18. Versioning / 18.5 Versioning Invariants | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| TC-VSN-004 | MCC-TC-001 | 18. Versioning / 18.5 Versioning Invariants | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |

## Limitations of This Assessment

- Assessment was performed at requirement-category granularity, not as an independently bespoke code review of all 429 individual requirements. Requirements sharing a specification section and normative theme share a status and rationale unless repository evidence specifically distinguished them. This is disclosed, not hidden.
- No requirement is marked CONFORMANT in this baseline. That status requires both an implementation and a meaningful automated test tied to the specific requirement; as of the reviewed commit, no code in this repository implements the Evidence Bundle, Certification Manifest, Technical Certificate, or Certification Program process these specifications define.
- PARTIAL status is granted only for two narrow, independently verifiable primitives (deterministic canonical serialization / digest, and Ed25519-only / asymmetric-only signing) that exist and are tested for a different artifact (the runtime Decision Token) and are not wired to any Evidence Bundle, Manifest, or Certificate object.
- This assessment does not execute or validate any generated Evidence Bundle, Manifest, or Certificate, because none exist to generate. It is a static, source-level trace only.

## Reproduction

```
python -m mcc_conformance generate
python -m mcc_conformance validate
pytest tests/test_conformance_baseline.py -v
```

