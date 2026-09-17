"""Deny-by-default permission-decision boundary."""

from .contracts import (
    DecisionOutcome,
    DecisionReason,
    DelegatedAuthority,
    PermissionDecision,
    PermissionRequest,
    PrincipalContext,
    PrincipalType,
    ReasonCode,
)
from .errors import (
    DuplicatePolicyError,
    PermissionRequestValidationError,
    PolicyEvaluationError,
    PolicyValidationError,
)
from .evaluator import DenyByDefaultPermissionEvaluator
from .interfaces import PermissionEvaluator
from .policies import InMemoryPolicyRegistry, ToolPermissionPolicy, safe_echo_policy

__all__ = [
    "DecisionOutcome",
    "DecisionReason",
    "DelegatedAuthority",
    "DenyByDefaultPermissionEvaluator",
    "DuplicatePolicyError",
    "InMemoryPolicyRegistry",
    "PermissionDecision",
    "PermissionEvaluator",
    "PermissionRequest",
    "PermissionRequestValidationError",
    "PolicyEvaluationError",
    "PolicyValidationError",
    "PrincipalContext",
    "PrincipalType",
    "ReasonCode",
    "ToolPermissionPolicy",
    "safe_echo_policy",
]
