from pathlib import Path
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from skill_lab.market_data.cache import JsonCache, build_cache_key
from skill_lab.market_data.file_provider import FileProvider
from skill_lab.market_data.quality import QualityBaseline, check_bars, check_market_breadth, check_theme_scores
from skill_lab.shared.schemas import Bar, MarketBreadth, ThemeScore


def test_file_provider_daily_inputs_quality_report():
    provider = FileProvider(ROOT)
    report = provider.check_daily_inputs("2026-06-04")
    assert report.checked_count > 0
    assert report.passed


def test_quality_detects_invalid_bars():
    report = check_bars([
        Bar(symbol="600580", timestamp="2026-06-04", open=10, high=9, low=8, close=10.5),
    ], symbol="600580")
    assert not report.passed
    assert "invalid_ohlc" in {issue.code for issue in report.issues}


def test_quality_warns_theme_score_range():
    report = check_theme_scores([
        ThemeScore(trade_date="2026-06-04", theme="AI", total_score=120),
    ], trade_date="2026-06-04")
    assert report.passed
    assert "score_out_of_range" in {issue.code for issue in report.issues}


def test_quality_baseline_warns_outlier_breadth():
    report = check_market_breadth(
        MarketBreadth(trade_date="2026-06-04", limit_up_count=999),
        baseline=QualityBaseline(max_limit_up_count=100),
    )
    assert report.passed
    assert "limit_up_count_outlier" in {issue.code for issue in report.issues}


def test_json_cache_roundtrip():
    with tempfile.TemporaryDirectory() as tmp:
        cache = JsonCache(tmp, namespace="smoke")
        key = build_cache_key("file", "get_market_breadth", trade_date="2026-06-04")
        cache.set(key, {"ok": True})
        assert cache.get(key) == {"ok": True}


if __name__ == "__main__":
    test_file_provider_daily_inputs_quality_report()
    test_quality_detects_invalid_bars()
    test_quality_warns_theme_score_range()
    test_quality_baseline_warns_outlier_breadth()
    test_json_cache_roundtrip()
