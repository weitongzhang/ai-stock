#!/usr/bin/env python3
"""Validate catalog IDs, required fields, and topic coverage."""

from __future__ import annotations

import importlib.util
from collections import Counter
from pathlib import Path


SCRIPT = Path(__file__).with_name("search_knowledge.py")
SPEC = importlib.util.spec_from_file_location("search_knowledge", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(MODULE)


def main() -> None:
    entries = MODULE.load_entries(SCRIPT.resolve().parents[1])
    failures = []
    counts = Counter(entry["id"] for entry in entries)
    duplicates = sorted(entry_id for entry_id, count in counts.items() if count > 1)
    if duplicates:
        failures.append(f"重复ID: {duplicates}")
    for entry in entries:
        for field in ("source", "topics", "attribution", "text"):
            if not entry[field].strip():
                failures.append(f"{entry['id']} 缺少 {field}")
    required_topics = {"主线", "龙头", "换手", "盘子", "月K", "周K", "情绪周期", "退出"}
    all_topics = " ".join(entry["topics"] for entry in entries)
    missing = sorted(topic for topic in required_topics if topic not in all_topics)
    if missing:
        failures.append(f"缺少主题: {missing}")
    if failures:
        print("\n".join(f"FAIL: {failure}" for failure in failures))
        raise SystemExit(1)
    print(f"PASS: {len(entries)} entries, unique IDs, required fields and topic coverage")


if __name__ == "__main__":
    main()
