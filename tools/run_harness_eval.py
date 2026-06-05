#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Run a minimal Trading Research Harness evaluation dataset."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from skill_lab.evaluation.datasets import load_jsonl
from skill_lab.evaluation.judges import RequiredFieldJudge
from skill_lab.evaluation.reports import render_markdown
from skill_lab.evaluation.runner import run_judge
from skill_lab.tracking.journal import append_jsonl, entry_from_eval_result


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Harness evaluation on a JSONL dataset.")
    parser.add_argument("--dataset", required=True, help="Path to EvalSample JSONL.")
    parser.add_argument("--target-version", default="dev", help="Target version label.")
    parser.add_argument("--out", help="Optional Markdown output path.")
    parser.add_argument("--journal", help="Optional JSONL decision journal path.")
    parser.add_argument("--json", action="store_true", help="Print JSON report instead of Markdown.")
    args = parser.parse_args()

    samples = load_jsonl(Path(args.dataset))
    if not samples:
        raise SystemExit("No samples found.")
    required_fields = samples[0].ground_truth.get("required_fields")
    if not isinstance(required_fields, list):
        raise SystemExit("Dataset ground_truth.required_fields must be a list for this runner.")

    report = run_judge(
        RequiredFieldJudge([str(item) for item in required_fields]),
        samples,
        target_version=args.target_version,
    )
    if args.json:
        output = json.dumps(report.to_dict(), ensure_ascii=False, indent=2)
    else:
        output = render_markdown(report)

    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(output, encoding="utf-8")
    else:
        print(output)

    if args.journal:
        journal_path = Path(args.journal)
        for result in report.results:
            append_jsonl(journal_path, entry_from_eval_result(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
