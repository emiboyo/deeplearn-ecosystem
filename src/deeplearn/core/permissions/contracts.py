"""Immutable owned contracts for M1.6 permission evaluation."""

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from enum import StrEnum
import re

from .errors import PermissionRequestValidationError


IDENTIFIER_PATTERN = re.compile(r"^[a-z][a-z0-9_.:-]{2,127}$")
SEMANTIC_VERSION_PATTERN = re.compile(
    r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$"
)


class PrincipalType(StrEnum):
    HUMAN = "human"
    SERVICE = "service"


class DecisionOutcome(StrEnum):
    ALLOW = "allow"
    DENY = "deny"


class ReasonCode(StrEnum):
    ALLOWED = "allowed"
    UNAUTHENTICATED = "unauthenticated"
    WRONG_TENANT = "wrong_tenant"
    WRONG_PRODUCT = "wrong_product"
    MISSING_SCOPE = "missing_scope"
    PURPOSE_NOT_ALLOWED = "purpose_not_allowed"
    ACTION_NOT_ALLOWED = "action_not_allowed"
    CONSEQUENTIAL_NOT_ALLOWED = "consequential_not_allowed"
    POLICY_NOT_FOUND = "policy_not_found"
    POLICY_ERROR = "policy_error"
    MALFORMED_PERMISSION_REQUEST = "malformed_permission_request"


def _identifier(value: object, field: str) -> str:
    if not isinstance(value, str) or not IDENTIFIER_PATTERN.fullmatch(value):
        raise PermissionRequestValidationError(
            f"{field} must be a controlled identifier"
        )
    return value


def _identifiers(value: object, field: str) -> tuple[str, ...]:
    if isinstance(value, (str, bytes)) or not isinstance(value, Sequence):
        raise PermissionRequestValidationError(
            f"{field} must be an array of controlled identifiers"
        )
    result = tuple(_identifier(item, field) for item in value)
    if len(result) != len(set(result)):
        raise PermissionRequestValidationError(f"{field} must not contain duplicates")
    return result


def _opaque_id(value: object, field: str) -> str:
    if not isinstance(value, str) or not 8 <= len(value) <= 128:
        raise PermissionRequestValidationError(
            f"{field} must be an opaque identifier of 8-128 characters"
        )
    return value


@dataclass(frozen=True, slots=True)
class DelegatedAuthority:
    originating_principal_reference: str
    delegable_scopes: tuple[str, ...]
    effective_scopes: tuple[str, ...]

    def __post_init__(self) -> None:
        if (
            not isinstance(self.originating_principal_reference, str)
            or len(self.originating_principal_reference) < 3
        ):
            raise PermissionRequestValidationError(
                "originating_principal_reference must be present"
            )
        object.__setattr__(
            self, "delegable_scopes", _identifiers(self.delegable_scopes, "delegable_scopes")
        )
        object.__setattr__(
            self, "effective_scopes", _identifiers(self.effective_scopes, "effective_scopes")
        )


@dataclass(frozen=True, slots=True)
class PrincipalContext:
    authenticated: bool
    principal_type: PrincipalType
    principal_id: str
    tenant_id: str
    product_id: str
    scopes: tuple[str, ...]
    delegated_authority: DelegatedAuthority | None = None

    def __post_init__(self) -> None:
        if type(self.authenticated) is not bool:
            raise PermissionRequestValidationError("authenticated must be a boolean")
        if not isinstance(self.principal_type, PrincipalType):
            raise PermissionRequestValidationError(
                "principal_type must be human or service"
            )
        for value, field in (
            (self.principal_id, "principal_id"),
            (self.tenant_id, "tenant_id"),
            (self.product_id, "product_id"),
        ):
            _identifier(value, field)
        object.__setattr__(self, "scopes", _identifiers(self.scopes, "scopes"))
        if self.delegated_authority is not None and not isinstance(
            self.delegated_authority, DelegatedAuthority
        ):
            raise PermissionRequestValidationError(
                "delegated_authority must contain structured authority facts"
            )

    @property
    def reference(self) -> str:
        return f"principal/{self.principal_id}"

    @property
    def effective_scopes(self) -> frozenset[str]:
        principal_scopes = frozenset(self.scopes)
        if self.delegated_authority is None:
            return principal_scopes
        return principal_scopes.intersection(
            self.delegated_authority.delegable_scopes,
            self.delegated_authority.effective_scopes,
        )

    @classmethod
    def from_mapping(cls, document: Mapping[str, object]) -> "PrincipalContext":
        expected = {
            "authenticated", "principal_type", "principal_id", "tenant_id",
            "product_id", "scopes", "delegated_authority",
        }
        required = expected - {"delegated_authority"}
        missing, extra = required - document.keys(), document.keys() - expected
        if missing or extra:
            raise PermissionRequestValidationError(
                "principal context has missing or unsupported fields"
            )
        try:
            principal_type = PrincipalType(document["principal_type"])
        except (TypeError, ValueError) as exc:
            raise PermissionRequestValidationError(
                "principal_type must be human or service"
            ) from exc
        delegated_document = document.get("delegated_authority")
        delegated = None
        if delegated_document is not None:
            if not isinstance(delegated_document, Mapping):
                raise PermissionRequestValidationError(
                    "delegated_authority must be an object"
                )
            delegated_expected = {
                "originating_principal_reference", "delegable_scopes", "effective_scopes"
            }
            if set(delegated_document) != delegated_expected:
                raise PermissionRequestValidationError(
                    "delegated_authority has missing or unsupported fields"
                )
            delegated = DelegatedAuthority(
                originating_principal_reference=delegated_document[
                    "originating_principal_reference"
                ],
                delegable_scopes=_identifiers(
                    delegated_document["delegable_scopes"], "delegable_scopes"
                ),
                effective_scopes=_identifiers(
                    delegated_document["effective_scopes"], "effective_scopes"
                ),
            )
        return cls(
            authenticated=document["authenticated"],
            principal_type=principal_type,
            principal_id=document["principal_id"],
            tenant_id=document["tenant_id"],
            product_id=document["product_id"],
            scopes=_identifiers(document["scopes"], "scopes"),
            delegated_authority=delegated,
        )


