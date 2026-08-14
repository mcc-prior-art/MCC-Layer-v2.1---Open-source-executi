"""``python -m mutation`` -- run all targeted mutations and report the
mutation score (PR #71, Workstream J; 26 defects as of the gate.py
fail-open matrix extension -- see mutation/defects.py).

    python -m mutation                       # human + JSON summary, exit 0 iff all detected
    python -m mutation --output report.json   # also write the full report

Exit code is 0 only when every defect was DETECTED; 1 if any survived. This
mirrors the required outcome ("100% detection") as a real, checkable exit
code, not just a printed number a reviewer has to notice.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from mutation.harness import run_all_mutants


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="mutation")
    parser.add_argument("--output", default=None, help="Path to write the full JSON report.")
    parser.add_argument("--timeout", type=float, default=120.0, help="Per-mutant pytest timeout (seconds).")
    args = parser.parse_args(argv)

    report = run_all_mutants(timeout=args.timeout)

    for r in report.results:
        status = "DETECTED" if r.detected else "SURVIVED"
        print(f"{status:9s} {r.defect_id:45s} ({r.duration_seconds:.1f}s)")

    summary = report.to_dict()
    print()
    print(json.dumps({"total": summary["total"], "detected": summary["detected"],
                       "mutation_score": summary["mutation_score"],
                       "survived_defect_ids": summary["survived_defect_ids"]}, indent=2))

    if args.output:
        Path(args.output).write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")

    return 0 if not report.survived else 1


if __name__ == "__main__":
    raise SystemExit(main())
