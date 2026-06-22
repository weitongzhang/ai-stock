#!/usr/bin/env python
"""Run the deterministic A-share research agent."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from skill_lab.agent import AgentRequest, AgentTask, ResearchAgentController
from skill_lab.market_data.ftshare_provider import FTShareProvider


def main() -> int:
    parser = argparse.ArgumentParser(description="Run deterministic research-agent tasks.")
    parser.add_argument("task", choices=[item.value for item in AgentTask])
    parser.add_argument("--date", default="", help="Trade date for daily tasks.")
    parser.add_argument("--symbol", default="", help="Stock symbol for holding-analysis.")
    parser.add_argument("--name", default="", help="Optional stock name.")
    parser.add_argument("--cost", type=float, default=None, help="Holding cost.")
    parser.add_argument("--position-pct", type=float, default=None, help="Position percentage from 0 to 100.")
    parser.add_argument("--allow-quality-warnings", action="store_true")
    parser.add_argument("--offline", action="store_true", help="Disable live FTShare provider.")
    parser.add_argument("--out", default="", help="Optional JSON output path.")
    args = parser.parse_args()

    bar_provider = None if args.offline else FTShareProvider(ROOT)
    controller = ResearchAgentController(ROOT, bar_provider=bar_provider)
    result = controller.run(
        AgentRequest(
            task=AgentTask(args.task),
            trade_date=args.date,
            symbol=args.symbol,
            name=args.name,
            cost=args.cost,
            position_pct=args.position_pct,
            allow_quality_warnings=args.allow_quality_warnings,
        )
    )
    data = result.to_dict()
    text = json.dumps(data, ensure_ascii=False, indent=2)
    if args.out:
        path = Path(args.out)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    print(text)
    return 0 if data["status"] in {"completed", "degraded"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
