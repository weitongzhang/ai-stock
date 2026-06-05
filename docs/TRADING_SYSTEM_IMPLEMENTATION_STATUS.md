# Trading System Implementation Status

This file tracks what has already been built from the development plan and what
the next engineering entry point should be.

| Iteration | Priority | Status | Implemented Artifacts | Next Entry |
|---|---|---|---|---|
| 0 Docs and skeleton | P0 | Done | roadmap, development plan, Harness docs, domain READMEs | Keep docs in sync with shipped modules |
| 1 Shared schema | P0 | Done | `shared/enums.py`, `shared/schemas.py`, `shared/serialization.py` | Add new fields through `raw` first, then promote |
| 2 Data provider | P0 | Started | `DataProvider`, `FileProvider`, `FTShareProvider`, normalizers, symbols, JSON cache, data-quality checks, trading calendar, quality baselines | Add real exchange holiday calendar and provider cache integration |
| 3 Market analysis | P0 | Done for smoke path | breadth, index environment, regime, position bias | Backfill more historical samples |
| 4 Sector analysis | P0 | Started | theme strength ranking and summary, theme registry, leader extraction, theme battle cards | Add rotation state and lifecycle classification |
| 5 Stock analysis | P0 | Started | YC-buy adapter, local YC-buy engine bridge, old `yc-buy-selector` script adapter path | Add more signal scoring and scenario rules |
| 6 Planning/review | P0 | Done for smoke path | tomorrow plan, daily review, markdown renderers, daily organization-analysis CLI | Add scenario/action rule modules |
| 7 Tracking/journal | P1 | Started | watchlist helpers, decision journal JSONL | Add next-day outcome updater |
| 8 Backtesting adapter | P1 | Started | backtest schemas, signal bridge, adapter protocol, metrics, simple engine | Wrap user's existing backtest code |
| 9 Harness | P1 | Started | eval schemas, datasets, judges, runner, reports, CLI | Add domain-specific judge prompts and datasets |
| 10 Daily scripts | P2 | Not started | none | Add pre-market, post-market, backtest scripts |
| 11 Visualization | P3 | Not started | none | Consume JSON/CSV/Markdown only |

## Current Smoke Coverage

| Capability | Smoke Test |
|---|---|
| Shared schema | `tests/smoke/test_shared_schemas.py` |
| File market data provider | `tests/smoke/test_market_data_file_provider.py` |
| Market data quality and cache | `tests/smoke/test_market_data_quality.py` |
| FTShare provider adapter | `tests/smoke/test_ftshare_provider.py` |
| Market analysis | `tests/smoke/test_market_analysis.py` |
| Sector leader extraction | `tests/smoke/test_sector_leaders.py` |
| Tomorrow plan pipeline | `tests/smoke/test_tomorrow_plan_pipeline.py` |
| Daily review pipeline | `tests/smoke/test_daily_review_pipeline.py` |
| Daily organization-analysis CLI | `tests/smoke/test_daily_org_analysis_cli.py` |
| Harness datasets and CLI | `tests/smoke/test_evaluation_dataset_runner.py`, `tests/smoke/test_harness_cli.py` |
| Journal and watchlist | `tests/smoke/test_decision_journal.py`, `tests/smoke/test_watchlist.py` |
| YC-buy adapter | `tests/smoke/test_yc_buy_adapter.py` |
| Backtesting adapter | `tests/smoke/test_backtesting_adapter.py` |

## Near-Term Build Order

| Order | Task | Why |
|---:|---|---|
| 1 | Wrap the user's existing backtest code as `BacktestEngine` | Avoids rewriting a working engine |
| 2 | Add real exchange holiday calendar and provider cache integration | Stabilizes repeated daily runs |
| 3 | Add rotation state and lifecycle classification | Turns sector analysis into a multi-day tracking model |
| 4 | Add pre-market and post-market script variants | Turns modules into repeatable workflows |
| 5 | Add domain-specific Harness judge datasets | Turns methodology into regression samples |
