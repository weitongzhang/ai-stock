from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from skill_lab.backtesting.adapters import BacktestAdapter
from skill_lab.backtesting.signals import filter_actionable_events, stock_signals_to_events
from skill_lab.backtesting.simple_engine import SimpleLongOnlyEngine
from skill_lab.shared.enums import SignalDirection
from skill_lab.shared.schemas import BacktestConfig, Bar, StockSignal


def test_stock_signals_to_backtest_result():
    bars = [
        Bar(symbol="600580", timestamp="2026-06-01", open=10, high=11, low=9.8, close=10.0),
        Bar(symbol="600580", timestamp="2026-06-02", open=10.2, high=11.5, low=10, close=11.0),
        Bar(symbol="600580", timestamp="2026-06-03", open=11.2, high=12, low=11, close=11.8),
    ]
    signals = [
        StockSignal(
            trade_date="2026-06-01",
            symbol="600580",
            signal_name="yc_buy",
            direction=SignalDirection.BUY,
            score=80,
            reasons=["buy point"],
        ),
        StockSignal(
            trade_date="2026-06-03",
            symbol="600580",
            signal_name="yc_buy",
            direction=SignalDirection.SELL,
            score=70,
            reasons=["exit"],
        ),
    ]
    events = stock_signals_to_events(signals, {"600580": bars})
    config = BacktestConfig(strategy_name="yc-buy-smoke", start_date="2026-06-01", end_date="2026-06-03")
    result = BacktestAdapter(SimpleLongOnlyEngine()).run(config, {"600580": bars}, filter_actionable_events(events))

    assert result.performance.strategy_name == "yc-buy-smoke"
    assert result.performance.trade_count == 1
    assert result.performance.total_return > 0
    assert result.trades[0].symbol == "600580"
    assert result.signals[0].source == "yc_buy"


if __name__ == "__main__":
    test_stock_signals_to_backtest_result()
