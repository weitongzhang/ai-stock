# Skills Engineering Workspace

这个工程用于持续开发、调优和工程化管理 Codex 技能。当前聚焦四类能力：金融市场数据、A 股技术选股、长中短周期跟踪、内容信息采集。

## Code Map

```text
skills-engineering-workspace/
  README.md
  SKILLS_MANIFEST.json

  docs/
    ARCHITECTURE.md       # 架构分层与能力整合说明
    DEVELOPMENT.md        # 开发、验证、同步运行副本的流程

  skills/                 # Codex 可触发的技能包工程副本
    market-data/
      ftshare-market-data/
    stock-selection/
      yc-buy-selector/
    tracking/
      watchlist-tracker/
    content-collection/
      wechat-official-collector/
      cls-telegraph-collector/

  src/skill_lab/          # 未来沉淀的可复用实现层
    market_data/
    stock_selection/
    tracking/
    content_collection/
    shared/

  sources/                # 策略来源与外部资料库
    upstream-repos/
      YC-buy/YC-buy-main/
    imported-methods/
    raw-materials/

  examples/               # 真实样例输入输出
    market/stock-selection/
    market/tracking/
    content/wechat/
    content/cls/

  tests/smoke/            # 最小可执行验证
  tools/                  # 同步、校验、脚手架等工程工具
```

## Capabilities

`ftshare-market-data` 是市场数据底座，负责获取 A 股行情、K 线、指数、ETF、基金、宏观等结构化数据。

`yc-buy-selector` 是策略选股层，基于 YC-buy 的 13 买点和三重滤网，把 OHLCV 数据转成买点、趋势信号、评分和候选报告。

`watchlist-tracker` 是观察池跟踪层，用于长期/中期/短期跟踪想持续关注的标的、板块、主题、ETF 和指数，记录逻辑、关键位、触发条件、失效条件和下次检查时间。

`wechat-official-collector` 是内容采集层，负责采集用户提供的微信公众号文章链接或 HTML，保存正文、图片、评论状态、图文 Markdown 和每日摘要。

`cls-telegraph-collector` 是财联社电报采集层，负责抓取 `https://www.cls.cn/telegraph` 对应的 7x24 快讯列表，保存 CSV、JSON、Markdown 摘要，并支持关键词和时间过滤。

## Design Philosophy

工程按“技能包 + 可复用实现 + 外部仓库 + 样例测试”分层，而不是把所有能力平铺在一个目录里。

- `skills/` 保持 Codex Skill 标准结构，面向触发和使用。
- `src/skill_lab/` 承接后续复杂逻辑，避免脚本越写越散。
- `sources/` 保存外部策略、方法论和原始资料；成熟后再内化到 `src/skill_lab/`。
- `examples/` 保存真实输入输出，逐步变成回归测试资产。
- `docs/` 记录设计决策，减少后续调整时的上下文丢失。

`ftshare-market-data` 和 `yc-buy-selector` 不合并。前者是数据层，后者是策略层。正确的整合方式是让选股策略消费 FTShare 标准化后的 OHLCV 数据，而不是让策略脚本自己维护多套取数逻辑。

后续新增的选股策略、交易策略、博主方法论、书籍笔记或上游仓库，先进入 `sources/`。经过理解、清洗、验证后，再沉淀进 `src/skill_lab/stock_selection`、`src/skill_lab/trading` 或新的领域模块。

```text
FTShare provider
  -> normalized OHLCV
  -> YC-buy strategy engine
  -> scoring / risk filters
  -> reports
```

## Expansion Plan

1. 在 `src/skill_lab/market_data` 实现统一数据 provider，优先接 FTShare，保留 sample/akshare fallback。
2. 在 `src/skill_lab/stock_selection` 抽象 YC-buy 策略 engine、评分模型、风险过滤和报告生成。
3. 在 `src/skill_lab/tracking` 抽象观察池 schema、周期分类、规则触发、定时报告和 market-data enrichment。
4. 在 `src/skill_lab/content_collection` 抽出公众号正文清洗、图片下载、评论抓取、财联社电报标准化和 Markdown 渲染模块。
5. 在 `tests/smoke` 增加四个领域的最小自动化测试。
6. 在 `tools/` 完善同步运行副本、技能校验和脚手架命令。
7. 后续新增技能时，先归入领域目录；若出现跨技能复用，再下沉到 `src/skill_lab/`。

## Safety Notes

- 股票筛选结果仅供技术研究，不构成投资建议。
- 微信公众号采集不绕过登录、付费、访问控制或反爬限制。
- 评论抓取只使用用户提供的合法登录态；没有 session 时保留失败状态。
- 财联社电报采集只使用公开页面/公开 JSON，不绕过验证码、登录、付费或访问频率限制。
