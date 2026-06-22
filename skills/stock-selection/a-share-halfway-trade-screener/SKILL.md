---
name: a-share-halfway-trade-screener
description: Use this skill for A-share intraday "半路" trading candidate screening when the user asks which stocks can be bought before涨停, which sectors have halfway opportunities today, or how to select/manage半路模式标的. It combines market mainline judgment, sector strength, front-row stock identification, intraday price/volume confirmation, and strict stop-loss/position rules. Prefer FTShare-market-data, a-share-market-flow-analyst, qiushi-stock-analysis, and BSA/LIFT style price behavior evidence.
---

# A-Share Halfway Trade Screener

## Role

Use this skill to find and rank intraday A-share "半路" candidates. 半路 means buying a strong stock before涨停/加速 confirmation, not chasing any stock that is already up.

Default to Chinese output when the user asks in Chinese.

## Core Principle

Only screen for **强上加强**:

- Strong market or at least non-crashing index environment.
- Clear same-day mainline or sector money flow.
- Sector has front-row confirmation, not one isolated stock.
- Candidate has主动上攻, healthy volume, and intraday support.
- Risk can be controlled within a nearby invalidation line.

If these are absent, output `当前建议：今日不做半路，等待`.

## Data Plan

Collect only the facts needed for same-day execution:

1. **Market environment**
   - Index detail for 上证/创业板/科创50 when relevant.
   - Market breadth or market-flow skill output when available.
   - Avoid halfway mode during broad intraday selloff.

2. **Sector/mainline**
   - Use `a-share-market-flow-analyst` when available to identify top sectors, limit-up clusters, and sector priority.
   - If no sector tool is available, use current quotes/news for the candidate sector and at least 2-3 peer references.

3. **Candidate stocks**
   - Use FTShare `stock-security-info` for price,涨跌幅, high/low,成交额,换手,估值,委比.
   - Use `stock-ohlcs` for recent volume, prior high/low, MA5/MA10/MA20, whether the move is fresh or extended.
   - Use `semantic-search-news` only to explain catalysts; never use news alone as a buy signal.
   - Use `references/stock-attribute-classification-protocol.md` to classify candidate attributes before ranking; raw industry labels are not enough.

## Candidate Filters

Reject a stock if any hard reject applies:

- Sector is not today's mainline or has no front-row confirmation.
- Stock is below VWAP/分时均线 and cannot reclaim.
- Up move is a single vertical spike with no pullback support.
- Turnover is extreme and price cannot make new highs: high-volume stagnation.
- Candidate is only media/KOL-driven without sector confirmation.
- Stock already has a large multi-day gain and is at high-volume resistance.
- Risk line is too far, making stop loss larger than 3%-4%.

Prefer candidates with:

- Gain usually in the 3%-8% observation zone before final acceleration.
- Price above intraday average price and pullbacks hold.
- Intraday lows lift step by step.
- Second push breaks the first high with volume.
- Sector has at least one leader sealed or several front-row stocks rising together.
- Volume is higher than recent average but not exhausted.

## Scoring

Rank candidates by 100 points:

- Market environment: 15
- Sector strength and front-row confirmation: 25
- Individual initiative and intraday structure: 25
- Volume quality: 15
- Risk/reward and stop distance: 15
- Catalyst fit: 5

Classification:

- 80-100: `可半路观察/小仓试`
- 65-79: `候选观察，等回踩确认`
- 50-64: `只观察，不买`
- Below 50: `剔除`

## Buy Setups

Use one of three setups:

1. **VWAP pullback setup**
   - Stock rises actively, pulls back to intraday average/VWAP, does not break, then re-accelerates.
   - Suitable for first small entry.

2. **Intraday high breakout setup**
   - First high forms, pullback holds, second push breaks first high with volume.
   - Better when sector also strengthens.

3. **Pre-limit acceleration setup**
   - Gain is 7%-9%, sector has multiple confirmed leaders, order flow is strong, and price is not high-volume stagnant.
   - Highest risk. Use smallest size.

## Position Rules

- First entry: 0.5-1成.
- Confirmed strength: total no more than 1.5-2成.
- Do not exceed 2成 for one halfway trade.
- If user already has high account exposure, lower to 0.5成 or skip.
- Wrong halfway trade must not become a long-term holding.

## Sell/Stop Rules

Exit or reduce when:

- Price loses intraday average/VWAP and cannot reclaim within 3-5 minutes.
- Breaks the pullback platform low after entry.
- Sector leader opens board/fails and sector rolls over.
- Price is high-volume but cannot make a new high.
- No further strength within 20-30 minutes after entry.

Normal risk control: stop loss around -2% to -3%. If this is impossible, do not buy.

## Output Contract

For screening:

```text
当前建议：今日可做半路 / 只观察 / 今日不做半路

市场与主线：
- ...

候选优先级：
1. 股票A：评分/板块/半路类型/买点/止损/仓位
2. 股票B：...

剔除标的：
- ...

执行纪律：
- ...
```

For one stock:

```text
当前建议：可半路小仓 / 等回踩确认 / 不适合半路

判断：
- 板块：...
- 个股：...
- 量能：...
- 风险：...

触发买点：
- ...

失效条件：
- ...
```

## More Detail

Read `references/halfway-checklist.md` when the user asks for a strict checklist, automation rule, or when screening multiple candidates.

Read `references/stock-attribute-classification-protocol.md` before building or reviewing a candidate pool, especially when the user challenges stock classification, hidden attributes, theme mapping, or missed candidates.

Use `references/theme-taxonomy.md` with the classification protocol for first-pass daily branch tagging. The correction ledger is only an exception memory; taxonomy plus peer validation is the scalable daily coverage layer.

Read `references/halfway-review-indicators.md` when the user asks for post-market review, next-day preparation, model improvement, or whether existing project indicators can support halfway-mode review.
