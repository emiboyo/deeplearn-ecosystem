"""Shared, provider-neutral model capability identifiers."""

from enum import StrEnum


class ModelCapability(StrEnum):
    """Model capabilities controlled by Core for Milestone 1."""

    TEXT_GENERATION = "text_generation"


__all__ = ["ModelCapability"]
