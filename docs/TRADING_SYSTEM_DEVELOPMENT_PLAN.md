# Trading System Development Plan

> 本文是开发执行计划，配合 `docs/TRADING_SYSTEM_ROADMAP.md` 使用。
>
> Roadmap 说明“系统要长成什么样”，本计划说明“每一步具体开发什么、先后顺序是什么、如何验收”。

## 1. 开发总原则

- 先建领域模型，再迁移脚本逻辑。
- 先保证旧脚本可用，再逐步下沉实现。
- 先做日常闭环，再做高级功能。
- 先接入回测 adapter，再考虑重构回测代码。
- 每个阶段都要有可运行产物，不做长期悬空重构。

## 2. 推荐迭代顺序

```text
Iteration 0: 文档与目录骨架
Iteration 1: 统一 schema 与枚举
Iteration 2: 数据 provider 与 normalizer
Iteration 3: 大盘分析服务
Iteration 4: 板块主题分析服务
Iteration 5: 个股分析与 YC-buy adapter
Iteration 6: 明日计划与每日复盘服务化
Iteration 7: 观察池与决策日志闭环
Iteration 8: 回测系统 adapter
Iteration 9: Trading Research Harness
Iteration 10: 日常脚本与自动化入口
Iteration 11: 可视化与高级扩展
```

优先级：

- P0：Iteration 0-6
- P1：Iteration 7-8
- P2：Iteration 9-10
- P3：Iteration 11

## 3. Iteration 0：文档与目录骨架

目标：把项目未来结构先占位，减少后续模块摇摆。

新增目录：

```text
src/skill_lab/shared/
src/skill_lab/market_analysis/
src/skill_lab/sector_analysis/
src/skill_lab/stock_analysis/
src/skill_lab/planning/
src/skill_lab/backtesting/
```

新增文档：

```text
docs/TRADING_DOMAIN_MODEL.md
docs/TRADING_DEVELOPMENT_CHECKLIST.md
```

开发任务：

- 建立各目录 `README.md`，说明职责边界。
- 写 `TRADING_DOMAIN_MODEL.md`，定义核心对象关系。
- 写 `TRADING_DEVELOPMENT_CHECKLIST.md`，作为后续任务打勾清单。

验收标准：

- 每个目录职责清楚。
- 能说明 `skills/`、`src/skill_lab/`、`sources/`、`examples/` 的分工。
- 没有业务逻辑迁移，只做结构准备。

## 4. Iteration 1：统一 Schema 与枚举

目标：让后续大盘、板块、个股、回测共用同一套对象。

建议文件：

```text
src/skill_lab/shared/enums.py
src/skill_lab/shared/schemas.py
src/skill_lab/shared/serialization.py
tests/smoke/test_shared_schemas.py
```

核心枚举：

- `InstrumentType`
- `Market`
- `BarSpan`
- `DataSource`
- `MarketRegime`
- `ActionLevel`
- `WatchStatus`
- `SignalDirection`

核心数据类：

- `Instrument`
- `Bar`
- `QuoteSnapshot`
- `MarketBreadth`
- `IndexEnvironment`
- `ThemeScore`
- `StockSignal`
- `TomorrowPlan`
- `DailyReview`
- `BacktestConfig`
- `PerformanceReport`

开发任务：

- 使用 `dataclass` 或轻量 Pydantic 风格对象。若项目暂未引入 Pydantic，先用标准库 `dataclasses`。
- 每个对象提供 `to_dict()` / `from_dict()` 或统一 serialization helper。
- 保留 `raw: dict` 字段，兼容外部数据源新增字段。

验收标准：

- `python -m py_compile src/skill_lab/shared/*.py` 通过。
- schema 可以表达现有 `market-flow.csv`、`daily-review.md` 的核心字段。
- 测试覆盖对象创建、序列化、反序列化。

## 5. Iteration 2：数据 Provider 与 Normalizer

目标：上层分析不再关心数据来自 FTShare、AkShare、Tushare 还是样例文件。

建议文件：

