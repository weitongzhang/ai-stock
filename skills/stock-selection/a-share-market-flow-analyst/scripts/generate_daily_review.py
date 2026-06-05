#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Generate an A-share post-market review report.

The review focuses on decisions rather than data display:

- market breadth and short-term sentiment
- market fragmentation / structural split
- leading theme internal movement
- tomorrow's attack directions and risk triggers
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


def read_rows(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        raise FileNotFoundError(path)
    if path.suffix.lower() == ".json":
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            for key in ("rows", "items", "data", "history"):
                if isinstance(data.get(key), list):
                    return [dict(x) for x in data[key]]
            return [data]
        if isinstance(data, list):
            return [dict(x) for x in data]
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return [dict(row) for row in csv.DictReader(f)]


def num(value: Any, default: float = 0.0) -> float:
    if value is None:
        return default
    text = str(value).replace(",", "").replace("%", "").strip()
    if not text or text in {"-", "None", "nan", "暂无"}:
        return default
    try:
        return float(text)
    except ValueError:
        return default


def metric_map(rows: list[dict[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for row in rows:
        if "metric" in row:
            result[str(row.get("metric"))] = row.get("value")
    return result


def read_optional(paths: list[str]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for item in paths:
        if item:
            rows.extend(read_rows(Path(item)))
    return rows


def stock_name(row: dict[str, Any]) -> str:
    for key in ("name", "名称", "股票名称", "ts_name"):
        if row.get(key):
            return str(row[key]).strip()
    return ""


def row_text(row: dict[str, Any]) -> str:
    return " ".join(str(v) for v in row.values() if v is not None)


def theme_words(row: dict[str, Any]) -> list[str]:
    text = str(row.get("theme") or row.get("主题") or row.get("sectors") or row.get("板块") or "")
    text = text.replace("/", "、").replace(",", "、").replace("，", "、")
    return [item.strip() for item in text.split("、") if item.strip()]


def classify_breadth(metrics: dict[str, Any]) -> tuple[str, list[str]]:
    if str(metrics.get("今日涨跌停数据状态")) == "未更新":
        return "盘前/待确认", ["今日涨跌停池未更新，不能用 0 数据判断强弱。"]

    limit_up = num(metrics.get("涨停数"))
    failed = num(metrics.get("炸板数"))
    limit_down = num(metrics.get("跌停数"))
    seal_rate = num(metrics.get("封板率"))
    failed_rate = num(metrics.get("炸板率"))
    ratio = num(metrics.get("涨跌停强弱比"))
    reasons: list[str] = []
    score = 0

    if limit_up >= 80:
        score += 2
        reasons.append("涨停家数活跃，资金具备扩散能力。")
    elif limit_up >= 50:
        score += 1
        reasons.append("涨停家数可交易，但不是全面高潮。")
    else:
        score -= 1
        reasons.append("涨停家数偏少，短线扩散不足。")

    if ratio > 7:
        score += 1
        reasons.append("涨跌停强弱比大于 7，赚钱效应占优。")
    elif ratio > 0:
        score -= 1
        reasons.append("涨跌停强弱比小于 7，短线环境偏谨慎。")

    if failed_rate <= 20 and seal_rate >= 75:
        score += 2
        reasons.append("封板率高、炸板率低，封板质量较好。")
    elif failed_rate >= 35:
        score -= 2
        reasons.append("炸板率偏高，追高失败率上升。")

    if limit_down <= 10:
        score += 1
        reasons.append("跌停数量低，亏钱效应未扩散。")
    elif limit_down >= 25:
        score -= 2
        reasons.append("跌停数量偏多，亏钱效应扩散。")

    if score >= 5:
        return "修复增强/局部进攻", reasons
    if score >= 2:
        return "结构性修复", reasons
    if score >= 0:
        return "震荡试错", reasons
    return "分歧/防守", reasons


def classify_fragmentation(metrics: dict[str, Any], themes: list[dict[str, Any]]) -> tuple[str, list[str]]:
    advancers = num(metrics.get("上涨家数") or metrics.get("advancers"))
    decliners = num(metrics.get("下跌家数") or metrics.get("decliners"))
    top_score = max((num(row.get("total_score") or row.get("score")) for row in themes), default=0.0)
    top_count = sum(1 for row in themes if num(row.get("total_score") or row.get("score")) >= 50)
    reasons: list[str] = []

    if decliners >= 3500 and top_score >= 50:
        reasons.append(f"下跌家数 {int(decliners)}，但仍有高分主线，说明局部强、整体弱。")
        return "高", reasons
    if decliners and advancers and decliners > advancers * 1.8:
        reasons.append("下跌家数显著多于上涨家数，市场赚钱效应割裂。")
        return "中高", reasons
    if top_count >= 2 and not (advancers or decliners):
        reasons.append("存在多个强主题，但缺少涨跌家数数据，需要警惕只强主线、不强全局。")
        return "待确认", reasons
    if top_count >= 2:
        reasons.append("多个主题有强度，结构未必极端割裂。")
        return "中", reasons
    reasons.append("暂未发现强主线与全市场宽度明显背离的证据。")
    return "低/待确认", reasons


def match_kpl_rows(theme_row: dict[str, Any], kpl_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    words = theme_words(theme_row)
    candidates = str(theme_row.get("core_names") or theme_row.get("candidates") or "")
    matched: list[dict[str, Any]] = []
    for row in kpl_rows:
        text = row_text(row)
        name = stock_name(row)
        if (name and name in candidates) or any(word and word in text for word in words):
            matched.append(row)
    return matched


def classify_internal_structure(theme_row: dict[str, Any], kpl_rows: list[dict[str, Any]]) -> tuple[str, list[str], str]:
    matched = match_kpl_rows(theme_row, kpl_rows)
    score = num(theme_row.get("total_score") or theme_row.get("score"))
    kpl_count = int(num(theme_row.get("kpl_count")))
    failed_count = int(num(theme_row.get("failed_count")))
    limit_rows = [row for row in matched if "涨停" in row_text(row) or "连板" in row_text(row)]
    failed_rows = [row for row in matched if "炸" in row_text(row)]
    high_rows = [row for row in matched if "2" in str(row.get("status") or "") or "3" in str(row.get("status") or "") or "连板" in str(row.get("status") or "")]
    first_rows = [row for row in matched if "首板" in row_text(row)]
    reasons: list[str] = []

    if matched:
        reasons.append(f"匹配到板块内样本 {len(matched)} 条，涨停/连板 {len(limit_rows)}，炸板 {len(failed_rows)}。")
    elif kpl_count:
        reasons.append(f"主题计划中已有开盘啦确认 {kpl_count} 条，但样本字段不足，内部结构需人工复核。")
    else:
        reasons.append("缺少板块内涨停/炸板样本，内部结构暂按主题强度保守判断。")

    if failed_count > 0 or len(failed_rows) > 0:
        return "内部分歧", reasons + ["板块内出现炸板/失败样本，说明分歧升温。"], "只看核心承接，后排不追。"
    if high_rows and not first_rows and score >= 50:
        return "高位抱团", reasons + ["高位/连板样本更突出，低位扩散证据不足。"], "只看核心低吸或分歧承接，不追后排。"
    if first_rows and high_rows:
        return "低位扩散", reasons + ["高位仍在，低位首板也出现，主线有扩散迹象。"], "观察低位补涨晋级，核心股不破分时均线则可继续跟踪。"
    if first_rows and not high_rows:
        return "高切低/补涨试探", reasons + ["低位首板更突出，高位持续性证据不足。"], "看低位前排晋级，高位核心只看承接。"
    if score < 32:
        return "退潮/弱化", reasons + ["主题得分偏低，缺少继续进攻证据。"], "暂不作为明日主攻方向。"
    return "结构待确认", reasons, "等竞价、开盘强弱和前排晋级确认。"


def build_attack_plan(themes: list[dict[str, Any]], kpl_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    plan: list[dict[str, Any]] = []
    sorted_themes = sorted(themes, key=lambda row: num(row.get("total_score") or row.get("score")), reverse=True)
    for row in sorted_themes[:4]:
        structure, reasons, strategy = classify_internal_structure(row, kpl_rows)
        plan.append({
            "theme": row.get("theme") or row.get("主题") or "未命名主题",
            "score": num(row.get("total_score") or row.get("score")),
            "stance": row.get("stance") or row.get("动作") or "",
            "structure": structure,
            "reasons": reasons,
            "strategy": strategy,
            "core": row.get("core_names") or row.get("candidates") or row.get("kpl_stocks") or "等待盘中确认",
            "confirm": row.get("confirm_signal") or "前排竞价强于板块，容量核心放量不破分时均线。",
            "give_up": row.get("give_up_signal") or "前排炸板、核心冲高回落，或板块无量无扩散。",
        })
    return plan


def write_report(
    path: Path,
    report_date: str,
    breadth_stage: str,
    breadth_reasons: list[str],
    fragmentation: str,
    fragmentation_reasons: list[str],
    attack_plan: list[dict[str, Any]],
    limits: list[str],
) -> None:
    lines = [
        f"# {report_date} A股盘后复盘报告",
        "",
        "> 研究用途，非投资建议。",
        "",
        "## 结论",
        "",
        f"- 市场宽度：{breadth_stage}",
        f"- 市场割裂度：{fragmentation}",
        "- 明日原则：先看主线核心与前排确认，弱分支和后排谨慎。",
        "",
        "## 市场宽度",
    ]
    lines.extend(f"- {item}" for item in breadth_reasons[:5])
    lines.extend(["", "## 市场割裂度", ""])
    lines.extend(f"- {item}" for item in fragmentation_reasons)
    lines.extend(["", "## 主线内部结构与明日方向", ""])
    for item in attack_plan:
        lines.extend([
            f"### {item['theme']}：{item['structure']}",
            "",
            f"- 分数/动作：{item['score']:.1f} / {item['stance']}",
            f"- 核心观察：{item['core']}",
            f"- 内部判断：{item['strategy']}",
            f"- 确认：{item['confirm']}",
            f"- 放弃：{item['give_up']}",
        ])
        for reason in item["reasons"][:3]:
            lines.append(f"- 依据：{reason}")
        lines.append("")
    lines.extend([
        "## 风险提示",
        "",
        "- 如果真实涨跌家数显示下跌超过 3500 家，即使主线强，也按割裂行情处理。",
        "- 如果主线核心冲高回落、前排炸板，优先降低进攻性。",
        "- 如果炸板率快速升高或跌停扩散，停止后排套利。",
        "- 如果强方向只剩高位抱团，低位补涨晋级失败，防止次日补跌。",
        "",
    ])
    if limits:
        lines.extend(["## 数据限制", ""])
        lines.extend(f"- {item}" for item in limits)
        lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate A-share post-market daily review.")
    parser.add_argument("--date", required=True, help="Report date, e.g. 2026-06-04.")
    parser.add_argument("--market-breadth", required=True, help="Market breadth CSV from collect_market_breadth.py.")
    parser.add_argument("--theme-plan", action="append", default=[], help="Market-flow or CLS theme plan CSV/JSON. Repeatable.")
    parser.add_argument("--kpl", action="append", default=[], help="KPL/Tushare limit-up CSV/JSON. Repeatable.")
    parser.add_argument("--out-dir", default="examples/market/daily-review", help="Output directory.")
    args = parser.parse_args()

    limits: list[str] = []
    breadth_rows = read_rows(Path(args.market_breadth))
    metrics = metric_map(breadth_rows)
    breadth_stage, breadth_reasons = classify_breadth(metrics)
    themes = read_optional(args.theme_plan)
    if not themes:
        limits.append("未提供主题计划，无法生成明日进攻方向。")
    kpl_rows = read_optional(args.kpl)
    if not kpl_rows:
        limits.append("未提供开盘啦/涨停样本，板块内部结构判断会偏保守。")
    fragmentation, fragmentation_reasons = classify_fragmentation(metrics, themes)
    attack_plan = build_attack_plan(themes, kpl_rows)

    out_dir = Path(args.out_dir)
    md_path = out_dir / f"{args.date}-daily-review.md"
    write_report(md_path, args.date, breadth_stage, breadth_reasons, fragmentation, fragmentation_reasons, attack_plan, limits)
    print(json.dumps({"status": "ok", "markdown": str(md_path), "themes": len(themes), "directions": len(attack_plan)}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
