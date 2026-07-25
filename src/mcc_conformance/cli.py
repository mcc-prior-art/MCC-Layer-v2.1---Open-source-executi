"""CLI entry point: ``python -m mcc_conformance {generate|validate}``."""

from __future__ import annotations

import sys
from pathlib import Path

from mcc_conformance.generate import generate
from mcc_conformance.validate import validate_all


def _repo_root() -> Path:
    # src/mcc_conformance/cli.py -> repo root
    return Path(__file__).resolve().parents[2]


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] not in ("generate", "validate"):
        print("usage: python -m mcc_conformance {generate|validate}", file=sys.stderr)
        return 2

    repo_root = _repo_root()

    if argv[0] == "generate":
        generate(repo_root)
        print("Generated conformance/normative-v1.0/{baseline,requirements,traceability_matrix}.json, "
              "traceability_matrix.md, gap_report.md")
        return 0

    errors = validate_all(repo_root)
    if errors:
        print(f"FAIL: {len(errors)} validation error(s):", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1
    print("OK: Normative v1.0 conformance baseline is structurally valid and deterministic.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