```text
src/skill_lab/market_data/providers.py
src/skill_lab/market_data/ftshare_provider.py
src/skill_lab/market_data/file_provider.py
src/skill_lab/market_data/normalizers.py
src/skill_lab/market_data/symbols.py
src/skill_lab/market_data/cache.py
tests/smoke/test_market_data_normalizers.py
```

开发任务：

- 定义 `DataProvider` 协议：
  - `get_bars(symbol, span, limit, until)`
  - `get_quote(symbol)`
  - `get_market_breadth(date)`
  - `get_index_environment(date)`
- 实现 `FileProvider`，优先读取 `examples/market`，方便离线测试。
- 实现 `FTShareProvider`，封装现有 `ftshare-market-data/run.py` 或子 skill handler。
- 实现代码格式转换：
  - `600519.SH`
  - `600519.XSHG`
  - `000001.SZ`
  - `000001.XSHE`

验收标准：

- 可以从样例文件生成 `MarketBreadth`。
- 可以从样例文件生成 `IndexEnvironment`。
- 可以读取 OHLCV 并转成标准 `Bar`。
- 不改现有 skill 的用户使用方式。

## 6. Iteration 3：大盘分析服务

目标：把市场宽度、指数环境、市场状态从脚本中拆成服务。

建议文件：

```text
src/skill_lab/market_analysis/breadth.py
src/skill_lab/market_analysis/index_environment.py
src/skill_lab/market_analysis/regime.py
src/skill_lab/market_analysis/position.py
tests/smoke/test_market_analysis.py
```

开发任务：

- 从 `collect_market_breadth.py` 和 `generate_daily_review.py` 抽取评分逻辑。
- 实现：
  - `classify_breadth(metrics) -> BreadthScore`
  - `classify_index_environment(index_rows) -> IndexEnvironment`
  - `classify_market_regime(breadth, index_env) -> MarketRegimeResult`
  - `suggest_position_bias(regime) -> PositionBias`

验收标准：

- 使用 `examples/market/market-breadth` 可输出市场状态。
- 使用 `examples/market/index-environment` 可输出指数环境。
- 旧脚本能逐步改为调用服务，但输出不明显变化。

## 7. Iteration 4：板块主题分析服务

目标：把 F-M-C-T 主题评分独立出来。

建议文件：

```text
src/skill_lab/sector_analysis/theme.py
src/skill_lab/sector_analysis/theme_registry.yml
src/skill_lab/sector_analysis/strength.py
src/skill_lab/sector_analysis/leaders.py
src/skill_lab/sector_analysis/rotation.py
tests/smoke/test_sector_analysis.py
```

开发任务：

- 把 `analyze_market_flow.py` 中的主题关键词和评分拆出。
- 主题关键词从硬编码迁移到 `theme_registry.yml`。
- 实现：
  - `detect_theme(row) -> Theme`
  - `score_theme(inputs) -> ThemeScore`
  - `classify_rotation_state(theme_score, limit_up_events) -> RotationState`
  - `extract_leader_candidates(theme, kpl, lhb) -> list[LeaderCandidate]`

验收标准：

- 使用现有 `examples/market/market-flow` 相关输入，可以生成同类 CSV。
- F/M/C/T 分项可测试。
- 新增主题无需改 Python 代码，只改配置。

## 8. Iteration 5：个股分析与 YC-buy Adapter

目标：把 YC-buy 作为策略引擎接入统一数据体系。

建议文件：

```text
src/skill_lab/stock_analysis/yc_buy_adapter.py
src/skill_lab/stock_analysis/technical.py
src/skill_lab/stock_analysis/triple_screen.py
src/skill_lab/stock_analysis/scoring.py
src/skill_lab/stock_analysis/scenarios.py
tests/smoke/test_yc_buy_adapter.py
```

开发任务：

- 包装 `sources/upstream-repos/YC-buy/YC-buy-main`。
- 将统一 `Bar` 转成 YC-buy 需要的 DataFrame。
- 将 YC-buy 输出转成标准 `StockSignal`。
- 保留原 `skills/stock-selection/yc-buy-selector/scripts/screen_yc_buy.py`，逐步让它调用 adapter。

验收标准：

- 使用 sample 数据能跑通。
- 使用统一 OHLCV 能跑通至少一个股票。
- 输出包含：
  - 触发买点
  - 三重滤网方向
  - 信号强度
  - 风险说明
  - 等待/观察/放弃状态

