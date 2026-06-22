from pathlib import Path
import json
import sys


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from skill_lab.institutional_research.context import (
    MCP_SERVER_ROLES,
    build_institutional_context,
    record_from_mcp_result,
)
from skill_lab.institutional_research.schemas import InstitutionalResearchRecord
from skill_lab.planning.daily_review import build_daily_review
from skill_lab.planning.renderers import render_daily_review_markdown, render_tomorrow_plan_markdown
from skill_lab.planning.tomorrow_plan import build_tomorrow_plan
from skill_lab.sector_analysis.strength import summarize_theme_strength
from skill_lab.shared.enums import MarketRegime, ThemeStance
from skill_lab.shared.schemas import MarketRegimeResult, ThemeScore


SECRET_MARKERS = [
    "Bear" + "er ",
    "mcp" + "Servers",
    "jz" + "fund_",
    "jz" + "mcp_",
    "jz" + "stratos_",
    "jz" + "skill_",
    "jz" + "report_",
]


def test_institutional_context_normalizes_mcp_evidence() -> None:
    record = record_from_mcp_result(
        "juzi-stratos",
        "asset allocation",
        {
            "date": "2026-06-08",
            "summary": "allocation prefers low beta exposure",
            "evidence": ["macro state is cautious"],
            "risks": ["conflicts with local theme attack"],
            "conflicts": ["asset allocation conflicts with local attack regime"],
            "next_checks": ["check market breadth tomorrow"],
            "confidence": 0.72,
        },
    )
    context = build_institutional_context("2026-06-08", [record])
    data = context.to_dict()

    assert data["trade_date"] == "2026-06-08"
    assert data["records"][0]["source"] == "juzi-stratos"
    assert data["records"][0]["raw"]["server_role"] == "asset-allocation-and-quant-strategy"
    assert data["conflicts"] == ["asset allocation conflicts with local attack regime"]
    assert not data["data_limits"]


def test_institutional_context_marks_missing_evidence_limits() -> None:
    context = build_institutional_context(
        "2026-06-08",
        [
            InstitutionalResearchRecord(
                source="juzi-fund",
                topic="fund crowding",
                summary="crowding is elevated",
            )
        ],
    )

    assert context.data_limits
    assert "missing evidence_date" in context.data_limits[0]
    assert "juzi-fund" in MCP_SERVER_ROLES


def test_institutional_context_flows_into_plan_and_review() -> None:
    institutional = build_institutional_context(
        "2026-06-08",
        [
            record_from_mcp_result(
                "juzi-report",
                "strategy card",
                {
                    "date": "2026-06-08",
                    "summary": "strategy card supports cautious participation",
                    "conflicts": ["strategy card conflicts with local main attack"],
                    "confidence": 0.66,
                },
            )
        ],
    )
    market = MarketRegimeResult(
        trade_date="2026-06-08",
        regime=MarketRegime.ATTACK,
        score=72,
        reasons=["breadth improved"],
    )
    themes = summarize_theme_strength([
        ThemeScore(
            trade_date="2026-06-08",
            theme="AI",
            total_score=70,
            stance=ThemeStance.ATTACK,
            core_names=["Sample Leader"],
            confirm_signal="leader confirms",
            give_up_signal="leader fails",
        )
    ])

    plan = build_tomorrow_plan(
        "2026-06-08",
        market,
        themes,
        institutional_context=institutional,
    )
    review = build_daily_review("2026-06-08", market, themes, plan)
    plan_md = render_tomorrow_plan_markdown(plan)
    review_md = render_daily_review_markdown(review)

    assert plan.raw["institutional_context"] is institutional
    assert review.raw["institutional_context"] is institutional
    assert "Institutional Research Context" in plan_md
    assert "juzi-report" in plan_md
    assert "institutional conflict" in "\n".join(review.findings)
    assert "Institutional Research Context" in review_md


def test_no_live_mcp_secret_material_committed() -> None:
    checked_paths = [
        ROOT / "docs" / "CSCI_JUZI_MCP_INTEGRATION.md",
        ROOT / "skills" / "institutional-research" / "csc-juzi-mcp" / "SKILL.md",
        ROOT / "skills" / "institutional-research" / "csc-juzi-mcp" / "agents" / "openai.yaml",
        ROOT / "src" / "skill_lab" / "institutional_research" / "context.py",
        ROOT / "src" / "skill_lab" / "institutional_research" / "schemas.py",
    ]
    for path in checked_paths:
        text = path.read_text(encoding="utf-8")
        for marker in SECRET_MARKERS:
            assert marker not in text, f"secret marker {marker!r} found in {path}"

    manifest = json.loads((ROOT / "SKILLS_MANIFEST.json").read_text(encoding="utf-8"))
    manifest_text = json.dumps(manifest, ensure_ascii=False)
    for marker in SECRET_MARKERS:
        assert marker not in manifest_text


if __name__ == "__main__":
    test_institutional_context_normalizes_mcp_evidence()
    test_institutional_context_marks_missing_evidence_limits()
    test_institutional_context_flows_into_plan_and_review()
    test_no_live_mcp_secret_material_committed()
    print("institutional research context ok")
