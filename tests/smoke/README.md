# Smoke Tests

Minimal validation commands for the engineering workspace.

```powershell
python -m py_compile ..\..\skills\stock-selection\yc-buy-selector\scripts\screen_yc_buy.py ..\..\skills\stock-selection\a-share-market-flow-analyst\scripts\analyze_market_flow.py ..\..\skills\stock-selection\a-share-market-flow-analyst\scripts\collect_market_breadth.py ..\..\skills\stock-selection\a-share-market-flow-analyst\scripts\collect_index_environment.py ..\..\skills\stock-selection\a-share-market-flow-analyst\scripts\generate_daily_review.py ..\..\skills\content-collection\wechat-official-collector\scripts\collect_wechat_articles.py ..\..\skills\content-collection\cls-telegraph-collector\scripts\collect_cls_telegraph.py ..\..\skills\content-collection\cls-telegraph-collector\scripts\analyze_cls_market_plan.py ..\..\skills\content-collection\cls-telegraph-collector\scripts\collect_tushare_kpl.py

python ..\..\skills\stock-selection\yc-buy-selector\scripts\screen_yc_buy.py --repo ..\..\sources\upstream-repos\YC-buy\YC-buy-main --codes 000001,600519,000333 --source sample --mode both

python ..\..\skills\tracking\watchlist-tracker\scripts\update_watchlist_report.py --input ..\..\examples\market\tracking\watchlist.csv --out-dir ..\..\examples\market\tracking

python ..\..\skills\content-collection\wechat-official-collector\scripts\collect_wechat_articles.py --input ..\..\examples\content\wechat\wechat_links.txt --out-dir ..\..\examples\content\wechat\wechat-daily

python ..\..\skills\content-collection\cls-telegraph-collector\scripts\collect_cls_telegraph.py --limit 50 --out-dir ..\..\examples\content\cls\cls-telegraph

python ..\..\skills\content-collection\cls-telegraph-collector\scripts\analyze_cls_market_plan.py --input ..\..\examples\content\cls\cls-telegraph\2026-06-04-cls-telegraph.json --input ..\..\examples\content\cls\cls-telegraph-red\2026-06-04-cls-telegraph.json --out-dir ..\..\examples\market\cls-market-plan

python ..\..\skills\stock-selection\a-share-market-flow-analyst\scripts\collect_market_breadth.py --date 2026-06-04 --history-days 5 --out-dir ..\..\examples\market\market-breadth

python ..\..\skills\stock-selection\a-share-market-flow-analyst\scripts\collect_index_environment.py --date 2026-06-04 --source sample --out-dir ..\..\examples\market\index-environment

python ..\..\skills\stock-selection\a-share-market-flow-analyst\scripts\analyze_market_flow.py --date 2026-06-04 --cls-plan ..\..\examples\market\cls-market-plan-kpl\2026-06-04-cls-market-plan.csv --kpl ..\..\examples\market\tushare-kpl\sample-tushare-kpl.csv --lhb ..\..\examples\market\dragon-tiger\20260604-eastmoney-lhb.csv --market ..\..\examples\market\market-breadth\2026-06-04-market-breadth.csv --out-dir ..\..\examples\market\market-flow

python ..\..\skills\stock-selection\a-share-market-flow-analyst\scripts\generate_daily_review.py --date 2026-06-04 --index-env ..\..\examples\market\index-environment\2026-06-04-index-environment.csv --market-breadth ..\..\examples\market\market-breadth\2026-06-04-market-breadth.csv --theme-plan ..\..\examples\market\market-flow\2026-06-04-market-flow.csv --kpl ..\..\examples\market\tushare-kpl\sample-tushare-kpl.csv --out-dir ..\..\examples\market\daily-review
```

Run these from `tests/smoke`.

## Trading System Foundation

Run these from the repository root:

```powershell
python tests\smoke\test_shared_schemas.py
python tests\smoke\test_evaluation_harness.py
python tests\smoke\test_market_data_file_provider.py
python tests\smoke\test_market_data_quality.py
python tests\smoke\test_trading_calendar.py
python tests\smoke\test_ftshare_provider.py
python tests\smoke\test_market_analysis.py
python tests\smoke\test_sector_leaders.py
python tests\smoke\test_tomorrow_plan_pipeline.py
python tests\smoke\test_daily_review_pipeline.py
python tests\smoke\test_daily_org_analysis_cli.py
python tests\smoke\test_evaluation_dataset_runner.py
python tests\smoke\test_harness_cli.py
python tests\smoke\test_decision_journal.py
python tests\smoke\test_watchlist.py
python tests\smoke\test_yc_buy_adapter.py
python tests\smoke\test_backtesting_adapter.py
python tests\smoke\test_perspective_skills.py
```

Minimal Harness CLI:

```powershell
python tools\run_harness_eval.py --dataset examples\evals\datasets\tomorrow_plan\sample.jsonl --target-version smoke
python tools\run_harness_eval.py --dataset examples\evals\datasets\daily_review\sample.jsonl --target-version smoke
```
