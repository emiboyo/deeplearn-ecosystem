"""Safety and normalized-failure tests for M1.5 tool dispatch."""

import json
from pathlib import Path

import pytest

from deeplearn.core.tools import (
    AdapterResponse,
    InMemoryToolRegistry,
    SafeEchoAdapter,
    SafeEchoFailure,
    SideEffectClass,
    ToolDispatcher,
    ToolFailure,
    ToolFailureCategory,
    ToolRequest,
    ToolResult,
    ToolStatus,
)


ROOT = Path(__file__).parents[2]
FIXTURE = ROOT / "fixtures" / "m1" / "tools" / "test.safe_echo-1.0.0.json"
WIRE_REQUEST_FIXTURE = ROOT / "fixtures" / "m1" / "success" / "tool-request.json"


def request(*, tool_id: str = "test.safe_echo", version: str = "1.0.0", arguments=None):
    return ToolRequest(
        tool_request_id="toolreq_test_0001",
        tool_id=tool_id,
        tool_version=version,
        arguments={"value": "synthetic hello"} if arguments is None else arguments,
        correlation_id="corr_test_0001",
        trace_id="trace_tool_0001",
        timeout_ms=1000,
    )


def dispatcher(failure: SafeEchoFailure | None = None):
    adapter = SafeEchoAdapter(failure=failure)
    registry = InMemoryToolRegistry()
    registry.register(json.loads(FIXTURE.read_text(encoding="utf-8")), adapter)
    return ToolDispatcher(registry), adapter


def test_valid_safe_echo_invocation() -> None:
    gateway, adapter = dispatcher()
    result = gateway.invoke(request())
    assert result.status is ToolStatus.SUCCEEDED
    assert dict(result.output) == {"message": "synthetic hello"}
    assert result.side_effect is SideEffectClass.NONE
    assert adapter.invocation_count == 1


def test_canonical_m1_tool_request_envelope_is_accepted() -> None:
    gateway, adapter = dispatcher()
    wire_request = json.loads(WIRE_REQUEST_FIXTURE.read_text(encoding="utf-8"))
    result_value = gateway.invoke(wire_request)
    assert result_value.status is ToolStatus.SUCCEEDED
    assert dict(result_value.output) == {"message": "synthetic hello"}
    assert adapter.invocation_count == 1


def test_malformed_request_is_normalized_before_adapter_invocation() -> None:
    gateway, adapter = dispatcher()
    result = gateway.invoke({"tool_request_id": "toolreq_test_0001"})
    assert result.failure.category is ToolFailureCategory.INVALID_TOOL_REQUEST
    assert adapter.invocation_count == 0


@pytest.mark.parametrize("arguments", [{}, {"wrong": "value"}, {"value": 1}, {"value": ""}])
def test_malformed_arguments_are_rejected_before_invocation(arguments) -> None:
    gateway, adapter = dispatcher()
    result = gateway.invoke(request(arguments=arguments))
    assert result.failure.category is ToolFailureCategory.INVALID_TOOL_REQUEST
    assert adapter.invocation_count == 0


def test_oversized_input_is_rejected_before_invocation() -> None:
    gateway, adapter = dispatcher()
    result = gateway.invoke(request(arguments={"value": "x" * 257}))
    assert result.failure.category is ToolFailureCategory.INPUT_TOO_LARGE
    assert adapter.invocation_count == 0


def test_timeout_above_registered_limit_is_rejected_before_invocation() -> None:
    gateway, adapter = dispatcher()
    oversized_timeout = request()
    oversized_timeout = ToolRequest(
        tool_request_id=oversized_timeout.tool_request_id,
        tool_id=oversized_timeout.tool_id,
        tool_version=oversized_timeout.tool_version,
        arguments=oversized_timeout.arguments,
        correlation_id=oversized_timeout.correlation_id,
        trace_id=oversized_timeout.trace_id,
        timeout_ms=1001,
    )
    result_value = gateway.invoke(oversized_timeout)
    assert result_value.failure.category is ToolFailureCategory.INVALID_TOOL_REQUEST
    assert adapter.invocation_count == 0


