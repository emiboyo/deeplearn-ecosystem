"""Owned interface for permission and purpose evaluation.

No role, scope, or allow/deny policy is implemented in M1.2.
"""

from typing import Protocol

from deeplearn.core.contracts import WireDocument


class PermissionEvaluator(Protocol):
    """Evaluate authority facts and return a canonical Decision document."""

    def evaluate(self, request: WireDocument) -> WireDocument:
        """Return a decision without executing the requested action."""


__all__ = ["PermissionEvaluator"]
