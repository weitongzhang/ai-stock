#!/usr/bin/env python3
"""Regression tests for the Chen Xiaoqun knowledge retriever."""

from __future__ import annotations

import importlib.util
from pathlib import Path


SCRIPT = Path(__file__).with_name("search_knowledge.py")
SPEC = importlib.util.spec_from_file_location("search_knowledge", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(MODULE)

CASES = [
    ("热点上热榜就是主线吗", {"CX-0002", "CX-0003"}, 5),
    ("首板怎么判断龙头", {"CX-0005"}, 4),
    ("高位分歧换手承接", {"CX-0007", "CX-0008", "CX-0009"}, 5),
    ("盘子太大为什么难走龙头", {"CX-0010", "CX-0011"}, 5),
    ("漂亮月K横盘图形", {"CX-0015", "CX-0016"}, 5),
    ("周K连续两周涨幅高度", {"CX-0018", "CX-0019"}, 5),
    ("单阳不破怎么看", {"CX-0022"}, 4),
    ("题材退潮什么时候退出", {"CX-0012", "CX-0020", "CX-0024"}, 5),
]


def main() -> None:
    entries = MODULE.load_entries(SCRIPT.resolve().parents[1])
    failures = []
    for query, expected, top_n in CASES:
        found = {item["id"] for item in MODULE.search(entries, query, top_n)}
        if not expected & found:
            failures.append((query, sorted(expected), sorted(found)))
    if len(entries) != 24:
        failures.append(("知识条目数", ["24"], [str(len(entries))]))
    if MODULE.search(entries, "海洋考古火星土壤", 5):
        failures.append(("无关问题应返回空", [], ["returned results"]))
    if failures:
        for query, expected, found in failures:
            print(f"FAIL {query}: expected one of {expected}, found {found}")
        raise SystemExit(1)
    print(f"PASS: {len(CASES)}/{len(CASES)} retrieval cases + 2 integrity checks")


if __name__ == "__main__":
    main()
