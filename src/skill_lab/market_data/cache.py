"""Small JSON cache for market data responses and normalized objects."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from skill_lab.shared.serialization import to_plain


@dataclass(slots=True)
class CacheEntry:
    key: str
    created_at: str
    payload: Any


class JsonCache:
    """Filesystem JSON cache with stable key hashing."""

    def __init__(self, root: Path | str, namespace: str = "market_data") -> None:
        self.root = Path(root)
        self.namespace = namespace

    def get(self, key: str, max_age_seconds: int | None = None) -> Any | None:
        path = self.path_for(key)
        if not path.exists():
            return None
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)
        entry = CacheEntry(
            key=str(data.get("key", "")),
            created_at=str(data.get("created_at", "")),
            payload=data.get("payload"),
        )
        if max_age_seconds is not None and is_expired(entry.created_at, max_age_seconds):
            return None
        return entry.payload

    def set(self, key: str, payload: Any) -> Path:
        path = self.path_for(key)
        path.parent.mkdir(parents=True, exist_ok=True)
        entry = CacheEntry(
            key=key,
            created_at=datetime.now().isoformat(timespec="seconds"),
            payload=to_plain(payload),
        )
        with path.open("w", encoding="utf-8") as file:
            json.dump(to_plain(entry), file, ensure_ascii=False, indent=2)
        return path

    def path_for(self, key: str) -> Path:
        digest = hashlib.sha1(key.encode("utf-8")).hexdigest()
        return self.root / ".cache" / self.namespace / f"{digest}.json"


def build_cache_key(source: str, method: str, **params: Any) -> str:
    normalized = json.dumps(params, ensure_ascii=False, sort_keys=True, default=str)
    return f"{source}:{method}:{normalized}"


def is_expired(created_at: str, max_age_seconds: int) -> bool:
    try:
        created = datetime.fromisoformat(created_at)
    except ValueError:
        return True
    return datetime.now() - created > timedelta(seconds=max_age_seconds)
