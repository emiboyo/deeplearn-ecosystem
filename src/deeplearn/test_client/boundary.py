"""Tiny programmatic boundary representing an external M1 test caller."""

from dataclasses import dataclass

from deeplearn.core.contracts import WireDocument
from deeplearn.core.runtime import RuntimeInterface


@dataclass(frozen=True, slots=True)
class TestClientBoundary:
    """Pass a wire request to the runtime boundary without adding behavior."""

    runtime: RuntimeInterface

    def submit(self, request: WireDocument) -> WireDocument:
        """Forward an ExecutionRequest document unchanged to the runtime."""
        return self.runtime.execute(request)


__all__ = ["TestClientBoundary"]
