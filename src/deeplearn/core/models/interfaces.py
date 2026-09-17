"""Owned provider-neutral model adapter and gateway interfaces."""

from collections.abc import Mapping
from typing import Protocol

from deeplearn.core.contracts import ModelCapability
from .contracts import AdapterResponse, ModelRequest, ModelResult


class ModelAdapter(Protocol):
    """Invoke one provider/model without exposing provider SDK types."""

    provider_id: str
    model_id: str
    model_version: str | None
    supported_capabilities: frozenset[ModelCapability]

    def invoke(self, request: ModelRequest) -> AdapterResponse:
        """Return a normalized response or raise an internal adapter error."""


class ModelGateway(Protocol):
    """Route a provider-neutral model request to a registered adapter."""

    def complete(self, request: ModelRequest | Mapping[str, object]) -> ModelResult:
        """Return a normalized result without leaking adapter exceptions."""


__all__ = ["ModelAdapter", "ModelGateway"]