## 9. Iteration 6：明日计划与每日复盘服务化

目标：把当前最有价值的日常工作流稳定下来。

建议文件：

```text
src/skill_lab/planning/daily_review.py
src/skill_lab/planning/tomorrow_plan.py
src/skill_lab/planning/scenarios.py
src/skill_lab/planning/action_rules.py
src/skill_lab/planning/renderers.py
tests/smoke/test_planning.py
```

开发任务：

- 把 `generate_daily_review.py` 中的核心判断拆成：
  - `DailyReviewService`
  - `TomorrowPlanService`
  - `ScenarioBuilder`
  - `MarkdownRenderer`
- 输出结构化对象，再渲染 Markdown。
- 每个计划项必须有：
  - 方向
  - 优先级
  - 观察标的
  - 触发条件
  - 放弃条件
  - 仓位约束
  - 数据限制

验收标准：

- 现有 daily-review 样例可以由新服务生成相近结构。
- Markdown 渲染和核心判断解耦。
- 可以输出 JSON，供后续观察池和回测消费。

## 10. Iteration 7：观察池与决策日志闭环

目标：让计划可以被跟踪、验证和复盘。

建议文件：

```text
src/skill_lab/tracking/watchlist.py
src/skill_lab/tracking/horizons.py
src/skill_lab/tracking/rules.py
src/skill_lab/tracking/journal.py
src/skill_lab/tracking/reports.py
tests/smoke/test_tracking.py
```

开发任务：

- 升级 watchlist schema：
  - `item_type`
  - `symbol`
  - `name`
  - `theme`
  - `horizon`
  - `status`
  - `trigger`
  - `invalidation`
  - `next_check_date`
  - `source_plan_id`
- 实现 `DecisionJournal`：
  - 计划生成
  - 是否触发
  - 是否执行
  - 结果
  - 错误归因

验收标准：

- 明日计划可以自动写入观察池候选。
- 次日可以更新触发/失效/继续观察。
- 能生成观察池报告。

## 11. Iteration 8：回测系统 Adapter

目标：把你的已有回测代码纳入当前系统，不先重写。

建议文件：

```text
src/skill_lab/backtesting/config.py
src/skill_lab/backtesting/signal_bridge.py
src/skill_lab/backtesting/engine_adapter.py
src/skill_lab/backtesting/result_schema.py
src/skill_lab/backtesting/metrics.py
src/skill_lab/backtesting/attribution.py
tests/smoke/test_backtesting_adapter.py
```

外部代码位置：

```text
sources/upstream-repos/<your-backtest-code>/
```

开发任务：

- 定义 `BacktestEngineAdapter` 协议：
  - `prepare_data()`
  - `run(config)`
  - `parse_result()`
- 定义 `SignalBridge`：
  - `StockSignal -> SignalEvent`
  - `ThemeScore -> FilterEvent`
  - `MarketRegime -> RiskFilterEvent`
- 实现标准结果：
  - `Trade`
  - `EquityCurve`
  - `PerformanceReport`
  - `AttributionReport`

第一批回测场景：

- YC-buy 单独信号。
- YC-buy + 大盘状态过滤。
- YC-buy + 板块强度过滤。
- YC-buy + 大盘状态 + 板块强度。

验收标准：

- 能跑出基础收益、回撤、胜率、交易次数。
- 能按买点、板块、市场状态做归因。
- 回测结果可以进入复盘报告。

## 12. Iteration 9：Trading Research Harness

目标：为交易系统建立持续评测、验证和规则迭代框架。

建议文件：

```text
docs/TRADING_RESEARCH_HARNESS.md
docs/evals/tomorrow_plan_eval.md
docs/evals/daily_review_eval.md
docs/evals/theme_strength_eval.md
docs/evals/lift_leader_eval.md
docs/evals/bsa_signal_eval.md
src/skill_lab/evaluation/schemas.py
src/skill_lab/evaluation/datasets.py
src/skill_lab/evaluation/judges.py
src/skill_lab/evaluation/metrics.py
src/skill_lab/evaluation/reports.py
src/skill_lab/evaluation/runner.py
examples/evals/datasets/
examples/evals/results/
examples/evals/reports/
```

