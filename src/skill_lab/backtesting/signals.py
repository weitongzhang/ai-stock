"""Helpers that convert research signals into backtest events."""

from __future__ import annotations

from skill_lab.shared.enums import SignalDirection
from skill_lab.shared.schemas import Bar, SignalEvent, StockSignal


def signal_event_from_stock_signal(signal: StockSignal, price: float | None = None) -> SignalEvent:
    return SignalEvent(
        trade_date=signal.trade_date,
        symbol=signal.symbol,
        direction=signal.direction,
        score=signal.score,
        price=price,
        reason="; ".join(signal.reasons),
        source=signal.signal_name,
        raw=signal.to_dict(),
    )


def latest_close_for_signal(signal: StockSignal, bars: list[Bar]) -> float | None:
    if not bars:
        return None
    same_day = [bar for bar in bars if bar.timestamp[:10] <= signal.trade_date]
    return (same_day[-1] if same_day else bars[-1]).close


def filter_actionable_events(events: list[SignalEvent]) -> list[SignalEvent]:
    actionable = {SignalDirection.BUY, SignalDirection.SELL}
    return [event for event in events if event.direction in actionable]


def stock_signals_to_events(signals: list[StockSignal], bars_by_symbol: dict[str, list[Bar]]) -> list[SignalEvent]:
    events: list[SignalEvent] = []
    for signal in signals:
        price = latest_close_for_signal(signal, bars_by_symbol.get(signal.symbol, []))
        events.append(signal_event_from_stock_signal(signal, price=price))
    return events
