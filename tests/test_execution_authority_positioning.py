"""Lightweight, static CI guard for the execution-authority positioning
docs (README.md + docs/EXECUTION_AUTHORITY_BOUNDARY.md).

Mirrors ``test_reproduction_entry_point.py``'s convention: cheap substring/
structure checks on tracked documentation content, not prose-formatting
tests. Protects against silent regression of the canonical positioning
language and the admission-control-vs-execution-authority distinction this
repository publicly makes, and against reintroducing an overclaim
(certification / third-party audit / production deployment) into either
document.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Distinctive fragments of the canonical positioning statement, checked
# independently (not as one brittle multi-line string) so hard line-wraps
# or an inserted <br> do not make this test fragile to reflow -- consistent
# with this repository's existing doc-guard convention of short substring
# checks rather than exact prose reproduction.
CANONICAL_POSITIONING_FRAGMENTS = (
    "MCC-Core does not merely determine whether an action is admissible.",
    "cryptographically attributable execution authority",
    "bound to the exact action and its execution",
    "before the gate permits execution.",
)

ADMISSION_VS_AUTHORITY_LINE = "Admission is a decision. Authority is a verifiable execution artifact."

# The five canonical elements of the "Current MCC-Core Messaging Standard"
# section, checked independently for the same reflow-fragility reason as
# CANONICAL_POSITIONING_FRAGMENTS above.
MESSAGING_STANDARD_ELEMENTS = {
    "business": "AI decides what to do. MCC-Core verifies whether it has the authority to do it.",
    "technical": "MCC-Core creates and verifies cryptographically attributable execution authority,",
    "category": "A safer model is still not an authority.",
    "execution_rule": "No verified authority. No execution.",
    "product_category": "Verifiable execution authority for autonomous AI systems.",
}


def _read(path: str) -> str:
    full = ROOT / path
    assert full.is_file(), f"missing: {full}"
    return full.read_text(encoding="utf-8")


def test_readme_carries_canonical_execution_authority_positioning():
    readme = _read("README.md")
    for fragment in CANONICAL_POSITIONING_FRAGMENTS:
        assert fragment in readme, (
            f"README.md is missing a fragment of the canonical execution-authority "
            f"positioning statement: {fragment!r}"
        )
    assert ADMISSION_VS_AUTHORITY_LINE in readme, (
        "README.md is missing the 'Admission is a decision. Authority is a "
        "verifiable execution artifact.' line"
    )


def test_readme_carries_current_messaging_standard_section():
    readme = _read("README.md")
    assert "## Current MCC-Core Messaging Standard" in readme, (
        "README.md is missing the 'Current MCC-Core Messaging Standard' section"
    )
    for label, fragment in MESSAGING_STANDARD_ELEMENTS.items():
        assert fragment in readme, (
            f"README.md is missing the {label!r} messaging-standard element: {fragment!r}"
        )
    for label_heading in ("**Business**", "**Technical**", "**Category**",
                          "**Execution rule**", "**Product category**"):
        assert label_heading in readme, (
            f"README.md's messaging-standard section is missing the {label_heading!r} label"
        )


def test_messaging_standard_explicitly_does_not_replace_historical_doctrine():
    readme = _read("README.md")
    assert (
        "This current messaging layer clarifies MCC-Core's product and category"
    ) in readme
    assert "does not replace or modify the historical MCC-Core" in readme
    assert "Doctrine Lines v1.0 or the dated doctrine record" in readme


def test_readme_links_to_execution_authority_boundary_doc():
    readme = _read("README.md")
    assert "docs/EXECUTION_AUTHORITY_BOUNDARY.md" in readme, (
        "README.md does not link to docs/EXECUTION_AUTHORITY_BOUNDARY.md"
    )


def test_readme_preserves_existing_doctrine():
    """This positioning layer must never replace the existing canonical
    doctrine -- both must coexist."""
    readme = _read("README.md")
    assert "A proposal is not permission." in readme
    assert "The model proposes." in readme
    assert "MCC-Core decides." in readme
    assert "The gate enforces." in readme
    assert "The audit chain records." in readme


def test_execution_authority_boundary_doc_exists_and_has_required_sections():
    doc = _read("docs/EXECUTION_AUTHORITY_BOUNDARY.md")
    for required_heading in (
        "# MCC-Core Execution Authority Boundary",
        "## Admission Control vs. Execution Authority",
        "## Required security properties",
        "## Important distinctions",
        "## Claim boundaries",
    ):
        assert required_heading in doc, f"missing required section: {required_heading!r}"


def test_execution_authority_boundary_doc_contains_the_current_chain():
    doc = _read("docs/EXECUTION_AUTHORITY_BOUNDARY.md")
    for stage in (
        "INTELLIGENCE",
        "ATTESTATION",
        "CONTROL",
        "SIGNED AUTHORITY",
        "AUTHORITY VERIFICATION",
        "GATE",
        "EXECUTION",
    ):
        assert stage in doc, f"execution-authority chain is missing stage: {stage!r}"


def test_execution_authority_boundary_doc_preserves_attestation_is_not_authority():
    doc = _read("docs/EXECUTION_AUTHORITY_BOUNDARY.md")
    assert "Attestation is evidence, not authority" in doc
    assert "A valid signature does not make an assessment true" in doc
    assert "A model proposal is not permission" in doc


def test_execution_authority_boundary_doc_retains_claim_boundary_language():
    """Presence-of-disclaimer check, not an absence-of-phrase scan: several
    legitimate disclaiming sentences in this document necessarily use words
    like "certification" or "regulatory approval" in the course of denying
    them (e.g. "does not imply ... regulatory approval"), so a naive
    substring-must-not-appear scan would fail on the disclaimers themselves.
    What must actually hold is that the disclaiming sentences exist."""
    doc = _read("docs/EXECUTION_AUTHORITY_BOUNDARY.md")
    assert "self-administered reproducible assurance is not a third-party audit" in doc.lower()
    assert "not a certified production system" in doc.lower()
    assert "no wording in this document should be read as implying formal" in doc.lower()
    assert "third-party security audit," in doc.lower()
    assert "production deployment" in doc.lower()


def test_readme_retains_accurate_positioning_disclaimers():
    """Same presence-of-disclaimer principle as above, applied to the
    pre-existing README sections these new positioning claims sit next to."""
    readme = _read("README.md")
    assert "Certified production safety system" in readme
    assert "Independently audited or formally verified" in readme
    assert "not a certified production system" in readme.lower()
