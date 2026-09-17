"""Immutable declarative tool metadata and validation."""

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
import re

from .errors import ToolDefinitionValidationError

IDENTIFIER_PATTERN = re.compile(r"^[a-z][a-z0-9_.:-]{2,127}$")
SEMANTIC_VERSION_PATTERN = re.compile(r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$")
CONTRACT_REFERENCE_PATTERN = re.compile(r"^contracts/v[1-9][0-9]*/[a-z0-9_./-]+\.schema\.json$")

class ToolLifecycle(StrEnum):
    DRAFT = "draft"
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    RETIRED = "retired"

class RiskClass(StrEnum):
    LOW = "low"

class SideEffectClass(StrEnum):
    NONE = "none"

def _error(message: str) -> ToolDefinitionValidationError:
    return ToolDefinitionValidationError(message)

def _identifier(value: object, field: str) -> str:
    if not isinstance(value, str) or not IDENTIFIER_PATTERN.fullmatch(value):
        raise _error(f"{field} must be a controlled identifier")
    return value

def _identifiers(value: object, field: str) -> tuple[str, ...]:
    if isinstance(value, (str, bytes)) or not isinstance(value, Sequence):
        raise _error(f"{field} must be an array of controlled identifiers")
    items = tuple(_identifier(item, field) for item in value)
    if not items:
        raise _error(f"{field} must not be empty")
    if len(items) != len(set(items)):
        raise _error(f"{field} must not contain duplicates")
    return items

@dataclass(frozen=True, slots=True)
class ToolDefinition:
    schema_version: str
    tool_id: str
    version: str
    owner: str
    purpose: str
    lifecycle: ToolLifecycle
    input_contract_ref: str
    output_contract_ref: str
    required_scopes: tuple[str, ...]
    allowed_purposes: tuple[str, ...]
    risk: RiskClass
    side_effect: SideEffectClass
    timeout_ms: int
    max_input_chars: int
    max_output_chars: int
    idempotent: bool
    consequential: bool
    created_at: str

    def __post_init__(self) -> None:
        if self.schema_version != "1.0": raise _error("schema_version must be 1.0")
        _identifier(self.tool_id, "tool_id")
        if not isinstance(self.version, str) or not SEMANTIC_VERSION_PATTERN.fullmatch(self.version): raise _error("version must be an explicit semantic version")
        _identifier(self.owner, "owner")
        if not isinstance(self.purpose, str) or not self.purpose.strip(): raise _error("purpose must be a non-empty string")
        if not isinstance(self.lifecycle, ToolLifecycle): raise _error("lifecycle must be supported")
        if not isinstance(self.risk, RiskClass): raise _error("risk must be supported")
        if not isinstance(self.side_effect, SideEffectClass): raise _error("side_effect must be supported")
        for value, field in ((self.input_contract_ref, "input_contract_ref"), (self.output_contract_ref, "output_contract_ref")):
            if not isinstance(value, str) or not CONTRACT_REFERENCE_PATTERN.fullmatch(value): raise _error(f"{field} must be a versioned JSON Schema reference")
        object.__setattr__(self, "required_scopes", _identifiers(self.required_scopes, "required_scopes"))
        object.__setattr__(self, "allowed_purposes", _identifiers(self.allowed_purposes, "allowed_purposes"))
        for value, field in ((self.timeout_ms, "timeout_ms"), (self.max_input_chars, "max_input_chars"), (self.max_output_chars, "max_output_chars")):
            if type(value) is not int or value < 1: raise _error(f"{field} must be a positive integer")
        if type(self.idempotent) is not bool: raise _error("idempotent must be a boolean")
        if type(self.consequential) is not bool: raise _error("consequential must be a boolean")
        if not self.idempotent: raise _error("M1.5 tools must be idempotent")
        if self.consequential: raise _error("M1.5 tools must be non-consequential")
        try: timestamp = datetime.fromisoformat(self.created_at.replace("Z", "+00:00"))
        except (AttributeError, ValueError) as exc: raise _error("created_at must be an ISO 8601 timestamp") from exc
        if timestamp.tzinfo is None: raise _error("created_at must include a timezone")

    @classmethod
    def from_mapping(cls, document: Mapping[str, object]) -> "ToolDefinition":
        expected = {"schema_version", "tool_id", "version", "owner", "purpose", "lifecycle", "input_contract_ref", "output_contract_ref", "required_scopes", "allowed_purposes", "risk", "side_effect", "timeout_ms", "max_input_chars", "max_output_chars", "idempotent", "consequential", "created_at"}
        missing, extra = expected - document.keys(), document.keys() - expected
        if missing: raise _error(f"tool definition missing fields: {', '.join(sorted(missing))}")
        if extra: raise _error(f"tool definition has unsupported fields: {', '.join(sorted(extra))}")
        try: lifecycle = ToolLifecycle(document["lifecycle"])
        except (TypeError, ValueError) as exc: raise _error("lifecycle must be one of draft, active, deprecated, retired") from exc
        try: risk = RiskClass(document["risk"])
        except (TypeError, ValueError) as exc: raise _error("risk must be low for M1.5") from exc
        try: side_effect = SideEffectClass(document["side_effect"])
        except (TypeError, ValueError) as exc: raise _error("side_effect must be none for M1.5") from exc
        return cls(schema_version=document["schema_version"], tool_id=document["tool_id"], version=document["version"], owner=document["owner"], purpose=document["purpose"], lifecycle=lifecycle, input_contract_ref=document["input_contract_ref"], output_contract_ref=document["output_contract_ref"], required_scopes=_identifiers(document["required_scopes"], "required_scopes"), allowed_purposes=_identifiers(document["allowed_purposes"], "allowed_purposes"), risk=risk, side_effect=side_effect, timeout_ms=document["timeout_ms"], max_input_chars=document["max_input_chars"], max_output_chars=document["max_output_chars"], idempotent=document["idempotent"], consequential=document["consequential"], created_at=document["created_at"])

__all__ = ["RiskClass", "SideEffectClass", "ToolDefinition", "ToolLifecycle"]
