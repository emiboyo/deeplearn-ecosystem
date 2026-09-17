"""Minimal explicit in-memory registry for immutable tool versions."""

from collections.abc import Mapping

from .definitions import ToolDefinition
from .errors import DuplicateToolError, UnknownToolError, UnknownToolVersionError
from .interfaces import ToolAdapter


class InMemoryToolRegistry:
    def __init__(self) -> None:
        self._definitions: dict[tuple[str, str], ToolDefinition] = {}
        self._adapters: dict[tuple[str, str], ToolAdapter] = {}

    def register(
        self,
        definition: ToolDefinition | Mapping[str, object],
        adapter: ToolAdapter,
    ) -> ToolDefinition:
        validated = (
            definition
            if isinstance(definition, ToolDefinition)
            else ToolDefinition.from_mapping(definition)
        )
        if (adapter.tool_id, adapter.version) != (validated.tool_id, validated.version):
            raise ValueError("adapter identity must match the registered tool definition")
        key = (validated.tool_id, validated.version)
        if key in self._definitions:
            raise DuplicateToolError(
                f"tool definition already registered: {validated.tool_id}@{validated.version}"
            )
        self._definitions[key] = validated
        self._adapters[key] = adapter
        return validated

    def resolve(self, tool_id: str, version: str) -> tuple[ToolDefinition, ToolAdapter]:
        key = (tool_id, version)
        if key in self._definitions:
            return self._definitions[key], self._adapters[key]
        if not any(registered_id == tool_id for registered_id, _ in self._definitions):
            raise UnknownToolError(f"unknown tool: {tool_id}")
        raise UnknownToolVersionError(f"unknown tool version: {tool_id}@{version}")


__all__ = ["InMemoryToolRegistry"]
