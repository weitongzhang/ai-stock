#!/usr/bin/env python
"""Collect normalized AkShare limit-pool and dragon-tiger evidence."""

from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path


def normalize_date(value: str) -> tuple[str, str]:
    compact = value.replace("-", "")
    if len(compact) != 8 or not compact.isdigit():
        raise ValueError(f"Unsupported date: {value}")
    return f"{compact[:4]}-{compact[4:6]}-{compact[6:]}", compact


def main() -> int:
    parser = argparse.ArgumentParser(description="Collect AkShare limit-pool and dragon-tiger evidence.")
    parser.add_argument("--date", default=date.today().isoformat())
    parser.add_argument("--out-dir", default="examples/market")
    args = parser.parse_args()

    report_date, compact = normalize_date(args.date)
    out_dir = Path(args.out_dir)
    limit_dir = out_dir / "limit-pool"
    lhb_dir = out_dir / "dragon-tiger"
    limit_dir.mkdir(parents=True, exist_ok=True)
    lhb_dir.mkdir(parents=True, exist_ok=True)

    import akshare as ak
    import pandas as pd

    limit_up = ak.stock_zt_pool_em(date=compact).copy()
    failed = ak.stock_zt_pool_zbgc_em(date=compact).copy()
    limit_up["tag"] = "涨停"
    failed["tag"] = "炸板"
    limit_up["source"] = "akshare:stock_zt_pool_em"
    failed["source"] = "akshare:stock_zt_pool_zbgc_em"
    limit_rows = pd.concat([limit_up, failed], ignore_index=True)
    limit_path = limit_dir / f"{compact}-akshare-limit-pool.csv"
    limit_rows.to_csv(limit_path, index=False, encoding="utf-8-sig")

    lhb = ak.stock_lhb_detail_em(start_date=compact, end_date=compact).copy()
    lhb["source"] = "akshare:stock_lhb_detail_em"
    lhb_path = lhb_dir / f"{compact}-eastmoney-lhb.csv"
    lhb.to_csv(lhb_path, index=False, encoding="utf-8-sig")

    result = {
        "status": "ok",
        "date": report_date,
        "limit_up": len(limit_up),
        "failed_limit_up": len(failed),
        "dragon_tiger_rows": len(lhb),
        "limit_pool_csv": str(limit_path),
        "dragon_tiger_csv": str(lhb_path),
        "limitations": [
            "AkShare limit-pool rows do not include KPL theme or limit-up-reason fields; downstream scoring discounts them."
        ],
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
