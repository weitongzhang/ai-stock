#!/usr/bin/env python3
"""Validate completeness and cross-reference integrity of the knowledge base."""

from __future__ import annotations

import importlib.util
import hashlib
import json
import re
from collections import Counter
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
SEARCH_SCRIPT = Path(__file__).with_name("search_knowledge.py")
SPEC = importlib.util.spec_from_file_location("search_knowledge", SEARCH_SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(MODULE)

ID_RE = re.compile(r"\bMX-\d{4}\b")
EXPECTED_ENTRIES = 351
EXPECTED_EXCLUDED = {"MX-0002", "MX-0240", "MX-0243", "MX-0340"}
DATE_RE = re.compile(r"^20\d{2}年\d{1,2}月\d{1,2}日(?:\d{1,2}点)?$")


def main() -> None:
    entries = MODULE.load_entries(SKILL_DIR)
    ids = [entry["id"] for entry in entries]
    counts = Counter(ids)
    failures = []

    if len(entries) != EXPECTED_ENTRIES:
        failures.append(f"expected {EXPECTED_ENTRIES} catalog entries, found {len(entries)}")
    duplicates = sorted(entry_id for entry_id, count in counts.items() if count != 1)
    if duplicates:
        failures.append(f"duplicate catalog ids: {', '.join(duplicates)}")

    all_ids = set(ids)
    expected_ids = {f"MX-{number:04d}" for number in range(1, EXPECTED_ENTRIES + 1)}
    missing = sorted(expected_ids - all_ids)
    if missing:
        failures.append(f"missing catalog ids: {', '.join(missing)}")
    malformed_dates = sorted(
        f"{entry['id']}={entry['date']}" for entry in entries if not DATE_RE.fullmatch(entry["date"])
    )
    if malformed_dates:
        failures.append(f"malformed or missing dates: {', '.join(malformed_dates)}")

    exclusions = SKILL_DIR / "references" / "knowledge" / "manual-review-exclusions.md"
    exclusion_ids = set(ID_RE.findall(exclusions.read_text(encoding="utf-8")))
    if exclusion_ids != EXPECTED_EXCLUDED:
        failures.append(
            "manual exclusions differ: "
            f"expected {sorted(EXPECTED_EXCLUDED)}, found {sorted(exclusion_ids)}"
        )

    knowledge_dir = SKILL_DIR / "references" / "knowledge"
    checked_refs = 0
    for path in knowledge_dir.glob("*.md"):
        if path.name == "manual-review-exclusions.md":
            continue
        referenced = set(ID_RE.findall(path.read_text(encoding="utf-8")))
        invalid = sorted(referenced - all_ids)
        checked_refs += len(referenced)
        if invalid:
            failures.append(f"{path.name} references missing ids: {', '.join(invalid)}")

    sources_dir = SKILL_DIR / "references" / "sources"
    manifest = json.loads((sources_dir / "manifest.json").read_text(encoding="utf-8"))
    checked_sources = 0
    for item in manifest.get("files", []):
        path = sources_dir / item["path"]
        if not path.is_file():
            failures.append(f"source file missing: {item['path']}")
            continue
        checked_sources += 1
        if path.stat().st_size != item["bytes"]:
            failures.append(f"source size changed: {item['path']}")
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != item["sha256"]:
            failures.append(f"source hash changed: {item['path']}")

    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        raise SystemExit(1)
    print(
        f"PASS: {len(entries)} unique entries, {checked_refs} valid cross-references, "
        f"{len(exclusion_ids)} isolated entries, {checked_sources} verified source files"
    )


if __name__ == "__main__":
    main()
