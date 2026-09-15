"""Explicit errors owned by the Agent Registry boundary."""


class RegistryError(Exception):
    """Base error for deterministic registry failures."""


class DefinitionValidationError(RegistryError, ValueError):
    """Raised when an agent definition is malformed."""


class DuplicateDefinitionError(RegistryError):
    """Raised when an immutable agent ID/version is already registered."""


class UnknownAgentError(RegistryError, LookupError):
    """Raised when no versions exist for an agent ID."""


class UnknownAgentVersionError(RegistryError, LookupError):
    """Raised when an agent exists but the requested version does not."""


class ToolNotAllowedError(RegistryError, PermissionError):
    """Raised when a tool is absent from a definition's allowlist."""


__all__ = [
    "DefinitionValidationError",
    "DuplicateDefinitionError",
    "RegistryError",
    "ToolNotAllowedError",
    "UnknownAgentError",
    "UnknownAgentVersionError",
]
