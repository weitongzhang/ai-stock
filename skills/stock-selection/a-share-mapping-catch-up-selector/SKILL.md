---
name: a-share-mapping-catch-up-selector
description: Use this skill for A-share mapping catch-up stock selection when the user asks to discover hot themes, hot core stocks, and related lagging candidates through parent-subsidiary, spin-off, equity holding, same-group, upstream/downstream, resource platform, or sector chain relationships. It applies the "go where the fish are" principle: first judge whether the theme pond has enough liquidity, breadth, recognition, and persistence, then map relationship chains, filter false concepts, maintain long-term watch pools, mark downgrades/removals, and output observation or trigger plans. Coordinate with a-share-market-flow-analyst, FTShare-market-data, a-share-halfway-trade-screener, watchlist-tracker, and stock-trade skills when available.
---

# A-Share Mapping Catch-Up Selector

## Role

Use this skill to find and rank A-share candidates that may be re-priced after a hot, high-elasticity core stock has already created market recognition.

Default to Chinese output when the user asks in Chinese.

This skill is for research and observation planning. It does not convert relationship logic into a buy signal without price/volume confirmation.

## Core Principle

Apply the Munger-style rule: **先找鱼多的池塘，再找鱼，再等合适下钩点**.

In trading terms:

```text
theme pond quality
-> hot elastic core stock
-> clear relationship chain
-> lower-position or larger-cap mapping candidate
-> price/volume confirmation
-> executable trigger or watchlist decision
```

Do not spend equal effort on every stock. If the pond has no money, no breadth, no recognized core, or no persistence, downgrade the whole chain even if the relationship looks interesting.

Treat relationship mining as a **secondary strategy**, not a standalone buy reason. A stock with a relationship but without pond quality, core-stock validation, and price/volume confirmation should enter the observation pool first, not the trading pool.

## Two Pools

Always maintain two pools:

- **长期映射观察池**: validated relationship chains tracked across days/weeks, even when they are not today's top gainers.
- **今日新发现池**: fresh hot cores and newly activated relationship chains found from today's涨幅榜、成交额榜、板块强度 or news.

Do not drop a validated mapping chain only because the core stock is down on the day. A high-volume core分歧 plus mapping candidate承接 is often a key observation state.

## Required Inputs

Use any available combination:

- Theme/sector strength: market-flow output, limit-up clusters, 20cm leaders, turnover leaders, sector breadth.
- Core stock name/code, if the user already provides one.
- Relationship evidence: annual report, prospectus, official company profile, equity holding, same controller, supply chain, customer/supplier, same group, sector taxonomy, news.
- Quotes/OHLC for both core stocks and candidate mapping stocks.
- Market environment and sector strength.

If data is incomplete, say which layer is missing and downgrade confidence instead of forcing a conclusion.

## Workflow

1. **Judge pond quality first**
   - Use `references/pond-quality.md` to classify the theme as `富矿池`, `活跃池`, `观察池`, or `贫瘠池`.
   - Reject or downgrade chains in a贫瘠池 even if a single stock rises.
   - Prefer ponds with repeated money flow, recognized core stocks, breadth, and a simple narrative.

2. **Load existing mapping watch pool**
   - Start from known validated chains before scanning today's new leaders.
   - Include chains mentioned by the user in recent analysis, such as `铜冠铜箔 -> 铜陵有色` and `大族数控 -> 大族激光` when relevant.
   - Classify each chain as `活跃`, `核心分歧-映射承接`, `降温`, `降级`, `观察期`, or `失效`.
   - Explicitly mark candidates that no longer fit the strategy; do not silently omit them.
   - Read `references/watch-pool.md` when maintaining a durable mapping list.

3. **Detect hot core stocks**
   - Prefer current market-flow outputs, limit-up clusters, 20cm leaders, high-turnover new highs, and sector front-row stocks.
   - A valid core stock should have both price strength and market recognition. One-day news spikes are not enough.

4. **Classify the core type**
   - Spin-off/subsidiary core.
   - Parent-company asset revaluation core.
   - Industrial chain elastic core.
   - Resource price core.
   - New technology or product validation core.
   - Policy or order catalyst core.

5. **Build the relationship map**
   - Search for parent company, controlling shareholder, actual controller, subsidiaries, invested companies, same group listed platforms, upstream resources, downstream demand, equipment suppliers, materials suppliers, and close peer companies.
   - Separate strong relationships from weak concept tags.
   - Use `references/relationship-and-scoring.md` for the relationship strength ladder and scorecard.

6. **Filter false mapping**
   - Reject candidates where the relationship is only同概念 but has no asset, revenue, supply-chain, or market-recognized link.
   - Reject candidates whose market cap/float/liquidity makes catch-up impractical.
   - Reject candidates already more extended than the core or showing high-volume stagnation.
   - Reject candidates if the hot core stock has entered clear退潮.
   - Downgrade same-group or weak-equity relationships to observation unless the market has already recognized the chain.

