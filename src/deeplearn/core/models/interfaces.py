"""Owned provider-neutral model invocation interface.

Routing, fake models, and provider adapters are deferred to M1.4.
"""

from typing import Protocol

from deeplearn.core.contracts import WireDocument


class ModelGateway(Protocol):
    """Invoke a model capability through provider-neutral documents."""

    def complete(self, request: WireDocument) -> WireDocument:
        """Return a provider-neutral result document."""


__all__ = ["ModelGateway"]
