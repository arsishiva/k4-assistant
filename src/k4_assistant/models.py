from datetime import date
from decimal import Decimal
from enum import StrEnum

from pydantic import BaseModel, Field, field_validator


class Side(StrEnum):
    BUY = "BUY"
    SELL = "SELL"


class Trade(BaseModel):
    trade_date: date
    symbol: str
    isin: str | None = None
    side: Side
    quantity: Decimal = Field(gt=0)
    price: Decimal = Field(gt=0)
    currency: str
    fee: Decimal = Field(default=Decimal(0), ge=0)

    @field_validator("currency")
    @classmethod
    def check_currency(cls, v: str) -> str:
        if len(v) != 3 or not v.isalpha() or not v.isupper():
            raise ValueError("currency must be a 3-letter uppercase code")
        return v