开发任务：

- 建立 Harness schema。
- 定义通用错误分类体系。
- 先建设 `TomorrowPlan Harness` 和 `DailyReview Harness`。
- 为明日计划建立事后验证样本。
- 为每日复盘建立人工标注样本。
- 设计专业 Judge Agent prompt：
  - `TomorrowPlanJudge`
  - `DailyReviewJudge`
  - `ThemeStrengthJudge`
  - `LiftLeaderJudge`
  - `BsaSignalJudge`
- 将 Harness 结果写入 `DecisionJournal`。

验收标准：

- 可以对一份明日计划输出结构化评测 JSON。
- 可以对一份每日复盘输出质量评分和错误分类。
- 能区分格式错误、证据不足、计划不可执行、放弃条件不清楚、过度确定等问题。
- Harness 报告可以反哺规则修改。

专业 Agent 建设原则：

- 数据、字段、数值、回测指标用代码服务，不建 Agent。
- 大盘、板块、LIFT、BSA、复盘、计划这类需要方法论判断的域，建立专业 Judge Agent。
- Agent 负责判断和归因，服务负责计算，回测负责验证。

## 13. Iteration 10：日常脚本与自动化入口

目标：把系统变成日常可用工具。

建议文件：

```text
tools/run_pre_market.ps1
tools/run_daily_review.ps1
tools/run_weekly_review.ps1
tools/run_backtest_yc_buy.ps1
```

开发任务：

- 盘前脚本：
  - 读取昨日计划。
  - 更新观察池。
  - 输出今日关注清单。
- 盘后脚本：
  - 更新数据。
  - 生成每日复盘。
  - 生成明日计划。
  - 更新观察池和 journal。
- 周末脚本：
  - 汇总本周计划。
  - 跑回测。
  - 输出周复盘。

验收标准：

- 一条命令生成盘后复盘。
- 一条命令生成明日计划。
- 一条命令跑基础回测。

## 14. Iteration 11：可视化与高级扩展

目标：提升使用体验，不影响核心系统稳定性。

可选方向：

- 报告索引页。
- 本地 dashboard。
- 观察池看板。
- 回测结果图表。
- 自动提醒。
- 盘中监控。

建议入口：

```text
apps/dashboard/
src/skill_lab/visualization/
```

验收标准：

- 可视化只消费 JSON/CSV/Markdown 产物。
- 不把核心判断逻辑写进前端。
- 前端坏了不影响脚本和回测。

## 15. 每次开发的标准流程

每个任务建议按下面顺序做：

```text
1. 明确输入输出对象
2. 写 schema 或接口
3. 写最小实现
4. 用 examples 跑通
5. 加 smoke test
6. 保持旧脚本兼容
7. 更新文档
```

每次提交前检查：

- 是否改动了不相关文件。
- 是否破坏了旧 skill 的调用方式。
- 是否可以用样例文件离线验证。
- 是否保留了金融研究免责声明。

## 16. 首批推荐开发任务

如果从明天开始动手，建议按这个小步序列：

1. 新建 `src/skill_lab/shared/enums.py`。
2. 新建 `src/skill_lab/shared/schemas.py`。
3. 给 `MarketBreadth`、`IndexEnvironment`、`ThemeScore`、`StockSignal` 建 dataclass。
4. 新建 `src/skill_lab/market_data/file_provider.py`，先读取 `examples/market`。
5. 新建 `src/skill_lab/market_analysis/breadth.py`，迁移市场宽度分类。
6. 新建 `src/skill_lab/sector_analysis/strength.py`，迁移 F-M-C-T 评分。
7. 新建 `src/skill_lab/planning/tomorrow_plan.py`，生成结构化明日计划。
8. 让现有 `generate_daily_review.py` 调用新服务。
9. 再接 YC-buy adapter。
10. 最后接回测 adapter。

这个顺序能最快形成一条主线：

```text
样例数据 -> 大盘/板块分析 -> 明日计划 -> 每日复盘
```

随后再接：

```text
统一 OHLCV -> YC-buy 信号 -> 回测验证
```
