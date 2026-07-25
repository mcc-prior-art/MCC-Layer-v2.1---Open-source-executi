"""Data model shared by extraction, assessment, and validation."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

ALLOWED_STATUSES = (
    "CONFORMANT",
    "PARTIAL",
    "GAP",
    "NOT_APPLICABLE",
    "NOT_ASSESSED",
)

# Priority order, strongest first. Only uppercase RFC 2119 / RFC 8174 forms
# count as normative in this document family (the specs themselves state
# lowercase forms are not normative unless explicitly stated).
NORMATIVE_KEYWORDS = (
    "MUST NOT",
    "SHALL NOT",
    "MUST",
    "SHALL",
    "REQUIRED",
    "SHOULD NOT",
    "SHOULD",
    "RECOMMENDED",
    "MAY",
)

BINDING_KEYWORDS = ("MUST NOT", "SHALL NOT", "MUST", "SHALL", "REQUIRED")


@dataclass
class Requirement:
    requirement_id: str
    specification_id: str
    specification_version: str
    source_file: str
    section: str
    normative_keyword: str
    requirement_text: str
    requirement_category: str
    id_origin: str  # "canonical" | "derived"
    implementation_references: List[str] = field(default_factory=list)
    test_references: List[str] = field(default_factory=list)
    evidence_references: List[str] = field(default_factory=list)
    conformance_status: str = "NOT_ASSESSED"
    rationale: str = ""
    notes: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "requirement_id": self.requirement_id,
            "specification_id": self.specification_id,
            "specification_version": self.specification_version,
            "source_file": self.source_file,
            "section": self.section,
            "normative_keyword": self.normative_keyword,
            "requirement_text": self.requirement_text,
            "requirement_category": self.requirement_category,
            "id_origin": self.id_origin,
            "implementation_references": self.implementation_references,
            "test_references": self.test_references,
            "evidence_references": self.evidence_references,
            "conformance_status": self.conformance_status,
            "rationale": self.rationale,
            "notes": self.notes,
        }
