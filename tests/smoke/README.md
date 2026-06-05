# Smoke Tests

Minimal validation commands for the engineering workspace.

```powershell
python -m py_compile ..\..\skills\stock-selection\yc-buy-selector\scripts\screen_yc_buy.py ..\..\skills\stock-selection\a-share-market-flow-analyst\scripts\analyze_market_flow.py ..\..\skills\stock-selection\a-share-market-flow-analyst\scripts\collect_market_breadth.py ..\..\skills\content-collection\wechat-official-collector\scripts\collect_wechat_articles.py ..\..\skills\content-collection\cls-telegraph-collector\scripts\collect_cls_telegraph.py ..\..\skills\content-collection\cls-telegraph-collector\scripts\analyze_cls_market_plan.py ..\..\skills\content-collection\cls-telegraph-collector\scripts\collect_tushare_kpl.py

python ..\..\skills\stock-selection\yc-buy-selector\scripts\screen_yc_buy.py --repo ..\..\sources\upstream-repos\YC-buy\YC-buy-main --codes 000001,600519,000333 --source sample --mode both

python ..\..\skills\tracking\watchlist-tracker\scripts\update_watchlist_report.py --input ..\..\examples\market\tracking\watchlist.csv --out-dir ..\..\examples\market\tracking

python ..\..\skills\content-collection\wechat-official-collector\scripts\collect_wechat_articles.py --input ..\..\examples\content\wechat\wechat_links.txt --out-dir ..\..\examples\content\wechat\wechat-daily

python ..\..\skills\content-collection\cls-telegraph-collector\scripts\collect_cls_telegraph.py --limit 50 --out-dir ..\..\examples\content\cls\cls-telegraph

python ..\..\skills\content-collection\cls-telegraph-collector\scripts\analyze_cls_market_plan.py --input ..\..\examples\content\cls\cls-telegraph\2026-06-04-cls-telegraph.json --input ..\..\examples\content\cls\cls-telegraph-red\2026-06-04-cls-telegraph.json --out-dir ..\..\examples\market\cls-market-plan

python ..\..\skills\stock-selection\a-share-market-flow-analyst\scripts\collect_market_breadth.py --date 2026-06-04 --history-days 5 --out-dir ..\..\examples\market\market-breadth

python ..\..\skills\stock-selection\a-share-market-flow-analyst\scripts\analyze_market_flow.py --date 2026-06-04 --cls-plan ..\..\examples\market\cls-market-plan-kpl\2026-06-04-cls-market-plan.csv --kpl ..\..\examples\market\tushare-kpl\sample-tushare-kpl.csv --lhb ..\..\examples\market\dragon-tiger\20260604-eastmoney-lhb.csv --market ..\..\examples\market\market-breadth\2026-06-04-market-breadth.csv --out-dir ..\..\examples\market\market-flow
```

Run these from `tests/smoke`.
