from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from k4_assistant.parsers.errors import ParseError
from k4_assistant.parsers.generic import GenericCsvParser

HEADER = "date,symbol,isin,side,quantity,price,currency,fee\n"

DATA = Path(__file__).parent / "data"


def test_parses_valid_file() -> None:
    trades = GenericCsvParser().parse(DATA / "generic_trades.csv")
    assert len(trades) == 4
    assert trades[0].symbol == "VOLV-B"
    assert trades[0].quantity == Decimal(100)
    assert trades[0].trade_date == date(2025, 1, 15)


def test_bad_value_reports_line_number(tmp_path: Path) -> None:
    f = tmp_path / "bad.csv"
    f.write_text(HEADER + "2025-01-15,VOLV-B,,BUY,abc,250,SEK,0\n")
    with pytest.raises(ParseError) as exc:
        GenericCsvParser().parse(f)
    assert exc.value.line == 2


def test_missing_column_raises(tmp_path: Path) -> None:
    f = tmp_path / "nocol.csv"
    f.write_text("date,symbol\n2025-01-15,VOLV-B\n")
    with pytest.raises(ParseError):
        GenericCsvParser().parse(f)


def test_empty_file_returns_empty_list(tmp_path: Path) -> None:
    f = tmp_path / "empty.csv"
    f.write_text("")
    assert GenericCsvParser().parse(f) == []
