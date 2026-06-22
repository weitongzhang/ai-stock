# Stock Attribute Classification Protocol

Use this protocol before building a halfway candidate pool. The goal is to improve classification quality so candidate ranking does not depend on a single raw industry field or a vague concept label.

Classification is a separate step from trade selection. A stock can have strong price action, but if its attribute map is wrong, the sector ranking, peer confirmation, and buy trigger will all be polluted.

Version: 2026-06-17. This protocol should evolve after review mistakes. When the user corrects a classification with reasonable evidence, update the correction ledger and reuse that mapping in later reviews.

## Three-Layer Classification

Classify every candidate on three separate layers. Do not merge them too early.

| Layer | Question | Example |
| --- | --- | --- |
| Fact attribute | What does the company actually do? | 深南电路: PCB, 封装基板, 电子装联 |
| Trade attribute | What is the market currently pricing? | 深南电路: AI服务器PCB / FC-BGA / ABF载板链 |
| Tape confirmation | Are peers and funds confirming this attribute? | PCB/ABF peers rising together, front-row stocks sealing or holding VWAP |

Decision rule:

- Fact strong + trade strong + tape confirmed = main attack pool.
- Fact strong + trade plausible + tape partial = trend or board-rush pool.
- Fact weak but trade strong + tape confirmed = uncertain opportunity pool, small size, active verification.
- Fact weak + trade weak + tape isolated = reject.

## Classification Sources

Use evidence in this order:

1. Eastmoney concept and industry board membership when available.
2. Company profile and主营业务 from `stock-security-info`.
3. Annual report, announcement, investor interaction, or official website when available.
4. Product keywords and industry-chain mapping.
5. Same-day peer movement and market style confirmation.
6. News and concept labels.
7. Market rumor or influencer narrative.

Do not treat item 6 or item 7 as enough for main-pool classification unless price action and peer confirmation also support it.

## Eastmoney Board Data

Prefer Eastmoney board membership as the scalable daily classification source instead of manually classifying every stock.

Available AkShare wrappers:

| Data | Function | Eastmoney endpoint pattern | Use |
| --- | --- | --- | --- |
| Concept board list | `ak.stock_board_concept_name_em()` | `push2.eastmoney.com/api/qt/clist/get`, `fs=m:90 t:3 f:!50` | Get all concept boards, daily board strength, leader, up/down counts |
| Concept board constituents | `ak.stock_board_concept_cons_em(symbol)` | `push2.eastmoney.com/api/qt/clist/get`, `fs=b:<BK code> f:!50` | Get stocks inside a concept board |
| Industry board list | `ak.stock_board_industry_name_em()` | `push2.eastmoney.com/api/qt/clist/get`, `fs=m:90 t:2 f:!50` | Get all industry boards and daily strength |
| Industry board constituents | `ak.stock_board_industry_cons_em(symbol)` | `push2.eastmoney.com/api/qt/clist/get`, `fs=b:<BK code> f:!50` | Get stocks inside an industry board |

Practical use:

1. Pull all concept boards and industry boards.
2. Rank boards by涨跌幅, 换手率, 上涨家数, 领涨股票.
3. Pull constituents only for active boards and user-relevant boards.
4. Invert board constituents into `stock -> boards`.
5. Use board membership as first-pass trade attributes.
6. Use taxonomy, company profile, and peer validation to refine or override.

Limitations:

- Eastmoney boards can be broad, delayed, or concept-tag heavy.
- Board membership does not prove revenue exposure.
- Hidden branches such as ABF膜 or robot equipment may still require product keyword and peer validation.
- If Eastmoney endpoint fails, use cached board data, FTShare industry sector, taxonomy keywords, and user corrections as fallback.

Never replace trade judgment with a board tag alone. Use Eastmoney to reduce missed coverage, then use this protocol to classify quality and pool placement.

## Multi-Source Board Tags

Do not depend on one data vendor. Use board tags as a multi-source evidence layer.

Available AkShare sources:

