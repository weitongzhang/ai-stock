#!/usr/bin/env python
"""Single entrypoint for the auditable A-share market-flow skill."""

from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
from datetime import date
from pathlib import Path
from typing import Any


SKILL_ROOT = Path(__file__).resolve().parents[1]
WORKSPACE_ROOT = Path(__file__).resolve().parents[4]
CLS_ROOT = WORKSPACE_ROOT / "skills" / "content-collection" / "cls-telegraph-collector" / "scripts"


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the A-share market-flow skill.")
    parser.add_argument("--date", default=date.today().isoformat())
    parser.add_argument("--out-dir", default="examples/market/market-flow-skill")
    parser.add_argument("--input-root", default="examples/market")
    parser.add_argument("--collect", action="store_true", help="Collect live inputs before analysis.")
    parser.add_argument("--offline", action="store_true", help="Use existing inputs only.")
    args = parser.parse_args()

    if args.collect and args.offline:
        parser.error("--collect and --offline are mutually exclusive")

    input_root = WORKSPACE_ROOT / args.input_root
    out_dir = WORKSPACE_ROOT / args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    compact = args.date.replace("-", "")
    steps: list[dict[str, Any]] = []

    if args.collect:
        collect_inputs(args.date, input_root, steps)

    paths = {
        "breadth": input_root / "market-breadth" / f"{args.date}-market-breadth.csv",
        "cls": input_root / "cls-telegraph" / f"{args.date}-cls-telegraph.json",
        "cls_red": input_root / "cls-telegraph-red" / f"{args.date}-cls-telegraph.json",
        "limit_pool": input_root / "limit-pool" / f"{compact}-akshare-limit-pool.csv",
        "dragon_tiger": input_root / "dragon-tiger" / f"{compact}-eastmoney-lhb.csv",
    }
    missing = [str(path.relative_to(WORKSPACE_ROOT)) for path in paths.values() if not path.exists()]
    if missing:
        result = blocked_result(args.date, missing, steps)
        write_result(out_dir, result)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 2

    cls_plan_dir = input_root / "cls-market-plan-skill"
    run_step(
        "analyze-cls-market-plan",
        [
            sys.executable,
            str(CLS_ROOT / "analyze_cls_market_plan.py"),
            "--input",
            str(paths["cls"]),
            "--input",
            str(paths["cls_red"]),
            "--out-dir",
            str(cls_plan_dir),
        ],
        steps,
    )
    cls_plan = cls_plan_dir / f"{args.date}-cls-market-plan.csv"
    market_flow_dir = out_dir / "report"
    run_step(
        "analyze-market-flow",
        [
            sys.executable,
            str(SKILL_ROOT / "scripts" / "analyze_market_flow.py"),
            "--date",
            args.date,
            "--cls-plan",
            str(cls_plan),
            "--kpl",
            str(paths["limit_pool"]),
            "--lhb",
            str(paths["dragon_tiger"]),
            "--market",
            str(paths["breadth"]),
            "--out-dir",
            str(market_flow_dir),
        ],
        steps,
    )
    flow_csv = market_flow_dir / f"{args.date}-market-flow.csv"
    flow_md = market_flow_dir / f"{args.date}-market-flow.md"
    result = audit_result(args.date, paths, flow_csv, flow_md, steps)
    write_result(out_dir, result)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] in {"completed", "degraded"} else 2


def collect_inputs(trade_date: str, input_root: Path, steps: list[dict[str, Any]]) -> None:
    commands = [
        (
            "collect-market-breadth",
            [
                sys.executable,
                str(SKILL_ROOT / "scripts" / "collect_market_breadth.py"),
                "--date",
                trade_date,
                "--history-days",
                "5",
                "--out-dir",
                str(input_root / "market-breadth"),
            ],
        ),
        (
            "collect-market-evidence",
            [
                sys.executable,
                str(SKILL_ROOT / "scripts" / "collect_market_evidence.py"),
                "--date",
                trade_date,
                "--out-dir",
                str(input_root),
            ],
        ),
        (
            "collect-cls",
            [
                sys.executable,
                str(CLS_ROOT / "collect_cls_telegraph.py"),
                "--limit",
                "50",
                "--out-dir",
                str(input_root / "cls-telegraph"),
            ],
        ),
        (
            "collect-cls-red",
            [
                sys.executable,
                str(CLS_ROOT / "collect_cls_telegraph.py"),
                "--category",
                "red",
                "--limit",
                "50",
                "--out-dir",
                str(input_root / "cls-telegraph-red"),
            ],
        ),
    ]
    for name, command in commands:
        run_step(name, command, steps, allow_failure=True)


