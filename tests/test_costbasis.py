from decimal import Decimal

import pytest

from k4_assistant.costbasis import CostBasisError, calculate_gains
from k4_assistant.models import Trade


def trade(
    day: str,
    side: str,
    qty: str,
    price: str,
    fee: str = "0",
    symbol: str = "VOLV-B",
    currency: str = "SEK",
) -> Trade:
    return Trade.model_validate(
        {
            "trade_date": day,
            "symbol": symbol,
            "side": side,
            "quantity": qty,
            "price": price,
            "fee": fee,
            "currency": currency,
        }
    )


def test_sale_uses_average_cost() -> None:
    trades = [
        trade("2025-01-15", "BUY", "100", "250.50", "39"),
        trade("2025-03-10", "BUY", "50", "262.00", "39"),
        trade("2025-06-20", "SELL", "80", "280.25", "39"),
    ]
    [result] = calculate_gains(trades)
    assert result.proceeds == Decimal("22381.00")
    assert result.cost_basis == Decimal("20388.27")
    assert result.gain == Decimal("1992.73")


def test_loss_is_negative() -> None:
    trades = [trade("2025-01-01", "BUY", "10", "100"), trade("2025-02-01", "SELL", "10", "80")]
    [result] = calculate_gains(trades)
    assert result.gain == Decimal("-200.00")


def test_symbols_are_tracked_separately() -> None:
    trades = [
        trade("2025-01-01", "BUY", "10", "100", symbol="AAA"),
        trade("2025-01-02", "BUY", "10", "500", symbol="BBB"),
        trade("2025-02-01", "SELL", "10", "110", symbol="AAA"),
    ]
    [result] = calculate_gains(trades)
    assert result.gain == Decimal("100.00")


def test_unsorted_input_is_handled() -> None:
    trades = [trade("2025-02-01", "SELL", "10", "110"), trade("2025-01-01", "BUY", "10", "100")]
    [result] = calculate_gains(trades)
    assert result.gain == Decimal("100.00")


def test_selling_more_than_held_raises() -> None:
    trades = [trade("2025-01-01", "BUY", "5", "100"), trade("2025-02-01", "SELL", "10", "110")]
    with pytest.raises(CostBasisError):
        calculate_gains(trades)


def test_non_sek_raises() -> None:
    with pytest.raises(CostBasisError):
        calculate_gains([trade("2025-01-01", "BUY", "5", "100", currency="USD")])
