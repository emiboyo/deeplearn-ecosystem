"""Minimal deterministic router for explicitly registered model adapters."""

from collections.abc import Mapping

from .contracts import (
    InvalidModelRequestError,
    ModelFailure,
    ModelFailureCategory,
    ModelRequest,
    ModelResult,
    ModelStatus,
    ZERO_USAGE,
)
from .errors import DuplicateAdapterError, ProviderTimeoutError, ProviderUnavailableError
from .interfaces import ModelAdapter


class ModelRouter:
    """Select the first registered adapter supporting the request capability."""

    def __init__(self) -> None:
        self._adapters: list[ModelAdapter] = []
        self._identities: set[tuple[str, str]] = set()

    def register(self, adapter: ModelAdapter) -> None:
        identity = (adapter.provider_id, adapter.model_id)
        if identity in self._identities:
            raise DuplicateAdapterError(
                f"model adapter already registered: {adapter.provider_id}/{adapter.model_id}"
            )
        self._identities.add(identity)
        self._adapters.append(adapter)

    def complete(self, request: ModelRequest | Mapping[str, object]) -> ModelResult:
        try:
            validated = (
                request if isinstance(request, ModelRequest) else ModelRequest.from_mapping(request)
            )
        except (InvalidModelRequestError, TypeError) as exc:
            return self._invalid_result(request, exc)

        eligible = [
            adapter
            for adapter in self._adapters
            if validated.capability in adapter.supported_capabilities
        ]
        if not self._adapters:
            return self._failure_result(
                validated, None, ModelFailureCategory.PROVIDER_UNAVAILABLE,
                "model.provider_unavailable", "No model provider is available.", True,
            )
        if not eligible:
            return self._failure_result(
                validated, None, ModelFailureCategory.UNSUPPORTED_CAPABILITY,
                "model.unsupported_capability", "No adapter supports the requested capability.", False,
            )

        adapter = eligible[0]
        try:
            response = adapter.invoke(validated)
        except ProviderUnavailableError:
            return self._failure_result(
                validated, adapter, ModelFailureCategory.PROVIDER_UNAVAILABLE,
                "model.provider_unavailable", "The selected model provider is unavailable.", True,
            )
        except ProviderTimeoutError:
            return self._failure_result(
                validated, adapter, ModelFailureCategory.PROVIDER_TIMEOUT,
                "model.provider_timeout", "The selected model provider timed out.", True,
            )
        except Exception:
            return self._failure_result(
                validated, adapter, ModelFailureCategory.PROVIDER_FAILURE,
                "model.provider_failure", "The selected model provider failed.", True,
            )

        return ModelResult(
            request_id=validated.request_id,
            status=ModelStatus.SUCCEEDED,
            output=response.output,
            provider_id=adapter.provider_id,
            model_id=adapter.model_id,
            model_version=adapter.model_version,
            latency_ms=response.latency_ms,
            usage=response.usage,
            correlation_id=validated.correlation_id,
            trace_id=validated.trace_id,
        )

    @staticmethod
    def _failure_result(
        request: ModelRequest,
        adapter: ModelAdapter | None,
        category: ModelFailureCategory,
        code: str,
        message: str,
        retryable: bool,
    ) -> ModelResult:
        return ModelResult(
            request_id=request.request_id,
            status=ModelStatus.FAILED,
            failure=ModelFailure(category, code, message, retryable),
            provider_id=adapter.provider_id if adapter else None,
            model_id=adapter.model_id if adapter else None,
            model_version=adapter.model_version if adapter else None,
            latency_ms=0,
            usage=ZERO_USAGE,
            correlation_id=request.correlation_id,
            trace_id=request.trace_id,
        )

    @staticmethod
    def _invalid_result(
        request: ModelRequest | Mapping[str, object], error: Exception
    ) -> ModelResult:
        request_id = request.get("request_id") if isinstance(request, Mapping) else None
        correlation_id = request.get("correlation_id") if isinstance(request, Mapping) else None
        trace_id = request.get("trace_id") if isinstance(request, Mapping) else None
        return ModelResult(
            request_id=request_id if isinstance(request_id, str) and request_id else "unknown_request",
            status=ModelStatus.FAILED,
            failure=ModelFailure(
                ModelFailureCategory.INVALID_MODEL_REQUEST,
                "model.invalid_request",
                "The model request is invalid.",
                False,
            ),
            provider_id=None,
            model_id=None,
            model_version=None,
            latency_ms=0,
            usage=ZERO_USAGE,
            correlation_id=(
                correlation_id
                if isinstance(correlation_id, str) and correlation_id
                else "unknown_correlation"
            ),
            trace_id=trace_id if isinstance(trace_id, str) and trace_id else None,
        )


__all__ = ["ModelRouter"]
