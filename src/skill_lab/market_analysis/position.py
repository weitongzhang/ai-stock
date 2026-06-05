"""Position-bias helper for market regimes."""

from __future__ import annotations

from skill_lab.shared.enums import MarketRegime


def suggest_position_bias(regime: MarketRegime) -> str:
    if regime == MarketRegime.ATTACK:
        return "medium position; add only after theme spread confirms"
    if regime == MarketRegime.STRUCTURAL_REPAIR:
        return "light-to-medium position; focus on front-row and capacity core"
    if regime == MarketRegime.CHOPPY_TRIAL:
        return "light trial position; confirmation before participation"
    if regime == MarketRegime.DEFENSIVE:
        return "defensive position; wait for breadth repair"
    return "unknown; keep exposure restrained"

