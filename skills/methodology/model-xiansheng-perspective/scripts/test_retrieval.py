#!/usr/bin/env python3
"""Regression tests for the local knowledge retriever."""

from __future__ import annotations

import importlib.util
from pathlib import Path


SCRIPT = Path(__file__).with_name("search_knowledge.py")
SPEC = importlib.util.spec_from_file_location("search_knowledge", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(MODULE)


CASES = [
    ("从市场中来 到市场中去", {"MX-0013"}, 3),
    ("追高怎么判断", {"MX-0147"}, 3),
    ("低位看逻辑 高位看图形", {"MX-0177"}, 3),
    ("交易系统完整性 层次性", {"MX-0022"}, 3),
    ("侧翼战 共识", {"MX-0091", "MX-0095"}, 5),
    ("股票被套怎么办", {"MX-0207"}, 3),
    ("商业航天 可回收火箭", {"MX-0201", "MX-0208", "MX-0244"}, 5),
    ("逻辑弱化 逻辑不在 卖出", {"MX-0219", "MX-0220"}, 5),
    ("买卖 两点论 最坏打算", {"MX-0024"}, 3),
    ("投资 历史感", {"MX-0030"}, 3),
]


def main() -> None:
    skill_dir = SCRIPT.resolve().parents[1]
    entries = MODULE.load_entries(skill_dir)
    failures = []
    for query, expected, top_n in CASES:
        results = MODULE.search(entries, query, top_n, None)
        found = {result["id"] for result in results}
        if not expected & found:
            failures.append((query, sorted(expected), [result["id"] for result in results]))
    by_id = {entry["id"]: entry for entry in entries}
    if not by_id["MX-0135"]["attribution"].startswith("较高"):
        failures.append(("归因：语录合集", ["较高"], [by_id["MX-0135"]["attribution"]]))
    if not by_id["MX-0244"]["attribution"].startswith(("中高", "中低")):
        failures.append(("归因：集大成材料", ["中高或中低"], [by_id["MX-0244"]["attribution"]]))
    excluded_results = MODULE.search(entries, "粉丝翻30倍 暗示个股", 10, None)
    if {result["id"] for result in excluded_results} & MODULE.EXCLUDED_IDS:
        failures.append(("隔离条目默认隐藏", [], [result["id"] for result in excluded_results]))
    included_results = MODULE.search(entries, "粉丝翻30倍 暗示个股", 10, None, True)
    if not {result["id"] for result in included_results} & MODULE.EXCLUDED_IDS:
        failures.append(("隔离条目显式召回", sorted(MODULE.EXCLUDED_IDS), []))
    unrelated_results = MODULE.search(entries, "火星海洋考古学", 10, None)
    if unrelated_results:
        failures.append(("无关问题返回空结果", [], [result["id"] for result in unrelated_results]))
    dated_results = MODULE.search(entries, "商业航天 三月下旬 即将见底", 5, None)
    dated_by_id = {result["id"]: result for result in dated_results}
    if dated_by_id.get("MX-0241", {}).get("context_date") != "2026年4月14日15点":
        failures.append(
            (
                "长条目片段日期",
                ["2026年4月14日15点"],
                [dated_by_id.get("MX-0241", {}).get("context_date", "missing")],
            )
        )
    if failures:
        for query, expected, found in failures:
            print(f"FAIL {query}: expected one of {expected}, found {found}")
        raise SystemExit(1)
    print(f"PASS: {len(CASES)}/{len(CASES)} retrieval cases + 6 safety checks")


if __name__ == "__main__":
    main()
