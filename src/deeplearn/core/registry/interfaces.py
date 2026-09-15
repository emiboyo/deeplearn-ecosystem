"""Owned interfaces for versioned agent-definition lookup.

Implementations and the first Test Agent definition are deferred to M1.3.
"""

from typing import Protocol

from deeplearn.core.contracts import WireDocument


class AgentDefinitionRegistry(Protocol):
    """Resolve an agent definition without prescribing its storage."""

    def resolve(self, agent_id: str, agent_version: str) -> WireDocument:
        """Return a definition conforming to its canonical wire contract."""


__all__ = ["AgentDefinitionRegistry"]
