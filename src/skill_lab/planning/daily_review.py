"""Build structured daily review objects from analysis outputs."""

from __future__ import annotations

from skill_lab.sector_analysis.strength import ThemeStrengthSummary
from skill_lab.shared.schemas import DailyReview, MarketRegimeResult, TomorrowPlan


def build_daily_review(
    trade_date: str,
    market: MarketRegimeResult,
    themes: ThemeStrengthSummary,
    tomorrow_plan: TomorrowPlan | None = None,
    data_limits: list[str] | None = None,
) -> DailyReview:
    findings = build_findings(market, themes, tomorrow_plan)
    return DailyReview(
        trade_date=trade_date,
        summary=build_summary(market, themes),
        market_regime=market.regime,
        findings=findings,
        tomorrow_plan=tomorrow_plan,
        data_limits=list(data_limits or []),
        raw={
            "market": market,
            "theme_count": len(themes.ranked),
        },
    )


def build_summary(market: MarketRegimeResult, themes: ThemeStrengthSummary) -> str:
    top_theme = themes.ranked[0].theme if themes.ranked else "no clear theme"
    return f"market={market.regime.value}; top_theme={top_theme}; score={market.score:.1f}"


def build_findings(
    market: MarketRegimeResult,
    themes: ThemeStrengthSummary,
    tomorrow_plan: TomorrowPlan | None,
) -> list[str]:
    findings: list[str] = []
    findings.append(f"market regime classified as {market.regime.value}")
    for reason in market.reasons[:3]:
        findings.append(f"market evidence: {reason}")
    if themes.ranked:
        top = themes.ranked[0]
        findings.append(
            f"top theme is {top.theme} with score {top.total_score:.1f}"
        )
        findings.append(
            f"top theme F/M/C/T={top.flow_score}/{top.map_score}/{top.core_score}/{top.timing_score}"
        )
    if tomorrow_plan and tomorrow_plan.items:
        findings.append(
            f"tomorrow plan has {len(tomorrow_plan.items)} items; first action={tomorrow_plan.items[0].action.value}"
        )
    for constraint in market.constraints[:2]:
        findings.append(f"risk constraint: {constraint}")
    return findings

