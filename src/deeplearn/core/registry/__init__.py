"""Agent-definition registry boundary and M1.3 in-memory implementation."""

from .definitions import AgentDefinition, AutonomyLevel, ExecutionLimits, Lifecycle, ModelRequirements
from .errors import (
    DefinitionValidationError,
    DuplicateDefinitionError,
    RegistryError,
    ToolNotAllowedError,
    UnknownAgentError,
    UnknownAgentVersionError,
)
from .in_memory import InMemoryAgentDefinitionRegistry
from .interfaces import AgentDefinitionRegistry

__all__ = [
    "AgentDefinition",
    "AgentDefinitionRegistry",
    "AutonomyLevel",
    "DefinitionValidationError",
    "DuplicateDefinitionError",
    "ExecutionLimits",
    "InMemoryAgentDefinitionRegistry",
    "Lifecycle",
    "ModelRequirements",
    "RegistryError",
    "ToolNotAllowedError",
    "UnknownAgentError",
    "UnknownAgentVersionError",
]
