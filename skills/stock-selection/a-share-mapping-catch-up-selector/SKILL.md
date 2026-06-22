---
name: a-share-mapping-catch-up-selector
description: Use this skill for A-share "mapping catch-up" stock selection when the user asks to discover hot core stocks and find related lagging candidates through parent-subsidiary, spin-off, equity holding, same-group, upstream/downstream, resource platform, or sector chain relationships. It identifies high-elasticity core stocks, maps relationship chains, filters false concept associations, scores catch-up candidates, and outputs observation or trigger plans. Coordinate with a-share-market-flow-analyst, FTShare-market-data, a-share-halfway-trade-screener, watchlist-tracker, and stock-trade skills when available.
---

# A-Share Mapping Catch-Up Selector

## Role

Use this skill to find and rank A-share candidates that may be re-priced after a hot, high-elasticity core stock has already created market recognition.

Default to Chinese output when the user asks in Chinese.

This skill is for research and observation planning. It does not convert relationship logic into a buy signal without price/volume confirmation.

## Core Idea

Screen for:

```text
hot elastic core stock
-> clear relationship chain
-> lower-position or larger-cap mapping candidate
-> market starts to recognize the relationship
-> price/volume confirms catch-up or revaluation
```

Typical examples:

- A spin-off or subsidiary surges, then the parent company is revalued.
- A high-elasticity materials/equipment stock leads, then a resource platform, parent company, or capacity carrier catches up.
- A small-cap thematic core opens space, then the market looks for larger, liquid, easier-to-hold related stocks.

Always separate two pools:

- **Long-term mapping watch pool**: relationship chains that have already been validated by the market and should be tracked across days/weeks even when they are not today's top gainers.
- **Daily new discovery pool**: fresh hot cores and newly activated relationship chains found from today's涨幅榜,成交额榜,板块强度, or news.

Do not drop a validated mapping chain only because the core stock is down on the day. A high-volume core分歧 plus mapping candidate承接 is often the key observation state.

## Required Inputs

Use any available combination:

- Hot stocks from涨幅榜,连板/20cm,成交额榜,换手率榜,近期新高, or market-flow outputs.
- Core stock name/code, if the user already provides one.
- Relationship evidence: annual report, prospectus, official company profile, equity holding, same controller, supply chain, customer/supplier, same group, sector taxonomy, news.
- Quotes/OHLC for both core stocks and candidate mapping stocks.
- Market environment and sector strength.

If data is incomplete, say which layer is missing and downgrade confidence instead of forcing a conclusion.

## Workflow

1. **Load existing mapping watch pool**
   - Start from known validated chains before scanning today's new leaders.
   - Include chains mentioned by the user in recent analysis, such as 铜冠铜箔->铜陵有色 and 大族数控->大族激光 when relevant.
   - Classify each chain as `活跃`, `核心分歧-映射承接`, `降温`, `降级`, `观察期`, or `失效`.
   - Explicitly mark candidates that no longer fit the strategy; do not silently omit them.
   - Read `references/watch-pool.md` when maintaining a durable mapping list.

2. **Detect hot core stocks**
   - Prefer current market-flow outputs, limit-up clusters, 20cm leaders, high-turnover new highs, and sector front-row stocks.
   - A valid core stock should have both price strength and market recognition. One-day news spikes are not enough.

3. **Classify the core type**
   - Spin-off/subsidiary core.
   - Parent-company asset revaluation core.
   - Industrial chain elastic core.
   - Resource price core.
   - New technology or product validation core.
   - Policy or order catalyst core.

4. **Build the relationship map**
   - Search for parent company, controlling shareholder, actual controller, subsidiaries, invested companies, same group listed platforms, upstream resources, downstream demand, equipment suppliers, materials suppliers, and close peer companies.
   - Separate strong relationships from weak concept tags.
   - Use `references/relationship-and-scoring.md` for the relationship strength ladder and scorecard.

5. **Filter false mapping**
   - Reject candidates where the relationship is only同概念 but has no asset, revenue, supply-chain, or market-recognized link.
   - Reject candidates whose market cap/float/liquidity makes catch-up impractical.
   - Reject candidates already more extended than the core or showing high-volume stagnation.
   - Reject candidates if the hot core stock has entered clear退潮.

6. **Score candidates**
   - Relationship strength: 30
   - Core stock strength and persistence: 20
   - Candidate position and catch-up room: 15
   - Liquidity/capacity and market acceptance: 10
   - Price/volume trigger quality: 15
   - Catalyst clarity and narrative simplicity: 10

7. **Classify output**
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

## Invalidation Rules

Downgrade or remove candidates when:

- Core stock breaks down with high volume or enters clear退潮.
- Candidate cannot rise while the core and sector remain strong.
- Candidate breaks the mapped support after a failed breakout.
- Relationship evidence is weak, outdated, or market does not recognize it.
- The market environment shifts from attack to defensive mode.

For long-term tracking, output one of:

- `保留`: Chain remains valid and should stay in the watch pool.
- `降级`: Chain still has logic, but current price/volume or sector state is no longer actionable.
- `观察期`: Chain failed once but deserves one more review because relationship strength is high.
- `剔除`: Chain no longer fits; mark the reason and do not keep it in active candidates.

Never hide a removed candidate. State why it failed, such as core退潮, mapping票不承接, relationship weak, repeated failed breakout, or sector失去主线.

## Output Contract

For automatic discovery:

```text
长期映射观察池：
- 链条A：状态 / 今日核心表现 / 映射票表现 / 继续跟踪理由 / 失效条件
- 链条B：...

降级/剔除标记：
- 链条C：降级/观察期/剔除 / 失败原因 / 下次恢复条件
- 标的D：剔除原因 / 是否需要后续复查

当前映射主线：
- 核心票：...
- 核心类型：...
- 强度判断：...

关系链：
- 强关系：...
- 中关系：...
- 弱关系/剔除：...

候选分级：
1. 股票A：评分 / 关系 / 位置 / 触发位 / 失效位 / 观察结论
2. 股票B：...

今日不做的原因：
- ...
```

For a core stock provided by the user:

```text
核心票判断：
- ...

可映射方向：
- 母公司/控股平台：...
- 同集团/参股：...
- 上游/下游：...
- 同概念低位：...

优先候选：
- ...

执行边界：
- 触发：...
- 失效：...
```

## Coordination

- Use `a-share-market-flow-analyst` to identify current hot themes and core stocks.
- Use `FTShare-market-data` or available quote/K-line providers for quotes, OHLC, turnover, and market cap.
- Use `a-share-halfway-trade-screener` when turning a candidate into intraday execution.
- Use `a-share-stock-trade-operator` when the user asks whether to buy/sell/add/reduce a specific candidate.
- Use `watchlist-tracker` to maintain candidates that are logical but not yet triggered.
- Use the long-term mapping watch pool before daily scanning so validated chains are not missed.

## More Detail

Read `references/relationship-and-scoring.md` when:

- Building a relationship map.
- Scoring multiple candidates.
- Explaining why a candidate is true mapping or false mapping.
- Converting examples such as 大族数控->大族激光 or 铜冠铜箔->铜陵有色 into reusable selection logic.

Read `references/watch-pool.md` when:

- The user wants longer-term tracking rather than one-day screening.
- A previously validated mapping chain is in high-volume分歧 or the mapping candidate is承接.
- Deciding whether to keep, downgrade, or invalidate a mapping chain after several sessions.
