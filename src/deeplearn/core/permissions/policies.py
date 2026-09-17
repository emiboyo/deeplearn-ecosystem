"""Narrow immutable synthetic policy and process-local registry for M1.6."""

from dataclasses import dataclass
import re

from .errors import DuplicatePolicyError, PolicyEvaluationError, PolicyValidationError


IDENTIFIER_PATTERN = re.compile(r"^[a-z][a-z0-9_.:-]{2,127}$")
SEMANTIC_VERSION_PATTERN = re.compile(
    r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$"
)


def _identifiers(values: tuple[str, ...], field: str) -> tuple[str, ...]:
    if not values:
        raise PolicyValidationError(f"{field} must not be empty")
    if any(not IDENTIFIER_PATTERN.fullmatch(value) for value in values):
        raise PolicyValidationError(f"{field} contains an invalid identifier")
    if len(values) != len(set(values)):
        raise PolicyValidationError(f"{field} must not contain duplicates")
    return values


@dataclass(frozen=True, slots=True)
class ToolPermissionPolicy:
    policy_id: str
    version: str
    tool_id: str
    tool_version: str
    allowed_actions: tuple[str, ...]
    required_scopes: tuple[str, ...]
    allowed_purposes: tuple[str, ...]
    consequential_allowed: bool
    same_tenant: bool
    synthetic_error: bool = False

    def __post_init__(self) -> None:
        for value, field in (
            (self.policy_id, "policy_id"),
            (self.tool_id, "tool_id"),
        ):
            if not IDENTIFIER_PATTERN.fullmatch(value):
                raise PolicyValidationError(f"{field} must be a controlled identifier")
        for value, field in (
            (self.version, "version"),
            (self.tool_version, "tool_version"),
        ):
            if not SEMANTIC_VERSION_PATTERN.fullmatch(value):
                raise PolicyValidationError(f"{field} must be a semantic version")
        object.__setattr__(
            self, "allowed_actions", _identifiers(self.allowed_actions, "allowed_actions")
        )
        object.__setattr__(
            self, "required_scopes", _identifiers(self.required_scopes, "required_scopes")
        )
        object.__setattr__(
            self,
            "allowed_purposes",
            _identifiers(self.allowed_purposes, "allowed_purposes"),
        )
        for value, field in (
            (self.consequential_allowed, "consequential_allowed"),
            (self.same_tenant, "same_tenant"),
            (self.synthetic_error, "synthetic_error"),
        ):
            if type(value) is not bool:
                raise PolicyValidationError(f"{field} must be a boolean")

    def ensure_evaluable(self) -> None:
        if self.synthetic_error:
            raise PolicyEvaluationError("raw synthetic policy detail must not escape")


class InMemoryPolicyRegistry:
    def __init__(self) -> None:
        self._policies: dict[tuple[str, str], ToolPermissionPolicy] = {}

    def register(self, policy: ToolPermissionPolicy) -> None:
        key = (policy.tool_id, policy.tool_version)
        if key in self._policies:
            raise DuplicatePolicyError(
                f"policy already registered for {policy.tool_id}@{policy.tool_version}"
            )
        self._policies[key] = policy

    def resolve(self, tool_id: str, tool_version: str) -> ToolPermissionPolicy | None:
        return self._policies.get((tool_id, tool_version))


def safe_echo_policy(*, synthetic_error: bool = False) -> ToolPermissionPolicy:
    return ToolPermissionPolicy(
        policy_id="test.safe_echo.invoke",
        version="1.0.0",
        tool_id="test.safe_echo",
        tool_version="1.0.0",
        allowed_actions=("test.safe_tool.invoke",),
        required_scopes=("test.safe_tool.invoke",),
        allowed_purposes=("test.execute_safe_tool",),
        consequential_allowed=False,
        same_tenant=True,
        synthetic_error=synthetic_error,
    )


__all__ = ["InMemoryPolicyRegistry", "ToolPermissionPolicy", "safe_echo_policy"]
