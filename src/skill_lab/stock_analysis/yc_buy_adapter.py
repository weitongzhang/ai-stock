"""Adapter for YC-buy style buy-point and triple-screen signals."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Protocol

from skill_lab.shared.enums import SignalDirection
from skill_lab.shared.schemas import Bar, StockSignal


class YcBuyEngine(Protocol):
    """Minimal engine interface used by the adapter."""

    def analyze(self, bars: list[Bar]) -> dict[str, Any]:
        """Return buy point and triple-screen details."""


class YcBuyAdapter:
    """Convert normalized Bars into standardized StockSignal objects."""

    def __init__(self, engine: YcBuyEngine) -> None:
        self.engine = engine

    def analyze(self, symbol: str, name: str, bars: list[Bar], trade_date: str = "") -> StockSignal:
        result = self.engine.analyze(bars)
        buy_points = [str(item) for item in result.get("buy_points", [])]
        triple_signal = str(result.get("triple_signal") or result.get("signal") or "hold")
        direction = parse_direction(triple_signal, buy_points)
        reasons = []
        reasons.extend(buy_points)
        if triple_signal:
            reasons.append(f"triple_screen={triple_signal}")
        return StockSignal(
            trade_date=trade_date or (bars[-1].timestamp[:10] if bars else ""),
            symbol=symbol,
            name=name,
            signal_name="yc_buy",
            direction=direction,
            score=score_signal(direction, buy_points),
            reasons=reasons,
            raw=result,
        )


class LocalYcBuyEngine:
    """Engine that imports the local YC-buy repository implementation."""

    def __init__(self, repo_root: Path | str) -> None:
        self.repo_root = Path(repo_root).resolve()

    def analyze(self, bars: list[Bar]) -> dict[str, Any]:
        data = bars_to_dataframe(bars)
        repo = str(self.repo_root)
        if repo not in sys.path:
            sys.path.insert(0, repo)
        from strategies.buy_points import BuyPointAnalyzer
        from strategies.triple_screen import TripleScreenSystem

        buy_points = BuyPointAnalyzer(data).analyze_all_buy_points()
        triple = TripleScreenSystem(data).analyze()
        return {
            "buy_points": buy_points,
            "triple_signal": triple.get("signal", "hold"),
            "triple": triple,
        }


class YcBuyClassEngine:
    """Engine that uses already imported YC-buy analyzer classes."""

    def __init__(self, buy_point_analyzer, triple_screen_system, mode: str = "both") -> None:
        self.buy_point_analyzer = buy_point_analyzer
        self.triple_screen_system = triple_screen_system
        self.mode = mode

    def analyze(self, bars: list[Bar]) -> dict[str, Any]:
        data = bars_to_dataframe(bars)
        buy_points: list[str] = []
        if self.mode in {"buy-points", "both"}:
            buy_points = self.buy_point_analyzer(data).analyze_all_buy_points()
        triple: dict[str, Any] = {}
        if self.mode in {"triple-screen", "both"}:
            triple = self.triple_screen_system(data).analyze()
        return {
            "buy_points": buy_points,
            "triple_signal": triple.get("signal", "hold"),
            "triple": triple,
        }


def bars_to_dataframe(bars: list[Bar]):
    """Convert normalized bars to a pandas DataFrame expected by YC-buy."""

    import pandas as pd

    rows = [
        {
            "timestamp": bar.timestamp,
            "open": bar.open,
            "high": bar.high,
            "low": bar.low,
            "close": bar.close,
            "volume": bar.volume,
            "amount": bar.amount,
        }
        for bar in bars
    ]
    frame = pd.DataFrame(rows)
    if not frame.empty:
        frame = frame.set_index("timestamp")
    return frame


def parse_direction(signal: str, buy_points: list[str]) -> SignalDirection:
    if signal in {"buy", "consider_buy"}:
        return SignalDirection.BUY
    if signal == "wait_breakout" or buy_points:
        return SignalDirection.WAIT
    if signal == "sell":
        return SignalDirection.SELL
    if signal == "hold":
        return SignalDirection.HOLD
    return SignalDirection.UNKNOWN


def score_signal(direction: SignalDirection, buy_points: list[str]) -> float:
    base = {
        SignalDirection.BUY: 70.0,
        SignalDirection.WAIT: 55.0,
        SignalDirection.HOLD: 35.0,
        SignalDirection.SELL: 20.0,
    }.get(direction, 0.0)
    return min(100.0, base + len(buy_points) * 5.0)
