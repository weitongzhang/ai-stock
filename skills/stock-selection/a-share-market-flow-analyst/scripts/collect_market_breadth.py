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
from datetime import date, datetime, timedelta
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


def read_metric(rows: list[dict[str, Any]], metric: str) -> float | None:
    for row in rows:
        if row.get("metric") == metric:
            return number(row.get("value"))
    return None


def collect_single_day_limit_snapshot(ak: Any, trade_date: str, retries: int, sleep_seconds: float) -> tuple[dict[str, Any] | None, list[str]]:
    rows: list[dict[str, Any]] = []
    errors: list[str] = []
    collect_limit_pools(ak, trade_date, rows, errors, retries, sleep_seconds)
    limit_up = read_metric(rows, "涨停数")
    failed = read_metric(rows, "炸板数")
    limit_down = read_metric(rows, "跌停数")
    if limit_up is None and failed is None and limit_down is None:
        return None, errors
    report_date = f"{trade_date[:4]}-{trade_date[4:6]}-{trade_date[6:]}"
    return {
        "date": report_date,
        "trade_date": trade_date,
        "limit_up_count": int(limit_up or 0),
        "failed_limit_up_count": int(failed or 0),
        "limit_down_count": int(limit_down or 0),
        "seal_rate": read_metric(rows, "封板率") or 0.0,
        "failed_limit_up_rate": read_metric(rows, "炸板率") or 0.0,
        "limit_up_seal_amount_yi": read_metric(rows, "涨停封板资金") or 0.0,
        "double_limit_up_count": int(read_metric(rows, "连板家数") or 0),
        "highest_limit_streak": int(read_metric(rows, "最高连板") or 0),
    }, errors


def is_empty_limit_snapshot(snapshot: dict[str, Any] | None) -> bool:
    if not snapshot:
        return True
    return (
        number(snapshot.get("limit_up_count")) == 0
        and number(snapshot.get("failed_limit_up_count")) == 0
        and number(snapshot.get("limit_down_count")) == 0
        and number(snapshot.get("highest_limit_streak")) == 0
    )


def collect_limit_history(ak: Any, end_trade_date: str, days: int, retries: int, sleep_seconds: float) -> tuple[list[dict[str, Any]], list[str]]:
    history: list[dict[str, Any]] = []
    errors: list[str] = []
    end_date = datetime.strptime(end_trade_date, "%Y%m%d").date()
    cursor = end_date
    max_calendar_days = max(days * 3, 10)
    while len(history) < days and (end_date - cursor).days <= max_calendar_days:
        if cursor.weekday() < 5:
            trade_date = cursor.strftime("%Y%m%d")
            snapshot, day_errors = collect_single_day_limit_snapshot(ak, trade_date, retries, sleep_seconds)
            errors.extend(f"{trade_date}: {error}" for error in day_errors)
            if snapshot and not is_empty_limit_snapshot(snapshot):
                history.append(snapshot)
        cursor -= timedelta(days=1)
    return sorted(history, key=lambda item: item["trade_date"]), errors


def append_history_metrics(rows: list[dict[str, Any]], history: list[dict[str, Any]]) -> None:
    if not history:
        return
    latest = history[-1]
    previous = history[:-1]
    add_metric(rows, "近N日样本数", len(history), "derived:market_breadth_history")
    if not previous:
        return
    prev_limit_avg = sum(number(x.get("limit_up_count")) for x in previous) / len(previous)
    prev_failed_rate_avg = sum(number(x.get("failed_limit_up_rate")) for x in previous) / len(previous)
    prev_down_avg = sum(number(x.get("limit_down_count")) for x in previous) / len(previous)
    prev_streak_avg = sum(number(x.get("highest_limit_streak")) for x in previous) / len(previous)
    add_metric(rows, "近几日涨停均值", round(prev_limit_avg, 2), "derived:market_breadth_history")
    add_metric(rows, "近几日炸板率均值", round(prev_failed_rate_avg, 2), "derived:market_breadth_history", "%")
    add_metric(rows, "近几日跌停均值", round(prev_down_avg, 2), "derived:market_breadth_history")
    add_metric(rows, "近几日最高连板均值", round(prev_streak_avg, 2), "derived:market_breadth_history")
    add_metric(rows, "涨停趋势差", round(number(latest.get("limit_up_count")) - prev_limit_avg, 2), "derived:market_breadth_history")
    add_metric(rows, "炸板率趋势差", round(number(latest.get("failed_limit_up_rate")) - prev_failed_rate_avg, 2), "derived:market_breadth_history", "%")
    add_metric(rows, "跌停趋势差", round(number(latest.get("limit_down_count")) - prev_down_avg, 2), "derived:market_breadth_history")
    add_metric(rows, "连板高度趋势差", round(number(latest.get("highest_limit_streak")) - prev_streak_avg, 2), "derived:market_breadth_history")


