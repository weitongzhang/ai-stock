from __future__ import annotations

import argparse
import json
from dataclasses import dataclass


RETRACEMENTS = (0.236, 0.382, 0.5, 0.618, 0.786)
EXTENSIONS = (1.272, 1.382, 1.618, 2.0)


@dataclass(frozen=True)
class FibonacciPlan:
    trend: str
    low: float
    high: float
    current: float | None
    retracements: dict[str, float]
    extensions: dict[str, float]
    current_zone: str | None


def _round_price(value: float) -> float:
    return round(value, 3)


def _current_zone(current: float | None, levels: dict[str, float], trend: str) -> str | None:
    if current is None:
        return None
    ordered = sorted(levels.items(), key=lambda item: item[1])
    if trend == "up":
        for name, value in ordered:
            if current <= value:
                return f"at_or_below_{name}"
        return "above_all_retracements"
    for name, value in reversed(ordered):
        if current >= value:
            return f"at_or_above_{name}"
    return "below_all_retracements"


def calculate_plan(low: float, high: float, trend: str, current: float | None = None) -> FibonacciPlan:
    if high <= low:
        raise ValueError("high must be greater than low")
    if trend not in {"up", "down"}:
        raise ValueError("trend must be 'up' or 'down'")

    span = high - low
    if trend == "up":
        retracements = {
            f"{ratio:.3f}".rstrip("0").rstrip("."): _round_price(high - span * ratio)
            for ratio in RETRACEMENTS
        }
        extensions = {
            f"{ratio:.3f}".rstrip("0").rstrip("."): _round_price(low + span * ratio)
            for ratio in EXTENSIONS
        }
    else:
        retracements = {
            f"{ratio:.3f}".rstrip("0").rstrip("."): _round_price(low + span * ratio)
            for ratio in RETRACEMENTS
        }
        extensions = {
            f"{ratio:.3f}".rstrip("0").rstrip("."): _round_price(high - span * ratio)
            for ratio in EXTENSIONS
        }

    return FibonacciPlan(
        trend=trend,
        low=_round_price(low),
        high=_round_price(high),
        current=_round_price(current) if current is not None else None,
        retracements=retracements,
        extensions=extensions,
        current_zone=_current_zone(current, retracements, trend),
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Calculate Fibonacci retracement and extension levels.")
    parser.add_argument("--low", type=float, required=True)
    parser.add_argument("--high", type=float, required=True)
    parser.add_argument("--current", type=float)
    parser.add_argument("--trend", choices=("up", "down"), required=True)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    plan = calculate_plan(args.low, args.high, args.trend, args.current)
    output = {
        "trend": plan.trend,
        "low": plan.low,
        "high": plan.high,
        "current": plan.current,
        "retracements": plan.retracements,
        "extensions": plan.extensions,
        "current_zone": plan.current_zone,
    }
    print(json.dumps(output, ensure_ascii=False, indent=2 if args.pretty else None))


if __name__ == "__main__":
    main()

