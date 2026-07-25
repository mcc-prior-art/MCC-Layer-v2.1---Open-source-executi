"""Deterministic normative-requirement extraction from the four MCC v1.0 specs.

Two extraction passes, in this priority order:

1. Canonical requirement identifiers — every standalone line matching
   ``^[A-Z][A-Z-]{1,20}-[0-9]{3}$`` is treated as a canonical requirement ID,
   consistent with the Requirement Identifier Registry section each of the
   four specifications defines for itself (e.g. MCC-EB-001 Section 23,
   MCC-TC-001 Section 22, MCC-CP-001 Appendix C). The following paragraph(s),
   up to the next ID line / heading / horizontal rule, form the requirement
   text.

2. Derived identifiers — for any top-level (H1) section that contains *no*
   canonical ID anywhere within it, every line containing an uppercase
   RFC 2119 / RFC 8174 binding keyword (MUST, MUST NOT, SHALL, SHALL NOT,
   REQUIRED) is extracted as its own requirement, with a deterministic ID of
   the form ``<SPEC_ID>-<SECTION_SLUG>-D<NN>``. This only fires for sections
   the specifications' own Invariants convention did not already cover, so
   it does not duplicate canonical requirements.

This module performs no judgment about implementation status. It only
discovers what the specifications say. See ``assess.py`` for the (disclosed,
category-grounded) conformance assessment overlay.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List, Tuple

from mcc_conformance.models import BINDING_KEYWORDS, NORMATIVE_KEYWORDS, Requirement

ID_LINE_RE = re.compile(r"^[A-Z][A-Z-]{1,20}-[0-9]{3}$")
HEADING_RE = re.compile(r"^(#{1,2})\s+(.*)$")
H1_RE = re.compile(r"^#\s+(.*)$")
H2_RE = re.compile(r"^##\s+(.*)$")

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


def _is_structural(line: str) -> bool:
    stripped = line.strip()
    return (
        stripped == "---"
        or stripped == ""
        or HEADING_RE.match(stripped) is not None
        or ID_LINE_RE.match(stripped) is not None
    )


def extract_spec(spec_id: str, repo_root: Path) -> List[Requirement]:
    rel_path = SPEC_FILES[spec_id]
    path = repo_root / rel_path
    text = path.read_text(encoding="utf-8")
    lines = text.split("\n")
    spec_version = _spec_version(lines)

    current_h1 = ""
    current_h2 = ""
    # h1_index -> list of (line_index, id, h2_at_time) for canonical IDs found
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

    # Pass 1: canonical requirements.
    for idx, (line_idx, req_id, h1, h2) in enumerate(canonical):
        next_boundary = len(lines)
        if idx + 1 < len(canonical):
            next_boundary = min(next_boundary, canonical[idx + 1][0])
        # Also stop at the next heading, whichever comes first.
        j = line_idx + 1
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
            )
        )

    # Pass 2: derived requirements, only for H1 sections with zero canonical IDs.
    covered_h1 = {h1 for (_, _, h1, _) in canonical}
    for start, end, h1 in h1_boundaries:
        if not h1 or h1 in covered_h1:
            continue
        derived_seq = 0
        current_h2_local = ""
        i = start
        while i < end:
            line = lines[i]
            h2m = H2_RE.match(line)
            if h2m:
                current_h2_local = h2m.group(1).strip()
                i += 1
                continue
            stripped = line.strip()
            if not stripped or _is_structural(stripped):
                i += 1
                continue
            if not any(
                re.search(rf"\b{re.escape(kw)}\b", stripped) for kw in BINDING_KEYWORDS
            ):
                i += 1
                continue
            # A list-introducing line ("... SHALL NOT:") absorbs the bullets
            # that immediately follow it, so the requirement text is complete
            # rather than a truncated stub.
            text_parts = [stripped]
            j = i + 1
            if stripped.endswith(":"):
                if j < end and lines[j].strip() == "":
                    j += 1
                while j < end and lines[j].strip().startswith("-"):
                    text_parts.append(lines[j].strip())
                    j += 1
            derived_seq += 1
            derived_id = f"{spec_id}-{_slug(h1)}-D{derived_seq:02d}"
            section = h1 + (f" / {current_h2_local}" if current_h2_local else "")
            req_text = " ".join(text_parts)
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
                )
            )
            i = j

    return requirements


def extract_all(repo_root: Path) -> List[Requirement]:
    out: List[Requirement] = []
    for spec_id in SPEC_FILES:
        out.extend(extract_spec(spec_id, repo_root))
    return out
