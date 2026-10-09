import csv
from pathlib import Path

from pydantic import ValidationError

from k4_assistant.models import Trade
from k4_assistant.parsers.base import TradeParser
from k4_assistant.parsers.errors import ParseError

REQUIRED_COLUMNS = {"date", "symbol", "side", "quantity", "price", "currency"}


class GenericCsvParser(TradeParser):
    def parse(self, path: Path) -> list[Trade]:
        trades: list[Trade] = []
        with path.open(newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            if reader.fieldnames is None:  # completely empty file
                return trades
            missing = REQUIRED_COLUMNS - set(reader.fieldnames)
            if missing:
                raise ParseError(f"Missing columns: {', '.join(sorted(missing))}")
            for row in reader:
                try:
                    trades.append(self._to_trade(row))
                except ValidationError as e:
                    raise ParseError(str(e), line=reader.line_num) from e
        return trades

    @staticmethod
    def _to_trade(row: dict[str, str]) -> Trade:
        return Trade.model_validate(
            {
                "trade_date": row["date"],
                "symbol": row["symbol"],
                "isin": row.get("isin") or None,
                "side": row["side"],
                "quantity": row["quantity"],
                "price": row["price"],
                "currency": row["currency"],
                "fee": row.get("fee") or "0",
            }
        )
