"""Report renderers for sector/theme analysis."""

from __future__ import annotations

from skill_lab.sector_analysis.leaders import ThemeLeaderSummary
from skill_lab.sector_analysis.strength import ThemeStrengthSummary


def render_theme_battle_cards(
    strength: ThemeStrengthSummary,
    leaders: list[ThemeLeaderSummary],
    max_themes: int = 5,
) -> str:
    leader_map = {item.theme: item for item in leaders}
    lines = [
        f"# {strength.trade_date} Theme Battle Cards",
        "",
        "| Priority | Theme | Score | Stance | Capacity Core | Front Row | Risk Samples |",
        "|---:|---|---:|---|---|---|---|",
    ]
    for index, theme in enumerate(strength.ranked[:max_themes], start=1):
        summary = leader_map.get(theme.theme)
        capacity = names(summary.capacity_core if summary else [])
        front_row = names(summary.front_row if summary else [])
        risks = names(summary.risk_samples if summary else [])
        lines.append(
            f"| {index} | {theme.theme} | {theme.total_score:.1f} | {theme.stance.value} | "
            f"{capacity} | {front_row} | {risks} |"
        )
    return "\n".join(lines)


def names(candidates) -> str:
    if not candidates:
        return "-"
    return ", ".join(item.name or item.symbol for item in candidates[:5])
