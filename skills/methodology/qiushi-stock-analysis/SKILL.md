---
name: qiushi-stock-analysis
description: Use this skill for A-share stock, sector, theme, index, ETF, watchlist, holding, position sizing, buy/sell timing, risk control, or next-trading-day analysis when the user wants market judgment grounded in data. It makes Qiushi methods the planning brain: investigate first, identify the principal contradiction, concentrate on the key decision, then verify with market data. Prefer workspace FTShare-market-data and existing A-share analysis skills for data collection.
---

# Qiushi Stock Analysis

## Role

Use this skill as the orchestration layer for stock-market analysis. It does not replace data-provider or strategy skills. It decides what facts must be collected, calls the appropriate data skills, then turns evidence into a concrete research plan.

Default to Chinese output when the user asks in Chinese.

## Workflow

Always follow this order:

1. **调查研究**
   - State the exact question being investigated.
   - List the required facts before giving a view.
   - Prefer current structured data over memory or media summaries.

2. **数据查询规划**
   - For A-share data, prefer `skills/market-data/ftshare-market-data/run.py`.
   - Use `stock-security-info` for single-stock quote, valuation, turnover, and company summary.
   - Use `stock-ohlcs` for OHLC, volume, amount, MA5/MA10/MA20, support, and resistance.
   - Use `stock-quotes-list` for market or peer comparison.
   - Use `margin-trading-details` when leverage or crowded positioning matters.
   - Use `semantic-search-news` only for recent catalysts, and label it as news evidence.
   - Use `a-share-market-flow-analyst` when the question is about sector priority, money flow, theme strength, or next-day plans.
   - Use `a-share-bsa-lift-analyst` when the question is about a specific stock's trade plan, leader status, breakout, add/hold/reduce/exit action, or intraday operation.
   - If a required live data source fails, say which source failed and fall back to the best available structured source or clearly marked public-source evidence.

3. **矛盾分析**
   - List the competing forces as `[A] vs [B]`.
   - Mark one principal contradiction.
   - Explain why solving it determines the current decision.

4. **集中兵力**
   - Do not scatter across many stocks or sectors when the user asks for an operation.
   - Pick the main decision first: add, hold, reduce, exit, or wait.
   - Treat other opportunities as observation items unless they directly affect the main decision.

5. **实践检验**
   - Convert the view into trigger conditions.
   - Include invalidation levels, confirmation signals, and next review time if relevant.
   - Never present a prediction without a condition that would prove it wrong.

## Output Contract

For holdings or operation questions, output:

```text
调查结论：
- ...

主要矛盾：
- [A] vs [B]
- 主要矛盾：...

当前建议：
- 持有 / 可小加 / 减仓 / 等待 / 退出

触发条件：
- 加仓条件：...
- 减仓条件：...
- 失效条件：...

仓位纪律：
- ...
```

For sector or stock-picking questions, output:

```text
调查结论：
- ...

板块优先级：
1. ...

主攻方向：
- ...

确认信号：
- ...

放弃条件：
- ...
```

## Guardrails

- Do not call a stock "buyable" just because it is thematically strong.
- Separate company quality from trade timing.
- Separate sector strength from individual-stock leadership.
- Treat high-open chase, one-day media/KOL catalysts, and crowded margin positions as risk factors.
- When the user gives cost and position, prioritize risk of the existing position before new opportunities.
- Use research language. Do not claim certainty or guarantee returns.