| Source | Functions | Strength | Limitation |
| --- | --- | --- | --- |
| Eastmoney | `stock_board_concept_name_em`, `stock_board_concept_cons_em`, `stock_board_industry_name_em`, `stock_board_industry_cons_em` | Strong for daily board strength, leaders, constituents, turnover and change data | Endpoint can be unstable; concept tags can be broad |
| Tonghuashun | `stock_board_concept_name_ths`, `stock_board_concept_info_ths`, `stock_board_concept_summary_ths`, `stock_board_industry_name_ths`, `stock_board_industry_info_ths`, `stock_board_industry_summary_ths` | Useful for concept/industry names, board descriptions, concept timing and supplementary classification | Some pages may require anti-bot handling; fields may be less standardized |
| Sina | `stock_classify_sina` with `热门概念`, `申万行业`, `申万二级`, `地域板块` | Useful as broad fallback classification and cross-check | Slower and less suitable for detailed theme strength; may time out |
| CNInfo / Shenwan | `stock_industry_category_cninfo`, `stock_industry_clf_hist_sw` | Better for formal industry classification | Less useful for fast trading concepts |

Multi-source scoring:

- If Eastmoney and Tonghuashun agree on a concept/industry, raise classification confidence.
- If one source has a concept and another has only broad industry, keep the concept but require peer validation.
- If sources conflict, prefer the one whose same-day board has stronger tape confirmation.
- If all sources fail, fall back to FTShare industry sector, company profile keywords, taxonomy, and corrections ledger.

Output source evidence when classification matters:

```text
Source tags:
- Eastmoney:
- Tonghuashun:
- Sina:
- Formal industry:
Classification decision:
Confidence impact:
```

## Attribute Card

Every candidate should have an attribute card before ranking:

```text
股票：
Raw industry：
Primary business：
Product keywords：
Primary trade attribute：
Secondary trade attributes：
Weak/rumor attributes：
Evidence level：A / B / C / mixed
Peer group：
Peer confirmation：
Classification confidence：high / medium / low
Fact score：0-3
Trade score：0-3
Tape score：0-3
Negative evidence：
Pool：main attack / trend halfway / board-rush halfway / uncertain opportunity / reject
```

Scoring guide:

- Fact score: 3 = direct主营/产品; 2 = adjacent product; 1 = weak business exposure; 0 = no evidence.
- Trade score: 3 = current market main narrative; 2 = active branch; 1 = weak concept; 0 = not traded.
- Tape score: 3 = multiple peers and leader confirmation; 2 = partial peer confirmation; 1 = isolated strength; 0 = no confirmation.

Pool mapping:

- 8-9 points: main attack pool.
- 6-7 points: trend or board-rush pool, depending on market cap and price behavior.
- 4-5 points: uncertain opportunity pool.
- 0-3 points: reject unless there is an extraordinary catalyst.

## Evidence Levels

- Level A: directly supported by company business, product, announcement, annual report, official website, or investor communication.
- Level B: supported by industry-chain mapping and same-day peer movement.
- Level C: supported only by concept label, rumor, influencer narrative, weak news, or market imagination.
- Mixed: multiple attributes have different evidence levels.

## Confidence Rules

High confidence:

- Primary attribute has Level A evidence.
- At least two peer stocks with the same attribute are strong.
- Price action matches the attribute's active branch.

Medium confidence:

- Primary attribute has Level A or B evidence.
- Peer confirmation exists but is not broad.
- Stock is front-row in price behavior, but branch leadership is not fully clear.

Low confidence:

- Attribute is mostly Level C.
- Peer confirmation is weak or absent.
- Price action is strong but could be event-driven or isolated.

Low confidence does not mean automatic rejection. It means the stock must enter the uncertain opportunity pool with a clear hypothesis, smaller size, and faster invalidation.

## Classification Workflow

1. Start from raw industry, but do not stop there.
2. Extract product keywords from company profile.
3. Map product keywords into trade attributes.
4. Compare with same-day peer groups.
5. Search for negative evidence: business exposure too small, company denial, reduction announcement, high-level risk warning, or purely rumor-driven movement.
6. Assign evidence level, three-layer score, and confidence.
7. Put the stock into the correct pool.
8. Write upgrade and downgrade conditions.

