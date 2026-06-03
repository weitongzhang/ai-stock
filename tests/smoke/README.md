# Smoke Tests

Minimal validation commands for the engineering workspace.

```powershell
python -m py_compile ..\..\skills\stock-selection\yc-buy-selector\scripts\screen_yc_buy.py ..\..\skills\content-collection\wechat-official-collector\scripts\collect_wechat_articles.py

python ..\..\skills\stock-selection\yc-buy-selector\scripts\screen_yc_buy.py --repo ..\..\sources\upstream-repos\YC-buy\YC-buy-main --codes 000001,600519,000333 --source sample --mode both

python ..\..\skills\tracking\watchlist-tracker\scripts\update_watchlist_report.py --input ..\..\examples\market\tracking\watchlist.csv --out-dir ..\..\examples\market\tracking

python ..\..\skills\content-collection\wechat-official-collector\scripts\collect_wechat_articles.py --input ..\..\examples\content\wechat\wechat_links.txt --out-dir ..\..\examples\content\wechat\wechat-daily
```

Run these from `tests/smoke`.