def write_history_csv(path: Path, history: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "date",
        "trade_date",
        "limit_up_count",
        "failed_limit_up_count",
        "limit_down_count",
        "seal_rate",
        "failed_limit_up_rate",
        "limit_up_seal_amount_yi",
        "double_limit_up_count",
        "highest_limit_streak",
    ]
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(history)


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


def classify_breadth(rows: list[dict[str, Any]]) -> tuple[str, str, list[str]]:
    by_metric = {str(row["metric"]): number(row.get("value")) for row in rows}
    status_by_metric = {str(row.get("metric")): str(row.get("value")) for row in rows}
    if status_by_metric.get("今日涨跌停数据状态") == "未更新":
        reasons = ["今日涨跌停池仍为空，当前不作为真实盘面宽度判断"]
        if by_metric.get("近N日样本数", 0.0) >= 3:
            reasons.append("近几日背景已保留，可用于盘前制定观察计划")
            limit_trend = by_metric.get("涨停趋势差", 0.0)
            failed_rate_trend = by_metric.get("炸板率趋势差", 0.0)
            down_trend = by_metric.get("跌停趋势差", 0.0)
            if limit_trend > 10:
                reasons.append("最近已完成交易日涨停数高于前期均值，背景偏修复")
            elif limit_trend < -10:
                reasons.append("最近已完成交易日涨停数低于前期均值，背景偏收缩")
            if failed_rate_trend < -5:
                reasons.append("最近已完成交易日炸板率低于前期均值，封板质量改善")
            if down_trend < 0:
                reasons.append("最近已完成交易日跌停数低于前期均值，亏钱效应收敛")
        reasons.append("成交额和涨跌家数缺失，仓位结论需要保守使用")
        return "盘前/待确认", "今天盘面宽度尚未形成，先参考最近已完成交易日背景；等9:35-10:00后重新采集，再决定是否提高进攻性。", reasons
    limit_up = by_metric.get("涨停数", 0.0)
    failed_rate = by_metric.get("炸板率", 0.0)
    limit_down = by_metric.get("跌停数", 0.0)
    highest = by_metric.get("最高连板", 0.0)
    limit_trend = by_metric.get("涨停趋势差", 0.0)
    failed_rate_trend = by_metric.get("炸板率趋势差", 0.0)
    down_trend = by_metric.get("跌停趋势差", 0.0)
    sample_count = by_metric.get("近N日样本数", 1.0)

    reasons: list[str] = []
    score = 0
    if limit_up >= 80:
        score += 2
        reasons.append("涨停家数处于较活跃区间")
    elif limit_up >= 50:
        score += 1
        reasons.append("涨停家数处于可交易区间")
    else:
        score -= 1
        reasons.append("涨停家数偏少，短线扩散不足")

    if failed_rate <= 20:
        score += 2
        reasons.append("炸板率低，封板质量较好")
    elif failed_rate <= 30:
        score += 1
        reasons.append("炸板率可控，但仍有分歧")
    else:
        score -= 2
        reasons.append("炸板率偏高，追高失败率上升")

    if limit_down <= 10:
        score += 1
        reasons.append("跌停数量未扩散，亏钱效应可控")
    elif limit_down >= 25:
        score -= 2
        reasons.append("跌停数量偏多，亏钱效应扩散")

    if highest >= 6:
        score += 1
        reasons.append("连板高度打开，短线风险偏好较强")
    elif highest <= 3:
        score -= 1
        reasons.append("连板高度有限，资金更偏轮动而非抱团")

    if sample_count >= 3:
        if limit_trend > 10:
            score += 1
            reasons.append("涨停数高于近几日均值，情绪在加强")
        elif limit_trend < -10:
            score -= 1
            reasons.append("涨停数低于近几日均值，扩散在收缩")
        if failed_rate_trend < -5:
            score += 1
            reasons.append("炸板率低于近几日均值，封板质量改善")
        elif failed_rate_trend > 5:
            score -= 1
            reasons.append("炸板率高于近几日均值，分歧升温")
        if down_trend > 5:
            score -= 1
            reasons.append("跌停数高于近几日均值，防守需求上升")
    if "两市成交额" not in {str(row.get("metric")) for row in rows} or "上涨家数" not in {str(row.get("metric")) for row in rows}:
        reasons.append("成交额和涨跌家数缺失，仓位结论需要保守使用")

    if score >= 5:
        stage = "修复增强/局部进攻"
        strategy = "明日可积极观察主线前排，但仍需竞价和开盘确认，不追后排一致性高潮。"
    elif score >= 2:
        stage = "结构性修复"
        strategy = "明日适合小仓试错强主题前排或容量核心，弱分支只观察。"
    elif score >= 0:
        stage = "震荡试错"
        strategy = "明日以确认后参与为主，优先低吸承接强的核心，减少追高。"
    else:
        stage = "分歧/防守"
        strategy = "明日以防守为主，等待炸板率回落、跌停减少或新主线确认。"
    return stage, strategy, reasons