def run_step(name: str, command: list[str], steps: list[dict[str, Any]], allow_failure: bool = False) -> None:
    completed = subprocess.run(command, cwd=WORKSPACE_ROOT, text=True, capture_output=True, check=False)
    step = {
        "name": name,
        "status": "completed" if completed.returncode == 0 else "failed",
        "returncode": completed.returncode,
        "stdout": completed.stdout.strip(),
        "stderr": completed.stderr.strip(),
    }
    steps.append(step)
    if completed.returncode != 0 and not allow_failure:
        raise RuntimeError(f"{name} failed: {completed.stderr or completed.stdout}")


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        return [dict(row) for row in csv.DictReader(file)]


def audit_result(
    trade_date: str,
    paths: dict[str, Path],
    flow_csv: Path,
    flow_md: Path,
    steps: list[dict[str, Any]],
) -> dict[str, Any]:
    breadth = {row["metric"]: row for row in read_csv(paths["breadth"])}
    themes = read_csv(flow_csv)
    issues: list[dict[str, str]] = []
    required_metrics = ["两市成交额", "上涨家数", "下跌家数", "平盘家数", "涨停数", "炸板数", "跌停数"]
    for metric in required_metrics:
        if metric not in breadth:
            issues.append({"severity": "high", "code": "MISSING_BREADTH_METRIC", "detail": metric})
    for row in themes:
        theme = row["theme"]
        core_names = row.get("core_names", "")
        if theme == "消费/旅游/短剧" and any(name in core_names for name in ("胜利精密", "安洁科技", "可川科技", "光大同创")):
            issues.append({"severity": "high", "code": "THEME_CORE_MISMATCH", "detail": f"{theme}: {core_names}"})
        if float(row.get("total_score") or 0) >= 68 and float(row.get("core_score") or 0) < 12:
            issues.append({"severity": "medium", "code": "HIGH_SCORE_WEAK_CORE", "detail": theme})
        if row.get("stance") == "重点进攻" and float(row.get("core_score") or 0) < 12:
            issues.append({"severity": "high", "code": "ATTACK_WITHOUT_CORE", "detail": theme})
    status = "degraded" if issues else "completed"
    return {
        "skill": "a-share-market-flow-analyst",
        "version": "2",
        "trade_date": trade_date,
        "status": status,
        "market_state": extract_market_state(flow_md),
        "input_quality": {
            "breadth_source": breadth.get("全A行情降级状态", {}).get("value", "primary-or-unknown"),
            "breadth_complete": not any(issue["code"] == "MISSING_BREADTH_METRIC" for issue in issues),
            "news": "complete",
            "limit_pool": "degraded-no-limit-up-reason",
            "dragon_tiger": "complete",
        },
        "top_themes": themes[:5],
        "quality_issues": issues,
        "artifacts": {
            "market_flow_csv": str(flow_csv.relative_to(WORKSPACE_ROOT)),
            "market_flow_markdown": str(flow_md.relative_to(WORKSPACE_ROOT)),
        },
        "steps": steps,
    }


def extract_market_state(path: Path) -> str:
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("## 市场状态："):
            return line.split("：", 1)[1].strip()
    return "unknown"


def blocked_result(trade_date: str, missing: list[str], steps: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "skill": "a-share-market-flow-analyst",
        "version": "2",
        "trade_date": trade_date,
        "status": "blocked",
        "reason": "required_inputs_missing",
        "missing_inputs": missing,
        "steps": steps,
    }


def write_result(out_dir: Path, result: dict[str, Any]) -> None:
    json_path = out_dir / "skill-result.json"
    md_path = out_dir / "skill-result.md"
    json_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    lines = [
        "# A-Share Market Flow Skill Result",
        "",
        f"- Trade date: `{result['trade_date']}`",
        f"- Status: `{result['status']}`",
    ]
    if result.get("market_state"):
        lines.append(f"- Market state: `{result['market_state']}`")
    if result.get("missing_inputs"):
        lines.extend(["", "## Missing Inputs", ""])
        lines.extend(f"- `{item}`" for item in result["missing_inputs"])
    if result.get("quality_issues"):
        lines.extend(["", "## Quality Issues", ""])
        lines.extend(
            f"- `{issue['severity']}` `{issue['code']}`: {issue['detail']}"
            for issue in result["quality_issues"]
        )
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
