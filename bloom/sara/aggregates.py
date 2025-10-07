"""Utility classes and methods to define aggregates."""

from collections.abc import Hashable
from typing import TypeVar

from bloom import parijata
from bloom.sara import Entity


AggregateId = TypeVar("AggregateId", bound=Hashable)


class Aggregate(Entity[AggregateId]):
    """Base class for aggregates."""

    def __init__(self, entity_id: AggregateId) -> None:
        """Initialize the aggregate."""
        super().__init__(entity_id)
        self._version: int = 0
        self._events: list[parijata.Event[AggregateId]] = []

    @property
    def version(self) -> int:
        """The current version of this aggregate."""
        return self._version

    @property
    def pending_events(self) -> list[parijata.Event[AggregateId]]:
        """The pending events for this entity."""
        return self._events.copy()

    def _increment_version(self) -> None:
        self._version += 1

    def raise_event(self, event: parijata.Event[AggregateId]) -> None:
        """Raises a domain event for publication."""
        event.entity_id = self._id
        self._events.append(event)

    def flush_events(self) -> list[parijata.Event[AggregateId]]:
        """Clears and returns all pending events."""
        events = self.pending_events
        self._events.clear()
        return events
