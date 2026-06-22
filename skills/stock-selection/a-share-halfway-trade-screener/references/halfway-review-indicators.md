# Halfway Review Indicators

Use this reference when reviewing whether a halfway trade setup was valid, why it succeeded or failed, and which candidates should be prepared for the next session.

The review should not only ask whether the stock rose. It should verify whether the trade matched the model: market permission, sector mainline, front-row stock behavior, healthy intraday volume, controllable risk, and next-day feedback.

## Existing Project Indicators

| Review layer | Project source | How to use it for halfway review |
| --- | --- | --- |
| Market breadth | `src/skill_lab/market_analysis/breadth.py`; `skills/stock-selection/a-share-market-flow-analyst/scripts/collect_market_breadth.py` | Decide whether the day allowed halfway trades. Focus on limit-up count, failed-board rate, limit-down pressure, breadth trend, and whether short-term sentiment was improving or fading. |
| Index environment | `src/skill_lab/market_analysis/index_environment.py`; `skills/stock-selection/a-share-market-flow-analyst/scripts/collect_index_environment.py` | Check whether Shanghai, ChiNext, STAR 50, or other relevant indexes supported the style. Halfway trades work better when the relevant style index is strong or at least not falling fast. |
| Market regime and position bias | `src/skill_lab/market_analysis/regime.py`; `src/skill_lab/market_analysis/position.py` | Convert market condition into execution intensity: can attack, observe only, lower size, or stop trading. |
| Board turnover share | `tools/generate_board_turnover_share_chart.py` | Track ChiNext and STAR board turnover share. Rising share supports 20cm/technology halfway setups; falling share warns that the style may be losing funding. |
| Sector and theme flow | `skills/stock-selection/a-share-market-flow-analyst/scripts/analyze_market_flow.py` | Rank the active themes and verify whether the candidate belonged to a top 1-3 same-day sector. |
| Daily review and tomorrow plan | `src/skill_lab/planning/daily_review.py`; `src/skill_lab/planning/tomorrow_plan.py`; `tools/run_daily_org_analysis.py` | Connect post-market review with next-day candidate preparation. The review should produce concrete trigger prices, invalidation levels, and sector confirmation rules. |
| Decision journal | `src/skill_lab/tracking/journal.py`; `tools/run_audit_loop_example.py` | Record planned trigger, actual trigger, execution, stop result, close strength, and next-day feedback so the model can be audited. |
| Watchlist tracking | `skills/tracking/watchlist-tracker` | Track whether a prepared candidate triggered, failed, or needs follow-up. |
| FTShare single-stock data | `stock-security-info`, `stock-ohlcs`, intraday price data when available | Review price, change rate, turnover, turnover rate, amplitude, MA5/MA10/MA20, recent volume comparison, and intraday support or failure. |

## Theme Attribution Layer

Before ranking candidates, expand each stock from its raw industry into tradeable theme attributes. Do not rely only on `industry_sector`; A-share money often trades second-order attributes before they are visible in the coarse industry label.

For detailed classification, use `stock-attribute-classification-protocol.md` first. This section is the review summary layer; the protocol is the source of truth for attribute cards, evidence levels, peer groups, and confidence.

Use three evidence levels:

- Level A: confirmed business exposure from company profile, annual report, announcement, or official investor communication.
- Level B: industry-chain mapping supported by product keywords and peer movement.
- Level C: market rumor, influencer narrative, or weak association. Level C can explain attention, but it cannot be the sole buy reason.

For each candidate, write at least one primary attribute and up to three secondary attributes:

```text
股票：深南电路
Primary：AI服务器PCB / 高速PCB
Secondary：封装基板 / FC-BGA / ABF载板链 / 数据中心
Evidence：公司业务含印制电路板、封装基板；市场同日 PCB/封装基板链共振
Action：如果 PCB/ABF 链强于半导体设备，则进入主线半路池
```

```text
股票：莲花控股
Primary：强趋势/连板
Secondary：ABF膜预期 / 算力材料预期 / 转型预期
Evidence：若缺少公告或公司口径，只按市场交易属性处理
Action：进入连板弱转强池，不直接等同于硬逻辑主线核心
```

Common attribute expansions:

| Raw label | Expanded halfway attributes |
| --- | --- |
| 电子元器件 | PCB, 高速PCB, AI服务器PCB, 铜箔, 覆铜板, 封装基板, FC-BGA, ABF载板链 |
| 集成电路 | 存储, 设备, 材料, 先进封装, 国产替代, 科创核心 |
| 通信设备 | CPO, 光模块, 交换机, 800G/1.6T, 卫星互联网, 6G |
| 其他化学制品/材料 | 半导体材料, ABF膜/树脂预期, PI膜, 光刻胶, 有机硅, 电子特气 |
| 电气部件与设备 | 800V高压平台, 电源, 储能, 机器人电机, 服务器电源 |

If a stock has strong price action but its attribute is only Level C, do not shelve it mechanically. Put it into a hypothesis-driven pool with explicit verification rules, smaller size, and faster invalidation. The goal is to keep uncertain but high-payoff opportunities alive while preventing vague stories from polluting the main pool.

