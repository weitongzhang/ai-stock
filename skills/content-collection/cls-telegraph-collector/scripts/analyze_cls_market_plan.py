#!/usr/bin/env python3
"""Turn collected CLS telegraph items into a next-day A-share theme plan."""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


THEME_RULES = [
    {
        "theme": "AI算力/数据中心",
        "keywords": ["AI", "人工智能", "算力", "数据中心", "服务器", "液冷", "光模块", "光通信", "光纤", "光缆", "AIDC", "算电协同", "智能体", "Agent"],
        "sectors": ["算力", "光模块", "服务器", "液冷", "电力配套", "数据中心"],
        "candidates": ["中际旭创", "新易盛", "天孚通信", "工业富联", "浪潮信息", "润泽科技", "曙光数创"],
    },
    {
        "theme": "半导体/国产替代",
        "keywords": ["半导体", "芯片", "出口管制", "先进封装", "EDA", "光刻", "晶圆", "存储", "HBM", "设备", "材料"],
        "sectors": ["半导体设备", "材料", "先进封装", "存储芯片", "国产替代"],
        "candidates": ["中芯国际", "北方华创", "中微公司", "华海清科", "拓荆科技", "寒武纪", "兆易创新"],
    },
    {
        "theme": "机器人/具身智能",
        "keywords": ["机器人", "具身智能", "人形机器人", "减速器", "伺服", "传感器", "灵巧手", "宇树", "特斯拉机器人"],
        "sectors": ["人形机器人", "减速器", "伺服系统", "传感器", "执行器"],
        "candidates": ["拓普集团", "三花智控", "鸣志电器", "绿的谐波", "中大力德", "双环传动", "柯力传感"],
    },
    {
        "theme": "6G/通信/卫星互联网",
        "keywords": ["6G", "通信", "卫星互联网", "商业航天", "低轨", "基站", "射频", "无线感知", "终端", "操作系统"],
        "sectors": ["6G", "通信设备", "卫星互联网", "商业航天", "射频器件"],
        "candidates": ["中兴通讯", "中国卫通", "上海瀚讯", "华力创通", "铖昌科技", "信维通信", "通宇通讯"],
    },
    {
        "theme": "电力/电网/绿电",
        "keywords": ["电力", "绿电", "电网", "储能", "特高压", "变压器", "电价", "发电侧", "新能源消纳", "虚拟电厂"],
        "sectors": ["电力", "电网设备", "储能", "特高压", "虚拟电厂"],
        "candidates": ["华电国际", "国电电力", "许继电气", "平高电气", "中国西电", "阳光电源", "东方电子"],
    },
    {
        "theme": "能源/煤炭/油气",
        "keywords": ["石油", "原油", "柴油", "油价", "煤炭", "天然气", "中东", "OPEC", "库存", "出口禁令"],
        "sectors": ["油气", "煤炭", "化工", "航运", "能源安全"],
        "candidates": ["中国石油", "中国海油", "中国石化", "陕西煤业", "中国神华", "中远海能", "招商轮船"],
    },
    {
        "theme": "低空经济/商业航天",
        "keywords": ["低空经济", "eVTOL", "无人机", "通航", "商业航天", "火箭", "卫星", "空管"],
        "sectors": ["低空经济", "无人机", "商业航天", "卫星应用"],
        "candidates": ["宗申动力", "万丰奥威", "中信海直", "航天电子", "航天宏图", "纵横股份"],
    },
    {
        "theme": "消费/旅游/短剧",
        "keywords": ["消费", "旅游", "零售", "白酒", "食品", "短剧", "影视", "游戏", "暑期", "促消费"],
        "sectors": ["消费", "旅游酒店", "传媒游戏", "短剧", "零售"],
        "candidates": ["中国中免", "锦江酒店", "王府井", "岩山科技", "中文在线", "恺英网络"],
    },
]

