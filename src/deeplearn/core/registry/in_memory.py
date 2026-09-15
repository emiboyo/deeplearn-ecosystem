"""Minimal in-memory Agent Registry for M1.3 tests.

This is process-local registration only. It is not persistence or a remote
registry service.
"""

from deeplearn.core.contracts import WireDocument
from deeplearn.core.registry.definitions import AgentDefinition
from deeplearn.core.registry.errors import (
    DuplicateDefinitionError,
    ToolNotAllowedError,
    UnknownAgentError,
    UnknownAgentVersionError,
)


class InMemoryAgentDefinitionRegistry:
    """Register immutable definitions and resolve exact versions."""

    def __init__(self) -> None:
        self._definitions: dict[tuple[str, str], AgentDefinition] = {}

    def register(self, definition: AgentDefinition | WireDocument) -> AgentDefinition:
        validated = (
            definition
            if isinstance(definition, AgentDefinition)
            else AgentDefinition.from_mapping(definition)
        )
        key = (validated.agent_id, validated.version)
        if key in self._definitions:
            raise DuplicateDefinitionError(
                f"agent definition already registered: {validated.agent_id}@{validated.version}"
            )
        self._definitions[key] = validated
        return validated

    def resolve(self, agent_id: str, agent_version: str) -> AgentDefinition:
        key = (agent_id, agent_version)
        if key in self._definitions:
            return self._definitions[key]
        if not any(registered_id == agent_id for registered_id, _ in self._definitions):
            raise UnknownAgentError(f"unknown agent: {agent_id}")
        raise UnknownAgentVersionError(f"unknown agent version: {agent_id}@{agent_version}")

    def is_tool_allowed(self, agent_id: str, agent_version: str, tool_id: str) -> bool:
        definition = self.resolve(agent_id, agent_version)
        return tool_id in definition.allowed_tools

    def require_tool_allowed(self, agent_id: str, agent_version: str, tool_id: str) -> None:
        if not self.is_tool_allowed(agent_id, agent_version, tool_id):
            raise ToolNotAllowedError(
                f"tool is not allowed for {agent_id}@{agent_version}: {tool_id}"
            )


__all__ = ["InMemoryAgentDefinitionRegistry"]