def test_unknown_tool_does_not_invoke_registered_adapter() -> None:
    gateway, adapter = dispatcher()
    result = gateway.invoke(request(tool_id="test.unknown"))
    assert result.failure.category is ToolFailureCategory.TOOL_NOT_REGISTERED
    assert adapter.invocation_count == 0


def test_unknown_version_does_not_invoke_registered_adapter() -> None:
    gateway, adapter = dispatcher()
    result = gateway.invoke(request(version="9.9.9"))
    assert result.failure.category is ToolFailureCategory.TOOL_VERSION_NOT_FOUND
    assert adapter.invocation_count == 0


@pytest.mark.parametrize(
    ("mode", "category"),
    [
        (SafeEchoFailure.UNAVAILABLE, ToolFailureCategory.TOOL_UNAVAILABLE),
        (SafeEchoFailure.TIMEOUT, ToolFailureCategory.TOOL_TIMEOUT),
        (SafeEchoFailure.FAILURE, ToolFailureCategory.TOOL_FAILURE),
    ],
)
def test_adapter_failures_are_normalized(mode, category) -> None:
    gateway, adapter = dispatcher(mode)
    result = gateway.invoke(request())
    assert result.failure.category is category
    assert "synthetic" not in result.failure.message
    assert "RuntimeError" not in result.failure.message
    assert adapter.invocation_count == 1


def test_malformed_adapter_output_is_normalized() -> None:
    class MalformedOutputAdapter(SafeEchoAdapter):
        def invoke(self, request_value):
            self.invocation_count += 1
            return AdapterResponse(output={"unexpected": "value"}, latency_ms=5)

    adapter = MalformedOutputAdapter()
    registry = InMemoryToolRegistry()
    registry.register(json.loads(FIXTURE.read_text(encoding="utf-8")), adapter)
    result_value = ToolDispatcher(registry).invoke(request())
    assert result_value.failure.category is ToolFailureCategory.TOOL_FAILURE
    assert adapter.invocation_count == 1


def failure() -> ToolFailure:
    return ToolFailure(
        ToolFailureCategory.TOOL_FAILURE, "tool.failure", "The tool failed.", True
    )


def result(status: ToolStatus, *, output=None, error=None) -> ToolResult:
    return ToolResult(
        tool_request_id="toolreq_test_0001",
        tool_id="test.safe_echo",
        tool_version="1.0.0",
        status=status,
        output=output,
        failure=error,
        latency_ms=0,
        correlation_id="corr_test_0001",
        side_effect=SideEffectClass.NONE,
    )


@pytest.mark.parametrize(
    ("status", "output", "error"),
    [
        (ToolStatus.SUCCEEDED, None, failure()),
        (ToolStatus.FAILED, {"message": "bad"}, None),
        (ToolStatus.SUCCEEDED, None, None),
        (ToolStatus.FAILED, None, None),
        (ToolStatus.SUCCEEDED, {"message": "bad"}, failure()),
    ],
)
def test_result_status_invariants(status, output, error) -> None:
    with pytest.raises(ValueError):
        result(status, output=output, error=error)


def test_valid_success_and_failure_results() -> None:
    assert result(ToolStatus.SUCCEEDED, output={"message": "ok"}).failure is None
    assert result(ToolStatus.FAILED, error=failure()).output is None


def test_tools_source_has_no_external_capability_imports() -> None:
    source = "\n".join(
        path.read_text(encoding="utf-8").lower()
        for path in sorted((ROOT / "src" / "deeplearn" / "core" / "tools").glob("*.py"))
    )
    for forbidden in (
        "import socket", "import urllib", "import requests", "import pathlib",
        "import os", "import subprocess", "import sqlite3", "import openai",
        "import anthropic", "eval(", "exec(",
    ):
        assert forbidden not in source


def test_wire_result_schema_binds_status_to_payload() -> None:
    schema = json.loads(
        (ROOT / "contracts" / "v1" / "tool-result.schema.json").read_text(
            encoding="utf-8"
        )
    )
    success, non_success = schema["oneOf"]
    assert success == {
        "properties": {"status": {"const": "succeeded"}},
        "required": ["result"],
        "not": {"required": ["failure"]},
    }
    assert non_success == {
        "properties": {"status": {"enum": ["failed", "timed_out", "denied"]}},
        "required": ["failure"],
        "not": {"required": ["result"]},
    }
