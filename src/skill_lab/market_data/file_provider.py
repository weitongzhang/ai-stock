"""File-backed provider for examples and offline smoke tests."""

from __future__ import annotations

import csv
from pathlib import Path

from skill_lab.market_data.normalizers import (
    normalize_index_environment,
    normalize_market_breadth,
    normalize_theme_score,
)
from skill_lab.market_data.providers import DataProvider
from skill_lab.market_data.quality import (
    DataQualityReport,
    check_index_environment,
    check_market_breadth,
    check_theme_scores,
    merge_reports,
)
from skill_lab.shared.enums import BarSpan, DataSource
from skill_lab.shared.schemas import Bar, IndexEnvironment, MarketBreadth, ThemeScore


class FileProvider(DataProvider):
    """Read normalized objects from the repository's examples directory."""

    def __init__(self, root: Path | str) -> None:
        self.root = Path(root)

    def get_bars(
        self,
        symbol: str,
        span: BarSpan = BarSpan.DAY1,
        limit: int = 250,
        until: str | None = None,
    ) -> list[Bar]:
        raise NotImplementedError("FileProvider bar loading will be added once OHLCV fixtures exist.")

    def get_market_breadth(self, trade_date: str) -> MarketBreadth:
        path = self.root / "examples" / "market" / "market-breadth" / f"{trade_date}-market-breadth.csv"
        rows = read_csv(path)
        return normalize_market_breadth(trade_date, rows, source=DataSource.FILE)

    def get_index_environment(self, trade_date: str) -> list[IndexEnvironment]:
        path = self.root / "examples" / "market" / "index-environment" / f"{trade_date}-index-environment.csv"
        rows = read_csv(path)
        return [normalize_index_environment(row, source=DataSource.FILE) for row in rows]

    def get_theme_scores(self, trade_date: str) -> list[ThemeScore]:
        path = self.root / "examples" / "market" / "market-flow" / f"{trade_date}-market-flow.csv"
        rows = read_csv(path)
        return [normalize_theme_score(trade_date, row) for row in rows]

    def check_daily_inputs(self, trade_date: str) -> DataQualityReport:
        reports = [
            check_market_breadth(self.get_market_breadth(trade_date)),
            check_index_environment(self.get_index_environment(trade_date), trade_date=trade_date),
            check_theme_scores(self.get_theme_scores(trade_date), trade_date=trade_date),
        ]
        return merge_reports(f"daily_inputs:{trade_date}", reports)


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError(path)
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        return [dict(row) for row in csv.DictReader(file)]
