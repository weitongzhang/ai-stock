---
name: watchlist-tracker
description: 标的与板块长中短周期跟踪工作流。Use when Codex needs to maintain watchlists, track A-share stocks, sectors, themes, ETFs, or indices over long/mid/short horizons, produce scheduled follow-up reports, update observation status, record triggers, risks, and next actions for targets the user wants to monitor.
---

# Watchlist Tracker

Use this skill for long-term, mid-term, and short-term tracking of stocks, sectors, themes, ETFs, indices, or strategy candidates.

## Purpose

Maintain a durable watchlist and produce repeatable tracking reports:

- Long-term: strategic thesis, industry trend, valuation, major structure.
- Mid-term: trend stage, weekly/daily structure, capital rotation, key levels.
- Short-term: trigger, breakout/retest, intraday/1-5 day action plan.

## Workflow

1. Read or create a watchlist CSV.
2. Classify each item as `stock`, `sector`, `theme`, `etf`, or `index`.
3. Assign horizon: `long`, `mid`, `short`, or a combination like `long+mid`.
4. Update tracking fields: thesis, key levels, trigger, invalidation, status, next check date.
5. Use market-data skills for quotes/K-line when live data is required.
6. Write Markdown and CSV reports for review.

## Script

```powershell
python skills\tracking\watchlist-tracker\scripts\update_watchlist_report.py --input examples\market\tracking\watchlist.csv --out-dir examples\market\tracking
```

## Scheduling

This skill defines the tracking workflow. Create actual recurring reminders/automations only when the user explicitly asks to schedule them.

## Reference

Read `references/tracking-framework.md` before changing the schema or designing scheduled reports.