## Dynamic Peer Validation

A classification is stronger when the stock's peer basket confirms it.

For each candidate, choose 3-8 peers from the same suspected trade attribute. Then check:

- Are at least 2 peers also rising or holding above VWAP?
- Is there a clear leader in the peer basket?
- Is the candidate stronger than the median peer by gain, turnover, or new-high behavior?
- Is the sector still improving after the candidate moves?
- Are high-liquidity core stocks confirming, or only small rear-row stocks moving?

If peer validation fails, keep the attribute but lower confidence. Do not erase the opportunity; move it to uncertain opportunity or smaller-size board-rush pool.

## Negative Evidence

Negative evidence does not always cancel a trade, but it must change pool and size.

Examples:

- Company denies a rumor or says exposure is very small.
- The business exists but revenue contribution is below meaningful level.
- Major shareholders announce reduction.
- Price rises on isolated media attention while peers do not follow.
- The stock is only concept-tagged and the company profile does not support the attribute.

When negative evidence exists:

- Main attack pool requires stronger tape confirmation.
- Position ceiling should be reduced.
- Invalidation must be closer.
- Output must explicitly say what evidence would upgrade or reject the hypothesis.

## Trade Attribute Map

| Product or business keywords | Possible trade attributes |
| --- | --- |
| PCB, 印制电路板, 高速板, HDI | PCB, AI服务器PCB, 数据中心硬件 |
| 封装基板, FC-BGA, IC substrate | 先进封装, ABF载板链, 半导体封装材料链 |
| ABF膜, ABF树脂, 电子级树脂 | ABF膜/树脂, 半导体材料, AI服务器材料 |
| 光模块, 光器件, 800G, 1.6T | CPO, 光模块, AI算力网络 |
| 存储, DRAM, NAND, Nor Flash | 存储, 半导体周期, 国产替代 |
| 半导体设备, 刻蚀, 清洗, 薄膜沉积 | 半导体设备, 国产替代 |
| CMP, 光刻胶, 电子特气, 前驱体 | 半导体材料 |
| 减速器, 丝杠, 执行器, 电机 | 人形机器人核心零部件 |
| 数控机床, 磨床, 研磨抛光, 工业母机 | 机器人设备链, 工业母机, 半导体设备边缘映射 |
| 电源, 高压直流, 800V, 服务器电源 | 800V, AI服务器电源, 电气设备 |
| 卫星通信, 相控阵, 天线, 射频 | 商业航天, 卫星互联网, 6G |

## Robot Chain Split

Do not put all robot-related stocks into one bucket.

| Robot branch | Typical attributes |
| --- | --- |
| Human-robot core parts | 减速器, 丝杠, 执行器, 关节模组, 空心杯电机, 灵巧手 |
| Robot control and sensors | 控制器, 伺服, 编码器, 传感器, 视觉 |
| Robot equipment / industrial mother machine | 数控机床, 磨削设备, 研磨抛光, 工业母机, 自动化设备 |
| Robot application / automation | 自动化产线, 仓储物流, 工业机器人集成 |

Example:

```text
股票：宇环数控
Raw industry：其他通用机械 / 数控设备
Primary business：数控磨削设备、研磨抛光设备、智能装备
Product keywords：数控磨床、研磨抛光、智能装备、3C、半导体、液晶显示
Primary trade attribute：工业母机 / 机器人设备链
Secondary trade attributes：智能装备 / 半导体设备边缘映射
Weak/rumor attributes：人形机器人核心
Evidence level：B/C mixed
Peer group：工业母机、智能装备、机器人设备链
Peer confirmation：看华中数控、秦川机床、机器人设备链是否共振
Classification confidence：medium if peers confirm; low if isolated
Pool：uncertain opportunity or board-rush halfway, not human-robot core main pool
```

## PCB / ABF Chain Split

