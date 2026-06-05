from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from skill_lab.market_analysis.breadth import classify_breadth
from skill_lab.market_analysis.index_environment import summarize_index_environment
from skill_lab.market_analysis.position import suggest_position_bias
from skill_lab.market_analysis.regime import classify_market_regime
from skill_lab.market_data.file_provider import FileProvider
from skill_lab.shared.enums import MarketRegime


def test_market_analysis_pipeline_from_examples():
    provider = FileProvider(ROOT)
    breadth = provider.get_market_breadth("2026-06-04")
    indexes = provider.get_index_environment("2026-06-04")

    breadth_score = classify_breadth(breadth)
    index_summary = summarize_index_environment(indexes)
    regime = classify_market_regime(breadth_score, index_summary)
    position = suggest_position_bias(regime.regime)

    assert breadth_score.score >= 4
    assert index_summary.stage == "structural_split"
    assert regime.regime in {MarketRegime.ATTACK, MarketRegime.STRUCTURAL_REPAIR}
    assert "position" in position


if __name__ == "__main__":
    test_market_analysis_pipeline_from_examples()
