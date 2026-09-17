"""Internal validation and deterministic policy errors."""


class PermissionRequestValidationError(ValueError):
    """Raised when an owned permission request is malformed."""


class PolicyValidationError(ValueError):
    """Raised when declarative policy metadata is malformed."""


class DuplicatePolicyError(ValueError):
    """Raised when an exact policy target is already registered."""


class PolicyEvaluationError(RuntimeError):
    """Raised internally to exercise safe fail-closed behavior."""


__all__ = [
    "DuplicatePolicyError",
    "PermissionRequestValidationError",
    "PolicyEvaluationError",
    "PolicyValidationError",
]
