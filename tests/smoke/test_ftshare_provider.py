from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from skill_lab.market_data.ftshare_provider import FTShareProvider
from skill_lab.market_data.symbols import (
    detect_market,
    to_cn_suffix,
    to_ftshare_stock_symbol,
)
from skill_lab.shared.enums import BarSpan, DataSource, Market


def fake_runner(args):
    assert args[0] == "stock-ohlcs"
    assert args[2] == "600519.XSHG"
    return {
        "ohlcs": [
            {
                "ctm": "2026-06-04T15:00:00",
                "open": 10,
                "high": 11,
                "low": 9,
                "close": 10.5,
                "volume": 1000,
                "amount": 123456,
            }
        ]
    }


def test_symbol_mapping():
    assert detect_market("600519.SH") == Market.SH
    assert detect_market("000001.SZ") == Market.SZ
    assert to_ftshare_stock_symbol("600519.SH") == "600519.XSHG"
    assert to_ftshare_stock_symbol("000001.SZ") == "000001.XSHE"
    assert to_cn_suffix("600519.XSHG") == "600519.SH"


def test_ftshare_provider_normalizes_bars_with_fake_runner():
    provider = FTShareProvider(ROOT, runner=fake_runner)
    bars = provider.get_bars("600519.SH", span=BarSpan.DAY1, limit=1)
    assert len(bars) == 1
    assert bars[0].symbol == "600519.SH"
    assert bars[0].close == 10.5
    assert bars[0].source == DataSource.FTSHARE


if __name__ == "__main__":
    test_symbol_mapping()
    test_ftshare_provider_normalizes_bars_with_fake_runner()
