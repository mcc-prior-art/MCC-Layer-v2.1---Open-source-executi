"""MCC-side support for the VoltAgent governed integration.

These are NOT part of VoltAgent and NOT a new governance contract. They are the
existing MCC-Core deployment roles the VoltAgent integration runs against:

* :mod:`evaluator_quorum` — an independent N-of-M evaluator quorum. It holds the
  evaluator signing keys (which the VoltAgent process never sees), independently
  re-evaluates a proposal against the gateway, and only signs consensus votes for
  an executable (ALLOW/CONSTRAIN) decision, bound to the gateway-issued challenge
  nonce + policy hash. The gateway still verifies every vote — the quorum cannot
  force execution, and VoltAgent cannot forge a vote.
* :mod:`generate_config` — generate the evaluator keyset: PUBLIC consensus trust
  config for the gateway + PRIVATE keys for the quorum (never committed).

The signing primitive is the existing ``mcc_core.issue_vote``; no governance or
consensus logic is re-implemented here.
"""
