"""A tiny deterministic long-only engine for smoke tests and examples."""

from __future__ import annotations

from skill_lab.shared.enums import SignalDirection
from skill_lab.shared.schemas import (
    BacktestConfig,
    BacktestResult,
    Bar,
    EquityPoint,
    SignalEvent,
    TradeRecord,
)

from .metrics import build_performance_report


class SimpleLongOnlyEngine:
    """Execute buy/sell signal events at supplied event prices.

    This is intentionally small. Production backtests should wrap the user's
    existing engine behind the same adapter contract.
    """

    def run(
        self,
        config: BacktestConfig,
        bars_by_symbol: dict[str, list[Bar]],
        signals: list[SignalEvent],
    ) -> BacktestResult:
        cash = config.initial_cash
        position_qty = 0.0
        position_symbol = ""
        entry_price = 0.0
        entry_date = ""
        trades: list[TradeRecord] = []
        equity_curve: list[EquityPoint] = []

        ordered_events = sorted(signals, key=lambda item: (item.trade_date, item.symbol))
        for event in ordered_events:
            price = event.price or _close_on_or_before(bars_by_symbol.get(event.symbol, []), event.trade_date)
            if price is None or price <= 0:
                continue
            if event.direction == SignalDirection.BUY and not position_symbol:
                position_symbol = event.symbol
                entry_price = price * (1 + config.slippage_rate)
                entry_date = event.trade_date
                position_qty = cash / entry_price
                cash -= position_qty * entry_price * (1 + config.commission_rate)
            elif event.direction == SignalDirection.SELL and position_symbol == event.symbol:
                exit_price = price * (1 - config.slippage_rate)
                gross = position_qty * exit_price
                fees = gross * config.commission_rate
                pnl = gross - fees - config.initial_cash
                trades.append(
                    TradeRecord(
                        trade_id=f"{event.symbol}-{entry_date}-{event.trade_date}",
                        symbol=event.symbol,
                        entry_date=entry_date,
                        exit_date=event.trade_date,
                        entry_price=entry_price,
                        exit_price=exit_price,
                        quantity=position_qty,
                        pnl=pnl,
                        return_pct=exit_price / entry_price - 1.0,
                        fees=fees,
                    )
                )
                cash = gross - fees
                position_qty = 0.0
                position_symbol = ""
                entry_price = 0.0
                entry_date = ""
            market_value = position_qty * price if position_symbol == event.symbol else 0.0
            equity = cash + market_value
            equity_curve.append(
                EquityPoint(
                    trade_date=event.trade_date,
                    equity=equity,
                    cash=cash,
                    exposure=market_value / equity if equity else 0.0,
                )
            )

        performance = build_performance_report(config, equity_curve, trades)
        return BacktestResult(
            config=config,
            performance=performance,
            trades=trades,
            equity_curve=equity_curve,
            signals=signals,
        )


def _close_on_or_before(bars: list[Bar], trade_date: str) -> float | None:
    eligible = [bar for bar in bars if bar.timestamp[:10] <= trade_date]
    if not eligible:
        return None
    return eligible[-1].close