## Uncertain Attribute Opportunity Pool

Use this pool when classification is unclear but price action is strong enough that excluding the stock may lose a real market opportunity.

This pool is not a trash bin. It is an active verification list.

Entry requirements:

- Price action is front-row: limit-up, near limit-up, strong reversal, or clear intraday leadership.
- Liquidity is tradable: turnover and turnover rate are enough for execution.
- There is at least one plausible market hypothesis, even if the official evidence is incomplete.
- There are identifiable peer stocks or adjacent themes that can confirm or reject the hypothesis.
- Risk line is close enough to keep the first trade small and reversible.

Output the hypothesis card before ranking:

```text
股票：
Hypothesis：
Possible attributes：
Evidence level：A / B / C / mixed
Peer confirmation：
Trigger：
Invalidation：
Position ceiling：
Upgrade condition：
Downgrade condition：
```

Pool behavior:

- If peer confirmation appears and the stock remains front-row, upgrade it from `uncertain opportunity pool` to `main attack pool`.
- If only the single stock moves and peers do not confirm, keep it as a small-size event trade.
- If price breaks the trigger platform or falls below VWAP after entry, remove it quickly.
- If news or company evidence contradicts the market hypothesis, downgrade it even if price is temporarily strong.
- Never let an uncertain-attribute trade become a large position before confirmation.

Example:

```text
股票：宇环数控
Hypothesis：机器人设备/工业母机链可能被资金交易
Possible attributes：数控磨削设备 / 智能装备 / 机器人制造设备 / 半导体设备边缘映射
Evidence level：B/C mixed
Peer confirmation：工业母机、智能装备、机器人设备链是否同步强于机器人核心零部件
Trigger：涨停次日高开后回踩不破前日涨停价或分时均线，再突破早盘高点
Invalidation：跌破前日涨停价后无法收回，或同属性无跟随
Position ceiling：0.5-1 unit
Upgrade condition：同属性出现多个前排，且该股继续保持强度
Downgrade condition：只有个股独立冲高，无板块承接
```

## Review Score

Score a completed or prepared halfway setup out of 100:

- Market permission: 15
- Theme attribution and sector/mainline strength: 25
- Individual front-row behavior: 20
- Intraday price-volume quality: 20
- Next-day verification and execution discipline: 15
- Evidence quality: 5

Classification:

- 80-100: model match. Keep or prioritize similar setups.
- 65-79: conditionally valid. Improve trigger precision or reduce size.
- 50-64: weak model match. Observe only unless the next day confirms strongly.
- Below 50: reject. Treat as noise, impulse, or rear-row chase.

## Market Permission Checklist

Review these before judging individual stocks:

- Was the broad market rising, stable, or in a fast selloff?
- Did the relevant style index confirm the direction? For technology/20cm trades, check ChiNext and STAR 50.
- Were limit-up stocks increasing or failing?
- Was the failed-board rate acceptable?
- Did board turnover share show money moving toward the candidate's style?

If the market permission layer fails, a strong individual stock should be downgraded. In halfway mode, isolated strength is not enough.

## Sector Review Checklist

For the candidate sector, record:

- Sector rank among same-day themes.
- Whether there were sealed leaders or multiple front-row names.
- Whether high-liquidity core names rose with the sector.
- Whether the candidate was front-row or rear-row.
- Whether the sector strengthened after the candidate entry or weakened.
- Whether the stock's expanded attributes match the strongest branch of the sector.
- Whether there are attribute peers moving together, especially for hidden branches such as ABF膜, FC-BGA, 封装基板, AI服务器PCB, or CPO.

Good halfway trades usually come from top-sector continuation. Bad halfway trades often come from late rear-row diffusion after the leader has already exhausted.

## Individual Stock Review Checklist

For each candidate or executed trade, record:

- Planned trigger price.
- Planned stop or invalidation line.
- Whether price was above intraday average/VWAP at the trigger.
- Whether pullbacks held with lower volume.
- Whether breakouts happened with higher volume.
- Whether the stock made new intraday highs after entry.
- Whether it closed near high, sealed limit-up, or faded.
- Whether the next day opened with premium, neutral feedback, or punishment.

## Output Template

```text
半路复盘结论：有效 / 条件有效 / 失败 / 应剔除

1. 市场环境
- 指数：
- 情绪：
- 风格成交占比：
- 结论：

2. 板块主线
- 板块排名：
- 前排确认：
- 核心中军：
- 结论：

3. 个股行为
- 计划触发：
- 实际走势：
- 量价质量：
- 风险线：
- 收盘反馈：

4. 次日验证
- 观察位：
- 强确认：
- 弱转强失败：
- 止损/减仓：

5. 模式改进
- 保留规则：
- 修正规则：
- 下次剔除条件：
```

## Integration Rule

When preparing tomorrow's halfway candidates, use the review indicators to create the next-day pool:

1. Keep stocks that matched the model and still have a nearby risk line.
2. Downgrade stocks that rose only because of isolated news or influencer attention.
3. Reject stocks with high-volume stagnation, long upper shadow, or sector leader failure.
4. Prefer candidates where market style, sector flow, and individual structure point in the same direction.
