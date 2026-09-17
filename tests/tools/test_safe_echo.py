"""Offline behavior tests for the deterministic safe echo adapter."""

from deeplearn.core.tools import SafeEchoAdapter, ToolRequest


def request(value: str = "synthetic hello") -> ToolRequest:
    return ToolRequest(
        tool_request_id="toolreq_test_0001",
        tool_id="test.safe_echo",
        tool_version="1.0.0",
        arguments={"value": value},
        correlation_id="corr_test_0001",
        trace_id="trace_tool_0001",
        timeout_ms=1000,
    )


def test_safe_echo_is_deterministic_and_bounded() -> None:
    adapter = SafeEchoAdapter(latency_ms=6)
    adapter.validate_arguments(request().arguments, 256)
    first = adapter.invoke(request())
    second = adapter.invoke(request())
    assert first == second
    assert dict(first.output) == {"message": "synthetic hello"}
    assert first.latency_ms == 6
