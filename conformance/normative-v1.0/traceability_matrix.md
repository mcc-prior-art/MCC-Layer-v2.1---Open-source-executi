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
| MCC-CP-001 | 340 |
| MCC-EB-001 | 144 |
| MCC-CM-001 | 130 |
| MCC-TC-001 | 196 |
| **Total** | **810** |

## Totals by Conformance Status

| Status | Count | % of total |
|---|---|---|
| CONFORMANT | 13 | 1.6% |
| PARTIAL | 593 | 73.2% |
| GAP | 114 | 14.1% |
| NOT_APPLICABLE | 90 | 11.1% |
| NOT_ASSESSED | 0 | 0.0% |

**Conformance coverage (CONFORMANT / applicable requirements): 1.8% (13/720)**

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
| CM-HASH-001 | MCC-CM-001 | 13. Hash References / 13.5 Hash Reference Invariants | CONFORMANT | src/mcc_evidence/hash_reference.py | tests/test_hash_reference.py |
| CM-HASH-002 | MCC-CM-001 | 13. Hash References / 13.5 Hash Reference Invariants | CONFORMANT | src/mcc_evidence/hash_reference.py | tests/test_hash_reference.py |
| CM-HASH-003 | MCC-CM-001 | 13. Hash References / 13.5 Hash Reference Invariants | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| CM-HASH-004 | MCC-CM-001 | 13. Hash References / 13.5 Hash Reference Invariants | CONFORMANT | src/mcc_evidence/hash_reference.py | tests/test_hash_reference.py |
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
| MCC-CM-001-10-MANIFEST-SCHEMA-D01 | MCC-CM-001 | 10. Manifest Schema / 10.2 Top-Level Structure | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| MCC-CM-001-10-MANIFEST-SCHEMA-D02 | MCC-CM-001 | 10. Manifest Schema / 10.3 Field Typing | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| MCC-CM-001-10-MANIFEST-SCHEMA-D03 | MCC-CM-001 | 10. Manifest Schema / 10.3 Field Typing | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| MCC-CM-001-10-MANIFEST-SCHEMA-D04 | MCC-CM-001 | 10. Manifest Schema / 10.4 Canonical Form | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| MCC-CM-001-11-REQUIRED-FIELDS-D01 | MCC-CM-001 | 11. Required Fields / 11.1 Purpose | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| MCC-CM-001-11-REQUIRED-FIELDS-D02 | MCC-CM-001 | 11. Required Fields / 11.2 Identification Fields | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| MCC-CM-001-11-REQUIRED-FIELDS-D03 | MCC-CM-001 | 11. Required Fields / 11.3 Baseline Required Fields | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| MCC-CM-001-11-REQUIRED-FIELDS-D04 | MCC-CM-001 | 11. Required Fields / 11.4 Field Presence Rule | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| MCC-CM-001-12-OPTIONAL-FIELDS-D01 | MCC-CM-001 | 12. Optional Fields / 12.3 Optional Field Constraints | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| MCC-CM-001-12-OPTIONAL-FIELDS-D02 | MCC-CM-001 | 12. Optional Fields / 12.3 Optional Field Constraints | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| MCC-CM-001-12-OPTIONAL-FIELDS-D03 | MCC-CM-001 | 12. Optional Fields / 12.3 Optional Field Constraints | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| MCC-CM-001-13-HASH-REFERENCES-D01 | MCC-CM-001 | 13. Hash References / 13.2 Hash Reference Structure | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| MCC-CM-001-13-HASH-REFERENCES-D02 | MCC-CM-001 | 13. Hash References / 13.3 Hash Algorithm Requirements | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| MCC-CM-001-13-HASH-REFERENCES-D03 | MCC-CM-001 | 13. Hash References / 13.3 Hash Algorithm Requirements | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| MCC-CM-001-13-HASH-REFERENCES-D04 | MCC-CM-001 | 13. Hash References / 13.4 Hash Reference Usage | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| MCC-CM-001-14-EVIDENCE-BUNDLE-REFERENCES-D01 | MCC-CM-001 | 14. Evidence Bundle References / 14.2 Primary Evidence Bundle Reference | GAP | — | — |
| MCC-CM-001-14-EVIDENCE-BUNDLE-REFERENCES-D02 | MCC-CM-001 | 14. Evidence Bundle References / 14.2 Primary Evidence Bundle Reference | GAP | — | — |
| MCC-CM-001-14-EVIDENCE-BUNDLE-REFERENCES-D03 | MCC-CM-001 | 14. Evidence Bundle References / 14.3 Supplementary Evidence Bundle References | GAP | — | — |
| MCC-CM-001-14-EVIDENCE-BUNDLE-REFERENCES-D04 | MCC-CM-001 | 14. Evidence Bundle References / 14.4 Reference Integrity | GAP | — | — |
| MCC-CM-001-14-EVIDENCE-BUNDLE-REFERENCES-D05 | MCC-CM-001 | 14. Evidence Bundle References / 14.4 Reference Integrity | GAP | — | — |
| MCC-CM-001-15-CERTIFICATION-METADATA-D01 | MCC-CM-001 | 15. Certification Metadata / 15.2 Subject and Scope Metadata | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| MCC-CM-001-15-CERTIFICATION-METADATA-D02 | MCC-CM-001 | 15. Certification Metadata / 15.3 Certification Result | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| MCC-CM-001-15-CERTIFICATION-METADATA-D03 | MCC-CM-001 | 15. Certification Metadata / 15.3 Certification Result | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| MCC-CM-001-15-CERTIFICATION-METADATA-D04 | MCC-CM-001 | 15. Certification Metadata / 15.4 Requirement Results | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| MCC-CM-001-15-CERTIFICATION-METADATA-D05 | MCC-CM-001 | 15. Certification Metadata / 15.4 Requirement Results | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| MCC-CM-001-15-CERTIFICATION-METADATA-D06 | MCC-CM-001 | 15. Certification Metadata / 15.5 Generation Metadata | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| MCC-CM-001-16-VERSIONING-RULES-D01 | MCC-CM-001 | 16. Versioning Rules / 16.2 Schema Version Declaration | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| MCC-CM-001-16-VERSIONING-RULES-D02 | MCC-CM-001 | 16. Versioning Rules / 16.2 Schema Version Declaration | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| MCC-CM-001-16-VERSIONING-RULES-D03 | MCC-CM-001 | 16. Versioning Rules / 16.3 Schema Version Scope | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| MCC-CM-001-16-VERSIONING-RULES-D04 | MCC-CM-001 | 16. Versioning Rules / 16.4 Version Evolution | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| MCC-CM-001-17-COMPATIBILITY-RULES-D01 | MCC-CM-001 | 17. Compatibility Rules / 17.3 Forward Compatibility | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| MCC-CM-001-17-COMPATIBILITY-RULES-D02 | MCC-CM-001 | 17. Compatibility Rules / 17.3 Forward Compatibility | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| MCC-CM-001-17-COMPATIBILITY-RULES-D03 | MCC-CM-001 | 17. Compatibility Rules / 17.4 Breaking Changes | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| MCC-CM-001-17-COMPATIBILITY-RULES-D04 | MCC-CM-001 | 17. Compatibility Rules / 17.5 Cross-Specification Compatibility | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| MCC-CM-001-18-VALIDATION-RULES-D01 | MCC-CM-001 | 18. Validation Rules / 18.1 Purpose | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| MCC-CM-001-18-VALIDATION-RULES-D02 | MCC-CM-001 | 18. Validation Rules / 18.2 Structural Validation | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| MCC-CM-001-18-VALIDATION-RULES-D03 | MCC-CM-001 | 18. Validation Rules / 18.2 Structural Validation | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| MCC-CM-001-18-VALIDATION-RULES-D04 | MCC-CM-001 | 18. Validation Rules / 18.3 Hash Reference Validation | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| MCC-CM-001-18-VALIDATION-RULES-D05 | MCC-CM-001 | 18. Validation Rules / 18.3 Hash Reference Validation | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| MCC-CM-001-18-VALIDATION-RULES-D06 | MCC-CM-001 | 18. Validation Rules / 18.4 Evidence Bundle Reference Validation | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| MCC-CM-001-18-VALIDATION-RULES-D07 | MCC-CM-001 | 18. Validation Rules / 18.4 Evidence Bundle Reference Validation | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| MCC-CM-001-18-VALIDATION-RULES-D08 | MCC-CM-001 | 18. Validation Rules / 18.5 Metadata Consistency Validation | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| MCC-CM-001-18-VALIDATION-RULES-D09 | MCC-CM-001 | 18. Validation Rules / 18.6 Fail-Closed Validation | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| MCC-CM-001-18-VALIDATION-RULES-D10 | MCC-CM-001 | 18. Validation Rules / 18.6 Fail-Closed Validation | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| MCC-CM-001-19-SECURITY-CONSIDERATIONS-D01 | MCC-CM-001 | 19. Security Considerations / 19.2 Threat Model | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| MCC-CM-001-19-SECURITY-CONSIDERATIONS-D02 | MCC-CM-001 | 19. Security Considerations / 19.4 Sensitive Data | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| MCC-CM-001-19-SECURITY-CONSIDERATIONS-D03 | MCC-CM-001 | 19. Security Considerations / 19.4 Sensitive Data | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| MCC-CM-001-2-ABSTRACT-D01 | MCC-CM-001 | 2. Abstract | NOT_APPLICABLE | — | — |
| MCC-CM-001-20-EXTENSION-MODEL-D01 | MCC-CM-001 | 20. Extension Model / 20.2 Extension Points | GAP | — | — |
| MCC-CM-001-20-EXTENSION-MODEL-D02 | MCC-CM-001 | 20. Extension Model / 20.3 Extension Constraints | GAP | — | — |
| MCC-CM-001-20-EXTENSION-MODEL-D03 | MCC-CM-001 | 20. Extension Model / 20.3 Extension Constraints | GAP | — | — |
| MCC-CM-001-22-CONFORMANCE-REQUIREMENTS-D01 | MCC-CM-001 | 22. Conformance Requirements / 22.2 Conforming Manifest Producer | GAP | — | — |
| MCC-CM-001-22-CONFORMANCE-REQUIREMENTS-D02 | MCC-CM-001 | 22. Conformance Requirements / 22.2 Conforming Manifest Producer | GAP | — | — |
| MCC-CM-001-22-CONFORMANCE-REQUIREMENTS-D03 | MCC-CM-001 | 22. Conformance Requirements / 22.3 Conforming Manifest Validator | GAP | — | — |
| MCC-CM-001-22-CONFORMANCE-REQUIREMENTS-D04 | MCC-CM-001 | 22. Conformance Requirements / 22.3 Conforming Manifest Validator | GAP | — | — |
| MCC-CM-001-22-CONFORMANCE-REQUIREMENTS-D05 | MCC-CM-001 | 22. Conformance Requirements / 22.4 Conformance Independence | GAP | — | — |
| MCC-CM-001-23-REQUIREMENT-IDENTIFIER-REGISTRY-D01 | MCC-CM-001 | 23. Requirement Identifier Registry / 23.2 Namespace Convention | NOT_APPLICABLE | — | — |
| MCC-CM-001-23-REQUIREMENT-IDENTIFIER-REGISTRY-D02 | MCC-CM-001 | 23. Requirement Identifier Registry / 23.4 Registry Requirements | NOT_APPLICABLE | — | — |
| MCC-CM-001-23-REQUIREMENT-IDENTIFIER-REGISTRY-D03 | MCC-CM-001 | 23. Requirement Identifier Registry / 23.4 Registry Requirements | NOT_APPLICABLE | — | — |
| MCC-CM-001-23-REQUIREMENT-IDENTIFIER-REGISTRY-D04 | MCC-CM-001 | 23. Requirement Identifier Registry / 23.4 Registry Requirements | NOT_APPLICABLE | — | — |
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
| MCC-CP-001-10-CONFORMANCE-MODEL-D01 | MCC-CP-001 | 10. Conformance Model / 10.1 Purpose | PARTIAL | src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json | tests/test_compliance_suite.py |
| MCC-CP-001-10-CONFORMANCE-MODEL-D02 | MCC-CP-001 | 10. Conformance Model / 10.1 Purpose | PARTIAL | src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json | tests/test_compliance_suite.py |
| MCC-CP-001-10-CONFORMANCE-MODEL-D03 | MCC-CP-001 | 10. Conformance Model / 10.2 Normative Requirements | PARTIAL | src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json | tests/test_compliance_suite.py |
| MCC-CP-001-10-CONFORMANCE-MODEL-D04 | MCC-CP-001 | 10. Conformance Model / 10.2 Normative Requirements | PARTIAL | src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json | tests/test_compliance_suite.py |
| MCC-CP-001-10-CONFORMANCE-MODEL-D05 | MCC-CP-001 | 10. Conformance Model / 10.2 Normative Requirements | PARTIAL | src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json | tests/test_compliance_suite.py |
| MCC-CP-001-10-CONFORMANCE-MODEL-D06 | MCC-CP-001 | 10. Conformance Model / 10.3 Requirement Classification | PARTIAL | src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json | tests/test_compliance_suite.py |
| MCC-CP-001-10-CONFORMANCE-MODEL-D07 | MCC-CP-001 | 10. Conformance Model / 10.3 Requirement Classification | PARTIAL | src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json | tests/test_compliance_suite.py |
| MCC-CP-001-10-CONFORMANCE-MODEL-D08 | MCC-CP-001 | 10. Conformance Model / 10.3 Requirement Classification | PARTIAL | src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json | tests/test_compliance_suite.py |
| MCC-CP-001-10-CONFORMANCE-MODEL-D09 | MCC-CP-001 | 10. Conformance Model / 10.3 Requirement Classification | PARTIAL | src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json | tests/test_compliance_suite.py |
| MCC-CP-001-10-CONFORMANCE-MODEL-D10 | MCC-CP-001 | 10. Conformance Model / 10.4 Conformance Evaluation | PARTIAL | src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json | tests/test_compliance_suite.py |
| MCC-CP-001-10-CONFORMANCE-MODEL-D11 | MCC-CP-001 | 10. Conformance Model / 10.5 Overall Conformance | PARTIAL | src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json | tests/test_compliance_suite.py |
| MCC-CP-001-10-CONFORMANCE-MODEL-D12 | MCC-CP-001 | 10. Conformance Model / 10.5 Overall Conformance | PARTIAL | src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json | tests/test_compliance_suite.py |
| MCC-CP-001-10-CONFORMANCE-MODEL-D13 | MCC-CP-001 | 10. Conformance Model / 10.5 Overall Conformance | PARTIAL | src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json | tests/test_compliance_suite.py |
| MCC-CP-001-11-CAPABILITY-PROFILES-D01 | MCC-CP-001 | 11. Capability Profiles / 11.2 Capability Profile Identifier | PARTIAL | src/mcc_compliance/capability_profile.py | tests/test_capability_profile.py |
| MCC-CP-001-11-CAPABILITY-PROFILES-D02 | MCC-CP-001 | 11. Capability Profiles / 11.2 Capability Profile Identifier | PARTIAL | src/mcc_compliance/capability_profile.py | tests/test_capability_profile.py |
| MCC-CP-001-11-CAPABILITY-PROFILES-D03 | MCC-CP-001 | 11. Capability Profiles / 11.2 Capability Profile Identifier | PARTIAL | src/mcc_compliance/capability_profile.py | tests/test_capability_profile.py |
| MCC-CP-001-11-CAPABILITY-PROFILES-D04 | MCC-CP-001 | 11. Capability Profiles / 11.3 Capability Definition | PARTIAL | src/mcc_compliance/capability_profile.py | tests/test_capability_profile.py |
| MCC-CP-001-11-CAPABILITY-PROFILES-D05 | MCC-CP-001 | 11. Capability Profiles / 11.3 Capability Definition | PARTIAL | src/mcc_compliance/capability_profile.py | tests/test_capability_profile.py |
| MCC-CP-001-11-CAPABILITY-PROFILES-D06 | MCC-CP-001 | 11. Capability Profiles / 11.4 Capability Evaluation | PARTIAL | src/mcc_compliance/capability_profile.py | tests/test_capability_profile.py |
| MCC-CP-001-11-CAPABILITY-PROFILES-D07 | MCC-CP-001 | 11. Capability Profiles / 11.4 Capability Evaluation | PARTIAL | src/mcc_compliance/capability_profile.py | tests/test_capability_profile.py |
| MCC-CP-001-11-CAPABILITY-PROFILES-D08 | MCC-CP-001 | 11. Capability Profiles / 11.4 Capability Evaluation | PARTIAL | src/mcc_compliance/capability_profile.py | tests/test_capability_profile.py |
| MCC-CP-001-11-CAPABILITY-PROFILES-D09 | MCC-CP-001 | 11. Capability Profiles / 11.5 Capability Dependencies | PARTIAL | src/mcc_compliance/capability_profile.py | tests/test_capability_profile.py |
| MCC-CP-001-11-CAPABILITY-PROFILES-D10 | MCC-CP-001 | 11. Capability Profiles / 11.5 Capability Dependencies | PARTIAL | src/mcc_compliance/capability_profile.py | tests/test_capability_profile.py |
| MCC-CP-001-11-CAPABILITY-PROFILES-D11 | MCC-CP-001 | 11. Capability Profiles / 11.6 Capability Claims | PARTIAL | src/mcc_compliance/capability_profile.py | tests/test_capability_profile.py |
| MCC-CP-001-11-CAPABILITY-PROFILES-D12 | MCC-CP-001 | 11. Capability Profiles / 11.6 Capability Claims | PARTIAL | src/mcc_compliance/capability_profile.py | tests/test_capability_profile.py |
| MCC-CP-001-12-CERTIFICATION-REQUIREMENTS-D01 | MCC-CP-001 | 12. Certification Requirements / 12.1 Purpose | PARTIAL | src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json | tests/test_compliance_suite.py |
| MCC-CP-001-12-CERTIFICATION-REQUIREMENTS-D02 | MCC-CP-001 | 12. Certification Requirements / 12.1 Purpose | PARTIAL | src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json | tests/test_compliance_suite.py |
| MCC-CP-001-12-CERTIFICATION-REQUIREMENTS-D03 | MCC-CP-001 | 12. Certification Requirements / 12.1 Purpose | PARTIAL | src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json | tests/test_compliance_suite.py |
| MCC-CP-001-12-CERTIFICATION-REQUIREMENTS-D04 | MCC-CP-001 | 12. Certification Requirements / 12.2 Requirement Identifier | PARTIAL | src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json | tests/test_compliance_suite.py |
| MCC-CP-001-12-CERTIFICATION-REQUIREMENTS-D05 | MCC-CP-001 | 12. Certification Requirements / 12.2 Requirement Identifier | PARTIAL | src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json | tests/test_compliance_suite.py |
| MCC-CP-001-12-CERTIFICATION-REQUIREMENTS-D06 | MCC-CP-001 | 12. Certification Requirements / 12.3 Requirement Applicability | PARTIAL | src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json | tests/test_compliance_suite.py |
| MCC-CP-001-12-CERTIFICATION-REQUIREMENTS-D07 | MCC-CP-001 | 12. Certification Requirements / 12.3 Requirement Applicability | PARTIAL | src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json | tests/test_compliance_suite.py |
| MCC-CP-001-12-CERTIFICATION-REQUIREMENTS-D08 | MCC-CP-001 | 12. Certification Requirements / 12.4 Requirement Verification | PARTIAL | src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json | tests/test_compliance_suite.py |
| MCC-CP-001-12-CERTIFICATION-REQUIREMENTS-D09 | MCC-CP-001 | 12. Certification Requirements / 12.4 Requirement Verification | PARTIAL | src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json | tests/test_compliance_suite.py |
| MCC-CP-001-12-CERTIFICATION-REQUIREMENTS-D10 | MCC-CP-001 | 12. Certification Requirements / 12.4 Requirement Verification | PARTIAL | src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json | tests/test_compliance_suite.py |
| MCC-CP-001-12-CERTIFICATION-REQUIREMENTS-D11 | MCC-CP-001 | 12. Certification Requirements / 12.5 Requirement Traceability | PARTIAL | src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json | tests/test_compliance_suite.py |
| MCC-CP-001-12-CERTIFICATION-REQUIREMENTS-D12 | MCC-CP-001 | 12. Certification Requirements / 12.5 Requirement Traceability | PARTIAL | src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json | tests/test_compliance_suite.py |
| MCC-CP-001-13-REQUIREMENT-CLASSIFICATION-D01 | MCC-CP-001 | 13. Requirement Classification / 13.1 Purpose | PARTIAL | src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json | tests/test_compliance_suite.py |
| MCC-CP-001-13-REQUIREMENT-CLASSIFICATION-D02 | MCC-CP-001 | 13. Requirement Classification / 13.1 Purpose | PARTIAL | src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json | tests/test_compliance_suite.py |
| MCC-CP-001-13-REQUIREMENT-CLASSIFICATION-D03 | MCC-CP-001 | 13. Requirement Classification / 13.2 Classification Categories | PARTIAL | src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json | tests/test_compliance_suite.py |
| MCC-CP-001-13-REQUIREMENT-CLASSIFICATION-D04 | MCC-CP-001 | 13. Requirement Classification / 13.2 Classification Categories | PARTIAL | src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json | tests/test_compliance_suite.py |
| MCC-CP-001-13-REQUIREMENT-CLASSIFICATION-D05 | MCC-CP-001 | 13. Requirement Classification / 13.3 REQUIRED Requirements | PARTIAL | src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json | tests/test_compliance_suite.py |
| MCC-CP-001-13-REQUIREMENT-CLASSIFICATION-D06 | MCC-CP-001 | 13. Requirement Classification / 13.3 REQUIRED Requirements | PARTIAL | src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json | tests/test_compliance_suite.py |
| MCC-CP-001-13-REQUIREMENT-CLASSIFICATION-D07 | MCC-CP-001 | 13. Requirement Classification / 13.4 OPTIONAL Requirements | PARTIAL | src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json | tests/test_compliance_suite.py |
| MCC-CP-001-13-REQUIREMENT-CLASSIFICATION-D08 | MCC-CP-001 | 13. Requirement Classification / 13.5 CONDITIONAL Requirements | PARTIAL | src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json | tests/test_compliance_suite.py |
| MCC-CP-001-13-REQUIREMENT-CLASSIFICATION-D09 | MCC-CP-001 | 13. Requirement Classification / 13.5 CONDITIONAL Requirements | PARTIAL | src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json | tests/test_compliance_suite.py |
| MCC-CP-001-14-EVIDENCE-REQUIREMENTS-D01 | MCC-CP-001 | 14. Evidence Requirements / 14.1 Purpose | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| MCC-CP-001-14-EVIDENCE-REQUIREMENTS-D02 | MCC-CP-001 | 14. Evidence Requirements / 14.1 Purpose | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| MCC-CP-001-14-EVIDENCE-REQUIREMENTS-D03 | MCC-CP-001 | 14. Evidence Requirements / 14.2 Evidence Sources | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| MCC-CP-001-14-EVIDENCE-REQUIREMENTS-D04 | MCC-CP-001 | 14. Evidence Requirements / 14.3 Evidence Properties | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| MCC-CP-001-14-EVIDENCE-REQUIREMENTS-D05 | MCC-CP-001 | 14. Evidence Requirements / 14.3 Evidence Properties | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| MCC-CP-001-14-EVIDENCE-REQUIREMENTS-D06 | MCC-CP-001 | 14. Evidence Requirements / 14.4 Evidence Traceability | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| MCC-CP-001-14-EVIDENCE-REQUIREMENTS-D07 | MCC-CP-001 | 14. Evidence Requirements / 14.4 Evidence Traceability | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| MCC-CP-001-14-EVIDENCE-REQUIREMENTS-D08 | MCC-CP-001 | 14. Evidence Requirements / 14.5 Evidence Retention | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| MCC-CP-001-14-EVIDENCE-REQUIREMENTS-D09 | MCC-CP-001 | 14. Evidence Requirements / 14.5 Evidence Retention | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| MCC-CP-001-15-CERTIFICATION-MANIFEST-REQUIREMENTS-D01 | MCC-CP-001 | 15. Certification Manifest Requirements / 15.1 Purpose | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| MCC-CP-001-15-CERTIFICATION-MANIFEST-REQUIREMENTS-D02 | MCC-CP-001 | 15. Certification Manifest Requirements / 15.2 Manifest Contents | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| MCC-CP-001-15-CERTIFICATION-MANIFEST-REQUIREMENTS-D03 | MCC-CP-001 | 15. Certification Manifest Requirements / 15.3 Manifest Integrity | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| MCC-CP-001-15-CERTIFICATION-MANIFEST-REQUIREMENTS-D04 | MCC-CP-001 | 15. Certification Manifest Requirements / 15.3 Manifest Integrity | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| MCC-CP-001-15-CERTIFICATION-MANIFEST-REQUIREMENTS-D05 | MCC-CP-001 | 15. Certification Manifest Requirements / 15.3 Manifest Integrity | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| MCC-CP-001-15-CERTIFICATION-MANIFEST-REQUIREMENTS-D06 | MCC-CP-001 | 15. Certification Manifest Requirements / 15.4 Manifest Traceability | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| MCC-CP-001-15-CERTIFICATION-MANIFEST-REQUIREMENTS-D07 | MCC-CP-001 | 15. Certification Manifest Requirements / 15.5 Manifest Versioning | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| MCC-CP-001-15-CERTIFICATION-MANIFEST-REQUIREMENTS-D08 | MCC-CP-001 | 15. Certification Manifest Requirements / 15.5 Manifest Versioning | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| MCC-CP-001-16-TECHNICAL-CERTIFICATE-REQUIREMENTS-D01 | MCC-CP-001 | 16. Technical Certificate Requirements / 16.1 Purpose | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| MCC-CP-001-16-TECHNICAL-CERTIFICATE-REQUIREMENTS-D02 | MCC-CP-001 | 16. Technical Certificate Requirements / 16.1 Purpose | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| MCC-CP-001-16-TECHNICAL-CERTIFICATE-REQUIREMENTS-D03 | MCC-CP-001 | 16. Technical Certificate Requirements / 16.2 Certificate Contents | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| MCC-CP-001-16-TECHNICAL-CERTIFICATE-REQUIREMENTS-D04 | MCC-CP-001 | 16. Technical Certificate Requirements / 16.3 Certificate Issuance | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| MCC-CP-001-16-TECHNICAL-CERTIFICATE-REQUIREMENTS-D05 | MCC-CP-001 | 16. Technical Certificate Requirements / 16.3 Certificate Issuance | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| MCC-CP-001-16-TECHNICAL-CERTIFICATE-REQUIREMENTS-D06 | MCC-CP-001 | 16. Technical Certificate Requirements / 16.4 Certificate Integrity | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| MCC-CP-001-16-TECHNICAL-CERTIFICATE-REQUIREMENTS-D07 | MCC-CP-001 | 16. Technical Certificate Requirements / 16.4 Certificate Integrity | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| MCC-CP-001-16-TECHNICAL-CERTIFICATE-REQUIREMENTS-D08 | MCC-CP-001 | 16. Technical Certificate Requirements / 16.4 Certificate Integrity | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| MCC-CP-001-16-TECHNICAL-CERTIFICATE-REQUIREMENTS-D09 | MCC-CP-001 | 16. Technical Certificate Requirements / 16.5 Certificate Traceability | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| MCC-CP-001-17-VERSIONING-D01 | MCC-CP-001 | 17. Versioning / 17.1 Purpose | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| MCC-CP-001-17-VERSIONING-D02 | MCC-CP-001 | 17. Versioning / 17.1 Purpose | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| MCC-CP-001-17-VERSIONING-D03 | MCC-CP-001 | 17. Versioning / 17.2 Specification Versions | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| MCC-CP-001-17-VERSIONING-D04 | MCC-CP-001 | 17. Versioning / 17.2 Specification Versions | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| MCC-CP-001-17-VERSIONING-D05 | MCC-CP-001 | 17. Versioning / 17.2 Specification Versions | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| MCC-CP-001-17-VERSIONING-D06 | MCC-CP-001 | 17. Versioning / 17.3 Version Compatibility | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| MCC-CP-001-17-VERSIONING-D07 | MCC-CP-001 | 17. Versioning / 17.3 Version Compatibility | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| MCC-CP-001-17-VERSIONING-D08 | MCC-CP-001 | 17. Versioning / 17.3 Version Compatibility | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| MCC-CP-001-17-VERSIONING-D09 | MCC-CP-001 | 17. Versioning / 17.4 Certification Revalidation | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| MCC-CP-001-17-VERSIONING-D10 | MCC-CP-001 | 17. Versioning / 17.4 Certification Revalidation | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| MCC-CP-001-18-SECURITY-CONSIDERATIONS-D01 | MCC-CP-001 | 18. Security Considerations / 18.1 Purpose | PARTIAL | src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json | tests/test_compliance_suite.py |
| MCC-CP-001-18-SECURITY-CONSIDERATIONS-D02 | MCC-CP-001 | 18. Security Considerations / 18.1 Purpose | PARTIAL | src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json | tests/test_compliance_suite.py |
| MCC-CP-001-18-SECURITY-CONSIDERATIONS-D03 | MCC-CP-001 | 18. Security Considerations / 18.2 Security Objectives | PARTIAL | src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json | tests/test_compliance_suite.py |
| MCC-CP-001-18-SECURITY-CONSIDERATIONS-D04 | MCC-CP-001 | 18. Security Considerations / 18.2 Security Objectives | PARTIAL | src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json | tests/test_compliance_suite.py |
| MCC-CP-001-18-SECURITY-CONSIDERATIONS-D05 | MCC-CP-001 | 18. Security Considerations / 18.3 Threat Model | PARTIAL | src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json | tests/test_compliance_suite.py |
| MCC-CP-001-18-SECURITY-CONSIDERATIONS-D06 | MCC-CP-001 | 18. Security Considerations / 18.3 Threat Model | PARTIAL | src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json | tests/test_compliance_suite.py |
| MCC-CP-001-18-SECURITY-CONSIDERATIONS-D07 | MCC-CP-001 | 18. Security Considerations / 18.3 Threat Model | PARTIAL | src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json | tests/test_compliance_suite.py |
| MCC-CP-001-18-SECURITY-CONSIDERATIONS-D08 | MCC-CP-001 | 18. Security Considerations / 18.3 Threat Model | PARTIAL | src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json | tests/test_compliance_suite.py |
| MCC-CP-001-19-REGISTRY-CONSIDERATIONS-D01 | MCC-CP-001 | 19. Registry Considerations / 19.1 Purpose | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| MCC-CP-001-19-REGISTRY-CONSIDERATIONS-D02 | MCC-CP-001 | 19. Registry Considerations / 19.2 Registry Scope | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| MCC-CP-001-19-REGISTRY-CONSIDERATIONS-D03 | MCC-CP-001 | 19. Registry Considerations / 19.3 Registry Requirements | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| MCC-CP-001-19-REGISTRY-CONSIDERATIONS-D04 | MCC-CP-001 | 19. Registry Considerations / 19.3 Registry Requirements | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| MCC-CP-001-19-REGISTRY-CONSIDERATIONS-D05 | MCC-CP-001 | 19. Registry Considerations / 19.3 Registry Requirements | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| MCC-CP-001-19-REGISTRY-CONSIDERATIONS-D06 | MCC-CP-001 | 19. Registry Considerations / 19.3 Registry Requirements | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| MCC-CP-001-2-GOALS-D01 | MCC-CP-001 | 2. Goals / G1. Framework Neutrality | GAP | — | — |
| MCC-CP-001-2-GOALS-D02 | MCC-CP-001 | 2. Goals / G1. Framework Neutrality | GAP | — | — |
| MCC-CP-001-2-GOALS-D03 | MCC-CP-001 | 2. Goals / G2. Reproducibility | GAP | — | — |
| MCC-CP-001-2-GOALS-D04 | MCC-CP-001 | 2. Goals / G3. Independent Verification | GAP | — | — |
| MCC-CP-001-2-GOALS-D05 | MCC-CP-001 | 2. Goals / G4. Conformance | GAP | — | — |
| MCC-CP-001-2-GOALS-D06 | MCC-CP-001 | 2. Goals / G4. Conformance | GAP | — | — |
| MCC-CP-001-20-CONFORMANCE-STATEMENT-D01 | MCC-CP-001 | 20. Conformance Statement / 20.1 Purpose | GAP | — | — |
| MCC-CP-001-20-CONFORMANCE-STATEMENT-D02 | MCC-CP-001 | 20. Conformance Statement / 20.2 Conformance Claims | GAP | — | — |
| MCC-CP-001-20-CONFORMANCE-STATEMENT-D03 | MCC-CP-001 | 20. Conformance Statement / 20.2 Conformance Claims | GAP | — | — |
| MCC-CP-001-20-CONFORMANCE-STATEMENT-D04 | MCC-CP-001 | 20. Conformance Statement / 20.2 Conformance Claims | GAP | — | — |
| MCC-CP-001-21-REFERENCES-D01 | MCC-CP-001 | 21. References / 21.2 Normative References | NOT_APPLICABLE | — | — |
| MCC-CP-001-21-REFERENCES-D02 | MCC-CP-001 | 21. References / 21.3 Informative References | NOT_APPLICABLE | — | — |
| MCC-CP-001-3-NON-GOALS-D01 | MCC-CP-001 | 3. Non-Goals | GAP | — | — |
| MCC-CP-001-5-NORMATIVE-LANGUAGE-D01 | MCC-CP-001 | 5. Normative Language | NOT_APPLICABLE | — | — |
| MCC-CP-001-6-ARCHITECTURAL-PRINCIPLES-D01 | MCC-CP-001 | 6. Architectural Principles | GAP | — | — |
| MCC-CP-001-6-ARCHITECTURAL-PRINCIPLES-D02 | MCC-CP-001 | 6. Architectural Principles | GAP | — | — |
| MCC-CP-001-6-ARCHITECTURAL-PRINCIPLES-D03 | MCC-CP-001 | 6. Architectural Principles | GAP | — | — |
| MCC-CP-001-7-CERTIFICATION-MODEL-D01 | MCC-CP-001 | 7. Certification Model | PARTIAL | src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json | tests/test_compliance_suite.py |
| MCC-CP-001-7-CERTIFICATION-MODEL-D02 | MCC-CP-001 | 7. Certification Model | PARTIAL | src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json | tests/test_compliance_suite.py |
| MCC-CP-001-7-CERTIFICATION-MODEL-D03 | MCC-CP-001 | 7. Certification Model | PARTIAL | src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json | tests/test_compliance_suite.py |
| MCC-CP-001-7-CERTIFICATION-MODEL-D04 | MCC-CP-001 | 7. Certification Model | PARTIAL | src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json | tests/test_compliance_suite.py |
| MCC-CP-001-7-CERTIFICATION-MODEL-D05 | MCC-CP-001 | 7. Certification Model | PARTIAL | src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json | tests/test_compliance_suite.py |
| MCC-CP-001-7-CERTIFICATION-MODEL-D06 | MCC-CP-001 | 7. Certification Model / 7.1 Certification Authority | PARTIAL | src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json | tests/test_compliance_suite.py |
| MCC-CP-001-7-CERTIFICATION-MODEL-D07 | MCC-CP-001 | 7. Certification Model / 7.2 Certification Subject | PARTIAL | src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json | tests/test_compliance_suite.py |
| MCC-CP-001-7-CERTIFICATION-MODEL-D08 | MCC-CP-001 | 7. Certification Model / 7.3 Certification Inputs | PARTIAL | src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json | tests/test_compliance_suite.py |
| MCC-CP-001-7-CERTIFICATION-MODEL-D09 | MCC-CP-001 | 7. Certification Model / 7.3 Certification Inputs | PARTIAL | src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json | tests/test_compliance_suite.py |
| MCC-CP-001-7-CERTIFICATION-MODEL-D10 | MCC-CP-001 | 7. Certification Model / 7.4 Certification Outputs | PARTIAL | src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json | tests/test_compliance_suite.py |
| MCC-CP-001-7-CERTIFICATION-MODEL-D11 | MCC-CP-001 | 7. Certification Model / 7.4 Certification Outputs | PARTIAL | src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json | tests/test_compliance_suite.py |
| MCC-CP-001-7-CERTIFICATION-MODEL-D12 | MCC-CP-001 | 7. Certification Model / 7.5 Certification Invariants | PARTIAL | src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json | tests/test_compliance_suite.py |
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
| MCC-CP-001-9-CERTIFICATION-PIPELINE-D01 | MCC-CP-001 | 9. Certification Pipeline | PARTIAL | src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json | tests/test_compliance_suite.py |
| MCC-CP-001-9-CERTIFICATION-PIPELINE-D02 | MCC-CP-001 | 9. Certification Pipeline | PARTIAL | src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json | tests/test_compliance_suite.py |
| MCC-CP-001-9-CERTIFICATION-PIPELINE-D03 | MCC-CP-001 | 9. Certification Pipeline / 9.2 Stage 2 — Environment Validation | PARTIAL | src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json | tests/test_compliance_suite.py |
| MCC-CP-001-9-CERTIFICATION-PIPELINE-D04 | MCC-CP-001 | 9. Certification Pipeline / 9.8 Stage 8 — Publication | PARTIAL | src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json | tests/test_compliance_suite.py |
| MCC-CP-001-9-CERTIFICATION-PIPELINE-D05 | MCC-CP-001 | 9. Certification Pipeline / 9.9 Pipeline Invariants | PARTIAL | src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json | tests/test_compliance_suite.py |
| MCC-CP-001-ABSTRACT-D01 | MCC-CP-001 | Abstract | NOT_APPLICABLE | — | — |
| MCC-CP-001-APPENDIX-A-CERTIFICATION-STATE-MACHINE-D01 | MCC-CP-001 | Appendix A — Certification State Machine / A.2 States | GAP | — | — |
| MCC-CP-001-APPENDIX-A-CERTIFICATION-STATE-MACHINE-D02 | MCC-CP-001 | Appendix A — Certification State Machine / A.3 State Transitions | GAP | — | — |
| MCC-CP-001-APPENDIX-A-CERTIFICATION-STATE-MACHINE-D03 | MCC-CP-001 | Appendix A — Certification State Machine / A.3 State Transitions | GAP | — | — |
| MCC-CP-001-APPENDIX-A-CERTIFICATION-STATE-MACHINE-D04 | MCC-CP-001 | Appendix A — Certification State Machine / A.3 State Transitions | GAP | — | — |
| MCC-CP-001-APPENDIX-A-CERTIFICATION-STATE-MACHINE-D05 | MCC-CP-001 | Appendix A — Certification State Machine / A.3 State Transitions | GAP | — | — |
| MCC-CP-001-APPENDIX-B-CERTIFICATION-DECISION-MATRIX-D01 | MCC-CP-001 | Appendix B — Certification Decision Matrix / B.1 Overview | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| MCC-CP-001-APPENDIX-B-CERTIFICATION-DECISION-MATRIX-D02 | MCC-CP-001 | Appendix B — Certification Decision Matrix / B.2 Decision Outcomes | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| MCC-CP-001-APPENDIX-B-CERTIFICATION-DECISION-MATRIX-D03 | MCC-CP-001 | Appendix B — Certification Decision Matrix / B.2 Decision Outcomes | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| MCC-CP-001-APPENDIX-B-CERTIFICATION-DECISION-MATRIX-D04 | MCC-CP-001 | Appendix B — Certification Decision Matrix / B.3 Decision Rules | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| MCC-CP-001-APPENDIX-B-CERTIFICATION-DECISION-MATRIX-D05 | MCC-CP-001 | Appendix B — Certification Decision Matrix / B.3 Decision Rules | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| MCC-CP-001-APPENDIX-B-CERTIFICATION-DECISION-MATRIX-D06 | MCC-CP-001 | Appendix B — Certification Decision Matrix / B.3 Decision Rules | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| MCC-CP-001-APPENDIX-C-REQUIREMENT-IDENTIFIER-REGIST-D01 | MCC-CP-001 | Appendix C — Requirement Identifier Registry / C.1 Purpose | NOT_APPLICABLE | — | — |
| MCC-CP-001-APPENDIX-C-REQUIREMENT-IDENTIFIER-REGIST-D02 | MCC-CP-001 | Appendix C — Requirement Identifier Registry / C.2 Identifier Structure | NOT_APPLICABLE | — | — |
| MCC-CP-001-APPENDIX-C-REQUIREMENT-IDENTIFIER-REGIST-D03 | MCC-CP-001 | Appendix C — Requirement Identifier Registry / C.3 Registry Requirements | NOT_APPLICABLE | — | — |
| MCC-CP-001-APPENDIX-C-REQUIREMENT-IDENTIFIER-REGIST-D04 | MCC-CP-001 | Appendix C — Requirement Identifier Registry / C.3 Registry Requirements | NOT_APPLICABLE | — | — |
| MCC-CP-001-APPENDIX-D-REVISION-HISTORY-D01 | MCC-CP-001 | Appendix D — Revision History / D.1 Purpose | NOT_APPLICABLE | — | — |
| MCC-CP-001-APPENDIX-D-REVISION-HISTORY-D02 | MCC-CP-001 | Appendix D — Revision History / D.3 Future Revisions | NOT_APPLICABLE | — | — |
| MCC-CP-001-APPENDIX-D-REVISION-HISTORY-D03 | MCC-CP-001 | Appendix D — Revision History / D.3 Future Revisions | NOT_APPLICABLE | — | — |
| MCC-CP-001-APPENDIX-D-REVISION-HISTORY-D04 | MCC-CP-001 | Appendix D — Revision History / D.3 Future Revisions | NOT_APPLICABLE | — | — |
| MCC-CP-001-APPENDIX-E-EXAMPLE-CERTIFICATION-FLOW-D01 | MCC-CP-001 | Appendix E — Example Certification Flow / E.1 Purpose | NOT_APPLICABLE | — | — |
| MCC-CP-001-APPENDIX-F-FUTURE-EXTENSIONS-D01 | MCC-CP-001 | Appendix F — Future Extensions / F.1 Purpose | NOT_APPLICABLE | — | — |
| MCC-CP-001-APPENDIX-F-FUTURE-EXTENSIONS-D02 | MCC-CP-001 | Appendix F — Future Extensions / F.2 Potential Extensions | NOT_APPLICABLE | — | — |
| MCC-CP-001-APPENDIX-G-CONFORMANCE-RESULT-REQUIREMEN-D01 | MCC-CP-001 | Appendix G — Conformance Result Requirements / G.2 Conformance Result Content | PARTIAL | src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json | tests/test_compliance_suite.py |
| MCC-CP-001-APPENDIX-G-CONFORMANCE-RESULT-REQUIREMEN-D02 | MCC-CP-001 | Appendix G — Conformance Result Requirements / G.3 Relationship to the Certification Manifest | PARTIAL | src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json | tests/test_compliance_suite.py |
| MCC-CP-001-APPENDIX-G-CONFORMANCE-RESULT-REQUIREMEN-D03 | MCC-CP-001 | Appendix G — Conformance Result Requirements / G.3 Relationship to the Certification Manifest | PARTIAL | src/mcc_compliance/runner.py; src/mcc_compliance/registry.py; src/mcc_compliance/vectors/v1/manifest.json | tests/test_compliance_suite.py |
| MCC-CP-001-APPENDIX-H-CERTIFICATION-REPORT-REQUIREM-D01 | MCC-CP-001 | Appendix H — Certification Report Requirements / H.2 Certification Report Content | PARTIAL | src/mcc_compliance/reporting.py | tests/test_compliance_suite.py; tests/test_sdk_certification.py |
| MCC-CP-001-APPENDIX-H-CERTIFICATION-REPORT-REQUIREM-D02 | MCC-CP-001 | Appendix H — Certification Report Requirements / H.3 Certification Report Properties | PARTIAL | src/mcc_compliance/reporting.py | tests/test_compliance_suite.py; tests/test_sdk_certification.py |
| MCC-CP-001-APPENDIX-H-CERTIFICATION-REPORT-REQUIREM-D03 | MCC-CP-001 | Appendix H — Certification Report Requirements / H.5 Certification Report Applicability | PARTIAL | src/mcc_compliance/reporting.py | tests/test_compliance_suite.py; tests/test_sdk_certification.py |
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
| EB-FILE-001 | MCC-EB-001 | 11. Required Files / 11.5 Required Files Invariants | CONFORMANT | src/mcc_evidence/eb001_schema.py; src/mcc_evidence/eb001_export.py; src/mcc_evidence/eb001_verify.py | tests/test_eb001_evidence_bundle.py |
| EB-FILE-002 | MCC-EB-001 | 11. Required Files / 11.5 Required Files Invariants | CONFORMANT | src/mcc_evidence/eb001_schema.py; src/mcc_evidence/eb001_export.py; src/mcc_evidence/eb001_verify.py | tests/test_eb001_evidence_bundle.py |
| EB-FILE-003 | MCC-EB-001 | 11. Required Files / 11.5 Required Files Invariants | CONFORMANT | src/mcc_evidence/eb001_schema.py; src/mcc_evidence/eb001_export.py; src/mcc_evidence/eb001_verify.py | tests/test_eb001_evidence_bundle.py |
| EB-FILE-004 | MCC-EB-001 | 11. Required Files / 11.5 Required Files Invariants | CONFORMANT | src/mcc_evidence/eb001_schema.py; src/mcc_evidence/eb001_export.py; src/mcc_evidence/eb001_verify.py | tests/test_eb001_evidence_bundle.py |
| EB-FILE-005 | MCC-EB-001 | 11. Required Files / 11.5 Required Files Invariants | CONFORMANT | src/mcc_evidence/eb001_schema.py; src/mcc_evidence/eb001_export.py; src/mcc_evidence/eb001_verify.py | tests/test_eb001_evidence_bundle.py |
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
| EB-STR-001 | MCC-EB-001 | 10. Bundle Directory Structure / 10.5 Structure Invariants | CONFORMANT | src/mcc_evidence/eb001_schema.py; src/mcc_evidence/eb001_export.py; src/mcc_evidence/eb001_verify.py | tests/test_eb001_evidence_bundle.py |
| EB-STR-002 | MCC-EB-001 | 10. Bundle Directory Structure / 10.5 Structure Invariants | CONFORMANT | src/mcc_evidence/eb001_schema.py; src/mcc_evidence/eb001_export.py; src/mcc_evidence/eb001_verify.py | tests/test_eb001_evidence_bundle.py |
| EB-STR-003 | MCC-EB-001 | 10. Bundle Directory Structure / 10.5 Structure Invariants | CONFORMANT | src/mcc_evidence/eb001_schema.py; src/mcc_evidence/eb001_export.py; src/mcc_evidence/eb001_verify.py | tests/test_eb001_evidence_bundle.py |
| EB-STR-004 | MCC-EB-001 | 10. Bundle Directory Structure / 10.5 Structure Invariants | CONFORMANT | src/mcc_evidence/eb001_schema.py; src/mcc_evidence/eb001_export.py; src/mcc_evidence/eb001_verify.py | tests/test_eb001_evidence_bundle.py |
| EB-STR-005 | MCC-EB-001 | 10. Bundle Directory Structure / 10.5 Structure Invariants | CONFORMANT | src/mcc_evidence/eb001_schema.py; src/mcc_evidence/eb001_export.py; src/mcc_evidence/eb001_verify.py | tests/test_eb001_evidence_bundle.py |
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
| MCC-EB-001-10-BUNDLE-DIRECTORY-STRUCTURE-D01 | MCC-EB-001 | 10. Bundle Directory Structure / 10.1 Bundle Root | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| MCC-EB-001-10-BUNDLE-DIRECTORY-STRUCTURE-D02 | MCC-EB-001 | 10. Bundle Directory Structure / 10.1 Bundle Root | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| MCC-EB-001-10-BUNDLE-DIRECTORY-STRUCTURE-D03 | MCC-EB-001 | 10. Bundle Directory Structure / 10.2 Top-Level Layout | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| MCC-EB-001-10-BUNDLE-DIRECTORY-STRUCTURE-D04 | MCC-EB-001 | 10. Bundle Directory Structure / 10.3 Evidence Directory | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| MCC-EB-001-10-BUNDLE-DIRECTORY-STRUCTURE-D05 | MCC-EB-001 | 10. Bundle Directory Structure / 10.3 Evidence Directory | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| MCC-EB-001-10-BUNDLE-DIRECTORY-STRUCTURE-D06 | MCC-EB-001 | 10. Bundle Directory Structure / 10.3 Evidence Directory | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| MCC-EB-001-10-BUNDLE-DIRECTORY-STRUCTURE-D07 | MCC-EB-001 | 10. Bundle Directory Structure / 10.4 Path Rules | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| MCC-EB-001-10-BUNDLE-DIRECTORY-STRUCTURE-D08 | MCC-EB-001 | 10. Bundle Directory Structure / 10.4 Path Rules | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| MCC-EB-001-10-BUNDLE-DIRECTORY-STRUCTURE-D09 | MCC-EB-001 | 10. Bundle Directory Structure / 10.4 Path Rules | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| MCC-EB-001-11-REQUIRED-FILES-D01 | MCC-EB-001 | 11. Required Files / 11.1 Bundle Descriptor | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| MCC-EB-001-11-REQUIRED-FILES-D02 | MCC-EB-001 | 11. Required Files / 11.1 Bundle Descriptor | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| MCC-EB-001-11-REQUIRED-FILES-D03 | MCC-EB-001 | 11. Required Files / 11.2 Integrity Record | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| MCC-EB-001-11-REQUIRED-FILES-D04 | MCC-EB-001 | 11. Required Files / 11.2 Integrity Record | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| MCC-EB-001-11-REQUIRED-FILES-D05 | MCC-EB-001 | 11. Required Files / 11.2 Integrity Record | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| MCC-EB-001-11-REQUIRED-FILES-D06 | MCC-EB-001 | 11. Required Files / 11.3 Provenance Record | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| MCC-EB-001-11-REQUIRED-FILES-D07 | MCC-EB-001 | 11. Required Files / 11.3 Provenance Record | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| MCC-EB-001-11-REQUIRED-FILES-D08 | MCC-EB-001 | 11. Required Files / 11.4 Evidence Items | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| MCC-EB-001-12-REQUIRED-METADATA-D01 | MCC-EB-001 | 12. Required Metadata / 12.1 Bundle-Level Metadata | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| MCC-EB-001-12-REQUIRED-METADATA-D02 | MCC-EB-001 | 12. Required Metadata / 12.2 Evidence Item Metadata | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| MCC-EB-001-12-REQUIRED-METADATA-D03 | MCC-EB-001 | 12. Required Metadata / 12.3 Metadata Integrity | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| MCC-EB-001-12-REQUIRED-METADATA-D04 | MCC-EB-001 | 12. Required Metadata / 12.3 Metadata Integrity | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| MCC-EB-001-13-HASH-AND-INTEGRITY-MODEL-D01 | MCC-EB-001 | 13. Hash and Integrity Model / 13.2 Canonical Form | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| MCC-EB-001-13-HASH-AND-INTEGRITY-MODEL-D02 | MCC-EB-001 | 13. Hash and Integrity Model / 13.2 Canonical Form | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| MCC-EB-001-13-HASH-AND-INTEGRITY-MODEL-D03 | MCC-EB-001 | 13. Hash and Integrity Model / 13.3 Hash Algorithm | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| MCC-EB-001-13-HASH-AND-INTEGRITY-MODEL-D04 | MCC-EB-001 | 13. Hash and Integrity Model / 13.3 Hash Algorithm | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| MCC-EB-001-13-HASH-AND-INTEGRITY-MODEL-D05 | MCC-EB-001 | 13. Hash and Integrity Model / 13.3 Hash Algorithm | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| MCC-EB-001-13-HASH-AND-INTEGRITY-MODEL-D06 | MCC-EB-001 | 13. Hash and Integrity Model / 13.4 Digest Coverage | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| MCC-EB-001-13-HASH-AND-INTEGRITY-MODEL-D07 | MCC-EB-001 | 13. Hash and Integrity Model / 13.4 Digest Coverage | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| MCC-EB-001-13-HASH-AND-INTEGRITY-MODEL-D08 | MCC-EB-001 | 13. Hash and Integrity Model / 13.5 Integrity Verification | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| MCC-EB-001-13-HASH-AND-INTEGRITY-MODEL-D09 | MCC-EB-001 | 13. Hash and Integrity Model / 13.5 Integrity Verification | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| MCC-EB-001-13-HASH-AND-INTEGRITY-MODEL-D10 | MCC-EB-001 | 13. Hash and Integrity Model / 13.5 Integrity Verification | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| MCC-EB-001-14-PROVENANCE-REQUIREMENTS-D01 | MCC-EB-001 | 14. Provenance Requirements / 14.1 Purpose | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| MCC-EB-001-14-PROVENANCE-REQUIREMENTS-D02 | MCC-EB-001 | 14. Provenance Requirements / 14.2 Required Provenance Fields | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| MCC-EB-001-14-PROVENANCE-REQUIREMENTS-D03 | MCC-EB-001 | 14. Provenance Requirements / 14.3 Chain of Custody | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| MCC-EB-001-14-PROVENANCE-REQUIREMENTS-D04 | MCC-EB-001 | 14. Provenance Requirements / 14.3 Chain of Custody | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| MCC-EB-001-15-REPRODUCIBILITY-REQUIREMENTS-D01 | MCC-EB-001 | 15. Reproducibility Requirements / 15.2 Deterministic Generation | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| MCC-EB-001-15-REPRODUCIBILITY-REQUIREMENTS-D02 | MCC-EB-001 | 15. Reproducibility Requirements / 15.3 Prohibited Non-Determinism | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| MCC-EB-001-15-REPRODUCIBILITY-REQUIREMENTS-D03 | MCC-EB-001 | 15. Reproducibility Requirements / 15.4 Regeneration Equivalence | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| MCC-EB-001-16-VALIDATION-RULES-D01 | MCC-EB-001 | 16. Validation Rules / 16.1 Purpose | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| MCC-EB-001-16-VALIDATION-RULES-D02 | MCC-EB-001 | 16. Validation Rules / 16.2 Structural Validation | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| MCC-EB-001-16-VALIDATION-RULES-D03 | MCC-EB-001 | 16. Validation Rules / 16.2 Structural Validation | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| MCC-EB-001-16-VALIDATION-RULES-D04 | MCC-EB-001 | 16. Validation Rules / 16.3 Metadata Validation | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| MCC-EB-001-16-VALIDATION-RULES-D05 | MCC-EB-001 | 16. Validation Rules / 16.4 Integrity Validation | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| MCC-EB-001-16-VALIDATION-RULES-D06 | MCC-EB-001 | 16. Validation Rules / 16.4 Integrity Validation | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| MCC-EB-001-16-VALIDATION-RULES-D07 | MCC-EB-001 | 16. Validation Rules / 16.5 Provenance Validation | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| MCC-EB-001-16-VALIDATION-RULES-D08 | MCC-EB-001 | 16. Validation Rules / 16.6 Fail-Closed Validation | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| MCC-EB-001-16-VALIDATION-RULES-D09 | MCC-EB-001 | 16. Validation Rules / 16.6 Fail-Closed Validation | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| MCC-EB-001-17-VERSIONING-RULES-D01 | MCC-EB-001 | 17. Versioning Rules / 17.2 Schema Version Declaration | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| MCC-EB-001-17-VERSIONING-RULES-D02 | MCC-EB-001 | 17. Versioning Rules / 17.2 Schema Version Declaration | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| MCC-EB-001-17-VERSIONING-RULES-D03 | MCC-EB-001 | 17. Versioning Rules / 17.3 Schema Version Scope | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| MCC-EB-001-17-VERSIONING-RULES-D04 | MCC-EB-001 | 17. Versioning Rules / 17.4 Version Evolution | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| MCC-EB-001-18-COMPATIBILITY-REQUIREMENTS-D01 | MCC-EB-001 | 18. Compatibility Requirements / 18.3 Forward Compatibility | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| MCC-EB-001-18-COMPATIBILITY-REQUIREMENTS-D02 | MCC-EB-001 | 18. Compatibility Requirements / 18.3 Forward Compatibility | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| MCC-EB-001-18-COMPATIBILITY-REQUIREMENTS-D03 | MCC-EB-001 | 18. Compatibility Requirements / 18.4 Breaking Changes | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| MCC-EB-001-19-SECURITY-CONSIDERATIONS-D01 | MCC-EB-001 | 19. Security Considerations / 19.2 Threat Model | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| MCC-EB-001-19-SECURITY-CONSIDERATIONS-D02 | MCC-EB-001 | 19. Security Considerations / 19.3 Tamper Detection | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| MCC-EB-001-19-SECURITY-CONSIDERATIONS-D03 | MCC-EB-001 | 19. Security Considerations / 19.4 Sensitive Data | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| MCC-EB-001-19-SECURITY-CONSIDERATIONS-D04 | MCC-EB-001 | 19. Security Considerations / 19.4 Sensitive Data | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| MCC-EB-001-2-ABSTRACT-D01 | MCC-EB-001 | 2. Abstract | NOT_APPLICABLE | — | — |
| MCC-EB-001-20-EXTENSION-MODEL-D01 | MCC-EB-001 | 20. Extension Model / 20.2 Extension Points | GAP | — | — |
| MCC-EB-001-20-EXTENSION-MODEL-D02 | MCC-EB-001 | 20. Extension Model / 20.3 Extension Constraints | GAP | — | — |
| MCC-EB-001-20-EXTENSION-MODEL-D03 | MCC-EB-001 | 20. Extension Model / 20.3 Extension Constraints | GAP | — | — |
| MCC-EB-001-20-EXTENSION-MODEL-D04 | MCC-EB-001 | 20. Extension Model / 20.3 Extension Constraints | GAP | — | — |
| MCC-EB-001-22-CONFORMANCE-REQUIREMENTS-D01 | MCC-EB-001 | 22. Conformance Requirements / 22.2 Conforming Bundle Producer | GAP | — | — |
| MCC-EB-001-22-CONFORMANCE-REQUIREMENTS-D02 | MCC-EB-001 | 22. Conformance Requirements / 22.2 Conforming Bundle Producer | GAP | — | — |
| MCC-EB-001-22-CONFORMANCE-REQUIREMENTS-D03 | MCC-EB-001 | 22. Conformance Requirements / 22.3 Conforming Bundle Validator | GAP | — | — |
| MCC-EB-001-22-CONFORMANCE-REQUIREMENTS-D04 | MCC-EB-001 | 22. Conformance Requirements / 22.3 Conforming Bundle Validator | GAP | — | — |
| MCC-EB-001-22-CONFORMANCE-REQUIREMENTS-D05 | MCC-EB-001 | 22. Conformance Requirements / 22.4 Conformance Independence | GAP | — | — |
| MCC-EB-001-23-REQUIREMENT-IDENTIFIER-REGISTRY-D01 | MCC-EB-001 | 23. Requirement Identifier Registry / 23.2 Namespace Convention | NOT_APPLICABLE | — | — |
| MCC-EB-001-23-REQUIREMENT-IDENTIFIER-REGISTRY-D02 | MCC-EB-001 | 23. Requirement Identifier Registry / 23.4 Registry Requirements | NOT_APPLICABLE | — | — |
| MCC-EB-001-23-REQUIREMENT-IDENTIFIER-REGISTRY-D03 | MCC-EB-001 | 23. Requirement Identifier Registry / 23.4 Registry Requirements | NOT_APPLICABLE | — | — |
| MCC-EB-001-23-REQUIREMENT-IDENTIFIER-REGISTRY-D04 | MCC-EB-001 | 23. Requirement Identifier Registry / 23.4 Registry Requirements | NOT_APPLICABLE | — | — |
| MCC-EB-001-5-GOALS-D01 | MCC-EB-001 | 5. Goals / EB-G1. Framework Neutrality | GAP | — | — |
| MCC-EB-001-5-GOALS-D02 | MCC-EB-001 | 5. Goals / EB-G2. Reproducibility | GAP | — | — |
| MCC-EB-001-5-GOALS-D03 | MCC-EB-001 | 5. Goals / EB-G3. Independent Verifiability | GAP | — | — |
| MCC-EB-001-5-GOALS-D04 | MCC-EB-001 | 5. Goals / EB-G4. Structural Determinism | GAP | — | — |
| MCC-EB-001-6-NON-GOALS-D01 | MCC-EB-001 | 6. Non-Goals | GAP | — | — |
| MCC-EB-001-9-EVIDENCE-BUNDLE-OVERVIEW-D01 | MCC-EB-001 | 9. Evidence Bundle Overview / 9.1 Role in Certification | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| MCC-EB-001-9-EVIDENCE-BUNDLE-OVERVIEW-D02 | MCC-EB-001 | 9. Evidence Bundle Overview / 9.2 Bundle Forms | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| MCC-EB-001-9-EVIDENCE-BUNDLE-OVERVIEW-D03 | MCC-EB-001 | 9. Evidence Bundle Overview / 9.2 Bundle Forms | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| MCC-EB-001-9-EVIDENCE-BUNDLE-OVERVIEW-D04 | MCC-EB-001 | 9. Evidence Bundle Overview / 9.3 Relationship to Certification Requirements | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| MCC-TC-001-1-PURPOSE-D01 | MCC-TC-001 | 1. Purpose | GAP | — | — |
| MCC-TC-001-1-PURPOSE-D02 | MCC-TC-001 | 1. Purpose | GAP | — | — |
| MCC-TC-001-1-PURPOSE-D03 | MCC-TC-001 | 1. Purpose | GAP | — | — |
| MCC-TC-001-1-PURPOSE-D04 | MCC-TC-001 | 1. Purpose | GAP | — | — |
| MCC-TC-001-10-ISSUER-INFORMATION-D01 | MCC-TC-001 | 10. Issuer Information / 10.2 Issuer Fields | PARTIAL | gateway/trust.py | tests/test_trust.py |
| MCC-TC-001-10-ISSUER-INFORMATION-D02 | MCC-TC-001 | 10. Issuer Information / 10.3 Issuer Authority | PARTIAL | gateway/trust.py | tests/test_trust.py |
| MCC-TC-001-11-VALIDITY-PERIOD-D01 | MCC-TC-001 | 11. Validity Period / 11.2 Issuance Timestamp | PARTIAL | gateway/trust.py | tests/test_trust.py |
| MCC-TC-001-11-VALIDITY-PERIOD-D02 | MCC-TC-001 | 11. Validity Period / 11.3 Expiration | PARTIAL | gateway/trust.py | tests/test_trust.py |
| MCC-TC-001-11-VALIDITY-PERIOD-D03 | MCC-TC-001 | 11. Validity Period / 11.3 Expiration | PARTIAL | gateway/trust.py | tests/test_trust.py |
| MCC-TC-001-12-REVOCATION-MODEL-D01 | MCC-TC-001 | 12. Revocation Model / 12.2 Immutability and Revocation | PARTIAL | gateway/trust.py | tests/test_trust.py |
| MCC-TC-001-12-REVOCATION-MODEL-D02 | MCC-TC-001 | 12. Revocation Model / 12.2 Immutability and Revocation | PARTIAL | gateway/trust.py | tests/test_trust.py |
| MCC-TC-001-12-REVOCATION-MODEL-D03 | MCC-TC-001 | 12. Revocation Model / 12.2 Immutability and Revocation | PARTIAL | gateway/trust.py | tests/test_trust.py |
| MCC-TC-001-12-REVOCATION-MODEL-D04 | MCC-TC-001 | 12. Revocation Model / 12.3 Revocation Record | PARTIAL | gateway/trust.py | tests/test_trust.py |
| MCC-TC-001-12-REVOCATION-MODEL-D05 | MCC-TC-001 | 12. Revocation Model / 12.4 Revocation Authority | PARTIAL | gateway/trust.py | tests/test_trust.py |
| MCC-TC-001-12-REVOCATION-MODEL-D06 | MCC-TC-001 | 12. Revocation Model / 12.5 Revocation Effect | PARTIAL | gateway/trust.py | tests/test_trust.py |
| MCC-TC-001-12-REVOCATION-MODEL-D07 | MCC-TC-001 | 12. Revocation Model / 12.5 Revocation Effect | PARTIAL | gateway/trust.py | tests/test_trust.py |
| MCC-TC-001-12-REVOCATION-MODEL-D08 | MCC-TC-001 | 12. Revocation Model / 12.6 Revocation Check Requirement | PARTIAL | gateway/trust.py | tests/test_trust.py |
| MCC-TC-001-13-CRYPTOGRAPHIC-INTEGRITY-D01 | MCC-TC-001 | 13. Cryptographic Integrity / 13.2 Digest Requirements | PARTIAL | src/mcc_core/signing.py | tests/test_mcc_core.py::test_sign_and_verify_roundtrip; tests/test_mcc_core.py::test_canonical_serialization_is_deterministic |
| MCC-TC-001-14-SIGNATURE-REQUIREMENTS-D01 | MCC-TC-001 | 14. Signature Requirements / 14.2 Signature Algorithm | PARTIAL | src/mcc_core/signing.py | tests/test_mcc_core.py::test_sign_and_verify_roundtrip; tests/test_mcc_core.py::test_canonical_serialization_is_deterministic |
| MCC-TC-001-14-SIGNATURE-REQUIREMENTS-D02 | MCC-TC-001 | 14. Signature Requirements / 14.2 Signature Algorithm | PARTIAL | src/mcc_core/signing.py | tests/test_mcc_core.py::test_sign_and_verify_roundtrip; tests/test_mcc_core.py::test_canonical_serialization_is_deterministic |
| MCC-TC-001-14-SIGNATURE-REQUIREMENTS-D03 | MCC-TC-001 | 14. Signature Requirements / 14.3 Signature Coverage | PARTIAL | src/mcc_core/signing.py | tests/test_mcc_core.py::test_sign_and_verify_roundtrip; tests/test_mcc_core.py::test_canonical_serialization_is_deterministic |
| MCC-TC-001-14-SIGNATURE-REQUIREMENTS-D04 | MCC-TC-001 | 14. Signature Requirements / 14.3 Signature Coverage | PARTIAL | src/mcc_core/signing.py | tests/test_mcc_core.py::test_sign_and_verify_roundtrip; tests/test_mcc_core.py::test_canonical_serialization_is_deterministic |
| MCC-TC-001-14-SIGNATURE-REQUIREMENTS-D05 | MCC-TC-001 | 14. Signature Requirements / 14.4 Signature Declaration | PARTIAL | src/mcc_core/signing.py | tests/test_mcc_core.py::test_sign_and_verify_roundtrip; tests/test_mcc_core.py::test_canonical_serialization_is_deterministic |
| MCC-TC-001-15-VERIFICATION-PROCEDURE-D01 | MCC-TC-001 | 15. Verification Procedure / 15.1 Purpose | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| MCC-TC-001-15-VERIFICATION-PROCEDURE-D02 | MCC-TC-001 | 15. Verification Procedure / 15.2 Structural Verification | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| MCC-TC-001-15-VERIFICATION-PROCEDURE-D03 | MCC-TC-001 | 15. Verification Procedure / 15.2 Structural Verification | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| MCC-TC-001-15-VERIFICATION-PROCEDURE-D04 | MCC-TC-001 | 15. Verification Procedure / 15.3 Signature Verification | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| MCC-TC-001-15-VERIFICATION-PROCEDURE-D05 | MCC-TC-001 | 15. Verification Procedure / 15.3 Signature Verification | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| MCC-TC-001-15-VERIFICATION-PROCEDURE-D06 | MCC-TC-001 | 15. Verification Procedure / 15.4 Manifest Reference Verification | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| MCC-TC-001-15-VERIFICATION-PROCEDURE-D07 | MCC-TC-001 | 15. Verification Procedure / 15.4 Manifest Reference Verification | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| MCC-TC-001-15-VERIFICATION-PROCEDURE-D08 | MCC-TC-001 | 15. Verification Procedure / 15.5 Evidence Bundle Reference Consistency Verification | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| MCC-TC-001-15-VERIFICATION-PROCEDURE-D09 | MCC-TC-001 | 15. Verification Procedure / 15.5 Evidence Bundle Reference Consistency Verification | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| MCC-TC-001-15-VERIFICATION-PROCEDURE-D10 | MCC-TC-001 | 15. Verification Procedure / 15.5 Evidence Bundle Reference Consistency Verification | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| MCC-TC-001-15-VERIFICATION-PROCEDURE-D11 | MCC-TC-001 | 15. Verification Procedure / 15.5 Evidence Bundle Reference Consistency Verification | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| MCC-TC-001-15-VERIFICATION-PROCEDURE-D12 | MCC-TC-001 | 15. Verification Procedure / 15.6 Subject and Result Consistency Verification | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| MCC-TC-001-15-VERIFICATION-PROCEDURE-D13 | MCC-TC-001 | 15. Verification Procedure / 15.7 Validity and Revocation Verification | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| MCC-TC-001-15-VERIFICATION-PROCEDURE-D14 | MCC-TC-001 | 15. Verification Procedure / 15.7 Validity and Revocation Verification | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| MCC-TC-001-15-VERIFICATION-PROCEDURE-D15 | MCC-TC-001 | 15. Verification Procedure / 15.8 Fail-Closed Verification | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| MCC-TC-001-15-VERIFICATION-PROCEDURE-D16 | MCC-TC-001 | 15. Verification Procedure / 15.8 Fail-Closed Verification | PARTIAL | src/mcc_evidence/schema.py; src/mcc_evidence/export.py; src/mcc_evidence/verify.py | tests/test_evidence_bundle.py; tests/test_evidence_tamper.py; tests/test_evidence_security.py |
| MCC-TC-001-16-TRUST-MODEL-D01 | MCC-TC-001 | 16. Trust Model / 16.2 Trust Anchors | PARTIAL | gateway/trust.py | tests/test_trust.py |
| MCC-TC-001-16-TRUST-MODEL-D02 | MCC-TC-001 | 16. Trust Model / 16.3 Trust Anchor Recognition | PARTIAL | gateway/trust.py | tests/test_trust.py |
| MCC-TC-001-16-TRUST-MODEL-D03 | MCC-TC-001 | 16. Trust Model / 16.3 Trust Anchor Recognition | PARTIAL | gateway/trust.py | tests/test_trust.py |
| MCC-TC-001-16-TRUST-MODEL-D04 | MCC-TC-001 | 16. Trust Model / 16.4 Trust Anchor Rotation and Revocation | PARTIAL | gateway/trust.py | tests/test_trust.py |
| MCC-TC-001-16-TRUST-MODEL-D05 | MCC-TC-001 | 16. Trust Model / 16.5 Multiple Trust Domains | PARTIAL | gateway/trust.py | tests/test_trust.py |
| MCC-TC-001-17-COMPATIBILITY-D01 | MCC-TC-001 | 17. Compatibility / 17.3 Forward Compatibility | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| MCC-TC-001-17-COMPATIBILITY-D02 | MCC-TC-001 | 17. Compatibility / 17.3 Forward Compatibility | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| MCC-TC-001-17-COMPATIBILITY-D03 | MCC-TC-001 | 17. Compatibility / 17.4 Cross-Specification Compatibility | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| MCC-TC-001-17-COMPATIBILITY-D04 | MCC-TC-001 | 17. Compatibility / 17.4 Cross-Specification Compatibility | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| MCC-TC-001-18-VERSIONING-D01 | MCC-TC-001 | 18. Versioning / 18.2 Schema Version Declaration | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| MCC-TC-001-18-VERSIONING-D02 | MCC-TC-001 | 18. Versioning / 18.2 Schema Version Declaration | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| MCC-TC-001-18-VERSIONING-D03 | MCC-TC-001 | 18. Versioning / 18.3 Schema Version Scope | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| MCC-TC-001-18-VERSIONING-D04 | MCC-TC-001 | 18. Versioning / 18.4 Version Evolution | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| MCC-TC-001-19-SECURITY-CONSIDERATIONS-D01 | MCC-TC-001 | 19. Security Considerations / 19.2 Threat Model | PARTIAL | gateway/trust.py | tests/test_trust.py |
| MCC-TC-001-19-SECURITY-CONSIDERATIONS-D02 | MCC-TC-001 | 19. Security Considerations / 19.3 Forgery and Tamper Resistance | PARTIAL | gateway/trust.py | tests/test_trust.py |
| MCC-TC-001-19-SECURITY-CONSIDERATIONS-D03 | MCC-TC-001 | 19. Security Considerations / 19.4 Sensitive Data | PARTIAL | gateway/trust.py | tests/test_trust.py |
| MCC-TC-001-19-SECURITY-CONSIDERATIONS-D04 | MCC-TC-001 | 19. Security Considerations / 19.4 Sensitive Data | PARTIAL | gateway/trust.py | tests/test_trust.py |
| MCC-TC-001-19-SECURITY-CONSIDERATIONS-D05 | MCC-TC-001 | 19. Security Considerations / 19.5 Runtime Governance Boundary | PARTIAL | gateway/trust.py | tests/test_trust.py |
| MCC-TC-001-19-SECURITY-CONSIDERATIONS-D06 | MCC-TC-001 | 19. Security Considerations / 19.5 Runtime Governance Boundary | PARTIAL | gateway/trust.py | tests/test_trust.py |
| MCC-TC-001-20-EXTENSION-MODEL-D01 | MCC-TC-001 | 20. Extension Model / 20.2 Extension Points | GAP | — | — |
| MCC-TC-001-20-EXTENSION-MODEL-D02 | MCC-TC-001 | 20. Extension Model / 20.3 Extension Constraints | GAP | — | — |
| MCC-TC-001-20-EXTENSION-MODEL-D03 | MCC-TC-001 | 20. Extension Model / 20.3 Extension Constraints | GAP | — | — |
| MCC-TC-001-20-EXTENSION-MODEL-D04 | MCC-TC-001 | 20. Extension Model / 20.3 Extension Constraints | GAP | — | — |
| MCC-TC-001-21-CONFORMANCE-REQUIREMENTS-D01 | MCC-TC-001 | 21. Conformance Requirements / 21.2 Conforming Certificate Issuer | GAP | — | — |
| MCC-TC-001-21-CONFORMANCE-REQUIREMENTS-D02 | MCC-TC-001 | 21. Conformance Requirements / 21.2 Conforming Certificate Issuer | GAP | — | — |
| MCC-TC-001-21-CONFORMANCE-REQUIREMENTS-D03 | MCC-TC-001 | 21. Conformance Requirements / 21.2 Conforming Certificate Issuer | GAP | — | — |
| MCC-TC-001-21-CONFORMANCE-REQUIREMENTS-D04 | MCC-TC-001 | 21. Conformance Requirements / 21.2 Conforming Certificate Issuer | GAP | — | — |
| MCC-TC-001-21-CONFORMANCE-REQUIREMENTS-D05 | MCC-TC-001 | 21. Conformance Requirements / 21.3 Conforming Certificate Verifier | GAP | — | — |
| MCC-TC-001-21-CONFORMANCE-REQUIREMENTS-D06 | MCC-TC-001 | 21. Conformance Requirements / 21.3 Conforming Certificate Verifier | GAP | — | — |
| MCC-TC-001-21-CONFORMANCE-REQUIREMENTS-D07 | MCC-TC-001 | 21. Conformance Requirements / 21.4 Conformance Independence | GAP | — | — |
| MCC-TC-001-22-REQUIREMENT-IDENTIFIER-REGISTRY-D01 | MCC-TC-001 | 22. Requirement Identifier Registry / 22.2 Namespace Convention | NOT_APPLICABLE | — | — |
| MCC-TC-001-22-REQUIREMENT-IDENTIFIER-REGISTRY-D02 | MCC-TC-001 | 22. Requirement Identifier Registry / 22.4 Registry Requirements | NOT_APPLICABLE | — | — |
| MCC-TC-001-22-REQUIREMENT-IDENTIFIER-REGISTRY-D03 | MCC-TC-001 | 22. Requirement Identifier Registry / 22.4 Registry Requirements | NOT_APPLICABLE | — | — |
| MCC-TC-001-22-REQUIREMENT-IDENTIFIER-REGISTRY-D04 | MCC-TC-001 | 22. Requirement Identifier Registry / 22.4 Registry Requirements | NOT_APPLICABLE | — | — |
| MCC-TC-001-3-CERTIFICATE-MODEL-D01 | MCC-TC-001 | 3. Certificate Model / 3.2 Role in Certification | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| MCC-TC-001-3-CERTIFICATE-MODEL-D02 | MCC-TC-001 | 3. Certificate Model / 3.3 Relationship to Other Certification Artifacts | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| MCC-TC-001-3-CERTIFICATE-MODEL-D03 | MCC-TC-001 | 3. Certificate Model / 3.3 Relationship to Other Certification Artifacts | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| MCC-TC-001-3-CERTIFICATE-MODEL-D04 | MCC-TC-001 | 3. Certificate Model / 3.3 Relationship to Other Certification Artifacts | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| MCC-TC-001-3-CERTIFICATE-MODEL-D05 | MCC-TC-001 | 3. Certificate Model / 3.3 Relationship to Other Certification Artifacts | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| MCC-TC-001-4-CERTIFICATE-SCHEMA-D01 | MCC-TC-001 | 4. Certificate Schema / 4.2 Top-Level Structure | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| MCC-TC-001-4-CERTIFICATE-SCHEMA-D02 | MCC-TC-001 | 4. Certificate Schema / 4.3 Field Typing | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| MCC-TC-001-4-CERTIFICATE-SCHEMA-D03 | MCC-TC-001 | 4. Certificate Schema / 4.3 Field Typing | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| MCC-TC-001-4-CERTIFICATE-SCHEMA-D04 | MCC-TC-001 | 4. Certificate Schema / 4.4 Canonical Form | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| MCC-TC-001-4-CERTIFICATE-SCHEMA-D05 | MCC-TC-001 | 4. Certificate Schema / 4.4 Canonical Form | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| MCC-TC-001-5-CERTIFICATE-IDENTITY-D01 | MCC-TC-001 | 5. Certificate Identity / 5.2 Identity Fields | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| MCC-TC-001-5-CERTIFICATE-IDENTITY-D02 | MCC-TC-001 | 5. Certificate Identity / 5.3 Identifier Stability | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| MCC-TC-001-5-CERTIFICATE-IDENTITY-D03 | MCC-TC-001 | 5. Certificate Identity / 5.3 Identifier Stability | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| MCC-TC-001-6-REQUIRED-FIELDS-D01 | MCC-TC-001 | 6. Required Fields / 6.1 Purpose | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| MCC-TC-001-6-REQUIRED-FIELDS-D02 | MCC-TC-001 | 6. Required Fields / 6.2 Baseline Required Fields | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| MCC-TC-001-6-REQUIRED-FIELDS-D03 | MCC-TC-001 | 6. Required Fields / 6.3 Additional Required Fields | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| MCC-TC-001-6-REQUIRED-FIELDS-D04 | MCC-TC-001 | 6. Required Fields / 6.4 Field Presence Rule | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| MCC-TC-001-6-REQUIRED-FIELDS-D05 | MCC-TC-001 | 6. Required Fields / 6.4 Field Presence Rule | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| MCC-TC-001-6-REQUIRED-FIELDS-D06 | MCC-TC-001 | 6. Required Fields / 6.5 Manifest Reference Structure | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| MCC-TC-001-6-REQUIRED-FIELDS-D07 | MCC-TC-001 | 6. Required Fields / 6.6 Evidence Bundle Reference Structure | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| MCC-TC-001-6-REQUIRED-FIELDS-D08 | MCC-TC-001 | 6. Required Fields / 6.6 Evidence Bundle Reference Structure | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| MCC-TC-001-6-REQUIRED-FIELDS-D09 | MCC-TC-001 | 6. Required Fields / 6.6 Evidence Bundle Reference Structure | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| MCC-TC-001-6-REQUIRED-FIELDS-D10 | MCC-TC-001 | 6. Required Fields / 6.6 Evidence Bundle Reference Structure | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| MCC-TC-001-7-OPTIONAL-FIELDS-D01 | MCC-TC-001 | 7. Optional Fields / 7.3 Optional Field Constraints | GAP | — | — |
| MCC-TC-001-7-OPTIONAL-FIELDS-D02 | MCC-TC-001 | 7. Optional Fields / 7.3 Optional Field Constraints | GAP | — | — |
| MCC-TC-001-7-OPTIONAL-FIELDS-D03 | MCC-TC-001 | 7. Optional Fields / 7.3 Optional Field Constraints | GAP | — | — |
| MCC-TC-001-8-SUBJECT-IDENTIFICATION-D01 | MCC-TC-001 | 8. Subject Identification / 8.2 Subject Field | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| MCC-TC-001-8-SUBJECT-IDENTIFICATION-D02 | MCC-TC-001 | 8. Subject Identification / 8.2 Subject Field | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| MCC-TC-001-8-SUBJECT-IDENTIFICATION-D03 | MCC-TC-001 | 8. Subject Identification / 8.3 Subject Consistency | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| MCC-TC-001-8-SUBJECT-IDENTIFICATION-D04 | MCC-TC-001 | 8. Subject Identification / 8.3 Subject Consistency | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| MCC-TC-001-9-CERTIFICATION-RESULT-REPRESENTATION-D01 | MCC-TC-001 | 9. Certification Result Representation / 9.2 Result Value | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| MCC-TC-001-9-CERTIFICATION-RESULT-REPRESENTATION-D02 | MCC-TC-001 | 9. Certification Result Representation / 9.2 Result Value | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| MCC-TC-001-9-CERTIFICATION-RESULT-REPRESENTATION-D03 | MCC-TC-001 | 9. Certification Result Representation / 9.3 Result Consistency | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| MCC-TC-001-9-CERTIFICATION-RESULT-REPRESENTATION-D04 | MCC-TC-001 | 9. Certification Result Representation / 9.3 Result Consistency | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| MCC-TC-001-9-CERTIFICATION-RESULT-REPRESENTATION-D05 | MCC-TC-001 | 9. Certification Result Representation / 9.4 Certified Capability Profiles | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
| MCC-TC-001-9-CERTIFICATION-RESULT-REPRESENTATION-D06 | MCC-TC-001 | 9. Certification Result Representation / 9.4 Certified Capability Profiles | PARTIAL | src/mcc_compliance/program.py; certifications/manifest.json | tests/test_certified_adapter_program.py |
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

- Assessment was performed at requirement-category granularity, not as an independently bespoke code review of all 810 individual requirements. Requirements sharing a specification section and normative theme share a status and rationale unless repository evidence specifically distinguished them. This is disclosed, not hidden.
- No requirement is marked CONFORMANT in this baseline. That status requires both an implementation and a meaningful automated test tied to the specific requirement; as of the reviewed commit, no code in this repository implements the Evidence Bundle, Certification Manifest, Technical Certificate, or Certification Program process these specifications define.
- PARTIAL status is granted only for two narrow, independently verifiable primitives (deterministic canonical serialization / digest, and Ed25519-only / asymmetric-only signing) that exist and are tested for a different artifact (the runtime Decision Token) and are not wired to any Evidence Bundle, Manifest, or Certificate object.
- This assessment does not execute or validate any generated Evidence Bundle, Manifest, or Certificate, because none exist to generate. It is a static, source-level trace only.

## Reproduction

```
python -m mcc_conformance generate
python -m mcc_conformance validate
pytest tests/test_conformance_baseline.py -v
```

