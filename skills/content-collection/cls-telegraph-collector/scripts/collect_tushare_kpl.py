#!/usr/bin/env python3
"""Collect Tushare kpl_list data, sourced from 开盘啦榜单."""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Any


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


TUSHARE_API = "http://api.tushare.pro"
FIELDS = [
    "ts_code",
    "name",
    "trade_date",
    "tag",
    "theme",
    "status",
    "lu_desc",
    "lu_time",
    "open_time",
    "last_time",
    "net_change",
    "bid_amount",
    "bid_change",
    "bid_turnover",
    "lu_bid_vol",
    "pct_chg",
    "bid_pct_chg",
    "rt_pct_chg",
    "limit_order",
    "amount",
    "turnover_rate",
    "free_float",
    "lu_limit_order",
]


def post_tushare(token: str, params: dict[str, Any], fields: list[str]) -> dict[str, Any]:
    payload = json.dumps(
        {
            "api_name": "kpl_list",
            "token": token,
            "params": params,
            "fields": ",".join(fields),
        },
        ensure_ascii=False,
    ).encode("utf-8")
    req = urllib.request.Request(
        TUSHARE_API,
        data=payload,
        headers={"Content-Type": "application/json", "User-Agent": "skills-engineering-workspace"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8", errors="replace"))


def rows_from_response(data: dict[str, Any]) -> list[dict[str, Any]]:
    if data.get("code") not in (0, "0"):
        raise RuntimeError(f"tushare error {data.get('code')}: {data.get('msg')}")
    body = data.get("data") or {}
    fields = body.get("fields") or []
    items = body.get("items") or []
    return [dict(zip(fields, item)) for item in items]


def collect(token: str, trade_date: str, tags: list[str], fields: list[str]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    rows: list[dict[str, Any]] = []
    raw: list[dict[str, Any]] = []
    for tag in tags:
        params = {"trade_date": trade_date, "tag": tag}
        data = post_tushare(token, params, fields)
        raw.append({"params": params, "response": data})
        for row in rows_from_response(data):
            row["query_tag"] = tag
            rows.append(row)
    return rows, raw


def write_outputs(rows: list[dict[str, Any]], raw: list[dict[str, Any]], out_dir: Path, trade_date: str) -> tuple[Path, Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    csv_path = out_dir / f"{trade_date}-tushare-kpl.csv"
    json_path = out_dir / f"{trade_date}-tushare-kpl.json"
    md_path = out_dir / f"{trade_date}-tushare-kpl.md"

    fields = list(FIELDS) + ["query_tag"]
    with csv_path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})

    json_path.write_text(
        json.dumps({"source": "tushare.kpl_list", "trade_date": trade_date, "count": len(rows), "items": rows, "raw": raw}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    lines = [f"# {trade_date} Tushare KPL List", "", f"- 数量：{len(rows)}", ""]
    for row in rows[:120]:
        lines.extend(
            [
                f"## {row.get('name') or '-'} {row.get('ts_code') or ''}",
                "",
                f"- 标签：{row.get('tag') or row.get('query_tag') or '-'}",
                f"- 主题：{row.get('theme') or '-'}",
                f"- 状态：{row.get('status') or '-'}",
                f"- 涨停原因：{row.get('lu_desc') or '-'}",
                f"- 涨停时间：{row.get('lu_time') or '-'}，最后涨停：{row.get('last_time') or '-'}，开板：{row.get('open_time') or '-'}",
                f"- 成交额：{row.get('amount') or '-'}，封单：{row.get('limit_order') or '-'}，换手：{row.get('turnover_rate') or '-'}",
                "",
            ]
        )
    md_path.write_text("\n".join(lines), encoding="utf-8")
    return csv_path, json_path, md_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Collect Tushare kpl_list data")
    parser.add_argument("--trade-date", default=datetime.now().strftime("%Y%m%d"), help="Trade date in YYYYMMDD")
    parser.add_argument("--tag", action="append", default=[], help="榜单类型：涨停/炸板/跌停/自然涨停/竞价；repeatable")
    parser.add_argument("--token", default="", help="Tushare token; defaults to TUSHARE_TOKEN env var")
    parser.add_argument("--out-dir", default="tushare-kpl", help="Output directory")
    parser.add_argument("--fields", default=",".join(FIELDS), help="Comma-separated Tushare fields")
    args = parser.parse_args()

    token = args.token or os.environ.get("TUSHARE_TOKEN", "")
    if not token:
        print(json.dumps({"status": "missing_token", "message": "Set TUSHARE_TOKEN or pass --token"}, ensure_ascii=False, indent=2), file=sys.stderr)
        return 2

    tags = args.tag or ["涨停", "炸板", "跌停", "竞价"]
    fields = [field.strip() for field in args.fields.split(",") if field.strip()]
    rows, raw = collect(token, args.trade_date, tags, fields)
    csv_path, json_path, md_path = write_outputs(rows, raw, Path(args.out_dir), args.trade_date)
    print(json.dumps({"status": "ok", "count": len(rows), "csv": str(csv_path), "json": str(json_path), "markdown": str(md_path)}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
