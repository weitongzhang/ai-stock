"""Market breadth classification service."""

from __future__ import annotations

from dataclasses import dataclass, field

from skill_lab.shared.enums import MarketRegime
from skill_lab.shared.schemas import MarketBreadth


@dataclass(slots=True)
class BreadthScore:
    trade_date: str
    score: float
    regime_hint: MarketRegime
    reasons: list[str] = field(default_factory=list)


def classify_breadth(breadth: MarketBreadth) -> BreadthScore:
    score = 0.0
    reasons: list[str] = []

    if breadth.limit_up_count >= 80:
        score += 2
        reasons.append("limit-up count is active enough for short-term expansion")
    elif breadth.limit_up_count >= 50:
        score += 1
        reasons.append("limit-up count is tradable but not broad euphoria")
    else:
        score -= 1
        reasons.append("limit-up count is weak")

    if breadth.limit_down_count <= 10:
        score += 1
        reasons.append("limit-down pressure is contained")
    elif breadth.limit_down_count >= 25:
        score -= 2
        reasons.append("limit-down pressure is spreading")

    if breadth.seal_rate >= 75 and breadth.failed_limit_up_rate <= 20:
        score += 2
        reasons.append("seal quality is strong")
    elif breadth.failed_limit_up_rate >= 35:
        score -= 2
        reasons.append("failed-limit rate is high")

    if breadth.advancers and breadth.decliners:
        if breadth.advancers > breadth.decliners * 1.2:
            score += 1
            reasons.append("advancers lead decliners")
        elif breadth.decliners > breadth.advancers * 1.8:
            score -= 2
            reasons.append("decliners dominate advancers")

    if score >= 4:
        regime = MarketRegime.ATTACK
    elif score >= 2:
        regime = MarketRegime.STRUCTURAL_REPAIR
    elif score >= 0:
        regime = MarketRegime.CHOPPY_TRIAL
    else:
        regime = MarketRegime.DEFENSIVE

    return BreadthScore(
        trade_date=breadth.trade_date,
        score=score,
        regime_hint=regime,
        reasons=reasons,
    )

