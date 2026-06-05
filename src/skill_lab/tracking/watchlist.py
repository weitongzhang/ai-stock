"""Watchlist helpers for turning plans into trackable items."""

from __future__ import annotations

from skill_lab.shared.enums import InstrumentType, WatchStatus
from skill_lab.shared.schemas import TomorrowPlan, WatchItem


def watch_items_from_plan(plan: TomorrowPlan, plan_id: str | None = None) -> list[WatchItem]:
    source_plan_id = plan_id or f"plan:{plan.trade_date}"
    items: list[WatchItem] = []
    for plan_item in plan.items:
        if plan_item.candidates:
            for index, name in enumerate(plan_item.candidates, start=1):
                items.append(
                    WatchItem(
                        item_id=f"{source_plan_id}:{plan_item.priority}:{index}",
                        item_type=InstrumentType.STOCK,
                        name=name,
                        theme=plan_item.theme,
                        horizon="short",
                        status=WatchStatus.CANDIDATE,
                        trigger=plan_item.confirm_signal,
                        invalidation=plan_item.give_up_signal,
                        source_plan_id=source_plan_id,
                        raw={"plan_item": plan_item.to_dict()},
                    )
                )
        else:
            items.append(
                WatchItem(
                    item_id=f"{source_plan_id}:{plan_item.priority}:theme",
                    item_type=InstrumentType.THEME,
                    name=plan_item.theme,
                    theme=plan_item.theme,
                    horizon="short",
                    status=WatchStatus.CANDIDATE,
                    trigger=plan_item.confirm_signal,
                    invalidation=plan_item.give_up_signal,
                    source_plan_id=source_plan_id,
                    raw={"plan_item": plan_item.to_dict()},
                )
            )
    return items


def mark_triggered(item: WatchItem, note: str = "") -> WatchItem:
    return WatchItem(
        item_id=item.item_id,
        item_type=item.item_type,
        symbol=item.symbol,
        name=item.name,
        theme=item.theme,
        horizon=item.horizon,
        status=WatchStatus.TRIGGERED,
        trigger=item.trigger,
        invalidation=item.invalidation,
        next_check_date=item.next_check_date,
        source_plan_id=item.source_plan_id,
        raw={**item.raw, "status_note": note},
    )


def mark_invalidated(item: WatchItem, note: str = "") -> WatchItem:
    return WatchItem(
        item_id=item.item_id,
        item_type=item.item_type,
        symbol=item.symbol,
        name=item.name,
        theme=item.theme,
        horizon=item.horizon,
        status=WatchStatus.INVALIDATED,
        trigger=item.trigger,
        invalidation=item.invalidation,
        next_check_date=item.next_check_date,
        source_plan_id=item.source_plan_id,
        raw={**item.raw, "status_note": note},
    )

