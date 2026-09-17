"""Registered, bounded tool execution boundary."""

from .contracts import (
    AdapterResponse,
    InvalidToolRequestError,
    ToolFailure,
    ToolFailureCategory,
    ToolRequest,
    ToolResult,
    ToolStatus,
)
from .definitions import RiskClass, SideEffectClass, ToolDefinition, ToolLifecycle
from .dispatcher import ToolDispatcher
from .errors import (
    DuplicateToolError,
    InvalidToolArgumentsError,
    ToolDefinitionValidationError,
    ToolInputTooLargeError,
    ToolTimeoutError,
    ToolUnavailableError,
    UnknownToolError,
    UnknownToolVersionError,
)
from .interfaces import ToolAdapter, ToolGateway
from .registry import InMemoryToolRegistry
from .safe_echo import SafeEchoAdapter, SafeEchoFailure

__all__ = [
    "AdapterResponse", "DuplicateToolError", "InMemoryToolRegistry",
    "InvalidToolArgumentsError", "InvalidToolRequestError", "RiskClass",
    "SafeEchoAdapter", "SafeEchoFailure", "SideEffectClass", "ToolAdapter",
    "ToolDefinition", "ToolDefinitionValidationError", "ToolDispatcher",
    "ToolFailure", "ToolFailureCategory", "ToolGateway", "ToolInputTooLargeError",
    "ToolLifecycle", "ToolRequest", "ToolResult", "ToolStatus", "ToolTimeoutError",
    "ToolUnavailableError", "UnknownToolError", "UnknownToolVersionError",
]
