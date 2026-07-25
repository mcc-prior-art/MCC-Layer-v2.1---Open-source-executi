# MCC Normative v1.0 — Extraction Coverage Audit

Auto-generated. Do not hand-edit — regenerate with:

```
python -m mcc_conformance generate
```

Reconciles every normative-looking (MUST/MUST NOT/SHALL/SHALL NOT/REQUIRED) source line previously silently dropped by the extractor because its H1 section already contained a canonical requirement ID elsewhere, against its disposition under the corrected extractor (`src/mcc_conformance/extract.py`). See `conformance/normative-v1.0/remediation/``wave-1-execution-boundary-scope-manifest.md` (Finding 1) for how this defect was discovered, and `conformance/normative-v1.0/README.md` for the resulting coverage semantics.

## Disposition totals

| Disposition | Count |
|---|---|
| EXTRACTED | 382 |
| DUPLICATE_OF_CANONICAL | 8 |
| DUPLICATE_WITHIN_DERIVED | 0 |
| **Total** | **390** |

## Totals by specification

| Specification | Entries |
|---|---|
| MCC-CP-001 | 153 |
| MCC-EB-001 | 72 |
| MCC-CM-001 | 59 |
| MCC-TC-001 | 106 |

## Full audit trail

| Spec | Line | Disposition | Requirement ID | Duplicate of | Normalized text |
|---|---|---|---|---|---|
| MCC-CP-001 | 184 | EXTRACTED | MCC-CP-001-7-CERTIFICATION-MODEL-D01 | — | All certifications SHALL be performed according to this model. |
| MCC-CP-001 | 190 | EXTRACTED | MCC-CP-001-7-CERTIFICATION-MODEL-D02 | — | Certification SHALL always evaluate normative requirements. |
| MCC-CP-001 | 192 | EXTRACTED | MCC-CP-001-7-CERTIFICATION-MODEL-D03 | — | Certification SHALL NOT evaluate implementation popularity, project ownership, programm... |
| MCC-CP-001 | 194 | EXTRACTED | MCC-CP-001-7-CERTIFICATION-MODEL-D04 | — | Every successful certification SHALL produce reproducible certification artifacts. |
| MCC-CP-001 | 196 | EXTRACTED | MCC-CP-001-7-CERTIFICATION-MODEL-D05 | — | Those artifacts SHALL be sufficient for independent verification. |
| MCC-CP-001 | 213 | EXTRACTED | MCC-CP-001-7-CERTIFICATION-MODEL-D06 | — | Implementations SHALL NOT redefine certification requirements. |
| MCC-CP-001 | 230 | EXTRACTED | MCC-CP-001-7-CERTIFICATION-MODEL-D07 | — | Certification SHALL evaluate behavior rather than implementation origin. |
| MCC-CP-001 | 236 | EXTRACTED | MCC-CP-001-7-CERTIFICATION-MODEL-D08 | — | Certification SHALL consume one or more of the following inputs: - implementation under... |
| MCC-CP-001 | 245 | EXTRACTED | MCC-CP-001-7-CERTIFICATION-MODEL-D09 | — | Certification inputs SHALL be versioned. |
| MCC-CP-001 | 251 | EXTRACTED | MCC-CP-001-7-CERTIFICATION-MODEL-D10 | — | Every successful certification SHALL produce: - Evidence Bundle; - Certification Manife... |
| MCC-CP-001 | 259 | EXTRACTED | MCC-CP-001-7-CERTIFICATION-MODEL-D11 | — | These outputs SHALL be reproducible. |
| MCC-CP-001 | 265 | EXTRACTED | MCC-CP-001-7-CERTIFICATION-MODEL-D12 | — | The following invariants SHALL always hold. |
| MCC-CP-001 | 433 | EXTRACTED | MCC-CP-001-9-CERTIFICATION-PIPELINE-D01 | — | Every certification SHALL execute every mandatory stage in the order defined below. |
| MCC-CP-001 | 437 | EXTRACTED | MCC-CP-001-9-CERTIFICATION-PIPELINE-D02 | — | A failed mandatory stage SHALL terminate certification. |
| MCC-CP-001 | 459 | EXTRACTED | MCC-CP-001-9-CERTIFICATION-PIPELINE-D03 | — | Validation SHALL include: - specification version; - required tooling; - capability pro... |
| MCC-CP-001 | 544 | EXTRACTED | MCC-CP-001-9-CERTIFICATION-PIPELINE-D04 | — | Publication SHALL preserve reproducibility. |
| MCC-CP-001 | 550 | EXTRACTED | MCC-CP-001-9-CERTIFICATION-PIPELINE-D05 | — | The Certification Pipeline SHALL satisfy the following invariants. |
| MCC-CP-001 | 662 | EXTRACTED | MCC-CP-001-10-CONFORMANCE-MODEL-D01 | — | Conformance SHALL be evaluated only against normative requirements defined by MCC speci... |
| MCC-CP-001 | 664 | EXTRACTED | MCC-CP-001-10-CONFORMANCE-MODEL-D02 | — | No implementation-specific behavior SHALL influence conformance results. |
| MCC-CP-001 | 670 | EXTRACTED | MCC-CP-001-10-CONFORMANCE-MODEL-D03 | — | Each normative requirement SHALL have a unique identifier. |
| MCC-CP-001 | 672 | EXTRACTED | MCC-CP-001-10-CONFORMANCE-MODEL-D04 | — | Each requirement SHALL define: - identifier; - requirement statement; - applicability; ... |
| MCC-CP-001 | 680 | EXTRACTED | MCC-CP-001-10-CONFORMANCE-MODEL-D05 | — | Requirements SHALL remain stable within a published specification version. |
| MCC-CP-001 | 686 | EXTRACTED | MCC-CP-001-10-CONFORMANCE-MODEL-D06 | — | Normative requirements SHALL be classified as one of: - REQUIRED - OPTIONAL - CONDITIONAL |
| MCC-CP-001 | 692 | EXTRACTED | MCC-CP-001-10-CONFORMANCE-MODEL-D07 | — | REQUIRED requirements SHALL always be evaluated. |
| MCC-CP-001 | 694 | EXTRACTED | MCC-CP-001-10-CONFORMANCE-MODEL-D08 | — | OPTIONAL requirements SHALL NOT affect mandatory certification. |
| MCC-CP-001 | 696 | EXTRACTED | MCC-CP-001-10-CONFORMANCE-MODEL-D09 | — | CONDITIONAL requirements SHALL apply only when their stated conditions are satisfied. |
| MCC-CP-001 | 702 | EXTRACTED | MCC-CP-001-10-CONFORMANCE-MODEL-D10 | — | Each evaluated requirement SHALL produce exactly one outcome: - PASS - FAIL - NOT APPLI... |
| MCC-CP-001 | 714 | EXTRACTED | MCC-CP-001-10-CONFORMANCE-MODEL-D11 | — | Overall conformance SHALL be determined only after all REQUIRED and applicable CONDITIO... |
| MCC-CP-001 | 716 | EXTRACTED | MCC-CP-001-10-CONFORMANCE-MODEL-D12 | — | Certification SHALL NOT be issued if any REQUIRED requirement fails. |
| MCC-CP-001 | 718 | EXTRACTED | MCC-CP-001-10-CONFORMANCE-MODEL-D13 | — | OPTIONAL requirements SHALL NOT prevent certification. |
| MCC-CP-001 | 762 | DUPLICATE_OF_CANONICAL | — | CAP-001 | Capability Profiles SHALL remain framework-neutral. |
| MCC-CP-001 | 768 | EXTRACTED | MCC-CP-001-11-CAPABILITY-PROFILES-D01 | — | Each Capability Profile SHALL have a globally unique identifier. |
| MCC-CP-001 | 770 | EXTRACTED | MCC-CP-001-11-CAPABILITY-PROFILES-D02 | — | Each profile SHALL define: - profile identifier; - profile name; - specification versio... |
| MCC-CP-001 | 778 | EXTRACTED | MCC-CP-001-11-CAPABILITY-PROFILES-D03 | — | Capability Profile identifiers SHALL remain stable within a published specification ver... |
| MCC-CP-001 | 784 | EXTRACTED | MCC-CP-001-11-CAPABILITY-PROFILES-D04 | — | Each capability SHALL define: - capability identifier; - capability description; - norm... |
| MCC-CP-001 | 792 | EXTRACTED | MCC-CP-001-11-CAPABILITY-PROFILES-D05 | — | Capabilities SHALL reference only normative MCC requirements. |
| MCC-CP-001 | 798 | EXTRACTED | MCC-CP-001-11-CAPABILITY-PROFILES-D06 | — | Each declared capability SHALL be evaluated independently. |
| MCC-CP-001 | 800 | EXTRACTED | MCC-CP-001-11-CAPABILITY-PROFILES-D07 | — | Capability evaluation SHALL produce one of the following outcomes: - PASS - FAIL - NOT ... |
| MCC-CP-001 | 806 | EXTRACTED | MCC-CP-001-11-CAPABILITY-PROFILES-D08 | — | Capability evaluation SHALL be reproducible. |
| MCC-CP-001 | 814 | EXTRACTED | MCC-CP-001-11-CAPABILITY-PROFILES-D09 | — | Dependent capabilities SHALL be evaluated before the capability that references them. |
| MCC-CP-001 | 816 | EXTRACTED | MCC-CP-001-11-CAPABILITY-PROFILES-D10 | — | Circular capability dependencies SHALL NOT be permitted. |
| MCC-CP-001 | 824 | EXTRACTED | MCC-CP-001-11-CAPABILITY-PROFILES-D11 | — | Capability claims SHALL be verified during certification. |
| MCC-CP-001 | 826 | EXTRACTED | MCC-CP-001-11-CAPABILITY-PROFILES-D12 | — | Unverified capability claims SHALL NOT appear within Certification Manifests or Technic... |
| MCC-CP-001 | 870 | EXTRACTED | MCC-CP-001-12-CERTIFICATION-REQUIREMENTS-D01 | — | Certification Requirements define the normative requirements that SHALL be evaluated du... |
| MCC-CP-001 | 872 | EXTRACTED | MCC-CP-001-12-CERTIFICATION-REQUIREMENTS-D02 | — | Certification Requirements SHALL be technology-independent and framework-neutral. |
| MCC-CP-001 | 874 | EXTRACTED | MCC-CP-001-12-CERTIFICATION-REQUIREMENTS-D03 | — | Certification SHALL evaluate only published normative requirements. |
| MCC-CP-001 | 880 | EXTRACTED | MCC-CP-001-12-CERTIFICATION-REQUIREMENTS-D04 | — | Each Certification Requirement SHALL define: - requirement identifier; - requirement ti... |
| MCC-CP-001 | 889 | EXTRACTED | MCC-CP-001-12-CERTIFICATION-REQUIREMENTS-D05 | — | Requirement identifiers SHALL be globally unique within a specification version. |
| MCC-CP-001 | 895 | EXTRACTED | MCC-CP-001-12-CERTIFICATION-REQUIREMENTS-D06 | — | Each requirement SHALL specify its applicability. |
| MCC-CP-001 | 904 | EXTRACTED | MCC-CP-001-12-CERTIFICATION-REQUIREMENTS-D07 | — | Requirements SHALL NOT be evaluated outside their stated applicability. |
| MCC-CP-001 | 910 | EXTRACTED | MCC-CP-001-12-CERTIFICATION-REQUIREMENTS-D08 | — | Each requirement SHALL define at least one normative verification method. |
| MCC-CP-001 | 912 | EXTRACTED | MCC-CP-001-12-CERTIFICATION-REQUIREMENTS-D09 | — | Verification methods SHALL produce reproducible results. |
| MCC-CP-001 | 914 | EXTRACTED | MCC-CP-001-12-CERTIFICATION-REQUIREMENTS-D10 | — | Verification SHALL remain implementation-independent. |
| MCC-CP-001 | 920 | EXTRACTED | MCC-CP-001-12-CERTIFICATION-REQUIREMENTS-D11 | — | Every Certification Requirement SHALL be traceable to: - the governing specification; -... |
| MCC-CP-001 | 927 | EXTRACTED | MCC-CP-001-12-CERTIFICATION-REQUIREMENTS-D12 | — | Traceability SHALL be preserved throughout certification. |
| MCC-CP-001 | 969 | EXTRACTED | MCC-CP-001-13-REQUIREMENT-CLASSIFICATION-D01 | — | Classification SHALL determine how requirements participate in certification. |
| MCC-CP-001 | 971 | EXTRACTED | MCC-CP-001-13-REQUIREMENT-CLASSIFICATION-D02 | — | Requirement Classification SHALL remain framework-neutral. |
| MCC-CP-001 | 977 | EXTRACTED | MCC-CP-001-13-REQUIREMENT-CLASSIFICATION-D03 | — | Each Certification Requirement SHALL be classified as exactly one of: - REQUIRED - OPTI... |
| MCC-CP-001 | 983 | EXTRACTED | MCC-CP-001-13-REQUIREMENT-CLASSIFICATION-D04 | — | Multiple classifications for the same requirement SHALL NOT be permitted. |
| MCC-CP-001 | 989 | EXTRACTED | MCC-CP-001-13-REQUIREMENT-CLASSIFICATION-D05 | — | REQUIRED requirements SHALL always be evaluated. |
| MCC-CP-001 | 991 | EXTRACTED | MCC-CP-001-13-REQUIREMENT-CLASSIFICATION-D06 | — | Failure of a REQUIRED requirement SHALL prevent certification. |
| MCC-CP-001 | 999 | EXTRACTED | MCC-CP-001-13-REQUIREMENT-CLASSIFICATION-D07 | — | Failure of OPTIONAL requirements SHALL NOT prevent certification. |
| MCC-CP-001 | 1007 | EXTRACTED | MCC-CP-001-13-REQUIREMENT-CLASSIFICATION-D08 | — | CONDITIONAL requirements SHALL apply only when their stated applicability conditions ar... |
| MCC-CP-001 | 1009 | EXTRACTED | MCC-CP-001-13-REQUIREMENT-CLASSIFICATION-D09 | — | When applicability conditions are not satisfied, the requirement SHALL produce the resu... |
| MCC-CP-001 | 1051 | EXTRACTED | MCC-CP-001-14-EVIDENCE-REQUIREMENTS-D01 | — | Certification evidence SHALL support independent verification of certification results. |
| MCC-CP-001 | 1053 | EXTRACTED | MCC-CP-001-14-EVIDENCE-REQUIREMENTS-D02 | — | Evidence SHALL remain implementation-independent and framework-neutral. |
| MCC-CP-001 | 1067 | EXTRACTED | MCC-CP-001-14-EVIDENCE-REQUIREMENTS-D03 | — | Evidence sources SHALL be explicitly identified. |
| MCC-CP-001 | 1073 | EXTRACTED | MCC-CP-001-14-EVIDENCE-REQUIREMENTS-D04 | — | Certification evidence SHALL be: - reproducible; - traceable; - verifiable; - immutable... |
| MCC-CP-001 | 1081 | EXTRACTED | MCC-CP-001-14-EVIDENCE-REQUIREMENTS-D05 | — | Evidence SHALL reference the applicable specification version. |
| MCC-CP-001 | 1087 | EXTRACTED | MCC-CP-001-14-EVIDENCE-REQUIREMENTS-D06 | — | Every evidence item SHALL be traceable to: - the Certification Subject; - the evaluated... |
| MCC-CP-001 | 1094 | EXTRACTED | MCC-CP-001-14-EVIDENCE-REQUIREMENTS-D07 | — | Evidence traceability SHALL be preserved throughout certification. |
| MCC-CP-001 | 1100 | EXTRACTED | MCC-CP-001-14-EVIDENCE-REQUIREMENTS-D08 | — | Evidence SHALL remain available for independent verification. |
| MCC-CP-001 | 1104 | EXTRACTED | MCC-CP-001-14-EVIDENCE-REQUIREMENTS-D09 | — | Evidence SHALL NOT be modified after certification. |
| MCC-CP-001 | 1146 | EXTRACTED | MCC-CP-001-15-CERTIFICATION-MANIFEST-REQUIREMENTS-D01 | — | A Certification Manifest SHALL describe the certification results in a structured, mach... |
| MCC-CP-001 | 1152 | EXTRACTED | MCC-CP-001-15-CERTIFICATION-MANIFEST-REQUIREMENTS-D02 | — | Every Certification Manifest SHALL include: - manifest identifier; - specification vers... |
| MCC-CP-001 | 1167 | EXTRACTED | MCC-CP-001-15-CERTIFICATION-MANIFEST-REQUIREMENTS-D03 | — | Certification Manifests SHALL accurately represent the certification results. |
| MCC-CP-001 | 1169 | EXTRACTED | MCC-CP-001-15-CERTIFICATION-MANIFEST-REQUIREMENTS-D04 | — | A Certification Manifest SHALL NOT contain unverifiable claims. |
| MCC-CP-001 | 1171 | EXTRACTED | MCC-CP-001-15-CERTIFICATION-MANIFEST-REQUIREMENTS-D05 | — | Manifest integrity SHALL be preserved after generation. |
| MCC-CP-001 | 1177 | EXTRACTED | MCC-CP-001-15-CERTIFICATION-MANIFEST-REQUIREMENTS-D06 | — | Every Certification Manifest SHALL be traceable to: - the Certification Subject; - the ... |
| MCC-CP-001 | 1188 | EXTRACTED | MCC-CP-001-15-CERTIFICATION-MANIFEST-REQUIREMENTS-D07 | — | Certification Manifests SHALL declare the specification version against which certifica... |
| MCC-CP-001 | 1190 | EXTRACTED | MCC-CP-001-15-CERTIFICATION-MANIFEST-REQUIREMENTS-D08 | — | Manifest versions SHALL remain immutable after publication. |
| MCC-CP-001 | 1232 | EXTRACTED | MCC-CP-001-16-TECHNICAL-CERTIFICATE-REQUIREMENTS-D01 | — | A Technical Certificate SHALL represent the authoritative certification outcome for a C... |
| MCC-CP-001 | 1234 | EXTRACTED | MCC-CP-001-16-TECHNICAL-CERTIFICATE-REQUIREMENTS-D02 | — | Technical Certificates SHALL be derived only from successful certification. |
| MCC-CP-001 | 1240 | EXTRACTED | MCC-CP-001-16-TECHNICAL-CERTIFICATE-REQUIREMENTS-D03 | — | Every Technical Certificate SHALL include: - certificate identifier; - Certification Su... |
| MCC-CP-001 | 1255 | EXTRACTED | MCC-CP-001-16-TECHNICAL-CERTIFICATE-REQUIREMENTS-D04 | — | Technical Certificates SHALL be issued only after successful completion of certification. |
| MCC-CP-001 | 1257 | EXTRACTED | MCC-CP-001-16-TECHNICAL-CERTIFICATE-REQUIREMENTS-D05 | — | Certificates SHALL NOT be issued for unsuccessful certification. |
| MCC-CP-001 | 1263 | EXTRACTED | MCC-CP-001-16-TECHNICAL-CERTIFICATE-REQUIREMENTS-D06 | — | Technical Certificates SHALL accurately represent certification results. |
| MCC-CP-001 | 1265 | EXTRACTED | MCC-CP-001-16-TECHNICAL-CERTIFICATE-REQUIREMENTS-D07 | — | Certificates SHALL NOT contain unverifiable claims. |
| MCC-CP-001 | 1267 | EXTRACTED | MCC-CP-001-16-TECHNICAL-CERTIFICATE-REQUIREMENTS-D08 | — | Certificate integrity SHALL be preserved after issuance. |
| MCC-CP-001 | 1273 | EXTRACTED | MCC-CP-001-16-TECHNICAL-CERTIFICATE-REQUIREMENTS-D09 | — | Every Technical Certificate SHALL be traceable to: - the Certification Subject; - the a... |
| MCC-CP-001 | 1320 | EXTRACTED | MCC-CP-001-17-VERSIONING-D01 | — | Versioning SHALL support reproducible certification. |
| MCC-CP-001 | 1322 | EXTRACTED | MCC-CP-001-17-VERSIONING-D02 | — | Versioning SHALL support long-term compatibility. |
| MCC-CP-001 | 1326 | EXTRACTED | MCC-CP-001-17-VERSIONING-D03 | — | Each certification SHALL reference an explicit specification version. |
| MCC-CP-001 | 1328 | EXTRACTED | MCC-CP-001-17-VERSIONING-D04 | — | Specification versions SHALL uniquely identify the normative document used during certi... |
| MCC-CP-001 | 1330 | EXTRACTED | MCC-CP-001-17-VERSIONING-D05 | — | Version identifiers SHALL remain immutable. |
| MCC-CP-001 | 1334 | EXTRACTED | MCC-CP-001-17-VERSIONING-D06 | — | Certification SHALL be evaluated only against the referenced specification version. |
| MCC-CP-001 | 1336 | EXTRACTED | MCC-CP-001-17-VERSIONING-D07 | — | Different specification versions SHALL NOT be considered equivalent unless explicitly d... |
| MCC-CP-001 | 1338 | EXTRACTED | MCC-CP-001-17-VERSIONING-D08 | — | Compatibility rules SHALL be documented. |
| MCC-CP-001 | 1344 | EXTRACTED | MCC-CP-001-17-VERSIONING-D09 | — | Each revalidation SHALL produce a new certification result. |
| MCC-CP-001 | 1346 | EXTRACTED | MCC-CP-001-17-VERSIONING-D10 | — | Previous certification results SHALL remain preserved. |
| MCC-CP-001 | 1386 | EXTRACTED | MCC-CP-001-18-SECURITY-CONSIDERATIONS-D01 | — | Security requirements SHALL protect certification integrity. |
| MCC-CP-001 | 1388 | EXTRACTED | MCC-CP-001-18-SECURITY-CONSIDERATIONS-D02 | — | Security requirements SHALL remain implementation-independent. |
| MCC-CP-001 | 1392 | EXTRACTED | MCC-CP-001-18-SECURITY-CONSIDERATIONS-D03 | — | Certification SHALL resist unauthorized modification. |
| MCC-CP-001 | 1394 | DUPLICATE_OF_CANONICAL | — | SEC-004 | Certification SHALL preserve evidence integrity. |
| MCC-CP-001 | 1396 | EXTRACTED | MCC-CP-001-18-SECURITY-CONSIDERATIONS-D04 | — | Certification SHALL support independent verification. |
| MCC-CP-001 | 1398 | DUPLICATE_OF_CANONICAL | — | SEC-002 | Certification SHALL remain reproducible. |
| MCC-CP-001 | 1402 | EXTRACTED | MCC-CP-001-18-SECURITY-CONSIDERATIONS-D05 | — | Certification SHALL assume untrusted implementations. |
| MCC-CP-001 | 1404 | EXTRACTED | MCC-CP-001-18-SECURITY-CONSIDERATIONS-D06 | — | Certification SHALL assume potentially malicious inputs. |
| MCC-CP-001 | 1406 | EXTRACTED | MCC-CP-001-18-SECURITY-CONSIDERATIONS-D07 | — | Certification SHALL rely only on evaluated evidence. |
| MCC-CP-001 | 1408 | EXTRACTED | MCC-CP-001-18-SECURITY-CONSIDERATIONS-D08 | — | Certification SHALL remain independent of implementation identity. |
| MCC-CP-001 | 1448 | EXTRACTED | MCC-CP-001-19-REGISTRY-CONSIDERATIONS-D01 | — | Registries SHALL support reproducibility, traceability, and long-term interoperability. |
| MCC-CP-001 | 1454 | EXTRACTED | MCC-CP-001-19-REGISTRY-CONSIDERATIONS-D02 | — | Registry contents SHALL remain implementation-independent. |
| MCC-CP-001 | 1458 | EXTRACTED | MCC-CP-001-19-REGISTRY-CONSIDERATIONS-D03 | — | Registry entries SHALL be uniquely identifiable. |
| MCC-CP-001 | 1460 | EXTRACTED | MCC-CP-001-19-REGISTRY-CONSIDERATIONS-D04 | — | Registry entries SHALL be immutable after publication. |
| MCC-CP-001 | 1462 | EXTRACTED | MCC-CP-001-19-REGISTRY-CONSIDERATIONS-D05 | — | Registry entries SHALL remain traceable. |
| MCC-CP-001 | 1464 | EXTRACTED | MCC-CP-001-19-REGISTRY-CONSIDERATIONS-D06 | — | Registry entries SHALL reference applicable specification versions. |
| MCC-CP-001 | 1504 | EXTRACTED | MCC-CP-001-20-CONFORMANCE-STATEMENT-D01 | — | Conformance SHALL be evaluated solely against normative requirements defined by this sp... |
| MCC-CP-001 | 1510 | EXTRACTED | MCC-CP-001-20-CONFORMANCE-STATEMENT-D02 | — | Conformance claims SHALL reference the applicable specification version. |
| MCC-CP-001 | 1512 | EXTRACTED | MCC-CP-001-20-CONFORMANCE-STATEMENT-D03 | — | Conformance claims SHALL reference the associated Certification Manifest. |
| MCC-CP-001 | 1514 | EXTRACTED | MCC-CP-001-20-CONFORMANCE-STATEMENT-D04 | — | Conformance claims SHALL reference the associated Technical Certificate. |
| MCC-CP-001 | 1560 | EXTRACTED | MCC-CP-001-21-REFERENCES-D01 | — | The following specifications SHALL be considered normative when referenced by this docu... |
| MCC-CP-001 | 1575 | EXTRACTED | MCC-CP-001-21-REFERENCES-D02 | — | Informative material SHALL NOT introduce normative requirements. |
| MCC-CP-001 | 1619 | EXTRACTED | MCC-CP-001-APPENDIX-A-CERTIFICATION-STATE-MACHINE-D01 | — | The certification process SHALL consist of the following states: - Draft - Submitted - ... |
| MCC-CP-001 | 1634 | EXTRACTED | MCC-CP-001-APPENDIX-A-CERTIFICATION-STATE-MACHINE-D02 | — | State transitions SHALL occur only through defined certification procedures. |
| MCC-CP-001 | 1636 | EXTRACTED | MCC-CP-001-APPENDIX-A-CERTIFICATION-STATE-MACHINE-D03 | — | Undefined transitions SHALL NOT occur. |
| MCC-CP-001 | 1638 | EXTRACTED | MCC-CP-001-APPENDIX-A-CERTIFICATION-STATE-MACHINE-D04 | — | Revocation SHALL NOT modify historical certification evidence. |
| MCC-CP-001 | 1640 | EXTRACTED | MCC-CP-001-APPENDIX-A-CERTIFICATION-STATE-MACHINE-D05 | — | Archival SHALL preserve certification history. |
| MCC-CP-001 | 1680 | EXTRACTED | MCC-CP-001-APPENDIX-B-CERTIFICATION-DECISION-MATRIX-D01 | — | Certification decisions SHALL be derived exclusively from evaluated normative requireme... |
| MCC-CP-001 | 1689 | EXTRACTED | MCC-CP-001-APPENDIX-B-CERTIFICATION-DECISION-MATRIX-D02 | — | No additional certification outcomes SHALL be defined unless introduced by a future spe... |
| MCC-CP-001 | 1691 | EXTRACTED | MCC-CP-001-APPENDIX-B-CERTIFICATION-DECISION-MATRIX-D03 | — | The governance runtime outcomes ALLOW, DENY, ESCALATE, and CONSTRAIN belong exclusively... |
| MCC-CP-001 | 1695 | EXTRACTED | MCC-CP-001-APPENDIX-B-CERTIFICATION-DECISION-MATRIX-D04 | — | Certification SHALL be granted only when all REQUIRED normative requirements have been ... |
| MCC-CP-001 | 1697 | EXTRACTED | MCC-CP-001-APPENDIX-B-CERTIFICATION-DECISION-MATRIX-D05 | — | OPTIONAL requirements SHALL NOT determine certification status. |
| MCC-CP-001 | 1699 | EXTRACTED | MCC-CP-001-APPENDIX-B-CERTIFICATION-DECISION-MATRIX-D06 | — | CONDITIONAL requirements SHALL be evaluated only when their applicability conditions ar... |
| MCC-CP-001 | 1739 | EXTRACTED | MCC-CP-001-APPENDIX-C-REQUIREMENT-IDENTIFIER-REGIST-D01 | — | Requirement identifiers SHALL remain globally unique within a published specification v... |
| MCC-CP-001 | 1749 | EXTRACTED | MCC-CP-001-APPENDIX-C-REQUIREMENT-IDENTIFIER-REGIST-D02 | — | Identifier formats SHALL remain stable across specification revisions. |
| MCC-CP-001 | 1753 | EXTRACTED | MCC-CP-001-APPENDIX-C-REQUIREMENT-IDENTIFIER-REGIST-D03 | — | The registry SHALL maintain: - identifier; - requirement title; - specification version... |
| MCC-CP-001 | 1761 | EXTRACTED | MCC-CP-001-APPENDIX-C-REQUIREMENT-IDENTIFIER-REGIST-D04 | — | Registry entries SHALL remain immutable after publication. |
| MCC-CP-001 | 1801 | EXTRACTED | MCC-CP-001-APPENDIX-D-REVISION-HISTORY-D01 | — | Revision history SHALL provide a complete and traceable record of specification evolution. |
| MCC-CP-001 | 1816 | EXTRACTED | MCC-CP-001-APPENDIX-D-REVISION-HISTORY-D02 | — | Future revisions SHALL preserve backward traceability. |
| MCC-CP-001 | 1818 | DUPLICATE_OF_CANONICAL | — | REV-003 | Breaking changes SHALL be explicitly identified. |
| MCC-CP-001 | 1820 | EXTRACTED | MCC-CP-001-APPENDIX-D-REVISION-HISTORY-D03 | — | Deprecated requirements SHALL remain documented. |
| MCC-CP-001 | 1822 | EXTRACTED | MCC-CP-001-APPENDIX-D-REVISION-HISTORY-D04 | — | Superseded requirements SHALL reference their replacements where applicable. |
| MCC-CP-001 | 1862 | EXTRACTED | MCC-CP-001-APPENDIX-E-EXAMPLE-CERTIFICATION-FLOW-D01 | — | The example is provided for illustration only and SHALL NOT introduce additional normat... |
| MCC-CP-001 | 1914 | EXTRACTED | MCC-CP-001-APPENDIX-F-FUTURE-EXTENSIONS-D01 | — | The items described in this appendix are informative only and SHALL NOT introduce norma... |
| MCC-CP-001 | 1928 | EXTRACTED | MCC-CP-001-APPENDIX-F-FUTURE-EXTENSIONS-D02 | — | Future extensions SHALL preserve backward traceability unless an explicitly documented ... |
| MCC-CP-001 | 1972 | EXTRACTED | MCC-CP-001-APPENDIX-G-CONFORMANCE-RESULT-REQUIREMEN-D01 | — | The Conformance Result SHALL identify: - the Certification Subject identifier, as defin... |
| MCC-CP-001 | 1982 | EXTRACTED | MCC-CP-001-APPENDIX-G-CONFORMANCE-RESULT-REQUIREMEN-D02 | — | It SHALL be carried by the Manifest Fields required under Section 15.2 ("certification ... |
| MCC-CP-001 | 1984 | EXTRACTED | MCC-CP-001-APPENDIX-G-CONFORMANCE-RESULT-REQUIREMEN-D03 | — | A certification implementation MUST NOT produce a Conformance Result as a document dist... |
| MCC-CP-001 | 2020 | EXTRACTED | MCC-CP-001-APPENDIX-H-CERTIFICATION-REPORT-REQUIREM-D01 | — | Every Certification Report SHALL include: - the Certification Subject identifier; - the... |
| MCC-CP-001 | 2031 | DUPLICATE_OF_CANONICAL | — | CREP-002 | The Certification Report SHALL be human-readable. |
| MCC-CP-001 | 2033 | EXTRACTED | MCC-CP-001-APPENDIX-H-CERTIFICATION-REPORT-REQUIREM-D02 | — | The Certification Report SHALL NOT be treated as the authoritative record of a certific... |
| MCC-CP-001 | 2035 | DUPLICATE_OF_CANONICAL | — | CREP-005 | The Certification Report SHALL NOT contain claims inconsistent with its referenced Cert... |
| MCC-CP-001 | 2047 | EXTRACTED | MCC-CP-001-APPENDIX-H-CERTIFICATION-REPORT-REQUIREM-D03 | — | A Certification Report SHALL be produced for every successful certification, consistent... |
| MCC-EB-001 | 194 | DUPLICATE_OF_CANONICAL | — | EB-STR-001 | Every Evidence Bundle SHALL have exactly one Bundle Root. |
| MCC-EB-001 | 196 | EXTRACTED | MCC-EB-001-10-BUNDLE-DIRECTORY-STRUCTURE-D01 | — | All Bundle contents SHALL be located within the Bundle Root. |
| MCC-EB-001 | 198 | EXTRACTED | MCC-EB-001-10-BUNDLE-DIRECTORY-STRUCTURE-D02 | — | The Bundle Root SHALL NOT contain content that is not part of the Evidence Bundle. |
| MCC-EB-001 | 202 | EXTRACTED | MCC-EB-001-10-BUNDLE-DIRECTORY-STRUCTURE-D03 | — | The Bundle Root SHALL contain, directly at its top level: - exactly one Bundle Descript... |
| MCC-EB-001 | 213 | EXTRACTED | MCC-EB-001-10-BUNDLE-DIRECTORY-STRUCTURE-D04 | — | The Evidence Directory SHALL contain one entry per Evidence Item. |
| MCC-EB-001 | 215 | EXTRACTED | MCC-EB-001-10-BUNDLE-DIRECTORY-STRUCTURE-D05 | — | Each Evidence Item entry SHALL be uniquely named within the Evidence Directory. |
| MCC-EB-001 | 217 | EXTRACTED | MCC-EB-001-10-BUNDLE-DIRECTORY-STRUCTURE-D06 | — | The internal structure of an individual Evidence Item MAY vary by requirement type but ... |
| MCC-EB-001 | 221 | EXTRACTED | MCC-EB-001-10-BUNDLE-DIRECTORY-STRUCTURE-D07 | — | All paths within a Bundle SHALL be relative to the Bundle Root. |
| MCC-EB-001 | 223 | EXTRACTED | MCC-EB-001-10-BUNDLE-DIRECTORY-STRUCTURE-D08 | — | Path names within a Bundle SHALL NOT encode information that is not also present in the... |
| MCC-EB-001 | 225 | EXTRACTED | MCC-EB-001-10-BUNDLE-DIRECTORY-STRUCTURE-D09 | — | Path names SHALL be stable across regeneration of an equivalent Bundle, in support of E... |
| MCC-EB-001 | 255 | EXTRACTED | MCC-EB-001-11-REQUIRED-FILES-D01 | — | The Bundle Descriptor MUST be present at the Bundle Root. |
| MCC-EB-001 | 257 | EXTRACTED | MCC-EB-001-11-REQUIRED-FILES-D02 | — | The Bundle Descriptor MUST declare: - the Evidence Bundle Schema Version; - a Bundle id... |
| MCC-EB-001 | 265 | EXTRACTED | MCC-EB-001-11-REQUIRED-FILES-D03 | — | The Integrity Record MUST be present at the Bundle Root. |
| MCC-EB-001 | 267 | EXTRACTED | MCC-EB-001-11-REQUIRED-FILES-D04 | — | The Integrity Record MUST enumerate a Digest for every file within the Bundle other tha... |
| MCC-EB-001 | 269 | EXTRACTED | MCC-EB-001-11-REQUIRED-FILES-D05 | — | The Integrity Record MUST declare the hash algorithm used, as governed by Section 13. |
| MCC-EB-001 | 273 | EXTRACTED | MCC-EB-001-11-REQUIRED-FILES-D06 | — | The Provenance Record MUST be present at the Bundle Root. |
| MCC-EB-001 | 275 | EXTRACTED | MCC-EB-001-11-REQUIRED-FILES-D07 | — | The Provenance Record MUST satisfy the Provenance Requirements defined in Section 14. |
| MCC-EB-001 | 281 | EXTRACTED | MCC-EB-001-11-REQUIRED-FILES-D08 | — | Where Evidence Items are present, each MUST be referenced by at least one entry in the ... |
| MCC-EB-001 | 311 | EXTRACTED | MCC-EB-001-12-REQUIRED-METADATA-D01 | — | The Bundle Descriptor MUST include: - Bundle identifier; - Evidence Bundle Schema Versi... |
| MCC-EB-001 | 321 | EXTRACTED | MCC-EB-001-12-REQUIRED-METADATA-D02 | — | Each Evidence Item MUST be associated with metadata identifying: - the Certification Re... |
| MCC-EB-001 | 329 | EXTRACTED | MCC-EB-001-12-REQUIRED-METADATA-D03 | — | Required metadata fields MUST be included in the data covered by the Integrity Record. |
| MCC-EB-001 | 331 | EXTRACTED | MCC-EB-001-12-REQUIRED-METADATA-D04 | — | Metadata fields MUST NOT be modified after Bundle generation without invalidating the B... |
| MCC-EB-001 | 365 | EXTRACTED | MCC-EB-001-13-HASH-AND-INTEGRITY-MODEL-D01 | — | Data covered by a Digest MUST first be reduced to a Canonical Form. |
| MCC-EB-001 | 367 | EXTRACTED | MCC-EB-001-13-HASH-AND-INTEGRITY-MODEL-D02 | — | Canonical Form MUST be deterministic: identical logical content MUST always produce an ... |
| MCC-EB-001 | 371 | EXTRACTED | MCC-EB-001-13-HASH-AND-INTEGRITY-MODEL-D03 | — | The Integrity Record MUST declare the cryptographic hash algorithm used to compute its ... |
| MCC-EB-001 | 373 | EXTRACTED | MCC-EB-001-13-HASH-AND-INTEGRITY-MODEL-D04 | — | The declared hash algorithm MUST be a collision-resistant cryptographic hash function. |
| MCC-EB-001 | 375 | EXTRACTED | MCC-EB-001-13-HASH-AND-INTEGRITY-MODEL-D05 | — | A Bundle MUST NOT be considered valid if it declares a hash algorithm that is not colli... |
| MCC-EB-001 | 379 | EXTRACTED | MCC-EB-001-13-HASH-AND-INTEGRITY-MODEL-D06 | — | Every file within the Bundle Root, other than the Integrity Record itself, MUST have a ... |
| MCC-EB-001 | 381 | EXTRACTED | MCC-EB-001-13-HASH-AND-INTEGRITY-MODEL-D07 | — | A Digest MUST cover the complete Canonical Form of the file it corresponds to. |
| MCC-EB-001 | 385 | EXTRACTED | MCC-EB-001-13-HASH-AND-INTEGRITY-MODEL-D08 | — | A validator MUST recompute the Digest of every file covered by the Integrity Record and... |
| MCC-EB-001 | 387 | EXTRACTED | MCC-EB-001-13-HASH-AND-INTEGRITY-MODEL-D09 | — | A Bundle SHALL be considered tampered if any recomputed Digest does not match its decla... |
| MCC-EB-001 | 389 | EXTRACTED | MCC-EB-001-13-HASH-AND-INTEGRITY-MODEL-D10 | — | A tampered Bundle MUST NOT be treated as valid evidence. |
| MCC-EB-001 | 419 | EXTRACTED | MCC-EB-001-14-PROVENANCE-REQUIREMENTS-D01 | — | Provenance Requirements define what an Evidence Bundle MUST record about its own origin... |
| MCC-EB-001 | 423 | EXTRACTED | MCC-EB-001-14-PROVENANCE-REQUIREMENTS-D02 | — | The Provenance Record MUST identify: - the certification run that produced the Bundle; ... |
| MCC-EB-001 | 432 | EXTRACTED | MCC-EB-001-14-PROVENANCE-REQUIREMENTS-D03 | — | Where an Evidence Bundle is derived from, or supersedes, a prior Bundle, the Provenance... |
| MCC-EB-001 | 434 | EXTRACTED | MCC-EB-001-14-PROVENANCE-REQUIREMENTS-D04 | — | Provenance references MUST NOT be circular. |
| MCC-EB-001 | 472 | EXTRACTED | MCC-EB-001-15-REPRODUCIBILITY-REQUIREMENTS-D01 | — | Given identical certification inputs and an identical specification version, Bundle gen... |
| MCC-EB-001 | 476 | EXTRACTED | MCC-EB-001-15-REPRODUCIBILITY-REQUIREMENTS-D02 | — | Canonical Form and Digest computation MUST NOT depend on: - wall-clock time, other than... |
| MCC-EB-001 | 484 | EXTRACTED | MCC-EB-001-15-REPRODUCIBILITY-REQUIREMENTS-D03 | — | Two Bundles produced from identical certification inputs and an identical specification... |
| MCC-EB-001 | 510 | EXTRACTED | MCC-EB-001-16-VALIDATION-RULES-D01 | — | Validation Rules define the normative procedure and criteria a validator MUST apply to ... |
| MCC-EB-001 | 514 | EXTRACTED | MCC-EB-001-16-VALIDATION-RULES-D02 | — | A validator MUST verify that the Bundle conforms to the Bundle Directory Structure defi... |
| MCC-EB-001 | 516 | EXTRACTED | MCC-EB-001-16-VALIDATION-RULES-D03 | — | A Bundle that fails structural validation MUST be rejected without further processing. |
| MCC-EB-001 | 520 | EXTRACTED | MCC-EB-001-16-VALIDATION-RULES-D04 | — | A validator MUST verify that all Required Metadata defined in Section 12 is present and... |
| MCC-EB-001 | 524 | EXTRACTED | MCC-EB-001-16-VALIDATION-RULES-D05 | — | A validator MUST perform Integrity Verification as defined in Section 13.5. |
| MCC-EB-001 | 526 | EXTRACTED | MCC-EB-001-16-VALIDATION-RULES-D06 | — | A Bundle that fails integrity validation MUST be rejected. |
| MCC-EB-001 | 530 | EXTRACTED | MCC-EB-001-16-VALIDATION-RULES-D07 | — | A validator MUST verify that Provenance Requirements defined in Section 14 are satisfie... |
| MCC-EB-001 | 534 | EXTRACTED | MCC-EB-001-16-VALIDATION-RULES-D08 | — | Validation SHALL be fail-closed: a Bundle MUST be treated as invalid unless every appli... |
| MCC-EB-001 | 536 | EXTRACTED | MCC-EB-001-16-VALIDATION-RULES-D09 | — | Partial or inconclusive validation results MUST NOT be treated as valid. |
| MCC-EB-001 | 570 | EXTRACTED | MCC-EB-001-17-VERSIONING-RULES-D01 | — | Every Bundle MUST declare its Evidence Bundle Schema Version in the Bundle Descriptor. |
| MCC-EB-001 | 572 | EXTRACTED | MCC-EB-001-17-VERSIONING-RULES-D02 | — | The Schema Version MUST be immutable once assigned to a published revision of this spec... |
| MCC-EB-001 | 578 | EXTRACTED | MCC-EB-001-17-VERSIONING-RULES-D03 | — | The Evidence Bundle Schema Version is distinct from, and SHALL NOT be conflated with, t... |
| MCC-EB-001 | 584 | EXTRACTED | MCC-EB-001-17-VERSIONING-RULES-D04 | — | A validator MUST reject a Bundle declaring a Schema Version it does not recognize, cons... |
| MCC-EB-001 | 618 | EXTRACTED | MCC-EB-001-18-COMPATIBILITY-REQUIREMENTS-D01 | — | A validator MUST NOT assume forward compatibility with a Schema Version it does not rec... |
| MCC-EB-001 | 620 | EXTRACTED | MCC-EB-001-18-COMPATIBILITY-REQUIREMENTS-D02 | — | An unrecognized Schema Version MUST be treated per Section 17.4 and Section 16.6, not s... |
| MCC-EB-001 | 624 | EXTRACTED | MCC-EB-001-18-COMPATIBILITY-REQUIREMENTS-D03 | — | A revision of this specification that alters the Bundle Directory Structure, Required F... |
| MCC-EB-001 | 654 | EXTRACTED | MCC-EB-001-19-SECURITY-CONSIDERATIONS-D01 | — | Validation of an Evidence Bundle MUST assume: - the Bundle MAY originate from an untrus... |
| MCC-EB-001 | 664 | EXTRACTED | MCC-EB-001-19-SECURITY-CONSIDERATIONS-D02 | — | A validator MUST NOT treat any Bundle content as authoritative prior to successful Inte... |
| MCC-EB-001 | 668 | EXTRACTED | MCC-EB-001-19-SECURITY-CONSIDERATIONS-D03 | — | An Evidence Bundle MUST NOT include secrets, credentials, or other sensitive material n... |
| MCC-EB-001 | 670 | EXTRACTED | MCC-EB-001-19-SECURITY-CONSIDERATIONS-D04 | — | Where underlying certification inputs contain sensitive material, Evidence Items MUST r... |
| MCC-EB-001 | 706 | EXTRACTED | MCC-EB-001-20-EXTENSION-MODEL-D01 | — | Extensions MUST be declared in the Bundle Descriptor. |
| MCC-EB-001 | 710 | EXTRACTED | MCC-EB-001-20-EXTENSION-MODEL-D02 | — | An extension MUST NOT alter the meaning of any Required File or Required Metadata defin... |
| MCC-EB-001 | 712 | EXTRACTED | MCC-EB-001-20-EXTENSION-MODEL-D03 | — | A validator that does not recognize a declared extension MUST ignore that extension's c... |
| MCC-EB-001 | 714 | EXTRACTED | MCC-EB-001-20-EXTENSION-MODEL-D04 | — | An extension MUST be covered by the Integrity Record like any other Bundle content. |
| MCC-EB-001 | 754 | EXTRACTED | MCC-EB-001-22-CONFORMANCE-REQUIREMENTS-D01 | — | A conforming Bundle producer MUST generate Bundles satisfying Sections 10 through 15 of... |
| MCC-EB-001 | 756 | EXTRACTED | MCC-EB-001-22-CONFORMANCE-REQUIREMENTS-D02 | — | A conforming Bundle producer MUST NOT emit a Bundle that fails validation under Section... |
| MCC-EB-001 | 760 | EXTRACTED | MCC-EB-001-22-CONFORMANCE-REQUIREMENTS-D03 | — | A conforming Bundle validator MUST implement the validation procedure defined in Sectio... |
| MCC-EB-001 | 762 | EXTRACTED | MCC-EB-001-22-CONFORMANCE-REQUIREMENTS-D04 | — | A conforming Bundle validator MUST reject a Bundle whenever any applicable validation s... |
| MCC-EB-001 | 766 | EXTRACTED | MCC-EB-001-22-CONFORMANCE-REQUIREMENTS-D05 | — | Conformance to this specification SHALL be evaluated independently of any specific prog... |
| MCC-EB-001 | 796 | EXTRACTED | MCC-EB-001-23-REQUIREMENT-IDENTIFIER-REGISTRY-D01 | — | Every normative requirement identifier defined by this specification SHALL be prefixed ... |
| MCC-EB-001 | 817 | EXTRACTED | MCC-EB-001-23-REQUIREMENT-IDENTIFIER-REGISTRY-D02 | — | Requirement identifiers under this specification's `EB-` namespace SHALL be globally un... |
| MCC-EB-001 | 819 | EXTRACTED | MCC-EB-001-23-REQUIREMENT-IDENTIFIER-REGISTRY-D03 | — | A future revision of this specification MUST NOT reuse a retired identifier for a diffe... |
| MCC-EB-001 | 821 | EXTRACTED | MCC-EB-001-23-REQUIREMENT-IDENTIFIER-REGISTRY-D04 | — | A future revision of this specification MUST NOT introduce a new category tag that coll... |
| MCC-CM-001 | 189 | EXTRACTED | MCC-CM-001-10-MANIFEST-SCHEMA-D01 | — | A Certification Manifest SHALL be composed of the following field groups: - Identificat... |
| MCC-CM-001 | 201 | EXTRACTED | MCC-CM-001-10-MANIFEST-SCHEMA-D02 | — | Every Manifest Field MUST have a defined type consistent with this specification: ident... |
| MCC-CM-001 | 203 | EXTRACTED | MCC-CM-001-10-MANIFEST-SCHEMA-D03 | — | Manifest Fields MUST NOT be ambiguous as to type. |
| MCC-CM-001 | 207 | EXTRACTED | MCC-CM-001-10-MANIFEST-SCHEMA-D04 | — | For any purpose requiring a Digest of a Certification Manifest, or a Digest of a subset... |
| MCC-CM-001 | 237 | EXTRACTED | MCC-CM-001-11-REQUIRED-FIELDS-D01 | — | Required Fields are the Manifest Fields that MUST be present in every conforming Certif... |
| MCC-CM-001 | 241 | EXTRACTED | MCC-CM-001-11-REQUIRED-FIELDS-D02 | — | Every Certification Manifest MUST include: - a manifest identifier, unique to the certi... |
| MCC-CM-001 | 250 | EXTRACTED | MCC-CM-001-11-REQUIRED-FIELDS-D03 | — | Consistent with MCC-CP-001, Section 15.2, every Certification Manifest MUST include: - ... |
| MCC-CM-001 | 263 | EXTRACTED | MCC-CM-001-11-REQUIRED-FIELDS-D04 | — | A Certification Manifest MUST NOT omit a Required Field regardless of certification out... |
| MCC-CM-001 | 310 | EXTRACTED | MCC-CM-001-12-OPTIONAL-FIELDS-D01 | — | An Optional Field, where present, MUST conform to the type rules of Section 10.3. |
| MCC-CM-001 | 312 | EXTRACTED | MCC-CM-001-12-OPTIONAL-FIELDS-D02 | — | The absence of an Optional Field MUST NOT be treated as a validation failure. |
| MCC-CM-001 | 314 | EXTRACTED | MCC-CM-001-12-OPTIONAL-FIELDS-D03 | — | An Optional Field MUST NOT be used to satisfy a Required Field obligation defined in Se... |
| MCC-CM-001 | 344 | EXTRACTED | MCC-CM-001-13-HASH-REFERENCES-D01 | — | A Hash Reference MUST identify: - the Digest value; - the hash algorithm used to produc... |
| MCC-CM-001 | 352 | EXTRACTED | MCC-CM-001-13-HASH-REFERENCES-D02 | — | The hash algorithm identified by a Hash Reference MUST be a collision-resistant cryptog... |
| MCC-CM-001 | 354 | EXTRACTED | MCC-CM-001-13-HASH-REFERENCES-D03 | — | A Certification Manifest MUST NOT be considered valid if any Hash Reference identifies ... |
| MCC-CM-001 | 358 | EXTRACTED | MCC-CM-001-13-HASH-REFERENCES-D04 | — | Every Evidence Bundle Reference, per Section 14, MUST include at least one Hash Referen... |
| MCC-CM-001 | 390 | EXTRACTED | MCC-CM-001-14-EVIDENCE-BUNDLE-REFERENCES-D01 | — | A Certification Manifest MUST reference exactly one primary Evidence Bundle correspondi... |
| MCC-CM-001 | 392 | EXTRACTED | MCC-CM-001-14-EVIDENCE-BUNDLE-REFERENCES-D02 | — | The primary Evidence Bundle Reference MUST include: - the Evidence Bundle identifier, a... |
| MCC-CM-001 | 402 | EXTRACTED | MCC-CM-001-14-EVIDENCE-BUNDLE-REFERENCES-D03 | — | A supplementary Evidence Bundle Reference MUST be distinguishable from the primary Evid... |
| MCC-CM-001 | 406 | EXTRACTED | MCC-CM-001-14-EVIDENCE-BUNDLE-REFERENCES-D04 | — | An Evidence Bundle Reference MUST NOT be considered satisfied unless the Hash Reference... |
| MCC-CM-001 | 408 | EXTRACTED | MCC-CM-001-14-EVIDENCE-BUNDLE-REFERENCES-D05 | — | A Certification Manifest whose primary Evidence Bundle Reference cannot be verified MUS... |
| MCC-CM-001 | 438 | EXTRACTED | MCC-CM-001-15-CERTIFICATION-METADATA-D01 | — | Certification Metadata MUST identify: - the Certification Subject, as defined by MCC-CP... |
| MCC-CM-001 | 446 | EXTRACTED | MCC-CM-001-15-CERTIFICATION-METADATA-D02 | — | Certification Metadata MUST record the overall certification result as one of the outco... |
| MCC-CM-001 | 451 | EXTRACTED | MCC-CM-001-15-CERTIFICATION-METADATA-D03 | — | A Certification Manifest MUST NOT record a certification result other than PASS or FAIL. |
| MCC-CM-001 | 455 | EXTRACTED | MCC-CM-001-15-CERTIFICATION-METADATA-D04 | — | Certification Metadata MUST include a Requirement Result for every Certification Requir... |
| MCC-CM-001 | 457 | EXTRACTED | MCC-CM-001-15-CERTIFICATION-METADATA-D05 | — | Each Requirement Result MUST identify: - the Certification Requirement identifier, as d... |
| MCC-CM-001 | 465 | EXTRACTED | MCC-CM-001-15-CERTIFICATION-METADATA-D06 | — | Certification Metadata MUST include a generation timestamp identifying when the Manifes... |
| MCC-CM-001 | 499 | EXTRACTED | MCC-CM-001-16-VERSIONING-RULES-D01 | — | Every Certification Manifest MUST declare its Manifest Schema Version among its Identif... |
| MCC-CM-001 | 501 | EXTRACTED | MCC-CM-001-16-VERSIONING-RULES-D02 | — | The Manifest Schema Version MUST be immutable once assigned to a published revision of ... |
| MCC-CM-001 | 507 | EXTRACTED | MCC-CM-001-16-VERSIONING-RULES-D03 | — | The Manifest Schema Version is distinct from, and SHALL NOT be conflated with, the MCC-... |
| MCC-CM-001 | 513 | EXTRACTED | MCC-CM-001-16-VERSIONING-RULES-D04 | — | A validator MUST reject a Certification Manifest declaring a Schema Version it does not... |
| MCC-CM-001 | 547 | EXTRACTED | MCC-CM-001-17-COMPATIBILITY-RULES-D01 | — | A validator MUST NOT assume forward compatibility with a Manifest Schema Version it doe... |
| MCC-CM-001 | 549 | EXTRACTED | MCC-CM-001-17-COMPATIBILITY-RULES-D02 | — | An unrecognized Manifest Schema Version MUST be treated per Section 16.4 and Section 18... |
| MCC-CM-001 | 553 | EXTRACTED | MCC-CM-001-17-COMPATIBILITY-RULES-D03 | — | A revision of this specification that alters the Manifest Schema, Required Fields, Hash... |
| MCC-CM-001 | 557 | EXTRACTED | MCC-CM-001-17-COMPATIBILITY-RULES-D04 | — | A Certification Manifest MUST NOT be considered valid if it references an Evidence Bund... |
| MCC-CM-001 | 583 | EXTRACTED | MCC-CM-001-18-VALIDATION-RULES-D01 | — | Validation Rules define the normative procedure and criteria a validator MUST apply to ... |
| MCC-CM-001 | 587 | EXTRACTED | MCC-CM-001-18-VALIDATION-RULES-D02 | — | A validator MUST verify that the Manifest conforms to the Manifest Schema defined in Se... |
| MCC-CM-001 | 589 | EXTRACTED | MCC-CM-001-18-VALIDATION-RULES-D03 | — | A Manifest that fails structural validation MUST be rejected without further processing. |
| MCC-CM-001 | 593 | EXTRACTED | MCC-CM-001-18-VALIDATION-RULES-D04 | — | A validator MUST independently recompute and verify every Hash Reference contained in t... |
| MCC-CM-001 | 595 | EXTRACTED | MCC-CM-001-18-VALIDATION-RULES-D05 | — | A Manifest containing any unverifiable Hash Reference MUST be rejected. |
| MCC-CM-001 | 599 | EXTRACTED | MCC-CM-001-18-VALIDATION-RULES-D06 | — | A validator MUST verify the primary Evidence Bundle Reference defined in Section 14.2 a... |
| MCC-CM-001 | 601 | EXTRACTED | MCC-CM-001-18-VALIDATION-RULES-D07 | — | A Manifest whose primary Evidence Bundle Reference cannot be verified MUST be rejected. |
| MCC-CM-001 | 605 | EXTRACTED | MCC-CM-001-18-VALIDATION-RULES-D08 | — | A validator MUST verify that Certification Metadata is internally consistent: that the ... |
| MCC-CM-001 | 609 | EXTRACTED | MCC-CM-001-18-VALIDATION-RULES-D09 | — | Validation SHALL be fail-closed: a Certification Manifest MUST be treated as invalid un... |
| MCC-CM-001 | 611 | EXTRACTED | MCC-CM-001-18-VALIDATION-RULES-D10 | — | Partial or inconclusive validation results MUST NOT be treated as valid. |
| MCC-CM-001 | 645 | EXTRACTED | MCC-CM-001-19-SECURITY-CONSIDERATIONS-D01 | — | Validation of a Certification Manifest MUST assume: - the Manifest MAY originate from a... |
| MCC-CM-001 | 659 | EXTRACTED | MCC-CM-001-19-SECURITY-CONSIDERATIONS-D02 | — | A Certification Manifest MUST NOT include secrets, credentials, or other sensitive mate... |
| MCC-CM-001 | 661 | EXTRACTED | MCC-CM-001-19-SECURITY-CONSIDERATIONS-D03 | — | Where underlying certification inputs contain sensitive material, Manifest Fields MUST ... |
| MCC-CM-001 | 697 | EXTRACTED | MCC-CM-001-20-EXTENSION-MODEL-D01 | — | Extensions MUST be declared and identified as such within the Manifest. |
| MCC-CM-001 | 701 | EXTRACTED | MCC-CM-001-20-EXTENSION-MODEL-D02 | — | An extension MUST NOT alter the meaning of any Required Field, Hash Reference, or Evide... |
| MCC-CM-001 | 703 | EXTRACTED | MCC-CM-001-20-EXTENSION-MODEL-D03 | — | A validator that does not recognize a declared extension MUST ignore that extension's c... |
| MCC-CM-001 | 739 | EXTRACTED | MCC-CM-001-22-CONFORMANCE-REQUIREMENTS-D01 | — | A conforming Manifest producer MUST generate Manifests satisfying Sections 10 through 1... |
| MCC-CM-001 | 741 | EXTRACTED | MCC-CM-001-22-CONFORMANCE-REQUIREMENTS-D02 | — | A conforming Manifest producer MUST NOT emit a Manifest that fails validation under Sec... |
| MCC-CM-001 | 745 | EXTRACTED | MCC-CM-001-22-CONFORMANCE-REQUIREMENTS-D03 | — | A conforming Manifest validator MUST implement the validation procedure defined in Sect... |
| MCC-CM-001 | 747 | EXTRACTED | MCC-CM-001-22-CONFORMANCE-REQUIREMENTS-D04 | — | A conforming Manifest validator MUST reject a Manifest whenever any applicable validati... |
| MCC-CM-001 | 751 | EXTRACTED | MCC-CM-001-22-CONFORMANCE-REQUIREMENTS-D05 | — | Conformance to this specification SHALL be evaluated independently of any specific prog... |
| MCC-CM-001 | 781 | EXTRACTED | MCC-CM-001-23-REQUIREMENT-IDENTIFIER-REGISTRY-D01 | — | Every normative requirement identifier defined by this specification SHALL be prefixed ... |
| MCC-CM-001 | 802 | EXTRACTED | MCC-CM-001-23-REQUIREMENT-IDENTIFIER-REGISTRY-D02 | — | Requirement identifiers under this specification's `CM-` namespace SHALL be globally un... |
| MCC-CM-001 | 804 | EXTRACTED | MCC-CM-001-23-REQUIREMENT-IDENTIFIER-REGISTRY-D03 | — | A future revision of this specification MUST NOT reuse a retired identifier for a diffe... |
| MCC-CM-001 | 806 | EXTRACTED | MCC-CM-001-23-REQUIREMENT-IDENTIFIER-REGISTRY-D04 | — | A future revision of this specification MUST NOT introduce a new category tag that coll... |
| MCC-TC-001 | 144 | EXTRACTED | MCC-TC-001-3-CERTIFICATE-MODEL-D01 | — | A Technical Certificate SHALL NOT be issued where the Certification Decision is FAIL. |
| MCC-TC-001 | 148 | EXTRACTED | MCC-TC-001-3-CERTIFICATE-MODEL-D02 | — | A Technical Certificate MUST reference exactly one Certification Manifest, as defined b... |
| MCC-TC-001 | 150 | EXTRACTED | MCC-TC-001-3-CERTIFICATE-MODEL-D03 | — | A Technical Certificate MUST also reference, by a direct Evidence Bundle Reference per ... |
| MCC-TC-001 | 152 | EXTRACTED | MCC-TC-001-3-CERTIFICATE-MODEL-D05 | — | A verifier MUST check this consistency, per Section 15.5. |
| MCC-TC-001 | 152 | EXTRACTED | MCC-TC-001-3-CERTIFICATE-MODEL-D04 | — | The Evidence Bundle identified by the Certificate's direct Evidence Bundle Reference MU... |
| MCC-TC-001 | 188 | EXTRACTED | MCC-TC-001-4-CERTIFICATE-SCHEMA-D01 | — | A Technical Certificate SHALL be a single structured, machine-readable document compose... |
| MCC-TC-001 | 203 | EXTRACTED | MCC-TC-001-4-CERTIFICATE-SCHEMA-D02 | — | Every Certificate field MUST have a defined type consistent with this specification: id... |
| MCC-TC-001 | 205 | EXTRACTED | MCC-TC-001-4-CERTIFICATE-SCHEMA-D03 | — | Certificate fields MUST NOT be ambiguous as to type. |
| MCC-TC-001 | 209 | EXTRACTED | MCC-TC-001-4-CERTIFICATE-SCHEMA-D04 | — | For any purpose requiring a Digest or signature over a Technical Certificate, the data ... |
| MCC-TC-001 | 211 | EXTRACTED | MCC-TC-001-4-CERTIFICATE-SCHEMA-D05 | — | The Canonical Form used for signing MUST exclude the Signature field itself. |
| MCC-TC-001 | 245 | EXTRACTED | MCC-TC-001-5-CERTIFICATE-IDENTITY-D01 | — | Every Technical Certificate MUST include: - a certificate identifier, globally unique a... |
| MCC-TC-001 | 253 | EXTRACTED | MCC-TC-001-5-CERTIFICATE-IDENTITY-D02 | — | A certificate identifier, once assigned, MUST NOT be reused for a different Technical C... |
| MCC-TC-001 | 255 | EXTRACTED | MCC-TC-001-5-CERTIFICATE-IDENTITY-D03 | — | A revalidation that produces a new certification result MUST be issued as a new Technic... |
| MCC-TC-001 | 277 | EXTRACTED | MCC-TC-001-6-REQUIRED-FIELDS-D01 | — | Required Fields are the fields that MUST be present in every conforming Technical Certi... |
| MCC-TC-001 | 281 | EXTRACTED | MCC-TC-001-6-REQUIRED-FIELDS-D02 | — | Consistent with MCC-CP-001, Section 16.2, every Technical Certificate MUST include: - c... |
| MCC-TC-001 | 294 | EXTRACTED | MCC-TC-001-6-REQUIRED-FIELDS-D03 | — | In addition to Section 6.2, every Technical Certificate MUST include: - Issuer identity... |
| MCC-TC-001 | 302 | EXTRACTED | MCC-TC-001-6-REQUIRED-FIELDS-D05 | — | A Certificate that omits any Required Field MUST be rejected under Section 15. |
| MCC-TC-001 | 302 | EXTRACTED | MCC-TC-001-6-REQUIRED-FIELDS-D04 | — | A Technical Certificate MUST NOT omit a Required Field. |
| MCC-TC-001 | 306 | EXTRACTED | MCC-TC-001-6-REQUIRED-FIELDS-D06 | — | The Manifest Reference MUST include: - the Certification Manifest identifier; - the Man... |
| MCC-TC-001 | 314 | EXTRACTED | MCC-TC-001-6-REQUIRED-FIELDS-D08 | — | It MUST NOT be satisfied only by transitive resolution through the Certification Manifest. |
| MCC-TC-001 | 314 | EXTRACTED | MCC-TC-001-6-REQUIRED-FIELDS-D07 | — | The Evidence Bundle Reference MUST be present as direct Certificate content. |
| MCC-TC-001 | 316 | EXTRACTED | MCC-TC-001-6-REQUIRED-FIELDS-D09 | — | The Evidence Bundle Reference MUST include: - the Evidence Bundle identifier, as define... |
| MCC-TC-001 | 322 | EXTRACTED | MCC-TC-001-6-REQUIRED-FIELDS-D10 | — | The Evidence Bundle identified by this Hash Reference MUST be the same Evidence Bundle ... |
| MCC-TC-001 | 368 | EXTRACTED | MCC-TC-001-7-OPTIONAL-FIELDS-D01 | — | An Optional Field, where present, MUST conform to the type rules of Section 4.3. |
| MCC-TC-001 | 370 | EXTRACTED | MCC-TC-001-7-OPTIONAL-FIELDS-D02 | — | The absence of an Optional Field MUST NOT be treated as a validation failure. |
| MCC-TC-001 | 372 | EXTRACTED | MCC-TC-001-7-OPTIONAL-FIELDS-D03 | — | An Optional Field MUST NOT be used to satisfy a Required Field obligation defined in Se... |
| MCC-TC-001 | 398 | EXTRACTED | MCC-TC-001-8-SUBJECT-IDENTIFICATION-D01 | — | A Technical Certificate MUST identify exactly one Certification Subject, using the Cert... |
| MCC-TC-001 | 400 | EXTRACTED | MCC-TC-001-8-SUBJECT-IDENTIFICATION-D02 | — | A Technical Certificate MUST NOT apply to more than one Certification Subject. |
| MCC-TC-001 | 404 | EXTRACTED | MCC-TC-001-8-SUBJECT-IDENTIFICATION-D03 | — | The Certification Subject identified by a Technical Certificate MUST match the Certific... |
| MCC-TC-001 | 406 | EXTRACTED | MCC-TC-001-8-SUBJECT-IDENTIFICATION-D04 | — | A mismatch MUST cause verification to fail under Section 15. |
| MCC-TC-001 | 432 | EXTRACTED | MCC-TC-001-9-CERTIFICATION-RESULT-REPRESENTATION-D01 | — | A Technical Certificate MUST record its certification result as exactly PASS, consisten... |
| MCC-TC-001 | 434 | EXTRACTED | MCC-TC-001-9-CERTIFICATION-RESULT-REPRESENTATION-D02 | — | A Technical Certificate MUST NOT record a certification result of FAIL. No Certificate ... |
| MCC-TC-001 | 438 | EXTRACTED | MCC-TC-001-9-CERTIFICATION-RESULT-REPRESENTATION-D03 | — | The certification result recorded by a Technical Certificate MUST match the certificati... |
| MCC-TC-001 | 440 | EXTRACTED | MCC-TC-001-9-CERTIFICATION-RESULT-REPRESENTATION-D04 | — | A mismatch MUST cause verification to fail under Section 15. |
| MCC-TC-001 | 444 | EXTRACTED | MCC-TC-001-9-CERTIFICATION-RESULT-REPRESENTATION-D05 | — | A Technical Certificate MUST record the capability profiles verified during certificati... |
| MCC-TC-001 | 446 | EXTRACTED | MCC-TC-001-9-CERTIFICATION-RESULT-REPRESENTATION-D06 | — | A capability profile MUST NOT appear as certified on a Technical Certificate unless it ... |
| MCC-TC-001 | 472 | EXTRACTED | MCC-TC-001-10-ISSUER-INFORMATION-D01 | — | A Technical Certificate MUST identify its Issuer by a stable Issuer identifier associat... |
| MCC-TC-001 | 476 | EXTRACTED | MCC-TC-001-10-ISSUER-INFORMATION-D02 | — | A Technical Certificate MUST NOT be considered validly issued unless its Issuer is reco... |
| MCC-TC-001 | 502 | DUPLICATE_OF_CANONICAL | — | TC-VALID-001 | Every Technical Certificate MUST record an issuance timestamp. |
| MCC-TC-001 | 504 | EXTRACTED | MCC-TC-001-11-VALIDITY-PERIOD-D01 | — | A Technical Certificate MUST NOT be considered valid before its issuance timestamp. |
| MCC-TC-001 | 510 | EXTRACTED | MCC-TC-001-11-VALIDITY-PERIOD-D02 | — | Where no expiration timestamp is declared, a Technical Certificate SHALL remain valid i... |
| MCC-TC-001 | 512 | EXTRACTED | MCC-TC-001-11-VALIDITY-PERIOD-D03 | — | Where an expiration timestamp is declared, a Technical Certificate MUST NOT be consider... |
| MCC-TC-001 | 542 | EXTRACTED | MCC-TC-001-12-REVOCATION-MODEL-D01 | — | A Technical Certificate MUST remain immutable after issuance, consistent with MCC-CP-00... |
| MCC-TC-001 | 544 | EXTRACTED | MCC-TC-001-12-REVOCATION-MODEL-D02 | — | Revocation SHALL NOT be represented by modifying a Technical Certificate's own content. |
| MCC-TC-001 | 544 | EXTRACTED | MCC-TC-001-12-REVOCATION-MODEL-D03 | — | Revocation SHALL be represented by an external Revocation Record. |
| MCC-TC-001 | 548 | EXTRACTED | MCC-TC-001-12-REVOCATION-MODEL-D04 | — | A Revocation Record MUST identify: - the certificate identifier of the revoked Technica... |
| MCC-TC-001 | 558 | EXTRACTED | MCC-TC-001-12-REVOCATION-MODEL-D05 | — | A Technical Certificate MUST NOT be revoked by any party other than the Issuer that iss... |
| MCC-TC-001 | 562 | EXTRACTED | MCC-TC-001-12-REVOCATION-MODEL-D06 | — | Once a valid Revocation Record exists for a Technical Certificate, that Certificate MUS... |
| MCC-TC-001 | 564 | EXTRACTED | MCC-TC-001-12-REVOCATION-MODEL-D07 | — | A revoked Technical Certificate's content, and the historical fact that it was issued, ... |
| MCC-TC-001 | 568 | EXTRACTED | MCC-TC-001-12-REVOCATION-MODEL-D08 | — | A verifier MUST check for the existence of a valid Revocation Record for a Technical Ce... |
| MCC-TC-001 | 608 | EXTRACTED | MCC-TC-001-13-CRYPTOGRAPHIC-INTEGRITY-D01 | — | Where a Technical Certificate includes a Hash Reference to its Certification Manifest o... |
| MCC-TC-001 | 640 | EXTRACTED | MCC-TC-001-14-SIGNATURE-REQUIREMENTS-D01 | — | The signature algorithm used to sign a Technical Certificate MUST be an asymmetric (pub... |
| MCC-TC-001 | 642 | EXTRACTED | MCC-TC-001-14-SIGNATURE-REQUIREMENTS-D02 | — | The signature algorithm MUST NOT be a symmetric-key or shared-secret authentication mec... |
| MCC-TC-001 | 648 | EXTRACTED | MCC-TC-001-14-SIGNATURE-REQUIREMENTS-D03 | — | A Technical Certificate's Signature MUST cover the complete Canonical Form of the Certi... |
| MCC-TC-001 | 650 | EXTRACTED | MCC-TC-001-14-SIGNATURE-REQUIREMENTS-D04 | — | A Signature MUST become invalid if any covered field is modified after signing. |
| MCC-TC-001 | 654 | EXTRACTED | MCC-TC-001-14-SIGNATURE-REQUIREMENTS-D05 | — | A Technical Certificate MUST declare the signature algorithm used and the Issuer identi... |
| MCC-TC-001 | 684 | EXTRACTED | MCC-TC-001-15-VERIFICATION-PROCEDURE-D01 | — | This section defines the normative procedure and criteria a verifier MUST apply to dete... |
| MCC-TC-001 | 688 | EXTRACTED | MCC-TC-001-15-VERIFICATION-PROCEDURE-D02 | — | A verifier MUST verify that the Certificate conforms to the Certificate Schema defined ... |
| MCC-TC-001 | 690 | EXTRACTED | MCC-TC-001-15-VERIFICATION-PROCEDURE-D03 | — | A Certificate that fails structural verification MUST be rejected without further proce... |
| MCC-TC-001 | 694 | EXTRACTED | MCC-TC-001-15-VERIFICATION-PROCEDURE-D04 | — | A verifier MUST verify the Certificate's Signature against a Trust Anchor associated wi... |
| MCC-TC-001 | 696 | EXTRACTED | MCC-TC-001-15-VERIFICATION-PROCEDURE-D05 | — | A Certificate with an invalid or unverifiable Signature MUST be rejected. |
| MCC-TC-001 | 700 | EXTRACTED | MCC-TC-001-15-VERIFICATION-PROCEDURE-D06 | — | A verifier MUST verify the Manifest Reference, including its Hash Reference, against th... |
| MCC-TC-001 | 702 | EXTRACTED | MCC-TC-001-15-VERIFICATION-PROCEDURE-D07 | — | A Certificate whose Manifest Reference cannot be verified MUST be rejected. |
| MCC-TC-001 | 706 | EXTRACTED | MCC-TC-001-15-VERIFICATION-PROCEDURE-D08 | — | A verifier MUST perform the following steps, in order, to verify the Certificate's Evid... |
| MCC-TC-001 | 713 | EXTRACTED | MCC-TC-001-15-VERIFICATION-PROCEDURE-D09 | — | Both Evidence Bundle References MUST identify the exact same Evidence Bundle. |
| MCC-TC-001 | 715 | EXTRACTED | MCC-TC-001-15-VERIFICATION-PROCEDURE-D10 | — | A verifier MUST return verification failure if the two Evidence Bundle References ident... |
| MCC-TC-001 | 717 | EXTRACTED | MCC-TC-001-15-VERIFICATION-PROCEDURE-D11 | — | A Certificate whose direct Evidence Bundle Reference cannot itself be verified against ... |
| MCC-TC-001 | 721 | EXTRACTED | MCC-TC-001-15-VERIFICATION-PROCEDURE-D12 | — | A verifier MUST verify Subject consistency per Section 8.3 and Certification Result con... |
| MCC-TC-001 | 725 | EXTRACTED | MCC-TC-001-15-VERIFICATION-PROCEDURE-D13 | — | A verifier MUST verify that the Certificate is within its Validity Period per Section 1... |
| MCC-TC-001 | 727 | EXTRACTED | MCC-TC-001-15-VERIFICATION-PROCEDURE-D14 | — | A Certificate that is expired or revoked MUST NOT be treated as currently valid, even i... |
| MCC-TC-001 | 731 | EXTRACTED | MCC-TC-001-15-VERIFICATION-PROCEDURE-D15 | — | Verification SHALL be fail-closed: a Technical Certificate MUST be treated as invalid u... |
| MCC-TC-001 | 733 | EXTRACTED | MCC-TC-001-15-VERIFICATION-PROCEDURE-D16 | — | Partial or inconclusive verification results MUST NOT be treated as valid. |
| MCC-TC-001 | 773 | EXTRACTED | MCC-TC-001-16-TRUST-MODEL-D01 | — | A verifier MUST possess or obtain a set of Trust Anchors it recognizes through a mechan... |
| MCC-TC-001 | 777 | EXTRACTED | MCC-TC-001-16-TRUST-MODEL-D02 | — | A Technical Certificate signed by a key that does not correspond to a Trust Anchor reco... |
| MCC-TC-001 | 779 | EXTRACTED | MCC-TC-001-16-TRUST-MODEL-D03 | — | Recognition of a Trust Anchor MUST NOT be inferred from the Certificate itself; a Certi... |
| MCC-TC-001 | 783 | EXTRACTED | MCC-TC-001-16-TRUST-MODEL-D04 | — | Where an Issuer's signing key is rotated or revoked, a verifier MUST cease treating Tec... |
| MCC-TC-001 | 791 | EXTRACTED | MCC-TC-001-16-TRUST-MODEL-D05 | — | A verifier MUST NOT treat a Technical Certificate as valid solely because it was signed... |
| MCC-TC-001 | 825 | EXTRACTED | MCC-TC-001-17-COMPATIBILITY-D01 | — | A verifier MUST NOT assume forward compatibility with a Certificate Schema Version it d... |
| MCC-TC-001 | 827 | EXTRACTED | MCC-TC-001-17-COMPATIBILITY-D02 | — | An unrecognized Certificate Schema Version MUST be treated per Section 18.4 and Section... |
| MCC-TC-001 | 831 | EXTRACTED | MCC-TC-001-17-COMPATIBILITY-D03 | — | A Technical Certificate MUST NOT be considered valid if it references a Manifest Schema... |
| MCC-TC-001 | 833 | EXTRACTED | MCC-TC-001-17-COMPATIBILITY-D04 | — | A Technical Certificate MUST NOT be considered valid if its direct Evidence Bundle Refe... |
| MCC-TC-001 | 863 | EXTRACTED | MCC-TC-001-18-VERSIONING-D01 | — | Every Technical Certificate MUST declare its Certificate Schema Version among its Ident... |
| MCC-TC-001 | 865 | EXTRACTED | MCC-TC-001-18-VERSIONING-D02 | — | The Certificate Schema Version MUST be immutable once assigned to a published revision ... |
| MCC-TC-001 | 871 | EXTRACTED | MCC-TC-001-18-VERSIONING-D03 | — | The Certificate Schema Version is distinct from, and SHALL NOT be conflated with, the M... |
| MCC-TC-001 | 877 | EXTRACTED | MCC-TC-001-18-VERSIONING-D04 | — | A verifier MUST reject a Technical Certificate declaring a Schema Version it does not r... |
| MCC-TC-001 | 907 | EXTRACTED | MCC-TC-001-19-SECURITY-CONSIDERATIONS-D01 | — | Verification of a Technical Certificate MUST assume: - the Certificate MAY originate fr... |
| MCC-TC-001 | 917 | EXTRACTED | MCC-TC-001-19-SECURITY-CONSIDERATIONS-D02 | — | A verifier MUST NOT treat any Certificate content as authoritative prior to successful ... |
| MCC-TC-001 | 921 | EXTRACTED | MCC-TC-001-19-SECURITY-CONSIDERATIONS-D03 | — | A Technical Certificate MUST NOT include secrets, credentials, or other sensitive mater... |
| MCC-TC-001 | 923 | EXTRACTED | MCC-TC-001-19-SECURITY-CONSIDERATIONS-D04 | — | Where underlying certification inputs contain sensitive material, Certificate fields MU... |
| MCC-TC-001 | 927 | EXTRACTED | MCC-TC-001-19-SECURITY-CONSIDERATIONS-D05 | — | A Technical Certificate MUST NOT be used, by any implementation, as a substitute for a ... |
| MCC-TC-001 | 927 | EXTRACTED | MCC-TC-001-19-SECURITY-CONSIDERATIONS-D06 | — | Possession of a valid Technical Certificate for a Certification Subject MUST NOT be tre... |
| MCC-TC-001 | 963 | EXTRACTED | MCC-TC-001-20-EXTENSION-MODEL-D01 | — | Extensions MUST be declared and identified as such within the Certificate. |
| MCC-TC-001 | 967 | EXTRACTED | MCC-TC-001-20-EXTENSION-MODEL-D02 | — | An extension MUST NOT alter the meaning of any Required Field, the Signature, the Manif... |
| MCC-TC-001 | 969 | EXTRACTED | MCC-TC-001-20-EXTENSION-MODEL-D03 | — | An extension MUST be covered by the Certificate's Signature like any other Certificate ... |
| MCC-TC-001 | 971 | EXTRACTED | MCC-TC-001-20-EXTENSION-MODEL-D04 | — | A verifier that does not recognize a declared extension MUST ignore that extension's co... |
| MCC-TC-001 | 1001 | EXTRACTED | MCC-TC-001-21-CONFORMANCE-REQUIREMENTS-D01 | — | A conforming Certificate issuer MUST issue Technical Certificates satisfying Sections 4... |
| MCC-TC-001 | 1003 | EXTRACTED | MCC-TC-001-21-CONFORMANCE-REQUIREMENTS-D02 | — | A conforming Certificate issuer MUST NOT issue a Technical Certificate for a certificat... |
| MCC-TC-001 | 1005 | EXTRACTED | MCC-TC-001-21-CONFORMANCE-REQUIREMENTS-D03 | — | A conforming Certificate issuer MUST NOT issue a Technical Certificate that fails verif... |
| MCC-TC-001 | 1007 | EXTRACTED | MCC-TC-001-21-CONFORMANCE-REQUIREMENTS-D04 | — | A conforming Certificate issuer MUST ensure that the Certificate's direct Evidence Bund... |
| MCC-TC-001 | 1011 | EXTRACTED | MCC-TC-001-21-CONFORMANCE-REQUIREMENTS-D05 | — | A conforming Certificate verifier MUST implement the verification procedure defined in ... |
| MCC-TC-001 | 1013 | EXTRACTED | MCC-TC-001-21-CONFORMANCE-REQUIREMENTS-D06 | — | A conforming Certificate verifier MUST reject a Technical Certificate whenever any appl... |
| MCC-TC-001 | 1017 | EXTRACTED | MCC-TC-001-21-CONFORMANCE-REQUIREMENTS-D07 | — | Conformance to this specification SHALL be evaluated independently of any specific prog... |
| MCC-TC-001 | 1051 | EXTRACTED | MCC-TC-001-22-REQUIREMENT-IDENTIFIER-REGISTRY-D01 | — | Every normative requirement identifier defined by this specification SHALL be prefixed ... |
| MCC-TC-001 | 1079 | EXTRACTED | MCC-TC-001-22-REQUIREMENT-IDENTIFIER-REGISTRY-D02 | — | Requirement identifiers under this specification's `TC-` namespace SHALL be globally un... |
| MCC-TC-001 | 1081 | EXTRACTED | MCC-TC-001-22-REQUIREMENT-IDENTIFIER-REGISTRY-D03 | — | A future revision of this specification MUST NOT reuse a retired identifier for a diffe... |
| MCC-TC-001 | 1083 | EXTRACTED | MCC-TC-001-22-REQUIREMENT-IDENTIFIER-REGISTRY-D04 | — | A future revision of this specification MUST NOT introduce a new category tag that coll... |

