---
name: a-share-market-flow-analyst
description: A股资金流向、市场状态、板块强度、龙虎榜/涨停/财联社催化综合分析。Use when the user asks how to use market flow, sector money, CLS news, KPL limit-up data, or dragon-tiger data to choose tomorrow's sectors and stocks.
---

# A-Share Market Flow Analyst

Use this skill to turn intraday news, limit-up data, dragon-tiger list data, and optional market breadth/fund-flow snapshots into a next-day sector and stock observation plan.

This skill is for research and review only. It does not provide investment advice.

## Core Idea

Build a four-layer F-M-C-T view:

- F / Flow: market liquidity and money intensity, such as turnover, advancing/declining breadth, limit-up count, failed limit-up count, and CLS/KPL activity.
- M / Map: where money is concentrating by theme/sector.
- C / Core: whether the sector has recognized leaders, capacity stocks, dragon-tiger support, or limit-up confirmation.
- T / Timing: whether the theme has actionable timing for tomorrow's auction, opening, intraday divergence, and invalidation.

The output should answer:

- Is the market in attack, structural, mixed, or defensive mode?
- Which themes deserve priority tomorrow?
- Which core names should only be watched, and under what confirmation conditions?
- Which signals invalidate the plan?

## Inputs

Use any available combination:

- CLS market plan CSV from `cls-telegraph-collector/scripts/analyze_cls_market_plan.py`.
- KPL / Tushare `kpl_list` CSV or JSON from `collect_tushare_kpl.py`.
- Eastmoney/AkShare dragon-tiger CSV.
- Market breadth CSV from `scripts/collect_market_breadth.py`, or any compatible overview CSV with columns such as `metric,value`.

The workflow is designed to run even when some inputs are missing. Missing data is written into the report as a limitation.

## Commands

Collect market breadth from Eastmoney/AkShare:

```powershell
python skills\stock-selection\a-share-market-flow-analyst\scripts\collect_market_breadth.py --date 2026-06-04 --history-days 5 --out-dir examples\market\market-breadth
```

Collect index environment:

```powershell
python skills\stock-selection\a-share-market-flow-analyst\scripts\collect_index_environment.py --date 2026-06-04 --out-dir examples\market\index-environment
```

Generate a next-day market-flow plan:

```powershell
python skills\stock-selection\a-share-market-flow-analyst\scripts\analyze_market_flow.py --date 2026-06-04 --cls-plan examples\market\cls-market-plan-kpl\2026-06-04-cls-market-plan.csv --kpl examples\market\tushare-kpl\sample-tushare-kpl.csv --lhb examples\market\dragon-tiger\20260604-eastmoney-lhb.csv --market examples\market\market-breadth\2026-06-04-market-breadth.csv --out-dir examples\market\market-flow
```

Generate a post-market daily review:

```powershell
python skills\stock-selection\a-share-market-flow-analyst\scripts\generate_daily_review.py --date 2026-06-04 --index-env examples\market\index-environment\2026-06-04-index-environment.csv --market-breadth examples\market\market-breadth\2026-06-04-market-breadth.csv --theme-plan examples\market\market-flow\2026-06-04-market-flow.csv --kpl examples\market\tushare-kpl\sample-tushare-kpl.csv --out-dir examples\market\daily-review
```

The script writes:

- `<date>-market-breadth.csv`: market breadth metrics, including turnover, advancing/declining counts when available, limit-up count, failed-limit count, limit-down count, seal rate, failed-limit rate, and recent trend deltas.
- `<date>-market-breadth-history.csv`: recent daily limit-pool history used as context.
- `<date>-index-environment.csv`: major index trend and style environment.
- `<date>-market-flow.csv`: theme score table.
- `<date>-market-flow.md`: readable market state and next-day observation plan.
- `<date>-daily-review.md`: post-market review with breadth, fragmentation, leading theme internal movement, tomorrow attack plan, attack target pool, and risk warnings.

## Reading The Result

Use the result as a decision aid:

- `重点进攻`: only when theme score is high and there is both map concentration and core confirmation.
- `积极观察`: theme has evidence but needs auction/opening confirmation.
- `跟踪等待`: theme has news but lacks money/core confirmation.
- `放弃`: score weak or invalidation signal is active.

For tomorrow's plan, prefer scenarios over predictions:

- Strong auction plus front-row continuation: follow the leader or capacity core only after confirmation.
- Strong news but weak board response: do not chase.
- Dragon-tiger net buying supports the same core names: raise priority.
- Failed limit-up or high-open fade in the theme core: reduce priority.
