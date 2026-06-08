from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from skill_lab.planning.perspectives import build_methodology_perspectives
from skill_lab.planning.renderers import render_perspective_line, render_tomorrow_plan_markdown
from skill_lab.planning.tomorrow_plan import build_tomorrow_plan
from skill_lab.sector_analysis.strength import summarize_theme_strength
from skill_lab.shared.enums import MarketRegime, ThemeStance
from skill_lab.shared.schemas import MarketRegimeResult, ThemeScore


def test_methodology_perspectives_are_embedded_in_plan() -> None:
    market = MarketRegimeResult(
        trade_date="2026-06-08",
        regime=MarketRegime.ATTACK,
        score=75,
        reasons=["breadth improved"],
    )
    themes = summarize_theme_strength([
        ThemeScore(
            trade_date="2026-06-08",
            theme="AI",
            total_score=72,
            stance=ThemeStance.ATTACK,
            core_names=["Sample Leader"],
            confirm_signal="leader confirms strength",
            give_up_signal="leader breaks support",
        )
    ])
    plan = build_tomorrow_plan("2026-06-08", market, themes)
    data = plan.to_dict()
    markdown = render_tomorrow_plan_markdown(plan)

    sources = {item["source"] for item in data["raw"]["perspectives"]}
    assert sources == {
        "chen-xiaoqun-perspective",
        "model-xiansheng-perspective",
        "qiushi-stock-analysis",
    }
    assert "Methodology Perspectives" in markdown
    assert "model-xiansheng-perspective" in markdown
    assert "chen-xiaoqun-perspective" in render_perspective_line(data["raw"]["perspectives"][0])


def test_methodology_conflicts_are_exposed_not_suppressed() -> None:
    market = MarketRegimeResult(
        trade_date="2026-06-08",
        regime=MarketRegime.DEFENSIVE,
        score=35,
        reasons=["weak breadth"],
        constraints=["position should stay defensive"],
    )
    themes = summarize_theme_strength([
        ThemeScore(
            trade_date="2026-06-08",
            theme="Robotics",
            total_score=76,
            stance=ThemeStance.ATTACK,
            core_names=[],
            confirm_signal="front row keeps limit-up",
            give_up_signal="front row fails",
        )
    ])

    perspectives = build_methodology_perspectives(market, themes)
    conflicts = [
        conflict
        for perspective in perspectives
        for conflict in perspective.conflicts
    ]

    assert conflicts
    assert any("defensive" in conflict or "leader" in conflict for conflict in conflicts)


if __name__ == "__main__":
    test_methodology_perspectives_are_embedded_in_plan()
    test_methodology_conflicts_are_exposed_not_suppressed()
    print("methodology perspective coordination ok")
