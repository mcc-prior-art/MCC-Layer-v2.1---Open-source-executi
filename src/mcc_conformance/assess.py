"""Conformance assessment overlay for the Normative v1.0 baseline.

This module applies an explicit, disclosed, *category-level* assessment to
every extracted requirement. It does not claim per-requirement bespoke code
review of all ~430 requirements; instead it groups requirements by
specification section / category, and assigns each group a status and
rationale grounded in concrete, verified evidence (or its confirmed
absence) in this repository as of the reviewed baseline commit.

Methodology (disclosed in full in
``conformance/normative-v1.0/README.md``):

Per explicit correction to an earlier draft of this module: absence of a
requirement's exact vocabulary in the repository (e.g. no literal string
"Bundle Descriptor") is treated only as an investigation *signal*, never as
final evidence of GAP. Before any GAP classification below, the following
pre-existing subsystems were read and semantically compared against the
relevant specification section, not just grepped for terminology:

  - ``src/mcc_evidence/`` (schema.py, export.py, verify.py) — a real,
    tested "Governance Evidence Bundle" system: directory/.tar.gz bundle
    forms, SHA-256 digest recomputation and tamper detection, schema-
    version rejection, fail-closed verification, Ed25519 signature
    verification. Semantically close to MCC-EB-001 in behavior, though it
    uses one ``manifest.json`` plus named artifact paths rather than this
    specification's Bundle Descriptor / Integrity Record / Provenance
    Record three-file split.
  - ``src/mcc_compliance/`` (program.py, runner.py, reporting.py,
    registry.py) plus the committed ``certifications/manifest.json`` — a
    real, tested, deterministic certification system: golden vectors with
    stable requirement-like IDs and a ``mandatory`` (required/optional)
    flag, a compliance runner producing pass/fail-style scenario counts, a
    versioned certification manifest with digest-bound evidence and a
    CERTIFIED/NOT_CERTIFIED-style status, and both JSON and human-readable
    Markdown report generation. Semantically close to substantial parts of
    MCC-CP-001 (Certification Model/Lifecycle/Pipeline/Conformance Model/
    Requirement Classification/Appendix G Conformance Result/Appendix H
    Certification Report) and MCC-CM-001 (Manifest Schema/Versioning/
    Certification Metadata), though scoped to certifying *adapters against
    the Integration Contract*, not implementations against these four
    specifications, and using different field names and verdict vocabulary
    (CERTIFIED vs. PASS).
  - ``gateway/trust.py`` — a real, tested multi-issuer trust set: per-
    issuer Ed25519 keys, key rotation, per-key expiry, explicit REVOKED_KEY
    status, fail-closed unresolved-key handling. Semantically very close to
    MCC-TC-001's Trust Model (Section 16), Validity Period (Section 11),
    and Revocation Model (Section 12), though scoped to mandate/approval
    trust, not to Technical Certificates specifically.
  - ``src/mcc_compliance/capability_profile.py`` — a real, tested
    "Governance Capability Profile" validator (declared/validated/
    certified/authorized trust ladder, fail-closed on malformed or
    contradictory profiles). Semantically close to MCC-CP-001 Section 11
    (Capability Profiles).

Given this, PARTIAL is used wherever a section's *behavior* has a real,
tested analog under different names/scope, even with zero lexical overlap.
GAP is reserved for sections where, after this investigation, no equivalent
implementation behavior, test, or evidence mechanism was found anywhere in
the repository — principally: the exact three-file Bundle structure
(MCC-EB-001 Sections 10-11), structured Hash Reference / Evidence Bundle
Reference / Manifest Reference *sub-objects* as these specifications define
their required composition (MCC-CM-001 Section 13-14, MCC-TC-001 Section
6.5-6.6), the Revocation Record content model applied to an actual
Technical Certificate, and every specification's Extension Model (no
extension mechanism was found anywhere).

No requirement in this baseline is marked CONFORMANT. That status requires
both an implementation reference *and* a meaningful automated test tied to
the specific requirement as this specification states it, not to a
semantically-adjacent requirement in a different, differently-scoped
system. The PARTIAL findings above are exactly the candidates for
CONFORMANT once that specific wiring is built — see the gap report for
each one's recommended remediation.
"""

from __future__ import annotations

import re
from typing import Dict, List, Optional, Pattern, Tuple

from mcc_conformance.models import Requirement

# ---------------------------------------------------------------------------
# Evidence citation groups, named for readability in the rules table below.
# ---------------------------------------------------------------------------

# Note: src/mcc_core also has a dedicated repository-wide invariant test
# confirming no symmetric-key/shared-secret signing mechanism appears
# anywhere in the authority-bearing runtime path (tests/test_mcc_core.py).
# That test's name is deliberately not spelled out here so this file itself
# never contains the excluded algorithm's name, consistent with the
# repository's own "no such mechanism anywhere in src/" invariant.
EV_SIGNING = (
    ["src/mcc_core/signing.py"],
    ["tests/test_mcc_core.py::test_sign_and_verify_roundtrip",
     "tests/test_mcc_core.py::test_canonical_serialization_is_deterministic"],
)
EV_EB001_BUNDLE = (
    ["src/mcc_evidence/eb001_schema.py", "src/mcc_evidence/eb001_export.py", "src/mcc_evidence/eb001_verify.py"],
    ["tests/test_eb001_evidence_bundle.py"],
)
EV_CM001_MANIFEST = (
    ["src/mcc_evidence/cm001_manifest.py"],
    ["tests/test_cm001_evidence_bundle_reference.py"],
)
EV_HASH_REFERENCE = (
    ["src/mcc_evidence/hash_reference.py"],
    ["tests/test_hash_reference.py"],
)
EV_TC001_CERTIFICATE = (
    ["src/mcc_evidence/tc001_certificate.py"],
    ["tests/test_tc001_technical_certificate.py"],
)
EV_EVIDENCE_BUNDLE = (
    ["src/mcc_evidence/schema.py", "src/mcc_evidence/export.py", "src/mcc_evidence/verify.py"],
    ["tests/test_evidence_bundle.py", "tests/test_evidence_tamper.py", "tests/test_evidence_security.py"],
)
EV_COMPLIANCE_MANIFEST = (
    ["src/mcc_compliance/program.py", "certifications/manifest.json"],
    ["tests/test_certified_adapter_program.py"],
)
EV_COMPLIANCE_RUNNER = (
    ["src/mcc_compliance/runner.py", "src/mcc_compliance/registry.py",
     "src/mcc_compliance/vectors/v1/manifest.json"],
    ["tests/test_compliance_suite.py"],
)
EV_REPORTING = (
    ["src/mcc_compliance/reporting.py"],
    ["tests/test_compliance_suite.py", "tests/test_sdk_certification.py"],
)
EV_TRUST = (
    ["gateway/trust.py"],
    ["tests/test_trust.py"],
)
EV_CAPABILITY_PROFILE = (
    ["src/mcc_compliance/capability_profile.py"],
    ["tests/test_capability_profile.py"],
)

# ---------------------------------------------------------------------------
# Category rules. Matched by (specification_id, category regex), first hit
# wins. `evidence` is one of the EV_* tuples above, or None for GAP/N-A.
# ---------------------------------------------------------------------------

Rule = Tuple[str, Pattern, str, Optional[Tuple[List[str], List[str]]], str]

_META = re.compile(
    r"^(Status of This Specification|Abstract|\d+\.\s*Status|\d+\.\s*Abstract|"
    r"\d+\.\s*Normative (Language|References)|\d+\.\s*References|"
    r"\d+\.\s*Informative References|Appendix [A-Z] — Requirement Identifier Registry|"
    r"\d+\.\s*Requirement Identifier Registry|Appendix D — Revision History|"
    r"Document Roadmap|Appendix E — Example Certification Flow|"
    r"Appendix F — Future Extensions|\d+\.\s*IANA Considerations)$"
)

_NOT_APPLICABLE_RATIONALE = (
    "Interpretive, bibliographic, non-normative-by-design (explicitly marked "
    "informative/example), or document-self-referential statement. It does "
    "not describe a discrete, independently implementable system behavior."
)

_EXTENSION_MODEL_RATIONALE = (
    "No extension-declaration mechanism (a way to mark additional fields as "
    "explicit, non-breaking extensions to a committed schema) was found "
    "anywhere in this repository for any artifact."
)

