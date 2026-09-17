"""Errors owned and normalized by the M1.5 tools boundary."""

class ToolDefinitionValidationError(ValueError): pass
class DuplicateToolError(ValueError): pass
class UnknownToolError(LookupError): pass
class UnknownToolVersionError(LookupError): pass
class InvalidToolArgumentsError(ValueError): pass
class ToolInputTooLargeError(InvalidToolArgumentsError): pass
class ToolUnavailableError(RuntimeError): pass
class ToolTimeoutError(TimeoutError): pass

__all__ = ["DuplicateToolError", "InvalidToolArgumentsError", "ToolDefinitionValidationError", "ToolInputTooLargeError", "ToolTimeoutError", "ToolUnavailableError", "UnknownToolError", "UnknownToolVersionError"]
