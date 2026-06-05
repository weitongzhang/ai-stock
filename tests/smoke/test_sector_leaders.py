from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from skill_lab.market_data.file_provider import FileProvider, read_csv
from skill_lab.sector_analysis.leaders import extract_theme_leaders
from skill_lab.sector_analysis.reports import render_theme_battle_cards
from skill_lab.sector_analysis.registry import default_registry
from skill_lab.sector_analysis.strength import summarize_theme_strength
from skill_lab.shared.enums import ThemeLeaderRole


def test_theme_registry_matches_alias():
    registry = default_registry()
    assert registry.match_theme("光通信叠加AI算力订单催化").theme == "AI算力/数据中心"
    assert registry.get("能源/煤炭/油气").capacity_names


def test_extract_theme_leaders_from_examples():
    provider = FileProvider(ROOT)
    themes = provider.get_theme_scores("2026-06-04")
    kpl_rows = read_csv(ROOT / "examples" / "market" / "tushare-kpl" / "sample-tushare-kpl.csv")
    lhb_rows = read_csv(ROOT / "examples" / "market" / "dragon-tiger" / "20260604-eastmoney-lhb.csv")

    energy = next(theme for theme in themes if theme.theme == "能源/煤炭/油气")
    summary = extract_theme_leaders(energy, kpl_rows=kpl_rows, lhb_rows=lhb_rows)
    roles = {candidate.role for candidate in summary.candidates}

    assert summary.theme == "能源/煤炭/油气"
    assert summary.candidates
    assert ThemeLeaderRole.CAPACITY_CORE in roles or ThemeLeaderRole.FRONT_ROW in roles


def test_extract_theme_leaders_marks_failed_limit_up_as_risk():
    provider = FileProvider(ROOT)
    themes = provider.get_theme_scores("2026-06-04")
    kpl_rows = read_csv(ROOT / "examples" / "market" / "tushare-kpl" / "sample-tushare-kpl.csv")
    semi = next(theme for theme in themes if theme.theme == "半导体/国产替代")

    summary = extract_theme_leaders(semi, kpl_rows=kpl_rows)
    assert summary.risk_samples
    assert summary.risk_samples[0].role == ThemeLeaderRole.RISK_SAMPLE


def test_render_theme_battle_cards():
    provider = FileProvider(ROOT)
    themes = provider.get_theme_scores("2026-06-04")
    strength = summarize_theme_strength(themes)
    kpl_rows = read_csv(ROOT / "examples" / "market" / "tushare-kpl" / "sample-tushare-kpl.csv")
    leaders = [extract_theme_leaders(theme, kpl_rows=kpl_rows) for theme in strength.ranked]
    markdown = render_theme_battle_cards(strength, leaders)
    assert "Theme Battle Cards" in markdown
    assert "Capacity Core" in markdown
    assert "Risk Samples" in markdown


if __name__ == "__main__":
    test_theme_registry_matches_alias()
    test_extract_theme_leaders_from_examples()
    test_extract_theme_leaders_marks_failed_limit_up_as_risk()
    test_render_theme_battle_cards()
