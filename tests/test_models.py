from decimal import Decimal

import pytest
from pydantic import ValidationError

from k4_assistant.models import Trade

VALID: dict[str, object] = {
    "trade_date": "2025-01-15",
    "symbol": "VOLV-B",
    "side": "BUY",
    "quantity": "100",
    "price": "250.50",
    "currency": "SEK",
}


def make(**overrides: object) -> Trade:
    return Trade.model_validate({**VALID, **overrides})


def test_valid_trade() -> None:
    trade = make()
    assert trade.quantity == Decimal(100)
    assert trade.fee == Decimal(0)


def test_negative_quantity_rejected() -> None:
    with pytest.raises(ValidationError):
        make(quantity="-5")


def test_bad_currency_rejected() -> None:
    with pytest.raises(ValidationError):
        make(currency="sek")


def test_negative_fee_rejected() -> None:
    with pytest.raises(ValidationError):
        make(fee="-1")
