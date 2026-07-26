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
