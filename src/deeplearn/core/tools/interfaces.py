"""Provider-neutral interfaces for registered tool invocation."""

from collections.abc import Mapping
from typing import Protocol

from .contracts import AdapterResponse, ToolRequest, ToolResult

class ToolAdapter(Protocol):
    tool_id: str
    version: str
    def validate_arguments(self, arguments: Mapping[str, object], max_input_chars: int) -> None: ...
    def validate_output(self, output: Mapping[str, object], max_output_chars: int) -> None: ...
    def invoke(self, request: ToolRequest) -> AdapterResponse: ...


class ToolGateway(Protocol):
    def invoke(self, request: ToolRequest | Mapping[str, object]) -> ToolResult: ...


__all__ = ["ToolAdapter", "ToolGateway"]
