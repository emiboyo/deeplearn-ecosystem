"""Validated dispatch to explicitly registered tool adapters."""

from collections.abc import Mapping

from .contracts import (
    InvalidToolRequestError,
    ToolFailure,
    ToolFailureCategory,
    ToolRequest,
    ToolResult,
    ToolStatus,
)
from .definitions import SideEffectClass, ToolDefinition
from .errors import (
    InvalidToolArgumentsError,
    ToolInputTooLargeError,
    ToolTimeoutError,
    ToolUnavailableError,
    UnknownToolError,
    UnknownToolVersionError,
)
from .interfaces import ToolAdapter
from .registry import InMemoryToolRegistry


class ToolDispatcher:
    def __init__(self, registry: InMemoryToolRegistry) -> None:
        self._registry = registry

    def invoke(self, request: ToolRequest | Mapping[str, object]) -> ToolResult:
        try:
            validated = (
                request if isinstance(request, ToolRequest) else ToolRequest.from_mapping(request)
            )
        except (InvalidToolRequestError, TypeError):
            return self._invalid_result(request)

        try:
            definition, adapter = self._registry.resolve(
                validated.tool_id, validated.tool_version
            )
        except UnknownToolError:
            return self._failure_result(
                validated, None, ToolFailureCategory.TOOL_NOT_REGISTERED,
                "tool.not_registered", "The requested tool is not registered.", False,
            )
        except UnknownToolVersionError:
            return self._failure_result(
                validated, None, ToolFailureCategory.TOOL_VERSION_NOT_FOUND,
                "tool.version_not_found", "The requested tool version is not registered.", False,
            )

        try:
            adapter.validate_arguments(validated.arguments, definition.max_input_chars)
        except ToolInputTooLargeError:
            return self._failure_result(
                validated, definition, ToolFailureCategory.INPUT_TOO_LARGE,
                "tool.input_too_large", "The tool input exceeds its registered limit.", False,
            )
        except InvalidToolArgumentsError:
            return self._failure_result(
                validated, definition, ToolFailureCategory.INVALID_TOOL_REQUEST,
                "tool.invalid_arguments", "The tool arguments are invalid.", False,
            )

        if validated.timeout_ms > definition.timeout_ms:
            return self._failure_result(
                validated, definition, ToolFailureCategory.INVALID_TOOL_REQUEST,
                "tool.invalid_timeout", "The requested timeout exceeds the registered limit.", False,
            )

        try:
            response = adapter.invoke(validated)
            adapter.validate_output(response.output, definition.max_output_chars)
        except ToolUnavailableError:
            return self._failure_result(
                validated, definition, ToolFailureCategory.TOOL_UNAVAILABLE,
                "tool.unavailable", "The registered tool is unavailable.", True,
            )
        except ToolTimeoutError:
            return self._failure_result(
                validated, definition, ToolFailureCategory.TOOL_TIMEOUT,
                "tool.timeout", "The registered tool timed out.", True,
            )
        except Exception:
            return self._failure_result(
                validated, definition, ToolFailureCategory.TOOL_FAILURE,
                "tool.failure", "The registered tool failed.", True,
            )

        return ToolResult(
            tool_request_id=validated.tool_request_id,
            tool_id=validated.tool_id,
            tool_version=validated.tool_version,
            status=ToolStatus.SUCCEEDED,
            output=response.output,
            latency_ms=response.latency_ms,
            correlation_id=validated.correlation_id,
            trace_id=validated.trace_id,
            side_effect=definition.side_effect,
        )

    @staticmethod
    def _failure_result(
        request: ToolRequest,
        definition: ToolDefinition | None,
        category: ToolFailureCategory,
        code: str,
        message: str,
        retryable: bool,
    ) -> ToolResult:
        return ToolResult(
            tool_request_id=request.tool_request_id,
            tool_id=request.tool_id,
            tool_version=request.tool_version,
            status=ToolStatus.FAILED,
            failure=ToolFailure(category, code, message, retryable),
            latency_ms=0,
            correlation_id=request.correlation_id,
            trace_id=request.trace_id,
            side_effect=(definition.side_effect if definition else SideEffectClass.NONE),
        )

    @staticmethod
    def _invalid_result(request: ToolRequest | Mapping[str, object]) -> ToolResult:
        request_id = request.get("tool_request_id") if isinstance(request, Mapping) else None
        tool_id = request.get("tool_id") if isinstance(request, Mapping) else None
        version = request.get("tool_version") if isinstance(request, Mapping) else None
        correlation = request.get("correlation_id") if isinstance(request, Mapping) else None
        trace = request.get("trace_id") if isinstance(request, Mapping) else None
        return ToolResult(
            tool_request_id=request_id if isinstance(request_id, str) and request_id else "unknown_request",
            tool_id=tool_id if isinstance(tool_id, str) and tool_id else "unknown.tool",
            tool_version=version if isinstance(version, str) and version else "0.0.0",
            status=ToolStatus.FAILED,
            failure=ToolFailure(
                ToolFailureCategory.INVALID_TOOL_REQUEST,
                "tool.invalid_request",
                "The tool request is invalid.",
                False,
            ),
            latency_ms=0,
            correlation_id=(correlation if isinstance(correlation, str) and correlation else "unknown_correlation"),
            trace_id=trace if isinstance(trace, str) and trace else None,
            side_effect=SideEffectClass.NONE,
        )


__all__ = ["ToolDispatcher"]
