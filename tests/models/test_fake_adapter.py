"""Offline tests for the deterministic M1.4 fake model adapter."""

from deeplearn.core.contracts import ModelCapability
from deeplearn.core.models import DeterministicFakeAdapter, ModelRequest


def _request() -> ModelRequest:
    return ModelRequest(
        request_id="model_req_0001",
        capability=ModelCapability.TEXT_GENERATION,
        input="hello",
        correlation_id="corr_model_0001",
        trace_id="trace_model_0001",
        timeout_ms=1000,
        max_output_units=100,
    )


def test_valid_provider_neutral_request() -> None:
    request = _request()
    assert request.capability is ModelCapability.TEXT_GENERATION
    assert request.input == "hello"


def test_fake_adapter_is_deterministic() -> None:
    adapter = DeterministicFakeAdapter()
    first = adapter.invoke(_request())
    second = adapter.invoke(_request())
    assert first == second
    assert first.output == "fake:hello"


def test_fake_usage_is_synthetic_and_deterministic() -> None:
    response = DeterministicFakeAdapter().invoke(_request())
    assert response.usage.input_units == len("hello")
    assert response.usage.output_units == len("fake:hello")
    assert response.usage.total_units == len("hello") + len("fake:hello")


def test_fake_latency_is_synthetic_and_not_wall_clock_timing() -> None:
    response = DeterministicFakeAdapter(latency_ms=11).invoke(_request())
    assert response.latency_ms == 11
