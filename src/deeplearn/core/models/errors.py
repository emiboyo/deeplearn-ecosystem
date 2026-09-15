"""Internal adapter and registration errors handled by the model boundary."""


class DuplicateAdapterError(ValueError):
    """Raised when a provider/model identity is already registered."""


class ProviderUnavailableError(RuntimeError):
    """Raised by an adapter when its provider cannot accept the request."""


class ProviderTimeoutError(TimeoutError):
    """Raised by an adapter when its bounded invocation times out."""


__all__ = ["DuplicateAdapterError", "ProviderTimeoutError", "ProviderUnavailableError"]
