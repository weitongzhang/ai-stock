#!/usr/bin/env python
"""First-pass A-share sentiment and event-risk checker."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import locale
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


DEFAULT_RUN_PY = Path(r"C:\Users\wtzhang12\.codex\skills\ftshare-market-data\run.py")


KEYWORDS = {
    "red": [
        "立案", "证监会立案", "行政处罚", "纪律处分", "违法违规", "信披违法", "信息披露违法",
        "误导性陈述", "虚假记载", "财务造假", "退市", "ST", "暂停上市", "无法表示意见",
        "债务违约", "流动性危机", "破产", "重整", "银行账户冻结", "查封", "留置",
        "重大诉讼", "巨额亏损", "净资产为负",
    ],
    "orange": [
        "异动公告", "异常波动", "澄清", "问询函", "关注函", "监管工作函", "预亏",
        "业绩下滑", "减值", "减持", "限售解禁", "质押", "停牌", "不确定性",
        "媒体报道", "风险提示",
    ],
    "green": [
        "中标", "重大合同", "订单", "回购", "增持", "预增", "扭亏", "股权激励",
        "新产品", "新技术", "政策支持", "涨价", "产能释放", "海外项目", "交付",
    ],
}

SEVERITY_ORDER = {"red": 3, "orange": 2, "green": 1, "neutral": 0}


@dataclass
class Evidence:
    label: str
    keyword: str
    source: str
    title: str
    text: str
    url: str = ""
    publish_time: str = ""


def run_ftshare(run_py: Path, subskill: str, args: list[str]) -> Any:
    raw = subprocess.check_output(["python", str(run_py), subskill] + args)
    for encoding in ("utf-8", locale.getpreferredencoding(False), "gbk"):
        try:
            text = raw.decode(encoding)
            break
        except UnicodeDecodeError:
            continue
    else:
        text = raw.decode("utf-8", errors="replace")
    return json.loads(text)


def normalize_space(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def scan_text(text: str, source: str, title: str, url: str = "", publish_time: str = "") -> list[Evidence]:
    found: list[Evidence] = []
    combined = normalize_space(text)
    for label, words in KEYWORDS.items():
        for word in words:
            if word in combined:
                snippet_start = max(combined.find(word) - 45, 0)
                snippet = combined[snippet_start: snippet_start + 140]
                found.append(Evidence(label, word, source, title, snippet, url, publish_time))
    return found


def classify(evidence: list[Evidence]) -> str:
    if not evidence:
        return "neutral"
    return max(evidence, key=lambda item: SEVERITY_ORDER[item.label]).label


def label_cn(label: str) -> str:
    return {
        "red": "红色风险",
        "orange": "橙色风险",
        "green": "正向事件",
        "neutral": "中性/未发现强信号",
    }.get(label, label)


def action_guidance(label: str) -> str:
    if label == "red":
        return "降低或否决普通技术买点权重；反弹先按风险释放或超跌反弹处理；不建议亏损摊平。"
    if label == "orange":
        return "保留观察，但要求更强价格确认；突破必须有后续跟随；仓位低于普通技术信号。"
    if label == "green":
        return "提供观察理由，但不等于买点；必须等待价格突破、回踩不破或趋势跟随确认。"
    return "未发现强方向事件；以价格行为、成交量和关键位为主。"


def build_report(symbol: str, name: str, info: dict[str, Any], news: list[dict[str, Any]], evidence: list[Evidence]) -> str:
    label = classify(evidence)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = [
        f"# {name or symbol} 舆情监控报告",
        "",
        f"- 生成时间：{now}",
        f"- 标的：{symbol}" + (f" / {name}" if name else ""),
        f"- 综合标签：{label_cn(label)}",
        f"- 交易影响：{action_guidance(label)}",
        "",
        "## 个股基础摘要",
        "",
    ]

    for key, label_name in [
        ("symbol_name", "名称"),
        ("close", "最新收盘"),
        ("change_rate", "涨跌幅"),
        ("pe_ttm", "PE TTM"),
        ("pb", "PB"),
        ("roe_ttm", "ROE TTM"),
    ]:
        if key in info:
            value = info[key]
            if key == "change_rate":
                try:
                    value = f"{float(value) * 100:.2f}%"
                except Exception:
                    pass
            lines.append(f"- {label_name}：{value}")

    intro = normalize_space(str(info.get("introduction", "")))
    if intro:
        lines += ["", "## 基础信息风险扫描", ""]
        intro_hits = [item for item in evidence if item.source == "stock-security-info"]
        if intro_hits:
            for item in intro_hits[:12]:
                lines.append(f"- [{label_cn(item.label)}] `{item.keyword}`：{item.text}")
        else:
            lines.append("- 未在基础信息文本中发现强风险关键词。")

    lines += ["", "## 新闻扫描", ""]
    if news:
        for item in news[:10]:
            title = normalize_space(str(item.get("title") or ""))
            source = item.get("source_site") or item.get("media_name") or "未知来源"
            publish_time = item.get("publish_time") or ""
            url = item.get("article_url") or ""
            lines.append(f"- {publish_time} [{source}] {title}" + (f" ({url})" if url else ""))
    else:
        lines.append("- 未返回相关新闻。")

    news_hits = [item for item in evidence if item.source != "stock-security-info"]
    lines += ["", "## 命中证据", ""]
    if news_hits:
        for item in news_hits[:20]:
            lines.append(f"- [{label_cn(item.label)}] `{item.keyword}` | {item.publish_time} {item.title}：{item.text}")
    else:
        lines.append("- 新闻文本未命中强风险/正向关键词。")

    lines += [
        "",
        "## 与技术交易结合",
        "",
        "- 先用舆情标签确定风险底色，再看价格行为是否确认。",
        "- 红色风险下，普通突破、H1/H2、缩量止跌都要降权。",
        "- 橙色风险下，只接受有成交量和后续跟随的信号。",
        "- 正向事件下，若价格没有突破或回踩确认，只加入观察池。",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="A-share sentiment/event-risk checker")
    parser.add_argument("--symbol", required=True, help="A-share symbol, e.g. 600481.SH")
    parser.add_argument("--name", default="", help="Stock name for news query")
    parser.add_argument("--query", default="", help="Override news search query")
    parser.add_argument("--limit", type=int, default=8, help="News result limit")
    parser.add_argument("--year", type=int, default=datetime.now().year, help="News search year")
    parser.add_argument("--run-py", default=str(DEFAULT_RUN_PY), help="FTShare run.py path")
    parser.add_argument("--out-dir", default="", help="Directory to write Markdown report")
    parser.add_argument("--skip-news", action="store_true", help="Only scan stock-security-info")
    args = parser.parse_args()

    run_py = Path(args.run_py)
    info = run_ftshare(run_py, "stock-security-info", ["--symbol", args.symbol])
    query = args.query or args.name or str(info.get("symbol_name") or args.symbol)

    news: list[dict[str, Any]] = []
    if not args.skip_news:
        news = run_ftshare(run_py, "semantic-search-news", ["--query", query, "--limit", str(args.limit), "--year", str(args.year)])

    evidence: list[Evidence] = []
    evidence.extend(scan_text(str(info.get("introduction", "")), "stock-security-info", "个股基础信息"))
    for item in news:
        text = " ".join(str(item.get(key) or "") for key in ("title", "summary", "content"))
        evidence.extend(scan_text(
            text,
            str(item.get("source_site") or item.get("media_name") or "news"),
            str(item.get("title") or ""),
            str(item.get("article_url") or ""),
            str(item.get("publish_time") or ""),
        ))

    report = build_report(args.symbol, args.name or str(info.get("symbol_name") or ""), info, news, evidence)
    print(report)

    if args.out_dir:
        out_dir = Path(args.out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        safe_name = re.sub(r"[^0-9A-Za-z._-]+", "-", f"{args.symbol}-{args.name or query}").strip("-")
        output = out_dir / f"{datetime.now().strftime('%Y-%m-%d')}-{safe_name}-sentiment.md"
        output.write_text(report, encoding="utf-8")
        print(f"\n[written] {output}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
