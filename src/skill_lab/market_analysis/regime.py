"""Combine breadth and index context into a market regime result."""

from __future__ import annotations

from skill_lab.market_analysis.breadth import BreadthScore
from skill_lab.market_analysis.index_environment import IndexEnvironmentSummary
from skill_lab.shared.enums import MarketRegime
from skill_lab.shared.schemas import MarketRegimeResult


def classify_market_regime(
    breadth: BreadthScore,
    index_summary: IndexEnvironmentSummary,
) -> MarketRegimeResult:
    regime = breadth.regime_hint
    score = breadth.score
    reasons = list(breadth.reasons) + list(index_summary.reasons)
    constraints = list(index_summary.constraints)

    if index_summary.stage == "defensive":
        score -= 2
        constraints.append("index environment is defensive")
    elif index_summary.stage == "structural_split":
        score -= 0.5
        constraints.append("only trade with strong-index resonance")
    elif index_summary.stage == "supports_attack":
        score += 1
        reasons.append("index environment supports attack")

    if score >= 4:
        regime = MarketRegime.ATTACK
    elif score >= 2:
        regime = MarketRegime.STRUCTURAL_REPAIR
    elif score >= 0:
        regime = MarketRegime.CHOPPY_TRIAL
    else:
        regime = MarketRegime.DEFENSIVE

    return MarketRegimeResult(
        trade_date=breadth.trade_date or index_summary.trade_date,
        regime=regime,
        score=score,
        reasons=reasons,
        constraints=constraints,
        raw={
            "breadth": breadth,
            "index_summary": index_summary,
        },
    )

