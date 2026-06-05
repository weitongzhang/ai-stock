"""Provider protocols for normalized market data."""

from __future__ import annotations

from typing import Protocol

from skill_lab.shared.enums import BarSpan
from skill_lab.shared.schemas import Bar, IndexEnvironment, MarketBreadth, ThemeScore


class DataProvider(Protocol):
    """Read-only interface expected by analysis services."""

    def get_bars(
        self,
        symbol: str,
        span: BarSpan = BarSpan.DAY1,
        limit: int = 250,
        until: str | None = None,
    ) -> list[Bar]:
        """Return normalized OHLCV bars."""

    def get_market_breadth(self, trade_date: str) -> MarketBreadth:
        """Return normalized market breadth for a trade date."""

    def get_index_environment(self, trade_date: str) -> list[IndexEnvironment]:
        """Return normalized index environment rows."""

    def get_theme_scores(self, trade_date: str) -> list[ThemeScore]:
        """Return normalized theme score rows."""

