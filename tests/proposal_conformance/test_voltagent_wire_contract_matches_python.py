"""VoltAgent (TypeScript) is verified for real in
``integrations/voltagent/tests/mcc-client-unit.test.ts`` (its own vitest
process — this repo does not run Node from Python tests). What THIS test
guards is drift between that TS suite's asserted wire shape and the Python
canonical model: both currently assert the exact same five-field set
(``action``, ``actor``, ``logical_operation_id``, ``payload``, ``resource``).
If either side ever adds/removes/renames a field without updating the other,
this is the test that catches it.
"""

from __future__ import annotations

from pathlib import Path

from mcc_proposal.models import ALLOWED_REQUEST_FIELDS

TS_TEST_FILE = (
    Path(__file__).resolve().parents[2]
    / "integrations" / "voltagent" / "tests" / "mcc-client-unit.test.ts"
)


def test_python_canonical_field_set_is_pinned():
    assert ALLOWED_REQUEST_FIELDS == frozenset({
        "logical_operation_id", "actor", "action", "resource", "payload",
    })


def test_ts_client_test_asserts_the_identical_field_set():
    """The TS unit test hardcodes the sorted field list it expects
    ``submitProposal`` to send. Assert that literal is present verbatim and
    matches the Python allow-list, sorted the same way — a cheap, real
    tripwire against silent cross-language drift without needing to execute
    the TypeScript."""
    source = TS_TEST_FILE.read_text(encoding="utf-8")
    expected_literal = '["action", "actor", "logical_operation_id", "payload", "resource"]'
    assert expected_literal in source, (
        "the VoltAgent TS unit test's asserted proposal field list has changed; "
        "update it AND mcc_proposal.models.ALLOWED_REQUEST_FIELDS together"
    )
    assert sorted(ALLOWED_REQUEST_FIELDS) == sorted(
        f.strip('"') for f in expected_literal.strip("[]").split(", ")
    )
