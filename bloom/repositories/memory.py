"""In-memory repository."""

from collections.abc import Hashable
from typing import Any, override

from bloom import domain
from bloom.repositories import abc


class InMemoryRepository[T: domain.Entity[Any], E: Hashable](abc.BaseRepository[T, E]):
    """In-memory repository implementation for testing and prototyping.

    Stores entities in a dictionary keyed by their ID.
    Not suitable for production use, but ideal for unit tests and rapid prototyping.

    Type Parameters:
        T: The entity type this repository manages
        E: The id type of the entity type

    Example:
        >>> class Product(Entity[int]):
        ...     pass
        >>> repo = InMemoryRepository(Product, int)
        >>> product = Product(123)
        >>> repo.add(product)
        >>> found = repo.get(123)

        >>> repo = InMemoryRepository(Product, str)
    """

    def __init__(self, entity_type: type[T], id_type: type[E]):
        """Initialize an empty in-memory repository."""
        super().__init__(entity_type, id_type)
        self._entities: dict[E, T] = {}

    @override
    def add(self, entity: T) -> None:
        """Add a new entity to the in-memory store."""
        self._entities[entity.id] = entity

    @override
    def get(self, entity_id: E) -> T | None:
        """Retrieve an entity by its ID from the in-memory store."""
        return self._entities.get(entity_id)

    @override
    def remove(self, entity_id: E) -> None:
        """Remove an entity from the in-memory store."""
        self._entities.pop(entity_id, None)

    @override
    def list(self) -> list[T]:
        """List all entities in the in-memory store."""
        return list(self._entities.values())
