#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Build an A-share market-flow and next-day sector plan.

The script intentionally accepts loose CSV/JSON inputs from other local skills.
It favors explainable scoring over fragile point predictions.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from datetime import date
from pathlib import Path
from typing import Any


THEME_KEYWORDS = {
    "AI算力/数据中心": ["AI", "算力", "光通信", "光模块", "数据中心", "服务器", "液冷"],
    "6G/通信/卫星互联网": ["6G", "通信", "卫星", "商业航天", "射频", "终端"],
    "半导体/国产替代": ["半导体", "芯片", "国产替代", "光刻", "先进封装", "存储"],
    "能源/煤炭/油气": ["能源", "煤炭", "油气", "油价", "柴油", "航运"],
    "机器人/具身智能": ["机器人", "具身", "减速器", "伺服", "传感器", "执行器"],
    "消费/旅游/短剧": ["消费", "旅游", "酒店", "零售", "短剧", "传媒", "游戏"],
}


def read_rows(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        raise FileNotFoundError(path)
    if path.suffix.lower() == ".json":
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            for key in ("items", "data", "rows"):
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
    text = str(value).strip().replace(",", "").replace("%", "")
    if not text:
        return default
    try:
        return float(text)
    except ValueError:
        return default


def split_names(value: Any) -> list[str]:
    if value is None:
        return []
    text = str(value).replace("，", ",").replace("、", ",")
    return [x.strip() for x in text.split(",") if x.strip()]


def norm_text(row: dict[str, Any]) -> str:
    return " ".join(str(v) for v in row.values() if v is not None)


def detect_theme(row: dict[str, Any]) -> str | None:
    text = norm_text(row)
    best_theme = None
    best_hits = 0
    for theme, words in THEME_KEYWORDS.items():
        hits = sum(1 for word in words if word and word in text)
        if hits > best_hits:
            best_theme = theme
            best_hits = hits
    return best_theme


def read_cls_plan(paths: list[Path]) -> dict[str, dict[str, Any]]:
    themes: dict[str, dict[str, Any]] = {}
    for path in paths:
        for row in read_rows(path):
            theme = str(row.get("theme") or row.get("板块") or row.get("主题") or "").strip()
            if not theme:
                theme = detect_theme(row) or "未归类"
            item = themes.setdefault(
                theme,
                {
                    "theme": theme,
                    "cls_score": 0.0,
                    "news_count": 0.0,
                    "red_count": 0.0,
                    "policy_count": 0.0,
                    "candidates": [],
                    "keywords": set(),
                    "sectors": set(),
                    "confirm": "",
                    "give_up": "",
                },
            )
            item["cls_score"] = max(item["cls_score"], num(row.get("score") or row.get("评分")))
            item["news_count"] += num(row.get("news_count") or row.get("新闻数"))
            item["red_count"] += num(row.get("red_count") or row.get("加红数"))
            item["policy_count"] += num(row.get("policy_count") or row.get("政策数"))
            item["candidates"].extend(split_names(row.get("candidates") or row.get("候选股")))
            item["keywords"].update(split_names(row.get("keywords") or row.get("关键词")))
            item["sectors"].update(split_names(row.get("sectors") or row.get("板块")))
            item["confirm"] = item["confirm"] or str(row.get("confirm_signal") or "")
            item["give_up"] = item["give_up"] or str(row.get("give_up_signal") or "")
    return themes


def read_kpl(paths: list[Path]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in paths:
        rows.extend(read_rows(path))
    return rows


def stock_name(row: dict[str, Any]) -> str:
    for key in ("名称", "name", "股票名称", "ts_name"):
        if row.get(key):
            return str(row[key]).strip()
    return ""


def kpl_tag(row: dict[str, Any]) -> str:
    return str(row.get("tag") or row.get("标签") or row.get("status") or row.get("状态") or "")


def attach_kpl(themes: dict[str, dict[str, Any]], rows: list[dict[str, Any]]) -> None:
    for item in themes.values():
        item["kpl_rows"] = []
        item["kpl_stocks"] = []
    for row in rows:
        name = stock_name(row)
        text = norm_text(row)
        matched: set[str] = set()
        for theme, item in themes.items():
            if name and name in item.get("candidates", []):
                matched.add(theme)
            words = THEME_KEYWORDS.get(theme, [])
            if any(word in text for word in words):
                matched.add(theme)
        if not matched:
            theme = detect_theme(row)
            if theme and theme in themes:
                matched.add(theme)
        for theme in matched:
            themes[theme]["kpl_rows"].append(row)
            if name:
                themes[theme]["kpl_stocks"].append(name)


def read_lhb(paths: list[Path]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in paths:
        rows.extend(read_rows(path))
    return rows


def lhb_net(row: dict[str, Any]) -> float:
    for key in ("龙虎榜净买额", "net_buy", "净买额", "净额"):
        if key in row:
            return num(row.get(key))
    return 0.0


def attach_lhb(themes: dict[str, dict[str, Any]], rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    top = sorted(rows, key=lhb_net, reverse=True)[:10]
    for item in themes.values():
        names = set(item.get("candidates", [])) | set(item.get("kpl_stocks", []))
        hits = [row for row in rows if stock_name(row) in names]
        item["lhb_rows"] = hits
        item["lhb_net_buy"] = sum(lhb_net(row) for row in hits)
        item["lhb_stocks"] = [stock_name(row) for row in sorted(hits, key=lhb_net, reverse=True) if stock_name(row)]
    return top


def read_market_overview(paths: list[Path]) -> dict[str, float]:
    overview: dict[str, float] = {}
    for path in paths:
        for row in read_rows(path):
            if "metric" in row and "value" in row:
                overview[str(row["metric"])] = num(row["value"])
            else:
                for key, value in row.items():
                    overview[str(key)] = num(value)
    return overview


def score_theme(item: dict[str, Any], overview: dict[str, float]) -> dict[str, Any]:
    flow = min(35.0, item.get("cls_score", 0.0) * 0.35 + item.get("red_count", 0.0) * 3.0)
    kpl_rows = item.get("kpl_rows", [])
    kpl_count = len(kpl_rows)
    failed_count = sum(1 for row in kpl_rows if "炸" in kpl_tag(row))
    limit_count = sum(1 for row in kpl_rows if "涨停" in kpl_tag(row) or "连板" in kpl_tag(row))
    map_score = min(25.0, item.get("news_count", 0.0) * 2.0 + kpl_count * 5.0 + len(item.get("sectors", [])) * 0.8)
    lhb_net_buy = item.get("lhb_net_buy", 0.0)
    core = min(25.0, limit_count * 5.0 + len(item.get("lhb_rows", [])) * 3.0 + max(0.0, lhb_net_buy) / 100_000_000 * 2.0)
    timing = 10.0 if limit_count else 5.0
    timing -= failed_count * 2.0
    if overview:
        turnover = overview.get("两市成交额") or overview.get("成交额") or overview.get("turnover")
        if turnover and turnover >= 10_000:
            flow += 3.0
        limit_ups = overview.get("涨停数") or overview.get("limit_up_count")
        failed = overview.get("炸板数") or overview.get("failed_limit_up_count")
        if limit_ups and failed and limit_ups > failed:
            timing += 2.0
    timing = max(0.0, min(15.0, timing))
    total = round(flow + map_score + core + timing, 1)
    if total >= 68 and core >= 12:
        stance = "重点进攻"
    elif total >= 50:
        stance = "积极观察"
    elif total >= 32:
        stance = "跟踪等待"
    else:
        stance = "放弃"
    return {
        "theme": item["theme"],
        "total_score": total,
        "stance": stance,
        "flow_score": round(flow, 1),
        "map_score": round(map_score, 1),
        "core_score": round(core, 1),
        "timing_score": round(timing, 1),
        "news_count": int(item.get("news_count", 0)),
        "red_count": int(item.get("red_count", 0)),
        "kpl_count": kpl_count,
        "failed_count": failed_count,
        "lhb_net_buy": round(lhb_net_buy, 2),
        "core_names": "、".join((item.get("kpl_stocks") or item.get("candidates") or [])[:8]),
        "lhb_stocks": "、".join(item.get("lhb_stocks", [])[:6]),
        "confirm_signal": item.get("confirm") or f"{item['theme']}前排竞价强于板块，容量核心放量不破分时均线。",
        "give_up_signal": item.get("give_up") or f"{item['theme']}核心低开低走、冲高回落，或消息强但板块无量无扩散。",
    }


def classify_market(rows: list[dict[str, Any]], overview: dict[str, float], has_lhb: bool, has_kpl: bool) -> str:
    if not rows:
        return "数据不足"
    top = rows[0]["total_score"]
    strong = sum(1 for row in rows if row["total_score"] >= 50)
    if overview:
        up = overview.get("上涨家数") or overview.get("advancers")
        down = overview.get("下跌家数") or overview.get("decliners")
        if up and down and up < down * 0.7 and top < 55:
            return "防守观察"
    if top >= 68 and strong >= 2 and has_kpl:
        return "局部进攻"
    if top >= 50:
        return "结构性轮动"
    if has_lhb or has_kpl:
        return "弱修复/试错"
    return "信息不足"


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "theme",
        "total_score",
        "stance",
        "flow_score",
        "map_score",
        "core_score",
        "timing_score",
        "news_count",
        "red_count",
        "kpl_count",
        "failed_count",
        "lhb_net_buy",
        "core_names",
        "lhb_stocks",
        "confirm_signal",
        "give_up_signal",
    ]
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def write_markdown(
    path: Path,
    report_date: str,
    market_state: str,
    rows: list[dict[str, Any]],
    top_lhb: list[dict[str, Any]],
    overview: dict[str, float],
    limits: list[str],
) -> None:
    lines = [
        f"# {report_date} A股资金流与明日观察计划",
        "",
        "> 研究用途，非投资建议。",
        "",
        f"## 市场状态：{market_state}",
        "",
        "判断口径：F-M-C-T = Flow资金强度、Map板块集中、Core核心确认、Timing交易时机。",
        "",
    ]
    if overview:
        def show(*names: str) -> str:
            for name in names:
                if name in overview:
                    value = overview[name]
                    return str(int(value)) if float(value).is_integer() else str(value)
            return "暂无"

        def show_with_unit(unit: str, *names: str) -> str:
            value = show(*names)
            return value if value == "暂无" else f"{value}{unit}"

        lines.extend(
            [
                "## 市场宽度快照",
                "",
                f"- 成交额：{show_with_unit('亿元', '两市成交额', '成交额', 'turnover')}",
                f"- 涨跌家数：上涨 {show('上涨家数', 'advancers')} / 下跌 {show('下跌家数', 'decliners')} / 平盘 {show('平盘家数', 'flat_count')}",
                f"- 涨跌停：涨停 {show('涨停数', 'limit_up_count')} / 炸板 {show('炸板数', 'failed_limit_up_count')} / 跌停 {show('跌停数', 'limit_down_count')}",
                f"- 情绪质量：封板率 {show_with_unit('%', '封板率', 'seal_rate')}，炸板率 {show_with_unit('%', '炸板率', 'failed_limit_up_rate')}",
                "",
            ]
        )
    lines.extend(
        [
            "## 主题优先级",
            "",
            "| 排名 | 主题 | 分数 | 动作 | F | M | C | T | 开盘啦 | 龙虎榜净买额 | 核心观察 |",
            "|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---|",
        ]
    )
    for idx, row in enumerate(rows, start=1):
        lines.append(
            f"| {idx} | {row['theme']} | {row['total_score']} | {row['stance']} | "
            f"{row['flow_score']} | {row['map_score']} | {row['core_score']} | {row['timing_score']} | "
            f"{row['kpl_count']} | {row['lhb_net_buy']:.0f} | {row['core_names']} |"
        )
    lines.extend(["", "## 明日执行框架", ""])
    for row in rows[:5]:
        lines.extend(
            [
                f"### {row['theme']}：{row['stance']}",
                "",
                f"- 确认：{row['confirm_signal']}",
                f"- 放弃：{row['give_up_signal']}",
                f"- 观察核心：{row['core_names'] or row['lhb_stocks'] or '等待盘中确认'}",
                "",
            ]
        )
    if top_lhb:
        lines.extend(["## 龙虎榜净买额前列", ""])
        for row in top_lhb[:10]:
            lines.append(f"- {stock_name(row)}：净买额 {lhb_net(row):.0f}，原因：{row.get('上榜原因') or row.get('reason') or ''}")
        lines.append("")
    if limits:
        lines.extend(["## 数据限制", ""])
        lines.extend(f"- {item}" for item in limits)
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Analyze A-share market flow and build next-day sector plan.")
    parser.add_argument("--date", default=date.today().isoformat(), help="Report date, e.g. 2026-06-04.")
    parser.add_argument("--cls-plan", action="append", default=[], help="CLS market plan CSV/JSON. Repeatable.")
    parser.add_argument("--kpl", action="append", default=[], help="KPL/Tushare limit-up CSV/JSON. Repeatable.")
    parser.add_argument("--lhb", action="append", default=[], help="Dragon-tiger CSV/JSON. Repeatable.")
    parser.add_argument("--market", action="append", default=[], help="Optional market overview CSV/JSON. Repeatable.")
    parser.add_argument("--out-dir", default="examples/market/market-flow", help="Output directory.")
    args = parser.parse_args()

    limits: list[str] = []
    themes = read_cls_plan([Path(x) for x in args.cls_plan])
    if not themes:
        themes = {theme: {"theme": theme, "cls_score": 0.0, "news_count": 0.0, "red_count": 0.0, "sectors": set(), "candidates": [], "confirm": "", "give_up": ""} for theme in THEME_KEYWORDS}
        limits.append("未提供财联社主题计划，报告只保留资金验证框架。")

    kpl_rows = read_kpl([Path(x) for x in args.kpl])
    if not kpl_rows:
        limits.append("未提供开盘啦/涨停数据，连板与封板确认不足。")
    attach_kpl(themes, kpl_rows)

    lhb_rows = read_lhb([Path(x) for x in args.lhb])
    if not lhb_rows:
        limits.append("未提供龙虎榜数据，核心资金验证不足。")
    top_lhb = attach_lhb(themes, lhb_rows)

    overview = read_market_overview([Path(x) for x in args.market])
    if not overview:
        limits.append("未提供全市场成交额、涨跌家数、炸板率等宽度数据，市场状态按题材证据保守判断。")

    scored = sorted((score_theme(item, overview) for item in themes.values()), key=lambda row: row["total_score"], reverse=True)
    market_state = classify_market(scored, overview, bool(lhb_rows), bool(kpl_rows))

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    csv_path = out_dir / f"{args.date}-market-flow.csv"
    md_path = out_dir / f"{args.date}-market-flow.md"
    write_csv(csv_path, scored)
    write_markdown(md_path, args.date, market_state, scored, top_lhb, overview, limits)

    print(json.dumps({"status": "ok", "market_state": market_state, "themes": len(scored), "csv": str(csv_path), "markdown": str(md_path)}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
