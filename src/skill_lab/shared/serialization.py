"""Serialization helpers for lightweight dataclass schemas."""

from __future__ import annotations

from dataclasses import asdict, is_dataclass
from datetime import date, datetime
from enum import Enum
from typing import Any, TypeVar


T = TypeVar("T")


def to_plain(value: Any) -> Any:
    """Convert dataclasses, enums, dates, and containers to JSON-like values."""

    if is_dataclass(value):
        return {key: to_plain(item) for key, item in asdict(value).items()}
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(key): to_plain(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [to_plain(item) for item in value]
    return value


def parse_enum(enum_type: type[T], value: Any, default: T) -> T:
    """Parse a string into an enum while preserving a safe default."""

    if isinstance(value, enum_type):
        return value
    if value is None:
        return default
    try:
        return enum_type(str(value))
    except ValueError:
        return default


def compact_dict(data: dict[str, Any]) -> dict[str, Any]:
    """Drop keys with None or empty-list values from a dict."""

    return {
        key: value
        for key, value in data.items()
        if value is not None and value != []
    }
