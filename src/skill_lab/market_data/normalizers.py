"""Normalizers for current CSV/JSON market examples."""

from __future__ import annotations

from typing import Any

from skill_lab.shared.enums import DataSource, ThemeStance
from skill_lab.shared.schemas import IndexEnvironment, MarketBreadth, ThemeScore
from skill_lab.shared.serialization import parse_enum


def num(value: Any, default: float = 0.0) -> float:
    if value is None:
        return default
    text = str(value).replace(",", "").replace("%", "").strip()
    if not text or text in {"-", "None", "nan"}:
        return default
    try:
        return float(text)
    except ValueError:
        return default


def metric_map(rows: list[dict[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for row in rows:
        if "metric" in row:
            result[str(row.get("metric", "")).strip()] = row.get("value")
    return result


def normalize_market_breadth(
    trade_date: str,
    rows: list[dict[str, Any]],
    source: DataSource = DataSource.FILE,
) -> MarketBreadth:
    metrics = metric_map(rows)
    return MarketBreadth(
        trade_date=trade_date,
        turnover=num(metrics.get("两市成交额") or metrics.get("成交额") or metrics.get("turnover")),
        advancers=int(num(metrics.get("上涨家数") or metrics.get("advancers"))),
        decliners=int(num(metrics.get("下跌家数") or metrics.get("decliners"))),
        flat_count=int(num(metrics.get("平盘家数") or metrics.get("flat_count"))),
        limit_up_count=int(num(metrics.get("涨停数") or metrics.get("limit_up_count"))),
        failed_limit_up_count=int(num(metrics.get("炸板数") or metrics.get("failed_limit_up_count"))),
        limit_down_count=int(num(metrics.get("跌停数") or metrics.get("limit_down_count"))),
        seal_rate=num(metrics.get("封板率") or metrics.get("seal_rate")),
        failed_limit_up_rate=num(metrics.get("炸板率") or metrics.get("failed_limit_up_rate")),
        source=source,
        raw={"metrics": metrics, "rows": rows},
    )


def normalize_index_environment(
    row: dict[str, Any],
    source: DataSource = DataSource.FILE,
) -> IndexEnvironment:
    return IndexEnvironment(
        trade_date=str(row.get("date") or row.get("trade_date") or ""),
        name=str(row.get("name") or ""),
        symbol=str(row.get("symbol") or row.get("code") or ""),
        pct_chg=num(row.get("pct_chg")),
        five_day_pct=num(row.get("five_day_pct")),
        shape=str(row.get("shape") or ""),
        environment=str(row.get("environment") or ""),
        role=str(row.get("role") or ""),
        meaning=str(row.get("meaning") or ""),
        source=parse_enum(DataSource, row.get("source"), source),
        raw=dict(row),
    )


def normalize_theme_score(
    trade_date: str,
    row: dict[str, Any],
) -> ThemeScore:
    return ThemeScore(
        trade_date=trade_date,
        theme=str(row.get("theme") or ""),
        total_score=num(row.get("total_score") or row.get("score")),
        stance=parse_theme_stance(str(row.get("stance") or "")),
        flow_score=num(row.get("flow_score")),
        map_score=num(row.get("map_score")),
        core_score=num(row.get("core_score")),
        timing_score=num(row.get("timing_score")),
        core_names=split_names(row.get("core_names")),
        confirm_signal=str(row.get("confirm_signal") or ""),
        give_up_signal=str(row.get("give_up_signal") or ""),
        raw=dict(row),
    )


def parse_theme_stance(text: str) -> ThemeStance:
    if text in {"重点进攻", "主攻"}:
        return ThemeStance.ATTACK
    if text in {"积极观察", "观察"}:
        return ThemeStance.ACTIVE_WATCH
    if text in {"跟踪等待", "等待"}:
        return ThemeStance.TRACK_WAIT
    if text in {"放弃"}:
        return ThemeStance.GIVE_UP
    return ThemeStance.UNKNOWN


def split_names(value: Any) -> list[str]:
    if value is None:
        return []
    text = str(value).strip()
    if not text:
        return []
    for sep in ("、", "/", ";", "|"):
        text = text.replace(sep, ",")
    return [item.strip() for item in text.split(",") if item.strip()]

