---
name: yc-buy-selector
description: A股技术选股工作流，基于 YC-buy 仓库的13个买点和三重滤网系统。Use when Codex needs to analyze A-share stock candidates, audit or run YC-buy style buy-point screening, explain triggered buy signals, combine long-cycle trend with short-cycle timing, or create CSV stock-selection outputs.
---

# YC Buy Selector

Use this skill for A股技术选股 requests that mention 13个买点、三重滤网、道氏/威科夫/波浪理论、A股买点筛选、突破/回踩/箱体弹簧, or the `pinarocko346-creator/YC-buy` repository.

## Workflow

1. Confirm the working directory contains the YC-buy project or ask for the repo path.
2. Prefer running the wrapper script:

```powershell
python scripts\screen_yc_buy.py --repo <YC-buy路径> --codes 000001,600519 --source sample --mode both
```

3. For real market data, use `--source akshare` or `--source auto`; if dependencies or network fail, report that the result used sample data instead.
4. Read `references/logic-notes.md` before changing strategy code or explaining why a signal did/did not trigger.
5. Treat output as research only. Always mention that technical signals are not investment advice.

## Interpretation Rules

- Use三重滤网先定方向: long-cycle MACD trend up/down/neutral.
- Use13个买点找时机: bottom reversal, breakout/continuation, trend pullback.
- Prefer candidates where both systems agree: `buy`, `wait_breakout`, or `consider_buy` plus at least one concrete buy point.
- Be cautious with single low-quality signals caused by synthetic/sample data, thin volume, or only one-day price spikes.
- When auditing code, verify that current-day K线 is excluded from historical resistance/box comparisons.

## Script

`scripts/screen_yc_buy.py` runs the repo's own data fetcher and strategy classes, prints concise results, and writes a CSV when `--output` is supplied.
