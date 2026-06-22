---
name: sector-money-flow-chart
description: Generate A-share sector intraday money-flow style charts, including vertical mobile-style SVG charts, CSV outputs, and data-quality notes. Use when the user asks to make charts like 板块主力资金净流入分时图, 板块资金曲线, sector money-flow visualization, or daily sector flow replay.
---

# Sector Money Flow Chart

This skill generates the multi-line intraday sector chart used for market replay.

Default to Chinese when the user asks in Chinese.

## What This Skill Does

- Render a vertical mobile-style SVG, a single-date animated HTML replay, and a full-screen multi-date browser player similar to "主力资金净流入" screenshots.
- Read true sector minute-flow data from CSV when available.
- Try Eastmoney/AkShare board minute data as a degraded proxy when minute money-flow is not available.
- Build a FTShare intraday proxy from top-turnover stocks grouped by `industry_sector`.
- Write a data-quality note so simulated/proxy data is never confused with real minute main-fund flow.

## Data Truth Rules

Do not label a chart as "真实主力净流入" unless the input data is true minute-level sector main-fund net inflow.

Supported data levels:

- `real`: CSV contains minute sector net inflow values.
- `proxy`: built from board minute price/amount data; useful for replay shape, not equal to main-fund flow.
- `demo`: simulated data for style testing only.

## Primary Command

```powershell
python skills\stock-selection\sector-money-flow-chart\scripts\generate_sector_money_flow_chart.py --date 2026-06-22 --mode demo --out-dir reports\sector-money-flow
```

The command writes:

- `<date>-sector-money-flow.svg`
- `<date>-sector-money-flow.html`
- `index.html`
- `<date>-sector-money-flow.csv`
- `<date>-sector-money-flow-quality.md`

The per-date HTML file is self-contained and can be opened directly in a browser. `index.html` is a full-screen player that embeds all generated trading-day CSV files in the output directory and supports trading-day selection, replay, pause, and 0.5x/1x/2x playback speed.

## Real CSV Input

Use this mode when you have true minute sector net inflow data:

```powershell
python skills\stock-selection\sector-money-flow-chart\scripts\generate_sector_money_flow_chart.py --date 2026-06-22 --mode csv --input-csv data\sector_minute_flow.csv --out-dir reports\sector-money-flow
```

CSV columns:

- `time`: `09:30`, `09:31`, ...
- `sector`: board/theme name
- `value_yi`: cumulative net inflow in 亿元

Optional columns:

- `source`
- `data_level`

## Eastmoney Proxy Mode

```powershell
python skills\stock-selection\sector-money-flow-chart\scripts\generate_sector_money_flow_chart.py --date 2026-06-22 --mode eastmoney-board --sectors 半导体,存储芯片,证券,有色金属,机器人 --board-type concept --out-dir reports\sector-money-flow
```

This tries `akshare.stock_board_concept_hist_min_em` or `stock_board_industry_hist_min_em`.

If Eastmoney rejects the connection, the command exits with a clear `blocked` quality note unless `--fallback-demo` is provided.

## FTShare Aggregate Proxy Mode

Use this when real sector minute main-fund flow is unavailable but FTShare stock minute data is available:

```powershell
python skills\stock-selection\sector-money-flow-chart\scripts\generate_sector_money_flow_chart.py --date 2026-06-22 --mode ftshare-aggregate --sample-size 80 --top-n 20 --out-dir reports\sector-money-flow
```

How it works:

- Pulls top-turnover A-shares through `stock-quotes-list`.
- Groups sampled stocks by `industry_sector`.
- Pulls each stock's one-minute `stock-prices`.
- Signs each minute's turnover by price direction and accumulates by sector.

This is a `proxy` level signal. It can help identify intraday sector承接/掉队, but it is not true main-fund net inflow.

## How To Use In Review

Read the quality file before interpreting the chart:

- `real`: can be used to judge sector main-fund persistence, divergence, and tail buying.
- `proxy`: use only for relative board intraday strength, not money-flow amount.
- `demo`: visual template only.

For trading analysis, combine the chart with:

- `a-share-market-flow-analyst` for market state and sector priority.
- `a-share-halfway-trade-screener` for intraday candidate execution.
- `qiushi-stock-analysis` for principal contradiction and position plan.
