"""Markdown renderers for planning objects."""

from __future__ import annotations

from typing import Any

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
    perspectives = plan.raw.get("perspectives") if isinstance(plan.raw, dict) else None
    if perspectives:
        lines.extend(["", "## Methodology Perspectives", ""])
        for perspective in perspectives:
            lines.append(render_perspective_line(perspective))
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
    perspectives = review.raw.get("perspectives") if isinstance(review.raw, dict) else None
    if perspectives:
        lines.extend(["", "## Methodology Perspectives", ""])
        for perspective in perspectives:
            lines.append(render_perspective_line(perspective))
    return "\n".join(lines)


def render_perspective_line(perspective: Any) -> str:
    if isinstance(perspective, dict):
        source = str(perspective.get("source", "unknown"))
        summary = str(perspective.get("summary", ""))
        conflicts_list = list(perspective.get("conflicts") or [])
        confidence = float(perspective.get("confidence") or 0.0)
    else:
        source = perspective.source
        summary = perspective.summary
        conflicts_list = list(perspective.conflicts)
        confidence = float(perspective.confidence)
    conflicts = "; ".join(str(item) for item in conflicts_list) if conflicts_list else "none"
    return f"- {source}: {summary} (confidence={confidence:.2f}; conflicts={conflicts})"
