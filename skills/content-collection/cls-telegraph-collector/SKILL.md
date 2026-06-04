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

Run:

```powershell
python C:\Users\wtzhang12\.codex\skills\cls-telegraph-collector\scripts\collect_cls_telegraph.py --out-dir .\cls-telegraph
```

Collect fewer items:

```powershell
python C:\Users\wtzhang12\.codex\skills\cls-telegraph-collector\scripts\collect_cls_telegraph.py --limit 50 --out-dir .\cls-telegraph
```

Filter by keyword:

```powershell
python C:\Users\wtzhang12\.codex\skills\cls-telegraph-collector\scripts\collect_cls_telegraph.py --keyword AI --keyword 半导体 --out-dir .\cls-telegraph
```

Collect highlighted/red telegraph items:

```powershell
python C:\Users\wtzhang12\.codex\skills\cls-telegraph-collector\scripts\collect_cls_telegraph.py --category red --limit 10 --out-dir .\cls-telegraph-red
```

Collect items after a Unix timestamp:

```powershell
python C:\Users\wtzhang12\.codex\skills\cls-telegraph-collector\scripts\collect_cls_telegraph.py --since-ts 1780502400 --out-dir .\cls-telegraph
```

## Outputs

The script writes:

- `YYYY-MM-DD-cls-telegraph.csv`: structured item table.
- `YYYY-MM-DD-cls-telegraph.json`: normalized items plus raw item payloads.
- `YYYY-MM-DD-cls-telegraph.md`: readable digest with time, title, content, and source link.
- `raw/YYYY-MM-DD/telegraph-response.json`: raw API response for audit/debug.
- `raw/YYYY-MM-DD/images/<item-id>/`: downloaded item images when image URLs are present.

## Workflow

1. Use `scripts/collect_cls_telegraph.py` for the public telegraph list.
2. Inspect the generated Markdown digest and CSV row count.
3. Check `image_count`, `image_urls`, and `local_images` for image-bearing items such as “涨停分析”.
4. If the API returns no data or verification content, retry later with a smaller `--limit`; do not escalate into bypass tactics.
5. For monitoring, filter with `--keyword` and keep daily output folders under `examples/content/cls` or a user-specified archive directory.
6. Summarize only the count, time span, strongest themes, and output paths in chat.

## Interpretation

- `status=ok`: the API returned telegraph items and outputs were written.
- `status=no_items`: the request succeeded but no `roll_data` items were available after filtering.
- `status=fetch_failed`: network/API access failed; preserve the error and retry later if appropriate.
- `--category red` collects the CLS highlighted/red feed. These items currently return `level=B` in the payload.
- `is_red=1`, `level=B`, or similar raw fields may indicate highlighted/important CLS items when present in the payload.