Do not treat all electronics names as the same branch.

| Branch | Attributes |
| --- | --- |
| AI server PCB | 高速PCB, HDI, 数据中心, AI服务器 |
| Package substrate | 封装基板, FC-BGA, IC substrate |
| ABF chain | ABF载板, ABF膜, ABF树脂, 高端封装材料 |
| Passive/electronic components | MLCC, 电容, 电感, 连接器 |

Example:

```text
股票：深南电路
Raw industry：电子元器件
Primary business：印制电路板、封装基板、电子装联
Product keywords：PCB、封装基板、FC-BGA、数据中心
Primary trade attribute：AI服务器PCB
Secondary trade attributes：封装基板 / FC-BGA / ABF载板链
Evidence level：A/B
Peer group：沪电股份、生益科技、鹏鼎控股、兴森科技
Pool：main attack or trend halfway, depending on price behavior
```

## Output Requirement

When the user asks for a candidate pool, include a compact classification column:

```text
标的 / 池子 / 主属性 / 证据等级 / 置信度 / 触发 / 失效
```

When the user challenges a classification, answer by showing the attribute card and peer group instead of defending the previous label.

## Persistent Correction Rule

If the user corrects a stock's classification and the correction is reasonable:

1. Accept the correction.
2. Update the attribute card.
3. State whether the stock moves between pools.
4. Add the corrected mapping to future reviews.

The system should improve classification ability over time instead of only adding uncertain stocks after the fact.

Record corrections in `attribute-corrections.md` when the correction is reusable.

## Daily Coverage Workflow

The correction ledger cannot cover all stocks. For each daily review, run classification as a coverage workflow over the whole strong-stock universe, not only over known names.

Universe construction:

1. Pull Eastmoney concept/industry board lists when available.
2. Pull full-market quotes or the largest available sample.
3. Include all stocks meeting at least one condition:
   - limit-up or near limit-up;
   - change rate in the top active group;
   - turnover in the top active group;
   - turnover rate unusually high;
   - strong reversal or new high in recent OHLC data;
   - belongs to a top-ranked market-flow theme.
4. Add constituents of the top active Eastmoney concept/industry boards.
5. Add user holdings and user-mentioned stocks even if they do not meet strength filters.
6. Add known leaders from active themes.

Batch classification:

1. Use Eastmoney concept/industry memberships as first-pass tags.
2. Use raw industry plus product keywords to assign supplementary attributes.
3. Apply `theme-taxonomy.md` keyword branches.
4. Check `attribute-corrections.md` for reusable corrections.
5. Group stocks by suspected trade attribute.
6. Re-rank each group by price strength, turnover, turnover rate, and front-row behavior.
7. Promote or downgrade classifications based on peer confirmation.

Fine classification:

- Only produce full attribute cards for shortlisted candidates, challenged stocks, user holdings, and high-strength low-confidence names.
- Do not spend equal time on every stock. Coverage comes from batch tags; precision comes from full attribute cards.

## Coverage Report

Every post-market halfway review should include a short classification coverage report:

```text
分类覆盖：
- 强势样本数量：
- 已高置信分类：
- 中置信分类：
- 低置信但盘面强：
- 主要低置信方向：
- 今日最容易误分的分支：
- 需要盘中验证的属性假设：
```

If classification coverage is weak, state it directly and reduce confidence in the candidate pool.

## Unknown Handling

Unknown does not mean ignored. Use these buckets:

| Bucket | Meaning | Action |
| --- | --- | --- |
| Unknown-strong | Price is front-row, attribute unclear | Put into uncertain opportunity pool with hypothesis card |
| Unknown-peer | Attribute unclear, but several similar names move together | Build a temporary peer group and observe as a possible new branch |
| Unknown-isolated | Price strong but no peer and no plausible chain | Small event watch only, no main-pool ranking |
| Unknown-risk | Attribute unclear plus negative evidence | Reject or observe only |

The goal is to avoid both errors: missing emerging branches and polluting the main pool with vague stories.
