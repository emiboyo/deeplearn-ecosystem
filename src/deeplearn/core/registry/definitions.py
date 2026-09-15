"""Immutable, provider-neutral Agent Definition representation."""

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
import re

from deeplearn.core.registry.errors import DefinitionValidationError


IDENTIFIER_PATTERN = re.compile(r"^[a-z][a-z0-9_.:-]{2,127}$")
SEMANTIC_VERSION_PATTERN = re.compile(r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$")
CONTRACT_REFERENCE_PATTERN = re.compile(
    r"^contracts/v[1-9][0-9]*/[a-z0-9_./-]+\.schema\.json$"
)


class Lifecycle(StrEnum):
    DRAFT = "draft"
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    RETIRED = "retired"


class AutonomyLevel(StrEnum):
    ASSIST = "assist"
    RECOMMEND = "recommend"
    PREPARE = "prepare"
    EXECUTE = "execute"


class ModelCapability(StrEnum):
    """Provider-neutral model capabilities supported for M1.3."""

    TEXT_GENERATION = "text_generation"


def _error(message: str) -> DefinitionValidationError:
    return DefinitionValidationError(message)


def _require_identifier(value: object, field: str) -> str:
    if not isinstance(value, str) or not IDENTIFIER_PATTERN.fullmatch(value):
        raise _error(f"{field} must be a controlled identifier")
    return value


def _require_string(value: object, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise _error(f"{field} must be a non-empty string")
    if len(value) > 512:
        raise _error(f"{field} must not exceed 512 characters")
    return value


def _require_identifier_tuple(value: object, field: str, *, non_empty: bool = False) -> tuple[str, ...]:
    if isinstance(value, (str, bytes)) or not isinstance(value, Sequence):
        raise _error(f"{field} must be an array of controlled identifiers")
    items = tuple(_require_identifier(item, field) for item in value)
    if non_empty and not items:
        raise _error(f"{field} must not be empty")
    if len(items) != len(set(items)):
        raise _error(f"{field} must not contain duplicates")
    return items


def _expect_fields(document: Mapping[str, object], expected: set[str], context: str) -> None:
    missing = expected - document.keys()
    extra = document.keys() - expected
    if missing:
        raise _error(f"{context} missing fields: {', '.join(sorted(missing))}")
    if extra:
        raise _error(f"{context} has unsupported fields: {', '.join(sorted(extra))}")


@dataclass(frozen=True, slots=True)
class ExecutionLimits:
    max_steps: int
    max_duration_ms: int
    max_cost_units: int | float

    def __post_init__(self) -> None:
        if type(self.max_steps) is not int or self.max_steps < 1:
            raise _error("execution_limits.max_steps must be a positive integer")
        if type(self.max_duration_ms) is not int or self.max_duration_ms < 1:
            raise _error("execution_limits.max_duration_ms must be a positive integer")
        if isinstance(self.max_cost_units, bool) or not isinstance(self.max_cost_units, (int, float)) or self.max_cost_units < 0:
            raise _error("execution_limits.max_cost_units must be a non-negative number")


@dataclass(frozen=True, slots=True)
class ModelRequirements:
    capabilities: tuple[ModelCapability, ...]

    def __post_init__(self) -> None:
        identifiers = _require_identifier_tuple(
            self.capabilities, "model_requirements.capabilities", non_empty=True
        )
        try:
            capabilities = tuple(ModelCapability(item) for item in identifiers)
        except ValueError as exc:
            raise _error("model_requirements.capabilities contains an unsupported capability") from exc
        object.__setattr__(self, "capabilities", capabilities)


@dataclass(frozen=True, slots=True)
class AgentDefinition:
    schema_version: str
    agent_id: str
    version: str
    owner: str
    purpose: str
    lifecycle: Lifecycle
    input_contract_ref: str
    output_contract_ref: str
    allowed_tools: tuple[str, ...]
    allowed_purposes: tuple[str, ...]
    required_scopes: tuple[str, ...]
    autonomy: AutonomyLevel
    execution_limits: ExecutionLimits
    model_requirements: ModelRequirements
    created_at: str

    def __post_init__(self) -> None:
        if self.schema_version != "1.0":
            raise _error("schema_version must be 1.0")
        _require_identifier(self.agent_id, "agent_id")
        if not isinstance(self.version, str) or not SEMANTIC_VERSION_PATTERN.fullmatch(self.version):
            raise _error("version must be an explicit semantic version")
        _require_identifier(self.owner, "owner")
        _require_string(self.purpose, "purpose")
        if not isinstance(self.lifecycle, Lifecycle):
            raise _error("lifecycle must be a supported value")
        for value, field in (
            (self.input_contract_ref, "input_contract_ref"),
            (self.output_contract_ref, "output_contract_ref"),
        ):
            if not isinstance(value, str) or not CONTRACT_REFERENCE_PATTERN.fullmatch(value):
                raise _error(f"{field} must be a versioned JSON Schema reference")
        for value, field, non_empty in (
            (self.allowed_tools, "allowed_tools", False),
            (self.allowed_purposes, "allowed_purposes", True),
            (self.required_scopes, "required_scopes", False),
        ):
            validated = _require_identifier_tuple(value, field, non_empty=non_empty)
            object.__setattr__(self, field, validated)
        if not isinstance(self.autonomy, AutonomyLevel):
            raise _error("autonomy must be a supported value")
        if not isinstance(self.execution_limits, ExecutionLimits):
            raise _error("execution_limits must be structured limits")
        if not isinstance(self.model_requirements, ModelRequirements):
            raise _error("model_requirements must be provider-neutral capabilities")
        try:
            timestamp = datetime.fromisoformat(self.created_at.replace("Z", "+00:00"))
        except (AttributeError, ValueError) as exc:
            raise _error("created_at must be an ISO 8601 timestamp") from exc
        if timestamp.tzinfo is None:
            raise _error("created_at must include a timezone")

    @classmethod
    def from_mapping(cls, document: Mapping[str, object]) -> "AgentDefinition":
        expected = {
            "schema_version", "agent_id", "version", "owner", "purpose", "lifecycle",
            "input_contract_ref", "output_contract_ref", "allowed_tools", "allowed_purposes",
            "required_scopes", "autonomy", "execution_limits", "model_requirements", "created_at",
        }
        _expect_fields(document, expected, "agent definition")

        limits = document["execution_limits"]
        if not isinstance(limits, Mapping):
            raise _error("execution_limits must be an object")
        _expect_fields(limits, {"max_steps", "max_duration_ms", "max_cost_units"}, "execution_limits")

        model = document["model_requirements"]
        if not isinstance(model, Mapping):
            raise _error("model_requirements must be an object")
        _expect_fields(model, {"capabilities"}, "model_requirements")

        try:
            lifecycle = Lifecycle(document["lifecycle"])
        except (TypeError, ValueError) as exc:
            raise _error("lifecycle must be one of draft, active, deprecated, retired") from exc
        try:
            autonomy = AutonomyLevel(document["autonomy"])
        except (TypeError, ValueError) as exc:
            raise _error("autonomy must be one of assist, recommend, prepare, execute") from exc

        return cls(
            schema_version=document["schema_version"],
            agent_id=document["agent_id"],
            version=document["version"],
            owner=document["owner"],
            purpose=document["purpose"],
            lifecycle=lifecycle,
            input_contract_ref=document["input_contract_ref"],
            output_contract_ref=document["output_contract_ref"],
            allowed_tools=_require_identifier_tuple(document["allowed_tools"], "allowed_tools"),
            allowed_purposes=_require_identifier_tuple(document["allowed_purposes"], "allowed_purposes", non_empty=True),
            required_scopes=_require_identifier_tuple(document["required_scopes"], "required_scopes"),
            autonomy=autonomy,
            execution_limits=ExecutionLimits(
                max_steps=limits["max_steps"],
                max_duration_ms=limits["max_duration_ms"],
                max_cost_units=limits["max_cost_units"],
            ),
            model_requirements=ModelRequirements(
                capabilities=_require_identifier_tuple(model["capabilities"], "model_requirements.capabilities", non_empty=True)
            ),
            created_at=document["created_at"],
        )


__all__ = [
    "AgentDefinition",
    "AutonomyLevel",
    "ExecutionLimits",
    "Lifecycle",
    "ModelCapability",
    "ModelRequirements",
]
