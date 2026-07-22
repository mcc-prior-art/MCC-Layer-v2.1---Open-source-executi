"""Adapter SDK error surface — reuses the existing contract taxonomy (PR #50).

The SDK introduces **no new stable error taxonomy**. Every SDK failure carries an
existing :class:`mcc_client.contract.ContractErrorCode`, so there is one set of
stable codes across the platform. SDK failures are always fail-closed and never an
authorization.
"""

from __future__ import annotations

from mcc_client.contract import ContractErrorCode, category_of


class AdapterSDKError(Exception):
    """A fail-closed Adapter SDK error. Always carries a blocking contract code."""

    def __init__(self, message: str, *,
                 code: ContractErrorCode = ContractErrorCode.CONTRACT_FIELD_INVALID) -> None:
        self.code = code
        super().__init__(message)

    @property
    def category(self) -> str:
        return category_of(self.code).value

    def to_dict(self) -> dict:
        return {"error": str(self), "error_code": self.code.value,
                "error_category": self.category}


__all__ = ["AdapterSDKError"]
