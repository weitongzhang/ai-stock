"""Leader and core-candidate extraction for theme analysis."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from skill_lab.market_data.normalizers import num, split_names
from skill_lab.sector_analysis.registry import ThemeDefinition, ThemeRegistry, default_registry
from skill_lab.shared.enums import ThemeLeaderRole
from skill_lab.shared.schemas import Serializable, ThemeScore


@dataclass(slots=True)
class ThemeLeaderCandidate(Serializable):
    theme: str
    symbol: str = ""
    name: str = ""
    role: ThemeLeaderRole = ThemeLeaderRole.UNKNOWN
    score: float = 0.0
    evidence: list[str] = field(default_factory=list)
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ThemeLeaderSummary(Serializable):
    trade_date: str
    theme: str
    candidates: list[ThemeLeaderCandidate] = field(default_factory=list)
    front_row: list[ThemeLeaderCandidate] = field(default_factory=list)
    capacity_core: list[ThemeLeaderCandidate] = field(default_factory=list)
    followers: list[ThemeLeaderCandidate] = field(default_factory=list)
    risk_samples: list[ThemeLeaderCandidate] = field(default_factory=list)


def extract_theme_leaders(
    theme_score: ThemeScore,
    kpl_rows: list[dict[str, Any]] | None = None,
    lhb_rows: list[dict[str, Any]] | None = None,
    registry: ThemeRegistry | None = None,
) -> ThemeLeaderSummary:
    registry = registry or default_registry()
    definition = registry.get(theme_score.theme) or ThemeDefinition(theme=theme_score.theme)
    candidates: dict[str, ThemeLeaderCandidate] = {}

    for name in theme_score.core_names:
        upsert_candidate(
            candidates,
            theme_score.theme,
            name=name,
            role=role_from_registry(name, definition),
            score=20,
            evidence=["listed in theme core_names"],
            raw={"source": "theme_score"},
        )

    for row in kpl_rows or []:
        if not row_matches_theme(row, definition):
            continue
        name = str(row.get("name") or "")
        status = str(row.get("status") or row.get("tag") or "")
        amount = num(row.get("amount"))
        role = ThemeLeaderRole.FRONT_ROW
        if "炸" in status or "failed" in status.lower():
            role = ThemeLeaderRole.RISK_SAMPLE
        elif amount >= 1_000_000_000 or name in definition.capacity_names:
            role = ThemeLeaderRole.CAPACITY_CORE
        evidence = [
            f"KPL status={status or '-'}",
            f"amount={amount:.0f}",
        ]
        upsert_candidate(
            candidates,
            theme_score.theme,
            symbol=str(row.get("ts_code") or row.get("code") or ""),
            name=name,
            role=role,
            score=score_from_kpl(status, amount),
            evidence=evidence,
            raw={"source": "kpl", "row": row},
        )

    for row in lhb_rows or []:
        name = str(row.get("名称") or row.get("name") or "")
        if not name:
            continue
        net_buy = num(row.get("龙虎榜净买额") or row.get("net_buy"))
        float_mv = num(row.get("流通市值") or row.get("float_market_value"))
        if not lhb_row_matches_theme(name, definition, net_buy):
            continue
        role = ThemeLeaderRole.CAPACITY_CORE if float_mv >= 10_000_000_000 or name in definition.capacity_names else ThemeLeaderRole.FOLLOWER
        evidence = [
            f"LHB net_buy={net_buy:.0f}",
            f"float_mv={float_mv:.0f}",
        ]
        upsert_candidate(
            candidates,
            theme_score.theme,
            symbol=str(row.get("代码") or row.get("symbol") or ""),
            name=name,
            role=role,
            score=score_from_lhb(net_buy, float_mv),
            evidence=evidence,
            raw={"source": "lhb", "row": row},
        )

    ranked = sorted(candidates.values(), key=lambda item: item.score, reverse=True)
    return ThemeLeaderSummary(
        trade_date=theme_score.trade_date,
        theme=theme_score.theme,
        candidates=ranked,
        front_row=[item for item in ranked if item.role == ThemeLeaderRole.FRONT_ROW],
        capacity_core=[item for item in ranked if item.role == ThemeLeaderRole.CAPACITY_CORE],
        followers=[item for item in ranked if item.role == ThemeLeaderRole.FOLLOWER],
        risk_samples=[item for item in ranked if item.role == ThemeLeaderRole.RISK_SAMPLE],
    )


def upsert_candidate(
    candidates: dict[str, ThemeLeaderCandidate],
    theme: str,
    name: str,
    role: ThemeLeaderRole,
    score: float,
    evidence: list[str],
    symbol: str = "",
    raw: dict[str, Any] | None = None,
) -> None:
    key = symbol or name
    if not key:
        return
    existing_key = key
    if existing_key not in candidates and name:
        for candidate_key, candidate in candidates.items():
            if candidate.name == name:
                existing_key = candidate_key
                break
    existing = candidates.get(existing_key)
    if existing is None:
        candidates[key] = ThemeLeaderCandidate(
            theme=theme,
            symbol=symbol,
            name=name,
            role=role,
            score=score,
            evidence=list(evidence),
            raw=raw or {},
        )
        return
    existing.score += score
    existing.evidence.extend(evidence)
    if role_priority(role) > role_priority(existing.role):
        existing.role = role
    if symbol and not existing.symbol:
        existing.symbol = symbol


def role_from_registry(name: str, definition: ThemeDefinition) -> ThemeLeaderRole:
    if name in definition.capacity_names:
        return ThemeLeaderRole.CAPACITY_CORE
    return ThemeLeaderRole.FOLLOWER


def row_matches_theme(row: dict[str, Any], definition: ThemeDefinition) -> bool:
    text = " ".join(str(row.get(key) or "") for key in ("theme", "lu_desc", "name", "tag", "query_tag"))
    tokens = [definition.theme] + definition.aliases + definition.front_row_keywords
    return any(token and token in text for token in tokens)


def lhb_row_matches_theme(name: str, definition: ThemeDefinition, net_buy: float) -> bool:
    if name in definition.capacity_names:
        return True
    return net_buy > 0 and any(token and token in name for token in definition.aliases)


def score_from_kpl(status: str, amount: float) -> float:
    score = 35.0
    if "连" in status:
        score += 15
    if "首" in status:
        score += 5
    if "炸" in status:
        score -= 20
    if amount >= 1_000_000_000:
        score += 15
    elif amount >= 500_000_000:
        score += 8
    return max(0.0, score)


def score_from_lhb(net_buy: float, float_mv: float) -> float:
    score = 10.0
    if net_buy > 0:
        score += min(30.0, net_buy / 50_000_000)
    if float_mv >= 10_000_000_000:
        score += 10
    return max(0.0, score)


def role_priority(role: ThemeLeaderRole) -> int:
    return {
        ThemeLeaderRole.RISK_SAMPLE: 4,
        ThemeLeaderRole.CAPACITY_CORE: 3,
        ThemeLeaderRole.FRONT_ROW: 2,
        ThemeLeaderRole.FOLLOWER: 1,
    }.get(role, 0)


def extract_all_theme_leaders(
    themes: list[ThemeScore],
    kpl_rows: list[dict[str, Any]] | None = None,
    lhb_rows: list[dict[str, Any]] | None = None,
    registry: ThemeRegistry | None = None,
) -> list[ThemeLeaderSummary]:
    registry = registry or default_registry()
    return [
        extract_theme_leaders(theme, kpl_rows=kpl_rows, lhb_rows=lhb_rows, registry=registry)
        for theme in themes
    ]
