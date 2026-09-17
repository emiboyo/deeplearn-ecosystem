"""Deterministic read-only synthetic echo adapter for M1.5 tests."""

from collections.abc import Mapping
from enum import StrEnum

from .contracts import AdapterResponse, ToolRequest
from .errors import (
    InvalidToolArgumentsError,
    ToolInputTooLargeError,
    ToolTimeoutError,
    ToolUnavailableError,
)


class SafeEchoFailure(StrEnum):
    UNAVAILABLE = "unavailable"
    TIMEOUT = "timeout"
    FAILURE = "failure"


class SafeEchoAdapter:
    def __init__(
        self,
        *,
        tool_id: str = "test.safe_echo",
        version: str = "1.0.0",
        failure: SafeEchoFailure | None = None,
        latency_ms: int = 5,
    ) -> None:
        self._tool_id = tool_id
        self._version = version
        self.failure = failure
        self.latency_ms = latency_ms
        self.invocation_count = 0

    @property
    def tool_id(self) -> str:
        return self._tool_id

    @property
    def version(self) -> str:
        return self._version

    def validate_arguments(
        self, arguments: Mapping[str, object], max_input_chars: int
    ) -> None:
        if set(arguments) != {"value"}:
            raise InvalidToolArgumentsError("arguments must contain only value")
        value = arguments["value"]
        if not isinstance(value, str) or not value:
            raise InvalidToolArgumentsError("value must be a non-empty string")
        if len(value) > max_input_chars:
            raise ToolInputTooLargeError("value exceeds the registered input limit")

    def invoke(self, request: ToolRequest) -> AdapterResponse:
        self.invocation_count += 1
        if self.failure is SafeEchoFailure.UNAVAILABLE:
            raise ToolUnavailableError("synthetic unavailable detail")
        if self.failure is SafeEchoFailure.TIMEOUT:
            raise ToolTimeoutError("synthetic timeout detail")
        if self.failure is SafeEchoFailure.FAILURE:
            raise RuntimeError("raw synthetic adapter detail must not escape")
        return AdapterResponse(
            output={"message": request.arguments["value"]},
            latency_ms=self.latency_ms,
        )

    def validate_output(
        self, output: Mapping[str, object], max_output_chars: int
    ) -> None:
        if set(output) != {"message"} or not isinstance(output["message"], str):
            raise ValueError("output must contain only a text message")
        if not output["message"] or len(output["message"]) > max_output_chars:
            raise ValueError("output violates the registered output limit")


__all__ = ["SafeEchoAdapter", "SafeEchoFailure"]