RULES: List[Rule] = [
    # --- Cross-cutting: Extension Models, everywhere GAP ---
    ("*", re.compile(r"Extension Model"), "GAP", None, _EXTENSION_MODEL_RATIONALE),

    # --- MCC-EB-001 ---
    ("MCC-EB-001", re.compile(r"Evidence Bundle Overview|Bundle Directory Structure|Required Files|Required Metadata"),
     "PARTIAL", EV_EVIDENCE_BUNDLE,
     "src/mcc_evidence exports/verifies bundles in directory and .tar.gz form with bundle-level metadata "
     "(bundle_id, created_at), semantically close to this section, but uses one manifest.json plus named "
     "artifact paths rather than this specification's separate Bundle Descriptor / Integrity Record / "
     "Provenance Record files, so the exact structural requirement is not met."),
    ("MCC-EB-001", re.compile(r"Hash and Integrity Model"), "PARTIAL", EV_EVIDENCE_BUNDLE,
     "src/mcc_evidence/verify.py recomputes SHA-256 digests over canonical form and rejects any bundle with "
     "a mismatched digest as tampered, with dedicated tamper tests — behaviorally equivalent to this "
     "requirement, though bound to the mcc-evidence/1 schema rather than this specification's Bundle."),
    ("MCC-EB-001", re.compile(r"Provenance Requirements"), "PARTIAL", EV_EVIDENCE_BUNDLE,
     "EvidenceInput (export.py) records the originating governance run and correlation id, a narrower "
     "provenance model than this section's full requirement set (no explicit prior-bundle chain-of-custody "
     "reference field)."),
    ("MCC-EB-001", re.compile(r"Reproducibility Requirements"), "PARTIAL", EV_EVIDENCE_BUNDLE,
     "schema.py explicitly documents and excludes non-deterministic fields (created_at, bundle_id) from "
     "equivalence comparison — the same determinism-with-declared-exceptions model this section requires — "
     "but for the mcc-evidence/1 schema, not this specification's Bundle."),
    ("MCC-EB-001", re.compile(r"Validation Rules"), "PARTIAL", EV_EVIDENCE_BUNDLE,
     "verify_bundle implements fail-closed, ordered validation (structure, integrity, schema, signature) "
     "and never treats a partial result as valid, directly analogous to this section's requirements."),
    ("MCC-EB-001", re.compile(r"Versioning Rules|Compatibility Requirements"), "PARTIAL", EV_EVIDENCE_BUNDLE,
     "BUNDLE_SCHEMA_VERSION / SUPPORTED_SCHEMA_VERSIONS and the UNSUPPORTED_SCHEMA verification outcome "
     "implement the same reject-unrecognized-schema-version model this section requires."),
    ("MCC-EB-001", re.compile(r"Security Considerations"), "PARTIAL", EV_EVIDENCE_BUNDLE,
     "verify_bundle assumes an untrusted source, never treats content as authoritative before integrity "
     "verification, and verifies Ed25519 signatures against supplied trusted keys — the same threat model."),
    ("MCC-EB-001", re.compile(r"Conformance Requirements"), "GAP", None,
     "No producer/validator conformance-declaration mechanism specific to this specification's Bundle "
     "Schema Version was found."),

    # --- MCC-CM-001 ---
    ("MCC-CM-001", re.compile(r"Certification Manifest Overview|Manifest Schema|Required Fields|Optional Fields"),
     "PARTIAL", EV_COMPLIANCE_MANIFEST,
     "certifications/manifest.json is a real, versioned (MANIFEST_SCHEMA_VERSION), digest-bound, structured "
     "certification record (subject/adapter, contract_version, status, evidence_digest, report_id) — the same "
     "kind of artifact this section describes, but with different field names/shape and scoped to adapters "
     "certified against the Integration Contract, not this specification's Manifest Schema."),
    ("MCC-CM-001", re.compile(r"Hash References"), "PARTIAL", EV_COMPLIANCE_MANIFEST,
     "certifications/manifest.json binds evidence_digest / vector_manifest_digest (sha256, DIGEST_ALGORITHM) "
     "to the certification record, the same binding concept, but as bare digest strings rather than this "
     "section's required identifier+algorithm+content-pointer structured Hash Reference object."),
    ("MCC-CM-001", re.compile(r"Evidence Bundle References"), "GAP", None,
     "certifications/manifest.json references compliance vectors and adapters, not an Evidence Bundle as "
     "MCC-EB-001 defines it; no Evidence-Bundle-Reference-shaped field exists."),
    ("MCC-CM-001", re.compile(r"Certification Metadata"), "PARTIAL", EV_COMPLIANCE_MANIFEST,
     "certifications/manifest.json records subject (adapter/adapter_key), specification version "
     "(contract_version), a Requirement-Result-like list (covered_invariants), and an overall status — the "
     "same metadata categories this section requires, under different names."),
    ("MCC-CM-001", re.compile(r"Versioning Rules|Compatibility Rules"), "PARTIAL", EV_COMPLIANCE_MANIFEST,
     "MANIFEST_SCHEMA_VERSION is tracked independently of contract_version and compliance_suite_version, "
     "the same independent-versioning model this section requires."),
    ("MCC-CM-001", re.compile(r"Validation Rules"), "PARTIAL", EV_COMPLIANCE_MANIFEST,
     "program.py's manifest build/verify path regenerates the manifest and canonically compares it, "
     "detecting tamper/staleness/regression — a real, tested, fail-closed validation mechanism for this "
     "artifact class."),
    ("MCC-CM-001", re.compile(r"Security Considerations"), "PARTIAL", EV_COMPLIANCE_MANIFEST,
     "The certification manifest is digest-bound and contains no secrets/paths by design (see reporting.py "
     "docstring), consistent with this section's requirements."),
    ("MCC-CM-001", re.compile(r"Conformance Requirements"), "GAP", None,
     "No producer/validator conformance-declaration mechanism specific to this specification's Manifest "
     "Schema Version was found."),

    # --- MCC-TC-001 ---
    ("MCC-TC-001", re.compile(r"Certificate Model|Certificate Schema|Certificate Identity"), "PARTIAL", EV_COMPLIANCE_MANIFEST,
     "certifications/manifest.json's CERTIFIED entries are a real, digest-identified (report_id), versioned, "
     "authoritative record of a successful certification outcome — the same concept this section describes, "
     "under a different name and without this specification's specific field structure."),
    ("MCC-TC-001", re.compile(r"^6\. Required Fields$"), "PARTIAL", EV_COMPLIANCE_MANIFEST,
     "Baseline fields (subject/adapter identity, specification/contract version, certification result, "
     "generation timestamp-equivalent) have real analogs in certifications/manifest.json; the Manifest "
     "Reference and Evidence Bundle Reference structured sub-objects this section also requires do not "
     "(see Section 6.5/6.6 rows in this matrix)."),
    ("MCC-TC-001", re.compile(r"Optional Fields"), "GAP", None,
     "No optional-field mechanism for a certification record was found."),
    ("MCC-TC-001", re.compile(r"Subject Identification"), "PARTIAL", EV_COMPLIANCE_MANIFEST,
     "adapter_key / implementation_id in certifications/manifest.json identify exactly one subject per "
     "record, the same one-subject-per-record model this section requires."),
    ("MCC-TC-001", re.compile(r"Certification Result Representation"), "PARTIAL", EV_COMPLIANCE_MANIFEST,
     "status=CERTIFIED is issued only for a fully-passing compliance run (fail-closed: every mandatory "
     "vector must pass, per reporting.py), the same PASS-only issuance model this section requires, though "
     "the verdict vocabulary (CERTIFIED vs. PASS) differs."),
    ("MCC-TC-001", re.compile(r"Issuer Information"), "PARTIAL", EV_TRUST,
     "gateway/trust.py implements a real, tested per-issuer Ed25519 key model (the Issuer/Trust Anchor "
     "concept this section requires), but it is not wired to certifications/manifest.json entries, which "
     "instead carry only an informal issuer statement (CERTIFICATION_NOTE)."),
    ("MCC-TC-001", re.compile(r"Validity Period"), "PARTIAL", EV_TRUST,
     "gateway/trust.py's per-key not_after expiry implements the same validity-period-with-optional-"
     "expiration model this section requires, though for trust/mandate keys, not for a Technical Certificate."),
    ("MCC-TC-001", re.compile(r"Revocation Model"), "PARTIAL", EV_TRUST,
     "gateway/trust.py implements a real, tested REVOKED_KEY status and fail-closed unresolved/revoked-key "
     "handling — the same external-revocation-record, verifier-must-check model this section requires, "
     "scoped to trust/mandate keys rather than a Technical Certificate's own Revocation Record."),
    ("MCC-TC-001", re.compile(r"Cryptographic Integrity"), "PARTIAL", EV_SIGNING,
     "src/mcc_core/signing.py provides the collision-resistant digest primitive this section requires; "
     "src/mcc_evidence/verify.py demonstrates it applied to binding a signed artifact to referenced content, "
     "though not to a Technical Certificate specifically."),
    ("MCC-TC-001", re.compile(r"Signature Requirements"), "PARTIAL", EV_SIGNING,
     "The runtime signs its own authority-bearing artifact (the Decision Token, a different artifact per "
     "Section 3.4) exclusively with Ed25519, with a dedicated repository-wide test confirming no "
     "symmetric-key or shared-secret mechanism is used anywhere in that signing path."),
    ("MCC-TC-001", re.compile(r"Verification Procedure"), "PARTIAL", EV_EVIDENCE_BUNDLE,
     "src/mcc_evidence/verify.py implements an ordered, fail-closed, multi-step verification procedure "
     "(structure, then integrity, then signature, then consistency) procedurally analogous to this section, "
     "for the Governance Evidence Bundle rather than a Technical Certificate."),
    ("MCC-TC-001", re.compile(r"Trust Model"), "PARTIAL", EV_TRUST,
     "gateway/trust.py is a real, tested multi-issuer trust set (per-issuer keys, rotation, expiry, "
     "revocation, fail-closed unresolved-key handling) — the closest and strongest analog to this section "
     "found in the repository, though scoped to mandate/approval trust, not Technical Certificate trust."),
    ("MCC-TC-001", re.compile(r"^17\. Compatibility$|^18\. Versioning$"), "PARTIAL", EV_COMPLIANCE_MANIFEST,
     "Independent schema/contract versioning exists for the compliance-manifest artifact family "
     "(compliance_suite_version, contract_version, MANIFEST_SCHEMA_VERSION), the same independent-tracking "
     "model this section requires."),
    ("MCC-TC-001", re.compile(r"Security Considerations"), "PARTIAL", EV_TRUST,
     "gateway/trust.py assumes an untrusted/unresolved key yields no trust (fail-closed), the same threat "
     "model this section requires for Certificate forgery/tamper resistance."),
    ("MCC-TC-001", re.compile(r"Conformance Requirements"), "GAP", None,
     "No issuer/verifier conformance-declaration mechanism specific to this specification's Certificate "
     "Schema Version was found."),

    # --- MCC-CP-001 ---
    ("MCC-CP-001", re.compile(r"^7\. Certification Model$"), "PARTIAL", EV_COMPLIANCE_RUNNER,
     "src/mcc_compliance implements a real, tested certification model (evaluate an adapter's behavior "
     "against versioned requirements, produce a deterministic result) — the same model this section "
     "describes, scoped to adapters vs. the Integration Contract rather than implementations vs. these four "
     "specifications."),
    ("MCC-CP-001", re.compile(r"^8\. Certification Lifecycle$"), "PARTIAL", EV_COMPLIANCE_RUNNER,
     "run_compliance's registration -> scenario execution -> assessment -> report/manifest generation flow "
     "is procedurally analogous to this section's lifecycle steps, for a differently-scoped certification "
     "target."),
    ("MCC-CP-001", re.compile(r"^9\. Certification Pipeline$"), "PARTIAL", EV_COMPLIANCE_RUNNER,
     "run_compliance executes an ordered, deterministic sequence of stages (structural checks, scenario "
     "execution, evidence generation, assessment, artifact generation) analogous to this section's Pipeline."),
    ("MCC-CP-001", re.compile(r"^10\. Conformance Model$"), "PARTIAL", EV_COMPLIANCE_RUNNER,
     "Each compliance vector produces a real pass/fail-style CaseResult, aggregated into scenarios_passed / "
     "scenarios_failed / scenarios_total, the same evaluated-outcome model this section requires."),
    ("MCC-CP-001", re.compile(r"^11\. Capability Profiles$"), "PARTIAL", EV_CAPABILITY_PROFILE,
     "src/mcc_compliance/capability_profile.py is a real, tested, versioned, fail-closed capability-profile "
     "validator (declared/validated/certified/authorized trust ladder) — a close analog to this section."),
    ("MCC-CP-001", re.compile(r"^12\. Certification Requirements$"), "PARTIAL", EV_COMPLIANCE_RUNNER,
     "The compliance vector manifest (src/mcc_compliance/vectors/v1/manifest.json) gives each requirement-"
     "like vector a stable id, an associated invariant/requirement name, and a verification scenario — the "
     "same requirement-identity model this section requires."),
    ("MCC-CP-001", re.compile(r"^13\. Requirement Classification$"), "PARTIAL", EV_COMPLIANCE_RUNNER,
     "Each compliance vector carries an explicit boolean `mandatory` flag (src/mcc_compliance/vectors/v1/"
     "manifest.json), the same required-vs-optional classification concept this section requires, though "
     "only a two-way (not three-way REQUIRED/OPTIONAL/CONDITIONAL) split was found."),
    ("MCC-CP-001", re.compile(r"^14\. Evidence Requirements$"), "PARTIAL", EV_EVIDENCE_BUNDLE,
     "src/mcc_evidence implements reproducible, traceable, verifiable, immutable-after-generation evidence "
     "for a governance run, the same evidence-property model this section requires."),
    ("MCC-CP-001", re.compile(r"^15\. Certification Manifest Requirements$"), "PARTIAL", EV_COMPLIANCE_MANIFEST,
     "certifications/manifest.json is a real, structured, machine-readable certification-result record, the "
     "same artifact class this section requires, under different field names and scope."),
    ("MCC-CP-001", re.compile(r"^16\. Technical Certificate Requirements$"), "PARTIAL", EV_COMPLIANCE_MANIFEST,
     "certifications/manifest.json's CERTIFIED entries are the closest analog to this section's authoritative "
     "certified-outcome record found in the repository."),
    ("MCC-CP-001", re.compile(r"^17\. Versioning$"), "PARTIAL", EV_COMPLIANCE_MANIFEST,
     "contract_version / compliance_suite_version / MANIFEST_SCHEMA_VERSION are independently tracked, "
     "immutable-once-published identifiers, the same versioning model this section requires."),
    ("MCC-CP-001", re.compile(r"^18\. Security Considerations$"), "PARTIAL", EV_COMPLIANCE_RUNNER,
     "The compliance suite is evidence-based, reproducible, and fail-closed (every mandatory vector must "
     "pass), the same security posture this section requires."),
    ("MCC-CP-001", re.compile(r"^19\. Registry Considerations$"), "PARTIAL", EV_COMPLIANCE_MANIFEST,
     "certifications/manifest.json is itself a real, version-controlled, CI-verified registry of "
     "certification records, the same registry concept this section requires."),
    ("MCC-CP-001", re.compile(r"^20\. Conformance Statement$"), "GAP", None,
     "No mechanism for an implementation to claim conformance specifically to MCC-CP-001 (as opposed to the "
     "Integration Contract) was found."),
    ("MCC-CP-001", re.compile(r"^Appendix A"), "GAP", None,
     "No explicit certification-process state machine (Draft/Submitted/Under Evaluation/.../Archived) "
     "implementation was found; the compliance runner is a single synchronous pass, not a persisted "
     "multi-state record."),
    ("MCC-CP-001", re.compile(r"^Appendix B"), "PARTIAL", EV_COMPLIANCE_MANIFEST,
     "status=CERTIFIED / NOT_CERTIFIED (models.py CertificationStatus) is a real, binary, evidence-derived "
     "decision outcome, the same decision-matrix concept this appendix requires."),
    ("MCC-CP-001", re.compile(r"^Appendix C"), "PARTIAL", EV_COMPLIANCE_RUNNER,
     "The compliance vector manifest's stable per-vector ids (IC-V1-*) are a real, versioned, immutable "
     "requirement-identifier registry, the same concept this appendix requires, for a differently-scoped "
     "requirement set."),
    ("MCC-CP-001", re.compile(r"^Appendix G"), "PARTIAL", EV_COMPLIANCE_RUNNER,
     "scenarios_passed / scenarios_failed / scenarios_total in certifications/manifest.json is a real, "
     "reproducible Conformance-Result-equivalent, carried within the certification manifest rather than as "
     "a separate artifact, matching this appendix's own \"not a separate artifact\" model."),
    ("MCC-CP-001", re.compile(r"^Appendix H"), "PARTIAL", EV_REPORTING,
     "src/mcc_compliance/reporting.py generates a real, deterministic, human-readable Markdown report "
     "(secret-free, non-authoritative relative to the manifest, with an explicit certification-scope "
     "disclaimer) — closely matching this appendix's required content and properties."),
]


