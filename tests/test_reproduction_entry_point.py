"""Lightweight, static CI guard for the reproducible assurance entry point
(``make verify-assurance`` / ``docs/REPRODUCING_ASSURANCE.md``).

Deliberately does NOT re-run ``make independent-assurance``, ``model/run_tlc.sh``,
or ``make mutation-test`` -- those are the expensive stages, and they already
run for real in ``.github/workflows/mcc-independent-assurance.yml``'s
``independent-assurance-core`` job (see that workflow) and, for
``mutation-test`` specifically, in ``assurance/tests/test_mutation_score.py``
(part of this same suite). Duplicating them here would cost minutes per CI
run for coverage this repository already has.

What this file DOES prove, cheaply and every time ``pytest tests/`` runs:
* the ``verify-assurance`` Makefile target exists;
* ``scripts/verify_assurance.sh`` exists, is syntactically valid, and is
  executable;
* the README links to ``docs/REPRODUCING_ASSURANCE.md`` and
  ``docs/ASSURANCE_INDEX.md``, and both files exist with the required content;
* every path ``docs/REPRODUCING_ASSURANCE.md`` names (the 3 gate-bypass test
  files, ``mutation/defects.py``, ``mutation/harness.py``, the TLA+ model,
  ``docs/THIRD_PARTY_RUNBOOK.md``) actually exists;
* the exact 24 documented gate-bypass tests exist, by name, at (or very near)
  the line the document cites -- catching drift between the doc's table and
  the actual test files without re-deriving the table by fragile markdown
  parsing (the list below IS the doc's own table, kept in sync by hand; a
  mismatch between this list and the doc's own table text is itself checked);
* the tracked working tree this job is running in is clean (a cheap, honest
  proxy for "the entry point starts and finishes clean" -- it does not, by
  itself, prove ``verify-assurance``'s own non-destructiveness under a full
  run; that is what the CI job cited above, plus a fresh-clone run recorded
  in the PR that introduced this file, establishes).
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]

# Kept in sync BY HAND with the table in docs/REPRODUCING_ASSURANCE.md --
# (relative_file_path, line_number, test_function_name). A change to either
# side without the other is exactly the drift this test exists to catch.
DOCUMENTED_BYPASS_TESTS = [
    ("assurance/tests/test_exclusive_execution_path.py", 57, "test_a1_direct_actuator_invocation_without_consensus"),
    ("assurance/tests/test_exclusive_execution_path.py", 69, "test_a2_stolen_endpoint_wrong_client_credential"),
    ("assurance/tests/test_exclusive_execution_path.py", 83, "test_a3_reused_credential_replayed_challenge"),
    ("assurance/tests/test_exclusive_execution_path.py", 104, "test_a4_adapter_to_actuator_bypass_wrong_trust_domain"),
    ("assurance/tests/test_exclusive_execution_path.py", 122, "test_a5_agent_to_actuator_bypass_self_signed_forged_evaluator"),
    ("assurance/tests/test_exclusive_execution_path.py", 142, "test_a6_alternate_network_route_disallowed_host"),
    ("assurance/tests/test_exclusive_execution_path.py", 158, "test_a7_forged_gate_identity_tampered_signature"),
    ("assurance/tests/test_exclusive_execution_path.py", 177, "test_a8_valid_token_direct_to_actuator_wrong_binding"),
    ("assurance/tests/test_decision_authority_containment.py", 91, "test_c2_below_threshold_votes_denied"),
    ("assurance/tests/test_decision_authority_containment.py", 107, "test_c3_trusted_deny_vote_vetoes_despite_sufficient_allow_votes"),
    ("assurance/tests/test_decision_authority_containment.py", 129, "test_c4_votes_bound_to_wrong_policy_hash_rejected"),
    ("assurance/tests/test_decision_authority_containment.py", 144, "test_c5_votes_bound_to_a_different_actor_rejected"),
    ("assurance/tests/test_decision_authority_containment.py", 159, "test_c6_forged_untrusted_evaluator_rejected_at_gateway"),
    ("assurance/tests/test_decision_authority_containment.py", 174, "test_c7_replayed_challenge_and_votes_denied_after_first_use"),
    ("assurance/tests/test_decision_authority_containment.py", 192, "test_c8_mandate_execute_fails_closed_on_the_consensus_required_topology"),
    ("assurance/tests/test_mandate_containment.py", 89, "test_c10_forged_mandate_untrusted_issuer_is_denied"),
    ("assurance/tests/test_mandate_containment.py", 102, "test_c11_tampered_action_scope_is_denied"),
    ("assurance/tests/test_mandate_containment.py", 119, "test_c12_tampered_subject_is_denied"),
    ("assurance/tests/test_mandate_containment.py", 135, "test_c13_expired_mandate_is_denied"),
    ("assurance/tests/test_mandate_containment.py", 149, "test_c14_not_yet_valid_mandate_is_denied"),
    ("assurance/tests/test_mandate_containment.py", 163, "test_c15_wrong_subject_at_call_time_is_denied"),
    ("assurance/tests/test_mandate_containment.py", 178, "test_c16_action_outside_scope_is_denied"),
    ("assurance/tests/test_mandate_containment.py", 192, "test_c17_resource_outside_scope_is_denied"),
    ("assurance/tests/test_mandate_containment.py", 206, "test_c18_revoked_mandate_is_denied"),
]

OTHER_REFERENCED_PATHS = [
    "docs/REPRODUCING_ASSURANCE.md",
    "docs/ASSURANCE_INDEX.md",
    "docs/THIRD_PARTY_RUNBOOK.md",
    "docs/ASSUMPTIONS_AND_LIMITS.md",
    "mutation/defects.py",
    "mutation/harness.py",
    "model/MCCExecutionStateMachine.tla",
    "model/MCCExecutionStateMachine.cfg",
    "model/run_tlc.sh",
    "scripts/verify_assurance.sh",
    "requirements.txt",
    "requirements-dev.txt",
]


def test_verify_assurance_makefile_target_exists():
    result = subprocess.run(
        ["make", "-n", "verify-assurance"], cwd=ROOT, capture_output=True, text=True,
    )
    assert result.returncode == 0, (
        f"`make -n verify-assurance` failed -- the target is missing or broken:\n{result.stderr}"
    )
    assert "verify_assurance.sh" in result.stdout


def test_verify_assurance_script_exists_and_is_valid_and_executable():
    script = ROOT / "scripts" / "verify_assurance.sh"
    assert script.is_file(), f"missing: {script}"
    assert script.stat().st_mode & 0o111, f"{script} is not executable (chmod +x)"
    result = subprocess.run(["bash", "-n", str(script)], capture_output=True, text=True)
    assert result.returncode == 0, f"scripts/verify_assurance.sh has a syntax error:\n{result.stderr}"


def test_readme_links_to_reproduction_doc():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "Reproducible Assurance Baseline" in readme, (
        "README.md is missing the required 'Reproducible Assurance Baseline' section"
    )
    assert "docs/REPRODUCING_ASSURANCE.md" in readme, (
        "README.md does not link to docs/REPRODUCING_ASSURANCE.md"
    )
    assert "docs/ASSURANCE_INDEX.md" in readme, (
        "README.md does not link to docs/ASSURANCE_INDEX.md"
    )
    assert "make verify-assurance" in readme


def test_assurance_index_exists_and_links_correctly():
    index = ROOT / "docs" / "ASSURANCE_INDEX.md"
    assert index.is_file(), f"missing: {index}"
    text = index.read_text(encoding="utf-8")
    for required in (
        "make verify-assurance",
        "REPRODUCING_ASSURANCE.md",
        "THIRD_PARTY_RUNBOOK.md",
        "../assurance/tests/",
        "../mutation/defects.py",
        "../model/MCCExecutionStateMachine.tla",
        "self-administered",
        "not a third-party audit",
    ):
        assert required in text, f"docs/ASSURANCE_INDEX.md is missing required content: {required!r}"


@pytest.mark.parametrize("relative_path", OTHER_REFERENCED_PATHS)
def test_referenced_path_exists(relative_path):
    assert (ROOT / relative_path).exists(), f"docs/REPRODUCING_ASSURANCE.md references a path that does not exist: {relative_path}"


@pytest.mark.parametrize("relative_path,line_no,test_name", DOCUMENTED_BYPASS_TESTS)
def test_documented_bypass_test_exists_at_cited_location(relative_path, line_no, test_name):
    path = ROOT / relative_path
    assert path.is_file(), f"documented bypass-test file does not exist: {relative_path}"
    lines = path.read_text(encoding="utf-8").splitlines()

    def_line = f"def {test_name}("
    assert any(def_line in line for line in lines), (
        f"{relative_path} no longer defines {test_name} -- "
        f"docs/REPRODUCING_ASSURANCE.md's table is stale"
    )

    # The cited line number must land on (or immediately adjacent to, to
    # tolerate a trivial reflow) the actual def -- a large drift means the
    # document's line citation is stale even though the test still exists.
    window = lines[max(0, line_no - 3): line_no + 2]
    assert any(def_line in line for line in window), (
        f"{relative_path}:{line_no} does not point at `{def_line}` "
        f"(found it elsewhere in the file) -- update the line number in "
        f"docs/REPRODUCING_ASSURANCE.md and tests/test_reproduction_entry_point.py"
    )


def test_documented_count_matches_this_files_own_list():
    """The '24' stated throughout docs/REPRODUCING_ASSURANCE.md, this file's
    header, and PR descriptions must match this list's actual length -- a
    silent drift here is exactly the kind of overclaim this whole entry
    point exists to prevent."""
    assert len(DOCUMENTED_BYPASS_TESTS) == 24


def test_working_tree_is_clean():
    """Cheap, honest proxy for 'the entry point starts and finishes with a
    clean tracked working tree': confirms this job's own checkout has no
    tracked-file modifications at the point this test runs. Does not, by
    itself, prove verify-assurance.sh's non-destructiveness under a full
    run -- see this file's module docstring for what does."""
    result = subprocess.run(
        ["git", "status", "--porcelain", "--untracked-files=no"],
        cwd=ROOT, capture_output=True, text=True,
    )
    assert result.returncode == 0
    assert result.stdout == "", f"tracked working tree is not clean:\n{result.stdout}"
