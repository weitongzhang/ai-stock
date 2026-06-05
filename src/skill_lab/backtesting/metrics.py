"""Deterministic performance metrics for normalized backtest results."""

from __future__ import annotations

from skill_lab.shared.schemas import BacktestConfig, EquityPoint, PerformanceReport, TradeRecord


def total_return(equity_curve: list[EquityPoint], initial_cash: float) -> float:
    if not equity_curve or initial_cash == 0:
        return 0.0
    return equity_curve[-1].equity / initial_cash - 1.0


def max_drawdown(equity_curve: list[EquityPoint]) -> float:
    peak = 0.0
    worst = 0.0
    for point in equity_curve:
        peak = max(peak, point.equity)
        if peak > 0:
            worst = min(worst, point.equity / peak - 1.0)
    return abs(worst)


def win_rate(trades: list[TradeRecord]) -> float:
    closed = [trade for trade in trades if trade.exit_date]
    if not closed:
        return 0.0
    wins = [trade for trade in closed if trade.pnl > 0]
    return len(wins) / len(closed)


def profit_loss_ratio(trades: list[TradeRecord]) -> float:
    profits = [trade.pnl for trade in trades if trade.pnl > 0]
    losses = [abs(trade.pnl) for trade in trades if trade.pnl < 0]
    if not profits or not losses:
        return 0.0
    return (sum(profits) / len(profits)) / (sum(losses) / len(losses))


def exposure_days(equity_curve: list[EquityPoint]) -> int:
    return len([point for point in equity_curve if point.exposure > 0])


def annual_return(equity_curve: list[EquityPoint], initial_cash: float) -> float:
    if len(equity_curve) < 2:
        return 0.0
    period_return = total_return(equity_curve, initial_cash)
    trading_days = max(1, len(equity_curve) - 1)
    return (1.0 + period_return) ** (252 / trading_days) - 1.0


def build_performance_report(
    config: BacktestConfig,
    equity_curve: list[EquityPoint],
    trades: list[TradeRecord],
) -> PerformanceReport:
    return PerformanceReport(
        strategy_name=config.strategy_name,
        start_date=config.start_date,
        end_date=config.end_date,
        total_return=total_return(equity_curve, config.initial_cash),
        annual_return=annual_return(equity_curve, config.initial_cash),
        max_drawdown=max_drawdown(equity_curve),
        win_rate=win_rate(trades),
        profit_loss_ratio=profit_loss_ratio(trades),
        trade_count=len(trades),
        exposure_days=exposure_days(equity_curve),
    )
