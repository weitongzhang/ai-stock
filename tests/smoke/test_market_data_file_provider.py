from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from skill_lab.market_data.file_provider import FileProvider
from skill_lab.shared.enums import ThemeStance


def test_file_provider_loads_market_examples():
    provider = FileProvider(ROOT)
    breadth = provider.get_market_breadth("2026-06-04")
    indexes = provider.get_index_environment("2026-06-04")
    themes = provider.get_theme_scores("2026-06-04")

    assert breadth.limit_up_count == 80
    assert breadth.failed_limit_up_count == 19
    assert len(indexes) >= 5
    assert indexes[0].name == "上证指数"
    assert len(themes) >= 3
    assert themes[0].stance == ThemeStance.ACTIVE_WATCH


if __name__ == "__main__":
    test_file_provider_loads_market_examples()
