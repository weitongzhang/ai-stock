---
name: cls-telegraph-collector
description: 财联社电报信息采集、归档与摘要工作流。Use when Codex needs to collect CLS / 财联社 7x24 telegraph items from https://www.cls.cn/telegraph or the CLS telegraph API, save rolling financial news as CSV/JSON/Markdown, filter by keyword or time, and produce a local digest for market monitoring or sentiment review.
---

# CLS Telegraph Collector

Use this skill for requests like:

- “采集财联社电报”
- “抓取 https://www.cls.cn/telegraph”
- “保存财联社 7x24 快讯”
- “按关键词筛选财联社电报”
- “生成今日财联社快讯摘要”

## Boundaries

- Use public pages or public JSON endpoints only; do not bypass login, paywalls, request limits, verification pages, or anti-scraping controls.
- Keep request volume conservative. Prefer one-shot collection with `--limit 100` or lower unless the user explicitly asks for a wider archive.
- Do not reproduce large copyrighted news feeds in chat. Archive locally when requested; summarize key items in the final answer.
- Treat outputs as market information for research, not investment advice.

## Quick Start

Run from the `cls-telegraph-collector` skill directory, or replace `scripts\...` with the script path in the current installation:

```powershell
python scripts\collect_cls_telegraph.py --out-dir .\cls-telegraph
```

Collect fewer items:

```powershell
python scripts\collect_cls_telegraph.py --limit 50 --out-dir .\cls-telegraph
```

Filter by keyword:

```powershell
python scripts\collect_cls_telegraph.py --keyword AI --keyword 半导体 --out-dir .\cls-telegraph
```

Collect highlighted/red telegraph items:

```powershell
python scripts\collect_cls_telegraph.py --category red --limit 10 --out-dir .\cls-telegraph-red
```

Turn ordinary and red telegraph outputs into a next-day A-share theme plan:

```powershell
python scripts\analyze_cls_market_plan.py --input .\cls-telegraph\YYYY-MM-DD-cls-telegraph.json --input .\cls-telegraph-red\YYYY-MM-DD-cls-telegraph.json --out-dir .\cls-market-plan
```

Collect Tushare `kpl_list` data sourced from 开盘啦榜单:

```powershell
$env:TUSHARE_TOKEN="your-token"
python scripts\collect_tushare_kpl.py --trade-date YYYYMMDD --tag 涨停 --tag 炸板 --out-dir .\tushare-kpl
```

Add 开盘啦榜单 validation to the market plan:

```powershell
python scripts\analyze_cls_market_plan.py --input .\cls-telegraph\YYYY-MM-DD-cls-telegraph.json --input .\cls-telegraph-red\YYYY-MM-DD-cls-telegraph.json --kpl .\tushare-kpl\YYYYMMDD-tushare-kpl.csv --out-dir .\cls-market-plan
```

Collect items after a Unix timestamp:

```powershell
python scripts\collect_cls_telegraph.py --since-ts 1780502400 --out-dir .\cls-telegraph
```

## Outputs

The script writes:

- `YYYY-MM-DD-cls-telegraph.csv`: structured item table.
- `YYYY-MM-DD-cls-telegraph.json`: normalized items plus raw item payloads.
- `YYYY-MM-DD-cls-telegraph.md`: readable digest with time, title, content, and source link.
- `raw/YYYY-MM-DD/telegraph-response.json`: raw API response for audit/debug.
- `raw/YYYY-MM-DD/images/<item-id>/`: downloaded item images when image URLs are present.

The market-plan script writes:

- `YYYY-MM-DD-cls-market-plan.csv`: theme score, sectors, candidate stocks, confirmation signals, give-up signals, and position plan.
- `YYYY-MM-DD-cls-market-plan.md`: next-day plan using CLS news, LIFT-style theme/candidate mapping, and BSA-style action rules.

The Tushare KPL script writes:

- `YYYYMMDD-tushare-kpl.csv`: 开盘啦榜单 rows from Tushare `kpl_list`.
- `YYYYMMDD-tushare-kpl.json`: normalized rows and raw API responses.
- `YYYYMMDD-tushare-kpl.md`: readable list of names, themes, status, and涨停原因.

## Workflow

1. Use `scripts/collect_cls_telegraph.py` for the public telegraph list.
2. Inspect the generated Markdown digest and CSV row count.
3. Check `image_count`, `image_urls`, and `local_images` for image-bearing items such as “涨停分析”.
4. If the API returns no data or verification content, retry later with a smaller `--limit`; do not escalate into bypass tactics.
5. For monitoring, filter with `--keyword` and keep daily output folders under `examples/content/cls` or a user-specified archive directory.
6. If a Tushare token is available, run `scripts/collect_tushare_kpl.py` for tags such as `涨停`, `炸板`, `跌停`, `竞价`.
7. Run `scripts/analyze_cls_market_plan.py` on ordinary/red CLS JSON outputs, plus `--kpl` CSV/JSON when available, to create the next-day theme plan.
8. Summarize only the count, time span, strongest themes, and output paths in chat.

## Interpretation

- `status=ok`: the API returned telegraph items and outputs were written.
- `status=no_items`: the request succeeded but no `roll_data` items were available after filtering.
- `status=fetch_failed`: network/API access failed; preserve the error and retry later if appropriate.
- `--category red` collects the CLS highlighted/red feed. These items currently return `level=B` in the payload.
- `is_red=1`, `level=B`, or similar raw fields may indicate highlighted/important CLS items when present in the payload.
- `collect_tushare_kpl.py` requires a valid Tushare token with `kpl_list` permission; pass `--token` or set `TUSHARE_TOKEN`.
- The market-plan output is a candidate-pool generator. Confirm with next-day index, sector, volume, front-row, and core-stock feedback before acting.
