"""Provider-neutral model routing boundary."""

from .contracts import (
    AdapterResponse,
    InvalidModelRequestError,
    ModelFailure,
    ModelFailureCategory,
    ModelRequest,
    ModelResult,
    ModelStatus,
    ModelUsage,
)
from .errors import DuplicateAdapterError, ProviderTimeoutError, ProviderUnavailableError
from .fake import DeterministicFakeAdapter, FakeFailure
from .interfaces import ModelAdapter, ModelGateway
from .router import ModelRouter

__all__ = [
    "AdapterResponse", "DeterministicFakeAdapter", "DuplicateAdapterError",
    "FakeFailure", "InvalidModelRequestError", "ModelAdapter", "ModelFailure",
    "ModelFailureCategory", "ModelGateway", "ModelRequest", "ModelResult",
    "ModelRouter", "ModelStatus", "ModelUsage", "ProviderTimeoutError",
    "ProviderUnavailableError",
]
