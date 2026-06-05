"""Build structured tomorrow plans from market and theme conclusions."""

from __future__ import annotations

from datetime import datetime

from skill_lab.market_analysis.position import suggest_position_bias
from skill_lab.sector_analysis.strength import ThemeStrengthSummary
from skill_lab.shared.enums import ActionLevel, MarketRegime, ThemeStance
from skill_lab.shared.schemas import MarketRegimeResult, ThemeScore, TomorrowPlan, TomorrowPlanItem


def build_tomorrow_plan(
    trade_date: str,
    market: MarketRegimeResult,
    themes: ThemeStrengthSummary,
    max_items: int = 5,
) -> TomorrowPlan:
    items = [
        plan_item_from_theme(index + 1, theme, market.regime)
        for index, theme in enumerate(themes.ranked[:max_items])
    ]
    return TomorrowPlan(
        trade_date=trade_date,
        generated_at=datetime.now().isoformat(timespec="seconds"),
        market_regime=market.regime,
        summary=build_summary(market, themes),
        items=items,
        data_limits=[],
        raw={
            "market": market,
            "theme_count": len(themes.ranked),
        },
    )


def plan_item_from_theme(priority: int, theme: ThemeScore, regime: MarketRegime) -> TomorrowPlanItem:
    return TomorrowPlanItem(
        theme=theme.theme,
        priority=priority,
        action=choose_action(theme, regime),
        candidates=theme.core_names,
        confirm_signal=theme.confirm_signal,
        give_up_signal=theme.give_up_signal,
        position_constraint=suggest_position_bias(regime),
        reasons=theme_reasons(theme),
        raw={"theme_score": theme},
    )


def choose_action(theme: ThemeScore, regime: MarketRegime) -> ActionLevel:
    if theme.stance == ThemeStance.GIVE_UP or theme.total_score < 32:
        return ActionLevel.GIVE_UP
    if regime == MarketRegime.DEFENSIVE:
        return ActionLevel.OBSERVE_ONLY
    if theme.total_score >= 68:
        return ActionLevel.MAIN_ATTACK
    if theme.total_score >= 50:
        return ActionLevel.WATCH if regime == MarketRegime.CHOPPY_TRIAL else ActionLevel.CORE_DIP
    if theme.total_score >= 32:
        return ActionLevel.WATCH
    return ActionLevel.GIVE_UP


def theme_reasons(theme: ThemeScore) -> list[str]:
    return [
        f"total_score={theme.total_score}",
        f"F/M/C/T={theme.flow_score}/{theme.map_score}/{theme.core_score}/{theme.timing_score}",
    ]


def build_summary(market: MarketRegimeResult, themes: ThemeStrengthSummary) -> str:
    top = themes.ranked[0].theme if themes.ranked else "no theme"
    return f"market={market.regime.value}; top_theme={top}; position={suggest_position_bias(market.regime)}"

