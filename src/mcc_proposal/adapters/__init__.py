"""Thin per-framework proposal/status facades (Section 13).

Every module here reduces to exactly:

    framework tool/node argument shape
        -> ProposalRequestV1
        -> ProposalBackend.submit_proposal() / get_operation_status()
        -> framework-native return shape

No module in this package computes a binding, evaluates policy, infers
status, or calls an actuator/upstream. See
``tests/test_proposal_service_architecture_guards.py``.
"""

from __future__ import annotations
