"""Owned interfaces for later runtime composition.

This module makes allowed dependency direction explicit but implements no
orchestration, storage access, provider calls, or business behavior.
"""

from dataclasses import dataclass
from typing import Protocol

from deeplearn.core.audit import AuditWriter
from deeplearn.core.contracts import WireDocument
from deeplearn.core.models import ModelGateway
from deeplearn.core.permissions import PermissionEvaluator
from deeplearn.core.registry import AgentDefinitionRegistry
from deeplearn.core.tools import ToolGateway


@dataclass(frozen=True, slots=True)
class RuntimeDependencies:
    """Interfaces the future runtime may orchestrate, without implementations."""

    registry: AgentDefinitionRegistry
    models: ModelGateway
    tools: ToolGateway
    permissions: PermissionEvaluator
    audit: AuditWriter


class RuntimeInterface(Protocol):
    """Programmatic entry point for a canonical ExecutionRequest document."""

    def execute(self, request: WireDocument) -> WireDocument:
        """Return a canonical ExecutionResult document."""


__all__ = ["RuntimeDependencies", "RuntimeInterface"]
