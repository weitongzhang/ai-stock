#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
from datetime import datetime
from pathlib import Path


FIELDS = [
    "symbol",
    "name",
    "item_type",
    "horizon",
    "status",
    "thesis",
    "key_levels",
    "trigger",
    "invalidation",
    "next_check",
    "notes",
]


def read_watchlist(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDS)
            writer.writeheader()
        return []
    with path.open("r", newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def normalized(row: dict[str, str]) -> dict[str, str]:
    out = {field: (row.get(field) or "").strip() for field in FIELDS}
    out["status"] = out["status"] or "watching"
    out["horizon"] = out["horizon"] or "mid"
    out["item_type"] = out["item_type"] or "stock"
    return out


def write_csv(rows: list[dict[str, str]], path: Path) -> None:
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def section(title: str, rows: list[dict[str, str]]) -> list[str]:
    lines = [f"## {title}", ""]
    if not rows:
        lines.extend(["- None", ""])
        return lines
    for row in rows:
        lines.extend([
            f"### {row['symbol']} {row['name']}".strip(),
            "",
            f"- 类型：{row['item_type']}",
            f"- 周期：{row['horizon']}",
            f"- 状态：{row['status']}",
            f"- 逻辑：{row['thesis'] or '-'}",
            f"- 关键位：{row['key_levels'] or '-'}",
            f"- 触发：{row['trigger'] or '-'}",
            f"- 失效：{row['invalidation'] or '-'}",
            f"- 下次检查：{row['next_check'] or '-'}",
            f"- 备注：{row['notes'] or '-'}",
            "",
        ])
    return lines


def write_report(rows: list[dict[str, str]], out_dir: Path) -> Path:
    date = datetime.now().strftime("%Y-%m-%d")
    out_dir.mkdir(parents=True, exist_ok=True)
    report = out_dir / f"{date}-watchlist-report.md"
    triggered = [r for r in rows if r["status"] == "triggered"]
    short = [r for r in rows if "short" in r["horizon"] and r["status"] not in {"archived", "invalidated"}]
    mid = [r for r in rows if "mid" in r["horizon"] and r["status"] not in {"archived", "invalidated"}]
    long = [r for r in rows if "long" in r["horizon"] and r["status"] not in {"archived", "invalidated"}]
    inactive = [r for r in rows if r["status"] in {"cooldown", "invalidated", "archived"}]

    lines = [f"# {date} Watchlist Tracking Report", ""]
    lines += section("Triggered Today", triggered)
    lines += section("Short-Term Watch", short)
    lines += section("Mid-Term Structure", mid)
    lines += section("Long-Term Thesis", long)
    lines += section("Cooldown / Invalidated / Archived", inactive)
    report.write_text("\n".join(lines), encoding="utf-8")
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Watchlist CSV path")
    parser.add_argument("--out-dir", default="", help="Output directory; defaults to input parent")
    args = parser.parse_args()

    input_path = Path(args.input)
    rows = [normalized(row) for row in read_watchlist(input_path)]
    write_csv(rows, input_path)
    out_dir = Path(args.out_dir) if args.out_dir else input_path.parent
    report = write_report(rows, out_dir)
    print(f"watchlist={input_path}")
    print(f"report={report}")
    print(f"count={len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
