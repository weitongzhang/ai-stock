#!/usr/bin/env python3
"""Search the model-xiansheng high-fidelity knowledge catalog."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from math import ceil


BLOCK_RE = re.compile(r"^## (MX-\d{4}) · (.+?)\n(.*?)(?=^## MX-\d{4} · |\Z)", re.MULTILINE | re.DOTALL)
FIELD_RE = re.compile(r"^- (日期|来源|主题|归因置信度)：(.+)$", re.MULTILINE)
INLINE_DATE_RE = re.compile(r"20\d{2}年\d{1,2}月\d{1,2}[日号鈤](?:\d{1,2}点)?")
STOPWORDS = {
    "模型先生", "怎么看", "怎么", "怎么办", "如何", "判断", "分析", "一下",
    "这个", "股票", "市场", "观点",
}
ATTRIBUTION_BONUS = {
    "较高": 8,
    "中高": 4,
    "中低": 0,
}
EXCLUDED_IDS = {"MX-0002", "MX-0240", "MX-0243", "MX-0340"}


def terms(query: str) -> list[str]:
    normalized = query.lower()
    for stopword in sorted(STOPWORDS, key=len, reverse=True):
        normalized = normalized.replace(stopword, " ")
    chunks = re.findall(r"[A-Za-z0-9]+|[\u4e00-\u9fff]{2,}", normalized)
    result = []
    for chunk in chunks:
        if chunk in STOPWORDS:
            continue
        result.append(chunk)
        if re.fullmatch(r"[\u4e00-\u9fff]{4,}", chunk):
            result.extend(chunk[index : index + 2] for index in range(len(chunk) - 1))
    return list(dict.fromkeys(result))


def load_entries(skill_dir: Path) -> list[dict]:
    entries = []
    catalog = skill_dir / "references" / "knowledge" / "catalog"
    for path in sorted(catalog.glob("*.md")):
        content = path.read_text(encoding="utf-8")
        for match in BLOCK_RE.finditer(content):
            entry_id, title, body = match.groups()
            fields = dict(FIELD_RE.findall(body))
            text = body.split("\n\n", 1)[-1].strip()
            entries.append(
                {
                    "id": entry_id,
                    "title": title,
                    "date": fields.get("日期", "日期未标注"),
                    "source": fields.get("来源", ""),
                    "topics": fields.get("主题", ""),
                    "attribution": fields.get("归因置信度", ""),
                    "text": text,
                    "catalog": path.name,
                }
            )
    return entries


def score(entry: dict, query_terms: list[str]) -> tuple[int, list[str]]:
    title = entry["title"].lower()
    topics = entry["topics"].lower()
    text = entry["text"].lower()
    matched = []
    total = 0
    for term in query_terms:
        title_hits = title.count(term)
        topic_hits = topics.count(term)
        text_hits = text.count(term)
        if title_hits or topic_hits or text_hits:
            matched.append(term)
            total += title_hits * 12 + topic_hits * 5 + min(text_hits, 8) * 2
            if len(term) >= 4:
                total += 4
    total += len(matched) * 8
    if query_terms and len(matched) == len(query_terms):
        total += 10
    # Attribution adjusts ranking only after a semantic match. Otherwise every
    # high-confidence entry would become a false-positive result.
    if matched:
        for prefix, bonus in ATTRIBUTION_BONUS.items():
            if entry["attribution"].startswith(prefix):
                total += bonus
                break
        if entry["id"] in EXCLUDED_IDS:
            total -= 30
    return total, matched


def excerpt(text: str, matched: list[str], limit: int = 220) -> str:
    plain = re.sub(r"\s+", " ", text).strip()
    positions = [plain.lower().find(term) for term in matched if plain.lower().find(term) >= 0]
    start = max(0, min(positions) - 55) if positions else 0
    result = plain[start : start + limit]
    return ("…" if start else "") + result + ("…" if start + limit < len(plain) else "")


def context_date(text: str, matched: list[str], fallback: str) -> str:
    plain = re.sub(r"\s+", " ", text).strip()
    positions = [plain.lower().find(term) for term in matched if plain.lower().find(term) >= 0]
    position = min(positions) if positions else 0
    preceding = [match.group(0) for match in INLINE_DATE_RE.finditer(plain[: position + 1])]
    if not preceding:
        return fallback
    return preceding[-1].replace("2824年", "2024年").replace("鈤", "日").replace("号", "日")


def search(
    entries: list[dict],
    query: str,
    limit: int,
    topic: str | None,
    include_excluded: bool = False,
) -> list[dict]:
    query_terms = terms(query)
    minimum_matches = max(1, ceil(len(query_terms) * 0.4))
    results = []
    for entry in entries:
        if entry["id"] in EXCLUDED_IDS and not include_excluded:
            continue
        if topic and topic.lower() not in entry["topics"].lower():
            continue
        entry_score, matched = score(entry, query_terms)
        if entry_score <= 0 or len(matched) < minimum_matches:
            continue
        result = dict(entry)
        result["score"] = entry_score
        result["matched"] = matched
        result["excerpt"] = excerpt(entry["text"], matched)
        result["context_date"] = context_date(entry["text"], matched, entry["date"])
        results.append(result)
    return sorted(results, key=lambda item: (-item["score"], item["id"]))[:limit]


def main() -> None:
    parser = argparse.ArgumentParser(description="检索模型先生高保真知识库")
    parser.add_argument("query", nargs="?", default="", help="检索问题或关键词")
    parser.add_argument("--id", help="直接读取条目编号，例如 MX-0135")
    parser.add_argument("--topic", help="仅检索某个主题，例如 交易系统")
    parser.add_argument("--include-excluded", action="store_true", help="包含人工隔离条目")
    parser.add_argument("--limit", type=int, default=8)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    skill_dir = Path(__file__).resolve().parents[1]
    entries = load_entries(skill_dir)
    if args.id:
        results = [entry for entry in entries if entry["id"] == args.id.upper()]
    else:
        results = search(entries, args.query, args.limit, args.topic, args.include_excluded)

    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
        return
    for result in results:
        date_label = result["date"]
        if result.get("context_date") and result["context_date"] != result["date"]:
            date_label += f" | 片段日期: {result['context_date']}"
        print(f"{result['id']} | {date_label} | {result['title']}")
        print(f"主题: {result['topics']} | 归因: {result['attribution']}")
        print(result.get("excerpt", result["text"][:220]))
        print()


if __name__ == "__main__":
    main()