@dataclass(frozen=True, slots=True)
class PermissionRequest:
    decision_id: str
    principal: PrincipalContext
    tenant_id: str
    product_id: str
    requested_action: str
    requested_scopes: tuple[str, ...]
    purpose: str
    tool_id: str
    tool_version: str
    consequential: bool
    correlation_id: str
    trace_id: str | None = None
    agent_execution_id: str | None = None

    def __post_init__(self) -> None:
        _opaque_id(self.decision_id, "decision_id")
        if not isinstance(self.principal, PrincipalContext):
            raise PermissionRequestValidationError("principal must be structured")
        for value, field in (
            (self.tenant_id, "tenant_id"),
            (self.product_id, "product_id"),
            (self.requested_action, "requested_action"),
            (self.purpose, "purpose"),
            (self.tool_id, "tool_id"),
        ):
            _identifier(value, field)
        object.__setattr__(
            self,
            "requested_scopes",
            _identifiers(self.requested_scopes, "requested_scopes"),
        )
        if not isinstance(self.tool_version, str) or not SEMANTIC_VERSION_PATTERN.fullmatch(
            self.tool_version
        ):
            raise PermissionRequestValidationError(
                "tool_version must be an explicit semantic version"
            )
        if type(self.consequential) is not bool:
            raise PermissionRequestValidationError("consequential must be a boolean")
        _opaque_id(self.correlation_id, "correlation_id")
        if self.trace_id is not None:
            _opaque_id(self.trace_id, "trace_id")
        if self.agent_execution_id is not None:
            _opaque_id(self.agent_execution_id, "agent_execution_id")

    @classmethod
    def from_mapping(cls, document: Mapping[str, object]) -> "PermissionRequest":
        expected = {
            "decision_id", "principal", "tenant_id", "product_id",
            "requested_action", "requested_scopes", "purpose", "tool_id",
            "tool_version", "consequential", "correlation_id", "trace_id",
            "agent_execution_id",
        }
        required = expected - {"trace_id", "agent_execution_id"}
        missing, extra = required - document.keys(), document.keys() - expected
        if missing or extra:
            raise PermissionRequestValidationError(
                "permission request has missing or unsupported fields"
            )
        principal = document["principal"]
        if not isinstance(principal, Mapping):
            raise PermissionRequestValidationError("principal must be an object")
        return cls(
            decision_id=document["decision_id"],
            principal=PrincipalContext.from_mapping(principal),
            tenant_id=document["tenant_id"],
            product_id=document["product_id"],
            requested_action=document["requested_action"],
            requested_scopes=_identifiers(
                document["requested_scopes"], "requested_scopes"
            ),
            purpose=document["purpose"],
            tool_id=document["tool_id"],
            tool_version=document["tool_version"],
            consequential=document["consequential"],
            correlation_id=document["correlation_id"],
            trace_id=document.get("trace_id"),
            agent_execution_id=document.get("agent_execution_id"),
        )


@dataclass(frozen=True, slots=True)
class DecisionReason:
    code: ReasonCode
    message: str


@dataclass(frozen=True, slots=True)
class PermissionDecision:
    decision_id: str
    decision: DecisionOutcome
    reasons: tuple[DecisionReason, ...]
    policy_id: str
    policy_version: str
    principal_reference: str
    principal_type: PrincipalType | None
    tenant_id: str
    evaluated_action: str
    evaluated_purpose: str
    evaluated_scopes: tuple[str, ...]
    consequential: bool
    correlation_id: str
    trace_id: str | None = None

    def __post_init__(self) -> None:
        if not self.reasons:
            raise ValueError("permission decisions require at least one reason")
        object.__setattr__(
            self,
            "evaluated_scopes",
            tuple(dict.fromkeys(self.evaluated_scopes)),
        )

    @property
    def outcome(self) -> DecisionOutcome:
        return self.decision

    @property
    def reason(self) -> DecisionReason:
        return self.reasons[0]


__all__ = [
    "DecisionOutcome",
    "DecisionReason",
    "DelegatedAuthority",
    "PermissionDecision",
    "PermissionRequest",
    "PrincipalContext",
    "PrincipalType",
    "ReasonCode",
]
