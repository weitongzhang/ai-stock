#!/usr/bin/env python3
"""Search the Chen Xiaoqun perspective high-fidelity knowledge catalog."""

from __future__ import annotations

import argparse
import json
import re
from math import ceil
from pathlib import Path


BLOCK_RE = re.compile(r"^## (CX-\d{4}) · (.+?)\n(.*?)(?=^## CX-\d{4} · |\Z)", re.MULTILINE | re.DOTALL)
FIELD_RE = re.compile(r"^- (来源|主题|归因置信度)：(.+)$", re.MULTILINE)
STOPWORDS = {"陈小群", "怎么看", "怎么", "如何", "判断", "分析", "一下", "这个", "股票", "板块"}


def terms(query: str) -> list[str]:
    normalized = query.lower()
    for stopword in sorted(STOPWORDS, key=len, reverse=True):
        normalized = normalized.replace(stopword, " ")
    chunks = re.findall(r"[A-Za-z0-9]+|[\u4e00-\u9fff]{2,}", normalized)
    result = []
    for chunk in chunks:
        result.append(chunk)
        if re.fullmatch(r"[\u4e00-\u9fff]{4,}", chunk):
            result.extend(chunk[index : index + 2] for index in range(len(chunk) - 1))
    return list(dict.fromkeys(result))


def load_entries(skill_dir: Path) -> list[dict]:
    entries = []
    catalog = skill_dir / "references" / "knowledge" / "catalog"
    for path in sorted(catalog.glob("*.md")):
        for match in BLOCK_RE.finditer(path.read_text(encoding="utf-8")):
            entry_id, title, body = match.groups()
            fields = dict(FIELD_RE.findall(body))
            entries.append(
                {
                    "id": entry_id,
                    "title": title,
                    "source": fields.get("来源", ""),
                    "topics": fields.get("主题", ""),
                    "attribution": fields.get("归因置信度", ""),
                    "text": body.split("\n\n", 1)[-1].strip(),
                    "catalog": path.name,
                }
            )
    return entries


def score(entry: dict, query_terms: list[str]) -> tuple[int, list[str]]:
    title, topics, text = (entry[key].lower() for key in ("title", "topics", "text"))
    matched, total = [], 0
    for term in query_terms:
        hits = (title.count(term), topics.count(term), text.count(term))
        if any(hits):
            matched.append(term)
            total += hits[0] * 12 + hits[1] * 6 + min(hits[2], 8) * 2
            if len(term) >= 4:
                total += 4
    total += len(matched) * 8
    if query_terms and len(matched) == len(query_terms):
        total += 10
    if matched and entry["attribution"].startswith("中高"):
        total += 5
    return total, matched


def excerpt(text: str, matched: list[str], limit: int = 220) -> str:
    plain = re.sub(r"\s+", " ", text).strip()
    positions = [plain.lower().find(term) for term in matched if plain.lower().find(term) >= 0]
    start = max(0, min(positions) - 45) if positions else 0
    result = plain[start : start + limit]
    return ("…" if start else "") + result + ("…" if start + limit < len(plain) else "")


def search(entries: list[dict], query: str, limit: int, topic: str | None = None) -> list[dict]:
    query_terms = terms(query)
    minimum_matches = max(1, ceil(len(query_terms) * 0.20))
    results = []
    for entry in entries:
        if topic and topic.lower() not in entry["topics"].lower():
            continue
        entry_score, matched = score(entry, query_terms)
        if entry_score <= 0 or len(matched) < minimum_matches:
            continue
        result = dict(entry)
        result.update(score=entry_score, matched=matched, excerpt=excerpt(entry["text"], matched))
        results.append(result)
    return sorted(results, key=lambda item: (-item["score"], item["id"]))[:limit]


def main() -> None:
    parser = argparse.ArgumentParser(description="检索陈小群交易视角高保真知识库")
    parser.add_argument("query", nargs="?", default="")
    parser.add_argument("--id", help="直接读取条目编号，例如 CX-0007")
    parser.add_argument("--topic", help="仅检索某个主题")
    parser.add_argument("--limit", type=int, default=6)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    entries = load_entries(Path(__file__).resolve().parents[1])
    results = [entry for entry in entries if entry["id"] == args.id.upper()] if args.id else search(entries, args.query, args.limit, args.topic)
    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
        return
    for result in results:
        print(f"{result['id']} | {result['title']}")
        print(f"主题: {result['topics']} | 归因: {result['attribution']}")
        print(result.get("excerpt", result["text"][:220]))
        print()


if __name__ == "__main__":
    main()
