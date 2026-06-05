"""Backtest engine adapter contracts."""

from __future__ import annotations

from typing import Protocol

from skill_lab.shared.schemas import BacktestConfig, BacktestResult, Bar, SignalEvent


class BacktestEngine(Protocol):
    """Minimal contract for any local or external backtest implementation."""

    def run(
        self,
        config: BacktestConfig,
        bars_by_symbol: dict[str, list[Bar]],
        signals: list[SignalEvent],
    ) -> BacktestResult:
        """Execute a deterministic backtest and return normalized results."""


class BacktestAdapter:
    """Thin orchestration wrapper around a concrete backtest engine."""

    def __init__(self, engine: BacktestEngine) -> None:
        self.engine = engine

    def run(
        self,
        config: BacktestConfig,
        bars_by_symbol: dict[str, list[Bar]],
        signals: list[SignalEvent],
    ) -> BacktestResult:
        return self.engine.run(config, bars_by_symbol, signals)
