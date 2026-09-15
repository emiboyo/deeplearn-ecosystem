"""Owned interfaces for versioned agent-definition lookup.

Implementations and the first Test Agent definition are deferred to M1.3.
"""

from typing import Protocol

from deeplearn.core.contracts import WireDocument
from deeplearn.core.registry.definitions import AgentDefinition


class AgentDefinitionRegistry(Protocol):
    """Register and resolve immutable, explicitly versioned definitions."""

    def register(self, definition: AgentDefinition | WireDocument) -> AgentDefinition:
        """Validate and register one definition without overwriting."""

    def resolve(self, agent_id: str, agent_version: str) -> AgentDefinition:
        """Return the exact immutable definition version."""

    def is_tool_allowed(self, agent_id: str, agent_version: str, tool_id: str) -> bool:
        """Inspect whether a tool is declared in the definition allowlist."""

    def require_tool_allowed(self, agent_id: str, agent_version: str, tool_id: str) -> None:
        """Reject a tool absent from the definition allowlist."""


__all__ = ["AgentDefinitionRegistry"]