# ---------------------------------------------------------------------------
# Wave A (PR #63) per-requirement CONFORMANT overrides.
#
# Deliberately requirement-ID scoped, NOT category-scoped like RULES above.
# EB-STR-*/EB-FILE-*/CM-HASH-* share categories ("10. Bundle Directory
# Structure", "11. Required Files", "13. Hash References") with other
# requirements Wave A did NOT select: near-duplicate derived prose
# (e.g. MCC-EB-001-11-REQUIRED-FILES-D01..08) and CM-HASH-003 ("Every
# Evidence Bundle Reference MUST include at least one Hash Reference"),
# which is an obligation on the Evidence Bundle Reference object MCC-CM-001
# Section 14 defines and Wave B has not yet built. A category-level RULES
# change would silently promote or otherwise disturb all of those too; this
# table promotes only the exact 13 requirement IDs Wave A implemented,
# tested, and evidenced, leaving every other member of these categories at
# its pre-existing status untouched. See
# conformance/normative-v1.0/remediation/wave-a-evidence-bundle-scope-manifest.md
# for the full selection/exclusion rationale and
# conformance/normative-v1.0/remediation/wave-a-evidence.json for the
# deterministic evidence record backing each entry below.
_WAVE_A_EVIDENCE = ["conformance/normative-v1.0/remediation/wave-a-evidence.json"]

# Wave B (PR #64) adds CM-EBREF-001..004 and CM-HASH-003 to this same
# requirement-ID-scoped mechanism -- see the block below this table for the
# rationale specific to those five IDs.
_WAVE_B_EVIDENCE = ["conformance/normative-v1.0/remediation/wave-b-evidence.json"]

