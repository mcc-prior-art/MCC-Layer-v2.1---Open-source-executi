"""Normative v1.0 implementation-conformance baseline tooling.

Traces every normative requirement in the four MCC Specification Program
documents (MCC-CP-001, MCC-EB-001, MCC-CM-001, MCC-TC-001) to implementation
code, automated tests, and evidence artifacts, and records an explicit,
honest conformance status for each.

This package does not modify, reinterpret, or weaken the normative
specifications. It is observational tooling only: specifications define
requirements; this package evaluates the repository against them.

It does not certify MCC-Core or any adapter. See
``conformance/normative-v1.0/README.md`` for what the baseline proves and
does not prove.
"""

from mcc_conformance.models import (
    ALLOWED_STATUSES,
    NORMATIVE_KEYWORDS,
    Requirement,
)

__all__ = ["Requirement", "ALLOWED_STATUSES", "NORMATIVE_KEYWORDS"]
