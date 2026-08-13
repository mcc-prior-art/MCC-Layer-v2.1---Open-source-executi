"""Independent Assurance runner spine (PR #71, Workstream L).

Discovers and executes every workstream test module under
``assurance/tests/`` in-process (no subprocess-per-module, no extra
dependency such as ``pytest-json-report``) via a small pytest result-
collection plugin, and produces a machine-readable ``RunReport`` the
evidence-bundle builder (``assurance.evidence``) and CLI
(``assurance.cli``) both consume.

This module never decides pass/fail itself -- it faithfully relays what
pytest reported. A workstream module that does not exist yet is simply
absent from the report; the runner never fabricates a result for it.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
TESTS_DIR = REPO_ROOT / "assurance" / "tests"

#: Best-effort, human-facing workstream labels. Purely cosmetic -- absence
#: from this map never excludes a module from being discovered and run.
WORKSTREAM_LABELS: Dict[str, str] = {
    "test_boundary_guards.py": "ARCH-GUARD",
    "test_exclusive_execution_path.py": "A",
    "test_execution_atomicity.py": "B",
    "test_decision_authority_containment.py": "C",
    "test_canonical_action_differential.py": "D",
    "test_replay_resistance.py": "E",
    "test_constraint_enforcement.py": "F",
    "test_audit_survivability.py": "G",
    "test_property_based.py": "H",
    "test_negative_control.py": "NEGATIVE-CONTROL",
    "test_semantic_equivalence.py": "K",
}


@dataclass
class TestOutcome:
    __test__ = False  # not a pytest test class despite the name

    nodeid: str
    outcome: str  # "passed" | "failed" | "skipped"
    duration: float
    longrepr: Optional[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "nodeid": self.nodeid, "outcome": self.outcome,
            "duration": self.duration, "longrepr": self.longrepr,
        }


@dataclass
class ModuleResult:
    path: str
    workstream: str
    tests: List[TestOutcome] = field(default_factory=list)
    collection_error: Optional[str] = None

    @property
    def passed(self) -> int:
        return sum(1 for t in self.tests if t.outcome == "passed")

    @property
    def failed(self) -> int:
        return sum(1 for t in self.tests if t.outcome == "failed")

    @property
    def skipped(self) -> int:
        return sum(1 for t in self.tests if t.outcome == "skipped")

    @property
    def status(self) -> str:
        if self.collection_error:
            return "ERROR"
        if self.failed:
            return "FAIL"
        if not self.tests:
            return "EMPTY"
        return "PASS"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "path": self.path, "workstream": self.workstream, "status": self.status,
            "passed": self.passed, "failed": self.failed, "skipped": self.skipped,
            "collection_error": self.collection_error,
            "tests": [t.to_dict() for t in self.tests],
        }


@dataclass
class RunReport:
    run_id: str
    started_at: str
    finished_at: str
    modules: List[ModuleResult] = field(default_factory=list)

    @property
    def summary(self) -> Dict[str, Any]:
        total = sum(len(m.tests) for m in self.modules)
        passed = sum(m.passed for m in self.modules)
        failed = sum(m.failed for m in self.modules)
        skipped = sum(m.skipped for m in self.modules)
        errored = sum(1 for m in self.modules if m.collection_error)
        return {
            "total_tests": total, "passed": passed, "failed": failed, "skipped": skipped,
            "modules_run": len(self.modules), "modules_errored": errored,
            "overall_status": "FAIL" if (failed or errored) else "PASS",
        }

    def to_dict(self) -> Dict[str, Any]:
        return {
            "run_id": self.run_id, "started_at": self.started_at, "finished_at": self.finished_at,
            "summary": self.summary, "modules": [m.to_dict() for m in self.modules],
        }


class _ResultCollector:
    """Minimal pytest plugin: records one TestOutcome per test's ``call``
    phase (or its ``setup``/``teardown`` phase if that phase itself failed,
    e.g. a fixture error) -- never both, so counts never double."""

    def __init__(self) -> None:
        self.outcomes: List[TestOutcome] = []
        self.collection_errors: List[str] = []

    def pytest_runtest_logreport(self, report: "pytest.TestReport") -> None:  # noqa: F821
        record = report.when == "call" or (report.when in ("setup", "teardown") and report.outcome == "failed")
        if not record:
            return
        self.outcomes.append(TestOutcome(
            nodeid=report.nodeid, outcome=report.outcome, duration=report.duration,
            longrepr=str(report.longrepr) if report.longrepr else None,
        ))

    def pytest_collectreport(self, report: "pytest.CollectReport") -> None:  # noqa: F821
        if report.failed:
            self.collection_errors.append(str(report.longrepr))


def discover_test_modules(tests_dir: Path = TESTS_DIR) -> List[Path]:
    return sorted(
        p for p in tests_dir.glob("test_*.py")
        if p.name != "__init__.py"
    )


def run_module(path: Path, *, extra_args: Optional[List[str]] = None) -> ModuleResult:
    collector = _ResultCollector()
    args = [str(path), "-q", "-p", "no:cacheprovider"] + (extra_args or [])
    exit_code = pytest.main(args, plugins=[collector])
    workstream = WORKSTREAM_LABELS.get(path.name, path.stem)
    collection_error = "; ".join(collector.collection_errors) or None
    if collection_error is None and exit_code == pytest.ExitCode.INTERRUPTED:
        collection_error = "pytest run interrupted"
    resolved = path.resolve()
    rel_path = str(resolved.relative_to(REPO_ROOT)) if REPO_ROOT in resolved.parents else str(resolved)
    return ModuleResult(
        path=rel_path, workstream=workstream, tests=collector.outcomes,
        collection_error=collection_error,
    )


def run_all(*, modules: Optional[List[Path]] = None, extra_args: Optional[List[str]] = None) -> RunReport:
    started = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    targets = modules if modules is not None else discover_test_modules()
    results = [run_module(p, extra_args=extra_args) for p in targets]
    finished = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    return RunReport(run_id=str(uuid.uuid4()), started_at=started, finished_at=finished, modules=results)
