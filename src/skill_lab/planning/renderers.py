"""Markdown renderers for planning objects."""

from __future__ import annotations

from skill_lab.shared.schemas import DailyReview, TomorrowPlan


def render_tomorrow_plan_markdown(plan: TomorrowPlan) -> str:
    lines = [
        f"# {plan.trade_date} Tomorrow Plan",
        "",
        f"- Market regime: {plan.market_regime.value}",
        f"- Summary: {plan.summary}",
        "",
        "| Priority | Theme | Action | Candidates | Confirm | Give up |",
        "|---:|---|---|---|---|---|",
    ]
    for item in plan.items:
        candidates = ", ".join(item.candidates)
        lines.append(
            f"| {item.priority} | {item.theme} | {item.action.value} | "
            f"{candidates} | {item.confirm_signal} | {item.give_up_signal} |"
        )
    if plan.data_limits:
        lines.extend(["", "## Data Limits", ""])
        lines.extend(f"- {item}" for item in plan.data_limits)
    return "\n".join(lines)


def render_daily_review_markdown(review: DailyReview) -> str:
    lines = [
        f"# {review.trade_date} Daily Review",
        "",
        f"- Market regime: {review.market_regime.value}",
        f"- Summary: {review.summary}",
        "",
        "## Findings",
        "",
    ]
    lines.extend(f"- {item}" for item in review.findings)
    if review.tomorrow_plan:
        lines.extend([
            "",
            "## Linked Tomorrow Plan",
            "",
            f"- Items: {len(review.tomorrow_plan.items)}",
            f"- Summary: {review.tomorrow_plan.summary}",
        ])
    if review.data_limits:
        lines.extend(["", "## Data Limits", ""])
        lines.extend(f"- {item}" for item in review.data_limits)
    return "\n".join(lines)

