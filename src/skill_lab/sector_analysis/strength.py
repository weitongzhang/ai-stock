"""Theme strength service built on normalized ThemeScore objects."""

from __future__ import annotations

from dataclasses import dataclass, field

from skill_lab.shared.enums import ThemeStance
from skill_lab.shared.schemas import ThemeScore


@dataclass(slots=True)
class ThemeStrengthSummary:
    trade_date: str
    ranked: list[ThemeScore] = field(default_factory=list)
    attackable: list[ThemeScore] = field(default_factory=list)
    watchable: list[ThemeScore] = field(default_factory=list)
    rejected: list[ThemeScore] = field(default_factory=list)


def rank_theme_scores(themes: list[ThemeScore]) -> list[ThemeScore]:
    return sorted(themes, key=lambda item: item.total_score, reverse=True)


def summarize_theme_strength(themes: list[ThemeScore]) -> ThemeStrengthSummary:
    ranked = rank_theme_scores(themes)
    trade_date = ranked[0].trade_date if ranked else ""
    attackable = [
        item
        for item in ranked
        if item.stance == ThemeStance.ATTACK or item.total_score >= 68
    ]
    watchable = [
        item
        for item in ranked
        if item not in attackable
        and item.stance in {ThemeStance.ACTIVE_WATCH, ThemeStance.TRACK_WAIT}
    ]
    rejected = [
        item
        for item in ranked
        if item.stance == ThemeStance.GIVE_UP or item.total_score < 32
    ]
    return ThemeStrengthSummary(
        trade_date=trade_date,
        ranked=ranked,
        attackable=attackable,
        watchable=watchable,
        rejected=rejected,
    )

