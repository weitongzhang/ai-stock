"""Named deterministic tools exposed to the research-agent controller."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any


Tool = Callable[..., Any]


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    def register(self, name: str, tool: Tool) -> None:
        if not name:
            raise ValueError("tool name cannot be empty")
        if name in self._tools:
            raise ValueError(f"tool already registered: {name}")
        self._tools[name] = tool

    def call(self, name: str, **kwargs):
        try:
            tool = self._tools[name]
        except KeyError as exc:
            raise KeyError(f"unknown tool: {name}") from exc
        return tool(**kwargs)

    def names(self) -> list[str]:
        return sorted(self._tools)
