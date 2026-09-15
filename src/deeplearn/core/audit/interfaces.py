"""Owned append/query interfaces for audit evidence.

Persistence and a test repository are deferred to M1.8.
"""

from typing import Protocol

from deeplearn.core.contracts import WireDocument


class AuditWriter(Protocol):
    """Accept an AuditRecord document for an eventual append-only store."""

    def append(self, record: WireDocument) -> None:
        """Append an audit record; no implementation exists in M1.2."""


class AuditReader(Protocol):
    """Read audit evidence through a boundary rather than direct storage."""

    def query(self, audit_record_id: str) -> WireDocument | None:
        """Return one record when available."""


__all__ = ["AuditReader", "AuditWriter"]
