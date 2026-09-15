"""Deterministic, offline model adapter used only for tests."""

from enum import StrEnum

from deeplearn.core.contracts import ModelCapability
from .contracts import AdapterResponse, ModelRequest, ModelUsage
from .errors import ProviderTimeoutError, ProviderUnavailableError


class FakeFailure(StrEnum):
    UNAVAILABLE = "unavailable"
    FAILURE = "failure"
    TIMEOUT = "timeout"


class DeterministicFakeAdapter:
    """Return synthetic text, usage, and latency without network access."""

    def __init__(
        self,
        *,
        provider_id: str = "test.fake",
        model_id: str = "test.fake-text",
        model_version: str = "1.0.0",
        prefix: str = "fake:",
        latency_ms: int = 7,
        supported_capabilities: frozenset[ModelCapability] | None = None,
        failure: FakeFailure | None = None,
    ) -> None:
        self.provider_id = provider_id
        self.model_id = model_id
        self.model_version = model_version
        self.prefix = prefix
        self.latency_ms = latency_ms
        self.supported_capabilities = (
            frozenset({ModelCapability.TEXT_GENERATION})
            if supported_capabilities is None
            else supported_capabilities
        )
        self.failure = failure

    def invoke(self, request: ModelRequest) -> AdapterResponse:
        if self.failure is FakeFailure.UNAVAILABLE:
            raise ProviderUnavailableError("synthetic provider unavailable")
        if self.failure is FakeFailure.TIMEOUT:
            raise ProviderTimeoutError("synthetic provider timeout")
        if self.failure is FakeFailure.FAILURE:
            raise RuntimeError("raw synthetic adapter detail must not escape")

        output = f"{self.prefix}{request.input}"[: request.max_output_units]
        usage = ModelUsage(
            input_units=len(request.input),
            output_units=len(output),
            total_units=len(request.input) + len(output),
        )
        return AdapterResponse(output=output, usage=usage, latency_ms=self.latency_ms)


__all__ = ["DeterministicFakeAdapter", "FakeFailure"]
