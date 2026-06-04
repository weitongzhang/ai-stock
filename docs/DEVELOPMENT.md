# Development Guide

## Skill Anatomy

每个技能至少包含：

- `SKILL.md`: 触发描述和核心工作流。
- `agents/openai.yaml`: UI 展示信息。
- `scripts/`: 可执行、可测试的自动化脚本。
- `references/`: 复杂流程、接口说明、失败处理和设计约定。

## Directory Rules

- `skills/<domain>/<skill-name>`: Codex 技能包工程副本。
- `src/skill_lab/<domain>`: 跨技能复用代码和适配器。
- `sources/upstream-repos/<name>`: 外部源码或上游仓库镜像。
- `sources/imported-methods/<name>`: 导入后的策略方法论笔记。
- `sources/raw-materials`: 原始文章、书籍笔记、导出资料。
- `examples/<domain>/<scenario>`: 样例输入输出。
- `tests/smoke`: 最小可执行验证。
- `tools`: 同步、校验、脚手架等工程工具。

## Validation Checklist

- `SKILL.md` frontmatter 只保留 `name` 和 `description`。
- `description` 写清楚触发场景。
- 脚本支持 Windows 路径和 UTF-8 输出。
- 输出文件路径可读、可复现。
- 失败状态要写入 CSV/Markdown，不要静默吞掉。
- 涉及金融结论时标注“研究用途，非投资建议”。
- 涉及微信内容时不绕过登录、付费、访问控制或反爬限制。

## Sync To Runtime

开发副本验证后，可把单个技能同步到运行目录：

```powershell
$RuntimeRoot = "$env:USERPROFILE\.codex\skills"
Copy-Item -Recurse -Force .\skills\content-collection\wechat-official-collector (Join-Path $RuntimeRoot "wechat-official-collector")
Copy-Item -Recurse -Force .\skills\content-collection\cls-telegraph-collector (Join-Path $RuntimeRoot "cls-telegraph-collector")
Copy-Item -Recurse -Force .\skills\stock-selection\yc-buy-selector (Join-Path $RuntimeRoot "yc-buy-selector")
Copy-Item -Recurse -Force .\skills\stock-selection\a-share-market-flow-analyst (Join-Path $RuntimeRoot "a-share-market-flow-analyst")
Copy-Item -Recurse -Force .\skills\tracking\watchlist-tracker (Join-Path $RuntimeRoot "watchlist-tracker")
Copy-Item -Recurse -Force .\skills\market-data\ftshare-market-data (Join-Path $RuntimeRoot "ftshare-market-data")
```

## Test Commands

```powershell
python skills\content-collection\wechat-official-collector\scripts\collect_wechat_articles.py --input examples\content\wechat\wechat_links.txt --out-dir examples\content\wechat\wechat-daily

python skills\content-collection\cls-telegraph-collector\scripts\collect_cls_telegraph.py --limit 50 --out-dir examples\content\cls\cls-telegraph

python skills\content-collection\cls-telegraph-collector\scripts\collect_tushare_kpl.py --trade-date 20260604 --tag 涨停 --tag 炸板 --out-dir examples\market\tushare-kpl

python skills\content-collection\cls-telegraph-collector\scripts\analyze_cls_market_plan.py --input examples\content\cls\cls-telegraph\2026-06-04-cls-telegraph.json --input examples\content\cls\cls-telegraph-red\2026-06-04-cls-telegraph.json --out-dir examples\market\cls-market-plan

python skills\stock-selection\a-share-market-flow-analyst\scripts\collect_market_breadth.py --date 2026-06-04 --out-dir examples\market\market-breadth

python skills\stock-selection\a-share-market-flow-analyst\scripts\analyze_market_flow.py --date 2026-06-04 --cls-plan examples\market\cls-market-plan-kpl\2026-06-04-cls-market-plan.csv --kpl examples\market\tushare-kpl\sample-tushare-kpl.csv --lhb examples\market\dragon-tiger\20260604-eastmoney-lhb.csv --market examples\market\market-breadth\2026-06-04-market-breadth.csv --out-dir examples\market\market-flow

python skills\stock-selection\yc-buy-selector\scripts\screen_yc_buy.py --repo sources\upstream-repos\YC-buy\YC-buy-main --codes 000001,600519,000333 --source sample --mode both

python skills\tracking\watchlist-tracker\scripts\update_watchlist_report.py --input examples\market\tracking\watchlist.csv --out-dir examples\market\tracking

python skills\market-data\ftshare-market-data\run.py stock-quotes-list --order_by "turnover desc" --page_no 1 --page_size 10
```

## Backlog

- 给 `yc-buy-selector` 增加 FTShare provider，减少对 akshare 的依赖。
- 在 `src/skill_lab/market_data` 定义统一 OHLCV provider 接口。
- 在 `src/skill_lab/stock_selection` 抽出策略评分与报告生成。
- 在 `src/skill_lab/tracking` 抽出观察池 schema、周期分类、规则触发和定时报告。
- 给微信公众号采集技能增加浏览器导出 HTML 的辅助流程。
- 给财联社电报采集增加去重增量归档和主题聚类。
- 给财联社市场计划接入真实板块涨幅、涨停梯队和 FTShare 行情验证。
- 给三个技能补统一 smoke test。
- 增加技能版本号和变更记录字段。
