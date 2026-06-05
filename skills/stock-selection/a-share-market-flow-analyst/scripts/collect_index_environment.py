#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Collect and classify major A-share index environment.

Indexes define the trading environment and position constraints:

- 上证指数: large-cap / weight stability
- 深证成指: broad growth environment
- 创业板指: growth risk appetite
- 科创50: hard-tech risk appetite
- 北证50: small-cap / theme spillover
"""

from __future__ import annotations

import argparse
import csv
import json
import time
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, Callable


INDEXES = [
    {"code": "000001", "name": "上证指数", "role": "权重与大盘稳定性"},
    {"code": "399001", "name": "深证成指", "role": "成长股整体环境"},
    {"code": "399006", "name": "创业板指", "role": "成长风险偏好"},
    {"code": "000688", "name": "科创50", "role": "硬科技风险偏好"},
    {"code": "899050", "name": "北证50", "role": "小票与题材外溢"},
]


SAMPLE_ROWS = [
    {"code": "000001", "name": "上证指数", "role": "权重与大盘稳定性", "close": 3384.10, "pct_chg": 0.23, "amount_yi": 4100.0, "ma5": 3375.0, "ma10": 3368.0, "ma20": 3340.0, "above_ma5": "是", "above_ma10": "是", "above_ma20": "是", "five_day_pct": 1.10, "shape": "小阳震荡", "environment": "偏稳", "meaning": "大盘环境不拖累结构性进攻"},
    {"code": "399001", "name": "深证成指", "role": "成长股整体环境", "close": 10240.20, "pct_chg": -0.15, "amount_yi": 5400.0, "ma5": 10260.0, "ma10": 10180.0, "ma20": 10060.0, "above_ma5": "否", "above_ma10": "是", "above_ma20": "是", "five_day_pct": 0.80, "shape": "冲高回落", "environment": "中性", "meaning": "成长整体并不强，需精选主线"},
    {"code": "399006", "name": "创业板指", "role": "成长风险偏好", "close": 2050.10, "pct_chg": -0.60, "amount_yi": 2100.0, "ma5": 2070.0, "ma10": 2060.0, "ma20": 2030.0, "above_ma5": "否", "above_ma10": "否", "above_ma20": "是", "five_day_pct": -0.30, "shape": "弱阴线", "environment": "偏弱", "meaning": "高弹性成长仓位需要收敛"},
    {"code": "000688", "name": "科创50", "role": "硬科技风险偏好", "close": 980.50, "pct_chg": 1.85, "amount_yi": 920.0, "ma5": 950.0, "ma10": 930.0, "ma20": 900.0, "above_ma5": "是", "above_ma10": "是", "above_ma20": "是", "five_day_pct": 5.60, "shape": "放量强阳", "environment": "强", "meaning": "硬科技方向获得指数环境支持"},
    {"code": "899050", "name": "北证50", "role": "小票与题材外溢", "close": 880.20, "pct_chg": 0.70, "amount_yi": 180.0, "ma5": 872.0, "ma10": 870.0, "ma20": 860.0, "above_ma5": "是", "above_ma10": "是", "above_ma20": "是", "five_day_pct": 2.10, "shape": "阳线修复", "environment": "偏强", "meaning": "题材情绪有外溢，但仍需看宽度确认"},
]


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
        except Exception as exc:
            last_error = exc
            if attempt < retries:
                time.sleep(sleep_seconds)
    errors.append(f"{name}: {type(last_error).__name__}: {last_error}")
    return None


def moving_average(values: list[float], window: int) -> float:
    if not values:
        return 0.0
    sample = values[-window:] if len(values) >= window else values
    return round(sum(sample) / len(sample), 2)


def classify_shape(row: dict[str, Any]) -> str:
    open_price = number(row.get("开盘"))
    close = number(row.get("收盘"))
    high = number(row.get("最高"))
    low = number(row.get("最低"))
    pct = number(row.get("涨跌幅"))
    span = max(high - low, 0.0001)
    upper_shadow = max(high - max(open_price, close), 0.0) / span
    lower_shadow = max(min(open_price, close) - low, 0.0) / span
    if pct >= 1.5 and close >= open_price:
        return "强阳线"
    if pct > 0 and upper_shadow >= 0.45:
        return "冲高回落"
    if pct > 0:
        return "阳线修复"
    if pct < 0 and lower_shadow >= 0.45:
        return "探底回升"
    if pct <= -1.2:
        return "弱阴线"
    return "震荡"


def classify_environment(pct: float, close: float, ma5: float, ma10: float, ma20: float, five_day_pct: float, shape: str) -> tuple[str, str]:
    score = 0
    if pct >= 1:
        score += 2
    elif pct > 0:
        score += 1
    elif pct <= -1:
        score -= 2
    else:
        score -= 1
    if close >= ma5:
        score += 1
    else:
        score -= 1
    if close >= ma10:
        score += 1
    if close >= ma20:
        score += 1
    else:
        score -= 1
    if five_day_pct >= 2:
        score += 1
    elif five_day_pct <= -2:
        score -= 1
    if shape == "冲高回落":
        score -= 1
    if shape == "强阳线":
        score += 1

    if score >= 4:
        return "强", "指数环境支持对应风格进攻"
    if score >= 2:
        return "偏强", "指数环境允许结构性进攻"
    if score >= 0:
        return "中性", "指数环境不拖累，但需要板块确认"
    return "偏弱", "指数环境约束仓位和追高"


def collect_one_index(ak: Any, item: dict[str, str], start_date: str, end_date: str, retries: int, sleep_seconds: float, errors: list[str]) -> dict[str, Any] | None:
    code = item["code"]
    df = call_with_retry(
        f"index_zh_a_hist:{code}",
        lambda: ak.index_zh_a_hist(symbol=code, period="daily", start_date=start_date, end_date=end_date),
        retries,
        sleep_seconds,
        errors,
    )
    if df is None or len(df) == 0:
        return None
    df = df.sort_values("日期")
    latest = df.iloc[-1].to_dict()
    closes = [number(x) for x in df["收盘"].tolist()]
    close = number(latest.get("收盘"))
    pct = number(latest.get("涨跌幅"))
    ma5 = moving_average(closes, 5)
    ma10 = moving_average(closes, 10)
    ma20 = moving_average(closes, 20)
    five_day_pct = round((close / closes[-6] - 1) * 100, 2) if len(closes) >= 6 and closes[-6] else 0.0
    shape = classify_shape(latest)
    environment, meaning = classify_environment(pct, close, ma5, ma10, ma20, five_day_pct, shape)
    return {
        "source": "akshare",
        "code": code,
        "name": item["name"],
        "role": item["role"],
        "date": str(latest.get("日期")),
        "close": close,
        "pct_chg": pct,
        "amount_yi": round(number(latest.get("成交额")) / 100_000_000, 2),
        "ma5": ma5,
        "ma10": ma10,
        "ma20": ma20,
        "above_ma5": "是" if close >= ma5 else "否",
        "above_ma10": "是" if close >= ma10 else "否",
        "above_ma20": "是" if close >= ma20 else "否",
        "five_day_pct": five_day_pct,
        "shape": shape,
        "environment": environment,
        "meaning": meaning,
    }


def summarize_index_environment(rows: list[dict[str, Any]]) -> tuple[str, list[str]]:
    if not rows:
        return "指数数据不足", ["指数行情未采集成功，复盘中暂不使用指数约束。"]
    strong = [row for row in rows if str(row.get("environment")) in {"强", "偏强"}]
    weak = [row for row in rows if str(row.get("environment")) == "偏弱"]
    reasons: list[str] = []
    for row in sorted(rows, key=lambda x: number(x.get("pct_chg")), reverse=True)[:2]:
        reasons.append(f"{row['name']}相对更强，{row['role']}偏受资金认可。")
    if any(row.get("name") == "科创50" and row.get("environment") in {"强", "偏强"} for row in rows):
        reasons.append("科创50偏强时，硬科技、半导体、AI硬件方向的指数约束更友好。")
    if any(row.get("name") == "创业板指" and row.get("environment") == "偏弱" for row in rows):
        reasons.append("创业板偏弱时，高弹性成长方向需要降低追高。")
    if any(row.get("name") == "北证50" and row.get("environment") in {"强", "偏强"} for row in rows):
        reasons.append("北证50偏强时，小票题材有外溢可能，但仍需宽度配合。")
    if len(strong) >= 4 and not weak:
        return "指数环境支持进攻", reasons
    if strong and weak:
        return "指数环境结构分化", reasons
    if weak and len(weak) >= 3:
        return "指数环境偏防守", reasons
    return "指数环境中性", reasons


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = ["source", "code", "name", "role", "date", "close", "pct_chg", "amount_yi", "ma5", "ma10", "ma20", "above_ma5", "above_ma10", "above_ma20", "five_day_pct", "shape", "environment", "meaning"]
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def write_markdown(path: Path, report_date: str, rows: list[dict[str, Any]], conclusion: str, reasons: list[str], errors: list[str]) -> None:
    lines = [
        f"# {report_date} A股指数环境",
        "",
        "> 研究用途，非投资建议。",
        "",
        f"## 结论：{conclusion}",
        "",
    ]
    lines.extend(f"- {item}" for item in reasons)
    lines.extend([
        "",
        "## 五大指数",
        "",
        "| 指数 | 涨跌幅 | 5日涨跌 | 形态 | 趋势 | 含义 |",
        "|---|---:|---:|---|---|---|",
    ])
    for row in rows:
        lines.append(f"| {row['name']} | {row['pct_chg']} | {row['five_day_pct']} | {row['shape']} | {row['environment']} | {row['meaning']} |")
    if errors:
        lines.extend(["", "## 数据限制", ""])
        lines.extend(f"- {item}" for item in errors)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Collect major A-share index environment.")
    parser.add_argument("--date", default=date.today().isoformat(), help="Report date, YYYY-MM-DD or YYYYMMDD.")
    parser.add_argument("--out-dir", default="examples/market/index-environment", help="Output directory.")
    parser.add_argument("--retries", type=int, default=2, help="Retry count per index.")
    parser.add_argument("--sleep", type=float, default=1.5, help="Seconds between retries.")
    parser.add_argument("--source", choices=["akshare", "sample"], default="akshare", help="Use live AkShare data or sample data.")
    args = parser.parse_args()

    compact = args.date.replace("-", "")
    report_date = f"{compact[:4]}-{compact[4:6]}-{compact[6:]}" if len(compact) == 8 else args.date
    end_dt = datetime.strptime(compact, "%Y%m%d").date() if len(compact) == 8 else date.today()
    start_date = (end_dt - timedelta(days=45)).strftime("%Y%m%d")
    end_date = end_dt.strftime("%Y%m%d")
    errors: list[str] = []

    if args.source == "sample":
        rows = [dict(row, date=report_date, source="sample") for row in SAMPLE_ROWS]
        errors.append("当前指数环境由 --source sample 生成，仅用于报告结构演示；实盘复盘请使用 akshare 实时采集结果。")
    else:
        try:
            import akshare as ak  # type: ignore
        except Exception as exc:
            print(json.dumps({"status": "missing_dependency", "message": str(exc)}, ensure_ascii=False, indent=2))
            return 2
        rows = []
        for item in INDEXES:
            result = collect_one_index(ak, item, start_date, end_date, args.retries, args.sleep, errors)
            if result:
                rows.append(result)

    conclusion, reasons = summarize_index_environment(rows)
    out_dir = Path(args.out_dir)
    csv_path = out_dir / f"{report_date}-index-environment.csv"
    json_path = out_dir / f"{report_date}-index-environment.json"
    md_path = out_dir / f"{report_date}-index-environment.md"
    write_csv(csv_path, rows)
    json_path.write_text(json.dumps({"date": report_date, "source": args.source, "conclusion": conclusion, "reasons": reasons, "rows": rows, "errors": errors}, ensure_ascii=False, indent=2), encoding="utf-8")
    write_markdown(md_path, report_date, rows, conclusion, reasons, errors)

    status = "ok" if rows and not errors else "partial" if rows else "failed"
    print(json.dumps({"status": status, "conclusion": conclusion, "indexes": len(rows), "csv": str(csv_path), "json": str(json_path), "markdown": str(md_path), "errors": errors}, ensure_ascii=False, indent=2))
    return 0 if rows else 1


if __name__ == "__main__":
    raise SystemExit(main())
