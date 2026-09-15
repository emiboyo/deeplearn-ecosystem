"""Owned provider-neutral Python contracts for model routing."""

from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum

from deeplearn.core.contracts import ModelCapability


class ModelStatus(StrEnum):
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class ModelFailureCategory(StrEnum):
    UNSUPPORTED_CAPABILITY = "unsupported_capability"
    PROVIDER_UNAVAILABLE = "provider_unavailable"
    PROVIDER_FAILURE = "provider_failure"
    PROVIDER_TIMEOUT = "provider_timeout"
    INVALID_MODEL_REQUEST = "invalid_model_request"


class InvalidModelRequestError(ValueError):
    """Raised when a model request does not satisfy the owned contract."""


def _required_text(
    value: object, field: str, *, minimum: int = 1, maximum: int | None = None
) -> str:
    if not isinstance(value, str) or not value.strip():
        raise InvalidModelRequestError(f"{field} must be a non-empty string")
    if len(value) < minimum or (maximum is not None and len(value) > maximum):
        raise InvalidModelRequestError(f"{field} has an invalid length")
    return value


@dataclass(frozen=True, slots=True)
class ModelRequest:
    request_id: str
    capability: ModelCapability
    input: str
    correlation_id: str
    timeout_ms: int
    max_output_units: int
    trace_id: str | None = None
    schema_version: str = "1.0"

    def __post_init__(self) -> None:
        if self.schema_version != "1.0":
            raise InvalidModelRequestError("schema_version must be 1.0")
        for value, field in (
            (self.request_id, "request_id"),
            (self.correlation_id, "correlation_id"),
        ):
            _required_text(value, field, minimum=8, maximum=128)
        _required_text(self.input, "input", maximum=100000)
        if self.trace_id is not None:
            _required_text(self.trace_id, "trace_id", minimum=8, maximum=128)
        if not isinstance(self.capability, ModelCapability):
            raise InvalidModelRequestError("capability must be a controlled ModelCapability")
        if type(self.timeout_ms) is not int or self.timeout_ms < 1:
            raise InvalidModelRequestError("timeout_ms must be a positive integer")
        if type(self.max_output_units) is not int or self.max_output_units < 1:
            raise InvalidModelRequestError("max_output_units must be a positive integer")

    @classmethod
    def from_mapping(cls, document: Mapping[str, object]) -> "ModelRequest":
        expected = {
            "schema_version", "request_id", "capability", "input", "correlation_id",
            "trace_id", "timeout_ms", "max_output_units",
        }
        required = expected - {"trace_id"}
        missing = required - document.keys()
        extra = document.keys() - expected
        if missing:
            raise InvalidModelRequestError(
                f"model request missing fields: {', '.join(sorted(missing))}"
            )
        if extra:
            raise InvalidModelRequestError(
                f"model request has unsupported fields: {', '.join(sorted(extra))}"
            )
        try:
            capability = ModelCapability(document["capability"])
        except (TypeError, ValueError) as exc:
            raise InvalidModelRequestError("capability is not supported by this contract") from exc
        return cls(
            schema_version=document["schema_version"],
            request_id=document["request_id"],
            capability=capability,
            input=document["input"],
            correlation_id=document["correlation_id"],
            trace_id=document.get("trace_id"),
            timeout_ms=document["timeout_ms"],
            max_output_units=document["max_output_units"],
        )


@dataclass(frozen=True, slots=True)
class ModelUsage:
    input_units: int
    output_units: int
    total_units: int

    def __post_init__(self) -> None:
        values = (self.input_units, self.output_units, self.total_units)
        if any(type(value) is not int or value < 0 for value in values):
            raise ValueError("usage counters must be non-negative integers")
        if self.total_units != self.input_units + self.output_units:
            raise ValueError("total_units must equal input_units plus output_units")


@dataclass(frozen=True, slots=True)
class AdapterResponse:
    output: str
    usage: ModelUsage
    latency_ms: int

    def __post_init__(self) -> None:
        if not isinstance(self.output, str):
            raise ValueError("adapter output must be text")
        if not isinstance(self.usage, ModelUsage):
            raise ValueError("adapter usage must be normalized ModelUsage")
        if type(self.latency_ms) is not int or self.latency_ms < 0:
            raise ValueError("adapter latency_ms must be a non-negative integer")


@dataclass(frozen=True, slots=True)
class ModelFailure:
    category: ModelFailureCategory
    code: str
    message: str
    retryable: bool


@dataclass(frozen=True, slots=True)
class ModelResult:
    request_id: str
    status: ModelStatus
    provider_id: str | None
    model_id: str | None
    model_version: str | None
    latency_ms: int
    usage: ModelUsage
    correlation_id: str
    trace_id: str | None = None
    output: str | None = None
    failure: ModelFailure | None = None
    schema_version: str = "1.0"

    def __post_init__(self) -> None:
        if self.status is ModelStatus.SUCCEEDED:
            if self.output is None or self.failure is not None:
                raise ValueError(
                    "a succeeded model result requires output and prohibits failure"
                )
        elif self.status is ModelStatus.FAILED:
            if self.failure is None or self.output is not None:
                raise ValueError(
                    "a failed model result requires failure and prohibits output"
                )
        else:
            raise ValueError("status must be a supported ModelStatus")
        if type(self.latency_ms) is not int or self.latency_ms < 0:
            raise ValueError("latency_ms must be a non-negative integer")


ZERO_USAGE = ModelUsage(input_units=0, output_units=0, total_units=0)


__all__ = [
    "AdapterResponse", "InvalidModelRequestError", "ModelFailure",
    "ModelFailureCategory", "ModelRequest", "ModelResult", "ModelStatus",
    "ModelUsage", "ZERO_USAGE",
]
