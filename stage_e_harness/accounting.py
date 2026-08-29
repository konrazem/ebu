"""Exact synthetic accounting primitives; no model dynamics live here."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Iterable

from .canonical import Refusal, canonical_digest


@dataclass(frozen=True)
class LedgerDelta:
    account: str
    amount: Fraction
    unit: str


@dataclass(frozen=True)
class Receipt:
    receipt_id: str
    inputs: tuple[LedgerDelta, ...]
    outputs: tuple[LedgerDelta, ...]
    boundary: tuple[LedgerDelta, ...] = ()

    def identity(self) -> str:
        return canonical_digest(
            {
                "receipt_id": self.receipt_id,
                "inputs": [_delta_value(value) for value in self.inputs],
                "outputs": [_delta_value(value) for value in self.outputs],
                "boundary": [_delta_value(value) for value in self.boundary],
            }
        )


def _delta_value(delta: LedgerDelta) -> dict[str, object]:
    return {
        "account": delta.account,
        "numerator": delta.amount.numerator,
        "denominator": delta.amount.denominator,
        "unit": delta.unit,
    }


def fold_receipts(receipts: Iterable[Receipt]) -> dict[tuple[str, str], Fraction]:
    ledger: dict[tuple[str, str], Fraction] = {}
    seen: set[str] = set()
    for receipt in receipts:
        if receipt.receipt_id in seen:
            raise Refusal("duplicate receipt identity")
        seen.add(receipt.receipt_id)
        for delta in receipt.inputs:
            key = (delta.account, delta.unit)
            ledger[key] = ledger.get(key, Fraction()) - delta.amount
        for delta in (*receipt.outputs, *receipt.boundary):
            key = (delta.account, delta.unit)
            ledger[key] = ledger.get(key, Fraction()) + delta.amount
    return ledger


def assert_closed(receipts: Iterable[Receipt], *, account: str, unit: str) -> None:
    residual = fold_receipts(receipts).get((account, unit), Fraction())
    if residual != 0:
        raise Refusal(f"unreconciled exact ledger residual: {residual}")