def write_markdown(path: Path, report_date: str, rows: list[dict[str, Any]], history: list[dict[str, Any]], errors: list[str]) -> None:
    by_metric = {str(row["metric"]): row for row in rows}

    def val(metric: str, default: str = "暂无") -> str:
        row = by_metric.get(metric)
        if not row:
            return default
        note = str(row.get("note") or "")
        return f"{row['value']}{note}" if note in {"%", "亿元"} else str(row["value"])

    stage, strategy, reasons = classify_breadth(rows)
    lines = [
        f"# {report_date} A股市场宽度快照",
        "",
        "> 研究用途，非投资建议。",
        "",
        f"## 结论：{stage}",
        "",
        strategy,
        "",
        "依据：",
    ]
    lines.extend(f"- {reason}" for reason in reasons)
    lines.extend([
        "",
        "## 核心指标",
        "",
        f"- 两市成交额：{val('两市成交额')}",
        f"- 涨跌家数：上涨 {val('上涨家数')} / 下跌 {val('下跌家数')} / 平盘 {val('平盘家数')}",
        f"- 涨跌停：涨停 {val('涨停数')} / 炸板 {val('炸板数')} / 跌停 {val('跌停数')}",
        f"- 情绪质量：封板率 {val('封板率')}，炸板率 {val('炸板率')}",
        f"- 连板结构：连板 {val('连板家数')}，最高连板 {val('最高连板')}",
        "",
    ])
    if history:
        lines.extend([
            "## 近几日背景",
            "",
            "| 日期 | 涨停 | 炸板 | 跌停 | 封板率 | 炸板率 | 连板家数 | 最高连板 |",
            "|---|---:|---:|---:|---:|---:|---:|---:|",
        ])
        for item in history:
            lines.append(
                f"| {item['date']} | {item['limit_up_count']} | {item['failed_limit_up_count']} | "
                f"{item['limit_down_count']} | {item['seal_rate']} | {item['failed_limit_up_rate']} | "
                f"{item['double_limit_up_count']} | {item['highest_limit_streak']} |"
            )
        lines.extend([
            "",
            f"- 涨停趋势差：{val('涨停趋势差')}，炸板率趋势差：{val('炸板率趋势差')}，跌停趋势差：{val('跌停趋势差')}",
            "",
        ])
    lines.extend([
        "## 明细",
        "",
        "| 指标 | 数值 | 来源 | 备注 |",
        "|---|---:|---|---|",
    ])
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
    parser.add_argument("--history-days", type=int, default=5, help="Collect recent limit-pool history for context.")
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
    current_snapshot = {
        "limit_up_count": read_metric(rows, "涨停数") or 0.0,
        "failed_limit_up_count": read_metric(rows, "炸板数") or 0.0,
        "limit_down_count": read_metric(rows, "跌停数") or 0.0,
        "highest_limit_streak": read_metric(rows, "最高连板") or 0.0,
    }
    if is_empty_limit_snapshot(current_snapshot):
        add_metric(rows, "今日涨跌停数据状态", "未更新", "derived:current_limit_pools", "盘前或数据源未更新")
    if not args.skip_fund_flow:
        collect_market_fund_flow(ak, rows, errors, args.retries, args.sleep)
    history: list[dict[str, Any]] = []
    if args.history_days > 1:
        history, history_errors = collect_limit_history(ak, trade_date, args.history_days, args.retries, args.sleep)
        errors.extend(history_errors)
        append_history_metrics(rows, history)

    out_dir = Path(args.out_dir)
    csv_path = out_dir / f"{report_date}-market-breadth.csv"
    json_path = out_dir / f"{report_date}-market-breadth.json"
    md_path = out_dir / f"{report_date}-market-breadth.md"
    history_csv_path = out_dir / f"{report_date}-market-breadth-history.csv"
    write_csv(csv_path, rows)
    write_history_csv(history_csv_path, history)
    json_path.write_text(json.dumps({"date": report_date, "rows": rows, "history": history, "errors": errors}, ensure_ascii=False, indent=2), encoding="utf-8")
    write_markdown(md_path, report_date, rows, history, errors)

    status = "ok" if rows and not errors else "partial" if rows else "failed"
    print(json.dumps({"status": status, "metrics": len(rows), "history_days": len(history), "errors": errors, "csv": str(csv_path), "history_csv": str(history_csv_path), "json": str(json_path), "markdown": str(md_path)}, ensure_ascii=False, indent=2))
    return 0 if rows else 1


if __name__ == "__main__":
    raise SystemExit(main())
