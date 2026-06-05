#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Run the daily organization-analysis pipeline from file-backed examples."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from skill_lab.market_analysis.breadth import classify_breadth
from skill_lab.market_analysis.index_environment import summarize_index_environment
from skill_lab.market_analysis.regime import classify_market_regime
from skill_lab.market_data.calendar import WeekdayTradeCalendar
from skill_lab.market_data.file_provider import FileProvider
from skill_lab.planning.daily_review import build_daily_review
from skill_lab.planning.renderers import render_daily_review_markdown, render_tomorrow_plan_markdown
from skill_lab.planning.tomorrow_plan import build_tomorrow_plan
from skill_lab.sector_analysis.leaders import extract_all_theme_leaders
from skill_lab.sector_analysis.reports import render_theme_battle_cards
from skill_lab.sector_analysis.strength import summarize_theme_strength


def main() -> int:
    parser = argparse.ArgumentParser(description="Run daily market organization analysis.")
    parser.add_argument("--date", required=True, help="Trade date, e.g. 2026-06-04.")
    parser.add_argument("--root", default=str(ROOT), help="Workspace root.")
    parser.add_argument("--out-dir", default="", help="Optional output directory for Markdown/JSON artifacts.")
    parser.add_argument("--json", action="store_true", help="Print compact JSON summary instead of Markdown.")
    parser.add_argument("--allow-quality-warnings", action="store_true", help="Continue when quality warnings exist.")
    parser.add_argument("--require-trade-date", action="store_true", help="Fail when --date is not a trade date.")
    parser.add_argument("--kpl", default="", help="Optional KPL/limit-up CSV for leader extraction.")
    parser.add_argument("--lhb", default="", help="Optional dragon-tiger CSV for leader extraction.")
    args = parser.parse_args()

    root = Path(args.root)
    calendar = WeekdayTradeCalendar()
    if args.require_trade_date and not calendar.is_trade_date(args.date):
        latest = calendar.latest_trade_date_on_or_before(args.date)
        print(f"{args.date} is not a trade date. Latest trade date on or before it is {latest}.")
        raise SystemExit(4)
    provider = FileProvider(root)
    quality = provider.check_daily_inputs(args.date)
    if not quality.passed:
        print_quality(quality)
        raise SystemExit(2)
    if quality.issues and not args.allow_quality_warnings:
        print_quality(quality)
        raise SystemExit(3)

    breadth = classify_breadth(provider.get_market_breadth(args.date))
    indexes = summarize_index_environment(provider.get_index_environment(args.date))
    market = classify_market_regime(breadth, indexes)
    themes = summarize_theme_strength(provider.get_theme_scores(args.date))
    kpl_rows = read_optional_csv(args.kpl)
    lhb_rows = read_optional_csv(args.lhb)
    leader_summaries = extract_all_theme_leaders(themes.ranked, kpl_rows=kpl_rows, lhb_rows=lhb_rows)
    plan = build_tomorrow_plan(args.date, market, themes)
    review = build_daily_review(args.date, market, themes, plan)
    battle_cards_md = render_theme_battle_cards(themes, leader_summaries)

    summary = {
        "trade_date": args.date,
        "market_regime": market.regime.value,
        "market_score": market.score,
        "theme_count": len(themes.ranked),
        "attackable_count": len(themes.attackable),
        "watchable_count": len(themes.watchable),
        "rejected_count": len(themes.rejected),
        "top_theme": themes.ranked[0].theme if themes.ranked else "",
        "plan_items": len(plan.items),
        "review_findings": len(review.findings),
        "quality_issue_count": len(quality.issues),
        "leader_candidate_count": sum(len(item.candidates) for item in leader_summaries),
        "theme_leaders": [
            {
                "theme": item.theme,
                "candidate_count": len(item.candidates),
                "front_row_count": len(item.front_row),
                "capacity_core_count": len(item.capacity_core),
                "risk_sample_count": len(item.risk_samples),
            }
            for item in leader_summaries[:5]
        ],
    }

    if args.out_dir:
        out_dir = Path(args.out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / f"{args.date}-theme-battle-cards.md").write_text(battle_cards_md, encoding="utf-8")
        (out_dir / f"{args.date}-tomorrow-plan.md").write_text(render_tomorrow_plan_markdown(plan), encoding="utf-8")
        (out_dir / f"{args.date}-daily-review.md").write_text(render_daily_review_markdown(review), encoding="utf-8")
        (out_dir / f"{args.date}-summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        print(f"# {args.date} Organization Analysis")
        print("")
        print(f"- Market regime: {market.regime.value} ({market.score})")
        print(f"- Top theme: {summary['top_theme']}")
        print(f"- Themes: {len(themes.ranked)} ranked, {len(themes.watchable)} watchable, {len(themes.rejected)} rejected")
        print(f"- Plan items: {len(plan.items)}")
        print(f"- Review findings: {len(review.findings)}")
        print(f"- Leader candidates: {summary['leader_candidate_count']}")
        print("")
        print(battle_cards_md)
        print("")
        print(render_tomorrow_plan_markdown(plan))
        print("")
        print(render_daily_review_markdown(review))
    return 0


def print_quality(report) -> None:
    print(f"Data quality failed for {report.subject}:")
    for issue in report.issues:
        print(f"- [{issue.severity}] {issue.code}: {issue.message}")


def read_optional_csv(path: str):
    if not path:
        return []
    from skill_lab.market_data.file_provider import read_csv

    return read_csv(Path(path))


if __name__ == "__main__":
    raise SystemExit(main())
