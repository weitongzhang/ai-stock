"""Methodology-perspective coordination for plans and reviews."""

from __future__ import annotations

from skill_lab.market_analysis.position import suggest_position_bias
from skill_lab.sector_analysis.strength import ThemeStrengthSummary
from skill_lab.shared.enums import MarketRegime, ThemeStance
from skill_lab.shared.schemas import MarketRegimeResult, PerspectiveAnalysis, ThemeScore


def build_methodology_perspectives(
    market: MarketRegimeResult,
    themes: ThemeStrengthSummary,
) -> list[PerspectiveAnalysis]:
    """Build deterministic perspective checks without overriding data facts."""

    top = themes.ranked[0] if themes.ranked else None
    return [
        build_chen_xiaoqun_perspective(market, top),
        build_model_xiansheng_perspective(market, top),
        build_qiushi_coordination_perspective(market, themes),
    ]


def build_chen_xiaoqun_perspective(
    market: MarketRegimeResult,
    top: ThemeScore | None,
) -> PerspectiveAnalysis:
    if top is None:
        return PerspectiveAnalysis(
            source="chen-xiaoqun-perspective",
            focus="theme-mainline-and-leader",
            summary="no ranked theme; cannot judge mainline or leader quality",
            cautions=["missing theme strength data"],
            conflicts=[],
            required_evidence=["theme score", "core names", "turnover acceptance", "cycle stage"],
            confidence=0.1,
        )

    supports = [
        f"top_theme={top.theme}",
        f"theme_score={top.total_score:.1f}",
        f"core_names={','.join(top.core_names) if top.core_names else '-'}",
    ]
    cautions = []
    conflicts = []
    required = [
        "theme must keep social attention and money-flow confirmation",
        "leader candidates must show role, turnover acceptance and invalidation boundary",
    ]

    if not top.core_names:
        conflicts.append("top theme lacks core leader candidates")
    if top.total_score < 50:
        cautions.append("theme score is not strong enough for mainline confirmation")
    if market.regime == MarketRegime.DEFENSIVE and top.total_score >= 68:
        conflicts.append("strong theme score conflicts with defensive market regime")
    if top.stance == ThemeStance.GIVE_UP:
        conflicts.append("theme stance is give_up, so leader framework should not force action")

    confidence = min(0.9, max(0.2, top.total_score / 100))
    return PerspectiveAnalysis(
        source="chen-xiaoqun-perspective",
        focus="theme-mainline-and-leader",
        summary=f"judge {top.theme} by mainline continuity, leader role and acceptance",
        supports=supports,
        cautions=cautions,
        conflicts=conflicts,
        required_evidence=required,
        confidence=confidence,
        raw={"theme": top},
    )


def build_model_xiansheng_perspective(
    market: MarketRegimeResult,
    top: ThemeScore | None,
) -> PerspectiveAnalysis:
    if top is None:
        return PerspectiveAnalysis(
            source="model-xiansheng-perspective",
            focus="principal-contradiction",
            summary="principal contradiction cannot be formed without theme evidence",
            cautions=["missing sector/theme evidence"],
            required_evidence=["market regime", "theme strength", "counterevidence"],
            confidence=0.1,
        )

    contradiction = classify_principal_contradiction(market.regime, top)
    supports = [
        f"market_regime={market.regime.value}",
        f"market_score={market.score:.1f}",
        f"top_theme={top.theme}",
        f"theme_stance={top.stance.value}",
    ]
    cautions = list(market.constraints[:2])
    conflicts = []
    if market.regime == MarketRegime.DEFENSIVE and top.stance == ThemeStance.ATTACK:
        conflicts.append("market risk constraint conflicts with theme attack stance")
    if market.score < 45 and top.total_score >= 68:
        conflicts.append("low market score conflicts with high theme score")
    if top.total_score < 32:
        cautions.append("top theme is weak; thesis should be observation-only")

    return PerspectiveAnalysis(
        source="model-xiansheng-perspective",
        focus="principal-contradiction",
        summary=contradiction,
        supports=supports,
        cautions=cautions,
        conflicts=conflicts,
        required_evidence=[
            "separate facts from expectation",
            "write falsification condition before action",
            "check whether the theme is already priced in",
        ],
        confidence=min(0.85, max(0.2, (market.score + top.total_score) / 200)),
        raw={"theme": top},
    )


def build_qiushi_coordination_perspective(
    market: MarketRegimeResult,
    themes: ThemeStrengthSummary,
) -> PerspectiveAnalysis:
    supports = [
        f"ranked_theme_count={len(themes.ranked)}",
        f"position_bias={suggest_position_bias(market.regime)}",
    ]
    cautions = list(market.constraints[:2])
    conflicts = collect_cross_methodology_conflicts(market, themes)
    return PerspectiveAnalysis(
        source="qiushi-stock-analysis",
        focus="fact-first-coordination",
        summary="data facts decide the conclusion; perspectives only add checks and boundaries",
        supports=supports,
        cautions=cautions,
        conflicts=conflicts,
        required_evidence=[
            "market breadth and index environment",
            "theme strength ranking",
            "leader evidence before action upgrade",
            "next-day validation and invalidation",
        ],
        confidence=0.8 if not conflicts else 0.55,
    )


def collect_cross_methodology_conflicts(
    market: MarketRegimeResult,
    themes: ThemeStrengthSummary,
) -> list[str]:
    conflicts: list[str] = []
    top = themes.ranked[0] if themes.ranked else None
    if top is None:
        return ["no theme ranking; methodology perspectives cannot produce a grounded conclusion"]
    if market.regime == MarketRegime.DEFENSIVE and top.total_score >= 68:
        conflicts.append("Chen-style mainline attack conflicts with Qiushi/market defensive constraint")
    if top.stance == ThemeStance.ATTACK and not top.core_names:
        conflicts.append("attack stance lacks leader evidence required by theme-leader methodology")
    if market.regime in {MarketRegime.CHOPPY_TRIAL, MarketRegime.DEFENSIVE} and top.stance == ThemeStance.ATTACK:
        conflicts.append("aggressive theme stance needs downgrade or explicit validation trigger")
    return conflicts


def classify_principal_contradiction(regime: MarketRegime, top: ThemeScore) -> str:
    if regime == MarketRegime.ATTACK and top.total_score >= 68:
        return f"principal contradiction is whether {top.theme} can convert strength into sustained leadership"
    if regime == MarketRegime.DEFENSIVE:
        return "principal contradiction is risk control versus any local theme opportunity"
    if regime == MarketRegime.CHOPPY_TRIAL:
        return "principal contradiction is trial participation versus false-positive theme rotation"
    if regime == MarketRegime.STRUCTURAL_REPAIR:
        return "principal contradiction is structural repair breadth versus leader continuity"
    return "principal contradiction is unclear; more market evidence is required"
