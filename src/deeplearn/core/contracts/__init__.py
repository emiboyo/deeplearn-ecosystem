"""References to the canonical M1 wire contracts.

The JSON Schemas in ``contracts/v1`` are authoritative. ``WireDocument`` is
only a minimal interface annotation and is not a second contract model.
"""

from collections.abc import Mapping
from typing import TypeAlias

from .model_capabilities import ModelCapability

WireDocument: TypeAlias = Mapping[str, object]

__all__ = ["ModelCapability", "WireDocument"]
