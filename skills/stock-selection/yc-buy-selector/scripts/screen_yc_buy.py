#!/usr/bin/env python3
"""Run YC-buy 13-buy-point and triple-screen analysis from a repo checkout."""
from __future__ import annotations

import argparse
import csv
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


WORKSPACE_ROOT = Path(__file__).resolve().parents[4]
SRC_ROOT = WORKSPACE_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from skill_lab.shared.enums import BarSpan, DataSource
from skill_lab.shared.schemas import Bar
from skill_lab.stock_analysis.yc_buy_adapter import YcBuyAdapter, YcBuyClassEngine


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run YC-buy stock screening")
    parser.add_argument("--repo", default=".", help="Path to YC-buy repository root")
    parser.add_argument("--codes", default="", help="Comma-separated stock codes; empty means repo default/sample list")
    parser.add_argument("--source", default="sample", choices=["sample", "akshare", "baostock", "auto"])
    parser.add_argument("--mode", default="both", choices=["buy-points", "triple-screen", "both"])
    parser.add_argument("--start", default="", help="Start date YYYY-MM-DD")
    parser.add_argument("--end", default="", help="End date YYYY-MM-DD")
    parser.add_argument("--output", default="", help="Optional CSV output path")
    return parser.parse_args()


def load_repo(repo: Path):
    repo = repo.resolve()
    if not (repo / "strategies" / "buy_points.py").exists():
        raise SystemExit(f"Not a YC-buy repo: {repo}")
    sys.path.insert(0, str(repo))
    from data.data_fetcher import StockDataFetcher
    from strategies.buy_points import BuyPointAnalyzer
    from strategies.triple_screen import TripleScreenSystem

    return StockDataFetcher, BuyPointAnalyzer, TripleScreenSystem


def default_codes(fetcher) -> list[str]:
    try:
        codes = fetcher.get_all_stock_codes()
    except Exception:
        codes = []
    return codes or ["000001", "000333", "600519"]


def summarize_triple(result: dict | None) -> tuple[str, str, str, str]:
    if not result:
        return "none", "neutral", "neutral", "none"
    return (
        result.get("signal", "hold"),
        result["screen1"].get("trend", "neutral"),
        result["screen2"].get("position", "neutral"),
        result["screen3"].get("breakout", "none"),
    )


def dataframe_to_bars(code: str, data, source: str) -> list[Bar]:
    source_map = {
        "sample": DataSource.SAMPLE,
        "akshare": DataSource.AKSHARE,
        "baostock": DataSource.UNKNOWN,
        "auto": DataSource.UNKNOWN,
    }
    bars: list[Bar] = []
    for index, row in data.iterrows():
        bars.append(
            Bar(
                symbol=code,
                timestamp=str(index)[:10],
                open=float(row.get("open", 0.0)),
                high=float(row.get("high", 0.0)),
                low=float(row.get("low", 0.0)),
                close=float(row.get("close", 0.0)),
                volume=float(row.get("volume", 0.0)),
                amount=float(row.get("amount", 0.0)),
                span=BarSpan.DAY1,
                source=source_map.get(source, DataSource.UNKNOWN),
                raw=row.to_dict(),
            )
        )
    return bars


def main() -> int:
    args = parse_args()
    repo = Path(args.repo)
    StockDataFetcher, BuyPointAnalyzer, TripleScreenSystem = load_repo(repo)

    end_date = args.end or datetime.now().strftime("%Y-%m-%d")
    start_date = args.start or (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
    fetcher = StockDataFetcher(data_source=args.source)
    codes = [c.strip() for c in args.codes.split(",") if c.strip()] or default_codes(fetcher)

    rows: list[dict[str, str]] = []
    for code in codes:
        data = fetcher.get_stock_data(code, start_date=start_date, end_date=end_date)
        if data is None or len(data) < 60:
            print(f"{code}: skipped, insufficient data")
            continue

        buy_points: list[str] = []
        triple = None
        signal, trend, position, breakout = summarize_triple(triple)
        name = f"股票{code}"
        if args.source != "sample":
            try:
                name = fetcher.get_stock_name(code)
            except Exception:
                pass
        bars = dataframe_to_bars(code, data, args.source)
        engine = YcBuyClassEngine(BuyPointAnalyzer, TripleScreenSystem, mode=args.mode)
        stock_signal = YcBuyAdapter(engine).analyze(code, name, bars, trade_date=end_date)
        result = stock_signal.raw
        buy_points = [str(item) for item in result.get("buy_points", [])]
        signal, trend, position, breakout = summarize_triple(result.get("triple") or None)
        price = f"{data['close'].iloc[-1]:.2f}"
        reasons = "; ".join(buy_points) if buy_points else "-"

        if buy_points or signal in {"buy", "wait_breakout", "consider_buy"}:
            print(f"{code} {name}: price={price}, buy_points={len(buy_points)}, triple={signal}, reasons={reasons}")
            row = {
                "股票代码": code,
                "股票名称": name,
                "最新价格": price,
                "买点数量": str(len(buy_points)),
                "买点原因": reasons,
                "三重滤网信号": signal,
                "长周期趋势": trend,
                "中周期位置": position,
                "短周期突破": breakout,
                "分析日期": end_date,
            }
            row["domain_signal_direction"] = stock_signal.direction.value
            row["domain_signal_score"] = f"{stock_signal.score:.1f}"
            rows.append(row)

    if args.output:
        output = Path(args.output)
        if not output.is_absolute():
            output = repo / output
        with output.open("w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()) if rows else ["股票代码"])
            writer.writeheader()
            writer.writerows(rows)
        print(f"CSV written: {output}")

    print(f"Matched {len(rows)} / {len(codes)} candidates. Research only, not investment advice.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
