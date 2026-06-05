"""Theme registry loading and matching helpers."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


DEFAULT_REGISTRY_PATH = Path(__file__).with_name("theme_registry.json")


@dataclass(slots=True)
class ThemeDefinition:
    theme: str
    aliases: list[str] = field(default_factory=list)
    capacity_names: list[str] = field(default_factory=list)
    front_row_keywords: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ThemeDefinition":
        return cls(
            theme=str(data.get("theme") or ""),
            aliases=[str(item) for item in data.get("aliases", [])],
            capacity_names=[str(item) for item in data.get("capacity_names", [])],
            front_row_keywords=[str(item) for item in data.get("front_row_keywords", [])],
        )


class ThemeRegistry:
    """Registry for theme aliases and known capacity names."""

    def __init__(self, definitions: list[ThemeDefinition]) -> None:
        self.definitions = definitions

    @classmethod
    def load(cls, path: Path | str = DEFAULT_REGISTRY_PATH) -> "ThemeRegistry":
        with Path(path).open("r", encoding="utf-8") as file:
            data = json.load(file)
        return cls([ThemeDefinition.from_dict(item) for item in data])

    def match_theme(self, text: str) -> ThemeDefinition | None:
        normalized = text.strip()
        if not normalized:
            return None
        for definition in self.definitions:
            tokens = [definition.theme] + definition.aliases
            if any(token and token in normalized for token in tokens):
                return definition
        return None

    def get(self, theme: str) -> ThemeDefinition | None:
        for definition in self.definitions:
            if definition.theme == theme:
                return definition
        return self.match_theme(theme)


def default_registry() -> ThemeRegistry:
    return ThemeRegistry.load(DEFAULT_REGISTRY_PATH)
