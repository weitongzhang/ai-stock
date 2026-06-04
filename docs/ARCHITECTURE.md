# Architecture

## Problem

旧目录把三个技能、外部仓库和样例平铺在同一层：

- 技能定义与可复用代码没有分层。
- `ftshare-market-data` 和 `yc-buy-selector` 都涉及行情/K线，但没有明确数据层与策略层边界。
- 缺少“持续跟踪”层，无法把一次性选股结果沉淀成长期/中期/短期观察池。
- 微信采集样例、选股样例和工程文档混在一起，后续扩展会越来越难扫。

## Target Model

```text
skills/      Codex runtime-facing skill packages
src/         Reusable implementation modules and adapters
sources/     External strategies, upstream repos, methods, and raw materials
examples/    Real inputs/outputs for manual regression
tests/       Automated smoke/regression tests
docs/        Architecture and development docs
tools/       Sync, validation, scaffolding utilities
```

## Layering

### Data Layer

Owned by `ftshare-market-data`.

Responsibilities:

- 股票列表、行情、OHLC、分时、指数、ETF、基金等数据获取。
- 处理外部接口参数、分页、代码后缀、原始 JSON。
- 向上输出标准化行情对象或 `DataFrame`。

Future module:

```text
src/skill_lab/market_data/
  providers.py
  ftshare_provider.py
  symbols.py
```

### Strategy Layer

Owned by `yc-buy-selector`.

Responsibilities:

- 接收标准 OHLCV 数据。
- 运行 13 买点、三重滤网、评分、风险过滤。
- 输出候选列表、原因、状态、CSV/Markdown 报告。

Future module:

```text
src/skill_lab/stock_selection/
  yc_engine.py
  scoring.py
  reports.py
```

### Tracking Layer

Owned by `watchlist-tracker`.

Responsibilities:

- Maintain watchlists for stocks, sectors, themes, ETFs, and indices.
- Separate long-term thesis, mid-term structure, and short-term triggers.
- Record key levels, invalidation conditions, status, next check date, and notes.
- Generate scheduled review reports and eventually alerts.

Future module:

```text
src/skill_lab/tracking/
  watchlist.py
  horizons.py
  rules.py
  reports.py
```

### Content Collection Layer

Owned by `wechat-official-collector` and `cls-telegraph-collector`.

Responsibilities:

- 采集用户提供的公众号文章 URL 或本地 HTML。
- 保存 HTML、图片、图文 Markdown、评论文件。
- 输出每日 digest 和 CSV。
- 采集财联社 7x24 电报列表，标准化为 CSV/JSON/Markdown。
- 支持按关键词、时间窗口筛选快讯，用于市场信息监控和情绪复盘。

Future module:

```text
src/skill_lab/content_collection/
  wechat_article.py
  cls_telegraph.py
  markdown_render.py
  comments.py
```

## Sources

`sources/` is the intake area for external strategy knowledge:

- `sources/upstream-repos`: cloned or downloaded strategy repositories.
- `sources/imported-methods`: structured notes for methods such as Wyckoff, Elder triple screen, Dow theory, or blogger-specific systems.
- `sources/raw-materials`: articles, book notes, exports, and source documents.

Only validated and cleaned ideas should move from `sources/` into `src/skill_lab/`.

## FTShare vs YC-buy

There is overlap, but not duplication if layered correctly.

| Capability | FTShare | YC-buy Selector | Decision |
|---|---|---|---|
| 股票列表 | Yes | Fallback via `data_fetcher.py` | Use FTShare as primary. |
| 实时行情 | Yes | No/limited | Use FTShare. |
| OHLC K线 | Yes | Via akshare/baostock/sample | Use FTShare primary, keep existing fallback. |
| 技术买点 | No | Yes | Keep in strategy layer. |
| 三重滤网 | No | Yes | Keep in strategy layer. |
| CSV 报告 | Raw data only | Candidate report | Keep in strategy/report layer. |

## Migration Rule

- Do not delete runtime skills under `C:\Users\wtzhang12\.codex\skills` automatically.
- Treat this workspace as source-of-truth for development.
- Sync into runtime only after validation.
