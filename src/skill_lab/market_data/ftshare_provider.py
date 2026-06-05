"""FTShare-backed provider adapter.

This adapter wraps the existing `skills/market-data/ftshare-market-data/run.py`
entrypoint. It keeps network and API details outside analysis services.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable

from skill_lab.market_data.providers import DataProvider
from skill_lab.market_data.symbols import to_ftshare_index_symbol, to_ftshare_stock_symbol
from skill_lab.shared.enums import BarSpan, DataSource
from skill_lab.shared.schemas import Bar, IndexEnvironment, MarketBreadth, ThemeScore


Runner = Callable[[list[str]], dict[str, Any]]


SPAN_TO_FTSHARE = {
    BarSpan.DAY1: "DAY1",
    BarSpan.WEEK1: "WEEK1",
    BarSpan.MONTH1: "MONTH1",
    BarSpan.YEAR1: "YEAR1",
}


class FTShareProvider(DataProvider):
    """Provider that delegates to the local FTShare skill runner."""

    def __init__(
        self,
        repo_root: Path | str,
        runner: Runner | None = None,
        python_executable: str | None = None,
    ) -> None:
        self.repo_root = Path(repo_root)
        self.run_py = self.repo_root / "skills" / "market-data" / "ftshare-market-data" / "run.py"
        self.runner = runner or self._run
        self.python_executable = python_executable or sys.executable

    def get_bars(
        self,
        symbol: str,
        span: BarSpan = BarSpan.DAY1,
        limit: int = 250,
        until: str | None = None,
    ) -> list[Bar]:
        ft_span = SPAN_TO_FTSHARE.get(span)
        if ft_span is None:
            raise ValueError(f"Unsupported FTShare bar span: {span}")
        args = [
            "stock-ohlcs",
            "--stock",
            to_ftshare_stock_symbol(symbol),
            "--span",
            ft_span,
            "--limit",
            str(limit),
        ]
        if until:
            raise NotImplementedError("until datetime conversion to until_ts_ms is not implemented yet.")
        data = self.runner(args)
        return normalize_ftshare_bars(symbol, data, span=span)

    def get_index_bars(
        self,
        symbol: str,
        span: BarSpan = BarSpan.DAY1,
        limit: int = 250,
    ) -> list[Bar]:
        ft_span = SPAN_TO_FTSHARE.get(span)
        if ft_span is None:
            raise ValueError(f"Unsupported FTShare bar span: {span}")
        data = self.runner([
            "index-ohlcs",
            "--index",
            to_ftshare_index_symbol(symbol),
            "--span",
            ft_span,
            "--limit",
            str(limit),
        ])
        return normalize_ftshare_bars(symbol, data, span=span)

    def get_market_breadth(self, trade_date: str) -> MarketBreadth:
        raise NotImplementedError("FTShare market breadth endpoint is not wired yet.")

    def get_index_environment(self, trade_date: str) -> list[IndexEnvironment]:
        raise NotImplementedError("Index environment is an analysis service, not a direct FTShare endpoint yet.")

    def get_theme_scores(self, trade_date: str) -> list[ThemeScore]:
        raise NotImplementedError("Theme scores are computed by sector analysis, not FTShare.")

    def _run(self, args: list[str]) -> dict[str, Any]:
        if not self.run_py.exists():
            raise FileNotFoundError(self.run_py)
        completed = subprocess.run(
            [self.python_executable, str(self.run_py), *args],
            cwd=self.repo_root,
            text=True,
            capture_output=True,
            check=True,
        )
        return json.loads(completed.stdout)


def normalize_ftshare_bars(
    requested_symbol: str,
    data: dict[str, Any],
    span: BarSpan,
) -> list[Bar]:
    raw_bars = extract_ohlcs(data)
    bars: list[Bar] = []
    for row in raw_bars:
        timestamp = str(row.get("ctm") or row.get("otm") or row.get("time") or row.get("date") or "")
        bars.append(
            Bar(
                symbol=requested_symbol,
                timestamp=timestamp,
                open=float(row.get("open") or row.get("o") or 0.0),
                high=float(row.get("high") or row.get("h") or 0.0),
                low=float(row.get("low") or row.get("l") or 0.0),
                close=float(row.get("close") or row.get("c") or 0.0),
                volume=float(row.get("volume") or row.get("vol") or 0.0),
                amount=float(row.get("amount") or row.get("turnover") or 0.0),
                span=span,
                source=DataSource.FTSHARE,
                raw=dict(row),
            )
        )
    return bars


def extract_ohlcs(data: dict[str, Any]) -> list[dict[str, Any]]:
    if isinstance(data.get("ohlcs"), list):
        return [dict(item) for item in data["ohlcs"]]
    nested = data.get("data")
    if isinstance(nested, dict) and isinstance(nested.get("ohlcs"), list):
        return [dict(item) for item in nested["ohlcs"]]
    if isinstance(nested, list):
        return [dict(item) for item in nested]
    return []

