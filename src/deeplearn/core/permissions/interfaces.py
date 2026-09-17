"""Owned interface for permission and purpose evaluation."""

from collections.abc import Mapping
from typing import Protocol

from .contracts import PermissionDecision, PermissionRequest


class PermissionEvaluator(Protocol):
    """Evaluate authority facts without executing the requested action."""

    def evaluate(
        self, request: PermissionRequest | Mapping[str, object]
    ) -> PermissionDecision:
        """Return a machine-readable, fail-closed permission decision."""


__all__ = ["PermissionEvaluator"]
