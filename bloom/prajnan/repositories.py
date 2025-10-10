"""Repository patterns and implementations for DDD."""

from abc import ABC, abstractmethod
from collections.abc import Callable, Hashable
from typing import Protocol, TypeVar, override

from bloom.parijata import Event
from bloom.sara import Aggregate, Entity


EntityIdT = TypeVar("EntityIdT", bound=Hashable)
T = TypeVar("T", bound="Entity[Hashable]")
A = TypeVar("A", bound="Aggregate[Hashable]")


class Repository[T: Entity[Hashable]](Protocol):
    """Protocol defining the repository interface for entities.

    Repositories provide an abstraction over data persistence,
    allowing domain logic to remain independent of infrastructure concerns.
    """

    def add(self, entity: T) -> None:
        """Add a new entity to the repository.

        Args:
            entity: The entity to add.
        """
        ...

    def get(self, entity_id: Hashable) -> T | None:
        """Retrieve an entity by its ID.

        Args:
            entity_id: The unique identifier of the entity.

        Returns:
            The entity if found, None otherwise.
        """
        ...

    def remove(self, entity_id: Hashable) -> None:
        """Remove an entity from the repository.

        Args:
            entity_id: The unique identifier of the entity to remove.
        """
        ...

    def list(self) -> list[T]:
        """List all entities in the repository.

        Returns:
            A list of all entities.
        """
        ...


class AbstractRepository[T: Entity[Hashable]](ABC):
    """Abstract base class for repository implementations.

    Provides common functionality and enforces the repository contract.
    """

    @abstractmethod
    def add(self, entity: T) -> None:
        """Add a new entity to the repository."""
        raise NotImplementedError

    @abstractmethod
    def get(self, entity_id: Hashable) -> T | None:
        """Retrieve an entity by its ID."""
        raise NotImplementedError

    @abstractmethod
    def remove(self, entity_id: Hashable) -> None:
        """Remove an entity from the repository."""
        raise NotImplementedError

    @abstractmethod
    def list(self) -> list[T]:
        """List all entities in the repository."""
        raise NotImplementedError


class InMemoryRepository[T: Entity[Hashable]](AbstractRepository[T]):
    """In-memory repository implementation for testing and prototyping.

    Stores entities in a dictionary keyed by their ID.
    Not suitable for production use, but ideal for unit tests and rapid prototyping.
    """

    def __init__(self) -> None:
        """Initialize an empty in-memory repository."""
        self._entities: dict[Hashable, T] = {}

    @override
    def add(self, entity: T) -> None:
        """Add a new entity to the in-memory store."""
        self._entities[entity.id] = entity

    @override
    def get(self, entity_id: Hashable) -> T | None:
        """Retrieve an entity by its ID from the in-memory store."""
        return self._entities.get(entity_id)

    @override
    def remove(self, entity_id: Hashable) -> None:
        """Remove an entity from the in-memory store."""
        self._entities.pop(entity_id, None)

    @override
    def list(self) -> list[T]:
        """List all entities in the in-memory store."""
        return list(self._entities.values())


class EventPublishingRepository[A: Aggregate[Hashable]]:
    """Decorator that publishes domain events from aggregates.

    Wraps a repository and publishes any pending events from aggregates
    after they are added to the repository. This ensures that domain events
    are handled as part of the persistence transaction.

    Example:
        >>> base_repo = InMemoryRepository[MyAggregate]()
        >>> repo = EventPublishingRepository(base_repo, event_bus.publish)
        >>> aggregate.raise_event(SomethingHappened())
        >>> repo.add(aggregate)  # Events are published automatically
    """

    def __init__(
        self,
        repository: Repository[A],
        publish_event: Callable[[Event[Hashable]], None],
    ) -> None:
        """Initialize the event-publishing repository.

        Args:
            repository: The underlying repository to wrap.
            publish_event: A callable that publishes a single event.
        """
        self._repository = repository
        self._publish_event = publish_event

    def add(self, entity: A) -> None:
        """Add an aggregate and publish its pending events.

        Args:
            entity: The aggregate to add.
        """
        self._repository.add(entity)
        self._publish_events(entity)

    def get(self, entity_id: Hashable) -> A | None:
        """Retrieve an aggregate by its ID.

        Args:
            entity_id: The unique identifier of the aggregate.

        Returns:
            The aggregate if found, None otherwise.
        """
        return self._repository.get(entity_id)

    def remove(self, entity_id: Hashable) -> None:
        """Remove an aggregate from the repository.

        Args:
            entity_id: The unique identifier of the aggregate to remove.
        """
        self._repository.remove(entity_id)

    def list(self) -> list[A]:
        """List all aggregates in the repository.

        Returns:
            A list of all aggregates.
        """
        return self._repository.list()

    def _publish_events(self, aggregate: A) -> None:
        """Publish all pending events from an aggregate."""
        events = aggregate.flush_events()
        for event in events:
            self._publish_event(event)