7. **Apply the secondary-strategy gate**
   - A relationship candidate can upgrade from `观察池` to `候选观察` only when the pond is at least `活跃池` and the core stock remains recognizable.
   - It can upgrade to `重点观察` only after the candidate itself confirms with volume, breakout, or controlled pullback承接.
   - If the relationship is valid but the pond is cold, output `观察池，不交易`.

8. **Score candidates**
   - Pond quality: 20
   - Relationship strength: 25
   - Core stock strength and persistence: 15
   - Candidate position and catch-up room: 15
   - Liquidity/capacity and market acceptance: 10
   - Price/volume trigger quality: 10
   - Catalyst clarity and narrative simplicity: 5

9. **Classify output**
   - 80-100: `重点观察，可等触发`
   - 65-79: `候选观察，等确认`
   - 50-64: `逻辑观察，暂不交易`
   - Below 50: `剔除`

## Trigger Rules

Do not treat relationship discovery as a buy point. Require at least one:

- Candidate放量突破 key platform/high.
- Candidate回踩不破 key support or MA5/MA10 after first recognition.
- Core stock continues strong while candidate starts主动放量.
- Sector breadth expands from one core into multiple related stocks.
- News/公告/互动易 confirms the relationship and price reacts positively.

## Negative Marking

For long-term tracking, output one of:

- `保留`: Chain remains valid and should stay in the watch pool.
- `降级`: Chain still has logic, but current pond quality, price/volume, or sector state is no longer actionable.
- `观察期`: Chain failed once but deserves one more review because relationship strength is high.
- `剔除`: Chain no longer fits; mark the reason and do not keep it in active candidates.

Never hide a removed candidate. State why it failed, such as核心退潮、映射票不承接、关系弱、突破失败、鱼塘退潮 or sector失去主线.

## Relationship Mining Boundary

Use relationship mining to discover candidates, not to justify a trade after the fact.

Default states:

- Strong parent/subsidiary or spin-off relationship: can enter `候选观察` if pond quality is at least活跃池.
- Same-group/platform relationship: start as `观察池`; upgrade only after market recognition.
- Same concept without official relationship: usually `逻辑观察` or `剔除`.
- Interesting but cold pond: `观察池，不交易`.

Example: 有研新材 can be tracked as a同集团央企新材料平台映射 if有研系/新材料/稀土/半导体材料 becomes active, but it should not be treated as a strong子母映射 unless official ownership and market recognition support that conclusion.

## Output Contract

For automatic discovery:

```text
鱼塘质量：
- 主线/板块：富矿池 / 活跃池 / 观察池 / 贫瘠池
- 依据：资金、核心票、扩散、持续性、叙事清晰度

长期映射观察池：
- 链条A：状态 / 今日核心表现 / 映射票表现 / 继续跟踪理由 / 失效条件
- 链条B：...

降级/剔除标记：
- 链条C：降级/观察期/剔除 / 失败原因 / 下次恢复条件
- 标的D：剔除原因 / 是否需要后续复查

二级策略边界：
- 关系是否足够强：强子母 / 同集团 / 产业链 / 同概念
- 是否已经被市场认可：是/否
- 当前状态：观察池 / 候选观察 / 重点观察 / 剔除

今日新发现：
- 核心票：...
- 核心类型：...
- 强度判断：...

关系链：
- 强关系：...
- 中关系：...
- 弱关系/剔除：...

候选分级：
1. 股票A：评分 / 鱼塘 / 关系 / 位置 / 触发位 / 失效位 / 观察结论
2. 股票B：...
```

## Coordination

- Use `a-share-market-flow-analyst` to identify current hot themes and core stocks.
- Use `FTShare-market-data` or available quote/K-line providers for quotes, OHLC, turnover, and market cap.
- Use `a-share-halfway-trade-screener` when turning a candidate into intraday execution.
- Use `a-share-stock-trade-operator` when the user asks whether to buy/sell/add/reduce a specific candidate.
- Use `watchlist-tracker` to maintain candidates that are logical but not yet triggered.

## More Detail

Read `references/pond-quality.md` when:

- Deciding whether a theme deserves attention before stock selection.
- Explaining why a stock is not worth tracking despite a relationship.
- Comparing multiple theme ponds such as Rubin液冷、铜箔、PCB设备、有色资源、金融科技.

Read `references/relationship-and-scoring.md` when:

- Building a relationship map.
- Scoring multiple candidates.
- Explaining why a candidate is true mapping or false mapping.

Read `references/watch-pool.md` when:

- The user wants longer-term tracking rather than one-day screening.
- A previously validated mapping chain is in high-volume分歧 or the mapping candidate is承接.
- Deciding whether to keep, downgrade, or invalidate a mapping chain after several sessions.
