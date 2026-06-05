"""Trading calendar helpers used by daily workflows."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path


def parse_date(value: str | date) -> date:
    if isinstance(value, date):
        return value
    return datetime.strptime(value, "%Y-%m-%d").date()


def format_date(value: date) -> str:
    return value.isoformat()


@dataclass(slots=True)
class WeekdayTradeCalendar:
    """Fallback A-share-like calendar that treats weekdays as trade days."""

    holidays: set[str] | None = None

    def is_trade_date(self, value: str | date) -> bool:
        day = parse_date(value)
        if day.weekday() >= 5:
            return False
        return day.isoformat() not in (self.holidays or set())

    def previous_trade_date(self, value: str | date, n: int = 1) -> str:
        day = parse_date(value)
        found = 0
        while found < n:
            day -= timedelta(days=1)
            if self.is_trade_date(day):
                found += 1
        return format_date(day)

    def next_trade_date(self, value: str | date, n: int = 1) -> str:
        day = parse_date(value)
        found = 0
        while found < n:
            day += timedelta(days=1)
            if self.is_trade_date(day):
                found += 1
        return format_date(day)

    def latest_trade_date_on_or_before(self, value: str | date) -> str:
        day = parse_date(value)
        while not self.is_trade_date(day):
            day -= timedelta(days=1)
        return format_date(day)


class FileTradeCalendar(WeekdayTradeCalendar):
    """Calendar backed by a CSV containing date and is_trade_date columns."""

    def __init__(self, path: Path | str) -> None:
        self.path = Path(path)
        self.trade_dates = load_trade_dates(self.path)
        super().__init__(holidays=set())

    def is_trade_date(self, value: str | date) -> bool:
        return parse_date(value).isoformat() in self.trade_dates


def load_trade_dates(path: Path) -> set[str]:
    if not path.exists():
        raise FileNotFoundError(path)
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        rows = list(csv.DictReader(file))
    trade_dates: set[str] = set()
    for row in rows:
        day = str(row.get("date") or row.get("trade_date") or "").strip()
        flag = str(row.get("is_trade_date") or row.get("is_open") or "1").strip().lower()
        if day and flag not in {"0", "false", "no"}:
            trade_dates.add(day)
    return trade_dates
