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


def test_tomorrow_plan_pipeline_from_examples():
    provider = FileProvider(ROOT)
    trade_date = "2026-06-04"
    breadth = classify_breadth(provider.get_market_breadth(trade_date))
    indexes = summarize_index_environment(provider.get_index_environment(trade_date))
    market = classify_market_regime(breadth, indexes)
    themes = summarize_theme_strength(provider.get_theme_scores(trade_date))
    plan = build_tomorrow_plan(trade_date, market, themes)

    data = plan.to_dict()
    assert data["trade_date"] == trade_date
    assert len(data["items"]) >= 3
    assert data["items"][0]["theme"] == "能源/煤炭/油气"
    assert data["items"][0]["confirm_signal"]
    assert len(data["raw"]["perspectives"]) == 3


if __name__ == "__main__":
    test_tomorrow_plan_pipeline_from_examples()
