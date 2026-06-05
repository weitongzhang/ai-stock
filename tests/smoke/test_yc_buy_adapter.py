from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from skill_lab.shared.enums import BarSpan, DataSource, SignalDirection
from skill_lab.shared.schemas import Bar
from skill_lab.stock_analysis.yc_buy_adapter import YcBuyAdapter, YcBuyClassEngine, bars_to_dataframe


class FakeEngine:
    def analyze(self, bars):
        return {
            "buy_points": ["buy point 1"],
            "triple_signal": "wait_breakout",
        }


class FakeBuyPointAnalyzer:
    def __init__(self, data):
        self.data = data

    def analyze_all_buy_points(self):
        return ["buy point class"]


class FakeTripleScreenSystem:
    def __init__(self, data):
        self.data = data

    def analyze(self):
        return {"signal": "buy"}


def sample_bars():
    return [
        Bar(
            symbol="600519.SH",
            timestamp=f"2026-06-{day:02d}",
            open=10.0,
            high=11.0,
            low=9.5,
            close=10.5 + day * 0.01,
            volume=1000 + day,
            span=BarSpan.DAY1,
            source=DataSource.FILE,
        )
        for day in range(1, 6)
    ]


def test_bars_to_dataframe_shape():
    frame = bars_to_dataframe(sample_bars())
    assert list(frame.columns) == ["open", "high", "low", "close", "volume", "amount"]
    assert len(frame) == 5


def test_yc_buy_adapter_outputs_stock_signal():
    signal = YcBuyAdapter(FakeEngine()).analyze("600519.SH", "贵州茅台", sample_bars())
    assert signal.signal_name == "yc_buy"
    assert signal.direction == SignalDirection.WAIT
    assert signal.score > 50
    assert signal.reasons


def test_yc_buy_class_engine_uses_imported_classes():
    engine = YcBuyClassEngine(FakeBuyPointAnalyzer, FakeTripleScreenSystem)
    signal = YcBuyAdapter(engine).analyze("600519.SH", "Kweichow Moutai", sample_bars())
    assert signal.direction == SignalDirection.BUY
    assert signal.score >= 70
    assert "buy point class" in signal.reasons


if __name__ == "__main__":
    test_bars_to_dataframe_shape()
    test_yc_buy_adapter_outputs_stock_signal()
    test_yc_buy_class_engine_uses_imported_classes()
