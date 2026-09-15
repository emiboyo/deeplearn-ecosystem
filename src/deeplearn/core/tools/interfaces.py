"""Owned interface for registered tool invocation.

Tool implementations, dispatch, and credentials are deferred to M1.5.
"""

from typing import Protocol

from deeplearn.core.contracts import WireDocument


class ToolGateway(Protocol):
    """Invoke only a separately registered tool contract."""

    def invoke(self, request: WireDocument) -> WireDocument:
        """Return a result conforming to the canonical ToolResult schema."""


__all__ = ["ToolGateway"]
