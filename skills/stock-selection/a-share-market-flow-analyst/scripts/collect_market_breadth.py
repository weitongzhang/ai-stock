#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Collect A-share market breadth from Eastmoney/AkShare.

The collector is deliberately tolerant: if the full A-share spot endpoint is
temporarily rejected by Eastmoney, limit-up / failed-limit / limit-down pools can
still produce a useful partial market overview.
"""

from __future__ import annotations

import argparse
import csv
import json
import time
from datetime import date
from pathlib import Path
from typing import Any, Callable


def normalize_date(value: str) -> tuple[str, str]:
    text = value.strip()
    if len(text) == 8 and text.isdigit():
        return f"{text[:4]}-{text[4:6]}-{text[6:]}", text
    compact = text.replace("-", "")
    if len(compact) == 8 and compact.isdigit():
        return f"{compact[:4]}-{compact[4:6]}-{compact[6:]}", compact
    raise ValueError(f"Unsupported date format: {value}")


def number(value: Any, default: float = 0.0) -> float:
    if value is None:
        return default
    text = str(value).replace(",", "").replace("%", "").strip()
    if not text or text in {"-", "None", "nan"}:
        return default
    try:
        return float(text)
    except ValueError:
        return default


def call_with_retry(name: str, fn: Callable[[], Any], retries: int, sleep_seconds: float, errors: list[str]) -> Any:
    last_error: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            return fn()
        except Exception as exc:  # AkShare/Eastmoney raises several network/parser errors.
            last_error = exc
            if attempt < retries:
                time.sleep(sleep_seconds)
    errors.append(f"{name}: {type(last_error).__name__}: {last_error}")
    return None


def add_metric(rows: list[dict[str, Any]], metric: str, value: Any, source: str, note: str = "") -> None:
    rows.append({"metric": metric, "value": value, "source": source, "note": note})


def collect_spot(ak: Any, rows: list[dict[str, Any]], errors: list[str], retries: int, sleep_seconds: float) -> None:
    df = call_with_retry("stock_zh_a_spot_em", ak.stock_zh_a_spot_em, retries, sleep_seconds, errors)
    if df is None:
        return
    if "涨跌幅" not in df.columns or "成交额" not in df.columns:
        errors.append(f"stock_zh_a_spot_em: missing expected columns, got {list(df.columns)}")
        return

    pct = df["涨跌幅"].map(number)
    amount = df["成交额"].map(number)
    total_amount_yi = round(float(amount.sum()) / 100_000_000, 2)
    add_metric(rows, "两市成交额", total_amount_yi, "eastmoney:stock_zh_a_spot_em", "亿元")
    add_metric(rows, "上涨家数", int((pct > 0).sum()), "eastmoney:stock_zh_a_spot_em")
    add_metric(rows, "下跌家数", int((pct < 0).sum()), "eastmoney:stock_zh_a_spot_em")
    add_metric(rows, "平盘家数", int((pct == 0).sum()), "eastmoney:stock_zh_a_spot_em")
    add_metric(rows, "全A股票数", int(len(df)), "eastmoney:stock_zh_a_spot_em")


def collect_limit_pools(ak: Any, trade_date: str, rows: list[dict[str, Any]], errors: list[str], retries: int, sleep_seconds: float) -> None:
    pools = [
        ("涨停数", "eastmoney:stock_zt_pool_em", lambda: ak.stock_zt_pool_em(date=trade_date)),
        ("炸板数", "eastmoney:stock_zt_pool_zbgc_em", lambda: ak.stock_zt_pool_zbgc_em(date=trade_date)),
        ("跌停数", "eastmoney:stock_zt_pool_dtgc_em", lambda: ak.stock_zt_pool_dtgc_em(date=trade_date)),
    ]
    counts: dict[str, int] = {}
    for metric, source, fn in pools:
        df = call_with_retry(source, fn, retries, sleep_seconds, errors)
        if df is None:
            continue
        count = int(len(df))
        counts[metric] = count
        add_metric(rows, metric, count, source)
        if metric == "涨停数" and "连板数" in df.columns:
            add_metric(rows, "连板家数", int((df["连板数"].map(number) >= 2).sum()), source)
            add_metric(rows, "最高连板", int(df["连板数"].map(number).max() or 0), source)
        if metric == "涨停数" and "封板资金" in df.columns:
            add_metric(rows, "涨停封板资金", round(float(df["封板资金"].map(number).sum()) / 100_000_000, 2), source, "亿元")

    limit_up = counts.get("涨停数")
    failed = counts.get("炸板数")
    if limit_up is not None and failed is not None:
        denominator = limit_up + failed
        failed_rate = round(failed / denominator * 100, 2) if denominator else 0.0
        seal_rate = round(limit_up / denominator * 100, 2) if denominator else 0.0
        add_metric(rows, "炸板率", failed_rate, "derived:eastmoney_limit_pools", "%")
        add_metric(rows, "封板率", seal_rate, "derived:eastmoney_limit_pools", "%")


def collect_market_fund_flow(ak: Any, rows: list[dict[str, Any]], errors: list[str], retries: int, sleep_seconds: float) -> None:
    df = call_with_retry("stock_market_fund_flow", ak.stock_market_fund_flow, retries, sleep_seconds, errors)
    if df is None or len(df) == 0:
        return
    latest = df.iloc[-1].to_dict()
    for key in ("主力净流入-净额", "主力净流入净额", "净流入", "今日主力净流入"):
        if key in latest:
            add_metric(rows, "大盘主力净流入", round(number(latest.get(key)) / 100_000_000, 2), "eastmoney:stock_market_fund_flow", "亿元")
            break


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["metric", "value", "source", "note"])
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, report_date: str, rows: list[dict[str, Any]], errors: list[str]) -> None:
    by_metric = {str(row["metric"]): row for row in rows}

    def val(metric: str, default: str = "-") -> str:
        row = by_metric.get(metric)
        if not row:
            return default
        note = str(row.get("note") or "")
        return f"{row['value']}{note}" if note in {"%", "亿元"} else str(row["value"])

    lines = [
        f"# {report_date} A股市场宽度快照",
        "",
        "> 研究用途，非投资建议。",
        "",
        "## 核心指标",
        "",
        f"- 两市成交额：{val('两市成交额')}",
        f"- 涨跌家数：上涨 {val('上涨家数')} / 下跌 {val('下跌家数')} / 平盘 {val('平盘家数')}",
        f"- 涨跌停：涨停 {val('涨停数')} / 炸板 {val('炸板数')} / 跌停 {val('跌停数')}",
        f"- 情绪质量：封板率 {val('封板率')}，炸板率 {val('炸板率')}",
        f"- 连板结构：连板 {val('连板家数')}，最高连板 {val('最高连板')}",
        "",
        "## 明细",
        "",
        "| 指标 | 数值 | 来源 | 备注 |",
        "|---|---:|---|---|",
    ]
    for row in rows:
        lines.append(f"| {row['metric']} | {row['value']} | {row['source']} | {row.get('note', '')} |")
    if errors:
        lines.extend(["", "## 采集限制", ""])
        lines.extend(f"- {error}" for error in errors)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Collect A-share market breadth from Eastmoney/AkShare.")
    parser.add_argument("--date", default=date.today().isoformat(), help="Trade date, YYYY-MM-DD or YYYYMMDD.")
    parser.add_argument("--out-dir", default="examples/market/market-breadth", help="Output directory.")
    parser.add_argument("--retries", type=int, default=2, help="Retry count for each data endpoint.")
    parser.add_argument("--sleep", type=float, default=1.5, help="Seconds between retries.")
    parser.add_argument("--skip-spot", action="store_true", help="Skip full A-share realtime quote endpoint.")
    parser.add_argument("--skip-fund-flow", action="store_true", help="Skip market fund-flow endpoint.")
    args = parser.parse_args()

    report_date, trade_date = normalize_date(args.date)
    rows: list[dict[str, Any]] = []
    errors: list[str] = []

    try:
        import akshare as ak  # type: ignore
    except Exception as exc:
        print(json.dumps({"status": "missing_dependency", "message": str(exc)}, ensure_ascii=False, indent=2))
        return 2

    if not args.skip_spot:
        collect_spot(ak, rows, errors, args.retries, args.sleep)
    collect_limit_pools(ak, trade_date, rows, errors, args.retries, args.sleep)
    if not args.skip_fund_flow:
        collect_market_fund_flow(ak, rows, errors, args.retries, args.sleep)

    out_dir = Path(args.out_dir)
    csv_path = out_dir / f"{report_date}-market-breadth.csv"
    json_path = out_dir / f"{report_date}-market-breadth.json"
    md_path = out_dir / f"{report_date}-market-breadth.md"
    write_csv(csv_path, rows)
    json_path.write_text(json.dumps({"date": report_date, "rows": rows, "errors": errors}, ensure_ascii=False, indent=2), encoding="utf-8")
    write_markdown(md_path, report_date, rows, errors)

    status = "ok" if rows and not errors else "partial" if rows else "failed"
    print(json.dumps({"status": status, "metrics": len(rows), "errors": errors, "csv": str(csv_path), "json": str(json_path), "markdown": str(md_path)}, ensure_ascii=False, indent=2))
    return 0 if rows else 1


if __name__ == "__main__":
    raise SystemExit(main())
