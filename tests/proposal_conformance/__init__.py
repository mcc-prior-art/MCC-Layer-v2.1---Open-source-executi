"""Adapter Conformance Suite — Universal Proposal Service Phase 1 (Section 15).

Every supported adapter (Generic HTTP, MCP, LangGraph, CrewAI, AutoGen, the
native Python SDK) is wrapped behind the identical two-method protocol:

    submit(request: dict) -> ProposalReceiptV1 dict
    status(logical_operation_id: str) -> OperationStatusV1 dict

and exercised through ``run_common_scenarios`` in ``harness.py`` so no
adapter can drift from what the others observe. VoltAgent (TypeScript) is
verified separately, at the wire-contract level, by
``integrations/voltagent/tests/mcc-client-unit.test.ts`` — see
``test_voltagent_wire_contract_matches_python.py`` for the drift guard
between the two.
"""

from __future__ import annotations
