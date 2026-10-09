from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from pydantic import BaseModel

from k4_assistant.models import Side, Trade


class CostBasisError(Exception):
    """Raised when gains cannot be calculated from the given trades."""

    pass


class RealizedGain(BaseModel):
    symbol: str
    sale_date: date
    quantity: Decimal
    proceeds: Decimal
    cost_basis: Decimal
    gain: Decimal


@dataclass
class Position:
    quantity: Decimal = Decimal(0)
    total_cost: Decimal = Decimal(0)


CENT = Decimal("0.01")


def calculate_gains(trades: list[Trade]) -> list[RealizedGain]:
    for trade in trades:
        if trade.currency != "SEK":
            raise CostBasisError(f"Only SEK is supported, got {trade.currency} for {trade.symbol}")

    positions: defaultdict[str, Position] = defaultdict(Position)
    results: list[RealizedGain] = []

    for trade in sorted(trades, key=lambda x: x.trade_date):
        position = positions[trade.symbol]

        if trade.side == Side.BUY:
            position.quantity += trade.quantity
            position.total_cost += trade.quantity * trade.price + trade.fee
            continue

        if trade.quantity > position.quantity:
            raise CostBasisError(
                f"Cannot sell {trade.quantity} {trade.symbol} on {trade.trade_date}: "
                f"only {position.quantity} held"
            )

        cost_basis = position.total_cost * trade.quantity / position.quantity
        proceeds = trade.quantity * trade.price - trade.fee
        position.quantity -= trade.quantity
        position.total_cost -= cost_basis

        results.append(
            RealizedGain(
                symbol=trade.symbol,
                sale_date=trade.trade_date,
                quantity=trade.quantity,
                proceeds=proceeds.quantize(CENT),
                cost_basis=cost_basis.quantize(CENT),
                gain=(proceeds - cost_basis).quantize(CENT),
            )
        )

    return results
