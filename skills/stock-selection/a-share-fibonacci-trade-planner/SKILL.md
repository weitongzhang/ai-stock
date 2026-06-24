---
name: a-share-fibonacci-trade-planner
description: Use this skill for A-share Fibonacci trading plans across indices, sector indices, ETFs, and individual stocks. It defines Fibonacci retracement and extension levels, ranks applicability by instrument type, and converts levels into executable attack/defense trigger plans with volume, sector, and trend confirmation.
---

# A-Share Fibonacci Trade Planner

Use this skill when the user asks about 斐波那契, 黄金分割, 回撤位, 扩展位, 进攻位, 支撑压力, or asks for a trading plan that needs clear price levels.

## Core Principle

Fibonacci is a location framework, not a standalone signal and not a prediction engine. It answers:

- Where can price react?
- Where does attack space open?
- Where should risk fail?
- Where is the risk/reward no longer attractive?

It does not answer by itself whether to buy or sell. Always combine it with trend, volume, sector/index confirmation, and price behavior.

## Applicability Priority

Prefer Fibonacci on broad and liquid instruments before using it on single stocks:

1. **Broad indices**: highest reliability because they reflect group behavior and deep liquidity.
2. **Sector indices / industry baskets / ETFs**: very useful for judging whether a theme has room to attack or is near pressure.
3. **Institutional trend stocks**: usable when trend is clear, liquidity is high, and K-line structure is complete.
4. **Theme leaders**: usable only with strong sector confirmation and active turnover.
5. **Weak fit**: illiquid stocks, pure news spikes, one-word limit-up chains, suspected manipulated names, or stocks without a complete swing structure.

When analyzing a single stock, first ask whether the relevant index or sector is also confirming. If not, downgrade the confidence of the individual-stock Fibonacci plan.

## Required Data

Use market data first when available:

- For indices or ETFs: recent OHLC, current price, MA5/MA10/MA20, volume or turnover if available.
- For stocks: current quote, recent 40-80 daily bars, turnover, amount, MA5/MA10/MA20, previous swing high/low, and sector/index context.
- For intraday attack decisions: add 5-minute or minute behavior when available.

## Anchor Selection

Select anchors from visible market structure, not arbitrary points.

- Uptrend pullback: swing low to swing high.
- Downtrend rebound: swing high to swing low.
- Breakout extension: most recent meaningful low to breakout high, or prior range low to range high.
- If multiple anchors are plausible, show the primary anchor and mark secondary anchors as reference only.

Do not force Fibonacci on a chart with no clean swing, news gap only, or chaotic consolidation.

## Level Map

Retracement levels:

```text
23.6%, 38.2%, 50%, 61.8%, 78.6%
```

Extension levels:

```text
1.272, 1.382, 1.618, 2.000
```

Interpretation:

- 38.2%: strong trend pullback.
- 50%: normal pullback.
- 61.8%: key trend test.
- 78.6%: deep pullback; failure risk rises after losing it.
- 1.272/1.382: first attack target zone.
- 1.618: strong trend target.
- 2.000: extreme attack target; requires strong market/sector support.

## Trading Plan Rules

Always separate **defense map** from **attack map**:

```text
Defense map: retracement supports, invalidation, profit protection.
Attack map: breakout trigger, extension targets, no-chase zone.
```

For single-stock attack plans:

- Breakout buy requires price to break the prior high or key Fibonacci pressure.
- Require volume expansion, sector/index confirmation, or a pullback that does not lose the breakout level.
- Do not recommend adding just because price touches a retracement support.
- Prefer "breakout then pullback holds" for losing or passive positions.
- For profitable positions, extension zones are profit-management zones, not blind sell points.

## Output Contract

Use this structure:

```text
适用性判断：
- 标的类型：
- 斐波那契适配度：
- 是否需要先看指数/板块：

结构锚点：
- 主锚点：
- 当前所处区间：

防守地图：
- 第一支撑：
- 强弱分界：
- 失效位：

进攻地图：
- 突破触发：
- 第一目标：
- 第二目标：
- 强趋势目标：
- 不追条件：

操作计划：
- 当前建议：
- 加仓/买入条件：
- 持有条件：
- 减仓/止盈条件：
- 止损/失效条件：
```

## Script

For deterministic level calculation, use:

```bash
python scripts/calculate_fibonacci_plan.py --low 5.70 --high 8.02 --current 7.93 --trend up
python scripts/calculate_fibonacci_plan.py --high 46.49 --low 34.09 --current 35.84 --trend down
```

