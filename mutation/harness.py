"""Mutation-testing harness (PR #71, Workstream J).

For each ``Defect`` in ``mutation.defects``: copy the repository to an
isolated temp directory, apply the ONE mutation, run its named detector
tests as a real ``pytest`` subprocess against the mutated copy (a genuine
fresh 3-process SUT boots against the MUTATED source, exactly as
``python -m assurance run`` would), and record whether the mutation was
DETECTED (a detector test failed -- correct) or SURVIVED (every detector
test still passed against broken code -- a real, reportable gap).

Never fabricates a result: a defect whose ``find`` text is not found
exactly once in the copy (e.g. after an unrelated refactor) raises rather
than silently skipping or reporting a false "detected".
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from mutation.defects import DEFECTS, Defect

REPO_ROOT = Path(__file__).resolve().parents[1]

# Copying these directories/files is either wasteful (VCS metadata, caches,
# prior build output) or actively wrong (a stray local .hypothesis example
# database must not leak between mutants). Never excludes anything under
# assurance/, src/, egress_proxy/, gateway/, pilot_notify/, sdk/, tests/,
# mutation/ (mutation/detectors.py's own detector tests must be present in
# the copy for pytest to find them) -- the mutated tree must be a faithful,
# complete copy of everything a real test run needs.
_COPY_IGNORE = shutil.ignore_patterns(
    ".git", "__pycache__", "*.pyc", ".pytest_cache", ".hypothesis", ".mypy_cache",
    ".ruff_cache", "build", "dist", "*.egg-info", "artifacts", "node_modules",
    "model",
)

# pytest exit codes: 0 OK, 1 TESTS_FAILED (the only code that means "the
# mutation was genuinely detected"), 2 INTERRUPTED, 3 INTERNAL_ERROR,
# 4 USAGE_ERROR, 5 NO_TESTS_COLLECTED. Codes 2-5 mean the HARNESS is broken
# (wrong test path, import error, crash) -- never silently counted as a
# detection, which would be a false positive hiding a real gap.
_PYTEST_TESTS_FAILED = 1


class MutationHarnessError(RuntimeError):
    """The mutation could not be applied as specified -- fail loudly rather
    than silently mutating nothing or the wrong thing."""


@dataclass
class MutantResult:
    defect_id: str
    description: str
    detected: bool
    returncode: int
    duration_seconds: float
    detector_tests: List[str] = field(default_factory=list)
    output_tail: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "defect_id": self.defect_id, "description": self.description,
            "detected": self.detected, "returncode": self.returncode,
            "duration_seconds": round(self.duration_seconds, 2),
            "detector_tests": self.detector_tests, "output_tail": self.output_tail,
        }


@dataclass
class MutationReport:
    results: List[MutantResult]

    @property
    def total(self) -> int:
        return len(self.results)

    @property
    def detected_count(self) -> int:
        return sum(1 for r in self.results if r.detected)

    @property
    def mutation_score(self) -> float:
        return (self.detected_count / self.total) if self.total else 0.0

    @property
    def survived(self) -> List[MutantResult]:
        return [r for r in self.results if not r.detected]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total": self.total, "detected": self.detected_count,
            "mutation_score": round(self.mutation_score, 4),
            "survived_defect_ids": [r.defect_id for r in self.survived],
            "results": [r.to_dict() for r in self.results],
        }


def _copy_repo(dest: Path) -> None:
    shutil.copytree(REPO_ROOT, dest, ignore=_COPY_IGNORE)


def apply_mutation(defect: Defect, repo_copy: Path) -> None:
    path = repo_copy / defect.file_path
    if not path.is_file():
        raise MutationHarnessError(f"{defect.id}: {path} does not exist in the copied tree")
    text = path.read_text(encoding="utf-8")
    count = text.count(defect.find)
    if count != 1:
        raise MutationHarnessError(
            f"{defect.id}: expected the target text exactly once in {defect.file_path}, found {count} "
            "(the source has likely changed since this defect was written -- update mutation/defects.py)"
        )
    path.write_text(text.replace(defect.find, defect.replace, 1), encoding="utf-8")


def run_mutant(defect: Defect, *, timeout: float = 120.0) -> MutantResult:
    started = time.monotonic()
    with tempfile.TemporaryDirectory(prefix=f"mcc-mutant-{defect.id}-") as tmp:
        repo_copy = Path(tmp) / "repo"
        _copy_repo(repo_copy)
        apply_mutation(defect, repo_copy)

        pythonpath = f"{repo_copy / 'src'}:{repo_copy}:{repo_copy / 'sdk' / 'python' / 'src'}"
        proc = subprocess.run(
            [sys.executable, "-m", "pytest", "-q", *defect.detector_tests],
            cwd=str(repo_copy), env={"PYTHONPATH": pythonpath, "PATH": "/usr/bin:/bin:/usr/local/bin"},
            capture_output=True, text=True, timeout=timeout,
        )
        output = (proc.stdout + proc.stderr)
        if proc.returncode not in (0, _PYTEST_TESTS_FAILED):
            raise MutationHarnessError(
                f"{defect.id}: pytest exited {proc.returncode} (not a clean pass/fail) against "
                f"{defect.detector_tests} -- harness/detector-test problem, not a real mutation "
                f"result. Output:\n{output[-2000:]}"
            )
        return MutantResult(
            defect_id=defect.id, description=defect.description,
            detected=proc.returncode == _PYTEST_TESTS_FAILED, returncode=proc.returncode,
            duration_seconds=time.monotonic() - started,
            detector_tests=list(defect.detector_tests), output_tail=output[-2000:],
        )


def run_all_mutants(*, defects: Optional[List[Defect]] = None, timeout: float = 120.0) -> MutationReport:
    targets = defects if defects is not None else DEFECTS
    return MutationReport(results=[run_mutant(d, timeout=timeout) for d in targets])
