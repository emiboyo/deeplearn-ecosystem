"""Immutable normalized Python contracts for tool dispatch."""

from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum
from types import MappingProxyType
import re

from .definitions import SideEffectClass

IDENTIFIER_PATTERN = re.compile(r"^[a-z][a-z0-9_.:-]{2,127}$")
SEMANTIC_VERSION_PATTERN = re.compile(r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$")

class InvalidToolRequestError(ValueError): pass
class ToolStatus(StrEnum):
    SUCCEEDED = "succeeded"
    FAILED = "failed"
class ToolFailureCategory(StrEnum):
    INVALID_TOOL_REQUEST = "invalid_tool_request"
    TOOL_NOT_REGISTERED = "tool_not_registered"
    TOOL_VERSION_NOT_FOUND = "tool_version_not_found"
    TOOL_UNAVAILABLE = "tool_unavailable"
    TOOL_TIMEOUT = "tool_timeout"
    TOOL_FAILURE = "tool_failure"
    INPUT_TOO_LARGE = "input_too_large"

def _bounded_id(value: object, field: str) -> str:
    if not isinstance(value, str) or not 8 <= len(value) <= 128: raise InvalidToolRequestError(f"{field} must be an opaque identifier of 8-128 characters")
    return value

@dataclass(frozen=True, slots=True)
class ToolRequest:
    tool_request_id: str
    tool_id: str
    tool_version: str
    arguments: Mapping[str, object]
    correlation_id: str
    timeout_ms: int
    trace_id: str | None = None
    schema_version: str = "1.0"
    def __post_init__(self) -> None:
        if self.schema_version != "1.0": raise InvalidToolRequestError("schema_version must be 1.0")
        _bounded_id(self.tool_request_id, "tool_request_id"); _bounded_id(self.correlation_id, "correlation_id")
        if self.trace_id is not None: _bounded_id(self.trace_id, "trace_id")
        if not isinstance(self.tool_id, str) or not IDENTIFIER_PATTERN.fullmatch(self.tool_id): raise InvalidToolRequestError("tool_id must be a controlled identifier")
        if not isinstance(self.tool_version, str) or not SEMANTIC_VERSION_PATTERN.fullmatch(self.tool_version): raise InvalidToolRequestError("tool_version must be an explicit semantic version")
        if not isinstance(self.arguments, Mapping): raise InvalidToolRequestError("arguments must be an object")
        object.__setattr__(self, "arguments", MappingProxyType(dict(self.arguments)))
        if type(self.timeout_ms) is not int or self.timeout_ms < 1: raise InvalidToolRequestError("timeout_ms must be a positive integer")
    @classmethod
    def from_mapping(cls, document: Mapping[str, object]) -> "ToolRequest":
        wire_expected = {
            "schema_version", "tool_request_id", "execution_id", "tool_id",
            "tool_version", "arguments", "principal_context", "requested_action",
            "purpose", "consequential", "approval", "correlation_id", "trace_id",
            "causation_id", "idempotency_key", "limits",
        }
        wire_required = {
            "schema_version", "tool_request_id", "execution_id", "tool_id",
            "tool_version", "arguments", "principal_context", "requested_action",
            "purpose", "consequential", "correlation_id", "idempotency_key",
        }
        normalized_expected = {
            "schema_version", "tool_request_id", "tool_id", "tool_version", "arguments",
            "correlation_id", "trace_id", "timeout_ms",
        }
        is_wire = "execution_id" in document or "limits" in document
        expected = wire_expected if is_wire else normalized_expected
        required = wire_required if is_wire else normalized_expected - {"trace_id"}
        missing, extra = required - document.keys(), document.keys() - expected
        if missing: raise InvalidToolRequestError(f"tool request missing fields: {', '.join(sorted(missing))}")
        if extra: raise InvalidToolRequestError(f"tool request has unsupported fields: {', '.join(sorted(extra))}")
        if is_wire:
            limits = document.get("limits", {})
            if not isinstance(limits, Mapping) or "timeout_ms" not in limits:
                raise InvalidToolRequestError("limits.timeout_ms must be present")
            timeout_ms = limits["timeout_ms"]
        else:
            timeout_ms = document["timeout_ms"]
        return cls(schema_version=document["schema_version"], tool_request_id=document["tool_request_id"], tool_id=document["tool_id"], tool_version=document["tool_version"], arguments=document["arguments"], correlation_id=document["correlation_id"], trace_id=document.get("trace_id"), timeout_ms=timeout_ms)

@dataclass(frozen=True, slots=True)
class AdapterResponse:
    output: Mapping[str, object]
    latency_ms: int
    def __post_init__(self) -> None:
        if not isinstance(self.output, Mapping): raise ValueError("adapter output must be an object")
        object.__setattr__(self, "output", MappingProxyType(dict(self.output)))
        if type(self.latency_ms) is not int or self.latency_ms < 0: raise ValueError("adapter latency_ms must be a non-negative integer")

@dataclass(frozen=True, slots=True)
class ToolFailure:
    category: ToolFailureCategory
    code: str
    message: str
    retryable: bool

@dataclass(frozen=True, slots=True)
class ToolResult:
    tool_request_id: str
    tool_id: str
    tool_version: str
    status: ToolStatus
    latency_ms: int
    correlation_id: str
    side_effect: SideEffectClass
    trace_id: str | None = None
    output: Mapping[str, object] | None = None
    failure: ToolFailure | None = None
    schema_version: str = "1.0"
    def __post_init__(self) -> None:
        if self.status is ToolStatus.SUCCEEDED:
            if self.output is None or self.failure is not None: raise ValueError("a succeeded tool result requires output and prohibits failure")
        elif self.status is ToolStatus.FAILED:
            if self.failure is None or self.output is not None: raise ValueError("a failed tool result requires failure and prohibits output")
        else: raise ValueError("status must be a supported ToolStatus")
        if self.output is not None: object.__setattr__(self, "output", MappingProxyType(dict(self.output)))
        if type(self.latency_ms) is not int or self.latency_ms < 0: raise ValueError("latency_ms must be a non-negative integer")

__all__ = ["AdapterResponse", "InvalidToolRequestError", "ToolFailure", "ToolFailureCategory", "ToolRequest", "ToolResult", "ToolStatus"]