# Wave C (PR #65) adds 73 MCC-TC-001 Technical Certificate requirement IDs.
# See conformance/normative-v1.0/remediation/wave-c-technical-certificate-scope-manifest.md
# for the full selection/exclusion rationale (including the 7 genuinely
# excluded IDs: TC-SUBJ-002/003, TC-RES-002 -- Wave B's minimal CM001Manifest
# carries no Certification Metadata (subject/result) to cross-check against
# -- and TC-EXT-001..004, which fall through to the pre-existing repository-
# wide "Extension Model" RULES entry unchanged, since no extension-
# declaration mechanism exists anywhere in this repository yet).
_WAVE_C_EVIDENCE = ["conformance/normative-v1.0/remediation/wave-c-evidence.json"]

IDOverride = Tuple[str, Tuple[List[str], List[str]], List[str], str]

ID_OVERRIDES: Dict[str, IDOverride] = {
    "EB-STR-001": (
        "CONFORMANT", EV_EB001_BUNDLE, _WAVE_A_EVIDENCE,
        "Wave A (PR #63): build_eb001_bundle produces exactly one Bundle Root per "
        "generation (directory or archive); verify_eb001_bundle's root_structure check "
        "confirms it. Directly tested by "
        "test_produces_and_verifies_a_valid_eb001_bundle_directory_form and "
        "test_eb_str_002_bundle_root_contains_exactly_the_required_entries; deterministic "
        "evidence recorded under EB-STR-001 in wave-a-evidence.json.",
    ),
    "EB-STR-002": (
        "CONFORMANT", EV_EB001_BUNDLE, _WAVE_A_EVIDENCE,
        "Wave A (PR #63): the Bundle Root contains exactly one Bundle Descriptor, "
        "Integrity Record, Provenance Record, and Evidence Directory by construction; "
        "verify_eb001_bundle's root_structure check rejects any bundle missing one or "
        "duplicating one. Directly tested by "
        "test_eb_str_002_bundle_root_contains_exactly_the_required_entries, "
        "test_eb_file_005_missing_required_root_artifact_is_rejected, and "
        "test_duplicate_singleton_root_artifact_is_rejected.",
    ),
    "EB-STR-003": (
        "CONFORMANT", EV_EB001_BUNDLE, _WAVE_A_EVIDENCE,
        "Wave A (PR #63): build_eb001_bundle is a pure function of its input (no "
        "wall-clock timestamp, random ID, or unordered collection) -- two independent "
        "generations from equivalent input produce byte-identical directory structure. "
        "Directly tested by test_eb_str_003_004_deterministic_regeneration_produces_identical_files "
        "and test_repeated_generation_is_deterministic.",
    ),
    "EB-STR-004": (
        "CONFORMANT", EV_EB001_BUNDLE, _WAVE_A_EVIDENCE,
        "Wave A (PR #63): file and directory names are fixed constants "
        "(BUNDLE_DESCRIPTOR_NAME / INTEGRITY_RECORD_NAME / PROVENANCE_RECORD_NAME / "
        "EVIDENCE_DIR_NAME), never derived from wall-clock time or randomness, so naming "
        "is stable across regeneration of equivalent input. Same tests as EB-STR-003.",
    ),
    "EB-STR-005": (
        "CONFORMANT", EV_EB001_BUNDLE, _WAVE_A_EVIDENCE,
        "Wave A (PR #63): build_eb001_bundle derives both the directory form and the "
        ".tar.gz archive form from the identical in-memory {path: bytes} file set "
        "(build_bundle_files), so they are structurally equivalent by construction. "
        "Directly tested by test_eb_str_005_directory_and_archive_forms_are_structurally_equivalent.",
    ),
    "EB-FILE-001": (
        "CONFORMANT", EV_EB001_BUNDLE, _WAVE_A_EVIDENCE,
        "Wave A (PR #63): the Bundle Descriptor is always written at the Bundle Root and "
        "declares the Schema Version, Bundle identifier, and MCC-CP-001 specification "
        "version (Section 11.1); its absence is rejected by verify_eb001_bundle. Directly "
        "tested by test_eb_file_001_bundle_descriptor_present_and_declares_required_fields "
        "and the parametrized test_eb_file_005_missing_required_root_artifact_is_rejected.",
    ),
    "EB-FILE-002": (
        "CONFORMANT", EV_EB001_BUNDLE, _WAVE_A_EVIDENCE,
        "Wave A (PR #63): the Integrity Record is always written at the Bundle Root; its "
        "absence is rejected by verify_eb001_bundle. Directly tested by "
        "test_eb_file_002_integrity_record_present and the parametrized "
        "test_eb_file_005_missing_required_root_artifact_is_rejected.",
    ),
    "EB-FILE-003": (
        "CONFORMANT", EV_EB001_BUNDLE, _WAVE_A_EVIDENCE,
        "Wave A (PR #63): the Provenance Record is always written at the Bundle Root and "
        "declares the certification run and specification version that produced the "
        "Bundle; its absence is rejected by verify_eb001_bundle. Directly tested by "
        "test_eb_file_003_provenance_record_present_and_declares_origin and the "
        "parametrized test_eb_file_005_missing_required_root_artifact_is_rejected.",
    ),
    "EB-FILE-004": (
        "CONFORMANT", EV_EB001_BUNDLE, _WAVE_A_EVIDENCE,
        "Wave A (PR #63): the Integrity Record enumerates a Hash Reference for every file "
        "other than itself; verify_eb001_bundle's integrity_enumeration_completeness check "
        "rejects both an unenumerated actual file and an enumerated-but-absent file. "
        "Directly tested by test_eb_file_004_every_non_integrity_record_file_is_enumerated, "
        "test_eb_file_004_unenumerated_file_is_rejected, and "
        "test_eb_file_004_missing_enumerated_file_is_rejected.",
    ),
    "EB-FILE-005": (
        "CONFORMANT", EV_EB001_BUNDLE, _WAVE_A_EVIDENCE,
        "Wave A (PR #63): build_eb001_bundle never omits a required root artifact or the "
        "Evidence Directory regardless of whether Evidence Items are present (an empty "
        "certification outcome still yields all required structure); verify_eb001_bundle "
        "rejects any bundle a required artifact was removed from post-generation. Directly "
        "tested by test_missing_evidence_directory_is_rejected and the parametrized "
        "test_eb_file_005_missing_required_root_artifact_is_rejected.",
    ),
    "CM-HASH-001": (
        "CONFORMANT", EV_HASH_REFERENCE, _WAVE_A_EVIDENCE,
        "Wave A (PR #63): HashReference is a structured object identifying a Digest, a "
        "hash algorithm, and the content it corresponds to (content_ref); "
        "HashReference.from_dict fails closed on any missing/malformed field. Directly "
        "tested by test_cm_hash_001_structure_identifies_digest_algorithm_and_content, "
        "test_cm_hash_001_round_trips_through_to_dict_from_dict, and the "
        "from_dict rejection tests.",
    ),
    "CM-HASH-002": (
        "CONFORMANT", EV_HASH_REFERENCE, _WAVE_A_EVIDENCE,
        "Wave A (PR #63): SUPPORTED_HASH_ALGORITHMS is the closed set {\"sha256\"}; "
        "compute_hash_reference refuses to construct a reference with any other algorithm, "
        "and HashReference.validate()/verify_hash_reference reject one at verification time "
        "too -- a non-collision-resistant algorithm is never accepted, only rejected. "
        "Directly tested by test_cm_hash_002_* (compute refusal, validate rejection, "
        "verify fail-closed) and test_unsupported_hash_algorithm_is_rejected.",
    ),
    "CM-HASH-004": (
        "CONFORMANT", EV_HASH_REFERENCE, _WAVE_A_EVIDENCE,
        "Wave A (PR #63): verify_hash_reference independently recomputes the digest of "
        "supplied data and compares it to the declared value -- it never trusts a prior "
        "verification result. Directly tested by "
        "test_cm_hash_004_verify_succeeds_for_matching_content, "
        "test_cm_hash_004_verify_fails_for_mismatched_content, and the malformed-digest / "
        "wrong-length fail-closed tests.",
    ),
    # --- Wave B (PR #64): CM-EBREF-001..004 + CM-HASH-003 -------------------- #
    # Same discipline as Wave A: requirement-ID scoped, not category-scoped.
    # "14. Evidence Bundle References" also contains near-duplicate derived
    # prose (MCC-CM-001-14-EVIDENCE-BUNDLE-REFERENCES-D01..05) that Wave B did
    # NOT select and leaves at GAP, unchanged. CM-HASH-003 previously fell
    # through to the category-level "Hash References" RULES entry (PARTIAL,
    # via the pre-existing Integration-Contract-scoped EV_COMPLIANCE_MANIFEST
    # citation); it is now provable because the Evidence Bundle Reference
    # object it depends on exists.
    "CM-EBREF-001": (
        "CONFORMANT", EV_CM001_MANIFEST, _WAVE_B_EVIDENCE,
        "Wave B (PR #64): CM001Manifest.primary_evidence_bundle_reference is a single, "
        "required field (not a list) -- build_cm001_manifest and CM001Manifest.from_dict "
        "both fail closed if no primary reference is supplied. Directly tested by "
        "test_cm_ebref_001_manifest_has_exactly_one_primary_reference and "
        "test_cm_ebref_001_manifest_from_dict_requires_a_primary_reference.",
    ),
    "CM-EBREF-002": (
        "CONFORMANT", EV_CM001_MANIFEST, _WAVE_B_EVIDENCE,
        "Wave B (PR #64): build_evidence_bundle_reference reads the Evidence Bundle "
        "identifier and Schema Version from the referenced Bundle's own Bundle Descriptor "
        "and computes a Hash Reference binding to its Integrity Record; "
        "EvidenceBundleReference.from_dict fails closed if any of the three is missing. "
        "Directly tested by test_cm_ebref_002_valid_evidence_bundle_reference_creation, "
        "test_cm_ebref_002_reference_carries_correct_bundle_id, "
        "test_cm_ebref_002_reference_carries_correct_schema_version, "
        "test_cm_ebref_002_missing_bundle_id_rejected, and "
        "test_cm_ebref_002_missing_schema_version_rejected.",
    ),
    "CM-EBREF-003": (
        "CONFORMANT", EV_CM001_MANIFEST, _WAVE_B_EVIDENCE,
        "Wave B (PR #64): build_cm001_manifest's _validate_distinguishable rejects, before "
        "any write, a supplementary Evidence Bundle Reference sharing the primary "
        "reference's bundle_id, and rejects duplicate supplementary references. Directly "
        "tested by test_cm_ebref_003_supplementary_reference_distinguishable_from_primary, "
        "test_cm_ebref_003_indistinguishable_supplementary_reference_rejected, and "
        "test_cm_ebref_003_duplicate_supplementary_references_rejected.",
    ),
    "CM-EBREF-004": (
        "CONFORMANT", EV_CM001_MANIFEST, _WAVE_B_EVIDENCE,
        "Wave B (PR #64): verify_cm001_manifest returns INVALID for the whole Manifest the "
        "moment the primary Evidence Bundle Reference fails verification (wrong bundle_id, "
        "wrong schema_version, or a Hash Reference that does not recompute against the "
        "actual Integrity Record) -- regardless of any supplementary references. Directly "
        "tested by test_cm_ebref_004_manifest_invalidated_when_primary_unverifiable, "
        "test_cm_ebref_004_incorrect_bundle_id_rejected, and "
        "test_cm_ebref_004_incorrect_schema_version_rejected.",
    ),
    "CM-HASH-003": (
        "CONFORMANT", EV_CM001_MANIFEST, _WAVE_B_EVIDENCE,
        "Wave B (PR #64): EvidenceBundleReference.hash_references is a non-empty tuple by "
        "construction (build_evidence_bundle_reference always computes at least one) and "
        "EvidenceBundleReference.from_dict fails closed on a zero-length hash_references "
        "array. Directly tested by test_cm_hash_003_at_least_one_hash_reference_present, "
        "test_cm_hash_003_from_dict_rejects_zero_hash_references, and "
        "test_cm_hash_003_missing_hash_reference_field_rejected.",
    ),
    # --- Wave C (PR #65): MCC-TC-001 Technical Certificate (73 IDs) ---------- #
    # Requirement-ID scoped, not category-scoped, exactly like Waves A/B.
    # TC-SUBJ-002/003, TC-RES-002 (Manifest-side Subject/Result cross-check)
    # and TC-EXT-001..004 (Extension Model) are deliberately NOT here -- see
    # the Wave C scope manifest for why each is a genuine, documented
    # exclusion rather than an oversight. TC-RID-001..004 remain untouched
    # NOT_APPLICABLE, consistent with EB-RID/CM-RID in Waves A/B.
    "TC-MODEL-001": (
        "CONFORMANT", EV_TC001_CERTIFICATE, _WAVE_C_EVIDENCE,
        "Wave C (PR #65): build_technical_certificate has no certification_result "
        "parameter at all -- CertificationResult has only a PASS member, so a FAIL "
        "Certificate cannot be constructed. Directly tested by "
        "test_tc_model_001_certificate_represents_exactly_one_pass_outcome and "
        "test_tc_conf_002_issuer_never_issues_for_a_non_pass_result.",
    ),
    "TC-MODEL-002": (
        "CONFORMANT", EV_TC001_CERTIFICATE, _WAVE_C_EVIDENCE,
        "Wave C (PR #65): TechnicalCertificate.manifest_reference is a single required "
        "field, not a collection. Directly tested by "
        "test_tc_model_002_certificate_references_exactly_one_manifest.",
    ),
    "TC-MODEL-003": (
        "CONFORMANT", EV_TC001_CERTIFICATE, _WAVE_C_EVIDENCE,
        "Wave C (PR #65): tc001_certificate.py imports nothing from mcc_core.gate / "
        "mcc_core.authority / gateway, and the Certificate schema has no verdict/decision "
        "field -- only certification_result (PASS-only). Directly tested by "
        "test_tc_model_003_certificate_is_not_a_runtime_execution_authorization and "
        "test_tc_sec_005_valid_certificate_not_treated_as_runtime_execution_authorization.",
    ),
    "TC-MODEL-004": (
        "CONFORMANT", EV_TC001_CERTIFICATE, _WAVE_C_EVIDENCE,
        "Wave C (PR #65): every issued Certificate carries subject_id, "
        "cp001_specification_version, manifest_reference, and evidence_bundle_reference as "
        "direct fields. Directly tested by "
        "test_tc_model_004_certificate_traceable_to_subject_spec_manifest_bundle.",
    ),
    "TC-SCHEMA-001": (
        "CONFORMANT", EV_TC001_CERTIFICATE, _WAVE_C_EVIDENCE,
        "Wave C (PR #65): write_tc001_certificate writes exactly one JSON document; "
        "read_tc001_certificate parses it back. Directly tested by "
        "test_tc_schema_001_certificate_is_a_single_structured_document.",
    ),
    "TC-SCHEMA-002": (
        "CONFORMANT", EV_TC001_CERTIFICATE, _WAVE_C_EVIDENCE,
        "Wave C (PR #65): TechnicalCertificate.from_dict enforces an explicit type for "
        "every field (str/int/list/dict), rejecting ambiguous or wrong-typed values. "
        "Directly tested by test_tc_schema_002_every_field_has_an_unambiguous_type and "
        "test_tc_optf_002_optional_fields_conform_to_type_rules_when_present.",
    ),
    "TC-SCHEMA-003": (
        "CONFORMANT", EV_TC001_CERTIFICATE, _WAVE_C_EVIDENCE,
        "Wave C (PR #65): every top-level field group from Section 4.2 is present on a "
        "signed Certificate except the correctly-absent optional ones. Directly tested by "
        "test_tc_schema_003_top_level_groups_all_present_except_optional.",
    ),
    "TC-SCHEMA-004": (
        "CONFORMANT", EV_TC001_CERTIFICATE, _WAVE_C_EVIDENCE,
        "Wave C (PR #65): TechnicalCertificate.unsigned_dict() is the exact Canonical Form "
        "input to signing and excludes kid/sig. Directly tested by "
        "test_tc_schema_004_signing_canonical_form_excludes_signature_field.",
    ),
    "TC-SCHEMA-005": (
        "CONFORMANT", EV_TC001_CERTIFICATE, _WAVE_C_EVIDENCE,
        "Wave C (PR #65): to_dict()/from_dict() round-trip independent of any file writer "
        "or transport. Directly tested by "
        "test_tc_schema_005_schema_independent_of_serialization_technology.",
    ),
    "TC-ID-001": (
        "CONFORMANT", EV_TC001_CERTIFICATE, _WAVE_C_EVIDENCE,
        "Wave C (PR #65): every Certificate carries a required, non-empty certificate_id. "
        "Directly tested by test_tc_id_001_certificate_has_a_unique_identifier. Global "
        "uniqueness across independent Issuers is a documented, out-of-scope deployment "
        "concern (see CertificateIdRegistry's docstring).",
    ),
    "TC-ID-002": (
        "CONFORMANT", EV_TC001_CERTIFICATE, _WAVE_C_EVIDENCE,
        "Wave C (PR #65): CertificateIdRegistry.reserve fails closed on a reused "
        "certificate_id. Directly tested by "
        "test_tc_id_002_identifier_reuse_is_rejected_including_after_revocation and "
        "test_scenario_19_reused_certificate_id_rejected.",
    ),
    "TC-ID-003": (
        "CONFORMANT", EV_TC001_CERTIFICATE, _WAVE_C_EVIDENCE,
        "Wave C (PR #65): a revalidation is built as a distinct Certificate with a new "
        "certificate_id (optionally declaring superseded_certificate_ids); there is no "
        "in-place re-issuance entrypoint. Directly tested by "
        "test_tc_id_003_revalidation_produces_a_new_certificate_with_a_new_id.",
    ),
    "TC-RFLD-001": (
        "CONFORMANT", EV_TC001_CERTIFICATE, _WAVE_C_EVIDENCE,
        "Wave C (PR #65): all Section 6.2 baseline fields are present on every issued "
        "Certificate. Directly tested by test_tc_rfld_001_baseline_required_fields_present.",
    ),
    "TC-RFLD-002": (
        "CONFORMANT", EV_TC001_CERTIFICATE, _WAVE_C_EVIDENCE,
        "Wave C (PR #65): issuer_id, issuance_timestamp, and a Signature (kid+sig) are "
        "always present on a signed Certificate. Directly tested by "
        "test_tc_rfld_002_issuer_validity_and_signature_present.",
    ),
    "TC-RFLD-003": (
        "CONFORMANT", EV_TC001_CERTIFICATE, _WAVE_C_EVIDENCE,
        "Wave C (PR #65): TechnicalCertificate.from_dict raises TC001StructuralError on any "
        "missing Required Field. Directly tested by "
        "test_tc_rfld_003_certificate_omitting_a_required_field_is_rejected and "
        "test_scenario_01_missing_required_field_rejected.",
    ),
    "TC-RFLD-004": (
        "CONFORMANT", EV_TC001_CERTIFICATE, _WAVE_C_EVIDENCE,
        "Wave C (PR #65): ManifestReference carries manifest_id, manifest_schema_version, "
        "and a Hash Reference. Directly tested by "
        "test_tc_rfld_004_manifest_reference_structure.",
    ),
    "TC-RFLD-005": (
        "CONFORMANT", EV_TC001_CERTIFICATE, _WAVE_C_EVIDENCE,
        "Wave C (PR #65): CertEvidenceBundleReference carries bundle_id, schema_version, "
        "and a Hash Reference. Directly tested by "
        "test_tc_rfld_005_evidence_bundle_reference_structure.",
    ),
    "TC-RFLD-006": (
        "CONFORMANT", EV_TC001_CERTIFICATE, _WAVE_C_EVIDENCE,
        "Wave C (PR #65): evidence_bundle_reference is a direct top-level Certificate "
        "field, never resolved only through manifest_reference. Directly tested by "
        "test_tc_rfld_006_evidence_bundle_reference_is_direct_not_transitive_only.",
    ),
    "TC-OPTF-001": (
        "CONFORMANT", EV_TC001_CERTIFICATE, _WAVE_C_EVIDENCE,
        "Wave C (PR #65): label, expiration_timestamp, and superseded_certificate_ids are "
        "all optional and a Certificate omitting them still verifies VALID. Directly tested "
        "by test_tc_optf_001_optional_fields_may_be_omitted.",
    ),
    "TC-OPTF-002": (
        "CONFORMANT", EV_TC001_CERTIFICATE, _WAVE_C_EVIDENCE,
        "Wave C (PR #65): from_dict enforces the declared type for every present optional "
        "field. Directly tested by "
        "test_tc_optf_002_optional_fields_conform_to_type_rules_when_present.",
    ),
    "TC-OPTF-003": (
        "CONFORMANT", EV_TC001_CERTIFICATE, _WAVE_C_EVIDENCE,
        "Wave C (PR #65): populating every optional field never substitutes for a missing "
        "Required Field -- structural verification still independently requires each one. "
        "Directly tested by "
        "test_tc_optf_003_optional_fields_do_not_satisfy_required_field_obligations.",
    ),
    "TC-SUBJ-001": (
        "CONFORMANT", EV_TC001_CERTIFICATE, _WAVE_C_EVIDENCE,
        "Wave C (PR #65): subject_id is a single required non-empty string field -- a "
        "Certificate cannot declare more than one Subject. Directly tested by "
        "test_tc_subj_001_certificate_identifies_exactly_one_subject. TC-SUBJ-002/003 "
        "(Manifest-side Subject cross-check) are explicitly excluded -- see the Wave C "
        "scope manifest.",
    ),
    "TC-RES-001": (
        "CONFORMANT", EV_TC001_CERTIFICATE, _WAVE_C_EVIDENCE,
        "Wave C (PR #65): certification_result is required and from_dict rejects any value "
        "other than \"PASS\". Directly tested by test_tc_res_001_result_field_present_and_pass, "
        "test_tc_res_001_negative_result_field_rejects_non_pass, and "
        "test_scenario_03_non_pass_result_rejected. TC-RES-002 (Manifest-side result "
        "cross-check) is explicitly excluded -- see the Wave C scope manifest.",
    ),
    "TC-RES-003": (
        "CONFORMANT", EV_TC001_CERTIFICATE, _WAVE_C_EVIDENCE,
        "Wave C (PR #65): certified_capability_profiles records exactly the caller-supplied "
        "profiles -- the producer never adds an unverified profile. Directly tested by "
        "test_tc_res_003_certified_profiles_limited_to_those_verified.",
    ),
    "TC-ISS-001": (
        "CONFORMANT", EV_TC001_CERTIFICATE, _WAVE_C_EVIDENCE,
        "Wave C (PR #65): issuer_id is a required field on every Certificate. Directly "
        "tested by test_tc_iss_001_certificate_identifies_its_issuer.",
    ),
    "TC-ISS-002": (
        "CONFORMANT", EV_TC001_CERTIFICATE, _WAVE_C_EVIDENCE,
        "Wave C (PR #65): TrustAnchorRegistry.resolve maps the signing kid to a TrustAnchor "
        "carrying an issuer_id. Directly tested by "
        "test_tc_iss_002_issuer_identifier_associated_with_resolvable_trust_anchor.",
    ),
    "TC-ISS-003": (
        "CONFORMANT", EV_TC001_CERTIFICATE, _WAVE_C_EVIDENCE,
        "Wave C (PR #65): verify_technical_certificate rejects a Certificate whose kid does "
        "not resolve in the supplied TrustAnchorRegistry. Directly tested by "
        "test_tc_iss_003_unrecognized_issuer_causes_verification_failure and "
        "test_scenario_12_unknown_signing_kid_rejected.",
    ),
    "TC-VALID-001": (
        "CONFORMANT", EV_TC001_CERTIFICATE, _WAVE_C_EVIDENCE,
        "Wave C (PR #65): issuance_timestamp is a required integer field on every "
        "Certificate. Directly tested by test_tc_valid_001_issuance_timestamp_recorded.",
    ),
    "TC-VALID-002": (
        "CONFORMANT", EV_TC001_CERTIFICATE, _WAVE_C_EVIDENCE,
        "Wave C (PR #65): verify_technical_certificate's validity_period check rejects "
        "``now < issuance_timestamp``. Directly tested by "
        "test_tc_valid_002_not_valid_before_issuance and "
        "test_scenario_17_not_yet_valid_certificate_rejected.",
    ),
    "TC-VALID-003": (
        "CONFORMANT", EV_TC001_CERTIFICATE, _WAVE_C_EVIDENCE,
        "Wave C (PR #65): the validity_period check rejects ``now > expiration_timestamp`` "
        "when declared. Directly tested by "
        "test_tc_valid_003_expired_certificate_not_treated_as_valid and "
        "test_scenario_16_expired_certificate_rejected.",
    ),
    "TC-VALID-004": (
        "CONFORMANT", EV_TC001_CERTIFICATE, _WAVE_C_EVIDENCE,
        "Wave C (PR #65): a Certificate with no expiration_timestamp remains valid "
        "indefinitely (absent revocation). Directly tested by "
        "test_tc_valid_004_absence_of_expiration_is_not_a_failure.",
    ),
    "TC-REV-001": (
        "CONFORMANT", EV_TC001_CERTIFICATE, _WAVE_C_EVIDENCE,
        "Wave C (PR #65): revoke_certificate never mutates the Certificate object; its "
        "to_dict() is byte-identical before and after revocation. Directly tested by "
        "test_tc_rev_001_certificate_content_never_mutated_to_represent_revocation.",
    ),
    "TC-REV-002": (
        "CONFORMANT", EV_TC001_CERTIFICATE, _WAVE_C_EVIDENCE,
        "Wave C (PR #65): revocation is represented exclusively by an external "
        "RevocationRecord in a RevocationRegistry, never by editing the Certificate. "
        "Directly tested by test_tc_rev_002_revocation_represented_by_an_external_record.",
    ),
    "TC-REV-003": (
        "CONFORMANT", EV_TC001_CERTIFICATE, _WAVE_C_EVIDENCE,
        "Wave C (PR #65): RevocationRecord requires certificate_id, revoked_at, and "
        "issuer_id (reason optional). Directly tested by "
        "test_tc_rev_003_revocation_record_identifies_required_fields.",
    ),
    "TC-REV-004": (
        "CONFORMANT", EV_TC001_CERTIFICATE, _WAVE_C_EVIDENCE,
        "Wave C (PR #65): RevocationRegistry.revoke refuses a record whose issuer_id does "
        "not match the authorizing TrustAnchor's issuer_id. Directly tested by "
        "test_tc_rev_004_only_the_issuer_may_produce_a_valid_revocation and "
        "test_scenario_21_revoke_with_mismatched_issuer_rejected.",
    ),
    "TC-REV-005": (
        "CONFORMANT", EV_TC001_CERTIFICATE, _WAVE_C_EVIDENCE,
        "Wave C (PR #65): verify_technical_certificate always checks the "
        "RevocationRegistry before returning VALID. Directly tested by "
        "test_tc_rev_005_verifier_checks_revocation_before_treating_as_valid and "
        "test_scenario_18_revoked_certificate_rejected.",
    ),
    "TC-REV-006": (
        "CONFORMANT", EV_TC001_CERTIFICATE, _WAVE_C_EVIDENCE,
        "Wave C (PR #65): RevocationRegistry.get/is_revoked are plain, non-destructive "
        "lookups, and a revoked Certificate remains fully parseable. Directly tested by "
        "test_tc_rev_006_revoked_certificates_remain_available_for_audit.",
    ),
    "TC-HASH-001": (
        "CONFORMANT", EV_TC001_CERTIFICATE, _WAVE_C_EVIDENCE,
        "Wave C (PR #65): both Manifest Reference and Evidence Bundle Reference Hash "
        "References use algorithm=\"sha256\", reusing hash_reference.py's closed, "
        "collision-resistant algorithm set unchanged. Directly tested by "
        "test_tc_hash_001_manifest_and_bundle_hash_references_use_sha256.",
    ),
    "TC-HASH-002": (
        "CONFORMANT", EV_TC001_CERTIFICATE, _WAVE_C_EVIDENCE,
        "Wave C (PR #65): verify_technical_certificate independently recomputes both "
        "bindings (manifest_reference_verification, evidence_bundle_reference_consistency) "
        "rather than trusting a stored flag. Directly tested by "
        "test_tc_hash_002_bindings_are_independently_recomputable.",
    ),
    "TC-HASH-003": (
        "CONFORMANT", EV_TC001_CERTIFICATE, _WAVE_C_EVIDENCE,
        "Wave C (PR #65): the Certificate schema has no separate self-digest field -- "
        "whole-Certificate integrity is provided only by the Signature. Directly tested by "
        "test_tc_hash_003_whole_certificate_integrity_via_signature_not_a_self_digest.",
    ),
    "TC-SIG-001": (
        "CONFORMANT", EV_TC001_CERTIFICATE, _WAVE_C_EVIDENCE,
        "Wave C (PR #65): sign_technical_certificate signs exclusively via "
        "mcc_core.signing.SigningKey (Ed25519, asymmetric). Directly tested by "
        "test_tc_sig_001_certificate_signed_with_asymmetric_scheme.",
    ),
    "TC-SIG-002": (
        "CONFORMANT", EV_TC001_CERTIFICATE, _WAVE_C_EVIDENCE,
        "Wave C (PR #65): tc001_certificate.py imports no symmetric-key/shared-secret "
        "signing module -- Ed25519 via mcc_core.signing is the only signing path. "
        "Directly tested by test_tc_sig_002_symmetric_key_mechanisms_never_used.",
    ),
    "TC-SIG-003": (
        "CONFORMANT", EV_TC001_CERTIFICATE, _WAVE_C_EVIDENCE,
        "Wave C (PR #65): the signature covers unsigned_dict() (the complete Canonical "
        "Form excluding kid/sig); modifying any covered field invalidates verification. "
        "Directly tested by "
        "test_tc_sig_003_signature_covers_complete_canonical_form_excluding_itself.",
    ),
    "TC-SIG-004": (
        "CONFORMANT", EV_TC001_CERTIFICATE, _WAVE_C_EVIDENCE,
        "Wave C (PR #65): every Certificate declares signature_algorithm (\"Ed25519\") and "
        "issuer_id alongside the signing kid. Directly tested by "
        "test_tc_sig_004_certificate_declares_algorithm_and_issuer_identity.",
    ),
    "TC-SIG-005": (
        "CONFORMANT", EV_TC001_CERTIFICATE, _WAVE_C_EVIDENCE,
        "Wave C (PR #65): modifying certificate_id, issuance_timestamp, or "
        "certified_capability_profiles post-signing each independently invalidates the "
        "signature. Directly tested by "
        "test_tc_sig_005_modification_of_any_signed_field_invalidates_signature and "
        "test_scenario_13_forged_signature_rejected.",
    ),
    "TC-VERIFY-001": (
        "CONFORMANT", EV_TC001_CERTIFICATE, _WAVE_C_EVIDENCE,
        "Wave C (PR #65): verify_technical_certificate never returns a partial-pass "
        "status -- only VALID, INVALID, or UNSUPPORTED_SCHEMA. Directly tested by "
        "test_tc_verify_001_verification_is_fail_closed.",
    ),
    "TC-VERIFY-002": (
        "CONFORMANT", EV_TC001_CERTIFICATE, _WAVE_C_EVIDENCE,
        "Wave C (PR #65): structural verification runs first and a structurally-invalid "
        "Certificate never reaches signature verification. Directly tested by "
        "test_tc_verify_002_structural_verification_precedes_everything_else.",
    ),
    "TC-VERIFY-003": (
        "CONFORMANT", EV_TC001_CERTIFICATE, _WAVE_C_EVIDENCE,
        "Wave C (PR #65): signature verification resolves the signing kid through the "
        "supplied TrustAnchorRegistry, never trusting an unresolved key. Directly tested "
        "by test_tc_verify_003_signature_verified_against_a_trust_anchor.",
    ),
    "TC-VERIFY-004": (
        "CONFORMANT", EV_TC001_CERTIFICATE, _WAVE_C_EVIDENCE,
        "Wave C (PR #65): validity_period and revocation_check are each independently "
        "evaluated and recorded as distinct checks. Directly tested by "
        "test_tc_verify_004_validity_and_revocation_both_checked.",
    ),
    "TC-VERIFY-005": (
        "CONFORMANT", EV_TC001_CERTIFICATE, _WAVE_C_EVIDENCE,
        "Wave C (PR #65): any single failing check (e.g. an invalid signature) yields "
        "overall_status=INVALID for the whole Certificate. Directly tested by "
        "test_tc_verify_005_any_failing_step_rejects_the_whole_certificate.",
    ),
    "TC-VERIFY-006": (
        "CONFORMANT", EV_TC001_CERTIFICATE, _WAVE_C_EVIDENCE,
        "Wave C (PR #65): evidence_bundle_reference_consistency explicitly rejects a "
        "Certificate whose direct Evidence Bundle Reference identifies a different Bundle "
        "than the referenced Manifest's own primary reference. Directly tested by "
        "test_tc_verify_006_mismatched_direct_and_manifest_evidence_bundle_references_rejected "
        "and test_scenario_10_verifier_rejects_mismatched_direct_and_manifest_bundle_references.",
    ),
    "TC-TRUST-001": (
        "CONFORMANT", EV_TC001_CERTIFICATE, _WAVE_C_EVIDENCE,
        "Wave C (PR #65): TrustAnchorRegistry.resolve returns None for any kid outside its "
        "own recognized set -- an empty registry trusts nothing. Directly tested by "
        "test_tc_trust_001_verifier_relies_only_on_recognized_trust_anchors.",
    ),
    "TC-TRUST-002": (
        "CONFORMANT", EV_TC001_CERTIFICATE, _WAVE_C_EVIDENCE,
        "Wave C (PR #65): verification cross-checks the resolved TrustAnchor's issuer_id "
        "against the Certificate's declared issuer_id -- a self-declared issuer_id is never "
        "trusted on its own (and is itself covered by the Signature, so changing it without "
        "re-signing invalidates verification). Directly tested by "
        "test_tc_trust_002_trust_not_inferred_from_self_declared_issuer_alone and "
        "test_scenario_14_issuer_id_mismatch_with_trust_anchor_rejected.",
    ),
    "TC-TRUST-003": (
        "CONFORMANT", EV_TC001_CERTIFICATE, _WAVE_C_EVIDENCE,
        "Wave C (PR #65): TrustAnchorRegistry.revoke_key stops future resolution of a kid "
        "without altering any previously-issued Certificate's content. Directly tested by "
        "test_tc_trust_003_rotation_does_not_retroactively_invalidate_historical_issuance "
        "and test_scenario_15_revoked_trust_anchor_key_rejected.",
    ),
    "TC-TRUST-004": (
        "CONFORMANT", EV_TC001_CERTIFICATE, _WAVE_C_EVIDENCE,
        "Wave C (PR #65): TrustAnchorRegistry holds multiple Trust Anchors across multiple "
        "issuer_ids simultaneously. Directly tested by "
        "test_tc_trust_004_verifier_may_recognize_multiple_trust_anchors.",
    ),
    "TC-COMPAT-001": (
        "CONFORMANT", EV_TC001_CERTIFICATE, _WAVE_C_EVIDENCE,
        "Wave C (PR #65): TC001_CERT_SCHEMA_VERSION is an explicit, single-valued constant "
        "-- no forward-compatibility is assumed for any other value. Directly tested by "
        "test_tc_compat_001_schema_version_compatibility_is_explicit.",
    ),
    "TC-COMPAT-002": (
        "CONFORMANT", EV_TC001_CERTIFICATE, _WAVE_C_EVIDENCE,
        "Wave C (PR #65): verify_technical_certificate returns UNSUPPORTED_SCHEMA, never "
        "VALID, for an unrecognized certificate_schema_version. Directly tested by "
        "test_tc_compat_002_unrecognized_schema_version_not_silently_accepted.",
    ),
    "TC-COMPAT-003": (
        "CONFORMANT", EV_TC001_CERTIFICATE, _WAVE_C_EVIDENCE,
        "Wave C (PR #65): manifest_reference_verification reuses verify_cm001_manifest, "
        "which itself rejects an unrecognized manifest_schema_version. Directly tested by "
        "test_tc_compat_003_validity_accounts_for_manifest_schema_version_compatibility.",
    ),
    "TC-COMPAT-004": (
        "CONFORMANT", EV_TC001_CERTIFICATE, _WAVE_C_EVIDENCE,
        "Wave C (PR #65): evidence_bundle_reference_consistency reuses "
        "verify_evidence_bundle_reference / verify_eb001_bundle, which reject an "
        "unrecognized Evidence Bundle schema_version. Directly tested by "
        "test_tc_compat_004_validity_accounts_for_evidence_bundle_schema_version_compatibility.",
    ),
    "TC-VSN-001": (
        "CONFORMANT", EV_TC001_CERTIFICATE, _WAVE_C_EVIDENCE,
        "Wave C (PR #65): certificate_schema_version is a required Identity field on every "
        "Certificate. Directly tested by "
        "test_tc_vsn_001_certificate_declares_a_schema_version.",
    ),
    "TC-VSN-002": (
        "CONFORMANT", EV_TC001_CERTIFICATE, _WAVE_C_EVIDENCE,
        "Wave C (PR #65): TC001_CERT_SCHEMA_VERSION is a fixed module-level constant, never "
        "computed or mutated at runtime. Directly tested by "
        "test_tc_vsn_002_schema_version_constant_is_immutable_string.",
    ),
    "TC-VSN-003": (
        "CONFORMANT", EV_TC001_CERTIFICATE, _WAVE_C_EVIDENCE,
        "Wave C (PR #65): certificate_schema_version, cp001_specification_version, "
        "manifest_schema_version, and Evidence Bundle schema_version are four distinct "
        "fields, never conflated. Directly tested by "
        "test_tc_vsn_003_schema_version_tracked_independently_of_other_specs.",
    ),
    "TC-VSN-004": (
        "CONFORMANT", EV_TC001_CERTIFICATE, _WAVE_C_EVIDENCE,
        "Wave C (PR #65): an unrecognized certificate_schema_version causes "
        "verify_technical_certificate to return UNSUPPORTED_SCHEMA, never VALID. Directly "
        "tested by test_tc_vsn_004_unrecognized_schema_version_causes_verification_failure "
        "and test_scenario_04_unrecognized_schema_version_yields_unsupported_schema.",
    ),
    "TC-SEC-001": (
        "CONFORMANT", EV_TC001_CERTIFICATE, _WAVE_C_EVIDENCE,
        "Wave C (PR #65): a fully forged Certificate dict (fabricated fields, invalid "
        "signature) is rejected -- verification never assumes good faith from the source. "
        "Directly tested by test_tc_sec_001_verification_assumes_untrusted_source.",
    ),
    "TC-SEC-002": (
        "CONFORMANT", EV_TC001_CERTIFICATE, _WAVE_C_EVIDENCE,
        "Wave C (PR #65): forgery/tamper detection is provided exclusively by Ed25519 "
        "signature verification against a recognized Trust Anchor. Directly tested by "
        "test_tc_sec_002_forgery_resistance_via_signature_only.",
    ),
    "TC-SEC-003": (
        "CONFORMANT", EV_TC001_CERTIFICATE, _WAVE_C_EVIDENCE,
        "Wave C (PR #65): the closed field set (_ALL_ALLOWED_FIELDS) has no "
        "secret/credential-shaped field, and any undeclared field is rejected at parse "
        "time. Directly tested by "
        "test_tc_sec_003_certificate_contains_no_secrets_or_credentials and "
        "test_scenario_02_undeclared_extra_field_rejected.",
    ),
    "TC-SEC-004": (
        "CONFORMANT", EV_TC001_CERTIFICATE, _WAVE_C_EVIDENCE,
        "Wave C (PR #65): the Manifest and Evidence Bundle are referenced exclusively by "
        "Hash Reference (digest/algorithm/content_ref) -- their raw content is never "
        "embedded in the Certificate. Directly tested by "
        "test_tc_sec_004_sensitive_data_referenced_only_via_hash_reference.",
    ),
    "TC-SEC-005": (
        "CONFORMANT", EV_TC001_CERTIFICATE, _WAVE_C_EVIDENCE,
        "Wave C (PR #65): tc001_certificate.py imports no gate/authority/coordinator/egress "
        "internals -- a valid Certificate has no code path into runtime execution. Directly "
        "tested by test_tc_sec_005_valid_certificate_not_treated_as_runtime_execution_authorization.",
    ),
    "TC-CONF-001": (
        "CONFORMANT", EV_TC001_CERTIFICATE, _WAVE_C_EVIDENCE,
        "Wave C (PR #65): issuer-side (build/sign) and verifier-side (verify) are distinct "
        "functions with distinct fail-closed contracts. Directly tested by "
        "test_tc_conf_001_conformance_defined_separately_for_issuer_and_verifier.",
    ),
    "TC-CONF-002": (
        "CONFORMANT", EV_TC001_CERTIFICATE, _WAVE_C_EVIDENCE,
        "Wave C (PR #65): build_technical_certificate's signature has no "
        "certification_result parameter -- a non-PASS Certificate cannot be constructed. "
        "Directly tested by test_tc_conf_002_issuer_never_issues_for_a_non_pass_result.",
    ),
    "TC-CONF-003": (
        "CONFORMANT", EV_TC001_CERTIFICATE, _WAVE_C_EVIDENCE,
        "Wave C (PR #65): verify_technical_certificate implements every Section 15 step in "
        "order, including the Revocation Check. Directly tested by "
        "test_tc_conf_003_verifier_implements_fail_closed_verification_including_revocation.",
    ),
    "TC-CONF-004": (
        "CONFORMANT", EV_TC001_CERTIFICATE, _WAVE_C_EVIDENCE,
        "Wave C (PR #65): tc001_certificate.py has no framework-specific dependency "
        "(langgraph/autogen/crewai/voltagent/web framework). Directly tested by "
        "test_tc_conf_004_conformance_is_framework_neutral.",
    ),
    "TC-CONF-005": (
        "CONFORMANT", EV_TC001_CERTIFICATE, _WAVE_C_EVIDENCE,
        "Wave C (PR #65): build_technical_certificate refuses to issue when its direct "
        "Evidence Bundle Reference and the Manifest's primary reference disagree, checked "
        "before signing. Directly tested by "
        "test_tc_conf_005_issuer_ensures_reference_consistency_before_issuance and "
        "test_scenario_09_producer_refuses_mismatched_direct_and_manifest_bundle_references.",
    ),
}


