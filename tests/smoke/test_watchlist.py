from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from skill_lab.market_analysis.breadth import classify_breadth
from skill_lab.market_analysis.index_environment import summarize_index_environment
from skill_lab.market_analysis.regime import classify_market_regime
from skill_lab.market_data.file_provider import FileProvider
from skill_lab.planning.tomorrow_plan import build_tomorrow_plan
from skill_lab.sector_analysis.strength import summarize_theme_strength
from skill_lab.shared.enums import WatchStatus
from skill_lab.tracking.watchlist import mark_invalidated, mark_triggered, watch_items_from_plan


def test_watchlist_items_from_plan():
    provider = FileProvider(ROOT)
    trade_date = "2026-06-04"
    market = classify_market_regime(
        classify_breadth(provider.get_market_breadth(trade_date)),
        summarize_index_environment(provider.get_index_environment(trade_date)),
    )
    themes = summarize_theme_strength(provider.get_theme_scores(trade_date))
    plan = build_tomorrow_plan(trade_date, market, themes)

    items = watch_items_from_plan(plan)
    triggered = mark_triggered(items[0], "auction confirmed")
    invalidated = mark_invalidated(items[0], "core faded")

    assert items
    assert items[0].source_plan_id == "plan:2026-06-04"
    assert triggered.status == WatchStatus.TRIGGERED
    assert invalidated.status == WatchStatus.INVALIDATED


if __name__ == "__main__":
    test_watchlist_items_from_plan()
