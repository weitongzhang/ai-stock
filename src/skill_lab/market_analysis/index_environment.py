"""Index environment summary service."""

from __future__ import annotations

from dataclasses import dataclass, field

from skill_lab.shared.schemas import IndexEnvironment


@dataclass(slots=True)
class IndexEnvironmentSummary:
    trade_date: str
    stage: str
    strong_indexes: list[str] = field(default_factory=list)
    weak_indexes: list[str] = field(default_factory=list)
    reasons: list[str] = field(default_factory=list)
    constraints: list[str] = field(default_factory=list)


def summarize_index_environment(rows: list[IndexEnvironment]) -> IndexEnvironmentSummary:
    if not rows:
        return IndexEnvironmentSummary(
            trade_date="",
            stage="missing",
            reasons=["index environment data is missing"],
            constraints=["do not enlarge risk without index context"],
        )

    strong = [row.name for row in rows if row.environment in {"强", "偏强"}]
    weak = [row.name for row in rows if row.environment == "偏弱"]
    trade_date = rows[0].trade_date
    reasons: list[str] = []
    constraints: list[str] = []

    ranked = sorted(rows, key=lambda row: row.pct_chg, reverse=True)
    for row in ranked[:2]:
        reasons.append(f"{row.name} is relatively stronger: {row.role or row.meaning}")

    if "科创50" in strong:
        constraints.append("hard-tech themes can receive priority verification")
    if "创业板指" in weak:
        constraints.append("high-beta growth positions should be restrained")
    if "北证50" in strong:
        constraints.append("small-cap theme spillover is possible but needs breadth support")

    if len(strong) >= 3 and not weak:
        stage = "supports_attack"
    elif strong and weak:
        stage = "structural_split"
    elif len(weak) >= 3:
        stage = "defensive"
    else:
        stage = "neutral"

    return IndexEnvironmentSummary(
        trade_date=trade_date,
        stage=stage,
        strong_indexes=strong,
        weak_indexes=weak,
        reasons=reasons,
        constraints=constraints,
    )