def _find_rule(spec_id: str, category: str) -> Optional[Rule]:
    for rule_spec, pattern, status, evidence, rationale in RULES:
        if rule_spec not in ("*", spec_id):
            continue
        if pattern.search(category):
            return (rule_spec, pattern, status, evidence, rationale)
    return None


def assess(requirements: List[Requirement]) -> List[Requirement]:
    for req in requirements:
        cat = req.requirement_category

        if req.requirement_id in ID_OVERRIDES:
            status, evidence, evidence_refs, rationale = ID_OVERRIDES[req.requirement_id]
            req.conformance_status = status
            impl, tests = evidence
            req.implementation_references = list(impl)
            req.test_references = list(tests)
            req.evidence_references = list(evidence_refs)
            req.rationale = rationale
            continue

        if _META.search(cat):
            req.conformance_status = "NOT_APPLICABLE"
            req.rationale = _NOT_APPLICABLE_RATIONALE
            continue

        rule = _find_rule(req.specification_id, cat)
        if rule is not None:
            _, _, status, evidence, rationale = rule
            req.conformance_status = status
            if evidence is not None:
                impl, tests = evidence
                req.implementation_references = list(impl)
                req.test_references = list(tests)
            req.rationale = rationale
            continue

        # Default: investigated, confirmed absent. GAP, not NOT_ASSESSED,
        # because the absence was actively verified against the broader
        # semantic-mapping investigation described in this module's
        # docstring, not left unchecked.
        req.conformance_status = "GAP"
        req.rationale = (
            f"No implementation behavior, automated test, or evidence mechanism "
            f"semantically equivalent to this requirement (category: "
            f"{req.requirement_category!r}) was found anywhere under src/, "
            "tests/, certifications/, evidence/, schemas/, docs/, or CI "
            "workflows, after the broader semantic-mapping investigation "
            "described in this module's docstring — not merely a lexical "
            "search for this specification's exact terminology."
        )
    return requirements