MARKET_KEYWORDS = ["涨停", "跌停", "封板", "炸板", "连板", "成交额", "收评", "午评", "竞价", "龙虎榜"]
POLICY_KEYWORDS = ["国务院", "发改委", "工信部", "商务部", "财政部", "央行", "证监会", "政策", "试点", "规划", "通知", "关税", "反倾销"]
RISK_KEYWORDS = ["监管", "禁令", "制裁", "调查", "下跌", "跌破", "冲突", "风险", "退潮", "缩量", "补跌"]


def clean_text(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def read_items(path: Path) -> list[dict[str, Any]]:
    if path.suffix.lower() == ".json":
        data = json.loads(path.read_text(encoding="utf-8"))
        rows = data.get("items")
        if isinstance(rows, list):
            for row in rows:
                row["source_file"] = str(path)
            return [row for row in rows if isinstance(row, dict)]
        roll = ((data.get("data") or {}).get("roll_data") or [])
        return [{"source_file": str(path), **normalize_raw(row)} for row in roll if isinstance(row, dict)]

    rows: list[dict[str, Any]] = []
    with path.open(newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            row["source_file"] = str(path)
            rows.append(row)
    return rows


def normalize_raw(raw: dict[str, Any]) -> dict[str, Any]:
    content = clean_text(raw.get("content") or raw.get("brief") or raw.get("title"))
    title = clean_text(raw.get("title")) or title_from_content(content)
    return {
        "id": str(raw.get("id") or ""),
        "time": ts_to_time(raw.get("ctime")),
        "title": title,
        "content": content,
        "level": clean_text(raw.get("level")),
        "shareurl": clean_text(raw.get("shareurl")),
        "category": clean_text(raw.get("category")),
        "raw": raw,
    }


def ts_to_time(value: Any) -> str:
    try:
        return datetime.fromtimestamp(int(value)).strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return ""


def title_from_content(content: str) -> str:
    match = re.match(r"^【([^】]{2,80})】", content)
    if match:
        return match.group(1)
    return re.split(r"[。！？]", content, maxsplit=1)[0][:80]


def dedupe_items(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    result: list[dict[str, Any]] = []
    for item in items:
        key = clean_text(item.get("id")) or clean_text(item.get("title")) + clean_text(item.get("content"))[:80]
        if key in seen:
            continue
        seen.add(key)
        result.append(item)
    return result


def classify_event(text: str) -> str:
    if any(k in text for k in MARKET_KEYWORDS):
        return "盘面验证"
    if any(k in text for k in POLICY_KEYWORDS):
        return "政策催化"
    if any(k in text for k in RISK_KEYWORDS):
        return "风险事件"
    return "产业消息"


def score_item(item: dict[str, Any], matched_keywords: list[str]) -> int:
    text = f"{item.get('title', '')} {item.get('content', '')}"
    raw = item.get("raw") if isinstance(item.get("raw"), dict) else {}
    score = 0
    if clean_text(item.get("level")).upper() in {"A", "B"}:
        score += 4
    if "red" in item.get("source_file", "").lower():
        score += 3
    if any(k in text for k in POLICY_KEYWORDS):
        score += 3
    if any(k in text for k in MARKET_KEYWORDS):
        score += 2
    score += min(len(matched_keywords), 4)
    if raw.get("stock_list"):
        score += 2
    if raw.get("subjects"):
        score += 1
    try:
        score += min(int(item.get("image_count") or 0), 2)
    except ValueError:
        pass
    return score


def keyword_in_text(keyword: str, text: str) -> bool:
    if re.fullmatch(r"[A-Za-z0-9]+", keyword):
        return re.search(rf"(?<![A-Za-z0-9]){re.escape(keyword)}(?![A-Za-z0-9])", text, re.I) is not None
    return keyword.lower() in text.lower()


def themes_for_item(item: dict[str, Any]) -> list[dict[str, Any]]:
    text = f"{item.get('title', '')} {item.get('content', '')}"
    matched: list[dict[str, Any]] = []
    for rule in THEME_RULES:
        keywords = [kw for kw in rule["keywords"] if keyword_in_text(kw, text)]
        if keywords:
            matched.append({"rule": rule, "keywords": keywords, "item_score": score_item(item, keywords)})
    return matched


def raw_subjects(item: dict[str, Any]) -> str:
    raw = item.get("raw") if isinstance(item.get("raw"), dict) else {}
    subjects = raw.get("subjects") or []
    names = [clean_text(s.get("subject_name")) for s in subjects if isinstance(s, dict) and s.get("subject_name")]
    return "、".join(names)


def raw_stocks(item: dict[str, Any]) -> str:
    raw = item.get("raw") if isinstance(item.get("raw"), dict) else {}
    stocks = raw.get("stock_list") or []
    names: list[str] = []
    for stock in stocks:
        if isinstance(stock, dict):
            names.append(clean_text(stock.get("name") or stock.get("stock_name") or stock.get("secu_name") or stock.get("code")))
    return "、".join(n for n in names if n)


def build_theme_rows(items: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    buckets: dict[str, dict[str, Any]] = {}
    evidence_rows: list[dict[str, Any]] = []
    for item in items:
        for match in themes_for_item(item):
            rule = match["rule"]
            theme = rule["theme"]
            bucket = buckets.setdefault(
                theme,
                {
                    "theme": theme,
                    "score": 0,
                    "news_count": 0,
                    "red_count": 0,
                    "policy_count": 0,
                    "market_count": 0,
                    "keywords": set(),
                    "sectors": rule["sectors"],
                    "candidates": rule["candidates"],
                    "evidence": [],
                },
            )
            event_type = classify_event(f"{item.get('title', '')} {item.get('content', '')}")
            bucket["score"] += match["item_score"]
            bucket["news_count"] += 1
            bucket["red_count"] += 1 if clean_text(item.get("level")).upper() in {"A", "B"} or "red" in item.get("source_file", "").lower() else 0
            bucket["policy_count"] += 1 if event_type == "政策催化" else 0
            bucket["market_count"] += 1 if event_type == "盘面验证" else 0
            bucket["keywords"].update(match["keywords"])
            bucket["evidence"].append(item)
            evidence_rows.append(
                {
                    "theme": theme,
                    "event_type": event_type,
                    "item_score": match["item_score"],
                    "time": item.get("time", ""),
                    "level": item.get("level", ""),
                    "title": item.get("title", ""),
                    "keywords": "、".join(match["keywords"]),
                    "subjects": raw_subjects(item),
                    "stocks": raw_stocks(item),
                    "shareurl": item.get("shareurl", ""),
                }
            )

    theme_rows: list[dict[str, Any]] = []
    for bucket in buckets.values():
        score = int(bucket["score"])
        if bucket["red_count"] and bucket["policy_count"]:
            stance = "重点观察"
        elif score >= 7:
            stance = "积极跟踪"
        elif bucket["market_count"] and bucket["news_count"] >= 2:
            stance = "盘面验证后参与"
        else:
            stance = "观察为主"
        theme_rows.append(
            {
                "theme": bucket["theme"],
                "score": score,
                "stance": stance,
                "news_count": bucket["news_count"],
                "red_count": bucket["red_count"],
                "policy_count": bucket["policy_count"],
                "market_count": bucket["market_count"],
                "keywords": "、".join(sorted(bucket["keywords"])),
                "sectors": "、".join(bucket["sectors"]),
                "candidates": "、".join(bucket["candidates"]),
                "confirm_signal": confirm_signal(bucket["theme"]),
                "give_up_signal": give_up_signal(bucket["theme"]),
                "position_plan": position_plan(stance),
                "evidence": bucket["evidence"],
            }
        )
    theme_rows.sort(key=lambda row: (row["score"], row["red_count"], row["policy_count"]), reverse=True)
    evidence_rows.sort(key=lambda row: int(row["item_score"]), reverse=True)
    return theme_rows, evidence_rows


def confirm_signal(theme: str) -> str:
    return f"{theme}前排竞价/开盘强于板块，容量核心放量不破分时均线，后排出现扩散。"


def give_up_signal(theme: str) -> str:
    return f"{theme}核心低开低走、冲高回落，或消息强但板块无量无扩散。"


def position_plan(stance: str) -> str:
    if stance == "重点观察":
        return "强反馈可小仓试错，确认扩散后再加；弱反馈不追。"
    if stance == "积极跟踪":
        return "只做前排或容量核心，等待分歧承接。"
    if stance == "盘面验证后参与":
        return "开盘先观察，只有核心确认后再考虑。"
    return "加入观察池，不作为首选进攻方向。"


def write_outputs(theme_rows: list[dict[str, Any]], evidence_rows: list[dict[str, Any]], out_dir: Path) -> tuple[Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    date = datetime.now().strftime("%Y-%m-%d")
    csv_path = out_dir / f"{date}-cls-market-plan.csv"
    md_path = out_dir / f"{date}-cls-market-plan.md"

    fields = ["theme", "score", "stance", "news_count", "red_count", "policy_count", "market_count", "keywords", "sectors", "candidates", "confirm_signal", "give_up_signal", "position_plan"]
    with csv_path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in theme_rows:
            writer.writerow({field: row.get(field, "") for field in fields})

    lines = [
        f"# {date} CLS Market Plan",
        "",
        "用途：把财联社普通/加红电报转成次日板块与个股观察计划。仅供研究复盘，不构成投资建议。",
        "",
        "## 结论",
        "",
    ]
    if not theme_rows:
        lines.extend(["未匹配到高价值主题。", ""])
    else:
        for idx, row in enumerate(theme_rows[:5], 1):
            lines.append(f"{idx}. {row['theme']}：{row['stance']}，分数 {row['score']}，关键词：{row['keywords'] or '-'}")
        lines.append("")

    lines.extend(["## 主题计划", ""])
    for row in theme_rows:
        lines.extend(
            [
                f"### {row['theme']} [{row['stance']}]",
                "",
                f"- 催化强度：{row['score']}，消息 {row['news_count']} 条，加红 {row['red_count']} 条，政策 {row['policy_count']} 条，盘面验证 {row['market_count']} 条",
                f"- 映射板块：{row['sectors']}",
                f"- 候选观察：{row['candidates']}",
                f"- 明日确认：{row['confirm_signal']}",
                f"- 放弃条件：{row['give_up_signal']}",
                f"- 仓位计划：{row['position_plan']}",
                "",
                "证据：",
            ]
        )
        for item in row["evidence"][:4]:
            lines.append(f"- {item.get('time') or '-'} {item.get('title') or '-'}")
        lines.append("")

    lines.extend(["## 消息证据表", ""])
    lines.append("| 主题 | 类型 | 分数 | 时间 | 标题 | 关键词 |")
    lines.append("|---|---:|---:|---|---|---|")
    for row in evidence_rows[:40]:
        title = str(row["title"]).replace("|", "/")
        lines.append(f"| {row['theme']} | {row['event_type']} | {row['item_score']} | {row['time']} | {title} | {row['keywords']} |")
    lines.extend(
        [
            "",
            "## 使用纪律",
            "",
            "- 消息只负责建立候选池，不能替代盘面确认。",
            "- 优先选择核心、前排、容量中军，回避低地位跟风。",
            "- 强消息但无板块扩散时只观察。",
            "- 判断错误时用仓位控制损失，先计划、后执行、再复盘。",
        ]
    )
    md_path.write_text("\n".join(lines), encoding="utf-8")
    return csv_path, md_path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", action="append", required=True, help="Collected CLS JSON/CSV file; repeatable")
    parser.add_argument("--out-dir", default="cls-market-plan", help="Output directory")
    args = parser.parse_args()

    items: list[dict[str, Any]] = []
    for value in args.input:
        items.extend(read_items(Path(value)))
    items = dedupe_items(items)
    theme_rows, evidence_rows = build_theme_rows(items)
    csv_path, md_path = write_outputs(theme_rows, evidence_rows, Path(args.out_dir))
    print(json.dumps({"themes": len(theme_rows), "items": len(items), "csv": str(csv_path), "markdown": str(md_path)}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
