"""Focused M1.4 tests for provider-neutral deterministic routing."""

import json
from pathlib import Path

import pytest

from deeplearn.core.contracts import ModelCapability
from deeplearn.core.models import (
    DeterministicFakeAdapter,
    DuplicateAdapterError,
    FakeFailure,
    ModelFailureCategory,
    ModelRequest,
    ModelRouter,
    ModelStatus,
)


ROOT = Path(__file__).parents[2]


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


def _result(adapter: DeterministicFakeAdapter | None = None):
    router = ModelRouter()
    router.register(adapter or DeterministicFakeAdapter())
    return router.complete(_request())


def test_router_records_selected_provider_model_and_version() -> None:
    result = _result()
    assert result.status is ModelStatus.SUCCEEDED
    assert (result.provider_id, result.model_id, result.model_version) == (
        "test.fake", "test.fake-text", "1.0.0"
    )
    assert result.correlation_id == "corr_model_0001"
    assert result.trace_id == "trace_model_0001"


def test_first_registered_eligible_adapter_is_selected() -> None:
    router = ModelRouter()
    router.register(DeterministicFakeAdapter(provider_id="test.first", prefix="first:"))
    router.register(DeterministicFakeAdapter(provider_id="test.second", prefix="second:"))
    result = router.complete(_request())
    assert result.provider_id == "test.first"
    assert result.output == "first:hello"


def test_unsupported_capability_is_normalized() -> None:
    router = ModelRouter()
    router.register(DeterministicFakeAdapter(supported_capabilities=frozenset()))
    result = router.complete(_request())
    assert result.failure is not None
    assert result.failure.category is ModelFailureCategory.UNSUPPORTED_CAPABILITY
    assert not result.failure.retryable


def test_provider_unavailable_is_normalized() -> None:
    result = _result(DeterministicFakeAdapter(failure=FakeFailure.UNAVAILABLE))
    assert result.failure is not None
    assert result.failure.category is ModelFailureCategory.PROVIDER_UNAVAILABLE
    assert result.failure.retryable
    assert result.provider_id == "test.fake"


def test_no_registered_provider_is_unavailable() -> None:
    result = ModelRouter().complete(_request())
    assert result.failure is not None
    assert result.failure.category is ModelFailureCategory.PROVIDER_UNAVAILABLE
    assert result.provider_id is None


def test_provider_failure_is_normalized_without_raw_exception() -> None:
    result = _result(DeterministicFakeAdapter(failure=FakeFailure.FAILURE))
    assert result.failure is not None
    assert result.failure.category is ModelFailureCategory.PROVIDER_FAILURE
    assert "raw synthetic" not in result.failure.message
    assert "RuntimeError" not in result.failure.message


def test_provider_timeout_is_normalized() -> None:
    result = _result(DeterministicFakeAdapter(failure=FakeFailure.TIMEOUT))
    assert result.failure is not None
    assert result.failure.category is ModelFailureCategory.PROVIDER_TIMEOUT
    assert result.failure.retryable


def test_invalid_request_is_normalized() -> None:
    result = ModelRouter().complete({"request_id": "model_req_0001"})
    assert result.failure is not None
    assert result.failure.category is ModelFailureCategory.INVALID_MODEL_REQUEST
    assert result.failure.code == "model.invalid_request"


def test_duplicate_provider_model_registration_is_rejected() -> None:
    router = ModelRouter()
    router.register(DeterministicFakeAdapter())
    with pytest.raises(DuplicateAdapterError):
        router.register(DeterministicFakeAdapter())


def test_provider_substitution_preserves_request_and_router_contract() -> None:
    request = _request()
    first_router = ModelRouter()
    first_router.register(DeterministicFakeAdapter())
    second_router = ModelRouter()
    second_router.register(
        DeterministicFakeAdapter(
            provider_id="test.alternative",
            model_id="test.alternative-text",
            prefix="alternative:",
        )
    )

    first = first_router.complete(request)
    second = second_router.complete(request)

    assert first.status is second.status is ModelStatus.SUCCEEDED
    assert first.request_id == second.request_id == request.request_id
    assert first.provider_id != second.provider_id
    assert first.model_id != second.model_id


def test_models_source_has_no_provider_sdk_or_provider_specific_type_leaks() -> None:
    models_root = ROOT / "src" / "deeplearn" / "core" / "models"
    source = "\n".join(
        path.read_text(encoding="utf-8").lower()
        for path in sorted(models_root.glob("*.py"))
    )
    for provider_term in ("import openai", "import anthropic", "import google", "api_key"):
        assert provider_term not in source


def test_model_wire_contracts_are_provider_neutral_and_controlled() -> None:
    contract_root = ROOT / "contracts" / "v1"
    request_schema = json.loads(
        (contract_root / "model-request.schema.json").read_text(encoding="utf-8")
    )
    error_schema = json.loads(
        (contract_root / "model-error.schema.json").read_text(encoding="utf-8")
    )
    result_schema = json.loads(
        (contract_root / "model-result.schema.json").read_text(encoding="utf-8")
    )

    assert request_schema["properties"]["capability"] == {"enum": ["text_generation"]}
    assert "provider_id" not in request_schema["properties"]
    assert set(error_schema["properties"]["category"]["enum"]) == {
        category.value for category in ModelFailureCategory
    }
    assert {"provider_id", "model_id", "model_version", "latency_ms", "usage"} <= set(
        result_schema["required"]
    )
