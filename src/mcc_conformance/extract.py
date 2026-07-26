"""Deterministic normative-requirement extraction from the four MCC v1.0 specs.

Two extraction passes, in this priority order:

1. Canonical requirement identifiers — every standalone line matching
   ``^[A-Z][A-Z-]{1,20}-[0-9]{3}$`` is treated as a canonical requirement ID,
   consistent with the Requirement Identifier Registry section each of the
   four specifications defines for itself (e.g. MCC-EB-001 Section 23,
   MCC-TC-001 Section 22, MCC-CP-001 Appendix C). The following paragraph(s),
   up to the next ID line / heading / horizontal rule, form the requirement
   text. This pass is unchanged from the original extractor and is
   authoritative: canonical IDs and their text are never altered, removed,
   or replaced by a derived ID.

2. Derived, independent normative obligations — every remaining binding
   (MUST, MUST NOT, SHALL, SHALL NOT, REQUIRED) statement in the document
   that a canonical requirement does not already represent, regardless of
   whether its enclosing H1 section also contains canonical IDs elsewhere.

   This corrects a defect in the original extractor: it previously skipped
   this second pass entirely for any H1 section that contained *any*
   canonical ID, silently dropping every other independent MUST/SHALL
   sentence in that section (documented in
   conformance/normative-v1.0/remediation/wave-1-execution-boundary-scope-manifest.md,
   Finding 1 — 391 such lines across the four specifications). The pass now
   runs across every H1 section; it tracks exactly which source lines were
   already consumed by canonical capture (a line-index provenance set) and
   only considers lines outside that set.

   Within an H1 section, extraction proceeds line by line:

   - A line already consumed by canonical capture is skipped.
   - A binding line that ends with ``:`` introduces an enumerated list of
     fields/inputs; the immediately following ``-``-prefixed lines (after at
     most one blank line) are fragments of that ONE requirement, not
     independent obligations — this mirrors how the specifications' own
     canonical Required-Fields-style sections state one requirement with an
     enumerated field list, and is unchanged from the original extractor's
     list-absorption behaviour.
   - A binding line that does not end with ``:`` — including a
     self-contained bullet that itself states a complete obligation (e.g. "-
     **Framework Neutrality.** The Certificate format MUST remain
     independent...") — is joined with any immediately following plain-prose
     continuation lines into one Markdown paragraph (a safeguard for
     wrapped/multi-line sentences; the four specifications currently write
     exactly one sentence per physical line, verified empirically, so this
     joining is a no-op on the current corpus but is exercised by the
     regression tests). The joined paragraph is then split at genuine
     sentence boundaries (a period followed by whitespace and a capital
     letter — not at colons, semicolons, or coordinating conjunctions, which
     routinely join a single compound obligation in this document family)
     so that two independently testable MUST/SHALL statements sharing one
     source line become two requirements, never one.
   - Every resulting candidate is compared, by normalized text (whitespace-
     collapsed, case-sensitive), against the canonical requirement texts
     already captured in the *same* H1 section. An exact match means the
     specification restates an existing canonical requirement verbatim
     elsewhere in the same section (observed, e.g., MCC-EB-001's EB-STR-001
     restating Section 10.1's opening sentence word for word) — it is
     recorded as a duplicate of that canonical ID, not extracted again.
     A candidate identical to one already extracted earlier in the same H1
     during this pass is likewise not re-extracted. Neither check is a bare
     line-index or raw-line comparison; both compare normalized text content
     against tracked provenance.

   Deliberately out of scope for this pass, because the current corpus does
   not exercise it and inventing unverified parsing logic would be worse
   than declining to guess: Markdown tables (none of the four specifications
   contain a pipe-table row anywhere) and semicolon-joined clauses (kept as
   one requirement; splitting reliably on semicolons without a real parser
   risks fragmenting genuine single compound obligations). Both exclusions
   are re-verified by test_conformance_extraction_correction.py rather than
   merely asserted here.

Every derived requirement records the 1-indexed source line at which its
text begins (``Requirement.source_line``), providing exact-location
provenance for every requirement, canonical or derived — not just the
section title, which is shared by many requirements.

This module performs no judgment about implementation status. It only
discovers what the specifications say. See ``assess.py`` for the (disclosed,
category-grounded) conformance assessment overlay, and ``coverage_audit.py``
for the deterministic reconciliation of every previously-orphaned normative
source line against this pass's output.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from mcc_conformance.models import BINDING_KEYWORDS, NORMATIVE_KEYWORDS, Requirement

ID_LINE_RE = re.compile(r"^[A-Z][A-Z-]{1,20}-[0-9]{3}$")
HEADING_RE = re.compile(r"^(#{1,2})\s+(.*)$")
H1_RE = re.compile(r"^#\s+(.*)$")
H2_RE = re.compile(r"^##\s+(.*)$")
BULLET_RE = re.compile(r"^[-*]\s|^\d+\.\s")

# Sentence boundary: a period preceded by a lowercase letter, digit, or
# closing parenthesis, followed by whitespace and a capital letter. This
# deliberately does not split on ":" or ";" (see module docstring) and does
# not misfire on decimal/section-number references (e.g. "Section 8.7,")
# because those are not followed by ". " + capital letter, nor on
# abbreviations, because none exist in this document family (verified: zero
# occurrences of "e.g." / "i.e." anywhere in specs/*.md).
SENTENCE_SPLIT_RE = re.compile(r"(?<=[a-z0-9)])\.\s+(?=[A-Z])")

SPEC_FILES = {
    "MCC-CP-001": "specs/MCC-CP-001.md",
    "MCC-EB-001": "specs/MCC-EB-001.md",
    "MCC-CM-001": "specs/MCC-CM-001.md",
    "MCC-TC-001": "specs/MCC-TC-001.md",
}


def _slug(text: str) -> str:
    text = re.sub(r"[^A-Za-z0-9]+", "-", text.strip()).strip("-").upper()
    return text[:40] if text else "SECTION"


def _spec_version(lines: List[str]) -> str:
    for line in lines[:20]:
        if line.startswith("Version:"):
            return line.split(":", 1)[1].strip()
    return "UNKNOWN"


def _dominant_keyword(text: str) -> str:
    for kw in NORMATIVE_KEYWORDS:
        if re.search(rf"\b{re.escape(kw)}\b", text):
            return kw
    return ""


# "REQUIRED" is unambiguously binding in isolation, but this document family
# also uses it, together with OPTIONAL and CONDITIONAL, purely as the name of
# the three-way Requirement Classification enum (e.g. "its classification
# (REQUIRED, OPTIONAL, or CONDITIONAL)", "Evidence Items for REQUIRED,
# OPTIONAL, and CONDITIONAL requirements alike") -- there "REQUIRED" is an
# enum-value label, not an RFC 2119 obligation on the sentence it appears in.
# A bare "REQUIRED" occurring in the same sentence as both OPTIONAL and
# CONDITIONAL is therefore not treated as binding on its own; MUST, MUST NOT,
# SHALL, and SHALL NOT are never ambiguous in this way and are always
# treated as binding.
_CLASSIFICATION_ENUM_RE = re.compile(
    r"\bREQUIRED\b.{0,60}\bOPTIONAL\b.{0,60}\bCONDITIONAL\b"
    r"|\bCONDITIONAL\b.{0,60}\bOPTIONAL\b.{0,60}\bREQUIRED\b"
)
_UNAMBIGUOUS_BINDING_KEYWORDS = ("MUST NOT", "SHALL NOT", "MUST", "SHALL")


def _has_binding(text: str) -> bool:
    if any(re.search(rf"\b{re.escape(kw)}\b", text) for kw in _UNAMBIGUOUS_BINDING_KEYWORDS):
        return True
    if not re.search(r"\bREQUIRED\b", text):
        return False
    if _CLASSIFICATION_ENUM_RE.search(text):
        return False
    return True


def _is_structural(line: str) -> bool:
    stripped = line.strip()
    return (
        stripped == "---"
        or stripped == ""
        or HEADING_RE.match(stripped) is not None
        or ID_LINE_RE.match(stripped) is not None
    )


def _normalize(text: str) -> str:
    return " ".join(text.split())


def _split_sentences(text: str) -> List[str]:
    """Split into sentences, restoring the period the split boundary
    consumes on every part but the last (which already retains its own
    trailing punctuation from the source paragraph)."""
    if not text.strip():
        return []
    parts = SENTENCE_SPLIT_RE.split(text)
    result: List[str] = []
    for idx, part in enumerate(parts):
        stripped = part.strip()
        if not stripped:
            continue
        if idx < len(parts) - 1 and not stripped.endswith((".", "!", "?", ":")):
            stripped += "."
        result.append(stripped)
    return result


class CoverageAuditEntry:
    """One disposition record for a candidate normative source line,
    consumed by coverage_audit.py to build the reconciliation artifact."""

    __slots__ = (
        "specification_id",
        "category",
        "source_line",
        "normalized_text",
        "disposition",
        "requirement_id",
        "duplicate_of",
        "rationale",
    )

    def __init__(
        self,
        specification_id: str,
        category: str,
        source_line: int,
        normalized_text: str,
        disposition: str,
        requirement_id: Optional[str],
        duplicate_of: Optional[str],
        rationale: str,
    ) -> None:
        self.specification_id = specification_id
        self.category = category
        self.source_line = source_line
        self.normalized_text = normalized_text
        self.disposition = disposition
        self.requirement_id = requirement_id
        self.duplicate_of = duplicate_of
        self.rationale = rationale

    def to_dict(self) -> dict:
        return {
            "specification_id": self.specification_id,
            "category": self.category,
            "source_line": self.source_line,
            "normalized_text": self.normalized_text,
            "disposition": self.disposition,
            "requirement_id": self.requirement_id,
            "duplicate_of": self.duplicate_of,
            "rationale": self.rationale,
        }


def extract_spec_with_audit(
    spec_id: str, repo_root: Path
) -> Tuple[List[Requirement], List[CoverageAuditEntry]]:
    rel_path = SPEC_FILES[spec_id]
    path = repo_root / rel_path
    text = path.read_text(encoding="utf-8")
    lines = text.split("\n")
    spec_version = _spec_version(lines)

    current_h1 = ""
    current_h2 = ""
    canonical: List[Tuple[int, str, str, str]] = []  # (line_idx, id, h1, h2)
    h1_boundaries: List[Tuple[int, int, str]] = []  # (start, end, h1_title)
    h1_start = 0
    h1_title = ""

    for i, line in enumerate(lines):
        h1m = H1_RE.match(line)
        h2m = H2_RE.match(line)
        if h1m:
            if h1_title or h1_start != i:
                h1_boundaries.append((h1_start, i, h1_title))
            h1_start = i
            h1_title = h1m.group(1).strip()
            current_h1 = h1_title
            current_h2 = ""
            continue
        if h2m:
            current_h2 = h2m.group(1).strip()
            continue
        if ID_LINE_RE.match(line.strip()):
            canonical.append((i, line.strip(), current_h1, current_h2))
    h1_boundaries.append((h1_start, len(lines), h1_title))

    requirements: List[Requirement] = []
    seen_ids: Dict[str, int] = {}
    captured: Set[int] = set()
    # h1 -> {normalized canonical text -> canonical requirement_id}
    canonical_by_h1: Dict[str, Dict[str, str]] = {}

    # Pass 1: canonical requirements. Unchanged from the original extractor
    # except for additionally recording source_line and building the
    # provenance/dedup structures the corrected Pass 2 relies on.
    for idx, (line_idx, req_id, h1, h2) in enumerate(canonical):
        next_boundary = len(lines)
        if idx + 1 < len(canonical):
            next_boundary = min(next_boundary, canonical[idx + 1][0])
        stop = next_boundary
        for k in range(line_idx + 1, next_boundary):
            if HEADING_RE.match(lines[k].strip()) or lines[k].strip() == "---":
                stop = k
                break
        paragraph_lines = [
            lines[k].strip() for k in range(line_idx + 1, stop) if lines[k].strip()
        ]
        req_text = " ".join(paragraph_lines).strip()
        section = f"{h1}" + (f" / {h2}" if h2 else "")
        keyword = _dominant_keyword(req_text) or "SHALL"

        final_id = req_id
        if final_id in seen_ids:
            seen_ids[final_id] += 1
            final_id = f"{req_id}#{seen_ids[req_id]}"
        else:
            seen_ids[final_id] = 0

        requirements.append(
            Requirement(
                requirement_id=final_id,
                specification_id=spec_id,
                specification_version=spec_version,
                source_file=rel_path,
                section=section,
                normative_keyword=keyword,
                requirement_text=req_text,
                requirement_category=h1,
                id_origin="canonical",
                source_line=line_idx + 1,
            )
        )
        captured.add(line_idx)
        for k in range(line_idx + 1, stop):
            captured.add(k)
        canonical_by_h1.setdefault(h1, {})[_normalize(req_text)] = final_id

    # Pass 2: derived, independent normative obligations. Runs across every
    # H1 section (the corrected behaviour), skipping lines already captured
    # by canonical extraction above. Deliberately unconditional: the loop
    # below does NOT filter by "does this H1 already have a canonical ID" --
    # that exact filter was the Wave 1 defect (391 silently dropped lines).
    # Do not reintroduce a covered/canonical-only H1 restriction here.
    audit_entries: List[CoverageAuditEntry] = []

    for start, end, h1 in h1_boundaries:
        if not h1:
            continue
        derived_seq = 0
        current_h2_local = ""
        i = start
        canon_texts = canonical_by_h1.get(h1, {})
        seen_candidate_texts: Dict[str, str] = {}  # normalized text -> derived id

        while i < end:
            line = lines[i]
            h2m = H2_RE.match(line)
            if h2m:
                current_h2_local = h2m.group(1).strip()
                i += 1
                continue
            if i in captured:
                i += 1
                continue
            stripped = line.strip()
            if not stripped or _is_structural(stripped):
                i += 1
                continue
            if not _has_binding(stripped):
                i += 1
                continue

            def emit(req_text: str, src_line: int) -> None:
                nonlocal derived_seq
                norm = _normalize(req_text)
                if norm in canon_texts:
                    audit_entries.append(
                        CoverageAuditEntry(
                            spec_id, h1, src_line, norm, "DUPLICATE_OF_CANONICAL",
                            None, canon_texts[norm],
                            "Normalized text is identical to an existing canonical "
                            "requirement in the same section; not extracted again.",
                        )
                    )
                    return
                if norm in seen_candidate_texts:
                    audit_entries.append(
                        CoverageAuditEntry(
                            spec_id, h1, src_line, norm, "DUPLICATE_WITHIN_DERIVED",
                            None, seen_candidate_texts[norm],
                            "Normalized text is identical to another derived "
                            "requirement already extracted in the same section.",
                        )
                    )
                    return
                derived_seq += 1
                derived_id = f"{spec_id}-{_slug(h1)}-D{derived_seq:02d}"
                section = h1 + (f" / {current_h2_local}" if current_h2_local else "")
                requirements.append(
                    Requirement(
                        requirement_id=derived_id,
                        specification_id=spec_id,
                        specification_version=spec_version,
                        source_file=rel_path,
                        section=section,
                        normative_keyword=_dominant_keyword(req_text),
                        requirement_text=req_text,
                        requirement_category=h1,
                        id_origin="derived",
                        source_line=src_line,
                    )
                )
                seen_candidate_texts[norm] = derived_id
                audit_entries.append(
                    CoverageAuditEntry(
                        spec_id, h1, src_line, norm, "EXTRACTED", derived_id, None,
                        "Independent normative obligation not already represented "
                        "by a canonical requirement in this section.",
                    )
                )

            if stripped.endswith(":"):
                # List-introducing line: absorb the following bullet
                # fragments into ONE requirement (unchanged convention).
                text_parts = [stripped]
                j = i + 1
                if j < end and lines[j].strip() == "":
                    j += 1
                while (
                    j < end
                    and j not in captured
                    and lines[j].strip().startswith("-")
                ):
                    text_parts.append(lines[j].strip())
                    j += 1
                emit(" ".join(text_parts), i + 1)
                i = j
                continue

            # Not list-introducing: join contiguous plain-prose continuation
            # lines into one paragraph (wrapped-sentence safeguard; a no-op
            # on the current corpus, see module docstring), then split into
            # independently testable sentences.
            para_lines = [stripped]
            j = i + 1
            while (
                j < end
                and j not in captured
                and lines[j].strip()
                and not _is_structural(lines[j].strip())
                and not BULLET_RE.match(lines[j].strip())
            ):
                para_lines.append(lines[j].strip())
                j += 1
            raw_para = " ".join(para_lines)

            for sentence in _split_sentences(raw_para):
                if not _has_binding(sentence):
                    continue
                emit(sentence, i + 1)
            i = j

    return requirements, audit_entries


def extract_spec(spec_id: str, repo_root: Path) -> List[Requirement]:
    requirements, _audit = extract_spec_with_audit(spec_id, repo_root)
    return requirements


def extract_all(repo_root: Path) -> List[Requirement]:
    out: List[Requirement] = []
    for spec_id in SPEC_FILES:
        out.extend(extract_spec(spec_id, repo_root))
    return out


def extract_all_with_audit(
    repo_root: Path,
) -> Tuple[List[Requirement], Dict[str, List[CoverageAuditEntry]]]:
    all_reqs: List[Requirement] = []
    audits: Dict[str, List[CoverageAuditEntry]] = {}
    for spec_id in SPEC_FILES:
        reqs, audit = extract_spec_with_audit(spec_id, repo_root)
        all_reqs.extend(reqs)
        audits[spec_id] = audit
    return all_reqs, audits
