"""Utility classes and methods to define aggregates."""

from collections.abc import Hashable
from typing import TypeVar

from bloom import events
from bloom.domain import entities


try:
    from sqlalchemy import orm as _orm

    HAS_SQLALCHEMY = True
except ImportError:
    HAS_SQLALCHEMY = False


AggregateId = TypeVar("AggregateId", bound=Hashable)


class Aggregate(entities.Entity[AggregateId]):
    """Base class for aggregates."""

    def __init__(self, entity_id: AggregateId) -> None:
        """Initialize the aggregate."""
        super().__init__(entity_id)
        self._init_aggregate_state()

    def _init_aggregate_state(self) -> None:
        """Initialize transient aggregate state.

        This method is called both during __init__ and by SQLAlchemy's
        reconstructor when loading from the database.
        """
        # Only initialize _version if it doesn't exist (i.e., for new objects)
        # When loading from DB, SQLAlchemy will have already set _version
        if not hasattr(self, "_version"):
            self._version: int = 0

        self._events: list[events.Event[AggregateId]] = []

    @property
    def version(self) -> int:
        """The current version of this aggregate."""
        return self._version

    @property
    def pending_events(self) -> list[events.Event[AggregateId]]:
        """The pending events for this entity."""
        return self._events.copy()

    def _increment_version(self) -> None:
        self._version += 1

    def raise_event(self, event: events.Event[AggregateId]) -> None:
        """Raises a domain event for publication."""
        event.entity_id = self._id
        self._events.append(event)

    def flush_events(self) -> list[events.Event[AggregateId]]:
        """Clears and returns all pending events."""
        events = self.pending_events
        self._events.clear()
        return events

    if HAS_SQLALCHEMY:
        _init_aggregate_state = _orm.reconstructor(_init_aggregate_state)
